"""Portable atomic JSON/optional-metadata tests; fake transport and real Windows locks."""
import ctypes,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from . import controller as control
from . import probe

class Publication(unittest.TestCase):
 scratch=None
 def setUp(self):
  parent=Path(self.scratch or tempfile.gettempdir()).resolve()
  self.temp=tempfile.TemporaryDirectory(prefix='publication-fixture-',dir=parent);self.root=Path(self.temp.name).resolve();self.assertEqual(self.root.parent,parent);self.addCleanup(self.temp.cleanup)
  self.target=self.root/'required.json';self.target.write_text('{"old":true}',encoding='utf-8')
 def leftovers(self):return list(self.root.glob('.*.tmp'))
 def test_transient_replace_locks_retry_then_publish_atomically(self):
  original=Path.replace;attempts=[]
  def replace(source,target):
   attempts.append(source)
   if len(attempts)<3:
    self.assertEqual(json.loads(self.target.read_text()),{'old':True});raise PermissionError('injected sharing lock')
   return original(source,target)
  with patch.object(Path,'replace',replace),patch.object(probe.time,'sleep')as sleep:probe.write_json(self.target,{'new':2})
  self.assertEqual(len(attempts),3);self.assertEqual(sleep.call_count,2);self.assertEqual(json.loads(self.target.read_text()),{'new':2});self.assertEqual(self.leftovers(),[])
 def test_persistent_required_lock_raises_bound_preserves_original_and_cleans(self):
  with patch.object(Path,'replace',side_effect=PermissionError('locked'))as replace,patch.object(probe.time,'sleep')as sleep:
   with self.assertRaises(PermissionError):probe.write_json(self.target,{'new':2})
  self.assertEqual(replace.call_count,5);self.assertEqual(sleep.call_count,4);self.assertEqual(json.loads(self.target.read_text()),{'old':True});self.assertEqual(self.leftovers(),[])
 def test_unique_temp_names_preserve_other_publishers_legacy_temp(self):
  sentinel=self.root/'required.json.tmp';sentinel.write_text('other owner',encoding='utf-8');names=[];original=Path.replace
  def replace(source,target):names.append(source.name);return original(source,target)
  with patch.object(Path,'replace',replace):
   probe.write_json(self.target,{'a':1});probe.write_json(self.target,{'b':2})
  self.assertEqual(len(set(names)),2);self.assertEqual(sentinel.read_text(),'other owner');self.assertEqual(self.leftovers(),[])
 def test_nonpermission_replace_error_and_serialization_failure_do_not_retry(self):
  with patch.object(Path,'replace',side_effect=OSError('disk failure'))as replace,patch.object(probe.time,'sleep')as sleep:
   with self.assertRaises(OSError):probe.write_json(self.target,{'new':2})
  self.assertEqual(replace.call_count,1);sleep.assert_not_called();self.assertEqual(self.leftovers(),[])
  with patch.object(Path,'replace')as replace:
   with self.assertRaises(TypeError):probe.write_json(self.target,{'bad':object()})
  replace.assert_not_called();self.assertEqual(self.leftovers(),[])
 def real_probe(self):
  user=self.root/'native-user';user.mkdir();(user/'Logs').mkdir();out=self.root/'run';out.mkdir()
  with patch.object(probe,'discover_contexts',lambda required:(4318,{'GameCore_Tuner':1})):runner=probe.make_probe_controller(out,user_root=user)
  runner.last_interval_turn=145;runner.study_endpoint=150;return runner
 def test_real_probe_live_status_persistent_lock_does_not_reactivate_or_lose_journal(self):
  runner=self.real_probe();ready=[];runner.ready=lambda turn,label:ready.append((turn,label));transmissions=[];proofs=iter(('CSC_SHARED_STATE 146 true 4 -1 false true','CSC_SHARED_STATE 150 false 0 0 true true'));original=runner.diagnostics.write;locked=[]
  def write(path,value):
   if path.name=='live-status.json':locked.append(path);raise PermissionError('persistent live reader lock')
   return original(path,value)
  runner.diagnostics.write=write
  def receive(code,*args,**kwargs):transmissions.append(code);return(next(proofs)if code==control.HANDOFF else'CSC_DIAG_AUTOPLAY 145 5 true'),True
  with patch.object(control,'receive_command',receive),patch.object(control.time,'sleep',return_value=None):runner.play(150)
  self.assertEqual(sum('AutoplayManager.SetActive(true)'in code for code in transmissions),1);self.assertEqual(sum(code==control.HANDOFF for code in transmissions),2);self.assertEqual(len(locked),10);self.assertEqual(runner.last_interval_turn,150)
  journal=[json.loads(line)for line in(runner.root/'controller-journal.ndjson').read_text().splitlines()]
  self.assertEqual(sum(x['event']=='command-begin'for x in journal),3);self.assertEqual(sum(x['event']=='command-end'for x in journal),3)
  warnings=[x for x in journal if x['event']=='live-status-metadata-warning'];self.assertEqual(len(warnings),2);self.assertTrue(all(x['no_native_command_replayed']for x in warnings))
  self.assertEqual(len(list((runner.root/'commands').glob('*.lua'))),3);self.assertEqual(len(list((runner.root/'commands').glob('*.txt'))),3);self.assertEqual(ready[-1],(150,'after-150'))
 def test_real_probe_live_status_transient_lock_retries_only_metadata(self):
  runner=self.real_probe();writes=[];original=runner.diagnostics.write
  def write(path,value):
   writes.append(path)
   if len(writes)<3:raise PermissionError('transient metadata lock')
   return original(path,value)
  runner.diagnostics.write=write
  with patch.object(control.time,'sleep',return_value=None):self.assertTrue(runner._metadata(runner.root/'live-status.json',{'turn':150},'live-status-metadata-warning'))
  self.assertEqual(len(writes),3);self.assertEqual(json.loads((runner.root/'live-status.json').read_text()),{'turn':150})
 def test_optional_metadata_does_not_swallow_required_journal_or_other_errors(self):
  runner=self.real_probe();runner.diagnostics.write=lambda *args:(_ for _ in()).throw(OSError('required disk fault'))
  with self.assertRaises(OSError):runner._metadata(runner.root/'live-status.json',{},'live-status-metadata-warning')
  runner.diagnostics.write=lambda *args:(_ for _ in()).throw(PermissionError('lock'));runner.diagnostics.journal=lambda *args,**kw:(_ for _ in()).throw(OSError('journal fault'))
  with patch.object(control.time,'sleep',return_value=None):
   with self.assertRaisesRegex(OSError,'journal fault'):runner._metadata(runner.root/'live-status.json',{},'live-status-metadata-warning')
 def deny_delete(self,path=None):
  from ctypes import wintypes
  kernel=ctypes.WinDLL('kernel32',use_last_error=True);kernel.CreateFileW.argtypes=[wintypes.LPCWSTR,wintypes.DWORD,wintypes.DWORD,wintypes.LPVOID,wintypes.DWORD,wintypes.DWORD,wintypes.HANDLE];kernel.CreateFileW.restype=wintypes.HANDLE;kernel.CloseHandle.argtypes=[wintypes.HANDLE];kernel.CloseHandle.restype=wintypes.BOOL
  handle=kernel.CreateFileW(str(path or self.target),0x80000000,0x1|0x2,None,3,0x80,None)
  if handle==ctypes.c_void_p(-1).value:raise ctypes.WinError(ctypes.get_last_error())
  return kernel,handle
 @unittest.skipUnless(sys.platform=='win32','Requires real Windows deny-delete handle')
 def test_real_Windows_transient_deny_delete_handle_retries_after_release(self):
  kernel,handle=self.deny_delete();held=[handle];failures=[];original=Path.replace
  def replace(source,target):
   try:return original(source,target)
   except PermissionError as error:failures.append(getattr(error,'winerror',None));raise
  def release(delay):
   if held:kernel.CloseHandle(held.pop())
  try:
   with patch.object(Path,'replace',replace),patch.object(probe.time,'sleep',release):probe.write_json(self.target,{'real_lock_released':True})
  finally:
   if held:kernel.CloseHandle(held.pop())
  self.assertEqual(len(failures),1);self.assertIn(failures[0],(5,32));self.assertEqual(json.loads(self.target.read_text()),{'real_lock_released':True});self.assertEqual(self.leftovers(),[])
 @unittest.skipUnless(sys.platform=='win32','Requires real Windows deny-delete handle')
 def test_real_Windows_persistent_deny_delete_raises_and_cleans_unique_temp(self):
  kernel,handle=self.deny_delete()
  try:
   with patch.object(probe.time,'sleep',return_value=None):
    with self.assertRaises(PermissionError):probe.write_json(self.target,{'blocked':True})
   self.assertEqual(self.leftovers(),[])
  finally:kernel.CloseHandle(handle)
  self.assertEqual(json.loads(self.target.read_text()),{'old':True})
 @unittest.skipUnless(sys.platform=='win32','Requires real Windows deny-delete handle')
 def test_real_Windows_live_status_lock_keeps_one_activation_with_bounded_nested_retry(self):
  runner=self.real_probe();live=runner.root/'live-status.json';probe.write_json(live,{'old':True});kernel,handle=self.deny_delete(live);transmissions=[];attempts=[];original=Path.replace
  runner.ready=lambda *args:None
  def replace(source,target):
   if target==live:attempts.append(source)
   return original(source,target)
  def receive(code,*args,**kwargs):transmissions.append(code);return('CSC_SHARED_STATE 150 false 0 0 true true'if code==control.HANDOFF else'CSC_DIAG_AUTOPLAY 145 5 true'),True
  try:
   with patch.object(Path,'replace',replace),patch.object(control,'receive_command',receive),patch.object(control.time,'sleep',return_value=None):runner.play(150)
   self.assertEqual(len(attempts),25);self.assertEqual(sum('AutoplayManager.SetActive(true)'in code for code in transmissions),1);self.assertEqual(sum(code==control.HANDOFF for code in transmissions),1);self.assertEqual(json.loads(live.read_text()),{'old':True});self.assertEqual(list(runner.root.glob('.*.tmp')),[])
   journal=[json.loads(line)for line in(runner.root/'controller-journal.ndjson').read_text().splitlines()]
   self.assertEqual(sum(x['event']=='live-status-metadata-warning'for x in journal),1);self.assertEqual(sum(x['event']=='command-end'for x in journal),2);self.assertEqual(len(list((runner.root/'commands').glob('*.txt'))),2)
  finally:kernel.CloseHandle(handle)
if __name__=='__main__':unittest.main()
