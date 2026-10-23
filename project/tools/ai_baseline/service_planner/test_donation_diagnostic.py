"""Routes, original-wallet observations, and actual Lua5.1 transactions; offline."""
import copy,json,sys,unittest
from pathlib import Path
from .donation_diagnostic import route,budget_snapshot,candidates
from .policy import Budget,Planner,Policy
from .test_material import observation
sys.path.insert(0,r'C:/Users/Shadow/Desktop/Codex/csc-adjacencies/test-deps')
from lupa.lua51 import LuaRuntime

class PlanningTests(unittest.TestCase):
 def fixture(self):
  o=observation()
  for p in o['tiles']:p['within_city_reach']=True
  o['tiles'].append(dict(index=1,owner=1,revealed=True,neighbors=[2]))
  o['tiles'].append(dict(index=2,owner=-1,revealed=True,within_city_reach=True,price=10,native_purchasable=True,neighbors=[1,42]))
  o['tiles'][0]['neighbors'].append(2)
  for p in o['tiles'][1:3]:p['neighbors']=[42]
  return o
 def test_connector_and_complete_cost(self):
  c=candidates(self.fixture())[0]
  self.assertEqual(c.plan_connectors,(2,));self.assertEqual(c.missing_tiles[0],2);self.assertEqual(c.remaining_price,110)
 def test_foreign_connector_cannot_be_acquired(self):
  o=self.fixture();o['tiles'][-1]['owner']=3
  self.assertEqual(candidates(o)[0].remaining_price,0)
 def test_unquoted_connector_cannot_be_free(self):
  o=self.fixture();o['tiles'][-1]['price']=0
  self.assertEqual(candidates(o)[0].remaining_price,0)
 def test_later_missing_quote_is_watchable_then_buyable_stepwise(self):
  o=self.fixture();o['tiles'][0]['price']=-1;o['tiles'][0]['native_purchasable']=False
  c=candidates(o)[0];self.assertEqual(c.purchase_plot,2);self.assertEqual(c.remaining_price,0)
  a=budget_snapshot(c,Budget(3),Planner(Policy.material_first_v2()),60)
  self.assertIsNone(a['quoted_total']);self.assertIsNone(a['raw_total_affordable'])
 def test_ring_four_unowned_material_watch_only(self):
  o=self.fixture();o['tiles'][2]['within_city_reach']=False
  self.assertEqual(candidates(o)[0].remaining_price,0)
 def test_base_only_is_not_diagnostic_target(self):
  o=self.fixture();o['tiles'][2]['spec_for']=[];self.assertEqual(candidates(o),[])
 def test_original_low_gold_is_recorded_as_fail(self):
  c=candidates(self.fixture())[0];a=budget_snapshot(c,Budget(3,net_income=5),Planner(Policy.material_first_v2()),60)
  self.assertEqual(a['original_gold'],3);self.assertFalse(a['raw_total_affordable']);self.assertFalse(a['complete_route_preserves_reserve'])
 def test_original_rich_gold_is_recorded_separately(self):
  c=candidates(self.fixture())[0];a=budget_snapshot(c,Budget(1000,net_income=5),Planner(Policy.material_first_v2()),60)
  self.assertTrue(a['whole_route_within_80pct_surplus']);self.assertTrue(a['complete_route_preserves_reserve'])
 def test_same_type_exclusion_and_other_type_allowed(self):
  o=self.fixture();o['same_quarter_types']=['BAKERS'];self.assertTrue(candidates(o))
  o['same_quarter_types']=['TAILORS'];self.assertEqual(candidates(o),[])

