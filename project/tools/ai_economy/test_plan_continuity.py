"""Multi-turn purchase/ownership sequences through real model and bid adapters."""
from pathlib import Path
import unittest
from lupa.lua51 import LuaRuntime
import test_boundaries as boundaries

AI = Path(__file__).resolve().parents[3] / 'Civ Supply Chains/Lua_UI/AI'


class PlanContinuity(unittest.TestCase):
    def module(self):
        vm=LuaRuntime()
        vm.execute((AI/'CSC_AI_PlanContinuity.lua').read_text(encoding='utf-8'))
        return vm

    def runtime(self):
        vm=boundaries.Boundaries().bid_vm()
        vm.execute((AI/'CSC_AI_PlanContinuity.lua').read_text(encoding='utf-8'))
        vm.execute((AI/'CSC_AI_EconomyModel.lua').read_text(encoding='utf-8'))
        vm.execute((AI/'CSC_AI_EconomyAdapters.lua').read_text(encoding='utf-8'))
        vm.execute('''
turn=1;props={};worked=false;missing=false;signature='0,-1,-1,-1';baseCount=1
Game.GetCurrentGameTurn=function()return turn end
Game.GetProperty=function(_,key)return props[key]end
Game.SetProperty=function(_,key,value)props[key]=value end
snapshot.FootprintSignature=function()return signature end
snapshot.Geometry=function()return{upper=2}end
snapshot.Supply=function()return{base=baseCount>0 and{{plot=9}}or{}}end
snapshot.Site=function(_,p)
 local direct={{id='YIELD_PRODUCTION',yield='YIELD_PRODUCTION',amount=2}}
 if worked and p:GetIndex()==2 then direct[#direct+1]={id='displaced:YIELD_FOOD',yield='YIELD_FOOD',amount=-3}end
 return{city=7,horizon=50,quarterReady=1,adjacency=2,baseCount=baseCount,materialYield='YIELD_FOOD',
 direct=direct,seconds={},customers={},footprintWorkers=worked and 1 or 0,footprintSignature=signature}
end
snapshot.Price=function(s,h)
 if missing then return nil end
 return math.floor(s.amount*(s.fixed and 1 or h-s.ready)*256)
end
function target(rows)for _,e in ipairs(rows)do if e.plot==2 and e.district==36 then return e end end end
function publish(previous,policy)
 local rows,stats=CSC_AI_EconomyAdapters.QuarterBids(snapshot,placement,{},policy or early,previous or{})
 CSC_AI_EconomyAdapters.Committed(rows)
 return rows,stats
end
function confirm(rows)
 local e=assert(target(rows))
 CE_AIDistrictScoresTraceRead=function()return string.format(
 '{"records":[{"k":"best","version":1,"existingDistrict":0,"player":1,"city":7,"district":36,"plot":2,"result":%d}]}',e.finalQ8)end
 CSC_AI_EconomyAdapters.ObserveNativeChoices('{"trace_count":1,"generation":1,"version":1}',rows)
end
function acquire()
 plots[2]=plot(2,1);worked=true
end
''')
        return vm

    def test_purchase_to_owned_uses_one_policy_and_preserves_the_selected_unworked_baseline(self):
        vm=self.runtime()
        vm.execute('''
local first=publish();assert(target(first).finalQ8==96*256)
turn=2;confirm(first)
local waiting=publish(first);assert(target(waiting).finalQ8==96*256)
turn=3;acquire()
-- The old scanner adds no-host128 only AFTER ownership. Complete valuation
-- must ignore it while retaining the current model's actual customer income.
local owned=publish(waiting,{{player=1,city=7,district=36,plot=2,delta=-128*256}})
local q=assert(target(owned))
assert(q.finalQ8==146*256 and q.footprintCostMode=='acquisition_baseline')
assert(q.currentDisplacementQ8==-147*256) -- Exposed, not double charged.
local facts=snapshot.Site(snapshot.cities[7].object,plots[2])
assert(#facts.direct==2) -- Facts stay truthful; only the plan's quote is rebased.
assert(CSC_AI_EconomyModel.Forecast(facts,snapshot.Price).valueQ8<0)
local restored=CSC_AI_PlanContinuity.New(1,3,props.CSC_AI_QuarterIntentV1_1)
assert(restored.plans['7:36:2'].acquired==3 and restored.plans['7:36:2'].baselineWorkers==0)
''')

    def test_unconfirmed_offers_do_not_create_a_footprint_anchor(self):
        vm=self.runtime()
        vm.execute('''
local first=publish()
turn=2;acquire()
local second=publish(first)
assert(target(second)==nil)
assert(next(CSC_AI_PlanContinuity.New(1,2,props.CSC_AI_QuarterIntentV1_1).plans)==nil)
''')

    def test_selected_owned_unworked_site_also_survives_temporary_staffing(self):
        vm=self.runtime()
        vm.execute('''
plots[2]=plot(2,1)
local first=publish();assert(target(first).finalQ8==146*256)
turn=2;confirm(first);worked=true
local second=publish(first)
assert(target(second).finalQ8==146*256)
assert(target(second).footprintCostMode=='selection_baseline')
''')

    def test_actual_customer_layout_credit_disappears_without_an_ownership_only_penalty(self):
        vm=self.runtime()
        vm.execute('''
local options={{city=7,district=20,family='HUB',plot=9,adjacency=2,bestAdjacency=2,displacedAdjacency=0}}
snapshot.CustomerOptions=function()return options end
GameInfo.Districts={[36]={RequiresPopulation=1},[20]={RequiresPopulation=1,Hash=20}}
snapshot.ui.GetLegalDistrictTargets=function()return{}end
local first=publish();assert(target(first).layoutPreferenceQ8==32*256)
turn=2;confirm(first);options={}
local second=publish(first)
assert(target(second).finalQ8==target(first).finalQ8-32*256)
turn=3;plots[2]=plot(2,1)
local third=publish(second,{{player=1,city=7,district=36,plot=2,delta=-128*256}})
assert(target(third).finalQ8>target(second).finalQ8)
assert(target(third).layoutPreferenceQ8==0)
''')

    def test_named_material_loss_survives_later_positive_legacy_site_entries(self):
        vm=self.runtime()
        vm.execute('''
local rows=publish({},{{player=1,city=7,district=36,plot=2,delta=-200*256,protectionQ8=200*256},
 {player=1,city=7,district=36,plot=2,delta=48*256}})
assert(target(rows)==nil)
''')

    def test_unknown_native_price_has_only_one_owned_confirmed_plan_grace_turn(self):
        vm=self.runtime()
        vm.execute('''
local first=publish();turn=2;confirm(first);local waiting=publish(first)
turn=3;acquire();local owned=publish(waiting)
turn=4;missing=true;local grace=publish(owned)
assert(target(grace).carried and target(grace).finalQ8==target(owned).finalQ8)
assert(target(grace).economicQ8==nil)
turn=5;local expired=publish(grace)
assert(target(expired)==nil)
assert(next(CSC_AI_PlanContinuity.New(1,5,props.CSC_AI_QuarterIntentV1_1).plans)==nil)
''')

    def test_missing_price_does_not_carry_a_frontier_purchase_bid(self):
        vm=self.runtime()
        vm.execute('''
local first=publish();turn=2;confirm(first);missing=true
assert(target(publish(first))==nil)
''')

    def test_continuity_keeps_the_ordinary_bid_without_stale_layout_credit(self):
        self.runtime().execute('''
local C=CSC_AI_PlanContinuity
local state=C.New(1,20)
local entry={player=1,city=7,district=36,plot=2,economy=true,finalQ8=420*256,
    ordinaryBidQ8=300*256,publishedTurn=19}
local plan=C.Selected(state,entry)
assert(plan.lastQ8==300*256)
entry.finalQ8=425*256;entry.ordinaryBidQ8=305*256
C.Committed(state,{entry})
assert(C.Grace(state,plan,'pricing_unavailable',true)==305*256)
entry.ordinaryBidQ8=-50
C.Committed(state,{entry})
local restored=next(C.New(1,21,C.Encode(state)).plans)
assert(restored and plan.lastQ8==0 and C.Grace(state,plan,'pricing_unavailable',true)==nil)
''')

    def test_material_loss_does_not_get_missing_price_grace(self):
        vm=self.runtime()
        vm.execute('''
local first=publish();turn=2;confirm(first);local second=publish(first)
turn=3;acquire();local owned=publish(second)
turn=4;baseCount=0;missing=true
assert(target(publish(owned))==nil)
''')

    def test_changed_feature_disables_anchor_and_reevaluates_economics(self):
        vm=self.runtime()
        vm.execute('''
local first=publish();turn=2;confirm(first);local second=publish(first)
turn=3;acquire();signature='0,4,-1,-1'
assert(target(publish(second))==nil)
''')

    def test_foreign_ownership_releases_the_plan(self):
        vm=self.runtime()
        vm.execute('''
local first=publish();turn=2;confirm(first);local second=publish(first)
turn=3;plots[2]=plot(2,2)
assert(target(publish(second))==nil)
assert(next(CSC_AI_PlanContinuity.New(1,3,props.CSC_AI_QuarterIntentV1_1).plans)==nil)
''')

    def test_foundation_releases_memory_and_stops_new_quarter_offers(self):
        vm=self.runtime()
        vm.execute('''
local first=publish();turn=2;confirm(first);local second=publish(first)
turn=3;acquire();hasQuarter=true;plots[2].GetDistrictType=function()return 36 end
assert(#publish(second)==0)
assert(next(CSC_AI_PlanContinuity.New(1,3,props.CSC_AI_QuarterIntentV1_1).plans)==nil)
''')

    def test_save_reload_keeps_confirmed_acquisition_baseline_without_game_objects(self):
        vm=self.runtime()
        vm.execute('''
local first=publish();turn=2;confirm(first);local second=publish(first)
turn=3;acquire();publish(second)
saved=props.CSC_AI_QuarterIntentV1_1
''')
        # Reload the real adapter closure: no process-local plan cache survives.
        vm.execute((AI/'CSC_AI_EconomyAdapters.lua').read_text(encoding='utf-8'))
        vm.execute('''
turn=4;props.CSC_AI_QuarterIntentV1_1=saved
local rows=publish()
assert(target(rows).finalQ8==146*256 and target(rows).footprintCostMode=='acquisition_baseline')
''')

    def test_acquired_lifetime_expires_even_when_positive_quotes_keep_refreshing(self):
        vm=self.runtime()
        vm.execute('''
local first=publish();turn=2;confirm(first);local second=publish(first)
turn=3;acquire();local last=publish(second)
for t=4,18 do turn=t;last=publish(last);assert(target(last))end
turn=19;assert(target(publish(last))==nil)
''')

    def test_invalid_saved_memory_is_ignored_and_the_confirmed_set_is_bounded(self):
        vm=self.module()
        vm.execute('''
local C=CSC_AI_PlanContinuity
assert(next(C.New(1,5,'1\ninvalid|fields\n').plans)==nil)
local state=C.New(1,5)
for i=1,300 do C.Selected(state,{economy=true,finalQ8=100,city=i,district=36,plot=i,frontier=true})end
local count=0;for _ in pairs(state.plans)do count=count+1 end
assert(count==C.MaxPlans and #state.events<=64 and state.eventsDropped>0)
assert(#C.Encode(state)<65536)
assert(next(C.New(1,46,C.Encode(state)).plans)==nil)
'''.replace("'1\ninvalid|fields\n'", "'1\\ninvalid|fields\\n'"))

    def test_a_new_native_best_does_not_erase_an_older_fixed_site_request(self):
        vm=self.module()
        vm.execute('''
local C=CSC_AI_PlanContinuity
local state=C.New(1,10)
C.Selected(state,{economy=true,finalQ8=100,city=7,district=36,plot=2,frontier=true})
C.Selected(state,{economy=true,finalQ8=200,city=7,district=36,plot=3,frontier=true})
assert(state.plans['7:36:2'] and state.plans['7:36:3'])
C.Withdraw(state,7,36,3,'economics')
assert(state.plans['7:36:2'] and not state.plans['7:36:3'])
assert(C.New(1,11,C.Encode(state)).plans['7:36:2'])
''')

    def test_native_confirmation_is_not_limited_to_the_first_diagnostic_page(self):
        vm=self.runtime()
        vm.execute('''
local first=publish();local q=target(first);turn=2
local pages=0
CE_AIDistrictScoresTraceRead=function(offset)
 pages=pages+1
 if offset<128 then return'{"records":[]}'end
 return string.format('{"records":[{"k":"best","version":1,"existingDistrict":0,"player":1,"city":7,"district":36,"plot":2,"result":%d}]}',q.finalQ8)
end
CSC_AI_EconomyAdapters.ObserveNativeChoices('{"trace_count":129,"generation":1,"version":1}',first)
CSC_AI_EconomyAdapters.Committed(first)
assert(pages==3)
assert(CSC_AI_PlanContinuity.New(1,2,props.CSC_AI_QuarterIntentV1_1).plans['7:36:2'].plot==2)
''')

    def test_stale_journal_page_cannot_partially_confirm_a_choice(self):
        vm=self.runtime()
        vm.execute('''
local first=publish();local q=target(first);turn=2
CE_AIDistrictScoresTraceRead=function(offset)
 if offset==64 then return'{"stale":true}'end
 return string.format('{"records":[{"k":"best","version":1,"existingDistrict":0,"player":1,"city":7,"district":36,"plot":2,"result":%d}]}',q.finalQ8)
end
CSC_AI_EconomyAdapters.ObserveNativeChoices('{"trace_count":65,"generation":1,"version":1}',first)
CSC_AI_EconomyAdapters.Committed(first)
assert(next(CSC_AI_PlanContinuity.New(1,2,props.CSC_AI_QuarterIntentV1_1).plans)==nil)
''')

    def test_existing_district_or_unmatched_native_value_creates_no_plan(self):
        vm=self.runtime()
        vm.execute('''
local first=publish();local q=target(first);turn=2
CE_AIDistrictScoresTraceRead=function()return string.format(
 '{"records":[{"k":"best","version":1,"existingDistrict":1,"player":1,"city":7,"district":36,"plot":2,"result":%d},{"k":"best","version":1,"existingDistrict":0,"player":1,"city":7,"district":36,"plot":2,"result":%d}]}',q.finalQ8,q.finalQ8+1)end
CSC_AI_EconomyAdapters.ObserveNativeChoices('{"trace_count":2,"generation":1,"version":1}',first)
CSC_AI_EconomyAdapters.Committed(first)
assert(next(CSC_AI_PlanContinuity.New(1,2,props.CSC_AI_QuarterIntentV1_1).plans)==nil)
''')


if __name__ == '__main__':
    unittest.main()
