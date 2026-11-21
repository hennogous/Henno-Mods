"""Gameplay declarations -> shared adjacency/Facts -> joint customer valuation."""
import unittest
from customer_world_fixture import world


class CustomerWorld(unittest.TestCase):
    def test_joint_quarter_adapter_scopes_cost_diagnostics_to_the_new_chain(self):
        vm=world()
        from customer_world_fixture import MOD
        vm.execute((MOD/'Lua_UI/AI/CSC_AI_EconomyAdapters.lua').read_text())
        vm.execute('''
local s=snapshot();s.Price=price
s.WorldQuote=function(w)return CSC_AI_EconomyModel.JointForecast(w,price)end
local site=assert(s.Site(CITIES[3],PLOTS[3],profile));site.purchaseGold=42
local quote=assert(CSC_AI_EconomyAdapters.QuarterForecast(s,CITIES[3],PLOTS[3],profile,site,1000,false))
assert(quote.jointEconomy and site.jointEconomy and quote.affectedChains==3)
local invoice=0
for _,flow in ipairs(quote.streams)do
 assert(not flow.id:find(s.chains[1].economy.key,1,true))
 if flow.id=='footprint-purchase'then invoice=invoice+1 end
end
assert(invoice==1)
''')

    def test_new_quarter_uses_common_world_and_enters_observed_route_forecast(self):
        world().execute('''
local s=snapshot();local site=assert(s.Site(CITIES[3],PLOTS[3],profile))
local before,after=assert(s.QuarterWorld(CITIES[3],PLOTS[3],profile,site))
assert(before==s.CurrentWorld() and #before.sites==2 and #after.sites==3)
assert(after.sites[3]~=site and after.sites[3].key==site.key and after.sites[3].service==nil)
assert(before.trade.observed==after.trade.observed and before.trade.definitions==after.trade.definitions)
local M=CSC_AI_EconomyModel
local result=assert(M.JointCustomerForecast(before,after,price))
assert(result.after.chainStages[site.key] and result.after.quarterReadyByChain[site.key]>=site.quarterReady)
local hasFoundation=false
for _,event in ipairs(after.trade.plannedChanges)do
 if event.quarterStartKey==site.key and event.field=='quarters'then hasFoundation=true end
end
assert(hasFoundation and #before.sites==2)
''')

    def test_two_quarters_share_one_market_upkeep_and_receiving_population_rounding(self):
        world().execute('''
local s=snapshot();local before,after=assert(s.CustomerWorld(3,GameInfo.Districts.DISTRICT_COMMERCIAL_HUB.Index,3))
local M=CSC_AI_EconomyModel;local q=assert(M.JointCustomerForecast(before,after,price))
assert(#before.sites==2 and #after.sites==2 and before.trade.observed==after.trade.observed)
assert(next(before.populationBaselines)==nil and next(after.populationBaselines)==nil)
assert(q.after.byBuilding['1:3:BUILDING_MARKET']==6)
local markets,upkeep,food=0,0,0
for _,i in ipairs(q.after.investments)do if i.type=='BUILDING_MARKET'then markets=markets+1 end end
local venue=after.sites[1].customers[#after.sites[1].customers]
for _,f in ipairs(q.after.streams)do
 if f.id=='upkeep:1:3:BUILDING_MARKET'then upkeep=upkeep+f.amount;assert(f.ready==6)end
 if f.id:find('population:1:3:YIELD_FOOD:',1,true)==1 then
  food=food+f.amount;assert(f.ready==6 and #f.contributors==2)
 end
end
assert(markets==1 and upkeep==-1)
assert(food==M.PopulationPayout(2*venue.transaction.amount*9,9))
assert(q.valueQ8>0 and q.servicesExcluded and q.modelOnly)
assert(s.CustomerWorld(3,GameInfo.Districts.DISTRICT_COMMERCIAL_HUB.Index,3)==before)
assert(#before.sites[1].customers<#after.sites[1].customers) -- No fact mutation.
''')

    def test_customer_queue_delays_other_investments_in_its_city_and_shared_prerequisites_once(self):
        world().execute('''
PLOTS[3].city=1;BUILDINGS[1].BUILDING_CSC_BAKERS_BAKERY=nil
local helper={Index=1000,BuildingType='BUILDING_HELPER',PrereqDistrict='DISTRICT_COMMERCIAL_HUB',Maintenance=1}
GameInfo.Buildings[1000]=helper;GameInfo.Buildings[helper.BuildingType]=helper
GameInfo.BuildingPrereqs=info({{Building='BUILDING_MARKET',PrereqBuilding=helper.BuildingType}})
local s=snapshot();local b,a=assert(s.CustomerWorld(1,GameInfo.Districts.DISTRICT_COMMERCIAL_HUB.Index,3))
local q=assert(CSC_AI_EconomyModel.JointCustomerForecast(b,a,price))
assert(q.before.byBuilding['1:1:BUILDING_CSC_BAKERS_BAKERY']==2)
assert(q.after.byBuilding['1:1:BUILDING_CSC_BAKERS_BAKERY']==6)
assert(q.after.byBuilding['1:1:BUILDING_HELPER']==8 and q.after.byBuilding['1:1:BUILDING_MARKET']==10)
local n=0;for _,i in ipairs(q.after.investments)do if i.type==helper.BuildingType then n=n+1 end end
assert(n==1 and a.queueReady['1:1']==4 and b.queueReady==nil)
''')

    def test_footprint_loses_material_transactions_and_adjacency_while_adding_customer_value(self):
        world().execute('''
local s=snapshot();local b,a=assert(s.CustomerWorld(1,GameInfo.Districts.DISTRICT_COMMERCIAL_HUB.Index,4))
assert(#b.sites[1].suppliers==1 and #a.sites[1].suppliers==0 and #a.sites[2].suppliers==1)
local production,gold=false,false
for _,f in ipairs(a.extraStreams)do if f.city==1 and f.component=='quarter-adjacency-externality'then
 if f.yield=='YIELD_PRODUCTION'then production=f.amount<0 and f.ready==0 end
 if f.yield=='YIELD_GOLD'then gold=f.amount>0 and f.ready==0 end
end end
assert(production and gold)
local q=assert(CSC_AI_EconomyModel.JointCustomerForecast(b,a,price))
local old,new=0,0
for _,f in ipairs(q.before.streams)do if f.id:find('/material:',1,true)and f.id:find(':4:',1,true)then old=old+1 end end
for _,f in ipairs(q.after.streams)do if f.id:find('/material:',1,true)and f.id:find(':4:',1,true)then new=new+1 end end
assert(old>0 and new==0)
assert(PLOTS[4].resource=='RESOURCE_WHEAT'and PLOTS[4].improvement=='IMPROVEMENT_FARM')
''')

    def test_city_lights_provider_affects_quarters_at_foundation_and_receives_at_completion(self):
        world(city_lights=True).execute('''
local s=snapshot();local b,a=assert(s.CustomerWorld(3,GameInfo.Districts.DISTRICT_RURALCOMMUNITYA.Index,3))
local suppliers,receiving=0,0
for _,f in ipairs(a.extraStreams)do
 if f.component=='quarter-adjacency-externality'and f.yield=='YIELD_PRODUCTION'then
  suppliers=suppliers+1;assert(f.amount==1 and f.ready==0)
 elseif f.component=='customer-csc-adjacency'then receiving=receiving+1;assert(f.ready==4)end
end
assert(suppliers==2 and receiving>0)
assert(CSC_AI_EconomyModel.JointCustomerForecast(b,a,price).valueQ8>0)
''')

    def test_existing_unfinished_customer_counts_as_an_adjacency_source(self):
        world().execute('''
local s=snapshot();local initial=s.DirectAmounts(CITIES[1],PLOTS[1],profile)
PLOTS[3].district='DISTRICT_COMMERCIAL_HUB';PLOTS[3].incomplete=true
local next=snapshot();local actual=next.DirectAmounts(CITIES[1],PLOTS[1],profile)
assert(actual.YIELD_GOLD==initial.YIELD_GOLD+1)
for _,chain in ipairs(next.chains)do for _,venue in ipairs(chain.economy.customers)do
 assert(venue.plot~=3) -- The source counts; its future Market is not yet an actual venue.
end end
''')

    def test_unique_customer_inherits_one_canonical_transaction_per_supplier(self):
        world().execute('''
local unique={Index=1000,BuildingType='BUILDING_UNIQUE_MARKET',PrereqDistrict='DISTRICT_COMMERCIAL_HUB',TraitType='TRAIT_UNIQUE'}
GameInfo.Buildings[1000]=unique;GameInfo.Buildings[unique.BuildingType]=unique
GameInfo.BuildingReplaces=info({{CivUniqueBuildingType=unique.BuildingType,ReplacesBuildingType='BUILDING_MARKET'}})
GameInfo.CivilizationTraits=info({{CivilizationType='CIV_TEST',TraitType='TRAIT_UNIQUE'}})
PlayerConfigurations[1]={GetCivilizationTypeName=function()return'CIV_TEST'end,GetLeaderTypeName=function()return nil end}
local s=snapshot();local b,a=assert(s.CustomerWorld(3,GameInfo.Districts.DISTRICT_COMMERCIAL_HUB.Index,3))
for _,site in ipairs(a.sites)do
 local n=0;for _,v in ipairs(site.customers)do if v.plot==3 then
  n=n+1;assert(v.type==unique.BuildingType and v.transaction.partner=='BUILDING_MARKET')
 end end;assert(n==1)
end
local q=assert(CSC_AI_EconomyModel.JointCustomerForecast(b,a,price))
assert(q.after.byBuilding['1:3:BUILDING_UNIQUE_MARKET']==6 and q.after.byBuilding['1:3:BUILDING_MARKET']==nil)
''')

    def test_stage_two_bid_resolves_the_actual_unique_granary_and_fixed_exchange(self):
        from customer_world_fixture import MOD
        vm=world()
        vm.execute((MOD/'Lua_UI/AI/CSC_AI_EconomyAdapters.lua').read_text())
        vm.execute('''
local unique={Index=1000,BuildingType='BUILDING_UNIQUE_GRANARY',PrereqDistrict='DISTRICT_CITY_CENTER',
 TraitType='TRAIT_UNIQUE',Cost=65,Maintenance=2}
GameInfo.Buildings[1000]=unique;GameInfo.Buildings[unique.BuildingType]=unique
GameInfo.BuildingReplaces=info({{CivUniqueBuildingType=unique.BuildingType,ReplacesBuildingType='BUILDING_GRANARY'}})
GameInfo.CivilizationTraits=info({{CivilizationType='CIV_TEST',TraitType='TRAIT_UNIQUE'}})
PlayerConfigurations[1]={GetCivilizationTypeName=function()return'CIV_TEST'end,GetLeaderTypeName=function()return nil end}
local s=snapshot();s.Price=price
local E=CSC_AI_EconomyAdapters
local chain=s.chains[1]
local value=assert(E.StageTwoCustomerValue(s,chain,CITIES[3],8,unique))
assert(value==3*(30-2)*256) -- Food to the Granary, Production and optional Gold to the Mill.
assert(E.StageTwoCustomerValue(s,chain,CITIES[3],8,GameInfo.Buildings.BUILDING_GRANARY)==nil)
PLOTS[8].incomplete=true
local next=snapshot();next.Price=price
assert(E.StageTwoCustomerValue(next,next.chains[1],CITIES[3],8,unique)==nil)
''')

    def test_bakers_and_tailors_share_market_and_tailors_two_venues_pool_at_source(self):
        world().execute('''
PLOTS[2].district='DISTRICT_CSC_TAILORS_QUARTER'
PLOTS[5].resource='RESOURCE_COTTON';PLOTS[5].improvement='IMPROVEMENT_PLANTATION'
for _,name in ipairs({'BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP','BUILDING_CSC_TAILORS_TAILOR','BUILDING_TEMPLE'})do GameInfo.Buildings[name].MustPurchase=0 end
BUILDINGS[2]={};grant(2,'BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP',2);grant(2,'BUILDING_CSC_TAILORS_TAILOR',2)
plot(9,3,-1,3,nil,nil,'DISTRICT_HOLY_SITE');grant(3,'BUILDING_TEMPLE',9)
local s=snapshot();local b,a=assert(s.CustomerWorld(3,GameInfo.Districts.DISTRICT_COMMERCIAL_HUB.Index,3))
local q=assert(CSC_AI_EconomyModel.JointCustomerForecast(b,a,price))
local markets=0;for _,i in ipairs(q.after.investments)do if i.type=='BUILDING_MARKET'then markets=markets+1 end end
assert(markets==1)
local target,paid=0,0
for _,venue in ipairs(a.sites[2].customers)do if venue.stage==3 then target=target+venue.transaction.amount*venue.population end end
for _,f in ipairs(q.after.streams)do if f.id:find('population:1:2:YIELD_PRODUCTION:',1,true)==1 then paid=paid+f.amount end end
assert(paid==CSC_AI_EconomyModel.PopulationPayout(target,9))
local food,culture=0,0
for _,f in ipairs(q.after.streams)do if f.city==3 and f.id:find('population:',1,true)==1 then
 if f.yield=='YIELD_FOOD'then food=food+f.amount end
 if f.yield=='YIELD_CULTURE'then culture=culture+f.amount end
end end
assert(food>0 and culture>0)
''')

    def test_zero_delta_common_world_and_explicit_owner_budget_failures(self):
        world().execute('''
local s=snapshot();local d=GameInfo.Districts.DISTRICT_COMMERCIAL_HUB.Index
local before=assert(s.CustomerWorld(3,d,3))
assert(CSC_AI_EconomyModel.JointCustomerForecast(before,before,price).valueQ8==0)
assert(s.CustomerWorld(1,d,3)==nil)
local over=snapshot();for i=3,65 do over.chains[i]=over.chains[1]end
local bad,error=over.CustomerWorld(3,d,3)
assert(bad==nil and error=='Affected chain budget exceeded')
''')

    def test_supplier_footprint_reprices_shared_route_receipts_with_the_other_chain_present(self):
        world().execute('''
local D=assert(CSC_TradeRouteCore.ReadDefinitions(GameInfo));local ch=D.byId.BAKERS_BAKERY
for id,c in pairs(CITIES)do local owner=id
 c.GetProperty=function(_,key)
  if owner<3 and key==ch.supplyProperty then return 1 end
  if owner==3 and key==ch.importProperty then return 2 end
  return 0
 end
end
CITIES[3].GetTrade=function()return{GetOutgoingRoutes=function()return{
 {OriginCityPlayer=1,OriginCityID=3,DestinationCityPlayer=1,DestinationCityID=1,TraderUnitPlayer=1,TraderUnitID=10},
 {OriginCityPlayer=1,OriginCityID=3,DestinationCityPlayer=1,DestinationCityID=2,TraderUnitPlayer=1,TraderUnitID=11}}
end}end
UnitOperationTypes={MAKE_TRADE_ROUTE=0x8374d954,PARAM_TURN=0xa783eab4}
player.GetUnits=function()return{FindID=function()return{
 GetOperationType=function()return 0x8374d954 end,GetOperationParameter=function()return 20 end}end}end
local s=snapshot();local b,a=assert(s.CustomerWorld(1,GameInfo.Districts.DISTRICT_COMMERCIAL_HUB.Index,4))
local q=assert(CSC_AI_EconomyModel.JointCustomerForecast(b,a,price))
assert(#a.sites==2 and #a.trade.observed.routes==2)
local foodBefore,foodAfter,loss=0,0,0
for _,f in ipairs(q.before.streams)do if f.id:find('route:',1,true)==1 and f.city==3 and f.yield=='YIELD_FOOD'then foodBefore=foodBefore+f.amount end end
for _,f in ipairs(q.after.streams)do
 if f.id:find('route:',1,true)==1 and f.city==3 and f.yield=='YIELD_FOOD'then foodAfter=foodAfter+f.amount end
 if f.city==3 and f.yield=='AMENITY'then loss=loss+f.amount;assert(f.ready==0 and f.finish==10)end
end
assert(foodBefore==2 and foodAfter==1 and loss==-1)
''')

    def test_out_of_horizon_customer_receiving_income_never_reaches_price(self):
        world().execute('''
local old=ui.GetEconomyCityNumber
ui.GetEconomyCityNumber=function(p,c,kind,index)if kind=='districtTurns'then return 40 end;return old(p,c,kind,index)end
local s=snapshot();local b,a=assert(s.CustomerWorld(3,GameInfo.Districts.DISTRICT_COMMERCIAL_HUB.Index,3))
local q=assert(CSC_AI_EconomyModel.JointCustomerForecast(b,a,function(f,h)
 assert(f.ready<math.min(h,f.finish or h),'Expired interval reached native pricing')
 return price(f,h)
end))
for _,f in ipairs(q.after.streams)do assert(f.component~='customer-csc-adjacency')end
''')

    def test_unfinished_quarter_and_its_producers_share_customer_construction_queue(self):
        world().execute('''
PLOTS[1].incomplete=true;PLOTS[3].city=1;BUILDINGS[1]={}
local s=snapshot();local b,a=assert(s.CustomerWorld(1,GameInfo.Districts.DISTRICT_COMMERCIAL_HUB.Index,3))
local q=assert(CSC_AI_EconomyModel.JointCustomerForecast(b,a,price));local key=b.sites[1].key
assert(q.before.quarterReadyByChain[key]==4 and q.after.quarterReadyByChain[key]==8)
assert(q.before.byBuilding['1:1:BUILDING_CSC_BAKERS_WIND_MILL']==6)
assert(q.after.byBuilding['1:1:BUILDING_CSC_BAKERS_WIND_MILL']==10)
for _,f in ipairs(q.after.streams)do if f.component=='quarter-adjacency-externality'and f.city==1 then assert(f.ready==8)end end
''')

    def test_district_repair_reschedules_hosts_and_route_gate_but_preserves_intact_owner_returns(self):
        world().execute('''
PLOTS[1].pillaged=true;PLOTS[3].city=1
local defs=assert(CSC_TradeRouteCore.ReadDefinitions(GameInfo));local channel=defs.byId.BAKERS_BAKERY
CITIES[2].GetProperty=function(_,key)return key==channel.supplyProperty and 1 or 0 end
CITIES[1].GetProperty=function(_,key)return key==channel.importProperty and 1 or 0 end
CITIES[1].GetTrade=function()return{GetOutgoingRoutes=function()return{{OriginCityPlayer=1,OriginCityID=1,
 DestinationCityPlayer=1,DestinationCityID=2,TraderUnitPlayer=1,TraderUnitID=10}}end}end
UnitOperationTypes={MAKE_TRADE_ROUTE=0x8374d954,PARAM_TURN=0xa783eab4}
player.GetUnits=function()return{FindID=function()return{GetOperationType=function()return 0x8374d954 end,
 GetOperationParameter=function()return 20 end}end}end
local s=snapshot();local b,a=assert(s.CustomerWorld(1,GameInfo.Districts.DISTRICT_COMMERCIAL_HUB.Index,3))
local q=assert(CSC_AI_EconomyModel.JointCustomerForecast(b,a,price));local key=b.sites[1].key
assert(q.before.quarterReadyByChain[key]==4 and q.after.quarterReadyByChain[key]==8)
assert(q.before.byBuilding['1:1:BUILDING_CSC_BAKERS_WIND_MILL']==4)
assert(q.after.byBuilding['1:1:BUILDING_CSC_BAKERS_WIND_MILL']==8)
local localReturns,imports=0,0
for _,f in ipairs(q.after.streams)do
 if f.id:find(b.sites[1].key..'/local:',1,true)==1 then localReturns=localReturns+1;assert(f.ready==0)end
 if f.id:find('route:',1,true)==1 and f.city==1 and f.yield=='YIELD_FOOD'then imports=imports+1;assert(f.ready==0 and f.finish==8)end
end
assert(localReturns>0 and imports==1)
''')


if __name__=='__main__':unittest.main()
