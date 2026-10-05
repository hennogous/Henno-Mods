from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
SCRIPT = Path(__file__).resolve().parents[1] / "quarter_checks/tailors_assertions.py"
SPEC = importlib.util.spec_from_file_location("tailors_assertions", SCRIPT)
assert SPEC and SPEC.loader
ASSERTIONS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ASSERTIONS)


class MappedResourcePediaTests(unittest.TestCase):
    def setUp(self) -> None:
        import tempfile
        import json
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.mod = self.root / "Civ Supply Chains"
        self.mod.mkdir()
        manifest = self.root / "project/modbuddy/CivSupplyChains.actions.json"
        manifest.parent.mkdir(parents=True)
        manifest.write_text(json.dumps({"blocks": {"inGameActions": [
            {"id": "mapping", "type": "UpdateDatabase", "files": ["mapping.sql"], "criteria": ["NovelMod"]},
            {"id": "text", "type": "UpdateText", "files": ["text.sql"], "criteria": ["NovelMod"]},
        ]}}))
        (self.mod / "mapping.sql").write_text("INSERT INTO TypeTags(Type,Tag) SELECT ResourceType,'CLASS_CSC_TEST_SPEC' FROM Resources WHERE ResourceType IN ('RESOURCE_NOVEL');")
        self.text = """INSERT INTO LocalizedText VALUES
            ('en_US','LOC_PEDIA_RESOURCES_PAGE_RESOURCE_NOVEL_CHAPTER_CSCQUAR_TITLE','Supply Chains'),
            ('en_US','LOC_PEDIA_RESOURCES_PAGE_RESOURCE_NOVEL_CHAPTER_CSCQUAR_PARA_1','Specialty Materials:[NEWLINE][NEWLINE][ICON_BULLET] [ICON_TEST] Test Quarter'),
            ('en_US','LOC_PEDIA_DISTRICTS_PAGE_DISTRICT_CSC_TEST_QUARTER_CHAPTER_CSCSPEC_PARA_1','[ICON_RESOURCE_NOVEL] Novel');"""
        (self.mod / "text.sql").write_text(self.text)
        import yaml
        folder = self.root / "project/specs/test"
        folder.mkdir(parents=True)
        (folder / "design.yaml").write_text(yaml.safe_dump({
            "identity": {"abbreviation": "TEST"},
            "materials": {"specialty": {"optional": [{"resource": "RESOURCE_NOVEL", "mod": "NovelMod"}]}},
        }))
        (folder / "control.yaml").write_text(yaml.safe_dump({"phase_gates": {"foundation": {"status": "approved"}}}))
        (folder / "implementation.yaml").write_text(yaml.safe_dump({"preserved_inputs": [{
            "resource": "RESOURCE_NOVEL", "class": "CLASS_CSC_TEST_SPEC",
            "file": "Civ Supply Chains/mapping.sql", "criteria": ["NovelMod"],
        }]}))

    def test_unlisted_resource_and_quarter_are_discovered(self) -> None:
        self.assertEqual(ASSERTIONS._validate_mapped_resource_pedia(self.root), [])

    def test_resource_missing_from_gameplay_and_text_is_rejected(self) -> None:
        (self.mod / "mapping.sql").write_text("-- omitted mapping")
        (self.mod / "text.sql").write_text("-- omitted text")
        failures = ASSERTIONS._validate_mapped_resource_pedia(self.root)
        self.assertTrue(any('design-required gameplay mapping is missing' in failure for failure in failures))
        self.assertTrue(any('reciprocal' in failure for failure in failures))

    def test_unexpected_gameplay_mapping_is_rejected(self) -> None:
        with (self.mod / "mapping.sql").open('a') as output:
            output.write("INSERT INTO TypeTags(Type,Tag) VALUES('RESOURCE_UNDESIGNED','CLASS_CSC_TEST_BASE');")
        self.assertTrue(any('unexpected gameplay material mapping' in failure for failure in ASSERTIONS._validate_mapped_resource_pedia(self.root)))

    def test_wrong_gameplay_role_is_rejected(self) -> None:
        path = self.mod / "mapping.sql"
        path.write_text(path.read_text().replace('CLASS_CSC_TEST_SPEC', 'CLASS_CSC_TEST_BASE'))
        failures = ASSERTIONS._validate_mapped_resource_pedia(self.root)
        self.assertTrue(any('design-required gameplay mapping is missing' in failure for failure in failures))
        self.assertTrue(any('unexpected gameplay material mapping' in failure for failure in failures))

    def test_missing_implementation_binding_is_rejected(self) -> None:
        import yaml
        (self.root / "project/specs/test/implementation.yaml").write_text(yaml.safe_dump({"preserved_inputs": []}))
        self.assertTrue(any('requires exactly one implementation binding' in failure for failure in ASSERTIONS._validate_mapped_resource_pedia(self.root)))

    def test_unapproved_quarter_is_not_validated(self) -> None:
        import yaml
        (self.root / "project/specs/test/control.yaml").write_text(yaml.safe_dump({"phase_gates": {"foundation": {"status": "blocked_by_contract_review"}}}))
        expected, failures = ASSERTIONS._material_design_expectations(self.root)
        self.assertEqual(expected, [])
        self.assertTrue(failures)

    def test_missing_reciprocal_entry_is_rejected(self) -> None:
        (self.mod / "text.sql").write_text(self.text.replace('RESOURCE_NOVEL_CHAPTER_CSCQUAR_PARA_1', 'RESOURCE_OTHER_CHAPTER_CSCQUAR_PARA_1'))
        self.assertTrue(any('RESOURCE_NOVEL' in failure and 'reciprocal' in failure for failure in ASSERTIONS._validate_mapped_resource_pedia(self.root)))

    def test_wrong_role_is_rejected(self) -> None:
        (self.mod / "text.sql").write_text(self.text.replace('Specialty Materials:', 'Base Materials:'))
        self.assertTrue(any('wrong material role' in failure for failure in ASSERTIONS._validate_mapped_resource_pedia(self.root)))

    def test_missing_quarter_entry_is_rejected(self) -> None:
        (self.mod / "text.sql").write_text(self.text.replace('[ICON_RESOURCE_NOVEL]', '[ICON_RESOURCE_OTHER]'))
        self.assertTrue(any('Quarter material list' in failure for failure in ASSERTIONS._validate_mapped_resource_pedia(self.root)))

    def test_mismatched_text_condition_is_rejected(self) -> None:
        import json
        path = self.root / "project/modbuddy/CivSupplyChains.actions.json"
        manifest = json.loads(path.read_text())
        manifest['blocks']['inGameActions'][1]['criteria'] = ['OtherMod']
        path.write_text(json.dumps(manifest))
        self.assertTrue(ASSERTIONS._validate_mapped_resource_pedia(self.root))


if __name__ == "__main__":
    unittest.main()
