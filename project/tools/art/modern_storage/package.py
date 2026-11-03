"""Save standalone editable masters, validate the saved sources, decode native contracts."""
import bpy,json,sys,shutil,hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[4];A=Path.home()/'Desktop/Working Files/3D Art';O=Path.home()/'Desktop/Codex/modern-storage-v1-20261029'
sys.path[:0]=[str(ROOT/'project/tools/blender'),str(ROOT/'project/tools/blender/scene_export')]
from csc_scene_validation import suspend_csc_repairs,validate_current_scene
import decode_blend as dec
P=A/'Storage/Props/modern/revision-01'
groups={'M':('CSC_Storage_M_Modern',A/'Storage/Storage_M/modern/revision-01'),'L':('CSC_Storage_L_Modern',A/'Storage/Storage_L/modern/revision-01'),'Hoist':('CSC_ALL_Storage_Hoist_Modern',P),'Truck':('CSC_ALL_Flatbed_Compact_Modern',P),'PalletJack':('CSC_ALL_Pallet_Jack_Modern',P),'Drum':('CSC_ALL_Ingredient_Drum_Modern',P)}
records=[]
for group,(ident,folder) in groups.items():
 folder.mkdir(parents=True,exist_ok=True);shutil.copytree(O/'textures',folder/'textures',dirs_exist_ok=True)
 with suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(O/'Local_Models.blend'),load_ui=False,use_scripts=False)
 for ob in list(bpy.data.objects):
  if ob.type=='MESH' and ob.get('module')!=group:bpy.data.objects.remove(ob,do_unlink=True)
 for sc in (bpy.data.scenes['Export'],bpy.data.scenes['Review']):sc['asset_id']=ident
 rig=next(ob for ob in bpy.data.scenes['Export'].objects if ob.type=='ARMATURE');rig.name=rig.data.name=ident
 for ob in bpy.data.scenes['Export'].objects:
  if ob.type=='MESH':ob['source_asset_id']=ident
 for ma in list(bpy.data.materials):
  if ma.users==0:bpy.data.materials.remove(ma)
 for im in list(bpy.data.images):
  if im.users==0:bpy.data.images.remove(im)
  elif im.source=='FILE':
   fn=im.filepath.replace('\\','/').split('/')[-1]
   if (folder/'textures'/fn).exists():im.filepath=str(folder/'textures'/fn);im.reload()
 review=bpy.data.scenes['Review'];bpy.context.window.scene=review;pts=[v.co for ob in review.objects if ob.type=='MESH' for v in ob.data.vertices];lo=Vector([min(v[i] for v in pts) for i in range(3)]);hi=Vector([max(v[i] for v in pts) for i in range(3)]);target=(lo+hi)/2;review.camera.location=target+Vector((-150,-220,160));review.camera.rotation_euler=(target-review.camera.location).to_track_quat('-Z','Y').to_euler();review.camera.data.ortho_scale=max(hi-lo)*1.6
 path=folder/(ident+'.blend');bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(path));bpy.ops.file.make_paths_relative();bpy.ops.wm.save_as_mainfile(filepath=str(path))
 with suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
 result=validate_current_scene();(O/'models'/(ident+'-validation.json')).write_text(json.dumps(result,indent=2));assert result['automated_pass'],result['findings']
 bpy.context.window.scene=bpy.data.scenes['Export'];bpy.context.view_layer.update();ms=[dec.decode_mesh(ob,ob.matrix_world) for ob in bpy.context.scene.objects if ob.type=='MESH'];model={'asset_id':ident,'kind':'building' if group in ('M','L') else 'prop','meshes':[dec.merge_meshes(ident,ms)]}
 for m in model['meshes']:
  for ma in m['materials']:ma['external']=ma['name'].split('.')[0]
 (O/'models'/(ident+'.json')).write_text(json.dumps(model));records.append({'id':ident,'group':group,'blend':str(path),'vertices':sum(len(m['vertices']) for m in model['meshes']),'triangles':sum(len(m['triangles']) for m in model['meshes']),'saved_validation':True,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bounds':[list(lo),list(hi)]})
(O/'masters.json').write_text(json.dumps(records,indent=2));print('MASTERS_SAVED',json.dumps(records),flush=True)
