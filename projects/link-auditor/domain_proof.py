#!/usr/bin/env python3
"""Exact-origin HTTPS file proof. Run in a deadline-bounded child process."""
import argparse
import ipaddress
import re
from urllib.parse import urlsplit
from link_auditor import Network


def owned_origin(value):
    if not isinstance(value,str) or len(value)>265:
        raise ValueError('Invalid origin')
    match=re.fullmatch(r'https://([a-z0-9](?:[a-z0-9.-]*[a-z0-9])?)/?',value)
    if not match:
        raise ValueError('Expected an HTTPS origin without path, query, IP or port')
    host=match[1]
    if len(host)>253 or '.' not in host or any(not re.fullmatch(r'[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?',label) for label in host.split('.')):
        raise ValueError('Invalid hostname')
    try:
        ipaddress.ip_address(host)
    except ValueError:
        return 'https://'+host+'/'
    raise ValueError('IP literals are not domains')


def verify(value,proof,network=None):
    origin=owned_origin(value)
    if not isinstance(proof,str) or not re.fullmatch(r'openvist-audit-verification=[a-f0-9]{64}',proof):
        raise ValueError('Invalid ownership proof')
    response=(network or Network(timeout=5,delay=0,byte_limit=4096)).get(origin+'.well-known/openvist-audit.txt')
    # No redirect following, cookies, ambient proxy, credentials or arbitrary paths.
    return response.status==200 and not response.truncated and response.body.strip()==proof.encode('ascii')


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('origin');parser.add_argument('proof');args=parser.parse_args()
    try:
        return 0 if verify(args.origin,args.proof) else 1
    except (ValueError,OSError):
        return 2


if __name__=='__main__':raise SystemExit(main())
