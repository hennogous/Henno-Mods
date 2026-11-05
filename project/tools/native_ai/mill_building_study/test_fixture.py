"""Exercise the actual Lua fixture with a native-shaped, delayed-yield model.

The model does not import CSC's evaluator. It deliberately supports bad native
yield, empire-wide activation and retained legacy bits, so the fixed-contract
assertions must reject them. These are fixture/phase checks, not native proof.
Set PYTHONPATH to the already installed Lupa dependencies; nothing is installed.
"""
from __future__ import annotations

import json
from pathlib import Path
import unittest

SOURCE = Path(__file__).with_name('fixture.lua').read_text(encoding='utf-8')

MODEL = r'''
Turn=1; Mutations=0; BadScope=false; BadYield=1; RetainLegacy=false; Misplace=false
CreateCalls=0;RemoveCalls=0;NextBuildingInstance=1
function changed() Mutations=Mutations+1 end
function info(rows,key)
 local out={}
 for _,row in ipairs(rows)do out[row.Index]=row;out[row[key]]=row end
 return setmetatable(out,{__call=function()local n=0;return function()n=n+1;return rows[n]end end})
end
GameInfo={
 Buildings=info({{Index=1,BuildingType='BUILDING_PALACE'},
 {Index=2,BuildingType='BUILDING_CSC_BAKERS_WIND_MILL'},
 {Index=3,BuildingType='BUILDING_CSC_BAKERS_WATER_MILL'}},'BuildingType'),
 Districts=info({{Index=0,DistrictType='DISTRICT_CITY_CENTER'},
 {Index=7,DistrictType='DISTRICT_CSC_BAKERS_QUARTER'}},'DistrictType'),
 Terrains=info({{Index=0,TerrainType='TERRAIN_GRASS'},
 {Index=1,TerrainType='TERRAIN_GRASS_HILLS'}},'TerrainType'),
 Yields={YIELD_PRODUCTION={Index=0}}
}
DirectionTypes={DIRECTION_NORTHEAST=0,DIRECTION_EAST=1,DIRECTION_SOUTHEAST=2,
 DIRECTION_SOUTHWEST=3,DIRECTION_WEST=4,DIRECTION_NORTHWEST=5}
FlowDirectionTypes={FLOWDIRECTION_SOUTH=0,FLOWDIRECTION_NORTHEAST=1,FLOWDIRECTION_NORTHWEST=2}
Game={GetCurrentGameTurn=function()return Turn end}
local offsets={{1,-1},{1,0},{0,1},{-1,1},{-1,0},{0,-1}}
local plots={};local cities={};local actual={}
function plot(x,y)
 local index=y*80+x
 if plots[index]then return plots[index]end
 local p={x=x,y=y,index=index,owner=0,district=-1,resource=42,improvement=-1,
 feature=0,hill=false,city=false,properties={},W=false,NW=false,NE=false}
 function p:GetIndex()return self.index end
 function p:GetX()return self.x end
 function p:GetY()return self.y end
 function p:GetOwner()return self.owner end
 function p:GetDistrictType()return self.district end
 function p:IsCity()return self.city end
 function p:IsHills()return self.hill end
 function p:GetResourceType()return self.resource end
 function p:GetImprovementType()return self.improvement end
 function p:GetProperty(key)return self.properties[key]end
 function p:IsWOfRiver()return self.W end
 function p:IsNWOfRiver()return self.NW end
 function p:IsNEOfRiver()return self.NE end
 function p:GetRiverCrossingCount()
  local n=0
  for _,value in ipairs({self.W,self.NW,self.NE,plot(self.x+1,self.y-1).NE,
    plot(self.x-1,self.y).W,plot(self.x,self.y-1).NW})do if value then n=n+1 end end
  return n
 end
 plots[index]=p;return p
end
Map={GetPlotByIndex=function(index)return plot(index%80,math.floor(index/80))end,
 GetAdjacentPlot=function(x,y,d)return plot(x+offsets[d+1][1],y+offsets[d+1][2])end,
 GetPlotDistance=function(x,y,a,b)return math.max(math.abs(x-a),math.abs(y-b),math.abs(x-a+y-b))end}
TerrainBuilder={
 SetTerrainType=function(p,n)changed();p.hill=n==1 end,
 SetFeatureType=function(p,n)changed();p.feature=n end,
 SetWOfRiver=function(p,value,flow)changed();assert(flow==0);p.W=value end,
 SetNWOfRiver=function(p,value,flow)changed();assert(flow==1);p.NW=value end,
 SetNEOfRiver=function(p,value,flow)changed();assert(flow==2);p.NE=value end}
ResourceBuilder={SetResourceType=function(p,value)changed();p.resource=value end}
WorldBuilder={CityManager=function()return {SetPlotOwner=function(_,x,y,owner,id)changed();plot(x,y).owner=owner end}end}
local function district(c,p,kind)
 local d={plot=p,kind=kind,pillaged=false,complete=true}
 function d:GetX()return self.plot.x end
 function d:GetY()return self.plot.y end
 function d:GetType()return self.kind end
 function d:IsComplete()return self.complete end
 function d:IsPillaged()return self.pillaged end
 function d:SetPillaged(value)changed();self.pillaged=value end
 function d:GetYield(index)assert(index==0);return actual[self.plot.index]or 0 end
 return d
end
local function city(id,x,y)
 local c={id=id,x=x,y=y,buildings={[1]=true},locations={[1]=y*80+x},pillage={},districts={},
  attached={},pendingAttachments={},instances={}}
 local center=plot(x,y);center.city=true;center.district=0
 c.districts[1]=district(c,center,0)
 function c:GetID()return self.id end
 function c:GetOwner()return 0 end
 function c:GetX()return self.x end
 function c:GetY()return self.y end
 function c:GetBuildings()
  return {HasBuilding=function(_,index)return self.buildings[index]==true end,
   IsPillaged=function(_,index)return self.pillage[index]==true end,
   GetBuildingLocation=function(_,index)return self.locations[index]or -1 end,
   RemoveBuilding=function(_,index)
    changed();RemoveCalls=RemoveCalls+1
    self.buildings[index]=nil;self.locations[index]=nil;self.pillage[index]=nil
    self.attached[index]=nil;self.pendingAttachments[index]=nil;self.instances[index]=nil
   end,
   SetPillaged=function(_,index,value)changed();self.pillage[index]=value end}
 end
 function c:GetDistricts()
  return {GetNumDistricts=function()return #self.districts end,
   GetDistrictByIndex=function(_,index)return self.districts[index+1]end}
 end
 function c:GetBuildQueue()
  return {CreateIncompleteDistrict=function(_,kind,index,progress)
    changed();assert(progress==100);local p=Map.GetPlotByIndex(index);assert(p.district==-1)
    p.district=kind;self.districts[#self.districts+1]=district(self,p,kind)
   end,
   CreateBuilding=function(_,index,where)
    changed();CreateCalls=CreateCalls+1;self.buildings[index]=true;self.locations[index]=Misplace and 1 or where
    self.instances[index]=NextBuildingInstance;NextBuildingInstance=NextBuildingInstance+1
    self.pendingAttachments[index]=true;self.attached[index]=nil
   end}
 end
 cities[id]=c;return c
end
city(65536,10,10);city(131072,30,10)
Players={[0]={IsHuman=function()return true end,GetCities=function()return {FindID=function(_,id)return cities[id]end}end}}
function MockCity(id)return cities[id]end
function MockFlush()
 -- Native-shaped adverse timing model: first enrollment is deferred until the
 -- command returns. If the Quarter is pillaged at that moment, the new source
 -- has no admitted district attachment. Simply changing the later property
 -- cannot manufacture the missing attachment. This models a fixture hazard;
 -- it is not an assertion that Civ implements precisely this lifecycle.
 for _,c in pairs(cities)do
  local quarter=nil;for _,d in ipairs(c.districts)do if d.kind==7 then quarter=d end end
  for index in pairs(c.pendingAttachments)do
   c.attached[index]=quarter and not quarter.pillaged or false
   c.pendingAttachments[index]=nil
  end
 end
 local anyWind,anyWater=false,false
 for _,c in pairs(cities)do anyWind=anyWind or c.attached[2];anyWater=anyWater or c.attached[3]end
 for _,c in pairs(cities)do for _,d in ipairs(c.districts)do if d.kind==7 then
  local p=d.plot
  local wind=p.properties.CSC_ADJ_CSC_BAKERS_WIND_MILL_PRODUCTION_FROM_HILLS_ENCODED_AMOUNT or 0
  local water=p.properties.CSC_ADJ_CSC_BAKERS_WATER_MILL_PRODUCTION_FROM_RIVER_ENCODED_AMOUNT or 0
  actual[p.index]=((c.attached[2]or(BadScope and anyWind))and wind or 0)
   +((c.attached[3]or(BadScope and anyWater))and water or 0)
  actual[p.index]=actual[p.index]*BadYield
 end end end
end
function CSC_RefreshAdjacencies()
 changed()
 local anyWind,anyWater=false,false
 for _,c in pairs(cities)do anyWind=anyWind or c.buildings[2];anyWater=anyWater or c.buildings[3]end
 for _,c in pairs(cities)do
  for _,d in ipairs(c.districts)do if d.kind==7 then
   local p=d.plot;local wind,water=0,0
   if not d.pillaged then
    if (c.buildings[2]or(BadScope and anyWind))and not c.pillage[2]and p.hill then wind=1 end
    if (c.buildings[3]or(BadScope and anyWater))and not c.pillage[3]then water=math.floor(p:GetRiverCrossingCount()/2)end
   end
   for _,r in ipairs({{'CSC_BAKERS_WIND_MILL_PRODUCTION_FROM_HILLS',wind,1},
     {'CSC_BAKERS_WATER_MILL_PRODUCTION_FROM_RIVER',water,3}})do
    local prefix='CSC_ADJ_'..r[1]..'_'
    p.properties[prefix..'TOTAL']=r[2];p.properties[prefix..'ACTUAL_AMOUNT']=r[2];p.properties[prefix..'ENCODED_AMOUNT']=r[2]
    for n=1,r[3]do p.properties[prefix..'STEP_'..n]=r[2]>=n and 1 or 0 end
    for _,bit in ipairs({1,2,4,8,16,32,64,128,256,512})do p.properties[prefix..bit]=RetainLegacy and 1 or 0 end
   end
  end end
 end
end
function print(value)LastPrint=value end
'''


