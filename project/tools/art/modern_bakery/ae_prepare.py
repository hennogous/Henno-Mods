"""Prepare the final human save, without rebuilding its geometry from generators."""
import bpy,json,sys,shutil,hashlib,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[4];ART=Path.home()/'Desktop/Working Files/3D Art'
O=Path.home()/'Desktop/Codex/modern-bakery-ae-20261028'
D=ART/'BAKERS/Bakery/modern/revision-03-height-interiors';L=ART/'Level 2/modern/revision-05-height-interiors'
NEW=D.parent/'revision-04-ae';NEWL=L.parent/'revision-06-ae'
sys.path[:0]=[str(ROOT/'project/tools/blender'),str(ROOT/'project/tools/blender/scene_export')]
from csc_scene_validation import suspend_csc_repairs,validate_current_scene
import decode_blend as dec
src=D/'CSC_BAKERS_Bakery_Modern_2_Review.blend'
def load(p):
 with suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(p),load_ui=False,use_scripts=False)
def dump(p,v):p.write_text(json.dumps(v,indent=2))
for f in ('sources','textures','bakes','models','masters'):(O/f).mkdir(exist_ok=True)
shutil.copy2(src,O/'sources'/src.name);shutil.copytree(D/'textures',O/'textures',dirs_exist_ok=True)
load(src);s=bpy.data.scenes['Review'];bpy.context.window.scene=s
meshes=[ob for ob in bpy.data.scenes['Export'].objects if ob.type=='MESH'];sel=[ob for ob in meshes if ob.get('module')=='Building']
placements={}
for ob in meshes:
 g=ob.get('module')
 if g not in placements:
  loc,rot,scale=ob.matrix_world.decompose();placements[g]={'position':list(loc),'rotation_degrees':[math.degrees(x) for x in rot.to_euler()],'scale':list(scale)}
dump(O/'placements.json',placements)
# Reuse UV2 islands so this is an AO refresh, not another geometry/UV redesign.
bpy.ops.object.select_all(action='DESELECT')
for ob in s.objects:
 if ob.type=='MESH':ob.hide_render=ob not in sel
for ob in sel:
 ob.select_set(True);ob.data.uv_layers.active_index=1;ob.data.uv_layers[1].active_render=True
 for d in ob.data.uv_layers[1].data:d.uv=((d.uv.x*2048-1028)/504,(d.uv.y*2048-1540)/504)
bpy.context.view_layer.objects.active=sel[0]
mat=sel[0].data.materials[0];ns=mat.node_tree.nodes;ls=mat.node_tree.links;bs=ns.get('Principled BSDF');node=ns['AO'];old=node.image
im=bpy.data.images.new('Bakery_AE_Building_AO',width=768,height=768,alpha=False);im.colorspace_settings.name='Non-Color';node.image=im;ns.active=node
restore=[(l.from_socket,l.to_socket) for slot in ('Base Color','Normal') for l in list(bs.inputs[slot].links)]
for slot in ('Base Color','Normal'):
 for link in list(bs.inputs[slot].links):ls.remove(link)
s.render.engine='CYCLES';s.cycles.samples=96;s.render.threads_mode='FIXED';s.render.threads=4;s.render.bake.margin=8
bpy.ops.object.bake(type='AO',uv_layer='UV2');im.filepath_raw=str(O/'bakes/Building.png');im.file_format='PNG';im.save();node.image=old
for a,b in restore:ls.new(a,b)
for ob in sel:
 for d in ob.data.uv_layers[1].data:d.uv=((1028+d.uv.x*504)/2048,(1540+d.uv.y*504)/2048)
 ob.data.uv_layers.active_index=0;ob.data.uv_layers[0].active_render=True;ob.select_set(False)
for ob in meshes:ob.hide_render=False
for im in bpy.data.images:
 if im.source=='FILE' and im.filepath:
  name=im.filepath.replace('\\','/').split('/')[-1]
  if name and (O/'textures'/name).is_file():im.filepath='//textures/'+name
