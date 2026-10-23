"""Own-first funding, cutoff, real transaction phases and radius boundary."""
import json,unittest,tempfile
from dataclasses import replace
from pathlib import Path
from .funded_acquisition import funding,FundedDiagnostic
from .policy import Planner,Policy,Budget
from .observations import build_material_candidates
from .donation_diagnostic import candidates
from .test_material import observation
from . import test_donation_diagnostic as donated_tests

class FundingTests(unittest.TestCase):
 def setUp(self):
  o=observation()
  for p in o['tiles']:p['within_city_reach']=True
  self.c=build_material_candidates(o,stepwise=True)[0]
  self.p=Planner(Policy.material_first_v2(max_connectors=2))
 def test_rich_AI_never_receives_fallback_even_early(self):
  q=funding(self.c,Budget(1000),self.p,60)
  self.assertEqual((q['action'],q['own_gold'],q['grant']),('acquire',self.c.price,0))
 def test_poor_AI_pays_safe_share_with_only_shortfall_donated(self):
  c=replace(self.c,price=40)
  q=funding(c,Budget(50),self.p,100)
  self.assertEqual((q['own_gold'],q['grant']),(20,20))
  self.assertEqual(50+q['grant']-40,30)
 def test_fallback_continues_past_turn100_by_human_override(self):
  self.assertEqual(funding(self.c,Budget(3),self.p,101)['action'],'acquire')
  self.assertEqual(funding(self.c,Budget(3),self.p,200)['grant'],self.c.price)
  self.assertEqual(funding(self.c,Budget(1000),self.p,101)['action'],'acquire')
 def test_reserve_target_is_not_clipped_to_an_already_poor_wallet(self):
  for b,target in [(Budget(19.1953125,7.19921875),25),(Budget(3,0,emergency_reserve=80,maintenance=40),80),(Budget(3,-10),100)]:
   q=funding(self.c,b,self.p,17)
   self.assertEqual((q['reserve'],q['own_gold'],q['grant']),(target,0,self.c.price))
 def test_donations_do_not_bypass_caps_cooldowns_pending_or_evidence(self):
  self.p.site_spend[self.c.site_key]=299
  self.assertEqual(funding(self.c,Budget(3),self.p,60)['action'],'wait')
  self.p.site_spend.clear();self.p.pending_players.add(self.c.player)
  self.assertEqual(funding(self.c,Budget(3),self.p,60)['action'],'wait')
  self.p.pending_players.clear();self.p.purchases=[(self.c.player,self.c.city,60,1)]
  self.assertEqual(funding(self.c,Budget(3),self.p,60)['action'],'wait')
  self.p.purchases=[]
  self.assertEqual(funding(self.c,Budget(3,cashflow_observed=False),self.p,60)['action'],'wait')
 def test_owned_fourth_ring_material_counts_but_unowned_is_unrouteable(self):
  o=donated_tests.PlanningTests().fixture()
  o['tiles'][2].update(within_city_reach=False,owner=1)
  rows=candidates(o);self.assertTrue(any(c.specialty>0 and c.purchase_plot is not None for c in rows))
  o['tiles'][2]['owner']=-1
  rows=candidates(o);self.assertTrue(rows);self.assertTrue(all(c.purchase_plot is None for c in rows))

