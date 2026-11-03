"""Install only the new L2 state geometry, its AO cell and three state references."""
import sys,json,hashlib,shutil,subprocess,copy,xml.etree.ElementTree as E
from pathlib import Path
from PIL import Image,ImageChops
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT/'project/tools/art/modern_windmill'))
import modular_v9_native as n
from render_ae_asset import read_xml
exp=n.exp;MOD=n.MOD;A=Path.home()/'Desktop/Working Files/3D Art';O=Path.home()/'Desktop/Codex/modern-l2-states-20261029';D=O/'staged'
BASE='CSC_Level_2_Modern';ID=BASE+'_CON+PIL';IDS=(BASE,'CSC_BAKERS_Bakery_Modern','CSC_BAKERS_Bakery_Modern_2')
LIB=A/'Textures/CSC_Buildings_Modern';CUR=LIB/'Current';RECT=[1024,512,1536,1024]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2))
def run(cmd,log,cwd=None):
 r=subprocess.run(list(map(str,cmd)),cwd=cwd,capture_output=True,text=True);log.write_text(r.stdout+r.stderr);assert r.returncode==0,(cmd,r.stdout[-600:],r.stderr[-600:]);return r

def stage():
 for folder in ('Assets','Geometries','Materials','Textures','CN6'):(D/folder).mkdir(parents=True,exist_ok=True)
 baseline={str(p.relative_to(MOD)):sha(p) for folder in ('Assets','ArtDefs','Geometries','Materials','Textures','XLPs') for p in (MOD/folder).glob('*') if p.is_file()};baseline['Civ Supply Chains.civ6proj']=sha(MOD/'Civ Supply Chains.civ6proj');dump(O/'baseline.json',baseline)
 old=Image.open(CUR/'textures/CSC_Atlas_Modern_AO.png').convert('RGB');new=old.copy();patch=Image.open(O/'bakes'/(ID+'.png')).convert('RGB');assert patch.size==(512,512);new.paste(patch,RECT[:2])
 plan=json.loads((CUR/'atlas-plan.json').read_text())
 for key,(page,r) in plan['AO_allocations'].items():
  if page=='building':assert new.crop(r).tobytes()==old.crop(r).tobytes(),key
 diff=ImageChops.difference(new,old);bounds=diff.getbbox();assert bounds and bounds[0]>=RECT[0] and bounds[1]>=RECT[1] and bounds[2]<=RECT[2] and bounds[3]<=RECT[3]
 new.save(O/'textures/CSC_Atlas_Modern_AO.png');(O/'scalar').mkdir(exist_ok=True);src=O/'scalar/CSC_Atlas_Modern_AO.png';new.getchannel('R').save(src)
 run([ROOT/'project/tools/directxtex/texconv.exe','-nologo','-y','-m','0','-f','R8_UNORM','--ignore-srgb','-o',D/'Textures',src],O/'ao-convert.log')
 spec={'slot':'AO','size':[2048,2048],'format':'R8_UNORM'};dds=D/'Textures/CSC_Atlas_Modern_AO.dds';exp.normalize_ao_dds(dds,spec,MOD/'Textures/CSC_Props_Shared_01_AO.dds');exp.validate_dds(dds,spec)
 shutil.copy2(MOD/'Textures/CSC_Atlas_Modern_AO.tex',D/'Textures/CSC_Atlas_Modern_AO.tex')
 model=json.loads((O/'models'/(ID+'.json')).read_text());cn6=D/'CN6'/(ID+'.cn6');fgx=D/'Geometries'/(ID+'.fgx');exp.write_cn6(cn6,model);n.save(D/'Geometries'/(ID+'.geo'),exp.geometry(model,read_xml(MOD/'Geometries/CSC_Level_2_Modern.geo')))
 exe,_=n.helper(O/'native-reader');converter=ROOT/'project/tools/cn6libs/CN6ToFGX.exe';run([converter,cn6,fgx,'2'],O/'conversion.log',converter.parent)
 native_path=O/'native.json';run([exe,exe.parent,fgx,native_path],O/'native-readback.log',exe.parent);data=json.loads(native_path.read_text());assert len(model['meshes'])==len(data['meshes']);err=0
 for a,b in zip(model['meshes'],data['meshes']):
  assert a['name']==b['name'] and a['triangles']==b['triangles'] and b['boneBindings']==['Bone'] and len(a['vertices'])==len(b['vertices'])
  for v,w in zip(a['vertices'],b['vertices']):
   vals=w['position']+w['normal']+w['tangent']+w['binormal']+w['uv']+w['uv2']+w['uv3'];err=max(err,max(abs(x-y) for x,y in zip(v,vals)));assert err<1e-4
   assert w['boneWeights']==[255,0,0,0,0,0,0,0] and w['boneIndices']==[0]*8
 vis={m['name']:('Construction',) if m['name'].endswith('_Scaffold') else ('Construction','Pillaged') for m in model['meshes']};mats={m['name']:m.get('external',m['name']) for mesh in model['meshes'] for m in mesh['materials']};state=exp.model_instance(model,mats,vis)
 for g in state.findall('m_GroupStates/Element'):
  for v in g.findall('m_Values/m_Values/Element'):
   if exp.txt(v,'m_ParamName')=='BurnMaterial':v.find('m_ObjectName').set('text','DefaultBurnMaterial' if exp.txt(g,'m_StateName')=='Pillaged' else '')
 preservation=[]
 for ident in IDS:
  orig=read_xml(MOD/'Assets'/(ident+'.ast'));r=copy.deepcopy(orig);ms=r.find(exp.MODELS);refs=r.find('m_BehaviorData/m_referenceGeometryNames');oldnames={exp.txt(m,'m_Name') for m in ms if 'CON+PIL' in exp.txt(m,'m_Name')};assert oldnames=={'CSC_Level_2_CON+PIL'},oldnames
  for m in list(ms):
   if exp.txt(m,'m_Name') in oldnames:ms.remove(m)
  for m in list(refs):
   if m.get('text') in oldnames:refs.remove(m)
  ms.append(copy.deepcopy(state));E.SubElement(refs,'Element',{'text':ID})
  assert n.semantic(r.find('m_BehaviorData/m_behaviorDataSets'))==n.semantic(orig.find('m_BehaviorData/m_behaviorDataSets'))
  for m in orig.find(exp.MODELS):
   name=exp.txt(m,'m_Name')
   if name not in oldnames:assert n.semantic(m)==n.semantic(next(a for a in ms if exp.txt(a,'m_Name')==name))
  n.save(D/'Assets'/(ident+'.ast'),r);preservation.append({'asset':ident,'worked_models_attachments_and_decal_rows_preserved':True})
 resolver=n.Resolver(MOD,n.DEFAULT_SDK)
 for p in D.rglob('*'):
  if p.is_file():resolver.index[p.name.casefold()]={p}
 visited=set()
 def deps(p):
  p=p.resolve()
  if p in visited:return
  visited.add(p)
  if not p.is_relative_to(MOD) and not p.is_relative_to(D):return
  if p.suffix not in ('.ast','.geo','.mtl','.tex'):return
  r=read_xml(p);todo=[]
  for x in r.findall('.//m_GeoName'):todo.append(resolver.resolve(x.get('text'),'.geo',p))
  for row in r.findall('.//Element'):
   name=exp.txt(row,'m_ObjectName');kind=row.findtext('m_eObjectType','')
   if name and kind in ('MATERIAL','TEXTURE'):todo.append(resolver.resolve(name,'.mtl' if kind=='MATERIAL' else '.tex',p))
   if exp.txt(row,'m_ParamName')=='Asset' and exp.txt(row,'m_EntryName'):todo.append(resolver.resolve(exp.txt(row,'m_EntryName'),'.ast',p))
  for x in r.findall('.//m_DataFiles/Element/m_RelativePath'):
   q=p.parent/x.get('text')
   if not q.exists() and q.is_relative_to(D):q=MOD/q.relative_to(D)
   assert q.exists(),q;todo.append(q)
  for q in todo:
   if q.is_relative_to(MOD):
    target=D/q.relative_to(MOD)
    if not target.exists():target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(q,target)
   deps(q)
 for ident in IDS:deps(D/'Assets'/(ident+'.ast'))
 for p in D.rglob('*'):
  if p.is_file():resolver.index[p.name.casefold()]={p}
 checks=[]
 for ident in IDS:
  for st in ('Worked','Unworked','Construction','Pillaged','Unbuilt'):
   assembly=n.Assembly(resolver,st);key=assembly.asset(D/'Assets'/(ident+'.ast'));record=assembly.assets[key]
   active=[m for m in record['models'] if m['groups']]
   if st in ('Construction','Pillaged'):
    assert not any('Workshop' in str(m) for m in active)
    assert any(ID in str(m) for m in active)
   checks.append({'asset':ident,'state':st,'models':record['models']})
 changes=[str(p.relative_to(D)) for folder in ('Assets','Geometries','Materials','Textures') for p in (D/folder).iterdir() if p.is_file() and (not (MOD/p.relative_to(D)).exists() or sha(p)!=sha(MOD/p.relative_to(D)))]
 assert len(changes)==6,changes
 dump(O/'staging-validation.json',{'passed':True,'native_max_error':err,'native_vertices':{m['name']:len(m['vertices']) for m in data['meshes']},'AO_changed_bounds':bounds,'preservation':preservation,'publish_files':changes,'state_checks':checks})
 print('STAGED_NATIVE_AND_ALL_STATES_PASS',changes,flush=True)

