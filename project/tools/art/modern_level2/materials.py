"""Pack generated artwork and author registered structural relief; no colour-noise height."""
from pathlib import Path
import json,shutil
import numpy as np
from PIL import Image,ImageDraw
O=Path.home()/'Desktop/Codex/modern-level2-v1-20261028'
SRC=Path.home()/'.codex/generated_images/01a17705-552a-7272-bb5e-272856a3d4c2/exec-9e1c4f74-6716-46c5-87e6-a827292d7bb0.png'
shutil.copy2(SRC,O/'Stage3_Generated_B.png');im=Image.open(SRC).convert('RGB');bounds=[0,313,627,941,1254]
patches=[im.crop((bounds[i%4],bounds[i//4],bounds[i%4+1],bounds[i//4+1])).resize((128,128),Image.Resampling.LANCZOS) for i in range(16)]
(O/'patches').mkdir(exist_ok=True)
for i,p in enumerate(patches):p.save(O/'patches'/f'{i:02}_B.png')
# Print deliberately bounded joint-position evidence for manual registration.
for i in (0,1,2,5,6,7):
 a=np.array(patches[i]).mean(2)
 print('PATCH',i,'Y',[(j,round(float(a[j].mean()),1)) for j in range(1,127) if a[j].mean()<a[j-1].mean() and a[j].mean()<a[j+1].mean()][:35])
 for y in ([8,24] if i==0 else [16,48] if i in (1,7) else [64]):
  line=a[max(0,y-2):y+3].mean(0);print('X',y,[(j,round(float(line[j]),1)) for j in range(1,127) if line[j]<line[j-1] and line[j]<line[j+1]][:40])
atlas=Image.open(O/'textures/CSC_Atlas_Modern_B_BAKERS.png').convert('RGB')
for i,p in enumerate(patches):atlas.paste(p,(512+i%4*128,i//4*128))
atlas.save(O/'textures/CSC_Atlas_Modern_B_BAKERS.png')
sheet=Image.new('RGB',(768,512))
for j,i in enumerate((0,1,2,5,6,7)):sheet.paste(patches[i].resize((256,256)),((j%3)*256,(j//3)*256))
sheet.save(O/'Registration_B.png')
