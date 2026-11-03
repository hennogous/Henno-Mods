import sqlite3,unittest
from pathlib import Path
from material_mapped_improvement_forecast import verify_loaded,mapped_pairs,MOD,REQ,SET,PRIVATE
SQL=Path(__file__).with_name('material_mapped_improvement_forecast.sql').read_text()if Path(__file__).with_name('material_mapped_improvement_forecast.sql').exists()else Path(__file__).with_name('experiments').joinpath('material_mapped_improvement_forecast.sql').read_text()

class Coverage(unittest.TestCase):
 def fixture(self,modded=False):
  db=sqlite3.connect(':memory:');self.addCleanup(db.close)
  db.executescript('''CREATE TABLE Resources(ResourceType TEXT PRIMARY KEY);CREATE TABLE TypeTags(Type TEXT,Tag TEXT,PRIMARY KEY(Type,Tag));CREATE TABLE Improvement_ValidResources(ImprovementType TEXT,ResourceType TEXT);CREATE TABLE Improvement_ValidTerrains(ImprovementType TEXT,TerrainType TEXT);CREATE TABLE Improvement_YieldChanges(ImprovementType TEXT,YieldType TEXT,YieldChange INTEGER);CREATE TABLE Requirements(RequirementId TEXT PRIMARY KEY,RequirementType TEXT);CREATE TABLE RequirementArguments(RequirementId TEXT,Name TEXT,Value TEXT,PRIMARY KEY(RequirementId,Name));CREATE TABLE RequirementSets(RequirementSetId TEXT PRIMARY KEY,RequirementSetType TEXT);CREATE TABLE RequirementSetRequirements(RequirementSetId TEXT,RequirementId TEXT,PRIMARY KEY(RequirementSetId,RequirementId));CREATE TABLE Modifiers(ModifierId TEXT PRIMARY KEY,ModifierType TEXT,OwnerRequirementSetId TEXT);CREATE TABLE ModifierArguments(ModifierId TEXT,Name TEXT,Value TEXT,PRIMARY KEY(ModifierId,Name));CREATE TABLE ImprovementModifiers(ImprovementType TEXT,ModifierId TEXT,PRIMARY KEY(ImprovementType,ModifierId));''')
  resources={'WHEAT':('FARM','BAKERS_BASE'),'FLAX':('FARM','TAILORS_BASE'),'SALT':('MINE','BAKERS_SPEC'),'SILVER':('MINE','TAILORS_SPEC'),'HONEY':('CAMP','BAKERS_SPEC'),'CATTLE':('PASTURE','BAKERS_BASE'),'SILK':('PLANTATION','TAILORS_SPEC'),'IRON':('MINE',None)}
  if modded:resources.update(MOD_SALT=('MINE','BAKERS_SPEC'),MOD_FRUIT=('MOD_ORCHARD','TAILORS_SPEC'))
  for name,(typ,tag)in resources.items():
   db.execute('INSERT INTO Resources VALUES(?)',('RESOURCE_'+name,));db.execute('INSERT INTO Improvement_ValidResources VALUES(?,?)',('IMPROVEMENT_'+typ,'RESOURCE_'+name))
   if tag:db.execute('INSERT INTO TypeTags VALUES(?,?)',('RESOURCE_'+name,'CLASS_CSC_'+tag))
  db.execute("INSERT INTO TypeTags VALUES('RESOURCE_FLAX','CLASS_CSC_BAKERS_BASE')")
  db.execute("INSERT INTO Improvement_ValidTerrains VALUES('IMPROVEMENT_MINE','TERRAIN_GRASS')")
  db.executemany('INSERT INTO Improvement_YieldChanges VALUES(?,?,?)',[(t,PRIVATE,80)for t in('IMPROVEMENT_PASTURE','IMPROVEMENT_CAMP','IMPROVEMENT_PLANTATION')]+[('IMPROVEMENT_MINE','YIELD_PRODUCTION',1)])
  # A native-style legacy Farm resource modifier: preserve its tested path.
  db.execute("INSERT INTO Modifiers VALUES('MOD_CSC_AI_FARM_RESOURCE_FORECAST','MODIFIER_SINGLE_PLOT_ADJUST_PLOT_YIELDS','FARM_RESOURCES')")
  db.execute("INSERT INTO RequirementSets VALUES('FARM_RESOURCES','REQUIREMENTSET_TEST_ANY')")
  for res in('RESOURCE_WHEAT','RESOURCE_FLAX'):
   db.execute('INSERT INTO Requirements VALUES(?,?)',('FARM_'+res,'REQUIREMENT_PLOT_RESOURCE_TYPE_MATCHES'));db.execute('INSERT INTO RequirementArguments VALUES(?,?,?)',('FARM_'+res,'ResourceType',res));db.execute('INSERT INTO RequirementSetRequirements VALUES(?,?)',('FARM_RESOURCES','FARM_'+res))
  db.executemany("INSERT INTO ModifierArguments VALUES('MOD_CSC_AI_FARM_RESOURCE_FORECAST',?,?)",[('YieldType',PRIVATE),('Amount','80')]);db.execute("INSERT INTO ImprovementModifiers VALUES('IMPROVEMENT_FARM','MOD_CSC_AI_FARM_RESOURCE_FORECAST')")
  # Existing adjacent support is independent and must not be replaced/stacked twice.
  db.execute("INSERT INTO Modifiers VALUES('MOD_CSC_AI_IMPROVE_SALT','MODIFIER_SINGLE_PLOT_ADJUST_PLOT_YIELDS','ADJACENT_ONLY')");db.execute("INSERT INTO ImprovementModifiers VALUES('IMPROVEMENT_MINE','MOD_CSC_AI_IMPROVE_SALT')")
  current=sqlite3.connect(':memory:');self.addCleanup(current.close);db.commit();db.backup(current);current.executescript(SQL)
  return db,current
 def test_Mine_only_gaps_added_preserving_legacy(self):
  base,db=self.fixture();v=verify_loaded(db,base);self.assertEqual(v['new_conditional_resources'],{'IMPROVEMENT_MINE':['RESOURCE_SALT','RESOURCE_SILVER']});self.assertEqual(v['mapped_pairs'],7)
 def test_modded_resource_and_improvement_automatically_covered(self):
  base,db=self.fixture(True);v=verify_loaded(db,base);self.assertIn('RESOURCE_MOD_SALT',v['new_conditional_resources']['IMPROVEMENT_MINE']);self.assertEqual(v['new_conditional_resources']['IMPROVEMENT_MOD_ORCHARD'],['RESOURCE_MOD_FRUIT'])
 def test_terrain_Mine_and_unmapped_Iron_not_eligible(self):
  base,db=self.fixture();verify_loaded(db,base);allowed={r[0]for r in db.execute("SELECT a.Value FROM RequirementSetRequirements s JOIN RequirementArguments a ON a.RequirementId=s.RequirementId WHERE s.RequirementSetId=? AND a.Name='ResourceType'",(SET+'IMPROVEMENT_MINE',))};self.assertEqual(allowed,{'RESOURCE_SALT','RESOURCE_SILVER'})
 def test_shared_resource_does_not_duplicate_early80(self):
  base,db=self.fixture();self.assertEqual(len([r for r in mapped_pairs(db)if r==('IMPROVEMENT_FARM','RESOURCE_FLAX')]),1);self.assertFalse(list(db.execute('SELECT * FROM ImprovementModifiers WHERE ModifierId=?',(MOD+'IMPROVEMENT_FARM',))))
 def test_replay_is_idempotent(self):
  base,db=self.fixture(True);dump='\n'.join(db.iterdump());db.executescript(SQL);self.assertEqual('\n'.join(db.iterdump()),dump);verify_loaded(db,base)
 def test_ordinary_yield_legality_and_adjacent_support_unchanged(self):
  base,db=self.fixture();verify_loaded(db,base)
  for table in('Improvement_YieldChanges','Improvement_ValidTerrains','Improvement_ValidResources','TypeTags'):
   self.assertEqual(list(base.execute('SELECT * FROM '+table)),list(db.execute('SELECT * FROM '+table)))
  self.assertTrue(list(db.execute("SELECT * FROM ImprovementModifiers WHERE ModifierId='MOD_CSC_AI_IMPROVE_SALT'")))
 def test_missing_native_validity_mapping_not_assumed(self):
  base,db=self.fixture();db.execute("INSERT INTO Resources VALUES('RESOURCE_MOD_UNMAPPED')");db.execute("INSERT INTO TypeTags VALUES('RESOURCE_MOD_UNMAPPED','CLASS_CSC_BAKERS_BASE')");db.executescript(SQL);self.assertFalse(list(db.execute('SELECT * FROM Requirements WHERE RequirementId=?',(REQ+'RESOURCE_MOD_UNMAPPED',))))
 def test_flat_Mine_bonus_rejected(self):
  base,db=self.fixture();db.execute('INSERT INTO Improvement_YieldChanges VALUES(?,?,80)',('IMPROVEMENT_MINE',PRIVATE))
  with self.assertRaises(AssertionError):verify_loaded(db,base)
 def test_missing_or_wrong_resource_predicate_rejected(self):
  for sql in("DELETE FROM RequirementSetRequirements WHERE RequirementId='"+REQ+"RESOURCE_SILVER'","UPDATE RequirementArguments SET Value='RESOURCE_IRON' WHERE RequirementId='"+REQ+"RESOURCE_SALT'"):
   base,db=self.fixture();db.execute(sql)
   with self.subTest(sql=sql),self.assertRaises(AssertionError):verify_loaded(db,base)
 def test_real_yield_change_rejected(self):
  base,db=self.fixture();db.execute("UPDATE Improvement_YieldChanges SET YieldChange=2 WHERE YieldType='YIELD_PRODUCTION'")
  with self.assertRaises(AssertionError):verify_loaded(db,base)
if __name__=='__main__':unittest.main()