class CoordinatorTests(unittest.TestCase):
 def write(self,path,value):
  path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value))
 def test_one_step_per_player_then_fresh_smaller_wallet_next_turn(self):
  o=observation()
  for row in o['tiles']:row['within_city_reach']=True
  c=replace(build_material_candidates(o,stepwise=True)[0],price=40)
  pool={(c.player,c.city):[c],(c.player,c.city+1):[replace(c,city=c.city+1,plot=43)]}
  class Runner:
   def __init__(self):self.request=None;self.buys=0
   def encode(self,q):self.request=q;return '{}'
   def cmd(self,*args):
    q=self.request;self.buys+=1
    return 'CSC_FUNDED_RECEIPT='+json.dumps(dict(status='confirmed',turn=q['turn'],original_gold=q['gold'],
     donated=q['grant'],spent=q['price'],own_gold_spent=q['own_gold'],final_gold=q['gold']+q['grant']-q['price'],
     steps=[dict(plot=q['plot'],price=q['price'])]))
  runner=Runner()
  class Adapter:
   def __init__(self):self.cities={key:{'district_state':{'TAILORS':{'can_produce':True}}}for key in pool};self.gold=50
   def budget(self,p):return Budget(self.gold)
   def collect(self,turn):
    self.gold=runner.request['gold']+runner.request['grant']-runner.request['price']
    key=(runner.request['player'],runner.request['city'])
    pool[key]=[replace(pool[key][0],missing_tiles=(82,),purchase_plot=82)]
   def place_zero(self,c):raise AssertionError('Partial route cannot place foundation')
  class Harness(FundedDiagnostic):
   def city_candidates(self,adapter,key,turn):return [replace(x,observed_turn=turn)for x in pool[key]]
  with tempfile.TemporaryDirectory(dir=Path.cwd())as tmp:
   test=Harness(runner,Path(tmp),self.write,runner.encode);adapter=Adapter()
   first=test.cycle(adapter,150)
   self.assertEqual(len(first),1);self.assertEqual(runner.buys,1)
   self.assertEqual((first[0]['funding']['own_gold'],first[0]['funding']['grant']),(20,20))
   second=test.cycle(adapter,151)
   self.assertEqual(len(second),1);self.assertEqual(runner.buys,2)
   self.assertEqual((second[0]['funding']['own_gold'],second[0]['funding']['grant']),(4,36))
   self.assertEqual(test.planner.site_spend[c.site_key],80)
 def test_partial_funded_history_reconciles_once_and_open_step_blocks(self):
  q=dict(player=1,city=10,quarter='TAILORS',source=42,token='one',turn=150)
  receipt=dict(status='confirmed',turn=150,original_gold=50,final_gold=30,spent=40,donated=20,own_gold_spent=20,steps=[dict(plot=81,price=40)])
  rows=[dict(event='funded-acquisition-begin',request=q),dict(event='funded-acquisition-confirmed',request=q,receipt=receipt)]
  with tempfile.TemporaryDirectory(dir=Path.cwd())as tmp:
   parent=Path(tmp)/'parent';parent.mkdir();(parent/'service-actions.ndjson').write_text(''.join(json.dumps(x)+'\n'for x in rows))
   current=Path(tmp)/'current';current.mkdir()
   test=FundedDiagnostic(object(),current,self.write,lambda x:'')
   result=test.inherit_confirmed(parent)
   self.assertEqual((result['tiles'],result['spent'],result['donated']),(1,40,20))
   self.assertEqual(test.planner.purchases,[(1,10,150,40)])
   self.assertEqual(test.planner.site_spend['1:10:TAILORS:42'],40)
   (parent/'service-actions.ndjson').write_text(json.dumps(rows[0])+'\n')
   other=Path(tmp)/'other';other.mkdir()
   with self.assertRaisesRegex(AssertionError,'Unconfirmed funded acquisition'):
    FundedDiagnostic(object(),other,self.write,lambda x:'').inherit_confirmed(parent)
 def test_verified_no_effect_begin_can_be_inherited_without_spending_or_pending(self):
  q=dict(player=4,city=10,quarter='BAKERS',source=42,token='rejected',turn=17)
  proof=dict(verified=True,ledger_absent=True,gold_unchanged=True,owner_unchanged=True,price_unchanged=True,read_only_preflight_failure=True,failed_token='rejected')
  rows=[dict(event='funded-acquisition-begin',request=q),dict(event='funded-acquisition-reconciled-no-effect',token='rejected',proof=proof)]
  with tempfile.TemporaryDirectory(dir=Path.cwd())as tmp:
   parent=Path(tmp)/'parent';parent.mkdir();(parent/'service-actions.ndjson').write_text(''.join(json.dumps(x)+'\n'for x in rows))
   current=Path(tmp)/'current';current.mkdir();test=FundedDiagnostic(object(),current,self.write,lambda x:'')
   result=test.inherit_confirmed(parent)
   self.assertEqual((result['tiles'],result['spent'],result['acquisitions']),(0,0,0))
   self.assertFalse(test.planner.pending_players);self.assertFalse(test.planner.purchases)

