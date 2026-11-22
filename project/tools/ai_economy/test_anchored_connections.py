"""Placement-order, backup and native packet regressions for the prototype."""
from pathlib import Path
import unittest

from lupa.lua51 import LuaRuntime


AI = Path(__file__).resolve().parents[3] / 'Civ Supply Chains/Lua_UI/AI'


class AnchoredConnections(unittest.TestCase):
    def vm(self):
        vm = LuaRuntime()
        vm.execute('''
print=function() end
turn=20
Game={GetCurrentGameTurn=function()return turn end}
GameInfo={}
local definitions={
    {Index=1,Hash=1,DistrictType='DISTRICT_HOLY_SITE'},
    {Index=2,Hash=2,DistrictType='DISTRICT_INDUSTRIAL_ZONE'},
    {Index=3,Hash=3,DistrictType='DISTRICT_CSC_TEST_QUARTER'},
    {Index=4,Hash=4,DistrictType='DISTRICT_LEU_GARDEN'},
}
GameInfo.Districts=setmetatable(definitions,{__call=function()
    local i=0;return function()i=i+1;return definitions[i] end
end})
Map={GetPlotByIndex=function(index)return {CanHaveDistrict=function()return index==20 or index==21 end}end}
values={[20]=64*256,[21]=64*256}
stage=3
CSC_AI_EconomyFacts={}
CSC_AI_EconomyModel={
    CustomerBuildingForecast=function(_,venues)return {valueQ8=values[venues[1].plot]}end,
    ExistingCustomerConnectionValue=function(site)return values[site.plot] end,
}
economy={horizon=50,suppliers={{kind='base',ready=0}}}
chain={ready=true,economy=economy,profile={key='TEST'},plot={GetIndex=function()return 10 end}}
main={plot=20,adjacency=2,chains={chain}}
backup={plot=21,adjacency=2,chains={chain}}
legal={20,21}
function venue(plot)
    return {plot=plot,stage=stage,building='BUILDING_CUSTOMER',transaction={id='defined'},districtType='DISTRICT_LEU_GARDEN'}
end
snapshot={id=1,districts={[9]={working=true}},
    connectionGroups={{city=7,district=1,candidates={main}}},
    ProjectedCustomers=function(_,_,_,plot)return {venue(plot)}end,
    ConnectionDistrictTurns=function()return 3 end,
    CustomerNetValue=function()return 120*256 end,
    ui={GetLegalDistrictTargets=function()return legal end}}
function quarterAt(plot)
    return {quarter='TEST',entry={plot=plot,city=7,district=3,finalQ8=200*256},
        site={plot=plot,horizon=50,suppliers=economy.suppliers,customers={venue(9)}}}
end
''')
        vm.execute((AI / 'CSC_AI_EconomyAdapters.lua').read_text(encoding='utf-8'))
        return vm

    def test_quarter_first_changes_a_near_tie_and_preserves_strong_competition(self):
        self.vm().execute('''
local E=CSC_AI_EconomyAdapters
local plans=E.AnchoredConnectionPlans(snapshot,{})
assert(#plans==1 and plans[1].anchor==10 and plans[1].costQ8==32*256)
local rows=E.ApplyConnectionCosts(snapshot,{},plans,{[3]=true})
local net={}
for _,row in ipairs(rows)do net[row.district]=120*256+row.delta end
assert(net[1]==nil and net[2]==88*256)
assert(net[2]<100*256) -- A merely 20-point advantage is displaced.
local stronger=180*256+rows[1].delta
assert(stronger>100*256) -- A strong ordinary site still wins.
''')

    def test_customer_first_switches_to_the_legal_backup_and_expires(self):
        self.vm().execute('''
local E=CSC_AI_EconomyAdapters
snapshot.connectionGroups={};snapshot.connectionQuarters={quarterAt(20),quarterAt(21)}
local equal=E.AnchoredConnectionPlans(snapshot,{})
assert(#equal==1 and equal[1].costQ8==0) -- keep the plan, with no footprint cost
snapshot.intentFootprints={[20]='7:3:20',[21]=true}
local retained=E.AnchoredConnectionPlans(snapshot,{})
assert(#retained==1 and retained[1].best.plot==20 and not retained[1].backup)
snapshot.intentFootprints={[20]='8:3:20'}
legal={21};turn=21
local plans=E.AnchoredConnectionPlans(snapshot,{})
assert(#plans==1 and plans[1].best.plot==21 and plans[1].order=='customerFirst')
local rows=E.ApplyConnectionCosts(snapshot,{},plans,{[3]=true})
for _,row in ipairs(rows)do assert(row.plot==21 and row.district~=3)end
snapshot.districts[9].working=false;turn=22
assert(#E.AnchoredConnectionPlans(snapshot,{})==0)
''')

    def test_only_the_marginal_cost_over_a_weaker_backup_is_charged(self):
        self.vm().execute('''
local E=CSC_AI_EconomyAdapters
snapshot.connectionGroups[1].candidates={main,backup}
values[21]=48*256
local plans=E.AnchoredConnectionPlans(snapshot,{})
assert(#plans==1 and plans[1].costQ8==8*256 and plans[1].backup.plot==21)
values[21]=nil
local uncertain=E.AnchoredConnectionPlans(snapshot,{})
assert(#uncertain==1 and uncertain[1].costQ8==0)
snapshot.intentFootprints={[20]=true};values[21]=48*256
plans=E.AnchoredConnectionPlans(snapshot,{})
assert(#plans==1 and plans[1].best.plot==21)
''')

    def test_one_slot_prices_a_real_foundation_yield_and_splits_the_loss_budget(self):
        self.vm().execute('''
local E=CSC_AI_EconomyAdapters
GameInfo.Districts[1].RequiresPopulation=true
snapshot.cities={[7]={object={}}};local freeSlots=1
snapshot.DistrictCapacity=function()return {known=true,used=2,allowed=2+freeSlots}end
values[20]=0 -- mapped future building is too far away to pay during the horizon
snapshot.ProjectedConnectionYields=function(_,district,plot)
    assert(district==1 and plot==20);return {YIELD_GOLD=1}
end
snapshot.Price=function(s,horizon)
    assert(s.yield=='YIELD_GOLD' and s.amount==1 and s.ready==0 and horizon==50)
    return 48*256
end
local plans=E.AnchoredConnectionPlans(snapshot,{})
assert(#plans==1 and plans[1].best.valueQ8==48*256 and plans[1].pressureQ8==36*256)
local existing={{player=1,city=7,district=1,plot=20,delta=36*256,connectionPressureQ8=36*256}}
local rows=E.ApplyConnectionCosts(snapshot,existing,plans,{[3]=true})
assert(rows[2].district==2 and rows[2].delta==-12*256)
freeSlots=2
plans=E.AnchoredConnectionPlans(snapshot,{})
assert(plans[1].pressureQ8==nil and plans[1].costQ8==24*256)
''')

    def test_both_placement_orders_can_reprice_from_a_physical_foundation(self):
        self.vm().execute('''
local E=CSC_AI_EconomyAdapters
chain.ready=false;chain.complete=false;economy.quarterReady=4
assert(#E.AnchoredConnectionPlans(snapshot,{})==1)
economy.quarterReady=50
assert(#E.AnchoredConnectionPlans(snapshot,{})==0)
chain.complete=true;economy.quarterReady=4 -- a pillaged district is not a new foundation
assert(#E.AnchoredConnectionPlans(snapshot,{})==0)

snapshot.connectionGroups={}
local established=quarterAt(20);established.site.customers={}
snapshot.connectionQuarters={established}
snapshot.districts[9]={working=false,complete=false}
local buyer=venue(9);buyer.anchorReady=3
snapshot.PendingConnectionVenues=function()return{buyer}end
local plans=E.AnchoredConnectionPlans(snapshot,{})
assert(#plans==1 and plans[1].order=='customerFirst' and plans[1].anchor==9)
snapshot.districts[9].complete=true
assert(#E.AnchoredConnectionPlans(snapshot,{})==0)
''')

    def test_stage_four_without_specialty_can_price_immediate_adjacency(self):
        self.vm().execute('''
local E=CSC_AI_EconomyAdapters
stage=4
CSC_AI_EconomyModel.CustomerBuildingForecast=function()error('No supported specialty transaction')end
snapshot.ProjectedConnectionYields=function()return{YIELD_GOLD=1}end
snapshot.Price=function()return 48*256 end
local plans=E.AnchoredConnectionPlans(snapshot,{})
assert(#plans==1 and plans[1].best.valueQ8==48*256 and plans[1].stage==4)
''')

    def test_stage_four_requires_specialty_and_a_real_mapped_partner(self):
        self.vm().execute('''
local E=CSC_AI_EconomyAdapters
stage=4;snapshot.connectionGroups[1].district=4
assert(#E.AnchoredConnectionPlans(snapshot,{})==0)
economy.suppliers[2]={kind='specialty',ready=5}
assert(#E.AnchoredConnectionPlans(snapshot,{})==1)
assert(#E.AnchoredConnectionPlans(snapshot,{[20]=true})==0)
economy.suppliers[2].plot=20
assert(#E.AnchoredConnectionPlans(snapshot,{})==0) -- the venue would consume its supplier
''')

    def test_one_cost_for_shared_plot_and_native_early_cell_floor(self):
        self.vm().execute('''
local E=CSC_AI_EconomyAdapters
snapshot.connectionQuarters={quarterAt(20)}
local plans=E.AnchoredConnectionPlans(snapshot,{})
assert(#plans==2)
snapshot.CustomerNetValue=function()return 10 end
local entries={{player=1,city=7,district=2,plot=20,delta=-3}}
local rows=E.ApplyConnectionCosts(snapshot,entries,plans,{[3]=true})
assert(rows[1].delta==-9 and rows[1].connectionCostQ8==6)
for _,row in ipairs(rows)do assert(row.district~=1 and row.district~=3)end
''')

    def test_managed_deduction_keeps_fresh_basis_and_skips_carried_score(self):
        self.vm().execute('''
local E=CSC_AI_EconomyAdapters
local plans=E.AnchoredConnectionPlans(snapshot,{})
local row={player=1,city=7,district=3,plot=20,delta=0,finalQ8=100*256}
E.ApplyConnectionCosts(snapshot,{row},plans,{[3]=true})
assert(row.finalQ8==68*256 and row.beforeConnectionQ8==100*256)
row.finalQ8=100*256;row.carried=true
E.ApplyConnectionCosts(snapshot,{row},plans,{[3]=true})
assert(row.finalQ8==100*256)
''')

    def test_quote_budget_and_three_legal_sites_leave_ordinary_choice_open(self):
        self.vm().execute('''
local E=CSC_AI_EconomyAdapters
local priceCount=0
CSC_AI_EconomyModel.CustomerBuildingForecast=function()
    priceCount=priceCount+1;return {valueQ8=64*256}
end
snapshot.connectionGroups[1].candidates={main,backup,{plot=22,adjacency=1,chains={chain}}}
local redundant=E.AnchoredConnectionPlans(snapshot,{})
assert(#redundant==1 and redundant[1].costQ8==0 and priceCount==2)
snapshot.connectionGroups={}
for i=1,12 do
    local distinct={ready=true,economy=economy,profile={key='TEST'},plot={GetIndex=function()return i end}}
    snapshot.connectionGroups[i]={city=7,district=1,candidates={{plot=20,adjacency=2,chains={distinct}}}}
end
assert(#E.AnchoredConnectionPlans(snapshot,{})==2 and priceCount==4)
''')

    def test_preferred_identity_survives_an_unpriced_visit(self):
        self.vm().execute('''
local E=CSC_AI_EconomyAdapters
values[21]=70*256
snapshot.connectionGroups[1].candidates={main,backup}
assert(E.AnchoredConnectionPlans(snapshot,{})[1].best.plot==21)
for i=7,8 do
    local distinct={ready=true,economy=economy,profile={key='TEST'},plot={GetIndex=function()return i end}}
    snapshot.connectionGroups[#snapshot.connectionGroups+1]={city=7,district=1,
        candidates={{plot=20,adjacency=2,chains={distinct}}}}
end
turn=21 -- Only anchors 7 and 8 are visited; 10 remains legal.
for _,plan in ipairs(E.AnchoredConnectionPlans(snapshot,{}))do assert(plan.anchor~=10)end
turn=22;values[21]=values[20]
for _,plan in ipairs(E.AnchoredConnectionPlans(snapshot,{}))do
    if plan.anchor==10 then assert(plan.best.plot==21);return end
end
error('Expected the previously deferred plan to receive a quote')
''')

    def test_linked_reference_shifts_type_value_without_doubling_site_difference(self):
        self.vm().execute('''
local E=CSC_AI_EconomyAdapters
snapshot.captureConnections=true
values[20]=32*256
local group={city=7,district=1,reference=main,candidates={main,{plot=19,adjacency=1,links=0}}}
main.links=1
snapshot.CustomerCandidateSets=function()return {group}end
snapshot.CustomerWorld=function(_,_,plot)return {},{value=plot==20 and 64*256 or 32*256,customer={ready=3}}end
snapshot.WorldQuote=function(world)return {valueQ8=world.value}end
local entries=E.CustomerEconomicOffers(snapshot,{})
assert(#entries==1 and entries[1].plot==20 and entries[1].delta==32*256)
group.candidates={main}
entries=E.CustomerEconomicOffers(snapshot,{})
assert(#entries==1 and entries[1].plot==20 and entries[1].delta==32*256)
''')

    def test_existing_customer_only_recovers_a_measured_quarter_cap_deduction(self):
        self.vm().execute('''
local E=CSC_AI_EconomyAdapters
snapshot.connectionGroups={};snapshot.connectionQuarters={quarterAt(20)}
local plans=E.AnchoredConnectionPlans(snapshot,{})
local entry={city=7,district=3,plot=20,economy=true,finalQ8=100*256,qualityCapQ8=100*256}
E.ApplyQuarterConnectionCredit(snapshot,{entry},plans)
assert(entry.finalQ8==100*256)
entry.qualityCapAdjustmentQ8=-20*256
E.ApplyQuarterConnectionCredit(snapshot,{entry},plans)
assert(entry.finalQ8==120*256 and entry.beforeConnectionQ8==100*256)
''')

    def test_campaign_observation_reports_both_orders_without_a_control_quote(self):
        self.vm().execute('''
local E=CSC_AI_EconomyAdapters
local messages={};print=function(msg)messages[#messages+1]=msg end
snapshot.connectionQuarters={quarterAt(21)}
snapshot.auditConnections=true;snapshot.auditConnectionsOnly=true
CSC_AI_EconomyModel.CustomerBuildingForecast=function()error('audit priced a forecast')end
CSC_AI_EconomyModel.ExistingCustomerConnectionValue=function()error('audit priced a forecast')end
assert(#E.AnchoredConnectionPlans(snapshot,{})==0 and #messages==2)
assert(messages[1]:find('identity=customerFirst:9:3:TEST:7:3:21',1,true))
assert(messages[2]:find('identity=quarterFirst:10:3:TEST:7:1:20',1,true))
assert(#E.AnchoredConnectionPlans(snapshot,{})==0 and #messages==2)
''')
