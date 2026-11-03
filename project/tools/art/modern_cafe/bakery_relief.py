"""Registered relief for existing Bakery paintings, without changing their colour."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
import numpy as np,shutil
O=Path.home()/'Desktop/Codex/modern-cafe-v1-20261029';A=Path.home()/'Desktop/Working Files/3D Art';p=O/'textures/CSC_Interiors_Modern_N.png';atlas=Image.open(p).convert('RGB');unchanged=atlas.crop((0,256,1024,1024)).tobytes()
for slot in range(3):
 h=Image.new('L',(512,512),0);d=ImageDraw.Draw(h)
 if slot==0:
  for y in (146,282,434):d.rounded_rectangle((18,y,491,y+18),radius=4,fill=235)
  for rect in ((32,87,257,145),(37,240,207,281),(218,237,316,282),(190,371,306,433)):d.rounded_rectangle(rect,radius=10,fill=170)
  for rect in ((44,42,144,101),(110,35,214,103),(172,42,249,109),(270,87,382,145),(49,215,110,251),(112,216,165,253),(154,217,205,256),(224,213,301,247)):d.ellipse(rect,fill=145)
  for rect in ((394,60,472,145),(414,226,472,281),(397,334,472,433),(315,365,386,432)):d.rounded_rectangle(rect,radius=12,fill=180)
  for y in (350,381,411):d.rounded_rectangle((36,y,181,y+22),radius=10,fill=160)
  for x,y,X,Y in ((205,328,226,382),(241,315,263,385),(275,320,303,383)):d.ellipse((x,y,X,Y),fill=180)
  d.rectangle((339,223,382,275),fill=135);d.ellipse((317,197,412,221),fill=165)
 elif slot==1:
  d.rectangle((0,281,511,511),fill=100)
  for row,(y,Y) in enumerate(zip((281,313,365,420,475),(313,365,420,475,512))):
   d.line((0,Y,511,Y),fill=5,width=3)
   for x in range(69 if row%2==0 else 10,512,99):d.line((x,y,x,Y),fill=5,width=3)
  d.rounded_rectangle((79,46,295,76),radius=3,fill=145);d.rounded_rectangle((75,151,143,249),radius=10,fill=170);d.rectangle((105,74,117,160),fill=140)
  d.rectangle((347,84,456,225),fill=135);d.rectangle((369,110,447,226),fill=180)
  d.polygon([(216,92),(245,95),(255,255),(230,277),(203,237)],fill=105)
 else:
  d.rectangle((0,0,511,511),fill=100)
  for y in (91,170,237,318,402):d.line((10,y,500,y),fill=0,width=4)
 a=np.asarray(h.filter(ImageFilter.GaussianBlur(1.3)),float)/255*(.75 if slot<2 else .18);dy,dx=np.gradient(a,30/512,30/512);n=np.stack((-dx,dy,np.ones_like(dx)),axis=-1);n/=np.linalg.norm(n,axis=-1,keepdims=True);patch=Image.fromarray(np.uint8((n*.5+.5)*255)).resize((256,256),Image.Resampling.LANCZOS)
 # Height coordinates were traced on the padded 512px view of each 256px cell.
 atlas.paste(patch,(slot*256,0));h.save(O/'sources'/f'Bakery_Interior_{slot}_Relief.png')
assert atlas.crop((0,256,1024,1024)).tobytes()==unchanged;atlas.save(p)
folders=[A/'Textures/CSC_Interiors_Modern/Candidates/2026-10-29_Garden_v001/textures',A/'Level 3/modern/revision-01-garden/textures',A/'BAKERS/Cafe/modern/revision-01-garden/textures',A/'Level 2/modern/revision-07-interior-atlas-preview/textures',A/'BAKERS/Bakery/modern/revision-05-interior-atlas-preview/textures']
for folder in folders:shutil.copy2(p,folder/p.name)
print('BAKERY_RELIEF_ADDED; CAFE_NORMALS_AND_ALL_B_E_PIXELS_UNCHANGED')
