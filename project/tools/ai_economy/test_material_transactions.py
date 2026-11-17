"""Loaded resource mappings drive ordinary incoming transactions without stacking.

This SQL changes gameplay, so verify exact missing roots, reapplication, absent
producer definitions and preservation of the separate Industry/Corporation path.
Live modifier delivery is qualified separately in the controlled game fixture.
"""
from pathlib import Path
import json
import sqlite3
import unittest
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[3]
SQL=(ROOT/'Civ Supply Chains/Data/CSC_Q_ALL_MaterialHosts.sql').read_text(encoding='utf-8')
ROOTS={
    'BW':'MOD_CSC_BAKERS_BASE_IMPROVEMENT_ATTACH_QUARTER_WATER',
    'BI':'MOD_CSC_BAKERS_BASE_IMPROVEMENT_ATTACH_QUARTER_WIND',
    'BS':'MOD_CSC_BAKERS_SPEC_IMPROVEMENT_ATTACH_QUARTER',
    'TB':'MOD_CSC_TAILORS_BASE_IMPROVEMENT_ATTACH_QUARTER',
    'TS':'MOD_CSC_TAILORS_SPEC_IMPROVEMENT_ATTACH_QUARTER'}


class MaterialTransactions(unittest.TestCase):
    def test_gameplay_attachment_repair_loads_independently_after_late_improvements(self):
        manifest=json.loads((ROOT/'project/modbuddy/CivSupplyChains.actions.json').read_text())
        actions={a['id']:a for a in manifest['blocks']['inGameActions']}
        action=actions['CSC_MaterialTransactions']
        self.assertFalse(action.get('criteria'))
        # R2 defines Sawmill at799990 and optionally edits it at800000;
        # CL's resource-validity links load at9999. Resource tags alone are early.
        self.assertEqual(int(action['properties']['LoadOrder']),800010)
        self.assertEqual(action['files'],['Data/CSC_Q_ALL_MaterialHosts.sql'])
        project=ET.parse(ROOT/'Civ Supply Chains/Civ Supply Chains.civ6proj')
        self.assertTrue(any(e.attrib.get('Include')=='Data\\CSC_Q_ALL_MaterialHosts.sql'for e in project.iter()))

    def setUp(self):
        self.db=sqlite3.connect(':memory:');self.addCleanup(self.db.close)
        self.db.executescript('''
CREATE TABLE Modifiers(ModifierId PRIMARY KEY);
CREATE TABLE Improvements(ImprovementType PRIMARY KEY);
CREATE TABLE Improvement_ValidResources(ImprovementType,ResourceType);
CREATE TABLE TypeTags(Type,Tag);
CREATE TABLE ImprovementModifiers(ImprovementType,ModifierId);
CREATE TABLE CSC_MaterialTransactions(TransactionId PRIMARY KEY,MaterialClass);
CREATE TABLE CSC_MaterialTransactionYields(TransactionId,LegKey,Recipient,ImprovementScope);
CREATE TABLE CSC_MaterialTransactionBindings(TransactionId,LegKey,RootModifierId);
''')
        self.db.executescript((ROOT/'Civ Supply Chains/Data/CSC_Q_ALL_Schema.sql').read_text(encoding='utf-8'))
        classes={'BW':'BAKERS_BASE','BI':'BAKERS_BASE','BS':'BAKERS_SPEC','TB':'TAILORS_BASE','TS':'TAILORS_SPEC'}
        for key,root in ROOTS.items():
            self.db.execute('INSERT INTO CSC_MaterialTransactions VALUES(?,?)',(key,'CLASS_CSC_'+classes[key]))
            self.db.execute("INSERT INTO CSC_MaterialTransactionYields VALUES(?,'INPUT','PRODUCER','REGISTERED_INPUT')",(key,))
            self.db.execute("INSERT INTO CSC_MaterialTransactionBindings VALUES(?,'INPUT',?)",(key,root))
        self.db.executemany('INSERT INTO Modifiers VALUES(?)',[(x,)for x in ROOTS.values()])
        self.db.executemany('INSERT INTO Improvements VALUES(?)',[(x,)for x in
            ('FARM','PASTURE','R2_SAWMILL','CL_TRADING_POST','CL_CRAFTSMEN','IMPROVEMENT_INDUSTRY','IMPROVEMENT_CORPORATION')])
        mappings=[('FARM','WHEAT'),('FARM','SORGHUM'),('R2_SAWMILL','BAMBOO'),
            ('R2_SAWMILL','MAPLE'),('PASTURE','CASHMERE'),('CL_TRADING_POST','WHEAT'),
            ('CL_TRADING_POST','COTTON'),('CL_CRAFTSMEN','GOLD'),('ABSENT_MOD','GOLD'),
            ('IMPROVEMENT_INDUSTRY','COTTON'),('IMPROVEMENT_CORPORATION','COTTON')]
        self.db.executemany('INSERT INTO Improvement_ValidResources VALUES(?,?)',mappings)
        self.db.executemany('INSERT INTO TypeTags VALUES(?,?)',[
            ('WHEAT','CLASS_CSC_BAKERS_BASE'),('SORGHUM','CLASS_CSC_BAKERS_BASE'),
            ('BAMBOO','CLASS_CSC_TAILORS_BASE'),('MAPLE','CLASS_CSC_BAKERS_SPEC'),
            ('CASHMERE','CLASS_CSC_TAILORS_SPEC'),('COTTON','CLASS_CSC_TAILORS_BASE'),
            ('COTTON','CLASS_CSC_TAILORS_SPEC'),('GOLD','CLASS_CSC_BAKERS_SPEC'),
            ('GOLD','CLASS_CSC_TAILORS_SPEC')])
        self.db.executemany('INSERT INTO ImprovementModifiers VALUES(?,?)',[
            ('FARM',ROOTS['BW']),('IMPROVEMENT_INDUSTRY','SPECIAL_INDUSTRY_ROOT')])

    def test_missing_pack_transactions_and_existing_control_are_attached_once(self):
        self.db.executescript(SQL)
        expected={('FARM',ROOTS['BW']),('FARM',ROOTS['BI']),
            ('R2_SAWMILL',ROOTS['TB']),('R2_SAWMILL',ROOTS['BS']),
            ('PASTURE',ROOTS['TS']),('CL_TRADING_POST',ROOTS['BW']),
            ('CL_TRADING_POST',ROOTS['BI']),('CL_TRADING_POST',ROOTS['TB']),
            ('CL_TRADING_POST',ROOTS['TS']),('CL_CRAFTSMEN',ROOTS['BS']),
            ('CL_CRAFTSMEN',ROOTS['TS']),('IMPROVEMENT_INDUSTRY','SPECIAL_INDUSTRY_ROOT')}
        rows=self.db.execute('SELECT * FROM ImprovementModifiers').fetchall()
        self.assertEqual(set(rows),expected);self.assertEqual(len(rows),len(expected))
        self.db.executescript(SQL)
        self.assertEqual(self.db.execute('SELECT COUNT(*) FROM ImprovementModifiers').fetchone()[0],len(expected))

    def test_absent_producer_root_does_not_create_a_dangling_attachment(self):
        self.db.execute('DELETE FROM Modifiers WHERE ModifierId=?',(ROOTS['TS'],))
        self.db.executescript(SQL)
        self.assertEqual(self.db.execute('SELECT COUNT(*) FROM ImprovementModifiers WHERE ModifierId=?',(ROOTS['TS'],)).fetchone()[0],0)


if __name__=='__main__':unittest.main()
