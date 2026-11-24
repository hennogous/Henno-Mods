"""Signed placement residuals, packet merging and bounded work with quote doubles.

Actual gameplay-to-world valuation has separate SQL/Core/Facts tests. These
checks exercise the adapter's score units and native transport boundaries.
"""
import unittest
from pathlib import Path
from lupa.lua51 import LuaRuntime

AI=Path(__file__).resolve().parents[3]/'Civ Supply Chains/Lua_UI/AI'


class CustomerEconomicOffers(unittest.TestCase):
    def test_provider_scope_requires_positive_owned_offer_and_viable_supply(self):
        self.vm().execute('''
print=function()end;local E=CSC_AI_EconomyAdapters
local profile={key='BAKERS'}
local site={horizon=10,suppliers={{kind='base',plot=99,ready=2}}}
local chain={profile=profile,economy=site,ready=true,complete=true}
for _,candidate in ipairs(groups[1].candidates)do candidate.chains={chain} end
snapshot.IsGoodsProvider=function(p,d)return p==profile and d==6 end
snapshot.providerDeclineLimit=72
E.ProspectiveConnectionsEnabled=true
local function offers()
 local result={}
 for _,offer in ipairs(E.CustomerEconomicOffers(snapshot,{}))do result[offer.plot]=offer end
 return result
end
local rows=offers()
assert(rows[20].readyProvider==profile and not rows[21].readyProvider)
rows=E.MergeCustomerOffers({{player=1,city=7,district=6,plot=20,delta=20}},{rows[20]})
assert(rows[1].readyProvider==profile and rows[1].delta==4020)
site.suppliers[1].plot=20;assert(not offers()[20].readyProvider)
site.suppliers[1].plot=99;site.suppliers[1].ready=10
assert(not offers()[20].readyProvider)
site.suppliers[1].ready=2;chain.ready=false
assert(not offers()[20].readyProvider)
chain.complete=false;site.quarterReady=10
assert(not offers()[20].readyProvider)
site.quarterReady=3
assert(offers()[20].readyProvider==profile)
snapshot.providerDeclineLimit=nil
assert(not offers()[20].readyProvider)
''')

    def test_legal_but_no_longer_linked_incumbent_loses_priority(self):
        self.vm().execute('''
print=function()end;local E=CSC_AI_EconomyAdapters
E.CustomerEconomicOffers(snapshot,{})
turn=21;E.CustomerEconomicOffers(snapshot,{})
groups[1].candidates[1].links=0
local observed={};local old=snapshot.CustomerWorld
snapshot.CustomerWorld=function(c,d,p)observed[#observed+1]=p;return old(c,d,p)end
turn=22;E.CustomerEconomicOffers(snapshot,{})
assert(observed[2]==21)
''')

    def test_losing_runner_up_keeps_incumbent_but_native_gated_winner_does_not(self):
        self.vm().execute('''
print=function()end;groups[1].candidates[2].links=0
local E=CSC_AI_EconomyAdapters
E.CustomerEconomicOffers(snapshot,{}) -- useful20 then losing unrelated21
turn=21;E.CustomerEconomicOffers(snapshot,{})
local observed={};local old=snapshot.CustomerWorld
snapshot.CustomerWorld=function(c,d,p)observed[#observed+1]=p;return old(c,d,p)end
turn=22;E.CustomerEconomicOffers(snapshot,{})
assert(observed[2]==20)
-- A linked but native-gated high quote must lose the hint to a viable rival.
nets[20]=0;values[21]=12000;groups[1].candidates[2].links=1
turn=23;E.CustomerEconomicOffers(snapshot,{})
observed={};turn=24;E.CustomerEconomicOffers(snapshot,{})
assert(observed[2]==21)
''')

    def test_pair_first_covers_eight_groups_and_skips_singletons(self):
        self.vm().execute('''
print=function()end;groups={}
for i=1,12 do groups[i]={city=i,district=6,reference={plot=10,links=0},candidates={
 {plot=20,adjacency=2,links=1},{plot=21,adjacency=2,links=1},{plot=22,adjacency=2,links=0}}}end
values[22]=8000;nets[22]=5000
groups[13]={city=99,district=6,reference={plot=10},candidates={{plot=10,links=1}}}
local rows,stats=CSC_AI_EconomyAdapters.CustomerEconomicOffers(snapshot,{})
assert(stats.groups==8 and stats.forecasts==16 and stats.singletons==1)
local seen={};for _,r in ipairs(rows)do seen[r.city]=true end
turn=21;rows,stats=CSC_AI_EconomyAdapters.CustomerEconomicOffers(snapshot,{})
for _,r in ipairs(rows)do seen[r.city]=true end
local n=0;for _ in pairs(seen)do n=n+1 end;assert(n==12)
''')

    def test_plot_exploration_survives_incumbent_repricing_at_full_budget(self):
        self.vm().execute('''
print=function()end;groups={};values[22]=8000;nets[22]=5000
for i=1,8 do groups[i]={city=i,district=6,reference={plot=10,links=0},candidates={
 {plot=20,adjacency=2,links=1},{plot=21,adjacency=2,links=1},{plot=22,adjacency=2,links=0}}}end
local seen={}
for t=20,27 do turn=t;local rows,stats=CSC_AI_EconomyAdapters.CustomerEconomicOffers(snapshot,{})
 assert(stats.forecasts==16)
 for _,r in ipairs(rows)do if r.city==1 then seen[r.plot]=true end end
end
assert(seen[20]and seen[21]and seen[22])
''')

    def test_persistent_connections_reprice_backups_at_full_budget(self):
        self.vm().execute('''
print=function()end;groups={};values[22]=8000;nets[22]=5000
local E=CSC_AI_EconomyAdapters
for i=1,8 do groups[i]={city=i,district=6,reference={plot=10,links=0},candidates={
 {plot=20,adjacency=2,links=1},{plot=21,adjacency=2,links=1},{plot=22,adjacency=2,links=0}}}end
snapshot.captureConnections=true
E.AnchoredConnectionPlans=function()
 local plans={}
 for city=1,8 do
  local option={city=city,district=6}
  local best={plot=20,option=option,valueQ8=500}
  plans[#plans+1]={order='quarterFirst',best=best,choices={best}}
 end
 return plans
end
local seen={}
for t=20,27 do turn=t;local rows,stats=E.CustomerEconomicOffers(snapshot,{})
 assert(stats.forecasts==16)
 for _,row in ipairs(rows)do if row.city==1 then seen[row.plot]=true end end
end
assert(seen[20]and seen[21]and seen[22])
''')

    def test_hint_requotes_new_value_and_disappears_with_illegal_candidate(self):
        self.vm().execute('''
print=function()end
local E=CSC_AI_EconomyAdapters
local rows=E.CustomerEconomicOffers(snapshot,{})
values[20]=10010;turn=21;rows=E.CustomerEconomicOffers(snapshot,{})
for _,r in ipairs(rows)do if r.plot==20 then assert(r.delta==10)end end
groups[1].candidates={{plot=21,adjacency=2,links=1}};turn=22
rows=E.CustomerEconomicOffers(snapshot,{})
assert(#rows==1 and rows[1].plot==21 and rows[1].delta==-3000)
''')

    def vm(self):
        vm=LuaRuntime(unpack_returned_tuples=True)
        vm.execute('''
Game={GetCurrentGameTurn=function()return turn end};turn=20
CSC_AI_EconomyModel={};CSC_AI_EconomyFacts={}
groups={{city=7,district=6,reference={plot=10},candidates={
 {plot=20,adjacency=2,links=1},{plot=21,adjacency=2,links=1}}}}
values={[10]=10000,[20]=14000,[21]=7000};nets={[20]=5000,[21]=5000}
snapshot={id=1,CustomerCandidateSets=function(protected)return groups end,
 CustomerWorld=function(city,district,plot)return{},{value=values[plot],customer={ready=3}}end,
 WorldQuote=function(world)if world.value then return{valueQ8=world.value}end end,
 CustomerNetValue=function(city,district,plot)return nets[plot]end}
''')
        vm.execute((AI/'CSC_AI_EconomyAdapters.lua').read_text())
        return vm

    def test_common_value_cancels_and_negative_site_effect_is_retained(self):
        self.vm().execute('''
local E=CSC_AI_EconomyAdapters
local rows,stats=E.CustomerEconomicOffers(snapshot,{})
assert(#rows==2 and rows[1].delta==4000 and rows[2].delta==-3000 and stats.clamped==0)
for k,v in pairs(values)do values[k]=v+10000000 end
local again=E.CustomerEconomicOffers(snapshot,{})
assert(again[1].delta==rows[1].delta and again[2].delta==rows[2].delta)
assert(rows[1].customerEconomic and not rows[1].economy and rows[1].finalQ8==nil)
''')

    def test_raw_zero_gate_and_policy_limit_preserve_common_native_forecast(self):
        self.vm().execute('''
values[20]=1000000;nets[21]=100
local rows,stats=CSC_AI_EconomyAdapters.CustomerEconomicOffers(snapshot,{})
assert(rows[1].delta==256*256 and rows[2].delta==-99 and stats.clamped==2)
nets[20]=0;nets[21]=nil
assert(#CSC_AI_EconomyAdapters.CustomerEconomicOffers(snapshot,{})==0)
''')

    def test_missing_reference_leaves_entire_city_type_without_economic_offers(self):
        self.vm().execute('''
values[10]=nil
local rows,stats=CSC_AI_EconomyAdapters.CustomerEconomicOffers(snapshot,{})
assert(#rows==0 and stats.forecasts==1 and stats.unknown==1)
''')

    def test_quotes_and_sites_are_bounded_and_group_start_rotates(self):
        self.vm().execute('''
groups={}
for i=1,80 do groups[i]={city=i,district=6,reference={plot=10},candidates={
 {plot=20,adjacency=2,links=1},{plot=21,adjacency=2,links=1}}}end
local E=CSC_AI_EconomyAdapters
local rows,stats=E.CustomerEconomicOffers(snapshot,{})
assert(stats.forecasts<=64 and #rows<=64)
turn=turn+1
local again=E.CustomerEconomicOffers(snapshot,{})
assert(rows[1].city~=again[1].city)
''')

    def test_duplicate_signals_merge_once_without_mutating_protection_or_whole_bids(self):
        self.vm().execute('''
local E=CSC_AI_EconomyAdapters
local original={{player=1,city=7,district=6,plot=20,delta=100,customerFirst=true},
 {player=1,city=7,district=36,plot=30,finalQ8=5000,economy=true}}
local offers=E.CustomerEconomicOffers(snapshot,{})
offers[#offers+1]={player=1,city=7,district=36,plot=30,delta=1000,customer=true}
local merged=E.MergeCustomerOffers(original,offers)
assert(#merged==3 and merged[1].delta==4100 and original[1].delta==100)
assert(merged[1].customerFirst and merged[1].customerEconomic and merged[2].finalQ8==5000)
local empty=E.MergeCustomerOffers({original[1]},{{player=1,city=7,district=6,plot=20,delta=-100}})
assert(#empty==0)
''')

    def test_skip_reasons_separate_native_gates_from_missing_world_quotes(self):
        self.vm().execute('''
local E=CSC_AI_EconomyAdapters
nets[20]=nil;nets[21]=0
local rows,stats=E.CustomerEconomicOffers(snapshot,{})
assert(#rows==0 and stats.unknown==2)
assert(stats.nativeUnavailable==1 and stats.nativeNonpositive==1)
assert(stats.referenceUnavailable==0 and stats.candidateUnavailable==0)
values[20]=nil;nets[21]=5000
rows,stats=E.CustomerEconomicOffers(snapshot,{})
assert(#rows==1 and stats.unknown==1 and stats.candidateUnavailable==1)
values[10]=nil
rows,stats=E.CustomerEconomicOffers(snapshot,{})
assert(#rows==0 and stats.forecasts==1 and stats.referenceUnavailable==1)
''')

    def test_quarter_funnel_uses_existing_facts_and_limits_output(self):
        self.vm().execute('''
local E=CSC_AI_EconomyAdapters
local logs={};print=function(line)logs[#logs+1]=line end
local evaluations={}
for i=1,20 do evaluations['1:7:6:'..i]={reason='reason'..i,adjacency=i}end
evaluations['1:7:6:99']={reason='positive',adjacency=4}
E.ReportQuarterFunnel(snapshot,evaluations);assert(#logs==0)
turn=25;E.ReportQuarterFunnel(snapshot,evaluations)
assert(#logs==9 and logs[9]:find('samples=8',1,true))
assert(evaluations['1:7:6:99'].reason=='positive' and values[20]==14000)
''')


if __name__=='__main__':unittest.main()
