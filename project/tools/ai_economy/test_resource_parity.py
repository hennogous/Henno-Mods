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

    def test_only_a_sole_pillaged_supplier_for_an_operating_buyer_qualifies_to_finish(self):
        for family in ('BAKERS', 'TAILORS'):
            with self.subTest(family=family):
                runtime(family).execute(r'''
baseImprovement,specImprovement=5,6
basePlot.IsImprovementPillaged=function()return true end
specPlot.IsImprovementPillaged=function()return true end
local function finishes()
    local _,offers=P.MaterialDeductions(Players[3],true,56*256,0,nil,false)
    local result={}
    for _,offer in ipairs(offers)do if offer.finishRepair then result[offer.plot]=true end end
    return result
end
assert(not next(finishes()))
owned[9],owned[12]=true,true
local repairs=finishes()
assert(repairs[101] and repairs[102])
damaged[12]=true
assert(not finishes()[102])
local second=setmetatable({GetIndex=function()return 103 end},{__index=basePlot})
Map.GetAdjacentPlots=function()return{basePlot,specPlot,second}end
Map.GetPlotByIndex=function(i)return i==101 and basePlot or i==102 and specPlot or second end
repairs=finishes()
assert(not repairs[101] and not repairs[103])
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

    def test_economic_job_bids_only_for_the_selected_legal_improvement(self):
        runtime().execute(r'''
GameInfo.Improvement_ValidResources[#GameInfo.Improvement_ValidResources+1]={
    ResourceType=baseName,ImprovementType='IMPROVEMENT_FIXTURE'}
owned[9]=true
CSC_AI_EconomyAdapters={
    SupplyValue=function()end,
    MaterialJobValue=function(_,_,kind,plot,improvement)
        assert(kind=='base' and plot:GetIndex()==101)
        return improvement==6 and 80*256 or 30*256
    end,
}
local _,sites=P.MaterialDeductions(Players[3],true,64*256,0,nil,false,{chains=chains()})
local pasture,selected
for _,site in ipairs(sites)do
    if site.plot==101 then
        assert(#site.improvements==1)
        if site.improvements[1]==5 then pasture=site else selected=site end
    end
end
assert(pasture and pasture.deltaQ8==nil)
assert(selected and selected.improvements[1]==6 and selected.deltaQ8==64*256)
''')

    def test_active_producer_starts_only_its_own_material_class_ahead_of_completion(self):
        for family in ('BAKERS', 'TAILORS'):
            with self.subTest(family=family):
                runtime(family).execute(r'''
local index,turns,value
CSC_AI_EconomyAdapters={SupplyValue=function()end,MaterialJobValue=function(_,_,kind,plot,improvement,ready,buyer)
    assert(buyer and ready==nil and buyer.turns==turns)
    assert(kind==(index==9 and 'base' or 'specialty'))
    return value
end}
local function jobs()
    local cs=chains()
    cs[1].economy={horizon=30}
    local _,sites=P.MaterialDeductions(Players[3],true,64*256,0,nil,false,{
        chains=cs,MaterialBuyerCommitment=function(_,buyers,horizon)
            for _,buyer in ipairs(buyers)do
                if buyer.Index==index and turns<horizon then return {type=buyer.BuildingType,turns=turns} end
            end
        end})
    local out={}
    for _,site in ipairs(sites)do out[site.plot]=site.deltaQ8 end
    return out
end
value,turns=0,4
assert(not next(jobs())) -- No current buyer and no customer.
index=9;local bids=jobs();assert(bids[101]==26*256 and not bids[102])
index=13;bids=jobs();assert(bids[102]==26*256 and not bids[101]) -- Unique Stage 4 replacement.
turns=9;assert(not next(jobs())) -- No first-supplier floor for a distant buyer.
value=8*256;bids=jobs();assert(bids[102]==value and not bids[101])
index=7;assert(not next(jobs())) -- A switch to another item ends the commitment.
''')

    def test_second_supplier_competes_on_its_actual_incremental_value(self):
        runtime().execute(r'''
owned[9]=true;baseImprovement=5
local second=setmetatable({GetIndex=function()return 103 end,GetImprovementType=function()return -1 end},{__index=basePlot})
Map.GetAdjacentPlots=function()return{basePlot,second}end
Map.GetPlotByIndex=function(i)return i==101 and basePlot or second end
local value=0
CSC_AI_EconomyAdapters={SupplyValue=function()end,MaterialJobValue=function(_,_,kind,plot)
    assert(kind=='base' and plot:GetIndex()==103);return value
end}
local function buy()
    local _,sites=P.MaterialDeductions(Players[3],true,64*256,0,nil,false,{chains=chains()})
    for _,site in ipairs(sites)do if site.plot==103 then return site.deltaQ8 end end
end
assert(buy()==nil)
value=5*256;assert(buy()==5*256)
''')

    def test_valuable_alt_improvement_research_waits_for_the_actual_buyer(self):
        for family in ('BAKERS', 'TAILORS'):
            with self.subTest(family=family):
                runtime(family).execute(r'''
local active=-1
GameInfo.Improvements[6].PrereqTech='TECH_FIXTURE_UNLOCK'
GameInfo.Technologies={TECH_FIXTURE_UNLOCK={Index=27}}
Players[3].GetTechs=function()return{
    HasTech=function()return false end,GetResearchingTech=function()return active end}
end
CSC_AI_EconomyAdapters={SupplyValue=function()end,MaterialJobValue=function(_,_,kind,plot,improvement,workTurn)
    if kind=='specialty' then
        assert(plot:GetIndex()==102 and improvement==6 and workTurn==9)
        return 12*256
    end
end}
local function offers()
    local research,cs={},chains()
    cs[1].economy={horizon=20}
    P.MaterialDeductions(Players[3],true,64*256,0,nil,false,{chains=cs,Research=function(kind,name)
        assert(kind=='tech' and name=='TECH_FIXTURE_UNLOCK');return 4 end},research)
    return research['tech:27']
end
owned[9]=true;assert(offers()==nil)
owned[12]=true
local topic=assert(offers());assert(topic.value==12*256 and topic.jobs[102])
active=27;assert(offers()==nil)
''')

    def test_working_buyer_prices_locked_second_supplier_alongside_ready_work(self):
        runtime().execute(r'''
owned[9]=true
GameInfo.Improvements[6].PrereqTech='TECH_SECOND_SUPPLIER'
GameInfo.Technologies={TECH_SECOND_SUPPLIER={Index=27}}
Players[3].GetTechs=function()return{HasTech=function()return false end}end
GameInfo.Improvement_ValidResources[#GameInfo.Improvement_ValidResources+1]={
    ResourceType=baseName,ImprovementType='IMPROVEMENT_FIXTURE'}
local second=setmetatable({GetIndex=function()return 103 end},{__index=basePlot})
Map.GetAdjacentPlots=function()return{basePlot,second}end
Map.GetPlotByIndex=function(i)return i==101 and basePlot or second end
ImprovementBuilder.CanHaveImprovement=function(plot,index)
    return plot==basePlot and index==5 or plot==second and index==6
end
CSC_AI_EconomyAdapters={SupplyValue=function()end,MaterialJobValue=function(_,_,kind,plot,index,delay)
    assert(kind=='base')
    if plot==basePlot then assert(index==5 and delay==nil);return 26*256 end
    assert(index==6 and delay==9);return 12*256
end}
local research,cs={},chains()
cs[1].economy={horizon=20}
local _,sites=P.MaterialDeductions(Players[3],true,64*256,0,nil,false,
    {chains=cs,Research=function()return 4 end},research)
local immediate
for _,site in ipairs(sites)do
    if site.plot==101 and site.deltaQ8 then immediate=site.deltaQ8 end
end
assert(immediate==26*256)
local topic=assert(research['tech:27'])
assert(topic.value==12*256 and topic.jobs[103] and not topic.jobs[101])
''')

    def test_builder_sponsorship_reserves_charges_across_city_boundaries(self):
        runtime().execute(r'''
GameInfo.Units={UNIT_BUILDER={Index=99}}
local units={}
Players[3].GetUnits=function()return{Members=function()return ipairs(units)end}end
ui.GetEconomyCityNumber=function(_,_,kind) assert(kind=='currentUnit');return -1 end
Map.GetPlotDistance=function(x1,y1,x2,y2)return math.abs(x1-x2)end
basePlot.GetX=function()return 3 end;specPlot.GetX=function()return 4 end
local x=2
local worker={GetID=function()return 39 end,GetType=function()return 99 end,GetBuildCharges=function()return 1 end,
    GetX=function()return x end,GetY=function()return 0 end}
local sites={
    {player=3,city=42,plot=101,improvements={5},deltaQ8=8192,jobValueQ8=10240,ordinaryQ8=10240},
    {player=3,city=99,plot=102,improvements={6},deltaQ8=6144,jobValueQ8=8192,ordinaryQ8=8192},
    {player=3,city=42,plot=101,improvements={6},deltaQ8=4096,jobValueQ8=4096,ordinaryQ8=4096},
}
local function bids()return P.MaterialBuilderOffers(Players[3],sites,ui,128*256)end
assert(#P.MaterialBuilderOffers(Players[3],sites,nil,128*256)==0)
assert(#bids()==2)
units[1]=worker;local rows=bids()
assert(#rows==2 and rows[1].city==99 and rows[1].plot==102 and rows[1].deltaQ8==2048 and not rows[1].contingency)
assert(rows[2].plot==101 and rows[2].deltaQ8==2048 and rows[2].contingency)
UnitManager={GetMoveToPath=function(_,plot)return plot==101 and {100} or {100,plot} end}
rows=bids();assert(#rows==2 and rows[1].plot==101 and rows[2].plot==102)
local _,dispatch=P.MaterialBuilderOffers(Players[3],sites,ui,128*256,4)
assert(#dispatch==0) -- Capacity routes never publish an early recruitment offer.
sites[1].repair=true
sites[1].finishRepair=true
UnitManager.GetMoveToPath=function(_,plot)return {100,plot}end
_,dispatch=P.MaterialBuilderOffers(Players[3],sites,ui,128*256,4)
assert(#dispatch==0) -- A Builder en route still uses the stock order.
x=3
_,dispatch=P.MaterialBuilderOffers(Players[3],sites,ui,128*256,4)
assert(#dispatch==1 and dispatch[1].unit==39 and dispatch[1].plot==101 and dispatch[1].x==3)
sites[1].finishRepair=false
_,dispatch=P.MaterialBuilderOffers(Players[3],sites,ui,128*256,4)
assert(#dispatch==0)
x=2
sites[1].repair=false
UnitManager=nil
_,dispatch=P.MaterialBuilderOffers(Players[3],sites,ui,128*256,4)
assert(#dispatch==0) -- Nearby capacity is not a verified dispatch route.
sites[1].repair=true;rows=bids()
assert(#rows==2 and rows[1].plot==101 and rows[2].plot==102 and rows[2].contingency) -- The repair leaves the build charge.
sites[1].repair=false
GameInfo.Units.UNIT_TEST_FARMER={Index=100}
worker.GetType=function()return 100 end
GameInfo.Improvement_ValidBuildUnits=function()
    return coroutine.wrap(function()
        coroutine.yield({UnitType='UNIT_BUILDER',ImprovementType='IMPROVEMENT_PASTURE'})
        coroutine.yield({UnitType='UNIT_BUILDER',ImprovementType='IMPROVEMENT_FIXTURE'})
        coroutine.yield({UnitType='UNIT_TEST_FARMER',ImprovementType='IMPROVEMENT_PASTURE',ValidRepairOnly=true})
    end)
end
assert(#bids()==2)
sites[1].repair=true;rows=bids();assert(#rows==2 and rows[1].plot==102 and rows[2].plot==101)
''')

    def test_queued_worker_covers_one_nearby_same_land_job(self):
        runtime().execute(r'''
GameInfo.Units={UNIT_BUILDER={Index=99}}
Players[3].GetUnits=function()return{Members=function()return ipairs({})end}end
local arrival,trainingArea=2,10
local trainingCity={GetID=function()return 88 end,GetX=function()return 2 end,GetY=function()return 0 end}
Players[3].GetCities=function()return{Members=function()return ipairs({trainingCity})end}end
ui.GetEconomyCityNumber=function(_,cityID,kind,index)
    assert(cityID==88)
    if kind=='currentUnit' then return 99 end
    assert(kind=='unitTurns' and index==99);return arrival
end
Map.GetPlotDistance=function(x1,y1,x2,y2)return math.abs(x1-x2)end
Map.GetPlot=function()return{GetArea=function()return{GetID=function()return trainingArea end}end}end
basePlot.GetArea=function()return{GetID=function()return 10 end}end
specPlot.GetArea=basePlot.GetArea
basePlot.GetX=function()return 3 end;specPlot.GetX=function()return 20 end
local first={player=3,city=42,plot=101,improvements={5},deltaQ8=8192,jobValueQ8=10240,ordinaryQ8=10240}
local second={player=3,city=99,plot=102,improvements={6},deltaQ8=6144,jobValueQ8=8192,ordinaryQ8=8192}
local function bids()return P.MaterialBuilderOffers(Players[3],{first,second},ui,128*256)end
local rows=bids();assert(#rows==1 and rows[1].plot==102)
specPlot.GetX=function()return 4 end
rows=bids();assert(#rows==1 and rows[1].plot==102) -- One queued worker credits one opening.
trainingArea=11;assert(#bids()==2) -- Near across water does not cover either.
trainingArea=10;arrival=6;assert(#bids()==2)
arrival=nil;rows=bids();assert(#rows==1 and rows[1].plot==102)
''')

    def test_builder_sponsorship_prices_only_uncredited_and_nearby_unstaffed_work(self):
        runtime().execute(r'''
GameInfo.Units={UNIT_BUILDER={Index=99}}
Players[3].GetUnits=function()return{Members=function()return ipairs({})end}end
ui.GetEconomyCityNumber=function()return -1 end
Map.GetPlotDistance=function(x1,y1,x2,y2)return math.abs(x1-x2)end
basePlot.GetX=function()return 3 end;specPlot.GetX=function()return 4 end
local sites={
    {player=3,city=42,plot=101,improvements={5},deltaQ8=30*256,jobValueQ8=40*256,ordinaryQ8=40*256},
    {player=3,city=42,plot=102,improvements={6},deltaQ8=20*256,jobValueQ8=20*256,ordinaryQ8=20*256},
}
local function bids()return P.MaterialBuilderOffers(Players[3],sites,ui,128*256)end
local rows=bids()
assert(#rows==2 and rows[1].deltaQ8==20*256 and rows[2].deltaQ8==20*256)
sites[2].ordinaryQ8=10*256
rows=bids();assert(rows[1].deltaQ8==15*256) -- The second job can restore the same Service.
sites[2].ordinaryQ8=-10*256
rows=bids();assert(rows[1].deltaQ8==10*256) -- A second charge is optional.
specPlot.GetX=function()return 7 end
rows=bids()
assert(#rows==1 and rows[1].plot==101 and rows[1].deltaQ8==10*256)
sites[1].deltaQ8=40*256
assert(#bids()==0)
''')

    def test_built_customer_and_legal_producer_can_justify_first_unlock(self):
        runtime().execute(r'''
GameInfo.Improvements[5].PrereqTech='TECH_FARMS_FIXTURE'
GameInfo.Technologies={TECH_FARMS_FIXTURE={Index=28}}
Players[3].GetTechs=function()return{HasTech=function()return false end}end
local customerPlot=setmetatable({GetIndex=function()return 104 end,GetDistrictType=function()return 0 end},
    {__index=basePlot})
Map.GetAdjacentPlots=function()return{basePlot,customerPlot}end
local customer={GetID=function()return 99 end,GetOwner=function()return 3 end,GetBuildings=function()
    return{HasBuilding=function(_,id)return id==8 end,IsPillaged=function()return false end,
        GetBuildingLocation=function()return 104 end}
end}
local getCity=Cities.GetPlotPurchaseCity
Cities.GetPlotPurchaseCity=function(plot)return plot==customerPlot and customer or getCity(plot)end
local phase={type='BUILDING_CSC_BAKERS_WATER_MILL',unlock=0,turns=15}
CSC_AI_EconomyAdapters={SupplyValue=function()end,MaterialJobValue=function(_,_,kind,plot,index,ready,pending)
    assert(kind=='base' and plot==basePlot and index==5 and ready==8)
    return pending==phase and 9*256 or 0
end}
local function bids(legal)
    local research,cs={},chains()
    cs[1].economy={horizon=30,seconds={phase}}
    local _,offers=P.MaterialDeductions(Players[3],true,64*256,0,function(pid,id,hash)
        assert(pid==3 and id==42 and hash==109);return legal
    end,false,{chains=cs,Research=function()return 3 end},research)
    for _,offer in ipairs(offers)do assert(offer.deltaQ8==nil)end
    return research['tech:28']
end
assert(bids(false)==nil)
local proposal=assert(bids(true));assert(proposal.value==9*256 and proposal.jobs[101])
''')


if __name__ == '__main__':
    unittest.main()
