"""One-shot checkpoint and exact-clock observation export contracts; no native client."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import json,re,unittest
from .continuation import read_research_export
from .checkpoint import save_inactive_boundary,checkpoint_name
from .transport import MissingAcknowledgment

class ExportTests(unittest.TestCase):
 def setUp(self):
  self.tmp=TemporaryDirectory(dir=Path.cwd());self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
  self.data=dict(turn=124,history=[dict(turn=123,player=1)],completions=[],defeats=[],errors=[],duplicate_callbacks=0)
 def put(self,name,data): (self.root/name).write_text(json.dumps(data),encoding='utf-8')
 def test_preservation_filename_is_a_valid_current_export(self):
  self.put('failure-preserved-research.json',self.data)
  data,path=read_research_export(self.root,turn=124);self.assertEqual(data,self.data);self.assertEqual(path.name,'failure-preserved-research.json')
 def test_stale_latest_does_not_override_current_preservation(self):
  self.put('research-latest.json',dict(self.data,turn=123));self.put('failure-preserved-research.json',self.data)
  self.assertEqual(read_research_export(self.root,turn=124)[0],self.data)
 def test_conflicting_same_turn_rejected(self):
  self.put('research-latest.json',dict(self.data,errors=['lost prefix']));self.put('failure-preserved-research.json',self.data)
  with self.assertRaisesRegex(AssertionError,'Conflicting'):read_research_export(self.root,turn=124)
 def test_duplicate_observations_rejected(self):
  self.put('failure-preserved-research.json',dict(self.data,history=self.data['history']*2))
  with self.assertRaisesRegex(AssertionError,'Duplicate'):read_research_export(self.root,turn=124)
 def test_missing_turn_is_not_inferred(self):
  self.put('research-latest.json',dict(self.data,turn=123))
  with self.assertRaises(FileNotFoundError):read_research_export(self.root,turn=124)

class CheckpointTests(unittest.TestCase):
 def fixture(self,*,missing_ack=False,phase_change=False):
  self.tmp=TemporaryDirectory(dir=Path.cwd());self.addCleanup(self.tmp.cleanup);root=Path(self.tmp.name)
  class Runner:
   game_pid=123;requests=0;reads=0
   def ready(self,*args):pass
   def state_read(self,label):
    self.reads+=1
    return dict(turn=125 if phase_change and self.reads>1 else 124,active=False,remaining=0,local_player=0,player0_human=True)
   def cmd(self,code,state,label):
    if label.startswith('save-exact-boundary'):
     self.requests+=1;self.name=json.loads(re.search(r'CSC_EXACT_CHECKPOINT_SAVE=\{name=("[^"]+")',code)[1]);(root/(self.name+'.Civ6Save')).write_bytes(b'CIV6'+b'0'*100010)
     if missing_ack:raise MissingAcknowledgment('fixture delayed ack','')
    return 'CSC_EXACT_CHECKPOINT_COMPLETE '+self.name+' true'
  return Runner(),root
 def save(self,r,root):
  with patch('full_game_controller.checkpoint.time.sleep'):
   return save_inactive_boundary(r,turn=124,name='unique',native_directory=root,archive=root/'archive.Civ6Save')
 def test_supported_checkpoint_is_one_request_and_equal_archive(self):
  r,root=self.fixture();report=self.save(r,root)
  self.assertTrue(report['verified']);self.assertEqual(r.requests,1);self.assertTrue(report['save_complete_event'])
 def test_missing_ack_uses_save_receipt_and_never_resends(self):
  r,root=self.fixture(missing_ack=True);report=self.save(r,root)
  self.assertFalse(report['initial_ack']);self.assertEqual(r.requests,1)
 def test_phase_movement_rejected_after_save(self):
  r,root=self.fixture(phase_change=True)
  with self.assertRaises(AssertionError):self.save(r,root)
  self.assertEqual(r.requests,1)
 def test_existing_checkpoint_never_overwritten(self):
  r,root=self.fixture();native=root/(checkpoint_name('unique',root/'archive.Civ6Save')+'.Civ6Save');native.write_bytes(b'preserve')
  with self.assertRaisesRegex(AssertionError,'Never overwrite'):self.save(r,root)
  self.assertEqual(r.requests,0);self.assertEqual(native.read_bytes(),b'preserve')

 def test_legacy_name_collision_is_preserved_and_new_boundary_saved_once(self):
  r,root=self.fixture();legacy=root/'unique.Civ6Save';legacy.write_bytes(b'old world')
  report=self.save(r,root)
  self.assertTrue(report['verified']);self.assertEqual(r.requests,1)
  self.assertEqual(legacy.read_bytes(),b'old world')
  self.assertNotEqual(Path(report['native_save']),legacy)
 def test_archive_identity_scopes_name_and_stays_bounded(self):
  a=checkpoint_name('x'*96,Path.cwd()/'run1/turn100.Civ6Save')
  b=checkpoint_name('x'*96,Path.cwd()/'run2/turn100.Civ6Save')
  self.assertNotEqual(a,b);self.assertEqual(len(a),96)
  self.assertEqual(a,checkpoint_name('x'*96,Path.cwd()/'run1/turn100.Civ6Save'))
 def test_existing_archive_blocks_before_any_native_request(self):
  r,root=self.fixture();(root/'archive.Civ6Save').write_bytes(b'preserve archive')
  with self.assertRaisesRegex(AssertionError,'Never overwrite'):self.save(r,root)
  self.assertEqual(r.requests,0)

if __name__=='__main__':unittest.main()
