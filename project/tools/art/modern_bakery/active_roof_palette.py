"""Historical active roof palette on the modern L2 atlas; registered detail retained."""
import sys,json,hashlib,shutil,subprocess,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];MOD=ROOT/'Civ Supply Chains';O=Path.home()/'Desktop/Codex/modern-bakery-active-roof-20261028';ART=Path.home()/'Desktop/Working Files/3D Art';LIB=ART/'Textures/CSC_Buildings_Modern';BID='CSC_Atlas_Modern_B_BAKERS'
sys.path.insert(0,str(ROOT/'project/tools/blender'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2))
def prepare():
 from PIL import Image
 import numpy as np
 import colorsys
 generated=Path(sys.argv[2]);image=Image.open(generated).convert('RGB');before=Image.open(O/'Modern_Before.png').convert('RGBA');out=before.copy();mask=np.zeros((1024,1024),bool);rows=[]
 for d in ('textures','staged/Textures','staged/Assets','sources'):(O/d).mkdir(parents=True,exist_ok=True)
 assert sha(LIB/'Current/textures'/(BID+'.png'))==sha(O/'Modern_Before.png')
 dump(O/'baseline.json',{'B_source':sha(LIB/'Current/textures'/(BID+'.png')),'B_runtime':sha(MOD/'Textures'/(BID+'.dds')),'ASTs':{p.name:sha(p) for p in (MOD/'Assets').glob('*.ast')}});shutil.copy2(generated,O/'sources/ImageGen_Roof_Palette.png')
 for i,slot in enumerate((2,3,8)):
  x=512+slot%4*128;y=slot//4*128;original=before.crop((x,y,x+128,y+128)).convert('RGB');gen=image.crop((round(i*image.width/3),0,round((i+1)*image.width/3),image.height));colors=np.asarray(gen,dtype=float).reshape(-1,3)/255
  # Palette from generated edit; retain every original seam/grain pixel through
  # original value modulation so companion relief maps stay exactly registered.
  selected=colors[(colors[:,1]>colors[:,0]*1.08)&(colors[:,1]>colors[:,2]*1.4)];assert len(selected)>500
  generated_color=np.median(selected,axis=0)
  reference=Image.open(O/'Historical_Roof_Trim_Colours.png').convert('RGB');ref=np.asarray(reference.crop((i*384,0,(i+1)*384,384)),dtype=float).reshape(-1,3)/255
  ref=ref[(ref[:,1]>ref[:,0]*1.08)&(ref[:,1]>ref[:,2]*1.4)&(ref[:,1]>50/255)]
  color=np.median(ref,axis=0);h,s,v=colorsys.rgb_to_hsv(*color);rgb=np.asarray(original,dtype=float)/255;value=rgb.max(axis=2);ratio=np.clip(value/np.median(value),.25,1.8)
  target=np.array(colorsys.hsv_to_rgb(h,s,1));paint=np.clip(ratio[:,:,None]*v*target[None,None,:],0,1);patch=Image.fromarray(np.uint8(paint*255));out.paste(patch,(x,y));mask[y:y+128,x:x+128]=True
  rows.append({'slot':slot,'generated_median_RGB':(generated_color*255).tolist(),'historical_calibrated_median_RGB':(color*255).tolist(),'original_detail_preserved':'Per-pixel value ratios; palette-only edit'})
 assert np.array_equal(np.asarray(before)[~mask],np.asarray(out)[~mask]);out.save(O/'textures'/(BID+'.png'));dump(O/'colour-checks.json',{'outside_three_cells_pixel_identical':True,'cells':rows,'geometry_UVs_AO_normals_unchanged':True})
 sys.path.insert(0,str(ROOT/'project/tools/art/modern_windmill'));import modular_v9_native as n
 r=subprocess.run([str(ROOT/'project/tools/directxtex/texconv.exe'),'-nologo','-y','-m','0','-f','R8G8B8A8_UNORM','--ignore-srgb','-srgb','-o',str(O/'staged/Textures'),str(O/'textures'/(BID+'.png'))],capture_output=True,text=True);assert r.returncode==0;n.exp.validate_dds(O/'staged/Textures'/(BID+'.dds'),{'slot':'B','size':[1024,1024],'format':'R8G8B8A8_UNORM'})
 shutil.copy2(MOD/'Textures'/(BID+'.tex'),O/'staged/Textures'/(BID+'.tex'))
 from render_ae_asset import Resolver,Assembly,DEFAULT_SDK,prepare_geometry,PRESETS
 for ident in ('CSC_BAKERS_Bakery_2','CSC_BAKERS_Bakery_Modern_2'):
  resolver=Resolver(MOD,DEFAULT_SDK)
  for p in (O/'staged/Textures').iterdir():resolver.index[p.name.casefold()]={p}
  a=Assembly(resolver,'Worked');key=a.asset(MOD/'Assets'/(ident+'.ast'));run=O/'review'/ident;run.mkdir(parents=True,exist_ok=True);prepare_geometry(a,O/'cache',run)
  camera=json.loads((ROOT/'project/tools/blender/ae_render_camera_presets.json').read_text())['classes']['L2'];camera['icon']['lens']*=.82
  settings={'presets':PRESETS,'resolution':1200,'samples':40,'camera_class':'L2','fixed_camera':camera,'render_emission_enabled':False,'state':'Worked'}
  job={'root':key,'assets':a.assets,'geometries':a.geometries,'materials':a.materials,'excluded':a.excluded,'warnings':a.warnings,'settings':settings,'output':str(run)};dump(run/'job.json',job)
 print('ACTIVE_ROOF_PREPARED',rows,flush=True)
