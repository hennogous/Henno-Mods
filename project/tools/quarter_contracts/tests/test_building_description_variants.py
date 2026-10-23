"""Prevent engine-stat duplication in conditional building-description overrides."""
from __future__ import annotations

import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "project/tools/localization"))
sys.path.insert(0, str(ROOT / "project/tools/quarter_contracts"))
import loc_md_to_sql as LOC
import validate_localization_patterns as PATTERNS


class BuildingDescriptionVariantTests(unittest.TestCase):
    duplicate = (
        "+1 [ICON_Citizen] Citizen slot, +1 [ICON_Food] Food and "
        "+1 [ICON_Culture] Culture to [ICON_Citizen] Citizens in the Quarter."
    )
    tag = "LOC_BUILDING_CSC_BAKERS_CAFE_DESCRIPTION_GARDEN"

    def entry(self, text=None, **changes):
        values = dict(heading="Override", line=1, mode="update", language="en_US",
                      tag=self.tag, tags=[], where=None, text=text or self.duplicate)
        values.update(changes)
        return LOC.Entry(**values)

    def test_all_entry_target_forms_reject_redundant_stats(self):
        entries = [
            self.entry(mode="upsert"),
            self.entry(),
            self.entry(tag=None, tags=[self.tag, self.tag.replace("_GARDEN", "")]),
            self.entry(tag=None, where=f"Tag = '{self.tag}'"),
            self.entry(tag=None, mode="raw", text=(
                f"UPDATE LocalizedText SET Text = {LOC.sql_quote(self.duplicate)} "
                f"WHERE Tag = '{self.tag}';"
            )),
            self.entry(tag=None, mode="raw", text=(
                "INSERT INTO LocalizedText (Language, Tag, Text) VALUES "
                f"('en_US', '{self.tag}', {LOC.sql_quote(self.duplicate)});"
            )),
        ]
        for entry in entries:
            with self.subTest(mode=entry.mode, tags=entry.tags, where=entry.where):
                failures = LOC.validate_editorial_entry(entry)
                self.assertTrue(any("Citizen slot" in item for item in failures))
                self.assertTrue(any("specialist yields" in item for item in failures))

    def test_plain_rendered_and_markdown_intrinsic_amenities_are_rejected(self):
        for prefix in ("", "- ", "* ", "[ICON_Bullet] ", "[NEWLINE]"):
            for suffix in ("to the city.", "within 6 tiles."):
                with self.subTest(prefix=prefix, suffix=suffix):
                    failures = LOC.validate_editorial_entry(self.entry(
                        text=prefix + "+1 [ICON_Amenities] Amenity " + suffix
                    ))
                    self.assertTrue(any("intrinsic Amenity" in item for item in failures))

    def test_service_disclosures_pedia_notifications_and_population_remain_valid(self):
        service = "+1 [ICON_Citizen] Citizen slot in the Harbor."
        entries = [
            self.entry(text=service),
            self.entry(text="A service grants +1 [ICON_Citizen] Citizen slot in the district."),
            self.entry(text=self.duplicate, tag="LOC_BUILDING_CSC_TAILORS_STAGE_3_SERVICE_DESCRIPTION"),
            self.entry(text=self.duplicate, tag="LOC_CSC_TAILORS_STAGE_3_EFFECT_DESCRIPTION_NEW"),
            self.entry(text=self.duplicate, tag="LOC_PEDIA_CONCEPTS_PAGE_CSC_SPECIALTY_CHAPTER_PROCESSING_PARA_1"),
            self.entry(text="+1 [ICON_Culture] Culture for every 5 [ICON_Citizen] Citizens in the city."),
            self.entry(text="+1 [ICON_Culture] Culture for every 5 [ICON_Citizen] Citizens in the Quarter."),
            self.entry(text="+1 [ICON_Amenities] Amenity to the origin city."),
        ]
        for entry in entries:
            with self.subTest(tag=entry.tag, text=entry.text):
                self.assertEqual(LOC.validate_editorial_entry(entry), [])

    def test_raw_replacement_checks_output_and_ignores_search_needles(self):
        # Removing an obsolete stat is valid; adding it through REPLACE is not.
        for old, new, rejected in ((self.duplicate, "", False), ("old", self.duplicate, True)):
            entry = self.entry(tag=None, mode="raw", text=(
                "-- +1 [ICON_Citizen] Citizen slot\n"
                f"UPDATE LocalizedText SET Text=REPLACE(Text,{LOC.sql_quote(old)},{LOC.sql_quote(new)}) "
                f"WHERE Tag='{self.tag}' AND INSTR(Text,{LOC.sql_quote(self.duplicate)})>0;"
            ))
            with self.subTest(rejected=rejected):
                self.assertEqual(bool(LOC.building_stat_errors(entry)), rejected)

    def test_real_combined_override_cannot_reintroduce_the_screenshot_line(self):
        source = LOC.parse_source(ROOT / "project/localization/ModSupport_LGD_MC_MODE_TEXT.md")
        source.entries[0].text += "[NEWLINE]" + self.duplicate
        with self.assertRaisesRegex(LOC.LocError, "engine-rendered Citizen slot"):
            LOC.render_sql(source)

    def test_catalog_source_audit_includes_nested_examples(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "examples" / "bad.md"
            path.parent.mkdir()
            path.write_text(
                "# Example\noutput: example.sql\n\n"
                f"## {self.tag}\nmode: update\n\n- {self.duplicate}\n",
                encoding="utf-8",
            )
            failures = PATTERNS.validate_localization_sources(Path(temporary))
            self.assertTrue(any("bad.md" in item and "Citizen slot" in item for item in failures))

    def test_cafe_effective_text_in_all_mode_and_garden_combinations(self):
        manifest = json.loads((ROOT / "project/modbuddy/CivSupplyChains.actions.json").read_text(encoding="utf-8"))
        family = {"CSC_BAKERS_TEXT", "CSC_MC_MODE_TEXT", "ModSupport_LGD_TEXT", "ModSupport_LGD_MC_MODE_TEXT"}
        actions = sorted(
            (action for action in manifest["blocks"]["inGameActions"] if action["id"] in family),
            key=lambda action: int(action["properties"]["LoadOrder"]),
        )
        self.assertEqual(len(actions), 4)
        for monopolies in (False, True):
            for garden in (False, True):
                enabled = {name for name, active in (("Monopolies_Mode", monopolies), ("ModSupport_LGD", garden)) if active}
                with self.subTest(monopolies=monopolies, garden=garden), sqlite3.connect(":memory:") as db:
                    db.execute("CREATE TABLE LocalizedText (Language TEXT, Tag TEXT, Text TEXT, PRIMARY KEY(Language,Tag))")
                    loaded = []
                    for action in actions:
                        if set(action.get("criteria", [])) <= enabled:
                            loaded.append(action["id"])
                            for file in action["files"]:
                                db.executescript((ROOT / "Civ Supply Chains" / file).read_text(encoding="utf-8"))
                    self.assertEqual("ModSupport_LGD_MC_MODE_TEXT" in loaded, monopolies and garden)
                    tag = self.tag if garden else self.tag.removesuffix("_GARDEN")
                    row = db.execute("SELECT Text FROM LocalizedText WHERE Language='en_US' AND Tag=?", (tag,)).fetchone()
                    self.assertIsNotNone(row)
                    description = row[0]
                    self.assertEqual(LOC.validate_engine_rendered_building_stats_omitted(description), [])
                    self.assertEqual("Industry" in description, monopolies)
                    self.assertEqual("Conservator" in description, garden)
                    self.assertIn("[ICON_Citizen] Citizens in the city", description)
                    self.assertIn("At Urbanization", description)


if __name__ == "__main__":
    unittest.main()
