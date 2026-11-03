"""One-time user-requested road-source move to 3D Art/Decals; no mesh edits."""
from pathlib import Path
import sys,json,shutil,hashlib,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[4]
ART=Path.home()/'Desktop/Working Files/3D Art'
OLD=ART/'Quarters/modern/roundabout-v1';NEW=ART/'Decals'
A=Path.home()/'Desktop/Codex/Quarter-Roads-Modern/draft-03-roundabout'
O=A/'source-relocation-20261029';MOD=ROOT/'Civ Supply Chains'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2))
def replace_string(s):return s.replace(str(OLD),str(NEW)).replace(OLD.as_posix(),NEW.as_posix())
def remap(x):
 if isinstance(x,str):return replace_string(x)
 if isinstance(x,list):return [remap(v) for v in x]
 if isinstance(x,dict):return {k:remap(v) for k,v in x.items()}
 return x

def move():
 assert OLD.resolve()==(ART.resolve()/'Quarters/modern/roundabout-v1') and NEW.resolve()==ART.resolve()/'Decals'
 assert not (O/'move-receipt.json').exists(),'Already moved'
 files=[p for p in OLD.rglob('*') if p.is_file()];assert len(files)>=70
 records=[]
 for p in files:
  dest=NEW/p.relative_to(OLD)
  assert p.resolve().is_relative_to(OLD.resolve()) and dest.resolve().is_relative_to(NEW.resolve())
  assert not dest.exists(),dest
  records.append({'source':str(p),'destination':str(dest),'sha256':sha(p)})
 dump(O/'move-plan.json',records)
 for r in records:
  p=Path(r['source']);dest=Path(r['destination']);assert sha(p)==r['sha256']
  dest.parent.mkdir(parents=True,exist_ok=True);shutil.move(str(p),str(dest));assert sha(dest)==r['sha256'] and not p.exists()
 dump(O/'move-receipt.json',{'files':records,'all_bytes_preserved':True})
 # Update only source-path attributes in installed AE wrappers.
 wrappers=[]
 for folder,pattern in [('Geometries','CSC_Road_*.geo'),('Geometries','CSC_ALL_Modern_Base*Road_Decals.geo'),('Textures','CSC_Roads_*.tex')]:
  for p in (MOD/folder).glob(pattern):
   raw=p.read_bytes();old=ET.fromstring(raw);field=old.find('m_SourceFilePath');source=field.get('text');target=replace_string(source)
   if target==source:continue
   assert Path(target).exists(),target
   data=raw.replace(source.encode(),target.encode());new=ET.fromstring(data)
   new.find('m_SourceFilePath').set('text',source)
   assert ET.tostring(new)==ET.tostring(old),'Non-path XML change'
   backup=O/'wrappers-before'/p.name;backup.parent.mkdir(exist_ok=True);backup.write_bytes(raw)
   assert p.read_bytes()==raw;p.write_bytes(data)
   wrappers.append({'destination':str(p),'before':hashlib.sha256(raw).hexdigest(),'after':sha(p)})
 assert len(wrappers)==28,len(wrappers)
 dump(O/'publication-report.json',{'installed':True,'files':wrappers,'change':'Source paths only; geometry/texture bytes preserved'})
 # Active tool inputs follow the canonical source. Historical receipts stay intact.
 active=[A/'masters.json',A/'combined-layout-20261029/model.json',A/'combined-layout-20261029/saved-validation.json',A/'layout-variants-20261029/saved-validation.json']
 active+=list((A/'models').glob('*.json'))+list((A/'layout-variants-20261029/models').glob('*.json'))
 for p in active:
  before=p.read_bytes();updated=remap(json.loads(before));backup=O/'active-inputs-before'/p.relative_to(A);backup.parent.mkdir(parents=True,exist_ok=True);backup.write_bytes(before);dump(p,updated)
 for p in Path(__file__).parent.glob('*.py'):
  if p.name=='relocate.py':continue
  text=p.read_text();updated=text.replace('Desktop/Working Files/3D Art/Quarters/modern/roundabout-v1','Desktop/Working Files/3D Art/Decals')
  if text!=updated:p.write_text(updated)
 (OLD/'MOVED.txt').write_text('Road source masters, modules and textures now live at:\n'+str(NEW)+'\nSee the CSC_ALL_Modern_Base_01..05_Road_Decals blends there.\n')
 sys.path.insert(0,str(ROOT/'project/tools/art/modern_windmill'));import modular_v9_native as n
 n.cache(O)
 print('MOVED',len(records),'files; updated',len(wrappers),'AE source references',flush=True)

def validate():
 import bpy
 sys.path.insert(0,str(ROOT/'project/tools/blender'))
 from csc_scene_validation import suspend_csc_repairs,validate_current_scene
 receipt=json.loads((O/'move-receipt.json').read_text());reports=[]
 for row in receipt['files']:
  p=Path(row['destination']);assert sha(p)==row['sha256'],p
  if p.suffix!='.blend':continue
  with suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(p),load_ui=False,use_scripts=False)
  report=validate_current_scene();assert report['automated_pass'],(p,report['findings'])
  images=[]
  for img in bpy.data.images:
   if img.source=='FILE' and img.filepath:
    resolved=Path(bpy.path.abspath(img.filepath));assert resolved.is_file(),(p,img.name,resolved)
    assert resolved.resolve().is_relative_to(NEW.resolve()),(p,resolved)
    images.append(str(resolved))
  assert sha(p)==row['sha256'];reports.append({'source':str(p),'saved_scene_pass':True,'external_images_resolve':len(images),'bytes_preserved':True})
 assert len(reports)==21,len(reports)
 dump(O/'saved-validation.json',reports);print('RELOCATED_MASTERS_PASS',len(reports),flush=True)

if __name__=='__main__':
 mode=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else sys.argv[1];globals()[mode]()
