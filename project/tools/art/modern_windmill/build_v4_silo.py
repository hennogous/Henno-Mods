"""Clean entrance joins and add the concept's silo to the v3 house."""
import bpy, sys, math, json, shutil, ast, bmesh
from pathlib import Path
from mathutils import Vector, Matrix
OUT=Path(sys.argv[sys.argv.index('--')+1]); ASSET='CSC_BAKERS_Wind_Mill_Modern'
ROOT=Path(__file__).resolve().parents[4]; PREV=Path.home()/'Desktop/Codex/modern-windmill-v3-20261026'
OUT.mkdir(parents=True,exist_ok=True);shutil.copytree(PREV/'textures',OUT/'textures',dirs_exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(PREV/(ASSET+'.blend')))
scene=bpy.data.scenes['Export'];review=bpy.data.scenes['Review'];bpy.context.window.scene=scene
rig=bpy.data.objects[ASSET];mat=bpy.data.materials[ASSET]
frame=Matrix.Rotation(math.radians(42.3),4,'Z')@Matrix.Translation(Vector((-101,-126,0)))
inv=frame.inverted(); meshes=[];uv_guide=[]
tree=ast.parse((Path(__file__).parent/'build_model.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('tileuv','mesh','box','beam','cylinder','sack')],type_ignores=[]),'<geometry helpers>','exec'))
# Remove the overlapping arch infill and narrow, individually stretched masonry piers.
for ob in list(scene.objects):
    if any(ob.name.startswith('CSC_Fixed_'+p) for p in ('Arch_Wall','Arch_Spandrel','Arch_Header','Concrete_Arch','Arch_Jamb')):
        bpy.data.objects.remove(ob,do_unlink=True)
# One continuous facade around an actual arch opening, with planar registered masonry.
inner=[(-11.6,0),(-11.6,19)]
inner += [(11.6*math.cos(math.pi-i*math.pi/8),19+10*math.sin(math.pi-i*math.pi/8)) for i in range(1,9)]
inner += [(11.6,0)]
outer=[(-16.24,0),(-16.24,19)]
outer += [(16.24*math.cos(math.pi-i*math.pi/8),19+14*math.sin(math.pi-i*math.pi/8)) for i in range(1,9)]
outer += [(16.24,0)]
vs=[];fs=[]
for x in (-44,-38):vs.extend([(x,y,z) for y,z in inner]+[(x,y,z) for y,z in outer])
nn=len(inner);off=nn*2
for i in range(nn-1):
    a=i;b=i+1;c=nn+i;d=c+1
    fs.extend([(a,b,d,c),(a+off,c+off,d+off,b+off),(a,a+off,b+off,b),(c,d,d+off,c+off)])
fs.extend([(0,nn,off+nn,off),(nn-1,off+nn-1,off+2*nn-1,2*nn-1)])
arch=mesh('Entrance_Concrete_Surround',vs,fs,[11]*len(fs))
for side in (-1,1):box('Entrance_Masonry_Pier_'+str(side),(-40.5,side*20.12,17),(3,7.76,34),1)
vs=[];fs=[]
for i in range(1,len(outer)-2):
    y0,z0=outer[i];y1,z1=outer[i+1];k=len(vs)
    vs.extend([(-42,y0,z0),(-42,y1,z1),(-42,y1,34),(-42,y0,34),(-39,y0,z0),(-39,y1,z1),(-39,y1,34),(-39,y0,34)])
    fs.extend([tuple(k+j for j in f) for f in [(0,1,2,3),(4,7,6,5),(0,4,5,1),(3,2,6,7)]])
mesh('Entrance_Masonry_Infill',vs,fs,[1]*len(fs))
for ob in meshes:
    bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free()
    # Shared world-plane sampling avoids a full block texture squeezed into each pier.
    tile=11 if ob==arch else 1
    for p in ob.data.polygons:
        for li in p.loop_indices:
            v=ob.data.vertices[ob.data.loops[li].vertex_index].co
            ob.data.uv_layers['UV1'].data[li].uv=tileuv(tile,(v.y+24)/(48 if tile==11 else 84),v.z/34)
# Silo sits adjacent to the shelter's right front corner, without intersecting it.
sx,sy=51,-93
cylinder('Silo_Foundation',sx,sy,[(-24,22),(12,22),(14,21)],16,1,11)
silo=cylinder('Silo_Body',sx,sy,[(14,20),(79,20)],16,3,5,start=math.pi/2)
cylinder('Silo_Foot_Rim',sx,sy,[(13,21),(16,21)],16,5)
cap=cylinder('Silo_Cap',sx,sy,[(79,23),(82,23),(96,3.6)],16,4,4)
cylinder('Silo_Neck',sx,sy,[(95,3.5),(99,3.5)],12,6)
# Reuse the generated seam texture as radial roof sectors; seams are never mesh strips.
for p in cap.data.polygons:
    if p.index<32:
        side=p.index%16
        for li in p.loop_indices:
            vi=cap.data.loops[li].vertex_index;v=cap.data.vertices[vi].co
            u=.25 if vi%16==side else .49
            cap.data.uv_layers['UV1'].data[li].uv=tileuv(2,u,(v.z-79)/17)
box('Elevator_Foundation',(72,-63,-9),(17,16,30),11)
box('Elevator',(72,-63,59),(13,12,106),14)
box('Elevator_Cap',(72,-63,113),(17,16,5),4)
beam('Transfer_Spout',(72,-68,106),(sx,sy,98),6,5)
# Close stock sits inside the original shelter; full buried bases remain under structural parts.
for i,(x,y) in enumerate([(12,-37),(24,-36)]):sack('Sack_Upright_'+str(i),(x,y,-2),(10,9,19))
box('Stock_Pallet',(20,-57,-3),(24,16,9),10,True)
for i in range(3):sack('Sack_Stack_'+str(i),(20+(.6 if i==1 else 0),-57,1.5+i*5),(21,13,5.5))
new=list(meshes)
for ob in new:
    ob.data.transform(frame);ob.parent=rig;review.collection.objects.link(ob)
    vg=ob.vertex_groups.new(name='Bone');vg.add(list(range(len(ob.data.vertices))),1,'REPLACE')
    mod=ob.modifiers.new('Static Bone','ARMATURE');mod.object=rig
    ob.data.uv_layers.new(name='UV2');uv3=ob.data.uv_layers.new(name='UV3')
    for d in uv3.data:d.uv=(.02,.02)
meshes=[o for o in scene.objects if o.type=='MESH']
bpy.ops.object.select_all(action='DESELECT')
for ob in meshes:ob.select_set(True);ob.data.uv_layers.active_index=1
bpy.context.view_layer.objects.active=meshes[0];bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=math.radians(75),island_margin=.012,area_weight=.8,scale_to_bounds=True);bpy.ops.object.mode_set(mode='OBJECT')
nodes=mat.node_tree.nodes;links=mat.node_tree.links;bs=nodes.get('Principled BSDF')
for ch in ('B','N','G','M','E'):
    im=bpy.data.images.load(str(OUT/'textures'/f'{ASSET}_{ch}.png'),check_existing=False);im.colorspace_settings.name='sRGB' if ch in ('B','E') else 'Non-Color';nodes[ch].image=im
for l in list(bs.inputs['Normal'].links):links.remove(l)
links.new(nodes['B'].outputs['Color'],bs.inputs['Base Color'])
ao=bpy.data.images.new(ASSET+'_AO_v4',width=2048,height=2048,alpha=False);ao.colorspace_settings.name='Non-Color';nodes['AO'].image=ao;nodes.active=nodes['AO'];scene.cycles.samples=32;scene.render.bake.margin=8;bpy.ops.object.bake(type='AO',uv_layer='UV2')
ao.filepath_raw=str(OUT/'textures'/f'{ASSET}_AO.png');ao.file_format='PNG';ao.save()
mix=next(n for n in nodes if n.type=='MIX_RGB');normal=next(n for n in nodes if n.type=='NORMAL_MAP');links.new(mix.outputs[0],bs.inputs['Base Color']);links.new(normal.outputs[0],bs.inputs['Normal'])
for ob in meshes:ob.data.uv_layers.active_index=0;ob.select_set(False)
for im in list(bpy.data.images):
    if im.users==0:bpy.data.images.remove(im)
for ch in ('B','N','G','M','E','AO'):nodes[ch].image.filepath='//textures/'+f'{ASSET}_{ch}.png'
bpy.context.window.scene=review;review['revision_scope']='v4: clean entrance, silo and integrated stock; assembly review.'
cam=review.camera;target=frame@Vector((15,-29,44));cam.data.ortho_scale=225
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/(ASSET+'.blend')),relative_remap=False)
# Resolve external textures only after the new file's folder is authoritative.
for ch in ('B','N','G','M','E','AO'):nodes[ch].image.reload()
offsets=[('assembly',Vector((190,-310,240))),('entrance',Vector((-300,-180,210))),('rear',Vector((-180,320,240))),('top',Vector((1,-1,500)))]
for name,offset in offsets:
    cam.location=target+offset;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();review.render.filepath=str(OUT/f'modern_v4_{name}.png');bpy.ops.render.render(write_still=True)
cam.location=target+offsets[0][1];cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/(ASSET+'.blend')),relative_remap=False)
sys.path.insert(0,str(ROOT/'project/tools/blender/scene_export'));import decode_blend as decoder
bpy.context.window.scene=scene;joined=decoder.merge_meshes(ASSET,[decoder.decode_mesh(o,o.matrix_world) for o in meshes])
report={'revision':'v4 entrance and silo','export_vertices':len(joined['vertices']),'triangles':len(joined['triangles']),'silo_center_local':[sx,sy],'silo_height':99,'foundation_depth':24,'textures':'Reused approved ImageGen atlas; geometry AO rebaked','runtime_installed':False}
(OUT/'assembly-review-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
