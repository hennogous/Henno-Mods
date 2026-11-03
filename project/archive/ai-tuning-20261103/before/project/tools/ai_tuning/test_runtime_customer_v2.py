"""Portable actual Lua51 staged v2 bridge/host fixtures, with no native IO.

Uses the maintained economic fixture and deliberately supplies only UI Members
for customer district lookup. Native bindings here are test doubles, not proof
that a new live UI context has been validated.
"""
import copy,hashlib,json,os,sys,unittest
from pathlib import Path
from lupa.lua51 import LuaRuntime
ROOT=Path(os.environ.get('CSC_V2_REPO_ROOT',Path(__file__).resolve().parents[3]))
sys.path.insert(0,str(ROOT/'project/tools/ai_tuning'))
import test_selective_screen as screen
HERE=Path(os.environ['CSC_V2_SOURCE_DIR'])if os.environ.get('CSC_V2_SOURCE_DIR')else ROOT/'Civ Supply Chains/Lua_UI/AI'
BEFORE=Path(os.environ['CSC_V2_BEFORE_DIR'])if os.environ.get('CSC_V2_BEFORE_DIR')else None
CASES=HERE/'actual150-cases.json'if os.environ.get('CSC_V2_SOURCE_DIR')else ROOT/'project/tools/ai_tuning/fixtures/customer_planner_v2_actual150.json'
HOST=(HERE/'CSC_AI_Assistance.lua').read_text()
POLICY=(HERE/'CSC_AI_OpportunityPolicy.lua').read_text()
UI_PATH=Path(os.environ.get('CSC_V2_UI_SOURCE_FILE',HERE/'CSC_AI_AssistanceUI.lua'))
UI=UI_PATH.read_text()
SETUP=r'''
properties.CSC_AI_SELECTIVE_SCREEN_V1={version=2};hasGranary=true
local function rows(items)return setmetatable(items,{__call=function(self)local i=0;return function()i=i+1;return self[i]end end})end
GameInfo.BuildingPrereqs=rows({});GameInfo.MutuallyExclusiveBuildings=rows({})
GameInfo.CSC_Stage3CustomerTransactions=rows({})
GameInfo.Buildings.BUILDING_CSC_BAKERS_RIVER_ACCESS={Index=101,BuildingType='BUILDING_CSC_BAKERS_RIVER_ACCESS'}
GameInfo.Buildings.BUILDING_CSC_BAKERS_NO_RIVER_ACCESS={Index=102,BuildingType='BUILDING_CSC_BAKERS_NO_RIVER_ACCESS'}
for _,row in pairs(GameInfo.Buildings)do if type(row)=='table'and row.Index then GameInfo.Buildings[row.Index]=row end end
GameInfo.Improvements[10].Index=10
GameInfo.Districts.DISTRICT_CITY_CENTER.Hash=0;GameInfo.Districts.DISTRICT_CITY_CENTER.RequiresPopulation=0
Cities={GetPlotPurchaseCity=function(plot)return plot.idx>=4 and city2 or city end}
for _,plot in pairs(plots)do plot.IsRiver=function()return river==true end;plot.CanHaveDistrict=function()return potential~=false end end
districts.Members=function(self)local a={};for i=0,self:GetNumDistricts()-1 do a[#a+1]=self:GetDistrictByIndex(i)end;return ipairs(a)end
local ds2=city2:GetDistricts();ds2.Members=function(self)return ipairs({self:GetDistrictByIndex(0)})end
-- UI-only collection must not accidentally gain the Gameplay-only getter.
savedLocation=districts.GetDistrictAtLocation;districts.GetDistrictAtLocation=nil;ds2.GetDistrictAtLocation=nil
initCalls=0
CSC_Adjacency.Initialize=function()initCalls=initCalls+1;CSC_Adjacency.ByDistrict={DISTRICT_CSC_BAKERS_QUARTER=rules or{{ID='real4',ModifierOwner='DistrictModifiers',ProvideType='SelfBonus',YieldType='YIELD_PRODUCTION',YieldChange=1,count=4}}}end
CSC_Adjacency.Eligible=function(row)return row.eligible~=false end
CSC_Adjacency.Count=function(row)return row.count end
CSC_Adjacency.Amount=function(row,count)return count*row.YieldChange end
CSC_Adjacency.Bounds=function()return 1,1 end
function uiTags()local items={{Type='RESOURCE_BASE',Tag='CLASS_CSC_BAKERS_BASE'},{Type='RESOURCE_SPEC',Tag='CLASS_CSC_BAKERS_SPEC'}};local i=0;return function()i=i+1;return items[i]end end
GameInfo.TypeTags=uiTags
function packet(spec,fresh)return ExposedMembers.CSC_AI_AssistanceUI.ReadPlannerV2(7,11,'BAKERS',3,1,spec, true,fresh~=false)end
function typed(spec)
 local p=assert(packet(spec));local v=CSC_AI_CustomerPlannerV2;local result=v.Evaluate({version=2},p)
 assert(result.status=='candidate',result.status)
 candidate.intent_version=2;candidate.materials=spec and{1,spec}or{1};candidate.v2_intent=v.Intent(result,candidate.materials)
 return result
end
'''
FUTURE=r'''
local function rows(a)return function()local i=0;return function()i=i+1;return a[i]end end end
GameInfo.Districts.DISTRICT_HARBOR={Index=8,Hash=88,DistrictType='DISTRICT_HARBOR',RequiresPopulation=1}
GameInfo.Districts.DISTRICT_CSC_BAKERS_QUARTER.RequiresPopulation=0
GameInfo.Buildings.BUILDING_LIGHTHOUSE={Index=120,BuildingType='BUILDING_LIGHTHOUSE'}
GameInfo.CSC_QuarterCustomerBuildings=rows({{QuarterKey='BAKERS',ProducerStage=2,DistrictType='DISTRICT_HARBOR',BuildingType='BUILDING_LIGHTHOUSE'}})
plots[7].owner=7;local adjacent=Map.GetAdjacentPlot
Map.GetAdjacentPlot=function(x,y,d)if x==1 and y==1 and d==3 then return plots[7]end;return adjacent(x,y,d)end
plots[7].CanHaveDistrict=function(self,...)potentialCalls=(potentialCalls or 0)+1;assert(select('#',...)==3);local index,pid,cid=...;assert(index==8 and pid==7 and cid==12);return potential~=false end
local ds=city2:GetDistricts();ds.GetNumZonedDistrictsRequiringPopulation=function()return capacityUsed or 2 end;ds.GetNumAllowedDistrictsRequiringPopulation=function()return 3 end
queue.CanProduce=function()return futureCanProduce~=false end;queue.HasBeenPlaced=function()return nativeCommitted==true end
CityOperationTypes={BUILD=1,PARAM_DISTRICT_TYPE='district',PARAM_X='x',PARAM_Y='y'};CityOperationResults={PLOTS='plots'}
CityManager.GetOperationTargets=function()return{plots=exactTarget==false and{}or{7}}end
CityManager.CanStartOperation=function()return exactOperation~=false end
'''

