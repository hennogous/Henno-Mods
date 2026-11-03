"""Measure paired vanilla dirt/modern-road alpha profiles in world coordinates."""
from pathlib import Path
import sys,json,numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(Path(__file__).parent))
import integrate as i
A=i.AUTHOR;D=i.D;REF=A/'vanilla-width-calibration-20261029';O=A/'vanilla-shoulder-calibration-20261029'
textures={}
def texture(name):
 if name not in textures:
  if name.startswith('CSC_'):p=D/'textures'/(name+'_B.png')
  else:
   era='Modern' if 'Modern' in name else 'Ancient';p=A.parent/'draft-02-industrial/textures'/f'Decals_Parts_{era}_01_B.dds'
  textures[name]=np.array(Image.open(p).convert('RGBA'))/255
 return textures[name]

def unpack(m):
 native='materialName' in m
 return (np.array([v['position'][:2] if native else v[:2] for v in m['vertices']]),np.array([v['uv'] if native else v[12:14] for v in m['vertices']]),texture(m['materialName'] if native else m['materials'][0]['name']))

def sample(m,points):
 xy,uv,img=unpack(m);h,w=img.shape[:2];result=np.zeros((len(points),4))
 for f in m['triangles']:
  p=xy[f[:3]];t=uv[f[:3]];a=p[1]-p[0];b=p[2]-p[0];det=a[0]*b[1]-a[1]*b[0]
  if abs(det)<1e-9:continue
  d=points-p[0];s=(d[:,0]*b[1]-d[:,1]*b[0])/det;r=(a[0]*d[:,1]-a[1]*d[:,0])/det;mask=(s>=-1e-7)&(r>=-1e-7)&(s+r<=1+1e-7)
  if not mask.any():continue
  st=t[0]+s[mask,None]*(t[1]-t[0])+r[mask,None]*(t[2]-t[0]);xx=np.clip(st[:,0]*w-.5,0,w-1.00001);yy=np.clip(st[:,1]*h-.5,0,h-1.00001);x0=xx.astype(int);y0=yy.astype(int);fx=(xx-x0)[:,None];fy=(yy-y0)[:,None]
  result[mask]=(img[y0,x0]*(1-fx)+img[y0,x0+1]*fx)*(1-fy)+(img[y0+1,x0]*(1-fx)+img[y0+1,x0+1]*fx)*fy
 return result

offsets=np.arange(-45,45.0001,.05)
def edges(profile,threshold):
 on=np.where(profile>=threshold)[0]
 return [float(offsets[on[0]]),float(offsets[on[-1]])] if len(on) else None

def profile(road,base,center,normal):
 points=center+offsets[:,None]*normal;aa=sample(road,points)[:,3];bb=sample(base,points)[:,3];edge=edges(aa,.5)
 if edge is None:return None
 row={'tarmac_edges_50':edge,'tarmac_width':edge[1]-edge[0]}
 for threshold in [.1,.25,.5,.9]:
  e=edges(bb,threshold)
  row[str(threshold)]={'edges':e,'total_width':e[1]-e[0],'shoulder_each_side':[max(0,edge[0]-e[0]),max(0,e[1]-edge[1])]} if e else None
 return row

