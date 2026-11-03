from pathlib import Path
from PIL import Image,ImageDraw
import json,math,shutil,collections
ROOT=Path(__file__).resolve().parents[4];A=Path.home()/'Desktop/Working Files/3D Art';O=Path.home()/'Desktop/Codex/modern-cafe-v1-20261029'
for d in ('textures','sources','bakes','review','models'): (O/d).mkdir(parents=True,exist_ok=True)
for fam in ('CSC_Buildings_Modern','CSC_Props_Modern','CSC_Buildings_Emissive'):
 for p in (A/'Textures'/fam/'Current/textures').glob('*.png'):shutil.copy2(p,O/'textures'/p.name)
m=json.loads((O/'historical-mesh.json').read_text());vs=m['vertices'];c=math.cos(math.radians(28.26));s=math.sin(math.radians(28.26));local=[(c*x-s*y,s*x+c*y,z) for x,y,z in vs]
print('local bounds',[(min(p[a] for p in local),max(p[a] for p in local)) for a in range(3)])
print('planes',[(a,collections.Counter(round(p[a],1) for p in local).most_common(20)) for a in range(3)])
for mi in range(2):
 fs=[f for f in m['faces'] if f['mat']==mi];uv=[u for f in fs for u in f['uv']];pts=[local[i] for f in fs for i in f['v']]
 print('material',mi,'faces',len(fs),'uvbounds',[(min(p[a] for p in uv),max(p[a] for p in uv)) for a in range(2)])
 if mi==1:print('interiorfaces',[{'v':[local[i] for i in f['v']],'uv':f['uv']} for f in fs[:8]])
historical=Image.open(A/'Textures/CSC_Atlas_B_BAKERS.dds').convert('RGB');historical.save(O/'sources/historical-atlas.png');historical.crop((0,512,512,1024)).resize((1024,1024)).save(O/'sources/L3_historical_paint.png')
uv=Image.new('RGB',(1024,1024),'#222222');d=ImageDraw.Draw(uv)
for f in m['faces']:
 pts=[(u*2048,(.5-v)*2048) for u,v in f['uv']];d.polygon(pts,outline='#ffffff')
uv.save(O/'sources/L3_UV_Guide.png')
# Fixed 4x4 interior grid. Existing Bakery 3 cells followed by Café 3 cells.
manifest={'status':'candidate; not installed','interior_atlas':{'B':1024,'N':1024,'E':512,'grid':[4,4],'UV1':'fixed cells; 6px padding at 1024','UV3':'same normalized mapping','slots':{'0':'Bakery rear shelves','1':'Bakery side wall','2':'Bakery floor','4':'Cafe rear espresso bar','5':'Cafe side reading wall','6':'Cafe floor'},'reserved':[3,7,8,9,10,11,12,13,14,15]},'building_L3':'bottom-left quadrant; preserve historical UV patch layout and footprint','concept':'C_Garden_Cafe','interior_geometry':'open five-face room support only; no furnishings geometry','props_surface_cells':{'40':'espresso face','41':'pastry cabinet face','42':'cream and green coffee van side','43':'coffee cup emblem'},'AO_candidate':{'building':[0,1024,512,1536],'shelter':[512,1024,768,1280],'counter':[0,512,256,768],'van':[0,768,512,1024],'parasol':[256,512,384,640]}}
(O/'atlas-plan.json').write_text(json.dumps(manifest,indent=2))
# Orthographic panel projection guide: the actual 3-face room skin design.
g=Image.new('RGB',(1536,1024),'#e9dbbb');d=ImageDraw.Draw(g)
for col in range(3):
 x=col*512
 d.rectangle((x+8,8,x+503,503),fill=('#e8ddbf','#ded8bd','#b7aa8a')[col])
 if col<2:
  for y in (128,267):d.rectangle((x+20,y,x+490,y+14),fill='#77725a')
  if col==0:
   d.rectangle((x+38,316,x+474,480),fill='#60715b');d.rectangle((x+44,292,x+468,319),fill='#d0ac75')
   for xx in (130,245,365):d.rectangle((x+xx-25,236,x+xx+25,264),fill='#f0e5c5')
  else:
   d.rectangle((x+170,338,x+340,364),fill='#a17b4f');d.ellipse((x+204,310,x+308,344),fill='#e9d3a6')
 else:
  for y in range(24,512,80):d.line((x,y,x+511,y),fill='#867959',width=3)
  for xx in range(x+10,x+512,128):d.line((xx,0,xx,511),fill='#867959',width=3)
# Bottom row espresso machine fascia, pastry case fascia, cup emblem.
d.rectangle((12,524,499,1008),fill='#355043');d.rectangle((35,541,477,608),fill='#d9d6ba');d.rectangle((50,652,465,932),fill='#233b34')
for x in (148,363):d.rectangle((x-32,623,x+32,699),fill='#bbbfb6');d.ellipse((x-38,790,x+38,863),fill='#f5e7c4');d.rectangle((x-38,824,x+38,877),fill='#e6d7b4')
d.rectangle((36,945,477,981),fill='#b4b6a8')
d.rectangle((528,528,1008,1008),fill='#735637');d.rectangle((552,550,984,966),fill='#d6ba80')
for y in (645,785,925):
 d.rectangle((554,y,982,y+13),fill='#786c50')
 for x in (610,760,910):d.ellipse((x-42,y-65,x+42,y-5),fill='#c58c41')
d.rectangle((1032,520,1528,1016),fill='#3d5544');d.rounded_rectangle((1158,661,1378,871),radius=35,fill='#ead9b0');d.ellipse((1327,686,1439,809),outline='#ead9b0',width=22);d.arc((1110,845,1440,924),0,180,fill='#ead9b0',width=15)
g.save(O/'sources/Interior_Prop_Projection_Guide.png');print('PREPARED')
