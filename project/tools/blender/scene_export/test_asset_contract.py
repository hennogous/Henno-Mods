"""Focused contract checks without Blender, Asset Editor, or live mod writes."""
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET

from asset_contract import contract_for, assert_groups, state_rows, material_for_mesh, COBBLE_MATERIAL
from export_scene import (model_instance, read_xml, shared_model_from_geo,
                          txt, write_xml)


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
        self.assertEqual(contract['cobble_visible'], ['Worked', 'Construction'])
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


if __name__ == '__main__':
    unittest.main()
