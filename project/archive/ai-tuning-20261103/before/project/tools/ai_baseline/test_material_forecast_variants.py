import unittest,sqlite3,copy
from pathlib import Path
from material_forecast_variants import variant,declared_database_delta,changed_tables,GATE_TABLES,HARVEST_TABLES,verify_native_guard_scope

class Variants(unittest.TestCase):
 def fixture(self):
  base={k:dict(rows=1,sha256='same')for k in('Resource_YieldChanges','Boosts','Units','AiFavoredItems','AiListTypes','AiLists','Strategy_Priorities')};raw={**base,'Resource_YieldChanges':dict(rows=2,sha256='raw')};gate={**raw,**{k:dict(rows=2,sha256='gate')for k in GATE_TABLES}};return base,raw,gate
 def test_existing_reference_default_unchanged(self):self.assertEqual(variant('S','reference',None)['runtime_deltas'],4)
 def test_gate_is_explicit514_six_deltas(self):
  v=variant('S','raw-resource','boost-gate-v3');self.assertTrue(v['measured_allocation']);self.assertTrue(v['boost_gate']);self.assertEqual(v['files'],514);self.assertEqual(v['runtime_deltas'],6)
 def test_undeclared_branch_or_wrong_arm_rejected(self):
  for arm,branch in(('reference','boost-gate-v3'),('raw-resource','new'),('other',None)):
   with self.subTest(arm=arm,branch=branch),self.assertRaises(AssertionError):variant('S',arm,branch)
 def test_exact_declared_database_scope(self):
  base,raw,gate=self.fixture();self.assertEqual(set(declared_database_delta(base,gate,treatment=True,boost_gate=True,raw_control=raw)),GATE_TABLES|{'Resource_YieldChanges'})
 def test_boost_rule_or_unit_change_rejected_even_in_otherwise_valid_gate(self):
  for field in('Boosts','Units'):
   base,raw,gate=self.fixture();gate[field]=dict(rows=2,sha256='wrong')
   with self.subTest(field=field),self.assertRaises(AssertionError):declared_database_delta(base,gate,treatment=True,boost_gate=True,raw_control=raw)
 def test_missing_declared_gate_table_rejected(self):
  base,raw,gate=self.fixture();gate['AiLists']=raw['AiLists']
  with self.assertRaises(AssertionError):declared_database_delta(base,gate,treatment=True,boost_gate=True,raw_control=raw)
 def test_gate_cannot_implicitly_weaken_existing_default(self):
  base,raw,gate=self.fixture()
  with self.assertRaises(AssertionError):declared_database_delta(base,gate,treatment=True)
 def test_bad_raw_control_scope_rejected(self):
  base,raw,gate=self.fixture();raw['Units']=dict(rows=2,sha256='wrong')
  with self.assertRaises(AssertionError):declared_database_delta(base,gate,treatment=True,boost_gate=True,raw_control=raw)

class NativeHarvestVariant(unittest.TestCase):
 def test_guard_scope_does_not_accept_boost_preferences(self):
  base,raw,gate=Variants().fixture()
  with self.assertRaises(AssertionError):declared_database_delta(base,gate,treatment=True,native_harvest_guard=True,raw_control=raw)
 def test_native_guard_has_exact_three_table_scope(self):
  base,raw,_=Variants().fixture()
  for key in HARVEST_TABLES:base[key]=raw[key]=dict(rows=1,sha256='same')
  guard={**raw,**{key:dict(rows=2,sha256='guard')for key in HARVEST_TABLES}}
  self.assertEqual(set(declared_database_delta(base,guard,treatment=True,native_harvest_guard=True,raw_control=raw)),HARVEST_TABLES|{'Resource_YieldChanges'})
 def test_distinct_interventions_cannot_be_conflated(self):
  base,raw,gate=Variants().fixture()
  with self.assertRaises(AssertionError):declared_database_delta(base,gate,treatment=True,boost_gate=True,native_harvest_guard=True,raw_control=raw)
 def test_guard_variant_uses_correct_extra_SQL_and_raw_control(self):
  v=variant('S','raw-resource','native-harvest-v4');self.assertTrue(v['needs_raw_control']);self.assertFalse(v['boost_gate']);self.assertTrue(v['native_harvest_guard']);self.assertEqual(v['extra_SQL'],'CSC_AI_NativeHarvestGuard_Diagnostic.sql');self.assertEqual(v['runtime_deltas'],6)

