"""Discovery tests use arbitrary filenames and identities, never the workshop preset."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from discovery import classify, find_blends, make_job
from export_scene import read_xml, txt, MODELS, POINTS, STATES, model_instance


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
        rows[0]['metadata']['template_asset'] = 'Assets/Factory.ast'
        rows[1]['metadata']['template_asset'] = 'Assets/Warehouse.ast'
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

    def test_existing_pantry_geometry_asset_can_be_reused_without_local_geo_fgx(self):
        (self.root/'XLPs').mkdir()
        (self.root/'XLPs/CSC_Tilebases.xlp').write_text('''<XLP><m_Entries><Element>
            <m_EntryID text="CSC_TAILORS_Rugs"/><m_ObjectName text="CSC_TAILORS_Rugs"/>
            </Element></m_Entries></XLP>''')
        ast=self.root/'Assets/CSC_TAILORS_Rugs.ast'
        ast.write_text('''<Asset><m_GeometrySet><m_ModelInstances><Element>
            <m_GeoName text="WON_Great_Zimbabwe_RugsF"/>
            </Element></m_ModelInstances></m_GeometrySet><m_Name text="CSC_TAILORS_Rugs"/></Asset>''')
        defaults={'templates':{},'reuse_existing_assets':['CSC_TAILORS_Rugs']}
        rows=[self.row('rugs.blend','prop','CSC_TAILORS_Rugs'),
              self.row('new.blend','prop','NewProp')]
        job,report=make_job(rows,defaults,self.root,self.root,self.root/'out',{})
        self.assertFalse(report['blockers'])
        self.assertEqual(job['references'],[{'asset_id':'CSC_TAILORS_Rugs'}])
        self.assertEqual([p['asset_id'] for p in job['props']],['NewProp'])
        self.assertEqual(report['files'][0]['status'],'existing_asset_reference')
        ast.write_text(ast.read_text().replace('WON_Great_Zimbabwe_RugsF','CSC_TAILORS_Rugs'))
        _,report=make_job(rows,defaults,self.root,self.root,self.root/'out',{})
        self.assertIn('own GEO/FGX',report['blockers'][0])

    def test_prior_run_can_replace_its_own_installed_prop_but_not_a_changed_collision(self):
        row = self.row('custom.blend', 'prop', 'CSC_Custom')
        output = self.root/'export-runs/current'
        prior = self.root/'export-runs/prior'
        prior.mkdir(parents=True)
        installed = self.root/'Assets/CSC_Custom.ast'
        installed.write_bytes(b'pipeline output')
        (prior/'job.json').write_text(json.dumps({
            'mod_root': str(self.root),
            'props': [{'asset_id': 'CSC_Custom', 'blend': row['path']}]}))
        (prior/'install-receipt.json').write_text(json.dumps({'installed_sha256': {
            'Assets\\CSC_Custom.ast': hashlib.sha256(installed.read_bytes()).hexdigest()}}))
        job, report = make_job([row], {'templates': {}}, self.root, self.root, output, {})
        self.assertFalse(report['blockers'])
        self.assertEqual([item['asset_id'] for item in job['props']], ['CSC_Custom'])
        installed.write_bytes(b'unrelated later edit')
        _, report = make_job([row], {'templates': {}}, self.root, self.root, output, {})
        self.assertIn('already has this ID', report['blockers'][0])

    def test_missing_decal_and_ambiguous_template_block(self):
        row = self.row('a.blend', 'building', 'Product', 'FactoryMesh')
        row['metadata']['template_asset'] = 'Assets/Factory.ast'
        row['metadata']['decals'] = ['Missing']
        _, report = self.job([row])
        self.assertIn('missing decal', report['blockers'][0])
        root = read_xml(self.root / 'Assets/Factory.ast')
        root.find(MODELS).append(copy.deepcopy(root.find(MODELS)[0]))
        import xml.etree.ElementTree as ET
        ET.ElementTree(root).write(self.root / 'Assets/Factory.ast')
        _, report = self.job([row])
        self.assertIn('2 building template/model matches', report['blockers'][0])
        self.template('Factory', 'FactoryMesh', 'FactoryModel', 'Ash')
        row['metadata'].update(template_asset='Assets/Factory.ast', decals=[])
        _, report = self.job([row])
        self.assertFalse(report['blockers'])

    def test_new_building_needs_no_existing_output_or_mesh_match(self):
        row = self.row('new.blend', 'building', 'BrandNew', 'UnseenMesh')
        job, report = self.job([row])
        self.assertFalse(report['blockers'])
        entry = job['buildings'][0]
        self.assertEqual(entry['template_profile'], 'tilebase')
        self.assertFalse((self.root / 'Assets/BrandNew.ast').exists())
        root = read_xml(entry['template_asset'])
        self.assertEqual(txt(root, 'm_ClassName'), 'TileBase')
        self.assertEqual(len(root.find(POINTS)), 0)
        self.assertEqual(len(root.find(MODELS)), 1)
        states = {txt(r, 'm_StateName'): r for r in root.find(MODELS)[0].find('m_GroupStates')}
        self.assertEqual(set(states), set(STATES))
        model = {'asset_id': 'BrandNew', 'meshes': [{'name': 'UnseenMesh',
                 'materials': [{'name': 'NewMaterial'}], 'triangles': [[0, 1, 2, 0]]}]}
        generated = model_instance(model, {'NewMaterial': 'NewRuntimeMaterial'},
                                   ('Worked', 'Unworked', 'Unbuilt'), states)
        self.assertEqual(txt(generated, 'm_GeoName'), 'BrandNew')
        for r in generated.find('m_GroupStates'):
            self.assertEqual(txt(r, 'm_MeshName'), 'UnseenMesh')

    def test_legacy_workshop_uses_owned_profile_with_or_without_old_output(self):
        row = self.row('any-name.blend', 'building', 'Sailmaking', 'WorkshopMesh')
        row['metadata'].update(template_asset='Assets/CSC_TAILORS_Textile_Workshop.ast',
                               replace_model='CSC_TAILORS_Textile_Workshop',
                               state_template_mesh='CSC_TAILORS_Textile_Workshop_Bldg',
                               decals=['NewPillage'])
        rows = [row, self.row('decal.blend', 'decal', 'NewPillage')]
        job, report = self.job(rows)
        self.assertFalse(report['blockers'])
        entry = job['buildings'][0]
        self.assertEqual(entry['template_profile'], 'level1_small')
        self.assertEqual(entry['preserve_models'], ['CSC_Level_1_S_CON+PIL', 'CSC_Level_1_Decals'])
        self.assertEqual(entry['decals'], ['NewPillage'])
        (self.root / row['metadata']['template_asset']).write_text('deliberately invalid old output')
        again, report = self.job(rows)
        self.assertFalse(report['blockers'])
        self.assertEqual(job, again)

    def test_legacy_tailor_self_templates_do_not_require_existing_outputs(self):
        rows = []
        for ident in ('CSC_TAILORS_Tailor', 'CSC_TAILORS_Tailor_2'):
            row = self.row(ident + '.blend', 'building', ident, 'CSC_Level_2_Bldg')
            row['metadata'].update(template_asset=f'Assets/{ident}.ast',
                                   replace_model=ident,
                                   state_template_mesh='CSC_Level_2_Bldg')
            rows.append(row)
        job, report = self.job(rows)
        self.assertFalse(report['blockers'])
        self.assertEqual([entry['template_profile'] for entry in job['buildings']],
                         ['tilebase', 'tilebase'])
        self.assertTrue(all(Path(entry['template_asset']).is_file()
                            for entry in job['buildings']))
        self.assertFalse(any((self.root / 'Assets' / (ident + '.ast')).exists()
                             for ident in ('CSC_TAILORS_Tailor', 'CSC_TAILORS_Tailor_2')))

    def test_explicit_profile_and_invalid_inputs(self):
        row = self.row('new.blend', 'building', 'New', 'Mesh')
        row['metadata']['template_profile'] = 'level1_small'
        job, report = self.job([row])
        self.assertFalse(report['blockers'])
        self.assertEqual(job['buildings'][0]['template_profile'], 'level1_small')
        row['metadata']['template_profile'] = 'unknown'
        self.assertIn('Unknown template_profile', self.job([row])[1]['blockers'][0])
        del row['metadata']['template_profile']
        row['metadata']['template_asset'] = 'Assets/MissingCustom.ast'
        self.assertTrue(self.job([row])[1]['blockers'])


if __name__ == '__main__':
    unittest.main()
