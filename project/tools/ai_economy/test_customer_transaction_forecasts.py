"""Real gameplay registry coverage and transaction-only customer forecasts."""
from pathlib import Path
import re
import sqlite3
import sys
import unittest

from lupa.lua51 import LuaRuntime
import test_boundaries as boundaries

ROOT=Path(__file__).resolve().parents[3]
AI=ROOT/'Civ Supply Chains/Lua_UI/AI'


class CustomerTransactions(unittest.TestCase):
    def test_current_gameplay_stage_three_customers_enter_shared_index_once(self):
        from driver import lua
        sys.path.insert(0,str(ROOT/'project/tools/transactions'))
        from population_catalogue_fixture import compile_catalogue
        db=compile_catalogue(lgd=False)
        names=['CSC_QuarterFlowBuildings','CSC_QuarterCustomerBuildings','CSC_Stage3CustomerTransactions','CSC_QuarterWonderSales']
        db.row_factory=sqlite3.Row
        rows={n:[dict(r)for r in db.execute('SELECT * FROM '+n)]for n in names}
        self.assertFalse(any(r['ProducerStage']==3 for r in rows['CSC_QuarterCustomerBuildings']))
        vm=boundaries.Boundaries().facts_vm()
        vm.execute('function list(rows)return setmetatable({},{__call=function()local i=0;return function()i=i+1;return rows[i]end end})end')
        for n,rs in rows.items():vm.execute('GameInfo.'+n+'=list('+lua(rs)+')')
        buildings={r['BuildingType']for r in rows['CSC_QuarterFlowBuildings']}
        wonders={r['BuildingType']for r in rows['CSC_QuarterWonderSales']}
        vm.execute('GameInfo.Buildings={}')
        for i,b in enumerate(sorted(buildings)):vm.execute('GameInfo.Buildings['+lua(b)+']={BuildingType='+lua(b)+',Index='+str(i)+'}')
        for i,b in enumerate(sorted(wonders),100):
            vm.execute('GameInfo.Buildings['+lua(b)+']={BuildingType='+lua(b)+',Index='+str(i)+',PrereqDistrict="DISTRICT_WONDER",IsWonder=true}')
        vm.execute('''
local F=CSC_AI_EconomyFacts
local function count(key,building)
 local n=0;for _,r in ipairs(F.CustomerDefinitions(key))do
 if r.ProducerStage==3 and r.BuildingType==building then n=n+1 end end;return n
end
assert(count('BAKERS','BUILDING_MARKET')==1)
assert(count('TAILORS','BUILDING_MARKET')==1 and count('TAILORS','BUILDING_TEMPLE')==1)
local n=0;for _,r in ipairs(F.CustomerDefinitions('TAILORS'))do
 if r.ProducerStage==4 and r.DistrictType=='DISTRICT_WONDER'then n=n+1 end end
assert(n==3) -- ordinary sales survive even with Service valuation deferred
''')
        # Old packs may still contain an overlapping Stage3 venue. Reload the
        # module against that schema and verify a duplicate registry row is free.
        rows['CSC_QuarterCustomerBuildings'].append(dict(QuarterKey='BAKERS',DistrictType='DISTRICT_COMMERCIAL_HUB',BuildingType='BUILDING_MARKET',ProducerStage=3))
        vm.execute('GameInfo.CSC_QuarterCustomerBuildings=list('+lua(rows['CSC_QuarterCustomerBuildings'])+')')
        vm.execute((AI/'CSC_AI_EconomyFacts.lua').read_text(encoding='utf-8'))
        vm.execute("local n=0;for _,r in ipairs(CSC_AI_EconomyFacts.CustomerDefinitions('BAKERS'))do if r.ProducerStage==3 then n=n+1 end end;assert(n==1)")
        db.close()

    def model(self):
        vm=LuaRuntime()
        vm.execute((AI/'CSC_AI_EconomyModel.lua').read_text(encoding='utf-8'))
        vm.execute('''
M=CSC_AI_EconomyModel
price=function(s,h)return math.floor(s.amount*(math.min(h,s.finish or h)-s.ready)*256+.5)end
site={city=1,population=10,horizon=30,quarterReady=0,materialYield='YIELD_FOOD',
 seconds={{type='MILL',working=true}},third={type='BAKERY',working=true},
 customers={},suppliers={},direct={},service={kind='GROWTH',amount=9999,unlock=0}}
venue={city=1,plot=7,stage=3,type='MARKET',building='MARKET',yield='YIELD_FOOD',
 population=10,rate=.101,sellerProperty='seller',customerProperty='buyer',
 turns=2,unlock=0,maintenance=999,complete=false,working=false,projected=true}
''')
        return vm

    def test_customer_delta_prices_transactions_after_building_and_does_not_repeat_native_upkeep(self):
        vm=self.model()
        vm.execute('''
local result=M.CustomerBuildingForecast(site,{venue},1,5,price)
assert(result and result.valueQ8==3*(26/256*10)*(30-7)*256)
assert(result.servicesExcluded and result.customerOrdinaryUpkeepExcluded)
assert(not venue.complete and venue.maintenance==999 and site.service.amount==9999)
local found=false
for _,s in ipairs(result.with.streams)do
 assert(not s.id:find('service:',1,true))
 if s.id:find(':buyer:',1,true) then assert(s.ready==7 and s.amount==26/256*10);found=true end
end
assert(found)
local duplicate=M.CustomerBuildingForecast(site,{venue,venue},1,5,price)
assert(duplicate.valueQ8==result.valueQ8)
assert(M.CustomerBuildingForecast(site,{},1,5,price).valueQ8==0)
assert(M.CustomerBuildingForecast(site,{venue},1,31,price).valueQ8==0)
assert(M.CustomerBuildingForecast(site,{venue},1,nil,price)==nil)
''')

    def test_existing_customer_link_values_only_the_mapped_exchange(self):
        self.model().execute('''
venue.complete=true;venue.working=true;venue.projected=false;venue.maintenance=0
site.customers={venue}
site.direct={{id='unrelated',yield='YIELD_FOOD',amount=100,ready=0,city=1}}
assert(M.ExistingCustomerConnectionValue(site,venue,price)==3*(26/256*10)*30*256)
assert(#site.customers==1 and site.customers[1]==venue and site.service.amount==9999)
''')

    def test_customer_queue_delays_missing_producer_in_same_city_but_cities_can_build_in_parallel(self):
        vm=self.model()
        vm.execute('''
site.third={type='BAKERY',working=false,unlock=0,turns=4}
local same=M.CustomerBuildingForecast(site,{venue},1,5,price)
local first
for _,s in ipairs(same.with.streams)do if s.id:find(':buyer:',1,true) then first=s.ready end end
assert(first==11) -- Hub5, Bakery4, Market2 in one queue
venue.city=2
local separate=M.CustomerBuildingForecast(site,{venue},2,5,price)
for _,s in ipairs(separate.with.streams)do if s.id:find(':buyer:',1,true) then assert(s.ready==7)end end
assert(separate.valueQ8>same.valueQ8)
''')

    def test_recursive_customer_prerequisites_keep_time_without_duplicate_upkeep(self):
        vm=self.model()
        vm.execute('''
venue.prerequisites={{type='ORDINARY_PREREQUISITE',working=false,unlock=0,turns=3,maintenance=777}}
local result=M.CustomerBuildingForecast(site,{venue},1,5,price)
assert(result.valueQ8==3*(26/256*10)*(30-10)*256)
assert(venue.prerequisites[1].maintenance==777)
for _,s in ipairs(result.with.streams)do
 assert(not s.id:find('upkeep:1:ORDINARY_PREREQUISITE',1,true))
end
''')

    def test_canonical_legs_keep_quantity_rounding_and_actual_yields(self):
        vm=self.model()
        vm.execute('''
venue.transaction={id='ACTUAL',kind='PARTNER_POPULATION',amount=.101,legs={
 {key='P',recipient='SOURCE',yield='YIELD_PRODUCTION',amount=2,property='seller'},
 {key='G',recipient='SOURCE',yield='YIELD_GOLD',amount=3,property='seller'},
 {key='R',recipient='PARTNER',yield='YIELD_SCIENCE',amount=4,property='buyer'}}}
local result=M.CustomerBuildingForecast(site,{venue},1,5,price)
-- Round .101 to the receiving city's Q8 rate BEFORE applying each leg factor.
assert(result.valueQ8==9*(26/256*10)*(30-7)*256)
local science=false
for _,s in ipairs(result.with.streams)do
 if s.yield=='YIELD_SCIENCE' then assert(s.amount==4*(26/256*10));science=true end
end
assert(science)
venue.transaction={id='STACK',kind='PARTNER_POPULATION_STEPS',amount=2,step=3,
 legs={{key='R',recipient='PARTNER',yield='YIELD_SCIENCE',amount=3,property='buyer'}}}
venue.population=9
local stack=M.CustomerBuildingForecast(site,{venue},1,5,price)
assert(stack.valueQ8==18*(30-7)*256) -- not a hardcoded /5 Culture exchange
''')

    def test_quarter_bid_excludes_service_without_mutating_shared_building_repair_site(self):
        vm=boundaries.Boundaries().bid_vm()
        vm.execute('''
local source={value=1000,baseCount=1,service={kind='GROWTH',amount=10}}
snapshot.Site=function()return source end
CSC_AI_EconomyModel.Forecast=function(site)
 assert(site.service==nil)
 return{valueQ8=1000,adjacency=4,streams={},omissions={}}
end
local rows=CSC_AI_EconomyAdapters.QuarterBids(snapshot,placement,{},early)
assert(#rows==3 and source.service.amount==10)
''')

    def test_supply_placement_delta_excludes_future_services_and_keeps_shared_facts(self):
        vm=boundaries.Boundaries().bid_vm()
        vm.execute('''
local source={service={amount=9999},suppliers={{plot=7},{plot=8}},direct={}}
local chain={economy=source}
snapshot.SupplyAdjacencyLoss=function()return{}end
CSC_AI_EconomyModel.Forecast=function(site)
 assert(site.service==nil)
 return{valueQ8=#site.suppliers*100}
end
assert(CSC_AI_EconomyAdapters.SupplyValue(snapshot,chain,7)==100)
assert(source.service.amount==9999 and #source.suppliers==2)
''')


if __name__=='__main__':unittest.main()
