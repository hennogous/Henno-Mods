"""Inspect only the L3 courtyard against the unchanged building and actual roads."""
import bpy, sys, math, os, json
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).parent))
from cafe_atlas import OUT,SOURCE
bpy.ops.wm.open_mainfile(filepath=str(OUT.parent/'revision-01-base/Cafe_L3_Bakers_E_Base.blend'),load_ui=False,use_scripts=False)
scene=bpy.data.scenes['Review'];bpy.context.window.scene=scene
ident='CSC_ALL_Stage_4_Cobble_Decals'
with bpy.data.libraries.load(str(SOURCE/(ident+'.blend')),link=False) as (src,dst):dst.objects=list(src.objects)
for ob in [o for o in dst.objects if o]:
    if ob.type=='MESH':
        scene.collection.objects.link(ob);world=ob.matrix_world.copy();ob.parent=None;ob.matrix_world=world;ob.modifiers.clear();ob.visible_shadow=False
        for v in ob.data.vertices:v.co.z=.12
    else:bpy.data.objects.remove(ob,do_unlink=True)
for im in bpy.data.images:
    if im.source=='FILE':
        candidate=SOURCE/'textures'/Path(bpy.path.abspath(im.filepath)).name
        if candidate.exists():im.filepath=str(candidate);im.reload()
measurements={}
for ob in scene.objects:
    if ob.type=='MESH' and ('Level_3' in ob.name or 'Road' in ob.name):
        points=[ob.matrix_world@v.co for v in ob.data.vertices]
        uv=[(.8660254*(p.x-146)-.5*(p.y-77),.5*(p.x-146)+.8660254*(p.y-77),p.z) for p in points]
        measurements[ob.name]={'local_min':[min(p[i] for p in uv) for i in range(3)],'local_max':[max(p[i] for p in uv) for i in range(3)]}
label=os.environ.get('CSC_COURTYARD_LABEL','After')
(OUT/(label+'-reference-bounds.json')).write_text(json.dumps(measurements,indent=2))
scene.render.resolution_x=1000;scene.render.resolution_y=1000;scene.cycles.samples=24;scene.cycles.transparent_max_bounces=64
cam=scene.camera;cam.location=(146,77,1000);cam.rotation_euler=(0,0,math.radians(150));cam.data.ortho_scale=270
scene.render.filepath=str(OUT/(label+'_Top_Front_Up.png'));bpy.ops.render.render(write_still=True)
if label=='After':
    target=Vector((146,67,35));cam.location=target+Vector((0,-1,.82)).normalized()*1000;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=300
    scene.render.filepath=str(OUT/'After_Hero.png');bpy.ops.render.render(write_still=True)
    bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Cafe_Courtyard_Review.blend'))
