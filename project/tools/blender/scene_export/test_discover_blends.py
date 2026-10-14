"""Scene selection regressions, independent of the Blender runtime."""
import importlib.util
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('scene_discover_test', Path(__file__).with_name('discover_blends.py'))
module = importlib.util.module_from_spec(spec)
with patch.dict(sys.modules, {'bpy': types.ModuleType('bpy')}):
    spec.loader.exec_module(module)


class Scene(dict):
    def __init__(self, name, metadata=None):
        super().__init__()
        self.name = name
        if metadata is not None:
            self['csc_export'] = metadata


class SceneSelectionTests(unittest.TestCase):
    def test_review_ignore_does_not_conflict_with_export_metadata(self):
        for kind in ('building', 'shared_geometry'):
            export = Scene('Export', '{"kind":"' + kind + '"}')
            self.assertIs(module.export_scene([export, Scene('Review', '{"kind":"ignore"}')]), export)

    def test_multiple_actual_exports_still_block(self):
        with self.assertRaisesRegex(ValueError, 'Provide one Export'):
            module.export_scene([Scene('Export', '{"kind":"building"}'),
                                 Scene('Other', '{"kind":"building"}')])

    def test_metadata_free_export_and_single_scene_fallbacks(self):
        export = Scene('Export')
        self.assertIs(module.export_scene([export, Scene('Review')]), export)
        single = Scene('Only')
        self.assertIs(module.export_scene([single]), single)


if __name__ == '__main__':
    unittest.main()
