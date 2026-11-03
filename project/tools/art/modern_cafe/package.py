import bpy,json,sys,shutil,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];A=Path.home()/'Desktop/Working Files/3D Art';O=Path.home()/'Desktop/Codex/modern-cafe-v1-20261029'
D=A/'BAKERS/Cafe/modern/revision-01-garden';L3=A/'Level 3/modern/revision-01-garden'
sys.path[:0]=[str(ROOT/'project/tools/blender'),str(ROOT/'project/tools/blender/scene_export')]
from csc_scene_validation import suspend_csc_repairs,validate_current_scene
import decode_blend as dec
groups={'Building':('CSC_Level_3_Modern',L3),'Counter':('CSC_BAKERS_Cafe_Counter_Modern',D),'Van':('CSC_BAKERS_Coffee_Van_Modern',D),'Parasol':('CSC_BAKERS_Cafe_Parasol_Modern',D),'Valance':('CSC_BAKERS_Cafe_Valance_Modern',D)}
for folder in (D,L3):folder.mkdir(parents=True,exist_ok=True);shutil.copytree(O/'textures',folder/'textures',dirs_exist_ok=True)
records=[]
for group,(ident,folder) in groups.items():
 with suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(O/'Local_Models.blend'),load_ui=False,use_scripts=False)
 for ob in list(bpy.data.objects):
  if ob.type=='MESH' and ob.get('module')!=group:bpy.data.objects.remove(ob,do_unlink=True)
 for sc in (bpy.data.scenes['Export'],bpy.data.scenes['Review']):sc['asset_id']=ident
 rig=next(ob for ob in bpy.data.scenes['Export'].objects if ob.type=='ARMATURE');rig.name=rig.data.name=ident
 for ob in bpy.data.scenes['Export'].objects:
  if ob.type=='MESH':ob['source_asset_id']=ident
 for ma in list(bpy.data.materials):
  if ma.users==0:bpy.data.materials.remove(ma)
 for img in list(bpy.data.images):
  if img.users==0:bpy.data.images.remove(img)
  elif img.source=='FILE' and img.filepath:
   fn=img.filepath.replace('\\','/').split('/')[-1]
   if (folder/'textures'/fn).exists():img.filepath=str(folder/'textures'/fn);img.reload()
 path=folder/(ident+'.blend');bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(path))
 with suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
 v=validate_current_scene();(folder/(ident+'-validation.json')).write_text(json.dumps(v,indent=2));assert v['automated_pass'],v['findings']
 bpy.context.window.scene=bpy.data.scenes['Export'];bpy.context.view_layer.update();ms=[dec.decode_mesh(ob,ob.matrix_world) for ob in bpy.context.scene.objects if ob.type=='MESH'];model={'asset_id':ident,'kind':'building' if group=='Building' else 'prop','meshes':[dec.merge_meshes(ident,ms)]}
 for m in model['meshes']:
  for ma in m['materials']:ma['external']=ma['name'].split('.')[0]
 (O/'models'/(ident+'.json')).write_text(json.dumps(model));records.append({'id':ident,'blend':str(path),'vertices':sum(len(m['vertices']) for m in model['meshes']),'triangles':sum(len(m['triangles']) for m in model['meshes']),'saved_validation':v['automated_pass']})
(O/'masters.json').write_text(json.dumps(records,indent=2));print('MASTERS_SAVED',json.dumps(records),flush=True)
