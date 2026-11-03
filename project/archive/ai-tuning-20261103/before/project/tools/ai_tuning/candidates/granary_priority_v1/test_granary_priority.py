"""Actual Lua51 predicate/callback and read-only-native-DB SQL fixtures."""
import collections
import os
from pathlib import Path
import re
import sqlite3
import unittest
import zlib
from lupa.lua51 import LuaRuntime

HERE=Path(__file__).resolve().parent
LUA=(HERE/'granary_priority.lua').read_text(encoding='utf-8')
SQL=(HERE/'granary_priority.sql').read_text(encoding='utf-8')
ROOT=Path(os.environ.get('CSC_GRANARY_REPO_ROOT',Path(__file__).resolve().parents[5]))
STRATEGY='STRATEGY_CSC_AI_GRANARY_PRIORITY_V1';LIST='CSC_AI_GranaryPriority_V1'
FIXTURE=r'''
function rows(values,key)
 local result={};for _,v in ipairs(values)do if v.Index then result[v.Index]=v end;if key and v[key]then result[v[key]]=v end end
 return setmetatable(result,{__call=function()local i=0;return function()i=i+1;return values[i]end end})
end
turn=110;mode='RH';roles={['0']=true};flag=nil;writes=0;alive=true;major=true
cityOwner=3;sourceOwner=3;sourceType=36;quarterComplete=true;quarterPillaged=false
hasWind=true;hasWater=false;millPillaged=false;granaryPresent=false;pottery=true
centerOwner=3;centerComplete=true;adjacent=true;baseOwner=3;baseDistrict=-1;baseImprovement=10;basePillaged=false;revealed=true;revealTech=true;revealCivic=true
Game={GetCurrentGameTurn=function()return turn end}
function Game:GetProperty(k)if k=='CSC_AI_GRANARY_PRIORITY_V1'then return flag end;if k=='CSC_AI_ASSISTANCE_V1_INITIAL_HUMANS'then return roles end end
function Game:SetProperty()writes=writes+1;error('Candidate must not write Game properties')end
function arm()flag={version=1,player=3,city=196610,source=2711,start_turn=110,deadline_turn=131}end
GameInfo={}
GameInfo.CSC_AI_Profile=function()local done=false;return function()if not done then done=true;return{Id='ACTIVE',Mode=mode}end end end
GameInfo.Districts=rows({{Index=36,DistrictType='DISTRICT_CSC_BAKERS_QUARTER'},{Index=0,DistrictType='DISTRICT_CITY_CENTER'}},'DistrictType')
GameInfo.Buildings=rows({{Index=3,BuildingType='BUILDING_GRANARY'},{Index=100,BuildingType='BUILDING_CSC_BAKERS_WIND_MILL',PrereqDistrict='DISTRICT_CSC_BAKERS_QUARTER'},{Index=101,BuildingType='BUILDING_CSC_BAKERS_WATER_MILL',PrereqDistrict='DISTRICT_CSC_BAKERS_QUARTER'}},'BuildingType')
GameInfo.Technologies=rows({{Index=1,TechnologyType='TECH_POTTERY'},{Index=2,TechnologyType='TECH_REVEAL'}},'TechnologyType')
GameInfo.Civics=rows({{Index=4,CivicType='CIVIC_REVEAL'}},'CivicType')
GameInfo.Resources=rows({{Index=5,ResourceType='RESOURCE_FLAX'}},'ResourceType')
GameInfo.Improvements=rows({{Index=10,ImprovementType='IMPROVEMENT_FARM'},{Index=11,ImprovementType='IMPROVEMENT_MINE'}},'ImprovementType')
GameInfo.TypeTags=rows({{Type='RESOURCE_FLAX',Tag='CLASS_CSC_BAKERS_BASE'}})
GameInfo.Improvement_ValidResources=rows({{ResourceType='RESOURCE_FLAX',ImprovementType='IMPROVEMENT_FARM'}})
player={IsAlive=function()return alive end,IsMajor=function()return major end,IsHuman=function()error('Current human flag is forbidden')end,
 GetTechs=function()return{HasTech=function(self,i)if i==1 then return pottery end;return revealTech end}end,
 GetCulture=function()return{HasCivic=function()return revealCivic end}end}
Players={[3]=player};PlayersVisibility={[3]={IsRevealed=function()return revealed end}}
source={GetOwner=function()return sourceOwner end,GetDistrictType=function()return sourceType end,GetX=function()return 47 end,GetY=function()return 36 end}
center={GetOwner=function()return centerOwner end,GetDistrictType=function()return 0 end,GetIndex=function()return 2710 end,GetX=function()return 46 end,GetY=function()return 36 end}
base={GetOwner=function()return baseOwner end,GetDistrictType=function()return baseDistrict end,GetResourceType=function()return 5 end,GetImprovementType=function()return baseImprovement end,IsImprovementPillaged=function()return basePillaged end,GetIndex=function()return 2636 end,GetX=function()return 46 end,GetY=function()return 35 end}
quarter={GetType=function()return sourceType end,IsComplete=function()return quarterComplete end,IsPillaged=function()return quarterPillaged end}
cc={GetType=function()return 0 end,IsComplete=function()return centerComplete end,IsPillaged=function()return true end}
districts={GetDistrictAtLocation=function(self,x,y)if x==47 then return quarter end;return cc end}
buildings={HasBuilding=function(self,i)if i==3 then return granaryPresent end;if i==100 then return hasWind end;if i==101 then return hasWater end;return false end,IsPillaged=function()return millPillaged end}
city={GetOwner=function()return cityOwner end,GetX=function()return 46 end,GetY=function()return 36 end,GetDistricts=function()return districts end,GetBuildings=function()return buildings end,GetBuildQueue=function()error('No queue API')end}
CityManager={GetCity=function(pid,cid)assert(pid==3 and cid==196610);return city end}
directions={};neighborCalls=0
Map={GetPlotByIndex=function(idx)assert(idx==2711);return source end,GetPlot=function()return center end,
 GetAdjacentPlot=function(x,y,direction)assert(x==47 and y==36 and direction>=0 and direction<=5);directions[direction]=(directions[direction]or 0)+1;neighborCalls=neighborCalls+1;if direction==0 then return base end end,
 GetPlotDistance=function()return adjacent and 1 or 2 end}
ExposedMembers={CSC_AI_AssistanceUI=setmetatable({},{__index=function()error('No UI roundtrip')end})}
GameEvents={CSC_AI_GranaryPriority_V1={Add=function(fn)callback=fn end}}
print=function()end
'''

