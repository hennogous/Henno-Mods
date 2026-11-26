"""Compare complete candidate forecasts with and without independent-chain reuse."""
from pathlib import Path
import sys
import unittest

import test_joint_customer_economy as economy

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS/'transactions'))
sys.path.insert(0, str(TOOLS/'native_ai/late_placement'))
import customer_world_fixture
import test_joint_route_economy as routes


# Include field order in arrays (streams, investments, contributors) and both
# returned values for failed quotes. Table identity itself is private to Lua.
COMPARE = '''
function same(a,b,path)
 if type(a)~='table' then assert(a==b,path);return end
 assert(type(b)=='table',path)
 for k,v in pairs(a)do same(v,b[k],path..'/'..tostring(k))end
 for k in pairs(b)do assert(a[k]~=nil,path..'/'..tostring(k))end
end
function compare(w,memo)
 local expected,message=M.JointForecast(w,price)
 local got,problem=M.JointForecast(w,price,memo)
 same(expected,got,'forecast');assert(message==problem)
 return got,problem
end
'''


class IndependentChains(unittest.TestCase):
    def test_live_adapters_reuse_distant_sites_for_quarters_and_customers(self):
        for city_lights in (False, True):
            with self.subTest(city_lights=city_lights):
                vm = customer_world_fixture.world(city_lights=city_lights)
                vm.execute((customer_world_fixture.MOD/'Lua_UI/AI/CSC_AI_EconomyAdapters.lua').read_text())
                vm.execute(COMPARE)
                vm.execute('''
local E,M=CSC_AI_EconomyAdapters,CSC_AI_EconomyModel
E.Available=function()return true end
local target=plot(9,1,-2,3)
local s=assert(E.Snapshot(player,placement,ui));s.Price=price
local actual=M.JointForecast
local counts={}
M.JointForecast=function(w,p,memo)
 if not memo then return actual(w,p)end
 local expected=assert(actual(w,p))
 local result=assert(actual(w,p,memo))
 same(expected,result,'adapter')
 local count=0
 for _,entry in pairs(memo)do if type(entry)=='table'then count=count+1 end end
 counts[#counts+1]=count
 return result
end
local site=assert(s.Site(CITIES[3],target,profile))
assert(E.QuarterForecast(s,CITIES[3],target,profile,site,0,false))
local _,customer=s.CustomerWorld(3,GameInfo.Districts.DISTRICT_COMMERCIAL_HUB.Index,9)
assert(s.WorldQuote(customer))
s.serviceKinds={GROWTH=true}
assert(E.QuarterForecast(s,CITIES[3],target,profile,site,0,false))
assert(#counts==3 and math.min(unpack(counts))>=1)
''')

    def test_warm_results_stay_exact_across_candidate_changes(self):
        vm = economy.JointEconomy().vm()
        vm.execute(COMPARE)
        vm.execute('''
local function buyer(plot,city)
 local v=venue(plot,city);v.maintenance=0;v.prerequisites[1].maintenance=0
 return v
end
local fixed=chain('fixed',2)
fixed.customers={buyer(92,2)}
fixed.omissions={'fixture coverage'}
fixed.suppliers={{kind='base',plot=19,city=2,ready=0,worked=true}}
local base=assert(M.JointForecast(world({fixed}),price))
local candidate=chain('candidate',1)
candidate.customers={buyer(35,1)}
local w=world({candidate,fixed})
w.baselinePlan=base.plan;w.affectedChains={candidate=true}
w.firstChainKey='candidate'
local memo={[fixed]=true}
local first=assert(compare(w,memo));assert(type(memo[fixed])=='table')
-- Returned plans and diagnostics belong to the caller. An inspection or
-- annotation of one quote cannot change the next candidate's inputs.
first.chainStages.fixed.ready[2]=100
for _,row in ipairs(first.investments)do row.cost=-100 end
for _,row in ipairs(first.omissions)do row.reason='annotated' end
for _,row in ipairs(first.streams)do row.ready=100 end
assert(compare(w,memo))
candidate.purchaseGold=25
local bought=assert(compare(w,memo));assert(bought.valueQ8~=first.valueQ8)
w.populationBaselines={['1:2:YIELD_FOOD:buyer']=1.7}
assert(compare(w,memo))
w.queueReady={['1:2']=8}
local delayed=assert(compare(w,memo));assert(delayed.byBuilding['1:2:MARKET']>=8)
w.queueReady=nil
candidate.customers={buyer(92,2)}
local linked=assert(compare(w,memo))
for _,s in ipairs(linked.streams)do
 if s.city==2 and s.yield=='YIELD_FOOD' and s.contributors then assert(#s.contributors==2)end
end
candidate.customers={}
local damaged=copy(fixed);damaged.suppliers={}
w.sites={candidate,damaged};w.affectedChains.fixed=true
local lost=assert(compare(w,memo));assert(memo[damaged]==nil)
w.sites={candidate,fixed};w.affectedChains.fixed=nil
local restored=assert(compare(w,memo));assert(restored.valueQ8>lost.valueQ8)
w.maxEvaluations=0
local result,reason=compare(w,memo);assert(not result and reason:find('budget'))
''')

    def test_pooled_housing_and_amenities_follow_changes_to_the_other_chain(self):
        vm = economy.JointEconomy().vm()
        vm.execute(COMPARE)
        vm.execute('''
local function producer(key,city)
 local site=chain(key,city)
 local buyer=venue(90+city,city);buyer.working=true
 site.customers={buyer}
 site.services={{id='housing',stage=3,producer='BAKERY',known=true,kind='HOUSING',
   amount=1,city=3,customer=buyer,unlock=0}}
 site.direct={{id='amenity',city=3,amount=1,ready=0,yield='AMENITY'}}
 return site
end
local a,b=producer('fixed',1),producer('candidate',2)
local base=world({a});base.includeServices=true
local w=world({a,b});w.includeServices=true
w.serviceHousing={cities={[3]={active=0,left=0,food=4}},activeCities={},stop=-4,quarter=0,half=1}
base.serviceHousing=w.serviceHousing
w.baselinePlan=assert(M.JointForecast(base,price)).plan;w.affectedChains={candidate=true}
local memo={[a]=true}
local r=assert(compare(w,memo));assert(type(memo[a])=='table' and r.serviceValueQ8>0)
b.services={};b.direct={}
local changed=assert(compare(w,memo));assert(changed.serviceValueQ8<r.serviceValueQ8)
''')

    def test_other_quarter_construction_sets_the_start_of_a_displaced_yield(self):
        vm = economy.JointEconomy().vm()
        vm.execute(COMPARE)
        vm.execute('''
local fixed,candidate=chain('fixed',2),chain('candidate',1)
fixed.direct={{id='displaced:plot',city=2,yield='YIELD_FOOD',amount=-1,quarterStartKey='candidate'}}
local w=world({fixed,candidate})
w.baselinePlan=assert(M.JointForecast(world({fixed}),price)).plan
w.firstChainKey='candidate';w.affectedChains={candidate=true}
candidate.quarterWork={turns=3,unlock=0}
local memo={[fixed]=true}
local immediate=assert(compare(w,memo))
w.queueReady={['1:1']=6}
local later=assert(compare(w,memo))
assert(memo[fixed]==true and later.valueQ8>immediate.valueQ8)
''')

    def test_route_loss_and_restoration_are_repriced_with_a_warm_chain(self):
        vm = routes.JointRoutes().vm()
        vm.execute(COMPARE)
        vm.execute('''
local origin,destination=endpoint(1,1),endpoint(2,2)
bakery(destination);paid(origin,'BAKERS_BAKERY','ORIGIN',1)
local t=trade({['1:1']=origin,['2:2']=destination},{{origin='1:1',destination='2:2',observedThrough=5}})
local fixed=chain();fixed.direct={{id='food',yield='YIELD_FOOD',amount=1,ready=0}}
local w=world(t,{fixed})
w.baselinePlan=assert(M.JointForecast(w,price)).plan
local memo={[fixed]=true}
local original=assert(compare(w,memo));assert(type(memo[fixed])=='table')
t.changes={{ready=0,city='1:1',field='quarters',key='DISTRICT_CSC_BAKERS_QUARTER',value=true}}
local lost=assert(compare(w,memo));assert(lost.valueQ8<original.valueQ8)
t.changes[2]={ready=2,city='1:1',field='quarters',key='DISTRICT_CSC_BAKERS_QUARTER',value=nil}
assert(assert(compare(w,memo)).valueQ8>lost.valueQ8)
''')
