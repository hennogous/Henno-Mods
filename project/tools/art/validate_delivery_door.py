"""Measure the moving meshes as they cross the actual workshop door plane."""
import bpy,json,math,sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
OUT=Path(r'C:\Users\Shadow\Desktop\Codex\CSC_Storage_L\delivery-01')
for event in ('load_post','depsgraph_update_post'):
 for cb in list(getattr(bpy.app.handlers,event)):
  if cb.__module__.rsplit('.',1)[-1]=='csc_scene_tools':getattr(bpy.app.handlers,event).remove(cb)
bpy.ops.wm.open_mainfile(filepath=str(OUT/'CSC_TAILORS_Storage_Delivery.blend'))
s=bpy.data.scenes['Export'];bpy.context.window.scene=s
door=Vector((-22.361,-189.7365,0));normal=Vector((.742,.670,0)).normalized();side=Vector((normal.y,-normal.x,0))
rig=bpy.data.objects['CSC_Storage_Crane_Rig'];dm=bpy.data.objects['CSC_Delivery_Donkey_Mesh']
bale=next(o for o in s.objects if o.type=='MESH' and 'Textile_Bale' in o.name)
rows=[];late=[]
if '--pose-probe' in sys.argv:
 sys.path.insert(0,str(Path(__file__).resolve().parent))
 from delivery_pose_adjustments import RecordedRoute,adjust_pose
 author=json.loads((OUT/'authoring-check.json').read_text())
 routes={k:RecordedRoute(author['route_centerlines'][k],author['body_scale']) for k in ('outbound','return')}
 donkey=bpy.data.objects['CSC_Delivery_Donkey_Rig']
workshop=bpy.data.objects['CSC_TAILORS_Textile_Workshop_Bldg']
wp=[workshop.matrix_world@v.co for v in workshop.data.vertices]
# Henno will remove the low threshold; validate the retained frame and arch.
front=[list(p.vertices) for p in workshop.data.polygons if all(-2<(wp[i]-door).dot(normal)<13 for i in p.vertices) and max(wp[i].z for i in p.vertices)>1.0]
wall=BVHTree.FromPolygons(wp,front);wall_hits=[]
for f in list(range(1,301,2))+list(range(1441,1742,2)):
 s.frame_set(f)
 if '--pose-probe' in sys.argv:
  t=(f-1)/30;route=routes['outbound'] if t<24 else routes['return'];fraction=(t-2)/22 if t<24 else (t-33)/25
  pos,theta=route.sample(fraction);before=donkey.matrix_world@donkey.pose.bones['Cart'].matrix
  cargo=rig.matrix_world@rig.pose.bones['Cargo'].matrix
  adjust_pose(donkey,pos,theta,author['body_scale'],route,fraction,door,normal);bpy.context.view_layer.update()
  if t<24:rig.pose.bones['Cargo'].matrix=rig.matrix_world.inverted()@(donkey.matrix_world@donkey.pose.bones['Cart'].matrix)@before.inverted()@cargo
  bpy.context.view_layer.update()
 dg=bpy.context.evaluated_depsgraph_get()
 for o in (dm,bale) if f<301 else (dm,):
  e=o.evaluated_get(dg);m=e.to_mesh();pts=[e.matrix_world@v.co for v in m.vertices]
  depths=[(p-door).dot(normal) for p in pts];crossings=[]
  for edge in m.edges:
   a,b=edge.vertices;da,db=depths[a],depths[b]
   if da*db<0:
    p=pts[a].lerp(pts[b],da/(da-db));lateral=(p-door).dot(side)
    if abs(lateral)<30:crossings.append([lateral,p.z])
  if crossings:rows.append({'frame':f,'mesh':o.name,'lateral':[min(p[0] for p in crossings),max(p[0] for p in crossings)],'height':max(p[1] for p in crossings)})
  body=BVHTree.FromPolygons(pts,[list(p.vertices) for p in m.polygons])
  hits=wall.overlap(body)
  if hits:
   groups=set()
   for wi,pi in hits:
    for vi in m.polygons[pi].vertices:
     for g in o.data.vertices[vi].groups:
      if g.weight>.2:groups.add(o.vertex_groups[g.group].name)
   wallz=[wp[vi].z for wi,pi in hits for vi in front[wi]]
   wall_hits.append({'frame':f,'mesh':o.name,'intersections':len(hits),'groups':sorted(groups),'wall_z':[min(wallz),max(wallz)]})
  if o==dm and f>=1711:late.append({'frame':f,'minimum_depth':min(depths),'scale':list(e.matrix_world.to_scale()),'yaw':e.matrix_world.to_euler().z})
  e.to_mesh_clear()
result={'door_center':list(door),'door_width':18.0,'crossings':rows,'end_of_return':late,'front_wall_intersections':wall_hits,'front_wall_polygons':len(front)}
(OUT/'door-clearance-check.json').write_text(json.dumps(result,indent=2))
# The wider approach crosses the infinite facade plane again along the road.
# Actual doorway/arch surfaces, rather than that infinite plane, decide contact.
assert rows and any(r['lateral'][0]<9 and r['lateral'][1]>-9 for r in rows),rows
assert all(r['minimum_depth']>0 for r in late if r['frame']>=1727),late
assert front and not wall_hits,wall_hits
(OUT/'door-clearance-check.json').write_text(json.dumps(result,indent=2));print('DOOR_CLEARANCE_PASS',json.dumps(result))
