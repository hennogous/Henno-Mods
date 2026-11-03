"""Material deposits under districts are physical resources, not improvable supply."""
import copy,importlib.util,json,re,unittest
from pathlib import Path
from .observations import build_material_candidates,material_deposit_available
from .test_material import observation
from . import test_funded_acquisition as funding_fixtures
from .execution import lua

class CandidateViability(unittest.TestCase):
 def test_district_zero_and_names_are_blocked_even_with_resource_owner(self):
  for kind in(0,13,'DISTRICT_CITY_CENTER'):
   self.assertFalse(material_deposit_available(dict(district=kind)))
   obs=observation();obs['tiles'][2].update(owner=1,district=kind)
   rows=build_material_candidates(obs,stepwise=True,connector_limit=2)
   self.assertFalse(any(c.specialty for c in rows));self.assertTrue(all(82 not in c.plan_materials for c in rows))
 def test_blocked_Base_cannot_justify_a_chain(self):
  obs=observation();obs['tiles'][1].update(owner=1,district=0)
  self.assertEqual(build_material_candidates(obs,stepwise=True),[])
 def test_future_improvement_technology_is_not_required_now(self):
  obs=observation();obs['tiles'][2].update(district=-1,improvement_prereq='TECH_IRRIGATION',improvement_unlocked=False)
  self.assertTrue(any(c.specialty>0 for c in build_material_candidates(obs,stepwise=True)))
 def test_blocked_deposit_does_not_mask_an_alternative_open_Spec(self):
  obs=observation();obs['tiles'][2].update(owner=1,district=0);alternative=copy.deepcopy(obs['tiles'][2]);alternative.update(index=83,owner=-1,district=-1);obs['tiles'].append(alternative);obs['tiles'][0]['neighbors'].append(83)
  rows=build_material_candidates(obs,stepwise=True);self.assertTrue(rows);self.assertTrue(all(c.specialty>0 and 83 in c.plan_materials and 82 not in c.plan_materials for c in rows))

class NativeEconomicGuards(unittest.TestCase):
 def setUp(self):
  fixture=funding_fixtures.FundedLuaTests();fixture.setUp();self.e=fixture.e;self.e.execute("print=function()end")
 def test_covered_Spec_rejects_before_even_a_ledger_is_created(self):
  self.e.execute('plots[82].GetDistrictType=function()return 0 end')
  with self.assertRaisesRegex(Exception,'Material covered by district'):self.e.execute('CSC_FUNDED_ACQUISITION.Begin(r)')
  self.assertIsNone(self.e.execute('return Game:GetProperty("CSC_FUNDED_"..r.token)'))
  for name in('credit_calls','debit_calls','assign_calls'):self.assertEqual(self.e.globals().state[name],0)
 def test_new_district_after_preparation_blocks_before_any_grant(self):
  self.e.execute('CSC_FUNDED_ACQUISITION.Begin(r);plots[81].GetDistrictType=function()return 0 end')
  with self.assertRaisesRegex(Exception,'Material covered by district'):self.e.execute('CSC_FUNDED_ACQUISITION.Advance({token=r.token})')
  for name in('credit_calls','debit_calls','assign_calls'):self.assertEqual(self.e.globals().state[name],0)
 def test_open_deposits_still_use_the_existing_wallet_transaction(self):
  self.e.execute('CSC_FUNDED_ACQUISITION.Begin(r)')
  for _ in range(4):
   result=self.e.execute('return CSC_FUNDED_ACQUISITION.Advance({token=r.token})')
   if result.status=='confirmed':break
  self.assertEqual(result.status,'confirmed');self.assertEqual(result.final_gold,90);self.assertEqual(self.e.globals().state.assign_calls,1)

class NativePurchaseGuard(unittest.TestCase):
 def test_direct_request_rejects_covered_planned_material_without_spending(self):
  from lupa.lua51 import LuaRuntime
  from .test_policy import LUA_FIXTURE
  e=LuaRuntime(unpack_returned_tuples=True);e.execute(LUA_FIXTURE);e.execute("GameInfo.TypeTags[2]={Type='WOOL',Tag='CLASS_CSC_TAILORS_SPEC'};Map.GetPlotByIndex(82).GetDistrictType=function()return 0 end")
  request=dict(player=1,city=10,purchase_plot=42,source_plot=42,quarter='TAILORS',turn=60,base=1,specialty=1,material_first=True,service=None,plan_materials={'81':True,'82':True},remaining_tiles={'42':True},gold=600,price=80,max_price=200,reserve=150,plot_purchase_parameter=True)
  e.globals().CSC_SERVICE_PURCHASE_REQUEST=e.eval(lua(request))
  with self.assertRaisesRegex(Exception,'Planned material covered by district'):e.execute(Path(__file__).with_name('native_purchase.lua').read_text(encoding='utf-8'))
  self.assertEqual(e.globals().requests,0);self.assertEqual(e.globals().gold,600)

