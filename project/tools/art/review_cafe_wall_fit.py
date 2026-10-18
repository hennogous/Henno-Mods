"""Disposable saved-AST courtyard fitting view; never export this scene to AE."""
import bpy,sys,json,math,os
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).parent))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'blender'))
from cafe_atlas import OUT,SOURCE
from ae_asset_render_blender import Builder
job=json.loads((OUT/'ae-job.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(OUT.parent/'revision-01-base/Cafe_L3_Bakers_E_Base.blend'),load_ui=False,use_scripts=False)
scene=bpy.data.scenes['Review'];bpy.context.window.scene=scene
for o in list(scene.objects):
    if o.type=='MESH':
        print('BASE MESH',o.name,flush=True)
        if not any(s in o.name.lower() for s in ['ground','grass','terrain']):bpy.data.objects.remove(o,do_unlink=True)
b=Builder(job,'sv');b.assemble(job['root'],root=True)
records=[]
for o,r in zip(b.objects,b.mapping):
    points=[list(o.matrix_world@v.co) for v in o.data.vertices]
    records.append(dict(**r,vertices=points,faces=[list(p.vertices) for p in o.data.polygons],uv=[[list(o.data.uv_layers[0].data[i].uv) for i in p.loop_indices] for p in o.data.polygons]))
    if 'Decal' in job['materials'][next(k for k,v in job['materials'].items() if v['id']==r['material'])]['shader']:
        mat=o.data.materials[0];nodes=mat.node_tree.nodes;bs=next(n for n in nodes if n.type=='BSDF_PRINCIPLED');base=nodes.get('BaseColor')
        if base:mat.node_tree.links.new(base.outputs['Alpha'],bs.inputs['Alpha'])
        if 'Stage_4_Cobble' in r['material']:
            fitted=OUT/'CSC_ALL_Stage_4_Cobbles_B.png'
            original=Path(job['materials'][next(k for k,v in job['materials'].items() if v['id']==r['material'])]['textures']['BaseColor']['source'])
            base.image=bpy.data.images.load(str(fitted if fitted.exists() else original),check_existing=False)
        for v in o.data.vertices:v.co.z=.12 if 'Cobble' in r['material'] else .15
        o.visible_shadow=False
(OUT/'ae-world-geometry.json').write_text(json.dumps(records))
scene.render.resolution_x=1000;scene.render.resolution_y=1000;scene.cycles.samples=24;scene.cycles.transparent_max_bounces=64
cam=scene.camera;cam.location=(146,77,1000);cam.rotation_euler=(0,0,math.radians(150));cam.data.ortho_scale=280
label=os.environ.get('CSC_COURTYARD_LABEL','Before')
scene.render.filepath=str(OUT/(label+'_Top.png'));bpy.ops.render.render(write_still=True)
target=Vector((146,77,35));cam.location=target+Vector((0,-1,.82)).normalized()*1000;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=310
scene.render.filepath=str(OUT/(label+'_Hero.png'));bpy.ops.render.render(write_still=True)
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(OUT/(label+'_AE_Review.blend')))

