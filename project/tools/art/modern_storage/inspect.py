"""Read-only storage source measurements for the modern family."""
import bpy,json,sys,collections
from pathlib import Path
from mathutils import Vector
A=Path.home()/'Desktop/Working Files/3D Art';O=Path.home()/'Desktop/Codex/modern-storage-v1-20261029';O.mkdir(parents=True,exist_ok=True)
records={}
for size in ('M','L'):
 p=A/f'Storage/Storage_{size}/CSC_Storage_{size}.blend'
 bpy.ops.wm.open_mainfile(filepath=str(p),load_ui=False,use_scripts=False)
 rows=[]
 for ob in bpy.data.objects:
  if ob.type!='MESH':continue
  pts=[ob.matrix_world@v.co for v in ob.data.vertices]
  rows.append({'name':ob.name,'scenes':[s.name for s in ob.users_scene],'bounds':[[min(v[i] for v in pts) for i in range(3)],[max(v[i] for v in pts) for i in range(3)]],'vertices':[list(v) for v in pts],'faces':[list(p.vertices) for p in ob.data.polygons],'materials':[m.name if m else None for m in ob.data.materials],'matrix':[list(r) for r in ob.matrix_world]})
 records[size]=rows
 print(size,[(r['name'],r['bounds'],len(r['vertices']),r['scenes']) for r in rows],flush=True)
(O/'historical-geometry.json').write_text(json.dumps(records))
for fam in ('CSC_Buildings_Modern','CSC_Props_Modern','CSC_Buildings_Emissive'):
 folder=A/'Textures'/fam
 for fn in ('CURRENT.json','Current/library.json'):
  p=folder/fn
  if p.exists(): print(fam,fn,p.read_text()[:1800],flush=True)
