"""Measure current crane, resized storage and delivery handoff before refitting."""
import bpy,json
from pathlib import Path
from mathutils import Vector
BASE=Path(r'C:\Users\Shadow\Desktop\Codex\CSC_Storage_L')
OUT=BASE/'delivery-refit-20261009';OUT.mkdir(exist_ok=True)
ROOT=Path(r'C:\Users\Shadow\Desktop\Working Files\3D Art\Storage\Storage_L')
paths={'crane':ROOT/'CSC_Storage_L_Crane.blend','building':ROOT/'CSC_Storage_L.blend',
       'delivery':BASE/'delivery-01/CSC_TAILORS_Storage_Delivery.blend'}
report={}
for label,path in paths.items():
 bpy.ops.wm.open_mainfile(filepath=str(path));bpy.context.window.scene=bpy.data.scenes['Review']
 scene=bpy.context.scene;rows=[]
 for o in scene.objects:
  if o.type not in ('ARMATURE','EMPTY','MESH'):continue
  row={'name':o.name,'type':o.type,'parent':o.parent.name if o.parent else None,'parent_bone':o.parent_bone,
       'matrix':[list(r) for r in o.matrix_world],'props':dict(o.items())}
  if o.type=='MESH':
   pts=[o.matrix_world@v.co for v in o.data.vertices]
   row.update(vertices=len(pts),bounds=[[min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]])
  rows.append(row)
 poses={}
 rigs=[o for o in scene.objects if o.type=='ARMATURE' and 'Crane' in o.name]
 for f in ([1,151,291,321] if label=='crane' else [1,721,841,1261]):
  scene.frame_set(f);bpy.context.view_layer.update()
  poses[f]={o.name:{b.name:[list(r) for r in o.matrix_world@b.matrix] for b in o.pose.bones} for o in rigs}
 report[label]={'objects':rows,'poses':poses}
(OUT/'source-measurements.json').write_text(json.dumps(report,indent=2,default=str))
print('REFIT_MEASUREMENTS_SAVED')
