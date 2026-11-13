"""Exercise the real fact/decision modules, including unavailable and frontier paths."""
from pathlib import Path
import re
import sqlite3
import unittest
from lupa.lua51 import LuaRuntime

ROOT = Path(__file__).resolve().parents[3]
AI = ROOT / 'Civ Supply Chains/Lua_UI/AI'


class Boundaries(unittest.TestCase):
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

    def test_full_city_defers_new_quarter_preserves_protection_and_reconsiders_growth(self):
        vm=self.bid_vm()
        vm.execute('''
local E=CSC_AI_EconomyAdapters
snapshot.DistrictCapacity=function()return{known=true,used=2,allowed=2,population=6,reason='full'}end
local geometry=snapshot.Geometry
snapshot.Geometry=function()error('Full city must not price candidate ledgers')end
early[#early+1]={player=1,city=7,district=10,plot=3,delta=-1000}
local rows,stats=E.QuarterBids(snapshot,placement,{},early)
assert(#rows==1 and rows[1].district==10 and stats.capacityDeferred==1 and stats.managed)
snapshot.DistrictCapacity=function()return{known=true,used=2,allowed=3,population=7,reason='ready'}end
snapshot.Geometry=geometry
rows,stats=E.QuarterBids(snapshot,placement,{},early)
assert(#rows==4 and stats.capacityReady==1 and stats.final==3)
assert(rows[1].capacityUsed==2 and rows[1].capacityAllowed==3)
''')

    def test_unknown_capacity_is_not_free_and_existing_quarter_bypasses_new_slot_gate(self):
        vm=self.bid_vm()
        vm.execute('''
local E=CSC_AI_EconomyAdapters
snapshot.DistrictCapacity=function()return{known=false,reason='stale'}end
local rows,stats=E.QuarterBids(snapshot,placement,{},early)
assert(#rows==0 and stats.capacityUnknown==1 and stats.managed)
hasQuarter=true
snapshot.DistrictCapacity=function()error('Existing construction must not need a new slot')end
rows,stats=E.QuarterBids(snapshot,placement,{},early)
assert(#rows==0 and stats.capacityUnknown==0 and stats.capacityDeferred==0)
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
assert(E.PlacementValue({adjacency=2,valueQ8=1000000},s)==E.DeferredQuarterQ8)
assert(E.PlacementValue({adjacency=4,valueQ8=-1},s)==-1)
local a=E.PlacementValue({adjacency=3,valueQ8=100*256},s)
local b=E.PlacementValue({adjacency=4,valueQ8=100*256},s)
assert(a>100*256 and b>a and b<500*256)
assert(E.PlacementValue({adjacency=8,valueQ8=100*256},s)<600*256)
s.baseCount=0;assert(E.PlacementValue({adjacency=5,valueQ8=1000000},s)==E.DeferredQuarterQ8)
s.baseCount=1;s.specialtyCount=1
assert(E.PlacementValue({adjacency=4,valueQ8=100*256},s)>b)
assert(E.PlacementValue({adjacency=4,valueQ8=100*256},s,-200*256)<=0)
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
CREATE TABLE DistrictReplaces(CivUniqueDistrictType,ReplacesDistrictType);
CREATE TABLE CSC_QuarterCustomerBuildings(QuarterKey,ProducerStage,DistrictType);
CREATE TABLE Adjacency_YieldChanges(ID PRIMARY KEY,Description,YieldType,YieldChange,TilesRequired,AdjacentDistrict);
CREATE TABLE District_Adjacencies(DistrictType,YieldChangeId,PRIMARY KEY(DistrictType,YieldChangeId));
INSERT INTO Districts VALUES('DISTRICT_CSC_TAILORS_QUARTER');
INSERT INTO DistrictReplaces VALUES('DISTRICT_UNIQUE_HARBOR','DISTRICT_HARBOR');
INSERT INTO CSC_QuarterCustomerBuildings VALUES
 ('TAILORS',2,'DISTRICT_HARBOR'),('TAILORS',3,'DISTRICT_HOLY_SITE'),
 ('TAILORS',4,'DISTRICT_THEATER'),('TAILORS',4,'DISTRICT_THEATER'),
 ('TAILORS',4,'DISTRICT_WONDER'),('TAILORS',2,'DISTRICT_CITY_CENTER');
''')
        sql = (ROOT / 'Civ Supply Chains/Data/CSC_AI_Connectors.sql').read_text(encoding='utf-8')
        db.executescript(sql)
        db.executescript(sql)
        self.assertEqual({r[0] for r in db.execute('SELECT DistrictType FROM District_Adjacencies')},
                         {'DISTRICT_HARBOR','DISTRICT_UNIQUE_HARBOR','DISTRICT_HOLY_SITE','DISTRICT_THEATER'})
        self.assertEqual(db.execute('SELECT COUNT(*) FROM Adjacency_YieldChanges').fetchone()[0],4)

    def test_loaded_unit_contract_leaves_match_current_source(self):
        source = (AI / 'CSC_AI_EconomyFacts.lua').read_text(encoding='utf-8')
        contract = source.split('local unitContracts={',1)[1].split('\nlocal function definitions',1)[0]
        roots = set(re.findall(r"'(MOD_CSC_[A-Z_]+)'",contract))
        files = ['CSC_Q_ALL.sql','CSC_Q_BAKERS.sql','CSC_Q_BAKERS_GOLD.sql',
                 'CSC_Q_TAILORS.sql','CSC_Q_TAILORS_GOLD.sql']
        amounts = {}
        for name in files:
            sql = (ROOT / 'Civ Supply Chains/Data' / name).read_text(encoding='utf-8')
            amounts.update({m[0]:float(m[1]) for m in re.findall(
                r"\(\s*'(MOD_CSC_[A-Z_]+)'\s*,\s*'Amount'\s*,\s*'?([0-9.]+)'?\s*\)",sql)})
        self.assertGreater(len(roots),20)
        self.assertEqual({root:amounts.get(root) for root in roots},{root:1 for root in roots})


if __name__ == '__main__':
    unittest.main()
