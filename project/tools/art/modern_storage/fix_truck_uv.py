"""UV-only split of the reused full front painting into grille and windscreen."""
import bpy,json,sys,hashlib,bmesh
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];O=Path.home()/'Desktop/Codex/modern-storage-v1-20261029';sys.path[:0]=[str(ROOT/'project/tools/blender'),str(ROOT/'project/tools/blender/scene_export')]
from csc_scene_validation import suspend_csc_repairs,validate_current_scene
import decode_blend as dec
records=json.loads((O/'masters.json').read_text());r=next(r for r in records if r['group']=='Truck');large=Path(next(r['blend'] for r in records if r['group']=='L')).parent
for path in (Path(r['blend']),large/'CSC_BAKERS_Storage_L_Modern_2_Review.blend'):
 with suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
 for ob in bpy.data.objects:
  if ob.type!='MESH' or ob.get('module')!='Truck':continue
  if 'Windscreen' not in ob.name and 'FrontPaint' not in ob.name:continue
  for k,(u,v) in enumerate(((0,0),(1,0),(1,1),(0,1))):
   u,v=(.10+.80*u,.60+.30*v) if 'Windscreen' in ob.name else (u,.02+.53*v);ob.data.uv_layers[0].data[k].uv=((3+u*122)/1024,1-(515+(1-v)*122)/1024)
 bpy.ops.wm.save_as_mainfile(filepath=str(path));result=validate_current_scene();assert result['automated_pass'],result['findings']
 if path==Path(r['blend']):
  bpy.context.window.scene=bpy.data.scenes['Export'];bpy.context.view_layer.update();ms=[dec.decode_mesh(ob,ob.matrix_world) for ob in bpy.context.scene.objects if ob.type=='MESH'];model={'asset_id':r['id'],'kind':'prop','meshes':[dec.merge_meshes(r['id'],ms)]}
  for m in model['meshes']:
   for ma in m['materials']:ma['external']=ma['name'].split('.')[0]
  (O/'models'/(r['id']+'.json')).write_text(json.dumps(model));r['sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
 else:
  s=bpy.data.scenes['Review'];bpy.context.window.scene=s
  for ob in s.objects:
   if ob.type=='MESH' and ob.get('module')=='L':
    ob.data=ob.data.copy();b=bmesh.new();b.from_mesh(ob.data);bmesh.ops.bisect_plane(b,geom=list(b.verts)+list(b.edges)+list(b.faces),plane_co=(0,0,0),plane_no=(0,0,1),clear_inner=True);b.to_mesh(ob.data);b.free()
  s.render.filepath=str(O/'review/L_Dispatch.png');bpy.ops.render.render(write_still=True)
(O/'masters.json').write_text(json.dumps(records,indent=2));print('TRUCK_UV_FIXED_NO_GEOMETRY_OR_AO_CHANGE',flush=True)
