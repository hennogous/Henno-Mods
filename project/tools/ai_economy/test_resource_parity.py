"""Class-driven supplier policy checks, without a game or native bid consumer.

Invented resource names deliberately exercise loaded TypeTags and improvement
mappings; passing these tests proves proposals, not purchases or Builder work.
"""
import importlib.util
from pathlib import Path
import unittest

from lupa.lua51 import LuaRuntime

ROOT = Path(__file__).resolve().parents[3]
_spec = importlib.util.spec_from_file_location(
    'supplier_policy_fixture',
    ROOT / 'project/tools/ai_workshop_bridge/ce_frontend/test_bakers_gameplay.py')
_fixture = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_fixture)


def runtime(family='BAKERS'):
    vm = LuaRuntime()
    vm.execute(_fixture.FIXTURE.replace('BAKERS', family))
    vm.globals().family = family
    vm.execute(r'''
local function info(rows)
    return setmetatable(rows,{__call=function()
        local i=0;return function()i=i+1;return rows[i]end
    end})
end
baseName,specName='RESOURCE_MODDED_FIBRE_TEST','RESOURCE_MODDED_DYE_TEST'
for id,name in pairs({[40]=baseName,[41]=specName})do
    local row={Index=id,ResourceType=name}
    GameInfo.Resources[id],GameInfo.Resources[name]=row,row
end
GameInfo.Improvement_ValidResources=info({
    {ResourceType=baseName,ImprovementType='IMPROVEMENT_PASTURE'},
    {ResourceType=specName,ImprovementType='IMPROVEMENT_FIXTURE'},
})
CSC_Adjacency.HasTag=function(tag,name)
    return tag=='CLASS_CSC_'..family..'_BASE' and name==baseName
        or tag=='CLASS_CSC_'..family..'_SPEC' and name==specName
end
local quarterType='DISTRICT_CSC_'..family..'_QUARTER'
local fourth={Index=12,Hash=112,BuildingType='BUILDING_MODDED_FOURTH',PrereqDistrict=quarterType}
local unique={Index=13,Hash=113,BuildingType='BUILDING_MODDED_UNIQUE_FOURTH',PrereqDistrict=quarterType}
GameInfo.Buildings[fourth.BuildingType]=fourth
GameInfo.Buildings[unique.BuildingType]=unique
GameInfo.CSC_QuarterFlowBuildings[#GameInfo.CSC_QuarterFlowBuildings+1]={
    QuarterKey=family,Stage=4,BuildingType=fourth.BuildingType}
GameInfo.BuildingReplaces[#GameInfo.BuildingReplaces+1]={
    ReplacesBuildingType=fourth.BuildingType,CivUniqueBuildingType=unique.BuildingType}
GameInfo.Civics={}
Players[3].GetCulture=function()return{HasCivic=function()return false end}end
owned,damaged,location={},{},{}
city.GetBuildings=function()return{
    HasBuilding=function(_,id)return owned[id]or false end,
    IsPillaged=function(_,id)return damaged[id]or false end,
    GetBuildingLocation=function(_,id)return location[id]or 100 end,
}end
baseOwner,specOwner,baseImprovement,specImprovement=3,3,-1,-1
basePlot=setmetatable({
    GetResourceType=function()return 40 end,
    GetOwner=function()return baseOwner end,
    GetImprovementType=function()return baseImprovement end,
    IsImprovementPillaged=function()return false end,
},{__index=pasture})
specPlot=setmetatable({
    GetIndex=function()return 102 end,
    GetResourceType=function()return 41 end,
    GetOwner=function()return specOwner end,
    GetImprovementType=function()return specImprovement end,
    IsImprovementPillaged=function()return false end,
},{__index=pasture})
Map.GetAdjacentPlots=function()return{basePlot,specPlot}end
Map.GetPlotByIndex=function(i)return i==101 and basePlot or specPlot end
ui={GetPlotPurchaseQuote=function()return 40 end}
''')
    vm.execute((ROOT / 'Civ Supply Chains/Lua_UI/AI/CSC_AI_QuarterPlacement.lua').read_text(encoding='utf-8'))
    vm.execute(r'''
P=CSC_AI_QuarterPlacement
function chains()return P.ReadChains(Players[3])end
function acquisitions()return P.SupplierAcquisitionOffers(Players[3],chains(),ui,56*256)end
function policy()
    local entries,builders=P.MaterialDeductions(Players[3],true,56*256,0,nil,false)
    local jobs={};for _,r in ipairs(builders)do jobs[r.plot]=r.deltaQ8 end
    return entries,jobs
end
''')
    return vm


