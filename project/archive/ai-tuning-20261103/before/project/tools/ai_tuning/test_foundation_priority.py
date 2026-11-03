"""Actual Lua51 callback decisions plus isolated native-schema SQL deltas."""
import collections,os,sqlite3,sys,unittest,zlib
from pathlib import Path
from lupa.lua51 import LuaRuntime
ROOT=Path(__file__).resolve().parents[3];MOD=ROOT/'Civ Supply Chains'
ROLE=(MOD/'ModSupport/ModSupport_RH_AI_Roles.lua').read_text()
FOOTER=ROLE[ROLE.index('-- Native strategy callbacks:'):]
SQL=(MOD/'ModSupport/ModSupport_RH_AI.sql').read_text().split('-- BEGIN CSC RH FOUNDATION PRIORITY V8')[1].split('-- END CSC RH FOUNDATION PRIORITY V8')[0]
ADJ=(MOD/'Data/CSC_AI.sql').read_text();ADJ=ADJ[ADJ.index('CREATE TEMP TABLE CSC_AI_SalesPairs'):ADJ.index('-- A deliberately broad Base-material')]
# Drop only temporary pair-generation tables, as the normal file does later.
ADJ+='\nDROP TABLE CSC_AI_Edges;DROP TABLE CSC_AI_DistrictVariants;DROP TABLE CSC_AI_SalesPairs;'
FIXTURE=r"""
modeValue='RH';identity={['0']=true};M={};Game={};major=true;alive=true;cityOwner=1;plotOwner=1;complete=false;exists=true;wrongType=false;hasCity=true
function mode()return modeValue end
function humans()return identity end
local index={'1:7:BAKERS:40'}
receipt={status='confirmed',source=40,quarter='BAKERS'}
function Game:GetProperty(k)if k=='CSC_AI_ASSISTANCE_V1_FOUNDATION_INDEX'then return index end;if k=='CSC_AI_ASSISTANCE_V1_FOUNDATION_1:7:BAKERS:40'then return receipt end end
function Game.GetCurrentGameTurn()return 30 end
GameInfo={Districts={DISTRICT_CSC_BAKERS_QUARTER={Index=8},DISTRICT_CSC_TAILORS_QUARTER={Index=9}}}
district={GetType=function()return wrongType and 9 or 8 end,IsComplete=function()return complete end}
districts={GetDistrictAtLocation=function(self,x,y)assert(x==2 and y==4);return exists and district or nil end}
city={GetOwner=function()return cityOwner end,GetDistricts=function()return districts end}
cities={FindID=function(self,cid)assert(cid==7);return hasCity and city or nil end}
player={IsAlive=function()return alive end,IsMajor=function()return major end,GetCities=function()return cities end}
Players={[1]=player,[0]=player}
plot={GetOwner=function()return plotOwner end,GetX=function()return 2 end,GetY=function()return 4 end}
Map={GetPlotByIndex=function(i)assert(i==40);return plot end}
local function ev()local fn;return{Add=function(f)fn=f end,Fire=function(...)return fn(...)end}end
GameEvents={CSC_RH_Finish_BAKERS=ev(),CSC_RH_Finish_TAILORS=ev()}
function bake(pid)return GameEvents.CSC_RH_Finish_BAKERS.Fire(pid or 1,0)end
function tailor()return GameEvents.CSC_RH_Finish_TAILORS.Fire(1,0)end
"""
class Callbacks(unittest.TestCase):
 def make(self,setup=''):
  l=LuaRuntime();l.execute(FIXTURE);l.execute(setup);l.execute(FOOTER);return l
 def test_confirmed_exact_original_incomplete_activates(self):
  l=self.make();self.assertTrue(l.eval('bake()'));self.assertEqual(l.eval('M.foundation_priority.registered'),2);self.assertEqual(l.eval("M.foundation_priority.states['1:BAKERS'].count"),1)
 def test_other_quarter_is_not_favoured(self):self.assertFalse(self.make().eval('tailor()'))
 def test_completed_switches_off(self):
  l=self.make();self.assertTrue(l.eval('bake()'));l.execute('complete=true');self.assertFalse(l.eval('bake()'));self.assertEqual(l.eval('#M.foundation_priority.transitions'),2)
 def test_capture_and_missing_original_city(self):
  for setup in('cityOwner=2','plotOwner=2','hasCity=false','exists=false','wrongType=true'):
   with self.subTest(setup=setup):self.assertFalse(self.make(setup).eval('bake()'))
 def test_requested_and_mismatched_receipts_fail_closed(self):
  for setup in("receipt.status='requested'","receipt.quarter='TAILORS'",'receipt.source=41','receipt=nil'):
   with self.subTest(setup=setup):self.assertFalse(self.make(setup).eval('bake()'))
 def test_unknown_original_human_and_nonalive_major(self):
  for setup in("identity={['1']=true}",'identity=nil','major=false','alive=false',"modeValue='BASIC'","modeValue='OFF'"):
   with self.subTest(setup=setup):self.assertFalse(self.make(setup).eval('bake()'))
 def test_same_turn_confirmation_not_stale_cached(self):
  l=self.make("receipt.status='requested'");self.assertFalse(l.eval('bake()'));l.execute("receipt.status='confirmed'");self.assertTrue(l.eval('bake()'))
 def test_errors_fail_closed_and_are_visible(self):
  l=self.make("cities.FindID=function()error('fixture missing binding')end");self.assertFalse(l.eval('bake()'));self.assertEqual(l.eval('#M.foundation_priority.errors'),1)
 def test_no_queue_legality_or_mutation_api_needed(self):
  l=self.make();self.assertTrue(l.eval('bake()'));self.assertEqual(l.eval('#M.foundation_priority.errors'),0)
 def test_unchanged_callback_state_does_not_grow_transitions(self):
  l=self.make();l.eval('bake()');l.eval('bake()');self.assertEqual(l.eval('#M.foundation_priority.transitions'),1);self.assertEqual(l.eval('M.foundation_priority.calls'),2)
