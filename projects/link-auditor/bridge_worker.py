#!/usr/bin/env python3
"""Account-based outbound-only WordPress bridge. Never prints authentication material."""
import argparse
import base64
import fcntl
import json
import os
from pathlib import Path
import re
import stat
import shutil
import time
import subprocess
import sys
import urllib.error
import urllib.request

from audit_queue import child_limits
from domain_proof import owned_origin


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


class Client:
    def __init__(self, config_path):
        path = Path(config_path).expanduser()
        if not stat.S_ISREG(path.stat().st_mode) or path.stat().st_mode & 0o077:
            raise ValueError('WordPress config must be a regular private file (chmod 600)')
        if path.stat().st_size > 65536:
            raise ValueError('Config too large')
        config = json.loads(path.read_text())
        if config.get('base_url', '').rstrip('/') != 'https://openvist.com':
            raise ValueError('Bridge requires the existing https://openvist.com WordPress config')
        user, password = config.get('username'), config.get('application_password')
        if not isinstance(user, str) or not isinstance(password, str) or not user or not password or ':' in user:
            raise ValueError('Missing WordPress application credentials')
        self.auth = 'Basic ' + base64.b64encode((user + ':' + password).encode()).decode()
        self.opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())

    def request(self, endpoint, payload=None):
        if endpoint not in ('health', 'claim', 'finish'):
            raise ValueError('Unexpected endpoint')
        body = None if payload is None else json.dumps(payload, separators=(',', ':')).encode()
        if body and len(body) > 2200000:
            raise ValueError('Delivery payload too large')
        request = urllib.request.Request('https://openvist.com/wp-json/openvist-link-auditor/v1/' + endpoint,
            data=body, method='GET' if payload is None else 'POST',
            headers={'Authorization': self.auth, 'Content-Type': 'application/json', 'User-Agent': 'OpenViST-Link-Auditor-Bridge/0.1'})
        try:
            with self.opener.open(request, timeout=20) as response:
                raw = response.read(2200001)
                if len(raw) > 2200000:
                    raise ValueError('Bridge response too large')
                return json.loads(raw)
        except urllib.error.HTTPError as error:
            if endpoint == 'finish' and error.code == 410:
                return {'id': payload['id'], 'state': payload['state'], 'discarded': True}
            raise ValueError('WordPress bridge HTTP ' + str(error.code) + '; no credentials or response body logged') from None


def atomic_json(path, data):
    temporary = path.with_suffix('.new')
    with temporary.open('x') as output:
        json.dump(data, output)
        output.flush()
        os.fsync(output.fileno())
    temporary.replace(path)


def deliver(client, folder):
    payload = json.loads((folder / 'result.json').read_text())
    response = client.request('finish', payload)
    if response.get('id') != payload['id'] or response.get('state') != payload['state']:
        raise ValueError('Unexpected receipt; delivery kept for reconciliation')
    atomic_json(folder / 'receipt.json', {'id': payload['id'], 'state': payload['state']})
    return {'id': payload['id'], 'state': payload['state'], 'delivered': True}


def work(root, client, runner=subprocess.run):
    root = Path(root).expanduser().resolve()
    root.mkdir(mode=0o700, parents=True, exist_ok=True)
    root.chmod(0o700)
    with (root / 'worker.lock').open('a') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return {'state': 'busy'}
        jobs = root / 'bridge-jobs'
        jobs.mkdir(mode=0o700, exist_ok=True)
        for folder in sorted(jobs.iterdir()):
            if folder.is_dir() and not folder.is_symlink() and re.fullmatch('[a-f0-9]{32}',folder.name) and time.time()-folder.stat().st_mtime>86400:
                shutil.rmtree(folder)
                continue
            if not folder.is_dir():
                continue
            if (folder / 'result.json').exists() and not (folder / 'receipt.json').exists():
                return deliver(client, folder)
            if (folder / 'claim.json').exists() and not (folder / 'result.json').exists():
                # Worker died before persisting a result. Never repeat those network requests.
                claim = json.loads((folder / 'claim.json').read_text())
                atomic_json(folder / 'result.json', {'id': claim['id'], 'lease': claim['lease'], 'state': 'failed', 'report': None})
                return deliver(client, folder)
        if len(list(jobs.iterdir())) >= 100:
            raise ValueError('Bridge reached its 100-job local storage cap; archive before continuing')
        claim = client.request('claim', {'protocol': 2})
        if claim.get('state') in ('idle', 'busy'):
            return {'state': claim['state']}
        identifier, lease = claim.get('id'), claim.get('lease')
        if not isinstance(identifier, str) or not re.fullmatch('[a-f0-9]{32}', identifier) or not isinstance(lease, str) or not re.fullmatch('[a-f0-9]{64}', lease) or claim.get('protocol') != 2 or claim.get('kind') not in ('audit','verify'):
            raise ValueError('Invalid claim; refused to execute')
        target = owned_origin(claim.get('url'))
        proof = claim.get('proof')
        if not isinstance(proof,str) or not re.fullmatch(r'openvist-audit-verification=[a-f0-9]{64}',proof):
            raise ValueError('Invalid proof format')
        trusted = claim.get('trusted_local') is True and target == 'https://openvist.com/'
        folder = jobs / identifier
        folder.mkdir(mode=0o700)  # Existing work is never overwritten or rerun.
        atomic_json(folder / 'claim.json', claim)
        prefix = folder / 'audit'
        report = None
        try:
            options = dict(stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                check=False, preexec_fn=child_limits,
                env={'PATH':'/usr/bin:/bin','LANG':'C.UTF-8','PYTHONUNBUFFERED':'1'})
            verified = trusted or runner([sys.executable,str(Path(__file__).with_name('domain_proof.py').resolve()),target,proof],timeout=15,**options).returncode==0
            if claim['kind']=='verify':
                state,report='completed',{'verified':verified}
            elif not verified:
                state='failed'
            else:
                result=runner([sys.executable,str(Path(__file__).with_name('link_auditor.py').resolve()),
                    target,'--max-pages','50','--max-urls','200','--output',str(prefix)],timeout=120,**options)
                report_file=prefix.with_suffix('.json')
                if result.returncode in (0,1) and report_file.is_file() and report_file.stat().st_size<=2097152:
                    report=json.loads(report_file.read_text())
                    state='completed'
                else:
                    state='failed'
        except subprocess.TimeoutExpired:
            state='timed_out'
        except (ValueError,OSError):
            state='failed'
        atomic_json(folder / 'result.json', {'id': identifier, 'lease': lease, 'state': state, 'report': report})
        return deliver(client, folder)


def main():
    os.umask(0o077)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=Path.home() / 'openvist/recipes/config/wordpress.json')
    parser.add_argument('--root', type=Path, default=Path.home() / 'openvist/tools/link-auditor-state')
    parser.add_argument('command', choices=['check', 'work'])
    args = parser.parse_args()
    try:
        client = Client(args.config)
        if args.command == 'check':
            response = client.request('health')
            if response.get('state') != 'ready' or response.get('protocol') != 2:
                raise ValueError('Bridge not ready')
            print('WORDPRESS BRIDGE PROTOCOL 2 AUTHENTICATION OK; no audit submitted or claimed')
        else:
            print(json.dumps(work(args.root, client)))
    except (ValueError, OSError, urllib.error.URLError):
        print('BRIDGE STOPPED: check plugin activation, administrator permission, private config and connectivity. No audit was automatically repeated.', file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
