from __future__ import annotations

import copy
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

    def test_phase_hash_ignores_unreferenced_design_subtrees(self) -> None:
        implementation = {
            "phases": [{"id": "one", "requirements": [{"design_refs": ["district"]}]}]
        }
        design = {"district": {"cost": 60}, "future": {"value": 1}}
        first = VALIDATOR.phase_design_sha256(design, implementation, "one")
        design["future"]["value"] = 2
        self.assertEqual(
            first, VALIDATOR.phase_design_sha256(design, implementation, "one")
        )


class TailorsContractTests(unittest.TestCase):
    def test_current_contracts_pass(self) -> None:
        result = VALIDATOR.validate_quarter("tailors", check_clean_start=True)
        self.assertEqual(result.errors, [])

    def test_quarter_icon_layout_uses_shared_catalog_convention(self) -> None:
        implementation = VALIDATOR.load_yaml(
            VALIDATOR.SPEC_ROOT / "tailors" / "implementation.yaml"
        )
        catalog = VALIDATOR.load_yaml(
            VALIDATOR.ROOT / implementation["gameplay_catalog"]
        )
        result = VALIDATOR.Validation()
        effective = VALIDATOR.validate_icon_atlas_layout(
            catalog, implementation, result
        )
        self.assertEqual(result.errors, [])
        self.assertEqual(effective, VALIDATOR.QUARTER_ICON_ATLAS_LAYOUT)

    def test_quarter_icon_layout_rejects_colliding_override(self) -> None:
        implementation = VALIDATOR.load_yaml(
            VALIDATOR.SPEC_ROOT / "tailors" / "implementation.yaml"
        )
        catalog = VALIDATOR.load_yaml(
            VALIDATOR.ROOT / implementation["gameplay_catalog"]
        )
        broken = copy.deepcopy(implementation)
        broken["icon_atlas_layout"]["overrides"] = {"stage3_building": 4}
        result = VALIDATOR.Validation()
        VALIDATOR.validate_icon_atlas_layout(catalog, broken, result)
        self.assertTrue(any("multiple semantic roles" in item for item in result.errors))

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

    def test_validation_ownership_and_engine_decisions_are_explicit(self) -> None:
        implementation = VALIDATOR.load_yaml(
            VALIDATOR.SPEC_ROOT / "tailors" / "implementation.yaml"
        )

    def test_approved_contract_requires_identity_timestamp_and_hash(self) -> None:
        control = VALIDATOR.load_yaml(
            VALIDATOR.SPEC_ROOT / "tailors" / "control.yaml"
        )
        invalid = copy.deepcopy(control)
        invalid["contract_approvals"]["design_transcription"]["status"] = "approved"
        result = VALIDATOR.Validation()
        VALIDATOR.validate_schema(invalid, "quarter-control.schema.json", result)
        self.assertTrue(
            any("design_transcription" in failure for failure in result.errors)
        )

    def test_every_build_output_has_exact_action_contract(self) -> None:
        implementation = VALIDATOR.load_yaml(
            VALIDATOR.SPEC_ROOT / "tailors" / "implementation.yaml"
        )
        content_only = {
            "icons",
            "buildings_artdef",
            "landmarks_artdef",
            "strategic_view_artdef",
            "property_ranges_artdef",
            "tilebase_xlp",
        }
        source_only = {
            key
            for key in implementation["planned_outputs"]
            if key.endswith("_source")
        }
        expected = set(implementation["planned_outputs"]) - content_only - source_only
        self.assertEqual(set(implementation["build_wiring"]["actions"]), expected)
        ownership = implementation["validation_ownership"]
        self.assertEqual(ownership["automated"]["owner"], "implementation_agent")
        self.assertTrue(ownership["automated"]["required_before_handoff"])
        self.assertEqual(ownership["in_game"]["owner"], "user")
        self.assertFalse(ownership["in_game"]["required_before_handoff"])
        self.assertEqual(implementation["open_engine_decisions"], [])
        self.assertEqual(
            {decision["id"] for decision in implementation["resolved_engine_decisions"]},
            {
                "E.DECIMAL_POPULATION",
                "E.TRADE_STACKING",
                "E.SERVICE_PERSISTENCE",
            },
        )


class SqlStyleTests(unittest.TestCase):
    def test_bakers_layout_formatter_is_idempotent(self) -> None:
        source = """INSERT INTO Example\n        ( A, B )\nVALUES  ( 'SHORT', 'ONE' ),\n        ( 'A_LONGER_VALUE', 'TWO' );\n"""
        formatter = VALIDATOR.SQL_STYLE.SQL_LAYOUT
        formatted = formatter.format_sql_layout_text(source)
        self.assertEqual(formatted, formatter.format_sql_layout_text(formatted))
        self.assertIn("'SHORT',", formatted)
        first = formatted.splitlines()[2].index("'ONE'")
        second = formatted.splitlines()[3].index("'TWO'")
        self.assertEqual(first, second)

    def test_compact_tuple_layout_is_rejected_for_new_quarter_sql(self) -> None:
        formatter = VALIDATOR.SQL_STYLE.SQL_LAYOUT
        compact = """INSERT INTO Example\n        ( A, B )\nVALUES  ( 'SHORT', 'ONE' ),\n        ( 'A_LONGER_VALUE', 'TWO' );\n"""
        self.assertNotEqual(compact, formatter.format_sql_layout_text(compact))

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
