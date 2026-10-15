#!/usr/bin/env python3
"""Reproduce the standalone download from source; exclude private bridge/config files."""
import argparse
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED

FILES=['link_auditor.py','report_view.py','run_audit.py','SELF_HOSTING.md','LICENSE']
PREFIX='openvist-link-auditor-self-hosted-0.4.1'


def build(output):
    source=Path(__file__).resolve().parent
    output=Path(output);output.parent.mkdir(parents=True,exist_ok=True)
    with ZipFile(output,'w',ZIP_DEFLATED) as archive:
        for name in FILES:
            info=__import__('zipfile').ZipInfo(PREFIX+'/'+name,date_time=(2026,10,15,0,0,0))
            info.compress_type=ZIP_DEFLATED;info.external_attr=0o100644<<16
            archive.writestr(info,(source/name).read_bytes())
    return output


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args();print(build(args.output))
