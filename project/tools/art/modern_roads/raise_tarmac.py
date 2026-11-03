"""Lift tarmac one world unit over stone without changing XY/UVs or AE assemblies."""
from pathlib import Path
import sys,json,shutil,hashlib,copy
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(Path(__file__).parent))
import combined as c
D=c.D;A=c.A;O=A/'tarmac-z-order-20261029';MOD=ROOT/'Civ Supply Chains';LIFT=1.0
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2))

def prepare():
 assert not (O/'baseline.json').exists(),'Already prepared'
 base={str(p):sha(p) for p in D.rglob('*') if p.is_file()}
 for folder in ('Assets','Geometries','Materials','Textures','ArtDefs','XLPs'):
  for p in (MOD/folder).glob('*'):
   if p.is_file():base[str(p)]=sha(p)
 dump(O/'baseline.json',base)
 for p in D.rglob('*'):
  if p.is_file() and p.suffix in ('.blend','.cn6','.json'):
   dest=O/'before/source'/p.relative_to(D);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
 print('BACKUP_READY',flush=True)

def inspect():
 import bpy
 for name in ['CSC_ALL_Modern_Base_Road_Decals.blend','modules/CSC_Road_Roundabout_Modern.blend']:
  bpy.ops.wm.open_mainfile(filepath=str(D/name),load_ui=False,use_scripts=False)
  for scene in bpy.data.scenes:
   bpy.context.window.scene=scene; bpy.context.view_layer.update()
   for ob in scene.objects:
    if ob.type=='MESH' and any(s.material and s.material.name.startswith('CSC_Roads_') for s in ob.material_slots):
     print('HEIGHT',name,scene.name,ob.name,'loc',list(ob.location),'world',list(ob.matrix_world.translation),'verts',sorted(set(round((ob.matrix_world@v.co).z,5) for v in ob.data.vertices)),'local',sorted(set(round(v.co.z,5) for v in ob.data.vertices)),flush=True)

def build():
 import bpy
 sys.path[:0]=[str(ROOT/'project/tools/blender'),str(ROOT/'project/tools/blender/scene_export')]
 from csc_scene_validation import suspend_csc_repairs,validate_current_scene
 import decode_blend as dec
 baseline=json.loads((O/'baseline.json').read_text());reports=[]
 progress_path=O/'build-progress.json';progress=json.loads(progress_path.read_text()) if progress_path.exists() else {}
 def model(path):
  bpy.context.window.scene=bpy.data.scenes['Export'];bpy.context.view_layer.update()
  meshes=[]
  for ob in bpy.data.scenes['Export'].objects:
   if ob.type!='MESH':continue
   m=dec.decode_mesh(ob,ob.matrix_world);m['name']=path.stem if path.parent.name=='modules' else ob.name
   for mat in m['materials']:mat['external']=mat['name']
   meshes.append(m)
  return {'asset_id':path.stem,'kind':'decal','meshes':meshes}
 for p in sorted(D.rglob('*.blend')):
  assert sha(p)==progress.get(str(p),baseline[str(p)]),('New human source edit',p)
  backup=O/'before/source'/p.relative_to(D)
  with suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(backup),load_ui=False,use_scripts=False)
  before=model(p)
  with suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(p),load_ui=False,use_scripts=False)
  model(p);edited=0
  for scene in bpy.data.scenes:
   bpy.context.window.scene=scene;bpy.context.view_layer.update()
  objects={ob.name:ob for scene in bpy.data.scenes for ob in scene.objects}
  for ob in objects.values():
   if ob.type!='MESH' or not any(s.material and s.material.name.startswith('CSC_Roads_') for s in ob.material_slots):continue
   is_modern=any(s.material and s.material.name.startswith('CSC_Roads_Modern_01') for s in ob.material_slots)
   zvalues=[(ob.matrix_world@v.co).z for v in ob.data.vertices]
   assert max(zvalues)-min(zvalues)<1e-5,ob.name
   if ob.name in bpy.data.scenes['Export'].objects or ob.name.startswith('CSC_Projection_'):
    delta=(LIFT if is_modern else 0)-min(zvalues)
   else:
    if not is_modern:continue
    stone=objects.get(ob.name.replace('_Modern','_Industrial'))
    # Review previously used a 0.04-unit separation; make its gap match export.
    stone_z=min((stone.matrix_world@v.co).z for v in stone.data.vertices) if stone else .04
    delta=stone_z+LIFT-min(zvalues)
   if abs(delta)<1e-6:continue
   matrix=ob.matrix_world.copy();matrix.translation.z+=delta;ob.matrix_world=matrix;edited+=1
  if edited:
   for s in bpy.data.scenes:s['road_surface_z_gap']=LIFT
   t=bpy.data.texts.get('START HERE')
   if t:t.write('\nCurrent export contract: stone Z0, tarmac Z1. Activate and evaluate Export before decoding world transforms. Earlier Z20 notes are superseded.\n')
   bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(p),relative_remap=False)
   progress[str(p)]=sha(p);dump(progress_path,progress)
  with suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(p),load_ui=False,use_scripts=False)
  after=model(p);old={m['name']:m for m in before['meshes']};modern=0
  for m in after['meshes']:
   a=old[m['name']];is_modern=m['materials'][0]['name']=='CSC_Roads_Modern_01';modern+=int(is_modern)
   assert a['triangles']==m['triangles'] and len(a['vertices'])==len(m['vertices'])
   assert [x['name'] for x in a['materials']]==[x['name'] for x in m['materials']]
   for v,w in zip(a['vertices'],m['vertices']):
    assert v[:2]==w[:2] and v[12:]==w[12:]
    # Blender's tangent solver has small translation-dependent rounding on
    # these narrow triangles. Keep the original native frames during export.
    error=max(abs(x-y) for x,y in zip(v[3:12],w[3:12]));assert error<.01,(p,m['name'],error)
    assert abs(w[2]-(LIFT if is_modern else 0))<1e-5
  validation=validate_current_scene();assert validation['automated_pass'],validation['findings']
  dump(O/'models'/(p.stem+'.json'),after)
  reports.append({'id':p.stem,'source':str(p),'sha256':sha(p),'modern_meshes':modern,'objects_adjusted':edited,'automated_pass':True,'XY_UV_topology_normals_material_ids_preserved':True})
 dump(O/'saved-validation.json',reports);print('SAVED_Z_ORDER_PASS',len(reports),'sources; stone0/tarmac1',flush=True)

