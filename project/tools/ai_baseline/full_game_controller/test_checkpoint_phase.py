"""Observed asynchronous save boundary plus invalid/active context controls."""
import unittest
from full_game_controller.checkpoint import validate_ui_save_phase
class UIPhase(unittest.TestCase):
 def setUp(self):
  self.core=dict(turn=125,active=False,local_player=0,player0_human=True)
  self.ui=dict(self.core,player0_alive=True)
 def test_matching_clocks(self):self.assertEqual(validate_ui_save_phase(self.core,self.ui),0)
 def test_observed_UI_one_turn_behind(self):self.ui['turn']=124;self.assertEqual(validate_ui_save_phase(self.core,self.ui),1)
 def test_older_and_future_UI_rejected(self):
  for t in(123,126):
   with self.subTest(t=t),self.assertRaises(AssertionError):validate_ui_save_phase(self.core,dict(self.ui,turn=t))
 def test_active_Core_rejected(self):
  with self.assertRaises(AssertionError):validate_ui_save_phase(dict(self.core,active=True),self.ui)
 def test_active_UI_rejected(self):
  with self.assertRaises(AssertionError):validate_ui_save_phase(self.core,dict(self.ui,active=True))
 def test_wrong_role_or_dead_return_player_rejected(self):
  for field,value in(('local_player',-1),('player0_human',False),('player0_alive',False)):
   with self.subTest(field=field),self.assertRaises(AssertionError):validate_ui_save_phase(self.core,dict(self.ui,**{field:value}))
if __name__=='__main__':unittest.main()
