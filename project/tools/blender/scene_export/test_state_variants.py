"""State wrappers retain native shader behavior and existing prop edits."""
import copy
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET

from export_scene import (STATES, MODELS, POINTS, model_instance, native_state_variant,
                          prop_state_templates, value, txt, write_xml)
from asset_contract import (material_is_ao_variant, state_rows, contract_visible_states,
                            contract_state_parameters, contract_material_binding)


def model():
    return {'asset_id':'CSC_Test', 'kind':'prop', 'meshes':[
        {'name':'Mesh#M', 'materials':[{'name':'OldGroup'}], 'triangles':[[0,1,2,0]]}]}


def source_asset():
    root = ET.Element('Asset')
    ET.SubElement(root,'m_Name',text='Native')
    parent = root
    for tag in MODELS.split('/'):
        parent = ET.SubElement(parent,tag)
    parent.append(model_instance(model(), {'OldGroup':'NativeFoliage'}, STATES))
    parent = root
    for tag in POINTS.split('/'):
        parent = ET.SubElement(parent,tag)
    return root


def canonical(node):
    return node.tag, sorted(node.attrib.items()), (node.text or '').strip(), tuple(canonical(c) for c in node)


class StateVariantTests(unittest.TestCase):
    def test_bundled_groups_keep_independent_construction_visibility(self):
        fixed={'name':'CSC_Fixed_Props','role':'fixed_geometry','materials':[
            {'name':'Arbour','visible_states':['Worked','Construction']},
            {'name':'Screens','visible_states':['Worked']}], 'triangles':[[0,1,2,0],[0,2,3,1]]}
        visible={(fixed['name'],m['name']):contract_visible_states(fixed,m) for m in fixed['materials']}
        root=model_instance({'asset_id':'CSC_Shop','meshes':[fixed]}, {'Arbour':'Shared','Screens':'DarkerAO'}, visible)
        rows=state_rows(root)
        self.assertEqual(rows[(fixed['name'],'Arbour','Construction')],(True,'Shared'))
        self.assertEqual(rows[(fixed['name'],'Screens','Construction')],(False,'DarkerAO'))
        self.assertFalse(rows[(fixed['name'],'Arbour','Pillaged')][0])

    def test_authored_visibility_does_not_expose_building_or_invalid_states(self):
        fixed={'name':'CSC_Fixed_Props','role':'fixed_geometry'}
        for states in [['Worked','Pillaged'],['Worked','Worked'],['Construction'],['Worked',{}]]:
            with self.assertRaisesRegex(ValueError,'civ_visible_states'):
                contract_visible_states(fixed,{'name':'Props','visible_states':states})
        with self.assertRaisesRegex(ValueError,'civ_visible_states'):
            contract_visible_states({'name':'Building','role':'building_geometry'},
                                    {'name':'Building','visible_states':['Worked','Construction']})

    def test_bundled_shader_parameters_override_building_template_and_reject_wrong_types(self):
        m=model();mesh=m['meshes'][0];mesh['role']='fixed_geometry'
        mat=mesh['materials'][0]
        mat['state_parameters']={s:{'EmissiveEnabled':s=='Worked','BurnMaterial':''} for s in STATES}
        contract_state_parameters(mesh,mat)
        template=model_instance(m,{'OldGroup':'Shared'},STATES)
        states={txt(r,'m_StateName'):r for r in template.findall('m_GroupStates/Element')}
        for row in states.values():
            next(p for p in row.findall('m_Values/m_Values/Element') if txt(p,'m_ParamName')=='EmissiveEnabled').find('m_bValue').text='true'
        result=model_instance(m,{'OldGroup':'Shared'},STATES,states)
        for row in result.findall('m_GroupStates/Element'):
            emission=next(p for p in row.findall('m_Values/m_Values/Element') if txt(p,'m_ParamName')=='EmissiveEnabled').findtext('m_bValue')
            self.assertEqual(emission,str(txt(row,'m_StateName')=='Worked').lower())
        mat['state_parameters']['Construction']['EmissiveEnabled']='true'
        with self.assertRaisesRegex(ValueError,'invalid fixed'):
            contract_state_parameters(mesh,mat)
        mat['state_parameters']['Construction']={'Visible':True}
        with self.assertRaisesRegex(ValueError,'invalid fixed'):
            contract_state_parameters(mesh,mat)

    def test_fixed_ao_override_reuses_shared_binding_and_selects_stable_private_variant(self):
        with tempfile.TemporaryDirectory() as directory:
            mod=Path(directory);root=ET.Element('Material');ET.SubElement(root,'m_Name',text='CSC_Props')
            vals=ET.SubElement(ET.SubElement(root,'m_CookParams'),'m_Values');value(vals,'AO','SharedAO')
            write_xml(mod/'Materials/CSC_Props.mtl',root)
            mesh={'name':'Fixed','role':'fixed_geometry'};mat={'name':'Props','external':'CSC_Props','ao_texture':'SharedAO'}
            contract={'building_material':'CSC_Building','prop_material':'CSC_Props'};job={'ao_policy':'stage_explicit'}
            self.assertEqual(contract_material_binding(mesh,mat,contract,job,mod),'CSC_Props')
            mat['ao_texture']='CSC_PrivateAO'
            self.assertEqual(contract_material_binding(mesh,mat,contract,job,mod),'CSC_Props__AO_CSC_PrivateAO')
            self.assertEqual(contract_material_binding(mesh,mat,contract,{'ao_policy':'reuse_existing'},mod),'CSC_Props')

    def test_native_wrapper_changes_only_identity_and_two_visibility_states(self):
        original = source_asset()
        before = canonical(original)
        variant = native_state_variant(original,'CSC_ALL_Plant',['Construction','Pillaged'])
        self.assertEqual(canonical(original),before)
        self.assertEqual(txt(variant,'m_Name'),'CSC_ALL_Plant')
        rows = state_rows(variant.find(MODELS+'/Element'))
        self.assertEqual({s for (_,_,s),(v,_) in rows.items() if v}, {'Worked','Unworked','Unbuilt'})
        # Restore exactly the two authorized changes and compare the entire native AST.
        variant.find('m_Name').set('text','Native')
        for row in variant.findall(MODELS+'/Element/m_GroupStates/Element'):
            if txt(row,'m_StateName') in ('Construction','Pillaged'):
                next(p for p in row.findall('m_Values/m_Values/Element')
                     if txt(p,'m_ParamName')=='Visible').find('m_bValue').text='true'
        self.assertEqual(canonical(variant),before)

    def test_native_wrapper_rejects_missing_group_state_and_nested_attachments(self):
        root = source_asset()
        gs = root.find(MODELS+'/Element/m_GroupStates')
        extra = copy.deepcopy(gs[0]); extra.find('m_GroupName').set('text','ExtraGroup');gs.append(extra)
        with self.assertRaisesRegex(ValueError,'every native group'):
            native_state_variant(root,'CSC_ALL_Plant',['Construction','Pillaged'])
        root = source_asset(); ET.SubElement(root.find(POINTS),'Element')
        with self.assertRaisesRegex(ValueError,'nested native attachments'):
            native_state_variant(root,'CSC_ALL_Plant',['Construction','Pillaged'])

    def test_native_wrapper_checks_groups_separately_per_model_instance(self):
        root = source_asset()
        models = root.find(MODELS)
        models.append(copy.deepcopy(models[0]))
        result = native_state_variant(root,'CSC_ALL_Plant',['Construction','Pillaged'])
        self.assertEqual(len(result.findall(MODELS+'/Element')),2)

    def test_native_wrapper_rejects_nonboolean_visibility(self):
        root = source_asset()
        for row in root.findall(MODELS+'/Element/m_GroupStates/Element'):
            if txt(row,'m_StateName')=='Construction':
                visible = next(p for p in row.findall('m_Values/m_Values/Element') if txt(p,'m_ParamName')=='Visible')
                visible.remove(visible.find('m_bValue'))
        with self.assertRaisesRegex(ValueError,'boolean Visible'):
            native_state_variant(root,'CSC_ALL_Plant',['Construction','Pillaged'])

    def test_prop_ao_group_rename_preserves_edited_visibility_and_shader_parameters(self):
        old = model_instance(model(), {'OldGroup':'Base'}, ('Worked','Construction'))
        for row in old.findall('m_GroupStates/Element'):
            value(row.find('m_Values/m_Values'),'CustomOverlay','Overlay_'+txt(row,'m_StateName'))
        new = model();new['meshes'][0]['materials'][0]['name']='NewAOGroup'
        templates = prop_state_templates(new,old)
        result = model_instance(new, {'NewAOGroup':'Base__AO_New'}, None, templates)
        self.assertEqual({s for (_,_,s),(v,_) in state_rows(result).items() if v}, {'Worked','Construction'})
        self.assertEqual({g for (_,g,_) in state_rows(result)}, {'NewAOGroup'})
        for row in result.findall('m_GroupStates/Element'):
            self.assertEqual(txt(row,'m_MeshName'),'Mesh_M')
            overlay = next(p for p in row.findall('m_Values/m_Values/Element') if txt(p,'m_ParamName')=='CustomOverlay')
            self.assertEqual(txt(overlay,'m_ObjectName'),'Overlay_'+txt(row,'m_StateName'))

    def test_prop_renamed_multiple_groups_cannot_guess_old_state_rows(self):
        old = model_instance(model(), {'OldGroup':'Base'}, ('Worked',))
        new = model();new['meshes'][0]['materials']=[{'name':'A'},{'name':'B'}]
        new['meshes'][0]['triangles'].append([0,2,3,1])
        with self.assertRaisesRegex(ValueError,'ambiguous/missing'):
            prop_state_templates(new,old)

    def test_contract_allows_only_ao_slot_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            mod = Path(directory)/'mod';stage = Path(directory)/'stage'
            base = ET.Element('Material');ET.SubElement(base,'m_Name',text='CSC_Base')
            vals = ET.SubElement(ET.SubElement(base,'m_CookParams'),'m_Values')
            for key,texture in [('AO','OldAO'),('BaseColor','OriginalColour')]:
                value(vals,key,texture)
            write_xml(mod/'Materials/CSC_Base.mtl',base)
            variant = copy.deepcopy(base);variant.find('m_Name').set('text','CSC_Base__AO_NewAO')
            variant.find('m_CookParams/m_Values/Element/m_ObjectName').set('text','NewAO')
            path = stage/'Materials/CSC_Base__AO_NewAO.mtl';write_xml(path,variant)
            write_xml(stage/'Textures/NewAO.tex',ET.Element('Texture'))
            self.assertTrue(material_is_ao_variant('CSC_Base__AO_NewAO','CSC_Base',stage,mod))
            variant.findall('m_CookParams/m_Values/Element')[1].find('m_ObjectName').set('text','WrongColour')
            write_xml(path,variant)
            self.assertFalse(material_is_ao_variant('CSC_Base__AO_NewAO','CSC_Base',stage,mod))


if __name__ == '__main__':
    unittest.main()
