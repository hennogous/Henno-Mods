"""Replace boxed window recesses with a continuous upper room; preserve exterior corners."""
import bpy,json,math,hashlib,shutil,sys
from pathlib import Path
from mathutils import Matrix,Vector
ROOT=Path(r'C:\Users\Shadow\Desktop\Working Files\3D Art\Storage\Storage_L')
OUT=Path(r'C:\Users\Shadow\Desktop\Codex\CSC_Storage_L\interior-20261008')
SOURCE=ROOT/'CSC_Storage_L.blend';STAGE=OUT/'CSC_Storage_L_Interior.blend'
for event in ('load_post','depsgraph_update_post'):
 for cb in list(getattr(bpy.app.handlers,event)):
  if cb.__module__.rsplit('.',1)[-1]=='csc_scene_tools':getattr(bpy.app.handlers,event).remove(cb)
old=json.loads((OUT/'CSC_Storage_L_before_rig_20261008-114851.blend.json').read_text())
M=Matrix(json.loads((OUT/'source-transform.json').read_text())['matrix']);inv=M.inverted()
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));obj=bpy.data.objects['CSC_Storage_L_Bldg'];mesh=obj.data
source_hash=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
def signature(points):return tuple(sorted(tuple(round(x,3) for x in p) for p in points))
lookup={signature([v.co for v in [mesh.vertices[i] for i in p.vertices]]):p.index for p in mesh.polygons}
old_objects={o['name']:o for o in old['objects'] if o['type']=='MESH'}
removed=[]
for name in ('Front_Loading_Interior','Left_Wing_Loading_Interior','Right_Window_Interior'):
 o=old_objects['CSC_Fixed_'+name]
 for face in o['faces']:
  key=signature([M@Vector(o['vertices'][i]) for i in face]);assert key in lookup,(name,key)
  removed.append(lookup[key])
assert len(set(removed))==12
slots=[]
allocation=json.loads((OUT/'ao-allocation.json').read_text());resolution=allocation['size']
for x,y,w,h in allocation['chart_rects_pixels_uv_origin']:
 slots.append(((x+2)/resolution,(x+w-2)/resolution,(y+2)/resolution,(y+h-2)/resolution))
floor_uv=[mesh.uv_layers['UV1'].data[i].uv.copy() for i in mesh.polygons[removed[4]].loop_indices]
wood=(min(p.x for p in floor_uv),max(p.x for p in floor_uv),min(p.y for p in floor_uv),max(p.y for p in floor_uv))
uvnames=[u.name for u in mesh.uv_layers];assert uvnames==['UV1','UV2','UV3']
retained=[p for p in mesh.polygons if p.index not in removed]
used=sorted({i for p in retained for i in p.vertices});remap={v:i for i,v in enumerate(used)}
vertices=[mesh.vertices[i].co.copy() for i in used]
weights=[[(g.group,g.weight) for g in mesh.vertices[i].groups] for i in used]
faces=[];uvdata=[];materials=[];smooth=[];normals=[];parts=[]
for p in retained:
 faces.append([remap[i] for i in p.vertices]);uvdata.append([[tuple(layer.data[i].uv) for i in p.loop_indices] for layer in mesh.uv_layers]);materials.append(p.material_index);smooth.append(p.use_smooth)
 normals.append([tuple(mesh.corner_normals[i].vector) for i in p.loop_indices]);parts.append(0)
original_corners=[(tuple(tuple(vertices[i]) for i in f),uv) for f,uv in zip(faces,uvdata)]
group_names=[g.name for g in obj.vertex_groups]
root=obj.vertex_groups.find('Root');assert root>=0
floor=46.55539321899414;inset=.65
new_records=[]
def add(points,uv1,slot,axes,bounds,part):
 start=len(vertices);points=[Vector(p) for p in points];vertices.extend(M@p for p in points);weights.extend([[(root,1.)] for p in points]);faces.append(list(range(start,len(vertices))))
 u0,u1,v0,v1=slots[slot];a,b=axes;x0,x1,y0,y1=bounds
 uv2=[(u0+(p[a]-x0)/(x1-x0)*(u1-u0),v0+(p[b]-y0)/(y1-y0)*(v1-v0)) for p in points]
 uvdata.append([uv1,uv2,[(.0625,.9375)]*len(points)]);materials.append(0);smooth.append(False);normals.append(None);parts.append(part)
 new_records.append({'face':len(faces)-1,'part':part,'slot':slot,'local_points':[list(p) for p in points]})
