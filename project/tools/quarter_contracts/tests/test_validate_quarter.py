from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "validate_quarter.py"
SPEC = importlib.util.spec_from_file_location("validate_quarter", SCRIPT)
assert SPEC and SPEC.loader
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class DesignReferenceTests(unittest.TestCase):
    def test_resolves_ids_containing_periods(self) -> None:
        design = {
            "buildings": [
                {
                    "id": "D.STAGE2",
                    "effects": [{"id": "D.STAGE2.SERVICE", "value": 1}],
                }
            ]
        }
        resolved, value = VALIDATOR.resolve_design_ref(
            design, "buildings.D.STAGE2.effects.D.STAGE2.SERVICE"
        )
        self.assertTrue(resolved)
        self.assertEqual(value["value"], 1)

    def test_rejects_unknown_design_id(self) -> None:
        resolved, _ = VALIDATOR.resolve_design_ref(
            {"effects": [{"id": "D.KNOWN"}]}, "effects.D.UNKNOWN"
        )
        self.assertFalse(resolved)


class TailorsContractTests(unittest.TestCase):
    def test_current_contracts_pass(self) -> None:
        result = VALIDATOR.validate_quarter("tailors", check_clean_start=True)
        self.assertEqual(result.errors, [])

    def test_all_preserved_modsupport_mappings_are_detected(self) -> None:
        implementation = VALIDATOR.load_yaml(
            VALIDATOR.SPEC_ROOT / "tailors" / "implementation.yaml"
        )
        for mapping in implementation["preserved_inputs"]:
            with self.subTest(mapping=mapping["id"]):
                self.assertTrue(
                    VALIDATOR.mapping_exists(
                        VALIDATOR.ROOT / mapping["file"],
                        mapping["resource"],
                        mapping["class"],
                    )
                )

    def test_mapping_check_rejects_wrong_class(self) -> None:
        path = VALIDATOR.ROOT / "Civ Supply Chains/ModSupport/ModSupport_CH.sql"
        self.assertFalse(
            VALIDATOR.mapping_exists(
                path, "RESOURCE_AOM_HEMP", "CLASS_CSC_TAILORS_SPEC"
            )
        )


class SqlStyleTests(unittest.TestCase):
    def test_bakers_reference_matches_all_style_profiles(self) -> None:
        cases = [
            ("CSC_Q_BAKERS.sql", "core"),
            ("CSC_Q_BAKERS_GOLD.sql", "gold"),
            ("CSC_Q_BAKERS_MC_MODE.sql", "monopolies"),
            ("CSC_Q_BAKERS_MC_MODE_GOLD.sql", "monopolies_gold"),
        ]
        for filename, profile in cases:
            with self.subTest(filename=filename):
                failures = VALIDATOR.SQL_STYLE.validate_sql_style(
                    VALIDATOR.ROOT / "Civ Supply Chains/Data" / filename,
                    profile,
                    "bakers",
                    strict_whitespace=False,
                )
                self.assertEqual(failures, [])

    def test_new_quarter_style_rejects_bad_header_and_whitespace(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.sql"
            path.write_text("-- wrong  \n SELECT 1;\n", encoding="utf-8")
            failures = VALIDATOR.SQL_STYLE.validate_sql_style(
                path, "core", "tailors", strict_whitespace=True
            )
        self.assertTrue(any("line 1 must identify" in failure for failure in failures))
        self.assertTrue(any("trailing whitespace" in failure for failure in failures))
        self.assertTrue(any("keyword is indented" in failure for failure in failures))

    def test_gold_companion_rejects_non_gold_yield(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad_gold.sql"
            path.write_text(
                "-- CSC_Q_TAILORS_GOLD.sql\n"
                "-- Author: Henno\n"
                "INSERT INTO ModifierArguments\n"
                "\t(ModifierId, Name, Value) VALUES\n"
                "\t('M', 'YieldType', 'YIELD_CULTURE');\n",
                encoding="utf-8",
            )
            failures = VALIDATOR.SQL_STYLE.validate_sql_style(
                path, "gold", "tailors", strict_whitespace=True
            )
        self.assertTrue(any("non-Gold" in failure for failure in failures))


if __name__ == "__main__":
    unittest.main()
