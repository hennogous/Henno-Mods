"""Deterministic Bakery shared-atlas additions; old occupied pixels are immutable."""
from pathlib import Path
import json,shutil,hashlib,sys,math,os
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(r'C:\Users\Shadow\Desktop\Codex\Bakery-redo-20261016\production')
LIB=Path(r'C:\Users\Shadow\Desktop\Working Files\3D Art\Textures\CSC_Props')
STAGE=OUT/'atlas-release'
SOURCE=Path(r'C:\Users\Shadow\Desktop\Working Files\3D Art\BAKERS\Bakery\revision-01-prop-kit')
RELEASE='2026-10-16_Shared_01_r025'
if os.environ.get('CSC_BAKERY_REVISION')=='02':
 OUT=OUT/'revision02';STAGE=OUT/'atlas-release';SOURCE=SOURCE.parent/'revision-02-prop-kit';RELEASE='2026-10-16_Shared_01_r026'
if os.environ.get('CSC_BAKERY_REVISION')=='03':
 OUT=OUT/'revision03';STAGE=OUT/'atlas-release';SOURCE=SOURCE.parent/'revision-03-prop-kit';RELEASE='2026-10-16_Shared_01_r027'

if os.environ.get('CSC_BAKERY_REVISION')=='04':
 OUT=OUT/'revision04';STAGE=OUT/'atlas-release';SOURCE=SOURCE.parent/'revision-04-prop-kit';RELEASE='2026-10-17_Shared_01_r028'

if os.environ.get('CSC_BAKERY_REVISION')=='05':
 OUT=OUT/'revision05';STAGE=OUT/'atlas-release';SOURCE=SOURCE.parent/'revision-05-prop-kit';RELEASE='2026-10-17_Shared_01_r029'

if os.environ.get('CSC_BAKERY_REVISION')=='06':
 OUT=OUT/'revision06';STAGE=OUT/'atlas-release';SOURCE=SOURCE.parent/'revision-06-prop-kit';RELEASE='2026-10-17_Shared_01_r030'

if os.environ.get('CSC_BAKERY_REVISION')=='07':
 OUT=OUT/'revision07';STAGE=OUT/'atlas-release';SOURCE=SOURCE.parent/'revision-07-prop-kit';RELEASE='2026-10-17_Shared_01_r031'

