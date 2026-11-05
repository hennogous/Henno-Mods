"""Run actual setup Lua and strict Mill binding in a native-shaped world model.

This checks once-only setup, city/owner API contracts and spatial isolation. It
does not model the AI evaluator or prove native API behavior. Method signatures
are taken from shipped Tuner code and prior native fixtures, not inferred by the
test. Use the existing Lupa Lua 5.1 runtime on PYTHONPATH; no package installation.
"""
from __future__ import annotations

import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
SETUP = (HERE / 'setup.lua').read_text(encoding='utf-8-sig')
FIXTURE = (HERE / 'fixture.lua').read_text(encoding='utf-8-sig')

MODEL = r'''
Turn=1;Mutations=0;Killed={};Ownership={};CreateAttempts={};Printed={}
NoRemoteBand=false;RejectRemote=false;ModelCities={};ModelUnits={};ModelPlots={}
local offsets={{1,-1},{1,0},{0,1},{-1,1},{-1,0},{0,-1}}
function changed()Mutations=Mutations+1 end
function info(rows,key)
 local out={}
 for i,row in ipairs(rows)do row.Index=row.Index or i;out[row.Index]=row;out[row[key]]=row end
 return setmetatable(out,{__call=function()local i=0;return function()i=i+1;return rows[i]end end})
end
local buildingRows={{BuildingType='BUILDING_PALACE'},{BuildingType='BUILDING_CSC_BAKERS_WIND_MILL'},
 {BuildingType='BUILDING_CSC_BAKERS_WATER_MILL'},{BuildingType='BUILDING_MARKET'},
 {BuildingType='BUILDING_ZOO'},{BuildingType='BUILDING_TEMPLE'},{BuildingType='BUILDING_AMPHITHEATER'},
 {BuildingType='BUILDING_LIGHTHOUSE'},{BuildingType='BUILDING_GRANARY'}}
local districtRows={{Index=0,DistrictType='DISTRICT_CITY_CENTER'},
 {Index=7,DistrictType='DISTRICT_CSC_BAKERS_QUARTER'},
 {Index=8,DistrictType='DISTRICT_COMMERCIAL_HUB'}, {Index=9,DistrictType='DISTRICT_ENTERTAINMENT_COMPLEX'},
 {Index=10,DistrictType='DISTRICT_HOLY_SITE'}, {Index=11,DistrictType='DISTRICT_THEATER'},
 {Index=12,DistrictType='DISTRICT_HARBOR'}}
local function named(names,key)local rows={};for _,name in ipairs(names)do rows[#rows+1]={[key]=name}end;return info(rows,key)end
GameInfo={Buildings=info(buildingRows,'BuildingType'),Districts=info(districtRows,'DistrictType'),
 Units={UNIT_SETTLER={Index=9}},Yields={YIELD_PRODUCTION={Index=0}},
 Terrains=info({{Index=0,TerrainType='TERRAIN_GRASS'},{Index=1,TerrainType='TERRAIN_GRASS_HILLS'}},'TerrainType'),
 Resources=named({'RESOURCE_WHEAT','RESOURCE_COCOA','RESOURCE_COTTON','RESOURCE_DYES'},'ResourceType'),
 Improvements=named({'IMPROVEMENT_FARM','IMPROVEMENT_PLANTATION'},'ImprovementType'),
 Technologies=named({'TECH_IRRIGATION','TECH_ENGINEERING','TECH_MACHINERY','TECH_CONSTRUCTION'},'TechnologyType'),
 Civics=named({'CIVIC_GUILDS','CIVIC_HUMANISM','CIVIC_FEUDALISM','CIVIC_MEDIEVAL_FAIRES',
 'CIVIC_URBANIZATION','CIVIC_NAVAL_TRADITION','CIVIC_DIVINE_RIGHT','CIVIC_OPERA_BALLET'},'CivicType')}
DirectionTypes={DIRECTION_NORTHEAST=0,DIRECTION_EAST=1,DIRECTION_SOUTHEAST=2,DIRECTION_SOUTHWEST=3,DIRECTION_WEST=4,DIRECTION_NORTHWEST=5}
FlowDirectionTypes={FLOWDIRECTION_SOUTH=0,FLOWDIRECTION_NORTHEAST=1,FLOWDIRECTION_NORTHWEST=2}
Game={GetCurrentGameTurn=function()return Turn end}
local function distance(x,y,a,b)return math.max(math.abs(x-a),math.abs(y-b),math.abs(x-a+y-b))end
function ModelPlot(x,y)
 if x<0 or x>=80 or y<0 or y>=60 then return nil end
 local index=y*80+x
 if ModelPlots[index]then return ModelPlots[index]end
 local p={x=x,y=y,index=index,owner=-1,district=-1,resource=-1,improvement=-1,feature=-1,
 hill=false,water=false,city=false,W=false,NW=false,NE=false,properties={}}
 function p:GetIndex()return self.index end
 function p:GetX()return self.x end
 function p:GetY()return self.y end
 function p:GetOwner()return self.owner end
 function p:GetDistrictType()return self.district end
 function p:IsCity()return self.city end
 function p:IsWater()return self.water end
 function p:IsHills()return self.hill end
 function p:GetResourceType()return self.resource end
 function p:GetImprovementType()return self.improvement end
 function p:GetFeatureType()return self.feature end
 function p:GetProperty(key)return self.properties[key]end
 function p:GetRiverCrossingCount()
  local n=0;for _,value in ipairs({self.W,self.NW,self.NE,
    ModelPlot(self.x+1,self.y-1).NE,ModelPlot(self.x-1,self.y).W,ModelPlot(self.x,self.y-1).NW})do if value then n=n+1 end end;return n
 end
 ModelPlots[index]=p;return p
end
Map={GetPlot=ModelPlot,GetPlotDistance=distance,
 GetPlotByIndex=function(index)return ModelPlot(index%80,math.floor(index/80))end,
 GetAdjacentPlot=function(x,y,d)return ModelPlot(x+offsets[d+1][1],y+offsets[d+1][2])end}
function Map.GetAdjacentPlots(x,y)
 local rows={};for d=0,5 do local p=Map.GetAdjacentPlot(x,y,d);if p then rows[#rows+1]=p end end;return rows
end
TerrainBuilder={SetTerrainType=function(p,t)changed();p.hill=t==1 end,
 SetFeatureType=function(p,f)changed();p.feature=f end,
 SetWOfRiver=function(p,v,flow)changed();assert(flow==0);p.W=v end,
 SetNWOfRiver=function(p,v,flow)changed();assert(flow==1);p.NW=v end,
 SetNEOfRiver=function(p,v,flow)changed();assert(flow==2);p.NE=v end}
ResourceBuilder={SetResourceType=function(p,r)changed();p.resource=r end}
ImprovementBuilder={SetImprovementType=function(p,index,pid)changed();assert(p.owner==pid);p.improvement=index end}
local function district(p,index)
 local d={plot=p,index=index,pillaged=false}
 function d:GetX()return self.plot.x end
 function d:GetY()return self.plot.y end
 function d:GetType()return self.index end
 function d:IsComplete()return true end
 function d:IsPillaged()return self.pillaged end
 function d:SetPillaged(value)changed();self.pillaged=value end
 function d:GetYield(index)return 0 end
 return d
end
function ModelCreateCity(pid,x,y)
 CreateAttempts[#CreateAttempts+1]={pid=pid,x=x,y=y}
 if RejectRemote and pid==0 and #ModelCities[0]>0 then return nil end
 for _,list in pairs(ModelCities)do for _,c in ipairs(list)do assert(distance(x,y,c.x,c.y)>=4,'Native city spacing rejects site')end end
 changed()
 local c={pid=pid,x=x,y=y,id=(#ModelCities[pid]+1)*65536,population=1,buildings={},locations={},pillage={},districts={}}
 function c:GetOwner()return self.pid end
 function c:GetID()return self.id end
 function c:GetX()return self.x end
 function c:GetY()return self.y end
 function c:GetPopulation()return self.population end
 function c:ChangePopulation(n)changed();self.population=self.population+n end
 function c:GetBuildings()
  return {HasBuilding=function(_,i)return self.buildings[i]==true end,
   IsPillaged=function(_,i)return self.pillage[i]==true end,
   GetBuildingLocation=function(_,i)return self.locations[i]or -1 end,
   RemoveBuilding=function(_,i)changed();self.buildings[i]=nil;self.locations[i]=nil end,
   SetPillaged=function(_,i,v)changed();self.pillage[i]=v end}
 end
 function c:GetDistricts()return {GetNumDistricts=function()return #self.districts end,GetDistrictByIndex=function(_,i)return self.districts[i+1]end}end
 function c:GetBuildQueue()
  return {CreateIncompleteDistrict=function(_,i,where,progress)
    changed();assert(progress==100);local p=Map.GetPlotByIndex(where);assert(p.owner==self.pid and p.district==-1)
    p.district=i;self.districts[#self.districts+1]=district(p,i)
   end,
   CreateBuilding=function(_,i,where)changed();local p=Map.GetPlotByIndex(where);assert(p.owner==self.pid and p.district~=-1);self.buildings[i]=true;self.locations[i]=where end}
 end
 local center=ModelPlot(x,y);assert(center.owner==-1 or center.owner==pid,'Native city would steal land')
 center.owner=pid;center.city=true;center.district=0;c.districts[1]=district(center,0)
 c.buildings[GameInfo.Buildings.BUILDING_PALACE.Index]=true;c.locations[GameInfo.Buildings.BUILDING_PALACE.Index]=center.index
 for _,p in ipairs(Map.GetAdjacentPlots(x,y))do if p.owner==-1 then p.owner=pid end end
 ModelCities[pid][#ModelCities[pid]+1]=c
 return c
end
Players={}
function ModelPlayer(pid,x,y)
 ModelCities[pid]={};ModelUnits[pid]={};local player={techs={},civics={}}
 local settler={x=x,y=y,pid=pid}
 function settler:GetType()return 9 end
 function settler:GetX()return self.x end
 function settler:GetY()return self.y end
 ModelUnits[pid][1]=settler
 function player:GetID()return pid end
 function player:IsHuman()return pid==0 end
 function player:GetCities()return {
  Members=function()local i=0;return function()i=i+1;if ModelCities[pid][i]then return i,ModelCities[pid][i]end end end,
  FindID=function(_,id)for _,c in ipairs(ModelCities[pid])do if c.id==id then return c end end end,
  Create=function(_,a,b)return ModelCreateCity(pid,a,b)end}end
 function player:GetUnits()return {Members=function()local i=0;return function()i=i+1;if ModelUnits[pid][i]then return i,ModelUnits[pid][i]end end end}end
 function player:GetTechs()return {SetTech=function(_,index,value)changed();player.techs[index]=value end}end
 function player:GetCulture()return {SetCivic=function(_,index,value)changed();player.civics[index]=value end}end
 Players[pid]=player;return player
end
ModelPlayer(0,12,12);ModelPlayer(1,35,12);ModelPlayer(2,58,12)
PlayerManager={
 GetAlive=function()local out={};for pid=0,63 do if Players[pid]then out[#out+1]=Players[pid]end end;return out end,
 GetAliveMajors=function()local out={};for pid=0,21 do if Players[pid]then out[#out+1]=Players[pid]end end;return out end}
UnitManager={Kill=function(unit,flag)
 changed();assert(flag==false,'Use shipped two-argument unit Kill contract');Killed[#Killed+1]=unit.pid
 local list=ModelUnits[unit.pid];for i,u in ipairs(list)do if u==unit then table.remove(list,i);return end end;error('Unit already absent')
end}
WorldBuilder={CityManager=function()return {SetPlotOwner=function(_,x,y,pid,id)
 local c=Players[pid]:GetCities():FindID(id);assert(c,'City ID must belong to requested player')
 local p=ModelPlot(x,y);assert(p.owner==-1 or p.owner==pid,'Foreign land theft');changed();
 Ownership[#Ownership+1]={x=x,y=y,before=p.owner,pid=pid,id=id};p.owner=pid
end}end}
CSC_Adjacency={PlotsInBand=function(center,a,b)
 if NoRemoteBand and a==8 then return {}end
 local out={};for y=0,59 do for x=0,79 do local d=distance(center.x,center.y,x,y);if d>=a and d<=b then out[#out+1]=ModelPlot(x,y)end end end;return out
end}
function CSC_RefreshAdjacencies()changed()end
function print(text)Printed[#Printed+1]=text end
CSC_MILL_STUDY_TOKEN='offline-setup-check'
'''


