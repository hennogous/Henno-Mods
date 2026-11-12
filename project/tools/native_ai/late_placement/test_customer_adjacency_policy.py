"""Native-only comparison must preserve yield identities and noncustomer policy."""
from pathlib import Path
from contextlib import closing
import sqlite3
import tempfile
import unittest
import xml.etree.ElementTree as ET
from lupa.lua51 import LuaRuntime
from customer_adjacency_policy import stage_metadata,stage_publisher,WITHHOLD,OFF_SQL,database_snapshot,qualify_database


class NativeCustomerPolicy(unittest.TestCase):
    def test_loaded_database_qualifies_both_arms_and_rejects_wrong_arm(self):
        with tempfile.TemporaryDirectory()as folder:
            path=Path(folder)/'DebugGameplay.sqlite'
            with closing(sqlite3.connect(path))as db:
                db.executescript('''
CREATE TABLE District_Adjacencies(DistrictType,YieldChangeId);
CREATE TABLE Adjacency_YieldChanges(ID,YieldType,YieldChange,TilesRequired,AdjacentDistrict);
CREATE TABLE Yields(YieldType,DefaultValue);
CREATE TABLE AiFavoredItems(ListType,Item,Value);
INSERT INTO Yields VALUES('YIELD_CSC_AI_PLACEMENT',1);
INSERT INTO AiFavoredItems VALUES('DefaultYieldBias','YIELD_CSC_AI_PLACEMENT',25);
INSERT INTO Adjacency_YieldChanges VALUES
 ('CSC_AI_CUSTOMER_DISTRICT_HARBOR__DISTRICT_CSC_TAILORS_QUARTER',
  'YIELD_CSC_AI_PLACEMENT',1,1,'DISTRICT_CSC_TAILORS_QUARTER');
INSERT INTO District_Adjacencies VALUES
 ('DISTRICT_HARBOR','CSC_AI_CUSTOMER_DISTRICT_HARBOR__DISTRICT_CSC_TAILORS_QUARTER');
''')
            on=database_snapshot(path);qualify_database(on,'on')
            with self.assertRaises(AssertionError):qualify_database(on,'off')
            with closing(sqlite3.connect(path))as db:db.executescript(OFF_SQL.decode())
            off=database_snapshot(path);qualify_database(off,'off')
            self.assertEqual(on['rules'],off['rules'])
            self.assertEqual(on['yields'],off['yields'])
            self.assertEqual(on['biases'],off['biases'])
            with self.assertRaises(AssertionError):qualify_database(off,'on')

    def test_sql_removes_only_the_target_link_and_keeps_definitions(self):
        db=sqlite3.connect(':memory:')
        db.executescript("""
CREATE TABLE District_Adjacencies(DistrictType,YieldChangeId);
CREATE TABLE Adjacency_YieldChanges(ID,YieldType,AdjacentDistrict);
CREATE TABLE Yields(YieldType,DefaultValue);
INSERT INTO Yields VALUES('YIELD_CSC_AI_PLACEMENT',1);
INSERT INTO Adjacency_YieldChanges VALUES
 ('target','YIELD_CSC_AI_PLACEMENT','DISTRICT_CSC_TAILORS_QUARTER'),
 ('other','YIELD_GOLD','DISTRICT_CITY_CENTER');
INSERT INTO District_Adjacencies VALUES
 ('DISTRICT_HARBOR','target'),('DISTRICT_ROYAL_NAVY_DOCKYARD','target'),('DISTRICT_HARBOR','other');
""")
        before=list(db.execute('SELECT * FROM Adjacency_YieldChanges'))
        db.executescript(OFF_SQL.decode())
        self.assertEqual(list(db.execute('SELECT * FROM District_Adjacencies')),
            [('DISTRICT_ROYAL_NAVY_DOCKYARD','target'),('DISTRICT_HARBOR','other')])
        self.assertEqual(list(db.execute('SELECT * FROM Adjacency_YieldChanges')),before)
        self.assertEqual(list(db.execute('SELECT * FROM Yields')),[('YIELD_CSC_AI_PLACEMENT',1)])

    def test_both_modes_have_identical_metadata_and_one_last_action(self):
        source=b'<Mod><InGameActions><UpdateDatabase id="old"><Properties><LoadOrder>50</LoadOrder></Properties><File>old.sql</File></UpdateDatabase></InGameActions><Files><File>old.sql</File></Files></Mod>'
        on,on_sql=stage_metadata(source,'on');off,off_sql=stage_metadata(source,'off')
        self.assertEqual(on,off);self.assertNotEqual(on_sql,off_sql)
        root=ET.fromstring(on)
        self.assertEqual(root.findall('InGameActions/UpdateDatabase')[-1].findtext('Properties/LoadOrder'),'51')
        self.assertEqual(len(root.findall('Files/File')),2)

    def test_optional_bonus_removal_preserves_other_entries_and_material_penalty(self):
        vm=LuaRuntime();vm.execute("""
print=function()end;turn=208;version=0
GameInfo={Districts={[4]={DistrictType='DISTRICT_HARBOR'},[36]={DistrictType='DISTRICT_CSC_BAKERS_QUARTER'}}}
entries={
 {player=3,city=393221,district=4,plot=1082,delta=10240,customer=true},
 {player=3,city=393221,district=4,plot=1084,delta=-32768},
 {player=3,city=393221,district=36,plot=1085,delta=6144},
 {player=3,city=123,district=4,plot=999,delta=10240,customer=true}}
""")
        vm.execute(WITHHOLD.decode())
        rows=list(vm.globals().entries.values())
        self.assertEqual([r['delta']for r in rows],[-32768,6144,10240])
        vm.execute('entries={{player=3,city=393221,district=4,plot=1082,delta=-100,customer=true}}')
        with self.assertRaises(Exception):vm.execute(WITHHOLD.decode())
        self.assertEqual(vm.globals().entries[1]['delta'],-100)

    def test_real_publisher_wrapper_compiles_and_is_before_commit(self):
        root=Path(__file__).resolve().parents[4]/'Civ Supply Chains/Lua_UI/AI'
        code=stage_publisher((root/'CSC_AI_BakersGameplay.lua').read_bytes()).decode('utf-8-sig')
        LuaRuntime().eval('function(s)assert(loadstring(s))end')(code)
        self.assertLess(code.index('CSC_CUSTOMER_CE_WITHHELD'),code.index('local accepted, message = bridge.Publish('))


if __name__=='__main__':unittest.main()
