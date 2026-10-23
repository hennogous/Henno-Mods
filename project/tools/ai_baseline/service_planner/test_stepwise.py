"""Opt-in wallet, establishment and sustained-material paths; no live game."""
import json,re,sys,tempfile,unittest
from pathlib import Path
from dataclasses import replace
from .policy import Policy,Planner,Budget
from .observations import build_candidates
from .execution import PurchaseExecutor,lua
from .test_material import observation
from .test_policy import LUA_FIXTURE

class StepwiseTests(unittest.TestCase):
 def setUp(self):
  self.p=Planner(Policy.material_first_v2());self.o=observation()
 def row(self):return build_candidates(self.o,material_first=True,stepwise=True)[0]
 def decide(self,c=None,b=None):return self.p.evaluate(c or self.row(),{},b or Budget(150,2),60)
 def test_resource_first_and_full_lifecycle(self):
  self.assertEqual(self.row().purchase_plot,81)
  self.o['tiles'][1]['owner']=1;self.assertEqual(self.row().purchase_plot,82)
  self.o['tiles'][0]['owner']=1
  self.assertEqual(self.decide().action,'place') # Stage2 foundation before Specialty.
  self.o['same_quarter_types']=['TAILORS'];self.o['tiles'][0].update(district=3,established_quarter='TAILORS')
  c=self.row();self.assertTrue(c.established);self.assertEqual(self.decide().action,'purchase')
  self.o['tiles'][2]['owner']=1
  self.assertEqual(self.decide().action,'watch');self.assertIn('monitor',self.decide().reason)
 def test_legacy_still_source_first(self):
  c=build_candidates(self.o,material_first=True)[0];self.assertEqual(c.purchase_plot,42)
 def test_owned_base_required_before_foundation(self):
  self.o['tiles'][0]['owner']=1;c=self.row()
  self.assertFalse(c.current_legal);self.assertEqual(self.decide(c).action,'purchase')
 def test_unowned_source_never_established(self):
  self.o['tiles'][0].update(district=3,established_quarter='TAILORS')
  self.assertFalse(build_candidates(self.o,material_first=True,stepwise=True))
 def test_other_same_type_source_stays_blocked(self):
  self.o['same_quarter_types']=['TAILORS'];self.assertFalse(build_candidates(self.o,material_first=True,stepwise=True))
 def test_route_total_does_not_gate_an_affordable_current_step(self):
  c=replace(self.row(),remaining_price=1500,price=30)
  self.assertEqual(self.decide(c,Budget(125,5)).action,'purchase')
  self.assertEqual(self.decide(c,Budget(125,0)).action,'purchase')
  self.assertEqual(self.decide(replace(c,price=110),Budget(125,100)).action,'watch')
 def test_deficit_and_upkeep_reserve_preserved(self):
  c=self.row();self.assertEqual(self.decide(c,Budget(150,-14)).action,'watch')
  self.assertEqual(self.decide(c,Budget(150,10,emergency_reserve=140,maintenance=70)).action,'watch')
 def test_unknown_cashflow_cannot_fund_purchase(self):
  self.assertEqual(self.decide(b=Budget(999,10,cashflow_observed=False)).reason,'cashflow unobserved')
 def test_recent_spend_not_deducted_twice_from_fresh_wallet(self):
  self.p.purchases=[(1,11,59,100)]
  d=self.decide(b=Budget(150,2));self.assertEqual(d.max_price,100);self.assertEqual(d.action,'purchase')
 def test_rolling_cap_and_site_lifetime_cap(self):
  self.p.purchases=[(1,11,59,285)];self.assertEqual(self.decide(b=Budget(999)).max_price,15)
  self.p.purchases=[];self.p.site_spend[self.row().site_key]=290
  self.assertEqual(self.decide(b=Budget(999)).max_price,10)
 def test_unknown_future_quotes_allow_resource_source_and_successive_steps(self):
  c=replace(self.row(),remaining_price=0)
  self.assertEqual(self.decide(c).action,'purchase')
  self.p.site_spend[c.site_key]=30;self.assertEqual(self.decide(c).action,'purchase')
  self.assertEqual(self.decide(replace(c,purchase_plot=42)).action,'purchase')
  connector=replace(c,purchase_plot=99,missing_tiles=c.missing_tiles+(99,),plan_connectors=(99,))
  self.assertEqual(self.decide(connector).action,'watch') # Connector limit remains enforced.
  self.p=Planner(Policy.material_first_v2(max_connectors=2))
  self.assertEqual(self.decide(connector).action,'purchase')
 def test_each_step_rechecks_wallet_and_can_wait_for_savings(self):
  c=replace(self.row(),remaining_price=0,price=40)
  self.assertEqual(self.decide(c,Budget(94.56640625,0)).action,'purchase')
  # A confirmed first purchase leaves the real wallet smaller. The next native
  # quote is 60: unknown future prices did not pre-authorize that second buy.
  self.p.purchases=[(c.player,c.city,59,40)];self.p.site_spend[c.site_key]=40
  next_step=replace(c,purchase_plot=82,price=60)
  self.assertEqual(self.decide(next_step,Budget(54.56640625,0)).action,'watch')
  self.assertEqual(self.decide(next_step,Budget(150,0)).action,'purchase')
 def test_unknown_quotes_never_override_price_reserve_pending_or_caps(self):
  c=replace(self.row(),remaining_price=0,price=80,purchase_plot=42)
  self.assertEqual(self.decide(c,Budget(1444.125,0,emergency_reserve=212)).action,'purchase')
  self.assertEqual(self.decide(replace(c,price=0),Budget(1444.125)).action,'watch')
  self.assertEqual(self.decide(c,Budget(40,1000)).action,'watch')
  self.p.pending_players.add(c.player)
  self.assertEqual(self.decide(c,Budget(1444.125)).reason,'purchase awaiting readback')
  self.p.pending_players.clear();self.p.site_spend[c.site_key]=250
  self.assertEqual(self.decide(c,Budget(1444.125)).max_price,50)
  self.assertEqual(self.decide(c,Budget(1444.125)).action,'watch')
 def test_executor_refresh_can_reject_a_previously_affordable_step_before_send(self):
  class NoSend:
   def cmd(self,*args,**kwargs):raise AssertionError('Must not send an unaffordable purchase')
  c=replace(self.row(),remaining_price=0,price=40)
  decision=self.decide(c,Budget(100,0));self.assertEqual(decision.action,'purchase')
  with tempfile.TemporaryDirectory(dir=Path.cwd())as tmp:
   path=Path(tmp)/'journal.ndjson'
   executor=PurchaseExecutor(self.p,NoSend(),path,allow_mutations=True,
    boundary=lambda:{'turn':60,'autoplay_active':False})
   for fresh_c,fresh_b in [(replace(c,price=100),Budget(100,0)),(c,Budget(50,0)),(c,Budget(100,0,emergency_reserve=90))]:
    with self.assertRaisesRegex(AssertionError,'next step exceeds real-wallet allowance'):
     executor.request(decision,{},lambda old:(fresh_c,fresh_b,60,True,None))
   self.assertFalse(path.exists());self.assertFalse(self.p.pending_players)
 def test_near_free_border_growth_buys_other_material_first(self):
  self.o['tiles'][1]['natural_border_in_turns']=1
  self.assertEqual(self.row().purchase_plot,82)
 def test_site_spend_identity_independent_of_material_set(self):
  a=self.row();b=replace(a,plan_materials=(83,84))
  self.assertEqual(a.site_key,b.site_key);self.assertNotEqual(a.key,b.key)
 def engine(self):
  from lupa.lua51 import LuaRuntime
  e=LuaRuntime(unpack_returned_tuples=True);e.execute(LUA_FIXTURE);return e
 def request(self):
  return {'player':1,'city':10,'purchase_plot':42,'source_plot':100,'quarter':'TAILORS','turn':60,
   'base':2,'specialty':1,'material_first':True,'stepwise':True,'established':True,'service':None,
   'plan_materials':{'81':True,'82':True,'42':True},'remaining_tiles':{'42':True},
   'gold':600,'price':80,'max_price':100,'reserve':150,'plot_purchase_parameter':True}
 def support_engine(self):
  e=self.engine();e.execute("""
city.GetDistricts=function()return {HasDistrict=function()return true end}end
Map.GetPlotByIndex(100).GetDistrictType=function()return 3 end
GameInfo.Districts.DISTRICT_CSC_TAILORS_QUARTER.Index=3
GameInfo.Resources.SILK={Index=11};GameInfo.Resources[11]={Index=11}
GameInfo.TypeTags[2]={Type='SILK',Tag='CLASS_CSC_TAILORS_SPEC'}
local source=Map.GetPlotByIndex(100);local target=Map.GetPlotByIndex(42)
target.GetResourceType=function()return 11 end
Map.GetAdjacentPlots=function()return {Map.GetPlotByIndex(81),Map.GetPlotByIndex(82),target}end
""");return e
 def test_actual_lua_established_quarter_buys_material_without_second_foundation(self):
  e=self.support_engine();e.globals().CSC_SERVICE_PURCHASE_REQUEST=e.eval(lua(self.request()))
  e.execute(Path(__file__).with_name('native_purchase.lua').read_text())
  self.assertEqual((e.globals().requests,e.globals().gold),(1,520))
 def test_actual_lua_established_wrong_type_rejects_before_send(self):
  e=self.support_engine();e.execute('Map.GetPlotByIndex(100).GetDistrictType=function()return 4 end')
  e.globals().CSC_SERVICE_PURCHASE_REQUEST=e.eval(lua(self.request()))
  with self.assertRaisesRegex(Exception,'ownership/type changed'):e.execute(Path(__file__).with_name('native_purchase.lua').read_text())
  self.assertEqual(e.globals().requests,0)
 def test_actual_collector_net_is_gross_minus_maintenance_and_unknown_not_zero(self):
  from lupa.lua51 import LuaRuntime
  source=Path(__file__).with_name('test_material.py').read_text()
  fixture=re.search(r"engine.execute\(r'''(.*?)'''\)",source,re.S)[1]
  e=LuaRuntime(unpack_returned_tuples=True);e.execute(fixture)
  e.execute("Players[1].GetTreasury=function()return {GetGoldBalance=function()return 100 end,GetGoldYield=function()return 25 end,GetTotalMaintenance=function()return 23 end}end")
  e.execute(Path(__file__).with_name('native_observer.lua').read_text())
  e.execute('CSC_SERVICE_NATIVE.Read()');p=json.loads(e.globals().captured.split('=',1)[1])['players'][0]
  self.assertEqual((p['gross_income'],p['maintenance'],p['net_income']),(25,23,2));self.assertTrue(p['cashflow_observed'])
  e.execute("Players[1].GetTreasury=function()return {GetGoldBalance=function()return 100 end,GetGoldYield=function()return 25 end}end;CSC_SERVICE_NATIVE.Read()")
  p=json.loads(e.globals().captured.split('=',1)[1])['players'][0];self.assertFalse(p['cashflow_observed']);self.assertNotIn('net_income',p)
 def test_support_source_import_includes_unfinished_and_natural(self):
  from lupa.lua51 import LuaRuntime
  e=LuaRuntime(unpack_returned_tuples=True);e.execute("""
Game={GetCurrentGameTurn=function()return 95 end}
GameInfo={Districts={DISTRICT_CSC_BAKERS_QUARTER={Index=1},DISTRICT_CSC_TAILORS_QUARTER={Index=2}}}
local ds={GetNumDistricts=function()return 2 end,GetDistrictByIndex=function(self,i)return {GetType=function()return i+1 end,GetX=function()return i+42 end,GetY=function()return 0 end,IsComplete=function()return i==1 end}end}
local city={GetID=function()return 10 end,GetDistricts=function()return ds end}
local player={GetID=function()return 1 end,GetCities=function()return {Members=function()local done=false;return function()if not done then done=true;return 10,city end end end}end}
PlayerManager={GetAliveMajors=function()return {player}end}
Map={GetPlot=function(x,y)return {GetIndex=function()return x end,GetOwner=function()return 1 end,GetX=function()return x end,GetY=function()return y end}end,GetAdjacentPlots=function()return {{GetIndex=function()return 81 end}}end}
print=function(v)captured=v end
""")
  e.execute(Path(__file__).with_name('native_quarter_sites.lua').read_text());data=json.loads(e.globals().captured.split('=',1)[1])
  self.assertEqual(len(data['cities']['1:10']),2);self.assertFalse(data['cities']['1:10'][0]['complete'])
 def test_metric_point_counts_unfinished_and_censors_empty_denominator(self):
  from .metrics import summarize
  s={'turn':60,'errors':[],'cities':[{'player':1,'city':10,'population':5,'buildings':[],
     'properties':{},'yields':{},'quarters':[{'quarter':'TAILORS','plot':42,'complete':False,'pillaged':False,
       'site':{'base':1,'spec':1,'base_improved':0,'spec_improved':0,'sales':0,'sales_plots':[],'materials':[]}}]}]}
  result=summarize(s);self.assertEqual(result['counts']['unfinished_quarters'],1)
  self.assertIsNone(result['ratios']['effective_base_supply']['value'])
  self.assertFalse(result['sales_transactions_observed']);self.assertFalse(result['formal_benchmark_ready'])
  s['cities'][0]['quarters'][0]['complete']=True
  s['cities'][0]['buildings']=[{'type':'BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP','pillaged':False}]
  result=summarize(s);self.assertEqual(result['ratios']['effective_base_supply'],{'numerator':0,'denominator':1,'value':0})
  s['cities'][0]['quarters'][0]['site']['base_improved']=1
  result=summarize(s);self.assertEqual(result['ratios']['effective_base_supply']['value'],1)
  self.assertEqual(result['counts']['functioning_with_structural_sales'],0)

if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--lua51-path',required=True);p.add_argument('--output',type=Path);a=p.parse_args();sys.path.insert(0,a.lua51_path)
 result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(StepwiseTests))
 if a.output:a.output.write_text(json.dumps({'passed':result.wasSuccessful(),'tests':result.testsRun,'native_connections':0},indent=2))
 raise SystemExit(not result.wasSuccessful())
