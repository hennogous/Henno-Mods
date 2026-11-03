import bpy,json,sys
from pathlib import Path
from mathutils import Matrix
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'project/tools/blender'))
from csc_scene_validation import suspend_csc_repairs
A=Path.home()/'Desktop/Working Files/3D Art';O=Path.home()/'Desktop/Codex/modern-l2-states-20261029';O.mkdir(parents=True,exist_ok=True)
T=Matrix(json.loads((Path.home()/'Desktop/Codex/modern-bakery-ae-20261028/registration.json').read_text())['matrix']);rows={}
for label,p in [('worked',A/'Level 2/modern/revision-06-ae/CSC_Level_2_Modern.blend'),('historical_state',A/'Level 2/CSC_Level_2_CON+PIL.blend')]:
 with suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(p),load_ui=False,use_scripts=False)
 records=[]
 for o in bpy.data.objects:
  if o.type!='MESH':continue
  pts=[T.inverted()@o.matrix_world@v.co for v in o.data.vertices]
  records.append({'name':o.name,'verts':len(pts),'bounds':[[min(v[i] for v in pts) for i in range(3)],[max(v[i] for v in pts) for i in range(3)]],'materials':[m.name if m else None for m in o.data.materials],'scenes':[s.name for s in o.users_scene]})
 rows[label]=records
(O/'inspection.json').write_text(json.dumps(rows,indent=2))
print(json.dumps(rows))
