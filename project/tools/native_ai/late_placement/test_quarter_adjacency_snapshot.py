"""Read-only adjacency separates active properties from a missing Mill's geometry."""
import json
from pathlib import Path
import unittest
from lupa.lua51 import LuaRuntime
from quarter_adjacency_snapshot import parse_rows

HERE=Path(__file__).resolve().parent


class Snapshot(unittest.TestCase):
    def test_missing_footer_or_rows_cannot_qualify(self):
        with self.assertRaises(AssertionError):parse_rows('CSC_QUARTER_ADJ_ROW\t{"kind":"site","plot":1}')
        with self.assertRaises(AssertionError):parse_rows('CSC_QUARTER_ADJ_END\t250\t1\t0')

    def test_real_reader_does_not_treat_missing_windmill_as_current(self):
        vm=LuaRuntime();lines=[]
        vm.globals().print=lambda *args:lines.append('\t'.join(map(str,args)))
        vm.execute('''
Game={GetCurrentGameTurn=function()return 250 end};AutoplayManager={IsActive=function()return false end}
local b={Index=36,DistrictType='DISTRICT_CSC_BAKERS_QUARTER'}
GameInfo={Districts={DISTRICT_CSC_BAKERS_QUARTER=b},Buildings={
 BUILDING_CSC_BAKERS_WIND_MILL={Index=1},BUILDING_CSC_BAKERS_WATER_MILL={Index=2}}}
local rules={
 {ID='base',YieldType='YIELD_PRODUCTION',ProvideType='SelfBonus',ModifierOwner='DistrictModifiers',count=2},
 {ID='sales',YieldType='YIELD_GOLD',ProvideType='SelfBonus',ModifierOwner='DistrictModifiers',count=1},
 {ID='wind',YieldType='YIELD_PRODUCTION',ProvideType='SelfBonus',ModifierOwner='BuildingModifiers',WhoIsTheOwner='BUILDING_CSC_BAKERS_WIND_MILL',count=1}}
local properties={CSC_ADJ_base_ENCODED_AMOUNT=2,CSC_ADJ_sales_ENCODED_AMOUNT=1,CSC_ADJ_wind_ENCODED_AMOUNT=0}
local plot={GetIndex=function()return 100 end,GetX=function()return 1 end,GetY=function()return 2 end,
 IsHills=function()return true end,IsRiver=function()return false end,GetRiverCrossingCount=function()return 0 end,
 GetProperty=function(_,key)return properties[key]end}
local district={GetType=function()return 36 end,GetX=plot.GetX,GetY=plot.GetY,
 IsComplete=function()return true end,IsPillaged=function()return false end}
local districts={GetNumDistricts=function()return 1 end,GetDistrictByIndex=function()return district end}
local city={GetID=function()return 42 end,GetName=function()return 'City' end,GetDistricts=function()return districts end,
 GetBuildings=function()return{HasBuilding=function()return false end}end}
local cities={Members=function()local once=false;return function()if not once then once=true;return 1,city end end end}
Players={[1]={IsAlive=function()return true end,IsHuman=function()return false end,GetCities=function()return cities end}}
PlayerConfigurations={[1]={GetCivilizationTypeName=function()return 'CIVILIZATION_TEST'end}}
Map={GetPlot=function()return plot end,GetAdjacentPlots=function()return{}end}
CSC_Adjacency={Initialize=function()end,ByDistrict={[b.DistrictType]=rules},
 Eligible=function(r)return r.ID~='wind'end,Count=function(r)return r.count end,Amount=function(_,count)return count end}
CSC_AI_QuarterPlacement={StageTwoProfiles=function()return{{key='BAKERS'}}end,
 ReadSuppliers=function()return{base={{working=true},{working=false}},specialty={}}end}
CSC_AI_QuarterAdjacencyValue=function()return{production=3,gold=1,total=4}end
''')
        code=(HERE/'quarter_adjacency_read.lua').read_text(encoding='utf-8').replace('__SCOPE__',"{turn=250,players={1},quarters={'BAKERS'}}")
        vm.execute(code);result=parse_rows('\n'.join(lines))
        site,=[r for r in result['rows']if r['kind']=='site']
        self.assertEqual(site['current']['total'],3)
        self.assertEqual(site['withWind']['total'],4)
        self.assertEqual(site['wind'],'absent')
        self.assertEqual(site['propertyMismatches'],0)
        self.assertNotIn('withWater',site)


if __name__=='__main__':unittest.main()
