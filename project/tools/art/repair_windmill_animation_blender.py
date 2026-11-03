"""Stage the historical mill's explicit native animation identity and real export."""
import sys,json,hashlib
from pathlib import Path
import bpy,numpy as np
ROOT=Path(__file__).resolve().parents[3]
OUT=Path.home()/'Desktop/Codex/windmill-animation-repair-20261030'
SOURCE=Path.home()/'Desktop/Working Files/3D Art/BAKERS/Wind Mill/CSC_BAKERS_Wind_Mill.blend'
sys.path.insert(0,str(ROOT/'project/tools/blender'))
sys.path.insert(0,str(Path.home()/'AppData/Roaming/Blender Foundation/Blender/5.1/scripts/addons'))
import io_export_cn6
from csc_scene_validation import validate_current_scene

def fingerprint():
    # Includes geometry, UVs, normals, weights, materials and rest bones.
    records={}
    for ob in bpy.data.objects:
        if ob.type=='MESH':
            records[ob.name]=dict(vertices=[list(v.co) for v in ob.data.vertices],
              polygons=[(list(p.vertices),p.material_index) for p in ob.data.polygons],
              uvs={l.name:[list(x.uv) for x in l.data] for l in ob.data.uv_layers},
              weights=[[(g.group,g.weight) for g in v.groups] for v in ob.data.vertices],
              groups=[g.name for g in ob.vertex_groups], materials=[m.name for m in ob.data.materials],
              transform=[list(r) for r in ob.matrix_world])
        elif ob.type=='ARMATURE':
            records[ob.name]=[(b.name,b.parent.name if b.parent else None,[list(r) for r in b.matrix_local]) for b in ob.data.bones]
    return hashlib.sha256(json.dumps(records,sort_keys=True).encode()).hexdigest()

def run():
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False)
    if bpy.context.object and bpy.context.object.mode!='OBJECT':bpy.ops.object.mode_set(mode='OBJECT')
    original_scene=bpy.context.scene.name
    before=fingerprint();rig=next(o for o in bpy.data.objects if o.type=='ARMATURE')
    assert rig.name=='CSC_BAKERS_Wind_Mill'
    assert rig.get('civ6_root_name')=='CSC_BAKERS_Wind_Mill_Tower'
    rig['csc_native_model_name']='CSC_BAKERS_Wind_Mill_Tower'
    bpy.context.preferences.filepaths.save_version=0
    staged=OUT/'master'/SOURCE.name;staged.parent.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(staged),relative_remap=False)
    assert fingerprint()==before
    bpy.ops.wm.open_mainfile(filepath=str(staged),load_ui=False,use_scripts=False)
    assert fingerprint()==before
    bpy.context.window.scene=bpy.data.scenes['Export']
    report=validate_current_scene()
    (OUT/'source-validation.json').write_text(json.dumps(report,indent=2))
    assert report['error_count']==0,report
    rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE')
    result=io_export_cn6.csc_export_fgx_geo(rig.name,str(OUT/'candidate'),'LandmarkModel',3,True,rig)
    (OUT/'source-preservation.json').write_text(json.dumps(dict(fingerprint=before,geometry_uvs_weights_materials_rest_rig_unchanged=True,export_result=result),indent=2,default=str))
    # Confirm a model with no identity override keeps ordinary naming, using
    # the same actual source and exporter without modifying the saved master.
    del rig['csc_native_model_name']
    io_export_cn6.csc_do_export_selected(str(OUT/'default-name-control.cn6'),[rig]+[o for o in bpy.context.scene.objects if o.type=='MESH'])
    rig['csc_native_model_name']='CSC_BAKERS_Wind_Mill_Tower'
    assert '0 "CSC_BAKERS_Wind_Mill" -1' in (OUT/'default-name-control.cn6').read_text()
    assert '0 "CSC_BAKERS_Wind_Mill_Tower" -1' in (OUT/'candidate/CSC_BAKERS_Wind_Mill.cn6').read_text()
    # Resolve portable textures against the unchanged original folder for review.
    for im in bpy.data.images:
        if im.filepath.startswith('//'):im.filepath=str(SOURCE.parent/im.filepath[2:])
    bpy.context.window.scene=bpy.data.scenes['Review'];scene=bpy.context.scene
    scene.render.resolution_x=scene.render.resolution_y=640
    scene.render.resolution_percentage=100;scene.cycles.samples=24
    for frame in [1,31]:
        scene.frame_set(frame);scene.render.filepath=str(OUT/f'pose-{frame}.png');bpy.ops.render.render(write_still=True)
    print('WINDMILL_CANDIDATE_READY',before)

def verify_installed():
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False)
    if bpy.context.object and bpy.context.object.mode!='OBJECT':bpy.ops.object.mode_set(mode='OBJECT')
    expected=json.loads((OUT/'source-preservation.json').read_text())['fingerprint']
    assert fingerprint()==expected
    rig=next(o for o in bpy.data.objects if o.type=='ARMATURE')
    assert rig.name=='CSC_BAKERS_Wind_Mill' and rig['csc_native_model_name']=='CSC_BAKERS_Wind_Mill_Tower'
    bpy.context.window.scene=bpy.data.scenes['Export']
    report=validate_current_scene();assert report['error_count']==0,report
    (OUT/'installed-source-validation.json').write_text(json.dumps(report,indent=2))
    print('INSTALLED_SOURCE_VALID',report['error_count'],'errors',report['warning_count'],'warnings')

if __name__=='__main__':
    verify_installed() if '--verify-installed' in sys.argv else run()
