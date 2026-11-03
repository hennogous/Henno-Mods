import json,os,tempfile,time,unittest
from pathlib import Path
from unittest.mock import patch
import session_gc as gc

class GCTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(dir=Path(__file__).parent,prefix='gc-test-')
        self.base=Path(self.tmp.name).resolve()
        assert self.base.parent==Path(__file__).resolve().parent
        self.addCleanup(self.tmp.cleanup)
        self.root=self.base/'sessions';self.root.mkdir()
        self.master=self.base/'master';self.master.mkdir();(self.master/'important').write_text('preserve')
        self.mine=dict(pid=os.getpid(),created=42);self.live={os.getpid():self.mine}
    def identity(self,pid):return self.live.get(pid)
    def clone(self,name='a',lease=None):
        p=self.root/(name*32);p.mkdir();(p/'project').mkdir();(p/'project/db').write_text('disposable')
        if lease is not None:gc.atomic_json(p/gc.LEASE,dict(version=1,session=p.name,owner=lease,worker=None))
        return p
    def collect(self,rows=None,**kwargs):
        return gc.collect(self.root,rows_provider=lambda:rows or[],identity=self.identity,**kwargs)
    def test_active_legacy_and_master_preserved(self):
        active=self.clone();old=self.clone('b')
        report=self.collect([dict(CommandLine=f'python --worker "{active}"')],grace=0)
        self.assertTrue(active.exists());self.assertFalse(old.exists());self.assertEqual(len(report['deleted']),1)
        self.assertEqual((self.master/'important').read_text(),'preserve')
    def test_live_owner_protects_copy_before_worker_launch(self):
        self.live[123]=dict(pid=123,created=9);p=self.clone(lease=self.live[123])
        self.assertFalse(self.collect(grace=0)['deleted']);self.assertTrue(p.exists())
    def test_dead_managed_owner_removed_without_waiting_ten_minutes(self):
        p=self.clone(lease=dict(pid=123,created=9));r=self.collect()
        self.assertEqual(len(r['deleted']),1);self.assertFalse(p.exists())
    def test_pid_reuse_does_not_preserve_abandoned_clone(self):
        p=self.clone(lease=dict(pid=123,created=9));self.live[123]=dict(pid=123,created=10)
        self.assertEqual(len(self.collect()['deleted']),1);self.assertFalse(p.exists())
    def test_live_worker_protected_after_parent_dies(self):
        p=self.clone(lease=dict(pid=123,created=9));lease=gc.read_lease(p)
        lease['worker']=dict(pid=456,created=12);gc.atomic_json(p/gc.LEASE,lease);self.live[456]=lease['worker']
        self.assertFalse(self.collect()['deleted']);self.assertTrue(p.exists())
    def test_recent_legacy_preserved_and_manifest_scope_respected(self):
        a=self.clone();b=self.clone('b');self.assertFalse(self.collect()['deleted'])
        r=self.collect(grace=0,only={a.name});self.assertFalse(a.exists());self.assertTrue(b.exists())
        self.assertEqual(len(r['deleted']),1)
    def test_reparse_and_out_of_root_rejected(self):
        p=self.clone();(p/'bad').mkdir()
        with patch.object(gc,'is_reparse',side_effect=lambda q:Path(q).name=='bad'):
            r=self.collect(grace=0);self.assertTrue(r['errors']);self.assertTrue(p.exists())
        with self.assertRaises(ValueError):gc.checked_tree(self.master,self.root)
    def test_process_inventory_failure_never_deletes(self):
        p=self.clone()
        def fail():raise RuntimeError('inventory unavailable')
        r=gc.collect(self.root,grace=0,rows_provider=fail,identity=self.identity)
        self.assertTrue(r['errors']);self.assertTrue(p.exists())
    def test_unscoped_ghidra_gui_preserves_clones(self):
        p=self.clone();r=self.collect([dict(CommandLine='java ghidra.GhidraRun')],grace=0)
        self.assertFalse(r['deleted']);self.assertTrue(p.exists())
    def test_invalid_lease_and_unknown_owner_access_preserved(self):
        p=self.clone();(p/gc.LEASE).write_text('{broken')
        self.assertTrue(self.collect(grace=0)['errors']);self.assertTrue(p.exists())
        (p/gc.LEASE).unlink();gc.atomic_json(p/gc.LEASE,dict(version=1,session=p.name,owner=dict(pid=123,created=9),worker=None))
        def inaccessible(pid):
            if pid==123:raise PermissionError('unknown owner')
            return self.identity(pid)
        r=gc.collect(self.root,identity=inaccessible,rows_provider=lambda:[])
        self.assertTrue(r['errors']);self.assertTrue(p.exists())

if __name__=='__main__':unittest.main()
