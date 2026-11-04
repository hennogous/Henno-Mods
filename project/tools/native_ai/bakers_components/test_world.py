"""Actual Lua checks for the read-only historical Bakers facts capture."""
import json
from pathlib import Path
import unittest

from lupa.lua51 import LuaRuntime


SOURCE = Path(__file__).with_name("world.lua").read_text(encoding="utf-8")
SETUP = r'''
CAPTURED={};READS=0;WRITES=0
print=function(s) CAPTURED[#CAPTURED+1]=s end
local function tableInfo(rows,key)
 local index={};for _,r in ipairs(rows)do if r[key]~=nil then index[r[key]]=r end;if r.Index~=nil then index[r.Index]=r end end
 return setmetatable(index,{__call=function()
  local n=0;return function()n=n+1;return rows[n]end
 end})
end
local names={'BUILDING_CSC_BAKERS_RIVER_ACCESS','BUILDING_CSC_BAKERS_NO_RIVER_ACCESS',
 'BUILDING_CSC_BAKERS_WIND_MILL','BUILDING_CSC_BAKERS_WATER_MILL',
 'BUILDING_CSC_BAKERS_BAKERY','BUILDING_CSC_BAKERS_CAFE'}
local bs={};for i,name in ipairs(names)do bs[#bs+1]={Index=i-1,BuildingType=name}end
GameInfo={Buildings=tableInfo(bs,'BuildingType'),Districts=tableInfo({
 {Index=0,DistrictType='DISTRICT_CITY_CENTER'},
 {Index=1,DistrictType='DISTRICT_CSC_BAKERS_QUARTER'}},'DistrictType')}
for _,name in ipairs({'BuildingPrereqs','MutuallyExclusiveBuildings','BuildingModifiers',
 'Modifiers','ModifierArguments','DynamicModifiers','Requirements','RequirementSetRequirements',
 'RequirementArguments','CSC_AdjacencyRules'})do GameInfo[name]=tableInfo({},'unused')end
GameInfo.BuildingPrereqs=tableInfo({{Building=names[4],PrereqBuilding=names[1]},
 {Building=names[5],PrereqBuilding=names[3]},
 {Building=names[5],PrereqBuilding=names[4]}},'unused')
GameInfo.MutuallyExclusiveBuildings=tableInfo({{Building=names[4],MutuallyExclusiveBuilding=names[3]}},'unused')
GameInfo.BuildingModifiers=tableInfo({{BuildingType=names[4],ModifierId='PARENT'}},'unused')
GameInfo.Modifiers=tableInfo({{ModifierId='PARENT',ModifierType='ATTACH'},
 {ModifierId='CHILD',ModifierType='SELF',OwnerRequirementSetId='BITSET'}},'ModifierId')
GameInfo.ModifierArguments=tableInfo({{ModifierId='PARENT',Name='ModifierId',Value='CHILD'},
 {ModifierId='CHILD',Name='Amount',Value='512'}},'unused')
GameInfo.DynamicModifiers=tableInfo({{ModifierType='ATTACH',CollectionType='COLLECTION_PLAYER_DISTRICTS',EffectType='EFFECT_ATTACH_MODIFIER'},
 {ModifierType='SELF',CollectionType='COLLECTION_OWNER',EffectType='EFFECT_ADJUST_DISTRICT_BASE_YIELD_CHANGE'}},'ModifierType')
GameInfo.RequirementSetRequirements=tableInfo({{RequirementSetId='BITSET',RequirementId='BIT'}},'unused')
GameInfo.Requirements=tableInfo({{RequirementId='BIT',RequirementType='REQUIREMENT_PLOT_PROPERTY_MATCHES'}},'RequirementId')
GameInfo.RequirementArguments=tableInfo({{RequirementId='BIT',Name='PropertyName',Value='test'}},'unused')
local function plot(index,x,y,owner,district)
 return {GetIndex=function()return index end,GetX=function()return x end,GetY=function()return y end,
  GetOwner=function()return owner end,GetDistrictType=function()return district end,
  GetFeatureType=function()return -1 end,GetResourceType=function()return -1 end,
  GetImprovementType=function()return -1 end,IsWater=function()return false end,
  IsHills=function()return true end,IsRiver=function()return false end,
  GetRiverCrossingCount=function()return 0 end,CanHaveDistrict=function()return true end,
  GetProperty=function(_,key)READS=READS+1;if key=='CSC_ADJ_CSC_BAKERS_WIND_MILL_PRODUCTION_FROM_HILLS_1' then return 1 end end,
  SetProperty=function()WRITES=WRITES+1;error('Write forbidden')end}
end
local plots={[1429]=plot(1429,5,5,5,-1),[1829]=plot(1829,8,8,3,-1),
 [101]=plot(101,1,1,5,0),[202]=plot(202,2,2,3,0)}
Map={GetGridSize=function()return 60,40 end,GetPlotByIndex=function(i)return plots[i]end,
 GetPlot=function(x,y)if x==1 and y==1 then return plots[101]elseif x==2 and y==2 then return plots[202]end end}
Game={GetCurrentGameTurn=function()return 80 end}
local function player(pid,x,y,name)
 local district={GetType=function()return 0 end,GetX=function()return x end,GetY=function()return y end,
  IsComplete=function()return true end,IsPillaged=function()return false end,GetID=function()return 17 end}
 local ds={GetNumDistricts=function()return 1 end,GetDistrictByIndex=function(_,i)if i==0 then return district end end}
 local buildings={HasBuilding=function(_,i)return i==0 end,IsPillaged=function()return false end}
 local queue={GetBuildingProgress=function()return 0 end,CurrentlyBuilding=function()return 'UNIT_WARRIOR'end,
  GetSize=function()return 1 end,GetCurrentProductionTypeHash=function()return 42 end}
 local city={GetID=function()return 65536 end,GetName=function()return name end,GetX=function()return x end,
  GetY=function()return y end,GetPopulation=function()return 7 end,GetBuildings=function()return buildings end,
  GetBuildQueue=function()return queue end,GetDistricts=function()return ds end}
 local cities={Members=function()local done=false;return function()if not done then done=true;return 1,city end end end}
 return {IsHuman=function()return false end,IsAlive=function()return true end,IsMajor=function()return true end,
  GetCities=function()return cities end}
end
Players={[0]={IsHuman=function()return true end,IsAlive=function()return true end},
 [5]=player(5,1,1,'Delhi\nfixture'),[3]=player(3,2,2,'Majapahit')}
PlayersVisibility={[5]={IsRevealed=function()return true end},[3]={IsRevealed=function()return true end}}
'''


