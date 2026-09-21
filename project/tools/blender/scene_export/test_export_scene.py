"""Run: python -m unittest discover -s project/tools/blender/scene_export -v"""
import copy
import math
import unittest
import xml.etree.ElementTree as ET
from export_scene import attachment_transform, merge_xlp, model_instance, geometry, validate_support, txt

class ContractTests(unittest.TestCase):
    def test_reuse_existing_materials_never_generates_unbound_names(self):
        from export_scene import existing_material
        with tempfile.TemporaryDirectory() as directory:
            mod=Path(directory); (mod/'Materials').mkdir()
            (mod/'Materials/CSC_Existing.mtl').write_text('<Material/>')
            (mod/'Materials/CSC_FromBlender.mtl').write_text('<Material/>')
            job={'material_policy':'reuse_existing','material_bindings':{'BlenderName':'CSC_Existing'}}
            self.assertEqual(existing_material({'name':'BlenderName'},job,mod),'CSC_Existing')
            self.assertEqual(existing_material({'name':'CSC_Existing'},job,mod),'CSC_Existing')
            self.assertEqual(existing_material({'name':'Other','external':'CSC_Existing'},job,mod),'CSC_Existing')
            self.assertEqual(existing_material({'name':'BlenderName','external':'CSC_FromBlender'},job,mod),'CSC_FromBlender')
            with self.assertRaisesRegex(ValueError,'no existing material binding'):
                existing_material({'name':'Unmapped'},job,mod)
            with self.assertRaisesRegex(ValueError,'existing CSC material not found'):
                existing_material({'name':'Other','external':'CSC_Missing'},job,mod)

    def placement(self):
        return {'instance_id':'A','support':'ground','position':[10,-20,30], 'rotation_degrees':[0,0,90], 'scale':[2,2,2]}

    def test_position_units_rotation_sign_and_scale(self):
        result,problems=attachment_transform(self.placement(),{})
        self.assertEqual(result,{'position':[1,-2,3],'rotation':[0,0,-math.pi/2],'scale':2})
        self.assertEqual(problems,[])

    def test_ae_display_uses_radians_from_ast(self):
        from export_scene import attachment, csc_binding
        a=self.placement(); a['rotation_degrees'][2]=56.419046185935734
        point,problems=attachment(a,csc_binding('Prop',Path('CSC_Tilebases.xlp')),'Owner',{})
        self.assertFalse(problems)
        self.assertAlmostEqual(math.degrees(float(point.findtext('m_orientation/z'))),-56.419046185935734,places=5)

    def test_unit_scale_noise_is_cleaned_without_changing_intentional_scale(self):
        a=self.placement(); a['scale']=[.99999952,.99999952,.9999994]
        self.assertEqual(attachment_transform(a,{})[0]['scale'],1.0)
        a['scale']=[.6975625]*3
        self.assertAlmostEqual(attachment_transform(a,{})[0]['scale'],.6975625)

    def test_nonuniform_is_explicit_and_preserves_source(self):
        row=self.placement(); row['scale']=[.7,.9,.8]; before=copy.deepcopy(row)
        self.assertTrue(attachment_transform(row,{})[1])
        output,problems=attachment_transform(row,{'nonuniform_scale':'uniform-min'})
        self.assertTrue(problems); self.assertEqual(row,before)
        # Even a stale direct caller requesting the removed policy cannot bypass validation.
        from export_scene import attachment
        point, errors=attachment(row,None,'Owner',{'nonuniform_scale':'uniform-min'})
        self.assertIsNone(point); self.assertTrue(errors)

    def test_xy_rotation_serializes_in_same_direction(self):
        row=self.placement(); row['rotation_degrees']=[10,-20,90]
        result,issues=attachment_transform(row,{})
        self.assertFalse(issues)
        self.assertEqual([round(math.degrees(v),5) for v in result['rotation']],[10,-20,-90])

    def test_sheared_transforms_stay_blocked(self):
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

    def test_shared_support_pivot_rejects_offset_even_with_legacy_policy(self):
        support = self.placement(); support['instance_id'] = 'Table'
        contents = copy.deepcopy(support)
        contents.update(instance_id='Contents', support='Table', terrain_follow='shared-support-pivot')
        validate_support([support, contents])
        self.assertFalse(attachment_transform(contents, {})[1])
        # Both placements evaluate height at the same location on a non-flat surface.
        terrain = lambda p: .1*p[0] - .2*p[1]
        for dz in [0, 13, -8]:
            support['position'][2] += dz; contents['position'][2] += dz
            validate_support([support, contents])
            self.assertEqual(terrain(support['position']), terrain(contents['position']))
        contents['position'][0] += .5
        with self.assertRaisesRegex(ValueError, 'must coincide'):
            validate_support([support, contents])

    def test_shared_support_pivot_cannot_claim_building_as_attachment_support(self):
        contents = self.placement()
        contents.update(support='building', terrain_follow='shared-support-pivot')
        with self.assertRaisesRegex(ValueError, 'needs an attachment support'):
            validate_support([contents])

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
        self.tmp=tempfile.TemporaryDirectory(prefix='csc-export-integration-')
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
            for name in b['preserve_models']:
                if name in old: self.assertEqual(self.canonical(models[name]),self.canonical(old[name]))
                else: self.assertIn(name, b['decals'])
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
                self.assertAlmostEqual(float(point.findtext('m_scale')),sum(a['scale'])/3,places=5)
                self.assertAlmostEqual(math.degrees(float(point.findtext('m_orientation/z'))),-a['rotation_degrees'][2],places=5)
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

    def test_reuse_mode_emits_no_material_or_texture_payload(self):
        if self.job.get('material_policy') != 'reuse_existing':
            self.skipTest('This integration job uses generated materials')
        self.assertFalse(list(self.stage.rglob('*.mtl')))
        self.assertFalse(list(self.stage.rglob('*.tex')))
        report=json.loads((self.out/'report.json').read_text())
        self.assertEqual(report['counts']['textures'],0)
        self.assertEqual(report['material_bindings']['CSC_Textile_Building_Material'],'CSC_TAILORS_E')

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
        existing=target/'Assets/CSC_TAILORS_Textile_Workshop.ast'
        existing.parent.mkdir(parents=True,exist_ok=True)
        if not existing.exists():
            existing.write_bytes(b'previous output for backup test')
            manifest['destination_baseline'][str(existing.relative_to(target))]=self.ex.sha(existing)
            (self.out/'manifest.json').write_text(json.dumps(manifest))
        before=existing.read_bytes()
        self.job['mod_root']=str(target); self.ex.install(self.job)
        after=json.loads((self.out/'report.json').read_text())
        self.assertEqual((Path(after['backup'])/'Assets/CSC_TAILORS_Textile_Workshop.ast').read_bytes(),before)
        ids=[self.ex.txt(e,'m_EntryID') for e in self.ex.read_xml(xlp).find('m_Entries')]
        self.assertIn('CSC_Concurrent_Test',ids)
        for tex in (target/'Textures').glob('*.tex'):
            self.assertTrue(Path(self.ex.txt(self.ex.read_xml(tex),'m_SourceFilePath')).is_file())


