"""Pack generated B and explicitly registered structural relief into candidate cells."""
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
import json,shutil,sys
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT/'project/tools/art/modern_windmill'))
def normals(height,world):
 # Pixel spacing must use THIS height array's dimensions. The older helper's
 # fixed 512px spacing makes 128px inputs four times too strong.
 dy,dx=np.gradient(height,world[1]/height.shape[0],world[0]/height.shape[1])
 vec=np.stack((-dx,dy,np.ones_like(height)),axis=-1);vec/=np.linalg.norm(vec,axis=2,keepdims=True)
 return Image.fromarray(np.uint8(np.clip((vec+1)*127.5,0,255)))
O=Path.home()/'Desktop/Codex/modern-bakery-v1-20261028'
source=Path.home()/'.codex/generated_images/01a17705-552a-7272-bb5e-272856a3d4c2/exec-9c5074c9-1441-4702-9aa4-447f26895a87.png'
shutil.copy2(source,O/'sources/Bakery_Generated_B.png');im=Image.open(source).convert('RGB')
maps={c:Image.open(O/'textures'/f'CSC_Props_Modern_01_{c}.png').convert('RGB') for c in ('B','N','G','M')}
for i,slot in enumerate(range(26,32)):
 patch=im.crop((i%3*512,i//3*512,i%3*512+512,i//3*512+512)).resize((122,122),Image.Resampling.LANCZOS)
 tile=Image.new('RGB',(128,128));tile.paste(patch,(3,3))
 for j in range(3):
  tile.paste(patch.crop((0,0,122,1)),(3,j));tile.paste(patch.crop((0,121,122,122)),(3,125+j))
  tile.paste(tile.crop((3,0,4,128)),(j,0));tile.paste(tile.crop((124,0,125,128)),(125+j,0))
 h=Image.new('L',(512,512),128);d=ImageDraw.Draw(h)
 if slot==26:
  for y in (51,248):
   d.rounded_rectangle((42,y,435,y+168),radius=7,fill=175)
   d.rectangle((63,y+20,414,y+116),fill=65)
   d.rounded_rectangle((76,y+121,398,y+144),radius=5,fill=215)
  d.rectangle((63,441,425,479),fill=62)
  for y in (102,177,284,356):d.ellipse((448,y-10,469,y+10),fill=180)
 elif slot==27:
  d.rectangle((24,24,488,488),fill=170);d.rectangle((41,41,471,471),fill=108)
  for y in (112,256,400):
   for x in (122,260,408):d.ellipse((x-46,y-48,x+46,y+48),fill=190)
 elif slot==28:
  for x in (64,128,192,256,320,384,448):d.line((x,0,x,512),fill=140,width=3)
  for y in (10,492):d.line((0,y,512,y),fill=149,width=4)
 elif slot==29:
  d.polygon([(256,9),(457,129),(457,385),(256,504),(52,386),(52,130)],fill=184)
  d.polygon([(256,30),(438,142),(438,370),(256,482),(72,370),(72,142)],fill=128)
 elif slot==30:
  d.rectangle((23,23,489,489),fill=188);d.rectangle((42,42,470,470),fill=70)
  d.rectangle((62,62,450,450),fill=110)
 else:
  for pts in [[(84,192),(422,89),(371,134),(119,210)],[(77,292),(432,214),(382,250),(108,312)],[(77,418),(432,337),(393,372),(110,439)]]:d.polygon(pts,fill=80)
 h=h.filter(ImageFilter.GaussianBlur(3)).resize((122,122),Image.Resampling.LANCZOS)
 height=np.pad((np.asarray(h,dtype=float)-128)/127*((.55,.18,.07,.14,.26,.045)[i]),3,mode='edge')
 coverage=[(22,27),(12,12),(46,22),(14,14),(12,10),(7,5)][i]
 n=normals(height,coverage)
 x=slot%8*128;y=slot//8*128
 maps['B'].paste(tile,(x,y));maps['N'].paste(n,(x,y))
 maps['G'].paste((int([95,42,13,25,110,26][i]),)*3,(x,y,x+128,y+128))
 maps['M'].paste((int([110,30,0,0,145,0][i]),)*3,(x,y,x+128,y+128))
 tile.save(O/'sources'/f'{slot}_B.png');n.save(O/'sources'/f'{slot}_N.png');np.save(O/'sources'/f'{slot}_height.npy',height)
for c,im in maps.items():im.save(O/'textures'/f'CSC_Props_Modern_01_{c}.png')
(O/'sources/painting-provenance.txt').write_text('Built-in ImageGen; Projection_Guide.png is layout authority and approved Bakery concept is palette authority. Six cells: oven, tray of bread, striped canopy, bread sign, empty tray, crust. Full request is retained in conversation. B packed with gutters; structural normals traced from generated artwork, not luminance/noise. Candidate only; current libraries untouched.\n')
print('BAKERY_MATERIALS_READY')
