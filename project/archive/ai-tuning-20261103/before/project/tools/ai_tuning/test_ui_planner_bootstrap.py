"""Cold UI/foreign include environments using actual Lua51 module source.

The contextual include implementation is a test double: this demonstrates a
plausible failure mechanism and the eager-capture repair, not Civ's C include ABI.
No native client, files outside this H directory, or engine world is changed.
"""
import os,sys,unittest
from pathlib import Path
from lupa.lua51 import LuaRuntime
ROOT=Path(os.environ.get('CSC_V2_REPO_ROOT',Path(__file__).resolve().parents[3]))
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'project/tools/ai_tuning'))
import test_selective_screen as screen
import test_runtime_customer_v2 as runtime_fixture
AI=ROOT/'Civ Supply Chains/Lua_UI/AI'
CORE=(ROOT/'Civ Supply Chains/Lua_UI/Adjacencies/CSC_AdjacencyCore.lua').read_text()
POLICY=(AI/'CSC_AI_OpportunityPolicy.lua').read_text()
SOURCE=Path(os.environ.get('CSC_UI_BOOTSTRAP_SOURCE_FILE',AI/'CSC_AI_AssistanceUI.lua'))
BEFORE=Path(os.environ['CSC_UI_BOOTSTRAP_BEFORE_FILE'])if os.environ.get('CSC_UI_BOOTSTRAP_BEFORE_FILE')else None
OLD=BEFORE.read_text()if BEFORE else None
NEW=SOURCE.read_text()

def make(source=NEW,missing=None,broken=None):
 l=screen.SelectiveScreen().make('',host=(AI/'CSC_AI_Assistance.lua').read_text(),policy=POLICY)
 l.execute(runtime_fixture.SETUP)
 l.execute(r'''
 local function rows(items)return function()local i=0;return function()i=i+1;return items[i]end end end
 DefenseTypes={DISTRICT_GARRISON=0,DISTRICT_OUTER=1} -- explicit fixture enum, not a native presence observation
 GameInfo.CSC_AdjacencyObjects=rows({});GameInfo.CSC_AdjacencySources=rows({})
 GameInfo.CSC_AdjacencyProviders=rows({{ProvideType='SelfBonus'}})
 GameInfo.CSC_AdjacencyRules=rows({{ID='fixture_real4',DistrictType='DISTRICT_CSC_BAKERS_QUARTER',ProvideType='SelfBonus',YieldType='YIELD_PRODUCTION',YieldChange=4,AdjacencyType='FROM_UNCONDITIONAL_BONUS',ModifierOwner='DistrictModifiers',Only='Human&AI'}})
 savedQuote=ExposedMembers.CSC_AI_AssistanceUI.Read
 savedProperties=properties;writes=0
 local write=Game.SetProperty;Game.SetProperty=function(...)writes=writes+1;return write(...)end
 moduleSources={};moduleLoads={};initCalls=0
 -- Each UI owns its globals; the fake include's resolver follows activeEnv.
 -- No modules are inherited from Gameplay through the fallback metatable.
 uiEnv=setmetatable({_G=false},{__index=function(t,key)
  if key=='CSC_Adjacency'or key=='CSC_AI_CustomerPlannerV2'or key=='CSC_AI_OpportunityPolicy'then return nil end
  return _G[key]
 end})
 uiEnv._G=uiEnv;gpEnv=_G;activeEnv=uiEnv
 function contextualInclude(name)
  moduleLoads[#moduleLoads+1]={name=name,ui=activeEnv==uiEnv}
  if missingModule==name then return end
  local text=assert(moduleSources[name],'unavailable fixture module:'..name)
  local fn=assert(loadstring(text));setfenv(fn,activeEnv);fn()
  if name=='CSC_AdjacencyCore'and activeEnv==uiEnv then
   local a=uiEnv.CSC_Adjacency;local initialize=a.Initialize
   a.Initialize=function(...)initCalls=initCalls+1;return initialize(...)end
   if brokenCapability then a[brokenCapability]=nil end
  end
 end
 uiEnv.include=contextualInclude
 function loadUI(text)
  activeEnv=uiEnv;local fn=assert(loadstring(text));setfenv(fn,uiEnv);fn()
  -- Native quote behavior is independently covered by maintained UI fixtures;
  -- this fixture isolates actual helper loading/projection through the bridge.
  ExposedMembers.CSC_AI_AssistanceUI.Read=savedQuote
 end
 function callReader(foreign)
  activeEnv=foreign and gpEnv or uiEnv
  return ExposedMembers.CSC_AI_AssistanceUI.ReadPlannerV2(7,11,'BAKERS',3,1,nil,true,true)
 end
 ''')
 l.globals().moduleSources['CSC_AdjacencyCore']=CORE
 l.globals().moduleSources['CSC_AI_OpportunityPolicy']=POLICY
 l.globals().missingModule=missing;l.globals().brokenCapability=broken
 l.globals().loadUI(source)
 return l