class ResourceParity(unittest.TestCase):
    def test_loaded_arbitrary_resource_classes_and_equal_last_deposit_protection(self):
        for family in ('BAKERS', 'TAILORS'):
            with self.subTest(family=family):
                runtime(family).execute(r'''
local c=chains()[1]
assert(#c.supply.base==1 and #c.supply.specialty==1)
assert(c.supply.base[1].resource==baseName and c.supply.specialty[1].resource==specName)
local rows=policy();local costs={}
for _,r in ipairs(rows)do costs[r.plot]=r.delta end
assert(costs[101]==-12288 and costs[102]==-12288)
-- No compatibility mapping means no legal supplier claim, even with a tag.
ImprovementBuilder.CanHaveImprovement=function()return false end
assert(#chains()[1].supply.specialty==0)
''')

    def test_base_buyer_without_customer_and_stage_four_spec_gate(self):
        for family in ('BAKERS', 'TAILORS'):
            with self.subTest(family=family):
                runtime(family).execute(r'''
local _,jobs=policy();assert(jobs[101]==nil and jobs[102]==nil)
owned[9]=true -- A functioning Stage 2 buyer, no adjacent customer district.
_,jobs=policy();assert(jobs[101]==26*256 and jobs[102]==nil)
owned[12]=true
_,jobs=policy();assert(jobs[101]==26*256 and jobs[102]==26*256)
damaged[12]=true
_,jobs=policy();assert(jobs[102]==nil)
damaged[12]=false;location[12]=999
_,jobs=policy();assert(jobs[102]==nil)
owned[12]=false;owned[13]=true -- Loaded unique Stage 4 replacement.
_,jobs=policy();assert(jobs[102]==26*256)
GameInfo.Improvements[6].PrereqTech='TECH_LOCKED'
GameInfo.Technologies={TECH_LOCKED={Index=22}}
Players[3].GetTechs=function()return{HasTech=function()return false end}end
_,jobs=policy();assert(jobs[102]==nil)
''')

    def test_acquisition_missing_class_independence_bounded_dedup_and_retirement(self):
        for family in ('BAKERS', 'TAILORS'):
            with self.subTest(family=family):
                runtime(family).execute(r'''
-- Already working Base must not suppress missing Spec acquisition.
baseImprovement=5;specOwner=-1
local rows=acquisitions()
assert(#rows==1 and rows[1].plot==102 and rows[1].materialClass=='specialty')
assert(rows[1].deltaQ8==26*256 and rows[1].improvements[1]==6)
specOwner=3;assert(#acquisitions()==0)
baseOwner=-1;specOwner=-1;baseImprovement=-1
ImprovementBuilder.CanHaveImprovement=function()error('Unowned Lua query')end
rows=acquisitions();assert(#rows==2)
local cs=chains()
rows=P.SupplierAcquisitionOffers(Players[3],{cs[1],cs[1]},ui,56*256)
assert(#rows==2) -- Shared chains cannot stack bids for the same purchase.
-- A shared resource can fill both classes: one offer, still only 26 utility.
Map.GetAdjacentPlots=function()return{basePlot}end
CSC_Adjacency.HasTag=function(_,name)return name==baseName end
rows=acquisitions();assert(#rows==1 and rows[1].deltaQ8==26*256)
''')


if __name__ == '__main__':
    unittest.main()
