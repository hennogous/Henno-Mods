"""Save and reopen portable masters, with exact source-scene validation and export counts."""
import bpy,sys,json,shutil,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];O=Path.home()/'Desktop/Codex/modern-level2-v1-20261028'
D=Path.home()/'Desktop/Working Files/3D Art/Level 2/modern/revision-01-concept-base'
O=Path(os.environ.get('CSC_LEVEL2_OUTPUT',str(O)));D=Path(os.environ.get('CSC_LEVEL2_MASTERS',str(D)))
sys.path[:0]=[str(ROOT/'project/tools/blender'),str(ROOT/'project/tools/blender/scene_export')]
from csc_scene_validation import suspend_csc_repairs,validate_current_scene
import decode_blend as dec
D.mkdir(parents=True,exist_ok=True);shutil.copytree(O/'textures',D/'textures',dirs_exist_ok=True);records=[]
for group,ident in [('Building','CSC_Level_2_Modern'),('Workshop','CSC_Level_2_Modern_Workshop')]:
 with suspend_csc_repairs():
  bpy.ops.wm.open_mainfile(filepath=str(O/'CSC_Level_2_Modern_Assembly.blend'),load_ui=False,use_scripts=False)
  for o in list(bpy.data.objects):
   if o.type=='MESH' and o.get('module')!=group:bpy.data.objects.remove(o,do_unlink=True)
  rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');rig.name=ident;rig.data.name=ident
  for scene in (bpy.data.scenes['Review'],bpy.data.scenes['Export']):scene['asset_id']=ident
  for o in bpy.data.scenes['Export'].objects:
   if o.type!='MESH':continue
   o['source_asset_id']=ident
   for j,d in enumerate(o.data.uv_layers[2].data):d.uv=o.data.uv_layers[0].data[j].uv if 'Window' in o.name else (.02,.02)
  for im in list(bpy.data.images):
   if im.users==0:bpy.data.images.remove(im)
   elif im.source=='FILE':im.filepath='//textures/'+im.filepath.replace('\\','/').split('/')[-1]
  bpy.context.window.scene=bpy.data.scenes['Review'];bpy.ops.wm.save_as_mainfile(filepath=str(D/(ident+'.blend')),relative_remap=False)
  bpy.ops.wm.open_mainfile(filepath=str(D/(ident+'.blend')),load_ui=False,use_scripts=False)
  report=validate_current_scene();(D/(ident+'-validation.json')).write_text(json.dumps(report,indent=2));assert report['automated_pass'],report['findings']
  bpy.context.window.scene=bpy.data.scenes['Export'];bpy.context.view_layer.update()
  model={'asset_id':ident,'kind':'building','meshes':[dec.merge_meshes(ident,[dec.decode_mesh(o,o.matrix_world) for o in bpy.context.scene.objects if o.type=='MESH'])]}
  (O/'models'/(ident+'.json')).write_text(json.dumps(model));count=sum(len(m['vertices']) for m in model['meshes']);tris=sum(len(m['triangles']) for m in model['meshes'])
  records.append({'id':ident,'blend':str(D/(ident+'.blend')),'vertices':count,'triangles':tris,'validation_errors':report['error_count']})
(O/'masters.json').write_text(json.dumps(records,indent=2));print('MASTERS',json.dumps(records),flush=True)
