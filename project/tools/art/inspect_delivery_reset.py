"""Measure the bay wall and cargo in the unplaced storage coordinate frame."""
import bpy,json
from pathlib import Path
from mathutils import Matrix
BASE=Path(r'C:\Users\Shadow\Desktop\Codex\CSC_Storage_L')
bpy.ops.wm.open_mainfile(filepath=str(BASE/'delivery-01/CSC_TAILORS_Storage_Delivery.blend'))
s=bpy.data.scenes['Review'];bpy.context.window.scene=s;s.frame_set(1261)
inv=Matrix(json.loads((BASE/'delivery-refit-20261009/source-refit-check.json').read_text())['new_building_transform']).inverted()
building=bpy.data.objects['CSC_Storage_L_Bldg'];rig=bpy.data.objects['CSC_Storage_Crane_Rig']
pts=[inv@building.matrix_world@v.co for v in building.data.vertices]
faces=[]
for p in building.data.polygons:
 v=[pts[i] for i in p.vertices]
 if max(x.x for x in v)<-30 and max(x.z for x in v)>44:
  faces.append({'index':p.index,'verts':[list(x) for x in v]})
bale=next(o for o in bpy.data.scenes['Export'].objects if o.type=='MESH' and 'Textile_Bale' in o.name)
rows=[]
for f in (841,1261,1321,1366,1381,1411):
 s.frame_set(f);e=bale.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();v=[inv@e.matrix_world@x.co for x in m.vertices];e.to_mesh_clear()
 rows.append({'frame':f,'cargo_local':list(inv@(rig.matrix_world@rig.pose.bones['Cargo'].matrix).translation),'bounds':[[min(x[i] for x in v) for i in range(3)],[max(x[i] for x in v) for i in range(3)]]})
print(json.dumps({'faces':faces,'poses':rows}))
