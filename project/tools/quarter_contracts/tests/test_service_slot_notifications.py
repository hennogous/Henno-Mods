"""Regression checks for service notification slots and persistent grants."""
import importlib.util
from pathlib import Path
import sqlite3
import unittest

ROOT = Path(__file__).resolve().parents[4]
SPEC = importlib.util.spec_from_file_location('stage4_assertions', ROOT / 'project/tools/quarter_contracts/quarter_checks/tailors_stage4_assertions.py')
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
PREFIX = 'LOC_CSC_TAILORS_STAGE_4_EFFECT_DESCRIPTION'

class ServiceSlotNotificationTests(unittest.TestCase):
    def setUp(self):
        with sqlite3.connect(':memory:') as db:
            db.execute('CREATE TABLE LocalizedText (Language TEXT,Tag TEXT,Text TEXT,PRIMARY KEY(Language,Tag))')
            db.executescript((ROOT / 'Civ Supply Chains/Text/CSC_TAILORS_TEXT.sql').read_text(encoding='utf-8-sig'))
            self.texts = dict(db.execute("SELECT Tag,Text FROM LocalizedText WHERE Language='en_US'"))

    def check(self, prefix=PREFIX, slots=1):
        return MODULE.validate_service_slot_notifications(self.texts, prefix, slots, 'Theater Square')

    def test_generated_stage_manager_names_granted_and_persistent_slot(self):
        self.assertEqual(self.check(), [])

    def test_missing_new_slot_is_rejected(self):
        self.texts[PREFIX+'_NEW'] = self.texts[PREFIX+'_NEW'].replace(' and +1 [ICON_Citizen] Citizen slot in the Theater Square', '')
        self.assertTrue(any('NEW must state' in failure for failure in self.check()))

    def test_missing_removal_persistence_is_rejected(self):
        self.texts[PREFIX+'_REMOVED'] = self.texts[PREFIX+'_REMOVED'].replace(' and its [ICON_Citizen] Citizen slot remain', ' remains')
        self.assertTrue(any('REMOVED must state' in failure for failure in self.check()))

    def test_supplier_increase_cannot_claim_another_slot(self):
        self.texts[PREFIX+'_INCREASED'] += ' and +1 [ICON_Citizen] Citizen slot in the Theater Square'
        self.assertTrue(any('INCREASED must not imply' in failure for failure in self.check()))

    def test_wonder_notifications_have_no_slot_and_reject_false_grant(self):
        for venue in ('BOLSHOI', 'BROADWAY', 'SYDNEY'):
            prefix = PREFIX+'_'+venue
            self.assertEqual(self.check(prefix, 0), [])
            self.texts[prefix+'_NEW'] += ' and +1 [ICON_Citizen] Citizen slot'
            self.assertTrue(any('NEW must not imply' in failure for failure in self.check(prefix, 0)))

if __name__ == '__main__':
    unittest.main()
