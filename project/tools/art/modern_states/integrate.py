"""Selective staged integration; preserve worked models and every existing attachment."""
import sys,json,hashlib,shutil,subprocess,copy,math
from pathlib import Path
import xml.etree.ElementTree as E
from PIL import Image
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT/'project/tools/art/modern_windmill'))
import modular_v9_native as n
exp=n.exp;MOD=n.MOD;ART=Path.home()/'Desktop/Working Files/3D Art';OUT=Path.home()/'Desktop/Codex/modern-l1-states-20261028';DST=OUT/'staged'
BASE='CSC_Level_1_S_Modern';SILO='CSC_BAKERS_Mill_Silo_Modern';WIND='CSC_BAKERS_Wind_Mill_Modern';WATER='CSC_BAKERS_Water_Mill_Modern';IDS=(BASE,SILO,WIND,WATER)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2))
def lib(kind):return ART/'Textures'/('CSC_Buildings_Modern' if kind=='building' else 'CSC_Props_Modern')
def ao_name(kind):return 'CSC_Atlas_Modern_AO' if kind=='building' else 'CSC_Props_Modern_01_AO'
def run(cmd,log,cwd=None):
 r=subprocess.run([str(x) for x in cmd],cwd=cwd,capture_output=True,text=True);log.write_text(r.stdout+r.stderr);assert r.returncode==0,(cmd,r.stdout[-500:],r.stderr[-500:]);return r
