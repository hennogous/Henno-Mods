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

    def test_prospective_pair_shares_one_loss_allowance_across_both_sites(self):
        self.vm().execute('''
local E=CSC_AI_EconomyAdapters
E.ProspectiveConnectionsEnabled=true
local candidate=quarterAt(20)
candidate.site.city=7;candidate.site.key='Q';candidate.site.quarterReady=6
candidate.entry.strongLayout={plot=9,city=7,stage=2,existing=true}
candidate.entry.prospectiveLayout={plot=21,city=7,district=1,stage=3,adjacency=2}
snapshot.connectionQuarters={candidate};snapshot.cities={[7]={object={}}}
snapshot.ProspectiveCustomerReady=function()return 3 end
snapshot.CustomerNetValue=function()return -1 end
snapshot.ProjectedConnectionYields=function()return {YIELD_GOLD=1}end
CSC_AI_EconomyModel.CustomerBuildingForecast=function(_,venues,_,ready)
    assert(#venues==1 and ready==3)
    return {valueQ8=180*256,with={quarterReadyByChain={Q=9}}}
end
snapshot.Price=function(stream)
    assert(stream.ready==9)
    return 20*256
end
local plans=E.ProspectiveConnectionPlans(snapshot,{})
assert(#plans==2 and plans[1].costQ8==50*256 and plans[2].costQ8==50*256)
assert(plans[1].best.plot==20 and plans[2].best.plot==21)
-- Same geometry as the two Panama layouts. A role swap cannot preserve a
-- pair if the winner occupies either of the two shared plots.
local alternate=quarterAt(21)
alternate.entry.finalQ8=198*256
alternate.entry.strongLayout={plot=20,city=7,district=1,stage=3,adjacency=2}
snapshot.connectionQuarters={candidate,alternate}
plans=E.ProspectiveConnectionPlans(snapshot,{})
assert(#plans==2 and plans[1].best.plot==20 and plans[2].best.plot==21)
alternate.entry.plot=22
plans=E.ProspectiveConnectionPlans(snapshot,{})
assert(#plans==1 and plans[1].best.plot==20)
snapshot.connectionQuarters={candidate}
plans=E.ProspectiveConnectionPlans(snapshot,{})
CE_AIDistrictScoresEarlyCost=function()end
local anchoredQuarter={player=1,city=7,district=3,plot=20,finalQ8=200*256,connectionPressureQ8=36*256}
local rows=E.ApplyConnectionCosts(snapshot,{anchoredQuarter},plans,{[3]=true})
assert(#rows>1 and rows[1]==anchoredQuarter)
for i=2,#rows do
    local row=rows[i]
    assert(row.earlyCostQ8==50*256 and row.connectionOrder=='prospective')
    assert(not (row.plot==20 and row.district==3) and not (row.plot==21 and row.district==1))
end
candidate.site.prospectiveCustomers={{plot=22,city=7,district=1,adjacency=2,
    bestAdjacency=2,displacedAdjacency=0,stages={[3]=true}}}
plans=E.ProspectiveConnectionPlans(snapshot,{})
assert(#plans==1 and plans[1].best.plot==20 and plans[1].costQ8==64*256)
assert(#E.ProspectiveConnectionPlans(snapshot,{[21]=true})==0)
candidate.site.prospectiveCustomers={}
candidate.entry.capacityState='ready'
snapshot.CustomerNetValue=function()return 256 end
local credits
plans,credits=E.ProspectiveConnectionPlans(snapshot,{})
assert(#plans==2 and #credits==2)
assert(plans[1].costQ8==25*256 and credits[1].valueQ8==25*256 and credits[1].quarter==true)
assert(plans[2].costQ8==25*256 and credits[2].valueQ8==25*256 and credits[2].quarter==false)
candidate.entry.economy=true;candidate.entry.player=1
local adjusted=E.ApplyProspectiveConnectionCredit(snapshot,{candidate.entry,
    {player=1,city=7,district=1,plot=21,delta=10*256,customer=true}},credits)
assert(adjusted[1].finalQ8==225*256 and adjusted[2].delta==35*256)
GameInfo.Districts[1].RequiresPopulation=true
GameInfo.Districts[3].RequiresPopulation=true
local allowed=1
snapshot.DistrictCapacity=function()return {known=true,allowed=allowed,used=0}end
plans,credits=E.ProspectiveConnectionPlans(snapshot,{})
assert(plans[1].costQ8==25*256 and credits[1].valueQ8==25*256)
allowed=2
plans,credits=E.ProspectiveConnectionPlans(snapshot,{})
assert(#plans==2 and #credits==2)
for i=1,2 do assert(plans[i].costQ8==32*256 and credits[i].valueQ8==32*256)end
allowed=1
snapshot.cities[8]={object={}}
candidate.entry.prospectiveLayout.city=8
plans,credits=E.ProspectiveConnectionPlans(snapshot,{})
assert(#plans==2 and #credits==2 and credits[2].city==8)
for i=1,2 do assert(plans[i].costQ8==32*256 and credits[i].valueQ8==32*256)end
candidate.entry.prospectiveLayout.city=7
candidate.site.quarterWork={unlock=0,turns=6}
snapshot.ProspectiveCustomerReady=function()return 14,10,4 end
CSC_AI_EconomyModel.CustomerBuildingForecast=function(_,_,_,ready,_,first)
    assert(first==6 and ready==14) -- build the Quarter while waiting for research
    return {valueQ8=180*256,with={quarterReadyByChain={Q=first}}}
end
snapshot.Price=function(stream)assert(stream.ready==14);return 20*256 end
assert(#E.ProspectiveConnectionPlans(snapshot,{})==2)
snapshot.ProspectiveCustomerReady=function()return 50 end
assert(#E.ProspectiveConnectionPlans(snapshot,{})==0)
''')

    def test_two_saved_quarters_choose_a_stable_customer_hint(self):
        vm = self.vm()
        vm.execute((AI/'CSC_AI_PlanContinuity.lua').read_text(encoding='utf-8'))
        vm.execute((AI/'CSC_AI_EconomyAdapters.lua').read_text(encoding='utf-8'))
        vm.execute('''
local E,C=CSC_AI_EconomyAdapters,CSC_AI_PlanContinuity
E.ProspectiveConnectionsEnabled=true
local supply={base={{plot=37}},specialty={}}
local function record(city,fresh)
    return C.LayoutRecord({city=city,district=3,plot=10+city},
        {city=5,district=1,plot=20+city,stage=2},supply,nil,nil,nil,fresh)
end
PlayersVisibility={}
Cities={GetPlotPurchaseCity=function(plot)return {GetID=function()return plot.city end}end}
Map.GetPlotByIndex=function(index)
    local founded=index<20
    return {city=founded and index-10 or 5,GetOwner=function()return 1 end,
        GetDistrictType=function()return founded and 3 or -1 end}
end
local placement={StageTwoProfiles=function()return {{key='TEST',district={Index=3}}}end}
local function loadPlans(a,b)
    turn=turn+1
    local encoded=C.EncodeLayouts({a,b})
    Game.GetProperty=function(_,k)if k=='CSC_AI_PlannedLayoutsV1_1' then return encoded end end
    local s={id=1,cities={[5]={},[6]={},[7]={}},districts={[16]={city=6,type=3},[17]={city=7,type=3}},
        Supply=function()return supply end,player={GetCities=function()return {Members=function()return ipairs({})end}end}}
    E.QuarterBids(s,placement,{},{})
    return s.partnerHints['5:1']
end
assert(loadPlans(record(6,19),record(7,20))==27)
assert(loadPlans(record(7,20),record(6,20))==26)
assert(loadPlans(record(6,20),record(7,20))==26)
''')

    def test_provider_foundation_hands_off_both_directions_without_a_buyer(self):
        vm=self.vm()
        vm.execute((AI/'CSC_AI_PlanContinuity.lua').read_text(encoding='utf-8'))
        vm.execute((AI/'CSC_AI_EconomyAdapters.lua').read_text(encoding='utf-8'))
        vm.execute('''
local E,C=CSC_AI_EconomyAdapters,CSC_AI_PlanContinuity
E.ProspectiveConnectionsEnabled=true
local p=C.LayoutRecord({city=7,district=3,plot=10},{city=7,district=1,plot=20,stage=0},
    {base={{plot=37},{plot=35}},specialty={{plot=36}}},12,21,nil,19)
local encoded=C.EncodeLayouts({['7:3']=p})
local saved=C.ReadLayouts(encoded,20)['7:3']
assert(saved.first==19 and saved.base[1]==35 and saved.specialty[1]==36 and saved.alternatePartner==21)
assert(next(C.ReadLayouts(encoded,60))==nil)
snapshot.IsGoodsProvider=function(_,district)return district==1 end
snapshot.ProjectedCustomers=function()return {}end
snapshot.ProjectedConnectionYields=function()return {YIELD_GOLD=1}end
snapshot.ExistingConnectionYields=function()return {YIELD_GOLD=1}end
snapshot.Price=function()return 30*256 end
snapshot.Supply=function()return {base={{plot=37}},specialty={}}end
snapshot.handoffs={['quarterFirst:10:0:TEST']={record=saved,plot=20,phase=1}}
snapshot.nextLayouts={}
local plans=E.AnchoredConnectionPlans(snapshot,{})
assert(#plans==1 and plans[1].best.plot==20 and plans[1].best.valueQ8==30*256)
local retained=C.ReadLayouts(C.EncodeLayouts(snapshot.nextLayouts),21)['7:3']
assert(retained.phase==1 and retained.first==19 and retained.base[1]==37 and #retained.specialty==0)
local provider={GetIndex=function()return 20 end}
Map.GetAdjacentPlots=function()return {provider}end
Map.GetPlotByIndex=function(i)return {GetX=function()return i end,GetY=function()return 0 end}end
local candidate=quarterAt(10);candidate.profile=chain.profile;candidate.site.customers={}
snapshot.connectionGroups={};snapshot.connectionQuarters={candidate}
snapshot.districts={[20]={working=true,complete=true,city=7,type=1}}
legal={10}
snapshot.handoffs={['customerFirst:20:0:TEST']={record=saved,plot=10,phase=2}}
plans=E.AnchoredConnectionPlans(snapshot,{})
assert(#plans==1 and plans[1].best.plot==10 and plans[1].best.valueQ8==30*256)
assert(snapshot.nextLayouts['7:3'].phase==2)
snapshot.IsGoodsProvider=function()return false end
assert(#E.AnchoredConnectionPlans(snapshot,{})==0)
''')

    def test_frontier_customer_competes_after_one_invoice_and_both_yield_gains(self):
        self.vm().execute('''
local E=CSC_AI_EconomyAdapters
E.ProspectiveConnectionsEnabled=true
local candidate=quarterAt(20)
candidate.entry.capacityState='ready';candidate.site.city=7;candidate.site.key='Q';candidate.site.quarterReady=3
candidate.entry.player=snapshot.id;candidate.entry.economy=true
local partner={plot=21,city=7,district=1,stage=3,adjacency=2,purchaseGold=40,customerYields={YIELD_FAITH=1}}
candidate.entry.prospectiveLayout=partner
snapshot.connectionQuarters={candidate};snapshot.cities={[7]={object={}}}
GameInfo.Districts[1].RequiresPopulation=true;GameInfo.Districts[3].RequiresPopulation=true
snapshot.DistrictCapacity=function()return{known=true,used=0,allowed=2}end
legal={20} -- the customer tile cannot appear in the owned BUILD list
snapshot.ProspectiveCustomerReady=function()return 5,0,5 end
snapshot.ProjectedConnectionYields=function()return {YIELD_GOLD=1}end
CSC_AI_EconomyModel.CustomerBuildingForecast=function()return{valueQ8=40*256,with={quarterReadyByChain={Q=3}}}end
snapshot.Price=function(flow)
    if flow.fixed then return flow.amount*256 end
    assert(flow.ready==5 and flow.amount==1)
    return 20*256
end
local costs,credits=E.ProspectiveConnectionPlans(snapshot,{})
assert(#credits==2)
-- 40 transaction +20 Quarter +20 customer -40 land =40. Two sites
-- split that budget and each assigns half to its own positive offer.
for _,credit in ipairs(credits)do assert(credit.valueQ8==10*256)end
local rows=E.ApplyProspectiveConnectionCredit(snapshot,{candidate.entry},credits)
assert(rows[2].plot==21 and rows[2].customerPurchaseGold==40 and rows[2].delta==10*256)
local prior={plot=20,partnerCity=7,partnerDistrict=1,partnerPlot=21}
for _,invoice in ipairs({80,81})do
    snapshot.savedLayouts={['7:3']=prior};partner.purchaseGold=invoice
    assert(#E.ProspectiveConnectionPlans(snapshot,{})==0)
    assert(not snapshot.savedLayouts['7:3'],'nonpositive pair survived on a positive Quarter bid')
end
snapshot.savedLayouts={['7:3']=prior}
snapshot.Price=function()return nil end
assert(#E.ProspectiveConnectionPlans(snapshot,{})==0)
assert(snapshot.savedLayouts['7:3']==prior,'unavailable quote retired the pair')
''')

    def test_fifth_saved_layout_is_a_carry_candidate_after_four_fresh_quotes(self):
        self.vm().execute('''
local E=CSC_AI_EconomyAdapters
E.ProspectiveConnectionsEnabled=true
snapshot.connectionQuarters={};snapshot.cities={};snapshot.savedLayouts={}
snapshot.nextLayouts={};snapshot.shortlistedLayouts={}
snapshot.ProjectedConnectionYields=function()return {}end
snapshot.ProspectiveCustomerReady=function()return 5,0,5 end
CSC_AI_EconomyModel.CustomerBuildingForecast=function()return {valueQ8=256,with={quarterReadyByChain={}}}end
for i=1,5 do
    local q=quarterAt(10+i)
    q.site.city=i;q.site.key='Q';q.site.quarterReady=1;q.site.suppliers={}
    q.entry.city=i;q.entry.prospectiveLayout={plot=20+i,city=i,district=1,stage=3}
    snapshot.cities[i]={object={}}
    snapshot.connectionQuarters[i]=q
    snapshot.savedLayouts[i..':3']={plot=10+i,partnerPlot=20+i,partnerDistrict=1,partnerCity=i}
end
E.ProspectiveConnectionPlans(snapshot,{})
local missed=0
for key in pairs(snapshot.shortlistedLayouts) do
    missed=missed+1
    assert(not snapshot.nextLayouts[key],'unquoted layout took priority over fresh site claims')
end
assert(missed==1)
''')

    def test_customer_substitute_requires_a_comparable_rank_after_price_and_delay(self):
        self.vm().execute('''
local E=CSC_AI_EconomyAdapters
E.ProspectiveConnectionsEnabled=true
local candidate=quarterAt(20)
local site=candidate.site
site.city=7;site.key='Q';site.quarterReady=4
site.suppliers={{kind='base',plot=30,ready=0},{kind='base',plot=31,ready=0}}
site.customers={}
snapshot.connectionQuarters={candidate}
snapshot.cities={[7]={object={}}}
snapshot.ProspectiveCustomerReady=function()return 3 end
snapshot.ProjectedConnectionYields=function()return {}end
CSC_AI_EconomyModel.CustomerBuildingForecast=function()return {valueQ8=80*256,with={quarterReadyByChain={Q=4}}}end
local options={}
for _,index in ipairs({21,22,23}) do
    options[#options+1]={city=7,district=1,plot=index,adjacency=2,bestAdjacency=2,
        displacedAdjacency=0,stages={[3]=true}}
end
-- All three have identical ordinary adjacency. The shortlist has already
-- priced their different invoices and completion dates. Only its strongest
-- feasible alternative should release our bid on plot 21.
local ranks={[21]=100,[22]=20}
local function check(costExpected,alternate)
    local _,layout=E.StrongQuarterLayout(site,options,{},true,function(option)return ranks[option.plot],1 end)
    assert(layout.plot==21 and layout.alternatePartnerPlot==alternate)
    candidate.entry.prospectiveLayout=layout
    local plans=E.ProspectiveConnectionPlans(snapshot,{})
    local found=false
    for _,p in ipairs(plans)do if p.best.plot==21 and p.costQ8>0 then found=true end end
    assert(found==costExpected)
end
check(true,nil)
ranks[23]=92;check(false,23)
ranks[22]=92;check(false,22)
options[2],options[3]=options[3],options[2];check(false,22)
''')

    def test_supplier_protection_preserves_bids_shares_cost_and_releases(self):
        self.vm().execute('''
local E=CSC_AI_EconomyAdapters
E.ProspectiveConnectionsEnabled=true
local candidate=quarterAt(20)
candidate.entry.capacityState='ready'
candidate.site.city=7;candidate.site.key='Q';candidate.site.quarterReady=3
local partner={plot=21,city=7,district=1,stage=2,adjacency=2,hasSpec=true}
candidate.entry.prospectiveLayout=partner
local supply={{plot=30,kind='base',ready=0},{plot=31,kind='specialty',ready=5}}
candidate.site.suppliers=supply
snapshot.connectionQuarters={candidate};snapshot.cities={[7]={object={}},[8]={object={}}}
GameInfo.Districts[1].RequiresPopulation=true;GameInfo.Districts[3].RequiresPopulation=true
snapshot.DistrictCapacity=function()return{known=true,used=0,allowed=2}end
snapshot.ProspectiveCustomerReady=function()return 5,0,5 end
snapshot.ProjectedConnectionYields=function()return {}end
CSC_AI_EconomyModel.CustomerBuildingForecast=function()return{valueQ8=96*256,with={quarterReadyByChain={Q=3}}}end
Map.GetPlotByIndex=function(i)return {GetOwner=function()return 1 end,GetDistrictType=function()return -1 end,
    CanHaveDistrict=function()return true end}end
Cities={GetPlotPurchaseCity=function()return {GetOwner=function()return 1 end,GetID=function()return 8 end}end}
local function costs()
    local plans,credits=E.ProspectiveConnectionPlans(snapshot,{})
    local cost,total={},0
    for _,p in ipairs(plans) do cost[p.best.plot]=p.costQ8;total=total+p.costQ8 end
    for _,offer in ipairs(credits) do assert(offer.valueQ8==24*256);total=total+offer.valueQ8 end
    assert(total==96*256)
    return cost,plans
end
local cost,plans=costs()
assert(cost[30]==16*256 and not cost[31])
CE_AIDistrictScoresEarlyCost=function()end
local rows=E.ApplyConnectionCosts(snapshot,{},plans,{[3]=true})
for _,row in ipairs(rows) do
    if row.plot==30 then assert(row.city==8 and row.connectionOrder=='plannedSupply') end
end
stage=4;partner.stage=4
cost=costs();assert(cost[30]==12*256 and cost[31]==12*256)
supply[3]={plot=32,kind='base',ready=1}
cost=costs();assert(not cost[30] and not cost[32] and cost[31]==16*256)
stage=2;partner.stage=2
cost=costs();assert(not cost[31] and cost[20]==24*256 and cost[21]==24*256)
''')

    def test_customer_purchase_and_rival_cost_share_the_same_anchored_allowance(self):
        self.vm().execute('''
local E=CSC_AI_EconomyAdapters
main.purchaseGold=32
snapshot.planCustomerPurchases=true
snapshot.cities={[7]={object={}}}
snapshot.DistrictCapacity=function()return {known=true,allowed=2,used=1}end
snapshot.Price=function(stream)
    assert(stream.fixed and stream.yield=='YIELD_GOLD' and stream.amount==-32)
    return -32*256
end
local plan=E.AnchoredConnectionPlans(snapshot,{})[1]
assert(plan.best.valueQ8==32*256)
local allowance=E.ConnectionLossQ8(plan.best.valueQ8,0)
assert(plan.purchaseCreditQ8>0 and plan.costQ8>0)
assert(plan.costQ8+plan.purchaseCreditQ8==allowance)
''')

    def test_early_customer_land_compares_waiting_owned_sites_at_the_same_start(self):
        self.vm().execute('''
local E=CSC_AI_EconomyAdapters
main.purchaseGold=32
backup.waiting=true
snapshot.connectionGroups[1].candidates={main,backup}
snapshot.planCustomerPurchases=true
snapshot.cities={[7]={object={}}}
snapshot.customerOwnedReferences={['7:1']={plot=22,links=0}}
local capacity={known=true,allowed=1,used=1,nextSlotTurns=4}
snapshot.DistrictCapacity=function()return capacity end
local prices={[20]=200*256,[21]=140*256,[22]=120*256}
local seen={}
snapshot.CustomerNetValue=function(_,_,plot,ready)
    assert(ready==7)
    seen[plot]=true
    return prices[plot]
end
CSC_AI_EconomyModel.CustomerBuildingForecast=function(_,venues,_,ready)
    assert(ready==7 or venues[1].plot==21 and ready==3)
    return {valueQ8=(venues[1].plot==20 and 96 or 64)*256}
end
snapshot.ProjectedConnectionYields=function()return {YIELD_PRODUCTION=1}end
snapshot.Price=function(stream)
    if stream.fixed then
        assert(stream.yield=='YIELD_GOLD' and stream.amount==-32 and stream.ready==0)
        return -32*256
    end
    assert(stream.ready==4 or stream.ready==0)
    return 8*256
end
local plan=E.AnchoredConnectionPlans(snapshot,{})[1]
assert(seen[20] and seen[21] and seen[22])
assert(plan.best.plot==20 and plan.backup.plot==21 and plan.purchaseCreditQ8>0)
assert(plan.best.wait==4 and plan.costQ8+plan.purchaseCreditQ8<=E.ConnectionCompletionCapQ8)
prices[22]=330*256
plan=E.AnchoredConnectionPlans(snapshot,{})[1]
assert(plan.best.plot==21 and not plan.purchaseCreditQ8)
prices[22]=nil
plan=E.AnchoredConnectionPlans(snapshot,{})[1]
assert(plan.best.plot==21 and not plan.purchaseCreditQ8)
capacity.nextSlotTurns=11;seen={}
assert(E.AnchoredConnectionPlans(snapshot,{})[1].best.plot==21 and not next(seen))
capacity.nextSlotTurns=4;capacity.known=false
assert(E.AnchoredConnectionPlans(snapshot,{})[1].best.plot==21 and not next(seen))
''')

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

    def test_standing_partner_gets_one_repeat_visit_and_other_sites_keep_rotating(self):
        self.vm().execute('''
local E=CSC_AI_EconomyAdapters
snapshot.connectionGroups={}
snapshot.Supply=function()return nil end
for i=1,6 do
    local anchor,plot=100+i,200+i
    local standing={ready=true,economy=economy,profile=chain.profile,plot={GetIndex=function()return anchor end}}
    values[plot]=64*256
    snapshot.connectionGroups[i]={city=7,district=1,candidates={{plot=plot,adjacency=2,chains={standing}}}}
end
snapshot.handoffs={['quarterFirst:101:3:TEST']={record={phase=1},plot=201,phase=1}}
local others={}
for now=20,30 do
    turn=now
    local plans=E.AnchoredConnectionPlans(snapshot,{})
    assert(#plans==2)
    local supported=false
    for _,p in ipairs(plans)do
        if p.anchor==101 then supported=true else others[p.anchor]=true end
    end
    assert(supported,'ready saved partner missed this publication')
end
for i=102,106 do assert(others[i]) end
-- With no available slot this target releases the priority visit.
snapshot.connectionGroups[1].candidates[1].waiting=true
local otherOnly=false
for now=31,36 do
    turn=now
    local p=E.AnchoredConnectionPlans(snapshot,{})
    if p[1].anchor~=101 and p[2].anchor~=101 then otherOnly=true end
end
assert(otherOnly)
''')

    def test_founded_customer_keeps_its_buyable_quarter_until_ordinary_build_admission(self):
        self.vm().execute('''
local E=CSC_AI_EconomyAdapters
local candidate=quarterAt(20)
local entry=candidate.entry
snapshot.connectionGroups={};snapshot.connectionQuarters={candidate}
entry.frontier=true;entry.purchaseGold=65;entry.capacityState='ready';entry.economy=true
entry.qualityCapQ8=200*256;entry.qualityCapAdjustmentQ8=-20*256
candidate.site.quarterWork={unlock=0};legal={}
assert(#E.AnchoredConnectionPlans(snapshot,{})==0)
E.ProspectiveConnectionsEnabled=true
local plans=E.AnchoredConnectionPlans(snapshot,{})
assert(#plans==1 and plans[1].order=='customerFirst' and plans[1].best.plot==20)
assert(not plans[1].purchaseCreditQ8)
E.ApplyQuarterConnectionCredit(snapshot,{entry},plans)
assert(entry.finalQ8==220*256)
candidate.site.quarterWork.unlock=3
assert(#E.AnchoredConnectionPlans(snapshot,{})==0)
candidate.site.quarterWork.unlock=0;entry.capacityState='stale'
assert(#E.AnchoredConnectionPlans(snapshot,{})==0)
entry.capacityState='ready';entry.purchaseGold=nil
assert(#E.AnchoredConnectionPlans(snapshot,{})==0)
entry.purchaseGold=65;entry.plot=22
assert(#E.AnchoredConnectionPlans(snapshot,{})==0)
entry.plot=20
entry.frontier=false;legal={20}
assert(E.AnchoredConnectionPlans(snapshot,{})[1].best.plot==20)
assert(#E.AnchoredConnectionPlans(snapshot,{[20]=true})==0)
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

    def test_paid_customer_beyond_the_geometry_shortlist_can_earn_a_bounded_offer(self):
        self.vm().execute('''
local E=CSC_AI_EconomyAdapters
local paid={plot=22,adjacency=1,chains={chain},purchaseGold=20}
snapshot.connectionGroups[1].candidates={main,backup,paid}
snapshot.planCustomerPurchases=true
snapshot.cities={[7]={object={}}}
local free,known=1,true
GameInfo.Districts[1].RequiresPopulation=true
snapshot.DistrictCapacity=function()return{known=known,used=2,allowed=2+free}end
snapshot.Price=function(flow)
 assert(flow.fixed and flow.yield=='YIELD_GOLD')
 return flow.amount*256
end
local native={[20]=100*256,[21]=90*256,[22]=80*256,[24]=80*256}
snapshot.CustomerNetValue=function(_,_,plot)return native[plot] end
values[20],values[21],values[22]=5*256,8*256,40*256
local function plan()return E.AnchoredConnectionPlans(snapshot,{})[1]end
local chosen=plan()
-- The owned site is 100 + 5. The paid site is 80 (invoice already in
-- native NetValue) + 40. CSC's credit is one quarter of the 15 margin.
assert(chosen.best.plot==22 and chosen.backup.plot==20)
assert(chosen.purchaseCreditQ8==960 and chosen.costQ8==960)
free=0;chosen=plan();assert(chosen.best.plot~=22 and not chosen.purchaseCreditQ8)
free=1;known=false;assert(plan().best.plot~=22)
known=true;native[20]=nil;assert(plan().best.plot~=22)
native[20]=100*256
snapshot.customerOwnedReferences={['7:1']={plot=24,links=0}}
native[24]=140*256
assert(plan().best.plot~=22,'unlinked owned reference beats the combined paid bid')
snapshot.customerOwnedReferences=nil
values[20],values[21],native[22]=40*256,40*256,140*256
assert(plan().best.plot~=22,'native advantage alone earns no CSC purchase credit')
values[20],values[21],native[22]=5*256,8*256,80*256
native[23],values[23]=85*256,40*256
snapshot.connectionGroups[1].candidates[4]={plot=23,adjacency=0,chains={chain},purchaseGold=20}
chosen=plan()
assert(chosen.best.plot==23 and chosen.backup.plot==22 and chosen.purchaseCreditQ8==5*256 and chosen.costQ8==0)
''')

    def test_paid_proposal_cannot_displace_a_live_handoff_in_saved_layouts(self):
        vm=self.vm()
        vm.execute((AI/'CSC_AI_PlanContinuity.lua').read_text(encoding='utf-8'))
        vm.execute((AI/'CSC_AI_EconomyAdapters.lua').read_text(encoding='utf-8'))
        vm.execute('''
local E,C=CSC_AI_EconomyAdapters,CSC_AI_PlanContinuity
local quarter={city=7,district=3,plot=10}
local supply={base={{plot=37}},specialty={}}
local old=C.LayoutRecord(quarter,{city=7,district=1,plot=20,stage=2},supply,nil,nil,nil,19)
old.phase=1
chain.city={GetID=function()return 7 end};chain.profile.district={Index=3}
local owned={city=7,district=1,candidates={main}}
local paid={city=7,district=2,candidates={{plot=22,chains={chain},adjacency=2,purchaseGold=20}}}
snapshot.connectionGroups={owned,paid};snapshot.planCustomerPurchases=true
snapshot.cities={[7]={object={}}}
GameInfo.Districts[2].RequiresPopulation=false
snapshot.ProjectedCustomers=function(_,_,district,plot)
    local row=venue(plot);row.stage=district==1 and 2 or 4;return {row}
end
snapshot.ProjectedConnectionYields=function(_,_,plot)return {YIELD_GOLD=plot==22 and 60 or 0}end
snapshot.Price=function(flow)return flow.amount*256 end
snapshot.Supply=function()return supply end
snapshot.handoffs={['quarterFirst:10:2:TEST']={record=old,plot=20,phase=1}}
local function publish()
    snapshot.nextLayouts={}
    local plans=E.AnchoredConnectionPlans(snapshot,{})
    local paidCredit
    for _,plan in ipairs(plans)do if plan.stage==4 then paidCredit=plan.purchaseCreditQ8 end end
    assert(paidCredit==10*256)
    return C.ReadLayouts(C.EncodeLayouts(snapshot.nextLayouts),turn+1)['7:3']
end
local held=publish()
assert(held.stage==2 and held.partnerPlot==20 and held.first==19)
supply.specialty={{plot=38}}
snapshot.connectionGroups={paid,owned};turn=turn+1
held=publish()
assert(held.stage==2 and held.partnerPlot==20 and held.first==19)
snapshot.handoffs={};turn=turn+1
local acquired=publish()
assert(acquired.stage==4 and acquired.partnerPlot==22 and acquired.invoice==20)
supply.specialty={{plot=37},{plot=22}};turn=turn+1
assert(not publish(),'a dual-tag without a second unclaimed deposit cannot back Stage 4 memory')
''')

    def test_ready_handoff_does_not_monopolise_customer_land_appraisal(self):
        self.vm().execute('''
local E=CSC_AI_EconomyAdapters
local nextChain={ready=true,economy=economy,profile=chain.profile,plot={GetIndex=function()return 11 end}}
local paidA={plot=22,adjacency=1,chains={chain},purchaseGold=20}
local paidB={plot=24,adjacency=1,chains={nextChain},purchaseGold=20}
local ownedB={plot=23,adjacency=2,chains={nextChain}}
snapshot.connectionGroups={{city=7,district=1,candidates={main,paidA,ownedB,paidB}}}
snapshot.planCustomerPurchases=true;snapshot.cities={[7]={object={}}}
GameInfo.Districts[1].RequiresPopulation=false
snapshot.Price=function(flow)return flow.amount*256 end
values[20],values[22],values[23],values[24]=30*256,10*256,5*256,50*256
local quoted={}
snapshot.CustomerNetValue=function(_,_,plot)quoted[plot]=true;return 120*256 end
snapshot.handoffs={['quarterFirst:10:3:TEST']={record={phase=1},plot=20,phase=1}}
snapshot.Supply=function()return nil end
local otherVisits=0
for t=20,23 do
    turn=t;quoted={}
    local plans=E.AnchoredConnectionPlans(snapshot,{})
    assert(#plans==2 and plans[1].anchor==10 and plans[1].best.plot==20)
    assert(not (quoted[22] and quoted[24]))
    if quoted[24] then
        assert(plans[2].best.plot==24 and plans[2].purchaseCreditQ8>0)
        otherVisits=otherVisits+1
    end
end
assert(otherVisits==2)
''')

    def test_customer_first_prefers_the_stronger_complete_bid_over_an_older_equal_link(self):
        self.vm().execute('''
local E=CSC_AI_EconomyAdapters
local earlier,new=quarterAt(20),quarterAt(21)
earlier.entry.finalQ8=100*256
snapshot.connectionGroups={};snapshot.connectionQuarters={earlier}
assert(E.AnchoredConnectionPlans(snapshot,{})[1].best.plot==20)
turn=21;snapshot.connectionQuarters={earlier,new}
local plan=E.AnchoredConnectionPlans(snapshot,{})[1]
assert(plan.best.plot==21 and plan.backup.plot==20)
assert(plan.competitiveBackupQ8==0 and plan.costQ8==32*256)
values[21]=40*256
assert(E.AnchoredConnectionPlans(snapshot,{})[1].best.plot==21)
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

    def test_full_capacity_can_retain_its_footprint_until_native_admission(self):
        self.vm().execute('''
local E=CSC_AI_EconomyAdapters
snapshot.connectionGroups={};snapshot.connectionQuarters={quarterAt(20)}
local entry=snapshot.connectionQuarters[1].entry
entry.capacityState='full';legal={}
local plans=E.AnchoredConnectionPlans(snapshot,{})
assert(#plans==1 and plans[1].best.option.waiting)
entry.capacityState='stale';assert(#E.AnchoredConnectionPlans(snapshot,{})==0)
entry.capacityState='full';snapshot.auditConnections=true;snapshot.auditConnectionsOnly=true
local messages={};print=function(s)messages[#messages+1]=s end
E.AnchoredConnectionPlans(snapshot,{})
assert(#messages==1 and messages[1]:find('CSC_AI_CONNECTION_CAPACITY_WAIT',1,true))
legal={20};entry.capacityState='ready';turn=21
E.AnchoredConnectionPlans(snapshot,{})
assert(#messages==2 and messages[2]:find('CSC_AI_CONNECTION_OPPORTUNITY',1,true))
''')

    def test_quarter_first_waiting_site_never_enters_the_ordinary_bid_list(self):
        self.vm().execute('''
local E=CSC_AI_EconomyAdapters
local group=snapshot.connectionGroups[1]
group.candidates[1].waiting=true
snapshot.captureConnections=true
snapshot.CustomerCandidateSets=function()return {},{group}end
snapshot.WorldQuote=function()error('Waiting site entered the ordinary auction')end
local offers,_,plans=E.CustomerEconomicOffers(snapshot,{})
assert(#offers==0 and #plans==1 and plans[1].order=='quarterFirst' and plans[1].best.option.waiting)
-- A destination that can build now leads while a fuller neighbour retains
-- its higher-valued footprint as a possible future backup.
group.candidates={main,backup};main.adjacency=9;values[20]=100*256;values[21]=48*256
plans=E.AnchoredConnectionPlans(snapshot,{})
assert(#plans==1 and plans[1].best.plot==21 and plans[1].backup.plot==20)
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

    def test_weak_native_backup_does_not_erase_a_competitive_footprint_loss(self):
        self.vm().execute('''
local E=CSC_AI_EconomyAdapters
snapshot.connectionGroups[1].candidates={main,backup}
snapshot.CustomerNetValue=function(city,district,plot)
    return (plot==20 and 1050 or 510)*256
end
local plans=E.AnchoredConnectionPlans(snapshot,{})
assert(#plans==1 and plans[1].best.plot==20 and plans[1].backup.plot==21)
assert(plans[1].backup.valueQ8==64*256 and plans[1].competitiveBackupQ8==0 and plans[1].costQ8==32*256)
snapshot.CustomerNetValue=function(_,_,plot)if plot==20 then return 1050*256 end end
plans=E.AnchoredConnectionPlans(snapshot,{})
assert(plans[1].competitiveBackupQ8==64*256 and plans[1].costQ8==0)

snapshot.connectionGroups={};snapshot.connectionQuarters={quarterAt(20),quarterAt(21)}
snapshot.connectionQuarters[1].entry.finalQ8=1050*256
snapshot.connectionQuarters[2].entry.finalQ8=510*256
plans=E.AnchoredConnectionPlans(snapshot,{})
assert(#plans==1 and plans[1].best.plot==20 and plans[1].backup.plot==21)
assert(plans[1].competitiveBackupQ8==0 and plans[1].costQ8==32*256)
-- The first full bid leads solely because of the local transaction.
-- Preserve the backup's real link and charge only half the 16-utility loss.
snapshot.connectionQuarters[1].entry.finalQ8=164*256
snapshot.connectionQuarters[2].entry.finalQ8=148*256
values[21]=48*256
plans=E.AnchoredConnectionPlans(snapshot,{})
assert(plans[1].competitiveBackupQ8==48*256 and plans[1].costQ8==8*256)
''')

    def test_managed_deduction_keeps_fresh_basis_and_skips_carried_score(self):
        self.vm().execute('''
local E=CSC_AI_EconomyAdapters
local plans=E.AnchoredConnectionPlans(snapshot,{})
local row={player=1,city=7,district=3,plot=20,delta=0,finalQ8=100*256,ordinaryBidQ8=100*256}
E.ApplyConnectionCosts(snapshot,{row},plans,{[3]=true})
assert(row.finalQ8==68*256 and row.ordinaryBidQ8==100*256)
row.finalQ8=100*256;row.carried=true
E.ApplyConnectionCosts(snapshot,{row},plans,{[3]=true})
assert(row.finalQ8==100*256)
''')

    def test_displacement_quotes_only_available_competitors_with_a_remaining_cost(self):
        self.vm().execute('''
local E=CSC_AI_EconomyAdapters
local plans=E.AnchoredConnectionPlans(snapshot,{})
local city={};snapshot.cities={[7]={object=city}}
snapshot.FutureDistrictTypes=function(object)
    assert(object==city)
    return {[1]=true,[2]=true}
end
local quotes=0
snapshot.CustomerNetValue=function(cityID,district,plot)
    assert(cityID==7 and district==2 and plot==20)
    quotes=quotes+1
    return 120*256
end
local rows=E.ApplyConnectionCosts(snapshot,{},plans,{[3]=true})
assert(#rows==1 and rows[1].district==2 and rows[1].delta==-32*256 and quotes==1)
local completion={player=1,city=7,district=1,plot=20,delta=32*256,connectionPressureQ8=32*256}
rows=E.ApplyConnectionCosts(snapshot,{completion},plans,{[3]=true})
assert(#rows==1 and rows[1]==completion and quotes==1)
''')

    def test_native_cost_keeps_the_regular_delta_and_needs_no_site_quote(self):
        vm = self.vm()
        vm.execute((AI / 'CSC_AI_DistrictBridge.lua').read_text(encoding='utf-8'))
        vm.execute('''
local E=CSC_AI_EconomyAdapters
local function okay()return 1 end
CE_AIDistrictScoresBegin=okay;CE_AIDistrictScoresAllow=okay;CE_AIDistrictScoresCommit=okay
CE_AIDistrictScoresDisable=okay;CE_AIDistrictScoresStatus=okay
CE_AIDistrictScoresEntry=function()error('Ordinary entry would lose the separate cost')end
local packet={}
CE_AIDistrictScoresEarlyCost=function(...)packet[#packet+1]={...};return 1 end
local plans=E.AnchoredConnectionPlans(snapshot,{})
snapshot.CustomerNetValue=function()error('Displacement must use the live native value')end
snapshot.ConnectionDistrictTurns=function()error('Displacement requires no queue quote')end
local regular={player=1,city=7,district=2,plot=20,delta=300}
local rows=E.ApplyConnectionCosts(snapshot,{regular},plans,{[3]=true})
assert(#rows==2 and regular.delta==300 and regular.earlyCostQ8==32*256)
assert(CSC_AI_DistrictBridge.Publish(1,10,10,5,{1},rows))
assert(#packet==2 and packet[1][5]==300 and packet[1][6]==32*256)
assert(packet[2][5]==0 and packet[2][6]==32*256)
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
-- Even near the positive limit, the reference's 64-utility credit reaches
-- both scores. The 240-point standalone difference stays intact.
values[20]=64*256
snapshot.CustomerNetValue=function()return 1000*256 end
local relative=240
snapshot.CustomerWorld=function(_,_,plot)
 return {},{value=(plot==20 and 400 or 400+relative)*256,customer={ready=3}}
end
local function deltas()
 local byPlot={}
 for _,entry in ipairs(E.CustomerEconomicOffers(snapshot,{}))do byPlot[entry.plot]=entry.delta end
 return byPlot
end
local positive=deltas()
assert(positive[20]==64*256 and positive[19]-positive[20]==240*256)
relative=-300
local negative=deltas()
assert(negative[20]==64*256 and negative[19]-negative[20]==-256*256)
group.candidates={main}
entries=E.CustomerEconomicOffers(snapshot,{})
assert(#entries==1 and entries[1].plot==20 and entries[1].delta==64*256)
''')

    def test_existing_customer_only_recovers_a_measured_quarter_cap_deduction(self):
        self.vm().execute('''
local E=CSC_AI_EconomyAdapters
snapshot.connectionGroups={};snapshot.connectionQuarters={quarterAt(20)}
local plans=E.AnchoredConnectionPlans(snapshot,{})
local entry={city=7,district=3,plot=20,economy=true,finalQ8=100*256,qualityCapQ8=100*256,ordinaryBidQ8=100*256}
E.ApplyQuarterConnectionCredit(snapshot,{entry},plans)
assert(entry.finalQ8==100*256)
entry.qualityCapAdjustmentQ8=-20*256
E.ApplyQuarterConnectionCredit(snapshot,{entry},plans)
assert(entry.finalQ8==120*256 and entry.ordinaryBidQ8==100*256)
''')

    def test_strong_site_measured_relief_scales_with_ordinary_district_value(self):
        self.vm().execute('''
local E=CSC_AI_EconomyAdapters
snapshot.connectionGroups={};snapshot.connectionQuarters={quarterAt(20)}
values[20]=200*256
local plans=E.AnchoredConnectionPlans(snapshot,{})
local function credit(adjacency,reference,removed)
    local startingScore=100*256
    local entry={city=7,district=3,plot=20,economy=true,adjacency=adjacency,finalQ8=startingScore,
        comparisonReferenceQ8=reference*256,qualityCapQ8=startingScore,qualityCapAdjustmentQ8=-removed*256}
    E.ApplyQuarterConnectionCredit(snapshot,{entry},plans)
    return (entry.finalQ8-startingScore)/256
end
assert(credit(2,2000,200)==64)
assert(credit(3,1000,200)==80)
assert(credit(3,2000,200)==128)
assert(credit(3,2000,20)==20)
values[20]=40*256;plans=E.AnchoredConnectionPlans(snapshot,{})
assert(credit(3,2000,200)==40)
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
