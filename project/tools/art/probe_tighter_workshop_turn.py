"""Compare tighter workshop routes using the full-size carrier and retained doorway."""
import bpy,json,ast,math,bisect,sys
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
sys.path.insert(0,str(Path(__file__).resolve().parent))
from delivery_pose_adjustments import adjust_pose,smooth
OUT=Path(r'C:\Users\Shadow\Desktop\Codex\CSC_Storage_L\delivery-01');BODY_SCALE=1.0
bpy.ops.wm.open_mainfile(filepath=str(OUT/'CSC_TAILORS_Storage_Delivery.blend'))
s=bpy.data.scenes['Export'];bpy.context.window.scene=s
rig=bpy.data.objects['CSC_Storage_Crane_Rig'];donkey=bpy.data.objects['CSC_Delivery_Donkey_Rig'];dm=bpy.data.objects['CSC_Delivery_Donkey_Mesh']
bale=next(o for o in s.objects if o.type=='MESH' and 'Textile_Bale' in o.name)
code=Path(__file__).with_name('build_storage_delivery.py').read_text();node=next(n for n in ast.parse(code).body if isinstance(n,ast.ClassDef) and n.name=='Route')
exec(compile(ast.Module(body=[node],type_ignores=[]),'<Route>','exec'))
report=json.loads((OUT/'authoring-check.json').read_text());stop_theta=math.pi/2
stop=Vector(report['route_centerlines']['outbound'][-1])-Matrix.Rotation(stop_theta,3,'Z')@Vector((0,-5.2,0))
block=code[code.index(' # Measured outer jambs'):code.index(' start,angle_start=outbound.sample')];block='\n'.join(line[1:] for line in block.splitlines())
door=Vector((-22.361,-189.7365,0));normal=Vector((.742,.670,0)).normalized();side=Vector((normal.y,-normal.x,0))
workshop=bpy.data.objects['CSC_TAILORS_Textile_Workshop_Bldg'];verts=[workshop.matrix_world@v.co for v in workshop.data.vertices]
front=[list(p.vertices) for p in workshop.data.polygons if all(-2<(verts[i]-door).dot(normal)<13 for i in p.vertices) and max(verts[i].z for i in p.vertices)>1]
wall=BVHTree.FromPolygons(verts,front);results=[]
for depth,knots in [(44,[(-65,-217),(-71,-204),(-66,-187),(-60,-177)]),(48,[(-69,-220),(-75,-206),(-68,-189),(-61,-178)]),(51,[(-72,-222),(-78,-208),(-70,-191),(-62,-179)])]:
 candidate=block.replace('workshop_turn=[(-75,-225),(-83,-211),(-76,-192),(-64,-179)]','workshop_turn='+repr(knots))
 candidate=candidate.replace('(60,42,28,14,0,-14,-28,-42,-55)',repr((60,42,28,14,0,-14,-28,-depth))).replace('(-55,-42,-28,-14,0,14,28,42,60)',repr((-depth,-28,-14,0,14,28,42,60)))
 exec(candidate);hits=[]
 for f in list(range(65,302,2))+list(range(1441,1726,2)):
  s.frame_set(f);t=(f-1)/30;old=rig.matrix_world@rig.pose.bones['DonkeyPath'].matrix;cargo=rig.matrix_world@rig.pose.bones['Cargo'].matrix
  oldpos=old.translation;oldtheta=old.to_euler().z;head=oldpos+Matrix.Rotation(oldtheta,3,'Z')@Vector((-25,-5.2,29))
  duck=smooth((48-abs((head-door).dot(normal)))/17)*smooth((40-abs((head-door).dot(side)))/15)
  b=donkey.pose.bones['Neck'];m=b.matrix.copy();pivot=m.translation
  b.matrix=Matrix.Translation(pivot)@Matrix.Rotation(math.radians(42)*duck,4,'Y')@Matrix.Translation(-pivot)@m
  route=outbound if t<24 else inbound;u=(t-2)/22 if t<24 else (t-33)/25;pos,theta=route.sample(u)
  new=Matrix.Translation(pos)@Matrix.Rotation(theta,4,'Z');rig.pose.bones['DonkeyPath'].matrix=rig.matrix_world.inverted()@new
  if t<24:rig.pose.bones['Cargo'].matrix=rig.matrix_world.inverted()@new@old.inverted()@cargo
  bpy.context.view_layer.update();adjust_pose(donkey,pos,theta,1,route,u,door,normal);bpy.context.view_layer.update()
  dg=bpy.context.evaluated_depsgraph_get()
  for o in (dm,bale) if t<24 else (dm,):
   e=o.evaluated_get(dg);mesh=e.to_mesh();pts=[e.matrix_world@v.co for v in mesh.vertices]
   overlaps=wall.overlap(BVHTree.FromPolygons(pts,[list(p.vertices) for p in mesh.polygons]))
   if overlaps:hits.append([f,o.name,len(overlaps)])
   e.to_mesh_clear()
 result={'depth':depth,'knots':knots,'hits':hits,'outbound_length':outbound.length,'return_length':inbound.length};results.append(result);print(result,flush=True)
(OUT/'tighter-turn-probe.json').write_text(json.dumps(results,indent=2))
