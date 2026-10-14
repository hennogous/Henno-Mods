"""Reject prose referrals in generated localization, including raw SQL blocks."""
from pathlib import Path
import copy
import sys
import unittest

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / 'project/tools/localization'))
import loc_md_to_sql as LOC

class LocalizationReferralTests(unittest.TestCase):
    def setUp(self):
        self.source = LOC.parse_source(ROOT / 'project/localization/CSC_TAILORS_TEXT.md')

    def test_current_sources_render_without_referrals(self):
        for name in ('CSC_TAILORS_TEXT.md', 'CSC_BAKERS_TEXT.md', 'ModSupport_LGD_TEXT.md'):
            LOC.render_sql(LOC.parse_source(ROOT / 'project/localization' / name))

    def test_referrals_are_rejected_in_text_and_raw_sql(self):
        for mode in ('upsert', 'raw'):
            for directive in ('See', 'Consult', 'Refer to'):
                source = copy.deepcopy(self.source)
                entry = next(entry for entry in source.entries if entry.mode == mode)
                entry.text += ' ' + directive + ' the ' + 'Civilopedia' + ' entry for details.'
                with self.subTest(mode=mode, directive=directive):
                    with self.assertRaisesRegex(LOC.LocError, 'state requirements and effects directly'):
                        LOC.render_sql(source)

if __name__ == '__main__':
    unittest.main()