def plank(points):
 xs=[p[0] for p in points];ys=[p[1] for p in points];x0,x1=min(xs),max(xs);y0,y1=min(ys),max(ys)
 return [(wood[0]+(p[0]-x0)/(x1-x0)*(wood[1]-wood[0]),wood[2]+(p[1]-y0)/(y1-y0)*(wood[3]-wood[2])) for p in points]
# Full T-shaped floor: same level as the crane's wide loading bay.
xmain=-26.68780517578125;xwing=-35.583736419677734;xr=42.70048522949219
yfront=-50.8550910949707;ya=-30.46857452392578;yb=36.25093460083008;yrear=56.637451171875
fb=(xwing,xr,yfront,yrear)
for lo,hi,left in [(yfront,ya,xmain),(ya,yb,xwing),(yb,yrear,xmain)]:
 count=math.ceil((hi-lo)/7)
 for i in range(count):
  y0=lo+(hi-lo)*i/count;y1=lo+(hi-lo)*(i+1)/count
  pts=[(left,y0,floor),(xr,y0,floor),(xr,y1,floor),(left,y1,floor)]
  add(pts,plank(pts),0,(0,1),fb,1)
outline=[(xmain,yfront),(xr,yfront),(xr,yrear),(xmain,yrear),(xmain,yb),(xwing,yb),(xwing,ya),(xmain,ya)]
pts=[(x,y,floor-.7) for x,y in reversed(outline)];add(pts,plank(pts),1,(0,1),fb,2)
# Copy only upper shell panels, reverse winding and inset along the exterior normal.
wall_groups=[('Front',2,(0,2),(xmain,xr,floor,104.83)),('Rear',3,(0,2),(xmain,xr,floor,104.83)),
 ('Left_Wing',4,(1,2),(ya,yb,floor,104.83)),('Right_Wall',5,(1,2),(yfront,yrear,floor,74.73))]
for name,slot,axes,bounds in wall_groups:
 o=old_objects['CSC_Fixed_'+name]
 # Current polygons retain Henno's topology and UV changes, including split panels.
 plane_axis=1 if name in ('Front','Rear') else 0;plane={'Front':yfront,'Rear':yrear,'Left_Wing':xwing,'Right_Wall':xr}[name]
 normal=Vector({'Front':(0,-1,0),'Rear':(0,1,0),'Left_Wing':(-1,0,0),'Right_Wall':(1,0,0)}[name])
 for p in retained:
  pts=[inv@mesh.vertices[i].co for i in p.vertices]
  if not all(abs(v[plane_axis]-plane)<.002 for v in pts) or min(v.z for v in pts)<floor-.002:continue
  if max(v.z for v in pts)<=floor+.002:continue
  if (M.to_3x3()@normal).normalized().dot(p.normal)<.99:continue
  points=[v-normal*inset for v in reversed(pts)]
  uv1=[tuple(mesh.uv_layers['UV1'].data[i].uv) for i in reversed(list(p.loop_indices))]
  add(points,uv1,slot,axes,bounds,3)
o=old_objects['CSC_Fixed_Left_Returns']
for face_index,slot in [(1,6),(3,7),(5,8),(7,9)]:
 pts=[Vector(o['vertices'][i]) for i in o['faces'][face_index]];normal=Vector(o['normals'][face_index])
 source_index=lookup[signature([M@v for v in pts])];p=mesh.polygons[source_index]
 pts=[v-normal*inset for v in reversed(pts)];axis=1 if abs(normal.x)>.9 else 0
 bounds=(min(v[axis] for v in pts),max(v[axis] for v in pts),floor,74.73)
 uv1=[tuple(mesh.uv_layers['UV1'].data[i].uv) for i in reversed(list(p.loop_indices))]
 add(pts,uv1,slot,(axis,2),bounds,3)
