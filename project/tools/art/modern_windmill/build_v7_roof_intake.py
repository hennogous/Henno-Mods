"""Focused edits to Henno's saved V6: roof, hopper, windows and entrance corner joins."""
import bpy,bmesh,sys,math,json,hashlib,ast
from pathlib import Path
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[4];OUT=Path(sys.argv[sys.argv.index('--')+1]);ASSET='CSC_BAKERS_Wind_Mill_Modern'
SOURCE=Path.home()/'Desktop/Working Files/3D Art/BAKERS/Wind Mill/modern/revision-06-concept-refinement'/f'{ASSET}.blend'
source_hash=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
sys.path.insert(0,str(ROOT/'project/tools/blender'));from csc_scene_validation import suspend_csc_repairs
guard=suspend_csc_repairs();guard.__enter__()
bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False)
scene=bpy.data.scenes['Export'];review=bpy.data.scenes['Review'];bpy.context.window.scene=scene
for o in list(review.objects):
    if o.type=='MESH' and o.get('export_role') in ('fixed_geometry','building_geometry') and o.name not in scene.objects:scene.collection.objects.link(o)
scene.view_layers[0].update();rig=bpy.data.objects[ASSET];mat=bpy.data.materials[ASSET]
frame=Matrix.Rotation(math.radians(42.3),4,'Z')@Matrix.Translation(Vector((-101,-126,0)));inv=frame.inverted()
meshes=[];uv_guide=[]
tree=ast.parse((Path(__file__).parent/'build_model.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('tileuv','mesh','box','beam')],type_ignores=[]),'<geometry helpers>','exec'))
tree=ast.parse((Path(__file__).parent/'build_v6_refinement.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('clip','map_periodic')],type_ignores=[]),'<UV helpers>','exec'))
def ob(n):return bpy.data.objects['CSC_Fixed_'+n]
def signature(o):
    return {'matrix':[list(r) for r in o.matrix_world],'vertices':[list(v.co) for v in o.data.vertices]}
kept={o.name:signature(o) for o in scene.objects if o.type=='MESH' and any(s in o.name for s in ('Silo_','Elevator','Rounded_Transfer','Sack_','Visible_','Truck_','Support_Foot'))}
def to_local(o):
    m=inv@o.matrix_world;o.data=o.data.copy();o.data.transform(m);return m.inverted()
def finish_local(o,back):o.data.transform(back)
def timber_uv(o,origin,long_axis,side_axis,length):
    long_axis=Vector(long_axis).normalized();side_axis=Vector(side_axis).normalized();third=long_axis.cross(side_axis).normalized();origin=Vector(origin)
    o.data.update()
    for p in o.data.polygons:
        # Full two-dimensional mapping on side, top AND end faces. Shared grain scale.
        axes=[long_axis,side_axis,third];normal=p.normal
        facing=max(range(3),key=lambda i:abs(normal.dot(axes[i])))
        ua,va=(axes[1],axes[2]) if facing==0 else (axes[0],axes[2] if facing==1 else axes[1])
        for li in p.loop_indices:
            v=o.data.vertices[o.data.loops[li].vertex_index].co-origin
            u=(v.dot(ua)+4)/8 if facing==0 else (v.dot(ua)+length/2)/128
            vv=(v.dot(va)+4)/8
            o.data.uv_layers[0].data[li].uv=tileuv(8,max(.005,min(.995,u)),max(.005,min(.995,vv)))
def remove_corner_internal_cap(o):
    bm=bmesh.new();bm.from_mesh(o.data)
    fs=[p for p in bm.faces if all(abs(v.co.x-(-39*(1+2/42*max(0,1-v.co.z/34))))<.001 for v in p.verts)]
    bmesh.ops.delete(bm,geom=fs,context='FACES');bm.to_mesh(o.data);bm.free()
changed=[]
for n in ('Main_Roof','Main_Ridge','Gable_Brick','Upper_Brick','Front_Lower','Rear_Lower'):
    o=ob(n);back=to_local(o)
    for v in o.data.vertices:
        if n=='Main_Roof':v.co.z=62.5+(v.co.z-61.5)*13.5/18.5
        elif n=='Main_Ridge':v.co.y*=7.6/4.8;v.co.z=78+(v.co.z-80.5)*5/3.4;v.co.x*=100/96
        elif n=='Gable_Brick':v.co.z=61.3+(v.co.z-62.5)*(73.8-61.3)/(78.5-62.5)
        elif n=='Upper_Brick':v.co.z=35.5+(v.co.z-35.5)*(61.3-35.5)/27
        elif n in ('Front_Lower','Rear_Lower') and v.co.x< -39:v.co.x=-39*(1+2/42*max(0,1-v.co.z/34))
    if n=='Main_Ridge':
        timber_uv(o,(0,0,78),(1,0,0),(0,1,0),100)
    if n in ('Front_Lower','Rear_Lower'):
        remove_corner_internal_cap(o);map_periodic(o,1,(84,32))
    finish_local(o,back);changed.append(n)
for n in ('Entrance_Masonry_Pier_-1','Entrance_Masonry_Pier_1'):
    o=ob(n);back=to_local(o);remove_corner_internal_cap(o);finish_local(o,back)
# Recess door is unnecessary; retain a shaded open passage, floor and masonry back wall.
bpy.data.objects.remove(ob('Recess_Loading_Door'),do_unlink=True)
# Substantial timber structure beneath the straight green metal covering.
for x in (-47.1,47.1):
    for s in (-1,1):
        o=beam(f'Barge_Timber_{x}_{s}',(x,s*26,60.45),(x,0,73.95),3.9,8)
        a=Vector((x,s*26,60.45));b=Vector((x,0,73.95));timber_uv(o,(a+b)/2,b-a,(1,0,0),(b-a).length)
for y in (-25.7,25.7):
    o=box('Eave_Timber_'+str(y),(0,y,60.4),(98,3.3,3.6),8)
    timber_uv(o,(0,y,60.4),(1,0,0),(0,1,0),98)
# The intake uses Henno's edited position. Change its silhouette without moving its foundation.
old=ob('Intake_Frame');pts=[inv@old.matrix_world@v.co for v in old.data.vertices]
cx=(min(v.x for v in pts)+max(v.x for v in pts))/2;cy=(min(v.y for v in pts)+max(v.y for v in pts))/2
for n in ('Intake_Frame','Intake_Hopper'):bpy.data.objects.remove(ob(n),do_unlink=True)
for x in (-4.8,4.8):
    for y in (-5.3,5.3):box(f'Intake_Post_{x}_{y}',(cx+x,cy+y,14.6),(1.65,1.65,21.2),4)
for x in (-4.8,4.8):beam('Intake_Side_Brace_'+str(x),(cx+x,cy-4.5,5.2),(cx+x,cy+4.5,15),1.25,4)
box('Intake_Lower_Rail',(cx,cy+4.9,5),(10.8,1.5,1.8),4)
# Actual tapered hopper, visible gaps beneath it, four broad planar sides only.
vs=[]
for z,w,d in ((10.2,3.6,3.6),(20,9,9),(24.8,9,9)):
    vs += [(cx-w/2,cy-d/2,z),(cx+w/2,cy-d/2,z),(cx+w/2,cy+d/2,z),(cx-w/2,cy+d/2,z)]
fs=[(0,3,2,1),(8,9,10,11)]
for j in (0,4):
    for i in range(4):fs.append((j+i,j+(i+1)%4,j+4+(i+1)%4,j+4+i))
mesh('Intake_Tapered_Hopper',vs,fs,[12]*len(fs));box('Intake_Outlet',(cx,cy,9),(3.4,3.4,3),6)
# All existing green roof edge surfaces use a calm sample from the same roof paint.
for o in list(scene.objects):
    if o.type!='MESH':continue
    if any(n in o.name for n in ('Main_Roof','Shelter_Roof','Intake_Roof','Silo_Cap','Elevator_Cap')):
        for p in o.data.polygons:
            us=[o.data.uv_layers[0].data[li].uv for li in p.loop_indices]
            tile=(int(sum(u.x for u in us)/len(us)*4)%4)+4*min(3,int((1-sum(u.y for u in us)/len(us))*4))
            if tile==4:
                for li,u in zip(p.loop_indices,us):o.data.uv_layers[0].data[li].uv=tileuv(2,.025+(u.x*4%1)*.045,.05+(u.y*4%1)*.9)
# Install new meshes, using only the shared static Bone and three UV channels.
for o in meshes:
    o.data.transform(frame);o.parent=rig
    if o.name not in review.objects:review.collection.objects.link(o)
    group=o.vertex_groups.new(name='Bone');group.add(list(range(len(o.data.vertices))),1,'REPLACE');m=o.modifiers.new('Static Bone','ARMATURE');m.object=rig
    o.data.uv_layers.new(name='UV2');uv=o.data.uv_layers.new(name='UV3')
    for d in uv.data:d.uv=(.02,.02)
# Rebuilt wall UVs need their static binding/extra UV channels restored after remeshing.
for n in ('Front_Lower','Rear_Lower'):
    o=ob(n);o.vertex_groups.clear();g=o.vertex_groups.new(name='Bone');g.add(list(range(len(o.data.vertices))),1,'REPLACE')
    while len(o.data.uv_layers)<3:o.data.uv_layers.new(name='UV'+str(len(o.data.uv_layers)+1))
    for d in o.data.uv_layers[2].data:d.uv=(.02,.02)
# Flat masonry corner normals must survive the CN6 per-vertex frame averaging.
for o in list(scene.objects):
    if o.type!='MESH':continue
    if any(s in o.name for s in ('Front_Lower','Rear_Lower','Entrance_Masonry','Entrance_Concrete','Barge_Timber','Eave_Timber','Intake_')):
        bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
        edges=[e for e in bm.edges if len(e.link_faces)==2 and e.calc_face_angle()>math.radians(32)]
        bmesh.ops.split_edges(bm,edges=edges);bm.to_mesh(o.data);bm.free()
nodes={n.label or n.name:n for n in mat.node_tree.nodes if n.type=='TEX_IMAGE'}
for ch in ('B','N','G','M','E','AO'):
    im=bpy.data.images.load(str(OUT/'textures'/f'{ASSET}_{ch}.png'),check_existing=False);im.colorspace_settings.name='sRGB' if ch in ('B','E') else 'Non-Color';nodes[ch].image=im
for name,sig in kept.items():assert signature(bpy.data.objects[name])==sig,('User placement changed',name)
bpy.context.window.scene=review
(OUT/'authoring').mkdir(exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'authoring'/f'{ASSET}.blend'))
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==source_hash
(OUT/'changes.json').write_text(json.dumps({'source':str(SOURCE),'source_sha256':source_hash,'source_unchanged':True,'preserved_user_objects':list(kept),'main_roof_pitch_before_degrees':math.degrees(math.atan(18.5/26)),'main_roof_pitch_after_degrees':math.degrees(math.atan(13.5/26)),'roof_sweep':False,'ridge_width':7.6,'ridge_height':5,'barge_thickness':3.9,'intake_center':[cx,cy],'removed':'Recess_Loading_Door','entrance_corner_fix':'Match the exact battered pier-back plane, remove shared internal caps and split sharp masonry normals','timber_UVs':'Non-degenerate two-dimensional grain mapping, consistent 128 by 8 model-unit sampling','buried_foundations':'preserved to -30'},indent=2))
print('V7_GEOMETRY_READY',flush=True)
guard.__exit__(None,None,None)