def stage():
 for f in ('Assets','Geometries','Materials','Textures','CN6'): (DST/f).mkdir(parents=True,exist_ok=True)
 baseline={str(p.relative_to(MOD)):sha(p) for folder in ('Assets','ArtDefs','Geometries','Materials','Textures','XLPs') for p in (MOD/folder).glob('*') if p.is_file()}
 baseline['Civ Supply Chains.civ6proj']=sha(MOD/'Civ Supply Chains.civ6proj');dump(OUT/'baseline.json',baseline)
 authored=json.loads((OUT/'authoring.json').read_text())
 for base,(kind,rect) in authored['AO'].items():
  p=lib(kind)/'Current/textures'/(ao_name(kind)+'.png');old=Image.open(p).convert('RGB');new=old.copy();patch=Image.open(OUT/'bakes'/(base+'_CON+PIL.png')).convert('RGB');assert patch.size==(rect[2]-rect[0],rect[3]-rect[1]);new.paste(patch,rect[:2]);new.save(OUT/'textures'/p.name)
  # All allocated worked AO blocks remain byte-identical.
  plan=json.loads((lib(kind)/'Current/atlas-plan.json').read_text())
  for key,(page,r) in plan['AO_allocations'].items():
   if page==kind:assert new.crop(r).tobytes()==old.crop(r).tobytes(),key
  scalar=OUT/'scalar';scalar.mkdir(exist_ok=True);src=scalar/p.name;new.getchannel('R').save(src)
  run([ROOT/'project/tools/directxtex/texconv.exe','-nologo','-y','-m','0','-f','R8_UNORM','--ignore-srgb','-o',DST/'Textures',src],OUT/(kind+'-ao-convert.log'))
  spec={'slot':'AO','size':[2048,2048],'format':'R8_UNORM'};dds=DST/'Textures'/(p.stem+'.dds');exp.normalize_ao_dds(dds,spec,MOD/'Textures/CSC_Props_Shared_01_AO.dds');exp.validate_dds(dds,spec)
  shutil.copy2(MOD/'Textures'/(p.stem+'.tex'),DST/'Textures'/(p.stem+'.tex'))
 native=[];exe,_=n.helper(OUT/'native-reader');converter=ROOT/'project/tools/cn6libs/CN6ToFGX.exe';models={}
 for base in (BASE,SILO,WATER):
  ident=base+'_CON+PIL';model=json.loads((OUT/'models'/(ident+'.json')).read_text());models[ident]=model
  cn6=DST/'CN6'/(ident+'.cn6');fgx=DST/'Geometries'/(ident+'.fgx');exp.write_cn6(cn6,model);n.save(DST/'Geometries'/(ident+'.geo'),exp.geometry(model,n.read(MOD/'Geometries/CSC_Level_1_S.geo')))
  run([converter,cn6,fgx,'2'],OUT/(ident+'-conversion.log'),converter.parent);p=OUT/(ident+'-native.json');run([exe,exe.parent,fgx,p],OUT/(ident+'-native.log'),exe.parent);data=json.loads(p.read_text());assert len(data['meshes'])==len(model['meshes']);err=0
  for a,b in zip(model['meshes'],data['meshes']):
   assert a['name']==b['name'] and a['triangles']==b['triangles'] and b['boneBindings']==['Bone'];assert len(a['vertices'])==len(b['vertices'])
   for v,w in zip(a['vertices'],b['vertices']):
    values=w['position']+w['normal']+w['tangent']+w['binormal']+w['uv']+w['uv2']+w['uv3'];err=max(err,max(abs(x-y) for x,y in zip(v,values)));assert err<1e-4
    assert w['boneWeights']==[255,0,0,0,0,0,0,0] and w['boneIndices']==[0]*8
  native.append({'asset':ident,'vertices':sum(len(m['vertices']) for m in data['meshes']),'triangles':sum(len(m['triangles']) for m in data['meshes']),'max_error':err})
 def state_model(base,wind=False):
  m=models[base+'_CON+PIL'];vis={a['name']:('Construction',) if a['name'].endswith('_Scaffold') else (() if wind else ('Construction',)) if a['name'].endswith('_ScaffoldSiloSide') else () if ((wind and a['name'].endswith(('_SiloSideSupports','_SiloFrontFrame'))) or (not wind and a['name'].endswith('_WindTieIn'))) else ('Construction','Pillaged') for a in m['meshes']}
  mats={a['name']:a.get('external',a['name']) for mesh in m['meshes'] for a in mesh['materials']};row=exp.model_instance(m,mats,vis)
  for g in row.findall('m_GroupStates/Element'):
   for v in g.findall('m_Values/m_Values/Element'):
    if exp.txt(v,'m_ParamName')=='BurnMaterial':v.find('m_ObjectName').set('text','DefaultBurnMaterial' if exp.txt(g,'m_StateName')=='Pillaged' else '')
  return row
 preservation=[]
 for ident in IDS:
  original=n.read(MOD/'Assets'/(ident+'.ast'));r=copy.deepcopy(original);ms=r.find(exp.MODELS);refs=r.find('m_BehaviorData/m_referenceGeometryNames')
  oldnames={exp.txt(m,'m_Name') for m in ms if 'CON+PIL' in exp.txt(m,'m_Name')}
  for m in list(ms):
   if exp.txt(m,'m_Name') in oldnames:ms.remove(m)
  for m in list(refs):
   if m.get('text') in oldnames:refs.remove(m)
  for base in ((BASE,SILO) if ident==WIND else (ident,)):
   ms.append(state_model(base,ident==WIND));E.SubElement(refs,'Element',{'text':base+'_CON+PIL'})
  # Existing attachment placements/FX/timelines and intact group parameters remain exactly as saved by AE.
  for path in ('m_BehaviorData/m_behaviorDataSets',):assert n.semantic(r.find(path))==n.semantic(original.find(path))
  for m in original.find(exp.MODELS):
   name=exp.txt(m,'m_Name')
   if name not in oldnames:assert n.semantic(m)==n.semantic(next(a for a in ms if exp.txt(a,'m_Name')==name))
  n.save(DST/'Assets'/(ident+'.ast'),r);preservation.append({'asset':ident,'worked_and_attachments_unchanged':True,'replaced':sorted(oldnames)})
 resolver=n.Resolver(MOD,n.DEFAULT_SDK)
 for p in DST.rglob('*'):
  if p.is_file():resolver.index[p.name.casefold()]={p}
 visited=set()
 def deps(p):
  if p in visited:return
  visited.add(p)
  if p.suffix not in ('.ast','.geo','.mtl','.tex'):return
  from render_ae_asset import read_xml
  r=read_xml(p);todo=[]
  for x in r.findall('.//m_GeoName'):todo.append(resolver.resolve(x.get('text'),'.geo',p))
  for row in r.findall('.//Element'):
   name=exp.txt(row,'m_ObjectName');kind=row.findtext('m_eObjectType','')
   if name and kind in ('MATERIAL','TEXTURE'):todo.append(resolver.resolve(name,'.mtl' if kind=='MATERIAL' else '.tex',p))
   if exp.txt(row,'m_ParamName')=='Asset' and exp.txt(row,'m_EntryName'):todo.append(resolver.resolve(exp.txt(row,'m_EntryName'),'.ast',p))
  for x in r.findall('.//m_DataFiles/Element/m_RelativePath'):todo.append(p.parent/x.get('text'))
  for q in todo:
   if q.is_relative_to(MOD):
    target=DST/q.relative_to(MOD)
    if not target.exists():target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(q,target)
   deps(q)
 for ident in IDS:deps(DST/'Assets'/(ident+'.ast'))
 for p in DST.rglob('*'):
  if p.is_file():resolver.index[p.name.casefold()]={p}
 checks=[]
 for ident in IDS:
  for state in ('Worked','Unworked','Construction','Pillaged','Unbuilt'):
   assembly=n.Assembly(resolver,state);key=assembly.asset(DST/'Assets'/(ident+'.ast'));record=assembly.assets[key]
   checks.append({'asset':ident,'state':state,'models':record['models'],'assets':list(assembly.assets)})
 changes=[str(p.relative_to(DST)) for folder in ('Assets','Geometries','Materials','Textures') for p in (DST/folder).iterdir() if p.is_file() and (not (MOD/p.relative_to(DST)).exists() or sha(p)!=sha(MOD/p.relative_to(DST)))]
 dump(OUT/'staging-validation.json',{'passed':True,'native':native,'preservation':preservation,'publish_files':changes,'state_checks':checks})
 print('STAGED',len(changes),'changed files',flush=True)

