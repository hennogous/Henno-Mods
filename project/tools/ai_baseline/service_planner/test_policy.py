"""Policy and full actual-Lua purchase-path tests, without a native connection."""
import argparse
from dataclasses import replace
import json
from pathlib import Path
import sys
import tempfile
import unittest
from .policy import Budget,Candidate,Need,Planner,Policy,PROFILES
from .execution import PurchaseExecutor
from .needs import from_observations
from .coordinator import Coordinator
from .observations import build_candidates


def candidate(**kwargs):
    c=Candidate(1,10,42,'TAILORS',2,0,service='dockmaster',venue_ready=True,
                research_ready=True,ready_in_turns=10,confidence=.9,
                dependencies_owned_or_in_purchase=True,missing_tiles=(42,),purchase_plot=42,
                price=80,revealed=True,material_visible=True,potential_legal=True,
                native_purchasable=True,eligible_ai=True,native_projection_verified=True,
                material_plots=(81,82),customer_plot=100,observed_turn=60)
    return replace(c,**kwargs)


NEEDS={'naval':Need(.95,.95,'observed naval production')}
BUDGET=Budget(600)
SCRATCH=None


class PolicyTests(unittest.TestCase):
    def setUp(self):self.p=Planner()
    def eval(self,c,needs=NEEDS,budget=BUDGET):return self.p.evaluate(c,needs,budget,60)
    def test_strong_service_buys_identical_tile_general_waits(self):
        self.assertEqual(self.eval(candidate()).action,'purchase')
        general=self.eval(candidate(service=None))
        self.assertEqual((general.action,general.max_price),('watch',36))
        self.assertEqual(self.eval(candidate()).max_price,112)
    def test_stage2_accepts_base_only(self):self.assertEqual(self.eval(candidate()).action,'purchase')
    def test_stage4_requires_both(self):
        self.assertEqual(self.eval(candidate(service='stage_manager'),{'culture':Need(1,1,'tourism investment')}).action,'reject')
    def test_weak_inference_gets_no_strong_budget(self):
        self.assertEqual(self.eval(candidate(),{'naval':Need(1,.5,'weak agenda prior')}).action,'watch')
    def test_missing_customer_has_no_strong_budget(self):self.assertEqual(self.eval(candidate(venue_ready=False)).action,'watch')
    def test_missing_research_has_no_strong_budget(self):self.assertEqual(self.eval(candidate(research_ready=False)).action,'watch')
    def test_distant_chain_has_no_strong_budget(self):self.assertEqual(self.eval(candidate(ready_in_turns=40)).action,'watch')
    def test_late_naval_era_has_no_production_premium(self):self.assertEqual(self.eval(candidate(era=4)).action,'watch')
    def test_emergency_reserve_protected(self):self.assertEqual(self.eval(candidate(),budget=Budget(600,emergency_reserve=550)).action,'watch')
    def test_deficit_reserve_protected(self):self.assertEqual(self.eval(candidate(),budget=Budget(600,-55)).action,'watch')
    def test_two_missing_tiles_watch_only(self):self.assertEqual(self.eval(candidate(missing_tiles=(42,81))).action,'watch')
    def test_unfunded_supply_dependency_rejects(self):self.assertEqual(self.eval(candidate(dependencies_owned_or_in_purchase=False)).action,'reject')
    def test_native_projection_unknown_watch_only(self):self.assertEqual(self.eval(candidate(native_projection_verified=False)).action,'watch')
    def test_unrevealed_site_rejected(self):self.assertEqual(self.eval(candidate(revealed=False)).action,'reject')
    def test_hidden_material_rejected(self):self.assertEqual(self.eval(candidate(material_visible=False)).action,'reject')
    def test_human_rejected(self):self.assertEqual(self.eval(candidate(human=True)).action,'reject')
    def test_unknown_ai_eligibility_rejected(self):self.assertEqual(self.eval(candidate(eligible_ai=False)).action,'reject')
    def test_same_type_quarter_rejected(self):self.assertEqual(self.eval(candidate(same_quarter_present=True)).action,'reject')
    def test_unsafe_frontier_rejected(self):self.assertEqual(self.eval(candidate(frontier_danger=True)).action,'reject')
    def test_imminent_border_growth_waits(self):self.assertEqual(self.eval(candidate(natural_border_in_turns=1)).action,'watch')
    def test_owned_site_needs_no_gold(self):
        c=candidate(missing_tiles=(),purchase_plot=None,current_legal=True)
        self.assertEqual(self.eval(c,budget=Budget(0)).action,'place')
    def test_owned_site_still_needs_native_legality(self):
        c=candidate(missing_tiles=(),purchase_plot=None,current_legal=False)
        self.assertEqual(self.eval(c).action,'watch')
    def test_city_cooldown(self):
        self.p.purchases=[(1,10,55,10)];self.assertEqual(self.eval(candidate()).reason,'city purchase cooldown')
    def test_player_cap(self):
        self.p.purchases=[(1,20,59,1),(1,21,58,1)];self.assertEqual(self.eval(candidate()).reason,'player purchase cap')
    def test_pending_blocks_second_dispatch(self):
        self.p.pending_players.add(1);self.assertEqual(self.eval(candidate()).action,'reject')
    def test_base_count_wins_total_within_same_service(self):
        self.p.update(1,10,60,[candidate(base=1,specialty=5),candidate(plot=43,purchase_plot=43,missing_tiles=(43,),base=2,specialty=1)])
        rows=self.p.select({(1,10):NEEDS},{1:BUDGET},60,lambda c:c)
        self.assertEqual(rows[0].candidate.plot,43)
    def test_aligned_base_site_wins_general_both_site(self):
        a=candidate(missing_tiles=(),purchase_plot=None,current_legal=True)
        b=candidate(plot=43,missing_tiles=(),purchase_plot=None,current_legal=True,service=None,specialty=2)
        self.p.update(1,10,60,[b,a]);self.assertEqual(self.p.select({(1,10):NEEDS},{1:BUDGET},60,lambda c:c)[0].candidate.service,'dockmaster')
    def test_stale_candidate_not_actionable(self):
        self.p.update(1,10,55,[candidate()])
        with self.assertRaises(AssertionError):self.p.select({(1,10):NEEDS},{1:BUDGET},61,lambda c:c)
    def test_event_coalescing_and_wide_schedule(self):
        self.assertTrue(self.p.wide_due(1,10,60));self.p.update(1,10,60,[candidate()])
        self.p.mark_dirty(1,10);self.p.mark_dirty(1,10)
        self.assertEqual(len(self.p.dirty),1);self.assertFalse(self.p.wide_due(1,10,61));self.assertTrue(self.p.wide_due(1,10,65))
    def test_disappearing_supply_drops_cached_plan(self):
        self.p.update(1,10,60,[candidate()]);self.assertEqual(self.p.select({(1,10):NEEDS},{1:BUDGET},60,lambda c:None),[])
    def test_placement_cannot_consume_selected_material(self):
        a=candidate(missing_tiles=(),purchase_plot=None,current_legal=True)
        b=candidate(city=11,plot=81,missing_tiles=(),purchase_plot=None,current_legal=True,service=None)
        self.p.update(1,10,60,[a]);self.p.update(1,11,60,[b])
        self.assertEqual(len(self.p.select({(1,10):NEEDS},{1:BUDGET},60,lambda c:c)),1)
    def test_observed_need_labels_distinguish_inference(self):
        n=from_observations(naval_unit_in_production=True,population=4,food_surplus=3,housing_shortfall=1)
        self.assertIn('observed',n['naval'].evidence);self.assertIn('inferred',n['growth'].evidence)


