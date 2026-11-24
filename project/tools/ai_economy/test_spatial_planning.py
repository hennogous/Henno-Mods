"""Exercise spatial choices and the actual main-mod publication boundaries."""
from pathlib import Path
import itertools
import random
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

    def test_strong_layout_supports_two_base_or_distinct_specialty_and_a_real_customer(self):
        self.adapters().execute('''
local E=CSC_AI_EconomyAdapters
local base={kind='base',plot=10,ready=0}
local other={kind='base',plot=11,ready=5}
local specialty={kind='specialty',plot=12,ready=5}
local site={suppliers={base,other},horizon=50}
local harbor={city=2,district=7,plot=21,adjacency=2,bestAdjacency=2,displacedAdjacency=1,stages={[2]=true}}
local theater={city=2,district=8,plot=22,adjacency=3,bestAdjacency=3,displacedAdjacency=2,stages={[4]=true}}
local rural={city=2,district=9,plot=23,adjacency=4,bestAdjacency=4,displacedAdjacency=1,stages={}}
assert(E.StrongQuarterLayout(site,{theater,harbor,rural},{}).plot==21)
assert(E.StrongQuarterLayout(site,{theater},{})==nil)
assert(E.StrongQuarterLayout(site,{theater,harbor,rural},{[11]=true})==nil)
site.suppliers={base,specialty}
assert(E.StrongQuarterLayout(site,{theater,harbor,rural},{}).plot==22)
site.customers={{city=1,plot=13,stage=2,transaction={spatial='ADJACENT_OWNED'}}}
local primary,prospect=E.StrongQuarterLayout(site,{theater,harbor,rural},{})
assert(primary.existing and primary.plot==13)
assert(not prospect.existing and prospect.plot==22 and prospect.stage==4)
site.customers={}
theater.bestAdjacency=4
assert(E.StrongQuarterLayout(site,{theater,harbor,rural},{}).plot==21)
specialty.plot=10 -- two tags on one plot cannot provide redundant supply
assert(E.StrongQuarterLayout(site,{theater,harbor,rural},{})==nil)
''')

    def test_strong_layout_keeps_spatial_terms_after_the_forecast_cap(self):
        self.adapters().execute('''
local E=CSC_AI_EconomyAdapters
local quote={adjacency=2,valueQ8=900*256}
local site={baseCount=2,comparisonReferenceQ8=600*256}
local ordinary,_,before=E.PlacementValue(quote,site)
site.strongLayout={plot=21,stage=2}
local guided,_,after=E.PlacementValue(quote,site)
assert(ordinary==300*256 and after.qualityCapQ8==before.qualityCapQ8)
assert(guided==ordinary+(48+24+72)*256)
assert(after.strongLayoutQ8==72*256 and after.capAdjustmentQ8==-(900-300)*256)
assert(after.ordinaryBidQ8==ordinary)
-- The same validated host survives even when the native score ceiling
-- leaves exactly zero room for the separate layout credit.
quote.adjacency=4;quote.valueQ8=9000*256
site.comparisonReferenceQ8=2100*256
local capped,_,ceiling=E.PlacementValue(quote,site)
assert(capped==4096*256 and ceiling.strongLayoutQ8==0 and ceiling.strongLayout==site.strongLayout)
-- Forecast headroom is preserved. An uncapped layout earns each component
-- once, and an independently priced Service enters the result once.
quote.adjacency=2;site.comparisonReferenceQ8=600*256
quote.valueQ8=204*256;quote.serviceValueQ8=4*256
local uncapped,_,parts=E.PlacementValue(quote,site)
assert(uncapped==(200+48+24+72+4)*256 and parts.capAdjustmentQ8==0)
quote.adjacency=1
assert(E.PlacementValue(quote,site)==E.DeferredQuarterQ8)
quote.adjacency=3;quote.valueQ8=-1
assert(E.PlacementValue(quote,site)==-1)
''')

    def test_exact_footprint_charges_survive_the_forecast_cap(self):
        self.adapters().execute('''
local E=CSC_AI_EconomyAdapters
local site={baseCount=2,comparisonReferenceQ8=600*256,strongLayout={plot=21,stage=2}}
local clean=E.PlacementValue({adjacency=2,valueQ8=900*256},site)
local paid={adjacency=2,valueQ8=800*256,footprintBidQ8=-100*256}
assert(E.PlacementValue(paid,site)==clean-100*256)
assert(E.PlacementValue(paid,site,0,true)==clean-(100+256)*256)
site.strongLayout=nil
assert(E.PlacementValue(paid,site)==200*256)
''')

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

    def test_customer_first_offers_spend_current_slots_and_combine_distinct_supplier_types(self):
        vm = self.adapters()
        vm.execute('''
Game={GetCurrentGameTurn=function()return 5 end}
local E=CSC_AI_EconomyAdapters
GameInfo={Districts={[20]={RequiresPopulation=1},[21]={RequiresPopulation=0}}}
local free=1
local options={
 {city=1,district=20,plot=5,quarterCity=1,quarterDistrict=10,quarterPlot=2,
  baseCount=3,specialtyCount=1,basePlots={7,8,9},specialtyPlots={10},adjacency=2,bestAdjacency=2},
 {city=1,district=20,plot=5,quarterCity=1,quarterDistrict=11,quarterPlot=3,
  baseCount=1,specialtyCount=0,basePlots={7},specialtyPlots={},adjacency=2,bestAdjacency=2}}
local snapshot={id=1,cities={[1]={object={}}},
 DistrictCapacity=function()return{known=true,used=0,allowed=free}end,
 CustomerFirstOptions=function()return options end}
local offers=E.CustomerOffers(snapshot,{},{});
assert(#offers==1 and offers[1].delta==24*256 and #offers[1].futureSuppliers==2)
local paired={economy=true,city=1,district=10,plot=2,finalQ8=100,
 strongLayout={city=1,district=20,plot=5,stage=4}}
local coordinated=E.CustomerOffers(snapshot,{paired},{})
assert(coordinated[1].delta==32*256 and coordinated[1].futureSuppliers[1].option.strongLayout)
paired.strongLayout.plot=6
assert(E.CustomerOffers(snapshot,{paired},{})[1].delta==24*256)
free=0;assert(#E.CustomerOffers(snapshot,{},{})==0)
GameInfo.Districts[20].RequiresPopulation=0
assert(#E.CustomerOffers(snapshot,{},{})==1)
assert(#E.CustomerOffers(snapshot,{}, {[5]=true})==0)
local row={economy=true,city=1,district=10,plot=5,finalQ8=100}
assert(#E.CustomerOffers(snapshot,{row},{})==0)
snapshot.planState={plans={retained={plot=5,district=10}}}
assert(#E.CustomerOffers(snapshot,{},{})==0)
''')

    def test_customer_first_rejects_weaker_ordinary_adjacency_and_missing_material(self):
        vm=self.adapters()
        vm.execute('''
local E=CSC_AI_EconomyAdapters
assert(E.CustomerFirstPreference({baseCount=1,specialtyCount=0,adjacency=2,bestAdjacency=2})==8)
assert(E.CustomerFirstPreference({baseCount=1,specialtyCount=1,adjacency=2,bestAdjacency=2})==12)
assert(E.CustomerFirstPreference({baseCount=30,specialtyCount=30,adjacency=2,bestAdjacency=2})==16)
assert(E.CustomerFirstPreference({baseCount=30,specialtyCount=30,adjacency=2,bestAdjacency=3})==0)
assert(E.CustomerFirstPreference({baseCount=0,specialtyCount=3,adjacency=4,bestAdjacency=4})==0)
assert(E.CustomerFirstPreference({baseCount=1,specialtyCount=0,adjacency=0/0,bestAdjacency=2})==0)
''')

    def test_customer_first_coordinated_nominations_keep_the_quarter_tile_free(self):
        vm=self.adapters()
        vm.execute('''
Game={GetCurrentGameTurn=function()return 5 end}
local E=CSC_AI_EconomyAdapters
GameInfo={Districts={[20]={RequiresPopulation=1},[21]={RequiresPopulation=1}}}
local function option(kind,plot,qplot,base)
 return{city=1,district=kind,plot=plot,quarterCity=1,quarterDistrict=10,quarterPlot=qplot,
 baseCount=base,specialtyCount=0,basePlots={8},specialtyPlots={},adjacency=2,bestAdjacency=2}
end
local options={option(20,5,2,3),option(21,2,3,1)}
local snapshot={id=1,cities={[1]={object={}}},
 DistrictCapacity=function()return{known=true,used=0,allowed=3}end,
 CustomerFirstOptions=function()return options end}
local offers=E.CustomerOffers(snapshot,{},{})
assert(#offers==1 and offers[1].plot==5 and offers[1].futureSuppliers[1].option.quarterPlot==2)
options={option(20,5,2,3),option(21,6,2,1)}
assert(#E.CustomerOffers(snapshot,{},{})==2) -- two customers may share one future Quarter
options={option(20,5,2,3),option(21,6,5,1)}
assert(#E.CustomerOffers(snapshot,{},{})==1) -- future Q cannot cover the first customer
''')

    def test_supplier_city_and_quarter_type_deduplicate_but_shared_materials_can_stack(self):
        vm=self.adapters()
        vm.execute('''
local E=CSC_AI_EconomyAdapters
local function option(city,kind,plot,base,spec)
 return{city=7,district=20,plot=50,quarterCity=city,quarterDistrict=kind,quarterPlot=plot,
 baseCount=base,specialtyCount=spec,basePlots={90},specialtyPlots={91},adjacency=3,bestAdjacency=3}
end
local rows={option(1,10,2,3,1),option(1,10,3,1,1),option(1,11,2,3,1)}
local plan=E.CustomerFirstPlan(rows,{},{})
assert(plan.rawPreference==28 and #plan.links==2) -- A uses3, leaving2 for B
assert(plan.links[1].option.quarterPlot==3 and plan.links[2].option.quarterPlot==2)
rows[#rows+1]=option(2,10,4,1,0) -- same Quarter type, different supplier city
plan=E.CustomerFirstPlan(rows,{},{})
assert(plan.rawPreference==36 and plan.preference==32 and #plan.links==3)
-- All three chains can refer to the SAME actual material plots90/91.
for _,link in ipairs(plan.links)do assert(link.option.basePlots[1]==90)end
rows={option(1,10,2,3,1),option(1,10,3,3,1)}
plan=E.CustomerFirstPlan(rows,{},{})
assert(plan.preference==16 and #plan.links==1) -- alternative sites do not multiply a city/type
rows={option(1,10,2,3,1),option(1,11,2,3,1)}
plan=E.CustomerFirstPlan(rows,{},{})
assert(plan.preference==16 and #plan.links==1) -- one footprint cannot host two Quarters
''')

    def test_supplier_matching_agrees_with_exhaustive_small_layouts(self):
        vm=self.adapters()
        choose=vm.globals().CSC_AI_EconomyAdapters.CustomerFirstPlan
        rng=random.Random(20261116)
        for _ in range(40):
            rows,groups=[],[]
            for group in range(4):
                choices=[]
                for plot in range(4):
                    if rng.random()<.5:
                        strong=rng.choice((False,True));value=16 if strong else 8
                        choices.append((plot,value))
                        rows.append(dict(quarterCity=group//2+1,quarterDistrict=group%2+10,
                            quarterPlot=plot,baseCount=3 if strong else 1,specialtyCount=1 if strong else 0,
                            adjacency=2,bestAdjacency=2))
                groups.append([None]+choices)
            oracle=0
            for combination in itertools.product(*groups):
                selected=[c for c in combination if c is not None]
                if len({c[0]for c in selected})==len(selected):
                    oracle=max(oracle,sum(c[1]for c in selected))
            plan=choose(vm.table_from([vm.table_from(r)for r in rows]),vm.table(),vm.table())
            self.assertEqual(plan.rawPreference,oracle)
            self.assertEqual(plan.preference,min(32,oracle))

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
GameInfo.Districts={
 [20]={Index=20,DistrictType='DISTRICT_COMMERCIAL_HUB'},
 [21]={Index=21,DistrictType='DISTRICT_HOLY_SITE'}}