class ColdBootstrap(unittest.TestCase):
 def test_cold_UI_module_types_capabilities_present_before_any_candidate_and_no_initialize(self):
  l=make();b=l.eval('ExposedMembers.CSC_AI_AssistanceUI.PlannerBootstrap()')
  self.assertEqual(b.phase,'UI_chunk');self.assertEqual(b.adjacency_type,'table');self.assertEqual(b.policy_type,'table');self.assertEqual(b.policy_version,2)
  self.assertTrue(b.adjacency_initialize);self.assertTrue(b.policy_project);self.assertTrue(b.policy_evaluate);self.assertTrue(b.policy_revalidate)
  for key in ('adjacency_resource_visible','adjacency_count','adjacency_eligible','adjacency_amount','adjacency_bounds'):self.assertTrue(b[key])
  self.assertFalse(b.rules_initialized);self.assertEqual(l.globals().initCalls,0);self.assertEqual(len(l.globals().moduleLoads),2);self.assertEqual(l.globals().writes,0)
  self.assertIsNone(l.eval('properties.CSC_AI_SELECTIVE_SCREEN_STATE_V1'))
 def test_foreign_callback_uses_actual_UI_captured_modules_even_after_global_change(self):
  l=make();l.execute('uiEnv.CSC_Adjacency=nil;uiEnv.CSC_AI_CustomerPlannerV2=nil')
  packet=l.globals().callReader(True)
  self.assertEqual(packet.quality.current.real.YIELD_PRODUCTION,4);self.assertEqual(packet.customer_paths[1].building,'BUILDING_GRANARY')
  self.assertEqual(l.globals().initCalls,1);self.assertEqual(len(l.globals().moduleLoads),2);self.assertEqual(l.globals().writes,0)
  l.globals().callReader(True);self.assertEqual(l.globals().initCalls,1)
 def test_old_lazy_reader_fails_in_the_contextual_model_but_same_UI_context_works(self):
  if OLD is None:self.skipTest('Explicit archived CSC_UI_BOOTSTRAP_BEFORE_FILE needed for differential, not compared to itself')
  old=make(OLD);packet,error=old.globals().callReader(True)
  self.assertIsNone(packet);self.assertIn('assertion failed',error)
  self.assertIsNone(old.eval('rawget(uiEnv,"CSC_Adjacency")'));self.assertIsNone(old.eval('rawget(uiEnv,"CSC_AI_CustomerPlannerV2")'))
  old=make(OLD);packet=old.globals().callReader(False);self.assertEqual(packet.quality.current.real.YIELD_PRODUCTION,4)
 def test_missing_each_module_has_distinct_named_failure_and_bridge_remains_registered(self):
  for module,expected in [('CSC_AdjacencyCore','planner_UI_adjacency_module_unavailable'),('CSC_AI_OpportunityPolicy','planner_UI_policy_module_unavailable')]:
   l=make(missing=module);packet,error=l.globals().callReader(True)
   self.assertIsNone(packet);self.assertEqual(error,expected);self.assertEqual(l.globals().writes,0)
   self.assertEqual(l.eval('type(ExposedMembers.CSC_AI_AssistanceUI.Read)'),'function')
 def test_missing_capability_has_named_failure_without_reimport_or_world_effect(self):
  l=make(broken='Count');packet,error=l.globals().callReader(True)
  self.assertIsNone(packet);self.assertEqual(error,'planner_UI_adjacency_capability_unavailable:Count')
  self.assertEqual(len(l.globals().moduleLoads),2);self.assertEqual(l.globals().writes,0);self.assertEqual(l.globals().assignments,0)
 def test_repeated_bootstrap_readback_does_not_initialize_or_create_natural_evidence(self):
  l=make();before=len(l.globals().properties)
  for _ in range(4):l.eval('ExposedMembers.CSC_AI_AssistanceUI.PlannerBootstrap()')
  self.assertEqual(l.globals().initCalls,0);self.assertEqual(l.globals().writes,0);self.assertEqual(len(l.globals().properties),before)
  self.assertIsNone(l.eval('properties.CSC_AI_SELECTIVE_SCREEN_STATE_V1'))

if __name__=='__main__':unittest.main()