LUA_FIXTURE=r'''
turn=60;gold=600;price=80;owner=-1;requests=0;potential=true;purchasable=true;reveal=true;human=false;civic_ready=true;venue_pillaged=false
function rows(values)return setmetatable(values,{__call=function(t)local i=0;return function()i=i+1;return t[i]end end})end
Game={GetCurrentGameTurn=function()return turn end,GetLocalPlayer=function()return 0 end}
GameInfo={Districts={DISTRICT_CSC_TAILORS_QUARTER={Index=37,Hash=370}},
 Civics={CIVIC_NAVAL_TRADITION={Index=5}},
 Buildings={BUILDING_LIGHTHOUSE={Index=21}},Resources={[10]={Index=10},WOOL={Index=10}},
 TypeTags=rows({{Type='WOOL',Tag='CLASS_CSC_TAILORS_BASE'}})}
local queue={HasBeenPlaced=function()return false end}
local ds={HasDistrict=function()return false end}
local buildings={HasBuilding=function()return true end,IsPillaged=function()return venue_pillaged end,GetBuildingLocation=function()return 100 end}
city={GetOwner=function()return 1 end,GetDistricts=function()return ds end,
 GetBuildQueue=function()return queue end,GetGold=function()return {GetPlotPurchaseCost=function()return price end}end,
 GetBuildings=function()return buildings end}
local p={IsAlive=function()return true end,IsMajor=function()return true end,
 IsHuman=function()return human end,GetTreasury=function()return {GetGoldBalance=function()return gold end}end,
 GetCulture=function()return {HasCivic=function()return civic_ready end}end,
 GetCities=function()return {Members=function()local used=false;return function()if not used then used=true;return 10,city end end end}end}
Players={[1]=p};PlayersVisibility={[1]={IsRevealed=function()return reveal end}}
function plot(index,res)
 return {GetIndex=function()return index end,GetOwner=function()return index==42 and owner or 1 end,
 GetX=function()return index end,GetY=function()return 0 end,GetResourceType=function()return res end,
 GetDistrictType=function()return -1 end,GetImprovementType=function()return -1 end,
 GetFeatureType=function()return -1 end,CanHaveDistrict=function()return potential end}
end
local plots={[42]=plot(42,-1),[81]=plot(81,10),[82]=plot(82,10),[100]=plot(100,-1)}
Map={GetPlotByIndex=function(i)return plots[i]end,GetAdjacentPlots=function()return {plots[81],plots[82],plots[100]}end}
CityCommandTypes={PURCHASE=7,PARAM_PLOT_PURCHASE='purchase',PARAM_X='x',PARAM_Y='y'}
CityManager={GetCity=function()return city end,CanStartCommand=function()return purchasable end,
 RequestCommand=function(c,cmd,pars)assert(cmd==7 and pars.purchase==true and pars.x==42);requests=requests+1;gold=gold-price;owner=1 end}
'''


