"""Offline native-schema isolation checks; these do not prove native benefit."""
import collections,json,sqlite3,unittest
from pathlib import Path
import os
ROOT=Path(__file__).resolve().parents[3]
DATABASE=os.environ.get('CSC_TEST_RH_STRATEGY_DATABASE')
SQL=(ROOT/'Civ Supply Chains/ModSupport/ModSupport_RH_AI.sql').read_text().split('-- BEGIN CSC RH STRATEGY BUILDING COVERAGE V7',1)[1].split('-- END CSC RH STRATEGY BUILDING COVERAGE V7',1)[0]
PRODUCERS=('BUILDING_CSC_BAKERS_WATER_MILL','BUILDING_CSC_BAKERS_WIND_MILL','BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP')
CONSUMERS=('BUILDING_CSC_BAKERS_BAKERY','BUILDING_CSC_TAILORS_TAILOR')
VENUES=('BUILDING_CSC_BAKERS_CAFE','BUILDING_CSC_TAILORS_FASHION_HOUSE')
TEMPLATES={'RHDevZoneBuildings':[(PRODUCERS,'BUILDING_WORKSHOP'),(CONSUMERS,'BUILDING_FACTORY'),(VENUES,'BUILDING_BROADCAST_CENTER')],
 'IndustrialBuildings':[(PRODUCERS,'BUILDING_WORKSHOP'),(CONSUMERS,'BUILDING_FACTORY')],
 **{name:[(PRODUCERS+CONSUMERS,'BUILDING_FACTORY')] for name in ('ModernBuildings','AtomicBuildings','InformationBuildings')}}

class StrategyCoverage(unittest.TestCase):
 def setUp(self):
  if not DATABASE:self.skipTest('CSC_TEST_RH_STRATEGY_DATABASE required')
  self.db=sqlite3.connect(':memory:')
  with sqlite3.connect(Path(DATABASE).resolve().as_uri()+'?mode=ro',uri=True)as src:src.backup(self.db)
 def tearDown(self):
  if hasattr(self,'db'):self.db.close()
 def rows(self):return collections.Counter(self.db.execute('SELECT * FROM AiFavoredItems').fetchall())
 def apply(self):self.db.executescript(SQL)
 def expected(self):
  expected=[]
  for name,groups in TEMPLATES.items():
   for targets,template in groups:
    source=self.db.execute('SELECT * FROM AiFavoredItems WHERE ListType=? AND Item=?',(name,template)).fetchone()
    self.assertIsNotNone(source)
    for target in targets:expected.append((name,target,*source[2:]))
  return collections.Counter(expected)
 def test_exact_native_inputs_and_all_other_tables_untouched(self):
  tables=[t for t, in self.db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' AND name!='AiFavoredItems'")]
  snapshot=lambda:{t:sorted(repr(r)for r in self.db.execute('SELECT * FROM "'+t+'"'))for t in tables}
  before=snapshot();items=self.rows();expected=self.expected();self.apply()
  self.assertEqual(self.rows()-items,expected);self.assertEqual(items-self.rows(),{})
  self.assertEqual(sum(expected.values()),27);self.assertEqual(before,snapshot())
 def test_replay_does_not_duplicate_preferences(self):
  self.apply();before=self.rows();self.apply();self.assertEqual(before,self.rows())
 def test_basic_and_off_profiles_do_not_add_rows(self):
  for mode in ('BASIC','OFF'):
   self.db.execute('UPDATE CSC_AI_Profile SET Mode=?',(mode,));before=self.rows();self.apply();self.assertEqual(before,self.rows())
 def test_existing_CSC_target_is_authoritative(self):
  self.db.execute("INSERT INTO AiFavoredItems(ListType,Item,Favored,Value) VALUES('RHDevZoneBuildings',?,0,-777)",(PRODUCERS[0],))
  self.apply();self.assertEqual(self.db.execute('SELECT Favored,Value FROM AiFavoredItems WHERE ListType=? AND Item=?',('RHDevZoneBuildings',PRODUCERS[0])).fetchall(),[(0,-777)])
 def test_missing_native_source_row_is_not_invented(self):
  self.db.execute("DELETE FROM AiFavoredItems WHERE ListType='IndustrialBuildings'AND Item='BUILDING_WORKSHOP'");self.apply()
  self.assertEqual(self.db.execute("SELECT COUNT(*)FROM AiFavoredItems WHERE ListType='IndustrialBuildings'AND Item IN(?,?,?)",PRODUCERS).fetchone()[0],0)
 def test_unbound_or_wrong_system_list_is_not_extended(self):
  self.db.execute("DELETE FROM Strategy_Priorities WHERE ListType='RHDevZoneBuildings'")
  self.db.execute("UPDATE AiLists SET System='Units' WHERE ListType='IndustrialBuildings'");before=self.rows();self.apply()
  added=self.rows()-before;self.assertFalse(any(r[0]in('RHDevZoneBuildings','IndustrialBuildings')for r in added))
 def test_hidden_purchase_only_wrong_quarter_and_zero_cost_excluded(self):
  self.db.execute('UPDATE Buildings SET InternalOnly=1 WHERE BuildingType=?',(PRODUCERS[0],))
  self.db.execute('UPDATE Buildings SET MustPurchase=1 WHERE BuildingType=?',(PRODUCERS[1],))
  self.db.execute("UPDATE Buildings SET PrereqDistrict='DISTRICT_CITY_CENTER' WHERE BuildingType=?",(PRODUCERS[2],))
  self.db.execute('UPDATE Buildings SET Cost=0 WHERE BuildingType=?',(CONSUMERS[0],));before=self.rows();self.apply()
  excluded=set(PRODUCERS+(CONSUMERS[0],));self.assertFalse(any(r[1]in excluded for r in self.rows()-before))
 def test_full_source_metadata_copied(self):
  self.db.execute("UPDATE AiFavoredItems SET Favored=0,Value=-55,StringVal='native-test',MinDifficulty='DIFFICULTY_PRINCE',MaxDifficulty='DIFFICULTY_DEITY',TooltipString='LOC_TEST' WHERE ListType='IndustrialBuildings'AND Item='BUILDING_WORKSHOP'")
  expected=self.db.execute("SELECT Favored,Value,StringVal,MinDifficulty,MaxDifficulty,TooltipString FROM AiFavoredItems WHERE ListType='IndustrialBuildings'AND Item='BUILDING_WORKSHOP'").fetchone()
  self.apply()
  for item in PRODUCERS:self.assertEqual(self.db.execute("SELECT Favored,Value,StringVal,MinDifficulty,MaxDifficulty,TooltipString FROM AiFavoredItems WHERE ListType='IndustrialBuildings'AND Item=?",(item,)).fetchone(),expected)

 def test_runtime_preflight_accepts_native_rows_and_rejects_mismatch(self):
  from profile_strategy_coverage import validate_database
  self.apply();self.assertEqual(validate_database(self.db)['rows'],27)
  self.db.execute("UPDATE AiFavoredItems SET Value=-999 WHERE ListType='IndustrialBuildings' AND Item=?",(PRODUCERS[0],))
  with self.assertRaisesRegex(AssertionError,'counterpart preference mismatch'):validate_database(self.db)
 def test_runtime_preflight_rejects_missing_row(self):
  from profile_strategy_coverage import validate_database
  self.apply();self.db.execute("DELETE FROM AiFavoredItems WHERE ListType='RHDevZoneBuildings' AND Item=?",(VENUES[0],))
  with self.assertRaises(AssertionError):validate_database(self.db)

if __name__=='__main__':unittest.main()
