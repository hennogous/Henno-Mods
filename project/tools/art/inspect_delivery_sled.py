"""Compare donor topology with the cargo-removal selection, without editing it."""
import bpy, json
from pathlib import Path
OUT=Path(r'C:\Users\Shadow\Desktop\Codex\CSC_Storage_L\delivery-01')
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\Shadow\Desktop\Codex\Civ6-animation-research-20261007\IMP_Mine_AN_Sledge_Geo-animation-study.blend')
o=next(o for o in bpy.data.objects if o.type=='MESH');m=o.data
cart=o.vertex_groups['Cart'].index
removed={v.index for v in m.vertices if any(g.group==cart and g.weight>.5 for g in v.groups)}
def bb(ids):
 p=[m.vertices[i].co for i in ids]
 return [[round(min(v[j] for v in p),4) for j in range(3)],[round(max(v[j] for v in p),4) for j in range(3)]]
groups={g.index:g.name for g in o.vertex_groups}
adj={v.index:set() for v in m.vertices}
# Join coincident seams for structural component diagnostics.
positions={}
for v in m.vertices:positions.setdefault(tuple(round(x,4) for x in v.co),[]).append(v.index)
for ids in positions.values():
 for i in ids:adj[i].update(ids)
for e in m.edges:
 a,b=e.vertices;adj[a].add(b);adj[b].add(a)
todo=set(adj);components=[]
while todo:
 stack=[todo.pop()];ids=set(stack)
 while stack:
  for n in adj[stack.pop()]-ids:
   ids.add(n);todo.discard(n);stack.append(n)
 faces=[p for p in m.polygons if p.vertices[0] in ids]
 components.append({'bounds':bb(ids),'vertices':len(ids),'faces':len(faces),'deleted_vertices':len(ids&removed),
 'deleted_faces':sum(bool(set(p.vertices)&removed) for p in faces),
 'groups':sorted({groups[g.group] for i in ids for g in m.vertices[i].groups if g.weight>.1}),
 'face_indices':[p.index for p in faces]})
mixed=[]
for p in m.polygons:
 if set(p.vertices)&removed and set(p.vertices)-removed:
  mixed.append({'face':p.index,'bounds':bb(p.vertices),'vertices':list(p.vertices),
   'weights':[[[groups[g.group],round(g.weight,4)] for g in m.vertices[i].groups if g.weight>.01] for i in p.vertices]})
data={'mesh':o.name,'vertices':len(m.vertices),'faces':len(m.polygons),'components':components,'mixed_deleted_faces':mixed}
(OUT/'sled-topology-inspection.json').write_text(json.dumps(data,indent=2))
print(json.dumps(data))
