"""Build exact native-derived editable masters and paired material reviews."""
import sys,json,math
from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'project/tools/art'));sys.path.insert(0,str(ROOT/'project/tools/blender'))
import l2_placement_blender as buildlib
from csc_scene_validation import validate_current_scene
from ae_asset_render_blender import Builder
OUT=Path('C:/Users/Shadow/Desktop/Codex/Basket-Well-shared-atlas-20261026')

def frame(scene):
    objects=[o for o in scene.objects if o.type=='MESH'];pts=[o.matrix_world@v.co for o in objects for v in o.data.vertices]
    low=Vector([min(p[i] for p in pts) for i in range(3)]);high=Vector([max(p[i] for p in pts) for i in range(3)]);center=(low+high)*.5
    span=max(high-low);cam=scene.camera;cam.location=center+Vector((1.3,-1.8,1.15))*span
    cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=span*1.65
    scene.render.resolution_x=scene.render.resolution_y=480;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.render.film_transparent=True;scene.cycles.samples=24

def tint_material(mat):
    nodes=mat.node_tree.nodes;links=mat.node_tree.links
    mask=next((n for n in nodes if n.type=='TEX_IMAGE' and n.label=='TintMask'),None)
    if not mask:return
    bs=next(n for n in nodes if n.type=='BSDF_PRINCIPLED');color=bs.inputs['Base Color'].links[0].from_socket
    separate=nodes.new('ShaderNodeSeparateColor');links.new(mask.outputs['Color'],separate.inputs[0])
    mix=nodes.new('ShaderNodeMixRGB');mix.name='Preview tint only';mix.blend_type='MULTIPLY';mix.inputs[2].default_value=(.35,.6,.25,1)
    links.new(separate.outputs['Red'],mix.inputs[0]);links.new(color,mix.inputs[1]);links.new(mix.outputs[0],bs.inputs['Base Color'])
    mat['preview_tint_only']='Green test tint; runtime inherits the saved AE assembly tint.'

def build():
    buildlib.OUT=OUT;buildlib.build()
    sys.path.insert(0,str(Path.home()/'AppData/Roaming/Blender Foundation/Blender/5.1/scripts/addons'))
    import io_export_cn6 as cn6
    checks=[]
    for row in json.loads((OUT/'source-build-report.json').read_text()):
        bpy.ops.wm.open_mainfile(filepath=row['source'],load_ui=False,use_scripts=False)
        review=bpy.data.scenes['Review'];frame(review)
        for mat in bpy.data.materials:
            if mat.use_nodes:tint_material(mat)
        bpy.context.window.scene=bpy.data.scenes['Export']
        bpy.context.scene['atlas_release']='2026-10-26_Shared_01_r045'
        bpy.ops.wm.save_as_mainfile(filepath=row['source'],relative_remap=False)
        bpy.ops.wm.open_mainfile(filepath=row['source'],load_ui=False,use_scripts=False)
        report=validate_current_scene();assert report['error_count']==0,report
        target=OUT/'source-export'/(row['name']+'.cn6');target.parent.mkdir(exist_ok=True)
        cn6.csc_do_export_selected(str(target),[o for o in bpy.context.scene.objects if o.type in ['MESH','ARMATURE']])
        checks.append(dict(name=row['name'],saved_source_valid=True,export=str(target)))
    (OUT/'source-validation.json').write_text(json.dumps(checks,indent=2))

def review():
    oldmats=json.loads((OUT/'before-materials.json').read_text())
    for row in json.loads((OUT/'source-build-report.json').read_text()):
        for phase in ['after','before']:
            bpy.ops.wm.open_mainfile(filepath=row['source'],load_ui=False,use_scripts=False)
            scene=bpy.data.scenes['Review'];bpy.context.window.scene=scene
            if phase=='before':
                raw=json.loads((OUT/'native-before'/(row['name']+'.json')).read_text());folder=OUT/'review'/phase/row['name'];folder.mkdir(parents=True,exist_ok=True)
                b=Builder(dict(output=str(folder),materials={'old':oldmats[row['name']]},warnings=[]),'sv')
                b.scene=scene
                for m in raw['meshes']:
                    ob=bpy.data.objects[m['name']]
                    for loop in ob.data.loops:
                        for i,k in enumerate(['uv','uv2','uv3']):
                            u,v=m['vertices'][loop.vertex_index][k];ob.data.uv_layers[i].data[loop.index].uv=(u,1-v)
                    mat=b.material('old',3);tint_material(mat);ob.data.materials.clear();ob.data.materials.append(mat)
            dest=OUT/'review'/(row['name']+'-'+phase+'.png');dest.parent.mkdir(exist_ok=True)
            scene.render.filepath=str(dest);bpy.ops.render.render(write_still=True,scene=scene.name)
            print('REVIEW',row['name'],phase,flush=True)

def verify():
    buildlib.OUT=OUT;buildlib.installed_verify()

if __name__=='__main__':globals()[sys.argv[sys.argv.index('--')+1]]()
