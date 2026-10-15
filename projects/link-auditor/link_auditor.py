#!/usr/bin/env python3
"""Bounded, read-only HTTP link audit. Python 3.11+, standard library only."""
import argparse
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timezone
from html import escape
from html.parser import HTMLParser
import http.client
import ipaddress
import json
from pathlib import Path
import socket
import time
from urllib.parse import urljoin, urlsplit, urlunsplit
from urllib.robotparser import RobotFileParser
import xml.etree.ElementTree as ET

VERSION = '0.4.1'
AGENT = 'OpenViST-Link-Auditor/0.4 (+https://openvist.com/tools/link-auditor/)'


def canonical(value, base=None):
    value = urljoin(base, value) if base else value
    p = urlsplit(value)
    if p.scheme not in ('http', 'https') or not p.hostname or p.username or p.password:
        raise ValueError('Expected an HTTP(S) URL without embedded credentials')
    if any(ord(c) < 33 for c in value) or len(value) > 4096:
        raise ValueError('Invalid or oversized URL')
    port = p.port
    host = p.hostname.encode('idna').decode('ascii').lower()
    if ':' in host:
        host = '[' + host + ']'
    netloc = host + ((':' + str(port)) if port and port != (443 if p.scheme == 'https' else 80) else '')
    return urlunsplit((p.scheme.lower(), netloc, p.path or '/', p.query, ''))


def origin(url):
    p = urlsplit(url)
    return p.scheme + '://' + p.netloc


def public_addresses(host, port):
    addresses = list(dict.fromkeys(row[4][0] for row in socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)))
    if not addresses or any(not ipaddress.ip_address(address).is_global for address in addresses):
        raise ValueError('Non-public network destination refused')
    return addresses


@dataclass
class Response:
    url: str
    status: int
    headers: dict
    body: bytes
    truncated: bool = False


class Network:
    def __init__(self, timeout=10, delay=0.25, byte_limit=1_000_000):
        self.timeout, self.delay, self.byte_limit = timeout, delay, byte_limit
        self.last = 0.0

    def get(self, url):
        p = urlsplit(url)
        port = p.port or (443 if p.scheme == 'https' else 80)
        addresses = public_addresses(p.hostname, port)
        time.sleep(max(0, self.delay - (time.monotonic() - self.last)))
        cls = http.client.HTTPSConnection if p.scheme == 'https' else http.client.HTTPConnection
        connection = cls(p.hostname, port, timeout=self.timeout)
        # Pin the validated address while retaining the original HTTP host and TLS name.
        connection._create_connection = lambda address, timeout, source_address=None: socket.create_connection((addresses[0], port), timeout, source_address)
        try:
            self.last = time.monotonic()
            target = urlunsplit(('', '', p.path or '/', p.query, ''))
            connection.request('GET', target, headers={'User-Agent': AGENT, 'Accept-Encoding':'identity', 'Connection':'close'})
            response = connection.getresponse()
            headers = {key.lower(): value for key, value in response.getheaders()}
            body = response.read(self.byte_limit + 1)
            return Response(url, response.status, headers, body[:self.byte_limit], len(body) > self.byte_limit)
        finally:
            connection.close()


class Links(HTMLParser):
    def __init__(self, limit=500):
        super().__init__(convert_charrefs=True)
        self.links, self.base, self.limit, self.truncated = [], None, limit, False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'base' and self.base is None:
            self.base = attrs.get('href')
        if tag == 'a' and attrs.get('href'):
            if len(self.links) < self.limit:
                self.links.append(attrs['href'])
            else:
                self.truncated = True


