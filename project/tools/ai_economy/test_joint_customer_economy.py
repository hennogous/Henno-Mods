"""Shared economic invariants, exercising production Lua without native mocks."""
from pathlib import Path
import unittest
from lupa.lua51 import LuaRuntime

MODEL=Path(__file__).resolve().parents[3]/'Civ Supply Chains/Lua_UI/AI/CSC_AI_EconomyModel.lua'


class JointEconomy(unittest.TestCase):
    def vm(self):
        vm=LuaRuntime(unpack_returned_tuples=True)
        vm.execute(MODEL.read_text(encoding='utf-8'))
        vm.execute('''
M=CSC_AI_EconomyModel
function price(s,h)return math.floor(s.amount*(h-s.ready)*256+.000001)end
function chain(key,city)
 return {key=key,player=1,city=city,population=9,horizon=30,quarterReady=0,existing=true,
  materialYield='YIELD_FOOD',seconds={{type='MILL',working=true}},
  third={type='BAKERY',working=true},customers={},suppliers={},direct={}}
end
function venue(plot,city)
 return {type='MARKET',building=5,plot=plot,city=city,population=9,stage=3,complete=true,
  unlock=0,turns=2,maintenance=2,forecastDepth=1,
  prerequisites={{type='PRE',unlock=0,turns=1,maintenance=1}},
  transaction={id='BUY',kind='PARTNER_POPULATION',amount=.099,legs={
   {key='P',recipient='SOURCE',yield='YIELD_PRODUCTION',amount=1,property='seller'},
   {key='G',recipient='SOURCE',yield='YIELD_GOLD',amount=1,property='seller'},
   {key='R',recipient='PARTNER',yield='YIELD_FOOD',amount=1,property='buyer'}}}}
end
function world(sites)return{horizon=30,sites=sites}end
function copy(v)local r={};for k,x in pairs(v)do r[k]=x end;return r end
''')
        return vm

    def test_shared_market_and_prerequisite_are_built_once_and_round_once(self):
        self.vm().execute('''
local a,b=chain('A',1),chain('B',2)
a.customers={venue(100,3)};b.customers={venue(100,3)}
local r=assert(M.JointForecast(world({a,b}),price))
assert(#r.investments==2)
assert(r.byBuilding['1:3:PRE']==1 and r.byBuilding['1:3:MARKET']==3)
local food,upkeep=0,0
for _,s in ipairs(r.streams)do
 if s.yield=='YIELD_FOOD' and s.city==3 then
  food=food+s.amount;assert(s.ready==3 and #s.contributors==2 and s.building==nil)
 end
 if s.id:find('upkeep:',1,true)then upkeep=upkeep+s.amount end
end
assert(food==M.PopulationPayout(2*.099*9,9))
assert(food<2*M.PopulationPayout(.099*9,9))
assert(upkeep==-3)
assert(r.servicesExcluded and r.modelOnly)
''')

    def test_input_order_cannot_change_joint_schedule_or_value(self):
        self.vm().execute('''
local a,b=chain('A',1),chain('B',1)
a.third={type='BAKERY',unlock=0,turns=4}
b.third={type='TAILOR',unlock=0,turns=5}
a.customers={venue(100,1)};b.customers={venue(100,1)}
for _,s in ipairs({a,b})do s.customers[1].maintenance=0;s.customers[1].prerequisites[1].maintenance=0 end
local first=assert(M.JointForecast(world({a,b}),price))
local reverse=assert(M.JointForecast(world({b,a}),price))
assert(first.valueQ8==reverse.valueQ8)
assert(first.byBuilding['1:1:MARKET']==reverse.byBuilding['1:1:MARKET'])
assert(first.byBuilding['1:1:BAKERY']~=first.byBuilding['1:1:TAILOR'])
local n=0;for _,v in ipairs(first.investments)do if v.type=='MARKET'then n=n+1 end end
assert(n==1)
''')

    def test_building_depth_uses_owner_and_city_identity(self):
        self.vm().execute('''
local a,b=chain('A',1),chain('B',2)
b.third={type='BAKERY',unlock=0,turns=2,forecastDepth=3}
a.customers={venue(100,3)};b.customers={venue(101,4)}
local r=assert(M.JointForecast(world({a,b}),price))
assert(r.futureDepths['1:1:BAKERY']==nil and r.futureDepths['1:2:BAKERY']==3)
local observed=false
for _,s in ipairs(r.streams)do
 if s.id:find('A/local-production:3',1,true)then assert(s.forecastDepth==nil)end
 if s.id:find('B/local-production:3',1,true)then
  assert(s.forecastDepth==3 and s.investmentKey=='1:2:BAKERY');observed=true
 end
end
assert(observed)
''')

    def test_candidate_reserves_queue_only_after_and_services_stay_excluded(self):
        self.vm().execute('''
local a=chain('A',1)
a.third={type='BAKERY',unlock=0,turns=4}
a.customers={venue(100,2)}
a.service={kind='GROWTH',amount=999999,unlock=0}
local before=world({a});local after=world({a});after.queueReady={['1:1']=5}
local q=assert(M.JointCustomerForecast(before,after,price))
assert(q.before.byBuilding['1:1:BAKERY']==4)
assert(q.after.byBuilding['1:1:BAKERY']==9 and q.valueQ8<0)
for _,r in ipairs({q.before,q.after})do for _,s in ipairs(r.streams)do assert(s.yield~='GROWTH')end end
assert(a.service.amount==999999 and a.third.unlock==0)
''')

    def test_population_pool_records_multiple_completion_events(self):
        self.vm().execute('''
local a,b=chain('A',1),chain('B',2)
a.customers={venue(100,3)};b.customers={venue(101,3)}
b.customers[1].type='TEMPLE';b.customers[1].turns=4
local r=assert(M.JointForecast(world({a,b}),price))
local events,total=0,0
for _,s in ipairs(r.streams)do if s.yield=='YIELD_FOOD' and s.city==3 then
 events=events+1;total=total+s.amount
 if events==1 then assert(s.ready==3 and #s.contributors==1)end
 if events==2 then assert(s.ready==7 and #s.contributors==2)end
end end
assert(events==2 and total==M.PopulationPayout(2*.099*9,9))
''')

    def test_work_budget_and_incomplete_world_return_unavailable(self):
        self.vm().execute('''
local a=chain('A',1)
 a.customers={venue(100,3)} -- A real optional decision must exceed the one-evaluation budget.
local w=world({a});w.maxEvaluations=1
local r,why=M.JointForecast(w,price);assert(r==nil and why=='Joint evaluation budget exceeded')
r,why=M.JointForecast(world({a,a}),price);assert(r==nil and why=='Missing or duplicate chain identity')
r,why=M.JointForecast(world({a}),function()return nil end);assert(r==nil and why)
''')

    def test_unchanged_sweep_still_charges_the_full_logical_budget(self):
        self.vm().execute('''
local a=chain('A',1)
a.customers={venue(100,3)};a.customers[1].maintenance=1000
local w=world({a});w.maxEvaluations=6
local q=assert(M.JointForecast(w,price))
assert(q.evaluations==6 and q.disabledBuildings['1:3:MARKET'])
w.maxEvaluations=5
local r,reason=M.JointForecast(w,price)
assert(r==nil and reason=='Joint evaluation budget exceeded')
''')

    def test_frozen_identity_world_reproduces_baseline_in_one_evaluation(self):
        self.vm().execute('''
local a,b=chain('A',1),chain('B',2)
a.third={type='BAKERY',unlock=0,turns=3}
local base=assert(M.JointForecast(world({a,b}),price))
local w=world({a,b});w.baselinePlan=base.plan;w.affectedChains={}
local frozen=assert(M.JointForecast(w,price))
assert(frozen.evaluations==1 and frozen.valueQ8==base.valueQ8)
assert(frozen.byBuilding['1:1:BAKERY']==base.byBuilding['1:1:BAKERY'])
w.queueReady={['1:1']=7}
local delayed=assert(M.JointForecast(w,price))
assert(delayed.evaluations==1 and delayed.byBuilding['1:1:BAKERY']==10)
assert(delayed.valueQ8<base.valueQ8)
''')

    def test_new_customer_unfreezes_affected_producers_and_shared_customer_peers(self):
        self.vm().execute('''
local a,b=chain('A',1),chain('B',2)
for _,s in ipairs({a,b})do s.third={type='BAKERY',unlock=0,turns=1,localTransactions={}} end
local base=assert(M.JointForecast(world({a,b}),price))
assert(base.plan.chains.A.third==nil and base.plan.chains.B.third==nil)
local aa,bb=copy(a),copy(b)
for _,s in ipairs({aa,bb})do
 s.customers={venue(100,3)}
 local v=s.customers[1];v.maintenance=3;v.turns=1;v.prerequisites={}
end
local w=world({aa,bb});w.baselinePlan=base.plan;w.affectedChains={A=true}
local opened=assert(M.JointForecast(w,price))
assert(opened.valueQ8>0 and #opened.investments==3)
assert(opened.byBuilding['1:1:BAKERY']==1 and opened.byBuilding['1:2:BAKERY']==1)
assert(opened.byBuilding['1:3:MARKET']==1)
assert(base.plan.chains.A.third==nil and next(base.plan.disabledBuildings)==nil)
''')

    def test_jointly_profitable_producers_can_cover_one_shared_customer(self):
        self.vm().execute('''
local a,b=chain('A',1),chain('B',2)
for _,s in ipairs({a,b})do
 s.third={type='BAKERY',unlock=0,turns=1,localTransactions={}}
 s.customers={venue(100,3)}
 local v=s.customers[1];v.maintenance=3;v.turns=1;v.prerequisites={}
 assert(M.Forecast(s,price).valueQ8==0) -- Each separate project loses.
end
local joint=assert(M.JointForecast(world({a,b}),price))
assert(joint.valueQ8>0 and #joint.investments==3)
assert(joint.byBuilding['1:1:BAKERY']==1 and joint.byBuilding['1:2:BAKERY']==1)
assert(joint.byBuilding['1:3:MARKET']==1)
''')

    def test_shared_customer_cannot_serve_only_the_chain_that_scheduled_it(self):
        self.vm().execute('''
local a,b=chain('A',1),chain('B',2)
a.fourth={type='CAFE',unlock=0,turns=1}
a.customers={venue(100,1)};b.customers={venue(100,1)}
for _,s in ipairs({a,b})do
 local v=s.customers[1];v.turns=10;v.maintenance=0;v.prerequisites={}
end
local joint=assert(M.JointForecast(world({a,b}),price))
assert(joint.byBuilding['1:1:MARKET']==10)
local sellers={}
for _,s in ipairs(joint.streams)do
 if s.id:find(':YIELD_PRODUCTION:seller:',1,true)then sellers[s.city]=true end
end
assert(sellers[1] and sellers[2]) -- Automatic links are physical, not optional.
assert(#a.customers==1 and #b.customers==1)
''')

    def test_contradictory_shared_buildings_and_missing_owners_are_unavailable(self):
        self.vm().execute('''
local a,b=chain('A',1),chain('B',2)
a.customers={venue(100,3)};b.customers={venue(100,3)}
b.customers[1].turns=3
local r,why=M.JointForecast(world({a,b}),price)
assert(r==nil and why=='Conflicting shared investment: 1:3:MARKET')
b.customers[1].turns=2;a.player=nil
r,why=M.JointForecast(world({a,b}),price)
assert(r==nil and why=='Explicit chain owner required')
''')

    def test_contradictory_population_pool_returns_unavailable_without_throwing(self):
        self.vm().execute('''
local a,b=chain('A',1),chain('B',2)
a.customers={venue(100,3)};b.customers={venue(101,3)}
b.customers[1].type='TEMPLE';b.customers[1].population=10
local r,why=M.JointForecast(world({a,b}),price)
assert(r==nil and why:find('Inconsistent shared population contract:',1,true))
''')

    def test_same_city_id_for_different_players_has_separate_buildings_and_pools(self):
        self.vm().execute('''
local a,b=chain('A',1),chain('B',1);b.player=2
a.customers={venue(100,3)};b.customers={venue(101,3)}
for _,s in ipairs({a,b})do s.customers[1].maintenance=0;s.customers[1].prerequisites[1].maintenance=0 end
local r=assert(M.JointForecast(world({a,b}),price))
assert(#r.investments==4)
assert(r.byBuilding['1:3:MARKET']==3 and r.byBuilding['2:3:MARKET']==3)
local recipients={}
for _,s in ipairs(r.streams)do if s.yield=='YIELD_FOOD' and s.city==3 then recipients[s.player]=true end end
assert(recipients[1]and recipients[2])
''')


if __name__=='__main__':unittest.main()
