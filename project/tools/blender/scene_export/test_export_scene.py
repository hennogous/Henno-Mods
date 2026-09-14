"""Run: python -m unittest discover -s project/tools/blender/scene_export -v"""
import copy
import unittest
import xml.etree.ElementTree as ET
from export_scene import attachment_transform, merge_xlp, model_instance, geometry, validate_support, txt

class ContractTests(unittest.TestCase):
    def placement(self):
        return {'instance_id':'A','support':'ground','position':[10,-20,30], 'rotation_degrees':[0,0,90], 'scale':[2,2,2]}

    def test_position_units_rotation_sign_and_scale(self):
        result,problems=attachment_transform(self.placement(),{})
        self.assertEqual(result,{'position':[1,-2,3],'rotation':[0,0,-90],'scale':2})
        self.assertEqual(problems,[])

    def test_nonuniform_is_explicit_and_preserves_source(self):
        row=self.placement(); row['scale']=[.7,.9,.8]; before=copy.deepcopy(row)
        self.assertTrue(attachment_transform(row,{})[1])
        output,problems=attachment_transform(row,{'nonuniform_scale':'uniform-min'})
        self.assertTrue(problems); self.assertEqual(row,before)
        # Even a stale direct caller requesting the removed policy cannot bypass validation.
        from export_scene import attachment
        point, errors=attachment(row,None,'Owner',{'nonuniform_scale':'uniform-min'})
        self.assertIsNone(point); self.assertTrue(errors)

    def test_unsupported_transforms_stay_blocked(self):
        row=self.placement(); row['rotation_degrees'][0]=10
        self.assertTrue(attachment_transform(row,{})[1])
        row=self.placement(); row['shear_error']=.2
        self.assertTrue(attachment_transform(row,{})[1])

    def test_support_missing_and_cycles(self):
        a=self.placement(); a['support']='B'
        with self.assertRaises(ValueError): validate_support([a])
        b=copy.deepcopy(a); b['instance_id']='B'; b['support']='A'
        with self.assertRaises(ValueError): validate_support([a,b])
        b['support']='ground'; validate_support([a,b])
        self.assertTrue(attachment_transform(a,{})[1])
        result,problems=attachment_transform(a,{'supported_props':'independent-pivot'})
        self.assertFalse(problems); self.assertEqual(result['position'],[1,-2,3])

    def test_xlp_unique_and_idempotent_preserving_other_entries(self):
        root=ET.fromstring('<X><m_Entries><Element><m_EntryID text="Keep"/><m_ObjectName text="Other"/></Element></m_Entries></X>')
        merge_xlp(root,['New','New']); first=ET.tostring(root)
        merge_xlp(root,['New']); self.assertEqual(ET.tostring(root),first)
        self.assertEqual(txt(root,'m_Entries/Element/m_ObjectName'),'Other')
        with self.assertRaises(ValueError): merge_xlp(root,['Keep'])

    def test_all_groups_all_states_and_fixed_visibility(self):
        model={'asset_id':'A','meshes':[{'name':'Mesh1','materials':[{'name':'Wood'},{'name':'Cloth'}], 'triangles':[[0,1,2,0],[0,1,2,1]]}, {'name':'Mesh2','materials':[{'name':'Wood'}], 'triangles':[[0,1,2,0]]}]}
        root=model_instance(model,{'Wood':'M1','Cloth':'M2'},('Worked','Unworked'))
        rows=root.findall('m_GroupStates/Element'); self.assertEqual(len(rows),15)
        for row in rows:
            params={txt(v,'m_ParamName'):v for v in row.findall('m_Values/m_Values/Element')}
            self.assertEqual(params['Visible'].find('m_bValue').text, str(txt(row,'m_StateName') in ('Worked','Unworked')).lower())


import os
import json
import tempfile
import shutil
from pathlib import Path