class Auditor:
    def __init__(self, start, max_pages=50, max_urls=500, external=False, network=None):
        self.start = canonical(start)
        self.home = origin(self.start)
        self.max_pages, self.max_urls, self.external = max_pages, max_urls, external
        self.network = network or Network()
        self.robots, self.robot_errors = {}, {}
        self.results, self.sources, self.queue, self.queued = [], {}, deque(), set()
        self.pages = 0
        self.limits_reached = False

    def permitted(self, url):
        site = origin(url)
        if site not in self.robots:
            parser = RobotFileParser()
            try:
                response = self.network.get(site + '/robots.txt')
                if response.status == 200 and not response.truncated:
                    parser.parse(response.body.decode('utf-8', errors='replace').splitlines())
                elif response.status in (404, 410):
                    parser.parse([])
                else:
                    raise ValueError('robots.txt unavailable (HTTP ' + str(response.status) + ')')
                self.robots[site] = parser
            except Exception as error:
                self.robots[site] = None
                self.robot_errors[site] = type(error).__name__ + ': robots.txt could not be checked'
        parser = self.robots[site]
        return parser is not None and parser.can_fetch(AGENT, url)

    def fetch(self, url):
        seen, chain = set(), []
        current = url
        for _ in range(6):
            if current in seen:
                raise ValueError('Redirect loop')
            seen.add(current)
            if not self.permitted(current):
                return None, chain, 'robots_unavailable' if origin(current) in self.robot_errors else 'robots_denied'
            response = self.network.get(current)
            if response.status not in (301, 302, 303, 307, 308):
                return response, chain, None
            if not response.headers.get('location'):
                raise ValueError('Redirect has no Location header')
            target = canonical(response.headers['location'], current)
            chain.append({'from':current,'to':target,'status':response.status})
            if origin(target) != self.home and not self.external:
                return None, chain, 'external_redirect_not_checked'
            current = target
        raise ValueError('Redirect limit exceeded')

    def enqueue(self, url, source, base=None):
        try:
            url = canonical(url, base or source)
        except (ValueError, UnicodeError):
            return
        if origin(url) != self.home and not self.external:
            return
        if url not in self.queued:
            if len(self.queued) >= self.max_urls:
                self.limits_reached = True
                return
            self.queued.add(url)
            self.queue.append(url)
            self.sources[url] = []
        if source not in self.sources[url] and len(self.sources[url]) < 20:
            self.sources[url].append(source)

    def sitemap(self, url):
        pending, seen = deque([canonical(url, self.start)]), set()
        while pending and len(seen) < 10:
            current = pending.popleft()
            if current in seen:
                continue
            if origin(current) != self.home:
                raise ValueError('Sitemaps must use the starting origin')
            seen.add(current)
            response, _, blocked = self.fetch(current)
            if blocked or response.status != 200 or response.truncated:
                raise ValueError('Sitemap could not be read completely')
            root = ET.fromstring(response.body)
            kind = root.tag.rsplit('}', 1)[-1]
            if kind not in ('sitemapindex','urlset'):
                raise ValueError('Expected an XML sitemap index or URL set')
            for child in root:
                for element in child:
                    if element.tag.rsplit('}',1)[-1] != 'loc' or not element.text:
                        continue
                    target = canonical(element.text.strip(), current)
                    if origin(target) != self.home:
                        continue
                    if kind == 'sitemapindex':
                        if len(pending) < 10:
                            pending.append(target)
                        else:
                            self.limits_reached = True
                    else:
                        self.enqueue(target, current)
        if pending:
            self.limits_reached = True

    def run(self, sitemap=None):
        self.enqueue(self.start, self.start)
        if sitemap:
            self.sitemap(sitemap)
        while self.queue:
            url = self.queue.popleft()
            row = {'url':url,'status':None,'outcome':'not_checked','redirects':[]}
            if origin(url) == self.home and self.pages >= self.max_pages:
                self.limits_reached = True
                self.results.append(row)
                continue
            if origin(url) == self.home:
                self.pages += 1
            try:
                response, chain, blocked = self.fetch(url)
                row['redirects'] = chain
                if blocked:
                    row['outcome'] = blocked
                else:
                    row.update(status=response.status, final_url=response.url, body_truncated=response.truncated)
                    status = response.status
                    row['outcome'] = ('ok' if 200 <= status < 300 else 'missing' if status in (404,410)
                        else 'restricted' if status in (401,403) else 'rate_limited' if status == 429
                        else 'server_error' if status >= 500 else 'http_error')
                    if response.truncated:
                        self.limits_reached = True
                    if origin(response.url) == self.home and 200 <= status < 300 and 'text/html' in response.headers.get('content-type',''):
                        content_type = response.headers.get('content-type','')
                        encoding = content_type.split('charset=')[-1].split(';')[0].strip(' "') if 'charset=' in content_type else 'utf-8'
                        parser = Links(self.max_urls)
                        parser.feed(response.body.decode(encoding, errors='replace'))
                        base = canonical(parser.base, response.url) if parser.base else response.url
                        for href in parser.links:
                            if not href.startswith('#'):
                                self.enqueue(href, response.url, base)
                        self.limits_reached |= parser.truncated
            except Exception as error:
                row.update(outcome='request_error', error=type(error).__name__ + ': request or parsing failed')
            self.results.append(row)
        for row in self.results:
            row['sources'] = self.sources[row['url']]
        counts = {}
        for row in self.results:
            counts[row['outcome']] = counts.get(row['outcome'],0) + 1
        return {'tool':'OpenViST Link Auditor','version':VERSION,'started_from':self.start,
            'generated_at':datetime.now(timezone.utc).isoformat(),'summary':counts,
            'limits_reached':self.limits_reached, 'robots_errors':self.robot_errors,
            'scope':{'max_pages':self.max_pages,'max_urls':self.max_urls,'external':self.external},'results':self.results}


