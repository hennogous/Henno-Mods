"""Measure actual historical horizontal outline in its local main-house frame."""
import bpy,sys,json,math
import numpy as np
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];O=Path.home()/'Desktop/Codex/modern-bakery-v2-20261028';ART=Path.home()/'Desktop/Working Files/3D Art'
sys.path.insert(0,str(ROOT/'project/tools/blender'));from csc_scene_validation import suspend_csc_repairs
with suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(ART/'Level 2/CSC_Level_2.blend'),load_ui=False,use_scripts=False)
ob=next(o for o in bpy.data.scenes['Export'].objects if o.type=='MESH');v=np.array([tuple(ob.matrix_world@p.co) for p in ob.data.vertices]);roof=v[v[:,2]>65,:2]
best=None
for angle in np.linspace(0,math.pi/2,901):
 c,s=math.cos(angle),math.sin(angle);R=np.array([[c,-s],[s,c]]);p=roof@R.T;span=p.max(0)-p.min(0);area=np.prod(span)
 if best is None or area<best[0]:best=(area,angle,R,p.min(0),p.max(0))
area,angle,R,lo,hi=best;centre=(lo+hi)/2;pts=v[:,:2]@R.T-centre
faces=[]
for poly in ob.data.polygons:
 if max(v[i,2] for i in poly.vertices)>=0:faces.append([pts[i].tolist() for i in poly.vertices])
report={'normalizing_rotation_degrees':math.degrees(angle),'roof_outline_dimensions':(hi-lo).tolist(),'full_outline_min':pts.min(0).tolist(),'full_outline_max':pts.max(0).tolist(),'normalizing_translation':centre.tolist(),'faces':faces,'source_height':float(v[:,2].max()),'scope':'Measured historical outline in fitted main-roof frame; no source transforms changed.'}
with suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(ART/'TAILORS/Tailor/revision-10-vertex-budget/CSC_TAILORS_Tailor_LeanTo.blend'),load_ui=False,use_scripts=False)
bpy.context.window.scene=bpy.data.scenes['Export'];bpy.context.view_layer.update();lean=[];leanpts=[]
from mathutils import Matrix,Vector
placed=Matrix.Translation(Vector((-188.45192680,-52.59447072,0)))@Matrix.Rotation(.203275,4,'Z')
for ob in bpy.context.scene.objects:
 if ob.type=='MESH':
  vs=np.array([tuple(placed@ob.matrix_world@p.co) for p in ob.data.vertices]);q=vs[:,:2]@R.T-centre;leanpts.extend(q.tolist())
  for p in ob.data.polygons:lean.append([q[i].tolist() for i in p.vertices])
report['historical_lean_to_faces']=lean
if leanpts:report['lean_to_bounds']=[np.min(leanpts,axis=0).tolist(),np.max(leanpts,axis=0).tolist()]
report['scope']='Historical reusable main plus authored Tailor lean-to in fitted main-roof frame; rigid normalization only, no scale fit.'
(O/'historical-footprint.json').write_text(json.dumps(report));print({k:x for k,x in report.items() if k not in ('faces','historical_lean_to_faces')})
