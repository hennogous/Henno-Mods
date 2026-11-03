"""Actual Lua51 offline fixtures for the opt-in single-site host pilot.

Uses existing test_profiles fakes; no Civ, installation, connection or orders.
CSC_PILOT_SOURCE_DIR permits reviewing staged Lua before source promotion.
"""
import os
from pathlib import Path
import sys
import unittest
from lupa.lua51 import LuaRuntime

ROOT = Path(os.environ.get('CSC_PILOT_REPO_ROOT', Path(__file__).resolve().parents[3]))
sys.path.insert(0, str(ROOT / 'project/tools/ai_tuning'))
from test_profiles import FIXTURE

AI = Path(os.environ.get('CSC_PILOT_SOURCE_DIR', ROOT / 'Civ Supply Chains/Lua_UI/AI'))
POLICY = (AI / 'CSC_AI_OpportunityPolicy.lua').read_text(encoding='utf-8')
HOST = (AI / 'CSC_AI_Assistance.lua').read_text(encoding='utf-8')

EXTRA = r'''
wallet=1000
GameInfo.Resources[5].ResourceType='RESOURCE_BASE';GameInfo.Resources[6].ResourceType='RESOURCE_SPEC'
GameInfo.Improvements={[10]={ImprovementType='IMPROVEMENT_BASE'},[20]={ImprovementType='IMPROVEMENT_SPEC'}}
GameInfo.Improvement_ValidResources=setmetatable({}, {__call=function()local i=0;local a={{ResourceType='RESOURCE_BASE',ImprovementType='IMPROVEMENT_BASE'},{ResourceType='RESOURCE_SPEC',ImprovementType='IMPROVEMENT_SPEC'}};return function()i=i+1;return a[i]end end})
GameInfo.Buildings=setmetatable({}, {__call=function()return function()return nil end end})
for _,p in pairs(plots)do
 p.imp=p.idx==1 and 10 or p.idx==2 and 20 or -1;p.pillaged=false;p.district=-1
 p.GetImprovementType=function(self)return self.imp end
 p.IsImprovementPillaged=function(self)return self.pillaged end
 p.GetDistrictType=function(self)return self.district end
end
plots[1].owner=7
player.GetCities=function()return {Members=function()return ipairs({city})end}end
Map.GetPlotCount=function()return 4 end
Map.GetAdjacentPlot=function(x,y,direction)local idx=y*2+x;local adj=idx==0 and {1,2}or idx==1 and {0,3}or idx==2 and {0,3}or {1,2};return plots[adj[direction+1]]end
districts.GetNumDistricts=function()return 0 end
city.GetBuildings=function()return {HasBuilding=function()return false end,IsPillaged=function()return false end}end
queue.GetSize=function()return 1 end;queue.GetCurrentProductionTypeHash=function()return 9 end;queue.GetAt=function()return {Hash=9}end
function arm(policy)
 properties.CSC_AI_INVESTMENT_PILOT_V1={version=1,player=7,city=11,city_x=0,city_y=0,quarter='BAKERS',source=3,materials={1,2},material_resources={5,6},start_turn=200,deadline_turn=225,spec_policy=policy or 'ready'}
end
'''

