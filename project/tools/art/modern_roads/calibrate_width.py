"""Measure native modern road coverage at actual FGX/UV world scale."""
from pathlib import Path
import sys,json,numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(Path(__file__).parent))
import integrate as i
O=i.AUTHOR/'vanilla-width-calibration-20261029'

def measure():
 a=np.array(Image.open(O/'vanilla-atlas.png'))[:,:,3]/255
 rows=[]
 for p in O.glob('DIS*.json'):
  for m in json.loads(p.read_text())['meshes']:
   if m['materialName']!='Decal_Parts_Modern_01' or 'Straight_Tileable' not in m['name'] or len(m['vertices'])!=4:continue
   uv=np.array([v['uv'] for v in m['vertices']]);xy=np.array([v['position'][:2] for v in m['vertices']]);lo=uv.min(0);hi=uv.max(0)
   # Native straight tile occupies the bottom horizontal stripe of this atlas.
   if lo[1]<.89:continue
   coeff=np.linalg.lstsq(np.c_[uv,np.ones(4)],xy,rcond=None)[0]
   assert np.max(np.abs(np.c_[uv,np.ones(4)]@coeff-xy))<.01
   along=coeff[0]/np.linalg.norm(coeff[0]);normal=np.array([-along[1],along[0]])
   unit=abs(coeff[1]@normal);vv=np.linspace(lo[1],hi[1],4096);step=(hi[1]-lo[1])/4095*unit
   for t in [.25,.5,.75]:
    u=lo[0]+t*(hi[0]-lo[0]);x=u*512-.5;y=vv*512-.5;x0=int(x);y0=np.floor(y).astype(int);fx=x-x0;fy=y-y0
    alpha=(a[y0,x0]*(1-fx)+a[y0,x0+1]*fx)*(1-fy)+(a[np.minimum(y0+1,511),x0]*(1-fx)+a[np.minimum(y0+1,511),x0+1]*fx)*fy
    rows.append({'geometry':p.stem,'mesh':m['name'],'along_fraction':t,'width_50':float((alpha>=.5).sum()*step),'width_90':float((alpha>=.9).sum()*step),'coverage_width':float(alpha.sum()*step),'projection_card_width':float((hi[1]-lo[1])*unit)})
 assert len(rows)>=12
 report={'method':'Affine native UV-to-XY; width perpendicular to road centerline; bilinear coverage sampled at 25/50/75 percent along straight cards, scale1','samples':rows,'median_width_50':float(np.median([r['width_50'] for r in rows])),'range_width_50':[min(r['width_50'] for r in rows),max(r['width_50'] for r in rows)],'old_CSC_nominal_width':26}
 i.dump(O/'measurement.json',report);print(json.dumps({k:v for k,v in report.items() if k!='samples'},indent=2));print('SAMPLES',len(rows))

def board():
 from PIL import ImageDraw,ImageFont
 size=900;extent=700
 textures={}
 def raster(meshes,native=False):
  rgb=np.zeros((size,size,3))+[38,45,42];coverage=np.zeros((size,size))
  for m in meshes:
   name=m['materialName'] if native else m['materials'][0]['name']
   if name not in textures:
    if native:
     era='Modern' if 'Modern' in name else 'Ancient';path=i.AUTHOR.parent/'draft-02-industrial/textures'/f'Decals_Parts_{era}_01_B.dds'
    else:path=i.D/'textures'/(name+'_B.png')
    textures[name]=np.array(Image.open(path).convert('RGBA'))/255
   img=textures[name];h,w=img.shape[:2]
   vs=np.array([v['position'][:2] for v in m['vertices']]) if native else np.array([v[:2] for v in m['vertices']])
   uv=np.array([v['uv'] for v in m['vertices']]) if native else np.array([v[12:14] for v in m['vertices']])
   pts=np.c_[(vs[:,0]+350)/extent*size,(350-vs[:,1])/extent*size]
   for f in m['triangles']:
    p=pts[f[:3]];t=uv[f[:3]];lo=np.maximum(np.floor(p.min(0)).astype(int),0);hi=np.minimum(np.ceil(p.max(0)).astype(int),size-1)
    if np.any(hi<lo):continue
    xx,yy=np.meshgrid(np.arange(lo[0],hi[0]+1)+.5,np.arange(lo[1],hi[1]+1)+.5);d=p[1]-p[0];e=p[2]-p[0];det=d[0]*e[1]-d[1]*e[0]
    if abs(det)<1e-9:continue
    s=((xx-p[0,0])*e[1]-(yy-p[0,1])*e[0])/det;r=(d[0]*(yy-p[0,1])-d[1]*(xx-p[0,0]))/det;inside=(s>=0)&(r>=0)&(s+r<=1)
    st=t[0]+s[...,None]*(t[1]-t[0])+r[...,None]*(t[2]-t[0]);tx=np.clip((st[:,:,0]*w).astype(int),0,w-1);ty=np.clip((st[:,:,1]*h).astype(int),0,h-1)
    c=img[ty,tx];a=c[:,:,3]*inside;dst=rgb[lo[1]:hi[1]+1,lo[0]:hi[0]+1];dst[:]=dst*(1-a[...,None])+c[:,:,:3]*255*a[...,None]
    dst=coverage[lo[1]:hi[1]+1,lo[0]:hi[0]+1];dst[:]=1-(1-dst)*(1-a)
  return Image.fromarray(rgb.clip(0,255).astype('uint8')),coverage
 panels=[]
 n=json.loads((O/'DIS_COM_Modern_Base_Decal_04.json').read_text())['meshes'];panels.append(('Vanilla modern Commercial Hub',raster(n,True)[0]))
 previous=O/'before/active-inputs/layout-variants-20261029/models/CSC_ALL_Modern_Base_05_Road_Decals.json'
 if not previous.exists():previous=i.AUTHOR/'layout-variants-20261029/models/CSC_ALL_Modern_Base_05_Road_Decals.json'
 for title,path in [('CSC before: 26 units',previous),('CSC calibrated: 15 units',O/'models/CSC_ALL_Modern_Base_05_Road_Decals.json')]:
  model=json.loads(path.read_text());meshes=sorted(model['meshes'],key=lambda m:'Modern' in m['materials'][0]['name']);im,cov=raster(meshes);panels.append((title,im))
 result=Image.new('RGB',(size*3,size+90),(26,30,33));draw=ImageDraw.Draw(result);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',26)
 for k,(title,im) in enumerate(panels):result.paste(im,(k*size,90));draw.text((k*size+20,15),title,font=font,fill='white');draw.text((k*size+20,50),'Same world scale | 700 units across',font=font,fill=(180,190,195))
 result.save(O/'Vanilla_CSC_Width_Comparison.png');print('WIDTH_COMPARISON_READY',flush=True)

if __name__=='__main__':globals()[sys.argv[1]]()
