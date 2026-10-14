"""Inventory current storage source before entrance-foundation edits."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
SOURCE=Path(r'C:\Users\Shadow\Desktop\Working Files\3D Art\Storage\Storage_L\CSC_Storage_L.blend')
OUT=Path(r'C:\Users\Shadow\Desktop\Codex\CSC_Storage_L\foundation-scale-20261009');OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
report={'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'scenes':[(s.name,[o.name for o in s.objects]) for s in bpy.data.scenes],'objects':[]}
for o in bpy.data.objects:
 row={'name':o.name,'type':o.type,'matrix':[list(r) for r in o.matrix_world],'parent':o.parent.name if o.parent else None,'props':dict(o.items())}
 if o.type=='MESH':
  m=o.data;adj={v.index:set() for v in m.vertices}
  for e in m.edges:
   a,b=e.vertices;adj[a].add(b);adj[b].add(a)
  unseen=set(adj);comps=[]
  while unseen:
   stack=[unseen.pop()];ids=set(stack)
   while stack:
    for i in adj[stack.pop()]-ids:ids.add(i);unseen.discard(i);stack.append(i)
   points=[m.vertices[i].co for i in ids]
   comps.append({'vertices':sorted(ids),'faces':[p.index for p in m.polygons if p.vertices[0] in ids],
     'bounds':[[min(p[j] for p in points) for j in range(3)],[max(p[j] for p in points) for j in range(3)]]})
  row.update(vertices=[list(v.co) for v in m.vertices],faces=[list(p.vertices) for p in m.polygons],normals=[list(p.normal) for p in m.polygons],
    materials=[mat.name if mat else None for mat in m.materials],uvs={uv.name:[[list(uv.data[i].uv) for i in p.loop_indices] for p in m.polygons] for uv in m.uv_layers},components=comps)
 report['objects'].append(row)
(OUT/'source.json').write_text(json.dumps(report,indent=2,default=str))
print(json.dumps({'scenes':report['scenes'],'objects':[{k:v for k,v in r.items() if k not in ('vertices','faces','normals','uvs','components')}|{'vertices':len(r.get('vertices',[])),'faces':len(r.get('faces',[])),'components':len(r.get('components',[]))} for r in report['objects']]},default=str))
