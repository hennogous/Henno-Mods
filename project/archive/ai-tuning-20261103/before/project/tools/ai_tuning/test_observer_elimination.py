"""Actual controller parsing/abort and failure-only cleanup, without native I/O."""
import json,os,sys,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'project/tools/ai_baseline'),str(ROOT/'project/tools/ai_tuning')]
from full_game_controller import controller as core
import native_profile_test as p
class Guards(unittest.TestCase):
 def reader(self,line):
  obj=object.__new__(core.FullGameController);obj.cmd=lambda *a,**kw:line;return obj
 def test_probe_actually_requests_liveness(self):self.assertIn('Players[0]:IsAlive()',core.HANDOFF)
 def test_native_liveness_is_parsed(self):self.assertIs(self.reader('CSC_SHARED_STATE 175 false 0 -1 false false').state_read('proof')['player0_alive'],False)
 def test_legacy_fixture_without_liveness_is_unknown(self):self.assertNotIn('player0_alive',self.reader('CSC_SHARED_STATE 150 false 0 0 true').state_read('proof'))
 def test_live_player_is_parsed(self):self.assertIs(self.reader('CSC_SHARED_STATE 150 false 0 0 true true').state_read('proof')['player0_alive'],True)
 def test_ready_fails_immediately_for_dead_observer(self):
  obj=self.reader('CSC_SHARED_STATE 175 false 0 -1 false false')
  with self.assertRaises(core.ObserverEliminated):obj.ready(175,'proof')
 def test_active_wait_aborts_before_another_control(self):
  obj=self.reader('CSC_SHARED_STATE 174 true 1 -1 false false');obj.root=Path(__file__).parent
  with patch.object(core.time,'sleep'),self.assertRaises(core.ObserverEliminated):obj._await_target(175)
class Cleanup(unittest.TestCase):
 def run_cleanup(self,receipt_failure=False,wrong_identity=False):
  with tempfile.TemporaryDirectory(dir=os.environ.get('CSC_TEST_SCRATCH'))as name:
   out=Path(name);p.write(out/'game-process.json',dict(pid=42,created='old'));calls=[]
   sequence=iter([[dict(pid=42,created='wrong'if wrong_identity else'old')],[]])
   c=SimpleNamespace(d=SimpleNamespace(processes=lambda:next(sequence)))
   def cmd(code,context,label,**kw):
    calls.append(label)
    if label=='observer-terminal-economic-journal':
     if receipt_failure:raise RuntimeError('fixture unavailable journal')
     return 'CSC_PROFILE_RECEIPTS={"turn":175,"totals":{"cost":900}}'
    return ''
   r=SimpleNamespace(game_pid=42,state_read=lambda label:dict(player0_alive=False,turn=175),cmd=cmd,wait=lambda *a:calls.append('wait-menu'))
   with patch.object(p,'restore_preferences',lambda *a:calls.append('preferences')),patch.object(p,'restore_package',lambda *a:calls.append('package')):
    if wrong_identity:
     with self.assertRaises(AssertionError):p.close_eliminated_observer(c,r,out)
     self.assertEqual(calls,[]);return
    p.close_eliminated_observer(c,r,out)
   self.assertTrue((out/'observer-elimination-cleanup.json').exists());self.assertFalse((out/'job-status.json').exists())
   self.assertEqual(calls.count('observer-eliminated-supported-menu'),1);self.assertEqual(calls.count('observer-eliminated-supported-exit'),1)
   self.assertLess(calls.index('observer-terminal-economic-journal'),calls.index('observer-eliminated-supported-menu'))
   self.assertTrue((out/('observer-terminal-receipt-warning.json'if receipt_failure else'observer-terminal-receipts.json')).exists())
 def test_preserves_journal_then_one_normal_exit(self):self.run_cleanup()
 def test_missing_journal_does_not_leave_engine_running(self):self.run_cleanup(receipt_failure=True)
 def test_reused_native_pid_blocks_commands(self):self.run_cleanup(wrong_identity=True)
if __name__=='__main__':unittest.main()
