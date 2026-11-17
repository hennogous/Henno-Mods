"""Signed placement residuals, packet merging and bounded work with quote doubles.

Actual gameplay-to-world valuation has separate SQL/Core/Facts tests. These
checks exercise the adapter's score units and native transport boundaries.
"""
import unittest
from pathlib import Path
from lupa.lua51 import LuaRuntime

AI=Path(__file__).resolve().parents[3]/'Civ Supply Chains/Lua_UI/AI'


class CustomerEconomicOffers(unittest.TestCase):
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


if __name__=='__main__':unittest.main()
