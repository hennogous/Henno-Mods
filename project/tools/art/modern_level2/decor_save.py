import bpy,sys,json,shutil
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[4];O=Path.home()/'Desktop/Codex/modern-level2-v3-details-20261028';ART=Path.home()/'Desktop/Working Files/3D Art'
D=ART/'Level 2/modern/revision-03-window-boxes-sign';P=ART/'Props/Modern/revision-01-architectural-details'
sys.path[:0]=[str(ROOT/'project/tools/blender'),str(ROOT/'project/tools/blender/scene_export')]
from csc_scene_validation import suspend_csc_repairs,validate_current_scene
import decode_blend as dec
records=[]
for group,ident,folder in [('Building','CSC_Level_2_Modern',D),('Workshop','CSC_Level_2_Modern_Workshop',D),('FlowerBox','CSC_ALL_Window_Box_Modern',P),('Sign','CSC_ALL_Hanging_Sign_Modern',P)]:
 folder.mkdir(parents=True,exist_ok=True);shutil.copytree(O/'textures',folder/'textures',dirs_exist_ok=True)
 with suspend_csc_repairs():
  bpy.ops.wm.open_mainfile(filepath=str(O/'Decor_Local_Masters.blend'),load_ui=False,use_scripts=False)
  for ob in list(bpy.data.objects):
   if ob.type=='MESH' and ob.get('module')!=group:bpy.data.objects.remove(ob,do_unlink=True)
  rig=next(ob for ob in bpy.data.objects if ob.type=='ARMATURE');rig.name=ident;rig.data.name=ident
  for s in (bpy.data.scenes['Review'],bpy.data.scenes['Export']):s['asset_id']=ident
  for ob in bpy.data.scenes['Export'].objects:
   if ob.type=='MESH':ob['source_asset_id']=ident
  for im in list(bpy.data.images):
   if im.users==0:bpy.data.images.remove(im)
   elif im.source=='FILE' and im.filepath:im.filepath='//textures/'+im.filepath.replace('\\','/').split('/')[-1]
  s=bpy.data.scenes['Review'];bpy.context.window.scene=s
  if group in ('FlowerBox','Sign'):
   target=Vector((0,-2,3) if group=='FlowerBox' else (10,0,-6));s.camera.location=target+Vector((35,-70,38));s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=40 if group=='FlowerBox' else 30
  path=folder/(ident+'.blend');bpy.ops.wm.save_as_mainfile(filepath=str(path),relative_remap=False);bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
  report=validate_current_scene();(folder/(ident+'-validation.json')).write_text(json.dumps(report,indent=2));assert report['automated_pass'],report['findings']
  bpy.context.window.scene=bpy.data.scenes['Export'];bpy.context.view_layer.update()
  model={'asset_id':ident,'kind':'building' if group in ('Building','Workshop') else 'prop','meshes':[dec.merge_meshes(ident,[dec.decode_mesh(ob,ob.matrix_world) for ob in bpy.context.scene.objects if ob.type=='MESH'])]}
  (O/'models'/(ident+'.json')).write_text(json.dumps(model));records.append({'id':ident,'blend':str(path),'vertices':sum(len(m['vertices']) for m in model['meshes']),'triangles':sum(len(m['triangles']) for m in model['meshes']),'validation_errors':report['error_count']})
shutil.copy2(O/'CSC_Level_2_Modern_Assembly.blend',D/'CSC_Level_2_Modern_Review.blend')
(O/'masters.json').write_text(json.dumps(records,indent=2));print('DECOR_MASTERS',json.dumps(records),flush=True)