class HostPilot(unittest.TestCase):
 def fixture(self,extra='arm()'):
  lua=LuaRuntime(unpack_returned_tuples=True)
  lua.execute(FIXTURE);lua.execute(EXTRA);lua.execute(extra)
  lua.execute(POLICY);lua.execute(HOST)
  return lua
 def acquire(self,lua):return lua.eval('CSC_AI_Assistance.Acquire(candidate,3,{3})')
 def status(self,lua):return lua.eval('properties.CSC_AI_INVESTMENT_PILOT_STATE_V1.status')
 def test_unconfigured_preserves_existing_purchase_backend(self):
  lua=self.fixture('plots[1].owner=-1')
  self.assertTrue(lua.eval('CSC_AI_Assistance.Acquire(candidate,1,{1,3})'))
  self.assertEqual(lua.globals().wallet,960);self.assertEqual(lua.globals().assignments,1)
 def test_review_and_unknown_configs_suppress_without_arming(self):
  for value in ("{version=1,status='review'}",'{version=1,review=true}',"{version=1}",'false'):
   with self.subTest(value=value):
    lua=self.fixture('properties.CSC_AI_INVESTMENT_PILOT_V1='+value)
    self.assertFalse(self.acquire(lua));self.assertIsNone(lua.eval('properties.CSC_AI_INVESTMENT_PILOT_STATE_V1'))
    self.assertEqual(lua.globals().assignments,0)
    lua.execute('arm()');self.assertTrue(self.acquire(lua))
 def test_direct_non_target_and_other_player_suppressed(self):
  lua=self.fixture()
  for change in ('city=12','player=8','source=0',"quarter='TAILORS'",'materials={2,1}'):
   self.assertFalse(lua.eval('CSC_AI_Assistance.Acquire({player=7,city=11,quarter="BAKERS",source=3,materials={1,2},'+change+'},3,{3})'))
  self.assertEqual(lua.globals().assignments,0)
  self.assertTrue(self.acquire(lua))
 def test_one_target_normal_turn_purchase_then_foundation(self):
  lua=self.fixture();lua.execute('turnHandler(7)')
  self.assertEqual(lua.globals().assignments,1);self.assertEqual(lua.globals().creations,0)
  lua.execute('turn=201;turnHandler(7);turn=202;turnHandler(7)')
  self.assertEqual(lua.globals().creations,1);self.assertEqual(self.status(lua),'observing')
  self.assertFalse(lua.eval('CSC_AI_Assistance.Place(candidate)'))
  self.assertFalse(self.acquire(lua))
 def test_normal_turn_skips_other_players_and_other_cities(self):
  lua=self.fixture('''arm();Players[8]=player
   local other=setmetatable({GetID=function()return 12 end,GetBuildQueue=function()error('non-target queue touched')end},{__index=city})
   player.GetCities=function()return {Members=function()return ipairs({other,city})end}end
  ''')
  lua.execute('turnHandler(8)')
  self.assertEqual(lua.globals().assignments,0)
  lua.execute('turnHandler(7)')
  self.assertEqual(lua.globals().assignments,1)
  self.assertIsNone(lua.eval("properties['CSC_AI_ASSISTANCE_V1_ERROR_7']"))
 def test_working_base_is_rechecked_after_route_investment(self):
  lua=self.fixture();self.assertTrue(self.acquire(lua))
  lua.execute('turn=201;plots[1].pillaged=true;turnHandler(7)')
  self.assertEqual(self.status(lua),'closed');self.assertEqual(lua.globals().creations,0)
  lua.execute('turn=202;plots[1].pillaged=false;turnHandler(7)')
  self.assertEqual(lua.globals().creations,0) # A terminal loss does not auto-rearm.
 def test_observing_survives_cold_module_reload_no_additional_start(self):
  lua=self.fixture();self.acquire(lua);lua.execute('turn=201;CSC_AI_Assistance.Place(candidate)')
  lua.execute(HOST);lua.execute('turn=202;turnHandler(7)')
  self.assertEqual(lua.globals().creations,1);self.assertEqual(self.status(lua),'observing')
 def test_armed_target_survives_cold_module_reload(self):
  lua=self.fixture();self.acquire(lua);lua.execute(HOST)
  lua.execute('turn=201;turnHandler(7)')
  self.assertEqual(lua.globals().assignments,1);self.assertEqual(lua.globals().creations,1)
 def test_deadline_closes_without_more_spending(self):
  lua=self.fixture();self.acquire(lua);lua.execute('turn=226;turnHandler(7)')
  self.assertEqual(self.status(lua),'closed');self.assertEqual(lua.globals().assignments,1)
  self.assertEqual(lua.globals().creations,0)
 def test_material_source_role_and_city_loss_fail_closed(self):
  changes=('plots[1].pillaged=true','plots[1].imp=-1','plots[1].owner=8','plots[1].res=6','plots[1].district=9',
   'plots[2].res=5','plots[2].pillaged=true','plots[3].owner=8','plots[3].imp=10','human=true',
   'city.GetX=function()return 20 end','GameInfo.Improvement_ValidResources=nil',
   'CityManager.GetCity=function()return nil end','plots[1].IsImprovementPillaged=nil')
  for change in changes:
   with self.subTest(change=change):
    lua=self.fixture();lua.execute(change)
    self.assertFalse(self.acquire(lua));self.assertEqual(self.status(lua),'closed')
    self.assertEqual(lua.globals().assignments,0);self.assertEqual(lua.globals().wallet,1000)
 def test_ready_spec_required_but_explicit_conditional_spec_supported(self):
  lua=self.fixture('arm();plots[2].imp=-1')
  self.assertFalse(self.acquire(lua))
  lua=self.fixture("arm('conditional');plots[2].imp=-1")
  self.assertTrue(self.acquire(lua));self.assertEqual(lua.globals().assignments,1)
 def test_changed_config_cannot_retarget_after_first_investment(self):
  lua=self.fixture();self.acquire(lua)
  lua.execute('properties.CSC_AI_INVESTMENT_PILOT_V1.source=0;candidate.source=0;turn=201')
  self.assertFalse(self.acquire(lua));self.assertEqual(self.status(lua),'closed')
  self.assertEqual(lua.globals().assignments,1)
 def test_removed_config_cold_reload_cannot_resume_normal_host(self):
  lua=self.fixture();self.assertTrue(self.acquire(lua))
  lua.execute('properties.CSC_AI_INVESTMENT_PILOT_V1=nil')
  lua.execute(HOST);lua.execute('turn=201;turnHandler(7)')
  self.assertEqual(self.status(lua),'closed');self.assertEqual(lua.globals().creations,0)
  self.assertFalse(self.acquire(lua));self.assertEqual(lua.globals().assignments,1)
 def test_malformed_persisted_state_cannot_rearm_or_enable_legacy(self):
  for value in ('false',"'unknown'",'3'):
   for config in ('arm()', 'properties.CSC_AI_INVESTMENT_PILOT_V1=nil'):
    with self.subTest(value=value,config=config):
     lua=self.fixture(config+';properties.CSC_AI_INVESTMENT_PILOT_STATE_V1='+value)
     self.assertFalse(self.acquire(lua));lua.execute('turnHandler(7)')
     self.assertEqual(lua.globals().assignments,0);self.assertEqual(lua.globals().creations,0)
 def test_existing_foundation_receipt_forces_observation(self):
  lua=self.fixture("arm();properties['CSC_AI_ASSISTANCE_V1_FOUNDATION_7:11:BAKERS:3']={status='requested'}")
  self.assertFalse(self.acquire(lua));self.assertEqual(self.status(lua),'observing')
 def test_ambiguous_native_foundation_failure_stays_one_shot(self):
  lua=self.fixture('arm();plots[3].owner=7;badQueue=true')
  ok,_=lua.eval('pcall(function()CSC_AI_Assistance.Place(candidate)end)')
  self.assertFalse(ok);self.assertEqual(self.status(lua),'observing')
  self.assertFalse(lua.eval('CSC_AI_Assistance.Place(candidate)'))
  self.assertEqual(lua.globals().creations,1)
 def test_other_player_pending_reconciles_under_review_without_resend(self):
  lua=self.fixture('lag=true')
  self.assertTrue(self.acquire(lua));self.assertEqual(lua.globals().wallet,1000)
  lua.execute("properties.CSC_AI_INVESTMENT_PILOT_V1={version=1,status='review'};lag=false;CSC_AI_Assistance.Reconcile();CSC_AI_Assistance.Reconcile()")
  self.assertEqual(lua.globals().wallet,960);self.assertEqual(lua.globals().assignments,1)
 def test_pending_reconciliation_survives_other_target_config(self):
  lua=self.fixture('arm();lag=true');self.acquire(lua)
  lua.execute('properties.CSC_AI_INVESTMENT_PILOT_V1.player=8;lag=false;CSC_AI_Assistance.Reconcile()')
  self.assertEqual(lua.globals().wallet,960);self.assertEqual(lua.globals().assignments,1)
 def test_inspection_is_read_only_includes_native_and_working_materials(self):
  lua=self.fixture("properties.CSC_AI_INVESTMENT_PILOT_V1={version=1,status='review'};writes=0;local old=Game.SetProperty;Game.SetProperty=function(...)writes=writes+1;return old(...)end")
  lua.execute('writes=0') # Ignore the pre-existing host diagnostic migration.
  result=lua.eval('CSC_AI_Assistance.Inspect(7)')
  self.assertIsNone(result.error);self.assertTrue(result.eligible)
  row=result.cities[1];self.assertIsNone(row.error)
  self.assertEqual(row.queue.hash,9);self.assertGreater(len(row.candidates),0)
  candidate=row.candidates[1]
  self.assertTrue(candidate.material_facts[1].working);self.assertTrue(candidate.material_facts[2].working)
  self.assertEqual(candidate.native.cost,45);self.assertEqual(candidate.pilot_input.material_resources[1],5)
  self.assertEqual(lua.globals().writes,0);self.assertEqual(lua.globals().assignments,0);self.assertEqual(lua.globals().creations,0)
 def test_inspection_pillage_stamp_refresh_and_no_fabricated_working(self):
  lua=self.fixture();first=lua.eval('CSC_AI_Assistance.Inspect(7)')
  lua.execute('plots[1].pillaged=true');second=lua.eval('CSC_AI_Assistance.Inspect(7)')
  self.assertNotEqual(first.cities[1].stamp,second.cities[1].stamp)
  self.assertFalse(second.cities[1].candidates[1].material_facts[1].working)
 def test_inspection_existing_quarter_dependency_inventory_and_queue(self):
  lua=self.fixture('''arm();placed=true
   districts.GetNumDistricts=function()return 1 end
   districts.GetDistrictByIndex=function()return {GetType=function()return 3 end,GetX=function()return 1 end,GetY=function()return 1 end,IsComplete=function()return true end,IsPillaged=function()return false end}end
  ''')
  row=lua.eval('CSC_AI_Assistance.Inspect(7)').cities[1]
  self.assertIsNone(row.error);self.assertEqual(len(row.candidates),0)
  self.assertEqual(row.queue.hash,9)
  district=row.districts[1];self.assertFalse(district.pillaged)
  self.assertTrue(district.materials.base[1].working);self.assertTrue(district.materials.spec[1].working)
 def test_inspection_missing_gameplay_queue_keeps_physical_inventory_read_only(self):
  for remove in ('queue.GetSize=nil;queue.GetCurrentProductionTypeHash=nil;queue.GetAt=nil',
   'queue.GetSize=nil','queue.GetCurrentProductionTypeHash=nil','queue.GetAt=nil'):
   with self.subTest(remove=remove):
    lua=self.fixture('''arm();placed=true
     districts.GetNumDistricts=function()return 1 end
     districts.GetDistrictByIndex=function()return {GetType=function()return 3 end,GetX=function()return 1 end,GetY=function()return 1 end,IsComplete=function()return true end,IsPillaged=function()return false end}end
    '''+remove)
    lua.execute('writes=0;local old=Game.SetProperty;Game.SetProperty=function(...)writes=writes+1;return old(...)end')
    row=lua.eval('CSC_AI_Assistance.Inspect(7)').cities[1]
    self.assertIsNone(row.error);self.assertEqual(len(row.candidates),0)
    self.assertGreater(len(row.tiles),0);self.assertIsNone(row.queue)
    self.assertIn('queue_unavailable:',row.queue_error)
    self.assertTrue(row.districts[1].materials.base[1].working)
    self.assertTrue(row.districts[1].materials.spec[1].working)
    self.assertEqual(lua.globals().writes,0);self.assertEqual(lua.globals().assignments,0);self.assertEqual(lua.globals().creations,0)
 def test_inspection_failed_optional_queue_getter_is_queue_error_only(self):
  lua=self.fixture("arm();placed=true;queue.GetSize=function()error('native getter unavailable')end")
  row=lua.eval('CSC_AI_Assistance.Inspect(7)').cities[1]
  self.assertIsNone(row.error);self.assertIsNone(row.queue)
  self.assertIn('native getter unavailable',row.queue_error);self.assertGreater(len(row.tiles),0)
 def test_inspection_exact_ui_candidate_queue_ignores_missing_gameplay_getters(self):
  lua=self.fixture('arm();queue.GetSize=nil;queue.GetCurrentProductionTypeHash=nil;queue.GetAt=nil')
  row=lua.eval('CSC_AI_Assistance.Inspect(7)').cities[1]
  self.assertIsNone(row.error);self.assertIsNone(row.queue_error)
  self.assertGreater(len(row.candidates),0);self.assertEqual(row.queue.hash,9)
  self.assertEqual(row.candidates[1].native.queue.hash,9)
 def test_deadline_and_bound_validation(self):
  lua=self.fixture()
  for update in ('deadline_turn=226','start_turn=201','deadline_turn=199',"spec_policy='unknown'",'material_resources={5}',"quarter='BREWERS'"):
   with self.subTest(update=update):
    lua.execute('arm();properties.CSC_AI_INVESTMENT_PILOT_V1.'+update)
    self.assertFalse(self.acquire(lua));self.assertEqual(lua.globals().assignments,0)

if __name__=='__main__':unittest.main()
