from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).parents[1]))
from domain_proof import owned_origin, verify
from link_auditor import Response
PROOF='openvist-audit-verification='+'a'*64


class DomainTests(unittest.TestCase):
    def test_exact_origin_only(self):
        self.assertEqual(owned_origin('https://example.com'),'https://example.com/')
        for bad in ['https://127.0.0.1/','http://example.com/','https://localhost/','https://example.com:443/','https://example.com/path','https://example.com/?x=1','https://user:pass@example.com/','https://a..example.com/','https://-a.example.com/']:
            with self.subTest(bad=bad),self.assertRaises(ValueError):owned_origin(bad)
    def test_proof_exact_content_and_no_redirect(self):
        class Network:
            def __init__(self,status=200,body=PROOF.encode(),truncated=False):self.status=status;self.body=body;self.truncated=truncated;self.calls=[]
            def get(self,url):self.calls.append(url);return Response(url,self.status,{},self.body,self.truncated)
        network=Network(body=(PROOF+'\n').encode());self.assertTrue(verify('https://example.com/',PROOF,network));self.assertEqual(network.calls,['https://example.com/.well-known/openvist-audit.txt'])
        for network in [Network(302),Network(body=b'wrong'),Network(truncated=True),Network(403)]:self.assertFalse(verify('https://example.com/',PROOF,network))
    def test_proof_format(self):
        with self.assertRaises(ValueError):verify('https://example.com/','anything')


if __name__=='__main__':unittest.main()
