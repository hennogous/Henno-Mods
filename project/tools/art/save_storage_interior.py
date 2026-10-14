"""Publish the checked source geometry and isolated shared AO patch with backups."""
import bpy,json,hashlib,shutil
from pathlib import Path
ROOT=Path(r'C:\Users\Shadow\Desktop\Working Files\3D Art\Storage\Storage_L')
OUT=Path(r'C:\Users\Shadow\Desktop\Codex\CSC_Storage_L\interior-20261008')
SOURCE=ROOT/'CSC_Storage_L.blend';AO=ROOT.parent.parent/'Textures/CSC_Atlas_AO2.png'
geometry=json.loads((OUT/'interior-check.json').read_text());patch=json.loads((OUT/'ao-patch-check.json').read_text())
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==geometry['source_hash'],'Source changed since inspection'
assert hashlib.sha256(AO.read_bytes()).hexdigest()==patch['original_sha256'],'Shared AO changed since baking'
backup=OUT/'before-interior';backup.mkdir(exist_ok=True)
for path in (SOURCE,AO):
 target=backup/path.name;assert not target.exists(),'Backup already exists';shutil.copy2(path,target)
for event in ('load_post','depsgraph_update_post'):
 for cb in list(getattr(bpy.app.handlers,event)):
  if cb.__module__.rsplit('.',1)[-1]=='csc_scene_tools':getattr(bpy.app.handlers,event).remove(cb)
bpy.ops.wm.open_mainfile(filepath=str(OUT/'CSC_Storage_L_Interior.blend'))
obj=bpy.data.objects['CSC_Storage_L_Bldg'];obj['interior_ao_status']='Baked into independent reserved charts of canonical CSC_Atlas_AO2.png; allocation and pixel-preservation report in interior-20261008.'
shutil.copy2(OUT/'CSC_Atlas_AO2.png',AO)
for image in bpy.data.images:
 if image.source=='FILE':image.filepath=bpy.path.abspath(image.filepath)
 if 'CSC_Atlas_AO2' in image.name:image.filepath=str(AO);image.reload()
bpy.context.window.scene=bpy.data.scenes['Review']
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
print('STORAGE_INTERIOR_SOURCE_SAVED',str(SOURCE))
