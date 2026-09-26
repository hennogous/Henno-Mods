"""Native default-state validation, without requiring a Blender process."""
import importlib.util
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch


class SourceAssemblyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location(
            'decode_source_test', Path(__file__).with_name('decode_blend.py'))
        cls.decoder = importlib.util.module_from_spec(spec)
        with patch.dict('sys.modules', {'bpy': SimpleNamespace(),
                                       'bmesh': SimpleNamespace(),
                                       'mathutils': SimpleNamespace(Matrix=object)}):
            spec.loader.exec_module(cls.decoder)

    def setUp(self):
        self.intact = SimpleNamespace(name='Shrub', type='MESH')
        self.ruin = SimpleNamespace(name='Shrub_PIL', type='MESH')
        self.scene = SimpleNamespace(objects=[self.intact, self.ruin,
                                             SimpleNamespace(name='Root', type='EMPTY')])
        self.record = {'components': [{'object': 'Shrub'},
                                     {'object': 'Shrub_PIL', 'default_visible': False}]}

    def test_native_intact_assembly_excludes_other_states(self):
        self.assertEqual(self.decoder.source_mesh_components(
            self.scene, 'Shrub', self.record), [self.intact])

    def test_custom_master_requires_all_meshes(self):
        self.assertEqual(self.decoder.source_mesh_components(
            self.scene, 'Custom'), [self.intact, self.ruin])

    def test_missing_declared_visible_component_fails(self):
        self.record['components'].append({'object': 'Missing'})
        with self.assertRaisesRegex(ValueError, 'components missing'):
            self.decoder.source_mesh_components(self.scene, 'Shrub', self.record)

    def test_no_visible_components_fails(self):
        self.record['components'][0]['default_visible'] = False
        with self.assertRaisesRegex(ValueError, 'components missing'):
            self.decoder.source_mesh_components(self.scene, 'Shrub', self.record)
