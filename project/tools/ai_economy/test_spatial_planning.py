"""Exercise spatial choices and the actual main-mod publication boundaries."""
from pathlib import Path
import unittest
from lupa.lua51 import LuaRuntime
import test_boundaries as boundaries

AI = Path(__file__).resolve().parents[3] / 'Civ Supply Chains/Lua_UI/AI'


class SpatialPlanning(unittest.TestCase):
    def test_footprint_signature_preserves_native_absence_ids(self):
        vm = LuaRuntime()
        vm.execute((AI / 'CSC_AI_EconomyFacts.lua').read_text(encoding='utf-8'))
        vm.execute('''
local values={GetTerrainType=4,GetFeatureType=-1,GetResourceType=-1,GetImprovementType=-1}
local plot={}
for name in pairs(values)do
 local method=name
 plot[method]=function()return values[method]end
end
local signature=CSC_AI_EconomyFacts.FootprintSignature
assert(signature(plot)=='4,-1,-1,-1')
values.GetResourceType=12
assert(signature(plot)=='4,-1,12,-1')
for _,invalid in ipairs({-2,1.5,math.huge,0/0,'unknown'})do
 values.GetFeatureType=invalid
 assert(signature(plot)=='_')
end
plot.GetFeatureType=nil
assert(signature(plot)=='_')
plot.GetFeatureType=function()error('native unavailable')end
assert(signature(plot)=='_')
''')

    def adapters(self):
        vm = LuaRuntime()
        vm.execute('CSC_AI_EconomyModel={};CSC_AI_EconomyFacts={}')
        vm.execute((AI / 'CSC_AI_EconomyAdapters.lua').read_text(encoding='utf-8'))
        return vm

    def test_native_terrain_and_alternative_tiles_change_customer_preference(self):
        vm = self.adapters()
        vm.execute('''
local E=CSC_AI_EconomyAdapters
local function option(plot,adj,best,displaced)
 return{city=1,district=2,family='HUB',plot=plot,adjacency=adj,
 bestAdjacency=best or adj,displacedAdjacency=displaced or 0}
end
assert(E.SpatialPlan({option(10,2)}).preference==32)
assert(E.SpatialPlan({option(10,4)}).preference==48)
assert(E.SpatialPlan({option(10,2,4)}).preference==16)
assert(E.SpatialPlan({option(10,2,4,4)}).preference==0)
assert(E.SpatialPlan({}).preference==0)
''')

    def test_pair_uses_distinct_tiles_and_families_and_keeps_second_best_footprint(self):
        vm = self.adapters()
        vm.execute('''
local E=CSC_AI_EconomyAdapters
local options={
 {city=1,district=1,family='HUB',plot=10,adjacency=4,bestAdjacency=4,displacedAdjacency=0},
 {city=1,district=1,family='HUB',plot=11,adjacency=3,bestAdjacency=4,displacedAdjacency=0},
 {city=1,district=2,family='HOLY',plot=10,adjacency=4,bestAdjacency=4,displacedAdjacency=0}}
local plan=E.SpatialPlan(options)
assert(plan.preference==80 and #plan.links==2)
assert(plan.links[1].plot~=plan.links[2].plot)
options[3].family='HUB'
assert(#E.SpatialPlan(options).links==1)
''')

    def test_cluster_bands_are_bounded_and_cannot_resurrect_losses_or_missing_base(self):
        vm = self.adapters()
        vm.execute('''
local E=CSC_AI_EconomyAdapters
local site={baseCount=3,specialtyCount=3,spatialPlan={preference=96}}
local value,why,parts=E.PlacementValue({adjacency=4,valueQ8=100*256},site)
assert(value==(100+288+64+48+32+96)*256 and why=='positive')
assert(parts.materialsQ8==144*256 and parts.layoutQ8==96*256)
site.baseCount=30;site.specialtyCount=30
assert(E.PlacementValue({adjacency=4,valueQ8=100*256},site)==value)
assert(E.PlacementValue({adjacency=4,valueQ8=-1},site)==-1)
site.baseCount=0
assert(E.PlacementValue({adjacency=6,valueQ8=100000},site)==E.DeferredQuarterQ8)
''')

    def test_future_layout_does_not_create_adjacency_or_transaction_income(self):
        vm = self.adapters()
        vm.execute((AI / 'CSC_AI_EconomyModel.lua').read_text(encoding='utf-8'))
        vm.execute('''
local site={city=1,horizon=50,quarterReady=0,adjacency=2,baseCount=1,
 direct={{id='actual',yield='YIELD_GOLD',amount=2}},seconds={},customers={}}
local function price(s,h)return s.amount*(h-s.ready)*256 end
local before=CSC_AI_EconomyModel.Forecast(site,price)
site.spatialPlan={preference=96,links={{plot=5}}}
local after=CSC_AI_EconomyModel.Forecast(site,price)
assert(after.valueQ8==before.valueQ8 and after.adjacency==2 and #after.streams==1)
''')

    def test_customer_offers_require_current_legal_targets_and_room_for_quarter(self):
        vm = self.adapters()
        vm.execute('''
local E=CSC_AI_EconomyAdapters
local city={GetID=function()return 1 end}
GameInfo={Districts={[10]={RequiresPopulation=1},[20]={RequiresPopulation=1,Hash=200},
 [21]={RequiresPopulation=1,Hash=210}}}
local free=1;local legal={5,6}
local snapshot={id=1,cities={[1]={object=city}},
 DistrictCapacity=function()return{known=true,used=0,allowed=free}end,
 ui={GetLegalDistrictTargets=function()return legal end}}
local row={economy=true,city=1,district=10,plot=2,finalQ8=100,
 customerLayout={{city=1,district=20,plot=5,preference=32},
 {city=1,district=21,plot=6,preference=40}}}
assert(#E.CustomerOffers(snapshot,{row},{})==0)
free=2;local offers=E.CustomerOffers(snapshot,{row},{})
assert(#offers==1 and offers[1].delta==32*256)
free=3;assert(#E.CustomerOffers(snapshot,{row},{})==2)
legal={};assert(#E.CustomerOffers(snapshot,{row},{})==0)
legal={5,6};assert(#E.CustomerOffers(snapshot,{row},{[5]=true,[6]=true})==0)
''')

    def test_cross_quarter_proposals_do_not_promote_conflicting_customer_types(self):
        vm = self.adapters()
        vm.execute('''
local E=CSC_AI_EconomyAdapters
GameInfo={Districts={[10]={RequiresPopulation=1},[11]={RequiresPopulation=1},
 [20]={RequiresPopulation=1,Hash=200},[21]={RequiresPopulation=1,Hash=210}}}
local snapshot={id=1,cities={[1]={object={}}},DistrictCapacity=function()return{known=true,used=0,allowed=6}end,
 ui={GetLegalDistrictTargets=function()return{5}end}}
local rows={
 {economy=true,city=1,district=10,plot=2,finalQ8=100,customerLayout={{city=1,district=20,plot=5,preference=32}}},
 {economy=true,city=1,district=11,plot=3,finalQ8=200,customerLayout={{city=1,district=21,plot=5,preference=48}}}}
local offers=E.CustomerOffers(snapshot,rows,{})
assert(#offers==1 and offers[1].district==21)
snapshot.planState={plans={retained={plot=5}}}
assert(#E.CustomerOffers(snapshot,rows,{})==0)
''')

    def facts(self):
        vm = boundaries.Boundaries().facts_vm()
        vm.execute('''
local function p(i)
 return{GetIndex=function()return i end,GetOwner=function()return 1 end,
 GetX=function()return i end,GetY=function()return 0 end,
 GetResourceType=function()return i==5 and 99 or -1 end,GetDistrictType=function()return -1 end,
 CanHaveDistrict=function(_,d)return d==20 and i<=4 or d==21 and i>=2 end}
end
plots={};for i=1,5 do plots[i]=p(i)end
city={GetID=function()return 7 end,GetX=function()return 0 end,GetY=function()return 0 end}
Map={GetPlot=function()return plots[1]end,GetAdjacentPlots=function()return{plots[2],plots[3],plots[5]}end}
Cities={GetPlotPurchaseCity=function()return city end}
PlayersVisibility={[1]={IsRevealed=function()return true end}}
CSC_Adjacency={PlotsInBand=function()return{plots[1],plots[2],plots[3],plots[4],plots[5]}end}
Game={GetCurrentGameTurn=function()return 100 end}
CSC_AI_FutureDistrictTypes=function()return{[20]=true,[21]=true}end
CSC_AI_SitingDistricts=function()return{buildable={
 {Index=20,DistrictType='DISTRICT_COMMERCIAL_HUB'},
 {Index=21,DistrictType='DISTRICT_HOLY_SITE'}}}end
local values={[1]=4,[2]=2,[3]=3,[4]=4,[5]=10}
reads=0;lag=0
ui={GetDistrictAdjacency=function(_,_,plot,district)
 reads=reads+1
 return{available=true,turn=100-lag,yields={
 YIELD_GOLD=district==20 and values[plot]or 0,
 YIELD_FAITH=district==21 and values[plot]or 0,YIELD_CSC_AI_PLACEMENT=999}}
end}
profile={key='BAKERS'}
''')
        return vm

    def test_real_quarter_publisher_combines_spatial_parts_and_separate_customer_offer(self):
        vm = boundaries.Boundaries().bid_vm()
        vm.execute('''
GameInfo.Districts={[36]={RequiresPopulation=1},[20]={RequiresPopulation=1,Hash=200}}
snapshot.CustomerOptions=function()return{{player=1,city=7,district=20,family='HUB',plot=4,
 adjacency=2,bestAdjacency=2,displacedAdjacency=0}}end
snapshot.ui.GetLegalDistrictTargets=function()return{4}end
snapshot.DistrictCapacity=function()return{known=true,used=0,allowed=3,population=7,reason='ready'}end
local entries,stats=CSC_AI_EconomyAdapters.QuarterBids(snapshot,placement,{},early)
assert(#entries==4 and stats.final==3)
for i=1,3 do local row=entries[i]
 assert(row.finalQ8==row.plot*1000+(288+32)*256)
 assert(row.adjacency==4 and row.economicQ8==row.plot*1000)
 assert(row.layoutPreferenceQ8==32*256 and row.customerLayout[1].plot==4)
end
assert(entries[4].customer and entries[4].plot==4 and entries[4].delta==32*256)
''')

    def test_frontier_gold_payback_uses_only_starting_gold_after_completion(self):
        vm = boundaries.Boundaries().bid_vm()
        vm.execute('''
snapshot.Site=function(_,p)return{value=p:GetIndex()*1000,baseCount=1,
 startingAdjacency=3,startingGold=2,quarterReady=12}end
local entries=CSC_AI_EconomyAdapters.QuarterBids(snapshot,placement,{},early)
assert(entries[1].startingGoldPaybackTurns==nil)
assert(entries[2].purchaseGold==50 and entries[2].startingGoldPaybackTurns==25)
assert(entries[3].purchaseGold==40 and entries[3].startingGoldPaybackTurns==20)
assert(entries[2].startingAdjacency==3 and entries[2].quarterReadyEstimate==12)
snapshot.Site=function(_,p)return{value=p:GetIndex()*1000,baseCount=1,startingGold=0}end
entries=CSC_AI_EconomyAdapters.QuarterBids(snapshot,placement,{},early)
assert(entries[2].startingGoldPaybackTurns==nil)
''')

    def test_native_customer_facts_use_loaded_yields_cache_and_keep_resource_tiles_free(self):
        vm = self.facts()
        vm.execute('''
local snapshot=CSC_AI_EconomyFacts.New(player,placement,ui)
local options=snapshot.CustomerOptions(city,plots[1],profile,{[3]=true})
assert(#options==2)
for _,o in ipairs(options)do
 assert(o.plot==2 and o.adjacency==2 and o.bestAdjacency==4)
 assert(o.plot~=5 and o.plot~=3)
 if o.district==20 then assert(o.displacedAdjacency==4)end
end
local previous=reads
snapshot.CustomerOptions(city,plots[1],profile,{[3]=true})
assert(reads==previous and snapshot.SpatialStats().maps==2)
''')

    def test_known_core_ui_phase_lag_is_accepted_and_counted(self):
        vm = self.facts()
        vm.execute('''
lag=1
local snapshot=CSC_AI_EconomyFacts.New(player,placement,ui)
assert(#snapshot.CustomerOptions(city,plots[1],profile,{})>0)
assert(snapshot.SpatialStats().laggedReads==snapshot.SpatialStats().adjacencyReads)
''')

    def test_stale_or_missing_native_adjacency_creates_no_customer_bonus(self):
        vm = self.facts()
        vm.execute('''
lag=2
local snapshot=CSC_AI_EconomyFacts.New(player,placement,ui)
assert(#snapshot.CustomerOptions(city,plots[1],profile,{})==0)
assert(snapshot.SpatialStats().unavailable>0)
ui.GetDistrictAdjacency=nil
assert(#CSC_AI_EconomyFacts.New(player,placement,ui).CustomerOptions(city,plots[1],profile,{})==0)
''')

    def test_customer_potential_does_not_reuse_a_retained_native_quarter_footprint(self):
        vm=self.facts()
        vm.execute('''
local snapshot=CSC_AI_EconomyFacts.New(player,placement,ui)
snapshot.intentFootprints={[2]=true}
local options=snapshot.CustomerOptions(city,plots[1],profile,{})
assert(#options>0)
for _,option in ipairs(options)do assert(option.plot~=2)end
''')


if __name__ == '__main__':
    unittest.main()
