"""New Stage3 authoring allocation; existing published atlas stays untouched."""
from pathlib import Path
import json,shutil
from PIL import Image,ImageDraw
O=Path.home()/'Desktop/Codex/modern-level2-v1-20261028'
ART=Path.home()/'Desktop/Working Files/3D Art'
O.mkdir(exist_ok=True);(O/'textures').mkdir(exist_ok=True)
LIB=ART/'Textures/CSC_Buildings_Modern/Current'
for p in (LIB/'textures').iterdir():shutil.copy2(p,O/'textures'/p.name)
im=Image.new('RGB',(1024,1024));d=ImageDraw.Draw(im)
colors=['#c9985b','#52606a','#7a9361','#c2bc87','#ded1ac','#d4c4a1','#29513b','#35404a','#416344','#876342','#92917f','#bac0b4','#6d6c60','#262c2b','#343b3c','#b79a67']
for i,c in enumerate(colors):
 x=i%4*256;y=i//4*256;d.rectangle((x,y,x+255,y+255),fill=c)
for slot,rows,cols in [(0,8,8),(1,4,4),(7,4,4)]:
 x=slot%4*256;y=slot//4*256
 for row in range(rows):
  yy=y+row*256/rows;d.line((x,yy,x+255,yy),fill='#7a725f' if slot==0 else '#303d43',width=3)
  for col in range(-1,cols+1):
   xx=x+(col+(row%2)*.5)*256/cols;d.line((xx,yy,xx,yy+256/rows),fill='#7a725f' if slot==0 else '#303d43',width=3)
for x in range(0,256,32):d.line((512+x,0,512+x,255),fill='#455c3d',width=4)
# The facade cards are front-on projected surfaces; strong frames belong in paint/N.
for slot,door in [(5,False),(6,True)]:
 x=slot%4*256;y=slot//4*256
 d.rectangle((x+24,y+16,x+232,y+240),fill='#aaa080' if not door else '#284933')
 for row in range(2 if not door else 3):
  for col in range(2):
   xx=x+42+col*90;yy=y+35+row*(89 if not door else 59)
   d.rectangle((xx,yy,xx+74,yy+(73 if not door else 45)),fill='#374b53')
im.save(O/'Stage3_Projection_Layout.png')
ref=Image.open(ART.parent/'Pantry Exports/DIS_COM_Base_B.dds').convert('RGB');ref.save(O/'Firaxis_Paint_Reference.png')
(O/'brief.json').write_text(json.dumps({'concept':str(Path.home()/'Desktop/Codex/bakery-modern-concept-20261026/Bakery_Modern_Sheltered_Dispatch_Concept.png'),'scope':'Reusable Level2/Stage3 main building, with separate side workshop module. No bakery equipment or stall.','reference_height':109.04,'planned_main':{'width':80,'depth':58,'ground':0,'foundation':-30,'ground_storey':32,'eaves':66,'ridge':110},'atlas':'1024 shared modern atlas Stage3 top-right 512 square; existing quadrants unchanged','cells':dict(enumerate(colors))},indent=2))
print(O)