class LuaRunner:
    def __init__(self):
        from lupa.lua51 import LuaRuntime
        self.lua=LuaRuntime(unpack_returned_tuples=True);self.lua.execute(LUA_FIXTURE);self.calls=0
    def cmd(self,code,*args,**kwargs):
        self.calls+=1;self.lua.execute(code);return 'native-request-submitted'


class ExecutionTests(unittest.TestCase):
    def ai_probe_fixture(self,enabled=True):
        self.p=Planner(Policy.material_first())
        self.executor=PurchaseExecutor(self.p,self.runner,self.path,allow_mutations=True,
                                      boundary=lambda:{'turn':60,'autoplay_active':False},allow_ai_native_request_probe=enabled)
        self.runner.lua.execute("GameInfo.TypeTags[2]={Type='WOOL',Tag='CLASS_CSC_TAILORS_SPEC'};CityCommandResults={PLOTS=1};CityManager.CanStartCommand=function(c,k,visible,p)if visible==true then return true,{[1]={42}}end;return false end")
        self.c=candidate(service=None,base=2,specialty=2,remaining_price=80,plan_materials=(81,82),purchase_base=2,purchase_specialty=2)
        self.d=self.p.evaluate(self.c,{},BUDGET,60)
        return lambda c:(c,BUDGET,60,True,None)
    def test_nonlocal_AI_native_request_requires_explicit_optin(self):
        fresh=self.ai_probe_fixture(False)
        with self.assertRaises(Exception):self.executor.request(self.d,{},fresh)
        self.assertEqual(self.runner.lua.globals().requests,0)
    def test_AI_visibility_is_not_confirmation_but_real_receipt_is(self):
        fresh=self.ai_probe_fixture()
        self.executor.request(self.d,{},fresh)
        self.assertFalse(self.executor.native_authority_confirmed)
        self.assertTrue(self.executor.reconcile(1,self.readback)['confirmed'])
        self.assertTrue(self.executor.native_authority_confirmed)
        self.assertEqual(self.runner.lua.globals().requests,1)
    def test_selected_plot_must_be_in_native_visibility_reach(self):
        fresh=self.ai_probe_fixture()
        self.runner.lua.execute('CityManager.CanStartCommand=function(c,k,visible,p)if visible==true then return true,{[1]={43}}end;return false end')
        with self.assertRaises(Exception):self.executor.request(self.d,{},fresh)
        self.assertEqual(self.runner.lua.globals().requests,0)
    def test_rejected_native_request_stays_pending_and_never_repeats(self):
        fresh=self.ai_probe_fixture()
        self.runner.lua.execute('CityManager.RequestCommand=function()requests=requests+1;return false end')
        self.executor.request(self.d,{},fresh)
        self.assertFalse(self.executor.reconcile(1,self.readback)['confirmed'])
        self.assertFalse(self.executor.native_authority_confirmed)
        with self.assertRaises(Exception):self.executor.request(self.d,{},fresh)
        self.assertEqual(self.runner.lua.globals().requests,1)
    def test_confirmed_AI_authority_restores_from_durable_journal(self):
        fresh=self.ai_probe_fixture();self.executor.request(self.d,{},fresh);self.executor.reconcile(1,self.readback)
        restored=PurchaseExecutor(Planner(Policy.material_first()),self.runner,self.path,
                                 allow_mutations=True,allow_ai_native_request_probe=True)
        self.assertTrue(restored.native_authority_confirmed)
        self.assertEqual(restored.planner.purchases,[(1,10,60,80)])
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(dir=SCRATCH);self.addCleanup(self.tmp.cleanup)
        self.p=Planner();self.runner=LuaRunner();self.path=Path(self.tmp.name)/'ledger.ndjson'
        self.executor=PurchaseExecutor(self.p,self.runner,self.path,allow_mutations=True,
                                      boundary=lambda:{'turn':60,'autoplay_active':False})
        self.c=candidate();self.d=self.p.evaluate(self.c,NEEDS,BUDGET,60)
    def fresh(self,c):return c,BUDGET,60,True,'BUILDING_LIGHTHOUSE'
    def readback(self,event):
        g=self.runner.lua.globals();return {'city_owner':1,'plot_owner':g.owner,'gold':g.gold,'turn':g.turn}
    def test_actual_lua_native_command_deducts_and_confirms(self):
        self.executor.request(self.d,NEEDS,self.fresh)
        self.assertEqual(self.runner.lua.globals().requests,1)
        self.assertEqual(self.runner.lua.globals().gold,520)
        self.assertTrue(self.executor.reconcile(1,self.readback)['confirmed'])
        self.assertEqual(self.p.purchases,[(1,10,60,80)])
    def test_ui_building_location_uses_fresh_gameplay_bridge(self):
        self.runner.lua.execute("city.GetBuildings=function()return {HasBuilding=function()return true end,IsPillaged=function()return false end}end;city.GetID=function()return 10 end;CSC_SERVICE_NATIVE={venues_turn=60,external_venues={{owner=1,city=10,type='BUILDING_LIGHTHOUSE',plot=100,functioning=true}}}")
        self.executor.request(self.d,NEEDS,self.fresh)
        self.assertTrue(self.executor.reconcile(1,self.readback)['confirmed'])
    def test_stale_gameplay_customer_bridge_rejects_before_purchase(self):
        self.runner.lua.execute("city.GetBuildings=function()return {HasBuilding=function()return true end,IsPillaged=function()return false end}end;city.GetID=function()return 10 end;CSC_SERVICE_NATIVE={venues_turn=59,external_venues={}}")
        with self.assertRaises(Exception):self.executor.request(self.d,NEEDS,self.fresh)
        self.assertEqual(self.runner.lua.globals().requests,0)
    def test_changed_native_price_sends_no_purchase(self):
        self.runner.lua.globals().price=90
        with self.assertRaises(Exception):self.executor.request(self.d,NEEDS,self.fresh)
        self.assertEqual(self.runner.lua.globals().requests,0)
        self.assertIn(1,self.executor.pending)
    def test_native_denial_sends_no_purchase(self):
        self.runner.lua.globals().purchasable=False
        with self.assertRaises(Exception):self.executor.request(self.d,NEEDS,self.fresh)
        self.assertEqual(self.runner.lua.globals().requests,0)
    def test_native_human_recheck(self):
        self.runner.lua.globals().human=True
        with self.assertRaises(Exception):self.executor.request(self.d,NEEDS,self.fresh)
        self.assertEqual(self.runner.lua.globals().requests,0)
    def test_native_unrevealed_recheck(self):
        self.runner.lua.globals().reveal=False
        with self.assertRaises(Exception):self.executor.request(self.d,NEEDS,self.fresh)
        self.assertEqual(self.runner.lua.globals().requests,0)
    def test_native_potential_legality_recheck(self):
        self.runner.lua.globals().potential=False
        with self.assertRaises(Exception):self.executor.request(self.d,NEEDS,self.fresh)
        self.assertEqual(self.runner.lua.globals().requests,0)
    def test_native_service_customer_pillage_recheck(self):
        self.runner.lua.globals().venue_pillaged=True
        with self.assertRaises(Exception):self.executor.request(self.d,NEEDS,self.fresh)
        self.assertEqual(self.runner.lua.globals().requests,0)
    def test_native_service_research_recheck(self):
        self.runner.lua.globals().civic_ready=False
        with self.assertRaises(Exception):self.executor.request(self.d,NEEDS,self.fresh)
        self.assertEqual(self.runner.lua.globals().requests,0)
    def test_unknown_native_purchase_parameter_no_dispatch(self):
        with self.assertRaises(AssertionError):self.executor.request(self.d,NEEDS,lambda c:(c,BUDGET,60,None,'BUILDING_LIGHTHOUSE'))
        self.assertEqual(self.runner.calls,0)
    def test_active_autoplay_no_dispatch(self):
        self.executor.boundary=lambda:{'turn':60,'autoplay_active':True}
        with self.assertRaises(AssertionError):self.executor.request(self.d,NEEDS,self.fresh)
        self.assertEqual(self.runner.calls,0)
    def test_mutations_opt_in(self):
        self.executor.allow_mutations=False
        with self.assertRaises(AssertionError):self.executor.request(self.d,NEEDS,self.fresh)
        self.assertEqual(self.runner.calls,0)
    def test_no_auto_resend_after_ambiguous_timeout(self):
        def fail(*args,**kwargs):raise TimeoutError('ACK unknown')
        self.runner.cmd=fail
        with self.assertRaises(TimeoutError):self.executor.request(self.d,NEEDS,self.fresh)
        restarted=PurchaseExecutor(Planner(),self.runner,self.path,allow_mutations=True,boundary=self.executor.boundary)
        with self.assertRaises(AssertionError):restarted.request(self.d,NEEDS,self.fresh)
        self.assertIn(1,restarted.pending)
    def test_ack_without_gold_deduction_not_confirmation(self):
        self.executor.request(self.d,NEEDS,self.fresh)
        self.assertFalse(self.executor.reconcile(1,lambda e:{'city_owner':1,'plot_owner':1,'gold':600,'turn':60})['confirmed'])
    def test_restart_retains_spent_budget_and_cooldown(self):
        self.executor.request(self.d,NEEDS,self.fresh);self.executor.reconcile(1,self.readback)
        restarted=PurchaseExecutor(Planner(),self.runner,self.path)
        self.assertEqual(restarted.planner.purchases,[(1,10,60,80)])


