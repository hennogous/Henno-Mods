"""Stage the refitted static building through the normal three-UV exporter."""
import bpy,json
from pathlib import Path
import io_export_cn6 as cn6
ROOT=Path(r'C:\Users\Shadow\Desktop\Working Files\3D Art\Storage\Storage_L')
OUT=Path(r'C:\Users\Shadow\Desktop\Codex\CSC_Storage_L\delivery-refit-20261009')
for event in ('load_post','depsgraph_update_post'):
 for cb in list(getattr(bpy.app.handlers,event)):
  if cb.__module__.rsplit('.',1)[-1]=='csc_scene_tools':getattr(bpy.app.handlers,event).remove(cb)
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'CSC_Storage_L.blend'))
bpy.context.window.scene=bpy.data.scenes['Export'];rig=bpy.data.objects['CSC_Storage_L']
result=cn6.csc_export_fgx_geo('CSC_Storage_L',str(OUT),'LandmarkModel',3,True,rig)
p=OUT/'CSC_Storage_L.geo';p.write_text(p.read_text().replace('AssetObjects:','AssetObjects..'))
print('STATIC_STORAGE_EXPORT_PASS',repr(result))
