"""Real Lua model/adapters with explicit quote doubles, never simulated AI wins.

Verify economic versus bid accounting, quality gates and native context usage.
Live qualification uses the shared controller and real CE quote functions.
"""
from pathlib import Path
import json
import unittest
from lupa.lua51 import LuaRuntime
import test_boundaries as boundaries

AI=Path(__file__).resolve().parents[3]/'Civ Supply Chains/Lua_UI/AI'


class NativeValuation(unittest.TestCase):
    def test_joint_value_keeps_structural_floor_without_repeating_supplier_income_loss(self):
        self.vm().execute('''
local s=site();local q={valueQ8=100000,bidValueQ8=100000,adjacency=3}
local _,_,ordinary=E.PlacementValue(q,s,1024,false)
assert(ordinary.penaltyQ8==1024)
s.jointEconomy=true
local _,_,joint=E.PlacementValue(q,s,1024,false)
assert(joint.penaltyQ8==0)
local _,_,covered=E.PlacementValue(q,s,1024,true)
assert(covered.penaltyQ8==256*256)
''')

    def test_interval_api_is_required_and_short_flows_keep_their_actual_window(self):
        self.vm().execute('''
local raw=snapshot.Price({city=10,yield='YIELD_PRODUCTION',amount=1,ready=0,finish=1},100)
assert(raw==256 and calls[#calls].r==0 and calls[#calls].h==1)
CE_AIYieldIntervalValue=nil
CE_AIYieldStreamValue=function()error('Legacy stream fallback must not be used')end
local available,reason=E.Available()
assert(not available and reason:find('interval',1,true))
''')

    def test_spatial_preference_cannot_consume_a_protected_supplier_plot(self):
        vm=boundaries.Boundaries().bid_vm()
        vm.execute('''
local rows,stats=CSC_AI_EconomyAdapters.QuarterBids(snapshot,placement,{[1]=true},early)
assert(stats.materialDeferred==1 and #rows==2)
for _,r in ipairs(rows)do assert(r.plot~=1)end
''')

    def vm(self):
        vm=LuaRuntime(unpack_returned_tuples=True)
        vm.execute((AI/'CSC_AI_EconomyModel.lua').read_text(encoding='utf-8'))
        vm.execute('''
Game={GetCurrentGameTurn=function()return 30 end}
GameInfo={Yields={YIELD_PRODUCTION={Index=1},YIELD_FOOD={Index=2},YIELD_GOLD={Index=3}}}
CE_AIEconomyStatus=function()return '{"pricingReady":1,"finalReady":1}'end
CE_AIDistrictScoresFinalEntry=function()end
CE_AIDistrictScoresManagedType=function()end
CE_AIDistrictScoresManagedReceipt=function()end
CE_AIDistrictSiteAdjustment=function()return '{"adjustmentQ8":-256,"includesPurchase":1}'end
CE_AIEvaluationContext=function()return '{"ordinaryHorizon":100,"discountQ8":512}'end
calls={}
CE_AIYieldIntervalValue=function(p,c,y,a,r,h,d)
 assert(d==512 and h<=100);calls[#calls+1]={a=a,r=r,h=h,y=y}
 return a*(h-r)
end
CE_AIYieldFixedValue=function(p,c,y,a,r,d)assert(d==512);return a end
CE_AIAmenityIntervalValue=function(p,c,a,r,h,d)assert(d==512);return a*256*(h-r)end
CSC_AI_EconomyFacts={New=function(_,_,_,context)
 assert(context.horizon==100 and context.discountQ8==512 and context.nativeSite)
 return{id=1,cities={[10]={foodSurplus=20,navalProduction=0}}}
end}
function site()
 return{city=10,population=10,horizon=100,quarterReady=2,maintenance=1,
  adjacency=3,baseCount=1,materialYield='YIELD_FOOD',direct={},customers={},
  suppliers={{kind='base',plot=99,city=10,ready=0,worked=true}},
  seconds={{type='Mill',unlock=0,turns=3,forecastDepth=0}},
  third={type='Bakery',unlock=0,turns=2,maintenance=1,forecastDepth=1}}
end
function find(r,id)for _,s in ipairs(r.streams)do if s.id==id then return s end end end
''')
        vm.execute((AI/'CSC_AI_EconomyAdapters.lua').read_text(encoding='utf-8'))
        vm.execute('M=CSC_AI_EconomyModel;E=CSC_AI_EconomyAdapters;snapshot=assert(E.Snapshot({}, {}, {}))')
        return vm

    def test_native_context_prices_effective_income_once_without_changing_economic_amounts(self):
        self.vm().execute('''
local s=site();s.nativeSiteAdjustmentQ8=-256
local quote=M.Forecast(s,snapshot.Price,function(q)return E.PlacementValue(q,s)end)
local flow=find(quote,'local-production:3')
assert(flow.amount==1 and flow.forecastDepth==1)
assert(flow.bidValueQ8==3*flow.valueQ8)
local upkeep=find(quote,'upkeep:10:Bakery')
assert(upkeep.bidValueQ8==upkeep.valueQ8)
local raw,bid=-256,-256
for _,v in ipairs(quote.streams)do raw=raw+v.valueQ8;bid=bid+v.bidValueQ8 end
assert(raw==quote.valueQ8 and bid==quote.bidValueQ8 and bid>raw)
assert(quote.forecastAdjustmentQ8==bid-raw)
local before=#calls
M.Forecast(s,snapshot.Price,function(q)return E.PlacementValue(q,s)end)
assert(#calls==before) -- same-publication cache, including weighted quotes
''')

    def test_quality_and_real_loss_gates_survive_large_forecast_preferences(self):
        self.vm().execute('''
local q={valueQ8=100*256,bidValueQ8=4000*256,adjacency=1}
local s=site()
assert(E.PlacementValue(q,s)==E.DeferredQuarterQ8)
q.adjacency=4;s.baseCount=0
assert(E.PlacementValue(q,s)==E.DeferredQuarterQ8)
s.baseCount=1;q.valueQ8=-256
assert(E.PlacementValue(q,s)==-256)
q.valueQ8=100*256
assert(E.PlacementValue(q,s,101*256)<=0)
''')

    def test_service_requires_supplier_producer_customer_and_civic_and_does_not_stack_recipients(self):
        self.vm().execute('''
local s=site();s.service={kind='GROWTH',amount=10,unlock=20}
s.customers={{stage=2,plot=8,city=10,complete=true,ready=0,working=true},
 {stage=2,plot=9,city=10,complete=true,ready=0,working=true}}
local r=M.Forecast(s,snapshot.Price)
local service=find(r,'service:GROWTH:10')
assert(service.amount==10 and service.ready==20 and service.valueQ8==2*(100-20)*256)
assert(service.bidValueQ8==service.valueQ8)
s.suppliers={};assert(not find(M.Forecast(s,snapshot.Price),'service:GROWTH:10'))
s.suppliers={{kind='base',plot=99,ready=math.huge}}
assert(not find(M.Forecast(s,snapshot.Price),'service:GROWTH:10'))
s.suppliers[1].ready=0;s.service.unlock=100
assert(not find(M.Forecast(s,snapshot.Price),'service:GROWTH:10'))
''')

    def test_dockmaster_uses_observed_naval_work_in_a_bounded_window(self):
        self.vm().execute('''
local s=site();s.service={kind='NAVAL_PRODUCTION_PERCENT',amount=20,unlock=0}
s.customers={{stage=2,plot=8,city=10,complete=true,ready=0,working=true}}
local r=M.Forecast(s,snapshot.Price)
local service=find(r,'service:NAVAL_PRODUCTION_PERCENT:10')
assert(service and service.finish-service.ready==10 and service.valueQ8==0)
snapshot.cities[10].navalProduction=20
-- A fresh snapshot would own the changed facts/quote cache; create one here.
local fresh=assert(E.Snapshot({}, {}, {}));fresh.cities[10].navalProduction=20
service=find(M.Forecast(s,fresh.Price),'service:NAVAL_PRODUCTION_PERCENT:10')
assert(service.valueQ8==4*10*256)
''')

    def test_unprofitable_later_building_stays_optional_with_native_weighting(self):
        self.vm().execute('''
local s=site();local before=M.Forecast(s,snapshot.Price,function(q)return E.PlacementValue(q,s)end)
s.fourth={type='Cafe',unlock=0,turns=2,maintenance=1000,forecastDepth=1}
local after=M.Forecast(s,snapshot.Price,function(q)return E.PlacementValue(q,s)end)
assert(after.valueQ8==before.valueQ8 and after.bidValueQ8==before.bidValueQ8)
''')

    def test_observed_strong_sites_beat_medium_control_districts_and_weak_sites_stay_below(self):
        vm=self.vm()
        fixture=json.loads((Path(__file__).parent/'fixtures/native_calibration_20261115.json').read_text())
        audit=json.loads((AI.parents[2]/'project/docs/research/mods/csc-ai-district-value-audit-20261115.json').read_text())
        medium=[r['choice']['median'] for r in audit['baseline']['strata']
                if r['district'] in ('DISTRICT_CAMPUS','DISTRICT_COMMERCIAL_HUB','DISTRICT_THEATER')
                and r['adjacency']==2 and r['period']=='001-075']
        self.assertEqual(len(medium),3)
        for row in fixture['records']:
            quote=vm.table_from(dict(valueQ8=row['valueQ8'],bidValueQ8=row['bidValueQ8'],adjacency=row['adjacency']))
            site=vm.table_from(dict(baseCount=row['base'],specialtyCount=row['spec'],
                                   comparisonReferenceQ8=600*256,sitingReadiness=1))
            bid,*_=vm.globals().E.PlacementValue(quote,site)
            if row['adjacency']==4:self.assertGreater(bid/256,max(medium))
            else:self.assertLess(bid/256,min(medium))

    def test_quality_caps_and_readiness_do_not_turn_remote_income_into_an_unconditional_bid(self):
        self.vm().execute('''
local s=site();s.comparisonReferenceQ8=600*256;s.sitingReadiness=1
local q={adjacency=2,valueQ8=10000*256,bidValueQ8=10000*256}
local bid,_,parts=E.PlacementValue(q,s)
assert(bid==300*256 and parts.qualityCapQ8==300*256)
assert(bid==q.bidValueQ8+parts.adjacencyQ8+parts.materialsQ8+parts.layoutQ8+parts.capAdjustmentQ8)
q.adjacency=4;q.valueQ8=256;q.bidValueQ8=256;s.sitingReadiness=.01
assert(E.PlacementValue(q,s)<10*256)
assert(E.NativeInvestmentReference(76,100)==2*E.NativeInvestmentReference(38,50))
local before=E.NativeInvestmentReference(112,50)
local after=E.NativeInvestmentReference(113,50)
assert(after-before==8*256) -- smooth interpolation, no phase-boundary jump
''')

    def test_population_and_stage_four_transactions_keep_their_producer_attribution(self):
        self.vm().execute('''
local s=site();s.fourth={type='Cafe',unlock=0,turns=2,forecastDepth=1}
s.customers={{stage=3,plot=8,city=10,population=10,rate=.101,complete=true,ready=0,working=true},
 {stage=4,plot=9,city=10,population=10,complete=true,ready=0,working=true}}
local r=M.Forecast(s,snapshot.Price)
assert(find(r,'population:10:YIELD_PRODUCTION:sale-production:7').forecastDepth==1)
assert(find(r,'sale-production:9:4:nil').forecastDepth==1)
''')

    def test_native_frontier_cost_prevents_a_second_purchase_invoice(self):
        self.vm().execute('''
local s=site();s.third=nil;s.nativeSiteAdjustmentQ8=-50*256;s.nativeSiteIncludesPurchase=true
snapshot.Site=function()return s end
local city={GetID=function()return 10 end}
local plot={GetIndex=function()return 1 end,GetOwner=function()return -1 end}
local profile={district={Index=42}}
local r=E.QuotePlacement(snapshot,city,plot,profile,{upper=4},true,50,0,0,false,{})
assert(r.quote and r.site.purchaseGold==0 and r.quote.siteAdjustmentQ8==-50*256)
assert(r.quote.footprintBidQ8==-50*256)
assert(not find(r.quote,'footprint-purchase'))
local total=-50*256
for _,f in ipairs(r.quote.streams)do total=total+f.valueQ8 end
assert(total==r.quote.valueQ8)
''')

    def test_only_a_live_decline_skips_the_actual_quarter_forecast(self):
        self.vm().execute('''
local s=site();snapshot.Site=function()return s end
local city={GetID=function()return 10 end}
local plot={GetIndex=function()return 1 end,GetOwner=function()return 1 end}
local profile={district={Index=42}}
local function evaluate()return E.QuotePlacement(snapshot,city,plot,profile,{upper=4},false,0,0,0,false,{})end
local calls=0;local forecast=E.QuarterForecast
E.QuarterForecast=function(...)calls=calls+1;return forecast(...)end
E.MeasureQuarterPricing=true
E.ShortlistObserver={live=true,site=function()return false end}
assert(evaluate().shortlistDeferred and calls==0 and not snapshot.deepForecastCalls)
E.ShortlistObserver.live=false
assert(evaluate().quote and calls==1)
E.ShortlistObserver={live=true,site=function()error('study fault')end}
assert(evaluate().quote and calls==2 and E.ShortlistObserver==nil and snapshot.deepForecastCalls==2)
''')

    def test_quality_bound_keeps_the_best_terrain_and_preserves_saved_sites(self):
        self.vm().execute('''
local s=site();s.adjacency=1
snapshot.Site=function()return s end
local city={GetID=function()return 10 end}
local plot={GetIndex=function()return 1 end,GetOwner=function()return 1 end}
local profile={district={Index=42}}
local forecasts=0
E.QuarterForecast=function()forecasts=forecasts+1;return nil,'test quote' end
E.ProspectiveConnectionsEnabled=true
local function evaluate()
    return E.QuotePlacement(snapshot,city,plot,profile,{upper=1},false,0,0,0,false,{})
end
assert(evaluate().qualityBoundDeferred and forecasts==0)
s.seconds[2]={type='Second',terrain=.9999995}
assert(not evaluate().qualityBoundDeferred and forecasts==1) -- Within the bid floor's tolerance.
s.seconds[2].terrain=.9
assert(evaluate().qualityBoundDeferred and forecasts==1)
s.pairAdjacencyGain=.1
assert(not evaluate().qualityBoundDeferred and forecasts==2)
s.pairAdjacencyGain=nil;s.seconds[2].terrain=nil
s.quarterKey='TAILORS';s.completedHarborPlot=21
assert(not evaluate().qualityBoundDeferred and forecasts==3)
s.completedHarborPlot=nil
snapshot.savedLayouts={['10:42']={plot=1}}
assert(not evaluate().qualityBoundDeferred and forecasts==4)
snapshot.savedLayouts['10:42'].plot=2
snapshot.intentFootprints={[1]='10:42:1'}
assert(not evaluate().qualityBoundDeferred and forecasts==5)
snapshot.intentFootprints=nil;s.seconds[2].terrain=math.huge
assert(not evaluate().qualityBoundDeferred and forecasts==6)
E.ProspectiveConnectionsEnabled=false;s.seconds[2].terrain=nil
assert(not evaluate().qualityBoundDeferred and forecasts==7)
''')

    def test_missing_readiness_price_cannot_leave_a_partially_valid_site_cache(self):
        self.vm().execute('''
local facts=site()
CSC_AI_EconomyFacts.New=function()return{id=1,cities={},Site=function()return facts end}end
local native=CE_AIYieldIntervalValue
CE_AIYieldIntervalValue=function()return nil end
local fresh=assert(E.Snapshot({}, {}, {}))
assert(fresh.Site()==nil and facts.comparisonReferenceQ8==nil and facts.sitingReadiness==nil)
assert(fresh.Site()==nil and facts.comparisonReferenceQ8==nil)
CE_AIYieldIntervalValue=native
assert(fresh.Site()==facts and facts.comparisonReferenceQ8 and facts.sitingReadiness)
''')


if __name__=='__main__':unittest.main()
