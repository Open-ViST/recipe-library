import copy
import hashlib
import importlib.util
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('exporter', Path(__file__).parents[1]/'tools/export_library.py')
exporter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(exporter)


class ExportTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        (self.root/'LICENSE').write_text('MIT test license\n')
        code = 'print("example")\n'
        self.item = {'record': {'slug':'example-task', 'version':'0.1.0',
            'language':'python','license':'MIT','title':'Example','goal':'Example task',
            'tested_scope':'One recorded case','sources':[], 'usage':'python3 example.py'},
            'url':'https://openvist.com/recipes/example-task/', 'code':code,
            'code_sha256':hashlib.sha256(code.encode()).hexdigest(), 'record_sha256':'0'*64}

    def snapshot(self, items=None):
        return {'schema':'openvist.recipe-catalogue.v1', 'recipes':items or [self.item]}

    def test_exact_code_and_idempotent_export(self):
        rows = exporter.export(self.snapshot(), self.root)
        before = {str(p.relative_to(self.root)):p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        self.assertEqual((self.root/rows[0]['code']).read_text(), self.item['code'])
        exporter.export(self.snapshot(), self.root)
        self.assertEqual(before, {str(p.relative_to(self.root)):p.read_bytes() for p in self.root.rglob('*') if p.is_file()})

    def test_hash_mismatch_writes_nothing(self):
        self.item['code'] += '# changed\n'
        with self.assertRaises(ValueError): exporter.export(self.snapshot(), self.root)
        self.assertEqual([p.name for p in self.root.iterdir()], ['LICENSE'])

    def test_existing_version_cannot_change(self):
        exporter.export(self.snapshot(), self.root)
        self.item['record']['goal'] = 'Changed documentation'
        with self.assertRaises(ValueError): exporter.export(self.snapshot(), self.root)

    def test_invalid_identity_license_and_duplicate(self):
        for field,value in [('slug','../../escape'),('license','proprietary'),('version','../1')]:
            with self.subTest(field=field):
                item=copy.deepcopy(self.item);item['record'][field]=value
                with self.assertRaises(ValueError): exporter.export(self.snapshot([item]), self.root)
        with self.assertRaises(ValueError): exporter.export(self.snapshot([self.item,self.item]), self.root)

    def test_empty_and_wrong_schema_fail_closed(self):
        for snapshot in [{'schema':'wrong','recipes':[self.item]}, {'schema':'openvist.recipe-catalogue.v1','recipes':[]}]:
            with self.assertRaises(ValueError): exporter.export(snapshot,self.root)

    def test_parent_symlink_is_rejected(self):
        outside = self.root/'outside';outside.mkdir()
        (self.root/'recipes').symlink_to(outside,target_is_directory=True)
        with self.assertRaises(ValueError): exporter.export(self.snapshot(),self.root)
        self.assertEqual(list(outside.iterdir()),[])

    def test_upstream_notice_is_preserved(self):
        self.item['record']['provenance']={'license':'MIT','license_notice':'Copyright Original Author\nMIT notice', 'url':'https://example.com/source','commit':'a'*40}
        rows=exporter.export(self.snapshot(),self.root)
        folder=(self.root/rows[0]['code']).parent
        self.assertIn('Copyright Original Author',(folder/'UPSTREAM-NOTICE.txt').read_text())


if __name__ == '__main__': unittest.main()
