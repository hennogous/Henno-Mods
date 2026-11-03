"""Exercise publication preparation when a corrected source is retired."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import prepare


class CorrectionRetirementTests(unittest.TestCase):
    def test_deleted_source_must_be_removed_from_correction_register(self):
        with tempfile.TemporaryDirectory(prefix='csc-handbook-retirement-') as directory:
            root = Path(directory)
            kb = root/'project/docs/civ6-ai'
            (kb/'data').mkdir(parents=True)
            (kb/'index.md').write_text('# Handbook\n', encoding='utf-8')
            old = root/'project/docs/integrations/csc-ai-roadmap.md'
            old.parent.mkdir(parents=True)
            old.write_text('# Original roadmap\n', encoding='utf-8')
            kept = old.with_name('csc-ai-objectives.md')
            kept.write_text('# Objectives\n', encoding='utf-8')
            relative_old = old.relative_to(root).as_posix()
            relative_kept = kept.relative_to(root).as_posix()
            corrections = [dict(id='COR-006', affected_sources=[relative_old, relative_kept],
                                summary='Historical trial closure.')]
            register = kb/'data/corrections.json'
            register.write_text(json.dumps(corrections), encoding='utf-8')
            stage = root/'docs/.ai-handbook/content'

            with patch.object(prepare, 'ROOT', root), patch.object(prepare, 'KB', kb):
                first = prepare.prepare(stage, update_catalog=True)
                self.assertEqual(first['sources'], 2)
                old_page = stage/'sources/project/docs/integrations/csc-ai-roadmap.md'
                self.assertTrue(old_page.is_file())

                old.unlink()
                with self.assertRaisesRegex(ValueError, 'Uncatalogued correction source: COR-006/'):
                    prepare.prepare(stage, update_catalog=True)

                corrections[0]['affected_sources'] = [relative_kept]
                register.write_text(json.dumps(corrections), encoding='utf-8')
                final = prepare.prepare(stage, update_catalog=True)
                self.assertEqual(final['sources'], 1)
                self.assertFalse(old_page.exists())
                self.assertTrue((stage/'sources/project/docs/integrations/csc-ai-objectives.md').is_file())
                published = json.loads((stage/'data/corrections.json').read_text(encoding='utf-8'))
                self.assertEqual(published[0]['affected_sources'], [relative_kept])

    def test_existing_but_unpublished_source_is_rejected(self):
        with tempfile.TemporaryDirectory(prefix='csc-handbook-unpublished-') as directory:
            root = Path(directory)
            kb = root/'project/docs/civ6-ai'
            (kb/'data').mkdir(parents=True)
            (kb/'index.md').write_text('# Handbook\n', encoding='utf-8')
            source = root/'project/docs/integrations/unrelated.md'
            source.parent.mkdir(parents=True)
            source.write_text('# Not part of the publication\n', encoding='utf-8')
            register = [dict(id='COR-TEST', affected_sources=[source.relative_to(root).as_posix()],
                             summary='An existing file alone is insufficient.')]
            (kb/'data/corrections.json').write_text(json.dumps(register), encoding='utf-8')
            with patch.object(prepare, 'ROOT', root), patch.object(prepare, 'KB', kb):
                with self.assertRaisesRegex(ValueError, 'Uncatalogued correction source: COR-TEST/'):
                    prepare.prepare(root/'docs/.ai-handbook/content', update_catalog=True)


if __name__ == '__main__':
    unittest.main()
