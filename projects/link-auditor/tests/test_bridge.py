import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).parents[1]))
from bridge_worker import Client, work

ID='a'*32
LEASE='b'*64


class FakeClient:
    def __init__(self):
        self.calls=[]
        self.fail_delivery=False
    def request(self, endpoint, payload=None):
        self.calls.append((endpoint,payload))
        if endpoint=='claim':return {'id':ID,'lease':LEASE,'state':'running','url':'https://openvist.com/','kind':'audit','protocol':2,'trusted_local':True,'proof':'openvist-audit-verification='+'c'*64}
        if self.fail_delivery:raise ValueError('Lost delivery response')
        return {'id':payload['id'],'state':payload['state']}


class BridgeTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
    def tearDown(self):self.temp.cleanup()
    def runner(self, command, **kwargs):
        self.assertEqual(kwargs['timeout'],120)
        Path(command[-1]+'.json').write_text(json.dumps({'started_from':'https://openvist.com/','summary':{'ok':1},'results':[],'limits_reached':False}))
        return subprocess.CompletedProcess(command,1)

    def test_success_delivery_and_receipt(self):
        client=FakeClient()
        self.assertTrue(work(self.root,client,self.runner)['delivered'])
        self.assertEqual([c[0] for c in client.calls],['claim','finish'])
        self.assertTrue((self.root/'bridge-jobs'/ID/'receipt.json').is_file())

    def test_failed_delivery_does_not_rerun_audit(self):
        client=FakeClient();client.fail_delivery=True
        with self.assertRaises(ValueError):work(self.root,client,self.runner)
        client.fail_delivery=False
        def no_run(*a,**k):raise AssertionError('Audit repeated')
        self.assertTrue(work(self.root,client,no_run)['delivered'])
        self.assertEqual([c[0] for c in client.calls],['claim','finish','finish'])

    def test_interrupted_claim_is_not_rerun(self):
        folder=self.root/'bridge-jobs'/ID;folder.mkdir(parents=True)
        (folder/'claim.json').write_text(json.dumps({'id':ID,'lease':LEASE}))
        client=FakeClient()
        def no_run(*a,**k):raise AssertionError('Audit repeated')
        self.assertEqual(work(self.root,client,no_run)['state'],'failed')
        self.assertEqual(client.calls[0][0],'finish')

    def test_claim_cannot_change_destination(self):
        class BadClient:
            def request(self,*a):return {'id':ID,'lease':LEASE,'url':'http://127.0.0.1/'}
        with self.assertRaises(ValueError):work(self.root,BadClient())

    def test_timeout_reported(self):
        def timeout(*a,**k):raise subprocess.TimeoutExpired(a[0],120)
        self.assertEqual(work(self.root,FakeClient(),timeout)['state'],'timed_out')

    def test_credentials_private_and_fixed_origin(self):
        path=self.root/'config.json';path.write_text(json.dumps({'base_url':'https://openvist.com','username':'user','application_password':'test-only'}));path.chmod(0o600)
        self.assertIsInstance(Client(path),Client)
        path.chmod(0o644)
        with self.assertRaises(ValueError):Client(path)
        path.chmod(0o600);path.write_text(json.dumps({'base_url':'https://other.example','username':'user','application_password':'test-only'}))
        with self.assertRaises(ValueError):Client(path)


if __name__=='__main__':unittest.main()
