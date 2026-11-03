"""Remove double opacity where the roundabout shoulder meets approach decals."""
import sys,json,shutil
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(Path(__file__).parent))
import crossing_shoulders as q
import calibrate_shoulders as c
import repair_height as h
A=q.A;D=q.D;MOD=q.MOD;O=A/'crossing-blend-20261029';sha=q.sha;dump=q.dump

def prepare():
 if globals().get('REFINE',False):
  for row in json.loads((O/'texture-validation.json').read_text()):
   assert sha(row['source'])==row['sha256'];shutil.copy2(O/'before/source/textures'/Path(row['source']).name,row['source'])
 else:
  assert not (O/'baseline.json').exists()
 base={str(p):sha(p) for folder in ['Assets','Geometries','ArtDefs','XLPs','Materials','Textures'] for p in (MOD/folder).glob('*') if p.is_file()}
 if not globals().get('REFINE',False):
  for p in (D/'textures').rglob('*'):
   if p.is_file():base[str(p)]=sha(p);dest=O/'before/source'/p.relative_to(D);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
  dump(O/'baseline.json',base)
 m=json.loads((D/'atlas-layout.json').read_text());a,b,d,e=m['cells']['roundabout']['rect'];sx,sy=m['cells']['roundabout']['industrial_world_size'];cx,cy=m['roundabout']['center'];w=d-a;hh=e-b
 x,y=np.meshgrid((np.arange(w)+.5)/w*sx-sx/2,sy/2-(np.arange(hh)+.5)/hh*sy);points=np.c_[x.ravel()+cx,y.ravel()+cy]
 original=np.array(Image.open(D/'textures/CSC_Roads_Industrial_01_B.png').convert('RGBA'));alpha=original[b:e,a:d,3]/255
 pa,pb,pc,pd=m['cells']['plain']['rect'];length=m['cells']['plain']['industrial_world_size'][0]
 fraction=np.clip(((np.arange(pc-pa)+.5)/(pc-pa)*length)/12,0,1);fraction=fraction*fraction*(3-2*fraction)
 approachalpha=np.rint(original[pb:pd,pa:pc,3]*fraction[None,:]).astype('uint8')
 faded=original.copy();faded[pb:pd,pa:pc,3]=approachalpha;c.textures['CSC_Roads_Industrial_01']=faded/255
 approaches=np.zeros_like(alpha)
 for key in ['NW','NE','E','SE','SW']:
  model=json.loads((A/'models'/f'CSC_Road_{key}_Industrial.json').read_text())['meshes'][0];coverage=c.sample(model,points)[:,3].reshape(hh,w);approaches=1-(1-approaches)*(1-coverage)
 target=np.maximum(alpha,approaches)
 corrected=np.clip((target-approaches)/np.maximum(1-approaches,1e-7),0,1)
 corrected[approaches==0]=alpha[approaches==0]
 # Only the ring loses duplicate coverage; the approaches remain authoritative.
 newalpha=np.rint(corrected*255).astype('uint8');after=1-(1-newalpha/255)*(1-approaches);error=float(np.max(np.abs(after-target)));assert error<=1/255
 overlap=(alpha>.1)&(approaches>.1);assert overlap.any();before=1-(1-alpha)*(1-approaches)
 dump(O/'overlap-validation.json',{'max_composite_coverage_error':error,'affected_texels':int(np.count_nonzero(newalpha<original[b:e,a:d,3])),'before_mean_excess_opacity':float(np.mean((before-target)[overlap])),'after_mean_excess_opacity':float(np.mean((after-target)[overlap])),'method':'Preserve max single-layer coverage by inverse source-over alpha on ring; approach layers unchanged'})
 (O/'staged/Textures').mkdir(parents=True,exist_ok=True);rows=[]
 for ch in ['B','FOW','H']:
  p=D/'textures'/f'CSC_Roads_Industrial_01_{ch}.png';data=np.array(Image.open(p).convert('RGBA'));rgb=data[:,:,:3].copy();data[b:e,a:d,3]=newalpha;data[pb:pd,pa:pc,3]=approachalpha;assert np.array_equal(rgb,data[:,:,:3]);Image.fromarray(data).save(p)
  args=[ROOT/'project/tools/directxtex/texconv.exe','-nologo','-y','-m','0','-f','R8G8B8A8_UNORM','--ignore-srgb','-o',O/'staged/Textures']
  if ch!='H':args+=['-srgb']
  q.i.run(args+[p],O/(p.stem+'-convert.log'));rows.append({'source':str(p),'sha256':sha(p),'RGB_preserved':True})
 bm=h.mips(O/'staged/Textures/CSC_Roads_Industrial_01_B.dds');hm=h.mips(O/'staged/Textures/CSC_Roads_Industrial_01_H.dds');assert len(bm)==10 and all(np.max(np.abs(u[:,:,3].astype(int)-v[:,:,3].astype(int)))<=1 for u,v in zip(bm,hm))
 dump(O/'texture-validation.json',rows);print('CROSSING_OVERLAP_CORRECTED',flush=True)

def review():
 q.O=O;q.BEFORE_LABEL='Before: double opacity at join';q.AFTER_LABEL='After: consistent shoulder opacity';q.review()

def stage():q.O=O;q.stage()
def publish():q.O=O;q.publish()

def refine():
 global REFINE
 REFINE=True;prepare()

if __name__=='__main__':globals()[sys.argv[1]]()
