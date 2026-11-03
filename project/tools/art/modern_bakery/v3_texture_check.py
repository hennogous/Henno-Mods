from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,shutil
O=Path.home()/'Desktop/Codex/modern-bakery-v3-20261028';D=Path.home()/'Desktop/Working Files/3D Art/BAKERS/Bakery/modern/revision-03-height-interiors';L=Path.home()/'Desktop/Working Files/3D Art/Level 2/modern/revision-05-height-interiors';old=D.parent/'revision-02-concept-c/textures';rows=[]
for p in (O/'textures').glob('*.png'):
 if p.name.endswith('_O.png'):continue
 a=np.array(Image.open(p).convert('RGB'));b=np.array(Image.open(old/p.name).convert('RGB'));mask=np.zeros(a.shape[:2],bool)
 if 'Props' in p.name:
  rects=[(512,512,768,768)] if '_AO.' in p.name else ([] if '_E.' in p.name else [(512,512,896,640)])
 else:
  rects=[(1024,0,1536,512)] if '_AO.' in p.name else ([] if '_E.' in p.name else [(896,256,1024,384),(512,384,640,512),(896,384,1024,512)])
  if '_B_' in p.name or '_G.' in p.name:rects +=[(768,128,896,256),(768,384,896,512)]
 for x,y,X,Y in rects:mask[y:Y,x:X]=True
 change=np.any(a!=b,axis=2);bad=int(np.count_nonzero(change&~mask));assert bad==0,(p.name,bad)
 rows.append({'file':p.name,'outside_allocations':bad,'changed_pixels':int(change.sum())})
initial=json.loads((O/'source-inspection.json').read_text());source=Path(initial['source']);assert hashlib.sha256(source.read_bytes()).hexdigest()==initial['source_sha256'],'Human source changed during the task; do not overwrite.'
opacity=np.array(Image.open(O/'textures/CSC_Atlas_Modern_O.png').convert('L'));allowed=np.zeros(opacity.shape,bool)
allowed[128:256,768:896]=True;allowed[384:512,768:896]=True
assert np.all(opacity[~allowed]==255),'Opacity leaked outside ground window/door cells'
report={'atlas_changes':rows,'human_source_unchanged':True,'new_opacity':'Ground glass only; opacity is white elsewhere','native_shader_tested':False}
(O/'texture-verification.json').write_text(json.dumps(report,indent=2))
for folder in (D,L):shutil.copy2(O/'sources/generation-provenance.json',folder/'texture-sources/generation-provenance.json')
print('V3_TEXTURE_SOURCE_CHECKS_PASS')
