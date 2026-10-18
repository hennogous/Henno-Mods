"""Regression guards for the five native QA findings, including negative tests."""
from pathlib import Path
import importlib.util
import sys
import unittest

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / 'project/tools/quarter_contracts'))
from quarter_checks.tailors_assertions import _load_phase_database
from quarter_checks.qa_regressions import material_total, validate_material_returns, validate_customer_delivery, validate_qa_regressions, validate_mechanism_bindings, validate_ownership_event

CASES = [
    ('BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP', 'RESOURCE_COTTON', (1, 2, 3)),
    ('BUILDING_CSC_TAILORS_FASHION_HOUSE', 'RESOURCE_DYES', (1, 2, 3)),
    ('BUILDING_CSC_BAKERS_WATER_MILL', 'RESOURCE_WHEAT', (1, 2, 3)),
    ('BUILDING_CSC_BAKERS_WIND_MILL', 'RESOURCE_WHEAT', (1, 2, 3)),
    ('BUILDING_CSC_BAKERS_CAFE', 'RESOURCE_COFFEE', (1, 2, 3)),
]


class QARegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.template, errors = _load_phase_database(ROOT)
        if errors:
            raise RuntimeError(errors)

    def setUp(self):
        import sqlite3
        self.db = sqlite3.connect(':memory:')
        self.template.backup(self.db)
        self.db.execute('PRAGMA foreign_keys=OFF')
        # The native cache may come from a game with Monopolies disabled.
        # Keep these graph tests independent of the last game's mode selection.
        for improvement in ('IMPROVEMENT_INDUSTRY', 'IMPROVEMENT_CORPORATION'):
            self.db.execute(
                'INSERT OR IGNORE INTO Improvements (ImprovementType,Name,PlunderType,Icon) '
                "SELECT ?,Name,PlunderType,Icon FROM Improvements WHERE ImprovementType='IMPROVEMENT_PLANTATION'",
                (improvement,),
            )
            self.assertIsNotNone(self.db.execute(
                'SELECT 1 FROM Improvements WHERE ImprovementType=?', (improvement,),
            ).fetchone())
        for name in ('CSC_Q_BAKERS_MC_MODE.sql', 'CSC_Q_BAKERS_MC_MODE_GOLD.sql'):
            self.db.executescript((ROOT / 'Civ Supply Chains/Data' / name).read_text(encoding='utf-8-sig'))

    def tearDown(self):
        self.db.close()

    def test_complete_material_graph_delivers_all_declared_totals(self):
        self.assertEqual(validate_material_returns(self.db, CASES), [])

    def test_wrong_material_classes_receive_nothing(self):
        for building, resource in [(CASES[0][0], 'RESOURCE_DYES'), (CASES[1][0], 'RESOURCE_COTTON')]:
            for improvement in ('IMPROVEMENT_PLANTATION', 'IMPROVEMENT_INDUSTRY', 'IMPROVEMENT_CORPORATION'):
                self.assertEqual(material_total(self.db, building, resource, improvement, 'YIELD_PRODUCTION'), 0)

    def test_unimproved_and_foreign_materials_receive_nothing(self):
        for building, resource, _ in CASES:
            for yield_type in ('YIELD_PRODUCTION', 'YIELD_GOLD'):
                self.assertEqual(material_total(self.db, building, resource, None, yield_type), 0)
                self.assertEqual(material_total(self.db, building, resource, 'IMPROVEMENT_PLANTATION', yield_type, owned=False), 0)

    def test_wrong_ownership_collection_is_rejected(self):
        self.db.execute("UPDATE DynamicModifiers SET CollectionType='COLLECTION_ALL_IMPROVEMENTS' WHERE ModifierType='MODIFIER_CSC_PLAYER_IMPROVEMENTS_ATTACH_MODIFIER'")
        self.assertTrue(validate_material_returns(self.db, CASES))

    def test_reintroducing_full_industry_amount_is_rejected(self):
        self.db.execute("UPDATE ModifierArguments SET Value=2 WHERE ModifierId='MOD_CSC_TAILORS_PROD_TO_ADJ_IND' AND Name='Amount'")
        self.assertTrue(validate_material_returns(self.db, CASES))

    def test_missing_specialty_producer_attachment_is_rejected(self):
        self.db.execute("DELETE FROM BuildingModifiers WHERE BuildingType='BUILDING_CSC_TAILORS_FASHION_HOUSE'")
        self.assertTrue(validate_material_returns(self.db, CASES))

    def test_missing_customer_property_is_rejected(self):
        self.db.execute("UPDATE CSC_Stage3CustomerTransactions SET CustomerYieldAmountProperty=NULL WHERE TransactionId='CSC_TAILORS_TAILOR_MARKET'")
        self.assertTrue(validate_customer_delivery(self.db))

    def test_missing_customer_activation_edge_is_rejected(self):
        self.db.execute("DELETE FROM RequirementSetRequirements WHERE RequirementSetId='REQSET_CSC_TAILORS_MARKET_CUSTOMER_CULTURE_BIT_1'")
        self.assertTrue(validate_customer_delivery(self.db))

    def test_declaring_pattern_without_actual_wiring_is_rejected(self):
        import yaml
        contract = yaml.safe_load((ROOT / 'project/specs/tailors/implementation.yaml').read_text(encoding='utf-8'))
        self.assertEqual(validate_mechanism_bindings(self.db, contract, 'stage3'), [])
        self.db.execute("DELETE FROM BuildingModifiers WHERE BuildingType='BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP'")
        self.assertTrue(validate_mechanism_bindings(self.db, contract, 'stage3'))

    def test_missing_mechanism_binding_is_rejected(self):
        import yaml
        contract = yaml.safe_load((ROOT / 'project/specs/tailors/implementation.yaml').read_text(encoding='utf-8'))
        del contract['mechanism_bindings']['customer_population_sales']
        self.assertTrue(validate_mechanism_bindings(self.db, contract, 'stage3'))

    def test_duplicate_return_cannot_bypass_total_validation(self):
        self.db.execute("INSERT INTO BuildingModifiers VALUES ('BUILDING_CSC_BAKERS_WATER_MILL','MOD_CSC_BAKERS_CAFE_ATTACH_ADJ_IMP_SPEC_PROD')")
        self.db.execute("UPDATE Modifiers SET SubjectRequirementSetId='REQSET_CSC_BAKERS_ADJ_PLOT_HAS_BASE' WHERE ModifierId='MOD_CSC_BAKERS_CAFE_ATTACH_ADJ_IMP_SPEC_PROD'")
        self.assertTrue(validate_material_returns(self.db, CASES))

    def test_shipped_notification_handler_preserves_loaded_comparisons(self):
        self.assertEqual(validate_qa_regressions(ROOT, self.db, 'stage3'), [])

    def test_original_notification_cache_reader_fails_behavior_fixture(self):
        import re
        from lupa import LuaRuntime
        lua = LuaRuntime(unpack_returned_tuples=True)
        lua.execute((ROOT / 'project/tools/quarter_contracts/tests/fixtures/notification_cache_world.lua').read_text())
        source = (ROOT / 'Civ Supply Chains/Lua_UI/Notifications_Suk_MCUIS/CSC_UI_Notifications.lua').read_text()
        source = source.replace('ReadAbilityCache(sCSC_CitiesAbilitiesStringKey)', 'ReadCustomData(sCSC_CitiesAbilitiesStringKey)')
        lua.execute(re.sub(r'\s*:\s*(?:number|table|string|boolean)\b', '', source))
        with self.assertRaises(Exception):
            lua.globals().TestNotificationCache()

    def test_missing_real_ownership_event_is_rejected(self):
        source = (ROOT / 'Civ Supply Chains/Lua_UI/Adjacencies/CSC_AdjacencyGameplay.lua').read_text(encoding='utf-8')
        self.assertEqual(validate_ownership_event(source), [])
        self.assertTrue(validate_ownership_event(source.replace("'CityTileOwnershipChanged'", "'PlotOwnershipChanged'")))


if __name__ == '__main__':
    unittest.main()
