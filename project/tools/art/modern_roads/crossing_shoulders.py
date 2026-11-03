"""Follow the actual paved flare around the five pedestrian crossings."""
from pathlib import Path
import sys,json,shutil
import numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(Path(__file__).parent))
import integrate as i
import calibrate_shoulders as c
import repair_height as h
A=i.AUTHOR;D=i.D;MOD=i.MOD;O=A/'crossing-shoulders-20261029';sha=i.sha;dump=i.dump

def prepare():
 assert not (O/'baseline.json').exists()
 base={str(p):sha(p) for folder in ['Assets','Geometries','ArtDefs','XLPs','Materials','Textures'] for p in (MOD/folder).glob('*') if p.is_file()}
 for p in (D/'textures').rglob('*'):
  if p.is_file():base[str(p)]=sha(p);q=O/'before/source'/p.relative_to(D);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
 dump(O/'baseline.json',base)
 manifest=json.loads((D/'atlas-layout.json').read_text());x0,y0,x1,y1=manifest['cells']['roundabout']['rect'];sx,sy=manifest['cells']['roundabout']['industrial_world_size'];cx,cy=manifest['roundabout']['center'];w=x1-x0;hh=y1-y0
 x,y=np.meshgrid((np.arange(w)+.5)/w*sx-sx/2,sy/2-(np.arange(hh)+.5)/hh*sy);points=np.c_[x.ravel()+cx,y.ravel()+cy]
 road=json.loads((A/'models/CSC_Road_Roundabout_Modern.json').read_text())['meshes'][0]
 paved=c.sample(road,points)[:,3].reshape(hh,w)>=.5
 # Exact distance to the sampled paved boundary, in world units. The half
 # texel subtraction places the contour between covered/uncovered pixels.
 boundary=paved.copy();boundary[1:-1,1:-1]&=~(paved[:-2,1:-1]&paved[2:,1:-1]&paved[1:-1,:-2]&paved[1:-1,2:])
 bp=np.c_[x[boundary],y[boundary]];distance=np.full(w*hh,np.inf)
 for k in range(0,len(bp),32):distance=np.minimum(distance,np.min(np.sum((points[:,None,:]-np.array([cx,cy])-bp[None,k:k+32,:])**2,axis=2),axis=1))
 distance=np.maximum(0,np.sqrt(distance).reshape(hh,w)-.5*sx/w)
 desired=np.interp(distance,[0,4.1,8.9,13.5,22],[.78,.5,.25,.1,0]);desired[paved]=1
 local=np.zeros_like(x)
 for angle in manifest['roundabout']['angles_degrees']:
  t=np.radians(angle);u=x*np.cos(t)+y*np.sin(t);v=-x*np.sin(t)+y*np.cos(t)
  weight=np.minimum(np.clip((u-79)/5,0,1),np.clip((108-u)/8,0,1))*np.clip((36-np.abs(v))/5,0,1);local=np.maximum(local,weight)
 (O/'staged/Textures').mkdir(parents=True,exist_ok=True);old=np.array(Image.open(D/'textures/CSC_Roads_Industrial_01_B.png').convert('RGBA'));alpha=old[y0:y1,x0:x1,3]/255;fixed=alpha+np.maximum(0,desired-alpha)*local;newalpha=np.rint(fixed*255).astype('uint8');rows=[]
 for ch in ['B','FOW','H']:
  p=D/'textures'/f'CSC_Roads_Industrial_01_{ch}.png';data=np.array(Image.open(p).convert('RGBA'));rgb=data[:,:,:3].copy();data[y0:y1,x0:x1,3]=newalpha;assert np.array_equal(data[:,:,:3],rgb);Image.fromarray(data).save(p)
  args=[ROOT/'project/tools/directxtex/texconv.exe','-nologo','-y','-m','0','-f','R8G8B8A8_UNORM','--ignore-srgb','-o',O/'staged/Textures']
  if ch!='H':args+=['-srgb']
  i.run(args+[p],O/(p.stem+'-convert.log'));rows.append({'source':str(p),'sha256':sha(p),'RGB_preserved':True})
 bm=h.mips(O/'staged/Textures/CSC_Roads_Industrial_01_B.dds');hm=h.mips(O/'staged/Textures/CSC_Roads_Industrial_01_H.dds');assert len(bm)==10 and all(np.max(np.abs(b[:,:,3].astype(int)-a[:,:,3].astype(int)))<=1 for b,a in zip(bm,hm))
 dump(O/'texture-validation.json',rows);print('CROSSING_COVERAGE_CORRECTED',int(np.count_nonzero(newalpha>old[y0:y1,x0:x1,3])),flush=True)

