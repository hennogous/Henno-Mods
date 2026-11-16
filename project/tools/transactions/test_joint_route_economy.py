"""Actual route SQL -> selected joint investments -> one city amenity quote.

Prices are explicit utility fixtures; native reception remains G4 qualification.
"""
import unittest
import test_trade_route_kernel as route_tests
from population_catalogue_fixture import MOD


class JointRoutes(unittest.TestCase):
    def vm(self):
        vm=route_tests.Routes().vm()
        vm.execute((MOD/'Lua_UI/AI/CSC_AI_EconomyModel.lua').read_text())
        vm.execute('''
M=CSC_AI_EconomyModel
function endpoint(player,id)
 local c={player=player,city=id,quarters={},properties={},buildings={},counts={}}
 for _,ch in ipairs(D.channels)do c.counts[ch.importProperty]=0;c.counts[ch.exportProperty]=0 end
 return c
end
function bakery(c)
 local channel=D.byId.BAKERS_BAKERY
 c.properties[channel.supplyProperty]=1;c.buildings[channel.producer]=true
end
function paid(c,ch,recipient,n)
 c.counts[recipient=='ORIGIN'and D.byId[ch].importProperty or D.byId[ch].exportProperty]=n
end
function trade(cities,routes)
 return{definitions=D,observed={cities=cities,routes=routes},changes={},plannedChanges={}}
end
function world(t,sites)return{player=1,horizon=10,sites=sites or{},trade=t}end
function price(s,h)
 return s.amount*(math.min(h,s.finish or h)-s.ready)*256
end
function chain()
 return{key='B',player=1,city=2,horizon=10,quarterReady=0,existing=true,
  materialYield='YIELD_FOOD',seconds={{type='MILL',working=true}},
  third={type='BUILDING_CSC_BAKERS_BAKERY',unlock=0,turns=5,localTransactions={}},
  direct={},suppliers={},customers={}}
end
''')
        return vm

    def test_foundation_loses_observed_imports_even_without_existing_quarter_chains(self):
        self.vm().execute('''
local a,b=endpoint(1,1),endpoint(2,2);bakery(b);paid(a,'BAKERS_BAKERY','ORIGIN',1)
local t=trade({['1:1']=a,['2:2']=b},{{origin='1:1',destination='2:2',observedThrough=5}})
local after=trade(t.observed.cities,t.observed.routes)
after.observed=t.observed
after.changes={{ready=0,city='1:1',field='quarters',key='DISTRICT_CSC_BAKERS_QUARTER',value=true}}
local quote=assert(M.JointCustomerForecast(world(t),world(after),price))
assert(quote.valueQ8==-2*5*256) -- Food plus amenities lost through the observed window.
assert(quote.before.affectedChains==0 and quote.after.affectedChains==0)
assert(a.quarters.DISTRICT_CSC_BAKERS_QUARTER==nil)
for _,s in ipairs(quote.after.streams)do
 if s.yield=='AMENITY'then assert(s.amount==-1 and s.ready==0 and s.finish==5)end
end
''')

    def test_two_channels_and_ordinary_amenities_share_one_nonlinear_quote(self):
        self.vm().execute('''
local a,b=endpoint(1,1),endpoint(2,2);bakery(b)
local cafe=D.byId.BAKERS_CAFE;b.properties[cafe.supplyProperty]=1;b.buildings[cafe.producer]=true
local t=trade({['1:1']=a,['2:2']=b},{{origin='1:1',destination='2:2',observedThrough=10}})
local calls=0
local function nonlinear(s,h)
 if s.yield~='AMENITY'then return 0 end
 calls=calls+1
 assert(s.amount==2 and s.counterfactualAmenity and s.forecastDepth==nil)
 return 100*256
end
local r=assert(M.JointForecast(world(t),nonlinear))
assert(r.valueQ8==100*256 and calls==2) -- Two bounded seeds; one pooled quote each.
local combined={streams={
 {id='route',player=1,city=1,yield='AMENITY',amount=1,ready=0},
 {id='existingCafe',player=1,city=1,yield='AMENITY',amount=1,amenityBaseline=1,ready=0},
 {id='newCafe',player=1,city=1,yield='AMENITY',amount=1,ready=3}}}
assert(M.PoolAmenities(combined,{['1:1']=1},10))
assert(#combined.streams==1 and combined.streams[1].amount==1 and combined.streams[1].ready==3)
''')

    def test_wrap_recovery_uses_all_foreign_contributors_and_exact_city_intervals(self):
        self.vm().execute('''
local a,b=endpoint(1,1),endpoint(2,2);bakery(b);paid(a,'BAKERS_BAKERY','ORIGIN',32)
local routes={};for i=1,32 do
 routes[i]={origin='1:1',destination='2:2',observedThrough=i==32 and 4 or 10}
end
local t=trade({['1:1']=a,['2:2']=b},routes)
local r=assert(M.JointForecast(world(t),price))
assert(r.valueQ8==0 and #r.streams==0) -- Coverage ends; no physical removal is known.
routes[32].removedAt=4
r=assert(M.JointForecast(world(t),price))
assert(r.valueQ8==62*6*256)
local amenities=0
for _,s in ipairs(r.streams)do
 assert(s.player==1 and s.ready==4 and s.finish==10)
 if s.yield=='AMENITY'then amenities=amenities+s.amount;assert(s.amount==31)end
end
assert(amenities==31)
''')

    def test_coverage_cutoff_does_not_invent_an_amenity_loss_or_distort_later_investments(self):
        self.vm().execute('''
local a,b=endpoint(1,1),endpoint(2,2);bakery(b);paid(a,'BAKERS_BAKERY','ORIGIN',1)
local t=trade({['1:1']=a,['2:2']=b},{{origin='1:1',destination='2:2',observedThrough=1}})
local ordinary={id='newCafe',player=1,city=1,yield='AMENITY',amount=1,ready=3}
local result={streams={ordinary},byBuilding={}}
assert(M.RouteLedger(result,t,1,10))
local amenities=0
for _,s in ipairs(result.streams)do if s.yield=='AMENITY'then
 amenities=amenities+1;assert(s.amount==1 and s.ready==3 and s.finish==10)
end end
assert(amenities==1) -- No -1 route-loss interval after its one-turn coverage.
local nativeCalls=0
local v=assert(M.Price(result,function(s,h)
 if s.yield~='AMENITY'then return 0 end
 nativeCalls=nativeCalls+1;assert(s.amount==1 and s.ready==3);return 777
end,10))
assert(v==777 and nativeCalls==1)
''')

    def test_marginal_worlds_must_share_actual_paid_counts_and_observation(self):
        self.vm().execute('''
local a,b=endpoint(1,1),endpoint(2,2);bakery(b)
local t=trade({['1:1']=a,['2:2']=b},{{origin='1:1',destination='2:2',observedThrough=10}})
local other=trade(t.observed.cities,t.observed.routes)
local quote,error=M.JointCustomerForecast(world(t),world(other),price)
assert(quote==nil and error=='Marginal trade observations differ')
other.observed=t.observed
assert(M.JointCustomerForecast(world(t),world(other),price).valueQ8==0)
local after=world(other);after.player=2
assert(M.JointCustomerForecast(world(t),after,price)==nil)
''')

    def test_foreign_origins_pay_local_export_once_without_pricing_foreign_receipts(self):
        self.vm().execute('''
local a,b,c=endpoint(2,1),endpoint(1,2),endpoint(3,1);bakery(b)
local routes={{origin='2:1',destination='1:2',observedThrough=10},
 {origin='3:1',destination='1:2',observedThrough=10}}
local r=assert(M.JointForecast(world(trade({['2:1']=a,['1:2']=b,['3:1']=c},routes)),price))
assert(r.valueQ8==4*10*256 and r.routeSegments==2)
for _,s in ipairs(r.streams)do assert(s.city==2 and s.player==1
 and(s.yield=='YIELD_PRODUCTION'or s.yield=='YIELD_GOLD'))end
''')

    def test_selected_producer_completion_enables_exports_only_inside_observed_window(self):
        self.vm().execute('''
for _,finish in ipairs({4,10})do
 local a,b=endpoint(2,1),endpoint(1,2)
 local t=trade({['2:1']=a,['1:2']=b},{{origin='2:1',destination='1:2',observedThrough=finish}})
 local channel=D.byId.BAKERS_BAKERY
 t.plannedChanges={
  {city='1:2',field='buildings',key=channel.producer,value=true,investmentKey='1:2:'..channel.producer},
  {city='1:2',field='properties',key=channel.supplyProperty,value=1,investmentKey='1:2:'..channel.producer}}
 local r=assert(M.JointForecast(world(t,{chain()}),price))
 if finish==4 then assert(r.valueQ8==0 and r.routeSegments==0)
 else
  assert(r.valueQ8==2*5*256 and r.byBuilding['1:2:'..channel.producer]==5)
  for _,s in ipairs(r.streams)do if s.id:find('route:',1,true)then assert(s.ready==5 and s.finish==10)end end
 end
 assert(b.properties[channel.supplyProperty]==nil and b.buildings[channel.producer]==nil)
end
''')

    def test_paid_count_baseline_is_independent_of_pending_observed_route_counts(self):
        self.vm().execute('''
local a,b=endpoint(1,1),endpoint(2,2);bakery(b);paid(a,'BAKERS_BAKERY','ORIGIN',1)
local cities={['1:1']=a,['2:2']=b}
assert(R.PaidAmenities(cities,D,1)['1:1']==1)
local t=trade(cities,{{origin='1:1',destination='2:2',observedThrough=10},
 {origin='1:1',destination='2:2',observedThrough=10}})
local r=assert(M.JointForecast(world(t),price));local n=0
for _,s in ipairs(r.streams)do if s.yield=='AMENITY'then n=n+1;assert(s.amount==1)end end
assert(n==1)
a.counts[D.byId.BAKERS_BAKERY.importProperty]=nil
assert(M.JointForecast(world(t),price)==nil)
''')

    def test_api_magnitude_limit_returns_unavailable_without_splitting_or_clipping(self):
        self.vm().execute('''
local a,b=endpoint(1,1),endpoint(2,2);bakery(b)
local routes={};for i=1,9 do routes[i]={origin='1:1',destination='2:2',observedThrough=10}end
local calls=0
local function bounded(s,h)
 if s.yield=='AMENITY'then calls=calls+1;if math.abs(s.amount)>8 then return nil end end
 return price(s,h)
end
local r,error=M.JointForecast(world(trade({['1:1']=a,['2:2']=b},routes)),bounded)
assert(r==nil and error:find('Native price unavailable',1,true)and calls==1)
''')


if __name__=='__main__':unittest.main()
