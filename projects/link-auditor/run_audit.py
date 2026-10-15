#!/usr/bin/env python3
"""Run a local CLI audit with a configurable overall process deadline."""
import argparse
from pathlib import Path
import subprocess
import sys


def deadline(value):
    seconds=int(value)
    if not 1<=seconds<=86400:
        raise argparse.ArgumentTypeError('Expected 1..86400 seconds')
    return seconds


def main(argv=None, runner=subprocess.run):
    parser=argparse.ArgumentParser(description=__doc__,epilog='Pass normal link_auditor.py arguments after --. Timeout exit: 124; a complete report may not be available.')
    parser.add_argument('--deadline',type=deadline,default=300,help='Overall child process deadline in seconds, default 300')
    parser.add_argument('audit_args',nargs=argparse.REMAINDER)
    args=parser.parse_args(argv)
    rest=args.audit_args[1:] if args.audit_args[:1]==['--'] else args.audit_args
    if not rest:parser.error('Provide a website URL and CLI arguments after --')
    try:
        return runner([sys.executable,str(Path(__file__).with_name('link_auditor.py').resolve()),*rest],timeout=args.deadline,check=False).returncode
    except subprocess.TimeoutExpired:
        print('Audit deadline reached. A complete report may not have been written.',file=sys.stderr)
        return 124


if __name__=='__main__':raise SystemExit(main())
