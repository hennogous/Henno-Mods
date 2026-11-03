"""Publish the authoring draft only and verify atlas writes stayed in candidate cells."""
from pathlib import Path
import json,shutil,hashlib
import numpy as np
from PIL import Image
O=Path.home()/'Desktop/Codex/modern-bakery-v1-20261028';ART=Path.home()/'Desktop/Working Files/3D Art';D=ART/'BAKERS/Bakery/modern/revision-01-sheltered-bakery'
checks=[]
for family,prefix,rects in [('CSC_Buildings_Modern','CSC_Atlas_Modern',{'default':[(512,0,1024,512)],'AO':[(1024,0,1536,512),(1536,0,1792,256)]}),('CSC_Props_Modern','CSC_Props_Modern_01',{'default':[(0,384,1024,512)],'AO':[(512,0,1024,256),(512,256,768,512),(512,512,768,768),(768,256,1024,512),(768,512,896,640)]})]:
 for ch in ('B','N','G','M','AO','E'):
  name=prefix+('_B_BAKERS' if prefix=='CSC_Atlas_Modern' and ch=='B' else '_'+ch)+'.png'
  original=next((ART/'Textures'/family/'Current').rglob(name));a=np.array(Image.open(original).convert('RGB'));b=np.array(Image.open(O/'textures'/name).convert('RGB'));assert a.shape==b.shape
  mask=np.zeros(a.shape[:2],dtype=bool)
  for box in rects.get(ch,rects['default']):
   if ch=='E':
    if family=='CSC_Props_Modern':continue
    box=[int(x*a.shape[0]/1024) for x in box]
   x,y,X,Y=box;mask[y:Y,x:X]=True
  outside=np.any(a!=b,axis=2)&~mask;assert not outside.any(),(name,int(outside.sum()))
  checks.append({'map':name,'outside_allocations_changed':0})
shutil.copytree(O/'textures',D/'textures',dirs_exist_ok=True);shutil.copytree(O/'sources',D/'texture-sources',dirs_exist_ok=True)
for path,sha in json.loads((O/'input-hashes.json').read_text()).items():assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==sha,path
report={'atlas_boundaries':checks,'source_architecture_blends_unchanged':True,'runtime_or_Current_publication':False,'emission_in_review':False,'native_geometry_checks':json.loads((O/'native-validation.json').read_text()),'draft_counts':json.loads((D/'assembly-validation.json').read_text())['counts']}
(O/'delivery-verification.json').write_text(json.dumps(report,indent=2));shutil.copy2(O/'delivery-verification.json',D/'delivery-verification.json')
print('DRAFT_VERIFIED',report['draft_counts'])
