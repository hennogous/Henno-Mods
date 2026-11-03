"""Explicit painted-feature relief profiles, measured on final packed Stage3 B."""
from pathlib import Path
import sys,json
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT/'project/tools/art/modern_windmill'))
from correct_modern_normals import X,Y,S,box,line,normals,ramp
O=Path.home()/'Desktop/Codex/modern-level2-v1-20261028'
heights={i:np.zeros((S,S)) for i in range(16)};coverage={i:(32,32) for i in range(16)};registration={}
for slot,ys,seeds,depth in [(0,[-1,15,31,47,64,80,97,112,128],[[17,49,80,112],[8,39,68,96,126]],.25),(1,[-1,33,66,98,129],[[39,94],[16,67,116]],.40),(7,[-1,33,67,100,129],[[30,95],[15,77]],.32)]:
 a=np.asarray(Image.open(O/'patches'/f'{slot:02}_B.png'),dtype=float).mean(2);coords=[]
 for row,(y0,y1) in enumerate(zip(ys,ys[1:])):
  stripe=a[max(0,int(y0+5)):min(128,int(y1-4))].mean(0);xs=[]
  for seed in seeds[row%2]:
   lo=max(1,seed-5);hi=min(127,seed+6);xs.append(lo+int(np.argmin(stripe[lo:hi])))
  xs=[-32]+xs+[160];coords.append(xs)
  for x0,x1 in zip(xs,xs[1:]):heights[slot]=np.maximum(heights[slot],depth*box(x0+.35,y0+.4,x1-.35,y1-.4,.7))
 registration[str(slot)]={'horizontal_joints':ys,'vertical_joints_per_row':coords}
for x in (1.7,21.3,42.8,65.3,87.4,108.6):heights[2]=np.maximum(heights[2],.42*(1-ramp((abs(X-x)-.18)/.85)))
coverage[2]=(44,55)
# Cream frame and four recessed glazing panels measured after generated layout was frozen.
h=.32*box(10,6,120,124,.8)
for x0,x1 in [(20,60),(68,109)]:
 for y0,y1 in [(15,54),(63,101)]:h-=.92*box(x0,y0,x1,y1,.8)
h+=.25*box(10,109,120,122,.9);heights[5]=h;coverage[5]=(16,20)
# Six-pane green shopfront, each pane recessed; kickplate remains a flat painted area.
h=.18*box(12,6,114,129,.7)
for x0,x1 in [(24,60),(66,103)]:
 for y0,y1 in [(15,40),(47,71),(78,101)]:h-=.64*box(x0,y0,x1,y1,.8)
heights[6]=h;coverage[6]=(20,28)
for slot in (4,8,9):
 for p in [[(0,19),(24,20),(48,18),(78,20),(104,18),(128,19)],[(0,45),(24,43),(48,46),(79,45),(105,47),(128,45)],[(0,87),(24,88),(48,85),(79,88),(105,87),(128,86)]]:heights[slot]-=.025*line(p,.8)
 if slot in (8,9):
  for yy in ([47,95] if slot==8 else [29,60,93]):heights[slot]-=.06*line([(-2,yy),(130,yy)],.7)
 coverage[slot]=(48,12)
for c in (42,85):heights[12]-=.16*line([(c,0),(c,128)],.8)+.16*line([(0,c),(128,c)],.8)
(O/'height').mkdir(exist_ok=True)
atlas=Image.open(O/'textures/CSC_Atlas_Modern_N.png').convert('RGB');sheet=Image.new('RGB',(6*256,800));d=ImageDraw.Draw(sheet)
for i,h in heights.items():
 np.save(O/'height'/f'{i:02}.npy',h.astype('float32'));n=normals(h,coverage[i]);n.save(O/'patches'/f'{i:02}_N.png');atlas.paste(n,(512+i%4*128,i//4*128))
 if i in (0,1,2,5,6,7):
  col=(0,1,2,5,6,7).index(i);b=Image.open(O/'patches'/f'{i:02}_B.png');hp=Image.fromarray(np.uint8((h-h.min())/max(.0001,h.max()-h.min())*255)).convert('RGB')
  for j,p in enumerate((b,hp,n)):sheet.paste(p.resize((256,256)),(col*256,32+j*256))
  d.text((col*256+5,8),str(i)+' B / authored height / N',fill='white')
atlas.save(O/'textures/CSC_Atlas_Modern_N.png');sheet.save(O/'Registered_Relief.png')
for ch in ('G','M'):
 a=Image.open(O/'textures'/('CSC_Atlas_Modern_'+ch+'.png')).convert('RGB')
 for i in range(16):
  value=(60 if i in (2,6,14) else 22) if ch=='G' else (35 if i==14 else 0)
  a.paste(Image.new('RGB',(128,128),(value,)*3),(512+i%4*128,i//4*128))
 a.save(O/'textures'/('CSC_Atlas_Modern_'+ch+'.png'))
(O/'relief-registration.json').write_text(json.dumps({'structural_joints':registration,'method':'Explicit profiles at measured final-paint feature coordinates; no general brightness or noise displacement','coverage':coverage},indent=2))
print('REGISTERED_RELIEF_READY')
