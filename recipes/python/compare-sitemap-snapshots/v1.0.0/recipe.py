# SPDX-License-Identifier: MIT
# Copyright (c) 2026 OpenViST contributors
"""Compare URLs in two saved sitemap urlsets without crawling the site."""
import argparse
from collections import Counter
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET

MAX_BYTES = 8 * 1024 * 1024
NS = "{http://www.sitemaps.org/schemas/sitemap/0.9}"


def read_urls(path):
    with Path(path).open("rb") as stream:
        raw = stream.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError("sitemap exceeds 8 MiB")
    text = raw.decode("utf-8-sig")
    if "\x00" in text or re.search(r"<!\s*(?:DOCTYPE|ENTITY)\b", text, re.I):
        raise ValueError("use UTF-8 XML without DTD or entity declarations")
    try:
        root = ET.fromstring(text)
    except ET.ParseError as error:
        raise ValueError("invalid sitemap XML") from error
    if root.tag != NS + "urlset":
        raise ValueError("use a namespaced urlset, not a sitemap index")
    urls, host = Counter(), None
    if len(root) > 50000:
        raise ValueError("sitemap exceeds 50,000 entries")
    for entry in root:
        locations = entry.findall(NS + "loc")
        if entry.tag != NS + "url" or len(locations) != 1:
            raise ValueError("each url must contain exactly one loc")
        url = (locations[0].text or "").strip()
        parsed = urlsplit(url)
        if len(url) > 2048 or re.search(r"\s", url) or parsed.scheme not in ("http", "https") or not parsed.hostname or parsed.username is not None or parsed.password is not None or parsed.fragment:
            raise ValueError("loc must be an absolute HTTP(S) URL without credentials or fragments")
        identity = (parsed.scheme, parsed.hostname, parsed.port)
        if host is None:
            host = identity
        elif identity != host:
            raise ValueError("each sitemap must use one protocol and host")
        urls[url] += 1
    return urls


def compare(before, after):
    old, new = read_urls(before), read_urls(after)
    return {"before_unique": len(old), "after_unique": len(new),
            "added": sorted(new.keys() - old.keys()), "removed": sorted(old.keys() - new.keys()),
            "unchanged": len(old.keys() & new.keys()),
            "duplicates_before": sorted(url for url, count in old.items() if count > 1),
            "duplicates_after": sorted(url for url, count in new.items() if count > 1)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("before")
    parser.add_argument("after")
    args = parser.parse_args()
    try:
        print(json.dumps(compare(args.before, args.after), ensure_ascii=False, indent=2))
    except (OSError, ValueError, UnicodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
