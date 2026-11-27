"""Exercise the real fact/decision modules, including unavailable and frontier paths."""
from pathlib import Path
import re
import sqlite3
import unittest
from lupa.lua51 import LuaRuntime

ROOT = Path(__file__).resolve().parents[3]
AI = ROOT / 'Civ Supply Chains/Lua_UI/AI'


class Boundaries(unittest.TestCase):
    def test_advanced_setup_gates_planner_before_first_include(self):
        publisher = (AI/'CSC_AI_BakersGameplay.lua').read_text(encoding='utf-8')
        for option, compatible, expected in (
                ('false', True, False), ('0', True, False), ('"0"', True, False),
                ('true', False, False), ('nil', False, False),
                ('true', True, True), ('nil', True, True)):
            with self.subTest(option=option, compatible=compatible):
                vm=LuaRuntime()
                vm.execute("GameConfiguration={GetValue=function(key) assert(key=='CSC_ADVANCED_AI_PLANNING'); return "
                           +option+" end}; function include(name) first=name;error('observed include') end")
                if compatible:
                    vm.execute('function CE_AIDistrictScoresStatus() end')
                ok,_ = vm.execute('local ok,err=pcall(function()\n'+publisher+'\nend);return ok,err')
                self.assertEqual(ok,not expected)
                self.assertEqual(vm.globals().first,'CSC_AdjacencyCore' if expected else None)

    def test_raw_invoice_survives_tied_buyers_while_legacy_screen_stays_conservative(self):
        vm=LuaRuntime()
        vm.execute('''
ExposedMembers={};local gold={GetPlotPurchaseCost=function()return 40 end}
local first={GetID=function()return 1 end,GetGold=function()return gold end}
local second={GetID=function()return 2 end,GetGold=function()return gold end}
CityManager={GetCity=function()return first end}
Players={[3]={GetCities=function()return{Members=function()
 local i=0;return function()i=i+1;if i==1 then return 1,first elseif i==2 then return 2,second end end end}end}}
''')
        vm.execute((ROOT/'Civ Supply Chains/Lua_UI/Adjacencies/CSC_AdjacencyUI.lua').read_text(encoding='utf-8'))
        vm.execute('''
assert(ExposedMembers.CSC_Adjacency.GetPlotPurchaseQuote(3,1,7)==nil)
assert(ExposedMembers.CSC_Adjacency.GetRawPlotPurchaseQuote(3,1,7)==40)
''')

    def facts_vm(self):
        vm = LuaRuntime()
        vm.execute('''
function info(rows)
 local result={};for _,r in ipairs(rows)do result[r.Technology or r.Civic]=r end
 return setmetatable(result,{__call=function()local i=0;return function()i=i+1;return rows[i]end end})
end
local empty=info({})
GameInfo={CSC_QuarterFlowBuildings=empty,CSC_QuarterCustomerBuildings=empty,
 ModifierArguments=empty,BuildingPrereqs=empty,MutuallyExclusiveBuildings=empty,
 BuildingReplaces=empty,TechnologyPrereqs=info({
 {Technology='A',PrereqTech='B'},{Technology='A',PrereqTech='C'},
 {Technology='B',PrereqTech='D'},{Technology='C',PrereqTech='D'}}),
 CivicPrereqs=empty,Technologies=info({{Technology='A',Index=1},{Technology='B',Index=2},
 {Technology='C',Index=3},{Technology='D',Index=4}}),Civics=empty}
rate=1
local tech={HasTech=function()return false end,GetResearchCost=function()return 10 end,
 GetResearchProgress=function()return 0 end,GetScienceYield=function()return rate end}
player={GetID=function()return 1 end,GetTechs=function()return tech end,
 GetCulture=function()return{}end,GetCities=function()return{Members=function()return function()end end}end}
PlayerConfigurations={};placement={ReadChains=function()return{}end}
''')
        vm.execute((AI / 'CSC_AI_EconomyFacts.lua').read_text(encoding='utf-8'))
        return vm

    def test_research_dag_counts_shared_prerequisite_once_and_missing_rate_is_unknown(self):
        vm=self.facts_vm()
        vm.execute('''
assert(CSC_AI_EconomyFacts.New(player,placement,{}).Research('tech','A')==40)
assert(CSC_AI_EconomyFacts.New(player,placement,{GetEconomyResearchNumbers=function()return{cost=10}end}).Research('tech','A')==40)
rate=0;assert(CSC_AI_EconomyFacts.New(player,placement,{}).Research('tech','A')==math.huge)
''')

    def test_producer_unlock_qualifies_only_the_exact_mapped_bare_supplier(self):
        vm=self.facts_vm()
        vm.execute('''
local function rows(entries)
    return function()
        local i=0
        return function()i=i+1;return entries[i]end
    end
end
local sawmill={Index=7,ImprovementType='IMPROVEMENT_SAWMILL',PrereqTech='A'}
GameInfo.Improvements={IMPROVEMENT_SAWMILL=sawmill}
GameInfo.Improvement_ValidResources=rows({
    {ResourceType='RESOURCE_BAMBOO',ImprovementType=sawmill.ImprovementType},
})
GameInfo.CSC_MaterialTransactions=rows({
    {TransactionId='BAMBOO_INPUT',QuarterKey='TAILORS',
        ProducerBuildingType='WORKSHOP',MaterialClass='BASE'},
})
GameInfo.CSC_MaterialTransactionYields=rows({
    {TransactionId='BAMBOO_INPUT',LegKey='CULTURE',Recipient='PRODUCER'},
})
GameInfo.CSC_MaterialTransactionInputHosts=rows({
    {TransactionId='BAMBOO_INPUT',LegKey='CULTURE',ImprovementType=sawmill.ImprovementType},
})
local legal,existing=true,-1
local bamboo={GetImprovementType=function()return existing end}
Map={GetPlotByIndex=function(i)if i==123 then return bamboo end end}
ImprovementBuilder={CanHaveImprovement=function(plot,index,id)
    assert(plot==bamboo and index==7 and id==1)
    return legal
end}
GameInfo.Civics.CIVIC_OTHER={Index=1}
player.GetCulture=function()return{HasCivic=function()return false end}end
local snapshot=CSC_AI_EconomyFacts.New(player,placement,{})
local producer={BuildingType='WORKSHOP',PrereqTech='A'}
local chain={profile={key='TAILORS',base='BASE'}}
local material={plot=123,resource='RESOURCE_BAMBOO'}
assert(snapshot.ProducerUnlocksBase(chain,producer,material))
sawmill.PrereqCivic='CIVIC_OTHER'
assert(not snapshot.ProducerUnlocksBase(chain,producer,material))
sawmill.PrereqCivic=nil
producer.BuildingType='OTHER'
assert(not snapshot.ProducerUnlocksBase(chain,producer,material))
producer.BuildingType='WORKSHOP'
legal=false
assert(not snapshot.ProducerUnlocksBase(chain,producer,material))
legal=true;existing=8
assert(not snapshot.ProducerUnlocksBase(chain,producer,material))
''')

    def test_partial_plot_ui_record_keeps_available_gameplay_staffing(self):
        vm=self.facts_vm()
        vm.execute('''
local snapshot=CSC_AI_EconomyFacts.New(player,placement,{GetEconomyPlotFacts=function()return{yields={YIELD_PRODUCTION=2}}end})
local facts=snapshot.PlotFacts({GetIndex=function()return 99 end,GetWorkerCount=function()return 1 end})
assert(facts.workers==1 and facts.yields.YIELD_PRODUCTION==2)
''')

    def test_supply_counterfactual_uses_real_adjacency_threshold_and_multiplier(self):
        vm=self.facts_vm()
        vm.execute('DefenseTypes={DISTRICT_GARRISON=0,DISTRICT_OUTER=1}')
        vm.execute((ROOT/'Civ Supply Chains/Lua_UI/Adjacencies/CSC_AdjacencyCore.lua').read_text(encoding='utf-8'))
        vm.execute('''
local A=CSC_Adjacency
local function plot(i)return{GetIndex=function()return i end}end
local center,first,second=plot(10),plot(1),plot(2)
A.PlotsInBand=function()return{first,second}end
A.Eligible=function()return true end
A.Sources.FROM_RINGS_TEST_RESOURCE={Quantity=function()return 1 end}
A.ByDistrict.QUARTER={
 {ID='resource',AdjacencyType='FROM_RINGS_TEST_RESOURCE',ProvideType='SelfBonus',YieldType='YIELD_PRODUCTION',YieldChange=.5},
 {ID='policy',AdjacencyType='FROM_UNCONDITIONAL_BONUS',ProvideType='SelfMultiplier',YieldType='YIELD_PRODUCTION',YieldChange=100}}
local snapshot=CSC_AI_EconomyFacts.New(player,placement,{})
local city={GetID=function()return 7 end}
local profile={key='BAKERS',district={DistrictType='QUARTER'}}
assert(snapshot.DirectAmounts(city,center,profile).YIELD_PRODUCTION==2)
assert(snapshot.DirectAmounts(city,center,profile,2).YIELD_PRODUCTION==0)
assert(snapshot.SupplyAdjacencyLoss({city=city,plot=center,profile=profile},2).YIELD_PRODUCTION==2)
''')

    def bid_vm(self):
        vm = LuaRuntime()
        vm.execute('''
CSC_AI_EconomyModel={Forecast=function(site)return{valueQ8=site.value,adjacency=4,streams={},omissions={}}end}
CSC_AI_EconomyFacts={}
function plot(index,owner)
 return{GetIndex=function()return index end,GetX=function()return index end,GetY=function()return 0 end,
 GetOwner=function()return owner end,GetResourceType=function()return -1 end,GetDistrictType=function()return -1 end,
 CanHaveDistrict=function()return true end}
end
plots={[1]=plot(1,1),[2]=plot(2,-1),[3]=plot(3,-1)}
local city={GetID=function()return 7 end,GetX=function()return 0 end,GetY=function()return 0 end,
 GetDistricts=function()return{HasDistrict=function()return hasQuarter==true end}end}
local player={GetID=function()return 1 end,GetCities=function()return{Members=function()
 local done=false;return function()if not done then done=true;return 1,city end end end}end}
PlayersVisibility={[1]={IsRevealed=function()return true end}}
Map={GetPlotByIndex=function(i)return plots[i]end,GetPlot=function()return plots[1]end,
 GetPlotDistance=function()return 1 end,GetAdjacentPlots=function()return{plots[1]}end}
Cities={GetPlotPurchaseCity=function(p)if p:GetOwner()==1 then return city end end}
GameInfo={Resources={}};Game={GetCurrentGameTurn=function()return 3 end};print=function()end
CSC_Adjacency={PlotsInBand=function()return{plots[1],plots[2],plots[3]}end,HasTag=function()return false end}
local profile={key='BAKERS',district={Index=36,Hash=1,RequiresPopulation=true}}
placement={StageTwoProfiles=function()return{profile}end}
invoice=40
snapshot={player=player,id=1,cities={[7]={object=city}},
 DistrictCapacity=function()return{known=true,used=1,allowed=2,population=4,reason='ready'}end,
 ui={GetLegalDistrictTargets=function()error('Current production menu must not limit native future bids')end,GetPlotPurchaseQuote=function()return 40 end,GetRawPlotPurchaseQuote=function(_,_,i)if i==3 then return invoice end;return 50 end},
 Geometry=function()return{upper=4}end,
 Site=function(_,p)return{value=p:GetIndex()*1000,baseCount=1}end,Price=function()end}
early={{player=1,city=7,district=36,plot=1,delta=48*256}}
''')
        vm.execute((AI / 'CSC_AI_EconomyAdapters.lua').read_text(encoding='utf-8'))
        return vm

    def test_complete_bid_covers_future_owned_and_quoted_frontier_with_managed_deferral(self):
        vm=self.bid_vm()
        vm.execute('''
local entries,stats=CSC_AI_EconomyAdapters.QuarterBids(snapshot,placement,{},early)
assert(#entries==3 and stats.final==3)
for _,entry in ipairs(entries)do assert(entry.delta==0 and entry.finalQ8>entry.plot*1000)end
snapshot.ui.GetPlotPurchaseQuote=function()return nil end
local blocked,scope=CSC_AI_EconomyAdapters.QuarterBids(snapshot,placement,{},early)
assert(#blocked==1 and scope.buyerBlocked==2 and blocked[1].finalQ8>1000 and scope.managed)
invoice=nil
local fallback,failed=CSC_AI_EconomyAdapters.QuarterBids(snapshot,placement,{},early)
assert(#fallback==1 and failed.invoiceDeferred==1 and failed.managed and not failed.fallback)
''')

    def test_two_quarter_types_share_land_checks_and_refresh_after_purchase(self):
        self.bid_vm().execute('''
local bakers=placement.StageTwoProfiles()[1]
local tailors={key='TAILORS',district={Index=37,Hash=2,RequiresPopulation=true}}
placement.StageTwoProfiles=function()return{bakers,tailors}end
local reads=0
local revealed=PlayersVisibility[1].IsRevealed
PlayersVisibility[1].IsRevealed=function(...)
 reads=reads+1;return revealed(...)
end
local E=CSC_AI_EconomyAdapters
local entries,stats=E.QuarterBids(snapshot,placement,{},{})
assert(reads==3 and stats.evaluated==6 and #entries==6)
-- A rival's purchase retires this frontier plot for both profiles next pass.
plots[2]=plot(2,2);reads=0
entries,stats=E.QuarterBids(snapshot,placement,{},{})
assert(reads==3 and stats.evaluated==4 and #entries==4)
for _,row in ipairs(entries)do assert(row.plot~=2)end
''')

    def test_minimum_two_site_reaches_publication_on_owned_and_frontier_paths(self):
        vm=self.bid_vm()
        vm.execute('''
local E=CSC_AI_EconomyAdapters
local geometry=2
snapshot.Geometry=function()return{upper=geometry}end
CSC_AI_EconomyModel.Forecast=function(site)return{valueQ8=site.value,adjacency=geometry,streams={},omissions={}}end
local entries,stats=E.QuarterBids(snapshot,placement,{},early)
assert(#entries==3 and stats.final==3 and stats.qualityDeferred==0)
for _,entry in ipairs(entries)do
 assert(entry.adjacency==2 and entry.finalQ8==entry.plot*1000+48*256)
 assert(entry.preferenceQ8==48*256)
end
geometry=1
entries,stats=E.QuarterBids(snapshot,placement,{},early)
assert(#entries==0 and stats.final==0 and stats.qualityDeferred==3)
''')

    def test_pair_qualifies_one_adjacency_and_credits_its_forecast_at_publication(self):
        self.bid_vm().execute('''
local E=CSC_AI_EconomyAdapters
E.AnchoredConnectionsEnabled=true
E.ProspectiveConnectionsEnabled=true
GameInfo.Districts={[36]={RequiresPopulation=true},[8]={RequiresPopulation=true}}
local slots,ready,gold,growth=2,5,1,nil
snapshot.DistrictCapacity=function()return{known=true,used=0,allowed=slots,population=6,reason='ready',nextSlotTurns=growth}end
snapshot.Geometry=function()return{upper=1}end
snapshot.Supply=function()return{base={{plot=16}}}end
snapshot.Site=function(_,p)return{city=7,value=1000,plot=p:GetIndex(),baseCount=1,adjacency=1,
    suppliers={{kind='base',plot=16,ready=2}},horizon=50,quarterReady=4,
    quarterWork={unlock=0,turns=4}}end
snapshot.CustomerOptions=function()return{{city=7,district=8,family='HARBOR',plot=20,adjacency=2,
    bestAdjacency=2,displacedAdjacency=0,stages={[2]=true}}}end
snapshot.ProspectiveCustomerReady=function()return ready,0,ready end
snapshot.ProjectedConnectionYields=function(_,district,plot)
    assert(district==8 and plot==20)
    return{YIELD_GOLD=gold}
end
local forecasts=0
CSC_AI_EconomyModel.Forecast=function(site)
    forecasts=forecasts+1
    return{valueQ8=site.value,adjacency=1,streams={},omissions={}}
end
local function offers()return E.QuarterBids(snapshot,placement,{},{})end
local entries=offers()
assert(#entries==3)
for _,entry in ipairs(entries)do
    assert(entry.adjacency==1 and entry.pairedAdjacency==2 and entry.pairReady==9)
    assert(entry.adjacencyPreferenceQ8==48*256 and entry.prospectiveLayout.plot==20)
    assert(entry.economicQ8==1000 and entry.ordinaryBidQ8==0)
end
gold=2
assert(offers()[1].adjacencyPreferenceQ8==144*256)
slots=1
local before=forecasts
local deferred,stats=offers()
assert(#deferred==0 and forecasts==before and stats.qualityDeferred==3
    and stats.qualityBoundDeferred==3 and stats.unknown==0)
growth=5 -- Customer first for five turns, Quarter can start as the slot opens.
assert(#offers()==3)
growth=6
assert(#offers()==0)
slots=2;ready=49
assert(#offers()==0)
ready=5;gold=0
assert(#offers()==0)
gold=1;E.ProspectiveConnectionsEnabled=false
assert(#offers()==0)
-- Competing customers use the real ranking path. The Stage 2 seller
-- is preferred until another site's earlier district income outweighs it.
E.ProspectiveConnectionsEnabled=true
local lateAdj=2
snapshot.CustomerOptions=function()
    return {{city=7,district=8,family='HARBOR',plot=20,adjacency=2,bestAdjacency=2,displacedAdjacency=0,stages={[2]=true}},
            {city=7,district=9,family='HUB',plot=21,adjacency=lateAdj,bestAdjacency=lateAdj,displacedAdjacency=0,stages={[3]=true}}}
end
GameInfo.Districts[9]={RequiresPopulation=true}
local siteReader=snapshot.Site
snapshot.Site=function(...)
    local site=siteReader(...)
    site.seconds={{unlock=0,turns=2}};site.third={unlock=25,turns=3}
    return site
end
snapshot.ProjectedConnectionYields=function()return {YIELD_GOLD=1}end
snapshot.CustomerStageSchedule=function()return {[2]=11,[3]=28}end
assert(offers()[1].prospectiveLayout.plot==20)
lateAdj=4
assert(offers()[1].prospectiveLayout.plot==21)
snapshot.CustomerOptions=function()return {{city=7,district=9,family='TOWN',plot=21,adjacency=3,
    bestAdjacency=3,displacedAdjacency=0,stages={},goodsProvider=true}}end
assert(offers()[1].prospectiveLayout.role=='provider')
snapshot.ProjectedConnectionYields=function()return {YIELD_GOLD=0}end
assert(#offers()==0)
''')

    def test_full_city_retains_future_bids_and_protection_without_raising_values(self):
        vm=self.bid_vm()
        vm.execute('''
local E=CSC_AI_EconomyAdapters
snapshot.DistrictCapacity=function()return{known=true,used=2,allowed=2,population=6,reason='full'}end
early[#early+1]={player=1,city=7,district=10,plot=3,delta=-1000}
local rows,stats=E.QuarterBids(snapshot,placement,{},early)
assert(#rows==4 and rows[4].district==10 and stats.capacityFull==1 and stats.managed)
assert(rows[1].capacityState=='full' and rows[1].capacityUsed==rows[1].capacityAllowed)
local priorBid=rows[1].finalQ8
snapshot.DistrictCapacity=function()return{known=true,used=2,allowed=3,population=7,reason='ready'}end
rows,stats=E.QuarterBids(snapshot,placement,{},early)
assert(#rows==4 and stats.capacityReady==1 and stats.final==3)
assert(rows[1].capacityUsed==2 and rows[1].capacityAllowed==3 and rows[1].capacityState=='ready')
assert(rows[1].finalQ8==priorBid) -- readiness labels do not inflate the economic price
''')

    def test_unknown_capacity_keeps_planning_but_never_claims_free_capacity(self):
        vm=self.bid_vm()
        vm.execute('''
local E=CSC_AI_EconomyAdapters
snapshot.DistrictCapacity=function()return{known=false,reason='stale'}end
local rows,stats=E.QuarterBids(snapshot,placement,{},early)
assert(#rows==3 and stats.capacityUnknown==1 and stats.managed)
assert(rows[1].capacityState=='stale' and rows[1].capacityUsed==nil and rows[1].capacityAllowed==nil)
hasQuarter=true
snapshot.DistrictCapacity=function()error('Existing construction must not need a new slot')end
rows,stats=E.QuarterBids(snapshot,placement,{},early)
assert(#rows==0 and stats.capacityUnknown==0 and stats.capacityFull==0)
''')

    def test_population_exempt_definition_does_not_need_capacity_reader(self):
        vm=self.bid_vm()
        vm.execute('''
placement.StageTwoProfiles()[1].district.RequiresPopulation=0
snapshot.DistrictCapacity=function()error('Exempt district needs no population slot')end
local rows,stats=CSC_AI_EconomyAdapters.QuarterBids(snapshot,placement,{},early)
assert(#rows==3 and stats.final==3 and stats.capacityReady==1 and stats.capacityUnknown==0)
''')

    def test_complete_frontier_bid_is_counted_and_tracked_without_changing_packet(self):
        # Execute the real diagnostic tail, not a second implementation of its
        # classification. No CE publisher or gameplay order is installed here.
        vm=LuaRuntime()
        vm.execute('''
lines={};print=function(s)lines[#lines+1]=s end
version=4;turn=5;capacity=4096;managedTypes={};declines={};nominations={}
CE_AIDistrictScoresReceipt=function()end
entries={
 {player=1,city=7,district=36,plot=3,delta=0,finalQ8=2048,frontier=true,adjacency=4,purchaseGold=50},
 {delta=0,finalQ8=-262144},{delta=256},{delta=128,customer=true},{delta=-256,weak=true},{delta=-128}}
''')
        source=(AI/'CSC_AI_BakersGameplay.lua').read_text(encoding='utf-8')
        start=source.index('    local siteBids, weakSites, customerSites =')
        vm.execute(source[start:source.index('    if builderStatus then',start)])
        vm.execute('''
assert(#previousOffers.frontier==1 and #previousOffers.economy==2)
assert(previousOffers.frontier[1]==entries[1] and entries[1].delta==0 and entries[1].finalQ8==2048)
assert(lines[1]:find('deltaQ8=0 finalQ8=2048',1,true))
assert(lines[2]:find('bids=2 weak=1 customer=1',1,true))
''')

    def test_capacity_fact_batches_cache_once_and_reject_stale_population_or_inventory(self):
        vm=self.facts_vm()
        vm.execute('''
GameInfo.Yields={YIELD_PRODUCTION={Index=1}}
GameInfo.Districts={[1]={RequiresPopulation=true},[2]={RequiresPopulation=false},
 [3]={RequiresPopulation=true,InternalOnly=true}}
local function d(kind,index,complete)return{GetType=function()return kind end,
 GetX=function()return index end,GetY=function()return 0 end,
 IsComplete=function()return complete end,IsPillaged=function()return false end}end
local inventory={d(2,10,true),d(1,11,false),d(3,12,true)}
local city={GetID=function()return 7 end,GetPopulation=function()return 4 end,
 GetBuildQueue=function()return{}end,GetBuildings=function()return{}end,
 GetDistricts=function()return{GetNumDistricts=function()return #inventory end,
 GetDistrictByIndex=function(_,i)return inventory[i+1]end}end}
player.GetCities=function()return{Members=function()local done=false;return function()
 if not done then done=true;return 1,city end end end}end
Map={GetPlot=function(x)return{GetIndex=function()return x end}end}
local calls=0;local ui={GetDistrictCapacity=function()calls=calls+1;return{population=4,used=1,allowed=3}end}
local s=CSC_AI_EconomyFacts.New(player,placement,ui)
assert(s.DistrictCapacity(city).known and s.DistrictCapacity(city).allowed==3 and calls==1)
assert(s.cities[7].populationDistricts==1) -- unfinished counted; internal/exempt not counted
ui.GetDistrictCapacity=function()return{population=3,used=1,allowed=3}end
assert(CSC_AI_EconomyFacts.New(player,placement,ui).DistrictCapacity(city).reason=='stale')
ui.GetDistrictCapacity=function()return{population=4,used=0,allowed=3}end
assert(not CSC_AI_EconomyFacts.New(player,placement,ui).DistrictCapacity(city).known)
GameInfo.GlobalParameters={DISTRICT_POPULATION_REQUIRED_PER={Value='3'}}
local pop,slots,growth=6,2,4
city.GetPopulation=function()return pop end
ui.GetDistrictCapacity=function()return{population=pop,used=1,allowed=slots,turnsToGrowth=growth}end
local function nextSlot()return CSC_AI_EconomyFacts.New(player,placement,ui).DistrictCapacity(city).nextSlotTurns end
assert(nextSlot()==4)
growth=-1;assert(nextSlot()==nil)
growth=1;pop=5;assert(nextSlot()==nil)
pop=6;slots=3;assert(nextSlot()==nil)
ui.GetDistrictCapacity=nil
assert(CSC_AI_EconomyFacts.New(player,placement,ui).DistrictCapacity(city).reason=='unavailable')
''')

    def test_quality_bands_cannot_turn_an_economic_loss_into_a_positive_investment(self):
        vm=LuaRuntime(unpack_returned_tuples=True)
        vm.execute('CSC_AI_EconomyModel={};CSC_AI_EconomyFacts={}')
        vm.execute((AI/'CSC_AI_EconomyAdapters.lua').read_text(encoding='utf-8'))
        vm.execute('''
local E=CSC_AI_EconomyAdapters
local s={baseCount=1,specialtyCount=0}
assert(E.PlacementValue({adjacency=1,valueQ8=1000000},s)==E.DeferredQuarterQ8)
assert(E.PlacementValue({adjacency=2,valueQ8=100*256},s)==(100+48)*256)
assert(E.PlacementValue({adjacency=2.5,valueQ8=100*256},s)==(100+96)*256)
assert(E.PlacementValue({adjacency=2,valueQ8=-1},s)==-1)
assert(E.PlacementValue({adjacency=4,valueQ8=-1},s)==-1)
local a=E.PlacementValue({adjacency=3,valueQ8=100*256},s)
local b=E.PlacementValue({adjacency=4,valueQ8=100*256},s)
assert(a==(100+144)*256 and b==(100+288)*256)
assert(E.PlacementValue({adjacency=8,valueQ8=100*256},s)==676*256)
s.baseCount=0;assert(E.PlacementValue({adjacency=5,valueQ8=1000000},s)==E.DeferredQuarterQ8)
s.baseCount=1;s.specialtyCount=1
assert(E.PlacementValue({adjacency=2,valueQ8=100*256},s)==(100+112)*256)
assert(E.PlacementValue({adjacency=4,valueQ8=100*256},s)>b)
assert(E.PlacementValue({adjacency=4,valueQ8=100*256},s,200*256)<=0)
''')

    def test_placement_ranks_feasible_mills_after_quality_gate_and_premium(self):
        vm=LuaRuntime()
        vm.execute((AI/'CSC_AI_EconomyModel.lua').read_text(encoding='utf-8'))
        vm.execute('CSC_AI_EconomyFacts={}')
        vm.execute((AI/'CSC_AI_EconomyAdapters.lua').read_text(encoding='utf-8'))
        vm.execute('''
local M,E=CSC_AI_EconomyModel,CSC_AI_EconomyAdapters
local site={city=1,horizon=50,quarterReady=0,adjacency=2,baseCount=1,materialYield='YIELD_FOOD',
 direct={{id='base',yield='YIELD_PRODUCTION',amount=2}},
 suppliers={{kind='base',plot=10,city=1,ready=0,worked=true}},seconds={
 {type='WATER',unlock=0,turns=8,terrain=0},
 {type='WIND',unlock=20,turns=8,terrain=1}}}
local function price(stream,horizon)return math.floor(stream.amount*(horizon-stream.ready)*256)end
assert(M.Forecast(site,price).alternative=='WATER')
local function placement(q)return E.PlacementValue(q,site)end
local chosen=M.Forecast(site,price,placement)
assert(chosen.alternative=='WIND' and chosen.adjacency==3 and chosen.selectionQ8>0)
-- Water +3 earns more raw utility, but profitable Wind +4 earns the stronger
-- placement bid. Neither premium may resurrect a loss-making producer plan.
site.adjacency=3;site.seconds[2].terrain=1
site.seconds[1].terrain=0
local raw=M.Forecast(site,price)
assert(raw.alternative=='WATER')
chosen=M.Forecast(site,price,placement)
assert(chosen.alternative=='WIND' and chosen.adjacency==4)
site.direct[1].amount=-100
assert(M.Forecast(site,price,placement).selectionQ8<=0)
''')

    def test_local_mill_geometry_uses_live_counts_and_production_multiplier(self):
        vm=self.facts_vm()
        vm.execute('''
CSC_Adjacency={ByDistrict={QUARTER={
 {ModifierOwner='BuildingModifiers',WhoIsTheOwner='BUILDING_CSC_BAKERS_WIND_MILL',YieldType='YIELD_PRODUCTION',ProvideType='SelfBonus'},
 {ModifierOwner='BuildingModifiers',WhoIsTheOwner='BUILDING_CSC_BAKERS_WATER_MILL',YieldType='YIELD_PRODUCTION',ProvideType='SelfBonus'}}},
 Count=function()return 1 end,Amount=function()return 1 end}
local snapshot=CSC_AI_EconomyFacts.New(player,placement,{})
snapshot.DirectAmounts=function()return{YIELD_PRODUCTION=2},{YIELD_PRODUCTION=100},{YIELD_PRODUCTION=1}end
local city={GetID=function()return 7 end}
local plot={GetIndex=function()return 99 end,IsRiver=function()return false end}
local geometry=snapshot.Geometry(city,plot,{key='BAKERS',district={DistrictType='QUARTER'}})
assert(geometry.base==2 and geometry.upper==4)
assert(geometry.mills.BUILDING_CSC_BAKERS_WIND_MILL==2)
assert(geometry.mills.BUILDING_CSC_BAKERS_WATER_MILL==nil)
''')

    def test_native_customer_sql_deduplicates_all_stages_and_expands_replacements(self):
        db = sqlite3.connect(':memory:')
        db.executescript('''
CREATE TABLE Types(Type PRIMARY KEY,Kind);
CREATE TABLE Yields(YieldType PRIMARY KEY,Name,IconString,OccupiedCityChange,DefaultValue);
CREATE TABLE AiFavoredItems(ListType,Item,Favored,Value);
CREATE TABLE AiLists(ListType,System);
CREATE TABLE BehaviorTreeNodes(NodeId,TreeName,NodeType);
CREATE TABLE TreeData(DefnId,NodeId,TreeName,DefaultData);
CREATE TABLE Districts(DistrictType PRIMARY KEY);
CREATE TABLE TypeTags(Type,Tag);
CREATE TABLE DistrictReplaces(CivUniqueDistrictType,ReplacesDistrictType);
CREATE TABLE CSC_QuarterCustomerBuildings(QuarterKey,ProducerStage,DistrictType);
CREATE TABLE CSC_Stage3CustomerTransactions(SellerDistrictType,CustomerDistrictType);
CREATE TABLE CSC_QuarterWonderSales(QuarterKey,BuildingType,ProducerStage);
CREATE TABLE CSC_QuarterMaterialAdjacencyConfig(QuarterKey,SourceTag,SourceFilter,AdjacencyType);
CREATE TABLE Improvement_ValidResources(ImprovementType,ResourceType);
CREATE TABLE Improvement_ValidTerrains(ImprovementType,TerrainType);
CREATE TABLE Improvement_ValidFeatures(ImprovementType,FeatureType);
CREATE TABLE Improvements(ImprovementType PRIMARY KEY,Buildable,Workable);
CREATE TABLE Adjacency_YieldChanges(ID PRIMARY KEY,Description,YieldType,YieldChange,TilesRequired,AdjacentDistrict,AdjacentImprovement);
CREATE TABLE District_Adjacencies(DistrictType,YieldChangeId,PRIMARY KEY(DistrictType,YieldChangeId));
INSERT INTO Districts VALUES('DISTRICT_CSC_TAILORS_QUARTER'),('DISTRICT_CSC_BAKERS_QUARTER'),
 ('DISTRICT_COMMERCIAL_HUB'),('DISTRICT_HOLY_SITE'),('DISTRICT_HARBOR'),
 ('DISTRICT_UNIQUE_HARBOR'),('DISTRICT_THEATER'),('DISTRICT_UNIQUE_HUB');
INSERT INTO DistrictReplaces VALUES('DISTRICT_UNIQUE_HARBOR','DISTRICT_HARBOR');
INSERT INTO DistrictReplaces VALUES('DISTRICT_UNIQUE_HUB','DISTRICT_COMMERCIAL_HUB');
INSERT INTO CSC_QuarterCustomerBuildings VALUES
 ('TAILORS',2,'DISTRICT_HARBOR'),('TAILORS',4,'DISTRICT_HOLY_SITE'),
 ('TAILORS',4,'DISTRICT_THEATER'),('TAILORS',4,'DISTRICT_THEATER'),
 ('TAILORS',4,'DISTRICT_WONDER'),('TAILORS',2,'DISTRICT_CITY_CENTER');
INSERT INTO CSC_Stage3CustomerTransactions VALUES
 ('DISTRICT_CSC_TAILORS_QUARTER','DISTRICT_HOLY_SITE'),
 ('DISTRICT_CSC_TAILORS_QUARTER','DISTRICT_COMMERCIAL_HUB'),
 ('DISTRICT_CSC_BAKERS_QUARTER','DISTRICT_COMMERCIAL_HUB');
INSERT INTO CSC_QuarterWonderSales VALUES('TAILORS','BUILDING_TEST_WONDER',4);
INSERT INTO BehaviorTreeNodes VALUES (13,'Build City Improvement','Build Unit'),(23,'Build City Improvement','Build Unit');
INSERT INTO TreeData VALUES (2,23,'Build City Improvement','7');
''')
        sql = (ROOT / 'Civ Supply Chains/Data/CSC_Q_ALL_AI_Connectors.sql').read_text(encoding='utf-8')
        db.executescript(sql)
        db.executescript(sql)
        self.assertEqual(db.execute('SELECT NodeId,DefaultData FROM TreeData').fetchall(),[(23,'7')])
        customer_hosts = "SELECT DistrictType FROM District_Adjacencies WHERE YieldChangeId GLOB 'CSC_AI_CUSTOMER_*'"
        self.assertEqual({r[0] for r in db.execute(customer_hosts)},
                         {'DISTRICT_HARBOR','DISTRICT_UNIQUE_HARBOR','DISTRICT_HOLY_SITE','DISTRICT_THEATER',
                          'DISTRICT_COMMERCIAL_HUB','DISTRICT_UNIQUE_HUB'})
        self.assertEqual(db.execute('SELECT COUNT(*) FROM Adjacency_YieldChanges').fetchone()[0],16)
        db.executescript('''
INSERT OR IGNORE INTO Districts VALUES('DISTRICT_RURALCOMMUNITYA'),('DISTRICT_HOLY_SITE'),('DISTRICT_UNIQUE_RURAL');
INSERT INTO DistrictReplaces VALUES('DISTRICT_UNIQUE_RURAL','DISTRICT_RURALCOMMUNITYA');
INSERT INTO TypeTags VALUES
 ('DISTRICT_RURALCOMMUNITYA','CLASS_CSC_TAILORS_GOODS_PROVIDER'),
 ('DISTRICT_HOLY_SITE','CLASS_CSC_TAILORS_GOODS_PROVIDER'),
 ('DISTRICT_ABSENT_MOD','CLASS_CSC_TAILORS_GOODS_PROVIDER');
''')
        db.executescript(sql);db.executescript(sql)
        self.assertEqual({r[0]for r in db.execute(customer_hosts)},
            {'DISTRICT_HARBOR','DISTRICT_UNIQUE_HARBOR','DISTRICT_HOLY_SITE','DISTRICT_THEATER',
             'DISTRICT_RURALCOMMUNITYA','DISTRICT_UNIQUE_RURAL','DISTRICT_COMMERCIAL_HUB','DISTRICT_UNIQUE_HUB'})
        self.assertEqual({r[0]for r in db.execute('SELECT DISTINCT DistrictType FROM District_Adjacencies WHERE DistrictType LIKE \'%HUB\'')},
                         {'DISTRICT_COMMERCIAL_HUB','DISTRICT_UNIQUE_HUB'})
        self.assertEqual(db.execute('SELECT COUNT(*) FROM Adjacency_YieldChanges').fetchone()[0],20)
        from customer_connector_audit import audit
        self.assertTrue(audit(db)['complete'])
        self.assertTrue(any(r.get('building')=='BUILDING_TEST_WONDER'for r in audit(db)['excluded']))
        # A new gameplay-defined Quarter/customer requires no AI mapping edit.
        db.executescript('''
INSERT INTO Districts VALUES('DISTRICT_CSC_TEST_QUARTER'),('DISTRICT_TEST_CUSTOMER');
INSERT INTO CSC_Stage3CustomerTransactions VALUES('DISTRICT_CSC_TEST_QUARTER','DISTRICT_TEST_CUSTOMER');
''')
        self.assertEqual(len(audit(db)['missing']),1)
        db.executescript(sql)
        self.assertTrue(audit(db)['complete'])
        # Tag-only gameplay partners, including a Quarter with no transaction
        # rows, must propagate without adding an AI-specific relationship.
        db.executescript('''
INSERT INTO Districts VALUES('DISTRICT_CSC_TAG_ONLY_QUARTER'),('DISTRICT_URBAN_CUSTOMER');
INSERT INTO TypeTags VALUES
 ('DISTRICT_URBAN_CUSTOMER','CLASS_CSC_TEST_SALES'),
 ('DISTRICT_URBAN_CUSTOMER','CLASS_CSC_TEST_GOODS_PROVIDER'),
 ('DISTRICT_URBAN_CUSTOMER','CLASS_CSC_TAG_ONLY_SALES'),
 ('DISTRICT_ABSENT_MOD','CLASS_CSC_TAG_ONLY_SALES');
''')
        self.assertEqual(len(audit(db)['missing']),2)
        db.executescript(sql);db.executescript(sql)
        result=audit(db)
        self.assertTrue(result['complete'],result)
        self.assertEqual(result['duplicates'],[])
        edge=next(e for e in result['edges'] if e['customer']=='DISTRICT_URBAN_CUSTOMER'
                  and e['quarter']=='DISTRICT_CSC_TEST_QUARTER')
        self.assertEqual(set(edge['sources']),{'sales-tag','goods-provider'})
        # A subscribed resource extends the same source catalogue. A shared
        # improvement needs one Base match, plus sufficient coverage of its
        # valid resources. Empty-land hosts need a cluster of two.
        db.executescript('''
INSERT INTO CSC_QuarterMaterialAdjacencyConfig VALUES
 ('TEST','CLASS_CSC_TEST_BASE','','FROM_RINGS_TYPETAG_RESOURCE'),
 ('TEST','CLASS_CSC_TEST_SPEC','','FROM_RINGS_TYPETAG_RESOURCE');
INSERT INTO TypeTags VALUES ('RESOURCE_MOD_BASE','CLASS_CSC_TEST_BASE'),('RESOURCE_MOD_SPEC','CLASS_CSC_TEST_SPEC');
INSERT INTO Improvements VALUES ('FARM',1,1),('PASTURE',1,1),('MINE',1,1);
INSERT INTO Improvement_ValidResources VALUES
 ('FARM','RESOURCE_MOD_BASE'),('PASTURE','RESOURCE_MOD_BASE'),('PASTURE','OTHER'),
 ('PASTURE','ANOTHER'),('MINE','RESOURCE_MOD_SPEC');
INSERT INTO Improvement_ValidTerrains VALUES ('FARM','PLAINS');
''')
        db.executescript(sql)
        db.executescript(sql)
        rows = db.execute('''SELECT DistrictType, AdjacentImprovement, TilesRequired
                             FROM District_Adjacencies JOIN Adjacency_YieldChanges ON YieldChangeId=ID
                             WHERE AdjacentImprovement IS NOT NULL ORDER BY AdjacentImprovement''')
        self.assertEqual(list(rows), [('DISTRICT_CSC_TEST_QUARTER','FARM',2),('DISTRICT_CSC_TEST_QUARTER','PASTURE',1)])
        self.assertTrue(audit(db)['complete'])

    def test_material_terms_match_generated_native_without_unit_assumptions(self):
        import sys
        sys.path.insert(0,str(ROOT/'project/tools/transactions'))
        from population_catalogue_fixture import compile_catalogue
        with compile_catalogue(mc=True)as db:
            rows=db.execute('''SELECT b.ChildModifierId,y.Amount,a.Value
                FROM CSC_MaterialTransactionBindings b JOIN CSC_MaterialTransactionYields y USING(TransactionId,LegKey)
                JOIN ModifierArguments a ON a.ModifierId=b.ChildModifierId AND a.Name='Amount' ''').fetchall()
            self.assertEqual(len(rows),45)
            self.assertTrue(all(float(r[1])==float(r[2])for r in rows))


if __name__ == '__main__':
    unittest.main()
