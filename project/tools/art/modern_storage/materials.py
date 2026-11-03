"""Reuse registered family materials; add painted storage details and semantic relief."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
import numpy as np,json,shutil
O=Path.home()/'Desktop/Codex/modern-storage-v1-20261029';T=O/'textures'
src=Path.home()/'.codex/generated_images/01a17705-552a-7272-bb5e-272856a3d4c2/exec-13ea4a20-a631-42fd-bf27-729d7b49d9f9.png'
shutil.copy2(src,O/'sources/Storage_Painted_Details.png');sheet=Image.open(src).convert('RGB').resize((1024,1024))
def rect(i,n=4,size=128,off=(512,512)):
 x=off[0]+i%n*size;y=off[1]+i//n*size;return x,y,x+size,y+size
def renorm(im):
 n=np.asarray(im,float)/127.5-1;n/=np.maximum(np.linalg.norm(n,axis=-1,keepdims=True),1e-8);return Image.fromarray(np.uint8(np.clip((n+1)*127.5,0,255)))
def normal(h,span=28,relief=.7):
 a=np.asarray(h.filter(ImageFilter.GaussianBlur(1.4)),float)/255*relief;dy,dx=np.gradient(a,span/h.height,span/h.width);n=np.stack((-dx,dy,np.ones_like(dx)),axis=-1);n/=np.linalg.norm(n,axis=-1,keepdims=True);return Image.fromarray(np.uint8((n+1)*127.5))
def pad(im,size=128):
 # Edge extrusion, never resize an unpadded image into a differently scaled chart.
 a=np.asarray(im.resize((size-6,size-6),Image.Resampling.LANCZOS));return Image.fromarray(np.pad(a,((3,3),(3,3),(0,0)),mode='edge'))
# Map storage materials from accepted family patches, preserving N/G/M correspondence.
mapping={0:((512,0),0),1:((512,0),1),2:((0,0),2),3:((0,0),4),4:((512,0),4),7:((512,0),10),8:((0,0),8),9:((512,0),13),10:((512,0),8),11:((0,0),11)}
for ch in ('B_BAKERS','N','G','M','O'):
 p=T/f'CSC_Atlas_Modern_{ch}.png';im=Image.open(p).convert('RGB');source=im.copy()
 for slot,(off,s) in mapping.items():
  tile=source.crop(rect(s,off=off))
  if ch=='B_BAKERS' and slot in (2,3):
   a=np.asarray(tile,float);target=np.array((125,145,93) if slot==2 else (155,169,111));a*=target/np.maximum(a.mean(axis=(0,1)),1);tile=Image.fromarray(np.uint8(np.clip(a,0,255)))
  if ch=='O':tile=Image.new('RGB',(128,128),'white')
  im.paste(tile,rect(slot))
 for slot,index in ((6,0),(5,1)):
  if ch=='B_BAKERS':tile=pad(sheet.crop((index*512,0,(index+1)*512,512)))
  elif ch=='N':tile=Image.new('RGB',(128,128),(128,128,255))
  else:tile=Image.new('RGB',(128,128),(255 if ch=='O' else 50 if ch=='G' else 0,)*3)
  im.paste(tile,rect(slot))
 im.save(p)
# Trace construction shapes in the actual generated image; ignore chips/paint grain.
heights=[]
for i in range(4):
 h=Image.new('L',(512,512),105);d=ImageDraw.Draw(h)
 if i==0:
  d.rectangle((10,10,502,502),outline=210,width=9)
  for x in (32,254,480):d.line((x,20,x,491),fill=35,width=7)
  for y in (65,449):d.rectangle((23,y-7,490,y+8),fill=235)
  for x in (154,329):d.line((x,23,x,488),fill=75,width=2)
 elif i==1:
  d.rectangle((0,0,511,511),fill=175);d.rectangle((28,27,484,484),fill=205)
  for x0,x1 in ((49,235),(264,462)):
   for y0,y1 in ((51,239),(268,460)):d.rectangle((x0,y0,x1,y1),fill=20)
 elif i==2:
  for y in (44,182,322,464):d.rectangle((22,y-5,490,y+7),fill=220)
 else:
  d.rounded_rectangle((62,60,443,386),radius=8,fill=195);d.rounded_rectangle((108,140,397,290),radius=5,fill=125);d.ellipse((164,183,199,218),fill=230)
 h.save(O/'sources'/f'Storage_Relief_{i}.png');heights.append(h)
bn=Image.open(T/'CSC_Atlas_Modern_N.png').convert('RGB');bn.paste(renorm(pad(normal(heights[0],28,.65))),rect(6));bn.paste(renorm(pad(normal(heights[1],24,.9))),rect(5));bn.save(T/'CSC_Atlas_Modern_N.png')
for ch in ('B','N','G','M'):
 p=T/f'CSC_Props_Modern_01_{ch}.png';im=Image.open(p).convert('RGB')
 for i,slot in ((2,46),(3,47)):
  tile=pad(sheet.crop(((i%2)*512,512,(i%2+1)*512,1024))) if ch=='B' else renorm(pad(normal(heights[i],24 if i==2 else 5,.35 if i==2 else .12))) if ch=='N' else Image.new('RGB',(128,128),(90 if ch=='G' else 80,)*3)
  im.paste(tile,rect(slot,8,128,(0,0)))
 im.save(p)
# Recolour an existing calm painted metal swatch for the reusable ingredient drum.
for ch in ('B','N','G','M'):
 p=T/f'CSC_Props_Modern_01_{ch}.png';im=Image.open(p).convert('RGB');tile=im.crop(rect(3,8,128,(0,0)))
 if ch=='B':
  a=np.asarray(tile,float);a*=np.array((135,143,145))/np.maximum(a.mean(axis=(0,1)),1);tile=Image.fromarray(np.uint8(np.clip(a,0,255)))
 elif ch=='G':tile=Image.new('RGB',(128,128),(140,)*3)
 elif ch=='M':tile=Image.new('RGB',(128,128),(180,)*3)
 im.paste(tile,rect(48,8,128,(0,0)));im.save(p)
# New storage railing samples the already-painted dark green modern metal.
for ch in ('B_BAKERS','N','G','M'):
 p=T/f'CSC_Atlas_Modern_{ch}.png';im=Image.open(p).convert('RGB');prop=Image.open(T/f"CSC_Props_Modern_01_{'B' if ch=='B_BAKERS' else ch}.png");im.paste(prop.crop(rect(44,8,128,(0,0))),rect(10));im.save(p)
# Stock window softly emits only glazing. The other storage surfaces remain dark.
p=T/'CSC_Atlas_Modern_E_BAKERS.png';im=Image.open(p).convert('RGB');patch=Image.new('RGB',(256,256));tile=Image.new('RGB',(64,64));a=np.asarray(sheet.crop((512,0,1024,512)).resize((58,58)),float);mask=np.asarray(heights[1].resize((58,58)))<40;a*=mask[:,:,None]*np.array([.28,.23,.15]);tile.paste(Image.fromarray(np.uint8(a)),(3,3));patch.paste(tile,(64,64));im.paste(patch,(256,256));im.save(p)
print('MATERIALS_READY')