class NativeSQL(unittest.TestCase):
 def setUp(self):
  path=os.environ.get('CSC_TEST_RH_STRATEGY_DATABASE');self.assertTrue(path,'Preserved native database required')
  self.db=sqlite3.connect(':memory:');self.db.create_function('Make_Hash',1,lambda x:zlib.crc32(x.encode()))
  with sqlite3.connect(Path(path).resolve().as_uri()+'?mode=ro',uri=True)as source:source.backup(self.db)
 def tearDown(self):self.db.close()
 def apply(self):
  self.db.executescript(SQL)
  self.db.execute("DELETE FROM District_Adjacencies WHERE YieldChangeId LIKE 'CSC_AI_SALES_%'")
  self.db.execute("DELETE FROM Adjacency_YieldChanges WHERE ID LIKE 'CSC_AI_SALES_%'")
  self.db.executescript(ADJ)
 def test_native_schema_inputs_and_direction(self):
  from profile_foundation_priority import validate_database
  self.apply();r=validate_database(self.db);self.assertEqual(len(r['strategies']),2);self.assertGreater(r['reverse_edges'],0)
 def test_existing_RH_favoured_rows_preserved(self):
  before=collections.Counter(self.db.execute('SELECT * FROM AiFavoredItems'));self.apply();after=collections.Counter(self.db.execute('SELECT * FROM AiFavoredItems'))
  self.assertFalse(before-after);self.assertEqual(sum((after-before).values()),2)
 def test_repeat_sql_is_idempotent(self):
  self.apply();tables=('Types','Strategies','StrategyConditions','AiListTypes','AiLists','Strategy_Priorities','AiFavoredItems');first={t:list(self.db.execute('SELECT * FROM '+t))for t in tables};self.db.executescript(SQL);self.assertEqual(first,{t:list(self.db.execute('SELECT * FROM '+t))for t in tables})
 def test_preflight_rejects_wrong_priority(self):
  from profile_foundation_priority import validate_database
  self.apply();self.db.execute("UPDATE AiFavoredItems SET Value=0 WHERE ListType='CSC_RH_Finish_BAKERS'")
  with self.assertRaises(AssertionError):validate_database(self.db)
if __name__=='__main__':unittest.main()

