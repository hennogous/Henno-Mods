"""Move the saved roundabout, easing its approaches into unchanged outer corridors.

Operate on saved masters, preserving their textures, UV allocations, scenes and
module identities. Archive the complete pre-edit source set before changing it.
"""
import bpy,json,sys,math,shutil,hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[4];sys.path[:0]=[str(ROOT/'project/tools/blender'),str(ROOT/'project/tools/blender/scene_export')]
from csc_scene_validation import suspend_csc_repairs,validate_current_scene
import decode_blend as dec
O=Path.home()/'Desktop/Codex/Quarter-Roads-Modern/draft-03-roundabout'
D=Path.home()/'Desktop/Working Files/3D Art/Decals/CSC_ALL_Modern_Roads'
delta=Vector((40,-20));oldcenter=Vector((-35,30));newcenter=oldcenter+delta
layout=json.loads((D/'layout-modules.json').read_text());oldroutes={k:[Vector(p) for p in points] for k,points in layout['routes'].items()}
metadata=json.loads((D/'atlas-layout.json').read_text());assert Vector(metadata['roundabout']['center'])==oldcenter,'Already shifted or edited; inspect before running again.'
archive=O/'history/before-center-shift';archive.mkdir(parents=True,exist_ok=False);shutil.copytree(D,archive/'source')
for name in ['Classical_Modern_Coverage_Overlay.png','Roundabout_Progression.png','delivery-validation.json','classical-alignment-validation.json']:
 shutil.copy2(O/name,archive/name)
def weight(t):
 t=max(0,min(1,t));return 1-3*t*t+2*t*t*t
def offset(name,i,f=0):
 if name=='Connector':
  t=(i+f)/(len(oldroutes[name])-1);return delta*(weight(34/40)*(1-t)+weight(36/40)*t)
 return delta*weight((i+f)/40)
newroutes={k:[p+offset(k,i) for i,p in enumerate(points)] for k,points in oldroutes.items()}
def shift_vertex(name,co):
 p=Vector(co[:2])
 if name=='Roundabout':return p+delta
 old=oldroutes[name];best=None
 for i,(a,b) in enumerate(zip(old,old[1:])):
  v=b-a;f=max(0,min(1,(p-a).dot(v)/max(1e-12,v.length_squared)));q=a+v*f;dist=(p-q).length_squared
  if best is None or dist<best[0]:best=(dist,i,f,q,v)
 _,i,f,q,v=best
 # Exactly preserve the complete historical outer corridors, not just endpoints.
 if name!='Connector' and i+f>=40-1e-6:return p
 diff=offset(name,i,f);newtan=(newroutes[name][i+1]-newroutes[name][i]).normalized();oldtan=v.normalized()
 ang=math.atan2(newtan.y,newtan.x)-math.atan2(oldtan.y,oldtan.x);off=p-q
 return q+diff+Vector((math.cos(ang)*off.x-math.sin(ang)*off.y,math.sin(ang)*off.x+math.cos(ang)*off.y))
records=json.loads((O/'masters.json').read_text());paths=[D/'CSC_ALL_Modern_Roundabout_Kit.blend']+[Path(r['blend']) for r in records];reports=[]
for path in paths:
 with suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
 seen=set();changed=[]
 # Modify each shared mesh once, preserving preview/projection synchronization.
 for ob in bpy.data.objects:
  if ob.type!='MESH' or ob.data.as_pointer() in seen:continue
  name=ob.name.removeprefix('CSC_Projection_').rsplit('_',1)[0]
  if name not in ['Roundabout',*oldroutes]:continue
  seen.add(ob.data.as_pointer())
  for v in ob.data.vertices:
   p=shift_vertex(name,v.co);v.co.x=p.x;v.co.y=p.y
  ob.data.update();changed.append(name)
 for s in bpy.data.scenes:s['roundabout_center']=list(newcenter)
 bpy.ops.wm.save_as_mainfile(filepath=str(path))
 with suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
 r=validate_current_scene();assert r['automated_pass'],r['findings'];reports.append({'id':path.stem,'automated_pass':True,'counts':r['counts']})
 if path.parent.name=='modules':
  ident=path.stem;ob=next(ob for ob in bpy.data.scenes['Export'].objects if ob.type=='MESH');m=dec.decode_mesh(ob,ob.matrix_world);m['name']=ident
  for mat in m['materials']:mat['external']=mat['name']
  (O/'models'/(ident+'.json')).write_text(json.dumps({'asset_id':ident,'kind':'decal','meshes':[m]}))
layout['routes']={k:[list(v) for v in points] for k,points in newroutes.items()};layout['roundabout_center']=list(newcenter);layout['center_shift']=list(delta)
(D/'layout-modules.json').write_text(json.dumps(layout,indent=2));metadata['roundabout']['center']=list(newcenter)
for path in [D/'atlas-layout.json',O/'atlas-layout.json']:path.write_text(json.dumps(metadata,indent=2))
(O/'final-saved-validation.json').write_text(json.dumps(reports,indent=2))
(O/'center-shift.json').write_text(json.dumps({'old_center':list(oldcenter),'new_center':list(newcenter),'delta':list(delta),'old_sources':str(archive/'source'),'outer_corridors':'unchanged from classical anchors','textures':'unchanged','method':'Ease translation into existing saved approach geometry; rotate cross sections to preserve width'},indent=2))
with suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(paths[0]),load_ui=False,use_scripts=False)
for name,fn in [('01 - Industrial paving','01_Stone'),('Review','02_First_building'),('03A - East destination','03A_East'),('03B - Southwest destination','03B_Southwest'),('04 - All routes','04_All_tarmac')]:
 s=bpy.data.scenes[name];s.render.filepath=str(O/(fn+'.png'));bpy.ops.render.render(write_still=True,scene=name)
print('CENTER_SHIFT_SAVED_AND_VALIDATED',list(newcenter),len(reports),flush=True)
