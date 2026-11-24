"""Real module isolation and semantic proofs for the zero-turn timing query."""
from pathlib import Path
import unittest
from lupa.lua51 import LuaRuntime
from customer_timing_query import build

MOD=Path(__file__).resolve().parents[4]/'Civ Supply Chains'


class TimingProof(unittest.TestCase):
    def test_bid_equivalence_compiles_with_layout_policy_enabled(self):
        code,provenance=build(MOD,MOD,layout_policy=True,bid_equivalence=True)
        LuaRuntime().eval('function(s)assert(loadstring(s))end')(code)
        self.assertTrue(provenance['bid_equivalence'] and provenance['layout_policy'])
        self.assertIn('local bidEquality=true',code)
        self.assertIn('local layoutPolicy=true',code)
        with self.assertRaises(AssertionError):
            build(MOD,MOD,bid_equivalence=True)

    def vm(self):
        code,_=build(MOD,MOD)
        vm=LuaRuntime()
        vm.eval('function(s)assert(loadstring(s))end')(code)
        vm.execute('setfenv=nil;_G=nil;CSC_AI_EconomyFacts={};CSC_AI_EconomyModel={};CSC_AI_EconomyAdapters={}')
        vm.execute(code.split('-- CSC_TIMING_NATIVE_BEGIN',1)[0]+'''
P=proofCopy;J=encode
for _,factory in pairs(factories)do
 local E,M=factory();assert(E~=active[3]and M~=active[2])
end
local current={activeTables()};assert(current[1]==active[1]and current[2]==active[2]and current[3]==active[3])
''')
        return vm

    def test_priced_record_permutation_is_equal_without_mutating_model_results(self):
        self.vm().execute('''
local a={streams={{id='B',valueQ8=2,contributors={{city=2},{city=1}}},{id='A',valueQ8=3}}}
local b={streams={{id='A',valueQ8=3},{id='B',valueQ8=2,contributors={{city=1},{city=2}}}}}
assert(J(P(a))==J(P(b)))
assert(a.streams[1].id=='B'and a.streams[1].contributors[1].city==2)
''')

    def test_equal_totals_do_not_hide_prices_swapped_between_stream_identities(self):
        self.vm().execute('''
local a={valueQ8=5,streams={{id='A',valueQ8=2},{id='B',valueQ8=3}}}
local b={valueQ8=5,streams={{id='A',valueQ8=3},{id='B',valueQ8=2}}}
assert(J(P(a))~=J(P(b)))
b.streams={{id='A',valueQ8=2},{id='B',valueQ8=3},{id='B',valueQ8=3}}
assert(J(P(a))~=J(P(b))) -- Preserve multiplicity too.
''')

    def test_sparse_plot_sets_and_contributor_maps_keep_all_keys(self):
        self.vm().execute('''
assert(J({[0]=true,[1]=true})=='{"0":true,"1":true}')
local a={contributors={[4]=true,[10]=true},streams={[0]={id='zero'},[2]={id='two'}}}
assert(J(P(a))==J(a))
local b={contributors={true,false}};assert(J(P(b))==J(b))
''')

    def test_timing_plan_investment_and_failure_changes_remain_visible(self):
        self.vm().execute('''
local a={plan={second='Water'},investments={{id='A'},{id='B'}},streams={{id='A',ready=2,valueQ8=3}}}
local b=P(a);b.streams[1].ready=3;assert(J(P(a))~=J(P(b)))
b=P(a);b.plan.second='Wind';assert(J(P(a))~=J(P(b)))
b=P(a);b.investments={b.investments[2],b.investments[1]};assert(J(P(a))~=J(P(b)))
assert(J(P({problem='Unknown'}))~=J(P({problem='Budget'})))
''')


if __name__=='__main__':unittest.main()
