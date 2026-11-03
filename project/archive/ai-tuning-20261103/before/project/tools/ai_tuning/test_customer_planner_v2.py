"""Portable actual Lua51 v2 policy/model + optional read-only SQL/capture controls."""
import copy,json,os,sys,sqlite3,unittest,hashlib,zlib
from pathlib import Path
from lupa.lua51 import LuaRuntime
ROOT=Path(os.environ.get('CSC_V2_REPO_ROOT',Path(__file__).resolve().parents[3]))
sys.path.insert(0,str(ROOT/'project/tools/ai_tuning'))
from shadow_projection import building_census,project
HERE=Path(os.environ['CSC_V2_SOURCE_DIR'])if os.environ.get('CSC_V2_SOURCE_DIR')else ROOT/'Civ Supply Chains/Lua_UI/AI'
SQL_PATH=HERE/'CSC_AI.sql'if os.environ.get('CSC_V2_SOURCE_DIR')else ROOT/'Civ Supply Chains/Data/CSC_AI.sql'
SOURCE=(HERE/'CSC_AI_OpportunityPolicy.lua').read_text()
def runtime():
 lua=LuaRuntime(unpack_returned_tuples=True);lua.execute(SOURCE);return lua,lua.globals().CSC_AI_CustomerPlannerV2
def packet():
 return dict(identity=dict(player=3,city=11,source=40,quarter='BAKERS',turn=50),original_AI=True,source_legal=True,source_can_produce=True,source_conflict=False,base=dict(plot=41,resource='RESOURCE_WHEAT',mapped=True,revealed=True,resource_visible=True,district=-1,owner=3,working=True),both_credible=False,quality=dict(current=dict(real=dict(YIELD_PRODUCTION=4,YIELD_GOLD=0))),private=dict(YIELD_CSC_AI_PLACEMENT=99),customer_paths=[dict(source='authored unit fixture',mapping_valid=True,stage=2,producer='BUILDING_CSC_BAKERS_WIND_MILL',district='DISTRICT_CITY_CENTER',building='BUILDING_GRANARY',plot=42,readiness='actual',owned=True,adjacent=True,footprint_conflict=False,district_complete=True,district_functioning=True,building_present=True,building_functioning=True)],unknown_secondary_costs=['travel','lost_tile_value','Builder_assignment'])
class Policy(unittest.TestCase):
 def evaluate(self,p):
  l,v=runtime();return l,v.Evaluate(l.table_from(dict(version=2)),l.table_from(p,recursive=True))
 def test_Base_only_real4_positive_and_unknown_secondary_cost_not_veto(self):
  l,row=self.evaluate(packet());self.assertEqual(row.status,'candidate');self.assertEqual(row.kind,'base_only_real4');self.assertEqual(row.current_real_combined,4);self.assertEqual(len(row.unknown_secondary_costs),3);self.assertFalse(row.action_authorization)
 def test_Both_below4_still_requires_concrete_customer(self):
  p=packet();p['both_credible']=True;p['quality']['current']['real']['YIELD_PRODUCTION']=1;l,row=self.evaluate(p);self.assertEqual(row.status,'candidate');self.assertEqual(row.kind,'both');p['customer_paths']=[];l,row=self.evaluate(p);self.assertEqual(row.status,'declined_no_customer_path')
 def test_private_only4_and_wrong_industry_BONUS_not_real_or_Base(self):
  p=packet();p['quality']['current']['real']={};p['private']={'YIELD_CSC_AI_PLACEMENT':4};l,row=self.evaluate(p);self.assertNotEqual(row.status,'candidate')
  p=packet();p['base']['mapped']=False;p['base']['resource']='RESOURCE_COPPER';l,row=self.evaluate(p);self.assertNotEqual(row.status,'candidate')
 def test_actual_existing_future_readiness_and_future_essential_unknown(self):
  p=packet();path=p['customer_paths'][0];path.update(readiness='future_plot',building_present=False,building_functioning=False,legal_plot=True,unlock_plausible=True,capacity_plausible=True);l,row=self.evaluate(p);self.assertEqual(row.status,'candidate');self.assertEqual(row.customer.readiness_rank,1);self.assertIn('unverified',row.customer.alternatives_status)
  path['legal_plot']=None;l,row=self.evaluate(p);self.assertNotEqual(row.status,'candidate')
 def test_Better_alternative_commitment_and_footprint_withhold_future_credit(self):
  for change in(dict(native_commitment=True),dict(native_score=5,alternative_score=6),dict(footprint_conflict=True)):
   p=packet();p['customer_paths'][0].update(readiness='future_plot',legal_plot=True,unlock_plausible=True,capacity_plausible=True,**change);l,row=self.evaluate(p);self.assertNotEqual(row.status,'candidate')
 def test_readiness_order_actual_over_existing_over_future(self):
  p=packet();actual=p['customer_paths'][0];existing=dict(actual,readiness='existing_district',plot=43,building_present=False,unlock_plausible=True);future=dict(actual,readiness='future_plot',plot=44,legal_plot=True,unlock_plausible=True,capacity_plausible=True);p['customer_paths']=[future,existing,actual];l,row=self.evaluate(p);self.assertEqual(row.customer.plot,42)
 def test_credible_future_Base_distinct_from_working_and_typed_fresh_revalidation(self):
  p=packet();p['base'].update(working=False,improvement_option='IMPROVEMENT_FARM',native_valid_option=True,improvement_unlocked=True);l,v=runtime();lp=l.table_from(p,recursive=True);row=v.Evaluate(l.table_from(dict(version=2)),lp);self.assertEqual(row.status,'candidate');self.assertTrue(row.conditional);intent=v.Intent(row,l.table_from([41]));fresh=v.Revalidate(intent,lp);self.assertEqual(fresh.status,'candidate');p['base']['resource']='RESOURCE_COPPER';fresh,error=v.Revalidate(intent,l.table_from(p,recursive=True));self.assertIsNone(fresh);self.assertEqual(error,'intent_Base_identity_changed')
 def test_nil_and_v1_not_opted_into_v2(self):
  l,v=runtime();self.assertEqual(v.Mode(None),'legacy');self.assertEqual(v.Mode(l.table_from(dict(version=1))),'paused')