class AdapterFixture:
    def __init__(self,runner):self.runner=runner;self.placed=False;self.commits=0;self.scans=0
    def wide_candidates(self,pid,city,turn):self.scans+=1;return [candidate()]
    def needs(self,pid,city):return NEEDS
    def budget(self,pid):return Budget(int(self.runner.lua.globals().gold))
    def refresh(self,c):
        if self.placed:return None
        if self.runner.lua.globals().owner==1:return replace(c,missing_tiles=(),purchase_plot=None,price=0,current_legal=True)
        return c
    def purchase_facts(self,c):return self.refresh(c),self.budget(1),60,True,'BUILDING_LIGHTHOUSE'
    def purchase_readback(self,e):
        g=self.runner.lua.globals();return {'city_owner':1,'plot_owner':g.owner,'gold':g.gold,'turn':g.turn}
    def place_zero(self,c):
        self.commits+=1;self.placed=True
        return {'verified':True,'owner':1,'plot':42,'quarter':'TAILORS',
                'progress_before':0,'progress_after':0,'cost_before':45,'cost_after':45,
                'native_incomplete':True,'queue_unchanged':True}


class CoordinatorTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(dir=SCRATCH);self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name)/'ledger.ndjson';self.runner=LuaRunner();self.adapter=AdapterFixture(self.runner)
        self.coordinator=Coordinator(self.runner,self.path,allow_mutations=True,
                                     boundary=lambda:{'turn':60,'autoplay_active':False})
    def test_purchase_then_fresh_placement_without_duplicate(self):
        first=self.coordinator.cycle(1,[10],60,self.adapter)
        self.assertEqual(first[0]['action'],'pending_purchase');self.assertEqual(self.adapter.commits,0)
        second=self.coordinator.cycle(1,[10],60,self.adapter)
        self.assertEqual(second[0]['action'],'foundation_confirmed');self.assertEqual(self.adapter.commits,1)
        self.assertEqual(self.coordinator.cycle(1,[10],60,self.adapter),[])
        self.assertEqual(self.runner.lua.globals().gold,520);self.assertEqual(self.adapter.scans,1)
    def test_dry_run_never_dispatches(self):
        self.coordinator.allow_mutations=False
        self.assertEqual(self.coordinator.cycle(1,[10],60,self.adapter)[0]['action'],'proposal')
        self.assertEqual(self.runner.calls,0);self.assertEqual(self.runner.lua.globals().gold,600)
    def test_events_only_dirty_never_mutate(self):
        for _ in range(10):self.coordinator.event(1,10)
        self.assertEqual(len(self.coordinator.planner.dirty),1);self.assertEqual(self.runner.calls,0)
    def test_other_player_cache_not_executed(self):
        self.coordinator.planner.update(2,20,60,[candidate(player=2,city=20)])
        self.assertEqual(len(self.coordinator.cycle(1,[10],60,self.adapter)),1)
    def test_ambiguous_foundation_not_replayed_after_restart(self):
        self.runner.lua.globals().owner=1
        def fail(c):raise TimeoutError('Foundation return unknown')
        self.adapter.place_zero=fail
        with self.assertRaises(TimeoutError):self.coordinator.cycle(1,[10],60,self.adapter)
        restarted=Coordinator(self.runner,self.path,allow_mutations=True,boundary=self.coordinator.executor.boundary)
        self.assertEqual(restarted.cycle(1,[10],60,self.adapter)[0]['action'],'already_attempted_foundation')