class LuaPredicate(unittest.TestCase):
 def make(self,setup='arm()'):
  lua=LuaRuntime(unpack_returned_tuples=True);lua.execute(FIXTURE);lua.execute(setup);lua.execute(LUA);return lua
 def inspect(self,lua):return lua.eval('ExposedMembers.CSC_AI_GranaryPriority.Inspect(3)')
 def test_default_nil_inactive_and_registered_without_callbacks(self):
  lua=self.make('');data=self.inspect(lua)
  self.assertFalse(data.predicate.active);self.assertEqual(data.predicate.reason,'flag_inactive')
  self.assertEqual(data.status.registered,1);self.assertEqual(data.status.calls,0)
 def test_valid_callback_only_counts_actual_calls(self):
  lua=self.make();self.assertTrue(lua.eval('callback(3,0)'));status=self.inspect(lua).status
  self.assertEqual((status.calls,status.true_calls,status.false_calls),(1,1,0))
  self.assertEqual(status.callback_forms['2'],1);self.assertEqual(status.last_callback.arguments[1].value,3)
  self.assertIn('UNOBSERVED',status.stopped_notifications);self.assertEqual(lua.globals().writes,0)
 def test_inspect_is_pure_and_detached(self):
  lua=self.make();first=self.inspect(lua);self.assertTrue(first.predicate.active)
  first.flag.city=0;first.status.registered=999
  second=self.inspect(lua);self.assertEqual(second.flag.city,196610);self.assertEqual(second.status.registered,1)
  self.assertEqual(second.status.calls,0);self.assertEqual(len(second.status.transitions),0);self.assertEqual(lua.globals().writes,0)
 def test_exact_flag_and_only_target_player(self):
  for change in ('flag.version=2','flag.player=4','flag.city=1','flag.source=2710','flag.start_turn=109','flag.deadline_turn=132','flag=false'):
   with self.subTest(change=change):self.assertFalse(self.make('arm();'+change).eval('callback(3,0)'))
  self.assertFalse(self.make().eval('callback(4,0)'))
 def test_original_role_mask_must_prove_observer_and_exclude_target(self):
  for setup in ('roles=nil','roles={}',"roles={['0']=false}","roles={['0']=true,['3']=true}",'roles={[0]=true,[3]=true}'):
   with self.subTest(setup=setup):self.assertFalse(self.make('arm();'+setup).eval('callback(3,0)'))
  self.assertTrue(self.make('arm();roles={[0]=true}').eval('callback(3,0)'))
 def test_RH_alive_major_only_without_current_human_read(self):
  for setup in ("mode='BASIC'","mode='OFF'",'alive=false','major=false'):
   self.assertFalse(self.make('arm();'+setup).eval('callback(3,0)'))
  self.assertTrue(self.make().eval('callback(3,0)'))
 def test_source_producer_and_customer_guards_fail_closed(self):
  for setup in ('cityOwner=4','sourceOwner=4','sourceType=37','quarterComplete=false','quarterPillaged=true',
                'hasWind=false','millPillaged=true','centerOwner=4','centerComplete=false','adjacent=false','granaryPresent=true','pottery=false'):
   with self.subTest(setup=setup):self.assertFalse(self.make('arm();'+setup).eval('callback(3,0)'))
  self.assertTrue(self.make('arm();hasWind=false;hasWater=true').eval('callback(3,0)'))
 def test_working_Base_requires_exact_native_improvement_mapping(self):
  for setup in ('baseOwner=4','baseDistrict=2','baseImprovement=-1','baseImprovement=11','basePillaged=true',
                "GameInfo.TypeTags=rows({})","GameInfo.Improvement_ValidResources=rows({})"):
   with self.subTest(setup=setup):self.assertFalse(self.make('arm();'+setup).eval('callback(3,0)'))
 def test_only_proven_singular_binding_scans_all_six_directions_with_nil_neighbors(self):
  lua=self.make();self.assertTrue(lua.eval('Map.GetAdjacentPlots==nil'))
  self.assertTrue(self.inspect(lua).predicate.active);self.assertEqual(lua.globals().neighborCalls,6)
  self.assertEqual([lua.globals().directions[i]for i in range(6)],[1]*6)
 def test_own_tech_civic_and_plot_visibility(self):
  for setup in ('revealed=false',"GameInfo.Resources[5].PrereqTech='TECH_REVEAL';revealTech=false", "GameInfo.Resources[5].PrereqCivic='CIVIC_REVEAL';revealCivic=false"):
   self.assertFalse(self.make('arm();'+setup).eval('callback(3,0)'))
 def test_inclusive_window_ends_without_native_stopped_claim(self):
  lua=self.make();self.assertTrue(lua.eval('callback(3,0)'));lua.execute('turn=131');self.assertTrue(lua.eval('callback(3,0)'))
  lua.execute('turn=132');self.assertFalse(lua.eval('callback(3,0)'));self.assertIn('UNOBSERVED',self.inspect(lua).status.stopped_notifications)
  self.assertFalse(self.make('arm();turn=109').eval('callback(3,0)'))
 def test_gap_completion_false_transition_and_bounded_repeat(self):
  lua=self.make();self.assertTrue(lua.eval('callback(3,0)'));lua.execute('granaryPresent=true');self.assertFalse(lua.eval('callback(3,0)'))
  lua.eval('callback(3,0)');status=self.inspect(lua).status
  self.assertEqual((status.calls,status.true_calls,status.false_calls),(3,1,2));self.assertEqual(len(status.transitions),2)
 def test_inspection_error_does_not_become_native_error_count(self):
  lua=self.make("arm();Map.GetPlotByIndex=function()error('binding unavailable')end")
  data=self.inspect(lua);self.assertFalse(data.predicate.active);self.assertEqual(data.predicate.reason,'predicate_error')
  self.assertEqual(data.status.error_count,0);self.assertEqual(data.status.calls,0)
  self.assertFalse(lua.eval('callback(3,0)'));status=self.inspect(lua).status
  self.assertEqual(status.error_count,1);self.assertEqual(status.false_calls,1)
 def test_missing_native_registration_is_visible(self):
  data=self.inspect(self.make('arm();GameEvents=nil'))
  self.assertEqual(data.status.registered,0);self.assertEqual(data.status.error_count,1)
 def test_append_compiles_and_uses_no_orders_queue_or_UI_methods(self):
  role=(ROOT/'Civ Supply Chains/ModSupport/ModSupport_RH_AI_Roles.lua').read_text(encoding='utf-8-sig')
  LuaRuntime().execute('assert(loadstring(...))',role+'\n'+LUA)
  for name in ('CanProduce','ChangeGoldBalance','SetPlotOwner','CreateIncompleteDistrict','CreateBuilding','RequestOperation','SetHuman','SetTurns','SetActive','GetBuildQueue'):
   self.assertNotRegex(LUA,r'\b'+name+r'\s*\(')