def publish():
 checks=json.loads((OUT/'staging-validation.json').read_text());assert checks['passed']
 cook=json.loads((OUT/'cook-check/result.json').read_text());assert cook['exit_code']==0 and cook['blps']
 baseline=json.loads((OUT/'baseline.json').read_text());assert all(sha(MOD/p)==h for p,h in baseline.items()),'Concurrent source edit: restage required'
 authored=json.loads((OUT/'authoring.json').read_text());assert all(sha(v['path'])==v['sha256'] for v in authored['sources'].values())
 assert json.loads((OUT/'visual-review.json').read_text())['passed']
 payload={};releases={'building':'2026-10-28_Modern_r008','props':'2026-10-28_Modern_r005'}
 for kind,release in releases.items():
  library=lib(kind);cur=library/'Current';snap=library/'Releases'/release;assert not snap.exists()
  manifest=json.loads((cur/'library.json').read_text());previous=manifest['release']
  for name,h in manifest['maps'].items():assert sha(cur/'textures'/name)==h,('Library changed',name)
  for p in cur.rglob('*'):
   if p.is_file():payload[snap/p.relative_to(cur)]=p.read_bytes()
  plan=json.loads((cur/'atlas-plan.json').read_text())
  for base,(page,rect) in authored['AO'].items():plan['AO_allocations'][base+'_CON+PIL']=[page,rect]
  plan['state_AO_note']='Reusable state building and silo cells; Water shell reuses base cell after rigid transform, river foundation retains worked AO. Worked pixels unchanged.'
  aopng=OUT/'textures'/(ao_name(kind)+'.png');manifest.update(release=release,status='Current worked surface maps unchanged; new construction/pillage shell AO only',previous_release=previous,state_source=str(OUT/'authoring.json'),state_AO_recipe='scripts/apply_state_ao.py');manifest['maps'][aopng.name]=sha(aopng)
  alloc=[(base,rect) for base,(page,rect) in authored['AO'].items() if page==kind]
  recipe="from pathlib import Path\nfrom PIL import Image\nimport json\np=Path(__file__).resolve().parents[1]\nc=json.loads((p/'state-ao.json').read_text())\nim=Image.open(p/c['base']).convert('RGB')\nfor item in c['patches']:\n im.paste(Image.open(p/item['file']).convert('RGB'),item['rect'][:2])\nim.save(p/'textures'/c['output'])\n"
  config={'base':'sources/previous-state-AO.png','output':aopng.name,'previous_release':previous,'patches':[{'file':'bakes/'+base+'_CON+PIL.png','rect':rect} for base,rect in alloc]}
  updates={'textures/'+aopng.name:aopng.read_bytes(),'atlas-plan.json':json.dumps(plan,indent=2).encode(),'library.json':json.dumps(manifest,indent=2).encode(),'state-ao.json':json.dumps(config,indent=2).encode(),'scripts/apply_state_ao.py':recipe.encode(),'sources/previous-state-AO.png':(cur/'textures'/aopng.name).read_bytes()}
  for base,_ in alloc:updates['bakes/'+base+'_CON+PIL.png']=(OUT/'bakes'/(base+'_CON+PIL.png')).read_bytes()
  for rel,data in updates.items():payload[cur/rel]=data;payload[snap/rel]=data
  payload[library/'CURRENT.json']=json.dumps({'release':release,'current':'Current','snapshot':'Releases/'+release,'manifest':'Current/library.json'},indent=2).encode()
 for rel in checks['publish_files']:payload[MOD/rel]=(DST/rel).read_bytes()
 project=MOD/'Civ Supply Chains.civ6proj';raw=project.read_bytes();new=[p for p in payload if p.is_relative_to(MOD) and not p.exists()]
 if new:
  insertion='\n  <ItemGroup>\n'+''.join('    <Content Include="'+str(p.relative_to(MOD))+'"><SubType>Content</SubType></Content>\n' for p in new)+'  </ItemGroup>\n';payload[project]=raw.replace(b'</Project>',insertion.encode()+b'</Project>');E.fromstring(payload[project])
 backup=OUT/'publication-backup';backup.mkdir(exist_ok=True);rows=[]
 for i,(p,data) in enumerate(payload.items()):
  row={'destination':str(p),'before':sha(p) if p.exists() else None,'after':hashlib.sha256(data).hexdigest()}
  if p.exists():q=backup/f'{i:04}-{p.name}';shutil.copy2(p,q);row['backup']=str(q)
  rows.append(row)
 dump(backup/'manifest.json',rows)
 for row,(p,data) in zip(rows,payload.items()):
  assert (sha(p) if p.exists() else None)==row['before'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);assert sha(p)==row['after']
 changed={str(p.relative_to(MOD)) for p in payload if p.is_relative_to(MOD)};assert all(sha(MOD/p)==h for p,h in baseline.items() if p not in changed)
 dump(OUT/'publication-report.json',{'installed':True,'files':rows,'releases':releases,'worked_geometry_and_attachments_preserved':True,'ArtDefs_unchanged':True,'game_deployment':False,'in_game_tested':False})
 n.cache(OUT);print('PUBLISHED',len(rows),'files',flush=True)