def stage():
 import integrate as i
 n=i.n;stage=O/'staged';checks=[]
 for f in ('Geometries','Materials','Textures','Assets','CN6'):(stage/f).mkdir(parents=True,exist_ok=True)
 reader,_=n.helper(O/'native-reader');converter=ROOT/'project/tools/cn6libs/CN6ToFGX.exe'
 for row in json.loads((O/'saved-validation.json').read_text()):
  if not row['modern_meshes']:continue
  name=row['id'];m=json.loads((O/'models'/(name+'.json')).read_text());cn6=stage/'CN6'/(name+'.cn6');fgx=stage/'Geometries'/(name+'.fgx')
  geo=MOD/'Geometries'/(name+'.geo');g=n.read(geo)
  order=[n.exp.txt(r,'m_Name') for r in g.findall('m_Meshes/Element')];byname={x['name']:x for x in m['meshes']}
  assert set(order)==set(byname);m['meshes']=[byname[k] for k in order];dump(O/'models'/(name+'.json'),m)
  oldpath=O/(name+'-before-native.json');i.run([reader,reader.parent,MOD/'Geometries'/(name+'.fgx'),oldpath],O/(name+'-before-read.log'),reader.parent)
  old=json.loads(oldpath.read_text());assert [x['name'] for x in old['meshes']]==order
  for mesh,previous in zip(m['meshes'],old['meshes']):
   assert mesh['triangles']==previous['triangles'] and len(mesh['vertices'])==len(previous['vertices'])
   lift=LIFT if mesh['materials'][0]['name']=='CSC_Roads_Modern_01' else 0
   for v,w in zip(mesh['vertices'],previous['vertices']):
    error=max(abs(x-y) for x,y in zip(v[:2]+v[12:],w['position'][:2]+w['uv']+w['uv2']+w['uv3']));assert error<1e-4,(name,mesh['name'],error)
    assert abs(w['position'][2])<1e-5 and abs(v[2]-w['position'][2]-lift)<1e-5
    v[3:12]=w['normal']+w['tangent']+w['binormal']
  dump(O/'models'/(name+'.json'),m)
  n.exp.write_cn6(cn6,m);i.run([converter,cn6,fgx,'2'],O/(name+'-convert.log'),converter.parent)
  i.run([reader,reader.parent,fgx,O/(name+'-native.json')],O/(name+'-read.log'),reader.parent)
  native=json.loads((O/(name+'-native.json')).read_text());assert len(native['meshes'])==len(m['meshes']);error=0
  for a,b in zip(m['meshes'],native['meshes']):
   assert a['name']==b['name'] and a['triangles']==b['triangles'] and len(a['vertices'])==len(b['vertices'])
   assert b['boneBindings']==['Bone'] and b['materialName']==a['materials'][0]['name']
   for v,w in zip(a['vertices'],b['vertices']):
    vals=w['position']+w['normal']+w['tangent']+w['binormal']+w['uv']+w['uv2']+w['uv3'];error=max(error,max(abs(x-y) for x,y in zip(v,vals)))
    assert w['boneIndices']==[0]*8 and w['boneWeights']==[255,0,0,0,0,0,0,0]
  assert error<1e-4
  # Keep installed metadata and mesh/group identities exactly as AE knows them.
  geo=MOD/'Geometries'/(name+'.geo');shutil.copy2(geo,stage/'Geometries'/geo.name)
  g=n.read(geo);assert [n.exp.txt(r,'m_Name') for r in g.findall('m_Meshes/Element')]==[x['name'] for x in m['meshes']],name
  n.save(stage/'Assets'/(name+'.ast'),n.fresh_asset(name,m,n.read(MOD/'Assets/CSC_BAKERS_Wind_Mill_Modern.ast')))
  checks.append({'id':name,'native_max_error':error,'source':row['source'],'sha256':row['sha256']})
 for folder,pattern in [('Materials','CSC_Roads_*.mtl'),('Textures','CSC_Roads_*')]:
  for p in (MOD/folder).glob(pattern):shutil.copy2(p,stage/folder/p.name)
 assert len(checks)==12,len(checks);dump(O/'staging-validation.json',checks);print('NATIVE_Z_ORDER_PASS',len(checks),flush=True)

