"""Read-only candidate evaluation for original-size donkey doorway clearance."""
import bpy,json,ast,math,bisect,sys
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
OUT=Path(r'C:\Users\Shadow\Desktop\Codex\CSC_Storage_L\delivery-01')
BODY_SCALE=1.0
bpy.ops.wm.open_mainfile(filepath=str(OUT/'CSC_TAILORS_Storage_Delivery.blend'))
s=bpy.data.scenes['Export'];bpy.context.window.scene=s
rig=bpy.data.objects['CSC_Storage_Crane_Rig'];donkey=bpy.data.objects['CSC_Delivery_Donkey_Rig'];dm=bpy.data.objects['CSC_Delivery_Donkey_Mesh']
bale=next(o for o in s.objects if o.type=='MESH' and 'Textile_Bale' in o.name)
code=Path(__file__).with_name('build_storage_delivery.py').read_text()
node=next(n for n in ast.parse(code).body if isinstance(n,ast.ClassDef) and n.name=='Route')
exec(compile(ast.Module(body=[node],type_ignores=[]),'<Route>','exec'))
report=json.loads((OUT/'authoring-check.json').read_text());stop_theta=math.pi/2
stop=Vector(report['route_centerlines']['outbound'][-1])-Matrix.Rotation(stop_theta,3,'Z')@Vector((0,-5.2,0))
block=code[code.index(' # Measured outer jambs'):code.index(' start,angle_start=outbound.sample')]
block='\n'.join(line[1:] for line in block.splitlines())
door=Vector((-22.361,-189.7365,0));normal=Vector((.742,.670,0)).normalized();side=Vector((normal.y,-normal.x,0))
o=bpy.data.objects['CSC_TAILORS_Textile_Workshop_Bldg'];verts=[o.matrix_world@v.co for v in o.data.vertices]
front=[list(p.vertices) for p in o.data.polygons if all(-2<(verts[i]-door).dot(normal)<13 for i in p.vertices)]
wall=BVHTree.FromPolygons(verts,front)
results=[]
for shift in (0,):
 depth=55
 candidate=block.replace('(60,42,28,14,0,-14,-28)','(60,42,28,14,0,-14,-28,-42,-55)').replace('(-28,-14,0,14,28,42,60)','(-55,-42,-28,-14,0,14,28,42,60)')
 candidate=candidate.replace('workshop_turn=[(-46,-204),(-48,-195),(-51,-185),(-54,-176)]','workshop_turn=[(-75,-225),(-83,-211),(-76,-192),(-64,-179)]')
 candidate=candidate.replace('door+inward*depth','door+inward*depth+Vector((inward.y,-inward.x,0))*('+str(shift)+' if outgoing else -'+str(shift)+')')
 exec(candidate)
 hits=[];max_side=0
 for f in list(range(65,302,2))+list(range(1441,1742,2)):
  s.frame_set(f);t=(f-1)/30;route=outbound if t<24 else inbound;u=(t-2)/22 if t<24 else (t-33)/25
  pos,theta=route.sample(u);old=rig.matrix_world@rig.pose.bones['DonkeyPath'].matrix;cargo=rig.matrix_world@rig.pose.bones['Cargo'].matrix
  new=Matrix.Translation(pos)@Matrix.Rotation(theta,4,'Z');rig.pose.bones['DonkeyPath'].matrix=rig.matrix_world.inverted()@new
  if t<24:rig.pose.bones['Cargo'].matrix=rig.matrix_world.inverted()@new@old.inverted()@cargo
  bpy.context.view_layer.update()
  b=donkey.pose.bones['Neck'];m=b.matrix.copy();pivot=m.translation
  head=pos+Matrix.Rotation(theta,3,'Z')@Vector((-25,-5.2,29));dist=abs((head-door).dot(normal))
  duck=max(0,min(1,(48-dist)/17))
  b.matrix=Matrix.Translation(pivot)@Matrix.Rotation(-math.radians(42)*duck,4,'Y')@Matrix.Translation(-pivot)@m
  bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
  for o in (dm,bale) if t<24 else (dm,):
   e=o.evaluated_get(dg);mesh=e.to_mesh();pts=[e.matrix_world@v.co for v in mesh.vertices]
   overlaps=wall.overlap(BVHTree.FromPolygons(pts,[list(p.vertices) for p in mesh.polygons]))
   if overlaps:
    groups=set()
    for wi,pi in overlaps:
     for vi in mesh.polygons[pi].vertices:
      if o==dm:
       for g in dm.data.vertices[vi].groups:
        if g.weight>.2:groups.add(dm.vertex_groups[g.group].name)
    wallz=[verts[vi].z for wi,pi in overlaps for vi in front[wi]]
    hits.append([f,o.name,len(overlaps),sorted(groups),[min(wallz),max(wallz)]])
   for edge in mesh.edges:
    a,b=edge.vertices;da=(pts[a]-door).dot(normal);db=(pts[b]-door).dot(normal)
    if da*db<0:
     x=abs((pts[a].lerp(pts[b],da/(da-db))-door).dot(side))
     if x<30:max_side=max(max_side,x)
   e.to_mesh_clear()
 results.append({'depth':depth,'shift':shift,'hits':hits,'maximum_side':max_side});print(results[-1],flush=True)
(OUT/'full-size-door-probe.json').write_text(json.dumps(results,indent=2))
