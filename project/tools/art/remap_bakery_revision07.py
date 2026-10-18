import bpy,sys,math,hashlib,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from build_bakery_props import *
# Load export helper without executing revision05's mutation loop.
helper=Path(__file__).with_name('remap_bakery_revision05.py').read_text();exec(helper[:helper.index('for index,ident in enumerate(IDS):')])
ident='CSC_BAKERS_Oven_v2';path=SOURCE/(ident+'.blend')
with V.suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
rows=[];x,y,x1,y1=C.REGIONS['bakery_brick']
for ob in bpy.data.scenes['Export'].objects:
 if ob.type!='MESH':continue
 uv=ob.data.uv_layers[0]
 for p in ob.data.polygons:
  if not all(x/1024-.00001<=uv.data[l].uv.x<=x1/1024+.00001 and 1-y1/1024-.00001<=uv.data[l].uv.y<=1-y/1024+.00001 for l in p.loop_indices):continue
  pts=[ob.matrix_world@ob.data.vertices[ob.data.loops[l].vertex_index].co for l in p.loop_indices];cz=sum(q.z for q in pts)/len(pts)
  if p.index>=200:
   n=p.normal
   if abs(n.z)>.8:coords=[(q.x+24,q.y+8) for q in pts];mode='chimney planar top'
   elif abs(n.x)>abs(n.y):coords=[(q.y,q.z-24) for q in pts];mode='chimney YZ'
   else:coords=[(q.x+24,q.z-24) for q in pts];mode='chimney XZ'
  elif p.normal.z>.85:
   coords=[(q.x+32,q.y+3.9+32) for q in pts];mode='planar crown'
  else:
   radius=30 if cz<35 else 28 if cz<46 else 25 if cz<54 else 20
   angles=[math.atan2(q.y+3.9,q.x) for q in pts]
   if max(angles)-min(angles)>math.pi:angles=[a+2*math.pi if a<0 else a for a in angles]
   coords=[(a*radius,34.5*math.atan2((q.z-28)/39,math.hypot(q.x,q.y+3.9)/30)) for a,q in zip(angles,pts)];mode='constant-scale side band'
  # Repeat by whole brick-pattern periods, keeping each face within its atlas cell.
  for axis,period in [(0,16),(1,8)]:
   lo=min(v[axis] for v in coords);hi=max(v[axis] for v in coords)
   if lo<1 or hi>63:
    shift=math.floor(lo/period)*period;coords=[tuple(value-shift if i==axis else value for i,value in enumerate(v)) for v in coords]
  assert all(0<=a<=64 and 0<=b<=64 for a,b in coords),(p.index,coords)
  for l,(a,b) in zip(p.loop_indices,coords):uv.data[l].uv=((x+(x1-x)*(.01+.98*a/64))/1024,1-(y+(y1-y)*(1-(.01+.98*b/64)))/1024)
  rows.append(dict(face=p.index,mapping=mode))
for scene in bpy.data.scenes:
 if scene.name in ('Export','Review'):scene['atlas_release']=RELEASE
bpy.ops.wm.save_as_mainfile(filepath=str(path));before=hashlib.sha256(path.read_bytes()).hexdigest()
with V.suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
report=V.validate_current_scene();report['source_sha256']=before;assert report['automated_pass'];(OUT/(ident+'-validation.json')).write_text(json.dumps(report,indent=2));(OUT/'oven-r031-UV-mapping.json').write_text(json.dumps(dict(brick_physical_size=[8,4],patch_physical_extent=[64,64],dome_centre=[0,-3.9],faces=rows,shape_unchanged=True,UV2_AO_unchanged=True),indent=2));export(ident,6,before,path)
