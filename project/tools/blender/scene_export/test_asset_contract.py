"""Focused contract checks without Blender, Asset Editor, or live mod writes."""
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET

from asset_contract import contract_for, assert_groups, state_rows, material_for_mesh, COBBLE_MATERIAL
from export_scene import (model_instance, read_xml, shared_model_from_geo, value,
                          txt, write_xml, geometry, native_catalogue_binding, write_cn6)


def geo(ident, groups):
    root = ET.Element('Geometry')
    meshes = ET.SubElement(root, 'm_Meshes')
    for mesh_name, group_name in groups:
        mesh = ET.SubElement(meshes, 'Element')
        ET.SubElement(mesh, 'm_Name', text=mesh_name)
        group_set = ET.SubElement(mesh, 'm_Groups')
        group = ET.SubElement(group_set, 'Element')
        ET.SubElement(group, 'm_Name', text=group_name)
    ET.SubElement(root, 'm_Name', text=ident)
    return root


class AssetContractTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.mod = Path(self.tmp.name)
        for folder in ('Materials', 'Geometries'):
            (self.mod / folder).mkdir()
        for ident in ('CSC_TAILORS_E', 'CSC_TAILORS_NE', 'CSC_ALL_Props_01',
                      COBBLE_MATERIAL):
            (self.mod / 'Materials' / (ident + '.mtl')).write_text(
                f'<Material><m_Name text="{ident}"/></Material>')
        self.shared('CSC_Level_2_CON+PIL', [('Building', 'Building'),
                                           ('Scaffolding', 'Pillage_Construction_01')])
        self.shared('CSC_ALL_Stage_3_Cobble_Decals', [('Cobble', COBBLE_MATERIAL)])

    def shared(self, ident, groups):
        write_xml(self.mod / 'Geometries' / (ident + '.geo'), geo(ident, groups))
        (self.mod / 'Geometries' / (ident + '.fgx')).write_bytes(b'fixture FGX')

    def test_stage_level_materials_and_missing_future_inputs(self):
        contract = contract_for('CSC_TAILORS_Textile_Workshop',
                                {'quarter': 'TAILORS', 'supply_chain_stage': 3}, self.mod)
        self.assertEqual(contract['building_level'], 2)
        self.assertEqual(contract['ruin_geometry'], 'CSC_Level_2_CON+PIL')
        self.assertEqual(contract['cobble_geometry'], 'CSC_ALL_Stage_3_Cobble_Decals')
        self.assertEqual(contract['prop_material'], 'CSC_ALL_Props_01')
        self.assertEqual(contract['cobble_visible'], ['Worked'])
        with self.assertRaisesRegex(ValueError, 'required existing material missing'):
            contract_for('CSC_CARPENTERS_Shop',
                         {'quarter': 'CARPENTERS', 'supply_chain_stage': 3}, self.mod)
        with self.assertRaisesRegex(ValueError, 'required shared geometry missing'):
            contract_for('CSC_TAILORS_Later',
                         {'quarter': 'TAILORS', 'supply_chain_stage': 4}, self.mod)

    def test_authored_construction_source_can_be_staged_before_install(self):
        contract = contract_for('CSC_TAILORS_Shop',
                                {'quarter':'TAILORS','supply_chain_stage':3,
                                 'construction_geometry':'CSC_TAILORS_Shop_CON+PIL'}, self.mod)
        self.assertEqual(contract['ruin_geometry'],'CSC_TAILORS_Shop_CON+PIL')

    def test_authored_paving_can_replace_missing_stage_cobble(self):
        metadata = {'quarter': 'TAILORS', 'supply_chain_stage': 4,
                    'construction_geometry': 'CSC_TAILORS_Shop_CON+PIL',
                    'cobble_geometry': None, 'decals': ['Entrance_Path'],
                    'decal_states': {'Entrance_Path': ['Worked', 'Unworked']}}
        contract = contract_for('CSC_TAILORS_Shop', metadata, self.mod)
        self.assertNotIn('cobble_geometry', contract)
        metadata['decal_states']['Entrance_Path'] = ['Pillaged']
        with self.assertRaisesRegex(ValueError, 'authored Worked decal'):
            contract_for('CSC_TAILORS_Shop', metadata, self.mod)

    def test_shared_models_get_exact_five_state_tables(self):
        ruin = shared_model_from_geo(self.mod, 'CSC_Level_2_CON+PIL',
            lambda group: 'Pillage_Construction_01' if group == 'Pillage_Construction_01' else 'CSC_TAILORS_NE',
            lambda group: ('Construction',) if group == 'Pillage_Construction_01' else ('Construction', 'Pillaged'))
        rows = state_rows(ruin)
        self.assertEqual(len(rows), 10)
        self.assertEqual(rows[('Building', 'Building', 'Pillaged')], (True, 'CSC_TAILORS_NE'))
        self.assertEqual(rows[('Scaffolding', 'Pillage_Construction_01', 'Pillaged')],
                         (False, 'Pillage_Construction_01'))
        assert_groups(ruin, read_xml(self.mod / 'Geometries/CSC_Level_2_CON+PIL.geo'),
                      lambda mesh, group, state: (
                          state == 'Construction' if group == 'Pillage_Construction_01' else state in ('Construction', 'Pillaged'),
                          'Pillage_Construction_01' if group == 'Pillage_Construction_01' else 'CSC_TAILORS_NE'))
        rows[('Building', 'Building', 'Pillaged')] = (False, 'CSC_TAILORS_NE')
        for row in ruin.findall('m_GroupStates/Element'):
            if txt(row, 'm_MeshName') == 'Building' and txt(row, 'm_StateName') == 'Pillaged':
                for value in row.findall('m_Values/m_Values/Element'):
                    if txt(value, 'm_ParamName') == 'Visible':
                        value.find('m_bValue').text = 'false'
        with self.assertRaisesRegex(ValueError, 'group-state mismatch'):
            assert_groups(ruin, read_xml(self.mod / 'Geometries/CSC_Level_2_CON+PIL.geo'),
                          lambda mesh, group, state: (state == 'Pillaged', 'CSC_TAILORS_NE'))

    def test_unused_material_slots_do_not_create_geometry_groups(self):
        model = {'asset_id': 'Shop', 'kind': 'building', 'meshes': [
            {'name': 'Fixed', 'materials': [{'name': 'Used'}, {'name': 'Unused'}],
             'triangles': [[0, 1, 2, 0]], 'vertices': [[], [], []]}]}
        template = ET.fromstring('<Geometry><m_Meshes/><m_Bones/><m_ModelName/><m_Name/>'
                                 '<m_SourceFilePath/><m_SourceObjectName/><m_ClassName/><m_Tags/><m_DataFiles/></Geometry>')
        output = geometry(model, template)
        self.assertEqual([txt(g, 'm_Name') for g in output.findall('m_Meshes/Element/m_Groups/Element')], ['Used'])
        assert_groups(model_instance(model, {'Used': 'Material'}, ('Worked',)), output,
                      lambda mesh, group, state: (state == 'Worked', 'Material'))

    def test_decal_states_reject_building_parameters_before_install(self):
        model = {'asset_id': 'Pillage', 'kind': 'decal', 'meshes': [
            {'name': 'Decal', 'materials': [{'name': 'Pillage_Decals'}],
             'triangles': [[0, 1, 2, 0]]}]}
        building = model_instance(dict(model, kind='building'),
                                  {'Pillage_Decals': 'Pillage_Decals'}, ('Worked',))
        template = {txt(row, 'm_StateName'): row for row in building.findall('m_GroupStates/Element')}
        decal = model_instance(model, {'Pillage_Decals': 'Pillage_Decals'}, ('Pillaged',), template)
        decal_geo = geo('Pillage', [('Decal', 'Pillage_Decals')])
        ET.SubElement(decal_geo, 'm_ClassName', text='DecalGeometry')
        expected = lambda mesh, group, state: (state == 'Pillaged', 'Pillage_Decals')
        assert_groups(decal, decal_geo, expected)
        self.assertEqual(state_rows(decal)[('Decal', 'Pillage_Decals', 'Pillaged')],
                         (True, 'Pillage_Decals'))
        # A valid visibility/material table must not hide an incompatible shader parameter.
        value(decal.find('m_GroupStates/Element/m_Values/m_Values'), 'SnowMaterial', 'DefaultSnowMaterial')
        with self.assertRaisesRegex(ValueError, 'DecalGeometry state parameters'):
            assert_groups(decal, decal_geo, expected)

    def test_shared_cobble_uses_native_decal_schema(self):
        path = self.mod / 'Geometries/CSC_ALL_Stage_3_Cobble_Decals.geo'
        root = read_xml(path)
        ET.SubElement(root, 'm_ClassName', text='DecalGeometry')
        write_xml(path, root)
        cobble = shared_model_from_geo(self.mod, 'CSC_ALL_Stage_3_Cobble_Decals',
                                      lambda group: COBBLE_MATERIAL,
                                      lambda group: ('Worked', 'Construction'))
        assert_groups(cobble, root,
                      lambda mesh, group, state: (state in ('Worked', 'Construction'), COBBLE_MATERIAL))

    def test_cn6_compacts_unused_materials_and_remaps_triangle_indices(self):
        model = {'asset_id': 'Shop', 'meshes': [
            {'name': 'Fixed', 'materials': [{'name': 'Unused'}, {'name': 'Used'}],
             'triangles': [[0, 1, 2, 1]], 'vertices': [[0.0] * 18 for _ in range(3)]}]}
        path = self.mod / 'shop.cn6'
        write_cn6(path, model)
        text = path.read_text()
        self.assertNotIn('"Unused"', text)
        self.assertIn('triangles\n0 1 2 0\n', text)
        self.assertEqual(model['meshes'][0]['triangles'][0][3], 1)

    def test_cn6_delimiter_mesh_names_match_geo_and_ast_without_source_edits(self):
        model = {'asset_id': 'Pillage', 'kind': 'decal', 'meshes': [
            {'name': 'Plane11008#M', 'materials': [{'name': 'Ruin_Debris_Decal'}],
             'triangles': [[0, 1, 2, 0]], 'vertices': [[0.0] * 18 for _ in range(3)]}]}
        path = self.mod / 'pillage.cn6'
        write_cn6(path, model)
        self.assertIn('mesh:"Plane11008_M"', path.read_text())
        template = ET.fromstring('<Geometry><m_Meshes/><m_Bones/><m_ModelName/><m_Name/>'
                                 '<m_SourceFilePath/><m_SourceObjectName/><m_ClassName/><m_Tags/><m_DataFiles/></Geometry>')
        output = geometry(model, template)
        self.assertEqual(txt(output, 'm_Meshes/Element/m_Name'), 'Plane11008_M')
        instance = model_instance(model, {'Ruin_Debris_Decal': 'Ruin_Debris_Decal'}, ('Pillaged',))
        assert_groups(instance, output,
                      lambda mesh, group, state: (state == 'Pillaged', 'Ruin_Debris_Decal'))
        self.assertEqual(txt(instance, 'm_GroupStates/Element/m_MeshName'), 'Plane11008_M')
        self.assertEqual(model['meshes'][0]['name'], 'Plane11008#M')
        model['meshes'].append(dict(model['meshes'][0], name='Plane11008_M'))
        with self.assertRaisesRegex(ValueError, 'mesh names collide'):
            write_cn6(path, model)

    def test_new_native_catalogue_binding_uses_exact_nonfallback_entry(self):
        row = {'entry_id': 'Shrub', 'asset_class': 'TileBase', 'package': 'landmarks/tilebases',
               'xlp': r'Civ6\pantry\XLPs\tilebases.xlp'}
        fallback = dict(row, xlp=r'Civ6\pantry\XLPs\tilebases_fallback.xlp')
        binding = native_catalogue_binding('Shrub', {'native_bindings': [fallback, row]})
        self.assertEqual(txt(binding, 'm_XLPPath'), 'tilebases.xlp')
        self.assertEqual(txt(binding, 'm_EntryName'), 'Shrub')
        self.assertIsNone(native_catalogue_binding('Other', {'native_bindings': [row]}))
        with self.assertRaisesRegex(ValueError, 'ambiguous'):
            native_catalogue_binding('Shrub', {'native_bindings': [row, dict(row, package='another')]})

    def test_main_and_fixed_meshes_can_have_distinct_materials_and_states(self):
        model = {'asset_id': 'CSC_TAILORS_Shop', 'meshes': [
            {'name': 'Shop', 'materials': [{'name': 'SameBlenderName'}], 'triangles': [[0,1,2,0]]},
            {'name': 'CSC_Fixed_Loom', 'materials': [{'name': 'SameBlenderName'}], 'triangles': [[0,1,2,0]]}]}
        root = model_instance(model, {('Shop', 'SameBlenderName'): 'CSC_TAILORS_E',
                                      ('CSC_Fixed_Loom', 'SameBlenderName'): 'CSC_ALL_Props_01'},
                              {'Shop': ('Worked',), 'CSC_Fixed_Loom': ('Worked',)})
        rows = state_rows(root)
        self.assertEqual(rows[('Shop', 'SameBlenderName', 'Worked')], (True, 'CSC_TAILORS_E'))
        self.assertEqual(rows[('CSC_Fixed_Loom', 'SameBlenderName', 'Worked')],
                         (True, 'CSC_ALL_Props_01'))
        self.assertEqual(rows[('Shop', 'SameBlenderName', 'Unworked')], (False, 'CSC_TAILORS_E'))

    def test_embedded_prop_group_and_leanto_keep_distinct_material_roles(self):
        contract={'building_material':'CSC_TAILORS_E','prop_material':'CSC_ALL_Props_01'}
        job={'material_bindings':{'ClothGroup':'CSC_ALL_Props_01'}}
        building={'name':'Shop','role':'building_geometry'}
        leanto={'name':'CSC_Storage_LeanTo','role':'fixed_geometry'}
        self.assertEqual(material_for_mesh(building,{'name':'ClothGroup'},contract,job),
                         'CSC_ALL_Props_01')
        self.assertEqual(material_for_mesh(building,{'name':'StoneGroup'},contract,job),
                         'CSC_TAILORS_E')
        self.assertEqual(material_for_mesh(leanto,{'name':'LeanToGroup'},contract,job),
                         'CSC_TAILORS_E')


    def test_fixed_architecture_keeps_explicit_building_material(self):
        contract = {'building_material': 'CSC_TAILORS_E', 'prop_material': 'CSC_ALL_Props_01'}
        panes = {'name': 'Original_Window_Panes', 'role': 'fixed_geometry'}
        self.assertEqual(material_for_mesh(panes, {'name': 'Kit', 'external': 'CSC_TAILORS_E'}, contract, {}),
                         'CSC_TAILORS_E')
        self.assertEqual(material_for_mesh(panes, {'name': 'Kit'}, contract,
                                         {'material_bindings': {'Kit': 'CSC_TAILORS_E'}}), 'CSC_TAILORS_E')
        with self.assertRaisesRegex(ValueError, 'fixed_geometry does not imply'):
            material_for_mesh(panes, {'name': 'Kit'}, contract, {})
        with self.assertRaisesRegex(ValueError, 'outside the building/prop contract'):
            material_for_mesh(panes, {'name': 'Kit', 'external': 'CSC_TAILORS_NE'}, contract, {})

    def test_intact_geometry_rejects_used_construction_material(self):
        contract = {'building_material': 'CSC_TAILORS_E', 'prop_material': 'CSC_ALL_Props_01'}
        with self.assertRaisesRegex(ValueError, 'construction/pillage material in intact'):
            material_for_mesh({'name': 'Building', 'role': 'building_geometry'},
                              {'name': 'CSC_Level_3_CON+PIL_Bldg'}, contract, {})


if __name__ == '__main__':
    unittest.main()
