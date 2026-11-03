"""Actual Lua51 admission/state/backend regressions; no game or connection."""
import os
from pathlib import Path
import sys
import unittest
from lupa.lua51 import LuaRuntime

ROOT=Path(os.environ.get('CSC_SCREEN_REPO_ROOT',Path(__file__).resolve().parents[3]))
sys.path.insert(0,str(ROOT/'project/tools/ai_tuning'))
from test_profiles import FIXTURE
from test_host_pilot import EXTRA
AI=Path(os.environ.get('CSC_SCREEN_SOURCE_DIR',ROOT/'Civ Supply Chains/Lua_UI/AI'))
HOST=(AI/'CSC_AI_Assistance.lua').read_text(encoding='utf-8')
POLICY=(AI/'CSC_AI_OpportunityPolicy.lua').read_text(encoding='utf-8')

SCREEN=r'''
hasGranary=false;hasProducer=false;producerPillaged=false;customerPillaged=false;quarterComplete=false;quarterPillaged=false
ccPillaged=true;farmUnlocked=true;reveal=true;baseReach=true;basePrice=40;cityPresent=true
GameInfo.Districts.DISTRICT_CSC_BAKERS_QUARTER.DistrictType='DISTRICT_CSC_BAKERS_QUARTER'
GameInfo.Districts[3]=GameInfo.Districts.DISTRICT_CSC_BAKERS_QUARTER
GameInfo.Districts.DISTRICT_CITY_CENTER={Index=0,DistrictType='DISTRICT_CITY_CENTER'};GameInfo.Districts[0]=GameInfo.Districts.DISTRICT_CITY_CENTER
GameInfo.Buildings={BUILDING_CSC_BAKERS_WIND_MILL={Index=100,BuildingType='BUILDING_CSC_BAKERS_WIND_MILL',PrereqDistrict='DISTRICT_CSC_BAKERS_QUARTER'},
 BUILDING_GRANARY={Index=3,BuildingType='BUILDING_GRANARY',PrereqDistrict='DISTRICT_CITY_CENTER'}}
local function rows(items)return function()local i=0;return function()i=i+1;return items[i]end end end
GameInfo.CSC_QuarterFlowBuildings=rows({{QuarterKey='BAKERS',Stage=2,BuildingType='BUILDING_CSC_BAKERS_WIND_MILL'},{QuarterKey='TAILORS',Stage=2,BuildingType='BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP'}})
GameInfo.CSC_QuarterCustomerBuildings=rows({{QuarterKey='BAKERS',ProducerStage=2,DistrictType='DISTRICT_CITY_CENTER',BuildingType='BUILDING_GRANARY'},{QuarterKey='TAILORS',ProducerStage=2,DistrictType='DISTRICT_HARBOR',BuildingType='BUILDING_LIGHTHOUSE'}})
GameInfo.Improvements.IMPROVEMENT_BASE=GameInfo.Improvements[10];GameInfo.Improvements[10].PrereqTech='TECH_FARM'
GameInfo.Improvements.IMPROVEMENT_SPEC=GameInfo.Improvements[20]
GameInfo.Technologies={TECH_FARM={Index=1}}
player.GetTechs=function()return{HasTech=function()return farmUnlocked end}end
for i=4,7 do local p={idx=i,owner=i==7 and -1 or 7,res=i==5 and 5 or i==6 and 6 or -1,x=2+i%2,y=math.floor((i-4)/2),imp=i==5 and 10 or i==6 and 20 or -1,district=i==4 and 0 or -1,pillaged=false}
 for _,method in ipairs({'GetOwner','GetResourceType','GetX','GetY','GetIndex','GetImprovementType','GetDistrictType','IsImprovementPillaged','GetFeatureType'})do p[method]=plots[1][method]end
 plots[i]=p
end
plots[0].district=0
Map.GetPlotCount=function()return 8 end
Map.GetPlot=function(x,y)for _,p in pairs(plots)do if p.x==x and p.y==y then return p end end end
Map.GetAdjacentPlot=function(x,y,direction)
 local index=Map.GetPlot(x,y).idx;local offset=index>=4 and 4 or 0;local n=index-offset
 local near=n==3 and{0,1,2}or n==0 and{1,2,3}or n==1 and{0,3}or{0,3}
 return near[direction+1]and plots[offset+near[direction+1]]or nil
end
PlayersVisibility[7].IsRevealed=function(self,x,y)return reveal and not(baseHidden and x==1 and y==0)end
WorldBuilder.CityManager=function()return{SetPlotOwner=function(self,x,y,pid,cid)assignments=assignments+1;if assignmentFails then error('assignment rejected')end;Map.GetPlot(x,y).owner=pid end}end
local cc={GetType=function()return 0 end,GetX=function()return 0 end,GetY=function()return 0 end,IsComplete=function()return true end,IsPillaged=function()return ccPillaged end}
local q={GetType=function()return 3 end,GetX=function()return 1 end,GetY=function()return 1 end,IsComplete=function()return quarterComplete end,IsPillaged=function()return quarterPillaged end}
districts.GetNumDistricts=function()return placed and 2 or 1 end
districts.GetDistrictByIndex=function(self,i)return i==0 and cc or q end
districts.GetDistrictAtLocation=function(self,x,y)if x==0 and y==0 then return cc end;if placed then return q end end
city.GetBuildings=function()return{HasBuilding=function(self,index)return index==100 and hasProducer or index==3 and hasGranary or false end,IsPillaged=function(self,index)return index==100 and producerPillaged or index==3 and customerPillaged or false end}end
local cc2={GetType=function()return 0 end,GetX=function()return 2 end,GetY=function()return 0 end,IsComplete=function()return true end,IsPillaged=function()return ccPillaged end}
local ds2={HasDistrict=function()return false end,GetNumDistricts=function()return 1 end,GetDistrictByIndex=function()return cc2 end,GetDistrictAtLocation=function()return cc2 end}
city2=setmetatable({GetID=function()return 12 end,GetX=function()return 2 end,GetY=function()return 0 end,GetDistricts=function()return ds2 end,GetBuildings=function()return{HasBuilding=function()return false end,IsPillaged=function()return false end}end},{__index=city})
player.GetCities=function()return{Members=function()return ipairs(cityPresent and{city,city2}or{city2})end}end
CityManager.GetCity=function(pid,cid)assert(pid==7);if cid==11 then return cityPresent and city or nil end;if cid==12 then return city2 end end
local read=ExposedMembers.CSC_AI_AssistanceUI.Read
ExposedMembers.CSC_AI_AssistanceUI.Read=function(pid,cid,q,source,index,exact)
 local f=read(pid,cid,q,source,index,exact);f.city=plots[index].owner==7 and(index>=4 and 12 or 11)or -1
 if index==1 then f.reach=baseReach;f.price=basePrice end
 if index==1 and baseQuoteStale then f.turn=turn-3 end
 return f
end
ExposedMembers.CSC_AI_AssistanceUI.Owner=function(index)if lag then return -1,-1,-1 end;return plots[index].owner,7,index>=4 and 12 or 11 end
queue.CreateIncompleteDistrict=function(self,index,source,progress)assert(index==3 and source==3 and progress==0);creations=creations+1;placed=true;plots[3].district=3 end
other={player=7,city=12,quarter='BAKERS',source=7,materials={5,6},base=1,spec=1,missing=1}
function enable()properties.CSC_AI_SELECTIVE_SCREEN_V1={version=1}end
function inspect()return CSC_AI_Assistance.InspectScreen(7)end
'''

