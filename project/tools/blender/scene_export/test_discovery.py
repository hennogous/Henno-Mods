"""Discovery tests use arbitrary filenames and identities, never the workshop preset."""
import copy
from pathlib import Path
import tempfile
import unittest
from discovery import classify, find_blends, make_job


class DiscoveryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / 'Assets').mkdir()
        self.template('Factory', 'FactoryMesh', 'FactoryModel', 'Ash')
        self.template('Warehouse', 'WarehouseMesh', 'WarehouseModel')

    def template(self, name, mesh, model, decal=None):
        aux = f'<Element><m_Name text="AshInstance"/><m_GeoName text="{decal}"/></Element>' if decal else ''
        (self.root / 'Assets' / (name + '.ast')).write_text(f'''<Asset>
        <m_GeometrySet><m_ModelInstances><Element><m_Name text="{model}"/>
        <m_GroupStates><Element><m_MeshName text="{mesh}"/></Element></m_GroupStates>
        </Element>{aux}</m_ModelInstances></m_GeometrySet></Asset>''')

    def row(self, filename, kind, ident, mesh=''):
        return {'path': str(self.root / filename), 'scene': 'Export', 'sha256': 'test',
                'metadata': {'kind': kind, 'asset_id': ident}, 'armatures': [ident],
                'meshes': [{'name': mesh, 'role': 'building_geometry', 'asset_id': ident}] if mesh else []}

    def job(self, rows):
        return make_job(rows, {'templates': {}}, self.root, self.root, self.root / 'out', {})

    def test_only_top_level_blends_including_case_variants(self):
        for name in ['unrelated.blend', 'second.BLEND', 'backup.blend1', 'notes.txt']:
            (self.root / name).touch()
        (self.root / 'sub').mkdir()
        (self.root / 'sub' / 'third.blend').touch()
        self.assertEqual([p.name for p in find_blends(self.root)], ['second.BLEND', 'unrelated.blend'])

    def test_renaming_inputs_preserves_asset_template_and_decal_binding(self):
        rows = [self.row('anything.blend', 'building', 'ProductA', 'FactoryMesh'),
                self.row('else.blend', 'building', 'ProductB', 'WarehouseMesh'),
                self.row('red.blend', 'decal', 'Ash'), self.row('blue.blend', 'prop', 'Bench')]
        first, report = self.job(rows)
        self.assertEqual(report['blockers'], [])
        self.assertEqual(first['buildings'][0]['decals'], ['Ash'])
        self.assertEqual(first['buildings'][0]['preserve_models'], [])
        self.assertNotEqual(first['buildings'][0]['template_asset'], first['buildings'][1]['template_asset'])
        for n,row in enumerate(rows): row['path'] = str(self.root / f'new-{n}.blend')
        second, report = self.job(rows)
        self.assertEqual(report['blockers'], [])
        for section in ('buildings', 'props', 'decals'):
            for a,b in zip(first[section], second[section]):
                self.assertNotEqual(a.pop('blend'), b.pop('blend'))
                self.assertEqual(a,b)

    def test_legacy_building_identity_comes_from_mesh_not_filename(self):
        row = self.row('random.blend', 'building', 'Product', 'FactoryMesh')
        row['metadata'] = {}
        self.assertEqual(classify(row, {}), ('building', 'Product'))

    def test_duplicate_identity_blocks_whole_batch(self):
        a = self.row('one.blend', 'prop', 'Bench')
        b = self.row('two.blend', 'prop', 'bench')
        _, report = self.job([a,b])
        self.assertIn('Duplicate asset identity', report['blockers'][0])

    def test_unknown_files_block_and_explicit_ignore_is_reported(self):
        row = self.row('unknown.blend', 'prop', 'Unknown')
        row['metadata'] = {}
        _, report = self.job([row])
        self.assertTrue(report['blockers'])
        row['metadata'] = {'kind': 'ignore'}
        _, report = self.job([row, self.row('bench.blend', 'prop', 'Bench')])
        self.assertFalse(report['blockers'])
        self.assertEqual(report['files'][0]['status'], 'explicitly_ignored')

    def test_missing_decal_and_ambiguous_template_block(self):
        row = self.row('a.blend', 'building', 'Product', 'FactoryMesh')
        row['metadata']['decals'] = ['Missing']
        _, report = self.job([row])
        self.assertIn('missing decal', report['blockers'][0])
        self.template('Other', 'FactoryMesh', 'OtherModel')
        _, report = self.job([row])
        self.assertIn('2 building template/model matches', report['blockers'][0])
        row['metadata'].update(template_asset='Assets/Factory.ast', decals=[])
        _, report = self.job([row])
        self.assertFalse(report['blockers'])


if __name__ == '__main__':
    unittest.main()
