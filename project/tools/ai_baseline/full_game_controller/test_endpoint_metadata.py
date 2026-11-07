import unittest
from types import SimpleNamespace,MethodType
from pathlib import Path
from unittest.mock import patch
from full_game_controller.controller import FullGameController
class EndpointMetadata(unittest.TestCase):
 def run_endpoint(self,configured,interval=None):
  writes=[];ready=[]
  row=dict(turn=19,active=False,remaining=0,local_player=0,player0_human=True)
  r=SimpleNamespace(root=Path(__file__).parent/'nonexistent-native-test-root',diagnostics=SimpleNamespace(write=lambda p,v:writes.append((p,v))),state_read=lambda label:dict(row),continue_after_victory=lambda target,state:False,boundary_decision=lambda turn,target,n:('done',n+1),ready=lambda target,label:ready.append(target))
  r._metadata=MethodType(FullGameController._metadata,r)
  if configured is not None:r.study_endpoint=configured
  if interval is not None:r.autoplay_interval_seconds=interval
  with patch('full_game_controller.controller.time.sleep',return_value=None),patch('full_game_controller.controller.time.monotonic',side_effect=[0,0,1900,1900]):FullGameController._await_target(r,19)
  self.assertEqual(ready,[19]);self.assertEqual(r.last_interval_turn,19);return writes[0][1]
 def test_configured_endpoint_reaches_actual_status_consumer(self):self.assertEqual(self.run_endpoint(75,3600)['endpoint'],75)
 def test_legacy_callers_keep_default_endpoint(self):self.assertEqual(self.run_endpoint(None,3600)['endpoint'],250)
 def test_legacy_interval_is_still_thirty_minutes(self):
  with self.assertRaisesRegex(TimeoutError,'1800-second'):self.run_endpoint(75)
if __name__=='__main__':unittest.main()
