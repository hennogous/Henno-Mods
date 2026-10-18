"""Non-authoritative Cafe placement proposal on the unchanged L3/road reference."""
import bpy,sys,math,json
from pathlib import Path
from mathutils import Vector,Matrix
sys.path.insert(0,str(Path(__file__).parent))
from cafe_atlas import OUT,SOURCE
bpy.ops.wm.open_mainfile(filepath=str(OUT.parent/'revision-01-base/Cafe_L3_Bakers_E_Base.blend'),load_ui=False,use_scripts=False)
scene=bpy.data.scenes['Review'];bpy.context.window.scene=scene;placements=[]
def put(ident,pos,angle=0,scale=1):
    with bpy.data.libraries.load(str(SOURCE/(ident+'.blend')),link=False) as (src,dst):dst.objects=list(src.objects)
    objects=[o for o in dst.objects if o];T=Matrix.Translation(Vector(pos))@Matrix.Rotation(angle,4,'Z')@Matrix.Scale(scale,4)
    for object_index,o in enumerate(objects):
        if o.type=='MESH':
            scene.collection.objects.link(o);world=o.matrix_world.copy();o.parent=None;o.modifiers.clear();o.matrix_world=T@world;o['review_only']=True
            if 'Cobble' in ident:
                o.visible_shadow=False
                for v in o.data.vertices:v.co.z=.1+object_index*.01
        else:bpy.data.objects.remove(o,do_unlink=True)
    placements.append(dict(asset=ident,position=list(pos),z_rotation=angle,scale=scale))
def local(u,v,z=0):return (146+.8660254*u+.5*v,77-.5*u+.8660254*v,z)
for i in range(8):
    a=math.radians(-20+30*i);put('CSC_ALL_Garden_Wall_Curve',(159+96*math.cos(a),62+96*math.sin(a),0),a-math.pi/2)
put('CSC_ALL_Stage_4_Cobble_Decals',(0,0,0))
for u,v,content in [(-22,-55,'CSC_BAKERS_Cafe_Table_Service'),(23,-70,'CSC_BAKERS_Cafe_Reading_Set')]:
    p=local(u,v);put('CSC_ALL_Oval_Table',p,-math.pi/6,1.15);put(content,p,-math.pi/6,1.15)
    for du in [-18,18]:put('CSC_BAKERS_Cafe_Chair',local(u+du,v),-math.pi/6+(math.pi/2 if du<0 else -math.pi/2),1.15)
put('CSC_BAKERS_Cafe_Counter',local(58,-20),-math.pi/6)
put('CSC_BAKERS_Cafe_Brewing_Set',local(58,-20),-math.pi/6)
put('CSC_BAKERS_Cafe_Pastry_Tray',local(66,-18,17.8),-math.pi/6)
for u,v in [(76,-3),(78,7)]:put('CSC_ALL_Flour_Sack_Closed',local(u,v),-math.pi/4,.85)
(OUT/'review-placements.json').write_text(json.dumps(placements,indent=2))
for im in bpy.data.images:
    if im.source=='FILE':
        candidate=SOURCE/'textures'/Path(bpy.path.abspath(im.filepath)).name
        if candidate.exists():im.filepath=str(candidate);im.reload()
scene.render.resolution_x=1200;scene.render.resolution_y=1200;scene.cycles.samples=32;scene.cycles.transparent_max_bounces=64
cam=scene.camera
def render(name,target,direction,scale):
    target=Vector(target);cam.location=target+Vector(direction).normalized()*1000;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale;scene.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True)
print('Saving review assembly',flush=True)
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Cafe_Regular_Review.blend'),compress=False)
print('Rendering review assembly',flush=True)
render('Cafe_Regular_Hero',(159,67,35),(0,-1,.82),300)
render('Cafe_Regular_Top',(150,65,0),(0,0,1),300)
render('Cafe_Regular_Rear',(159,67,32),(.6,1,.8),300)