def make(extra=''):
 lua=screen.SelectiveScreen().make('',host=HOST,policy=POLICY)
 lua.execute(SETUP)
 # Execute the complete UI chunk, including dependency/bootstrap phase. The
 # bridge's native quote doubles stay independent of the planning module tests.
 lua.execute('local previous=ExposedMembers.CSC_AI_AssistanceUI\n'+UI+'\nlocal current=ExposedMembers.CSC_AI_AssistanceUI;for key,value in pairs(previous)do if key~="ReadPlannerV2"and key~="PlannerBootstrap"then current[key]=value end end')
 lua.execute(extra)
 return lua

class Bridge(unittest.TestCase):
 def test_future_specific_plot_requires_three_arg_potential_and_separate_exact_permission(self):
  l=make(FUTURE);r=l.eval('typed()');p=r.customer
  self.assertEqual(p.readiness,'future_plot');self.assertEqual(p.plot,7)
  self.assertTrue(p.potential);self.assertTrue(p.exact_target);self.assertTrue(p.exact_operation)
  self.assertEqual(p.planned_Quarter_capacity,0);self.assertEqual(p.capacity_used,2);self.assertEqual(p.capacity_allowed,3)
  self.assertIn('unverified',p.alternatives_status);self.assertIsNone(p.native_score)
  self.assertGreater(l.globals().potentialCalls,0);self.assertEqual(l.globals().assignments,0)
  for change in('potential=false','futureCanProduce=false','exactTarget=false','exactOperation=false','capacityUsed=3','nativeCommitted=true'):
   l=make(FUTURE+change);r=l.eval('CSC_AI_CustomerPlannerV2.Evaluate({version=2},packet())');self.assertNotEqual(r.status,'candidate',change)
 def test_future_district_locked_even_currently_selected_defers_first_pilot(self):
  l=make(FUTURE+"GameInfo.Technologies.TECH_HARBOR={Index=9};GameInfo.Districts.DISTRICT_HARBOR.PrereqTech='TECH_HARBOR';player.GetTechs=function()return{HasTech=function(self,i)return i~=9 end,GetResearchingTech=function()return 9 end}end;futureCanProduce=false")
  p=l.eval('packet().customer_paths[1]');self.assertTrue(p.unlock_plausible);self.assertFalse(p.unlock_owned);self.assertFalse(p.can_produce);self.assertFalse(p.legal_plot)
  r=l.eval('CSC_AI_CustomerPlannerV2.Evaluate({version=2},packet())');self.assertNotEqual(r.status,'candidate')
 def test_same_city_future_capacity_includes_only_population_requiring_Quarter(self):
  l=make(FUTURE+"Cities.GetPlotPurchaseCity=function()return city end;plots[7].CanHaveDistrict=function(self,...)assert(select('#',...)==3);return true end;districts.GetNumZonedDistrictsRequiringPopulation=function()return 2 end;districts.GetNumAllowedDistrictsRequiringPopulation=function()return 3 end;GameInfo.Districts.DISTRICT_CSC_BAKERS_QUARTER.RequiresPopulation=1")
  # Future plot belongs to city11 here; required count2 + Quarter1 leaves no slot.
  p=l.eval('packet().customer_paths[1]');self.assertEqual(p.planned_Quarter_capacity,1);self.assertFalse(p.capacity_plausible)
 def test_runtime_embedded_implementation_and_UI_tail_match_reviewed_sources(self):
  self.assertEqual(POLICY.count('-- Pure customer-aware v2 policy'),1)
  self.assertEqual((HERE/'CSC_AI_AssistanceUI.lua').read_text().count('-- V2 evidence bridge.'),1)
  if (HERE/'CSC_AI_CustomerPlannerV2.lua').is_file():self.assertTrue(POLICY.endswith((HERE/'CSC_AI_CustomerPlannerV2.lua').read_text()))
  if (HERE/'runtime-ui-v2.lua').is_file():self.assertTrue((HERE/'CSC_AI_AssistanceUI.lua').read_text().endswith((HERE/'runtime-ui-v2.lua').read_text()))
 def test_UI_Members_without_Gameplay_location_getter_initializes_rules_once_and_reads_Base(self):
  l=make();p=l.eval('packet()');self.assertEqual(l.globals().initCalls,1);self.assertTrue(p.base.working)
  self.assertEqual(p.customer_paths[1].plot,0);self.assertEqual(p.customer_paths[1].readiness,'actual')
  self.assertTrue(p.customer_paths[1].district_functioning);self.assertTrue(p.customer_paths[1].raw_district_pillaged)
  self.assertEqual(p.quality.current.real.YIELD_PRODUCTION,4);self.assertIsNone(l.eval('districts.GetDistrictAtLocation'))
  l.eval('packet()');self.assertEqual(l.globals().initCalls,1)
 def test_missing_rules_and_unsupported_UI_evidence_defer_not_fake_zero(self):
  for setup in ('rules={}', 'CSC_Adjacency.Count=nil'):
   l=make(setup);p,error=l.eval('packet()');self.assertIsNone(p);self.assertTrue('unavailable'in error)
 def test_customer_missing_building_is_conditional_not_actual_and_pillage_rejected(self):
  l=make('hasGranary=false');r=l.eval('typed()');self.assertEqual(r.customer.readiness,'existing_district');self.assertTrue(r.conditional)
  l=make('customerPillaged=true');r=l.eval('CSC_AI_CustomerPlannerV2.Evaluate({version=2},packet())');self.assertNotEqual(r.status,'candidate')
 def test_cache_scope_and_fresh_admission_see_changed_customer(self):
  l=make('ExposedMembers.CSC_AI_AssistanceUI.scope={};packet(nil,false);customerPillaged=true')
  self.assertTrue(l.eval('packet(nil,false).customer_paths[1].building_functioning'))
  self.assertFalse(l.eval('packet().customer_paths[1].building_functioning'))
 def test_foreign_material_and_missing_native_option_never_credible(self):
  for change in ('plots[1].owner=8','plots[1].imp=-1;GameInfo.Improvement_ValidResources=nil'):
   l=make(change);r=l.eval('CSC_AI_CustomerPlannerV2.Evaluate({version=2},packet())');self.assertNotEqual(r.status,'candidate')
 def test_bound_customer_and_Both_materials_cannot_silently_retarget(self):
  l=make('typed(2);local p=packet(2);p.customer_paths[1].plot=77;bad=p')
  result,error=l.eval('CSC_AI_CustomerPlannerV2.Revalidate(candidate.v2_intent,bad)');self.assertIsNone(result);self.assertEqual(error,'intent_customer_identity_changed')
  l.execute('bad=packet(2);bad.spec.resource=99')
  result,error=l.eval('CSC_AI_CustomerPlannerV2.Revalidate(candidate.v2_intent,bad)');self.assertIsNone(result);self.assertEqual(error,'intent_Spec_identity_changed')
 def test_named_building_branch_allows_exact_active_unlock_not_unselected_tree(self):
  l=make("GameInfo.Technologies.TECH_MILL={Index=8};GameInfo.Buildings.BUILDING_CSC_BAKERS_WIND_MILL.PrereqTech='TECH_MILL';player.GetTechs=function()return{HasTech=function(self,i)return i~=8 end,GetResearchingTech=function()return researching or -1 end}end;researching=8")
  r=l.eval('typed()');self.assertTrue(r.conditional);self.assertEqual(r.real.projected.assumptions,None) # assumptions live beside projection, not in real totals
  self.assertEqual(r.real.assumptions.producer_steps[2].unlock_conditions[1].type,'TECH_MILL')
  l.execute('researching=-1');r=l.eval('CSC_AI_CustomerPlannerV2.Evaluate({version=2},packet())');self.assertNotEqual(r.status,'candidate')
 def test_river_flag_and_mutually_exclusive_producer_branch_project_without_grant(self):
  setup="""river=true;GameInfo.Buildings.BUILDING_CSC_BAKERS_WATER_MILL={Index=103,BuildingType='BUILDING_CSC_BAKERS_WATER_MILL',PrereqDistrict='DISTRICT_CSC_BAKERS_QUARTER'}
  local function rows(a)return function()local i=0;return function()i=i+1;return a[i]end end end
  GameInfo.CSC_QuarterFlowBuildings=rows({{QuarterKey='BAKERS',Stage=2,BuildingType='BUILDING_CSC_BAKERS_WATER_MILL'}})
  GameInfo.BuildingPrereqs=rows({{Building='BUILDING_CSC_BAKERS_WATER_MILL',PrereqBuilding='BUILDING_CSC_BAKERS_RIVER_ACCESS'}})
  GameInfo.MutuallyExclusiveBuildings=rows({{Building='BUILDING_CSC_BAKERS_WATER_MILL',MutuallyExclusiveBuilding='BUILDING_CSC_BAKERS_NO_RIVER_ACCESS'}})
  """
  l=make(setup);r=l.eval('typed()');self.assertEqual(r.customer.producer,'BUILDING_CSC_BAKERS_WATER_MILL')
  self.assertEqual(r.real.assumptions.producer_steps[1].type,'BUILDING_CSC_BAKERS_RIVER_ACCESS')
  self.assertFalse(l.eval('city:GetBuildings():HasBuilding(101)'));self.assertEqual(len(l.globals().goldChanges),0)
  l.execute('river=false');r=l.eval('CSC_AI_CustomerPlannerV2.Evaluate({version=2},packet())');self.assertNotEqual(r.status,'candidate')
 def test_named_Temple_after_Shrine_exact_branch(self):
  l=make("""local function rows(a)return function()local i=0;return function()i=i+1;return a[i]end end end
  GameInfo.Buildings.BUILDING_SHRINE={Index=110,BuildingType='BUILDING_SHRINE'}
  GameInfo.Buildings.BUILDING_GRANARY.BuildingType='BUILDING_TEMPLE';GameInfo.Buildings.BUILDING_TEMPLE=GameInfo.Buildings.BUILDING_GRANARY
  GameInfo.BuildingPrereqs=rows({{Building='BUILDING_TEMPLE',PrereqBuilding='BUILDING_SHRINE'}})
  GameInfo.CSC_QuarterCustomerBuildings=rows({{QuarterKey='BAKERS',ProducerStage=2,DistrictType='DISTRICT_CITY_CENTER',BuildingType='BUILDING_TEMPLE'}})
  hasGranary=false""")
  r=l.eval('typed()');steps=r.customer.customer_construction_steps;self.assertEqual(steps[1].type,'BUILDING_SHRINE');self.assertEqual(steps[2].type,'BUILDING_TEMPLE')