CSC_AI_SitingDistricts=function()return{buildable={GameInfo.Districts[20],GameInfo.Districts[21]}}end
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
snapshot.CustomerFirstOptions=function()return{{city=7,district=20,plot=4,
 quarterCity=7,quarterDistrict=36,quarterPlot=3,baseCount=1,specialtyCount=0,
 basePlots={5},specialtyPlots={},adjacency=2,bestAdjacency=2}}end
Game={GetCurrentGameTurn=function()return 5 end}
snapshot.DistrictCapacity=function()return{known=true,used=0,allowed=3,population=7,reason='ready'}end
local entries,stats=CSC_AI_EconomyAdapters.QuarterBids(snapshot,placement,{},early)
assert(#entries==4 and stats.final==3)
for i=1,3 do local row=entries[i]
 assert(row.finalQ8==row.plot*1000+(288+32)*256)
 assert(row.adjacency==4 and row.economicQ8==row.plot*1000)
 assert(row.layoutPreferenceQ8==32*256 and row.customerLayout[1].plot==4)
end
assert(entries[4].customer and entries[4].plot==4 and entries[4].delta==8*256)
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
local rings,assignments=0,0
local ring,buyer=Map.GetAdjacentPlots,Cities.GetPlotPurchaseCity
Map.GetAdjacentPlots=function(...) rings=rings+1;return ring(...) end
Cities.GetPlotPurchaseCity=function(p) assignments=assignments+1;return buyer(p) end
local options=snapshot.CustomerOptions(city,plots[1],profile,{[3]=true})
assert(#options==2)
for _,o in ipairs(options)do
 assert(o.plot==2 and o.adjacency==2 and o.bestAdjacency==4)
 assert(o.plot~=5 and o.plot~=3)
 if o.district==20 then assert(o.displacedAdjacency==4)end
end
local previous=reads
assert(rings==1 and assignments==5,('rings=%d assignments=%d'):format(rings,assignments))
snapshot.CustomerOptions(city,plots[1],profile,{[3]=true})
assert(reads==previous and snapshot.SpatialStats().maps==2 and assignments==5)
CSC_AI_EconomyFacts.New(player,placement,ui).CustomerOptions(city,plots[1],profile,{[3]=true})
assert(assignments==10)
''')

    def test_customer_frontier_quote_is_required_and_shared_between_districts(self):
        vm=self.facts()
        vm.execute('''
plots[2].GetOwner=function()return -1 end
Map.GetPlotDistance=function()return 2 end
local invoice,calls=40,0
ui.GetPlotPurchaseQuote=function(player,city,index)
    assert(player==1 and city==7 and index==2);calls=calls+1;return invoice
end
local function check(enabled,expected)
    local snapshot=CSC_AI_EconomyFacts.New(player,placement,ui)
    local found=0
    for _,o in ipairs(snapshot.CustomerOptions(city,plots[1],profile,{},false,enabled)) do
        if o.plot==2 then assert(o.purchaseGold==40);found=found+1 end
    end
    assert(found==expected)
end
check(false,0);assert(calls==0)
check(true,2);assert(calls==1)
invoice=nil
check(true,0);assert(calls==2)
''')

    def test_customer_projection_uses_native_district_pairs_and_displaced_improvements(self):
        vm=self.facts()
        vm.execute('''
GameInfo.Districts={[20]={DistrictType='HUB'},[5]={DistrictType='CENTER'}}
GameInfo.Improvements={[1]={ImprovementType='FARM'}}
GameInfo.District_Adjacencies=function()return ipairsRules()end
local rules={{DistrictType='HUB',YieldChangeId='districts'},{DistrictType='HUB',YieldChangeId='farms'},
    {DistrictType='HUB',YieldChangeId='private'}}
function ipairsRules() local i=0;return function()i=i+1;return rules[i] end end
GameInfo.Adjacency_YieldChanges={
 districts={OtherDistrictAdjacent=true,TilesRequired=2,YieldType='YIELD_GOLD',YieldChange=1},
 farms={AdjacentImprovement='FARM',TilesRequired=1,YieldType='YIELD_PRODUCTION',YieldChange=1},
 private={AdjacentDistrict='QUARTER',TilesRequired=1,YieldType='YIELD_CSC_AI_PLACEMENT',YieldChange=1}}
profile.district={DistrictType='QUARTER'}
Map.GetPlotByIndex=function(i)return plots[i]end
for i,plot in ipairs(plots)do plot.GetImprovementType=function()return i==2 and 1 or -1 end end
plots[3].GetDistrictType=function()return 5 end
local snapshot=CSC_AI_EconomyFacts.New(player,placement,ui)
local gains=snapshot.CustomerAdjacencyChange(profile,20,1,2)
assert(gains.YIELD_GOLD==1 and gains.YIELD_PRODUCTION==-1 and gains.YIELD_CSC_AI_PLACEMENT==nil)
plots[3].GetDistrictType=function()return -1 end
assert(snapshot.CustomerAdjacencyChange(profile,20,1,2).YIELD_GOLD==nil)
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