class Model(unittest.TestCase):
 def test_attachment_multiplicity_pillage_and_unknown_match_durable_model(self):
  l,v=runtime();cities={1:{},2:{},3:{}};inventory={1:{'MILL':True},2:{'MILL':False},3:{'MILL':False}};rule=dict(ID='r',ModifierOwner='BuildingModifiers',WhoIsTheOwner='MILL',CollectionType='COLLECTION_PLAYER_DISTRICTS',eligible=True,ProvideType='SelfBonus',YieldType='YIELD_PRODUCTION',computed_amount=1)
  for rules,inv in(([rule],inventory),([dict(rule,YieldType='YIELD_CSC_AI_PLACEMENT')],inventory),([rule],{1:inventory[1],2:inventory[2]})):
   py=project(dict(rules=rules),1,cities,inv);row=v.Project(l.table_from(dict(rules=rules),recursive=True),1,l.table_from(cities,recursive=True),l.table_from(inv,recursive=True));self.assertEqual(row.real.YIELD_PRODUCTION,py['real']['YIELD_PRODUCTION']);self.assertEqual(row.real.YIELD_GOLD,py['real']['YIELD_GOLD'])
 def test_captured_11_controls_match_existing_model_and_native_control_values(self):
  directory=os.environ.get('CSC_V2_SHADOW_CAPTURE')
  if not directory:self.skipTest('Explicit accepted shadow capture directory required')
  raw=json.loads((Path(directory)/'shadow-initial.json').read_text());core=json.loads((Path(directory)/'initial-census.json').read_text());cities,inventory=building_census(raw,core);l,v=runtime();matched=0
  for control in raw['controls']:
   result=v.Project(l.table_from(control['preview'],recursive=True),control['city'],l.table_from(cities,recursive=True),l.table_from(inventory,recursive=True));self.assertEqual({y:result.real[y]for y in('YIELD_PRODUCTION','YIELD_GOLD')},control['existing_adjacency']);matched+=1
  self.assertEqual(matched,11)
class SQL(unittest.TestCase):
 def test_native_schema_BONUS_only_removal_idempotent_nonBONUS_rows_preserved(self):
  path=os.environ.get('CSC_V2_NATIVE_DATABASE')
  if not path:self.skipTest('Explicit immutable native database reference required')
  path=Path(path);before=hashlib.sha256(path.read_bytes()).hexdigest();src=sqlite3.connect(path.resolve().as_uri()+'?mode=ro',uri=True);db=sqlite3.connect(':memory:');src.backup(db);src.close();db.create_function('Make_Hash',1,lambda value:zlib.crc32(value.encode('utf-8')))
  def table(name):return sorted(db.execute('SELECT * FROM '+name).fetchall(),key=repr)
  tables=('Adjacency_YieldChanges','District_Adjacencies','Modifiers','ModifierArguments','ImprovementModifiers','BuildingModifiers')
  original={name:table(name)for name in tables};columns={name:[c[1]for c in db.execute('PRAGMA table_info('+name+')')]for name in tables};sql=SQL_PATH.read_text();db.executescript(sql);first={name:table(name)for name in tables};db.executescript(sql);self.assertEqual(first,{name:table(name)for name in tables})
  for name in tables:
   old=[row for row in original[name]if 'CSC_AI_BONUS_RESOURCE'not in row];self.assertEqual(old,first[name],name)
  self.assertEqual(db.execute("SELECT COUNT(*) FROM Adjacency_YieldChanges WHERE ID='CSC_AI_BONUS_RESOURCE'").fetchone()[0],0);self.assertEqual(db.execute("SELECT YieldChange FROM Adjacency_YieldChanges WHERE ID='CSC_AI_RIVER'").fetchone()[0],4);db.close();self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),before)
if __name__=='__main__':unittest.main()
