"""Service activation/stacking in the real shared Lua ledger, without game orders."""
from pathlib import Path
import unittest
from lupa.lua51 import LuaRuntime
import test_joint_customer_economy as joint_fixtures
import test_native_valuation as native_fixtures

AI=Path(__file__).resolve().parents[3]/'Civ Supply Chains/Lua_UI/AI'


class ServiceForecasts(unittest.TestCase):
    def vm(self):
        vm=joint_fixtures.JointEconomy().vm()
        vm.execute('''
function supplied(key,city)
 local a=chain(key,city)
 a.suppliers={{kind='base',plot=11,ready=0}}
 a.customers={{type='BUYER',building=5,plot=100,city=3,stage=2,working=true,complete=true}}
 a.services={{id='ROOT/LEAF:100',root='ROOT',leaf='LEAF',producer='MILL',stage=2,
  customer=a.customers[1],city=3,plot=100,kind='PSEUDOYIELD',pseudoYield='PSEUDOYIELD_GPP_ENGINEER',
  amount=1,unlock=0,materials={base=1},known=true}}
 return a
end
function withServices(sites) local w=world(sites);w.includeServices=true;return w end
''')
        return vm

    def test_active_service_cancels_between_identical_worlds(self):
        self.vm().execute('''
local a=supplied('A',1)
local before=assert(M.JointForecast(withServices({a}),price))
local after=assert(M.JointForecast(withServices({a}),price))
assert(before.serviceStreams==1 and before.serviceValueQ8==30*256)
assert(after.valueQ8-before.valueQ8==0 and not before.servicesExcluded)
''')

    def test_exact_last_supplier_loss_removes_service(self):
        self.vm().execute('''
local a=supplied('A',1);local b=supplied('A',1);b.suppliers={}
local before=assert(M.JointForecast(withServices({a}),price))
local after=assert(M.JointForecast(withServices({b}),price))
assert(before.serviceStreams==1 and after.serviceStreams==0)
assert(before.serviceValueQ8-after.serviceValueQ8==30*256)
''')

    def test_material_work_values_only_a_service_that_this_job_can_restore(self):
        self.vm().execute('''
local a=supplied('A',1)
local s=a.services[1]
local function quote(kind,t)return M.MaterialServiceStreams(a,kind,t)end
assert(#quote('base',5)==0) -- Current supplier already operates the Service.
a.suppliers[1].ready=5
local added=quote('base',5)
assert(#added==1 and added[1].ready==5 and added[1].city==3 and added[1].service)
assert(price(added[1],a.horizon)==25*256 and #quote('specialty',5)==0)
s.materials.specialty=1
assert(#quote('base',5)==0) -- A second missing supplier still blocks this job's return.
a.suppliers[2]={kind='specialty',plot=12,ready=0}
assert(#quote('base',5)==1)
s.unlock=4;assert(#quote('base',5)==0);s.unlock=0
s.customer.working=false;assert(#quote('base',5)==0);s.customer.working=true
a.seconds[1].working=false;assert(#quote('base',5)==0);a.seconds[1].working=true
s.finish=5;assert(#quote('base',5)==0)
''')

    def test_material_repair_housing_prices_added_relief_against_actual_city(self):
        self.vm().execute('''
local a=supplied('A',1)
a.suppliers[1].ready=5
a.services[1].kind='HOUSING'
a.services[1].amount=2
local city={active=0,left=0,food=2}
local housing={cities={[3]=city},activeCities={},stop=-4,quarter=0,half=1}
local r=M.MaterialServiceStreams(a,'base',5,housing)
assert(#r==1 and r[1].yield=='YIELD_FOOD' and r[1].amount==1.5 and r[1].ready==5)
city.left=2
assert(#M.MaterialServiceStreams(a,'base',5,housing)==0)
''')

    def test_material_quote_preserves_ordinary_value_when_service_quote_is_unavailable(self):
        vm = self.vm()
        vm.execute((AI/'CSC_AI_EconomyAdapters.lua').read_text(encoding='utf-8'))
        vm.execute('''
local a=supplied('A',1)
a.suppliers[1].ready=5
local E=CSC_AI_EconomyAdapters
local snapshot={Price=price,MaterialJobStreams=function()
    return {{city=1,yield='YIELD_PRODUCTION',amount=2,ready=5}}
end}
local function quote()return E.MaterialJobValue(snapshot,{economy=a},'base',11,1)end
local ordinary,service=quote()
assert(ordinary==50*256 and service==25*256)
snapshot.Price=function(stream,horizon)
    if not stream.service then return price(stream,horizon)end
end
ordinary,service=quote()
assert(ordinary==50*256 and service==0)
''')

    def test_civic_and_supplier_delay_control_service_interval(self):
        self.vm().execute('''
local a=supplied('A',1);a.suppliers[1].ready=8;a.services[1].unlock=20
local r=assert(M.JointForecast(withServices({a}),price))
assert(r.serviceValueQ8==10*256)
a.services[1].unlock=30
assert(M.JointForecast(withServices({a}),price).serviceStreams==0)
''')

    def test_one_research_topic_credits_distinct_ready_chains_once(self):
        vm = self.vm()
        vm.execute((AI/'CSC_AI_EconomyAdapters.lua').read_text(encoding='utf-8'))
        vm.execute('''
local a=supplied('A',1);local b=supplied('B',2)
for _,site in ipairs({a,b})do
    site.services[1].unlock=5
    site.services[1].researchTopic={kind='civic',index=6}
end
local bids={['civic:6']={player=1,kind='civic',index=6,value=300,jobs={[9]=true}}}
local snapshot={id=1,evaluationContext={horizon=30},Price=price,
    chains={{ready=true,economy=a},{ready=true,economy=a},{ready=true,economy=b}}}
CSC_AI_EconomyAdapters.ServiceResearch(snapshot,bids)
local bid=assert(bids['civic:6'])
assert(bid.value==300+50*256 and bid.serviceQ8==50*256 and bid.serviceChains==2 and bid.jobs[9])
for key in pairs(bids)do assert(key=='civic:6')end
''')

    def test_service_research_requires_every_other_gate_to_be_ready(self):
        self.vm().execute('''
local a=supplied('A',1)
local s=a.services[1]
s.stage=4;s.producer='CAFE';s.unlock=5;s.researchTopic={kind='civic',index=12}
s.materials.specialty=1
a.fourth={type='CAFE',working=true}
local function offer()return M.ServiceResearchOffers({a},nil,30,price)['civic:12']end
assert(not offer())
a.suppliers[2]={kind='specialty',plot=12,ready=5};assert(not offer())
a.suppliers[2].ready=0;assert(offer().value==25*256)
s.customer.working=false;assert(not offer());s.customer.working=true
a.fourth.working=false;assert(not offer());a.fourth.working=true
s.finish=5;assert(not offer());s.finish=nil
s.researchTopic=nil;assert(not offer())
''')

    def test_service_research_pools_housing_across_chains(self):
        self.vm().execute('''
local a=supplied('A',1);local b=supplied('B',2)
for _,site in ipairs({a,b})do
    local service=site.services[1]
    service.kind='HOUSING';service.amount=1;service.unlock=5
    service.researchTopic={kind='civic',index=9}
end
local housing={cities={[3]={active=0,left=0,food=2}},activeCities={},stop=-4,quarter=0,half=1}
local bid=assert(M.ServiceResearchOffers({a,b},housing,30,price)['civic:9'])
assert(#bid.streams==1 and bid.streams[1].yield=='YIELD_FOOD' and bid.streams[1].amount==1.5)
assert(bid.value==25*256*1.5)
''')

    def test_two_physical_producers_can_pay_one_recipient(self):
        self.vm().execute('''
local a,b=supplied('A',1),supplied('B',2)
local r=assert(M.JointForecast(withServices({a,b}),price))
assert(r.serviceStreams==2 and r.serviceValueQ8==60*256)
''')

    def test_housing_stacks_before_pricing_and_only_rewards_growth_relief(self):
        self.vm().execute('''
local a,b=supplied('A',1),supplied('B',2)
for _,site in ipairs({a,b}) do
 site.services[1].kind='HOUSING';site.services[1].amount=2
end
local city={active=0,left=0,food=2}
local housing={cities={[3]=city},activeCities={},stop=-4,quarter=0,half=1}
local function value(sites)
 local w=withServices(sites)
 w.serviceHousing=housing
 return assert(M.JointForecast(w,price)).serviceValueQ8
end
assert(value({a})==45*256 and value({a,b})==45*256)
city.left=2;assert(value({a})==0)
city.left=0;city.food=0;assert(value({a})==0)
city.left=2;city.food=2;city.active=2
housing.activeCities={3}
assert(value({a})==0)
local supplies=a.suppliers;a.suppliers={}
assert(value({a})==-45*256)
a.suppliers=supplies
a.services[1].unlock=10
local w=withServices({a})
w.serviceHousing=housing
local r=assert(M.JointForecast(w,function(s,h)return price(s,math.min(h,s.finish or h))end))
assert(r.serviceValueQ8==-15*256) -- ten turns of relief lost
''')

    def test_shared_engineer_leaf_under_stage_two_and_four_roots_pays_both(self):
        self.vm().execute('''
local a=supplied('A',1);a.fourth={type='CAFE',working=true}
a.suppliers[2]={kind='specialty',plot=12,ready=0}
a.customers[2]={type='ZOO',plot=101,city=3,stage=4,working=true,complete=true}
a.services[2]={id='ROOT4/LEAF:101',root='ROOT4',leaf='LEAF',producer='CAFE',stage=4,
 customer=a.customers[2],city=3,plot=101,kind='PSEUDOYIELD',amount=1,unlock=0,
 materials={base=1,specialty=1},known=true}
local r=assert(M.JointForecast(withServices({a}),price))
assert(r.serviceStreams==2)
table.remove(a.suppliers,2)
assert(M.JointForecast(withServices({a}),price).serviceStreams==1)
''')

    def test_service_does_not_receive_future_building_depth_multiplier(self):
        self.vm().execute('''
local a=supplied('A',1);a.seconds[1]={type='MILL',unlock=0,turns=2,forecastDepth=3}
a.services[1].kind='YIELD_PERCENT';a.services[1].yieldType='YIELD_FAITH'
a.services[1].amount=10;a.services[1].base=20
local function weighted(s,h)
 local raw=price(s,h);return raw,raw*(1+2*(s.forecastDepth or 0))
end
local r=assert(M.JointForecast(withServices({a}),weighted))
assert(r.serviceStreams==1)
for _,s in ipairs(r.streams)do if s.service then assert(not s.forecastDepth and s.valueQ8==s.bidValueQ8)end end
''')

    def test_ordinary_customer_world_keeps_services_excluded(self):
        self.vm().execute('''
local a=supplied('A',1)
local r=assert(M.JointForecast(world({a}),price))
assert(r.servicesExcluded and r.serviceStreams==0 and #a.services==1)
''')

    def test_unavailable_optional_quote_preserves_ordinary_income(self):
        self.vm().execute('''
local a=supplied('A',1)
local ordinary=assert(M.JointForecast(world({a}),price))
local function missing(s,h)if s.service then return nil end;return price(s,h)end
local r=assert(M.JointForecast(withServices({a}),missing))
assert(r.valueQ8==ordinary.valueQ8 and r.serviceValueQ8==0 and #r.omissions>0)
''')

    def test_no_ship_demand_still_values_admiral_points(self):
        self.vm().execute('''
local a=supplied('A',1);a.services[2]=copy(a.services[1])
a.services[2].id='SHIP:100';a.services[2].kind='NAVAL_PRODUCTION_PERCENT'
a.services[2].amount=20;a.services[2].base=0;a.services[2].finish=10
assert(M.JointForecast(withServices({a}),price).serviceStreams==1)
a.services[2].base=20;a.services[2].unlock=12
assert(M.JointForecast(withServices({a}),price).serviceStreams==1)
''')

    def test_only_selected_mutually_exclusive_producer_has_a_service(self):
        self.vm().execute('''
local a=supplied('A',1)
a.seconds={{type='MILL',working=true},{type='OTHER',unlock=0,turns=1}}
a.services[2]=copy(a.services[1]);a.services[2].id='OTHER:100'
a.services[2].producer='OTHER';a.services[2].amount=100
local r=assert(M.JointForecast(withServices({a}),price))
assert(r.serviceStreams==1 and r.chainStages.A.second=='MILL')
''')

    def test_shared_unpriced_ledger_keeps_both_optima_and_priced_results_independent(self):
        self.vm().execute('''
local a=supplied('A',1)
a.third={type='BAKERY',unlock=0,turns=1,maintenance=10}
a.customers={{type='MARKET',plot=100,city=3,stage=3,working=true,complete=true}}
a.services={{id='BAKERY_GPP:100',root='ROOT3',leaf='GPP',producer='BAKERY',stage=3,
 customer=a.customers[1],city=3,plot=100,kind='PSEUDOYIELD',amount=20,
 unlock=0,materials={base=1},known=true}}
local token={};local memo={token=token,entries={},count=0,hits=0}
local ordinary=world({a});ordinary.evaluationMemo=memo;ordinary.ledgerMemoToken=token
local enabled=withServices({a});enabled.evaluationMemo=memo;enabled.ledgerMemoToken=token
local plain=assert(M.JointForecast(world({a}),price))
local full=assert(M.JointForecast(withServices({a}),price))
local off=assert(M.JointForecast(ordinary,price));local on=assert(M.JointForecast(enabled,price))
assert(off.valueQ8==plain.valueQ8 and on.valueQ8==full.valueQ8)
assert(off.evaluations==plain.evaluations and on.evaluations==full.evaluations)
assert(off.chainStages.A.third==nil and on.chainStages.A.third=='BAKERY')
assert(off.serviceStreams==0 and on.serviceStreams==1 and memo.hits>0 and memo.count<=16)
on.streams[1].amount=99999
assert(M.JointForecast(enabled,price).valueQ8==full.valueQ8)
''')

    def test_mismatched_shared_ledger_identity_fails_closed(self):
        self.vm().execute('''
local w=withServices({supplied('A',1)})
w.evaluationMemo={token={},entries={},count=0,hits=0};w.ledgerMemoToken={}
local r,reason=M.JointForecast(w,price)
assert(not r and reason:find('identity',1,true))
''')