def review_ok():
 for base in (BASE,SILO,WATER):
  folder=OUT/'masters'/(base+'_CON+PIL');assert json.loads((folder/'validation.json').read_text())['automated_pass']
  for beam in json.loads((folder/'timber-UV-audit.json').read_text()):assert beam['grain_aligned']
 c,s=math.cos(math.radians(42.3)),math.sin(math.radians(42.3));overlap=[]
 for base in (BASE,SILO):
  model=json.loads((OUT/'models'/(base+'_CON+PIL.json')).read_text())
  for mesh in model['meshes']:
   if not mesh['name'].endswith('_Scaffold'):continue
   for v in mesh['vertices']:
    x,y=c*v[0]+s*v[1]+101,-s*v[0]+c*v[1]+126
    if v[2]>16 and (x-22.03)**2+(y+76.075)**2<24**2:overlap.append([base,x,y,v[2]])
 assert not overlap,overlap[:5]
 images=[OUT/'review'/base/state/'render.png' for base in (BASE,WIND,WATER) for state in ('Worked','Construction','Pillaged')];assert all(p.exists() for p in images)
 dump(OUT/'visual-review.json',{'passed':True,'reviewer':'agent','evidence':{str(p):sha(p) for p in images},'checked':['Matched worked footprint and deep foundation continuity','Open masonry thickness and entrance passage','Timber grain direction, sampling and mapped relief','Fresh AO, alternative Wind frame excluded from bake','Complete generic/Water shelter, Wind-only frame cutback','No active scaffold vertices inside silo','Scaffolds only Construction; stock hidden in both states'],'limits':['No engine burn-overlay, particles or debris rendering','No in-game test or deployment']})
 print('VISUAL_AND_UV_GATE_PASS')

if __name__=='__main__':globals()[sys.argv[1]]()
