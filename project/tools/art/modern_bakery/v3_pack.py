from pathlib import Path
from PIL import Image
import numpy as np,json
O=Path.home()/'Desktop/Codex/modern-bakery-v3-20261028';allocation=json.loads((O/'v3-build-report.json').read_text())['AO']
for name,group in [('CSC_Atlas_Modern_AO.png','Building'),('CSC_Props_Modern_01_AO.png','Display')]:
 im=Image.open(O/'textures'/name).convert('RGB');x,y,X,Y=allocation[group];p=Image.open(O/'bakes'/f'{group}.png').convert('RGB').resize((X-x-8,Y-y-8),Image.Resampling.LANCZOS);p=Image.fromarray(np.pad(np.array(p),((4,4),(4,4),(0,0)),mode='edge'));im.paste(p,(x,y));im.save(O/'textures'/name)
path=O/'textures/CSC_Props_Modern_01_AO.png';a=np.array(Image.open(path).convert('RGB'),dtype=float)
for tr in json.loads((O/'microAO-triangles.json').read_text()):
 q=np.array(tr['UV2'])*[2048,-2048]+[0,2048];uv=np.array(tr['UV1']);lo=np.maximum(0,np.floor(q.min(0)).astype(int));hi=np.minimum(2047,np.ceil(q.max(0)).astype(int));A=np.vstack((q.T,np.ones(3)))
 if abs(np.linalg.det(A))<1e-8:continue
 inv=np.linalg.inv(A);slot=tr['slot'];m=np.array(Image.open(O/'sources'/f'tray_{slot}_microAO.png'),float)/255
 for y in range(lo[1],hi[1]+1):
  for x in range(lo[0],hi[0]+1):
   w=inv@np.array([x+.5,y+.5,1])
   if min(w)<-1e-6:continue
   u,v=w@uv;xx=int(round(u*1024-slot%8*128));yy=int(round((1-v)*1024-slot//8*128));a[y,x]*=m[np.clip(yy,0,127),np.clip(xx,0,127)]
Image.fromarray(np.uint8(np.clip(a,0,255))).save(path);print('V3_AO_PACKED')
