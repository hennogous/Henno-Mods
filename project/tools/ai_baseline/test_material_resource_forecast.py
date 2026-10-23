"""Offline boundaries for the isolated raw-resource forecast experiment."""
import sqlite3,unittest
from pathlib import Path
SQL=Path(__file__).parent/'experiments/material_resource_forecast.sql'
class ForecastTests(unittest.TestCase):
 def setUp(self):
  self.db=sqlite3.connect(':memory:');self.db.executescript("CREATE TABLE Resources(ResourceType TEXT PRIMARY KEY);CREATE TABLE TypeTags(Type TEXT,Tag TEXT);CREATE TABLE Resource_YieldChanges(ResourceType TEXT,YieldType TEXT,YieldChange INTEGER,PRIMARY KEY(ResourceType,YieldType));")
  self.db.executemany('INSERT INTO Resources VALUES(?)',[('WHEAT',),('HONEY',),('IRON',)])
  self.db.executemany('INSERT INTO TypeTags VALUES(?,?)',[('WHEAT','CLASS_CSC_BAKERS_BASE'),('WHEAT','CLASS_CSC_TAILORS_SPEC'),('HONEY','CLASS_CSC_BAKERS_SPEC'),('MISSING_RESOURCE','CLASS_CSC_BAKERS_BASE'),('IRON','CLASS_OTHER')])
  self.db.execute("INSERT INTO Resource_YieldChanges VALUES('WHEAT','YIELD_FOOD',2)")
 def test_only_live_mapped_resources_base_wins_and_replay_does_not_stack(self):
  for _ in range(2):self.db.executescript(SQL.read_text())
  self.assertEqual(self.db.execute("SELECT ResourceType,YieldChange FROM Resource_YieldChanges WHERE YieldType='YIELD_CSC_AI_PLACEMENT' ORDER BY 1").fetchall(),[('HONEY',20),('WHEAT',40)])
 def test_real_economic_yields_and_unrelated_resources_are_unchanged(self):
  self.db.executescript(SQL.read_text());self.assertEqual(self.db.execute("SELECT * FROM Resource_YieldChanges WHERE YieldType<>'YIELD_CSC_AI_PLACEMENT'").fetchall(),[('WHEAT','YIELD_FOOD',2)]);self.assertFalse(self.db.execute("SELECT * FROM Resource_YieldChanges WHERE ResourceType='IRON'").fetchall())
 def test_not_registered_in_live_mod_manifest(self):
  manifest=Path(__file__).resolve().parents[3]/'Civ Supply Chains/Civ Supply Chains.civ6proj';self.assertNotIn('material_resource_forecast.sql',manifest.read_text(encoding='utf-8-sig'))
if __name__=='__main__':unittest.main()
