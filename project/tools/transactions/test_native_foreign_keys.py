"""Civ's cascading native keys must not delete unrelated gameplay effects.

The ordinary SQL fixture intentionally loads partial graphs with FK checks off.
These tests add the native ON DELETE CASCADE relationships and enable enforcement
before generation. This reproduces the real loader failure that a minimal schema
missed, and checks insertion of completely new native gate identities as well.
"""
import sqlite3
import unittest

from population_catalogue_fixture import MOD,compile_catalogue

SQL=(MOD/'Data/CSC_FixedBuildingTransactionProcessor.sql').read_text()


def native_keys(db):
    schemas={
        'Modifiers':'''ModifierId TEXT PRIMARY KEY,ModifierType TEXT,OwnerRequirementSetId TEXT,SubjectRequirementSetId TEXT,
            RunOnce INTEGER DEFAULT 0,Permanent INTEGER DEFAULT 0,OwnerStackLimit INTEGER,SubjectStackLimit INTEGER,
            NewOnly INTEGER DEFAULT 0,Repeatable INTEGER DEFAULT 0,
            FOREIGN KEY(OwnerRequirementSetId) REFERENCES RequirementSets(RequirementSetId) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY(SubjectRequirementSetId) REFERENCES RequirementSets(RequirementSetId) ON DELETE CASCADE ON UPDATE CASCADE''',
        'ModifierArguments':'''ModifierId TEXT,Name TEXT,Value TEXT,PRIMARY KEY(ModifierId,Name),
            FOREIGN KEY(ModifierId) REFERENCES Modifiers(ModifierId) ON DELETE CASCADE ON UPDATE CASCADE''',
        'BuildingModifiers':'''BuildingType TEXT,ModifierId TEXT,UNIQUE(BuildingType,ModifierId),
            FOREIGN KEY(ModifierId) REFERENCES Modifiers(ModifierId) ON DELETE CASCADE ON UPDATE CASCADE''',
        'RequirementArguments':'''RequirementId TEXT,Name TEXT,Value TEXT,PRIMARY KEY(RequirementId,Name),
            FOREIGN KEY(RequirementId) REFERENCES Requirements(RequirementId) ON DELETE CASCADE ON UPDATE CASCADE''',
        'RequirementSetRequirements':'''RequirementSetId TEXT,RequirementId TEXT,PRIMARY KEY(RequirementSetId,RequirementId),
            FOREIGN KEY(RequirementSetId) REFERENCES RequirementSets(RequirementSetId) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY(RequirementId) REFERENCES Requirements(RequirementId) ON DELETE CASCADE ON UPDATE CASCADE''',
    }
    # There are no native FK declarations in the source fixture, so replacements
    # do not rewrite other native references to the temporary old-table names.
    for table,columns in schemas.items():
        db.execute(f'ALTER TABLE {table} RENAME TO {table}_Old')
        db.execute(f'CREATE TABLE {table}({columns})')
        db.execute(f'INSERT INTO {table} SELECT * FROM {table}_Old')
        db.execute(f'DROP TABLE {table}_Old')
    db.commit();db.execute('PRAGMA foreign_keys=ON')
    assert db.execute('PRAGMA foreign_keys').fetchone()[0]==1


class NativeForeignKeys(unittest.TestCase):
    def test_shared_requirements_preserve_service_siblings_and_their_attachments(self):
        db=compile_catalogue()
        db.execute("INSERT INTO Modifiers(ModifierId,ModifierType,SubjectRequirementSetId) VALUES('MOD_CSC_TEST_SERVICE','TEST_EFFECT','REQSET_CSC_ADJ_CITY_CENTER_GRANARY')")
        db.execute("INSERT INTO BuildingModifiers VALUES('BUILDING_GRANARY','MOD_CSC_TEST_SERVICE')")
        db.execute("INSERT INTO RequirementSets VALUES('REQSET_CSC_TEST_SIBLING','REQUIREMENTSET_TEST_ALL')")
        db.execute("INSERT INTO RequirementSetRequirements VALUES('REQSET_CSC_TEST_SIBLING','REQ_CSC_PLOT_ADJ_TO_OWNER')")
        native_keys(db);db.executescript(SQL)
        self.assertEqual(db.execute("SELECT COUNT(*) FROM Modifiers WHERE ModifierId='MOD_CSC_TEST_SERVICE'").fetchone()[0],1)
        self.assertEqual(db.execute("SELECT COUNT(*) FROM BuildingModifiers WHERE ModifierId='MOD_CSC_TEST_SERVICE'").fetchone()[0],1)
        self.assertEqual(db.execute("SELECT COUNT(*) FROM RequirementSetRequirements WHERE RequirementSetId='REQSET_CSC_TEST_SIBLING'").fetchone()[0],1)
        db.close()

    def test_new_gate_identities_are_created_before_foreign_key_consumers(self):
        db=compile_catalogue()
        db.executescript('''
INSERT INTO Buildings VALUES('BUILDING_TEST_CUSTOMER','DISTRICT_CITY_CENTER',0);
INSERT INTO CSC_BuildingTransactions VALUES('CSC_TEST_FIXED','BAKERS','BUILDING_CSC_BAKERS_WATER_MILL','BUILDING_TEST_CUSTOMER','ADJACENT_OWNED','FIXED',1,NULL,0,NULL);
INSERT INTO CSC_BuildingTransactionYields VALUES
 ('CSC_TEST_FIXED','SOURCE_PRODUCTION','SOURCE','YIELD_PRODUCTION',1,NULL),
 ('CSC_TEST_FIXED','PARTNER_RETURN','PARTNER','YIELD_FOOD',1,NULL);
INSERT INTO CSC_BuildingTransactionFixedBindings VALUES
 ('CSC_TEST_FIXED','SOURCE_PRODUCTION','PARTNER','MOD_CSC_TEST_BACK_ROOT','MOD_CSC_TEST_BACK_LEAF','REQSET_CSC_TEST_BACK','REQ_CSC_TEST_ADJ','REQ_CSC_TEST_QUARTER',NULL),
 ('CSC_TEST_FIXED','PARTNER_RETURN','SOURCE','MOD_CSC_TEST_OUT_ROOT','MOD_CSC_TEST_OUT_LEAF','REQSET_CSC_TEST_OUT','REQ_CSC_TEST_ADJ','REQ_CSC_TEST_CENTER','REQ_CSC_TEST_CUSTOMER');
''')
        native_keys(db);db.executescript(SQL)
        self.assertEqual(db.execute("SELECT Value FROM RequirementArguments WHERE RequirementId='REQ_CSC_TEST_CUSTOMER' AND Name='BuildingType'").fetchone()[0],'BUILDING_TEST_CUSTOMER')
        self.assertEqual(db.execute("SELECT COUNT(*) FROM BuildingModifiers WHERE ModifierId='MOD_CSC_TEST_OUT_ROOT'").fetchone()[0],1)
        db.close()

    def test_unimplemented_fixed_host_gate_is_rejected(self):
        db=compile_catalogue()
        with self.assertRaises(sqlite3.IntegrityError):
            db.execute("UPDATE CSC_BuildingTransactions SET PartnerDistrictMustFunction=1 WHERE QuantityKind='FIXED'")
        db.close()


if __name__=='__main__':unittest.main()
