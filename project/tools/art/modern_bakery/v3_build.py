"""Edit the human-saved v2 scene; preserve its dormers, chimney and prop placements."""
import bpy,bmesh,math,json,sys,ast,hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[4];ART=Path.home()/'Desktop/Working Files/3D Art';O=Path.home()/'Desktop/Codex/modern-bakery-v3-20261028'
SRC=ART/'BAKERS/Bakery/modern/revision-02-concept-c/CSC_BAKERS_Bakery_Modern_2_Review.blend'
sys.path[:0]=[str(ROOT/'project/tools/blender'),str(ROOT/'project/tools/blender/scene_export')]
from csc_scene_validation import suspend_csc_repairs
with suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(SRC),load_ui=False,use_scripts=False)
review=bpy.data.scenes['Review'];export=bpy.data.scenes['Export'];bpy.context.window.scene=review;rig=next(o for o in export.objects if o.type=='ARMATURE')
# User imported a historical comparison mesh and hid it in the viewport only.
# Keep it as a reference but exclude it from production renders and all AO rays.
reference_only=[]
for ob in review.objects:
 if ob.type=='MESH' and ob.name not in export.objects:
  reference_only.append(ob.name);ob.hide_render=True
meshes=[o for o in export.objects if o.type=='MESH'];bm=next(o.data.materials[0] for o in meshes if o.get('module')=='Building');pm=bpy.data.materials['CSC_Props_Modern_01']
for im in bpy.data.images:
 if im.source=='FILE' and im.filepath:
  p=O/'textures'/im.filepath.replace('\\','/').split('/')[-1]
  if p.exists():im.filepath=str(p);im.reload()
  else:im.filepath=bpy.path.abspath(im.filepath)
def worldverts(ob):return [ob.matrix_world@v.co for v in ob.data.vertices]
def signature(ob):return hashlib.sha256(repr(([tuple(v.co) for v in ob.data.vertices],[tuple(p.vertices) for p in ob.data.polygons],list(map(list,ob.matrix_world)))).encode()).hexdigest()
locked={o.name:signature(o) for o in meshes if o.get('module') in ('Oven','Rack','Trays','Truck','Workshop')}
source_special={o.name:[list(v) for v in worldverts(o)] for o in meshes if 'Dormer' in o.name or 'Chimney' in o.name}
delta=113-109.04442596435547
# Shorten only the upper wall band; shift roof, user-authored dormers/chimney,
# gable openings and high flower boxes rigidly. Preserve all object transforms.
for ob in meshes:
 group=ob.get('module');shift=False
 if group=='Building':
  if ob.name.startswith('CSC_Fixed_Upper_'):
   inv=ob.matrix_world.inverted()
   for v in ob.data.vertices:
    w=ob.matrix_world@v.co;w.z=32+(w.z-32)*(34-delta)/34;v.co=inv@w
  elif any(n in ob.name for n in ('Roof','Bargeboard','Ridge','Dormer','Chimney','Gable','Restored_Long_Upper_Window')):shift=True
 elif group in ('FlowerBox','FlowerBox_Instance') and min(v.z for v in worldverts(ob))>32:shift=True
 if shift:
  ob.data=ob.data.copy();inv=ob.matrix_world.inverted()
  extra=1.0 if 'Gable_Cream_Crossbeam' in ob.name else 0.0
  for v in ob.data.vertices:w=ob.matrix_world@v.co;w.z-=delta+extra;v.co=inv@w
 if group=='Sign':ob.location.z-=44-35.32764434814453
