import bpy,sys,json,shutil,hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[4];ART=Path.home()/'Desktop/Working Files/3D Art';O=Path.home()/'Desktop/Codex/modern-bakery-v3-20261028'
D=ART/'BAKERS/Bakery/modern/revision-03-height-interiors';L=ART/'Level 2/modern/revision-05-height-interiors'
sys.path[:0]=[str(ROOT/'project/tools/blender'),str(ROOT/'project/tools/blender/scene_export')]
from csc_scene_validation import suspend_csc_repairs,validate_current_scene
import decode_blend as dec
spec=[('Building','CSC_Level_2_Modern',L),('Workshop','CSC_Level_2_Modern_Workshop',L),('Truck','CSC_BAKERS_Delivery_Truck_Modern',D),('Oven','CSC_BAKERS_Deck_Oven_Modern',D),('Display','CSC_BAKERS_Bread_Display_Modern',D),('Rack','CSC_BAKERS_Bread_Rack_Modern',D),('Trays','CSC_BAKERS_Tray_Stack_Modern',D),('Sign','CSC_BAKERS_Hanging_Sign_Modern',D)]
for folder in (D,L):
 folder.mkdir(parents=True,exist_ok=True);shutil.copytree(O/'textures',folder/'textures',dirs_exist_ok=True);shutil.copytree(O/'sources',folder/'texture-sources',dirs_exist_ok=True,ignore=shutil.ignore_patterns('*.blend'));shutil.copy2(O/'atlas-plan-v3.json',folder/'atlas-plan-candidate.json')
def clean_reference():
 export=set(bpy.data.scenes['Export'].objects)
 for ob in list(bpy.data.objects):
  if ob.type=='MESH' and ob not in export:bpy.data.objects.remove(ob,do_unlink=True)
 # Drop only now-unused images/materials from the imported historical comparison.
 for m in list(bpy.data.materials):
  if m.users==0:bpy.data.materials.remove(m)
 for im in list(bpy.data.images):
  if im.users==0:bpy.data.images.remove(im)
  elif im.source=='FILE' and im.filepath and (O/'textures'/im.filepath.replace('\\','/').split('/')[-1]).exists():im.filepath='//textures/'+im.filepath.replace('\\','/').split('/')[-1]
def validate(path,reportpath):
 with suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
 report=validate_current_scene();reportpath.write_text(json.dumps(report,indent=2));assert report['automated_pass'],report['findings'];return report
records=[]
for group,ident,folder in spec:
 with suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(O/'CSC_BAKERS_Bakery_Modern_2_Review.blend'),load_ui=False,use_scripts=False)
 for ob in list(bpy.data.objects):
  if ob.type=='MESH' and ob.get('module')!=group:bpy.data.objects.remove(ob,do_unlink=True)
 clean_reference();rig=next(o for o in bpy.data.scenes['Export'].objects if o.type=='ARMATURE');rig.name=ident;rig.data.name=ident
 for s in (bpy.data.scenes['Review'],bpy.data.scenes['Export']):s['asset_id']=ident
 for ob in bpy.data.scenes['Export'].objects:
  if ob.type=='MESH':
   ob['source_asset_id']=ident;ob['reuse_approved']=False
   if group not in ('Building','Workshop'):ob.location=(0,0,0);ob.rotation_euler=(0,0,0);ob.scale=(1,1,1)
 s=bpy.data.scenes['Review'];bpy.context.window.scene=s
 if group not in ('Building','Workshop'):
  target=Vector((0,0,15) if group!='Sign' else (9,0,-6));s.camera.location=target+Vector((60,-100,55));s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=65
 path=folder/(ident+'.blend');bpy.ops.wm.save_as_mainfile(filepath=str(path),relative_remap=False);report=validate(path,folder/(ident+'-validation.json'))
 bpy.context.window.scene=bpy.data.scenes['Export'];bpy.context.view_layer.update();model={'asset_id':ident,'kind':'building' if group in ('Building','Workshop') else 'prop','meshes':[dec.merge_meshes(ident,[dec.decode_mesh(ob,ob.matrix_world) for ob in bpy.context.scene.objects if ob.type=='MESH'])]}
 (O/'models'/(ident+'.json')).write_text(json.dumps(model));records.append({'id':ident,'blend':str(path),'vertices':sum(len(m['vertices']) for m in model['meshes']),'triangles':sum(len(m['triangles']) for m in model['meshes']),'validation_errors':report['error_count']})
for ident in ('CSC_BAKERS_Bakery_Modern','CSC_BAKERS_Bakery_Modern_2'):
 with suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(O/(ident+'_Review.blend')),load_ui=False,use_scripts=False)
 clean_reference();path=D/(ident+'_Review.blend');bpy.ops.wm.save_as_mainfile(filepath=str(path),relative_remap=False);validate(path,D/(ident+'-validation.json'))
with suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(D/'CSC_BAKERS_Bakery_Modern_Review.blend'),load_ui=False,use_scripts=False)
for ob in list(bpy.data.objects):
 if ob.type=='MESH' and ob.get('module') not in ('Building','Workshop','FlowerBox','FlowerBox_Instance','Sign'):bpy.data.objects.remove(ob,do_unlink=True)
 elif ob.type=='MESH' and ob.get('module')=='Sign':
  ob['source_asset_id']='CSC_ALL_Hanging_Sign_Modern'
  if 'Sign_Hexagonal_Board' in ob.name:
   for p in ob.data.polygons:
    if len(p.vertices)==6:
     for k in p.loop_indices:ob.data.uv_layers[0].data[k].uv.x-=.5
clean_reference()
for s in (bpy.data.scenes['Review'],bpy.data.scenes['Export']):s['asset_id']='CSC_Level_2_Modern'
path=L/'CSC_Level_2_Modern_Review.blend';bpy.ops.wm.save_as_mainfile(filepath=str(path),relative_remap=False);validate(path,L/'review-validation.json')
(O/'masters.json').write_text(json.dumps(records,indent=2));print('V3_MASTERS',json.dumps(records),flush=True)
