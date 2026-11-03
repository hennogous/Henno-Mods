"""World-coordinate coverage comparison, using actual source UV/alpha masks."""
import json,math,hashlib
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
O=Path.home()/'Desktop/Codex/Quarter-Roads-Modern/draft-03-roundabout';D=Path.home()/'Desktop/Working Files/3D Art/Decals/CSC_ALL_Modern_Roads'
P=Path.home()/'Desktop/Codex/Quarter-Roads-Modern/draft-02-industrial/textures'
N=1400;S=700;origin=(-350,350)
def pixel(x,y):return ((x+350)/700*N,(350-y)/700*N)
def raster(objects,modern=False):
 canvas=np.zeros((N,N),dtype=float)
 for ob in objects:
  v=np.array(ob['vertices']);faces=ob['faces'];uv=np.array(ob['uvs']);li=0
  if modern:img=np.asarray(Image.open(D/'textures/CSC_Roads_Modern_01_B.png'))
  else:
   era='Ancient' if 'Ancient' in ob['materials'][0] else 'Classical';img=np.asarray(Image.open(P/f'Decals_Parts_{era}_01_B.dds'))
  coords=np.stack([(v[:,0]+350)/700*N,(350-v[:,1])/700*N],1);h,w=img.shape[:2]
  for face in faces:
   tuv=uv[li:li+len(face)];li+=len(face)
   for i in range(1,len(face)-1):
    pt=coords[[face[0],face[i],face[i+1]]];t=tuv[[0,i,i+1]];lo=np.maximum(np.floor(pt.min(0)).astype(int),0);hi=np.minimum(np.ceil(pt.max(0)).astype(int),N-1)
    if np.any(hi<lo):continue
    xx,yy=np.meshgrid(np.arange(lo[0],hi[0]+1)+.5,np.arange(lo[1],hi[1]+1)+.5);dx=xx-pt[0,0];dy=yy-pt[0,1];a=pt[1]-pt[0];b=pt[2]-pt[0];det=a[0]*b[1]-a[1]*b[0]
    if abs(det)<1e-6:continue
    s=(dx*b[1]-dy*b[0])/det;r=(a[0]*dy-a[1]*dx)/det;inside=(s>=0)&(r>=0)&(s+r<=1)
    st=t[0]+s[...,None]*(t[1]-t[0])+r[...,None]*(t[2]-t[0]);tx=np.clip((st[:,:,0]*(w-1)).astype(int),0,w-1);ty=np.clip(((1-st[:,:,1])*(h-1)).astype(int),0,h-1)
    alpha=img[ty,tx,3]/255*inside;dst=canvas[lo[1]:hi[1]+1,lo[0]:hi[0]+1];dst[:]=1-(1-dst)*(1-alpha)
 return canvas
j=json.loads((O/'classical-live.json').read_text());old=raster(j['objects']);widths={}
for name,a in j['anchors'].items():
 inner=np.array(a['inner']);direction=np.array(a['outward']);normal=np.array([-direction[1],direction[0]]);values=[]
 for dist in [0,15,30]:
  p=inner+direction*dist;offsets=np.arange(-40,40,.25);xy=p+offsets[:,None]*normal;px=((xy[:,0]+350)/700*N).astype(int);py=((350-xy[:,1])/700*N).astype(int);alpha=old[py,px]
  values.append({'distance_from_fade_start':dist,'width_at_50pct_alpha':float((alpha>.5).sum()*.25),'coverage_equivalent_width':float(alpha.sum()*.25)})
 widths[name]=values
(O/'classical-road-widths.json').write_text(json.dumps(widths,indent=2));print('CLASSICAL_WIDTHS',widths)
objects=[]
for path in (O/'models').glob('*_Modern.json'):
 m=json.loads(path.read_text())['meshes'][0];vs=m['vertices'];faces=[f[:3] for f in m['triangles']];objects.append({'vertices':[v[:3] for v in vs],'faces':faces,'uvs':[[vs[i][12],1-vs[i][13]] for f in faces for i in f]})
new=raster(objects,True);rgb=np.empty((N,N,3));rgb[:]=[29,34,38];rgb+=old[...,None]*np.array([173,103,22]);rgb+=new[...,None]*np.array([24,132,175]);rgb=rgb.clip(0,255).astype('uint8');im=Image.fromarray(rgb);dr=ImageDraw.Draw(im);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',22)
for name,a in j['anchors'].items():
 p=np.array(a['inner']);q=np.array(a['outer']);dr.line([pixel(*p),pixel(*q)],fill='white',width=2);x,y=pixel(*q);dr.ellipse((x-5,y-5,x+5,y+5),fill='white');dr.text((x+9,y-5),name,font=font,fill='white')
dr.text((28,24),'Same world scale | amber: classical | cyan: modern | pale: overlap',font=font,fill='white');im.save(O/'Classical_Modern_Coverage_Overlay.png')
# The last 12 authored segments must sit exactly on each historical fade centerline.
routes=json.loads((D/'layout-modules.json').read_text())['routes'];checks=[]
for name,a in j['anchors'].items():
 pts=np.array(routes[name])[-13:];start=np.array(a['inner']);out=np.array(a['outer']);d=out-start;d/=np.linalg.norm(d);cross=(pts[:,0]-start[0])*d[1]-(pts[:,1]-start[1])*d[0];error=float(np.max(np.abs(cross)));endpoint=float(np.linalg.norm(pts[-1]-out));assert error<1e-4 and endpoint<1e-4
 checks.append({'exit':name,'source':a['source_object'],'max_centerline_error':error,'endpoint_error':endpoint})
assert hashlib.sha256(Path(j['source']).read_bytes()).hexdigest()==j['sha256']
(O/'classical-alignment-validation.json').write_text(json.dumps({'source_unchanged':True,'world_scale':1,'exits':checks,'widths':widths,'note':'Centerlines and endpoint tangents exact; modern paved carriageway has a clean edge, while historical masks have broad low-alpha shoulders. Sixth historical spur omitted per five-exit brief.'},indent=2));print('EXACT_EXIT_ALIGNMENT_PASS')