def measure():
 O.mkdir(exist_ok=True);rows=[];pairs=[]
 measured=json.loads((REF/'measurement.json').read_text())['samples']
 for f in REF.glob('DIS*.json'):
  meshes=json.loads(f.read_text())['meshes'];anc=[m for m in meshes if m['materialName']=='Decal_Parts_Ancient_01']
  for m in meshes:
   samples=[r for r in measured if r['geometry']==f.stem and r['mesh']==m['name']]
   if not samples:continue
   xy,uv,img=unpack(m)
   def distance(other):
    v=np.array([v['position'][:2] for v in other['vertices']]);d=np.linalg.norm(xy[:,None,:]-v[None,:,:],axis=2);return max(d.min(0).max(),d.min(1).max())
   pair=min(anc,key=distance);error=float(distance(pair))
   if error>3:continue
   coeff=np.linalg.lstsq(np.c_[uv,np.ones(len(uv))],xy,rcond=None)[0];along=coeff[0]/np.linalg.norm(coeff[0]);normal=np.array([-along[1],along[0]]);lo=uv.min(0);hi=uv.max(0)
   # Locate actual asphalt center, rather than assuming the card's UV midpoint.
   for r in samples:
    u=lo[0]+r['along_fraction']*(hi[0]-lo[0]);center=np.array([u,(hi[1]+lo[1])/2,1])@coeff
    aa=sample(m,center+offsets[:,None]*normal)[:,3];e=edges(aa,.5)
    if e is None:continue
    center+=normal*sum(e)/2;row=profile(m,pair,center,normal)
    row.update({'geometry':f.stem,'road':m['name'],'underlay':pair['name'],'pair_xy_error':error,'along_fraction':r['along_fraction'],'center':center.tolist(),'normal':normal.tolist()});rows.append(row)
   pairs.append([f.stem,m['name'],pair['name'],error])
 current=[];routes=json.loads((D/'layout-modules.json').read_text())['routes']
 for key in ['NW','NE','E','SE','SW']:
  model_dir=globals().get('MODEL_DIR',A/'models')
  m=json.loads((model_dir/f'CSC_Road_{key}_Modern.json').read_text())['meshes'][0];b=json.loads((model_dir/f'CSC_Road_{key}_Industrial.json').read_text())['meshes'][0];pts=np.array(routes[key])
  for j in [18,26,34]:
   tangent=pts[j+1]-pts[j-1];tangent/=np.linalg.norm(tangent);normal=np.array([-tangent[1],tangent[0]]);row=profile(m,b,pts[j],normal);row.update({'module':key,'route_index':j,'center':pts[j].tolist(),'normal':normal.tolist()});current.append(row)
 def summary(rows):
  out={'samples':len(rows),'tarmac_median_width':float(np.median([r['tarmac_width'] for r in rows]))}
  for t in [.1,.25,.5,.9]:
   vals=[v for r in rows if r[str(t)] for v in r[str(t)]['shoulder_each_side']];out[str(t)]={'median_shoulder':float(np.median(vals)),'q25_q75':np.percentile(vals,[25,75]).tolist(),'range':[min(vals),max(vals)]} if vals else None
  return out
 result={'method':'Isolated matched native road/underlay cards; actual FGX positions + UV bilinear alpha; thresholds distinguish dense material from soft fringe; unrelated nearby patches excluded','native':rows,'CSC':current,'pairs':pairs,'summary':{'native':summary(rows),'CSC':summary(current)}}
 assert len(rows)>=9;i.dump(O/'measurement.json',result);print(json.dumps(result['summary'],indent=2))

def board():
 result=json.loads((O/'measurement.json').read_text())
 nr=min(result['native'],key=lambda r:abs(np.mean(r['0.5']['shoulder_each_side'])-3.775)+abs(np.mean(r['0.1']['shoulder_each_side'])-13.2)*.4)
 cr=min(result['CSC'],key=lambda r:abs(np.mean(r['0.1']['shoulder_each_side'])-1.25))
 native=json.loads((REF/(nr['geometry']+'.json')).read_text())['meshes'];road=next(m for m in native if m['name']==nr['road']);base=next(m for m in native if m['name']==nr['underlay'])
 croad=json.loads((A/'models'/f"CSC_Road_{cr['module']}_Modern.json").read_text())['meshes'][0];cbase=json.loads((A/'models'/f"CSC_Road_{cr['module']}_Industrial.json").read_text())['meshes'][0]
 board=Image.new('RGB',(1400,700),(27,31,34));draw=ImageDraw.Draw(board);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',25);small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',19)
 for j,(title,row,r,b) in enumerate([('Vanilla gravel underlay',nr,road,base),('Current CSC stone underlay',cr,croad,cbase)]):
  normal=np.array(row['normal']);along=np.array([-normal[1],normal[0]]);xx,yy=np.meshgrid(np.linspace(-35,35,700),np.linspace(25,-25,500));points=np.array(row['center'])+xx.reshape(-1,1)*normal+yy.reshape(-1,1)*along
  col=np.zeros((len(points),3))+[.17,.23,.14]
  for m in [b,r]:
   p=sample(m,points);col=col*(1-p[:,3,None])+p[:,:3]*p[:,3,None]
  board.paste(Image.fromarray((col.reshape(500,700,3)*255).clip(0,255).astype('uint8')),(j*700,100))
  draw.text((j*700+20,15),title,font=font,fill='white');draw.text((j*700+20,52),'Same world scale: 70 units across; tarmac ~15',font=small,fill=(190,200,205))
  draw.text((j*700+20,618),'Typical shoulder beyond asphalt, per side:',font=small,fill='white')
  label='~4 units visible gravel; soft fade to ~13' if j==0 else '~0.4 units visible stone; fade ends at ~1.25'
  draw.text((j*700+20,650),label,font=small,fill=(230,195,125))
 board.save(O/'Vanilla_CSC_Shoulders.png');i.dump(O/'comparison-samples.json',{'native':nr,'CSC':cr,'note':'Actual UV/colour/alpha sampling on flat neutral green; no game lighting. Labels are multi-sample medians, not exact values of these representative cuts.'});print('SHOULDER_COMPARISON_READY')

if __name__=='__main__':globals()[sys.argv[1]]()
