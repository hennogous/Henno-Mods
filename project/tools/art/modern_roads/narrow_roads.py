"""Calibrated road cross-sections; preserve painted atlases and route anchors."""
from pathlib import Path
import sys,json,math,shutil,hashlib
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(Path(__file__).parent))
import raise_tarmac as z
D=z.D;A=z.A;O=A/'vanilla-width-calibration-20261029';MOD=z.MOD
RATIO=15/26
sha=z.sha;dump=z.dump

def prepare():
 z.O=O;z.prepare()

def build():
 import bpy
 from mathutils import Vector
 sys.path[:0]=[str(ROOT/'project/tools/blender'),str(ROOT/'project/tools/blender/scene_export')]
 from csc_scene_validation import suspend_csc_repairs,validate_current_scene
 import decode_blend as dec
 baseline=json.loads((O/'baseline.json').read_text());reports=[]
 manifest=json.loads((D/'atlas-layout.json').read_text());cx,cy=manifest['roundabout']['center']
 def warp(x,y):
  dx=x-cx;dy=y-cy;r=math.hypot(dx,dy)
  candidates=[(cx+68*dx/max(r,.00001),cy+68*dy/max(r,.00001))]
  for angle in manifest['roundabout']['angles_degrees']:
   t=math.radians(angle);vx=math.cos(t);vy=math.sin(t);along=max(68,min(105,dx*vx+dy*vy));candidates.append((cx+vx*along,cy+vy*along))
  qx,qy=min(candidates,key=lambda q:(q[0]-x)**2+(q[1]-y)**2)
  return qx+(x-qx)*RATIO,qy+(y-qy)*RATIO
 for p in sorted(D.rglob('*.blend')):
  assert sha(p)==baseline[str(p)],('Source changed',p)
  with suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(p),load_ui=False,use_scripts=False)
  for s in bpy.data.scenes:bpy.context.window.scene=s;bpy.context.view_layer.update()
  objects={o.name:o for s in bpy.data.scenes for o in s.objects};seen=set();rings=0
  for ob in objects.values():
   if ob.type!='MESH' or not any(s.material and s.material.name.startswith('CSC_Roads_') for s in ob.material_slots) or ob.data.as_pointer() in seen:continue
   me=ob.data;seen.add(me.as_pointer())
   if 'Roundabout' in ob.name:
    assert len(me.vertices)==4,(p,ob.name)
    # A small editable grid lets the ring and its five mouths contract across
    # their width without scaling the layout or resampling any painted maps.
    olduv={li.vertex_index:[tuple(layer.data[li.index].uv) for layer in me.uv_layers] for li in me.loops}
    xmin=min(v.co.x for v in me.vertices);xmax=max(v.co.x for v in me.vertices);ymin=min(v.co.y for v in me.vertices);ymax=max(v.co.y for v in me.vertices)
    corners={('R' if v.co.x>(xmin+xmax)/2 else 'L')+('T' if v.co.y>(ymin+ymax)/2 else 'B'):olduv[v.index] for v in me.vertices}
    n=24;verts=[];uvs=[];faces=[]
    for j in range(n+1):
     v=j/n
     for k in range(n+1):
      u=k/n;x=xmin+(xmax-xmin)*u;y=ymin+(ymax-ymin)*v;xx,yy=warp(x,y);verts.append((xx,yy,0))
      uvs.append([tuple((1-u)*(1-v)*corners['LB'][ch][a]+u*(1-v)*corners['RB'][ch][a]+u*v*corners['RT'][ch][a]+(1-u)*v*corners['LT'][ch][a] for a in range(2)) for ch in range(3)])
    for j in range(n):
     for k in range(n):
      q=j*(n+1)+k;faces.append((q,q+1,q+n+2,q+n+1))
    mats=list(me.materials);me.clear_geometry();me.from_pydata(verts,[],faces);me.update()
    while me.uv_layers:me.uv_layers.remove(me.uv_layers[0])
    for name in ['UV1','UV2','UV3']:me.uv_layers.new(name=name)
    for ch,layer in enumerate(me.uv_layers):
     for li in me.loops:layer.data[li.index].uv=uvs[li.vertex_index][ch]
    assert len(me.uv_layers)==3
    for other in objects.values():
     if other.type=='MESH' and other.data==me:
      group=other.vertex_groups.get('Bone') or other.vertex_groups.new(name='Bone');group.add(list(range(len(verts))),1,'REPLACE')
    rings+=1
   else:
    assert len(me.vertices)%2==0
    for k in range(0,len(me.vertices),2):
     a,b=me.vertices[k:k+2];mid=(a.co+b.co)/2
     a.co=mid+(a.co-mid)*RATIO;b.co=mid+(b.co-mid)*RATIO
    me.update()
  for s in bpy.data.scenes:s['road_nominal_width']=15;s['connector_nominal_width']=18*RATIO
  text=bpy.data.texts.get('START HERE')
  if text:text.write('\nVanilla-calibrated road widths: main 15, connector 10.38; fixed route centerlines and roundabout center. Stone Z0 / tarmac Z1.\n')
  bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(p),relative_remap=False)
  with suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(p),load_ui=False,use_scripts=False)
  bpy.context.window.scene=bpy.data.scenes['Export'];bpy.context.view_layer.update()
  meshes=[]
  for ob in bpy.context.scene.objects:
   if ob.type!='MESH':continue
   m=dec.decode_mesh(ob,ob.matrix_world);m['name']=p.stem if p.parent.name=='modules' else ob.name
   for mat in m['materials']:mat['external']=mat['name']
   expected=1 if m['materials'][0]['name']=='CSC_Roads_Modern_01' else 0
   assert all(abs(v[2]-expected)<1e-5 for v in m['vertices'])
   meshes.append(m)
  check=validate_current_scene();assert check['automated_pass'],check['findings']
  dump(O/'models'/(p.stem+'.json'),{'asset_id':p.stem,'kind':'decal','meshes':meshes})
  reports.append({'id':p.stem,'source':str(p),'sha256':sha(p),'automated_pass':True,'ring_meshes':rings})
 dump(O/'saved-validation.json',reports);print('SAVED_WIDTH_PASS',len(reports),flush=True)

