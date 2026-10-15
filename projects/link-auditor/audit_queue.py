#!/usr/bin/env python3
"""Private, single-worker VPS pilot. No HTTP listener or public submission API."""
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import json
import os
from pathlib import Path
import resource
import sqlite3
import subprocess
import sys
import time
from urllib.parse import urlsplit
import uuid

from link_auditor import canonical


@contextmanager
def database(root):
    root = Path(root).expanduser().resolve()
    root.mkdir(mode=0o700, parents=True, exist_ok=True)
    root.chmod(0o700)
    db = sqlite3.connect(root / 'queue.sqlite', timeout=10)
    try:
        db.execute('CREATE TABLE IF NOT EXISTS jobs (id TEXT PRIMARY KEY, url TEXT NOT NULL, host TEXT NOT NULL, created REAL NOT NULL, state TEXT NOT NULL, detail TEXT NOT NULL DEFAULT "")')
        db.commit()
        yield root, db
    finally:
        db.close()


def allowed_url(root, value):
    url = canonical(value)
    parts = urlsplit(url)
    if parts.scheme != 'https' or parts.port not in (None, 443):
        raise ValueError('Pilot requires HTTPS on port 443')
    if parts.query:
        raise ValueError('Pilot start URL must not contain query parameters')
    hosts = json.loads((root / 'allowed-hosts.json').read_text())
    if not isinstance(hosts, list) or parts.hostname not in hosts:
        raise ValueError('Starting host is not on the private pilot allowlist')
    return url, parts.hostname


def submit(root, value, now=None):
    now = time.time() if now is None else now
    with database(root) as (root, db):
        url, host = allowed_url(root, value)
        db.execute('BEGIN IMMEDIATE')
        if db.execute('SELECT COUNT(*) FROM jobs').fetchone()[0] >= 100:
            raise ValueError('Private pilot storage limit reached (100 jobs); archive reports before continuing')
        if db.execute("SELECT COUNT(*) FROM jobs WHERE state IN ('queued','running')").fetchone()[0] >= 10:
            raise ValueError('Queue capacity reached (10 jobs)')
        if db.execute("SELECT 1 FROM jobs WHERE host=? AND (created>? OR state IN ('queued','running'))", (host, now - 900)).fetchone():
            raise ValueError('This host already has a pending job or a submission within 15 minutes')
        identifier = uuid.uuid4().hex
        db.execute('INSERT INTO jobs(id,url,host,created,state) VALUES(?,?,?,?,?)', (identifier, url, host, now, 'queued'))
        db.commit()
        return identifier


def child_limits():
    resource.setrlimit(resource.RLIMIT_AS, (256 * 1024 * 1024,) * 2)
    resource.setrlimit(resource.RLIMIT_CPU, (90,) * 2)
    resource.setrlimit(resource.RLIMIT_FSIZE, (8 * 1024 * 1024,) * 2)
    resource.setrlimit(resource.RLIMIT_NOFILE, (64,) * 2)
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))


def process_one(root, runner=subprocess.run):
    with database(root) as (root, db):
        with (root / 'worker.lock').open('a') as lock:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                return {'state': 'busy'}
            # A prior process was interrupted. Do not silently repeat its requests.
            db.execute("UPDATE jobs SET state='interrupted', detail='Previous worker stopped; no automatic retry' WHERE state='running'")
            db.execute('BEGIN IMMEDIATE') if not db.in_transaction else None
            row = db.execute("SELECT id,url FROM jobs WHERE state='queued' ORDER BY created,id LIMIT 1").fetchone()
            if not row:
                db.commit()
                return {'state': 'idle'}
            identifier, url = row
            db.execute("UPDATE jobs SET state='running' WHERE id=?", (identifier,))
            db.commit()
            reports = root / 'reports'
            reports.mkdir(mode=0o700, exist_ok=True)
            prefix = reports / identifier
            try:
                allowed_url(root, url)  # Recheck in case the host was removed after submission.
                result = runner([sys.executable, str(Path(__file__).with_name('link_auditor.py').resolve()), url,
                    '--max-pages', '50', '--max-urls', '200', '--output', str(prefix)],
                    stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                    timeout=120, check=False, preexec_fn=child_limits,
                    env={'PATH': '/usr/bin:/bin', 'LANG': 'C.UTF-8', 'PYTHONUNBUFFERED': '1'})
                if result.returncode in (0, 1) and prefix.with_suffix('.json').is_file() and prefix.with_suffix('.html').is_file():
                    state, detail = 'completed', 'Report available; inspect findings and limits'
                else:
                    state, detail = 'failed', 'Worker exit ' + str(result.returncode) + '; no automatic retry'
            except subprocess.TimeoutExpired:
                state, detail = 'timed_out', '120-second process deadline reached; no complete report promised'
            except (ValueError, OSError, json.JSONDecodeError):
                state, detail = 'failed', 'Configuration or process error; no automatic retry'
            db.execute('UPDATE jobs SET state=?,detail=? WHERE id=?', (state, detail, identifier))
            db.commit()
            return {'id': identifier, 'state': state, 'detail': detail}


def main():
    os.umask(0o077)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path.home() / 'openvist/tools/link-auditor-state')
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('init')
    submit_parser = sub.add_parser('submit')
    submit_parser.add_argument('url')
    sub.add_parser('work')
    sub.add_parser('status')
    args = parser.parse_args()
    try:
        if args.command == 'init':
            with database(args.root) as (root, db):
                config = root / 'allowed-hosts.json'
                if not config.exists():
                    with config.open('x') as output:
                        json.dump(['openvist.com'], output)
                print('Private pilot initialized; allowed starting host: see', config)
        elif args.command == 'submit':
            print('Queued:', submit(args.root, args.url))
        elif args.command == 'work':
            print(json.dumps(process_one(args.root)))
        else:
            with database(args.root) as (root, db):
                for identifier, url, created, state, detail in db.execute('SELECT id,url,created,state,detail FROM jobs ORDER BY created DESC LIMIT 20'):
                    print(json.dumps({'id':identifier, 'url':url, 'submitted_at':datetime.fromtimestamp(created, timezone.utc).isoformat(), 'state':state, 'detail':detail}))
    except (ValueError, OSError, sqlite3.Error) as error:
        parser.exit(2, str(error) + '\n')


if __name__ == '__main__':
    main()
