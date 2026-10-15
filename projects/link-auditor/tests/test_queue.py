from pathlib import Path
import subprocess
import tempfile
import fcntl
import unittest
from unittest.mock import patch
import sys
sys.path.insert(0, str(Path(__file__).parents[1]))
from audit_queue import database, submit, process_one
from link_auditor import Auditor, Response, html_report


class QueueTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / 'allowed-hosts.json').write_text('["openvist.com"]')

    def tearDown(self):
        self.temp.cleanup()

    def test_allowlist_and_scheme(self):
        for url in ['https://other.example/', 'http://openvist.com/', 'https://openvist.com:444/', 'https://openvist.com/?secret=x']:
            with self.assertRaises(ValueError):
                submit(self.root, url)

    def test_pending_and_cooldown(self):
        identifier = submit(self.root, 'https://openvist.com/', now=1000)
        with self.assertRaises(ValueError):
            submit(self.root, 'https://openvist.com/', now=3000)
        with database(self.root) as (_, db):
            db.execute("UPDATE jobs SET state='completed'");db.commit()
        with self.assertRaises(ValueError):
            submit(self.root, 'https://openvist.com/', now=1001)
        self.assertNotEqual(identifier, submit(self.root, 'https://openvist.com/', now=3000))

    def test_timeout_no_retry(self):
        submit(self.root, 'https://openvist.com/')
        def timeout(command, **kwargs):
            self.assertEqual(kwargs['timeout'], 120)
            self.assertIn('--max-pages', command)
            raise subprocess.TimeoutExpired(command, 120)
        self.assertEqual(process_one(self.root, timeout)['state'], 'timed_out')
        self.assertEqual(process_one(self.root, timeout)['state'], 'idle')

    def test_success_and_incomplete_failure(self):
        submit(self.root, 'https://openvist.com/')
        def success(command, **kwargs):
            prefix = Path(command[-1])
            prefix.with_suffix('.json').write_text('{}')
            prefix.with_suffix('.html').write_text('report')
            return subprocess.CompletedProcess(command, 1)
        self.assertEqual(process_one(self.root, success)['state'], 'completed')
        with database(self.root) as (_, db):
            db.execute('DELETE FROM jobs');db.commit()
        submit(self.root, 'https://openvist.com/')
        self.assertEqual(process_one(self.root, lambda *a, **k: subprocess.CompletedProcess(a, 0))['state'], 'failed')

    def test_removed_host_not_executed(self):
        submit(self.root, 'https://openvist.com/')
        (self.root / 'allowed-hosts.json').write_text('[]')
        with patch('subprocess.run', side_effect=AssertionError('No execution')):
            self.assertEqual(process_one(self.root)['state'], 'failed')

    def test_crashed_job_not_retried(self):
        submit(self.root, 'https://openvist.com/')
        with database(self.root) as (_, db):
            db.execute("UPDATE jobs SET state='running'");db.commit()
        self.assertEqual(process_one(self.root)['state'], 'idle')
        with database(self.root) as (_, db):
            self.assertEqual(db.execute('SELECT state FROM jobs').fetchone()[0], 'interrupted')

    def test_worker_lock_prevents_second_worker(self):
        submit(self.root, 'https://openvist.com/')
        with (self.root / 'worker.lock').open('a') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.assertEqual(process_one(self.root)['state'], 'busy')

    def test_storage_limit_stops_new_jobs(self):
        with database(self.root) as (_, db):
            db.executemany('INSERT INTO jobs(id,url,host,created,state) VALUES(?,?,?,?,?)',
                [(str(i), 'https://openvist.com/', 'openvist.com', 0, 'completed') for i in range(100)])
            db.commit()
        with self.assertRaisesRegex(ValueError, '100 jobs'):
            submit(self.root, 'https://openvist.com/')


if __name__ == '__main__':
    unittest.main()