class TransactionTests(unittest.TestCase):
 def setUp(self):
  self.e=LuaRuntime(unpack_returned_tuples=True)
  self.e.execute('''
   state={gold=3.25,turn=20,active=false,credit_calls=0,debit_calls=0,assign_calls=0,props={},price_bump=0}
   plots={ [42]={owner=-1,city=-1,res=-1},[81]={owner=-1,city=-1,res=1},[82]={owner=-1,city=-1,res=2},[2]={owner=-1,city=-1,res=-1} }
   for i,p in pairs(plots)do p.index=i;function p:GetIndex()return self.index end;function p:GetOwner()return self.owner end;function p:GetDistrictType()return -1 end;function p:GetResourceType()return self.res end;function p:GetImprovementType()return -1 end;function p:GetFeatureType()return -1 end;function p:GetX()return self.index end;function p:GetY()return 0 end end
   Game={GetCurrentGameTurn=function()return state.turn end,GetProperty=function(self,k)return state.props[k]end,SetProperty=function(self,k,v)state.props[k]=v end}
   AutoplayManager={IsActive=function()return state.active end}
   local treasury={GetGoldBalance=function()return state.gold end,ChangeGoldBalance=function(self,n)state.gold=state.gold+n;if n>0 then state.credit_calls=state.credit_calls+1 else state.debit_calls=state.debit_calls+1 end end}
   Players={[1]={IsAlive=function()return true end,IsMajor=function()return true end,IsHuman=function()return false end,GetTreasury=function()return treasury end}}
   CityManager={GetCity=function()return {GetOwner=function()return 1 end}end}
   Map={GetPlotByIndex=function(i)return plots[i]end,GetAdjacentPlots=function()return {plots[81],plots[82]}end}
   GameInfo={Resources={[1]={Index=1},[2]={Index=2}},TypeTags=function()local a={{Type=1,Tag='CLASS_CSC_TAILORS_BASE'},{Type=2,Tag='CLASS_CSC_TAILORS_SPEC'}};local i=0;return function()i=i+1;return a[i]end end}
   PlayersVisibility={[1]={IsRevealed=function()return true end}}
   local prices={[2]=10,[42]=40,[81]=30,[82]=30}
   ExposedMembers={CSC_DONATION_UI={}}
   function ExposedMembers.CSC_DONATION_UI.Quote(r,i)return {turn=state.turn,gold=state.gold,owner=plots[i].owner,city_owner=1,price=prices[i]+state.price_bump,revealed=true,within_range=true,native_reach=true,source_potential=true,can_produce=true,same_quarter=false}end
   function assignment_fixture(r,i)state.assign_calls=state.assign_calls+1;plots[i].owner=1;plots[i].city=10 end
   WorldBuilder={CityManager=function()return {SetPlotOwner=function(self,x,y,pid,cid)assignment_fixture(r,x)end}end}
   function ExposedMembers.CSC_DONATION_UI.Owner(r,i)return {owner=plots[i].owner,plot_city=plots[i].city,city_owner=1}end
   r={enabled=true,token='scene:1:10:42',turn=20,player=1,city=10,source=42,quarter='TAILORS',materials={81,82},route={2,42,81,82},initial_total=110,initial_quote_complete=true,original_gold=3.25}
  ''')
  self.e.execute(Path(__file__).with_name('donation_transaction.lua').read_text(encoding='utf-8'))
 def finish_tx(self):
  for _ in range(64):
   value=self.e.execute('return CSC_DONATION.Advance({token=r.token})')
   if value.status=='confirmed':return value
  raise RuntimeError('Fixture state remained unobservable')
 def run_tx(self):
  self.e.execute('CSC_DONATION.Begin(r)');return self.finish_tx()
 def fail(self):
  with self.assertRaises(Exception):self.run_tx()
 def test_donate_full_route_and_exact_debits(self):
  x=self.run_tx();self.assertEqual(x.status,'confirmed');self.assertEqual(x.donated,110);self.assertEqual(x.spent,110);self.assertEqual(x.final_gold,3.25);self.assertEqual(self.e.globals().state.assign_calls,4)
 def test_enabled_required(self):
  self.e.execute('r.enabled=false');self.fail();self.assertEqual(self.e.globals().state.credit_calls,0)
 def test_duplicate_never_grants_or_assigns_twice(self):
  self.run_tx();self.fail();self.assertEqual(self.e.globals().state.assign_calls,4);self.assertEqual(self.e.globals().state.credit_calls,1)
 def test_original_treasury_change_blocks(self):
  self.e.execute('state.gold=4');self.fail();self.assertEqual(self.e.globals().state.credit_calls,0)
 def test_quote_change_blocks_before_grant(self):
  self.e.execute('r.initial_total=109');self.fail();self.assertEqual(self.e.globals().state.credit_calls,0)
 def test_same_quarter_rejected_before_grant(self):
  self.e.execute('local f=ExposedMembers.CSC_DONATION_UI.Quote;ExposedMembers.CSC_DONATION_UI.Quote=function(r,i)local q=f(r,i);q.same_quarter=true;return q end');self.fail();self.assertEqual(self.e.globals().state.credit_calls,0)
 def test_missing_specialty_rejected_before_grant(self):
  self.e.execute('plots[82].res=-1');self.fail();self.assertEqual(self.e.globals().state.credit_calls,0)
 def test_failed_assignment_stops_without_charge_or_retry(self):
  self.e.execute('assignment_fixture=function()state.assign_calls=state.assign_calls+1 end');self.fail();self.fail();self.assertEqual(self.e.globals().state.assign_calls,1);self.assertEqual(self.e.globals().state.gold,113.25)
 def test_wrong_city_stops(self):
  self.e.execute('local f=assignment_fixture;assignment_fixture=function(r,i)f(r,i);plots[i].city=99 end');self.fail();self.assertEqual(self.e.globals().state.debit_calls,0)
 def test_missing_return_with_real_effect_is_confirmed(self):
  self.e.execute('local f=assignment_fixture;assignment_fixture=function(r,i)f(r,i);error("missing return")end');self.assertEqual(self.run_tx().status,'confirmed')
 def test_later_price_increase_topup_is_observed(self):
  self.e.execute('local f=assignment_fixture;assignment_fixture=function(r,i)f(r,i);state.price_bump=5 end')
  x=self.run_tx();self.assertEqual(x.spent,125);self.assertEqual(x.donated,125);self.assertEqual(x.final_gold,3.25)
 def test_missing_later_quote_gets_exact_grant_after_connector(self):
  self.e.execute('r.initial_total=80;r.initial_quote_complete=false;local f=ExposedMembers.CSC_DONATION_UI.Quote;ExposedMembers.CSC_DONATION_UI.Quote=function(r,i)local q=f(r,i);if i==81 and plots[42].owner==-1 then q.price=-1 end;return q end')
  x=self.run_tx();self.assertEqual(x.spent,110);self.assertEqual(x.donated,110);self.assertEqual(x.final_gold,3.25);self.assertFalse(x.initial_quote_complete)
 def test_phase_movement_blocks(self):
  self.e.execute('state.active=true');self.fail();self.assertEqual(self.e.globals().state.credit_calls,0)
 def test_observed_ui_previous_turn_allowed(self):
  self.e.execute('local f=ExposedMembers.CSC_DONATION_UI.Quote;ExposedMembers.CSC_DONATION_UI.Quote=function(r,i)local q=f(r,i);q.turn=r.turn-1;return q end');self.assertEqual(self.run_tx().status,'confirmed')
 def test_stale_ui_clock_rejected(self):
  self.e.execute('local f=ExposedMembers.CSC_DONATION_UI.Quote;ExposedMembers.CSC_DONATION_UI.Quote=function(r,i)local q=f(r,i);q.turn=r.turn-2;return q end');self.fail();self.assertEqual(self.e.globals().state.credit_calls,0)
 def test_UI_gold_lag_waits_without_extra_grant(self):
  self.e.execute('CSC_DONATION.Begin(r);saved_quote=ExposedMembers.CSC_DONATION_UI.Quote;ExposedMembers.CSC_DONATION_UI.Quote=function(r,i)local q=saved_quote(r,i);q.gold=r.original_gold;return q end')
  value=self.e.execute('return CSC_DONATION.Advance({token=r.token})');self.assertEqual(value.status,'awaiting_UI');self.assertEqual(self.e.globals().state.credit_calls,1);self.assertEqual(self.e.globals().state.assign_calls,0)
  self.e.execute('ExposedMembers.CSC_DONATION_UI.Quote=saved_quote');self.assertEqual(self.finish_tx().status,'confirmed')
 def test_assignment_lag_never_reissues_same_assignment(self):
  self.e.execute('CSC_DONATION.Begin(r);saved_assign=assignment_fixture;assignment_fixture=function(r,i)state.assign_calls=state.assign_calls+1;state.delayed_index=i end')
  self.e.execute('CSC_DONATION.Advance({token=r.token})')
  for _ in range(4):self.assertEqual(self.e.execute('return CSC_DONATION.Advance({token=r.token})').status,'awaiting_ownership')
  self.assertEqual(self.e.globals().state.assign_calls,1)
  self.e.execute('plots[state.delayed_index].owner=1;plots[state.delayed_index].city=10;assignment_fixture=saved_assign')
  self.assertEqual(self.finish_tx().status,'confirmed');self.assertEqual(self.e.globals().state.assign_calls,4)
 def test_no_UI_writer_is_required(self):
  self.assertIsNone(self.e.globals().ExposedMembers.CSC_DONATION_UI.Assign);self.assertEqual(self.run_tx().status,'confirmed')
 def test_native_multiline_assignment_error_is_one_valid_JSON_record(self):
  self.e.execute('messages={};print=function(s)messages[#messages+1]=s end;assignment_fixture=function()error("native line1\\nline2")end;CSC_DONATION.Begin(r);CSC_DONATION.Advance({token=r.token})')
  raw=self.e.globals().messages[2];value=json.loads(raw.split('=',1)[1]);self.assertEqual(value['status'],'assignment_requested');self.assertIn('line1',value['assignment_error'])
 def test_native_reach_false_is_not_assignment_authority(self):
  self.e.execute('local f=ExposedMembers.CSC_DONATION_UI.Quote;ExposedMembers.CSC_DONATION_UI.Quote=function(r,i)local q=f(r,i);q.native_reach=false;return q end');self.fail();self.assertEqual(self.e.globals().state.assign_calls,0)

if __name__=='__main__':unittest.main()
