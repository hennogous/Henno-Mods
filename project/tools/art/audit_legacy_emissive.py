"""Conservative runtime E sampling audit, including degenerate UV triangles."""
from bakery_props_atlas import *
from PIL import Image
import numpy as np
MOD=ROOT/'Civ Supply Chains'
report=json.loads((OUT/'native-emissive-candidate-audit.json').read_text())
a=np.asarray(Image.open(MOD/'Textures/CSC_Atlas_E.dds').convert('RGB'));lit=np.max(a,axis=2)>0
# Expand by one texel in all directions to conservatively cover bilinear filtering.
pad=np.pad(lit,1,mode='wrap');support=np.zeros_like(lit)
for y in range(3):
 for x in range(3):support|=pad[y:y+256,x:x+256]
ys,xs=np.where(support);pixels=np.column_stack((xs,ys));rows=[]
def intersects(poly,x,y):
 # Separating-axis triangle vs pixel box, also valid for degenerate triangles.
 box=np.array([[x,y],[x+1,y],[x+1,y+1],[x,y+1]],float)
 axes=[np.array([1.,0]),np.array([0.,1])]
 for p,q in zip(poly,np.roll(poly,-1,axis=0)):
  d=q-p
  if np.linalg.norm(d)>1e-10:axes.append(np.array([-d[1],d[0]]))
 return all(not ((poly@v).max()<(box@v).min() or (box@v).max()<(poly@v).min()) for v in axes)
for rec in report['geometries']:
 p=OUT/'native-emissive-audit'/(rec['geometry']+'.cn6')
 if '--after' in sys.argv and rec['geometry']=='CSC_BAKERS_Oven_v2':p=OUT/'CSC_BAKERS_Oven_v2-roundtrip.cn6'
 for chunk in p.read_text().split('mesh:"')[1:]:
  name,body=chunk.split('"',1)
  if name not in rec['mesh_refs']:continue
  vb,tb=body.split('vertices\n',1)[1].split('triangles\n',1);v=np.array([[float(x) for x in l.split()] for l in vb.strip().splitlines()]);tri=[[int(x) for x in l.split()[:3]] for l in tb.split('\nend')[0].strip().splitlines()];hits=[]
  for i,t in enumerate(tri):
   uv=v[t,16:18]*256;lo=uv.min(axis=0);hi=uv.max(axis=0)
   candidates=pixels[(pixels[:,0]+1>=lo[0])&(pixels[:,0]<=hi[0])&(pixels[:,1]+1>=lo[1])&(pixels[:,1]<=hi[1])]
   if any(intersects(uv,int(x),int(y)) for x,y in candidates):hits.append(i)
  rows.append(dict(geometry=rec['geometry'],mesh=name,triangles=len(tri),emissive_triangles=hits))
bad=[r for r in rows if r['emissive_triangles'] and r['geometry']!='CSC_BAKERS_Oven_v2']
out=dict(texture=str(MOD/'Textures/CSC_Atlas_E.dds'),sha256=sha(MOD/'Textures/CSC_Atlas_E.dds'),method='Every triangle versus actual nonzero runtime RGB texels expanded one texel for bilinear support; separating-axis intersection includes degenerate constant UVs.',geometries=len(report['geometries']),meshes=rows,unintended_other_prop_consumers=bad)
(OUT/('legacy-emissive-audit-after.json' if '--after' in sys.argv else 'legacy-emissive-audit-before.json')).write_text(json.dumps(out,indent=2));print(json.dumps([dict(geometry=r['geometry'],mesh=r['mesh'],hits=len(r['emissive_triangles'])) for r in rows if r['emissive_triangles']]))
