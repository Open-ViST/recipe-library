from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from zipfile import ZipFile
sys.path.insert(0,str(Path(__file__).parents[1]))
from build_self_hosted import build,FILES,PREFIX
from run_audit import main as launch
from link_auditor import main


class SelfHostedTests(unittest.TestCase):
    def test_launcher_forwards_limits_without_shell(self):
        def runner(command,**kwargs):
            self.assertEqual(kwargs,{'timeout':600,'check':False})
            self.assertTrue(command[1].endswith('link_auditor.py'))
            self.assertEqual(command[2:],['https://example.com/','--max-pages','200'])
            return subprocess.CompletedProcess(command,1)
        self.assertEqual(launch(['--deadline','600','--','https://example.com/','--max-pages','200'],runner),1)

    def test_deadline_returns_124(self):
        def runner(*a,**k):raise subprocess.TimeoutExpired(a[0],1)
        self.assertEqual(launch(['--deadline','1','--','https://example.com/'],runner),124)

    def test_settings_reach_transport_and_report(self):
        class Audit:
            def __init__(self,*args,network):
                self.network=network
            def run(self,sitemap):
                self_report={'started_from':'https://example.com/','generated_at':'fixture','results':[],'summary':{},'scope':{},'limits_reached':False}
                return self_report
        with tempfile.TemporaryDirectory() as folder,patch('link_auditor.Auditor',Audit):
            prefix=str(Path(folder)/'report')
            self.assertEqual(main(['https://example.com/','--delay','1','--request-timeout','15','--byte-limit','2000000','--output',prefix]),0)
            import json
            scope=json.loads(Path(prefix+'.json').read_text())['scope']
            self.assertEqual(scope,{'delay':1.0,'request_timeout':15.0,'byte_limit':2000000})

    def test_nonfinite_settings_rejected_before_requests(self):
        with patch('link_auditor.Auditor',side_effect=AssertionError('Network must not start')):
            for args in [['--delay','nan'],['--delay','-1'],['--request-timeout','inf'],['--byte-limit','0']]:
                with self.subTest(args=args),self.assertRaises(SystemExit) as stopped:main(['https://example.com/',*args])
                self.assertEqual(stopped.exception.code,2)

    def test_download_is_reproducible_and_has_no_bridge_or_secrets(self):
        with tempfile.TemporaryDirectory() as folder:
            a=build(Path(folder)/'a.zip');b=build(Path(folder)/'b.zip')
            self.assertEqual(a.read_bytes(),b.read_bytes())
            with ZipFile(a) as z:
                self.assertEqual(set(z.namelist()),{PREFIX+'/'+f for f in FILES})
                self.assertIsNone(z.testzip())
                self.assertTrue(all('config' not in n and 'bridge_worker' not in n for n in z.namelist()))


if __name__=='__main__':unittest.main()