class FixtureTests(unittest.TestCase):
    def setUp(self):
        from lupa.lua51 import LuaRuntime
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        self.lua.execute(MODEL)
        self.lua.execute(SOURCE)
        self.config = self.lua.table_from(dict(schema=1, player=0, localCity=65536,
            localPlot=811, remoteCity=131072, remotePlot=831, token='offline-test'))
        self.fixture = self.lua.globals().CSC_MillFixture

    def prepare(self):
        self.fixture.Prepare(self.config)
        self.lua.globals().MockFlush()

    def begin(self, name):
        self.fixture.PrepareCase(name)
        self.lua.globals().MockFlush()
        self.fixture.CaptureBaseline(name)

    def apply(self, name):
        self.fixture.ApplyCase(name)
        self.lua.globals().MockFlush()

    def run_until(self, count):
        cases = self.fixture.Describe()['cases']
        for i in range(1, count + 1):
            name = cases[i]['id']
            self.begin(name)
            self.apply(name)
            self.fixture.FinishCase(name, 'assert-local-contract')

    def test_all_cases_use_fixed_contract_and_export(self):
        self.assertEqual(len(self.fixture.Describe()['cases']), 21)
        self.assertEqual(self.lua.globals().Mutations, 0)
        self.prepare()
        self.run_until(21)
        exported = self.fixture.Export()
        self.assertEqual(exported['completedCases'], 21)
        self.assertEqual(exported['case'], 'repair-quarter')

    def test_capture_is_world_read_only_and_native_yield_may_lag(self):
        self.prepare()
        self.run_until(1)
        self.begin('wind-hill')
        self.fixture.ApplyCase('wind-hill')
        before = self.lua.globals().Mutations
        value = self.fixture.Capture('wind-hill')
        self.assertEqual(value['facts'][1]['production'], 0)
        self.assertEqual(value['expectedDelta'][1], 1)
        self.assertEqual(self.lua.globals().Mutations, before)
        with self.assertRaisesRegex(Exception, 'native Production delta'):
            self.fixture.FinishCase('wind-hill', 'assert-local-contract')
        self.lua.globals().MockFlush()
        self.fixture.FinishCase('wind-hill', 'assert-local-contract')

    def test_mutation_replays_rejected_before_native_operations(self):
        self.prepare()
        before = self.lua.globals().Mutations
        with self.assertRaisesRegex(Exception, 'already prepared'):
            self.fixture.Prepare(self.config)
        self.assertEqual(self.lua.globals().Mutations, before)
        self.begin('wind-flat')
        before = self.lua.globals().Mutations
        with self.assertRaisesRegex(Exception, 'unfinished'):
            self.fixture.PrepareCase('wind-flat')
        self.assertEqual(self.lua.globals().Mutations, before)
        self.apply('wind-flat')
        before = self.lua.globals().Mutations
        with self.assertRaisesRegex(Exception, 'settled baseline'):
            self.fixture.ApplyCase('wind-flat')
        self.assertEqual(self.lua.globals().Mutations, before)

    def test_turn_guard_and_case_order(self):
        self.prepare()
        self.lua.globals().Turn = 2
        before = self.lua.globals().Mutations
        with self.assertRaisesRegex(Exception, 'turn-1'):
            self.fixture.PrepareCase('wind-flat')
        self.assertEqual(self.lua.globals().Mutations, before)
        self.lua.globals().Turn = 1
        with self.assertRaisesRegex(Exception, 'declared order'):
            self.fixture.PrepareCase('water-0')
        self.assertEqual(self.lua.globals().Mutations, before)

    def test_existing_producer_rejected_without_mutation(self):
        self.lua.execute('MockCity(65536).buildings[2]=true')
        with self.assertRaisesRegex(Exception, 'Developed building'):
            self.fixture.Prepare(self.config)
        self.assertEqual(self.lua.globals().Mutations, 0)

    def test_wrong_owner_or_same_city_rejected_without_mutation(self):
        self.config['remoteCity'] = 65536
        with self.assertRaisesRegex(Exception, 'Distinct city IDs'):
            self.fixture.Prepare(self.config)
        self.assertEqual(self.lua.globals().Mutations, 0)
        self.config['remoteCity'] = 131072
        self.lua.execute('Map.GetPlotByIndex(811).owner=1')
        with self.assertRaisesRegex(Exception, 'owner changed'):
            self.fixture.Prepare(self.config)
        self.assertEqual(self.lua.globals().Mutations, 0)

    def test_remote_activation_bug_is_detected(self):
        self.prepare()
        self.run_until(9)
        self.begin('remote-wind')
        self.lua.globals().BadScope = True
        self.apply('remote-wind')
        with self.assertRaisesRegex(Exception, 'native Production delta'):
            self.fixture.FinishCase('remote-wind', 'assert-local-contract')

    def test_wrong_native_scale_and_retained_legacy_bits_are_detected(self):
        self.prepare()
        self.run_until(1)
        self.begin('wind-hill')
        self.lua.globals().BadYield = 2
        self.apply('wind-hill')
        with self.assertRaisesRegex(Exception, 'native Production delta'):
            self.fixture.FinishCase('wind-hill', 'assert-local-contract')
        self.lua.globals().BadYield = 1
        self.lua.globals().RetainLegacy = True
        self.lua.globals().CSC_RefreshAdjacencies()
        self.lua.globals().MockFlush()
        with self.assertRaisesRegex(Exception, 'retired numeric bit'):
            self.fixture.FinishCase('wind-hill', 'assert-local-contract')

    def test_bad_native_location_reserves_failed_mutation(self):
        self.prepare()
        self.begin('wind-flat')
        self.lua.globals().Misplace = True
        with self.assertRaisesRegex(Exception, 'placement'):
            self.fixture.ApplyCase('wind-flat')
        before = self.lua.globals().Mutations
        with self.assertRaisesRegex(Exception, 'settled baseline'):
            self.fixture.ApplyCase('wind-flat')
        self.assertEqual(self.lua.globals().Mutations, before)

    def test_record_only_is_explicit_and_not_a_pass(self):
        self.prepare()
        self.run_until(1)
        self.begin('wind-hill')
        self.lua.globals().BadYield = 2
        self.apply('wind-hill')
        value = self.fixture.FinishCase('wind-hill', 'record-only')
        self.assertEqual(value['validation'], 'record-only')
        self.assertEqual(value['facts'][1]['production'], 2)
        self.assertEqual(value['expectedDelta'][1], 1)

    def test_paired_quarter_repair_retains_objects_and_attachment_lifetime(self):
        self.prepare()
        self.run_until(20)
        g = self.lua.globals()
        city = g.MockCity(65536)
        instance = city['instances'][2]
        self.lua.execute('_SavedQuarter=MockCity(65536).districts[2]')
        before,created,removed = g.Mutations,g.CreateCalls,g.RemoveCalls
        receipt = self.fixture.PrepareCase('repair-quarter')
        self.assertTrue(receipt['retainedNativeObjects'])
        self.assertFalse(receipt['worldMutations'])
        self.assertEqual(g.Mutations,before)
        self.assertEqual((g.CreateCalls,g.RemoveCalls),(created,removed))
        self.assertEqual(city['instances'][2],instance)
        self.assertTrue(self.lua.eval('_SavedQuarter==MockCity(65536).districts[2]'))
        self.fixture.CaptureBaseline('repair-quarter')
        self.apply('repair-quarter')
        result = self.fixture.FinishCase('repair-quarter','assert-local-contract')
        self.assertEqual(result['facts'][1]['production'],1)
        self.assertEqual((g.CreateCalls,g.RemoveCalls),(created,removed))
        self.assertEqual(city['instances'][2],instance)

    def test_same_command_construction_then_pillage_can_lose_attachment(self):
        self.prepare()
        self.run_until(1)
        self.begin('wind-hill')
        self.fixture.ApplyCase('wind-hill')
        # Reproduce the adverse preparation shape from the first native run:
        # newly create the source, then pillage its district before enrollment
        # can flush. Healthy booleans and correct properties after repair alone
        # do not prove that its initial native attachment ever existed.
        self.lua.execute('''
local q=MockCity(65536).districts[2]
q:SetPillaged(true);CSC_RefreshAdjacencies();MockFlush()
q:SetPillaged(false);CSC_RefreshAdjacencies();MockFlush()
''')
        value = self.fixture.Capture('wind-hill')['facts'][1]
        self.assertFalse(value['quarterPillaged'])
        self.assertFalse(value['wind']['pillaged'])
        self.assertEqual(value['expectedWind'],1)
        self.assertEqual(value['properties'][1]['encoded'],1)
        self.assertEqual(value['production'],0)
        with self.assertRaisesRegex(Exception,'native Production delta'):
            self.fixture.FinishCase('wind-hill','assert-local-contract')

    def test_paired_repair_rejects_changed_building_before_world_mutation(self):
        self.prepare()
        self.run_until(20)
        self.lua.execute('MockCity(65536):GetBuildings():RemoveBuilding(2)')
        before = self.lua.globals().Mutations
        with self.assertRaisesRegex(Exception,'retained pillaged Quarter'):
            self.fixture.PrepareCase('repair-quarter')
        self.assertEqual(self.lua.globals().Mutations,before)

    def test_reload_compares_raw_native_facts_without_mutation(self):
        self.prepare()
        self.run_until(21)
        descriptor = self.fixture.Export()
        before = self.lua.globals().Mutations
        self.lua.execute('CSC_MillFixture=nil')
        self.lua.execute(SOURCE)
        reloaded = self.lua.globals().CSC_MillFixture
        result = reloaded.VerifyReload(descriptor)
        self.assertTrue(result['verified'])
        self.assertEqual(self.lua.globals().Mutations, before)
        self.lua.execute('Map.GetPlotByIndex(811).hill=false')
        with self.assertRaisesRegex(Exception, 'Reload'):
            reloaded.VerifyReload(descriptor)
        self.assertEqual(self.lua.globals().Mutations, before)

    def test_json_and_hks_integer_tags(self):
        self.lua.execute('''local old=type;type=function(value)
          if old(value)=='number' and value==math.floor(value) then return 'integer' end
          return old(value) end''')
        self.prepare()
        self.run_until(2)
        self.fixture.Print(self.fixture.Capture('wind-hill'))
        raw = self.lua.globals().LastPrint
        value = json.loads(raw.removeprefix('CSC_MILL_FIXTURE='))
        self.assertEqual(value['facts'][0]['expectedWind'], 1)


if __name__ == '__main__':
    unittest.main()