class ExistingRuleVariant(unittest.TestCase):
 def test_existing_rule_uses_unchanged_raw513_and_live_ownership_gate(self):
  v=variant('S','raw-resource','native-harvest-live-v4');self.assertTrue(v['runtime_harvest_rule']);self.assertTrue(v['ready_for_native']);self.assertTrue(v['needs_raw_control']);self.assertEqual(v['files'],513);self.assertEqual(v['runtime_deltas'],5);self.assertFalse(v['native_harvest_guard']);self.assertFalse(v['boost_gate'])
 def test_unexecuted_SQL_proposal_is_not_native_ready(self):self.assertFalse(variant('S','raw-resource','native-harvest-v4')['ready_for_native'])

class MeasuredRuleVariant(unittest.TestCase):
 def test_measured_legality_is_explicit_and_uses_distinct_branch_token(self):
  v=variant('S','raw-resource','native-harvest-live-v4b');self.assertTrue(v['measured_rule_legality']);self.assertEqual(v['runtime_rule_token'],'native-harvest-live-v4b');self.assertTrue(v['runtime_harvest_rule']);self.assertEqual(v['files'],513)

class OwnerScope(unittest.TestCase):
 def fixture(self):
  db=sqlite3.connect(':memory:');db.executescript("CREATE TABLE Modifiers(ModifierId,ModifierType,OwnerRequirementSetId);CREATE TABLE ModifierArguments(ModifierId,Name,Value);CREATE TABLE DynamicModifiers(ModifierType,CollectionType,EffectType);CREATE TABLE TraitModifiers(TraitType,ModifierId);CREATE TABLE LeaderTraits(LeaderType,TraitType);")
  mod='MOD_CSC_AI_NATIVE_HARVEST_GUARD_DIAGNOSTIC';typ='MODIFIER_PLAYER_ADJUST_PREVENT_HARVEST_RESOURCE'
  db.execute('INSERT INTO Modifiers VALUES(?,?,?)',(mod,typ,'REQSET_CSC_AI_SUPPLY_AI'));db.execute('INSERT INTO ModifierArguments VALUES(?,?,?)',(mod,'Enable','1'));db.execute('INSERT INTO DynamicModifiers VALUES(?,?,?)',(typ,'COLLECTION_OWNER','EFFECT_ADJUST_PLAYER_PREVENT_HARVEST_RESOURCE'))
  players=[dict(id=i,leader='LEADER_'+str(i),human=i==0)for i in range(6)];expected=[]
  for i in range(6):
   trait='TRAIT_'+str(i);db.execute('INSERT INTO LeaderTraits VALUES(?,?)',('LEADER_'+str(i),trait))
   if i:db.execute('INSERT INTO TraitModifiers VALUES(?,?)',(trait,mod));expected.append(dict(player=i,leader='LEADER_'+str(i),trait=trait))
  return db,players,expected
 def test_declared_loaded_scope_is_not_behavior_proof(self):
  db,p,e=self.fixture();self.addCleanup(db.close);v=verify_native_guard_scope(db,p,e);self.assertTrue(v['observer0_excluded_by_unique_traits']);self.assertFalse(v['native_prevention_effect_proven']);self.assertFalse(v['per_material_or_Quarter_targeted'])
 def test_observer_sharing_trait_rejected_even_with_observer_human_flag_false(self):
  db,p,e=self.fixture();self.addCleanup(db.close);p[0]['human']=False;db.execute('INSERT INTO LeaderTraits VALUES(?,?)',(p[0]['leader'],e[0]['trait']))
  with self.assertRaises(AssertionError):verify_native_guard_scope(db,p,e)
 def test_human_target_or_changed_leader_rejected(self):
  for field,value in(('human',True),('leader','OTHER')):
   db,p,e=self.fixture();self.addCleanup(db.close);p[1][field]=value
   with self.subTest(field=field),self.assertRaises(AssertionError):verify_native_guard_scope(db,p,e)
 def test_extra_owner_attachment_rejected(self):
  db,p,e=self.fixture();self.addCleanup(db.close);db.execute("INSERT INTO TraitModifiers VALUES('TRAIT_0','MOD_CSC_AI_NATIVE_HARVEST_GUARD_DIAGNOSTIC')")
  with self.assertRaises(AssertionError):verify_native_guard_scope(db,p,e)
 def test_wrong_effect_or_extra_argument_rejected(self):
  for effect in(True,False):
   db,p,e=self.fixture();self.addCleanup(db.close)
   if effect:db.execute("UPDATE DynamicModifiers SET EffectType='WRONG'")
   else:db.execute("INSERT INTO ModifierArguments VALUES('MOD_CSC_AI_NATIVE_HARVEST_GUARD_DIAGNOSTIC','Other','1')")
   with self.subTest(effect=effect),self.assertRaises(AssertionError):verify_native_guard_scope(db,p,e)

if __name__=='__main__':unittest.main()
