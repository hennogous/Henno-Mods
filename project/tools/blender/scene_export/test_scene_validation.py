"""Scene-authoring regression cases; no Blender or external assets required."""
import copy
import math
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('scene_validation_test', Path(__file__).resolve().parents[1]/'csc_scene_validation.py')
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


def mesh(name='Building', **changes):
    value = dict(name=name,type='MESH',scenes=['Export','Review'],parent=None,children=[],
                 role='building_geometry',export_vertices=2000,uv_layers=3,static_weights=True,
                 materials=['CSC_Quarter'],scale=[1,1,1])
    value.update(changes)
    return value


def controller(name='Attach_Crate', **changes):
    value = dict(name=name,type='EMPTY',scenes=['Export','Review'],parent=None,children=['Crate'],
                 role='reused_attachment',source_asset_id='DIS_COM_Crate',instance_id='Crate',
                 support='ground',terrain_follow='pivot',position=[10,20,0],scale=[1,1,1])
    value.update(changes)
    return value


def scene():
    snapshot = dict(main_geometry_maximum=2200,images=[],objects=[mesh()],scenes={})
    for name in ['Review','Export']:
        snapshot['scenes'][name] = dict(world=dict(color=[.7,.8,1],strength=.65),engine='CYCLES',
                                       view_transform='Standard' if name=='Review' else 'AgX',
                                       exposure=-.1 if name=='Review' else .35,gamma=1)
    snapshot['scenes']['Review']['review_key'] = dict(type='SUN',energy=3.2,color=[1,.92,.8],angle=math.radians(6),shadows=True)
    return snapshot


def add_crate(snapshot):
    root = controller()
    child = mesh('Crate',role='reused_asset',parent=root['name'],source_asset_id='DIS_COM_Crate',
                 library_source='DIS_COM_Crate',instance_id='Crate',export_vertices=10000,uv_layers=1)
    snapshot['objects'] += [root,child]
    return root,child