class NativeFoundationGuards(unittest.TestCase):
 def setUp(self):
  from lupa.lua51 import LuaRuntime
  from test_foundation_planner import BOOTSTRAP
  self.e=LuaRuntime(unpack_returned_tuples=True);self.e.execute(BOOTSTRAP);self.e.execute(Path(__file__).parents[1].joinpath('foundation_planner.lua').read_text(encoding='utf-8'))
 def test_requiredBoth_does_not_fall_back_to_a_covered_Spec(self):
  self.e.execute('local c=candidate(1,1,1);c.require_both_materials=true;plots[1].neighbors[2].GetDistrictType=function()return 0 end;CSC_FOUNDATION_PROBE.Plan({c});assert(#CSC_FOUNDATION_PROBE.plan==0);assert(mutations==0)')
 def test_stale_material_district_blocks_the_zero_progress_commit(self):
  self.e.execute('local c=candidate(1,1,1);c.require_both_materials=true;CSC_FOUNDATION_PROBE.Plan({c});assert(#CSC_FOUNDATION_PROBE.plan==1);plots[1].neighbors[2].GetDistrictType=function()return 0 end;local ok=pcall(CSC_FOUNDATION_PROBE.Commit);assert(not ok);assert(mutations==0)')
 def test_legacy_Base_only_legal_plan_stays_available(self):
  self.e.execute('local c=candidate(1,1,1);plots[1].neighbors[2].GetDistrictType=function()return 0 end;CSC_FOUNDATION_PROBE.Plan({c});assert(#CSC_FOUNDATION_PROBE.plan==1);assert(CSC_FOUNDATION_PROBE.plan[1].spec==0);CSC_FOUNDATION_PROBE.Commit();assert(mutations==1)')

class ArchivedNativeFacts(unittest.TestCase):
 def test_actual_precommit69_false_Both_is_removed(self):
  root=Path('C:/Users/Shadow/Desktop/Codex/csc-material-care-v2-20261023/raw-resource016-075-resource-improvement-forecast-v6');path=root/'commands/1000801-service-read-69.txt'
  if not path.exists():self.skipTest('Optional archived native fixture absent')
  text=path.read_text(encoding='utf-8-sig');packet=json.loads(re.findall(r'CSC_SERVICE_NATIVE=([^\r\n]+)',text)[-1]);obs=next(c for c in packet['cities']if(c['player'],c['city'])==(1,262147));tiles={p['index']:p for p in obs['tiles']};self.assertEqual(tiles[2091]['district'],0)
  before=Path('C:/Users/Shadow/.codex/visualizations/2026/10/11/01a12a24-6714-7540-8d23-154b092106fe/before-material-viability-v7/00-observations.py');spec=importlib.util.spec_from_file_location('service_planner.viability_old_fixture',before);old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
  prior=next(c for c in old.build_material_candidates(obs,stepwise=True,connector_limit=2)if c.plot==2165 and c.quarter=='TAILORS');self.assertEqual(prior.specialty,1)
  fixed=[c for c in build_material_candidates(obs,stepwise=True,connector_limit=2)if c.plot==2165 and c.quarter=='TAILORS'];self.assertTrue(all(c.specialty==0 and 2091 not in c.plan_materials for c in fixed))
 def test_actual_locked_open_Plantation_supply_remains_future_opportunity(self):
  root=Path('C:/Users/Shadow/Desktop/Codex/csc-material-care-v2-20261023/raw-resource016-075-resource-improvement-forecast-v6');path=root/'native-service/turn-075.json'
  if not path.exists():self.skipTest('Optional archived native fixture absent')
  data=json.loads(path.read_text(encoding='utf-8-sig'));obs=next(c for c in data['cities']if(c['player'],c['city'])==(2,65536));rows=build_material_candidates(obs,stepwise=True,connector_limit=2);self.assertTrue(any(c.plot==1278 and c.quarter=='BAKERS'and c.specialty>0 and 1204 in c.plan_materials for c in rows))

if __name__=='__main__':unittest.main()
