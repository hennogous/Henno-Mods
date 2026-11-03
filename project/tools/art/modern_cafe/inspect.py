import bpy,json,sys,math
from pathlib import Path
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT/'project/tools/blender'))
from csc_scene_validation import suspend_csc_repairs
A=Path.home()/'Desktop/Working Files/3D Art';O=Path.home()/'Desktop/Codex/modern-cafe-v1-20261029';O.mkdir(parents=True,exist_ok=True)
rows={}
for label,path in [('base',A/'Level 3/CSC_Level_3.blend'),('cafe',A/'BAKERS/Cafe/revision-01-fixed-counters/CSC_BAKERS_Cafe.blend')]:
 with suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
 records=[]
 for ob in bpy.data.objects:
  if ob.type!='MESH':continue
  pts=[ob.matrix_world@v.co for v in ob.data.vertices]
  records.append({'name':ob.name,'vertices':len(pts),'polygons':len(ob.data.polygons),'bounds':[[min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]],'matrix':[list(r) for r in ob.matrix_world],'materials':[m.name for m in ob.data.materials],'properties':dict(ob.items()),'scenes':[s.name for s in ob.users_scene]})
 rows[label]=records
 if label=='base':
  parts=[]
  for ob in bpy.data.objects:
   if ob.type!='MESH':continue
   # Component boundaries provide exact structural dimensions without guessing
   # the historical silhouette from the concept illustration.
   adj={v.index:set() for v in ob.data.vertices}
   for e in ob.data.edges:a,b=e.vertices;adj[a].add(b);adj[b].add(a)
   seen=set()
   for start in adj:
    if start in seen:continue
    pending=[start];comp=[];seen.add(start)
    while pending:
     i=pending.pop();comp.append(i)
     for j in adj[i]-seen:seen.add(j);pending.append(j)
    pts=[ob.matrix_world@ob.data.vertices[i].co for i in comp]
    parts.append({'object':ob.name,'verts':len(comp),'indices':comp,'bounds':[[min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]]})
  (O/'base-components.json').write_text(json.dumps(parts,indent=2))
(O/'inspection.json').write_text(json.dumps(rows,indent=2,default=str));print(json.dumps(rows,default=str))
