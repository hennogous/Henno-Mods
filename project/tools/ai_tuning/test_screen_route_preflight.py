"""Portable actual Lua51 pre-economic route facts; no native access.

CSC_SCREEN_ROUTE_SOURCE_DIR reviews staged Lua; default uses canonical sources.
Only the differential case needs an explicit CSC_SCREEN_ROUTE_BEFORE_DIR.
"""
import os,sys,unittest,re
from pathlib import Path
ROOT=Path(os.environ.get('CSC_SCREEN_REPO_ROOT',Path(__file__).resolve().parents[3]))
sys.path.insert(0,str(ROOT/'project/tools/ai_tuning'))
import test_selective_screen as screen
import test_profiles as profiles
AI=Path(os.environ.get('CSC_SCREEN_ROUTE_SOURCE_DIR',ROOT/'Civ Supply Chains/Lua_UI/AI'))
HOST=(AI/'CSC_AI_Assistance.lua').read_text(encoding='utf-8')
POLICY=(AI/'CSC_AI_OpportunityPolicy.lua').read_text(encoding='utf-8')
ONE_CITY="player.GetCities=function()return{Members=function()return ipairs({city})end}end;plots[2].owner=-1;"
class RoutePreflight(unittest.TestCase):
 def make(self,setup='enable();',host=HOST,policy=POLICY):return screen.SelectiveScreen().make(setup,host=host,policy=policy)
 def wrap(self,expression):return "local old=ExposedMembers.CSC_AI_AssistanceUI.Read;ExposedMembers.CSC_AI_AssistanceUI.Read=function(...)local f=old(...);local index=select(5,...);if index==2 then "+expression+" end;return f end;"
 def test_all_future_purchase_facts_required_but_future_reach_price_not_required(self):
  lua=self.make();p=lua.globals().CSC_AI_OpportunityPolicy;route=lua.table_from([3,2]);quotes=lua.table_from({3:dict(owner=-1,revealed=True,in_range=True,reach=True,price=40),2:dict(owner=-1,revealed=True,in_range=True,reach=False,price=0)},recursive=True)
  self.assertTrue(p.ScreenRouteQuotes(route,quotes));self.assertTrue(p.ScreenRouteQuotes(lua.table(),lua.table()))
  for field,value in(('revealed',False),('in_range',False),('owner',7)):
   prior=quotes[2][field];quotes[2][field]=value;self.assertFalse(p.ScreenRouteQuotes(route,quotes));quotes[2][field]=prior
  quotes[2]=None;self.assertFalse(p.ScreenRouteQuotes(route,quotes))
 def test_known_invalid_cached_future_quote_skips_before_any_mutation_claim_or_error(self):
  for expression in('f.in_range=false','f.revealed=false','f.owner=8'):
   lua=self.make('enable();'+ONE_CITY+self.wrap(expression));lua.execute('turnHandler(7)')
   self.assertEqual(lua.globals().assignments,0);self.assertEqual(lua.globals().wallet,1000);self.assertEqual(len(lua.globals().goldChanges),0)
   self.assertIsNone(lua.eval('properties.CSC_AI_ASSISTANCE_V1_PENDING_7'));self.assertIsNone(lua.eval('properties.CSC_AI_ASSISTANCE_V1_ERROR_7'));self.assertEqual(lua.eval('CSC_AI_Assistance.InspectScreen(7).summary.open'),0)
   self.assertGreater(lua.eval("properties.CSC_AI_SELECTIVE_SCREEN_STATE_V1.decisions['7'].rejected.route_quote_unavailable"),0)
 def test_valid_route_with_unknown_future_reach_price_performs_only_fresh_current_step(self):
  lua=self.make('enable();'+ONE_CITY+self.wrap('f.reach=false;f.price=0'));lua.execute('turnHandler(7)')
  self.assertEqual(lua.globals().assignments,1);self.assertEqual(lua.globals().wallet,960);self.assertEqual(lua.globals().plots[3].owner,7);self.assertEqual(lua.globals().plots[2].owner,-1)
  lua.execute('turn=201');self.assertFalse(lua.eval('CSC_AI_Assistance.Acquire(candidate,2,{2})'));self.assertEqual(lua.globals().assignments,1)
 def test_owned_range4_material_not_required_to_be_in_future_purchase_route(self):
  setup="""enable();local distance=Map.GetPlotDistance;Map.GetPlotDistance=function(x,y,a,b)if x==0 and y==0 and a==1 and b==0 then return 4 end;return distance(x,y,a,b)end;
  local read=ExposedMembers.CSC_AI_AssistanceUI.Read;ExposedMembers.CSC_AI_AssistanceUI.Read=function(...)local f=read(...);if select(5,...)==1 then f.in_range=false end;return f end;"""
  lua=self.make(setup);self.assertTrue(lua.eval('CSC_AI_Assistance.Acquire(candidate,3,{3})'));self.assertEqual(lua.globals().assignments,1)
 def test_actual_UI_Read_in_range_is_hard_distance3_independent_of_reach_or_owner(self):
  lua=profiles.NativeUIBindings().fixture();lua.execute('distance=4;Map.GetPlotDistance=function()return distance end;plots[1].owner=7')
  f=lua.eval("ExposedMembers.CSC_AI_AssistanceUI.Read(7,11,'BAKERS',3,1,false)");self.assertFalse(f.in_range);self.assertEqual(f.owner,7)
  lua.execute('distance=3;plots[2].owner=-1');f=lua.eval("ExposedMembers.CSC_AI_AssistanceUI.Read(7,11,'BAKERS',3,2,false)");self.assertTrue(f.in_range);self.assertFalse(f.reach)
 def test_SCREEN_direct_fresh_bad_quote_is_benign_with_compact_diagnostic(self):
  for expression,predicate in(('f.in_range=false','ui_in_range'),('f.revealed=false','ui_revealed'),('f.owner=8','ui_owner')):
   lua=self.make('enable();'+ONE_CITY+self.wrap(expression));self.assertFalse(lua.eval('CSC_AI_Assistance.Acquire(candidate,3,{3,2})'))
   self.assertEqual(lua.globals().assignments,0);self.assertEqual(lua.globals().wallet,1000);self.assertIsNone(lua.eval('properties.CSC_AI_ASSISTANCE_V1_PENDING_7'));self.assertIsNone(lua.eval('properties.CSC_AI_ASSISTANCE_V1_ERROR_7'))
   failure=lua.eval('CSC_AI_Assistance.InspectScreen(7).last_route_failure');self.assertEqual(failure.plot,2);self.assertEqual(failure.predicate,predicate);self.assertEqual(failure.gameplay_owner,-1);self.assertEqual(lua.eval('CSC_AI_Assistance.InspectScreen(7).summary.open'),0)
 def test_SCREEN_future_Gameplay_owner_change_is_benign_before_quote_or_claim(self):
  lua=self.make('enable();'+ONE_CITY+'plots[2].owner=8');self.assertFalse(lua.eval('CSC_AI_Assistance.Acquire(candidate,3,{3,2})'))
  self.assertEqual(lua.globals().assignments,0);self.assertEqual(lua.globals().wallet,1000);failure=lua.eval('CSC_AI_Assistance.InspectScreen(7).last_route_failure');self.assertEqual(failure.plot,2);self.assertEqual(failure.predicate,'gameplay_owner');self.assertEqual(failure.gameplay_owner,8);self.assertIsNone(lua.eval('properties.CSC_AI_ASSISTANCE_V1_PENDING_7'))
 def test_SCREEN_missing_fresh_future_quote_is_benign(self):
  lua=self.make('enable();'+ONE_CITY+'local old=ExposedMembers.CSC_AI_AssistanceUI.Read;ExposedMembers.CSC_AI_AssistanceUI.Read=function(...)if select(5,...)==2 then return nil end;return old(...)end');self.assertFalse(lua.eval('CSC_AI_Assistance.Acquire(candidate,3,{3,2})'));self.assertEqual(lua.globals().assignments,0);self.assertEqual(lua.eval('CSC_AI_Assistance.InspectScreen(7).last_route_failure.predicate'),'quote_unavailable')
 def test_late_change_after_cached_preplan_skips_before_economics_with_diagnostic(self):
  setup='enable();'+ONE_CITY+"local old=ExposedMembers.CSC_AI_AssistanceUI.Read;reads=0;ExposedMembers.CSC_AI_AssistanceUI.Read=function(...)local f=old(...);if select(5,...)==2 then f.reach=false;f.price=0;reads=reads+1;if reads>1 then f.in_range=false end end;return f end;"
  lua=self.make(setup);lua.execute('turnHandler(7)');self.assertEqual(lua.globals().assignments,0);self.assertEqual(lua.globals().wallet,1000);self.assertIsNone(lua.eval('properties.CSC_AI_ASSISTANCE_V1_ERROR_7'));self.assertIsNone(lua.eval('properties.CSC_AI_ASSISTANCE_V1_PENDING_7'));self.assertEqual(lua.eval('CSC_AI_Assistance.InspectScreen(7).last_route_failure.predicate'),'ui_in_range');self.assertEqual(lua.eval('CSC_AI_Assistance.InspectScreen(7).summary.open'),0)
 def test_diagnostic_survives_later_legitimate_purchase_without_replay(self):
  lua=self.make('enable();'+ONE_CITY+self.wrap('f.in_range=false'));self.assertFalse(lua.eval('CSC_AI_Assistance.Acquire(candidate,3,{3,2})'));lua.execute('local old=ExposedMembers.CSC_AI_AssistanceUI.Read;ExposedMembers.CSC_AI_AssistanceUI.Read=function(...)local f=old(...);f.in_range=true;return f end;turn=201');self.assertTrue(lua.eval('CSC_AI_Assistance.Acquire(candidate,3,{3,2})'));self.assertEqual(lua.globals().assignments,1);self.assertEqual(lua.eval('CSC_AI_Assistance.InspectScreen(7).last_route_failure.turn'),200)
 def test_current_step_still_requires_native_reach_and_positive_price(self):
  for expression in('f.reach=false','f.price=0'):
   setup='enable();local old=ExposedMembers.CSC_AI_AssistanceUI.Read;ExposedMembers.CSC_AI_AssistanceUI.Read=function(...)local f=old(...);if select(5,...)==3 then '+expression+' end;return f end'
   lua=self.make(setup);self.assertFalse(lua.eval('CSC_AI_Assistance.Acquire(candidate,3,{3})'));self.assertEqual(lua.globals().assignments,0);self.assertEqual(lua.globals().wallet,1000);self.assertEqual(lua.eval('CSC_AI_Assistance.InspectScreen(7).summary.open'),0)
 def test_post_mutation_economic_invariant_still_raises_and_never_resends(self):
  lua=self.make('enable();wallet=50;local old=treasury.ChangeGoldBalance;treasury.ChangeGoldBalance=function(self,v)if v<0 then return end;return old(self,v)end')
  ok,error=lua.eval('pcall(function()CSC_AI_Assistance.Acquire(candidate,3,{3})end)');self.assertFalse(ok);self.assertIn('Exact debit failed',error);self.assertEqual(lua.globals().assignments,1);self.assertEqual(lua.globals().wallet,70);self.assertEqual(lua.eval('properties.CSC_AI_ASSISTANCE_V1_PENDING_7.status'),'debit_requested')
  self.assertFalse(lua.eval('CSC_AI_Assistance.Acquire(candidate,3,{3})'));self.assertEqual(lua.globals().assignments,1);self.assertEqual(lua.globals().wallet,70)
 def test_nil_legacy_exact_actions_properties_and_invalid_route_error_parity(self):
  directory=os.environ.get('CSC_SCREEN_ROUTE_BEFORE_DIR')
  if not directory:self.skipTest('Set CSC_SCREEN_ROUTE_BEFORE_DIR to an archived before-source pair; differential not performed')
  before=Path(directory);host=before/'before-CSC_AI_Assistance.lua';policy=before/'before-CSC_AI_OpportunityPolicy.lua'
  if not host.is_file()or not policy.is_file():self.skipTest('Explicit archived before-source pair is absent; differential not performed')
  before_host=host.read_text(encoding='utf-8');before_policy=policy.read_text(encoding='utf-8')
  if before_host==HOST and before_policy==POLICY:self.skipTest('Archived pair matches current sources; self-comparison is not differential evidence')
  def plain(v):return{k:plain(x)for k,x in v.items()}if hasattr(v,'items')else v
  for setup,action in(('', 'turnHandler(7);turn=201;turnHandler(7)'),(ONE_CITY+self.wrap('f.in_range=false'),'result,error=pcall(function()CSC_AI_Assistance.Acquire(candidate,3,{3,2})end)')):
   old=self.make(setup,before_host,before_policy);new=self.make(setup)
   old.execute(action);new.execute(action);self.assertEqual(plain(old.globals().properties),plain(new.globals().properties));self.assertEqual((old.globals().assignments,old.globals().wallet,plain(old.globals().goldChanges)),(new.globals().assignments,new.globals().wallet,plain(new.globals().goldChanges)));self.assertEqual(old.globals().result,new.globals().result)
   if old.globals().result is not None:self.assertEqual(re.sub(r':\d+:',':LINE:',str(old.globals().error)),re.sub(r':\d+:',':LINE:',str(new.globals().error)))
if __name__=='__main__':unittest.main()
