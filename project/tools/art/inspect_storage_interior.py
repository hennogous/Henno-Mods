"""Read current storage and older shells without modifying their sources."""
import bpy,json
from pathlib import Path
ROOT=Path(r'C:\Users\Shadow\Desktop\Working Files\3D Art\Storage\Storage_L')
OUT=Path(r'C:\Users\Shadow\Desktop\Codex\CSC_Storage_L\interior-20261008');OUT.mkdir(parents=True,exist_ok=True)
names=['CSC_Storage_L.blend','CSC_Storage_L_CON+PIL.blend','CSC_Storage_L.pre-ao.blend','CSC_Storage_L_pre_medium_shape_2026-10-07.blend','CSC_Storage_L_before_rig_20261008-114851.blend']
for filename in names:
 bpy.ops.wm.open_mainfile(filepath=str(ROOT/filename));result={'file':filename,'scenes':[{ 'name':s.name,'props':dict(s.items())} for s in bpy.data.scenes],'objects':[]}
 for o in bpy.data.objects:
  row={'name':o.name,'type':o.type,'matrix':[list(r) for r in o.matrix_world],'props':dict(o.items()),'parent':o.parent.name if o.parent else None}
  if o.type=='MESH':
   mesh=o.data;parent=list(range(len(mesh.vertices)))
   def find(i):
    while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
    return i
   for e in mesh.edges:
    a,b=map(find,e.vertices);parent[a]=b
   comps={}
   for p in mesh.polygons:comps.setdefault(find(p.vertices[0]),[]).append(p.index)
   components=[]
   for fs in comps.values():
    vs=sorted({v for f in fs for v in mesh.polygons[f].vertices});points=[mesh.vertices[v].co for v in vs]
    components.append({'faces':fs,'vertices':vs,'bounds':[[min(v[i] for v in points) for i in range(3)],[max(v[i] for v in points) for i in range(3)]]})
   row.update(vertices=[list(v.co) for v in mesh.vertices],faces=[list(p.vertices) for p in mesh.polygons],normals=[list(p.normal) for p in mesh.polygons],uvs={u.name:[[list(u.data[i].uv) for i in p.loop_indices] for p in mesh.polygons] for u in mesh.uv_layers},materials=[m.name if m else None for m in mesh.materials],groups=[g.name for g in o.vertex_groups],components=components)
  result['objects'].append(row)
 result['images']=[{'name':i.name,'path':bpy.path.abspath(i.filepath)} for i in bpy.data.images if i.source=='FILE']
 (OUT/(filename+'.json')).write_text(json.dumps(result,indent=2,default=str))
 print(filename,[(o['name'],len(o.get('vertices',[])),len(o.get('components',[]))) for o in result['objects']],flush=True)
print('INTERIOR_INSPECTED')
