from __future__ import annotations

import unittest
from pathlib import Path

from validate_quarter import (
    find_repo_root,
    markdown_sections,
    matches_any,
    resolve_dot_path,
    validate,
)


class HelperTests(unittest.TestCase):
    def test_resolve_dot_path_supports_mapping_and_list(self) -> None:
        document = {"stages": {"items": [{"value": 7}]}}
        self.assertEqual(resolve_dot_path(document, "stages.items.0.value"), (True, 7))
        self.assertEqual(resolve_dot_path(document, "stages.items.1.value"), (False, None))

    def test_markdown_sections_extracts_loc_blocks(self) -> None:
        sections = markdown_sections("# File\n## LOC_ONE\nOne\n### Note\nTwo\n## LOC_TWO\nThree")
        self.assertEqual(sections["LOC_ONE"], "One\n### Note\nTwo")
        self.assertEqual(sections["LOC_TWO"], "Three")

    def test_glob_scope_normalizes_separators(self) -> None:
        self.assertTrue(matches_any("project/localization/CSC_TAILORS_TEXT.md", ["project/localization/**"]))
        self.assertTrue(matches_any(r"project\localization\CSC_TAILORS_TEXT.md", ["project/localization/**"]))


class RepositoryContractTests(unittest.TestCase):
    def test_tailors_l0_contract_is_valid(self) -> None:
        root = find_repo_root(Path(__file__).parent)
        report = validate(root, "tailors", phase_name=None, ready=False, generated=False)
        self.assertEqual(report.errors, [])
        self.assertGreater(report.checks, 250)


if __name__ == "__main__":
    unittest.main()