class NativeSchemaSQL(unittest.TestCase):
 tables=('Types','Strategies','StrategyConditions','AiListTypes','AiLists','Strategy_Priorities','AiFavoredItems')
 def setUp(self):
  path=Path(os.environ.get('CSC_TEST_GRANARY_DATABASE',r"C:\Users\Shadow\AppData\Local\Firaxis Games\Sid Meier's Civilization VI\Cache\DebugGameplay.sqlite"))
  if not path.is_file():self.skipTest('Preserved native gameplay database unavailable')
  self.db=sqlite3.connect(':memory:');self.db.create_function('Make_Hash',1,lambda text:zlib.crc32(text.encode()))
  with sqlite3.connect(path.resolve().as_uri()+'?mode=ro',uri=True)as source:source.backup(self.db)
 def tearDown(self):
  if hasattr(self,'db'):self.db.close()
 def rows(self):return{table:collections.Counter(self.db.execute('SELECT * FROM '+table))for table in self.tables}
 def test_only_additive_new_strategy_and_one_Favored_metadata_row(self):
  before=self.rows();critical={table:list(self.db.execute('SELECT * FROM '+table))for table in ('Modifiers','ModifierArguments','BuildingModifiers','TreeData')}
  self.db.executescript(SQL);after=self.rows()
  self.assertTrue(all(not(before[t]-after[t])for t in self.tables))
  self.assertEqual({t:sum((after[t]-before[t]).values())for t in self.tables},dict(Types=1,Strategies=1,StrategyConditions=2,AiListTypes=1,AiLists=1,Strategy_Priorities=1,AiFavoredItems=1))
  self.assertEqual(list(self.db.execute('SELECT Item,Favored,Value FROM AiFavoredItems WHERE ListType=?',(LIST,))),[('BUILDING_GRANARY',1,0)])
  self.assertEqual(list(self.db.execute('SELECT System FROM AiLists WHERE ListType=?',(LIST,))),[('Buildings',)])
  self.assertEqual(list(self.db.execute("SELECT StringValue,ThresholdValue FROM StrategyConditions WHERE StrategyType=? AND ConditionFunction='Call Lua Function'",(STRATEGY,))),[(LIST,0)])
  self.assertEqual(critical,{table:list(self.db.execute('SELECT * FROM '+table))for table in critical})
  amount=list(self.db.execute("SELECT Value FROM ModifierArguments WHERE ModifierId='MOD_CSC_RH_CUSTOMER_FORECAST_VALUE_BUILDING_GRANARY' AND Name='Amount'"))
  self.assertEqual(amount,[('40',)])
 def test_repeat_is_idempotent(self):
  self.db.executescript(SQL);before=self.rows();self.db.executescript(SQL);self.assertEqual(self.rows(),before)
 def test_non_RH_profile_does_not_add_candidate_rows(self):
  self.db.execute("UPDATE CSC_AI_Profile SET Mode='BASIC' WHERE Id='ACTIVE'");before=self.rows();self.db.executescript(SQL);self.assertEqual(self.rows(),before)

if __name__=='__main__':unittest.main()
