"""Search/check cargo slide clearance and occlusion during the underground reset."""
import bpy,json,math,sys
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
BASE=Path(r'C:\Users\Shadow\Desktop\Codex\CSC_Storage_L')
OUT=BASE/'delivery-reset-20261010';OUT.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(BASE/'delivery-01/CSC_TAILORS_Storage_Delivery.blend'))
s=bpy.data.scenes['Review'];bpy.context.window.scene=s
rig=bpy.data.objects['CSC_Storage_Crane_Rig'];building=bpy.data.objects['CSC_Storage_L_Bldg']
bale=next(o for o in bpy.data.scenes['Export'].objects if o.type=='MESH' and 'Textile_Bale' in o.name)
bone_name='Cargo'
if '--sack' in sys.argv:
 bale=bpy.data.objects['REVIEW_Closed_Sack_TipUpright'];bale.hide_set(False);bone_name='Cargo_TipUpright'
native=None
if '--native' in sys.argv:
 from civ6_animation import core
 native=core.parse_na2(BASE/'delivery-01/Master-sampled/clip.na2')[0]
def mesh(o):
 e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();m.calc_loop_triangles()
 pts=[e.matrix_world@v.co for v in m.vertices];tri=[list(t.vertices) for t in m.loop_triangles];e.to_mesh_clear();return pts,tri
s.frame_set(841);pickup=(rig.matrix_world@rig.pose.bones['Cargo'].matrix).translation.copy()
s.frame_set(1261);stored_pose=(rig.matrix_world@rig.pose.bones[bone_name].matrix).copy();stored=stored_pose.translation.copy()
v,tri=mesh(bale);wp,wt=mesh(building);wall=BVHTree.FromPolygons(wp,wt,all_triangles=True)
inside=stored-pickup;inside.z=0;inside.normalize();right=inside.cross(Vector((0,0,1))).normalized()
# Dense surface sampling, not just the origin or eight bounding-box corners.
surface=[]
for a,b,c in tri:
 for i in range(5):
  for j in range(5-i):surface.append(v[a]*(i/4)+v[b]*(j/4)+v[c]*(1-(i+j)/4))
views=[]
transform=Matrix(json.loads((BASE/'delivery-refit-20261009/source-refit-check.json').read_text())['new_building_transform'])
for elevation in (25,40,55):
 for yaw in range(145,216,5):
  a=math.radians(yaw);h=math.radians(elevation)
  views.append((transform.to_quaternion()@Vector((math.cos(a)*math.cos(h),math.sin(a)*math.cos(h),math.sin(h)))).normalized())
def visible_count(offset):
 count=0
 for p in surface:
  q=p+offset
  if q.z<=0:continue # terrain hides below-grade cargo
  for d in views:
   if wall.ray_cast(q+d*.002,d,1000)[0] is None:count+=1;break
 return count
if '--grid' in sys.argv:
 transform=Matrix(json.loads((BASE/'delivery-refit-20261009/source-refit-check.json').read_text())['new_building_transform']);inv=transform.inverted()
 local=inv@stored;rows=[]
 for x in (-23,-20,-18,-16,-13,-8,0):
  for y in (-30,-33,-36,-39,-42,-45,-48):
   target=transform@Vector((x,y,local.z));offset=target-stored
   collisions=sum(bool(wall.overlap(BVHTree.FromPolygons([p+offset*i/30 for p in v],tri,all_triangles=True))) for i in range(31))
   counts=[visible_count(offset+Vector((0,0,-(stored.z+100)*i/25))) for i in range(26)]
   rows.append({'local':[x,y],'visible':sum(counts),'start_visible':counts[0],'collisions':collisions,'target':list(target)})
 rows.sort(key=lambda r:r['visible']);(OUT/'grid-check.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows[:8]))
elif '--search' in sys.argv:
 rows=[]
 for distance in (20,24,28,32,36,40,44):
  offset=right*distance;collisions=[]
  for i in range(61):
   p=[x+offset*i/60 for x in v]
   if wall.overlap(BVHTree.FromPolygons(p,tri,all_triangles=True)):collisions.append(i)
  visible=[]
  for i in range(46):
   delta=offset+Vector((0,0,-(stored.z+100)*i/45))
   n=visible_count(delta)
   if n:visible.append({'step':i,'points':n})
  rows.append({'distance':distance,'slide_collisions':collisions,'visible_drop_steps':visible,'target':list(stored+offset)})
 (OUT/'candidate-check.json').write_text(json.dumps(rows,indent=2))
 print(json.dumps(rows))
else:
 # Actual final evaluated animation, one frame at a time through all reset motion.
 failures=[];slide_hits=[];trajectory=[]
 for f in range(1261,1742):
  s.frame_set(f)
  pose=(core.world_matrix(native['tracks'][bone_name][f-1]) if native else rig.matrix_world@rig.pose.bones[bone_name].matrix).translation
  offset=pose-stored
  if f<=1366:
   if wall.overlap(BVHTree.FromPolygons([p+offset for p in v],tri,all_triangles=True)):slide_hits.append(f)
  if 1366<=f<=1681:
   # Until the underground workshop rise, orientation is irrelevant below grade.
   n=visible_count(offset)
   if n:failures.append({'frame':f,'visible_surface_points':n})
  trajectory.append({'frame':f,'position':list(pose)})
 result={'slide_collisions':slide_hits,'visible_drop_frames':failures,'camera_azimuths':15,'camera_elevations':[25,40,55],
         'surface_samples':len(surface),'trajectory':trajectory,'scope':'All frames of slide/drop and underground return; terrain at z=0; long-side views within +/-35 degrees, 45 orthographic viewing directions.'}
 name=('native-' if native else '')+('sack-' if '--sack' in sys.argv else '')+'hidden-reset-check.json'
 (OUT/name).write_text(json.dumps(result,indent=2))
 assert not slide_hits and not failures,result
 print('HIDDEN_RESET_PASS',len(surface))