class UninstallTests(unittest.TestCase):
    def setUp(self):
        import export_scene as ex
        self.ex=ex
        self.tmp=tempfile.TemporaryDirectory(prefix='csc-uninstall-test-')
        self.addCleanup(self.tmp.cleanup)
        root=Path(self.tmp.name); self.mod=root/'mod'; self.out=root/'run'; self.stage=self.out/'stage'
        for p in (self.mod/'Assets',self.mod/'Geometries',self.mod/'XLPs',
                  self.stage/'Assets',self.stage/'Geometries',self.stage/'XLPs'):
            p.mkdir(parents=True,exist_ok=True)
        self.original=self.mod/'Assets/CSC_Old.ast'; self.original.write_bytes(b'original asset')
        (self.stage/'Assets/CSC_Old.ast').write_bytes(b'new asset')
        (self.stage/'Geometries/CSC_New.geo').write_bytes(b'new geometry')
        self.ex.write_xml(self.mod/'XLPs/CSC_Tilebases.xlp',self._xlp_root())
        self.ex.write_xml(self.stage/'XLPs/CSC_Tilebases.xlp',self.ex.merge_xlp(self.ex.read_xml(self.mod/'XLPs/CSC_Tilebases.xlp'),['CSC_New']))
        files={str(p.relative_to(self.stage)):self.ex.sha(p) for p in self.stage.rglob('*') if p.is_file()}
        baseline={rel:self.ex.sha(self.mod/rel) if (self.mod/rel).is_file() else None for rel in files}
        (self.out/'manifest.json').write_text(json.dumps({'converted_files':files,'destination_baseline':baseline,'textures':{}}))
        (self.out/'report.json').write_text(json.dumps({'status':'converted_pending_asset_editor_and_game_review',
            'assets':['CSC_Old','CSC_New']}))
        self.job={'output':str(self.out),'mod_root':str(self.mod)}

    def _xlp_root(self):
        root=self.ex.ET.Element('XLP'); entries=self.ex.elem(root,'m_Entries')
        row=self.ex.elem(entries,'Element'); self.ex.elem(row,'m_EntryID',text='CSC_Old')
        self.ex.elem(row,'m_ObjectName',text='CSC_Old')
        return root

    def test_uninstall_restores_prior_files_deletes_new_files_and_preserves_other_xlp_entries(self):
        self.ex.install(self.job)
        self.assertEqual(self.original.read_bytes(),b'new asset')
        new=self.mod/'Geometries/CSC_New.geo'; self.assertTrue(new.is_file())
        self.ex.write_xml(self.mod/'XLPs/CSC_Tilebases.xlp',self.ex.merge_xlp(
            self.ex.read_xml(self.mod/'XLPs/CSC_Tilebases.xlp'),['CSC_Later']))
        self.ex.uninstall(self.job,dry_run=True)
        self.assertTrue(new.is_file())
        self.ex.uninstall(self.job)
        self.assertEqual(self.original.read_bytes(),b'original asset')
        self.assertFalse(new.exists())
        ids={self.ex.txt(e,'m_EntryID') for e in self.ex.read_xml(self.mod/'XLPs/CSC_Tilebases.xlp').find('m_Entries')}
        self.assertEqual(ids,{'CSC_Old','CSC_Later'})
        self.assertEqual(json.loads((self.out/'report.json').read_text())['status'],'uninstalled')

    def test_uninstall_blocks_changed_installed_file(self):
        self.ex.install(self.job)
        self.original.write_bytes(b'later edit')
        with self.assertRaisesRegex(ValueError,'changed or missing'):
            self.ex.uninstall(self.job)
        self.assertEqual(self.original.read_bytes(),b'later edit')
        self.assertTrue((self.mod/'Geometries/CSC_New.geo').exists())

    def test_force_purge_backs_up_changed_output_and_accepts_missing_output(self):
        self.ex.install(self.job)
        self.original.write_bytes(b'later edit')
        (self.mod/'Geometries/CSC_New.geo').unlink()
        self.ex.uninstall(self.job,purge=True,force=True)
        self.assertFalse(self.original.exists())
        self.assertFalse((self.mod/'Geometries/CSC_New.geo').exists())
        report=json.loads((self.out/'report.json').read_text())
        backup=Path(report['uninstall_backup'])
        self.assertEqual((backup/'Assets/CSC_Old.ast').read_bytes(),b'later edit')
        self.assertFalse((backup/'Geometries/CSC_New.geo').exists())
        ids={self.ex.txt(e,'m_EntryID') for e in self.ex.read_xml(
            self.mod/'XLPs/CSC_Tilebases.xlp').find('m_Entries')}
        self.assertEqual(ids,set())
        self.assertEqual(report['status'],'purged')

    def test_uninstall_older_run_without_receipt_uses_stage_and_backup(self):
        self.ex.install(self.job)
        (self.out/'install-receipt.json').unlink()
        self.ex.uninstall(self.job)
        self.assertEqual(self.original.read_bytes(),b'original asset')
        self.assertFalse((self.mod/'Geometries/CSC_New.geo').exists())


    def test_purge_deletes_replaced_output_and_its_prior_xlp_registration(self):
        self.ex.install(self.job)
        self.ex.uninstall(self.job,purge=True)
        self.assertFalse(self.original.exists())
        self.assertFalse((self.mod/'Geometries/CSC_New.geo').exists())
        ids={self.ex.txt(e,'m_EntryID') for e in self.ex.read_xml(self.mod/'XLPs/CSC_Tilebases.xlp').find('m_Entries')}
        self.assertEqual(ids,set())
        self.assertTrue((Path(json.loads((self.out/'report.json').read_text())['uninstall_backup'])/
                         'Assets/CSC_Old.ast').is_file())

    def test_purge_listing_names_every_file_and_xlp_id_without_changes(self):
        import contextlib
        import io
        self.ex.install(self.job)
        printed=io.StringIO()
        with contextlib.redirect_stdout(printed):
            self.ex.uninstall(self.job,dry_run=True,purge=True)
        listing=printed.getvalue()
        self.assertIn(str(self.mod/'Assets/CSC_Old.ast'),listing)
        self.assertIn(str(self.mod/'Geometries/CSC_New.geo'),listing)
        self.assertIn(':: CSC_Old',listing)
        self.assertIn(':: CSC_New',listing)
        self.assertEqual(self.original.read_bytes(),b'new asset')
        self.assertEqual(json.loads((self.out/'report.json').read_text())['status'],
                         'installed_pending_asset_editor_and_game_review')


