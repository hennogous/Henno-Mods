"""Focused Lua51 legacy/LIGHT observation checks; no native client."""
import json
from pathlib import Path
import unittest
from lupa.lua51 import LuaRuntime
SOURCE=Path(__file__).resolve().parents[3]/'project/tools/ai_baseline/paired_observer.lua'
FIXTURE=r"""
local function iterator(rows)return function()local i=0;return function()i=i+1;return rows[i]end end end
geometry_calls=0;turn=1;handlers={}
Events={};for _,key in ipairs({'PlayerTurnActivated','DistrictAddedToMap','ImprovementAddedToMap'})do
 Events[key]={Add=function(f)handlers[key]=handlers[key]or{};table.insert(handlers[key],f)end}
end
Game={GetCurrentGameTurn=function()return turn end}
GameInfo={CSC_QuarterMaterialAdjacencyConfig=iterator({{QuarterKey='BAKERS',SourceTag='CLASS_CSC_BAKERS_BASE'}}),
 TypeTags=iterator({{Type='RESOURCE_WHEAT',Tag='CLASS_CSC_BAKERS_BASE'}}),Resources={RESOURCE_WHEAT={}},
 Districts={DISTRICT_CSC_BAKERS_QUARTER={Index=17}},Buildings=iterator({}),Yields=iterator({}),Technologies=iterator({}),Civics=iterator({}),Civilizations={[0]={CivilizationType='CIV_TEST'}},Leaders={[0]={LeaderType='LEADER_TEST'}}}
local ds={HasDistrict=function()return false end,GetNumDistricts=function()return 0 end}
local city={GetID=function()return 1 end,GetOwner=function()return 1 end,GetX=function()return 0 end,GetY=function()return 0 end,
 GetDistricts=function()return ds end,GetBuildings=function()return{}end,GetPopulation=function()return 1 end,GetName=function()return'CITY_TEST'end,GetProperty=function()return nil end}
local cities={Members=function()local done=false;return function()if not done then done=true;return 1,city end end end}
local player={GetID=function()return 1 end,IsMajor=function()return true end,IsHuman=function()return false end,GetCities=function()return cities end,
 GetTechs=function()return{HasTech=function()return false end}end,GetCulture=function()return{HasCivic=function()return false end}end}
Players={[1]=player};PlayerManager={GetAliveMajors=function()return{player}end};PlayerConfigurations={[1]={GetCivilizationTypeID=function()return 0 end,GetLeaderTypeID=function()return 0 end}}
CSC_Adjacency={PlotsInBand=function()geometry_calls=geometry_calls+1;return{}end}
Map={GetGridSize=function()return 0,0 end,GetPlot=function()return{}end}
function activate(t)turn=t;for _,f in ipairs(handlers.PlayerTurnActivated or{})do f(1)end end
print=function()end
"""
class LightTests(unittest.TestCase):
 def load(self,light):
  runtime=LuaRuntime();runtime.execute(FIXTURE)
  if light is not None:runtime.globals().CSCBASE_LIGHT_OBSERVATION=light
  runtime.execute(SOURCE.read_text());return runtime
 def test_nil_legacy_geometry_and_automatic_checkpoints_are_retained(self):
  runtime=self.load(None);self.assertEqual(runtime.globals().geometry_calls,1)
  self.assertEqual(len(runtime.globals().handlers.PlayerTurnActivated),2)
  runtime.globals().activate(25)
  self.assertEqual(runtime.globals().geometry_calls,3);self.assertIsNotNone(runtime.globals().CSCBASE.checkpoints[25]);self.assertEqual(len(runtime.globals().CSCBASE.errors),0)
 def test_light_omits_geometry_and_automatic_full_census_but_keeps_physical(self):
  runtime=self.load(True);runtime.globals().activate(25);base=runtime.globals().CSCBASE
  self.assertEqual(runtime.globals().geometry_calls,0);self.assertIsNone(base.checkpoints[25])
  value=base.capture();self.assertEqual(len(value.cities),1);self.assertEqual(len(value.options),0)
  self.assertEqual(runtime.globals().geometry_calls,0);self.assertEqual(len(runtime.globals().handlers.DistrictAddedToMap),1)
 def test_native_sandbox_without_rawget_or_global_table_default(self):
  runtime=LuaRuntime();runtime.execute(FIXTURE);runtime.execute('rawget=nil;_G=nil')
  runtime.execute(SOURCE.read_text());runtime.globals().activate(25)
  self.assertEqual(runtime.globals().geometry_calls,3)
  self.assertIsNotNone(runtime.globals().CSCBASE.checkpoints[25])
 def test_native_sandbox_without_rawget_or_global_table_light(self):
  runtime=LuaRuntime();runtime.execute(FIXTURE)
  runtime.execute('CSCBASE_LIGHT_OBSERVATION=true;rawget=nil;_G=nil')
  runtime.execute(SOURCE.read_text());runtime.globals().activate(25)
  self.assertEqual(runtime.globals().geometry_calls,0)
  self.assertIsNone(runtime.globals().CSCBASE.checkpoints[25])
  self.assertEqual(len(runtime.globals().CSCBASE.capture().cities),1)
 def test_false_is_legacy_and_scripts_compile(self):
  a=self.load(False);self.assertGreater(a.globals().geometry_calls,0)
  LuaRuntime().execute('assert(loadstring(...))',SOURCE.read_text())
if __name__=='__main__':unittest.main()