class Host(unittest.TestCase):
 def test_v2_open_cap_blocks_another_typed_plan_but_reconciliation_does_not_resend(self):
  l=make('typed()');self.assertTrue(l.eval('CSC_AI_Assistance.Acquire(candidate,3,{3})'))
  l.execute("turn=201;local p=assert(ExposedMembers.CSC_AI_AssistanceUI.ReadPlannerV2(7,12,'BAKERS',7,5,nil,true,true));local r=CSC_AI_CustomerPlannerV2.Evaluate({version=2},p);assert(r.status=='candidate');other.intent_version=2;other.materials={5};other.v2_intent=CSC_AI_CustomerPlannerV2.Intent(r,other.materials)")
  self.assertFalse(l.eval('CSC_AI_Assistance.Acquire(other,7,{7})'));self.assertEqual(l.eval('inspect().last_decision.reason'),'open_chain_cap')
  self.assertEqual(l.globals().assignments,1);self.assertEqual(l.globals().wallet,960)
 def test_callback_discovery_exposes_bounded_missing_binding_reason(self):
  l=make('ExposedMembers.CSC_AI_AssistanceUI.ReadPlannerV2=function()return nil,"fixture_missing_UI_binding"end')
  l.execute('turnHandler(7)');d=l.eval('inspect().last_planner_discovery')
  self.assertGreater(d.rejected.fixture_missing_UI_binding,0);self.assertEqual(d.candidates,0)
  self.assertEqual(d.last_missing_fact.reason,'fixture_missing_UI_binding');self.assertEqual(l.globals().assignments,0)
  prior=l.eval('inspect().planner_diagnostics.evidence_error_count');self.assertGreater(prior,0)
  l.execute('turn=201;ExposedMembers.CSC_AI_AssistanceUI.ReadPlannerV2=function()return nil,"different_missing_binding"end;turnHandler(7)')
  d=l.eval('inspect().planner_diagnostics');self.assertGreater(d.evidence_error_count,prior)
  self.assertEqual(d.first_error.reason,'fixture_missing_UI_binding');self.assertEqual(d.last_error.reason,'different_missing_binding')
 def test_first_candidate_evidence_is_detached_admission_time_not_recomputed_checkpoint(self):
  l=make();l.execute('turnHandler(7)');d=l.eval('inspect().planner_diagnostics')
  self.assertEqual(d.evidence_error_count,0);self.assertIsNotNone(d.first_packet);self.assertIsNotNone(d.first_candidate)
  self.assertEqual(d.first_candidate.captured_turn,200);self.assertFalse(d.first_candidate.action_authorization)
  self.assertEqual(d.first_candidate.current_real_combined,4)
  l.execute('customerPillaged=true;turn=205')
  self.assertEqual(l.eval('inspect().planner_diagnostics.first_candidate.captured_turn'),200)
 def test_readonly_target_inspection_cannot_create_natural_callback_evidence(self):
  l=make('properties.CSC_AI_ASSISTANCE_V1_INITIAL_HUMANS={["0"]=true};typed()');before=len(l.globals().properties)
  result=l.eval('CSC_AI_Assistance.InspectPlannerV2(candidate)');self.assertEqual(result.result.status,'candidate')
  self.assertIsNone(l.eval('inspect().planner_diagnostics.first_candidate'));self.assertEqual(l.eval('inspect().planner_diagnostics.evidence_error_count'),0);self.assertEqual(len(l.globals().properties),before)
 def test_Base_only_fresh_real4_uses_same_purchase_and_zero_percent_foundation(self):
  l=make('typed()');self.assertTrue(l.eval('CSC_AI_Assistance.Acquire(candidate,3,{3})'))
  self.assertEqual(l.globals().wallet,960);self.assertEqual(l.globals().assignments,1)
  l.execute('districts.GetDistrictAtLocation=savedLocation;turn=201')
  self.assertTrue(l.eval('CSC_AI_Assistance.Place(candidate)'));self.assertEqual(l.globals().creations,1)
  row=l.eval('inspect().records[1]');self.assertEqual(len(row.materials),1);self.assertEqual(row.intent_version,2)
  self.assertEqual(row.v2_intent.kind,'base_only_real4');self.assertEqual(row.admission.captured_turn,201)
  self.assertIn('ADMISSION-TIME',row.admission.value_scope);self.assertEqual(row.first_admission.captured_turn,200)
 def test_late_quality_or_customer_loss_refuses_before_claim_grant_assignment(self):
  for change in ('rules={{ID="low",ModifierOwner="DistrictModifiers",ProvideType="SelfBonus",YieldType="YIELD_PRODUCTION",YieldChange=0,count=0}};ExposedMembers.CSC_AI_AssistanceUI.plannerCoreReady=nil', 'customerPillaged=true','plots[1].res=6'):
   l=make('typed();'+change);self.assertFalse(l.eval('CSC_AI_Assistance.Acquire(candidate,3,{3})'))
   self.assertEqual(l.globals().assignments,0);self.assertEqual(l.globals().wallet,1000);self.assertIsNone(l.eval('properties.CSC_AI_ASSISTANCE_V1_PENDING_7'))
 def test_cap_and_missing_config_block_new_start_reconciliation_independent(self):
  l=make('typed();lag=true');self.assertTrue(l.eval('CSC_AI_Assistance.Acquire(candidate,3,{3})'))
  self.assertIsNotNone(l.eval('properties.CSC_AI_ASSISTANCE_V1_PENDING_7'))
  l.execute('properties.CSC_AI_SELECTIVE_SCREEN_V1=nil;lag=false;CSC_AI_Assistance.Reconcile();CSC_AI_Assistance.Reconcile()')
  self.assertEqual(l.globals().wallet,960);self.assertEqual(l.globals().assignments,1)
  self.assertFalse(l.eval('CSC_AI_Assistance.Acquire(other,7,{7})'));self.assertEqual(l.eval('inspect().summary.open'),1)
 def test_typed_state_survives_coldload_and_rejects_silent_new_customer(self):
  l=make('typed()');self.assertTrue(l.eval('CSC_AI_Assistance.Acquire(candidate,3,{3})'))
  l.execute('turn=201;candidate.v2_intent=nil;hasGranary=false');l.execute(HOST)
  # Same exact site may improve readiness, but a different selected footprint is forbidden.
  self.assertTrue(l.eval('typed().status=="candidate"'))
  l.execute("properties.CSC_AI_SELECTIVE_SCREEN_STATE_V1.records['7:11:BAKERS:3'].v2_intent.customer.plot=99")
  l.execute('candidate.v2_intent=nil');p=l.eval('CSC_AI_Assistance.InspectPlannerV2(candidate)');self.assertIsNone(p.result);self.assertEqual(p.error,'intent_customer_identity_changed')
 def test_deterministic_Base_only_ties_and_reservation_conflicts(self):
  l=make('typed();a=candidate;b={player=7,city=11,quarter="BAKERS",source=3,materials={1,2},base=1,spec=1,v2_evidence={}}')
  self.assertIsInstance(l.eval('CSC_AI_OpportunityPolicy.PlannerBetter(a,b)'),bool)
  l.execute('r={player=7,city=12,quarter="BAKERS",source=7,materials={5,6},status="open",v2_intent={customer={plot=3,readiness="future_plot"}}}')
  self.assertEqual(l.eval('CSC_AI_OpportunityPolicy.ScreenConflicts(candidate,{r=r},{})'),'source_over_reserved_customer')
 def test_operational_promise_releases_shared_actual_customer_footprint(self):
  l=make('typed();record={player=7,city=12,source=7,materials={5,6},status="operational",v2_intent={customer={plot=0,readiness="future_plot"}}}')
  self.assertIsNone(l.eval('CSC_AI_OpportunityPolicy.ScreenConflicts(candidate,{r=record},{})'))
  l.execute('record.status="open"');self.assertEqual(l.eval('CSC_AI_OpportunityPolicy.ScreenConflicts(candidate,{r=record},{})'),'conflicting_future_customer_reservation')
 def test_unaffordable_v2_never_claims(self):
  l=make('typed();wallet=0;subsidy=false');self.assertFalse(l.eval('CSC_AI_Assistance.Acquire(candidate,3,{3})'));self.assertIsNone(l.eval('properties.CSC_AI_SELECTIVE_SCREEN_STATE_V1'))
 def test_legacy_nil_v1_exact_action_property_and_receipt_differential(self):
  if BEFORE is None:self.skipTest('Explicit CSC_V2_BEFORE_DIR archived source pair required; not compared to itself')
  def plain(v):return{k:plain(x)for k,x in v.items()}if hasattr(v,'items')else v
  for config in ('','enable();'):
   old=screen.SelectiveScreen().make(config,host=(BEFORE/'before-CSC_AI_Assistance.lua').read_text(),policy=(BEFORE/'before-CSC_AI_OpportunityPolicy.lua').read_text())
   new=screen.SelectiveScreen().make(config,host=HOST,policy=POLICY)
   for l in(old,new):l.execute('turnHandler(7);turn=201;turnHandler(7)')
   self.assertEqual(plain(old.globals().properties),plain(new.globals().properties));self.assertEqual((old.globals().wallet,old.globals().assignments,old.globals().creations),(new.globals().wallet,new.globals().assignments,new.globals().creations))

