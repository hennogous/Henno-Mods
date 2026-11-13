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

    def test_complete_bid_covers_owned_and_all_quoted_frontier_or_falls_back(self):
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
 GetDistricts=function()return{HasDistrict=function()return false end}end}
local player={GetID=function()return 1 end,GetCities=function()return{Members=function()
 local done=false;return function()if not done then done=true;return 1,city end end end}end}
PlayersVisibility={[1]={IsRevealed=function()return true end}}
Map={GetPlotByIndex=function(i)return plots[i]end,GetPlot=function()return plots[1]end,
 GetPlotDistance=function()return 1 end,GetAdjacentPlots=function()return{plots[1]}end}
Cities={GetPlotPurchaseCity=function(p)if p:GetOwner()==1 then return city end end}
GameInfo={Resources={}};Game={GetCurrentGameTurn=function()return 3 end};print=function()end
CSC_Adjacency={PlotsInBand=function()return{plots[2],plots[3]}end,HasTag=function()return false end}
local profile={key='BAKERS',district={Index=36,Hash=1}}
placement={StageTwoProfiles=function()return{profile}end}
invoice=40
snapshot={player=player,id=1,cities={[7]={object=city}},
 ui={GetLegalDistrictTargets=function()return{1}end,GetPlotPurchaseQuote=function()return 40 end,GetRawPlotPurchaseQuote=function(_,_,i)if i==3 then return invoice end;return 50 end},
 Site=function(_,p)return{value=p:GetIndex()*1000,baseCount=1}end,Price=function()end}
early={{player=1,city=7,district=36,plot=1,delta=48*256}}
''')
        vm.execute((AI / 'CSC_AI_EconomyAdapters.lua').read_text(encoding='utf-8'))
        vm.execute('''
local entries,stats=CSC_AI_EconomyAdapters.QuarterBids(snapshot,placement,{},early)
assert(#entries==3 and stats.final==3)
for _,entry in ipairs(entries)do assert(entry.delta==0 and entry.finalQ8==entry.plot*1000)end
snapshot.ui.GetPlotPurchaseQuote=function()return nil end
local blocked,scope=CSC_AI_EconomyAdapters.QuarterBids(snapshot,placement,{},early)
assert(#blocked==3 and scope.buyerBlocked==2 and blocked[1].finalQ8==1000)
assert(blocked[2].finalQ8==0 and blocked[3].finalQ8==0)
invoice=nil
local fallback,failed=CSC_AI_EconomyAdapters.QuarterBids(snapshot,placement,{},early)
assert(fallback==early and failed.final==0 and failed.fallback)
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
