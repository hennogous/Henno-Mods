"""C-derived Bakery v2: scoped L2 corrections, short shelter, electric oven, delivery."""
import bpy,bmesh,math,json,sys,ast,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[4];ART=Path.home()/'Desktop/Working Files/3D Art'
O=Path.home()/'Desktop/Codex/modern-bakery-v2-20261028';SRC=ART/'BAKERS/Bakery/modern/revision-01-sheltered-bakery/CSC_BAKERS_Bakery_Modern_Review.blend'
sys.path[:0]=[str(ROOT/'project/tools/blender'),str(ROOT/'project/tools/blender/scene_export')]
from csc_scene_validation import suspend_csc_repairs
with suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(SRC),load_ui=False,use_scripts=False)
review=bpy.data.scenes['Review'];export=bpy.data.scenes['Export'];bpy.context.window.scene=review
rig=next(ob for ob in export.objects if ob.type=='ARMATURE')
bm=next(o.data.materials[0] for o in export.objects if o.type=='MESH' and o.get('module')=='Building');pm=bpy.data.materials['CSC_Props_Modern_01']
for im in bpy.data.images:
 if im.source=='FILE' and im.filepath:
  path=O/'textures'/im.filepath.replace('\\','/').split('/')[-1]
  if path.exists():im.filepath=str(path);im.reload()
# Record protected main-body geometry. Only dormers, windows and the extension change.
def geom_signature(ob):
 return hashlib.sha256(repr(([(tuple(v.co)) for v in ob.data.vertices],[tuple(p.vertices) for p in ob.data.polygons])).encode()).hexdigest()
protected={o.name:geom_signature(o) for o in export.objects if o.type=='MESH' and o.get('module')=='Building' and 'Dormer' not in o.name}
for ob in list(bpy.data.objects):
 if ob.type=='MESH' and (ob.get('module')=='Workshop' or (ob.get('module')=='Building' and 'Dormer' in ob.name)):bpy.data.objects.remove(ob,do_unlink=True)
meshes=[o for o in export.objects if o.type=='MESH']
for source,names in [('modern_level2/build.py',('mesh','panel')),('modern_bakery/build.py',('box','cylinder','loaf'))]:
 for node in ast.parse((ROOT/'project/tools/art'/source).read_text()).body:
  if isinstance(node,ast.FunctionDef) and node.name in names:exec(compile(ast.Module(body=[node],type_ignores=[]),'<mesh helpers>','exec'),globals())
prop_box=box
for node in ast.parse((ROOT/'project/tools/art/modern_level2/build.py').read_text()).body:
 if isinstance(node,ast.FunctionDef) and node.name=='box':
  node.name='building_box';exec(compile(ast.Module(body=[node],type_ignores=[]),'<building box>','exec'),globals())
