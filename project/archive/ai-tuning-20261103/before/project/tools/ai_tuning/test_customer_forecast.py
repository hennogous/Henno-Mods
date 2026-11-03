"""Actual Lua51 control reader fixtures; no FireTuner or native mutations."""
import json,sys,unittest
from pathlib import Path
from lupa.lua51 import LuaRuntime,LuaError
H=Path(__file__).resolve().parents[3]/'project/tools/ai_tuning'
class CustomerReader(unittest.TestCase):
 def run_lua(self,setup='',requested=25):
  e=LuaRuntime();captured=[];e.globals().print=lambda *x:captured.append(x)
  e.execute('''
ui_turn=25;owner_human=false;mill=true;mill_x=1;building_pillaged=false;district_pillaged=false;complete=true;built=false;actual=40;foreign=false;alias=false;marker=1;originalHuman=nil
ExposedMembers={CSC_RH_CustomerRoles={version=2,errors={},ready=true,writes=1,refreshes=1},CSC_AI_AssistanceUI={InitialHumanPlayers=function()return{['1']=originalHuman==true or(originalHuman==nil and owner_human)}end}}
Game={GetCurrentGameTurn=function()return ui_turn end}
GameInfo={Yields={YIELD_CSC_AI_PLACEMENT={YieldType='YIELD_CSC_AI_PLACEMENT'}},Buildings={
 BUILDING_GRANARY={Index=5,Hash=12345,BuildingType='BUILDING_GRANARY'},BUILDING_CSC_BAKERS_WIND_MILL={Index=6,Hash=20001,BuildingType='BUILDING_CSC_BAKERS_WIND_MILL'},
 BUILDING_CSC_BAKERS_WATER_MILL={Index=7,Hash=20002,BuildingType='BUILDING_CSC_BAKERS_WATER_MILL'},BUILDING_TEST_GRANARY={Index=9,Hash=23456,BuildingType='BUILDING_TEST_GRANARY'}},Districts={[8]={Index=8}}}
GameInfo.Buildings[6]=GameInfo.Buildings.BUILDING_CSC_BAKERS_WIND_MILL
GameInfo.BuildingReplaces=function()local used=false;return function()if alias and not used then used=true;return{ReplacesBuildingType='BUILDING_GRANARY',CivUniqueBuildingType='BUILDING_TEST_GRANARY'}end end end
local district={GetX=function()return mill_x end,GetY=function()return 0 end,GetType=function()return 8 end}
Map={GetPlot=function(x,y)assert(x==mill_x and y==0);return{GetX=function()return mill_x end,GetY=function()return 0 end,GetIndex=function()return 101 end,GetProperty=function()if originalHuman==true or(originalHuman==nil and owner_human)then return 0 end;return marker end}end,GetPlotDistance=function(x,y,a,b)return math.abs(x-a)+math.abs(y-b)end}
local function collection(values)return{Members=function()local i=0;return function()i=i+1;if values[i]then return i,values[i]end end end}end
function makecity(pid,x,hasMill)
 local bs={HasBuilding=function(self,index)return(index==6 and hasMill and mill)or((index==5 or index==9)and built)end,
  GetBuildingsAtLocation=function(self,index)assert(index==101);return hasMill and mill and{6}or{}end,IsPillaged=function(self,index)assert(index==6);return building_pillaged end}
 return{GetOwner=function()return pid end,GetID=function()return 1000+pid end,GetName=function()return 'City'..pid end,GetX=function()return x end,GetY=function()return 0 end,
 GetBuildings=function()return bs end,GetDistricts=function()local ds=collection({district});ds.IsPillaged=function(self,type,index)assert(type==8 and index==101);return district_pillaged end;ds.HasDistrict=function(self,index,mustComplete)assert(index==8 and mustComplete);return complete end;return ds end,
 GetBuildingYield=function()return actual end,GetBuildingPotentialYield=function(self,hash,yieldType)assert(hash==12345 or(alias and hash==23456),'Getter must receive Hash, not Index');assert(yieldType=='YIELD_CSC_AI_PLACEMENT');if foreign and pid==1 then return 0 end;return actual end}
end
Players={}
function prepare()
 if empty then Players={};return end
 local c1=makecity(1,0,not foreign)
 Players[1]={IsAlive=function()return true end,IsHuman=function()return owner_human end,GetCities=function()return collection({c1})end}
 if foreign then local c2=makecity(2,2,true);Players[2]={IsAlive=function()return true end,IsHuman=function()return false end,GetCities=function()return collection({c2})end}end
end
''');e.execute(setup);e.execute('prepare()')
  e.execute((H/'profile_customer_forecast.lua').read_text().replace('__TARGET_TURN__',str(requested)))
  return json.loads(next(x[0].split('=',1)[1]for x in captured if x and x[0].startswith('CSC_PROFILE_CUSTOMER_FORECAST=')))
 def test_positive_unbuilt_projection_and_built_application_separate(self):
  x=self.run_lua();self.assertTrue(x['unbuilt_forecast_observed']);self.assertEqual(x['controls']['positive_unbuilt'],1)
  x=self.run_lua('built=true');self.assertTrue(x['application_observed']);self.assertFalse(x['unbuilt_forecast_observed']);self.assertEqual(x['controls']['positive_built'],1)
 def test_no_source_or_distant_source_is_negative_not_application(self):
  for setup in ('mill=false;actual=0','mill_x=2;actual=0'):
   x=self.run_lua(setup);self.assertEqual(x['controls']['failed'],0);self.assertFalse(x['application_observed'])
 def test_human_owner_excluded(self):
  x=self.run_lua('owner_human=true;actual=0');self.assertEqual(x['records'][0]['control'],'negative_human');self.assertEqual(x['records'][0]['expected'],0)
 def test_foreign_adjacent_source_excluded_from_target(self):
  x=self.run_lua('foreign=true');r=next(r for r in x['records']if r['player']==1)
  self.assertEqual(r['expected'],0);self.assertEqual(len(r['adjacent_foreign_sources']),1);self.assertTrue(r['pass'])
 def test_pillaged_building_negative(self):
  x=self.run_lua('building_pillaged=true;actual=0');self.assertEqual(x['controls']['failed'],0);self.assertFalse(x['application_observed'])
 def test_ambiguous_district_functioning_excluded_not_faked(self):
  for setup in ('district_pillaged=true;actual=0','complete=false;actual=0'):
   x=self.run_lua(setup);self.assertEqual(x['controls']['uncertain'],1);self.assertFalse(x['application_observed'])
 def test_native_value_mismatch_is_failure(self):
  x=self.run_lua('actual=0');self.assertEqual(x['controls']['failed'],1);self.assertFalse(x['unbuilt_forecast_observed'])
 def test_UI_clock_lag_explicit_and_larger_lag_rejected(self):
  x=self.run_lua('ui_turn=24');self.assertEqual(x['ui_turn'],24);self.assertEqual(x['requested_core_turn'],25)
  with self.assertRaises(LuaError):self.run_lua('ui_turn=23')
 def test_direct_replacement_and_hash_getter(self):
  x=self.run_lua('alias=true');self.assertEqual({r['target']for r in x['records']},{'BUILDING_GRANARY','BUILDING_TEST_GRANARY'});self.assertEqual(x['controls']['failed'],0)
 def test_read_only_source(self):
  code=(H/'profile_customer_forecast.lua').read_text()
  for token in ('SetProperty','SetActive','SetTurns','RequestPlayerOperation','RequestOperation','CreateBuilding','ChangeGoldBalance','AddBuilding'):self.assertNotRegex(code,r'\b'+token+r'\s*\(')
 def test_initial_no_cities_is_unobserved(self):
  x=self.run_lua('empty=true');self.assertFalse(x['application_observed']);self.assertFalse(x['unbuilt_forecast_observed']);self.assertEqual(x['records'],[])
 def test_UI_fixture_does_not_expose_Gameplay_only_methods(self):
  code=(H/'profile_customer_forecast.lua').read_text()
  for token in ('GetBuildingLocation','GetDistrictByIndex','GetNumDistricts'):self.assertNotIn(token,code)
  x=self.run_lua();self.assertTrue(x['unbuilt_forecast_observed'])
 def test_original_human_excluded_even_when_current_flag_is_AI(self):
  x=self.run_lua('originalHuman=true;owner_human=false;actual=0');self.assertEqual(x['controls']['failed'],0);self.assertEqual(x['records'][0]['control'],'negative_human')
 def test_missing_source_role_marker_is_failure_not_no_exposure_success(self):
  x=self.run_lua('marker=nil');self.assertGreater(x['controls']['failed'],0);self.assertFalse(x['application_observed'])
 def test_human_actual_built_yield_is_checked(self):
  x=self.run_lua('originalHuman=true;built=true;actual=40');self.assertGreater(x['controls']['failed'],0);self.assertEqual(x['records'][0]['actual_building_yield'],40)
if __name__=='__main__':unittest.main()