def render():
 import bpy
 from ae_asset_render_blender import Builder
 for ident in ('CSC_BAKERS_Bakery_2','CSC_BAKERS_Bakery_Modern_2'):
  if 'modern-only' in sys.argv and ident=='CSC_BAKERS_Bakery_2':continue
  run=O/'review'/ident;job=json.loads((run/'job.json').read_text());bpy.ops.wm.read_factory_settings(use_empty=True);b=Builder(job,'icon');b.assemble(job['root'],root=True);bpy.context.view_layer.update();b.clip_foundation();b.setup();s=b.scene;s.use_nodes=False;s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.image_settings.color_depth='8';s.render.filepath=str(run/'render.png');bpy.ops.render.render(write_still=True);bpy.ops.wm.save_as_mainfile(filepath=str(run/'review.blend'));print('RENDERED',ident,flush=True)
def publish():
 base=json.loads((O/'baseline.json').read_text());cur=LIB/'Current';source=cur/'textures'/(BID+'.png');runtime=MOD/'Textures'/(BID+'.dds');assert sha(source)==base['B_source'] and sha(runtime)==base['B_runtime']
 release='2026-10-28_Modern_r014';snap=LIB/'Releases'/release;assert not snap.exists();payload={}
 for p in cur.rglob('*'):
  if p.is_file():payload[snap/p.relative_to(cur)]=p.read_bytes()
 manifest=json.loads((cur/'library.json').read_text());manifest.update(previous_release=manifest['release'],release=release,status='Modern L2 roof and trim match historical active Bakers palette; registered detail retained');manifest['maps'][BID+'.png']=sha(O/'textures'/(BID+'.png'))
 plan=json.loads((cur/'atlas-plan.json').read_text());plan.setdefault('building',{}).setdefault('stage_3_cells',{}).update({'2':'Active Bakers yellow-green standing-seam roof','3':'Active Bakers dark-green ridge and barge trim (formerly cream)','8':'Active Bakers green painted timber / roof edges'});plan.setdefault('modern_level2',{})['roof_palette']='Historical active CSC_Atlas_B_BAKERS_2; retained in base atlas for later human recolour'
 updates={'library.json':json.dumps(manifest,indent=2).encode(),'textures/'+BID+'.png':(O/'textures'/(BID+'.png')).read_bytes(),'sources/published-registered/'+BID+'.png':(O/'textures'/(BID+'.png')).read_bytes(),'sources/active-roof/colour-checks.json':(O/'colour-checks.json').read_bytes(),'sources/active-roof/ImageGen_Roof_Palette.png':(O/'sources/ImageGen_Roof_Palette.png').read_bytes()}
 updates['atlas-plan.json']=json.dumps(plan,indent=2).encode()
 for rel,data in updates.items():payload[cur/rel]=data;payload[snap/rel]=data
 payload[LIB/'CURRENT.json']=json.dumps({'release':release,'current':'Current','snapshot':'Releases/'+release,'manifest':'Current/library.json'},indent=2).encode()
 for folder in ('Level 2/modern/revision-06-ae','BAKERS/Bakery/modern/revision-04-ae'):payload[ART/folder/'textures'/(BID+'.png')]=(O/'textures'/(BID+'.png')).read_bytes()
 payload[runtime]=(O/'staged/Textures'/(BID+'.dds')).read_bytes();backup=O/'publication-backup';backup.mkdir(exist_ok=True);rows=[]
 for i,(p,data) in enumerate(payload.items()):
  row={'destination':str(p),'before':sha(p) if p.exists() else None,'after':hashlib.sha256(data).hexdigest()}
  if p.exists():q=backup/f'{i:03}-{p.name}';shutil.copy2(p,q);row['backup']=str(q)
  rows.append(row)
 dump(backup/'manifest.json',rows)
 for row,(p,data) in zip(rows,payload.items()):assert (sha(p) if p.exists() else None)==row['before'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
 dump(O/'publication-report.json',{'installed':True,'files':rows,'release':release,'texture_only':True});sys.path.insert(0,str(ROOT/'project/tools/art/modern_windmill'));import modular_v9_native as n;n.cache(O)
 assert all(sha(r['destination'])==r['after'] for r in rows);assert all(sha(MOD/'Assets'/name)==value for name,value in base['ASTs'].items());print('ACTIVE_ROOF_INSTALLED',release,flush=True)
def sheet():
 from PIL import Image,ImageDraw,ImageFont
 page=Image.new('RGB',(2400,1270),(25,29,35));draw=ImageDraw.Draw(page);font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',32)
 for i,(ident,title) in enumerate([('CSC_BAKERS_Bakery_2','Historical — active palette / bread cart'),('CSC_BAKERS_Bakery_Modern_2','Modern — matched palette / delivery truck')]):
  im=Image.open(O/'review'/ident/'render.png').convert('RGBA');page.paste(im,(i*1200,60),im);draw.text((i*1200+30,14),title,font=font,fill=(235,237,240))
 page.save(O/'Bakery-Historical-Modern-Active-Day.png')
if __name__=='__main__':render() if '--' in sys.argv else globals()[sys.argv[1]]()
