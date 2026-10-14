"""Check saved deck alignment through the whole loop and preservation of the source."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
BASE=Path(r'C:\Users\Shadow\Desktop\Codex\CSC_Storage_L');DEL=BASE/'delivery-01';OUT=BASE/'delivery-deck-20261010'
bpy.ops.wm.open_mainfile(filepath=str(DEL/'CSC_TAILORS_Storage_Delivery.blend'))
s=bpy.data.scenes['Export'];bpy.context.window.scene=s;dm=bpy.data.objects['CSC_Delivery_Donkey_Mesh']
ids=list(range(len(dm.data.vertices)-8,len(dm.data.vertices)))
references=[((8.6384773,-11.3072796,9.8199825),(39.6330719,-13.3300200,4.2172370)),((9.4621506,.7725677,9.7981892),(40.4145508,-1.2952501,4.1955452))]
edges=[[min(range(len(dm.data.vertices)-8),key=lambda i:(dm.data.vertices[i].co-Vector(p)).length_squared) for p in edge] for edge in references]
rows=[]
for f in range(31,1727,5):
 s.frame_set(f);e=dm.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();pts=[e.matrix_world@v.co for v in m.vertices];e.to_mesh_clear()
 d=pts[ids[4]]-pts[ids[0]];d.z=0;d.normalize()
 beam=Vector()
 for a,b in edges:
  v=pts[b]-pts[a];v.z=0;beam+=v.normalized()
 beam.normalize();angle=math.degrees(math.atan2(d.cross(beam).z,d.dot(beam)))
 rows.append({'frame':f,'yaw_error_degrees':abs(angle)})
maximum=max(r['yaw_error_degrees'] for r in rows)
print('DECK_MAX_YAW_ERROR',maximum)
def snapshot(o):
 return {'vertices':[tuple(v.co) for v in o.data.vertices],
 'weights':[[(o.vertex_groups[g.group].name,g.weight) for g in v.groups] for v in o.data.vertices],
 'faces':[list(p.vertices) for p in o.data.polygons],
 'uvs':[[tuple(p.uv) for p in layer.data] for layer in o.data.uv_layers]}
after=snapshot(dm)
with bpy.data.libraries.load(str(OUT/'before-deck-alignment/CSC_TAILORS_Storage_Delivery.blend'),link=False) as (a,b):b.objects=['CSC_Delivery_Donkey_Mesh']
old=b.objects[0];before=snapshot(old)
assert before['weights'][:-8]==after['weights'][:-8] and before['uvs']==after['uvs'] and before['faces']==after['faces']
assert all(len(weights)==2 and abs(dict(weights).get('Sledge_R',0)-.85)<1e-6 and abs(dict(weights).get('Cart',0)-.15)<1e-6 for weights in after['weights'][-8:])
assert before['vertices'][:-8]==after['vertices'][:-8]
result={'maximum_yaw_error_degrees':maximum,'sampled_poses':len(rows),'unchanged_original_vertices':len(before['vertices'])-8,'uvs_topology_and_original_weights_preserved':True,'deck_weights':{'Sledge_R':.85,'Cart':.15},'samples':rows}
(OUT/'deck-validation.json').write_text(json.dumps(result,indent=2))
assert maximum<.15,(maximum,sorted(rows,key=lambda r:r['yaw_error_degrees'],reverse=True)[:5])
print('DECK_VALIDATION_PASS',maximum)
