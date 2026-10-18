"""Use original windows/coals runtime E; modify only six opening UV3 faces."""
import bpy,sys,json,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from build_bakery_props import *
helper=Path(__file__).with_name('remap_bakery_revision05.py').read_text();exec(helper[:helper.index('for index,ident in enumerate(IDS):')])
ident='CSC_BAKERS_Oven_v2';path=SOURCE/(ident+'.blend')
with V.suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
changes=[]
for o in bpy.data.scenes['Export'].objects:
 if o.type!='MESH':continue
 for p in o.data.polygons:
  if p.index not in (112,113,114,116,117,118):continue
  for l in p.loop_indices:
   u,v=o.data.uv_layers[0].data[l].uv;a=(u*1024-388)/120;b=((1-v)*1024-900)/120
   before=list(o.data.uv_layers[2].data[l].uv);o.data.uv_layers[2].data[l].uv=((192+56*a)/256,1-(184+48*b)/256)
   changes.append(dict(object=o.name,face=p.index,loop=l,before=before,after=list(o.data.uv_layers[2].data[l].uv)))
for im in bpy.data.images:
 if im.source=='FILE' and im.users:
  q=SOURCE/'textures'/Path(bpy.path.abspath(im.filepath)).name
  if q.exists():im.filepath=str(q);im.reload()
# Material binding is deliberately deferred: the global audit found other lit consumers.
for s in bpy.data.scenes:s['atlas_release']=RELEASE;s['proposed_emissive_texture']='CSC_Atlas_E'
bpy.ops.file.make_paths_relative();bpy.ops.wm.save_as_mainfile(filepath=str(path));h=hashlib.sha256(path.read_bytes()).hexdigest()
with V.suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
r=V.validate_current_scene();r['source_sha256']=h;assert r['automated_pass'];(OUT/(ident+'-validation.json')).write_text(json.dumps(r,indent=2));(OUT/'oven-UV3-change.json').write_text(json.dumps(changes,indent=2));export(ident,6,h,path)
