"""SQL-only dose contrast: preserve native identities, links and other policy."""
from pathlib import Path
from contextlib import closing
import sqlite3
from tempfile import TemporaryDirectory
import unittest
import xml.etree.ElementTree as ET
from customer_signal_replay import stage, qualify_database, RULE, SQL_PATH, survey_code
from customer_adjacency_policy import database_snapshot


class CustomerSignalTests(unittest.TestCase):
    def test_real_survey_compiles_and_normalizes_tuple_scope(self):
        from lupa.lua51 import LuaRuntime
        code=survey_code(1,[(5,65536),(4,65536)])
        self.assertIn('{{5,65536},{4,65536}}',code)
        self.assertNotIn('__TARGETS__',code)
        LuaRuntime().eval('function(code)assert(loadstring(code))end')(code)

    def test_only_one_amount_changes_with_stable_metadata_and_database_identity(self):
        original = b'<Mod><InGameActions><UpdateDatabase id="normal"><Properties><LoadOrder>100</LoadOrder></Properties><File>normal.sql</File></UpdateDatabase></InGameActions><Files><File>normal.sql</File></Files></Mod>'
        metadata = []
        for amount in (0, 1, 4, 8):
            with self.subTest(amount=amount), TemporaryDirectory() as temp:
                manifest, sql = stage(original, amount)
                metadata.append(manifest)
                xml = ET.fromstring(manifest)
                action = xml.find("InGameActions/UpdateDatabase[@id='CSC_DIAG_CUSTOMER_STRENGTH']")
                self.assertEqual(action.findtext('File'), SQL_PATH)
                self.assertEqual(action.findtext('Properties/LoadOrder'), '101')
                path = Path(temp)/'db.sqlite'
                with closing(sqlite3.connect(path)) as db:
                    db.executescript('''
CREATE TABLE Adjacency_YieldChanges(ID TEXT,YieldType TEXT,YieldChange INT,TilesRequired INT,AdjacentDistrict TEXT);
CREATE TABLE District_Adjacencies(DistrictType TEXT,YieldChangeId TEXT);
CREATE TABLE Yields(YieldType TEXT,DefaultValue INT);
CREATE TABLE AiFavoredItems(ListType TEXT,Item TEXT,Value INT);
INSERT INTO Yields VALUES('YIELD_CSC_AI_PLACEMENT',1);
INSERT INTO AiFavoredItems VALUES('DefaultYieldBias','YIELD_CSC_AI_PLACEMENT',25);
''')
                    for rule, customer, quarter in ((RULE, 'DISTRICT_COMMERCIAL_HUB', 'DISTRICT_CSC_BAKERS_QUARTER'),
                                                    ('unrelated', 'DISTRICT_HARBOR', 'DISTRICT_CSC_TAILORS_QUARTER')):
                        db.execute('INSERT INTO Adjacency_YieldChanges VALUES(?,?,?,?,?)',
                                   (rule, 'YIELD_CSC_AI_PLACEMENT', 1, 1, quarter))
                        db.execute('INSERT INTO District_Adjacencies VALUES(?,?)', (customer, rule))
                    before = db.execute('SELECT rowid,ID FROM Adjacency_YieldChanges').fetchall()
                    db.executescript(sql.decode('utf-8'))
                    self.assertEqual(db.execute('SELECT rowid,ID FROM Adjacency_YieldChanges').fetchall(), before)
                    self.assertEqual(db.execute("SELECT YieldChange FROM Adjacency_YieldChanges WHERE ID='unrelated'").fetchone(), (1,))
                qualify_database(database_snapshot(path), amount)
        self.assertTrue(all(x == metadata[0] for x in metadata))

    def test_unbounded_or_noninteger_amount_rejected_before_staging(self):
        for amount in (True, -1, 3, 10000):
            with self.subTest(amount=amount), self.assertRaisesRegex(RuntimeError, 'Bounded diagnostic'):
                stage(b'irrelevant', amount)
