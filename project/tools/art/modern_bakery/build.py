"""First Bakery assembly proposal from saved L2 masters; never rebuild their geometry."""
import bpy,bmesh,math,json,sys,ast,shutil
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[4];ART=Path.home()/'Desktop/Working Files/3D Art'
O=Path.home()/'Desktop/Codex/modern-bakery-v1-20261028';L2=ART/'Level 2/modern/revision-03-window-boxes-sign'
sys.path[:0]=[str(ROOT/'project/tools/blender'),str(ROOT/'project/tools/blender/scene_export')]
from csc_scene_validation import suspend_csc_repairs
with suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(L2/'CSC_Level_2_Modern_Review.blend'),load_ui=False,use_scripts=False)
review=bpy.data.scenes['Review'];export=bpy.data.scenes['Export'];bpy.context.window.scene=review
rig=next(o for o in export.objects if o.type=='ARMATURE')
# Replace review copies with actual latest saved architecture, preserving authored coordinates.
for group,filename in [('Building','CSC_Level_2_Modern.blend'),('Workshop','CSC_Level_2_Modern_Workshop.blend')]:
 for ob in list(bpy.data.objects):
  if ob.type=='MESH' and ob.get('module')==group:bpy.data.objects.remove(ob,do_unlink=True)
 with bpy.data.libraries.load(str(L2/filename),link=False) as (src,dst):dst.objects=list(src.objects)
 for ob in dst.objects:
  if ob and ob.type=='MESH':
   review.collection.objects.link(ob);export.collection.objects.link(ob)
   for mod in ob.modifiers:
    if mod.type=='ARMATURE':mod.object=rig
  elif ob and ob.users==0:bpy.data.objects.remove(ob)
for im in bpy.data.images:
 if im.source=='FILE' and im.filepath:
  name=im.filepath.replace('\\','/').split('/')[-1]
  if (O/'textures'/name).exists():im.filepath=str(O/'textures'/name);im.reload()
for m in bpy.data.materials:
 if m.use_nodes:
  for n in m.node_tree.nodes:
   if n.type=='BSDF_PRINCIPLED':n.inputs['Emission Strength'].default_value=0
mat=bpy.data.materials['CSC_Props_Modern_01'];meshes=[o for o in export.objects if o.type=='MESH']
for node in ast.parse((ROOT/'project/tools/art/modern_level2/build.py').read_text()).body:
 if isinstance(node,ast.FunctionDef) and node.name in ('mesh','panel'):exec(compile(ast.Module(body=[node],type_ignores=[]),'<mesh helpers>','exec'),globals())
