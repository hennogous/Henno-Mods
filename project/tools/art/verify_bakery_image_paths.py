import bpy,sys,json,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from build_bakery_props import *
rows=[]
for ident in IDS+['CSC_BAKERS_Bakery_Prop_Kit']:
 path=SOURCE/(ident+'.blend')
 with V.suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
 images=[]
 for im in bpy.data.images:
  if im.source!='FILE' or not im.users:continue
  p=Path(bpy.path.abspath(im.filepath)).resolve();assert p.parent==SOURCE/'textures',(ident,str(p));assert p.exists();expected=STAGE/'textures'/p.name;assert expected.exists() and hashlib.sha256(p.read_bytes()).digest()==hashlib.sha256(expected.read_bytes()).digest();images.append(dict(name=im.name,path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
 assert images;rows.append(dict(source=str(path),images=images))
(OUT/'saved-source-image-resolution.json').write_text(json.dumps(rows,indent=2));print('ALL 7 MASTERS + KIT RESOLVE EXACT SNAPSHOT TEXTURES',RELEASE)