def building_uv(slot,u,v):return ((512+slot%4*128+2+u*124)/1024,1-(slot//4*128+2+(1-v)*124)/1024)
def prop_uv(slot,u,v):return ((slot%8*128+3+u*122)/1024,1-(slot//8*128+3+(1-v)*122)/1024)
uvmap=building_uv;mat=bm;MODULE='Building';ID='CSC_Level_2_Modern'
# Restore the two upper windows on the visible long wall, with correct proportions.
for x in (-21,21):panel('Restored_Long_Upper_Window', (x-8,-29.08,43),(x+8,-29.08,43),(x+8,-29.08,63),(x-8,-29.08,63),5)
# Three compact shed dormers: two front, retained historical rear-facing one.
for x,side in [(-21,-1),(21,-1),(-21,1)]:
 y0=side*21;y1=side*8
 vs=[(x-7,y0,78),(x+7,y0,78),(x+7,y0,94),(x-7,y0,94),(x-7,y1,98),(x+7,y1,98)]
 mesh('V2_Dormer_Cheek',vs,[(0,1,2,3),(3,2,5,4),(0,3,4),(1,5,2),(0,4,5,1)],4)
 yy=side*21.08
 corners=[(x-6.1,yy,78.7),(x+6.1,yy,78.7),(x+6.1,yy,94),(x-6.1,yy,94)]
 if side>0:corners=list(reversed(corners))
 panel('V2_Dormer_Window',*corners,5)
 # Thin green cap follows the roof slope, with minimal overhang and no thick cream slab.
 a=side*23;b=side*7
 vs=[(x-8.3,a,94.6),(x+8.3,a,94.6),(x+8.3,b,100),(x-8.3,b,100),(x-8.3,a,95.7),(x+8.3,a,95.7),(x+8.3,b,101.1),(x-8.3,b,101.1)]
 mesh('V2_Dormer_Green_Cap',vs,[(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)],[8,8,8,8,8,2])
# Give only lower windows the warm B cell. Their E sampling stays black.
for ob in meshes:
 if ob.get('module')=='Building' and 'Ground_Window' in ob.name:
  for d in ob.data.uv_layers[0].data:d.uv.x+=(14%4-5%4)*128/1024;d.uv.y-=(14//4-5//4)*128/1024
for ob in meshes:
 if ob.get('module')=='Building':
  upper='Window' in ob.name and 'Ground' not in ob.name
  for j,d in enumerate(ob.data.uv_layers[2].data):d.uv=ob.data.uv_layers[0].data[j].uv if upper else (.02,.02)
# Open C-style shelter with a ten-unit return just behind the main front corner.
MODULE='Workshop';ID='CSC_Level_2_Modern_Workshop'
box=building_box
roofz=lambda y:35+(y+65)*.11
for x,y in [(-51,-62),(-20,-56),(-51,-22),(-20,-31)]:
 box('Shelter_Post',(x-1.7,y-1.7,-30),(x+1.7,y+1.7,roofz(y)),8)
 box('Shelter_Stone_Foot',(x-2.2,y-2.2,-30),(x+2.2,y+2.2,5),1)
box('Shelter_Short_Left_Return',(-54,-33,-30),(-50,-22,roofz(-33)),0)
box('Shelter_Short_Rear_End',(-54,-22,-30),(-39,-19,roofz(-22)),0)
box('Shelter_Return_Plinth',(-54.2,-33,-30),(-49.8,-22.2,6),1)
box('Shelter_Back_Plinth',(-54.2,-22.2,-30),(-38.8,-18.8,6),1)
def roof_piece(name,poly):
 n=len(poly);vs=[(x,y,roofz(y)+z) for z in (0,1.8) for x,y in poly]
 fs=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 ob=mesh(name,vs,fs,[8,2]+[3]*n)
 for p in ob.data.polygons:
  if p.normal.z>.8:
   for k in p.loop_indices:
    co=ob.data.vertices[ob.data.loops[k].vertex_index].co;ob.data.uv_layers[0].data[k].uv=building_uv(2,(co.x+54)/38,(co.y+65)/46)
roof_piece('Shelter_Forward_Roof',[(-54,-65),(-17,-59),(-17,-29),(-54,-29)])
roof_piece('Shelter_Short_Return_Roof',[(-54,-29),(-39,-29),(-39,-19),(-54,-19)])
# Simple braces carry the open side; timber grain is sampled along each beam.
for x in (-51,-20):
 a,b=-61,-30;za,zb=roofz(a)-1,roofz(b)-1
 mesh('Shelter_Side_Bearer',[(x-1.3,a,za-2),(x+1.3,a,za-2),(x+1.3,b,zb-2),(x-1.3,b,zb-2),(x-1.3,a,za),(x+1.3,a,za),(x+1.3,b,zb),(x-1.3,b,zb)],[(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)],8)
# Align painted timber grain with each support's long edge, including sloped bearers.
for ob in meshes:
 if ob.get('module')=='Workshop' and any(s in ob.name for s in ('Shelter_Post','Side_Bearer')):
  for p in ob.data.polygons:
   coords=[ob.data.vertices[i].co for i in p.vertices];edges=[coords[(i+1)%len(coords)]-co for i,co in enumerate(coords)];u=max(edges,key=lambda e:e.length).normalized();v=p.normal.cross(u).normalized();projs=[(co.dot(u),co.dot(v)) for co in coords];lo=[min(q[i] for q in projs) for i in (0,1)];hi=[max(q[i] for q in projs) for i in (0,1)]
   for k,co in zip(p.loop_indices,coords):ob.data.uv_layers[0].data[k].uv=building_uv(8,(co.dot(u)-lo[0])/max(hi[0]-lo[0],.001),(co.dot(v)-lo[1])/max(hi[1]-lo[1],.001))
# Existing props are rigidly repositioned; no non-uniform scaling.
placements={'Oven':((-34,-46,0),math.pi/4),'Rack':((-43,-59,0),0),'Trays':((-24,-60,0),0),'Display':((10,-37,0),0)}
for ob in meshes:
 if ob.get('module') in placements:ob.location,ob.rotation_euler.z=placements[ob['module']]
# Delivery vehicle: front is -X, rear loading aperture +X. One coherent small truck.
uvmap=prop_uv;mat=pm;MODULE='Truck';ID='CSC_BAKERS_Delivery_Truck_Modern'
box=prop_box
box('Truck_Chassis',(-20,-6,2),(20,6,5),10)
profile=[(-20,5),(-20,12),(-15.5,14),(-12,22),(-5,22),(-5,5)]
vs=[(x,y,z) for y in (-7.5,7.5) for x,z in profile];n=len(profile)
faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
cab=mesh('Truck_Cab',vs,faces,1)
for p in cab.data.polygons:
 for k in p.loop_indices:
  co=cab.data.vertices[cab.data.loops[k].vertex_index].co
  if abs(p.normal.y)>.8:uv=prop_uv(33,(co.x+20)/15,(co.z-5)/17)
  elif p.normal.x<-.5:uv=prop_uv(32,(co.y+7.5)/15,(co.z-5)/17)
  else:uv=prop_uv(1,(co.x+20)/15,(co.y+7.5)/15)
  cab.data.uv_layers[0].data[k].uv=uv
box('Truck_Front_Bumper',(-21,-8,4),(-19.6,8,5.8),3)
box('Truck_Cargo_Floor',(-4,-8,5),(19,8,6.4),10)
box('Truck_Cargo_Roof',(-4.5,-8.5,25),(19.5,8.5,26.5),3)
box('Truck_Cargo_Bulkhead',(-4,-8,6),(-2.8,8,25),3)
for y in (-8,7.2):
 ob=box('Truck_Cargo_Side',(-4,y,6),(19,y+.8,25),3)
 for p in ob.data.polygons:
  if (y<0 and p.normal.y<-.9) or (y>0 and p.normal.y>.9):
   for k in p.loop_indices:
    co=ob.data.vertices[ob.data.loops[k].vertex_index].co;ob.data.uv_layers[0].data[k].uv=prop_uv(34,(co.x+4)/23,(co.z-6)/19)
 # Open rear doors run along X, leaving the full rear aperture clear.
 box('Truck_Open_Rear_Door',(19,y,6),(26,y+.8,25),3)
box('Truck_Rear_Loading_Step',(18.5,-8.7,4),(21,8.7,5.2),10)
for x in (-12,12):
 for y in (-8,8):
  ob=cylinder('Truck_Wheel',(x,0,3.4),3.4,1.8,10,axis='Z',segments=12)
  # Rotate an authored Z cylinder into Y; source meshes remain unit-scaled.
  for v in ob.data.vertices:
   xx,yy,zz=v.co.copy();v.co=(xx,y-(zz-3.4),3.4+yy)
  ob.data.update()
  for p in ob.data.polygons:
   if len(p.vertices)==12:
    for k in p.loop_indices:
     co=ob.data.vertices[ob.data.loops[k].vertex_index].co;ob.data.uv_layers[0].data[k].uv=prop_uv(35,(co.x-x)/6.8+.5,(co.z-3.4)/6.8+.5)
for z in (8,13,18):
 box('Truck_Bread_Shelf',(10,-6,z),(18,6,z+.7),10)
 for y in (-3,3):loaf('Truck_Bread_Load',14,y,z+.8,6,5)
# Bake changed modules in isolation; all unchanged props keep their proven UV2.
alloc={'Building':([1024,0,1536,512],bm),'Workshop':([1536,0,1792,256],bm),'Truck':([512,768,1024,1024],pm)}
review.cycles.samples=96;review.render.threads_mode='FIXED';review.render.threads=4
for group,(rect,m) in alloc.items():
 selected=[o for o in meshes if o.get('module')==group];bpy.ops.object.select_all(action='DESELECT')
 for o in meshes:o.hide_render=o not in selected
 for o in selected:o.select_set(True);o.data.uv_layers.active_index=1;o.data.uv_layers[1].active_render=True
 bpy.context.view_layer.objects.active=selected[0];bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=math.radians(75),island_margin=.018,area_weight=.8,scale_to_bounds=True);bpy.ops.object.mode_set(mode='OBJECT')
 ns=m.node_tree.nodes;ls=m.node_tree.links;bs=ns.get('Principled BSDF');node=ns['AO'];old=node.image;ao=bpy.data.images.new(group+'_v2_AO',width=768,height=768,alpha=False);ao.colorspace_settings.name='Non-Color';node.image=ao;ns.active=node;review.render.bake.margin=8
 restore=[(l.from_socket,l.to_socket) for slot in ('Base Color','Normal') for l in list(bs.inputs[slot].links)]
 for slot in ('Base Color','Normal'):
  for l in list(bs.inputs[slot].links):ls.remove(l)
 bpy.ops.object.bake(type='AO',uv_layer='UV2');ao.filepath_raw=str(O/'bakes'/f'{group}.png');ao.file_format='PNG';ao.save();node.image=old
 for a,b in restore:ls.new(a,b)
 x0,y0,x1,y1=rect
 for ob in selected:
  for d in ob.data.uv_layers[1].data:d.uv=((x0+4+d.uv.x*(x1-x0-8))/2048,1-(y1-4-d.uv.y*(y1-y0-8))/2048)
  ob.data.uv_layers.active_index=0;ob.data.uv_layers[0].active_render=True;ob.select_set(False)
 print('BAKED',group,flush=True)
for ob in meshes:ob.hide_render=False
assert all(geom_signature(bpy.data.objects[name])==sig for name,sig in protected.items())
for im in bpy.data.images:
 if im.source=='FILE' and im.filepath:im.filepath='//textures/'+im.filepath.replace('\\','/').split('/')[-1]
bpy.ops.wm.save_as_mainfile(filepath=str(O/'V2_Local_Masters.blend'),relative_remap=False)
for ob in meshes:
 if ob.get('module')=='Truck':ob.location=(-79,-64,0)
review.camera.data.ortho_scale=211;target=Vector((-16,-17,53));review.camera.location=target+Vector((230,-300,230));review.camera.rotation_euler=(target-review.camera.location).to_track_quat('-Z','Y').to_euler()
review['asset_id']='CSC_BAKERS_Bakery_Modern_2';export['asset_id']='CSC_BAKERS_Bakery_Modern_2'
bpy.ops.wm.save_as_mainfile(filepath=str(O/'CSC_BAKERS_Bakery_Modern_2_Review.blend'),relative_remap=False)
for ob in meshes:
 if ob.get('module')=='Truck':bpy.data.objects.remove(ob,do_unlink=True)
review['asset_id']='CSC_BAKERS_Bakery_Modern';export['asset_id']='CSC_BAKERS_Bakery_Modern'
bpy.ops.wm.save_as_mainfile(filepath=str(O/'CSC_BAKERS_Bakery_Modern_Review.blend'),relative_remap=False)
(O/'v2-build-report.json').write_text(json.dumps({'protected_main_objects_unchanged':list(protected),'shelter_return_end_y':-19,'main_front_y':-29,'main_back_y':29,'oven_yaw_degrees':45,'placements':{k:[list(v[0]),v[1]] for k,v in placements.items()},'truck_position':[-79,-64,0],'AO':{k:v[0] for k,v in alloc.items()}},indent=2))
print('BAKERY_V2_READY',flush=True)
