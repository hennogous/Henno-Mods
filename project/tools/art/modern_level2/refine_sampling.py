"""Match concept masonry scale by repeating the same painted patch 2x2 per fixed cell."""
from pathlib import Path
import sys,json
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT/'project/tools/art/modern_windmill'))
from correct_modern_normals import normals
O=Path.home()/'Desktop/Codex/modern-level2-v1-20261028'
b=Image.open(O/'textures/CSC_Atlas_Modern_B_BAKERS.png').convert('RGB');n=Image.open(O/'textures/CSC_Atlas_Modern_N.png').convert('RGB')
for slot in (0,1):
 src=Image.open(O/'patches'/f'{slot:02}_B.png').resize((64,64),Image.Resampling.LANCZOS);p=Image.new('RGB',(128,128))
 h=np.load(O/'height'/f'{slot:02}.npy');small=np.asarray(Image.fromarray(h).resize((256,256),Image.Resampling.BILINEAR));h=np.tile(small,(2,2));np.save(O/'height'/f'{slot:02}.npy',h)
 for x in (0,64):
  for y in (0,64):p.paste(src,(x,y))
 p.save(O/'patches'/f'{slot:02}_B.png');nn=normals(h,(32,32));nn.save(O/'patches'/f'{slot:02}_N.png');b.paste(p,(512+slot*128,0));n.paste(nn,(512+slot*128,0))
b.save(O/'textures/CSC_Atlas_Modern_B_BAKERS.png');n.save(O/'textures/CSC_Atlas_Modern_N.png')
sheet=Image.new('RGB',(1536,800));d=ImageDraw.Draw(sheet)
for col,i in enumerate((0,1,2,5,6,7)):
 h=np.load(O/'height'/f'{i:02}.npy');hp=Image.fromarray(np.uint8((h-h.min())/max(.0001,h.max()-h.min())*255)).convert('RGB')
 for row,im in enumerate((Image.open(O/'patches'/f'{i:02}_B.png'),hp,Image.open(O/'patches'/f'{i:02}_N.png'))):sheet.paste(im.resize((256,256)),(col*256,32+row*256))
 d.text((col*256+4,8),str(i)+' B / registered height / N',fill='white')
sheet.save(O/'Registered_Relief.png');r=json.loads((O/'relief-registration.json').read_text());r['sampling_refinement']={'cells':[0,1],'repeat':[2,2],'reason':'Match concept brick and lower-stone course scale. No geometry, UV or AO changes.'};(O/'relief-registration.json').write_text(json.dumps(r,indent=2))