class RerunOwnershipTests(unittest.TestCase):
    def test_purged_run_is_boundary_for_older_installed_receipts(self):
        import export_scene as ex
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory); mod=root/'mod'; runs=root/'blends/export-runs'
            (mod/'Assets').mkdir(parents=True); (mod/'XLPs').mkdir()
            ex.write_xml(mod/'XLPs/CSC_Tilebases.xlp',ex.ET.fromstring('<X><m_Entries/></X>'))
            def prepare(name,asset):
                out=runs/name; stage=out/'stage'; (stage/'Assets').mkdir(parents=True)
                (stage/'XLPs').mkdir()
                (stage/'Assets'/(asset+'.ast')).write_text(name)
                ex.write_xml(stage/'XLPs/CSC_Tilebases.xlp',ex.read_xml(mod/'XLPs/CSC_Tilebases.xlp'))
                files={str(p.relative_to(stage)):ex.sha(p) for p in stage.rglob('*') if p.is_file()}
                baseline={rel:ex.sha(mod/rel) if (mod/rel).is_file() else None for rel in files}
                (out/'manifest.json').write_text(json.dumps({'converted_files':files,
                    'destination_baseline':baseline,'textures':{}}))
                (out/'report.json').write_text(json.dumps({'status':'converted_pending_asset_editor_and_game_review',
                    'assets':[asset]}))
                job={'output':str(out),'mod_root':str(mod)}
                (out/'job.json').write_text(json.dumps(job))
                return job
            old=prepare('20260101','Old'); ex.install(old)
            middle=prepare('20260102','Middle'); ex.install(middle)
            ex.uninstall(middle,purge=True)
            # Old receipt still exists, but its outputs were retired by Middle.
            newer=prepare('20260103','New'); ex.install(newer)
            self.assertTrue((mod/'Assets/New.ast').is_file())
            self.assertIsNone(json.loads((runs/'20260103/install-receipt.json').read_text())['predecessor_job'])

    def test_rerun_retires_stale_assets_and_normal_uninstall_restores_prior_run(self):
        import export_scene as ex
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory); mod=root/'mod'; runs=root/'blends/export-runs'
            (mod/'Assets').mkdir(parents=True); (mod/'XLPs').mkdir()
            ex.write_xml(mod/'XLPs/CSC_Tilebases.xlp', ex.ET.fromstring('<X><m_Entries/></X>'))

            def prepare(name, assets):
                out=runs/name; stage=out/'stage'
                (stage/'Assets').mkdir(parents=True); (stage/'XLPs').mkdir()
                for ident in assets:
                    (stage/'Assets'/(ident+'.ast')).write_text(name+' '+ident)
                ex.write_xml(stage/'XLPs/CSC_Tilebases.xlp', ex.read_xml(mod/'XLPs/CSC_Tilebases.xlp'))
                files={str(p.relative_to(stage)):ex.sha(p) for p in stage.rglob('*') if p.is_file()}
                baseline={rel:ex.sha(mod/rel) if (mod/rel).is_file() else None for rel in files}
                (out/'manifest.json').write_text(json.dumps({'converted_files':files,
                    'destination_baseline':baseline,'textures':{}}))
                (out/'report.json').write_text(json.dumps({'status':'converted_pending_asset_editor_and_game_review',
                    'assets':assets}))
                job={'output':str(out),'mod_root':str(mod)}
                (out/'job.json').write_text(json.dumps(job))
                return job

            first=prepare('20260101-000000', ['Keep','Drop'])
            ex.install(first)
            self.assertTrue((mod/'Assets/Drop.ast').is_file())
            second=prepare('20260102-000000', ['Keep','New'])
            ex.install(second)
            self.assertFalse((mod/'Assets/Drop.ast').exists())
            self.assertEqual((mod/'Assets/Keep.ast').read_text(), '20260102-000000 Keep')
            ids={ex.txt(e,'m_EntryID') for e in ex.read_xml(mod/'XLPs/CSC_Tilebases.xlp').find('m_Entries')}
            self.assertEqual(ids,{'Keep','New'})
            self.assertEqual(json.loads((runs/'20260101-000000/report.json').read_text())['status'],'superseded')
            ex.uninstall(second)
            self.assertEqual((mod/'Assets/Keep.ast').read_text(), '20260101-000000 Keep')
            self.assertTrue((mod/'Assets/Drop.ast').is_file())
            self.assertFalse((mod/'Assets/New.ast').exists())
            ids={ex.txt(e,'m_EntryID') for e in ex.read_xml(mod/'XLPs/CSC_Tilebases.xlp').find('m_Entries')}
            self.assertEqual(ids,{'Keep','Drop'})
            self.assertEqual(json.loads((runs/'20260101-000000/report.json').read_text())['status'],
                             'installed_pending_asset_editor_and_game_review')


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