# The user moved shaft/cap but not its old mouth card. Reattach just that card.
cap=next(o for o in meshes if o.name=='CSC_Fixed_Chimney_Cap');mouth=next(o for o in meshes if o.name=='CSC_Fixed_Chimney_Dark_Mouth')
cv=worldverts(cap);center=sum(cv,Vector())/len(cv);mv=worldverts(mouth);oldcenter=sum(mv,Vector())/len(mv);offset=Vector((center.x-oldcenter.x,center.y-oldcenter.y,max(v.z for v in cv)+.08-oldcenter.z));inv=mouth.matrix_world.inverted()
for v in mouth.data.vertices:v.co=inv@(mouth.matrix_world@v.co+offset)
print('HEIGHT_AND_HUMAN_EDITS_READY',flush=True)
for source,names in [('modern_level2/build.py',('mesh','panel')),('modern_bakery/build.py',('box',))]:
 for n in ast.parse((ROOT/'project/tools/art'/source).read_text()).body:
  if isinstance(n,ast.FunctionDef) and n.name in names:exec(compile(ast.Module(body=[n],type_ignores=[]),'<helpers>','exec'),globals())
def buv(slot,u,v):return ((512+slot%4*128+2+u*124)/1024,1-(slot//4*128+2+(1-v)*124)/1024)
def puv(slot,u,v):return ((slot%8*128+3+u*122)/1024,1-(slot//8*128+3+(1-v)*122)/1024)
uvmap=buv;mat=bm;MODULE='Building';ID='CSC_Level_2_Modern'
# Close both open eave edges with continuous dark-green fascia, not an open shell.
for side in (-1,1):
 y=side*34;box('Closed_Eave_Fascia',(-44,y-.45,61.95-delta),(44,y+.45,64.15-delta),8)
 # Under-eave horizontal return meets the wall and existing sloping underside.
 pts=[(-40,side*29,65.5-delta),(40,side*29,65.5-delta),(40,side*34,62.2-delta),(-40,side*34,62.2-delta)]
 if side>0:pts.reverse()
 panel('Closed_Eave_Soffit',*pts,8)
# Open actual wall apertures behind the textured ground-level window/door cards.
windows=[o for o in meshes if o.get('module')=='Building' and ('Ground_Window' in o.name or 'Entrance_Door' in o.name)]
apertures=[]
for win in windows:
 vs=worldverts(win);axis=0 if max(v.x for v in vs)-min(v.x for v in vs)<.01 else 1;t=1-axis
 lo=min(v[t] for v in vs)+.45;hi=max(v[t] for v in vs)-.45;z0=min(v.z for v in vs)+.45;z1=max(v.z for v in vs)-.45
 wall=bpy.data.objects['CSC_Fixed_Ground_East' if axis==0 else 'CSC_Fixed_Ground_Rear'];bmsh=bmesh.new();bmsh.from_mesh(wall.data)
 for ax,val in ((t,lo),(t,hi),(2,z0),(2,z1)):
  co=Vector();co[ax]=val;normal=Vector();normal[ax]=1
  bmesh.ops.bisect_plane(bmsh,geom=list(bmsh.verts)+list(bmsh.edges)+list(bmsh.faces),dist=.00001,plane_co=co,plane_no=normal)
 delete=[f for f in bmsh.faces if lo+.001<f.calc_center_median()[t]<hi-.001 and z0+.001<f.calc_center_median().z<z1-.001]
 bmesh.ops.delete(bmsh,geom=delete,context='FACES');bmsh.to_mesh(wall.data);bmsh.free();wall.data.update()
 # Room box is behind the opening with a real gap. Only large faces are geometry.
 front=sum(v[axis] for v in vs)/len(vs);near=front-1.0;back=front-7.0
 low=min(v[t] for v in vs)-.5;high=max(v[t] for v in vs)+.5;bottom=min(v.z for v in vs)-.5;top=max(v.z for v in vs)+.5
 def point(a,u,z):return (a,u,z) if axis==0 else (u,a,z)
 roomverts=[point(a,u,z) for a,u,z in [(near,low,bottom),(near,high,bottom),(near,high,top),(near,low,top),(back,low,bottom),(back,high,bottom),(back,high,top),(back,low,top)]]
 faces=[(4,5,6,7),(0,4,7,3),(5,1,2,6),(0,1,5,4),(3,7,6,2)]
 uv=[[(0,0),(1,0),(1,1),(0,1)]]*5
 room=mesh('Inset_Interior_'+win.name,roomverts,faces,[11,12,12,15,12],uv)
 # Open box faces point inward for future native back-face culling.
 b=bmesh.new();b.from_mesh(room.data)
 target=Vector(point((near+back)/2,(low+high)/2,(bottom+top)/2))
 for f in b.faces:
  if f.normal.dot(target-f.calc_center_median())<0:f.normal_flip()
 b.to_mesh(room.data);b.free();room.data.update()
 apertures.append({'window':win.name,'gap':1,'depth':6,'wall_faces_removed':len(delete)})
print('WINDOW_BOXES_READY',flush=True)
# Connect native-style opacity data. Cycles alpha is an approximation of
# Generic_OPAC MSAA coverage, explicitly not a refraction shader.
ns=bm.node_tree.nodes;ls=bm.node_tree.links;bs=ns.get('Principled BSDF');node=ns.new('ShaderNodeTexImage');node.name='O';node.image=bpy.data.images.load(str(O/'textures/CSC_Atlas_Modern_O.png'));node.image.colorspace_settings.name='Non-Color';uv=ns.new('ShaderNodeUVMap');uv.uv_map='UV1';ls.new(uv.outputs['UV'],node.inputs['Vector']);ls.new(node.outputs['Color'],bs.inputs['Alpha']);bm.surface_render_method='DITHERED'
# Replace only the display's repeated loaf meshes. Preserve the user's display
# object transform and all unaffected props.
display_transform=next(o.matrix_world.copy() for o in meshes if o.get('module')=='Display')
for ob in list(meshes):
 if ob.get('module')=='Display' and 'Display_Loaf' in ob.name:meshes.remove(ob);bpy.data.objects.remove(ob,do_unlink=True)
uvmap=puv;mat=pm;MODULE='Display';ID='CSC_BAKERS_Bread_Display_Modern'
for row,z in enumerate((8,15,22)):
 for col,x in enumerate((-14.5,0,14.5)):
  verts=[(x-6.7,-6,z+1.1),(x+6.7,-6,z+1.1),(x+6.7,6,z+4.3),(x-6.7,6,z+4.3),(x-6.7,-6,z+.5),(x+6.7,-6,z+.5),(x+6.7,6,z+.5),(x-6.7,6,z+.5)]
  fs=[(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)];slot=36+(row+col)%3
  ob=mesh('Painted_Bread_Tray',verts,fs,[slot,10,10,10,10,10],[[(0,0),(1,0),(1,1),(0,1)]]*6);ob.matrix_world=display_transform;ob['microAO_slot']=slot
# Verify human dormer/shaft/cap form and placement survive as a rigid roof lowering.
preserved={}
for name,vs in source_special.items():
 if name=='CSC_Fixed_Chimney_Dark_Mouth':continue
 now=worldverts(bpy.data.objects[name]);err=max((v-(Vector(old)-Vector((0,0,delta)))).length for v,old in zip(now,vs));assert err<.00003,(name,err);preserved[name]=err
assert all(signature(bpy.data.objects[name])==sig for name,sig in locked.items())
# Bake changed groups in isolation; UV2 is positional AO, not the surface atlas.
allocation={'Building':([1024,0,1536,512],bm),'Display':([512,512,768,768],pm)}
review.render.engine='CYCLES';review.cycles.samples=96;review.render.threads_mode='FIXED';review.render.threads=4
for group,(rect,material) in allocation.items():
 sel=[o for o in meshes if o.get('module')==group];bpy.ops.object.select_all(action='DESELECT')
 for ob in meshes:ob.hide_render=ob not in sel
 for ob in sel:ob.select_set(True);ob.data.uv_layers.active_index=1;ob.data.uv_layers[1].active_render=True
 bpy.context.view_layer.objects.active=sel[0];bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=math.radians(75),island_margin=.018,area_weight=.8,scale_to_bounds=True);bpy.ops.object.mode_set(mode='OBJECT')
 ns=material.node_tree.nodes;ls=material.node_tree.links;bs=ns.get('Principled BSDF');node=ns['AO'];old=node.image;im=bpy.data.images.new(group+'_v3_AO',width=768,height=768,alpha=False);im.colorspace_settings.name='Non-Color';node.image=im;ns.active=node;review.render.bake.margin=8
 restore=[(l.from_socket,l.to_socket) for slot in ('Base Color','Normal') for l in list(bs.inputs[slot].links)]
 for slot in ('Base Color','Normal'):
  for l in list(bs.inputs[slot].links):ls.remove(l)
 bpy.ops.object.bake(type='AO',uv_layer='UV2');im.filepath_raw=str(O/'bakes'/f'{group}.png');im.file_format='PNG';im.save();node.image=old
 for a,b in restore:ls.new(a,b)
 x0,y0,x1,y1=rect
 for ob in sel:
  for d in ob.data.uv_layers[1].data:d.uv=((x0+4+d.uv.x*(x1-x0-8))/2048,1-(y1-4-d.uv.y*(y1-y0-8))/2048)
  ob.data.uv_layers.active_index=0;ob.data.uv_layers[0].active_render=True;ob.select_set(False)
 print('BAKED',group,flush=True)
for ob in meshes:ob.hide_render=False
# Triangle mappings transfer the intentionally painted bread-contact AO to UV2.
micro=[]
for ob in meshes:
 if 'microAO_slot' not in ob:continue
 ob.data.calc_loop_triangles()
 for tr in ob.data.loop_triangles:
  uvs=[list(ob.data.uv_layers[0].data[k].uv) for k in tr.loops]
  if int(sum(u[1] for u in uvs)/3*8)==3 and int(sum(u[0] for u in uvs)/3*8)>=4:
   micro.append({'slot':ob['microAO_slot'],'UV1':uvs,'UV2':[list(ob.data.uv_layers[1].data[k].uv) for k in tr.loops]})
(O/'microAO-triangles.json').write_text(json.dumps(micro))
for im in bpy.data.images:
 if im.source=='FILE' and im.filepath and (O/'textures'/im.filepath.replace('\\','/').split('/')[-1]).exists():im.filepath='//textures/'+im.filepath.replace('\\','/').split('/')[-1]
target=Vector((-4,-15,53));review.camera.location=target+Vector((230,-300,230));review.camera.rotation_euler=(target-review.camera.location).to_track_quat('-Z','Y').to_euler();review.camera.data.type='ORTHO';review.camera.data.ortho_scale=185
bpy.ops.wm.save_as_mainfile(filepath=str(O/'CSC_BAKERS_Bakery_Modern_2_Review.blend'),relative_remap=False)
for ob in list(meshes):
 if ob.get('module')=='Truck':bpy.data.objects.remove(ob,do_unlink=True)
for s in (review,export):s['asset_id']='CSC_BAKERS_Bakery_Modern'
bpy.ops.wm.save_as_mainfile(filepath=str(O/'CSC_BAKERS_Bakery_Modern_Review.blend'),relative_remap=False)
(O/'v3-build-report.json').write_text(json.dumps({'source':str(SRC),'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'ridge_before':113,'ridge_after':109.04442596435547,'height_reduction':delta,'historical_sign_bottom':35.32764434814453,'edited_geometry_preserved_after_rigid_lowering':preserved,'locked_groups_preserved':len(locked),'chimney_mouth_reconnected':True,'interior_apertures':apertures,'AO':{k:v[0] for k,v in allocation.items()}},indent=2))
print('V3_BUILT',flush=True)