class ObservationTests(unittest.TestCase):
    def setUp(self):
        self.o={'player':1,'city':10,'turn':60,'eligible_ai':True,'human':False,'era':2,
                'tiles':[{'index':42,'owner':-1,'revealed':True,'within_city_reach':True,'neighbors':[81,100],
                          'potential_legal':{'TAILORS':True},'native_projection_verified':True,
                          'native_purchasable':True,'price':80,'frontier_danger':False},
                         {'index':81,'owner':1,'resource':'WOOL','revealed':True,'material_visible':True,
                          'base_for':['TAILORS']},
                         {'index':100,'owner':1,'district':'HARBOR','revealed':True}],
                'venues':[{'plot':100,'owner':1,'type':'BUILDING_LIGHTHOUSE','functioning':True}],
                'readiness':{'dockmaster':{'research_ready':True,'ready_in_turns':10,'confidence':.9}}}
    def test_unowned_source_with_owned_chain_generates_service(self):
        c=next(c for c in build_candidates(self.o)if c.service=='dockmaster')
        self.assertEqual((c.missing_tiles,c.base,c.customer_plot),((42,),1,100))
        self.assertEqual(Planner().evaluate(c,NEEDS,BUDGET,60).action,'purchase')
    def test_source_and_material_both_unowned_do_not_become_one_tile_purchase(self):
        self.o['tiles'][1]['owner']=-1
        self.assertEqual(build_candidates(self.o),[])
    def test_owned_source_missing_material_can_buy_that_resource(self):
        self.o['tiles'][0]['owner']=1;self.o['tiles'][1].update(owner=-1,native_purchasable=True,price=80)
        c=next(c for c in build_candidates(self.o)if c.service=='dockmaster')
        self.assertEqual(c.purchase_plot,81)
    def test_same_type_only_exclusion(self):
        self.o['same_quarter_types']=['BAKERS']
        self.assertTrue(any(c.service=='dockmaster'for c in build_candidates(self.o)))
        self.o['same_quarter_types'].append('TAILORS');self.assertEqual(build_candidates(self.o),[])
    def test_wrong_customer_owner_not_a_service(self):
        self.o['venues'][0]['owner']=2
        self.assertFalse(any(c.service for c in build_candidates(self.o)))
    def test_pillaged_customer_not_a_service(self):
        self.o['venues'][0]['functioning']=False
        self.assertFalse(any(c.service for c in build_candidates(self.o)))
    def test_resource_on_source_is_not_cleared_for_placement(self):
        self.o['tiles'][0]['resource']='WOOL';self.assertEqual(build_candidates(self.o),[])
    def test_unknown_readiness_no_aggressive_purchase(self):
        self.o['readiness']={}
        c=next(c for c in build_candidates(self.o)if c.service=='dockmaster')
        self.assertEqual(Planner().evaluate(c,NEEDS,BUDGET,60).action,'watch')



