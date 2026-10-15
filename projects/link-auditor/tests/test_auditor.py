import importlib.util
import json
from pathlib import Path
import socket
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).parents[1]))
from link_auditor import Auditor, Network, Response, canonical, html_report, main, public_addresses

BASE='https://example.com'


class FakeNetwork:
    def __init__(self, routes):
        self.routes=routes;self.calls=[]

    def get(self,url):
        self.calls.append(url)
        status,headers,body=self.routes.get(url,(200,{'content-type':'text/plain'},b''))
        return Response(url,status,headers,body)


def page(body): return (200,{'content-type':'text/html; charset=utf-8'},body.encode())


class AuditTests(unittest.TestCase):
    def test_discovery_missing_link_and_sources(self):
        network=FakeNetwork({BASE+'/':page('<a href="/good#top">Good</a><a href="/missing">Missing</a><a href="mailto:x@y">Mail</a>'),BASE+'/missing':(404,{},b'')})
        report=Auditor(BASE,network=network).run()
        self.assertEqual(report['summary'],{'ok':2,'missing':1})
        missing=next(r for r in report['results'] if r['outcome']=='missing')
        self.assertEqual(missing['sources'],[BASE+'/'])
        self.assertEqual(network.calls.count(BASE+'/robots.txt'),1)

    def test_redirect_chain_and_loop(self):
        network=FakeNetwork({BASE+'/':(301,{'location':'/new'},b''),BASE+'/new':page('')})
        result=Auditor(BASE,network=network).run()['results'][0]
        self.assertEqual(result['final_url'],BASE+'/new');self.assertEqual(len(result['redirects']),1)
        network.routes[BASE+'/new']=(302,{'location':'/'},b'')
        self.assertEqual(Auditor(BASE,network=network).run()['summary'],{'request_error':1})

    def test_external_links_not_requested_by_default(self):
        network=FakeNetwork({BASE+'/':page('<a href="https://elsewhere.example/">Other</a>')})
        self.assertEqual(len(Auditor(BASE,network=network).run()['results']),1)
        self.assertFalse(any('elsewhere' in url for url in network.calls))

    def test_external_redirect_is_reported_without_following(self):
        network=FakeNetwork({BASE+'/':(302,{'location':'https://elsewhere.example/'},b'')})
        report=Auditor(BASE,network=network).run()
        self.assertEqual(report['summary'],{'external_redirect_not_checked':1})
        self.assertFalse(any('elsewhere' in url for url in network.calls))

    def test_robots_denied_and_unavailable(self):
        for status,body,outcome in [(200,b'User-agent: *\nDisallow: /\n','robots_denied'),(503,b'','robots_unavailable')]:
            network=FakeNetwork({BASE+'/robots.txt':(status,{},body)})
            report=Auditor(BASE,network=network).run()
            self.assertEqual(report['summary'],{outcome:1});self.assertNotIn(BASE+'/',network.calls)

    def test_page_limit_is_explicit_not_a_false_success(self):
        network=FakeNetwork({BASE+'/':page('<a href="/next">Next</a>')})
        report=Auditor(BASE,max_pages=1,network=network).run()
        self.assertTrue(report['limits_reached']);self.assertEqual(report['summary']['not_checked'],1)
        self.assertNotIn(BASE+'/next',network.calls)

    def test_url_budget_stops_discovery(self):
        network=FakeNetwork({BASE+'/':page('<a href="/a">A</a><a href="/b">B</a>')})
        report=Auditor(BASE,max_urls=2,network=network).run()
        self.assertEqual(len(report['results']),2);self.assertTrue(report['limits_reached'])

    def test_sitemap_index_and_duplicate_urls(self):
        network=FakeNetwork({BASE+'/sitemap.xml':(200,{},b'<sitemapindex><sitemap><loc>https://example.com/part.xml</loc></sitemap></sitemapindex>'),BASE+'/part.xml':(200,{},b'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://example.com/a</loc></url><url><loc>https://example.com/a</loc></url></urlset>')})
        report=Auditor(BASE,network=network).run('/sitemap.xml')
        self.assertEqual(report['summary'],{'ok':2});self.assertEqual(network.calls.count(BASE+'/a'),1)

    def test_http_outcomes_are_distinguished(self):
        for status,expected in [(403,'restricted'),(429,'rate_limited'),(500,'server_error'),(410,'missing')]:
            with self.subTest(status=status):
                report=Auditor(BASE,network=FakeNetwork({BASE+'/':(status,{},b'')})).run()
                self.assertEqual(report['summary'],{expected:1})

    def test_credential_and_non_http_urls_are_refused(self):
        for url in ['file:///etc/passwd','https://user:secret@example.com/','http://example.com/\nheader']:
            with self.assertRaises(ValueError): canonical(url)
        self.assertEqual(canonical('https://EXAMPLE.com:443/a#fragment'),BASE+'/a')

    def test_public_address_guard_rejects_mixed_dns(self):
        addresses=[(socket.AF_INET,socket.SOCK_STREAM,6,'',('93.184.216.34',443)),(socket.AF_INET,socket.SOCK_STREAM,6,'',('127.0.0.1',443))]
        with patch('socket.getaddrinfo',return_value=addresses):
            with self.assertRaises(ValueError): public_addresses('example.com',443)

    def test_report_escapes_markup(self):
        report=Auditor(BASE,network=FakeNetwork({})).run()
        report['results'][0]['sources']=['<script>alert(1)</script>']
        output=html_report(report)
        self.assertNotIn('<script>alert(1)</script>',output);self.assertIn('&lt;script&gt;',output)
        self.assertIn('Content-Security-Policy',output)


class TransportTests(unittest.TestCase):
    def test_real_http_transport_and_bounded_read(self):
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200);self.send_header('Content-Type','text/plain');self.end_headers();self.wfile.write(b'abcdef')
            def log_message(self,*args): pass
        server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        try:
            with patch('link_auditor.public_addresses',return_value=['127.0.0.1']):
                response=Network(delay=0,byte_limit=4).get('http://localhost:'+str(server.server_port)+'/')
            self.assertEqual(response.body,b'abcd');self.assertTrue(response.truncated)
        finally:
            server.shutdown();server.server_close();thread.join()


if __name__=='__main__':unittest.main()