@unittest.skipUnless(os.environ.get('CSC_EXPORT_TEST_JOB'), 'Set CSC_EXPORT_TEST_JOB for real workshop integration checks')
class WorkshopIntegration(unittest.TestCase):
    def setUp(self):
        import export_scene as ex
        self.ex=ex; self.job=ex.load_job(Path(os.environ['CSC_EXPORT_TEST_JOB']))
        original=Path(self.job['output'])
        self.tmp=tempfile.TemporaryDirectory(dir=original.parent,prefix='integration-')
        self.addCleanup(self.tmp.cleanup); self.job['output']=self.tmp.name
        self.out=Path(self.tmp.name); shutil.copy2(original/'decoded.json',self.out/'decoded.json')
        self.assertEqual(ex.build(self.job),0)
        self.stage=self.out/'stage'

    def canonical(self,e):
        return (e.tag,sorted(e.attrib.items()),(e.text or '').strip(),[self.canonical(c) for c in e])

    def test_workshop_state_geometry_and_xlp(self):
        ex=self.ex
        self.assertEqual(len(list((self.stage/'Assets').glob('*.ast'))),11)
        self.assertEqual(len(list((self.stage/'Geometries').glob('*.geo'))),12)
        original=ex.read_xml(Path(self.job['mod_root'])/self.job['buildings'][0].get('template_asset',self.job['templates'].get('asset','')))
        old={ex.txt(m,'m_Name'):m for m in original.find(ex.MODELS)}
        for b in self.job['buildings']:
            root=ex.read_xml(self.stage/'Assets'/(b['asset_id']+'.ast'))
            models={ex.txt(m,'m_Name'):m for m in root.find(ex.MODELS)}
            for name in b['preserve_models']: self.assertEqual(self.canonical(models[name]),self.canonical(old[name]))
            main=models[b['asset_id']]; mesh_names={ex.txt(r,'m_MeshName') for r in main.findall('m_GroupStates/Element')}
            self.assertIn('CSC_Fixed_Textile_Loom',mesh_names); self.assertIn('CSC_Fixed_Dye_Vat_Indigo',mesh_names)
            self.assertEqual(len(mesh_names),6)
            self.assertEqual(len(root.find(ex.POINTS)),16)
            decoded=json.loads((self.out/'decoded.json').read_text())['models'][b['asset_id']]
            placements={a['instance_id']:a for a in decoded['attachments']}
            for point in root.find(ex.POINTS):
                a=placements[ex.txt(point,'m_Name').removeprefix('CSC_Attach_')]
                for axis,expected in zip('xyz',a['position']):
                    self.assertAlmostEqual(float(point.findtext('m_position/'+axis))*10,expected,places=6)
                self.assertAlmostEqual(float(point.findtext('m_scale')),sum(a['scale'])/3,places=6)
            self.assertEqual(len(models['CSC_TAILORS_Textile_Workshop_PIL_Decals'].find('m_GroupStates')),55)
        xlp=ex.read_xml(self.stage/'XLPs/CSC_Tilebases.xlp')
        entries=[ex.txt(e,'m_EntryID') for e in xlp.find('m_Entries')]
        self.assertEqual(len(entries),len(set(entries)))
        self.assertNotIn('CSC_TAILORS_Textile_Workshop_PIL_Decals',entries)
        for ident in ['CSC_Attached_Textile_Loom_Teal','CSC_Attached_Dye_Vat_Indigo','CSC_Attached_Dye_Vat_Madder']:
            self.assertFalse((self.stage/'Assets'/(ident+'.ast')).exists())

    def test_rebuild_idempotent_and_protects_edited_stage(self):
        first=json.loads((self.out/'manifest.json').read_text())['files']
        self.assertEqual(self.ex.build(self.job),0)
        self.assertEqual(first,json.loads((self.out/'manifest.json').read_text())['files'])
        p=next((self.stage/'Assets').glob('*.ast')); p.write_text(p.read_text()+'\n<!-- manual edit -->')
        with self.assertRaises(ValueError): self.ex.build(self.job)

    def test_geometry_metadata_and_cn6_agree(self):
        decoded=json.loads((self.out/'decoded.json').read_text())
        for ident,m in decoded['models'].items():
            geo=self.ex.read_xml(self.stage/'Geometries'/(ident+'.geo'))
            self.assertEqual(geo.tag,'AssetObjects..GeometryInstance')
            self.assertEqual(len(geo.find('m_Meshes')),len(m['meshes']))
            for gr,mesh in zip(geo.find('m_Meshes'),m['meshes']):
                self.assertEqual(int(gr.findtext('m_nVertexCount')),len(mesh['vertices']))
                self.assertEqual(int(gr.findtext('m_nPrimitiveCount')),len(mesh['triangles']))
                self.assertEqual(sum(int(g.findtext('m_nPrims')) for g in gr.find('m_Groups')),len(mesh['triangles']))
            text=(self.stage/'CN6'/(ident+'.cn6')).read_text()
            self.assertEqual(text.count('mesh:"'),len(m['meshes']))
            for mesh in m['meshes']:
                for v in mesh['vertices']: self.assertEqual(len(v),18)

    def test_strict_policy_reports_and_blocks_conversion(self):
        self.job['policies']={}
        self.assertEqual(self.ex.build(self.job),2)
        with self.assertRaises(ValueError): self.ex.convert(self.job,'missing.exe','missing.exe')


    def test_converter_zero_exit_without_fgx_is_failure(self):
        from unittest.mock import patch
        with patch('export_scene.subprocess.run'):
            with self.assertRaisesRegex(ValueError,'produced no valid-sized output'):
                self.ex.convert(self.job,'missing.exe','missing.exe')

    def test_install_preserves_concurrent_xlp_entries_and_backs_up(self):
        # Simulate the conversion receipt; this exercises deployment, not FGX validity.
        manifest=json.loads((self.out/'manifest.json').read_text())
        report=json.loads((self.out/'report.json').read_text())
        target=self.out/'test-mod'; source=Path(self.job['mod_root'])
        for rel,h in manifest['destination_baseline'].items():
            if h is not None:
                dest=target/rel; dest.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(source/rel,dest)
        xlp=target/'XLPs/CSC_Tilebases.xlp'
        self.ex.write_xml(xlp,self.ex.merge_xlp(self.ex.read_xml(xlp),['CSC_Concurrent_Test']))
        manifest['converted_files']={str(p.relative_to(self.stage)):self.ex.sha(p) for p in self.stage.rglob('*') if p.is_file()}
        report['status']='converted_pending_asset_editor_and_game_review'
        (self.out/'manifest.json').write_text(json.dumps(manifest));(self.out/'report.json').write_text(json.dumps(report))
        before=(target/'Assets/CSC_TAILORS_Textile_Workshop.ast').read_bytes()
        self.job['mod_root']=str(target); self.ex.install(self.job)
        after=json.loads((self.out/'report.json').read_text())
        self.assertEqual((Path(after['backup'])/'Assets/CSC_TAILORS_Textile_Workshop.ast').read_bytes(),before)
        ids=[self.ex.txt(e,'m_EntryID') for e in self.ex.read_xml(xlp).find('m_Entries')]
        self.assertIn('CSC_Concurrent_Test',ids)
        tex=next((target/'Textures').glob('*.tex'))
        self.assertTrue(Path(self.ex.txt(self.ex.read_xml(tex),'m_SourceFilePath')).is_file())


class DDSValidationTests(unittest.TestCase):
    def test_reject_truncated_and_wrong_mips(self):
        import struct
        from unittest.mock import patch
        from export_scene import validate_dds
        header=bytearray(128); header[:4]=b'DDS '
        for offset,v in [(4,124),(12,2),(16,2),(28,2),(88,8)]: struct.pack_into('<I',header,offset,v)
        with patch.object(Path,'read_bytes',return_value=bytes(header)+b'\x00'*5):
            validate_dds('unused',{'format':'R8_UNORM','size':[2,2]})
        with patch.object(Path,'read_bytes',return_value=bytes(header)+b'\x00'*4):
            with self.assertRaises(ValueError): validate_dds('unused',{'format':'R8_UNORM','size':[2,2]})

if __name__=='__main__': unittest.main()
