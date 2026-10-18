"""Regression checks for relationship icons and clean MCUIS service labels."""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / 'project/tools/localization'))
import loc_md_to_sql as LOC

class LocalizationEditorialTests(unittest.TestCase):
    def entry(self, text, tag='LOC_TEST_DESCRIPTION', mode='upsert'):
        return LOC.Entry(heading=tag, line=1, mode=mode, language='en_US', tag=tag, tags=[], where=None, text=text)

    def test_current_localization_sources_follow_rules(self):
        for path in sorted((ROOT/'project/localization').glob('*.md')):
            source = LOC.parse_source(path)
            for entry in source.entries:
                with self.subTest(source=path.name, entry=entry.heading):
                    self.assertEqual(LOC.validate_editorial_entry(entry), [])

    def test_missing_or_wrong_icons_are_rejected(self):
        for text in ('Base Materials', 'Specialty Material', 'sales districts', 'Goods Providers', '[ICON_CSC_SPEC] Base Materials'):
            with self.subTest(text=text):
                self.assertTrue(LOC.relationship_icon_errors(text))

    def test_native_civilopedia_chapter_headings_stay_plain(self):
        tag = 'LOC_PEDIA_DISTRICTS_PAGE_DISTRICT_CSC_TAILORS_QUARTER_CHAPTER_CSCBASE_TITLE'
        self.assertEqual(LOC.validate_editorial_entry(self.entry('Base Materials', tag)), [])
        for text in ('[ICON_CSC_BASE] Base Materials', '[ICON_Culture] Historical Context'):
            with self.subTest(text=text):
                self.assertTrue(LOC.validate_editorial_entry(self.entry(text, tag)))
        self.assertTrue(LOC.validate_editorial_entry(self.entry('Base Materials', tag.replace('_TITLE', '_PARA_1'))))

    def test_grouped_chapter_headings_stay_plain(self):
        entry = self.entry('Specialty Materials', 'Grouped titles')
        entry.tag = None
        entry.tags = ['LOC_PEDIA_RESOURCES_PAGE_RESOURCE_FLAX_CHAPTER_CSCHAIN_TITLE']
        self.assertEqual(LOC.validate_editorial_entry(entry), [])
        entry.text = '[ICON_CSC_SPEC] Specialty Materials'
        self.assertTrue(LOC.validate_editorial_entry(entry))

    def test_shared_material_noun_requires_both_icons(self):
        self.assertEqual(len(LOC.relationship_icon_errors('Base and Specialty Materials')), 2)
        self.assertEqual(LOC.relationship_icon_errors('[ICON_CSC_BASE] Base and [ICON_CSC_SPEC] Specialty Materials'), [])
        self.assertEqual(LOC.relationship_icon_errors('[ICON_CSC_BASE] Base or [ICON_CSC_SPEC] Specialty Materials'), [])

    def test_correct_icons_and_ordinary_words_are_accepted(self):
        text = '[ICON_CSC_BASE] Base Materials; [ICON_CSC_SPEC] Specialty Materials; [ICON_CSC_SALES] Sales Districts; [ICON_CSC_GOODS] Goods Providers. Base game and specialty goods.'
        self.assertEqual(LOC.relationship_icon_errors(text), [])

    def test_raw_sql_visible_role_labels_are_checked(self):
        entry=self.entry("INSERT INTO LocalizedText VALUES('en_US','LOC_TEST','Base Materials:');",mode='raw')
        self.assertTrue(LOC.validate_editorial_entry(entry))

    def test_sql_search_needles_and_comments_are_not_display_text(self):
        entry=self.entry("-- Base Materials are used in this query.\nUPDATE LocalizedText SET Text='[ICON_CSC_SPEC] Specialty Materials' WHERE instr(Text, 'Specialty Materials')>0;",mode='raw')
        self.assertEqual(LOC.validate_editorial_entry(entry), [])

    def test_venue_suffix_rejected_in_preview_and_notification_families(self):
        for venue in ('BOLSHOI', 'BROADWAY', 'SYDNEY'):
            name='{LOC_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_'+venue+'_NAME}'
            for state in ('', '_NEW', '_INCREASED', '_DECREASED', '_REMOVED'):
                tag='LOC_CSC_TAILORS_STAGE_4_EFFECT_DESCRIPTION_'+venue+state
                with self.subTest(venue=venue,state=state):
                    self.assertTrue(LOC.validate_editorial_entry(self.entry(name+' service at the venue: +2 Tourism',tag)))
                    self.assertEqual(LOC.validate_editorial_entry(self.entry(name+': +2 Tourism. [NEWLINE]Supply Chain: adjacent Wonder.',tag)), [])

    def test_venue_context_remains_allowed_in_service_descriptions(self):
        text='{LOC_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_BOLSHOI_NAME} at Bolshoi Theatre'
        self.assertEqual(LOC.validate_editorial_entry(self.entry(text,'LOC_SERVICE_DESCRIPTION')), [])

if __name__ == '__main__':
    unittest.main()