def publish():
 checks=json.loads((O/'staging-validation.json').read_text());assert checks['passed'];cook=json.loads((O/'cook-check/result.json').read_text());assert cook['exit_code']==0 and cook['blps'];assert json.loads((O/'visual-review.json').read_text())['passed']
 baseline=json.loads((O/'baseline.json').read_text());assert all(sha(MOD/p)==h for p,h in baseline.items()),'Concurrent edit; restage required'
 authored=json.loads((O/'authoring.json').read_text());assert all(sha(v['path'])==v['sha256'] for v in authored['sources'].values())
 manifest=json.loads((CUR/'library.json').read_text());assert all(sha(CUR/'textures'/p)==h for p,h in manifest['maps'].items())
 release='2026-10-29_Modern_r015';snap=LIB/'Releases'/release;assert not snap.exists();payload={snap/p.relative_to(CUR):p.read_bytes() for p in CUR.rglob('*') if p.is_file()}
 previous=manifest['release'];manifest.update(release=release,previous_release=previous,status='Modern L2 main-only CON/PIL AO; all worked and painted maps preserved');manifest['maps']['CSC_Atlas_Modern_AO.png']=sha(O/'textures/CSC_Atlas_Modern_AO.png')
 plan=json.loads((CUR/'atlas-plan.json').read_text());plan['AO_allocations'][ID]=['building',RECT];plan['modern_level2']['state_master']='Level 2/modern/CON+PIL/revision-01/'+ID+'.blend';plan['modern_level2']['state_note']='Main building only; no extension. Scaffold Construction only; shell CON+PIL; independent AO.'
 updates={'textures/CSC_Atlas_Modern_AO.png':(O/'textures/CSC_Atlas_Modern_AO.png').read_bytes(),'library.json':json.dumps(manifest,indent=2).encode(),'atlas-plan.json':json.dumps(plan,indent=2).encode(),'sources/before-l2-state-AO.png':(CUR/'textures/CSC_Atlas_Modern_AO.png').read_bytes(),'bakes/'+ID+'.png':(O/'bakes'/(ID+'.png')).read_bytes(),'scripts/apply_l2_state_ao.py':b"from pathlib import Path\nfrom PIL import Image\np=Path(__file__).resolve().parents[1]\nim=Image.open(p/'sources/before-l2-state-AO.png').convert('RGB')\nim.paste(Image.open(p/'bakes/CSC_Level_2_Modern_CON+PIL.png').convert('RGB'),(1024,512))\nim.save(p/'textures/CSC_Atlas_Modern_AO.png')\n"}
 for rel,data in updates.items():payload[CUR/rel]=data;payload[snap/rel]=data
 payload[LIB/'CURRENT.json']=json.dumps({'release':release,'current':'Current','snapshot':'Releases/'+release,'manifest':'Current/library.json'},indent=2).encode()
 for rel in checks['publish_files']:payload[MOD/rel]=(D/rel).read_bytes()
 project=MOD/'Civ Supply Chains.civ6proj';new=[p for p in payload if p.is_relative_to(MOD) and not p.exists()]
 if new:
  insertion='\n  <ItemGroup>\n'+''.join('    <Content Include="'+str(p.relative_to(MOD))+'"><SubType>Content</SubType></Content>\n' for p in new)+'  </ItemGroup>\n';payload[project]=project.read_bytes().replace(b'</Project>',insertion.encode()+b'</Project>');E.fromstring(payload[project])
 backup=O/'publication-backup';backup.mkdir(exist_ok=True);rows=[]
 for i,(p,data) in enumerate(payload.items()):
  row={'destination':str(p),'before':sha(p) if p.exists() else None,'after':hashlib.sha256(data).hexdigest()}
  if p.exists():q=backup/f'{i:04}-{p.name}';shutil.copy2(p,q);row['backup']=str(q)
  rows.append(row)
 dump(backup/'manifest.json',rows)
 for row,(p,data) in zip(rows,payload.items()):
  assert (sha(p) if p.exists() else None)==row['before'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);assert sha(p)==row['after']
 changed={str(p.relative_to(MOD)) for p in payload if p.is_relative_to(MOD)};assert all(sha(MOD/p)==h for p,h in baseline.items() if p not in changed)
 dump(O/'publication-report.json',{'installed':True,'files':rows,'release':release,'no_extension':True,'game_deployment':False,'in_game_tested':False});n.cache(O);print('PUBLISHED',len(rows),flush=True)

if __name__=='__main__':globals()[sys.argv[1]]()
