"""Measure delivery paths against the road decal's opaque texture footprint."""
import json,re,sys
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
OUT=Path(r'C:\Users\Shadow\Desktop\Codex\CSC_Storage_L\delivery-01')
rows=json.loads((OUT/'road-reference.json').read_text())
native={}
for chunk in (OUT/'road-native.cn6').read_text().split('mesh:"')[1:]:
 name=chunk.split('"',1)[0]
 native[name]=np.array([[float(v) for v in line.split()[:3]] for line in chunk.split('vertices\n')[1].split('triangles')[0].strip().splitlines()])
relevant=[r for r in rows if any(n in r['name'] for n in ('Curve_L.001_CLA','Curve_M.008_CLA','Curve_M.007_CLA','Curve_M.001_CLA','Curve_M.010_CLA','Curve_M.009_CLA','Curve_M.002_CLA'))]
images={p:np.asarray(Image.open(p).convert('RGBA'))[:,:,3]/255. for r in relevant for _,p in r['images']}
def opacity(points,roads=relevant):
 points=np.asarray(points);answer=np.zeros(len(points))
 for r in roads:
  verts=np.array(r['vertices'])[:,:2];tex=images[r['images'][0][1]];h,w=tex.shape
  for indices,uvs in zip(r['polygons'],r['uvs']):
   v=verts[indices];uvs=np.array(uvs)
   weights=(points-v[0])@np.linalg.inv(np.stack((v[1]-v[0],v[2]-v[0]),axis=0))
   inside=(weights[:,0]>=-1e-5)&(weights[:,1]>=-1e-5)&(weights.sum(axis=1)<=1.00001)
   uv=uvs[0]+weights@(uvs[1:]-uvs[0]);x=uv[:,0]*(w-1);y=(1-uv[:,1])*(h-1)
   x=np.clip(x,0,w-1);y=np.clip(y,0,h-1);ix=x.astype(int);iy=y.astype(int);fx=x-ix;fy=y-iy
   a=(tex[iy,ix]*(1-fx)+tex[iy,np.minimum(ix+1,w-1)]*fx)*(1-fy)+(tex[np.minimum(iy+1,h-1),ix]*(1-fx)+tex[np.minimum(iy+1,h-1),np.minimum(ix+1,w-1)]*fx)*fy
   answer=np.maximum(answer,np.where(inside,a,0))
 return answer
native_error=max(min(np.linalg.norm(np.array(p[:2])-v[:2]) for v in native[r['name'].split('#')[0]]) for r in relevant for p in r['vertices'])
assert native_error<.001,native_error
centres=[]
for y in range(-180,81,10):
 x=np.arange(-175,0,.1);a=opacity(np.column_stack((x,np.full(len(x),y))),[r for r in relevant if 'Curve_L.001' in r['name'] or 'Curve_M.008' in r['name']])
 # Choose the main north/south branch, before its junction with the cross-road.
 keep=a>.6
 if keep.any():centres.append([round(float(np.average(x[keep],weights=a[keep])),2),y,round(float(x[keep].min()),2),round(float(x[keep].max()),2)])
result={'native_reference_xy_error':native_error,'road_centres_x_y_left_right':centres}
if '--route' in sys.argv:
 author=json.loads((OUT/'authoring-check.json').read_text());routes=author['route_centerlines']
 result['routes']={}
 im=Image.open(OUT/'layout-top.png');draw=ImageDraw.Draw(im)
 for name,color in [('outbound','red'),('return','cyan')]:
  points=np.array(routes[name])[:,:2]
  shared=(points[:,1]>=-178)&(points[:,1]<=60)&(points[:,0]<-25)
  front=(points[:,1]<-178)&(points[:,1]>=-211)&(points[:,0]<-40)&(author['body_scale']<1.0)
  road_points=points[shared|front]
  alpha=opacity(road_points)
  result['routes'][name]={'samples':len(alpha),'minimum_opacity':float(alpha.min()),'mean_opacity':float(alpha.mean()),'fraction_above_half_opacity':float((alpha>.5).mean())}
  if '--require-on-road' in sys.argv:assert np.all(alpha>.5),(name,result['routes'][name])
  draw.line([(550+x/.6,550-y/.6) for x,y in points],fill=color,width=2)
 im.save(OUT/'route-road-diagnostic.png')
(OUT/'road-alignment-check.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