from report_view import html_report


def bounded_int(value):
    number = int(value)
    if not 1 <= number <= 5000:
        raise argparse.ArgumentTypeError('Expected 1..5000')
    return number


def finite_number(value, minimum, maximum):
    import math
    number = float(value)
    if not math.isfinite(number) or not minimum <= number <= maximum:
        raise argparse.ArgumentTypeError('Expected '+str(minimum)+'..'+str(maximum))
    return number


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('url')
    parser.add_argument('--sitemap', help='Same-origin XML sitemap URL or path')
    parser.add_argument('--max-pages', type=bounded_int, default=50)
    parser.add_argument('--max-urls', type=bounded_int, default=500)
    parser.add_argument('--external', action='store_true', help='Also check discovered external links')
    parser.add_argument('--request-timeout', type=lambda v: finite_number(v,1,60), default=10, help='Socket timeout in seconds (1..60)')
    parser.add_argument('--delay', type=lambda v: finite_number(v,0,60), default=0.25, help='Seconds between request starts (0..60)')
    parser.add_argument('--byte-limit', type=lambda v: int(finite_number(v,1024,10485760)), default=1000000, help='Body bytes retained per response (1024..10485760)')
    parser.add_argument('--output', type=Path, default=Path('link-audit'))
    args = parser.parse_args(argv)
    json_path = Path(str(args.output)+'.json');html_path = Path(str(args.output)+'.html')
    if json_path.exists() or html_path.exists():
        parser.exit(2,'Output exists; choose a new --output prefix.\n')
    try:
        report = Auditor(args.url,args.max_pages,args.max_urls,args.external,network=Network(timeout=args.request_timeout,delay=args.delay,byte_limit=args.byte_limit)).run(args.sitemap)
        report['scope'].update(request_timeout=args.request_timeout,delay=args.delay,byte_limit=args.byte_limit)
    except (ValueError, OSError, ET.ParseError) as error:
        parser.exit(2, 'Audit could not start: '+type(error).__name__+'\n')
    json_path = Path(str(args.output)+'.json');html_path = Path(str(args.output)+'.html')
    if json_path.exists() or html_path.exists():
        parser.exit(2,'Output exists; choose a new --output prefix.\n')
    json_path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    html_path.write_text(html_report(report),encoding='utf-8')
    print(json.dumps(report['summary'],sort_keys=True))
    print('Reports:',json_path,html_path)
    return 1 if any(row['outcome'] not in ('ok',) for row in report['results']) or report['limits_reached'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
