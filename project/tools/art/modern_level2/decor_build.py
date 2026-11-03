"""Window correction and independent, reusable flower-box / hexagonal-sign masters."""
import bpy,bmesh,math,json,sys,ast
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[4];O=Path.home()/'Desktop/Codex/modern-level2-v3-details-20261028'
SRC=Path.home()/'Desktop/Working Files/3D Art/Level 2/modern/revision-02-tailor-footprint'
sys.path[:0]=[str(ROOT/'project/tools/blender'),str(ROOT/'project/tools/blender/scene_export')]
from csc_scene_validation import suspend_csc_repairs
with suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(SRC/'CSC_Level_2_Modern_Review.blend'),load_ui=False,use_scripts=False)
review=bpy.data.scenes['Review'];export=bpy.data.scenes['Export'];bpy.context.window.scene=review
rig=next(o for o in export.objects if o.type=='ARMATURE');ID='CSC_Level_2_Modern'
window=bpy.data.objects.get('CSC_Fixed_Front_Ground_Glazing_-21');assert window,'Expected front-left ground window at shelter junction'
bpy.data.objects.remove(window,do_unlink=True)
# Historical wall-opening arrangement: blank long upper walls; central gable windows;
# entrance + small window on east ground floor; one offset rear ground window.
for ob in list(bpy.data.objects):
 if ob.type=='MESH' and any(k in ob.name for k in ('Front_Upper_Window','Rear_Upper_Window','Attic_Window','Front_Ground_Glazing','Shopfront_','Rear_Service_Door')):bpy.data.objects.remove(ob,do_unlink=True)
for ob in bpy.data.objects:
 if ob.type=='MESH' and 'Gable_Upper_Window' in ob.name:
  for v in ob.data.vertices:v.co.y*=20/26;v.co.z=53+(v.co.z-53)*22/20
  ob.data.update()
# Historical rear-facing dormer opposite the retained chimney; mirror authored mesh
# coordinates, correcting winding while preserving every painted UV corner.
for suffix in ('Dormer_Cheek_-21','Dormer_Window_-21','Dormer_Shed_Roof_-21'):
 source=bpy.data.objects['CSC_Fixed_'+suffix];ob=source.copy();ob.data=source.data.copy();ob.name='CSC_Fixed_Rear_'+suffix
 review.collection.objects.link(ob);export.collection.objects.link(ob)
 for v in ob.data.vertices:v.co.y=-v.co.y
 for poly in ob.data.polygons:
  saved=[{ob.data.loops[k].vertex_index:layer.data[k].uv.copy() for k in poly.loop_indices} for layer in ob.data.uv_layers];poly.flip()
  for layer,lookup in zip(ob.data.uv_layers,saved):
   for k in poly.loop_indices:layer.data[k].uv=lookup[ob.data.loops[k].vertex_index]
 ob.data.update()
meshes=[o for o in export.objects if o.type=='MESH']
for im in bpy.data.images:
 if im.source=='FILE' and im.filepath:im.filepath=str(O/'textures'/im.filepath.replace('\\','/').split('/')[-1]);im.reload()
building_mat=bpy.data.materials['CSC_BAKERS_Modern']
mat=bpy.data.materials.new('CSC_Props_Modern_01');mat.use_nodes=True;ns=mat.node_tree.nodes;ls=mat.node_tree.links;bs=ns.get('Principled BSDF')
maps={}
for ch in ('B','N','G','M','AO','E'):
 n=ns.new('ShaderNodeTexImage');n.name=n.label=ch;n.image=bpy.data.images.load(str(O/'textures'/f'CSC_Props_Modern_01_{ch}.png'));n.image.colorspace_settings.name='sRGB' if ch in ('B','E') else 'Non-Color'
 uv=ns.new('ShaderNodeUVMap');uv.uv_map='UV2' if ch=='AO' else 'UV3' if ch=='E' else 'UV1';ls.new(uv.outputs['UV'],n.inputs['Vector']);maps[ch]=n
