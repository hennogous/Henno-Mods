import copy,unittest
from material_care_audit import completion_gate,funding_gate,terminal_gate
class AuditTests(unittest.TestCase):
 def request(self):
  q=dict(turn=17,player=4,city=65536,quarter='BAKERS',source=2564,plot=2564,price=40,gold=19.1953125,grant=40,own_gold=0,maintenance=0,net_income=7.1,reserve=25,remaining_cap=300,route=[2564,2565],connectors=[])
  v=dict(token='once',status='confirmed',turn=17,spent=40,steps=[dict(owner=4,city=65536,plot=2564)],original_gold=q['gold'],final_gold=q['gold'],donated=40,own_gold_spent=0,native_purchase_command=False)
  return q,v
 def test_prefix_cannot_pass_full_endpoint(self):
  with self.assertRaisesRegex(AssertionError,'Prefix'):completion_gate(dict(status='complete',native_endpoint=225),dict(status='complete',exit_code=0),150,225,True)
 def test_job_or_supervisor_not_complete_cannot_pass(self):
  with self.assertRaisesRegex(AssertionError,'incomplete'):completion_gate(dict(status='running'),dict(status='running'),225,225,True)
  with self.assertRaisesRegex(AssertionError,'Supervisor'):completion_gate(dict(status='complete',native_endpoint=225),dict(status='complete',exit_code=1),225,225,True)
 def test_partial_flag_never_claims_completion(self):self.assertFalse(completion_gate({}, {},150,225,False))
 def test_wallet_already_below_reserve_may_receive_exact_shortfall(self):
  self.assertEqual(funding_gate([self.request()]),dict(tiles=1,cost=40,own=0,fallback=40))
 def test_duplicate_native_token_is_not_another_purchase(self):
  q,v=self.request()
  with self.assertRaisesRegex(AssertionError,'Duplicate'):funding_gate([(q,v),(q,v)])
 def test_bad_treasury_and_native_purchase_label_fail(self):
  q,v=self.request();v['final_gold']-=1
  with self.assertRaisesRegex(AssertionError,'Treasury'):funding_gate([(q,v)])
  q,v=self.request();v['native_purchase_command']=True
  with self.assertRaisesRegex(AssertionError,'mislabeled'):funding_gate([(q,v)])
 def test_two_different_tokens_cannot_spend_twice_same_turn(self):
  q,v=self.request();q2=copy.deepcopy(q);v2=copy.deepcopy(v);v2['token']='twice'
  with self.assertRaisesRegex(AssertionError,'Repeated'):funding_gate([(q,v),(q2,v2)])
 def test_forged_remaining_cap_fails_even_if_price_small(self):
  q,v=self.request();q['remaining_cap']=299
  with self.assertRaisesRegex(AssertionError,'Remaining cap'):funding_gate([(q,v)])
class TerminalTests(unittest.TestCase):
 def proof(self):
  phase=dict(turn=192,active=False,remaining=1,local_player=0,player0_human=True)
  return dict(verified=True,turn=192,observer_alive=False,endgame_visible=True,one_more_turn_disabled=True,winning_team=None,winning_kind=None,AI_advance=0,native_controls_issued=0,original_controller_owners_absent=True,core_before=phase,core_after=dict(phase))
 def run_gate(self,p):return terminal_gate(dict(status='failed'),dict(status='attention',exit_code=1),p,192,225)
 def test_verified_disabled_defeat_is_partial_only(self):self.assertTrue(self.run_gate(self.proof()))
 def test_live_or_enabled_extension_does_not_pass(self):
  for key,value in [('observer_alive',True),('one_more_turn_disabled',False),('native_controls_issued',1),('AI_advance',1),('original_controller_owners_absent',False)]:
   p=self.proof();p[key]=value
   with self.subTest(key=key),self.assertRaises(AssertionError):self.run_gate(p)
 def test_clock_movement_and_full_endpoint_fail(self):
  p=self.proof();p['core_after']['turn']=193
  with self.assertRaises(AssertionError):self.run_gate(p)
  with self.assertRaises(AssertionError):terminal_gate(dict(status='failed'),dict(status='attention',exit_code=1),self.proof(),225,225)

if __name__=='__main__':unittest.main()
