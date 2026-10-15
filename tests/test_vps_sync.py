import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

spec=importlib.util.spec_from_file_location('sync',Path(__file__).parents[1]/'tools/sync_from_vps.py')
sync=importlib.util.module_from_spec(spec);spec.loader.exec_module(sync)


class SyncTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.key=self.root/'key';self.key.write_text('test fixture, not an SSH key');self.key.chmod(0o600)
        self.checkout=self.root/'checkout';self.checkout.mkdir()

    def git_result(self, checkout, *args, **kwargs):
        values={('remote','get-url','origin'):sync.HTTPS_REPO,('branch','--show-current'):'main',('status','--porcelain'):'',('rev-list','--count','origin/main..HEAD'):'0'}
        return subprocess.CompletedProcess(args,0,stdout=values.get(args,''))

    def test_no_changes_does_not_commit_or_push(self):
        with patch.object(sync,'git',side_effect=self.git_result) as git, patch.object(sync.subprocess,'run',return_value=subprocess.CompletedProcess([],0)):
            sync.synchronize(self.checkout,self.key)
        commands=[call.args[1:] for call in git.call_args_list]
        self.assertFalse(any('commit' in command or 'push' in command for command in commands))

    def test_dirty_checkout_stops_before_export(self):
        def result(checkout,*args,**kwargs):
            if args==('status','--porcelain'):return subprocess.CompletedProcess([],0,stdout=' M README.md')
            return self.git_result(checkout,*args,**kwargs)
        with patch.object(sync,'git',side_effect=result),patch.object(sync.subprocess,'run') as run:
            with self.assertRaises(ValueError):sync.synchronize(self.checkout,self.key)
            run.assert_not_called()

    def test_deploy_key_permissions_and_unpublished_commit_stop(self):
        self.key.chmod(0o644)
        with self.assertRaises(ValueError):sync.synchronize(self.checkout,self.key)
        self.key.chmod(0o600)
        def result(checkout,*args,**kwargs):
            if args==('rev-list','--count','origin/main..HEAD'):return subprocess.CompletedProcess([],0,stdout='1')
            return self.git_result(checkout,*args,**kwargs)
        with patch.object(sync,'git',side_effect=result),patch.object(sync.subprocess,'run') as run:
            with self.assertRaises(ValueError):sync.synchronize(self.checkout,self.key)
            run.assert_not_called()


if __name__=='__main__':unittest.main()
