from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "validate_phase.py"
SPEC = importlib.util.spec_from_file_location("validate_phase", SCRIPT)
assert SPEC and SPEC.loader
PHASES = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PHASES)

ASSERTIONS_SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "quarter_checks"
    / "tailors_assertions.py"
)
ASSERTIONS_SPEC = importlib.util.spec_from_file_location(
    "tailors_assertions", ASSERTIONS_SCRIPT
)
assert ASSERTIONS_SPEC and ASSERTIONS_SPEC.loader
ASSERTIONS = importlib.util.module_from_spec(ASSERTIONS_SPEC)
ASSERTIONS_SPEC.loader.exec_module(ASSERTIONS)


class SqlBoundaryTests(unittest.TestCase):
    def test_complete_sql_is_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "complete.sql"
            path.write_text("INSERT INTO T (A) VALUES (1);\n", encoding="utf-8")
            self.assertEqual(PHASES.validate_statement_boundaries(path), [])

    def test_truncated_sql_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "truncated.sql"
            path.write_text("INSERT INTO T (A) VALUES (1", encoding="utf-8")
            failures = PHASES.validate_statement_boundaries(path)
            self.assertTrue(any("complete SQLite statement" in item for item in failures))


class ModBuddyWiringTests(unittest.TestCase):
    def setUp(self) -> None:
        self.wiring = {
            "actions": {
                "core": {
                    "id": "CSC_Q_TAILORS",
                    "type": "UpdateDatabase",
                    "file": "Data/CSC_Q_TAILORS.sql",
                    "load_order": 100,
                    "criteria": [],
                }
            }
        }

    def test_exact_action_wiring_is_accepted(self) -> None:
        actions = {
            "blocks": {
                "inGameActions": [
                    {
                        "id": "CSC_Q_TAILORS",
                        "type": "UpdateDatabase",
                        "properties": {"LoadOrder": "100"},
                        "files": ["Data/CSC_Q_TAILORS.sql"],
                    }
                ]
            }
        }
        self.assertEqual(
            PHASES.validate_action_wiring(actions, self.wiring, {"core"}), []
        )

    def test_wrong_action_type_and_criteria_are_rejected(self) -> None:
        actions = {
            "blocks": {
                "inGameActions": [
                    {
                        "id": "CSC_Q_TAILORS",
                        "type": "UpdateText",
                        "properties": {"LoadOrder": "100"},
                        "criteria": ["Monopolies_Mode"],
                        "files": ["Data/CSC_Q_TAILORS.sql"],
                    }
                ]
            }
        }
        failures = PHASES.validate_action_wiring(actions, self.wiring, {"core"})
        self.assertTrue(any("action type" in item for item in failures))
        self.assertTrue(any("criteria" in item for item in failures))

    def test_unrequired_future_output_is_ignored(self) -> None:
        self.assertEqual(
            PHASES.validate_action_wiring(
                {"blocks": {"inGameActions": []}}, self.wiring, set()
            ),
            [],
        )


class TailorsPhaseContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.implementation = PHASES.CONTRACTS.load_yaml(
            PHASES.SPEC_ROOT / "tailors" / "implementation.yaml"
        )

    def test_each_phase_has_exact_assertion_requirement_coverage(self) -> None:
        for phase in self.implementation["phases"]:
            phase_id = phase["id"]
            declared = {item["id"] for item in phase["requirements"]}
            with self.subTest(phase=phase_id):
                self.assertEqual(ASSERTIONS.REQUIREMENTS_BY_PHASE[phase_id], declared)

    def test_each_phase_declares_required_validation_layers(self) -> None:
        for phase_id, contract in self.implementation["phase_validation"].items():
            with self.subTest(phase=phase_id):
                self.assertIn("contract", contract["required_suites"])
                self.assertIn("output_completeness", contract["required_suites"])
                self.assertIn("semantic_rows", contract["required_suites"])

    def test_future_red_semantic_sentinel_blocks_premature_handoff(self) -> None:
        failures = ASSERTIONS.validate_phase_assertions(
            PHASES.ROOT, "stage4", self.implementation
        )
        self.assertTrue(any("still red" in item for item in failures))

    def test_dockmaster_mcuis_strings_reject_a_second_sign(self) -> None:
        source = (
            PHASES.ROOT / "project/localization/CSC_TAILORS_TEXT.md"
        ).read_text(encoding="utf-8")
        self.assertEqual(ASSERTIONS._validate_dockmaster_mcuis_signs(source), [])
        stage2_heading = "## LOC_CSC_TAILORS_STAGE_2_EFFECT_DESCRIPTION\n"
        heading_at = source.index(stage2_heading)
        amount_at = source.index("{1_TotalAmount}%", heading_at)
        broken = (
            source[:amount_at]
            + "+{1_TotalAmount}%"
            + source[amount_at + len("{1_TotalAmount}%"):]
        )
        failures = ASSERTIONS._validate_dockmaster_mcuis_signs(broken)
        self.assertTrue(any("dynamically signs amounts" in item for item in failures))

    def test_tailor_description_rejects_engine_rendered_stats(self) -> None:
        assertions_source = ASSERTIONS_SCRIPT.read_text(encoding="utf-8")
        self.assertIn("[ICON_Citizen] Citizen slot", assertions_source)
        self.assertIn("[ICON_Amenities] Amenity to the city", assertions_source)
        self.assertIn("repeats engine-rendered building stats", assertions_source)

    def test_tailors_icon_binding_check_is_exact(self) -> None:
        self.assertEqual(
            ASSERTIONS._validate_tailors_icon_bindings(
                PHASES.ROOT,
                (
                    ("ICON_DISTRICT_CSC_TAILORS_QUARTER", 0),
                    ("ICON_DISTRICT_CSC_TAILORS_QUARTER_FOW", 1),
                    ("ICON_BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP", 4),
                    ("ICON_BUILDING_CSC_TAILORS_TAILOR", 5),
                    ("ICON_BUILDING_CSC_TAILORS_STAGE_2_SERVICE", 8),
                    ("ICON_BUILDING_CSC_TAILORS_STAGE_3_SERVICE", 9),
                ),
            ),
            [],
        )
        failures = ASSERTIONS._validate_tailors_icon_bindings(
            PHASES.ROOT,
            (("ICON_BUILDING_CSC_TAILORS_TAILOR", 6),),
        )
        self.assertTrue(any("index 6" in item for item in failures))

    def test_visual_state_bridge_belongs_to_its_gameplay_phase(self) -> None:
        phase = next(
            phase
            for phase in self.implementation["phases"]
            if phase["id"] == "materials_and_stage2"
        )
        dockmaster = next(item for item in phase["requirements"] if item["id"] == "I.DOCKMASTER")
        self.assertIn("art.properties.D.ART.STAGE2.LIGHTHOUSE", dockmaster["design_refs"])
        self.assertIn("GP.ART.PROPERTY_BRIDGE", dockmaster["gameplay_patterns"])
        self.assertIn("art_property_lua", dockmaster["outputs"])

    def test_physical_art_is_not_an_implementation_contract_output(self) -> None:
        forbidden = {
            "buildings_artdef",
            "landmarks_artdef",
            "strategic_view_artdef",
            "property_ranges_artdef",
            "tilebase_xlp",
        }
        self.assertTrue(forbidden.isdisjoint(self.implementation["planned_outputs"]))
        declared = {
            output
            for phase in self.implementation["phases"]
            for requirement in phase["requirements"]
            for output in requirement["outputs"]
        }
        self.assertTrue(forbidden.isdisjoint(declared))

    def test_blocked_phase_cannot_be_validated_as_implementation(self) -> None:
        result = PHASES.validate_phase(
            "tailors", "stage4", handoff=False, run_commands=False
        )
        self.assertTrue(any("gate status" in item for item in result.errors))


if __name__ == "__main__":
    unittest.main()
