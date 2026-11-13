"""Economic invariants with real Lua5.1; no Civ/native decisions simulated."""
from pathlib import Path
import unittest
from lupa.lua51 import LuaRuntime

ROOT=Path(__file__).resolve().parents[3]
MODEL=ROOT/'Civ Supply Chains/Lua_UI/AI/CSC_AI_EconomyModel.lua'


class EconomyModel(unittest.TestCase):
    def vm(self):
        vm=LuaRuntime(unpack_returned_tuples=True)
        vm.execute(MODEL.read_text(encoding='utf-8'))
        vm.execute('''
M=CSC_AI_EconomyModel
function price(s,h) return math.floor(s.amount*(h-s.ready)*256) end
function site()
 return {city=10,population=10,horizon=50,quarterReady=2,maintenance=1,
  materialYield='YIELD_FOOD',direct={},suppliers={},customers={},
  seconds={{type='Wind',unlock=0,turns=3,cost=40,maintenance=0,terrain=1}}}
end
function find(r,id)for _,s in ipairs(r.streams)do if s.id==id then return s end end end
''')
        return vm

    def test_supplier_improvement_yields_require_an_observed_worker(self):
        self.vm().execute('''
local s=site();s.suppliers={{kind='base',plot=99,city=10,ready=8,worked=false}}
local a=M.Forecast(s,price)
assert(find(a,'material-input:base:99').ready==8)
assert(not find(a,'material-production:base:99'))
s.suppliers[1].worked=true
local b=M.Forecast(s,price)
assert(b.valueQ8-a.valueQ8==2*(50-8)*256)
''')

    def test_unbuilt_customer_district_has_no_sale_even_with_ready_building(self):
        self.vm().execute('''
local s=site();s.customers={{stage=2,plot=8,city=11,complete=false,ready=0}}
assert(not find(M.Forecast(s,price),'sale-gold:8:2:nil'))
s.customers[1].complete=true
local r=M.Forecast(s,price)
assert(find(r,'sale-gold:8:2:nil').ready==5)
assert(find(r,'sale-return:8:2:nil').city==11)
''')

    def test_mutually_exclusive_mills_never_stack(self):
        self.vm().execute('''
local s=site();s.seconds[2]={type='Water',unlock=0,turns=3,terrain=3,maintenance=2}
local r=M.Forecast(s,price)
assert(r.alternative=='Water' and find(r,'producer-terrain').amount==3)
local n=0;for _,v in ipairs(r.investments)do if v.type=='Water'or v.type=='Wind'then n=n+1 end end
assert(n==1)
''')

    def test_same_city_customer_construction_is_not_parallel_production(self):
        self.vm().execute('''
local s=site();s.customers={{stage=2,plot=8,city=10,complete=true,
 ready=4,unlock=0,turns=4}}
assert(find(M.Forecast(s,price),'sale-gold:8:2:nil').ready==9)
''')

    def test_missing_producer_unlock_cannot_create_fictitious_transactions(self):
        self.vm().execute('''
local s=site();s.seconds[1].unlock=nil
s.suppliers={{kind='base',plot=1,ready=0,worked=true}}
local r=M.Forecast(s,price)
assert(not find(r,'material-input:base:1') and r.alternative==nil)
''')

    def test_later_producer_uses_one_selected_stage_two_recipient(self):
        self.vm().execute('''
local s=site();s.third={type='Bakery',unlock=0,turns=4,maintenance=2}
local r=M.Forecast(s,price)
assert(find(r,'local-production:3').ready==9)
assert(find(r,'local-return:3').amount==1)
local delta=M.Marginal(s,'Bakery',price)
assert(delta>0)
''')

    def test_population_returns_round_per_receiving_city_and_stage_four_per_venue(self):
        self.vm().execute('''
assert(M.PopulationPayout(1.01,10)==1.015625)
local s=site();s.third={type='Bakery',unlock=0,turns=1}
s.fourth={type='Cafe',unlock=0,turns=1}
s.customers={{stage=3,plot=8,city=11,population=10,rate=.101,complete=true,ready=0},
 {stage=4,plot=9,city=12,population=14,complete=true,ready=0,yield='YIELD_CULTURE'}}
local r=M.Forecast(s,price)
assert(find(r,'population:10:YIELD_PRODUCTION:sale-production:6').amount==1.015625)
assert(find(r,'sale-gold:9:4:nil').amount==2)
''')

    def test_unavailable_price_is_not_zero_or_a_publishable_bid(self):
        self.vm().execute('''
local s=site();local r,why=M.Forecast(s,function()return nil end)
assert(r==nil and why:find('price unavailable'))
''')

    def test_unprofitable_optional_later_stage_does_not_reduce_quarter_value(self):
        self.vm().execute('''
local s=site();local before=M.Forecast(s,price).valueQ8
s.fourth={type='Cafe',unlock=0,turns=2,maintenance=100}
assert(M.Forecast(s,price).valueQ8==before)
''')

    def test_customer_prerequisite_and_producers_share_one_queue(self):
        self.vm().execute('''
local s=site();s.third={type='Bakery',unlock=0,turns=2,maintenance=0}
s.customers={{type='Granary',building='Granary',stage=2,plot=8,city=10,complete=true,
 working=false,unlock=0,turns=4,rates={production=20,gold=20,outward=20}},
 {type='Zoo',building='Zoo',stage=3,plot=9,city=10,complete=true,working=false,
 unlock=0,turns=2,rate=1,population=10,prerequisites={{type='Arena',unlock=0,turns=3}}}}
local r=M.Forecast(s,price)
assert(r.byBuilding['10:Wind']==5 and r.byBuilding['10:Granary']==9)
assert(r.byBuilding['10:Bakery']==11 and r.byBuilding['10:Arena']==14 and r.byBuilding['10:Zoo']==16)
''')

    def test_population_rounding_aggregates_by_actual_property(self):
        self.vm().execute('''
local s=site();s.third={type='Bakery',working=true}
for i=1,7 do s.customers[i]={stage=3,plot=i,city=11,population=10,
 rate=.101,complete=true,ready=0,working=true,sellerProperty='SELL',customerProperty='BUY'..i}end
local r=M.Forecast(s,price)
local seller=find(r,'population:10:YIELD_PRODUCTION:SELL:0')
assert(seller.amount==M.PopulationPayout(7.07,10))
local total=0
for _,flow in ipairs(r.streams)do if flow.id:find('population:11:YIELD_FOOD:BUY',1,true)then total=total+flow.amount end end
assert(total==7*M.PopulationPayout(1.01,10) and total>seller.amount)
''')

    def test_new_customer_flow_prices_only_increment_after_existing_seller_rounding(self):
        self.vm().execute('''
local s=site();s.third={type='Bakery',working=true}
s.customers={{stage=3,plot=8,city=11,population=10,rate=.101,complete=true,
 ready=0,working=true,sellerProperty='SELL',customerProperty='BUY'}}
s.populationBaselines={['11:YIELD_FOOD:BUY']=6.06}
local r=M.Forecast(s,price)
assert(find(r,'population:11:YIELD_FOOD:BUY:0').amount==
 M.PopulationPayout(7.07,10)-M.PopulationPayout(6.06,10))
''')

    def test_supplier_removal_prices_transactions_and_resource_adjacency_loss(self):
        vm=self.vm()
        vm.execute('''
CSC_AI_EconomyFacts={}
local s=site();s.existing=true;s.quarterReady=0
s.seconds={{type='Wind',working=true}}
s.direct={{id='YIELD_PRODUCTION',yield='YIELD_PRODUCTION',amount=1}}
s.suppliers={{kind='base',plot=99,city=10,ready=0,worked=true}}
snapshot={Price=price,SupplyAdjacencyLoss=function()return{YIELD_PRODUCTION=1}end}
chain={economy=s}
''')
        vm.execute((MODEL.parent/'CSC_AI_EconomyAdapters.lua').read_text(encoding='utf-8'))
        vm.execute("assert(CSC_AI_EconomyAdapters.SupplyValue(snapshot,chain,99)==4*50*256)")

    def test_fixed_purchase_is_a_single_invoice(self):
        self.vm().execute('''
local s=site();s.purchaseGold=70
local seen=false
local r=M.Forecast(s,function(flow,h)
 if flow.id=='footprint-purchase'then assert(flow.fixed==true and flow.amount==-70 and flow.ready==0);seen=true;return -70*256 end
 return price(flow,h)
end)
assert(r and seen)
''')

    def test_forecasting_does_not_mutate_customer_facts(self):
        self.vm().execute('''
local s=site();local customer={stage=2,plot=1,city=10,complete=true,ready=0,unlock=0,turns=1}
s.customers={customer};M.Forecast(s,price)
assert(customer.modelReady==nil)
''')


if __name__=='__main__':unittest.main()