def capture(extra=""):
    lua = LuaRuntime(unpack_returned_tuples=True)
    lua.execute(SETUP)
    if extra:
        lua.execute(extra)
    lua.execute(SOURCE)
    lines = list(lua.globals().CAPTURED.values())
    marker = "CSC_BAKERS_COMPONENT_WORLD="
    raw = next(line[len(marker):] for line in lines if line.startswith(marker))
    return lua, json.loads(raw), lines, raw


class WorldTests(unittest.TestCase):
    def test_world_catalog_and_nested_modifier_closure(self):
        lua, facts, _, _ = capture()
        self.assertTrue(facts["mappingVerified"])
        self.assertEqual(facts["turn"], 80)
        self.assertEqual(facts["mapping"]["buildingCount"], 6)
        self.assertEqual(facts["mapping"]["districtIndex"], 1)
        self.assertEqual(len(facts["ownerDistricts"]), 2)
        self.assertEqual(facts["targets"][0]["candidate"]["index"], 1429)
        self.assertEqual(facts["targets"][0]["name"], "Delhi\nfixture")
        self.assertEqual(len(facts["relevantDB"]["modifiers"]["rows"]), 2)
        reqs=facts["relevantDB"]["requirements"]
        value=dict(zip(reqs["columns"],reqs["rows"][0]))["RequirementType"]
        self.assertEqual(facts["databaseStrings"][value["s"]-1], "REQUIREMENT_PLOT_PROPERTY_MATCHES")
        self.assertEqual(facts["targets"][0]["candidate"]["millProperties"][0]["amountSum"], 1)
        self.assertEqual(lua.globals().WRITES, 0)
        self.assertGreater(lua.globals().READS, 0)
        self.assertTrue(facts["sourceValidation"]["valid"])
        self.assertEqual(facts["observerConfig"]["maxRows"], 37)
        self.assertEqual(len(facts["observerConfig"]["buildings"]), 6)

    def test_optional_shared_evaluator_does_not_publish(self):
        extra = r'''
CSC_Adjacency={Initialize=function()end,ByDistrict={DISTRICT_CSC_BAKERS_QUARTER={
 {ID='REAL_WIND',YieldType='YIELD_PRODUCTION',ProvideType='SelfBonus',
 ModifierOwner='BuildingModifiers',WhoIsTheOwner='BUILDING_CSC_BAKERS_WIND_MILL'}}},
 Count=function()return 1 end,Amount=function(_,n)return n,n end,
 Write=function()WRITES=WRITES+1;error('Write forbidden')end}
'''
        lua, facts, _, _ = capture(extra)
        self.assertTrue(facts["sharedAdjacencyAvailable"])
        self.assertEqual(facts["targets"][0]["adjacency"]["plannedMill"], "BUILDING_CSC_BAKERS_WIND_MILL")
        self.assertEqual(facts["targets"][0]["adjacency"]["rules"][0]["amount"], 1)
        self.assertEqual(lua.globals().WRITES, 0)

    def test_missing_city_does_not_confirm_mapping(self):
        _, facts, _, _ = capture("Players[3]=nil")
        self.assertFalse(facts["mappingVerified"])
        self.assertFalse(facts["targets"][1]["exists"])

    def test_durable_chunks_reconstruct_complete_tuner_receipt(self):
        _, _, lines, raw = capture("CSC_BAKERS_COMPONENT_DURABLE_CHUNKS=true")
        prefix = "CSC_BAKERS_COMPONENT_WORLD_CHUNK="
        chunks = [json.loads(line[len(prefix):]) for line in lines if line.startswith(prefix)]
        self.assertTrue(chunks)
        self.assertTrue(all(len(line.encode("utf-8")) < 1600 for line in lines if line.startswith(prefix)))
        self.assertEqual([c["part"] for c in chunks], list(range(1, len(chunks) + 1)))
        decoded = b"".join(bytes.fromhex(c["data"]) for c in chunks)
        self.assertEqual(decoded, raw.encode("utf-8"))
        self.assertEqual(len(decoded), chunks[0]["bytes"])
        self.assertEqual(sum(decoded) % 2**32, chunks[0]["sum32"])


if __name__ == "__main__":
    unittest.main()
