import bpy,sys,math,hashlib,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from build_bakery_props import *
from bakery_props_atlas import LIB
helper=Path(__file__).with_name('remap_bakery_revision05.py').read_text();exec(helper[:helper.index('for index,ident in enumerate(IDS):')])
# Coordinate bounds are immutable r030 region rectangles, even after freeing other cells.
old=json.loads((LIB/'Releases/2026-10-17_Shared_01_r030/atlas/manifest.json').read_text());regions={r['slot']:r['bounds'] for r in old['regions']};dest=regions[61];changes=[]
for index,ident in enumerate(IDS):
 if ident not in IDS[2:6]:continue
 path=SOURCE/(ident+'.blend')
 with V.suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(SOURCE.parent/'revision-06-prop-kit'/(ident+'.blend')),load_ui=False,use_scripts=False)
 count=0
 for ob in bpy.data.scenes['Export'].objects:
  if ob.type!='MESH' or 'Bread_Fill' not in ob.name:continue
  kind=next(k for k in ['Round','Oval','Long'] if '_'+k+'_' in ob.name);uv=ob.data.uv_layers[0]
  for p in ob.data.polygons:
   for l in p.loop_indices:
    u,v=uv.data[l].uv;px=u*1024;py=(1-v)*1024;slot=int(py//128)*8+int(px//128);assert slot in [10,30,61,62],(ob.name,p.index,slot);x,y,x1,y1=regions[slot];a=(px-x)/(x1-x);b=(py-y)/(y1-y)
    if slot!=10:
     if kind in ['Oval','Long']:a=1-a
     if kind=='Long':b=1-b
     a=.02+.96*a;b=.02+.71*b
    else:
     if kind=='Oval':a=1-a
     face=((p.index-1)%12)//3
     span=.96;offset=.02
     a=offset+span*a;b=.77+.21*b
    x,y,x1,y1=dest;uv.data[l].uv=((x+(x1-x)*a)/1024,1-(y+(y1-y)*b)/1024);count+=1
 for scene in bpy.data.scenes:
  if scene.name in ('Export','Review'):scene['atlas_release']=RELEASE
 for image in bpy.data.images:
  if image.source=='FILE' and (SOURCE/'textures'/Path(bpy.path.abspath(image.filepath)).name).exists():image.filepath=str(SOURCE/'textures'/Path(bpy.path.abspath(image.filepath)).name)
 bpy.ops.wm.save_as_mainfile(filepath=str(path));bpy.ops.file.make_paths_relative();bpy.ops.wm.save_as_mainfile(filepath=str(path));before=hashlib.sha256(path.read_bytes()).hexdigest()
 with V.suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
 report=V.validate_current_scene();report['source_sha256']=before;assert report['automated_pass'];(OUT/(ident+'-validation.json')).write_text(json.dumps(report,indent=2));export(ident,index,before,path);changes.append(dict(asset=ident,UV1_loop_count=count,destination_slot=61))
(OUT/'bread-consolidation-UV.json').write_text(json.dumps(dict(changes=changes,freed_slots=[10,30,62],crown_image_V=[.02,.73],side_image_V=[.77,.98],no_geometry_change=True),indent=2))

