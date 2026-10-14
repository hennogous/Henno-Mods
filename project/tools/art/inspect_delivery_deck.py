"""Measure deck/runner alignment in rest space and evaluated delivery poses."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
BASE=Path(r'C:\Users\Shadow\Desktop\Codex\CSC_Storage_L');OUT=BASE/'delivery-deck-20261010';OUT.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(BASE/'delivery-01/CSC_TAILORS_Storage_Delivery.blend'))
s=bpy.data.scenes['Export'];bpy.context.window.scene=s
dm=bpy.data.objects['CSC_Delivery_Donkey_Mesh'];rig=bpy.data.objects['CSC_Delivery_Donkey_Rig']
deck=list(range(len(dm.data.vertices)-8,len(dm.data.vertices)))
edges=[]
for e in dm.data.edges:
 a,b=[dm.data.vertices[i].co for i in e.vertices];d=b-a
 if not any(i in deck for i in e.vertices) and abs(d.x)>10 and max(a.x,b.x)>10 and min(a.z,b.z)<10:
  edges.append(list(e.vertices))
def record(pts):
 def angle(d):return math.degrees(math.atan2(d.y,d.x))
 return {'deck':[list(pts[i]) for i in deck],
  'runner_edges':[{'ids':ab,'points':[list(pts[i]) for i in ab],'angle_xy':angle(pts[max(ab,key=lambda i:dm.data.vertices[i].co.x)]-pts[min(ab,key=lambda i:dm.data.vertices[i].co.x)])} for ab in edges]}
data={'deck_ids':deck,'rest':record([v.co for v in dm.data.vertices]),'poses':{}}
for f in (31,61,301,721,811,901,1081,1321):
 s.frame_set(f);e=dm.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();inv=rig.matrix_world.inverted()
 pts=[inv@e.matrix_world@v.co for v in m.vertices];e.to_mesh_clear();data['poses'][f]=record(pts)
data['deck_weights']=[[(dm.vertex_groups[g.group].name,g.weight) for g in dm.data.vertices[i].groups] for i in deck]
data['runner_weights']={i:[(dm.vertex_groups[g.group].name,g.weight) for g in dm.data.vertices[i].groups if g.weight>.0001] for i in (14,248,28,273)}
(OUT/'alignment-inspection.json').write_text(json.dumps(data,indent=2));print('RUNNER_WEIGHTS',json.dumps(data['runner_weights']))