class AuthoringTests(unittest.TestCase):
    def codes(self, data):
        return {f['code'] for f in validator.validate_snapshot(data)['findings'] if f['severity']=='error'}

    def assert_budget_advisory(self, data):
        report = validator.validate_snapshot(data)
        self.assertTrue(report['automated_pass'])
        self.assertEqual(report['error_count'], 0)
        self.assertEqual(report['warning_count'], 1)
        self.assertEqual([f['severity'] for f in report['findings'] if f['code']=='MAIN_BUDGET'], ['warning'])

    def test_budget_warning_does_not_mask_mechanical_errors(self):
        s=scene(); s['objects'][0]['export_vertices']=3000
        self.assert_budget_advisory(s)
        s['images']=[dict(path='missing.png',exists=False)]
        r=validator.validate_snapshot(s)
        self.assertFalse(r['automated_pass'])
        self.assertEqual(r['error_count'],1)
        self.assertEqual(r['warning_count'],1)
        self.assertEqual(self.codes(s),{'MISSING_TEXTURE'})

    def test_valid_native_attachments_excluded_from_main_budget(self):
        s=scene(); add_crate(s); before=copy.deepcopy(s); r=validator.validate_snapshot(s)
        self.assertTrue(r['automated_pass']); self.assertEqual(s,before)
        self.assertEqual(r['counts']['main_vertices'],2000)
        self.assertEqual(r['counts']['attachment_vertices'],10000)
        self.assertEqual(r['status'],'review_required')

    def test_bundled_native_crate_with_ordinary_empty_is_rejected(self):
        s=scene();root,child=add_crate(s);root.pop('instance_id');root['role']=None
        child['role']='fixed_geometry'
        self.assertIn('PANTRY_BUNDLED',self.codes(s))

    def test_custom_assembly_does_not_hide_native_provenance(self):
        s=scene();root,child=add_crate(s);root.update(role='custom_attachment',source_asset_id='CSC_Garden')
        child['source_asset_id']='CSC_Garden';child['derivation']='Modified native leaves'
        self.assertIn('PANTRY_BUNDLED',self.codes(s))

    def test_csc_authored_fixed_props_are_allowed_and_counted(self):
        s=scene();s['objects'].append(mesh('Cloth',role='fixed_geometry',library_source='CSC_ALL_Cloth',export_vertices=100))
        self.assertTrue(validator.validate_snapshot(s)['automated_pass'])
        s['objects'][-1]['export_vertices']=201
        self.assert_budget_advisory(s)

    def test_review_only_duplicate_cannot_disappear_from_export(self):
        s=scene();_,child=add_crate(s);child['scenes']=['Review']
        self.assertTrue({'REVIEW_ONLY_PROP','CHILD_NOT_EXPORTED'} <= self.codes(s))

    def test_identity_mismatch_and_duplicate_ids(self):
        s=scene();root,child=add_crate(s);child['instance_id']='Stale'
        s['objects'].append(controller('Other',children=[]))
        self.assertTrue({'CHILD_IDENTITY','DUPLICATE_INSTANCE','EMPTY_ATTACHMENT'} <= self.codes(s))

    def test_nonuniform_mirror_and_shear(self):
        s=scene();root,_=add_crate(s);root['scale']=[1,2,1]
        self.assertIn('NONUNIFORM_SCALE',self.codes(s))
        root['scale']=[1,1,1];root['determinant']=-1
        self.assertIn('INVALID_TRANSFORM',self.codes(s))
        root['determinant']=1;root['shear']=.02
        self.assertIn('SHEAR',self.codes(s))

    def test_legacy_terrain_bool_and_shared_pivot_offset(self):
        s=scene();root,_=add_crate(s);root['terrain_follow']=True
        self.assertIn('TERRAIN_MODE',self.codes(s))
        root['terrain_follow']='pivot'
        s['objects'].append(controller('Contents',instance_id='Contents',children=[],support='Crate',
                                       terrain_follow='shared-support-pivot',position=[11,20,0]))
        self.assertIn('SUPPORT_PIVOT',self.codes(s))

    def test_support_cycle(self):
        s=scene();root,_=add_crate(s);root['support']='Crate'
        self.assertIn('SUPPORT_REFERENCE',self.codes(s))

    def test_export_light_and_missing_world(self):
        s=scene();s['scenes']['Export']['world']=None;s['objects'].append(dict(name='Sun',type='LIGHT',scenes=['Export']))
        self.assertTrue({'WORLD_LIGHT','EXPORT_LIGHT'} <= self.codes(s))

    def test_texture_and_direct_mesh_contract(self):
        s=scene();s['images']=[dict(path='lost.png',exists=False)]
        s['objects'][0].update(uv_layers=1,static_weights=False,unsupported_modifiers=['MIRROR'],materials=[])
        self.assertTrue({'MISSING_TEXTURE','UV_CHANNELS','STATIC_WEIGHTS','MODIFIERS','MISSING_MATERIAL'} <= self.codes(s))

    def test_visual_quality_never_silently_passes(self):
        r=validator.validate_snapshot(scene()); reviews={f['code'] for f in r['findings'] if f['severity']=='review'}
        self.assertTrue({'ROAD_CLEARANCE','AO_QUALITY','STATE_ALIGNMENT','DOUBLE_SIDED_SURFACES'} <= reviews)

    def test_hidden_parent_excludes_entire_assembly_from_budget(self):
        s=scene();root,child=add_crate(s);root['excluded']=True
        self.assertEqual(validator.validate_snapshot(s)['counts']['attachment_vertices'],0)

    def test_one_off_attachment_counts_even_when_labeled_reused(self):
        s=scene();root,child=add_crate(s)
        root['source_asset_id']='CSC_Courtyard'
        child.update(source_asset_id='CSC_Courtyard',library_source=None,export_vertices=300)
        r=validator.validate_snapshot(s)
        self.assert_budget_advisory(s)
        self.assertEqual(r['counts']['budget_vertices'],2300)
        self.assertEqual(r['counts']['bespoke_attachment_vertices'],300)

    def test_potential_library_candidate_is_not_an_exemption(self):
        s=scene();root,child=add_crate(s)
        root.update(source_asset_id='CSC_Chair',reuse_scope='shared',reuse_approved=False,
                    reuse_reference='Proposed for library')
        child.update(source_asset_id='CSC_Chair',library_source=None,export_vertices=300)
        self.assert_budget_advisory(s)
        root['reuse_approved']=True;root.pop('reuse_reference')
        self.assert_budget_advisory(s)
        root['reuse_reference']='Approved shared chair, library catalogue'
        r=validator.validate_snapshot(s)
        self.assertTrue(r['automated_pass'])
        self.assertEqual(r['counts']['budget_vertices'],2000)
        self.assertEqual(r['counts']['reused_attachment_vertices'],300)

    def test_hidden_bespoke_attachment_is_not_budgeted(self):
        s=scene();root,child=add_crate(s)
        root.update(source_asset_id='CSC_Courtyard',excluded=True)
        child.update(source_asset_id='CSC_Courtyard',library_source=None)
        self.assertEqual(validator.validate_snapshot(s)['counts']['budget_vertices'],2000)

    def test_bespoke_decal_counts_but_road_review_context_does_not(self):
        s=scene();s['objects'][0]['export_vertices']=2190
        path=mesh('Entrance',role='decal_geometry',scenes=['Review'],
                  budget_role='bespoke_decal',export_vertices=16)
        s['objects'] += [path,mesh('Road',role='decal_geometry',scenes=['Review'],
                                  review_only=True,export_vertices=5000)]
        r=validator.validate_snapshot(s)
        self.assertEqual(r['counts']['budget_vertices'],2206)
        self.assertEqual(r['counts']['bespoke_decal_vertices'],16)
        self.assert_budget_advisory(s)
        path['excluded']=True
        self.assertEqual(validator.validate_snapshot(s)['counts']['budget_vertices'],2190)

    def test_tagged_direct_mesh_is_not_double_counted_as_decal(self):
        s=scene();s['objects'][0]['budget_role']='bespoke_decal'
        r=validator.validate_snapshot(s)
        self.assertEqual(r['counts']['budget_vertices'],2000)
        self.assertEqual(r['counts']['bespoke_decal_vertices'],0)
