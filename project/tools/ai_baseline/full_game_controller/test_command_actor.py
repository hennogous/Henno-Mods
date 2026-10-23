from pathlib import Path
from unittest.mock import patch
import json,unittest
from .command_actor import probe_command_actor

class Fake:
 def __init__(self,sync=99,fail=False,move=False):
  self.root=Path('unused');self.sync=sync;self.fail=fail;self.move=move;self.actor=0;self.observer=0;self.calls=[];self.queries=0;self.ready_called=False
 def ready(self,*a):self.ready_called=True
 def cmd(self,code,state,label):
  self.calls.append((label,code))
  assert 'RequestCommand('not in code and 'SetPlotOwner'not in code and 'ChangeGoldBalance'not in code and 'AutoplayManager.Set'not in code
  if label=='actor-switch-once':
   self.actor=1;self.observer=1;return 'OK'
  if label=='actor-restore-once':
   self.actor=0;self.observer=0;return 'OK'
  if state=='GameCore_Tuner':
   turn=132 if self.move and label.startswith('actor-current')else 131
   if self.move and label=='actor-after-restore':turn=132
   flags=','.join('1'if i==self.actor else'0'for i in range(6))
   return f'CSC_ACTOR_CORE {turn} false {self.actor} {self.observer} {flags}'
  self.queries+=1
  if self.fail:raise OSError('fixture readonly query interrupted')
  sync=self.queries>=self.sync
  return 'CSC_ACTOR_UI='+json.dumps(dict(turn=131,local_player=1 if sync else 0,actor_human=True,gold=100,rows=[dict(plot=42,price=30,normal=sync)]))

class ActorTests(unittest.TestCase):
 def run_case(self,r,**kw):
  self.writes=[]
  with patch('full_game_controller.command_actor.time.sleep')as sleep:
   out=probe_command_actor(r,turn=131,player=1,city=65536,decode=lambda raw,key:json.loads(raw.split('=',1)[1]),write=lambda p,v:self.writes.append((p,dict(v))),allow_unsafe_diagnostic=True,**kw)
  return out,sleep
 def test_rejected_route_is_disabled_by_default(self):
  r=Fake()
  with self.assertRaisesRegex(AssertionError,'Rejected role-switch'):
   probe_command_actor(r,turn=131,player=1,city=65536,decode=None,write=None)
  self.assertFalse(r.calls)
 def test_delayed_UI_binding_is_observed_before_restore(self):
  r=Fake(sync=3);out,sleep=self.run_case(r)
  self.assertTrue(out['permission_observed']);self.assertTrue(out['roles_restored']);self.assertEqual(r.queries,3);self.assertEqual(sleep.call_count,2)
  self.assertEqual(out['switch_requests'],1);self.assertEqual(out['restore_requests'],1)
 def test_no_UI_binding_is_bounded_and_never_purchase(self):
  r=Fake();out,sleep=self.run_case(r)
  self.assertFalse(out['permission_observed']);self.assertEqual(r.queries,5);self.assertEqual(out['purchase_requests'],0);self.assertTrue(r.ready_called)
 def test_query_failure_restores_and_preserves_original_error(self):
  r=Fake(fail=True)
  with self.assertRaisesRegex(OSError,'interrupted'):self.run_case(r)
  self.assertEqual(r.actor,0);self.assertEqual(len([x for x in r.calls if x[0]=='actor-switch-once']),1);self.assertEqual(len([x for x in r.calls if x[0]=='actor-restore-once']),1)
 def test_native_clock_movement_restores_and_blocks(self):
  r=Fake(move=True)
  with self.assertRaisesRegex(AssertionError,'clock moved'):self.run_case(r)
  self.assertEqual(r.actor,0);self.assertEqual(r.queries,0)
 def test_wrong_start_role_blocks_before_switch(self):
  r=Fake();r.actor=2
  with self.assertRaises(AssertionError):self.run_case(r)
  self.assertFalse(any(x[0]=='actor-switch-once'for x in r.calls))

if __name__=='__main__':unittest.main()