mix=ns.new('ShaderNodeMixRGB');mix.name='AO_Multiply';mix.blend_type='MULTIPLY';mix.inputs[0].default_value=.5;ls.new(maps['B'].outputs['Color'],mix.inputs[1]);ls.new(maps['AO'].outputs['Color'],mix.inputs[2]);ls.new(mix.outputs[0],bs.inputs['Base Color'])
normal=ns.new('ShaderNodeNormalMap');normal.uv_map='UV1';ls.new(maps['N'].outputs['Color'],normal.inputs['Color']);ls.new(normal.outputs[0],bs.inputs['Normal'])
inv=ns.new('ShaderNodeMath');inv.operation='SUBTRACT';inv.inputs[0].default_value=1;ls.new(maps['G'].outputs['Color'],inv.inputs[1]);ls.new(inv.outputs[0],bs.inputs['Roughness']);ls.new(maps['M'].outputs['Color'],bs.inputs['Metallic'])
src=(ROOT/'project/tools/art/modern_level2/build.py').read_text()
for node in ast.parse(src).body:
 if isinstance(node,ast.FunctionDef) and node.name in ('mesh','box','panel'):exec(compile(ast.Module(body=[node],type_ignores=[]),'<mesh helper>','exec'),globals())
props_mat=mat;mat=building_mat;MODULE='Building'
def uvmap(slot,u,v):return ((512+slot%4*128+2+u*124)/1024,1-(slot//4*128+2+(1-v)*124)/1024)
panel('Historical_Entrance_Door',(40.08,-20,0),(40.08,0,0),(40.08,0,30),(40.08,-20,30),6)
panel('Historical_East_Ground_Window',(40.08,10,10),(40.08,23,10),(40.08,23,28),(40.08,10,28),5)
panel('Historical_Rear_Ground_Window',(22,29.08,10),(6,29.08,10),(6,29.08,28),(22,29.08,28),5)
mat=props_mat
def uvmap(slot,u,v):return ((slot%8*128+3+u*122)/1024,1-(slot//8*128+3+(1-v)*122)/1024)
MODULE='FlowerBox';ID='CSC_ALL_Window_Box_Modern'
# Pivot is bottom centre at the wall-facing back; flowers are shallow painted mounds.
box('WindowBox_Body',(-13,-5,0),(13,0,3.7),1)
box('WindowBox_Lip',(-13.5,-5.4,3),(13.5,.2,4.1),1)
for x in (-8,8):box('WindowBox_Bracket', (x-.65,-4,-.9),(x+.65,.3,.4),10)
for i,(x,w,z) in enumerate([(-8.5,8.3,6.2),(0,9.2,7),(8.5,8.3,6.4)]):
 # Eight perimeter points and a broad raised centre, no individual flowers/leaves as mesh.
 pts=[(x-w/2,-4.4,4),(x-w/2+.9,-5.1,4.4),(x+w/2-.9,-5.1,4.4),(x+w/2,-4.4,4),(x+w/2,-.8,4),(x+w/2-.9,-.1,4.4),(x-w/2+.9,-.1,4.4),(x-w/2,-.8,4),(x,-2.6,z)]
 faces=[(j,(j+1)%8,8) for j in range(8)];uv=[]
 for face in faces:uv.append([((pts[k][0]-(x-w/2))/w,(pts[k][1]+5.1)/5) for k in face])
 mesh('WindowBox_Painted_Foliage_'+str(i),pts,faces,24,uv)
MODULE='Sign';ID='CSC_ALL_Hanging_Sign_Modern'
# Wall mount at origin, arm projects +X; sign plane faces -Y/+Y.
box('Sign_Wall_Plate',(0,-1.5,-4),(1.2,1.5,2.7),10)
box('Sign_Arm',(0,-.8,.1),(19,.8,1.7),10)
for x in (9,15):box('Sign_Hanger',(x-.55,-.55,-5.6),(x+.55,.55,.4),10)
outline=[(5,-10),(8.5,-4),(15.5,-4),(19,-10),(15.5,-16),(8.5,-16)]
# Historical orientation: rotate the board AND its mapped art, with points up/down.
outline=[(12-(z+10),-10+(x-12)) for x,z in outline]
vs=[(x,y,z) for y in (-.65,.65) for x,z in outline]
faces=[tuple(range(6)),tuple(range(11,5,-1))]+[(i,(i+1)%6,(i+1)%6+6,i+6) for i in range(6)]
# UV matches a literal six-sided inset, never the rounded-rectangle trial artwork.
faceuv=[[(0,.5),(.25,1),(.75,1),(1,.5),(.75,0),(.25,0)],[(.25,0),(.75,0),(1,.5),(.75,1),(.25,1),(0,.5)]]
uv=faceuv+[[(0,0),(1,0),(1,1),(0,1)] for _ in range(6)]
mesh('Sign_Hexagonal_Board',vs,faces,[25,25]+[1]*6,uv)
review.render.threads_mode='FIXED';review.render.threads=4;review.cycles.samples=24
# Rear dormer adds geometry: repack main UV2; props retain independent AO allocations.
for group,rect,size,m in [('Building',(1024,0,1536,512),1024,building_mat),('FlowerBox',(512,0,768,256),512,mat),('Sign',(768,0,1024,256),512,mat)]:
 selected=[o for o in meshes if o.get('module')==group];bpy.ops.object.select_all(action='DESELECT')
 for o in meshes:o.hide_render=o not in selected
 for o in selected:o.select_set(True);o.data.uv_layers.active_index=1
 bpy.context.view_layer.objects.active=selected[0]
 bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=math.radians(70),island_margin=.02,area_weight=.8,scale_to_bounds=True);bpy.ops.object.mode_set(mode='OBJECT')
 mn=m.node_tree.nodes;ml=m.node_tree.links;mb=mn.get('Principled BSDF');node=mn['AO'];old=node.image;ao=bpy.data.images.new(group+'_AO_v3',width=size,height=size,alpha=False);ao.colorspace_settings.name='Non-Color';node.image=ao;mn.active=node;review.render.bake.margin=8
 restore=[(l.from_socket,l.to_socket) for slot in ('Base Color','Normal') for l in list(mb.inputs[slot].links)]
 for slot in ('Base Color','Normal'):
  for l in list(mb.inputs[slot].links):ml.remove(l)
 bpy.ops.object.bake(type='AO',uv_layer='UV2');ao.filepath_raw=str(O/'bakes'/(group+'.png'));ao.file_format='PNG';ao.save();node.image=old
 for a,b in restore:ml.new(a,b)
 x0,y0,x1,y1=rect
 for o in selected:
  for d in o.data.uv_layers[1].data:d.uv=((x0+4+d.uv.x*(x1-x0-8))/2048,1-(y1-4-d.uv.y*(y1-y0-8))/2048)
  o.data.uv_layers.active_index=0;o.select_set(False)
for o in meshes:o.hide_render=False
# Save local-space reusable sources before applying proposed assembly placement.
for o in meshes:
 if o.get('module') in ('FlowerBox','Sign'):o['reuse_scope']='shared';o['reuse_approved']=True;o['source_asset_id']='CSC_ALL_Window_Box_Modern' if o['module']=='FlowerBox' else 'CSC_ALL_Hanging_Sign_Modern'
for im in bpy.data.images:
 if im.source=='FILE' and im.filepath:im.filepath='//textures/'+im.filepath.replace('\\','/').split('/')[-1]
bpy.ops.wm.save_as_mainfile(filepath=str(O/'Decor_Local_Masters.blend'),relative_remap=False)
for o in list(meshes):
 if o.get('module')=='FlowerBox':
  dup=o.copy();dup.data=o.data;review.collection.objects.link(dup);export.collection.objects.link(dup);dup['module']='FlowerBox_Instance';dup.location=(40.2,0,39.2);dup.rotation_euler.z=math.pi/2;dup.scale=(.8,.8,.8)
  rear=o.copy();rear.data=o.data;review.collection.objects.link(rear);export.collection.objects.link(rear);rear['module']='FlowerBox_Instance';rear.location=(14,29.2,7.2);rear.rotation_euler.z=math.pi;rear.scale=(.6,.6,.6)
  o.location=(-40.2,0,39.2);o.rotation_euler.z=-math.pi/2;o.scale=(.8,.8,.8)
 elif o.get('module')=='Sign':o.location=(40.2,18,61)
bpy.ops.wm.save_as_mainfile(filepath=str(O/'CSC_Level_2_Modern_Assembly.blend'),relative_remap=False)
print('DECOR_BUILD_READY',flush=True)