def review():
 c.textures.clear();rows=[];p=A/'models';road=json.loads((p/'CSC_Road_Roundabout_Modern.json').read_text())['meshes'][0];base=json.loads((p/'CSC_Road_Roundabout_Industrial.json').read_text())['meshes'][0]
 for name,angle in zip(['NW','NE','E','SE','SW'],[145,55,-8,-75,-140]):
  t=np.radians(angle);d=np.array([np.cos(t),np.sin(t)]);n=np.array([-d[1],d[0]])
  for u in [87,91.5,96]:
   row=c.profile(road,base,np.array([5,10])+u*d,n);row.update({'exit':name,'distance':u});rows.append(row)
 assert min(v for r in rows for v in r['0.5']['shoulder_each_side'])>=3.5
 dump(O/'crossing-width-validation.json',rows)
 # A close overhead view makes the crossing's inner shoulder visible.
 size=(420,320);x,y=np.meshgrid(np.linspace(-30,30,size[0]),np.linspace(112,72,size[1]));t=np.radians(-75);d=np.array([np.cos(t),np.sin(t)]);n=np.array([-d[1],d[0]]);pts=np.array([5,10])+x.reshape(-1,1)*n+y.reshape(-1,1)*d
 board=Image.new('RGB',(840,380),(28,33,36));draw=ImageDraw.Draw(board);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)
 saved={k:v.copy() for k,v in c.textures.items()}
 for j,label in enumerate([globals().get('BEFORE_LABEL','Before: shoulder pinches at flare'),globals().get('AFTER_LABEL','After: shoulder follows crossing')]):
  c.textures=dict(saved)
  if j==0:c.textures['CSC_Roads_Industrial_01']=np.array(Image.open(O/'before/source/textures/CSC_Roads_Industrial_01_B.png').convert('RGBA'))/255
  col=np.zeros((len(pts),3))+[.17,.23,.14]
  for key,era in [('Roundabout','Industrial'),('SE','Industrial'),('Roundabout','Modern'),('SE','Modern')]:
   m=json.loads((p/f'CSC_Road_{key}_{era}.json').read_text())['meshes'][0];data=c.sample(m,pts);col=col*(1-data[:,3,None])+data[:,:3]*data[:,3,None]
  board.paste(Image.fromarray((col.reshape(size[1],size[0],3)*255).clip(0,255).astype('uint8')),(j*420,60));draw.text((j*420+12,15),label,font=font,fill='white')
 board.save(O/'Crossing_Shoulders_Before_After.png');c.textures=saved;print('CROSSING_WIDTHS_PASS',flush=True)

def stage():
 for folder,pattern in [('Materials','CSC_Roads_*.mtl'),('Textures','CSC_Roads_*'),('Geometries','CSC_ALL_Modern_Base_05_Road_Decals.*')]:
  (O/'staged'/folder).mkdir(parents=True,exist_ok=True)
  for p in (MOD/folder).glob(pattern):
   if not (O/'staged'/folder/p.name).exists():shutil.copy2(p,O/'staged'/folder/p.name)
 (O/'staged/Assets').mkdir(parents=True,exist_ok=True);shutil.copy2(A/'shoulders-fixed-20261029/staged/Assets/CSC_ALL_Modern_Base_05_Road_Decals.ast',O/'staged/Assets/CSC_ALL_Modern_Base_05_Road_Decals.ast')

def publish():
 assert json.loads((O/'cook-check/result.json').read_text())['exit_code']==0;assert (O/'crossing-width-validation.json').exists();base=json.loads((O/'baseline.json').read_text());files=[]
 for row in json.loads((O/'texture-validation.json').read_text()):
  assert sha(row['source'])==row['sha256'];p=MOD/'Textures'/(Path(row['source']).stem+'.dds');assert sha(p)==base[str(p)]
 for row in json.loads((O/'texture-validation.json').read_text()):
  p=MOD/'Textures'/(Path(row['source']).stem+'.dds');backup=O/'before/Textures'/p.name;backup.parent.mkdir(exist_ok=True);shutil.copy2(p,backup);shutil.copy2(O/'staged/Textures'/p.name,p);shutil.copy2(p,D/'textures/native'/p.name);files.append({'destination':str(p),'before':base[str(p)],'after':sha(p)})
 for path,digest in base.items():
  if Path(path).parent in [MOD/'Assets',MOD/'Geometries',MOD/'ArtDefs',MOD/'XLPs',MOD/'Materials'] or 'CSC_Roads_Modern_01' in Path(path).name:assert sha(path)==digest,path
 dump(O/'publication-report.json',{'installed':True,'files':files,'RGB_geometry_UVs_tarmac_assemblies_preserved':True});i.n.cache(O);i.OUT=O;i.verify();print('CROSSING_SHOULDERS_INSTALLED',flush=True)

if __name__=='__main__':globals()[sys.argv[1]]()
