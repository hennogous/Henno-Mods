"""Audit installed native UV triangle intersections for every registered bread swatch."""
from bakery_props_atlas import *
import xml.etree.ElementTree as ET,subprocess,re
from PIL import Image,ImageDraw
MOD=ROOT/'Civ Supply Chains';suffix='';dest=OUT/'native-emissive-audit';dest.mkdir(exist_ok=True)
def txt(e,p):
 n=e.find(p);return n.get('text',n.text or '') if n is not None else ''
materials={p.stem for p in (MOD/'Materials').glob('*.mtl') if 'CSC_Props_Shared_01' in p.read_text(encoding='utf-8-sig')};refs={}
for p in (MOD/'Assets').glob('*.ast'):
 tree=ET.parse(p)
 for model in tree.findall('.//m_ModelInstances/Element'):
  geo=txt(model,'m_GeoName')
  for group in model.findall('m_GroupStates/Element'):
   values=group.findall('m_Values/m_Values/Element')
   if any(txt(v,'m_ParamName')=='Material' and txt(v,'m_ObjectName') in materials for v in values):refs.setdefault(geo,{}).setdefault(txt(group,'m_MeshName'),set()).add(p.stem)
regions=[dict(name='coals_candidate',slot=0,bounds=[130,133,180,169])];records={'coals_candidate':dict(consumers=[],triangle_count=0,uv_area_pixels=0)};overlays={'coals_candidate':Image.new('RGB',(200,144))}
def clip(poly,axis,bound,greater):
 out=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  ia=(a[axis]>=bound) if greater else (a[axis]<=bound);ib=(b[axis]>=bound) if greater else (b[axis]<=bound)
  if ia:out.append(a)
  if ia!=ib:
   t=(bound-a[axis])/(b[axis]-a[axis]);out.append([a[0]+t*(b[0]-a[0]),a[1]+t*(b[1]-a[1])])
 return out
def area(p):return abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(p,p[1:]+p[:1])))/2 if p else 0
geos=[]
for geo,meshes in refs.items():
 fgx=(OUT/(geo+'.fgx')) if suffix and (OUT/(geo+'.fgx')).exists() else MOD/'Geometries'/(geo+'.fgx');assert fgx.exists(),geo;cn6=dest/(geo+'.cn6');run=subprocess.run([str(ROOT/'project/tools/cn6libs/FGXToCN6.exe'),str(fgx),str(cn6)],cwd=ROOT/'project/tools/cn6libs',capture_output=True,text=True,creationflags=subprocess.CREATE_NO_WINDOW);assert run.returncode==0,(geo,run.stderr);geos.append(dict(geometry=geo,fgx_sha256=sha(fgx),mesh_refs={k:sorted(v) for k,v in meshes.items()}))
 for chunk in cn6.read_text().split('mesh:"')[1:]:
  name,body=chunk.split('"',1)
  if name not in meshes:continue
  vb,tb=body.split('vertices\n',1)[1].split('triangles\n',1);vertices=[[float(x) for x in l.split()] for l in vb.strip().splitlines()];tris=[[int(x) for x in l.split()] for l in tb.split('\nend')[0].strip().splitlines()]
  for r in regions:
   x,y,x1,y1=r['bounds'];count=0;total=0;draw=ImageDraw.Draw(overlays[r['name']])
   for tri in tris:
    poly=[[vertices[i][16]*256,vertices[i][17]*256] for i in tri[:3]]
    for axis,bound,greater in [(0,x,True),(0,x1,False),(1,y,True),(1,y1,False)]:poly=clip(poly,axis,bound,greater) if poly else []
    a=area(poly)
    if a>1e-5 or any(x<vertices[i][16]*256<x1 and y<vertices[i][17]*256<y1 for i in tri[:3]):
     count+=1;total+=a;pts=[((v[0]-x)*4,(v[1]-y)*4) for v in poly];draw.line(pts+[pts[0]],fill=(0,230,255),width=1)
   if count:
    rec=records[r['name']];rec['consumers'].append(dict(geometry=geo,mesh=name,assets=sorted(meshes[name]),triangles=count,uv_area_pixels=total));rec['triangle_count']+=count;rec['uv_area_pixels']+=total
for name,im in overlays.items():im.save(OUT/(name+'-UV3-before.jpg'),quality=95)
report=dict(shared_materials=sorted(materials),installed_shared_geometry_count=len(geos),installed_shared_asset_count=len({a for meshes in refs.values() for assets in meshes.values() for a in assets}),geometries=geos,bread_regions=records,unused_bread_regions=[n for n,r in records.items() if not r['consumers']],method='Fresh FGXToCN6 extraction of every installed AST geometry mesh bound to current shared atlas material; positive-area UV3 triangle/region clipping, no vertex-only approximation.')
(OUT/'native-emissive-candidate-audit.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k not in ['geometries','bread_regions']}));print(json.dumps(records))