bpy.ops.wm.save_as_mainfile(filepath=str(O/'CSC_BAKERS_Bakery_Modern_2_Review.blend'),relative_remap=False)
print('PREPARED_HUMAN_SAVE',flush=True)

spec=[('Building','CSC_Level_2_Modern',NEWL),('Workshop','CSC_Level_2_Modern_Workshop',NEWL),('FlowerBox','CSC_ALL_Window_Box_Modern',NEWL),('Truck','CSC_BAKERS_Delivery_Truck_Modern',NEW),('Oven','CSC_BAKERS_Deck_Oven_Modern',NEW),('Display','CSC_BAKERS_Bread_Display_Modern',NEW),('Rack','CSC_BAKERS_Bread_Rack_Modern',NEW),('Trays','CSC_BAKERS_Tray_Stack_Modern',NEW),('Sign','CSC_BAKERS_Hanging_Sign_Modern',NEW)]
for folder in (NEW,NEWL):
 folder.mkdir(exist_ok=True);shutil.copytree(O/'textures',folder/'textures',dirs_exist_ok=True)
records=[]
for group,ident,folder in spec:
 load(O/'CSC_BAKERS_Bakery_Modern_2_Review.blend')
 for ob in list(bpy.data.objects):
  if ob.type=='MESH' and ob.get('module')!=group:bpy.data.objects.remove(ob,do_unlink=True)
 rig=next(o for o in bpy.data.scenes['Export'].objects if o.type=='ARMATURE');rig.name=ident;rig.data.name=ident
 for sc in (bpy.data.scenes['Review'],bpy.data.scenes['Export']):sc['asset_id']=ident
 for ob in bpy.data.scenes['Export'].objects:
  if ob.type=='MESH':
   ob['source_asset_id']=ident;ob['reuse_approved']=False
   if group not in ('Building','Workshop'):ob.location=(0,0,0);ob.rotation_euler=(0,0,0);ob.scale=(1,1,1)
 p=folder/(ident+'.blend');bpy.ops.wm.save_as_mainfile(filepath=str(p),relative_remap=False);load(p)
 report=validate_current_scene();dump(folder/(ident+'-validation.json'),report);assert report['automated_pass'],report['findings']
 bpy.context.window.scene=bpy.data.scenes['Export'];bpy.context.view_layer.update()
 model={'asset_id':ident,'kind':'building' if group in ('Building','Workshop') else 'prop','meshes':[dec.merge_meshes(ident,[dec.decode_mesh(ob,ob.matrix_world) for ob in bpy.context.scene.objects if ob.type=='MESH'])]}
 for mesh in model['meshes']:
  for m in mesh['materials']:m['external']='CSC_BAKERS_Modern' if m['name'].startswith('CSC_BAKERS_Modern') else 'CSC_Props_Modern_01'
 dump(O/'models'/(ident+'.json'),model);records.append({'id':ident,'group':group,'blend':str(p),'vertices':sum(len(m['vertices']) for m in model['meshes']),'triangles':sum(len(m['triangles']) for m in model['meshes'])})
for ident in ('CSC_BAKERS_Bakery_Modern_2','CSC_BAKERS_Bakery_Modern'):
 load(O/'CSC_BAKERS_Bakery_Modern_2_Review.blend')
 if not ident.endswith('_2'):
  for ob in list(bpy.data.objects):
   if ob.type=='MESH' and ob.get('module')=='Truck':bpy.data.objects.remove(ob,do_unlink=True)
 for sc in (bpy.data.scenes['Review'],bpy.data.scenes['Export']):sc['asset_id']=ident
 p=NEW/(ident+'_Review.blend');bpy.ops.wm.save_as_mainfile(filepath=str(p),relative_remap=False);load(p)
 report=validate_current_scene();dump(NEW/(ident+'-validation.json'),report);assert report['automated_pass']
dump(O/'masters.json',records);assert hashlib.sha256(src.read_bytes()).hexdigest()==json.loads((O/'user-edits.json').read_text())['sha256']
print('MASTERS_READY',json.dumps(records),flush=True)
