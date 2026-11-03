"""Pack ImageGen painting and derive registered, material-specific relief."""
import sys,json,shutil
from pathlib import Path
import numpy as np
from PIL import Image,ImageFilter
from modular_v9 import ART,texname,sha,dump
O=Path.home()/'Desktop/Codex/modern-kit-refinement-20261027'
GEN=Path.home()/'.codex/generated_images/01a17705-552a-7272-bb5e-272856a3d4c2'
SLOTS=[51,53,54,55,52,7,48,35,19,27,2,32]
def normal(h,strength):
 gy,gx=np.gradient(h);n=np.stack((-gx*strength,gy*strength,np.ones_like(h)),axis=-1);n/=np.linalg.norm(n,axis=2,keepdims=True)
 return Image.fromarray(np.uint8(np.clip((n+1)*127.5,0,255)))
def blur(a,s):return np.asarray(Image.fromarray(np.float32(a),mode='F').filter(ImageFilter.GaussianBlur(s)))
def smooth(a,s):
 lo,hi=a.min(),a.max()
 if hi-lo<1e-8:return a
 return np.asarray(Image.fromarray(np.uint8((a-lo)/(hi-lo)*255)).filter(ImageFilter.GaussianBlur(s)))/255*(hi-lo)+lo
def grain(p):
 a=np.asarray(p,dtype=float);l=a.mean(2)/255
 # Select dark directional grain relative to its local underpaint, not global brightness.
 grooves=np.clip((smooth(l,4)-l-.015)*6,0,1)
 return smooth(-grooves,.6)
def patch(im,t,grid=4):
 x,y=t%grid*128,t//grid*128;return im.crop((x,y,x+128,y+128))
def put(im,t,p,grid=4):im.paste(p,(t%grid*128,t//grid*128))
bg=Image.open(GEN/'exec-63c576d3-ac65-4c48-b257-65f8c142d8f3.png').convert('RGB')
pg=Image.open(GEN/'exec-5180f891-f72b-4b84-ace2-98ae7860691c.png').convert('RGB')
for kind,gen in [('building',bg),('props',pg)]:
 root=O/'libraries'/kind;shutil.copy2(GEN/('exec-63c576d3-ac65-4c48-b257-65f8c142d8f3.png' if kind=='building' else 'exec-5180f891-f72b-4b84-ace2-98ae7860691c.png'),root/'sources/painted-refinement.png')
 maps={ch:Image.open(root/'textures'/(texname(kind,ch)+'.png')).convert('RGB') for ch in ('B','N','G','M')}
 original={ch:im.copy() for ch,im in maps.items()}
 if kind=='props':
  for ch in maps:maps[ch]=Image.new('RGB',(1024,1024),(128,128,255) if ch=='N' else (128,128,128) if ch=='B' else (0,0,0))
 tiles=[0,1,2,4,5,7,8,11,13] if kind=='building' else list(range(12))
 for t in tiles:
  dest=t if kind=='building' else t//4*8+t%4;old=t if kind=='building' else SLOTS[t]
  if kind=='building':
   x0=round(t%4*bg.width/4);x1=round((t%4+1)*bg.width/4);y0=round(t//4*bg.height/4);y1=round((t//4+1)*bg.height/4)
  else:
   xs=[0,363,724,1086,1448];ys=[0,333,686,1086];x0,x1=xs[t%4:t%4+2];y0,y1=ys[t//4:t//4+2]
  p=gen.crop((x0,y0,x1,y1)).resize((128,128),Image.Resampling.LANCZOS)
  if kind=='building' and t==0:
   # Restore approved eight bricks per period (generated painting has five).
   repeat=gen.crop((0,39,125,118));p=Image.new('RGB',(128,128))
   for yy in range(4):
    for xx in range(4):p.paste(repeat.resize((32,32),Image.Resampling.LANCZOS),(xx*32,yy*32))
  if kind=='props' and t==11:p=patch(Image.open(O/'libraries/building/textures/CSC_Atlas_Modern_B_BAKERS.png'),1)
  # Calm the most conspicuous chips without removing the painted structural definition.
  if not (kind=='building' and t==0) and not(kind=='props' and t in (8,9,10,11)):
   p=Image.blend(patch(original['B'],old,4 if kind=='building' else 8),p,.70)
  put(maps['B'],dest,p,4 if kind=='building' else 8)
  for ch in ('N','G','M'):put(maps[ch],dest,patch(original[ch],old,4 if kind=='building' else 8),4 if kind=='building' else 8)
  if kind=='building' and t==0:
   a=np.asarray(p,dtype=float);mortar=(a[:,:,0]<155)&(a[:,:,1]<125);h=smooth(1-mortar.astype(float),.7);n=normal(h,2.8)
  elif (kind=='building' and t==2) or (kind=='props' and t==0):
   a=np.asarray(p,dtype=float);v=a.mean(2).mean(0);centres=[i for i in range(2,126) if v[i]<=v[i-1] and v[i]<v[i+1] and v[i]<np.percentile(v,35)]
   x=np.arange(128);h=sum(np.exp(-((x-c)/.8)**2) for c in centres);h=np.tile(h,(128,1));n=normal(smooth(h,.35),2.1)
  elif (kind=='building' and t==8) or (kind=='props' and t==10):
   h=grain(p)
   if kind=='building':h[96:]=0
   n=normal(h,1.8)
  elif kind=='building' and t==1:
   a=np.asarray(patch(original['N'],old),dtype=float)/127.5-1;a[:,:,:2]*=1.65;a/=np.maximum(np.linalg.norm(a,axis=2,keepdims=True),1e-8);n=Image.fromarray(np.uint8(np.clip((a+1)*127.5,0,255)))
  else:n=None
  if n is not None:put(maps['N'],dest,n,4 if kind=='building' else 8)
 for ch,im in maps.items():im.save(root/'textures'/(texname(kind,ch)+'.png'))
 plan=json.loads((root/'atlas-plan.json').read_text());plan['artwork']='ImageGen refinement from Firaxis DIS_COM_Base_B; measured packing; registered semantic relief'
 plan['props']['slots']={str(k):SLOTS.index(v)//4*8+SLOTS.index(v)%4 for k,v in plan['props']['slots'].items()}
 plan['props']['layout']='Compact 4x3 occupied block in 8x8 page: painted metals; machinery/structure; sacks/timber/stone'
 plan['props']['previous_to_current_slots']={str(s):i//4*8+i%4 for i,s in enumerate(SLOTS)}
 plan['props'].pop('historical_layout_source',None)
 dump(root/'atlas-plan.json',plan)
 dump(root/'sources/refinement-provenance.json',{'generator':'built-in ImageGen','style_reference':'DIS_COM_Base_B.dds','B':'generated painting, cell crop/registration and restrained blend with prior accepted underpainting','N':'brick mortar semantic mask, measured roof seam locations, dark wood grain relative to local underpainting; existing registered window normals retained','sampling':'128px cells and UV local coordinates retained; eight-brick period restored'})
print('MATERIALS_READY')