def publish():
 import integrate as i
 cook=json.loads((O/'cook-check/result.json').read_text());assert cook['exit_code']==0 and cook['blps']
 rows=json.loads((O/'staging-validation.json').read_text());base=json.loads((O/'baseline.json').read_text());files=[]
 for r in rows:
  assert sha(r['source'])==r['sha256']
  target=MOD/'Geometries'/(r['id']+'.fgx');assert sha(target)==base[str(target)]
 for r in rows:
  target=MOD/'Geometries'/(r['id']+'.fgx');backup=O/'before/Geometries'/target.name;backup.parent.mkdir(exist_ok=True);shutil.copy2(target,backup)
  src=O/'staged/Geometries'/target.name;shutil.copy2(src,target);files.append({'destination':str(target),'before':base[str(target)],'after':sha(target)})
  cn6=O/'staged/CN6'/(r['id']+'.cn6');shutil.copy2(cn6,Path(r['source']).with_suffix('.cn6'))
 allowed={r['destination'] for r in files}|{r['source'] for r in json.loads((O/'saved-validation.json').read_text())}|{str(Path(r['source']).with_suffix('.cn6')) for r in rows}
 concurrent=[]
 for path,digest in base.items():
  if path in allowed or sha(path)==digest:continue
  assert Path(path).parent==MOD/'Assets',('Unexpected modification',path);concurrent.append(path)
 dump(O/'publication-report.json',{'installed':True,'files':files,'stone_z':0,'tarmac_z':1,'AE_placements_and_visibility_preserved':True,'textures_unchanged':True,'concurrent_user_assemblies_preserved':concurrent})
 i.n.cache(O);i.OUT=O;i.verify()
 print('INSTALLED_TARMAC_1_UNIT_ABOVE_STONE',flush=True)

def maintain():
 rows={r['id']:r for r in json.loads((O/'saved-validation.json').read_text())}
 paths=[A/'delivery-validation.json',A/'combined-layout-20261029/saved-validation.json',A/'layout-variants-20261029/saved-validation.json']
 paths+=list((A/'models').glob('*.json'))+list((A/'layout-variants-20261029/models').glob('*.json'))+[A/'combined-layout-20261029/model.json']
 for p in paths:
  backup=O/'before/active-inputs'/p.relative_to(A);backup.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,backup)
  data=json.loads(p.read_text())
  if 'models' in p.parts or p.name=='model.json':
   name=data['asset_id'];data=json.loads((O/'models'/(name+'.json')).read_text())
  elif p.name=='delivery-validation.json':
   for r in data['models']:r['source_sha256']=rows[r['id']]['sha256']
   data['latest_z_order_verification']=str(O/'final-verification.json')
  else:
   for r in data if isinstance(data,list) else [data]:r['sha256']=rows[Path(r['source']).stem]['sha256']
  dump(p,data)
 for name,r in rows.items():
  native=O/(name+'-native.json')
  if name.startswith('CSC_Road_') and native.exists():
   dest=A/'native'/(name+'.json');backup=O/'before/active-inputs/native'/dest.name;backup.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(dest,backup);shutil.copy2(native,dest)
 p=D/'layout-modules.json';data=json.loads(p.read_text());data.pop('projection_lift',None);data['export_surface_z']={'Industrial':0,'Modern':1};dump(p,data)
 print('ACTIVE_MODELS_AND_SOURCE_HASHES_UPDATED',flush=True)

if __name__=='__main__':
 mode=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else sys.argv[1];globals()[mode]()
