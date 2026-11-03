"""Rigidly register centered review geometry to the historical L2 district frame."""
import bpy,sys,json,math
from pathlib import Path
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[4];O=Path.home()/'Desktop/Codex/modern-bakery-ae-20261028'
sys.path[:0]=[str(ROOT/'project/tools/blender'),str(ROOT/'project/tools/blender/scene_export')]
from csc_scene_validation import suspend_csc_repairs,validate_current_scene
import decode_blend as dec
f=json.loads((Path.home()/'Desktop/Codex/modern-bakery-v2-20261028/historical-footprint.json').read_text());c=f['normalizing_translation'];angle=math.radians(f['normalizing_rotation_degrees'])
T=Matrix.Rotation(-angle,4,'Z')@Matrix.Translation(Vector((c[0],c[1],0)))
assert not (O/'registration.json').exists(),'Registration already applied'
rows=json.loads((O/'masters.json').read_text());report=[]
for row in rows:
 if row['group'] not in ('Building','Workshop'):continue
 path=Path(row['blend'])
 with suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
 for ob in bpy.data.scenes['Export'].objects:
  if ob.type=='MESH':ob.data.transform(T@ob.matrix_world);ob.matrix_world=Matrix.Identity(4)
 for ob in bpy.data.objects:
  if ob.type in ('CAMERA','LIGHT'):ob.matrix_world=T@ob.matrix_world
 bpy.ops.wm.save_as_mainfile(filepath=str(path))
 with suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
 v=validate_current_scene();path.with_name(path.stem+'-validation.json').write_text(json.dumps(v,indent=2));assert v['automated_pass']
 bpy.context.window.scene=bpy.data.scenes['Export'];bpy.context.view_layer.update()
 m={'asset_id':row['id'],'kind':'building','meshes':[dec.merge_meshes(row['id'],[dec.decode_mesh(ob,ob.matrix_world) for ob in bpy.context.scene.objects if ob.type=='MESH'])]}
 removed=0
 for mesh in m['meshes']:
  for mat in mesh['materials']:mat['external']='CSC_BAKERS_Modern'
  keep=[]
  for tr in mesh['triangles']:
   a,b,c=[Vector(mesh['vertices'][k][:3]) for k in tr[:3]]
   if (b-a).cross(c-a).length<1e-7:removed+=1
   else:keep.append(tr)
  mesh['triangles']=keep
 (O/'models'/(row['id']+'.json')).write_text(json.dumps(m));row['triangles']=sum(len(m['triangles']) for m in m['meshes']);report.append({'id':row['id'],'omitted_zero_area_triangles':removed})
placements=json.loads((O/'placements.json').read_text())
for group,p in placements.items():
 p['position']=list(T@Vector(p['position']));p['rotation_degrees'][2]-=math.degrees(angle)
(O/'placements.json').write_text(json.dumps(placements,indent=2))
folder=next(Path(r['blend']).parent for r in rows if r['group']=='Truck')
for path in folder.glob('*Review.blend'):
 with suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
 for ob in bpy.data.objects:
  if ob.type in ('MESH','CAMERA','LIGHT'):ob.matrix_world=T@ob.matrix_world
 bpy.ops.wm.save_as_mainfile(filepath=str(path))
(O/'masters.json').write_text(json.dumps(rows,indent=2));(O/'registration.json').write_text(json.dumps({'matrix':[list(r) for r in T],'source':'Inverse of historical L2 roof-frame normalization; no scale changes','models':report},indent=2));print('REGISTERED_TO_HISTORICAL_L2',flush=True)