class NativePreflightTests(unittest.TestCase):
    """Execute the adapter's real generated UI code with Civ's typed assert."""
    def probe(self,producible=True):
        from .native_adapter import NativeAdapter
        from .execution import lua
        from lupa.lua51 import LuaRuntime
        class PreflightComplete(Exception):pass
        engine=LuaRuntime(unpack_returned_tuples=True)
        engine.execute("""
local stockassert=assert
assert=function(ok,message)
 if message~=nil and type(message)~='string'then error("bad argument #2 to 'assert' (string expected, got table)")end
 return stockassert(ok,message)
end
producible=true;captured=false
local queue={HasBeenPlaced=function()return false end,CanProduce=function()return producible,{reason='native details'}end}
local city={GetBuildQueue=function()return queue end}
local plot={GetX=function()return 3 end,GetY=function()return 4 end}
Map={GetPlotByIndex=function()return plot end}
CityOperationTypes={PARAM_DISTRICT_TYPE=1,PARAM_X=2,PARAM_Y=3,BUILD=4}
CityOperationResults={PLOTS=1}
CityManager={GetCity=function()return city end,GetOperationTargets=function(c,op,pars)
 -- Enumerate with district-only args; a coordinate-scoped query does not
 -- represent the legal-target enumeration used by the native collector.
 if pars[2]~=nil or pars[3]~=nil then return {[1]={}}end
 return {[1]={42}}end,
 CanStartOperation=function()return true,{reason='native operation details'}end}
CSC_FOUNDATION_UI={Capture=function()captured=true end,Export=function()end}
""")
        engine.globals().producible=producible
        class Runner:
            def __init__(self):self.mutations=0
            def cmd(self,code,state,label):
                if label.startswith('ui-before-'):
                    engine.execute(code)
                    raise PreflightComplete()
                if label.startswith('zero-commit-'):
                    self.mutations+=1;raise AssertionError('Never commit in readonly preflight test')
                return 'CSC_FOUNDATION_EXPORT={"plan":[{"plot":42}]}\n'
        runner=Runner();adapter=NativeAdapter(runner,Path('unused'),lambda *a:None,lua)
        adapter.turn=18;adapter.cities[1,10]={'district_defs':{'TAILORS':{'Hash':12,'Index':37}}}
        c=candidate(player=1,city=10,plot=42)
        if producible:
            with self.assertRaises(PreflightComplete):adapter.place_zero(c)
            self.assertTrue(engine.globals().captured)
        else:
            with self.assertRaisesRegex(Exception,'District no longer producible'):adapter.place_zero(c)
            self.assertFalse(engine.globals().captured)
        self.assertEqual(runner.mutations,0)
    def test_real_generated_preflight_ignores_native_reason_table(self):self.probe(True)
    def test_real_generated_preflight_enumerates_before_XY_exactcheck(self):self.probe(True)
    def test_real_generated_preflight_rejects_false_with_string_message(self):self.probe(False)


def main():
    global SCRATCH
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--lua51-path',type=Path,required=True);parser.add_argument('--output',type=Path);parser.add_argument('--scratch',type=Path,required=True)
    args=parser.parse_args();sys.path.insert(0,str(args.lua51_path));SCRATCH=args.scratch
    suite=unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromTestCase(cls)for cls in (PolicyTests,ExecutionTests,CoordinatorTests,ObservationTests,NativePreflightTests))
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    if args.output:args.output.write_text(json.dumps({'passed':result.wasSuccessful(),'tests':result.testsRun,'purchase_path':'actual Lua5.1 with simulated engine; no live gold spent','native_connections':0},indent=2)+'\n',encoding='utf-8')
    return 0 if result.wasSuccessful()else 1


if __name__=='__main__':raise SystemExit(main())