class ExplicitAOTests(unittest.TestCase):
    def test_ao_reuse_variant_and_conflicting_pixels(self):
        from export_scene import stage_ao_binding, sha
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); mod=root/'mod'; stage=root/'stage'; (mod/'Materials').mkdir(parents=True)
            original='<M><m_Name text="CSC_M"/><m_CookParams><m_Values><Element><m_ParamName text="AO"/><m_ObjectName text="CSC_Old"/></Element><Element><m_ParamName text="BaseColor"/><m_ObjectName text="KeepSurface"/></Element></m_Values></m_CookParams></M>'
            path=mod/'Materials/CSC_M.mtl'; path.write_text(original)
            src=root/'ao.png'; src.write_bytes(b'actual source bytes')
            mat={'name':'Preview','ao_texture':'CSC_Shared_AO','images':{'AO':{'path':str(src),'sha256':sha(src),'size':[2048,2048]}}}
            tex={}; inputs={}; ident=stage_ao_binding(mat,'CSC_M',mod,stage,tex,inputs)
            variant=ET.parse(stage/'Materials'/(ident+'.mtl')).getroot()
            bindings={txt(e,'m_ParamName'):txt(e,'m_ObjectName') for e in variant.findall('m_CookParams/m_Values/Element')}
            self.assertEqual(bindings,{'AO':'CSC_Shared_AO','BaseColor':'KeepSurface'})
            self.assertEqual(path.read_text(),original)
            self.assertEqual((stage/tex['CSC_Shared_AO']['source']).read_bytes(),src.read_bytes())
            self.assertEqual(inputs[str(src)],sha(src))
            path.write_text(original.replace('CSC_Old','CSC_Shared_AO'))
            self.assertEqual(stage_ao_binding(mat,'CSC_M',mod,stage,tex,inputs),'CSC_M')
            src.write_bytes(b'other pixels'); mat['images']['AO']['sha256']=sha(src)
            with self.assertRaisesRegex(ValueError,'Conflicting AO source'):
                stage_ao_binding(mat,'CSC_M',mod,stage,tex,inputs)