class SelectiveScreen(unittest.TestCase):
 def make(self,setup='enable()',host=HOST,policy=POLICY):
  lua=LuaRuntime(unpack_returned_tuples=True);lua.execute(FIXTURE);lua.execute(EXTRA);lua.execute(SCREEN);lua.execute(setup)
  lua.execute(policy);lua.execute(host);return lua
 def acquire(self,lua):return lua.eval('CSC_AI_Assistance.Acquire(candidate,3,{3})')
 def start(self,lua):
  self.assertTrue(self.acquire(lua));lua.execute('turn=201');self.assertTrue(lua.eval('CSC_AI_Assistance.Place(candidate)'))
 def row(self,lua):return lua.eval('inspect().records[1]')
 def test_default_nil_keeps_economics_and_no_screen_state(self):
  lua=self.make('');self.assertTrue(self.acquire(lua));lua.execute('turn=201;CSC_AI_Assistance.Place(candidate)')
  self.assertEqual((lua.globals().assignments,lua.globals().creations,lua.globals().wallet),(1,1,960))
  self.assertIsNone(lua.eval('properties.CSC_AI_SELECTIVE_SCREEN_STATE_V1'));self.assertEqual(lua.eval('inspect().mode'),'legacy')
 def test_default_nil_exact_action_property_and_receipt_parity(self):
  before_host=(AI/'before-CSC_AI_Assistance.lua')
  before_policy=(AI/'before-CSC_AI_OpportunityPolicy.lua')
  if not before_host.exists():
   before_dir=Path(os.environ.get('CSC_SCREEN_BEFORE_DIR',AI))
   before_host=before_dir/'before-CSC_AI_Assistance.lua';before_policy=before_dir/'before-CSC_AI_OpportunityPolicy.lua'
  if not before_host.exists():self.skipTest('Set CSC_SCREEN_BEFORE_DIR to the archived before-source pair for differential receipt check')
  def run(host,policy,setup,actions):
   lua=self.make(setup,host=host,policy=policy)
   lua.execute(actions)
   return lua.eval('properties'),lua.globals()
  def plain(v):
   if hasattr(v,'items'):return {k:plain(value)for k,value in v.items()}
   return v
  for setup,actions in (
   ('','turnHandler(7);turn=201;turnHandler(7)'),
   ('wallet=50','CSC_AI_Assistance.Acquire(candidate,3,{3});turn=201;CSC_AI_Assistance.Place(candidate)'),
   ('lag=true','CSC_AI_Assistance.Acquire(candidate,3,{3});lag=false;CSC_AI_Assistance.Reconcile();CSC_AI_Assistance.Reconcile()'),
   ('wallet=0;subsidy=false','CSC_AI_Assistance.Acquire(candidate,3,{3})')):
   old,og=run(before_host.read_text(),before_policy.read_text(),setup,actions)
   new,ng=run(HOST,POLICY,setup,actions)
   self.assertEqual(plain(old),plain(new))
   self.assertEqual((og.assignments,og.creations,og.wallet,plain(og.goldChanges)),(ng.assignments,ng.creations,ng.wallet,plain(ng.goldChanges)))
 def test_missing_chain_registry_or_stage2_definition_is_unknown(self):
  for setup in ('GameInfo.CSC_QuarterFlowBuildings=nil','GameInfo.CSC_QuarterCustomerBuildings=nil',"GameInfo.Buildings.BUILDING_CSC_BAKERS_WIND_MILL=nil"):
   lua=self.make('enable();'+setup);self.assertFalse(self.acquire(lua));self.assertEqual(lua.globals().assignments,0)
 def test_pending_reconciliation_ignores_malformed_config(self):
  for config in ('false','{version=2}','{version=1,extra=true}'):
   lua=self.make('enable();lag=true');self.assertTrue(self.acquire(lua))
   lua.execute('properties.CSC_AI_SELECTIVE_SCREEN_V1='+config+';lag=false;CSC_AI_Assistance.Reconcile();CSC_AI_Assistance.Reconcile()')
   self.assertEqual(lua.globals().wallet,960);self.assertEqual(lua.globals().assignments,1)
 def test_cap_is_checked_after_affordability_no_false_claim(self):
  lua=self.make('enable();wallet=0;subsidy=false');self.assertFalse(self.acquire(lua))
  self.assertIsNone(lua.eval('properties.CSC_AI_SELECTIVE_SCREEN_STATE_V1'))
  lua.execute('wallet=1000;turn=201')
  self.assertTrue(lua.eval('CSC_AI_Assistance.Acquire(other,7,{7})'));self.assertEqual(lua.eval('inspect().summary.open'),1)
 def test_one_open_claim_blocks_other_site_but_can_resume(self):
  lua=self.make();self.assertTrue(self.acquire(lua));lua.execute('turn=201')
  self.assertFalse(lua.eval('CSC_AI_Assistance.Acquire(other,7,{7})'))
  self.assertTrue(lua.eval('CSC_AI_Assistance.Place(candidate)'));self.assertEqual(lua.eval('inspect().summary.open'),1)
 def test_normal_turn_screen_limits_new_start_to_one_city(self):
  lua=self.make();lua.execute('turnHandler(7)');self.assertEqual(lua.globals().assignments,1)
  lua.execute('turn=201;turnHandler(7)');self.assertEqual(lua.globals().creations,1)
  self.assertEqual(lua.eval('inspect().summary.open'),1)
 def test_unaffordable_or_unknown_quote_never_claims_slot(self):
  for setup in ('wallet=0;subsidy=false','basePrice=0;plots[1].owner=-1'):
   lua=self.make('enable();'+setup)
   if lua.globals().plots[1].owner==-1:result=lua.eval('CSC_AI_Assistance.Acquire(candidate,3,{3,1})')
   else:result=self.acquire(lua)
   self.assertFalse(result);self.assertEqual(lua.globals().assignments,0)
   self.assertEqual(lua.eval('inspect().summary.open'),0)
 def test_future_owned_Base_is_projection_not_working_or_Builder_proof(self):
  lua=self.make('enable();plots[1].imp=-1');self.assertTrue(self.acquire(lua));row=self.row(lua)
  self.assertFalse(row.admission.working_base);self.assertEqual(row.admission.development.status,'PROJECTION')
  self.assertEqual(row.admission.development.Builder_commitment,'UNOBSERVED')
 def test_future_unowned_Base_requires_fresh_backend_capture_evidence(self):
  for reach,expected in ((False,False),(True,True)):
   lua=self.make('enable();plots[1].owner=-1;plots[1].imp=-1;baseReach='+str(reach).lower())
   result=lua.eval('CSC_AI_Assistance.Acquire(candidate,3,{3,1})');self.assertEqual(result,expected)
   if expected:self.assertEqual(self.row(lua).admission.development.capture,'fresh_native_reach_and_quote')
 def test_stale_future_Base_quote_is_not_capture_certainty(self):
  lua=self.make('enable();plots[1].owner=-1;plots[1].imp=-1;baseQuoteStale=true')
  self.assertFalse(lua.eval('CSC_AI_Assistance.Acquire(candidate,3,{3,1})'));self.assertEqual(lua.globals().assignments,0)
 def test_locked_or_unknown_native_improvement_option_is_not_credited(self):
  for setup in ('farmUnlocked=false','GameInfo.Improvement_ValidResources=nil',"GameInfo.Improvements.IMPROVEMENT_BASE.TraitType='UNPROVED_TRAIT'"):
   lua=self.make('enable();plots[1].imp=-1;'+setup);self.assertFalse(self.acquire(lua));self.assertEqual(lua.globals().assignments,0)
 def test_operational_structural_release_allows_next_chain_without_Stage4(self):
  lua=self.make();self.start(lua);lua.execute('quarterComplete=true;hasProducer=true;hasGranary=true;turn=202')
  self.assertEqual(lua.eval('inspect().summary.operational'),1)
  self.assertTrue(lua.eval('CSC_AI_Assistance.Acquire(other,7,{7})'));self.assertEqual(lua.eval('inspect().summary.open'),1)
 def test_Tailors_registry_releases_only_with_workshop_and_Lighthouse(self):
  setup="""enable();ccPillaged=false
   local d=GameInfo.Districts.DISTRICT_CSC_BAKERS_QUARTER;d.DistrictType='DISTRICT_CSC_TAILORS_QUARTER'
   GameInfo.Districts.DISTRICT_CSC_TAILORS_QUARTER=d;GameInfo.Districts.DISTRICT_CSC_BAKERS_QUARTER=nil
   GameInfo.Districts.DISTRICT_HARBOR={Index=0,DistrictType='DISTRICT_HARBOR'};GameInfo.Districts[0]=GameInfo.Districts.DISTRICT_HARBOR
   GameInfo.Buildings.BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP={Index=100,BuildingType='BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP',PrereqDistrict='DISTRICT_CSC_TAILORS_QUARTER'}
   GameInfo.Buildings.BUILDING_LIGHTHOUSE={Index=3,BuildingType='BUILDING_LIGHTHOUSE',PrereqDistrict='DISTRICT_HARBOR'}
   GameInfo.TypeTags=function()local i=0;local tags={{Type=5,Tag='CLASS_CSC_TAILORS_BASE'},{Type=6,Tag='CLASS_CSC_TAILORS_SPEC'}};return function()i=i+1;return tags[i]end end
   candidate.quarter='TAILORS';other.quarter='TAILORS'
  """
  lua=self.make(setup);self.start(lua);lua.execute('quarterComplete=true;hasProducer=true;turn=202')
  self.assertEqual(lua.eval('inspect().summary.open'),1)
  lua.execute('hasGranary=true');self.assertEqual(lua.eval('inspect().summary.operational'),1)
  lua.execute('customerPillaged=true');self.assertEqual(lua.eval('inspect().summary.open'),1)
 def test_customer_shell_or_pillaged_building_does_not_release(self):
  for setup in ('hasGranary=false','hasGranary=true;customerPillaged=true','hasGranary=true;producerPillaged=true'):
   lua=self.make();self.start(lua);lua.execute('quarterComplete=true;hasProducer=true;turn=202;'+setup)
   self.assertFalse(lua.eval('CSC_AI_Assistance.Acquire(other,7,{7})'));self.assertEqual(lua.eval('inspect().summary.operational'),0)
 def test_maintenance_blocks_new_starts_then_native_repair_releases(self):
  lua=self.make();self.start(lua);lua.execute('quarterComplete=true;hasProducer=true;hasGranary=true;plots[5].imp=-1;farmUnlocked=false;turn=202;turnHandler(7)')
  lua.execute('farmUnlocked=true;turn=203;plots[1].pillaged=true')
  self.assertFalse(lua.eval('CSC_AI_Assistance.Acquire(other,7,{7})'));self.assertEqual(lua.eval('inspect().summary.maintenance'),1)
  lua.execute('turn=204;plots[1].pillaged=false');self.assertTrue(lua.eval('CSC_AI_Assistance.Acquire(other,7,{7})'))
 def test_fully_known_Base_resource_loss_is_failed_sunk_cost_retained(self):
  lua=self.make();self.start(lua);lua.execute('plots[1].res=-1;turn=202')
  self.assertEqual(lua.eval('inspect().summary.failed_sunk'),1);self.assertEqual(self.row(lua).cost,40)
  self.assertTrue(lua.eval('CSC_AI_Assistance.Acquire(other,7,{7})'));self.assertFalse(lua.eval('CSC_AI_Assistance.Place(candidate)'))
 def test_unknown_or_foreign_Base_is_not_terminal_failure(self):
  for setup in ('baseHidden=true','plots[1].owner=8'):
   lua=self.make();self.start(lua);lua.execute('turn=202;'+setup)
   self.assertEqual(lua.eval('inspect().summary.unknown'),1);self.assertEqual(lua.eval('inspect().summary.failed_sunk'),0)
   self.assertFalse(lua.eval('CSC_AI_Assistance.Acquire(other,7,{7})'))
 def test_city_capture_is_failed_sunk_no_replay(self):
  lua=self.make();self.assertTrue(self.acquire(lua));lua.execute('cityPresent=false;turn=201')
  self.assertEqual(lua.eval('inspect().summary.failed_sunk'),1)
  self.assertTrue(lua.eval('CSC_AI_Assistance.Acquire(other,7,{7})'))
  lua.execute('cityPresent=true;turn=202');self.assertFalse(lua.eval('CSC_AI_Assistance.Place(candidate)'))
 def test_source_capture_before_foundation_never_recreates_after_return(self):
  lua=self.make();self.assertTrue(self.acquire(lua));lua.execute('plots[3].owner=8;turn=201')
  self.assertEqual(lua.eval('inspect().summary.failed_sunk'),1)
  self.assertTrue(lua.eval('CSC_AI_Assistance.Acquire(other,7,{7})'))
  lua.execute('plots[3].owner=7;turn=202');self.assertFalse(lua.eval('CSC_AI_Assistance.Place(candidate)'));self.assertEqual(lua.globals().creations,0)
 def test_covered_Base_failure_and_native_rehabilitation_keep_sunk_history(self):
  lua=self.make();self.start(lua);lua.execute('plots[1].district=2;turn=202')
  self.assertTrue(lua.eval('CSC_AI_Assistance.Acquire(other,7,{7})'))
  self.assertEqual(lua.eval('inspect().summary.failed_sunk'),1)
  lua.execute('plots[1].district=-1;quarterComplete=true;hasProducer=true;hasGranary=true;turn=203')
  self.assertEqual(lua.eval('inspect().summary.rehabilitated'),1);self.assertEqual(lua.eval('inspect().summary.failed_sunk'),1)
  self.assertEqual(self.row(lua).cost,40);self.assertFalse(lua.eval('CSC_AI_Assistance.Place(candidate)'))
 def test_other_original_AI_commitment_is_not_a_global_veto(self):
  lua=self.make("enable();properties.CSC_AI_SELECTIVE_SCREEN_STATE_V1={version=1,records={['8:13:BAKERS:99']={player=8,city=13,quarter='BAKERS',source=99,city_x=0,city_y=0,first_turn=200,status='open',materials={98,97}}},decisions={}}")
  self.assertTrue(self.acquire(lua));self.assertEqual(lua.eval("properties.CSC_AI_SELECTIVE_SCREEN_STATE_V1.records['8:13:BAKERS:99'].status"),'open')
 def test_malformed_config_state_and_numeric_original_human_fail_closed(self):
  for setup in ("properties.CSC_AI_SELECTIVE_SCREEN_V1={version=2}","properties.CSC_AI_SELECTIVE_SCREEN_STATE_V1=false", "properties.CSC_AI_SELECTIVE_SCREEN_V1={version=1,extra=true}","properties.CSC_AI_ASSISTANCE_V1_INITIAL_HUMANS={[0]=true,[7]=true}","properties.CSC_AI_ASSISTANCE_V1_INITIAL_HUMANS={}"):
   lua=self.make('enable();'+setup);self.assertFalse(self.acquire(lua));self.assertEqual(lua.globals().assignments,0)
 def test_direct_unique_customer_building_is_eligible(self):
  setup="""enable();GameInfo.Buildings.BUILDING_UNIQUE_GRANARY={Index=30,BuildingType='BUILDING_UNIQUE_GRANARY',PrereqDistrict='DISTRICT_CITY_CENTER'}
   GameInfo.BuildingReplaces=function()local done=false;return function()if not done then done=true;return{ReplacesBuildingType='BUILDING_GRANARY',CivUniqueBuildingType='BUILDING_UNIQUE_GRANARY'}end end end
   local old=city.GetBuildings;city.GetBuildings=function()local b=old();local has=b.HasBuilding;b.HasBuilding=function(self,index)return index==30 or has(self,index)end;return b end
  """
  lua=self.make(setup);self.start(lua);lua.execute('quarterComplete=true;hasProducer=true;turn=202')
  self.assertEqual(lua.eval('inspect().summary.operational'),1)
 def test_actual_customer_building_in_direct_unique_district_is_eligible(self):
  setup="""enable();ccPillaged=false
   GameInfo.Districts.DISTRICT_UNIQUE_CENTER={Index=0,DistrictType='DISTRICT_UNIQUE_CENTER'}
   GameInfo.Districts.DISTRICT_CITY_CENTER.Index=9;GameInfo.Districts[0]=GameInfo.Districts.DISTRICT_UNIQUE_CENTER
   GameInfo.DistrictReplaces=function()local done=false;return function()if not done then done=true;return{ReplacesDistrictType='DISTRICT_CITY_CENTER',CivUniqueDistrictType='DISTRICT_UNIQUE_CENTER'}end end end
  """
  lua=self.make(setup);self.start(lua);lua.execute('quarterComplete=true;hasProducer=true;hasGranary=true;turn=202')
  self.assertEqual(lua.eval('inspect().summary.operational'),1)
 def test_pending_reconciliation_ignores_screen_cap_and_missing_config(self):
  lua=self.make('enable();lag=true');self.assertTrue(self.acquire(lua));lua.execute('properties.CSC_AI_SELECTIVE_SCREEN_V1=nil;lag=false;CSC_AI_Assistance.Reconcile();CSC_AI_Assistance.Reconcile()')
  self.assertEqual(lua.globals().wallet,960);self.assertEqual(lua.globals().assignments,1)
 def test_config_disappearance_and_cold_load_keep_records_fail_closed(self):
  lua=self.make();self.assertTrue(self.acquire(lua));lua.execute('properties.CSC_AI_SELECTIVE_SCREEN_V1=nil;turn=201');lua.execute(HOST)
  self.assertFalse(lua.eval('CSC_AI_Assistance.Acquire(other,7,{7})'));self.assertEqual(lua.eval('inspect().mode'),'missing_config')
  self.assertEqual(lua.eval('inspect().summary.open'),1)
 def test_inspection_has_no_Game_property_or_record_mutation(self):
  lua=self.make();self.start(lua);lua.execute('quarterComplete=true;hasProducer=true;hasGranary=true;writes=0;local old=Game.SetProperty;Game.SetProperty=function(...)writes=writes+1;return old(...)end')
  self.assertEqual(lua.eval('inspect().summary.operational'),1);self.assertEqual(lua.globals().writes,0)
  self.assertEqual(lua.eval("properties.CSC_AI_SELECTIVE_SCREEN_STATE_V1.records['7:11:BAKERS:3'].status"),'open')
 def test_compatible_material_sharing_and_conflicting_sources(self):
  lua=self.make();policy=lua.globals().CSC_AI_OpportunityPolicy
  records=lua.table_from({'7:11:BAKERS:3':dict(player=7,city=11,quarter='BAKERS',source=3,materials=[1,2],status='operational')},recursive=True)
  compatible=lua.table_from(dict(player=7,city=12,quarter='BAKERS',source=7,materials=[1,6]),recursive=True)
  self.assertIsNone(policy.ScreenConflicts(compatible,records,lua.table()))
  compatible.source=1;self.assertEqual(policy.ScreenConflicts(compatible,records,lua.table()),'source_over_committed_material')
 def test_record_iteration_order_cannot_change_cap_admission(self):
  for reverse in (False,True):
   lua=self.make();self.start(lua);lua.execute('turn=202')
   rows="local s=properties.CSC_AI_SELECTIVE_SCREEN_STATE_V1;local original=s.records['7:11:BAKERS:3'];local other={player=8,city=13,quarter='BAKERS',source=99,city_x=0,city_y=0,first_turn=200,status='open',materials={98,97}};s.records={};"
   first="s.records['7:11:BAKERS:3']=original;";second="s.records['8:13:BAKERS:99']=other;"
   lua.execute(rows+(second+first if reverse else first+second))
   self.assertFalse(lua.eval('CSC_AI_Assistance.Acquire(other,7,{7})'));self.assertEqual(lua.globals().assignments,1)
 def test_malformed_saved_records_fail_closed_before_player_filtering(self):
  for value in ('{}',"{player=8}","{player=8,city=13,quarter='BAKERS',source=99,city_x=0,city_y=0,first_turn=200,status='open',materials={98,97}}"):
   lua=self.make('enable();properties.CSC_AI_SELECTIVE_SCREEN_STATE_V1={version=1,records={bad='+value+'},decisions={}}')
   self.assertFalse(self.acquire(lua));self.assertEqual(lua.globals().assignments,0)
   self.assertEqual(lua.eval('inspect().error'),'screen_record_invalid')
 def test_invalid_saved_record_identity_fields_and_status_fail_closed(self):
  for change in ("player=nil", "city=-1", "source=1.5", "city_x=nil", "city_y=false", "first_turn=nil", "materials={1}", "materials={1,'2'}", "quarter='UNKNOWN'", "status='done'"):
   lua=self.make();self.assertTrue(self.acquire(lua));lua.execute("local r=properties.CSC_AI_SELECTIVE_SCREEN_STATE_V1.records['7:11:BAKERS:3'];r."+change+';turn=201')
   self.assertFalse(lua.eval('CSC_AI_Assistance.Acquire(other,7,{7})'));self.assertEqual(lua.globals().assignments,1)
 def test_malformed_saved_decisions_fail_closed(self):
  for value in ("{bad={}}", "{['7']={turn=200}}", "{['7']={turn=200,reason='x',rejected=false}}", "{['7']={turn=200,reason='x',site=3}}"):
   lua=self.make('enable();properties.CSC_AI_SELECTIVE_SCREEN_STATE_V1={version=1,records={},decisions='+value+'}')
   self.assertFalse(self.acquire(lua));self.assertEqual(lua.globals().assignments,0)
   self.assertEqual(lua.eval('inspect().error'),'screen_decision_invalid')
 def test_pending_reconciliation_ignores_malformed_saved_records_and_decisions(self):
  for field,value in (('records','{bad={}}'),('decisions','{bad={}}')):
   lua=self.make('enable();lag=true');self.assertTrue(self.acquire(lua))
   lua.execute('properties.CSC_AI_SELECTIVE_SCREEN_STATE_V1.'+field+'='+value+';lag=false;CSC_AI_Assistance.Reconcile();CSC_AI_Assistance.Reconcile();turn=201')
   self.assertEqual(lua.globals().wallet,960);self.assertEqual(lua.globals().assignments,1)
   self.assertFalse(lua.eval('CSC_AI_Assistance.Acquire(other,7,{7})'));self.assertEqual(lua.globals().assignments,1)
 def test_ranking_is_deterministic_without_weight_changes(self):
  lua=self.make();p=lua.globals().CSC_AI_OpportunityPolicy
  a=dict(working_base=True,existing_customer=False,base=1,spec=1,fresh_price=40,missing=1,source=3,materials=[1,2])
  b=dict(a,working_base=False,existing_customer=True,fresh_price=0,source=7,materials=[5,6])
  self.assertTrue(p.ScreenBetter(lua.table_from(a,recursive=True),lua.table_from(b,recursive=True)))
  b=dict(a,fresh_price=20,source=7,materials=[5,6]);self.assertTrue(p.ScreenBetter(lua.table_from(b,recursive=True),lua.table_from(a,recursive=True)))

if __name__=='__main__':unittest.main()
