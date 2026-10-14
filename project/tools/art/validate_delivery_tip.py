"""Verify both optional sack motion and existing bale lift against the shell."""
import bpy,json,sys,math
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
sys.path.insert(0,str(Path(__file__).resolve().parent))
from delivery_cargo_motion import TIP_BONE
BASE=Path(r'C:\Users\Shadow\Desktop\Codex\CSC_Storage_L');OUT=BASE/'delivery-reset-20261010'
bpy.ops.wm.open_mainfile(filepath=str(BASE/'delivery-01/CSC_TAILORS_Storage_Delivery.blend'))
s=bpy.data.scenes['Review'];bpy.context.window.scene=s
rig=bpy.data.objects['CSC_Storage_Crane_Rig'];sack=bpy.data.objects['REVIEW_Closed_Sack_TipUpright'];sack.hide_set(False)
building=bpy.data.objects['CSC_Storage_L_Bldg'];bale=next(o for o in bpy.data.scenes['Export'].objects if o.type=='MESH' and 'Textile_Bale' in o.name)
def geometry(o):
 e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();v=[e.matrix_world@p.co for p in m.vertices];tree=BVHTree.FromPolygons(v,[list(p.vertices) for p in m.polygons]);e.to_mesh_clear();return v,tree
s.frame_set(1261);_,wall=geometry(building);hits=[];support_error=0;angles={}
for f in range(841,1367):
 s.frame_set(f);cargo=rig.matrix_world@rig.pose.bones['Cargo'].matrix;tip=rig.matrix_world@rig.pose.bones[TIP_BONE].matrix
 for o in (sack,bale):
  v,tree=geometry(o)
  if wall.overlap(tree):hits.append({'frame':f,'object':o.name})
  if o==sack:support_error=max(support_error,abs(min(p.z for p in v)-cargo.translation.z))
 if f in (841,886,931,1261):angles[f]=math.degrees((cargo.inverted()@tip).to_quaternion().angle)
assert not hits,hits
assert support_error<.001,support_error
assert abs(angles[841]-90)<.01 and abs(angles[931])<.01,angles
result={'collisions':hits,'base_height_error':support_error,'relative_angles_degrees':angles,'frames_checked':526,'sack_attachment_scale':1.0}
(OUT/'tip-clearance-check.json').write_text(json.dumps(result,indent=2));print('TIP_CLEARANCE_PASS',json.dumps(result))
