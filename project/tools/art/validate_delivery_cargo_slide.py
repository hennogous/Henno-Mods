"""Verify the visible loading-bay slide stays level and clear of the building."""
import bpy,json,sys
from pathlib import Path
from mathutils.bvhtree import BVHTree
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from delivery_cargo_motion import RESET_CORNER_XY
OUT=Path(r'C:\Users\Shadow\Desktop\Codex\CSC_Storage_L\delivery-01')
bpy.ops.wm.open_mainfile(filepath=str(OUT/'CSC_TAILORS_Storage_Delivery.blend'))
s=bpy.data.scenes['Review'];bpy.context.window.scene=s
rig=bpy.data.objects['CSC_Storage_Crane_Rig'];building=bpy.data.objects['CSC_Storage_L_Bldg']
bale=next(o for o in bpy.data.scenes['Export'].objects if o.type=='MESH' and 'Textile_Bale' in o.name)
def surface(o):
 e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh()
 v=[e.matrix_world@p.co for p in m.vertices];tree=BVHTree.FromPolygons(v,[list(p.vertices) for p in m.polygons]);e.to_mesh_clear();return tree
s.frame_set(1261);wall=surface(building);start=(rig.matrix_world@rig.pose.bones['Cargo'].matrix).copy()
rows=[]
for f in range(1261,1367):
 s.frame_set(f);pose=rig.matrix_world@rig.pose.bones['Cargo'].matrix
 rows.append({'frame':f,'position':list(pose.translation),'height_error':abs(pose.translation.z-start.translation.z),
  'rotation_error':pose.to_quaternion().rotation_difference(start.to_quaternion()).angle,'wall_intersections':len(wall.overlap(surface(bale)))})
end=pose.translation-start.translation
result={'slide_distance':end.length,'slide_vector':list(end),'samples':rows,'scope':'Continuous level rightward slide to the concealed drop corner.'}
(OUT/'cargo-slide-check.json').write_text(json.dumps(result,indent=2))
assert (pose.translation.xy-Vector(RESET_CORNER_XY)).length<.001,result
axis=end.normalized();progress=[(Vector(r['position'])-start.translation).dot(axis) for r in rows]
assert all(b>=a-.001 for a,b in zip(progress,progress[1:])),result
assert max(r['height_error'] for r in rows)<.001,result
assert max(r['rotation_error'] for r in rows)<.001,result
assert not any(r['wall_intersections'] for r in rows),result
print('CARGO_SLIDE_PASS')
