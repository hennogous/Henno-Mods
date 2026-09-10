from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "validate_localization_patterns.py"
SPEC = importlib.util.spec_from_file_location("validate_localization_patterns", SCRIPT)
assert SPEC and SPEC.loader
PATTERNS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PATTERNS)


class LocalizationPatternCatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog_path = (
            PATTERNS.ROOT
            / "project/specs/reference/bakers-localization-patterns.yaml"
        )
        cls.catalog = PATTERNS.load_catalog(cls.catalog_path)

    def test_catalog_schema_and_semantics_pass(self) -> None:
        self.assertEqual(
            PATTERNS.validate_catalog(self.catalog, self.catalog_path), []
        )

    def test_catalog_rejects_declared_slots_that_drift_from_template(self) -> None:
        catalog = copy.deepcopy(self.catalog)
        pattern = next(
            item for item in catalog["patterns"]
            if item["id"] == "LP.LOCAL.EXCHANGE_BULLET"
        )
        pattern["required_slots"] = ["received", "target", "wrong_slot"]
        failures = PATTERNS.validate_catalog(catalog, self.catalog_path)
        self.assertTrue(any("do not exactly match" in failure for failure in failures))

    def test_bakers_material_pattern_is_reproduced_exactly(self) -> None:
        rendered = PATTERNS.render_pattern(
            self.catalog,
            "LP.MATERIAL.BULLET",
            {
                "received": "1 [ICON_Food] Food",
                "material_class": "[ICON_CSC_BASE] Base",
                "provided": (
                    "1 [ICON_Production] Production and +1 [ICON_Gold] Gold"
                ),
            },
            bullet_marker="-",
        )
        expected = (
            "- +1 [ICON_Food] Food from each adjacent [ICON_CSC_BASE] Base "
            "Materials improvement, in exchange for +1 [ICON_Production] "
            "Production and +1 [ICON_Gold] Gold."
        )
        self.assertEqual(rendered, expected)
        bakers = (
            PATTERNS.ROOT / self.catalog["reference_file"]
        ).read_text(encoding="utf-8")
        self.assertTrue(PATTERNS.source_contains_exact_text(bakers, rendered))

    def test_bakers_district_exchange_pattern_is_reproduced_exactly(self) -> None:
        rendered = PATTERNS.render_pattern(
            self.catalog,
            "LP.DISTRICT.BILATERAL_BULLET",
            {
                "source_amount": 1,
                "source_icon": "[ICON_Gold]",
                "SourceYield": "Gold",
                "target": "[ICON_CSC_SALES] City Center and Commercial Hub",
                "return_amount": 1,
                "return_icon": "[ICON_Food]",
                "ReturnYield": "Food",
            },
            bullet_marker="-",
        )
        expected = (
            "- +1 [ICON_Gold] Gold from each adjacent [ICON_CSC_SALES] City "
            "Center and Commercial Hub, and +1 [ICON_Food] Food in return."
        )
        self.assertEqual(rendered, expected)
        bakers = (
            PATTERNS.ROOT / self.catalog["reference_file"]
        ).read_text(encoding="utf-8")
        self.assertTrue(PATTERNS.source_contains_exact_text(bakers, rendered))

    def test_missing_slot_is_rejected(self) -> None:
        with self.assertRaisesRegex(PATTERNS.PatternError, "missing slots: target"):
            PATTERNS.render_pattern(
                self.catalog,
                "LP.LOCAL.EXCHANGE_BULLET",
                {"received": "1 Food", "provided": "1 Production"},
            )

    def test_extra_slot_is_rejected(self) -> None:
        with self.assertRaisesRegex(PATTERNS.PatternError, "extra slots: typo"):
            PATTERNS.render_pattern(
                self.catalog,
                "LP.LOCAL.EXCHANGE_BULLET",
                {
                    "received": "1 Food",
                    "target": "Bakery",
                    "provided": "1 Production",
                    "typo": "must not be ignored",
                },
            )

    def test_punctuation_and_exchange_wording_drift_are_rejected(self) -> None:
        slots = {
            "received": "1 [ICON_Food] Food",
            "target": "Bakery",
            "provided": "1 [ICON_Production] Production",
        }
        self.assertFalse(
            PATTERNS.pattern_matches(
                self.catalog,
                "LP.LOCAL.EXCHANGE_BULLET",
                slots,
                "- +1 [ICON_Food] Food from the local Bakery; in exchange for "
                "+1 [ICON_Production] Production.",
            )
        )
        self.assertFalse(
            PATTERNS.pattern_matches(
                self.catalog,
                "LP.LOCAL.EXCHANGE_BULLET",
                slots,
                "- +1 [ICON_Food] Food from the local Bakery, and +1 "
                "[ICON_Production] Production in return.",
            )
        )

    def test_building_description_order_is_enforced(self) -> None:
        correct = [
            "LP.MATERIAL.BULLET",
            "LP.BUILDING.ENGINE_RENDERED_STATS_OMITTED",
            "LP.LOCAL.EXCHANGE_BULLET",
            "LP.CUSTOMER.BILATERAL_BULLET",
            "LP.TRADE.DOMESTIC_BULLET",
            "LP.SERVICE.INTRO",
        ]
        self.assertEqual(PATTERNS.validate_description_order(self.catalog, correct), [])

        failures = PATTERNS.validate_description_order(
            self.catalog,
            ["LP.LOCAL.EXCHANGE_BULLET", "LP.MATERIAL.BULLET"],
        )
        self.assertTrue(any("material_input" in failure for failure in failures))

    def test_engine_rendered_building_stats_are_omission_only(self) -> None:
        patterns = PATTERNS.pattern_map(self.catalog)
        omission = patterns["LP.BUILDING.ENGINE_RENDERED_STATS_OMITTED"]
        self.assertNotIn("template", omission)
        self.assertNotIn("LP.CITIZEN.BULLET", patterns)
        self.assertNotIn("LP.REGIONAL.BULLET", patterns)
        with self.assertRaisesRegex(PATTERNS.PatternError, "structural"):
            PATTERNS.render_pattern(
                self.catalog,
                "LP.BUILDING.ENGINE_RENDERED_STATS_OMITTED",
                {},
            )

    def test_engine_rendered_stat_validator_preserves_cross_city_amenity(self) -> None:
        duplicated = (
            "- +1 [ICON_Citizen] Citizen slot, and +2 [ICON_Culture] Culture to "
            "[ICON_Citizen] Citizens in the Quarter.\n"
            "- +1 [ICON_Amenities] Amenity to the city."
        )
        self.assertEqual(
            len(PATTERNS.validate_engine_rendered_building_stats_omitted(duplicated)),
            3,
        )
        transaction = (
            "- +1 [ICON_Culture] Culture bonus to trade routes to the city. "
            "+1 [ICON_Amenities] Amenity to the origin city."
        )
        self.assertEqual(
            PATTERNS.validate_engine_rendered_building_stats_omitted(transaction),
            [],
        )


if __name__ == "__main__":
    unittest.main()