class ServiceDefinitions(unittest.TestCase):
    def vm(self):
        vm=LuaRuntime(unpack_returned_tuples=True)
        vm.execute('''
function info(rows,key)
 local t={};for _,v in ipairs(rows)do if key then t[v[key]]=v end end
 return setmetatable(t,{__call=function()local i=0;return function()i=i+1;return rows[i]end end})
end
GameInfo={
 CSC_QuarterFlowBuildings=info({{QuarterKey='NEW_FAMILY',Stage=3,BuildingType='PRODUCER'}}),
 BuildingModifiers=info({{BuildingType='PRODUCER',ModifierId='ROOT'}}),
 Modifiers=info({{ModifierId='ROOT',ModifierType='ATTACH',OwnerRequirementSetId='OWNER',SubjectRequirementSetId='SUBJECT'},
  {ModifierId='LEAF',ModifierType='GPP'}},'ModifierId'),
 DynamicModifiers=info({{ModifierType='ATTACH',EffectType='EFFECT_ATTACH_MODIFIER',CollectionType='COLLECTION_PLAYER_DISTRICTS'},
  {ModifierType='GPP',EffectType='EFFECT_ADJUST_DISTRICT_GREAT_PERSON_POINTS',CollectionType='COLLECTION_OWNER'}},'ModifierType'),
 ModifierArguments=info({{ModifierId='ROOT',Name='ModifierId',Value='LEAF'},
  {ModifierId='LEAF',Name='Amount',Value='3'},
  {ModifierId='LEAF',Name='GreatPersonClassType',Value='ARTIST'}}),
 Requirements=info({{RequirementId='CIVIC',RequirementType='REQUIREMENT_PLAYER_HAS_CIVIC'},
  {RequirementId='TAG',RequirementType='REQUIREMENT_PLOT_RESOURCE_TAG_MATCHES'},
  {RequirementId='BUYER',RequirementType='REQUIREMENT_CITY_HAS_BUILDING'},
  {RequirementId='MATCH_BUYER',RequirementType='REQUIREMENT_REQUIREMENTSET_IS_MET'},
  {RequirementId='UNKNOWN_REF',RequirementType='REQUIREMENT_REQUIREMENTSET_IS_MET'},
  {RequirementId='ANY_CUSTOMER',RequirementType='REQUIREMENT_COLLECTION_COUNT_ATLEAST'},
  {RequirementId='UNKNOWN',RequirementType='REQUIREMENT_PLOT_PROPERTY_MATCHES'}},'RequirementId'),
 RequirementSetRequirements=info({{RequirementSetId='OWNER',RequirementId='CIVIC'},
  {RequirementSetId='OWNER',RequirementId='TAG'},
  {RequirementSetId='OWNER',RequirementId='ANY_CUSTOMER'},
  {RequirementSetId='ANY_SET',RequirementId='MATCH_BUYER'},
  {RequirementSetId='ANY_SET',RequirementId='UNKNOWN_REF'},
  {RequirementSetId='UNKNOWN_SET',RequirementId='UNKNOWN'},
  {RequirementSetId='SUBJECT',RequirementId='BUYER'}}),
 RequirementArguments=info({{RequirementId='CIVIC',Name='CivicType',Value='MODDED_CIVIC'},
  {RequirementId='TAG',Name='Tag',Value='MODDED_BASE'},
  {RequirementId='BUYER',Name='BuildingType',Value='BUYER'},
  {RequirementId='ANY_CUSTOMER',Name='CollectionType',Value='COLLECTION_PLAYER_DISTRICTS'},
  {RequirementId='ANY_CUSTOMER',Name='RequirementSetId',Value='ANY_SET'},
  {RequirementId='MATCH_BUYER',Name='RequirementSetId',Value='SUBJECT'},
  {RequirementId='UNKNOWN_REF',Name='RequirementSetId',Value='UNKNOWN_SET'},
  {RequirementId='UNKNOWN',Name='PropertyName',Value='UNKNOWN_WONDER'}}),
 RequirementSets=info({{RequirementSetId='ANY_SET',RequirementSetType='REQUIREMENTSET_TEST_ANY'}},'RequirementSetId'),
 GreatPersonClasses=info({{GreatPersonClassType='ARTIST',PseudoYieldType='PSEUDOYIELD_GPP_ARTIST'}},'GreatPersonClassType'),
 BuildingReplaces=info({{CivUniqueBuildingType='UNIQUE_BUYER',ReplacesBuildingType='BUYER'}}),
}
''')
        vm.execute((AI/'CSC_AI_EconomyFacts.lua').read_text(encoding='utf-8'))
        return vm

    def test_wonder_offer_is_host_and_plot_specific_and_respects_material_protection(self):
        vm=native_fixtures.NativeValuation().vm()
        vm.execute('''
GameInfo.CSC_QuarterWonderSales=function()
 local rows={{BuildingType='BROADWAY',QuarterKey='TAILORS'},
  {BuildingType='HUB',QuarterKey='TAILORS'}}
 local i=0;return function()i=i+1;return rows[i]end
end
GameInfo.Buildings={BROADWAY={Index=77,IsWonder=1},HUB={Index=55,IsWonder=0}}
local function plot(index,owner,district)
 return {GetIndex=function()return index end,GetOwner=function()return owner end,
  GetDistrictType=function()return district end}
end
local city={GetID=function()return 10 end,GetOwner=function()return 1 end,
 GetBuildings=function()return{HasBuilding=function()return false end}end}
Cities={GetPlotPurchaseCity=function()return city end}
Map={GetAdjacentPlots=function()
 return {plot(20,1,-1),plot(21,1,-1),plot(22,2,-1),plot(23,1,4),plot(24,1,-1)}
end}
local source={GetX=function()return 0 end,GetY=function()return 0 end}
local function chain(key,working,specialty)
 return {profile={key=key},plot=source,ready=true,workingBase=working,
  supply={base={{working=working,ready=true}},specialty={{working=specialty,ready=true}}}}
end
local player={GetID=function()return 1 end}
local offers=E.WonderOffers(player,{chain('TAILORS',false,false),chain('TAILORS',true,true),
 chain('BAKERS',true,true)}, {[21]=true},1,24*256)
assert(#offers==1 and offers[1].city==10 and offers[1].building==77
 and offers[1].plot==20 and offers[1].deltaQ8==24*256)
assert(#E.WonderOffers(player,{chain('BAKERS',true,true)}, {},10,24*256)==0)
assert(E.WonderOffers(player,{chain('TAILORS',true,false)}, {},1,24*256)[1].deltaQ8==16*256)
assert(E.WonderOffers(player,{chain('TAILORS',false,false)}, {},1,24*256)[1].deltaQ8==8*256)
assert(E.WonderOffers(player,{chain('TAILORS',true,true)}, {},1,8*256)[1].deltaQ8==8*256)
local blocked=chain('TAILORS',true,false)
blocked.supply.specialty[1].ready=false
assert(#E.WonderOffers(player,{blocked}, {},10,24*256)==0)
''')

    def test_wonder_offers_publish_inside_the_native_packet(self):
        vm=LuaRuntime()
        vm.execute((AI/'CSC_AI_DistrictBridge.lua').read_text(encoding='utf-8'))
        vm.execute('''
local phase=0
CE_AIDistrictScoresBegin=function()phase=1;return 1 end
CE_AIDistrictScoresAllow=function(player)assert(phase==1 and player==1);phase=2;return 1 end
CE_AIDistrictScoresEntry=function() error('unexpected district row') end
CE_AIDistrictScoresCommit=function()assert(phase==3);phase=4;return 1 end
CE_AIDistrictScoresDisable=function()phase=-1;return 1 end
CE_AIDistrictScoresStatus=function()return '{}' end
local B=CSC_AI_DistrictBridge
local ready='{"ready":1,"faults":0,"offerCapacity":512}'
assert(B.WonderOfferLimit(ready)==0)
CE_AIWonderPlacementOffer=function(player,city,wonder,plot,delta)
 assert(phase==2 and player==1 and city==7 and wonder==77 and plot==9 and delta==6144)
 phase=3;return 1
end
local count,legacy=B.WonderOfferLimit(ready)
assert(count==512 and legacy==2048)
local max
count,max=B.WonderOfferLimit('{"ready":1,"faults":0,"offerCapacity":512,"maxOfferQ8":6144}')
assert(count==512 and max==6144)
assert(B.WonderOfferLimit('{"ready":1,"faults":1,"offerCapacity":512}')==0)
local offer={player=1,city=7,building=77,plot=9,deltaQ8=6144}
local function publish(offers)
 local args={2,10,10,10,{1},{}}
 args[21]=offers
 return B.Publish(unpack(args,1,21))
end
assert(publish({offer}) and phase==4)
assert(not publish({offer,offer}) and phase==-1)
''')

    def test_loaded_gameplay_amount_class_unlock_and_customer_define_the_service(self):
        self.vm().execute('''
local c=CSC_AI_EconomyFacts.ServiceCatalogue()
local r=c.byProducer.PRODUCER[1]
assert(r.amount==3 and r.pseudoYield=='PSEUDOYIELD_GPP_ARTIST')
assert(r.owner.civics.MODDED_CIVIC and r.subject.buildings.BUYER and r.owner.tags.MODDED_BASE==1)
assert(#c.omissions==0) -- an unrelated Wonder ANY cannot disable an admitted buyer
assert(c==CSC_AI_EconomyFacts.ServiceCatalogue())
''')

    def test_duplicate_and_unique_buyer_mappings_pay_once_per_physical_host(self):
        self.vm().execute('''
local c={type='UNIQUE_BUYER',stage=3,city=5,plot=20,complete=true}
local s={third={type='PRODUCER'},customers={c,c}}
local snapshot={cities={[5]={}},serviceKinds={PSEUDOYIELD=true}}
local records=CSC_AI_EconomyFacts.ServiceRecords(s,{base='MODDED_BASE'},snapshot,function(kind,name)
 assert(kind=='civic'and name=='MODDED_CIVIC');return 7 end)
assert(#records==1 and records[1].known and records[1].unlock==7 and records[1].amount==3)
''')

    def test_inverted_or_unknown_recipient_gate_is_an_omission(self):
        vm=self.vm()
        vm.execute('''
GameInfo.Requirements.BUYER.Inverse=1
local c=CSC_AI_EconomyFacts.ServiceCatalogue()
assert(not c.byProducer.PRODUCER and #c.omissions==1)
''')

    def test_percentage_service_keeps_native_current_output_cap(self):
        self.vm().execute('''
GameInfo.DynamicModifiers.GPP.EffectType='EFFECT_ADJUST_CITY_YIELD_MODIFIER'
GameInfo.Yields={FAITH={Index=5}}
local original=GameInfo.ModifierArguments
local rows={};for row in original()do rows[#rows+1]=row end
rows[#rows+1]={ModifierId='LEAF',Name='YieldType',Value='FAITH'}
GameInfo.ModifierArguments=info(rows)
local c={type='BUYER',stage=3,city=5,plot=20,complete=true}
local s={third={type='PRODUCER'},customers={c}}
local snapshot={cities={[5]={}},serviceKinds={YIELD_PERCENT=true},ServiceYield=function()return 1000 end}
local r=CSC_AI_EconomyFacts.ServiceRecords(s,{base='MODDED_BASE'},snapshot,function()return 0 end)
assert(#r==1 and r[1].known and r[1].base==100)
''')

    def test_unrecognized_requirement_is_not_silently_satisfied(self):
        self.vm().execute('''
GameInfo.Requirements.CIVIC.RequirementType='REQUIREMENT_MODDED_RESTRICTION'
local c=CSC_AI_EconomyFacts.ServiceCatalogue()
assert(not c.byProducer.PRODUCER and #c.omissions==1)
''')

    def test_unrelated_customer_boolean_is_not_proved_by_this_recipient(self):
        self.vm().execute('''
GameInfo.Requirements.MATCH_BUYER.Inverse=1
local c=CSC_AI_EconomyFacts.ServiceCatalogue()
assert(not c.byProducer.PRODUCER and #c.omissions==1)
''')

    def test_registered_wonder_is_a_future_gate_only_on_its_real_completed_plot(self):
        self.vm().execute('''
GameInfo.CSC_QuarterWonderServices=info({
 {HostType='WONDER',ServiceType='WONDER_SERVICE',ActivationProperty='UNKNOWN_WONDER'}})
GameInfo.Buildings={WONDER={IsWonder=1},OTHER={IsWonder=1}}
local inputs={}
for row in GameInfo.RequirementArguments() do inputs[#inputs+1]=row end
inputs[#inputs+1]={RequirementId='UNKNOWN',Name='PropertyMinimum',Value='1'}
GameInfo.RequirementArguments=info(inputs)
GameInfo.Modifiers.ROOT.SubjectRequirementSetId='UNKNOWN_SET'
local c=CSC_AI_EconomyFacts.ServiceCatalogue()
assert(#c.omissions==0 and #c.byService.WONDER_SERVICE.effects==1)
local host={type='WONDER',stage=3,city=5,plot=20,complete=true,working=true}
local other={type='OTHER',stage=3,city=5,plot=21,complete=true,working=true}
local s={third={type='PRODUCER'},customers={host,other}}
local snapshot={cities={[5]={}},serviceKinds={PSEUDOYIELD=true}}
local function records()
 return CSC_AI_EconomyFacts.ServiceRecords(s,{base='MODDED_BASE'},snapshot,function()return 7 end)
end
local r=records()
assert(#r==1 and r[1].plot==20 and r[1].known and r[1].unlock==7)
host.working=false;assert(#records()==0)
host.working=true;host.complete=false;assert(#records()==0)
''')

    def test_recipient_any_set_and_leaf_owner_gate_are_not_discarded(self):
        for mutation in [
            "GameInfo.RequirementSets={SUBJECT={RequirementSetType='REQUIREMENTSET_TEST_ANY'}}",
            "GameInfo.Modifiers.LEAF.OwnerRequirementSetId='OWNER'",
        ]:
            vm=self.vm();vm.execute(mutation)
            vm.execute("local c=CSC_AI_EconomyFacts.ServiceCatalogue();assert(not c.byProducer.PRODUCER and #c.omissions==1)")

    def test_native_price_cache_distinguishes_gpp_classes_and_growth_percentage_units(self):
        vm=native_fixtures.NativeValuation().vm()
        vm.execute('''
GameInfo.PseudoYields={ART={Index=7},ENGINEER={Index=8}}
local count=0
CE_AIPseudoYieldIntervalValue=function(pid,city,kind,amount,r,h,d)
 count=count+1;assert(pid==1 and city==10 and amount==256);return kind*256 end
local first=snapshot.Price({service=true,city=10,yield='PSEUDOYIELD',pseudoYield='ART',amount=1,ready=3},100)
local second=snapshot.Price({service=true,city=10,yield='PSEUDOYIELD',pseudoYield='ENGINEER',amount=1,ready=3},100)
assert(first==7*256 and second==8*256 and count==2)
assert(snapshot.Price({service=true,city=10,yield='PSEUDOYIELD',pseudoYield='ART',amount=1,ready=3},100)==first and count==2)
CE_AIGrowthIntervalValue=function(pid,city,percent,r,h,d)
 assert(percent==2560 and r==4 and h==100);return 1234 end
local raw,bid=snapshot.Price({service=true,city=10,yield='GROWTH',amount=10,ready=4,forecastDepth=3},100)
assert(raw==1234 and bid==raw)
''')

    def test_actual_ui_numeric_entry_observes_only_eligible_ship_work(self):
        vm=LuaRuntime()
        vm.execute('''
ExposedMembers={};hash=123
local queue={GetCurrentProductionTypeHash=function()return hash end,GetTurnsLeft=function()return 4 end}
CityManager={GetCity=function()return{GetBuildQueue=function()return queue end,GetYield=function()return 20 end}end}
GameInfo={Units={[123]={Index=7,UnitType='GALLEY',Domain='DOMAIN_SEA',PromotionClass='PROMOTION_CLASS_NAVAL_MELEE',PrereqTech='SAILING'},
 [124]={Index=8,UnitType='WARRIOR',Domain='DOMAIN_LAND',PromotionClass='PROMOTION_CLASS_MELEE'}},
 Buildings={[125]={Index=9,BuildingType='TEXTILE_WORKSHOP'}},
 Technologies={SAILING={EraType='ERA_ANCIENT'}},Civics={},
 Eras={ERA_ANCIENT={Index=0},ERA_RENAISSANCE={Index=3}},Yields={YIELD_PRODUCTION={Index=1}}}
''')
        vm.execute((AI.parent/'Adjacencies/CSC_AdjacencyUI.lua').read_text(encoding='utf-8'))
        vm.execute('''
local read=ExposedMembers.CSC_Adjacency.GetEconomyCityNumber
assert(read(1,5,'navalProduction',0)==20 and read(1,5,'currentUnit',0)==7)
assert(read(1,5,'unitTurns',7)==4 and read(1,5,'unitTurns',8)==nil)
hash=124;assert(read(1,5,'navalProduction',0)==0)
assert(read(1,5,'currentBuilding',0)==nil)
hash=125;assert(read(1,5,'currentBuilding',0)==9 and read(1,5,'currentBuildingTurns',9)==4)
assert(read(1,5,'currentBuildingTurns',8)==nil)
hash=124;assert(read(1,5,'currentBuildingTurns',9)==nil)
assert(read(1,5,'buildingTurns',7)==nil) -- retain existing timing behavior
''')

    def test_quarter_enables_both_service_worlds_without_mutating_customer_baseline(self):
        vm=native_fixtures.NativeValuation().vm()
        vm.execute('''
local before={sites={}},after
after={sites={},baselineWorld=before}
snapshot.serviceKinds={PSEUDOYIELD=true}
snapshot.QuarterWorld=function()return before,after end
local seen
snapshot.WorldQuote=function(w)
 assert(w.includeServices)
 if not w.baselineWorld then seen=w;return{valueQ8=1000,serviceValueQ8=50,siteAdjustmentQ8=0}end
 assert(w.baselineWorld==seen)
 return{valueQ8=1100,bidValueQ8=1100,serviceValueQ8=75,serviceStreams=2,servicesExcluded=false,siteAdjustmentQ8=0,
  chainStages={new={second='Mill'}},streams={},evaluations=1,affectedChains=1}
end
local s=site();s.key='new'
local city={GetID=function()return 10 end};local plot={GetIndex=function()return 20 end}
local q=E.QuarterForecast(snapshot,city,plot,{district={Index=7}},s,0,false)
assert(q.valueQ8==100 and q.serviceValueQ8==25 and not q.servicesExcluded)
assert(not before.includeServices and not after.includeServices and after.baselineWorld==before)
''')

    def test_service_is_added_once_after_ordinary_cap_and_cannot_bypass_site_quality(self):
        native_fixtures.NativeValuation().vm().execute('''
local s=site();s.comparisonReferenceQ8=600*256;s.baseCount=1
local plain={valueQ8=100000,bidValueQ8=100000,adjacency=2}
local positive={valueQ8=105000,bidValueQ8=105000,adjacency=2,serviceValueQ8=5000}
local negative={valueQ8=95000,bidValueQ8=95000,adjacency=2,serviceValueQ8=-5000}
local base=E.PlacementValue(plain,s,0,false)
assert(base==300*256)
assert(E.PlacementValue(positive,s,0,false)==base+5000)
assert(E.PlacementValue(negative,s,0,false)==base-5000)
s.comparisonReferenceQ8=nil
assert(E.PlacementValue(positive,s,0,false)==E.PlacementValue(plain,s,0,false)+5000)
assert(E.PlacementValue({valueQ8=-1,bidValueQ8=999999,adjacency=2,serviceValueQ8=100000},s,0,false)==-1)
positive.adjacency=1
assert(E.PlacementValue(positive,s,0,false)==E.DeferredQuarterQ8)
''')


if __name__=='__main__':
    unittest.main()
