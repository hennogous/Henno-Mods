"""Prove v2 atlas edits are confined to allocated cells; check E semantics."""
from pathlib import Path
from PIL import Image
import numpy as np,json
O=Path.home()/'Desktop/Codex/modern-bakery-v2-20261028'
OLD=Path.home()/'Desktop/Working Files/3D Art/BAKERS/Bakery/modern/revision-01-sheltered-bakery/textures'
records=[]
for p in (O/'textures').glob('*.png'):
 a=np.array(Image.open(p).convert('RGB'));b=np.array(Image.open(OLD/p.name).convert('RGB'))
 assert a.shape==b.shape,p.name
 mask=np.zeros(a.shape[:2],bool);rects=[]
 if 'Props' in p.name:
  if '_AO.' in p.name:rects=[(512,768,1024,1024)]
  elif '_E.' not in p.name:rects=[(0,512,512,640)]
 else:
  if '_AO.' in p.name:rects=[(1024,0,1536,512),(1536,0,1792,256)]
  elif '_E.' not in p.name:
   rects=[(768,384,896,512)]
   if '_B_' in p.name:rects.append((768,128,896,256))
 for x,y,X,Y in rects:mask[y:Y,x:X]=True
 changed=np.any(a!=b,axis=2);outside=int(np.count_nonzero(changed&~mask));assert outside==0,(p.name,outside)
 records.append({'file':p.name,'changed_pixels':int(changed.sum()),'outside_allocations':outside})
e=Image.open(O/'textures/CSC_Atlas_Modern_E.png').convert('RGB');w,h=e.size
def sample(u,v):return list(e.getpixel((int(u*w),int((1-v)*h))))
assert max(sample(.02,.02))==0
# Interior centres of the four upstairs panes, using source surface atlas coordinates.
panes=[sample((640+x)/1024,1-(128+y)/1024) for x,y in [(39,35),(88,35),(39,82),(88,82)]]
assert all(max(x)>0 for x in panes),panes
(O/'texture-verification.json').write_text(json.dumps({'files':records,'ground_uv3_black':True,'upper_four_panes':panes},indent=2))
print('TEXTURE_CHECKS_PASS',json.dumps(records))
