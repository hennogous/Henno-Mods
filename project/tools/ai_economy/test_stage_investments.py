"""Later-stage bids exercise the shipping adapters and shared Lua ledger."""
import unittest

import test_joint_customer_economy as joint_fixtures


class StageInvestments(unittest.TestCase):
    def vm(self):
        vm = joint_fixtures.JointEconomy().vm()
        vm.execute((joint_fixtures.MODEL.parent / 'CSC_AI_EconomyAdapters.lua').read_text(encoding='utf-8'))
        vm.execute('''
E=CSC_AI_EconomyAdapters
GameInfo={Buildings={
 BAKERY={Hash=51,Index=5,PrereqTech='SHOP'},
 FASHION={Hash=61,Index=6,PrereqCivic='OPERA'},
 UNIQUE_MARKET={Hash=71,Index=7}}}
function snapshot(sites)
 local s={id=1,chains={},Price=price,locked={},legal={},prerequisites=true,chargeCost=1}
 for _,site in ipairs(sites)do
  s.chains[#s.chains+1]={ready=true,city=site.city,economy=site,supply=site.supply}
 end
 s.ui={CanProduceItem=function(player,city,hash)return player==1 and s.legal[city..':'..hash]==true end}
 s.UnownedResearch=function(kind,topic)return s.locked[topic]end
 s.MaterialBuyerPrerequisitesMet=function()return s.prerequisites end
 s.MaterialBuyerCommitment=function()return s.committed end
 s.SupplierChargeCost=function()return s.chargeCost end
 return s
end
function offers(snapshot)
 local research,production={},{}
 E.LaterStageInvestments(snapshot,research,production,64*256)
 return research,production
end
function shop(city,pop)
 local a=chain('A'..city,city)
 a.population=pop
 a.third={type='BAKERY',unlock=0,turns=3,localTransactions={}}
 local market=venue(100,3);market.working=true
 a.customers={market}
 return a
end
function fashion(city,pop)
 local a=chain('T'..city,city)
 a.population=pop
 a.fourth={type='FASHION',unlock=0,turns=4}
 local theater=venue(100,3)
 theater.stage=4;theater.working=true;theater.population=12
 theater.transaction.kind='PARTNER_POPULATION_STEPS'
 theater.transaction.step=5;theater.transaction.amount=1
 a.customers={theater}
 a.supply={base={{plot=10,working=true,ready=true}},specialty={{plot=11,ready=true}}}
 a.suppliers={{kind='base',plot=10,ready=0},{kind='specialty',plot=11,ready=8}}
 return a
end
''')
        return vm

    def test_producer_population_gates_and_live_production_eligibility(self):
        self.vm().execute('''
local a=shop(1,6);local s=snapshot({a});s.locked.SHOP=42
local r,b=offers(s);assert(not next(r) and #b==0)
a.population=7;r,b=offers(s);assert(r['tech:42'].producerQ8>0 and #b==0)
s.prerequisites=false;r,b=offers(s);assert(not next(r) and #b==0)
s.prerequisites=true;s.locked.SHOP=nil;s.legal['1:51']=true
a.population=9;r,b=offers(s);assert(not next(r) and #b==0)
a.population=10;r,b=offers(s);assert(not next(r) and #b==1 and b[1].building==5 and b[1].delta>0)
s.committed=true;r,b=offers(s);assert(not next(r) and #b==0)
s.committed=nil;a.third.present=true;r,b=offers(s);assert(not next(r) and #b==0)
''')

    def test_research_pools_distinct_cities_once_and_preserves_existing_credit(self):
        self.vm().execute('''
local a,b=shop(1,7),shop(2,7)
local s=snapshot({a,b});s.locked.SHOP=42
local research={['tech:42']={value=13,jobs={{plot=49}},serviceQ8=13}}
E.LaterStageInvestments(s,research,{},0)
local q=research['tech:42'];assert(q.value==13+q.producerQ8 and q.producerQ8>0)
assert(q.producerQ8==q.producerCities[1]+q.producerCities[2] and #q.jobs==1)
local first=q.value
E.LaterStageInvestments(s,research,{},0)
assert(q.value==first)
''')

    def test_unique_customer_pools_two_present_producers_before_rounding(self):
        self.vm().execute('''
local a,b=chain('A',1),chain('B',2)
local customer=venue(100,3)
customer.type='UNIQUE_MARKET';customer.building='UNIQUE_MARKET';customer.prerequisites=nil
a.customers={customer};b.customers={customer}
local s=snapshot({a,b});s.legal['3:71']=true
local _,bids=offers(s)
local q=assert(M.StageBuildingInvestment({{site=a,customers={customer}},{site=b,customers={customer}}},price))
local perSource=M.PopulationPayout(.099*9,9)
local receiver=M.PopulationPayout(2*.099*9,9)
assert(q==(perSource*4+receiver)*28*256)
assert(#bids==1 and bids[1].city==3 and bids[1].building==7 and bids[1].delta==math.min(q,64*256))
a.third.working=false;b.third.working=false
_,bids=offers(s);assert(#bids==0)
''')

    def test_stage_four_requires_both_classes_and_charges_only_new_work(self):
        self.vm().execute('''
local a=fashion(1,10);local s=snapshot({a});s.legal['1:61']=true
local _,nom=offers(s);assert(#nom==1)
local s4=a.supply.specialty[1];local raw
local quote=s.Price
s.Price=function(stream,horizon)
 if stream.id:find('supplier-development',1,true)then raw=stream.amount;return stream.amount*256 end
 return quote(stream,horizon)
end
_,nom=offers(s);assert(#nom==1 and raw==-1)
s4.repairable=true;raw=nil;_,nom=offers(s);assert(#nom==1 and raw==nil)
s4.ready=false;_,nom=offers(s);assert(#nom==0)
s4.ready=true;a.suppliers[2].ready=31;_,nom=offers(s);assert(#nom==0)
a.suppliers[2].ready=8;s.locked.OPERA=45;a.population=7
local r,b=offers(s);assert(r['civic:45'].producerQ8>0 and #b==0)
''')

    def test_stage_four_population_steps_do_not_round_like_stage_three(self):
        self.vm().execute('''
local a=fashion(1,10)
a.fourth.localTransactions={}
local value=M.StageBuildingInvestment({{site=a,producer='fourth',building=a.fourth}},price)
local later=a.customers[1];later.population=14
assert(M.StageBuildingInvestment({{site=a,producer='fourth',building=a.fourth}},price)==value)
later.population=15
assert(M.StageBuildingInvestment({{site=a,producer='fourth',building=a.fourth}},price)==value+3*26*256)
''')

    def test_stage_four_customer_bid_uses_its_loaded_producer_transaction(self):
        self.vm().execute('''
local a=fashion(1,10);a.fourth.working=true
local theater=a.customers[1]
theater.type='UNIQUE_MARKET';theater.working=false;theater.unlock=0;theater.turns=5
theater.prerequisites=nil;theater.transactions={FASHION=theater.transaction}
local s=snapshot({a});s.legal['3:71']=true
local _,nom=offers(s)
assert(#nom==1 and nom[1].building==7 and nom[1].delta==64*256)
theater.transactions={};_,nom=offers(s);assert(#nom==0)
''')