class SetupTests(unittest.TestCase):
    def setUp(self):
        from lupa.lua51 import LuaRuntime
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        self.lua.execute(MODEL)

    def execute(self):
        self.lua.execute(SETUP)
        return self.lua.globals().CSC_MILL_STUDY_SETUP

    def test_actual_setup_passes_strict_fixture_bindings(self):
        value = self.execute()
        g = self.lua.globals()
        self.assertEqual(len(g.Killed), 3)
        self.assertEqual(len(g.ModelCities[0]), 2)
        self.assertEqual(g.ModelCities[1][1]['population'], 15)
        self.assertEqual(g.ModelCities[2][1]['population'], 15)
        self.assertTrue(g.Players[1]['techs'][g.GameInfo.Technologies.TECH_ENGINEERING.Index])
        self.assertTrue(g.Players[2]['civics'][g.GameInfo.Civics.CIVIC_HUMANISM.Index])
        self.assertEqual(len(value['rich']['resources']), 4)
        harbor = value['rich']['districts'][5]
        self.assertFalse(harbor['present'])
        self.assertIn('water', harbor['reason'])
        self.lua.execute(FIXTURE)
        receipt = g.CSC_MillFixture.Prepare(value['fixture'])
        self.assertEqual(receipt['phase'], 'ready')
        marker = g.Printed[1]
        decoded = json.loads(marker.removeprefix('CSC_MILL_STUDY_SETUP='))
        self.assertEqual(len(decoded['targets']), 2)
        self.assertEqual(decoded['fixture']['player'], 0)

    def test_goody_hut_is_excluded_from_human_neighborhood(self):
        self.lua.execute('ModelPlot(14,10).improvement=999')
        value = self.execute()
        self.assertEqual(self.lua.globals().ModelPlot(14,10)['improvement'], 999)
        site = self.lua.globals().Map.GetPlotByIndex(value['fixture']['localPlot'])
        for d in range(6):
            neighbor = self.lua.globals().Map.GetAdjacentPlot(site.GetX(site), site.GetY(site), d)
            self.assertEqual(neighbor.GetImprovementType(neighbor), -1)
        self.lua.execute(FIXTURE)
        self.lua.globals().CSC_MillFixture.Prepare(value['fixture'])
        self.assertEqual(self.lua.globals().ModelPlot(14,10)['improvement'], 999)

    def test_all_existing_major_cities_constrain_remote_choice(self):
        self.lua.execute('ModelPlayer(3,12,2);ModelCreateCity(3,12,2)')
        value = self.execute()
        g = self.lua.globals()
        remote = g.Players[0].GetCities(g.Players[0]).FindID(None, value['fixture']['remoteCity'])
        extra = g.ModelCities[3][1]
        self.assertGreaterEqual(g.Map.GetPlotDistance(remote['x'],remote['y'],extra['x'],extra['y']),6)
        self.lua.execute(FIXTURE)
        g.CSC_MillFixture.Prepare(value['fixture'])

    def test_missing_remote_plan_has_no_remote_creation_or_replay(self):
        self.lua.globals().NoRemoteBand = True
        with self.assertRaisesRegex(Exception, 'No separate human city'):
            self.execute()
        g = self.lua.globals()
        self.assertEqual(len(g.CreateAttempts), 3)
        before = g.Mutations
        with self.assertRaisesRegex(Exception, 'Never replay'):
            self.execute()
        self.assertEqual(g.Mutations, before)

    def test_city_state_spacing_is_considered_before_remote_creation(self):
        # Player 30 is omitted by the model's major-player enumeration. Its city
        # occupies the otherwise earliest remote candidate; a major-only check
        # would choose a neighboring site and fail native city spacing.
        self.lua.execute('ModelPlayer(30,12,2);ModelCreateCity(30,12,2)')
        value = self.execute()
        g = self.lua.globals()
        remote = g.Players[0].GetCities(g.Players[0]).FindID(None, value['fixture']['remoteCity'])
        minor = g.ModelCities[30][1]
        self.assertGreaterEqual(g.Map.GetPlotDistance(remote['x'],remote['y'],minor['x'],minor['y']),6)
        self.lua.execute(FIXTURE)
        g.CSC_MillFixture.Prepare(value['fixture'])

    def test_rejected_remote_creation_is_not_retried(self):
        self.lua.globals().RejectRemote = True
        with self.assertRaisesRegex(Exception, 'Remote city creation failed'):
            self.execute()
        g = self.lua.globals()
        self.assertEqual(len(g.CreateAttempts), 4)
        before = g.Mutations
        with self.assertRaisesRegex(Exception, 'Never replay'):
            self.execute()
        self.assertEqual(g.Mutations, before)

    def test_bad_turn_or_token_blocks_before_world_mutation(self):
        self.lua.globals().Turn = 2
        with self.assertRaisesRegex(Exception, 'turn-1'):
            self.execute()
        self.assertEqual(self.lua.globals().Mutations, 0)
        self.lua.globals().Turn = 1
        self.lua.globals().CSC_MILL_STUDY_TOKEN = 'quote-in-token"'
        with self.assertRaisesRegex(Exception, 'safe study token'):
            self.execute()
        self.assertEqual(self.lua.globals().Mutations, 0)


if __name__ == '__main__':
    unittest.main()