def uvmap(slot,u,v):return ((slot%8*128+3+u*122)/1024,1-(slot//8*128+3+(1-v)*122)/1024)
def box(name,lo,hi,slot):
 x,y,z=lo;X,Y,Z=hi
 ob=mesh(name,[(x,y,z),(X,y,z),(X,Y,z),(x,Y,z),(x,y,Z),(X,y,Z),(X,Y,Z),(x,Y,Z)],[(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)],slot)
 # Pallet-wood grain runs along U; choose each face's longest edge direction.
 if slot==18:
  for p in ob.data.polygons:
   axes=sorted((a for a in range(3) if abs(p.normal[a])<.9),key=lambda a:hi[a]-lo[a],reverse=True);u,v=axes
   for k in p.loop_indices:
    co=ob.data.vertices[ob.data.loops[k].vertex_index].co
    ob.data.uv_layers[0].data[k].uv=uvmap(slot,(co[u]-lo[u])/max(hi[u]-lo[u],.01),(co[v]-lo[v])/max(hi[v]-lo[v],.01))
 return ob
def cylinder(name,c,r,depth,slot,axis='Z',segments=8):
 vs=[]
 for q in (-depth/2,depth/2):
  for i in range(segments):
   a=2*math.pi*i/segments;v=(r*math.cos(a),r*math.sin(a),q)
   if axis=='X':v=(q,v[0],v[1])
   vs.append(tuple(c[j]+v[j] for j in range(3)))
 fs=[tuple(range(segments-1,-1,-1)),tuple(range(segments,segments*2))]+[(i,(i+1)%segments,(i+1)%segments+segments,i+segments) for i in range(segments)]
 return mesh(name,vs,fs,slot)
def loaf(name,x,y,z,w=6,d=5):
 vs=[]
 for scale,zz in [(0.84,.15),(1,.9),(.67,2.4)]:
  for i in range(8):
   a=math.tau*i/8;vs.append((x+math.cos(a)*w/2*scale,y+math.sin(a)*d/2*scale,z+zz))
 vs.append((x,y,z+2.9));fs=[tuple(range(7,-1,-1))]
 fs += [(j*8+i,j*8+(i+1)%8,(j+1)*8+(i+1)%8,(j+1)*8+i) for j in range(2) for i in range(8)]
 fs += [(16+i,16+(i+1)%8,24) for i in range(8)]
 uv=[]
 for face in fs:
  upper=all(v>=8 for v in face)
  uv.append([((vs[v][0]-x)/w+.5,(vs[v][1]-y)/d+.5) if upper else (.05+(vs[v][0]-x+w/2)/w*.16,.85+(vs[v][2]-z)/3*.1) for v in face])
 ob=mesh(name,vs,fs,31,uv)
 for p in ob.data.polygons:p.use_smooth=True
 return ob
# Oven is recessed within the existing open shelter, with a flue through its roof.
MODULE='Oven';ID='CSC_BAKERS_Deck_Oven_Modern'
oven=box('Oven_Body',(-11,0,1),(11,12,27),10)
for p in oven.data.polygons:
 if p.normal.y<-.9:
  for k in p.loop_indices:
   co=oven.data.vertices[oven.data.loops[k].vertex_index].co;oven.data.uv_layers[0].data[k].uv=uvmap(26,(co.x+11)/22,(co.z-1)/26)
for x in (-9,9):
 for y in (2,10):box('Oven_Foot',(x-1,y-1,0),(x+1,y+1,1.5),10)
cylinder('Oven_Flue',(0,8,36),2,20,10,segments=10)
cylinder('Oven_Flue_Rim',(0,8,46),2.5,1.1,10,segments=10)
# Dark cap opening is painted existing iron; rim silhouette remains geometry.
MODULE='Display';ID='CSC_BAKERS_Bread_Display_Modern'
box('Display_Wood_Cabinet',(-23,-7,0),(23,7,8),18)
for x in (-22,22):
 for y in (-7,7):box('Display_Green_Upright',(x-.8,y-.8,0),(x+.8,y+.8,29),1)
for z in (8,15,22):
 box('Display_Shelf',(-22,-7,z),(22,7,z+1),18)
 for i,x in enumerate((-16,-5.3,5.3,16)):
  loaf('Display_Loaf',x,-1,z+1,8.5,8)
# One closed cloth wedge: six broad stripes, short vertical valance.
vs=[(-24,-10,29),(24,-10,29),(24,8,35),(-24,8,35),(-24,-10,26.5),(24,-10,26.5),(24,8,33.5),(-24,8,33.5)]
fs=[(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]
uv=[[(0,0),(1,0),(1,1),(0,1)],[(0,0),(0,1),(1,1),(1,0)],[(0,.12),(0,0),(1,0),(1,.12)],[(0,0),(0,1),(1,1),(1,0)],[(0,0),(1,0),(1,1),(0,1)],[(0,0),(1,0),(1,1),(0,1)]]
mesh('Display_Striped_Canopy',vs,fs,28,uv)
MODULE='Rack';ID='CSC_BAKERS_Bread_Rack_Modern'
for x in (-6.3,6.3):
 for y in (-5.5,5.5):
  box('Rack_Post',(x-.65,y-.65,2),(x+.65,y+.65,25),10)
  cylinder('Rack_Caster',(x,y,1.6),1.6,1.4,10,axis='X')
for z in (4,11,18):
 tray=box('Rack_Tray',(-6,-5.5,z),(6,5.5,z+.7),10)
 for p in tray.data.polygons:
  if p.normal.z>.9:
   for k in p.loop_indices:
    co=tray.data.vertices[tray.data.loops[k].vertex_index].co;tray.data.uv_layers[0].data[k].uv=uvmap(30,(co.x+6)/12,(co.y+5.5)/11)
 for x in (-3.1,3.1):loaf('Rack_Bread',x,0,z+.8,5.6,8)
for x in (-6.3,6.3):box('Rack_Top_Rail',(x-.7,-6,24.3),(x+.7,6,25.7),10)
MODULE='Trays';ID='CSC_BAKERS_Tray_Stack_Modern'
for i in range(5):
 z=.4+i*1.5
 tray=box('Empty_Tray',(-5,-4,z),(5,4,z+.8),10)
 for p in tray.data.polygons:
  if p.normal.z>.9:
   for k in p.loop_indices:
    co=tray.data.vertices[tray.data.loops[k].vertex_index].co;tray.data.uv_layers[0].data[k].uv=uvmap(30,(co.x+5)/10,(co.y+4)/8)
# Quarter-specific sign graphic on the unchanged reusable point-up/down plaque.
for ob in meshes:
 if 'Sign_Hexagonal_Board' in ob.name:
  for p in ob.data.polygons:
   if len(p.vertices)==6:
    for k in p.loop_indices:
     co=ob.data.vertices[ob.data.loops[k].vertex_index].co
     ob.data.uv_layers[0].data[k].uv=uvmap(29,(co.x-6)/12,(co.z+17)/14)
# Bake each independent prop in isolation. Normal artwork never participates in AO.
review.render.engine='CYCLES';review.cycles.samples=96;review.render.threads_mode='FIXED';review.render.threads=4
allocation=json.loads((O/'brief.json').read_text())['AO_candidates']
for group,rect in allocation.items():
 sel=[o for o in meshes if o.get('module')==group];bpy.ops.object.select_all(action='DESELECT')
 for o in meshes:o.hide_render=o not in sel
 for o in sel:o.select_set(True);o.data.uv_layers.active_index=1;o.data.uv_layers[1].active_render=True
 bpy.context.view_layer.objects.active=sel[0]
 bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=math.radians(75),island_margin=.025,area_weight=.8,scale_to_bounds=True);bpy.ops.object.mode_set(mode='OBJECT')
 ns=mat.node_tree.nodes;ls=mat.node_tree.links;bs=ns.get('Principled BSDF');node=ns['AO'];old=node.image
 ao=bpy.data.images.new(group+'_AO',width=512,height=512,alpha=False);ao.colorspace_settings.name='Non-Color';node.image=ao;ns.active=node;review.render.bake.margin=6
 restore=[(l.from_socket,l.to_socket) for slot in ('Base Color','Normal') for l in list(bs.inputs[slot].links)]
 for slot in ('Base Color','Normal'):
  for l in list(bs.inputs[slot].links):ls.remove(l)
 bpy.ops.object.bake(type='AO',uv_layer='UV2');ao.filepath_raw=str(O/'bakes'/f'{group}.png');ao.file_format='PNG';ao.save();node.image=old
 for a,b in restore:ls.new(a,b)
 x0,y0,x1,y1=rect
 for o in sel:
  for d in o.data.uv_layers[1].data:d.uv=((x0+4+d.uv.x*(x1-x0-8))/2048,1-(y1-4-d.uv.y*(y1-y0-8))/2048)
  o.data.uv_layers.active_index=0;o.data.uv_layers[0].active_render=True;o.select_set(False)
 print('BAKED',group,flush=True)
for o in meshes:o.hide_render=False
for im in bpy.data.images:
 if im.source=='FILE' and im.filepath:im.filepath='//textures/'+im.filepath.replace('\\','/').split('/')[-1]
bpy.ops.wm.save_as_mainfile(filepath=str(O/'Local_Props.blend'),relative_remap=False)
placements={'Oven':(-34,-63,0),'Display':(10,-37,0),'Rack':(-45,-75,0),'Trays':(-20,-73,0)}
for ob in meshes:
 if ob.get('module') in placements:ob.location=placements[ob['module']]
review['asset_id']='CSC_BAKERS_Bakery_Modern';export['asset_id']='CSC_BAKERS_Bakery_Modern'
review['proposal_only']=True;review['architecture_source']=str(L2)
target=Vector((-4,-14,53));review.camera.location=target+Vector((230,-300,230));review.camera.rotation_euler=(target-review.camera.location).to_track_quat('-Z','Y').to_euler();review.camera.data.type='ORTHO';review.camera.data.ortho_scale=185
review.render.resolution_x=review.render.resolution_y=1200;review.render.resolution_percentage=100;review.render.film_transparent=True
bpy.ops.wm.save_as_mainfile(filepath=str(O/'CSC_BAKERS_Bakery_Modern_Review.blend'),relative_remap=False)
(O/'placements.json').write_text(json.dumps(placements,indent=2));print('BAKERY_BUILD_READY',flush=True)