class FundedLuaTests(donated_tests.TransactionTests):
 # Reuse only the engine fixture, not the old donated-route test methods.
 def setUp(self):
  donated_tests.TransactionTests.setUp(self)
  self.e.execute(Path(__file__).with_name('funded_acquisition.lua').read_text())
  self.e.execute("state.gold=100;r.gold=100;r.plot=2;r.price=10;r.reserve=25;r.remaining_cap=300;r.own_gold=10;r.grant=0;r.cashflow_observed=true;r.net_income=0;r.maintenance=0;r.connectors={2};r.turn=20;r.token='funded-test'")
 def finish(self):
  for _ in range(20):
   result=self.e.execute('return CSC_FUNDED_ACQUISITION.Advance({token=r.token})')
   if result.status=='confirmed':return result
  raise AssertionError('Unconfirmed fixture')
 def begin(self):return self.e.execute('return CSC_FUNDED_ACQUISITION.Begin(r)')
 def test_wallet_only_exact_debit_no_grant(self):
  self.begin();v=self.finish()
  self.assertEqual((v.donated,v.spent,v.own_gold_spent,v.final_gold),(0,10,10,90))
  self.assertEqual((self.e.globals().state.assign_calls,self.e.globals().state.credit_calls),(1,0))
 def test_early_mixed_shortfall_and_reserve(self):
  self.e.execute('state.gold=30;r.gold=30;r.own_gold=4;r.grant=6;r.turn=100;state.turn=100')
  self.begin();v=self.finish();self.assertEqual((v.donated,v.own_gold_spent,v.final_gold),(6,4,26))
 def test_native_already_below_reserve_full_shortfall_preserves_original_balance(self):
  self.e.execute('state.gold=19.1953125;r.gold=19.1953125;r.reserve=25;r.own_gold=0;r.grant=10')
  self.begin();v=self.finish();self.assertEqual((v.donated,v.own_gold_spent,v.final_gold),(10,0,19.1953125))
 def test_native_shortfall_continues_after100(self):
  self.e.execute('state.gold=30;r.gold=30;r.own_gold=4;r.grant=6;r.turn=101;state.turn=101')
  self.begin();v=self.finish();self.assertEqual((v.donated,v.own_gold_spent,v.final_gold),(6,4,26))
 def test_excess_grant_rejected_before_effect(self):
  self.e.execute('r.grant=10')
  with self.assertRaisesRegex(Exception,'Funding split'):self.begin()
  self.assertEqual(self.e.globals().state.credit_calls,0)
 def test_price_or_wallet_drift_rejects_before_effect(self):
  for expr in('r.price=11','r.gold=99'):
   with self.subTest(expr=expr):
    self.setUp();self.e.execute(expr)
    with self.assertRaises(Exception):self.begin()
    self.assertEqual(self.e.globals().state.assign_calls,0)
 def test_duplicate_closed_token_never_repeats(self):
  self.begin();self.finish()
  with self.assertRaises(Exception):self.begin()
  self.assertEqual(self.e.globals().state.assign_calls,1)
 def test_lagged_assignment_does_not_resend(self):
  self.e.execute('saved_assign=assignment_fixture;assignment_fixture=function(r,i)state.assign_calls=state.assign_calls+1;state.delayed_index=i end')
  self.begin();self.e.execute('CSC_FUNDED_ACQUISITION.Advance({token=r.token});CSC_FUNDED_ACQUISITION.Advance({token=r.token})')
  for _ in range(3):self.assertEqual(self.e.execute('return CSC_FUNDED_ACQUISITION.Advance({token=r.token})').status,'awaiting_ownership')
  self.assertEqual(self.e.globals().state.assign_calls,1)
  self.e.execute('plots[2].owner=1;plots[2].city=10')
  self.assertEqual(self.finish().final_gold,90)
 def test_pillage_or_resource_visibility_not_faked(self):
  self.e.execute('PlayersVisibility[1].IsRevealed=function()return false end')
  with self.assertRaises(Exception):self.begin()
  self.assertEqual(self.e.globals().state.assign_calls,0)

# Explicitly discard inherited old full-route tests: their names exercise a
# different backend. The imported class remains the source of the fixture only.
for _name in list(dir(FundedLuaTests)):
 if _name.startswith('test_')and _name not in FundedLuaTests.__dict__:
  setattr(FundedLuaTests,_name,None)

if __name__=='__main__':unittest.main()