def stage():
 import integrate as i
 n=i.n;stage=O/'staged';checks=[]
 for f in ('Geometries','Materials','Textures','Assets','CN6'):(stage/f).mkdir(parents=True,exist_ok=True)
 reader,_=n.helper(O/'native-reader');converter=ROOT/'project/tools/cn6libs/CN6ToFGX.exe'
 libs=converter.parent;repair=reader.parent/'RepairRoadMaterials.exe'
 refs=['System.Windows.Forms.dll',str(libs/'CivNexus6.exe')]+[str(p) for p in libs.glob('Firaxis.*.dll')]
 i.run(['C:/Windows/Microsoft.NET/Framework64/v4.0.30319/csc.exe','/nologo','/target:exe','/platform:x64','/out:'+str(repair)]+['/reference:'+r for r in refs]+[Path(__file__).with_name('RepairRoadMaterials.cs')],O/'material-compile.log')
 for row in json.loads((O/'saved-validation.json').read_text()):
  name=row['id']
  if name=='CSC_ALL_Modern_Roundabout_Kit':continue
  if 'STAGE_IDS' in globals() and name not in STAGE_IDS:continue
  m=json.loads((O/'models'/(name+'.json')).read_text());g=n.read(MOD/'Geometries'/(name+'.geo'))
  order=[n.exp.txt(r,'m_Name') for r in g.findall('m_Meshes/Element')];byname={x['name']:x for x in m['meshes']};assert set(order)==set(byname);m['meshes']=[byname[k] for k in order];dump(O/'models'/(name+'.json'),m)
  cn6=stage/'CN6'/(name+'.cn6');fgx=stage/'Geometries'/(name+'.fgx');n.exp.write_cn6(cn6,m)
  i.run([converter,cn6,fgx,'2'],O/(name+'-convert.log'),converter.parent)
  fixed=O/(name+'-bindings.fgx')
  i.run([repair,fgx,MOD/'Geometries'/(name+'.fgx'),fixed],O/(name+'-bindings.log'),reader.parent);shutil.copy2(fixed,fgx)
  i.run([reader,reader.parent,fgx,O/(name+'-native.json')],O/(name+'-read.log'),reader.parent)
  native=json.loads((O/(name+'-native.json')).read_text());assert len(native['meshes'])==len(m['meshes']);error=0
  for a,b,gr in zip(m['meshes'],native['meshes'],g.findall('m_Meshes/Element')):
   assert a['name']==b['name'] and a['triangles']==b['triangles'] and len(a['vertices'])==len(b['vertices'])
   assert b['boneBindings']==['Bone'] and b['materialName']==a['materials'][0]['name']
   for v,w in zip(a['vertices'],b['vertices']):
    vals=w['position']+w['normal']+w['tangent']+w['binormal']+w['uv']+w['uv2']+w['uv3'];error=max(error,max(abs(x-y) for x,y in zip(v,vals)))
    assert w['boneIndices']==[0]*8 and w['boneWeights']==[255,0,0,0,0,0,0,0]
   for tag,count in [('m_nVertexCount',len(a['vertices'])),('m_nPrimitiveCount',len(a['triangles']))]:gr.find(tag).text=str(count)
   groups=gr.findall('m_Groups/Element');assert len(groups)==1;groups[0].find('m_nPrims').text=str(len(a['triangles']))
  assert error<1e-4
  n.save(stage/'Geometries'/(name+'.geo'),g)
  n.save(stage/'Assets'/(name+'.ast'),n.fresh_asset(name,m,n.read(MOD/'Assets/CSC_BAKERS_Wind_Mill_Modern.ast')))
  checks.append({'id':name,'native_max_error':error,'source':row['source'],'sha256':row['sha256']})
 for folder,pattern in [('Materials','CSC_Roads_*.mtl'),('Textures','CSC_Roads_*')]:
  for p in (MOD/folder).glob(pattern):
   if not (stage/folder/p.name).exists():shutil.copy2(p,stage/folder/p.name)
 expected=len(STAGE_IDS) if 'STAGE_IDS' in globals() else len([r for r in json.loads((O/'saved-validation.json').read_text()) if r['id']!='CSC_ALL_Modern_Roundabout_Kit'])
 assert len(checks)==expected;dump(O/'staging-validation.json',checks);print('NATIVE_WIDTH_PASS',len(checks),flush=True)