class ArchivedAcceptance(unittest.TestCase):
 def test_actual_four_failed_sites_do_not_get_customer_credit_from_Both_alone(self):
  evidence=json.loads(CASES.read_text());self.assertEqual(len(evidence['cases']),6)
  l=LuaRuntime(unpack_returned_tuples=True);l.execute(POLICY);V=l.globals().CSC_AI_CustomerPlannerV2
  for case in evidence['cases']:
   if case['cohort']!='candidate':continue
   q=case['quarter'];base=next(m for m in q['materials']if m['working_base'])
   self.assertTrue(any(m['working_spec']for m in q['materials']))
   # These are terminal geometry counterexamples, not live placement permission.
   # Essential source/role booleans below isolate customer admission policy only.
   paths=[]
   for adjacent in case['adjacent_districts']:
    district=adjacent['district']
    for row in evidence['registry']['CSC_QuarterCustomerBuildings']:
     if row['QuarterKey']==q['quarter']and row['ProducerStage']==2 and row['DistrictType']==district['type']:
      self.assertFalse(any(b['type']==row['BuildingType']for b in adjacent['buildings']))
      paths.append(dict(source='accepted terminal150 geometry',mapping_valid=True,stage=2,producer=q['producers'][0]['type'],district=row['DistrictType'],building=row['BuildingType'],plot=district['plot'],readiness='existing_district',owned=True,adjacent=True,footprint_conflict=False,district_complete=district['complete'],district_functioning=district['functioning'],building_present=False,unlock_plausible=None))
   packet=dict(identity=case['identity'],original_AI=True,source_legal=True,source_can_produce=True,source_conflict=False,base=dict(plot=base['plot'],resource=base['resource'],mapped=True,revealed=True,resource_visible=True,district=-1,owner=q['player'],working=True),both_credible=True,customer_paths=paths)
   result=V.Evaluate(l.table_from({'version':2}),l.table_from(packet,recursive=True));self.assertNotEqual(result.status,'candidate',case['name'])
   if q['source']==2711:
    self.assertEqual(len(paths),1);self.assertEqual(paths[0]['plot'],2710);self.assertEqual(paths[0]['building'],'BUILDING_GRANARY')
    self.assertEqual(result.reasons[1],'existing_customer_building_prerequisites_unknown')
   else:self.assertEqual(len(paths),0);self.assertEqual(result.status,'declined_no_customer_path')
   self.assertEqual(case['native_future_customer_plot_legality'],'UNOBSERVED')
 def test_actual_inland_Temple_paths_qualify_without_Harbor_or_Stage2_customer(self):
  evidence=json.loads(CASES.read_text());l=LuaRuntime(unpack_returned_tuples=True);l.execute(POLICY)
  for case in evidence['cases']:
   if case['cohort']!='reference':continue
   q=case['quarter'];self.assertTrue(any(m['working_base']for m in q['materials']))
   self.assertFalse(any(a['district']['type']=='DISTRICT_HARBOR'for a in case['adjacent_districts']))
   matches=[]
   for row in evidence['registry']['CSC_Stage3CustomerTransactions']:
    if row['SellerDistrictType']!='DISTRICT_CSC_TAILORS_QUARTER':continue
    for a in case['adjacent_districts']:
     b=next((b for b in a['buildings']if b['type']==row['CustomerBuildingType']and b['pillaged']is False),None)
     if a['district']['type']==row['CustomerDistrictType']and b:
      p=dict(source='accepted terminal150 registered path',mapping_valid=True,stage=3,transaction=row['TransactionId'],producer=row['SellerBuildingType'],district=row['CustomerDistrictType'],building=b['type'],plot=a['district']['plot'],readiness='actual',owned=a['district']['owner']==q['player'],adjacent=True,footprint_conflict=False,district_complete=a['district']['complete'],district_functioning=a['district']['functioning'],building_functioning=True)
      self.assertEqual(l.globals().CSC_AI_CustomerPlannerV2.Customer(l.table_from(p)),3);matches.append(p)
   self.assertTrue(any(p['building']=='BUILDING_TEMPLE'for p in matches))
   self.assertEqual(case['effect_properties']['CSC_TAILORS_STAGE_3_EFFECT_FAITH']['value'],1)
   # Effect flag corroborates structure, never a payment/net-benefit assertion.

if __name__=='__main__':unittest.main()
