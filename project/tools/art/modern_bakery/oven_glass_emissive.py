"""Lift the entire oven glass area, retaining bread detail and dark metal trim."""
import sys,json,shutil,hashlib,subprocess,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];MOD=ROOT/'Civ Supply Chains';O=Path.home()/'Desktop/Codex/modern-oven-glass-emissive-20261028';LIB=Path.home()/'Desktop/Working Files/3D Art/Textures/CSC_Props_Modern';EID='CSC_Props_Modern_01_E'
sys.path.insert(0,str(Path(__file__).parent));sys.path.insert(0,str(ROOT/'project/tools/art/modern_windmill'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2))
def prepare():
 import modular_v9_native as n
 from PIL import Image,ImageDraw,ImageFilter
 import numpy as np
 for d in ('sources','textures','staged/Textures','staged/Assets'):(O/d).mkdir(parents=True,exist_ok=True)
 before=LIB/'Current/textures'/(EID+'.png');assert not (O/'baseline.json').exists();dump(O/'baseline.json',{'E_source':sha(before),'E_runtime':sha(MOD/'Textures'/(EID+'.dds')),'ASTs':{p.name:sha(p) for p in (MOD/'Assets').glob('*.ast')}})
 shutil.copy2(before,O/'sources/Before_E.png');page=Image.open(before).convert('RGB');old=np.array(page)
 b=LIB/'Current/textures/CSC_Props_Modern_01_B.png';tile=Image.open(b).convert('RGB').crop((256,384,384,512));rgb=np.array(tile,dtype=float)/255;linear=np.where(rgb<=.04045,rgb/12.92,((rgb+.055)/1.055)**2.4)
 mask=Image.new('L',(128,128));draw=ImageDraw.Draw(mask)
 for rect in ((20,23,99,42),(20,69,99,87)):draw.rectangle(rect,fill=255)
 mask=mask.filter(ImageFilter.GaussianBlur(.6))
 radiance=(np.array([.18,.075,.021])+linear*.32)*(np.array(mask)/255)[:,:,None]
 srgb=np.where(radiance<=.0031308,radiance*12.92,1.055*radiance**(1/2.4)-.055);patch=Image.fromarray(np.uint8(np.clip(srgb*255,0,255)));page.paste(patch.resize((32,32),Image.Resampling.LANCZOS),(64,96))
 keep=np.ones((256,256),bool);keep[96:128,64:96]=False;assert np.array_equal(old[keep],np.array(page)[keep]);page.save(O/'textures'/(EID+'.png'));patch.save(O/'sources/Oven_Window_E_Registered.png');mask.save(O/'sources/Oven_Window_Mask.png')
 result=subprocess.run([str(ROOT/'project/tools/directxtex/texconv.exe'),'-nologo','-y','-m','0','-f','R8G8B8A8_UNORM','--ignore-srgb','-srgb','-o',str(O/'staged/Textures'),str(O/'textures'/(EID+'.png'))],capture_output=True,text=True);assert result.returncode==0; n.exp.validate_dds(O/'staged/Textures'/(EID+'.dds'),{'slot':'E','size':[256,256],'format':'R8G8B8A8_UNORM'})
 shutil.copy2(MOD/'Textures'/(EID+'.tex'),O/'staged/Textures'/(EID+'.tex'));shutil.copy2(MOD/'Assets/CSC_BAKERS_Bakery_Modern_2.ast',O/'staged/Assets/CSC_BAKERS_Bakery_Modern_2.ast')
 dump(O/'recipe.json',{'change':'Whole-glass warm radiance floor, not bread-only glow','linear_warm_floor':[.18,.075,.021],'painted_detail_gain':.32,'masks_128':[[20,23,99,42],[20,69,99,87]],'outside_cell26_identical':True,'geometry_UV_material_changes':False})
 import interior_lighting_review as r
 r.O=O;r.SPECS=['after-night'];r.prepare();print('GLASS_E_PREPARED',flush=True)
def render():
 import interior_lighting_review as r
 r.O=O;r.SPECS=['after-night'];r.render()
def publish():
 import modular_v9_native as n
 baseline=json.loads((O/'baseline.json').read_text());cur=LIB/'Current';source=cur/'textures'/(EID+'.png');runtime=MOD/'Textures'/(EID+'.dds')
 assert sha(source)==baseline['E_source'] and sha(runtime)==baseline['E_runtime'];assert (O/'review/after-night/render.png').exists()
 release='2026-10-28_Modern_r009';snap=LIB/'Releases'/release;assert not snap.exists();payload={}
 for p in cur.rglob('*'):
  if p.is_file():payload[snap/p.relative_to(cur)]=p.read_bytes()
 manifest=json.loads((cur/'library.json').read_text());manifest.update(previous_release=manifest['release'],release=release,status='Whole oven glazing emits warm light; bread detail retained, metal dark');manifest['maps'][EID+'.png']=sha(O/'textures'/(EID+'.png'))
 plan=json.loads((cur/'atlas-plan.json').read_text());plan['emissive']['glass_lighting']=json.loads((O/'recipe.json').read_text());plan['emissive']['linear_painted_gain']=.32;plan['emissive']['linear_glass_floor']=[.18,.075,.021]
 updates={'library.json':json.dumps(manifest,indent=2).encode(),'atlas-plan.json':json.dumps(plan,indent=2).encode(),'textures/'+EID+'.png':(O/'textures'/(EID+'.png')).read_bytes(),'sources/published-registered/'+EID+'.png':(O/'textures'/(EID+'.png')).read_bytes()}
 for name in ('Oven_Window_E_Registered.png','Oven_Window_Mask.png'):updates['sources/oven-emissive/'+name]=(O/'sources'/name).read_bytes()
 updates['sources/oven-emissive/glass-recipe.json']=(O/'recipe.json').read_bytes()
 for rel,data in updates.items():payload[cur/rel]=data;payload[snap/rel]=data
 payload[LIB/'CURRENT.json']=json.dumps({'release':release,'current':'Current','snapshot':'Releases/'+release,'manifest':'Current/library.json'},indent=2).encode()
 payload[Path.home()/'Desktop/Working Files/3D Art/BAKERS/Bakery/modern/revision-04-ae/textures'/(EID+'.png')]=(O/'textures'/(EID+'.png')).read_bytes();payload[runtime]=(O/'staged/Textures'/(EID+'.dds')).read_bytes()
 backup=O/'publication-backup';backup.mkdir(exist_ok=True);rows=[]
 for i,(p,data) in enumerate(payload.items()):
  row={'destination':str(p),'before':sha(p) if p.exists() else None,'after':hashlib.sha256(data).hexdigest()}
  if p.exists():q=backup/f'{i:03}-{p.name}';shutil.copy2(p,q);row['backup']=str(q)
  rows.append(row)
 dump(backup/'manifest.json',rows)
 for row,(p,data) in zip(rows,payload.items()):
  assert (sha(p) if p.exists() else None)==row['before'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
 dump(O/'publication-report.json',{'installed':True,'files':rows,'release':release,'texture_only':True});n.cache(O)
 assert all(sha(row['destination'])==row['after'] for row in rows);assert all(sha(MOD/'Assets'/name)==value for name,value in baseline['ASTs'].items());print('GLASS_E_INSTALLED',release,flush=True)
if __name__=='__main__':render() if '--' in sys.argv else globals()[sys.argv[1]]()