def publish():
 import integrate as i
 cook=json.loads((O/'cook-check/result.json').read_text());assert cook['exit_code']==0 and cook['blps']
 rows=json.loads((O/'staging-validation.json').read_text());base=json.loads((O/'baseline.json').read_text());files=[]
 for r in rows:
  assert sha(r['source'])==r['sha256']
  for suffix in ['.fgx','.geo']:
   target=MOD/'Geometries'/(r['id']+suffix);assert sha(target)==base[str(target)]
 for r in rows:
  for suffix in ['.fgx','.geo']:
   target=MOD/'Geometries'/(r['id']+suffix);backup=O/'before/Geometries'/target.name;backup.parent.mkdir(exist_ok=True);shutil.copy2(target,backup);shutil.copy2(O/'staged/Geometries'/target.name,target);files.append({'destination':str(target),'before':base[str(target)],'after':sha(target)})
  shutil.copy2(O/'staged/CN6'/(r['id']+'.cn6'),Path(r['source']).with_suffix('.cn6'))
 allowed={r['destination'] for r in files}|{r['source'] for r in json.loads((O/'saved-validation.json').read_text())}|{str(Path(r['source']).with_suffix('.cn6')) for r in rows}
 allowed|={str(D/'atlas-layout.json'),str(D/'layout-modules.json')}
 for path,digest in base.items():
  if path not in allowed and Path(path).parent!=MOD/'Assets':assert sha(path)==digest,('Unexpected change',path)
 dump(O/'publication-report.json',{'installed':True,'files':files,'main_road_width':15,'connector_width':18*RATIO,'textures_unchanged':True,'AE_assemblies_written':False,'stone_z':0,'tarmac_z':1})
 i.n.cache(O);i.OUT=O;i.verify();print('CALIBRATED_WIDTH_INSTALLED',flush=True)

def maintain():
 z.O=O;z.maintain()
 for filename in ['atlas-layout.json','layout-modules.json']:
  p=D/filename;data=json.loads(p.read_text());data['width_calibration']={'main':15,'connector':18*RATIO,'previous_main':26,'ratio':RATIO,'evidence':str(O/'measurement.json'),'method':'Cross-section mesh contraction; painted atlas untouched; centerlines unchanged'};dump(p,data)

if __name__=='__main__':
 mode=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else sys.argv[1];globals()[mode]()
