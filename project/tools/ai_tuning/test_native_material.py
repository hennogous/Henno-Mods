"""Executed Lua51 reader contracts and physical stop semantics; no native calls."""
import copy
import json
import unittest
from pathlib import Path
from lupa.lua51 import LuaRuntime,LuaError
from native_material_probe import physical_changes, parse

FIXTURE = r'''
function rows(items)
 local t={};for _,v in ipairs(items)do if v.Index then t[v.Index]=v end
 for _,k in ipairs({'DistrictType','BuildingType','ResourceType','ImprovementType','YieldType','UnitType','FeatureType','TechnologyType'})do if v[k]then t[v[k]]=v end end end
 return setmetatable(t,{__call=function()local i=0;return function()i=i+1;return items[i]end end})
end
function collection(items)return{Members=function()local i=0;return function()i=i+1;if items[i]then return i,items[i]end end end}end
Game={GetCurrentGameTurn=function()return 110 end,GetProperty=function(self,key)if key:find('TOTALS')then return{cost=123}end end}
GameInfo={Resources=rows({{Index=54,ResourceType='FLAX'}}),Features=rows({{Index=32,FeatureType='F',RemoveTech='T'}}),
 Improvements=rows({{Index=1,ImprovementType='I',PrereqTech='T'}}),Technologies=rows({{Index=2,TechnologyType='T'}}),
 Units=rows({{Index=1,UnitType='UNIT_BUILDER'}}),Buildings=rows({{Index=8,BuildingType='MILL'}}),
 Districts=rows({{Index=36,DistrictType='BAKERS'}}),Yields=rows({{Index=1,YieldType='YIELD_PRODUCTION'},{Index=2,YieldType='YIELD_GOLD'},{Index=3,YieldType='YIELD_FOOD'}}),
 Improvement_ValidResources=rows({{ResourceType='FLAX',ImprovementType='I'}}),Improvement_ValidFeatures=rows({}),Feature_Removes=rows({})}
local function plot(idx)
 return{GetIndex=function()return idx end,GetX=function()return idx%74 end,GetY=function()return math.floor(idx/74)end,
 GetOwner=function()return 3 end,GetResourceType=function()return 54 end,GetResourceCount=function()return 1 end,
 GetFeatureType=function()return 32 end,GetImprovementType=function()return -1 end,GetDistrictType=function()return -1 end,
 GetTerrainType=function()return 3 end,IsImprovementPillaged=function()return false end,IsRiver=function()return true end,
 IsHills=function()return false end,IsWater=function()return false end,IsImpassable=function()return false end,GetProperty=function()return nil end}
end
Map={GetPlotByIndex=plot,GetPlot=function(x,y)return plot(x+y*74)end,GetAdjacentPlots=function()return{plot(2489)}end,
 GetPlotDistance=function(x,y,xx,yy)return math.abs(x-xx)+math.abs(y-yy)end}
local function district(idx)local p=plot(idx);p.GetType=function()return 36 end;p.IsComplete=function()return true end;p.IsPillaged=function()return false end;p.GetAdjacencyYield=function()return 2 end;return p end
local c={GetID=function()return 65536 end,GetDistricts=function()return collection({district(2488),district(2564),district(2419)})end,
 GetBuildings=function()return{HasBuilding=function()return true end,IsPillaged=function()return true end}end,GetYield=function()return 10 end}
local u={GetID=function()return 5242897 end,GetType=function()return 1 end,GetX=function()return 47 end,GetY=function()return 32 end,
 GetMovesRemaining=function()return 0 end,GetBuildCharges=function()return 2 end,GetDamage=function()return 0 end}
local player={IsAlive=function()return true end,IsMajor=function()return true end,IsHuman=function()return false end,GetID=function()return 3 end,
 GetUnits=function()return collection({u})end,GetCities=function()return collection({c})end,
 GetTechs=function()return{HasTech=function()return false end}end}
Players={[3]=player};PlayerManager={GetAlive=function()return{player}end};PlayerConfigurations={[3]={IsHuman=function()return false end}}
PlayersVisibility={[3]={IsRevealed=function()return true end}}
ImprovementBuilder={CanHaveImprovement=function(p,i,pid)assert(pid==3 and i==1);return false end}
'''


class MaterialReaderTests(unittest.TestCase):
    def capture(self, extra='', core=False):
        lua=LuaRuntime(); captured=[]; lua.globals().print=captured.append
        lua.execute(FIXTURE+extra)
        code=Path(__file__).with_name('native_material_reader.lua').read_text(encoding='utf-8-sig')
        lua.execute(code.replace('__CORE_LEGALITY_ONLY__',str(core).lower()))
        return parse(captured[-1], 'CSC_MATERIAL_LEGALITY' if core else 'CSC_MATERIAL_FOLLOWTHROUGH')

    def test_readonly_builder_charges_and_pillaged_producer(self):
        value=self.capture()
        self.assertEqual((value['builders'][0]['charges'],value['builders'][0]['moves']),(2,0))
        self.assertTrue(value['quarters'][0]['buildings'][0]['pillaged'])
        self.assertEqual(value['ledger']['TOTALS']['cost'],123)
        catalog=value['metadata']['improvement_catalog']
        self.assertEqual((catalog['count'],catalog['index_limit']),(1,2))
        self.assertEqual(catalog['rows'][0]['index'],1)
        self.assertEqual(catalog['rows'][0]['type'],'I')
        self.assertFalse(value['targets'][0]['feature_removal_tech_owned'])

    def test_false_legality_is_false_not_unknown(self):
        value=self.capture(core=True)
        self.assertIs(value['targets'][0]['legal_improvements'][0]['native_legal'],False)
        self.assertNotIn('builders',value)

    def test_core_mode_without_UI_configuration_human_method(self):
        value=self.capture('PlayerConfigurations={[3]={}}',core=True)
        self.assertIs(value['targets'][0]['legal_improvements'][0]['native_legal'],False)

    def test_UI_original_human_configuration_is_rejected(self):
        with self.assertRaisesRegex(LuaError,'assertion failed'):
            self.capture('PlayerConfigurations[3].IsHuman=function()return true end')

    def test_optional_binding_missing_is_unknown(self):
        for extra in ('ImprovementBuilder=nil','ImprovementBuilder.CanHaveImprovement=function()error("unsupported diagnostic")end'):
            value=self.capture(extra)
            self.assertEqual(value['targets'][0]['legal_improvements'][0]['native_status'],'unknown')
            self.assertEqual(len(value['builders']),1)

    def test_core_legality_does_not_traverse_ui_districts(self):
        value=self.capture('Players[3].GetCities=function()error("UI only")end',core=True)
        self.assertEqual(len(value['targets']),2)

    def test_stop_changes_are_physical(self):
        initial=self.capture();current=copy.deepcopy(initial)
        current['builders'][0]['x']+=1
        self.assertEqual(physical_changes(initial,current),[])
        for field,new in [('owner',4),('resource',-1),('count',0),('feature',-1),('improvement',2),('improvement_pillaged',True),('district',36)]:
            altered=copy.deepcopy(initial);altered['targets'][0][field]=new
            self.assertIn(field,physical_changes(initial,altered)[0]['fields'])

    def test_changed_scope_and_duplicate_marker_rejected(self):
        value=self.capture();altered=copy.deepcopy(value);altered['targets'].pop()
        with self.assertRaises(ValueError):physical_changes(value,altered)
        with self.assertRaises(ValueError):parse('X={}\nX={}', 'X')


if __name__=='__main__':unittest.main()