if os.environ.get('CSC_BAKERY_REVISION')=='08':
 OUT=OUT/'revision08';STAGE=OUT/'atlas-release';SOURCE=SOURCE.parent/'revision-08-prop-kit';RELEASE='2026-10-17_Shared_01_r034'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 from PIL import Image,ImageDraw,ImageFilter
 OUT.mkdir(parents=True,exist_ok=True);SOURCE.mkdir(parents=True,exist_ok=True)
 assert not STAGE.exists();shutil.copytree(LIB/'Current',STAGE)
 (OUT/'live-atlas-baseline.json').write_text(json.dumps({p.relative_to(LIB/'Current').as_posix():sha(p) for p in (LIB/'Current').rglob('*') if p.is_file()},indent=2))
 m=json.loads((STAGE/'atlas/manifest.json').read_text());old=json.loads(json.dumps(m));n=240
 specs=[('bakery_brick',34),('bakery_light_stone',35),('bakery_dark_stone',36),('bakery_logs',37),('bakery_fire',59),('bakery_canopy',29),('bakery_dough',60),('bakery_round_crust',61),('bakery_long_crust',62),('bakery_wicker',8),('bakery_flour',63)]
 crops={'bakery_light_stone':(205,256,368,465),'bakery_dark_stone':(0,256,205,465),'bakery_logs':(607,0,785,253),'bakery_fire':(819,812,880,860)}
 oldroot=LIB.parent
 for name,slot in specs:
  assert slot not in [r['slot'] for r in m['regions']]
  b=Image.new('RGB',(n,n),(197,153,91));height=Image.new('L',(n,n),128);d=ImageDraw.Draw(b);h=ImageDraw.Draw(height)
  if name in crops:
   b=Image.open(oldroot/'CSC_Atlas_Props_B.png').convert('RGB').crop(crops[name]).resize((n,n),Image.Resampling.LANCZOS)
  elif name=='bakery_brick':
   b.paste((109,69,43),(0,0,n,n));d=ImageDraw.Draw(b)
   for row in range(8):
    for col in range(-1,16):
     x=col*16+(row%2)*8;y=row*30
     shade=(row*7+col*11)%17
     d.rounded_rectangle((x+1,y+1,x+15,y+28),radius=2,fill=(169+shade,82+shade//2,44+shade//3))
     h.rectangle((x+1,y+1,x+15,y+28),fill=158)
  elif name=='bakery_canopy':
   for x in range(n):
    c=(238,220,157) if x//40%2 else (238,235,214)
    for y in range(n):b.putpixel((x,y),tuple(max(0,v-int(8*math.sin(y/n*math.pi))) for v in c))
   d=ImageDraw.Draw(b)
   for x in range(0,n,40):d.line((x,0,x,n),fill=(172,151,101),width=1)
  elif name=='bakery_wicker':
   b.paste((106,65,29),(0,0,n,n));d=ImageDraw.Draw(b)
   for y in range(0,n,16):
    for x in range(-16,n,28):
     xx=x+(14 if y//16%2 else 0);d.rounded_rectangle((xx+1,y+2,xx+26,y+13),radius=3,fill=(174+(x+y)%17,126+(x+y)%13,64));h.rectangle((xx+1,y+2,xx+26,y+13),fill=170)
  elif name=='bakery_dough':
   yy,xx=np.mgrid[:n,:n];v=6*np.sin(xx*.06)*np.cos(yy*.04);a=np.zeros((n,n,3));a[:]=(225,207,156);a+=v[:,:,None];b=Image.fromarray(a.astype('uint8'))
  elif name in ('bakery_round_crust','bakery_long_crust'):
   yy,xx=np.mgrid[:n,:n];radius=((xx-120)**2+(yy-120)**2)**.5/170;v=-28*radius+5*np.sin(xx*.04)*np.cos(yy*.07);a=np.zeros((n,n,3));a[:]=(206,139,62);a+=v[:,:,None];b=Image.fromarray(np.clip(a,0,255).astype('uint8'));d=ImageDraw.Draw(b)
   lines=[(55,85,170,145),(70,45,190,105),(40,130,160,190)] if name.endswith('long_crust') else [(60,60,180,180),(180,60,60,180)]
   for line in lines:d.line(line,fill=(128,68,24),width=16);d.line(tuple(v-2 if i%2 else v for i,v in enumerate(line)),fill=(242,206,134),width=10);h.line(line,fill=70,width=13)
  elif name=='bakery_flour':
   b.paste((240,231,204),(0,0,n,n))
  ha=np.array(height,dtype=float);gy,gx=np.gradient(ha/255);norm=np.dstack((-gx*2,-gy*2,np.ones_like(gx)));norm/=np.linalg.norm(norm,axis=2)[:,:,None]
  maps={'B':b,'N':Image.fromarray(((norm*.5+.5)*255).astype('uint8')),'G':Image.new('RGB',(n,n),(24,)*3),'M':Image.new('RGB',(n,n),(0,)*3)}
  sources={}
  for k,im in maps.items():
   p=STAGE/'atlas/sources'/f'{name}_{k}.png';im.save(p);sources[k]=f'sources/{p.name}'
  x,y=slot%8*128,slot//8*128;m['regions'].append(dict(id=max(r['id'] for r in m['regions'])+1,name=name,family='bakery',slot=slot,bounds=[x+4,y+4,x+124,y+124],sources=sources))
  for k,im in maps.items():
   path=STAGE/'textures'/f'CSC_Props_Shared_01_{k}.png';atlas=Image.open(path).convert('RGB');patch=im.resize((120,120),Image.Resampling.LANCZOS)
   arr=np.pad(np.array(patch),((4,4),(4,4),(0,0)),mode='edge');atlas.paste(Image.fromarray(arr),(x,y));atlas.save(path)
   master=STAGE/'atlas'/f'CSC_Props_Shared_01_v2_{k}_Master2048.png'
   if master.exists():a=Image.open(master);a.paste(Image.fromarray(arr).resize((256,256),Image.Resampling.LANCZOS),(x*2,y*2));a.save(master)
 m['reserved_slots']=[s for s in range(64) if s not in [r['slot'] for r in m['regions']]]
 (STAGE/'atlas/manifest.json').write_text(json.dumps(m,indent=2))
 op=Image.new('L',(1024,1024),255);mask=Image.new('L',(120,120),0);d=ImageDraw.Draw(mask)
 rng=np.random.default_rng(491)
 for _ in range(180):
  x,y=rng.normal(60,25,2);r=float(rng.uniform(.7,4));d.ellipse((x-r,y-r,x+r,y+r),fill=int(rng.uniform(75,220)))
 d.ellipse((24,30,89,88),fill=125);mask=mask.filter(ImageFilter.GaussianBlur(.8));op.paste(mask,(900,900));op.save(STAGE/'textures/CSC_Props_Shared_01_O.png')
 for k in 'BNGM':
  a=Image.open(LIB/'Current/textures'/f'CSC_Props_Shared_01_{k}.png').convert('RGB');b=Image.open(STAGE/'textures'/f'CSC_Props_Shared_01_{k}.png').convert('RGB')
  for r in old['regions']:
   x,y=r['slot']%8*128,r['slot']//8*128;assert a.crop((x,y,x+128,y+128)).tobytes()==b.crop((x,y,x+128,y+128)).tobytes();assert op.crop((x,y,x+128,y+128)).getextrema()==(255,255)
 (OUT/'atlas-prepare-report.json').write_text(json.dumps(dict(new_regions=specs,old_occupied_preserved=True,old_opacity_solid_white=True),indent=2))
 shutil.copytree(STAGE/'textures',SOURCE/'textures',dirs_exist_ok=True)
 print('ATLAS STAGED',RELEASE)
if __name__=='__main__':main()