# Replace the deep recesses with shallow opening reveals; the front sill stays at its existing height.
for j,(name,axis,plane,normal,a0,a1,z0,z1) in enumerate([
 ('front',1,yfront,Vector((0,-1,0)),-2.00158596,18.01426506,53.2273407,71.01921082),
 ('wing',0,xwing,Vector((-1,0,0)),-14.90069103,20.68304634,floor,77.69116211),
 ('right',0,xr,Vector((1,0,0)),-30.83924103,-11.56471539,52.93080902,70.72267914)]):
 def point(a,z):return Vector((a,plane,z) if axis==1 else (plane,a,z))
 edges=[(point(a0,z0),point(a1,z0)),(point(a1,z0),point(a1,z1)),(point(a1,z1),point(a0,z1)),(point(a0,z1),point(a0,z0))]
 for k,(a,b) in enumerate(edges):
  pts=[a,b,b-normal*inset,a-normal*inset]
  desired=(point((a0+a1)/2,(z0+z1)/2)-(a+b)/2).normalized()
  if (pts[1]-pts[0]).cross(pts[2]-pts[0]).dot(desired)<0:pts.reverse()
  uv1=[(wood[0],wood[2]),(wood[1],wood[2]),(wood[1],wood[3]),(wood[0],wood[3])]
  # Twelve small independent charts use the last two freed recess islands.
  base=slots[10+(j*4+k)//6]
  cell=(j*4+k)%6;u0,u1,v0,v1=base;du=(u1-u0)/3;dv=(v1-v0)/2
  slots.append((u0+(cell%3)*du+.0001,u0+(cell%3+1)*du-.0001,v0+(cell//3)*dv+.0001,v0+(cell//3+1)*dv-.0001))
  # Use local edge distance/depth for reveal UV2 rather than a degenerate plane projection.
  index=len(faces);add(pts,uv1,len(slots)-1,(0,2),(-100,100,0,110),4)
  su0,su1,sv0,sv1=slots[-1];uvdata[-1][1]=[(su0,sv0),(su1,sv0),(su1,sv1),(su0,sv1)]
new=bpy.data.meshes.new('CSC_Storage_L_Open_Interior');new.from_pydata(vertices,[],faces);new.update()
for material in mesh.materials:new.materials.append(material)
for name in uvnames:new.uv_layers.new(name=name)
for p,uv,mat,sm in zip(new.polygons,uvdata,materials,smooth):
 p.material_index=mat;p.use_smooth=sm
 for layer,values in zip(new.uv_layers,uv):
  for i,value in zip(p.loop_indices,values):layer.data[i].uv=value
new.normals_split_custom_set([n for p,ns in zip(new.polygons,normals) for n in (ns if ns is not None else [tuple(p.normal)]*len(p.vertices))])
obj.data=new
for name in group_names:
 if name not in obj.vertex_groups:obj.vertex_groups.new(name=name)
for i,groups in enumerate(weights):
 for group,weight in groups:obj.vertex_groups[group].add([i],weight,'REPLACE')
attr=new.attributes.new('storage_interior_part','INT','FACE')
for x,value in zip(attr.data,parts):x.value=value
obj['interior_design']='Open upper storey; inward shell lining; shallow opening reveals. Inspired by original pre-AO and CON+PIL sources.'
obj['interior_ao_status']='Independent shared-atlas charts reserved; pending staged AO bake.'
new.uv_layers.active_index=0;new.uv_layers['UV1'].active_render=True
for im in bpy.data.images:
 if im.source=='FILE':im.filepath=bpy.path.abspath(im.filepath)
for index,(positions,uv) in enumerate(original_corners):
 p=new.polygons[index];assert tuple(tuple(new.vertices[i].co) for i in p.vertices)==positions
 for layer,values in zip(new.uv_layers,uv):
  assert [tuple(layer.data[i].uv) for i in p.loop_indices]==values
for r in new_records:
 if r['part']==1:assert new.polygons[r['face']].normal.z>.999
 if r['part']==3:
  pts=[Vector(p) for p in r['local_points']];n=(M.to_3x3().inverted()@new.polygons[r['face']].normal).normalized();center=sum(pts,Vector())/len(pts)
  assert n.dot(Vector((4,3,center.z))-center)>0,(r,n)
report={'source_hash':source_hash,'removed_recess_faces':removed,'retained_faces_verified':len(retained),'new_faces':len(new_records),'vertices':len(new.vertices),'triangles':sum(len(p.vertices)-2 for p in new.polygons),'floor_local_z':floor,'preserved_exterior_uvs':True,'new_parts':new_records,'ao_status':obj['interior_ao_status']}
(OUT/'interior-check.json').write_text(json.dumps(report,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(STAGE))
print('INTERIOR_REWORK_SAVED',len(new.vertices),len(new.polygons),flush=True)
