"""Validate and selectively publish the refined kit without changing AE assemblies."""
import sys,json,shutil,subprocess,math
from pathlib import Path
from PIL import Image
from modular_v9 import ROOT,ART,BASE,SILO,TROLLEY,PALLET,texname,sha,dump
import modular_v9_native as native
exp=native.exp;MOD=native.MOD;WATER='CSC_BAKERS_Water_Mill_Modern';WIND='CSC_BAKERS_Wind_Mill_Modern'
O=Path.home()/'Desktop/Codex/modern-kit-refinement-20261027'
IDS=(BASE,WATER,SILO,TROLLEY,PALLET)
LIBS={'building':ART/'Textures/CSC_Buildings_Modern','props':ART/'Textures/CSC_Props_Modern'}
RELEASES={'building':'2026-10-27_Modern_r004','props':'2026-10-27_Modern_r003'}
DESTS={BASE:ART/'Level 1/modern/revision-04-painted-kit',WATER:ART/'BAKERS/Water Mill/modern/revision-02-painted-kit',SILO:ART/'BAKERS/Wind Mill/modern/revision-10-painted-kit',TROLLEY:ART/'BAKERS/Props/Modern/revision-02',PALLET:ART/'BAKERS/Props/Modern/revision-02'}
def pack():
 for kind,lib in LIBS.items():
  root=O/'libraries'/kind;plan=json.loads((root/'atlas-plan.json').read_text());ao=Image.open(root/'textures'/(texname(kind,'AO')+'.png')).convert('RGB')
  for ident,(k,rect) in plan['AO_allocations'].items():
   if k!=kind:continue
   source=O/'bakes'/((BASE if ident==BASE else WATER)+'.png')
   if ident!=BASE and not ident.startswith(WATER):continue
   shutil.copy2(source,root/'bakes'/(ident+'.png'));x0,y0,x1,y1=rect;p=Image.open(source).convert('RGB').resize((x1-x0-8,y1-y0-8),Image.Resampling.LANCZOS)
   ao.paste('white',rect);ao.paste(p,(x0+4,y0+4))
   for box,size,pos in [((0,0,1,p.height),(4,p.height),(x0,y0+4)),((p.width-1,0,p.width,p.height),(4,p.height),(x1-4,y0+4)),((0,0,p.width,1),(p.width,4),(x0+4,y0)),((0,p.height-1,p.width,p.height),(p.width,4),(x0+4,y1-4))]:ao.paste(p.crop(box).resize(size),pos)
  ao.save(root/'textures'/(texname(kind,'AO')+'.png'))
  for ch in ('B','N','G','M'):shutil.copy2(root/'textures'/(texname(kind,ch)+'.png'),root/'sources'/('registered_'+ch+'.png'))
  shutil.copy2(ROOT/'project/tools/art/modern_windmill/rebuild_modern_atlases.py',root/'scripts/rebuild_modern_atlases.py')
  for ident in IDS:
   folder=O/'masters'/ident/'textures'
   for p in (root/'textures').glob('*.png'):
    if (folder/p.name).exists():shutil.copy2(p,folder/p.name)
  info=json.loads((root/'library.json').read_text());info.update(release=RELEASES[kind],layout='Stage2 top-left quadrant' if kind=='building' else 'Compact 4x3 material families in 8x8 surface page; independent per-model AO',source=str(DESTS[BASE]/(BASE+'.blend')),status='Painted surface refinement, registered stronger normals; compact props UV migration',maps={p.name:sha(p) for p in (root/'textures').glob('*.png')});dump(root/'library.json',info)
 print('PACKED')
def stage():
 dst=O/'staged'
 for d in ('Assets','Geometries','Materials','Textures','CN6'):(dst/d).mkdir(parents=True,exist_ok=True)
 resolver=native.Resolver(MOD,native.DEFAULT_SDK)
 # Resolve every state and recursively copy exact current assembly dependencies.
 for ident in (*IDS,WIND):
  for state in ('Worked','Unworked','Construction','Pillaged','Unbuilt'):native.Assembly(resolver,state).asset(MOD/'Assets'/(ident+'.ast'))
 for p in resolver.inputs:
  p=Path(p)
  if p.is_relative_to(MOD):q=dst/p.relative_to(MOD);q.parent.mkdir(exist_ok=True,parents=True);shutil.copy2(p,q)
 # Hidden decal/state references are also cooker dependencies.
 from render_ae_asset import read_xml
 seen=set()
 def complete(p):
  if p in seen:return
  seen.add(p)
  if p.is_relative_to(MOD):q=dst/p.relative_to(MOD);q.parent.mkdir(exist_ok=True,parents=True);shutil.copy2(p,q)
  if p.suffix not in ('.ast','.geo','.mtl','.tex'):return
  r=read_xml(p);todo=[]
  for n in r.findall('.//m_GeoName'):todo.append(resolver.resolve(n.get('text'),'.geo',p))
  for n in r.findall('.//Element'):
   name=exp.txt(n,'m_ObjectName');kind=n.findtext('m_eObjectType','')
   if name and kind in ('MATERIAL','TEXTURE'):todo.append(resolver.resolve(name,'.mtl' if kind=='MATERIAL' else '.tex',p))
   if exp.txt(n,'m_ParamName')=='Asset' and exp.txt(n,'m_EntryName'):todo.append(resolver.resolve(exp.txt(n,'m_EntryName'),'.ast',p))
  for n in r.findall('.//m_DataFiles/Element/m_RelativePath'):todo.append(p.parent/n.get('text'))
  for q in todo:complete(q)
 for ident in (*IDS,WIND):complete(MOD/'Assets'/(ident+'.ast'))
 exe,_=native.helper(O/'native-reader');conv=ROOT/'project/tools/cn6libs/CN6ToFGX.exe';checks=[];changed=[]
 for ident in IDS:
  m=json.loads((O/'models'/(ident+'.json')).read_text())
  for mesh in m['meshes']:
   for mat in mesh['materials']:
    for im in mat['images'].values():im['sha256']=sha(im['path'])
  dump(O/'models'/(ident+'.json'),m)
  existing=native.read(MOD/'Geometries'/(ident+'.geo'));assert {x['name'] for x in m['meshes']}=={n.get('text') for n in existing.findall('m_Meshes/Element/m_Name')},ident
  cn6=dst/'CN6'/(ident+'.cn6');fgx=dst/'Geometries'/(ident+'.fgx');exp.write_cn6(cn6,m);native.save(dst/'Geometries'/(ident+'.geo'),exp.geometry(m,existing))
  p=subprocess.run([str(conv),str(cn6),str(fgx),'2'],cwd=conv.parent,capture_output=True,text=True);assert p.returncode==0,p.stdout+p.stderr
  np=O/(ident+'-native.json');subprocess.run([str(exe),str(exe.parent),str(fgx),str(np)],cwd=exe.parent,check=True,capture_output=True);decoded=json.loads(np.read_text());err=0
  assert len(decoded['meshes'])==len(m['meshes'])
  for a,b in zip(m['meshes'],decoded['meshes']):
   assert a['name']==b['name'] and a['triangles']==b['triangles'] and b['boneBindings']==['Bone'] and len(a['vertices'])==len(b['vertices'])
   for v,w in zip(a['vertices'],b['vertices']):
    values=w['position']+w['normal']+w['tangent']+w['binormal']+w['uv']+w['uv2']+w['uv3'];err=max(err,max(abs(x-y) for x,y in zip(v,values)));assert err<1e-4
    assert w['boneWeights']==[255,0,0,0,0,0,0,0] and w['boneIndices']==[0]*8
  checks.append({'asset':ident,'vertices':sum(len(x['vertices']) for x in m['meshes']),'triangles':sum(len(x['triangles']) for x in m['meshes']),'native_max_error':err})
  changed.extend('Geometries/'+ident+'.'+ext for ext in ('fgx','geo'))
 for kind in LIBS:
  for ch in ('B','N','G','M','AO'):
   p=O/'libraries'/kind/'textures'/(texname(kind,ch)+'.png');source=p;size=list(Image.open(p).size);fmt='R8_UNORM' if ch in ('G','M','AO') else 'R8G8B8A8_UNORM'
   if ch in ('G','M','AO'):
    source=O/'scalar'/p.name;source.parent.mkdir(exist_ok=True);Image.open(p).getchannel('R').save(source)
   cmd=[str(ROOT/'project/tools/directxtex/texconv.exe'),'-nologo','-y','-m','0','-f',fmt,'--ignore-srgb','-o',str(dst/'Textures')]
   if ch=='B':cmd+=['-srgb']
   r=subprocess.run(cmd+[str(source)],capture_output=True,text=True);assert r.returncode==0,r.stdout+r.stderr
   spec={'slot':ch,'size':size,'format':fmt};dds=dst/'Textures'/(p.stem+'.dds')
   if ch in ('G','M','AO'):exp.normalize_ao_dds(dds,spec,MOD/'Textures/CSC_Props_Shared_01_AO.dds')
   exp.validate_dds(dds,spec)
   tex=native.read(MOD/'Textures'/(p.stem+'.tex'));native.text(tex,'m_SourceFilePath',str(LIBS[kind]/'Current/textures'/p.name));native.save(dst/'Textures'/(p.stem+'.tex'),tex)
   changed.extend('Textures/'+p.stem+'.'+ext for ext in ('dds','tex'))
 for p in dst.rglob('*'):
  if p.is_file():resolver.index[p.name.casefold()]={p}
 for ident in (*IDS,WIND):
  for state in ('Worked','Unworked','Construction','Pillaged','Unbuilt'):native.Assembly(resolver,state).asset(dst/'Assets'/(ident+'.ast'))
  assert sha(MOD/'Assets'/(ident+'.ast'))==sha(dst/'Assets'/(ident+'.ast'))
 changed=[r for r in changed if sha(dst/r)!=sha(MOD/r)]
 dump(O/'staging-validation.json',{'passed':True,'native':checks,'publish_files':changed,'all_assemblies_byte_unchanged':True});print('STAGED',checks)
def publish():
 check=json.loads((O/'staging-validation.json').read_text());assert check['passed'];cook=json.loads((O/'cook-check/result.json').read_text());assert cook['exit_code']==0 and cook['blps']
 baseline=json.loads((O/'baseline.json').read_text());assert all(sha(Path(p))==h for p,h in baseline['sources'].items()),'User source changed'
 assert all(sha(MOD/p)==h for p,h in baseline['runtime'].items()),'Runtime changed'
 for kind,files in baseline['libraries'].items():assert all(sha(LIBS[kind]/'Current'/p)==h for p,h in files.items()),'Library changed'
 payload={}
 for ident,dest in DESTS.items():
  assert json.loads((O/'masters'/ident/'validation.json').read_text())['automated_pass'];assert not dest.exists()
  for p in (O/'masters'/ident).rglob('*'):
   if p.is_file() and p.suffix!='.blend1':payload[dest/(ident+'.validation.json') if p.name=='validation.json' and ident in (TROLLEY,PALLET) else dest/p.relative_to(O/'masters'/ident)]=p
  payload[dest/(ident+'.cn6')]=O/'staged/CN6'/(ident+'.cn6')
 for kind,lib in LIBS.items():
  assert not (lib/'Releases'/RELEASES[kind]).exists()
  for p in (O/'libraries'/kind).rglob('*'):
   if p.is_file():
    for dest in (lib/'Current',lib/'Releases'/RELEASES[kind]):payload[dest/p.relative_to(O/'libraries'/kind)]=p
  pointer=O/(kind+'-CURRENT.json');dump(pointer,{'release':RELEASES[kind],'current':'Current','snapshot':'Releases/'+RELEASES[kind],'manifest':'Current/library.json'});payload[lib/'CURRENT.json']=pointer
 for rel in check['publish_files']:payload[MOD/rel]=O/'staged'/rel
 backup=O/'publication-backup';backup.mkdir(exist_ok=True);rows=[]
 for i,(dest,p) in enumerate(payload.items()):
  row={'destination':str(dest),'before':sha(dest) if dest.exists() else None}
  if dest.exists():q=backup/f'{i:04}-{dest.name}';shutil.copy2(dest,q);row['backup']=str(q)
  rows.append(row)
 dump(backup/'manifest.json',rows)
 for row,(dest,p) in zip(rows,payload.items()):
  assert (sha(dest) if dest.exists() else None)==row['before'];dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest);assert sha(dest)==sha(p);row['after']=sha(dest)
 protected=[p for p in baseline['runtime'] if Path(p).as_posix() not in check['publish_files']];assert all(sha(MOD/p)==baseline['runtime'][p] for p in protected)
 dump(O/'publication-report.json',{'installed':True,'files':rows,'masters':{i:str(p/(i+'.blend')) for i,p in DESTS.items()},'cache_inputs':[str(MOD/'Assets'/(i+'.ast')) for i in (*IDS,WIND)],'in_game_tested':False});native.cache(O);print('PUBLISHED',len(rows))
def finish():
 # Resume only final verification after publication's Windows separator assertion.
 baseline=json.loads((O/'baseline.json').read_text());check=json.loads((O/'staging-validation.json').read_text())
 for p,h in baseline['runtime'].items():
  if Path(p).as_posix() in check['publish_files']:assert sha(MOD/p)==sha(O/'staged'/p)
  else:assert sha(MOD/p)==h,p
 for ident,dest in DESTS.items():
  for p in (O/'masters'/ident).rglob('*'):
   if p.is_file() and p.suffix!='.blend1':
    target=dest/p.relative_to(O/'masters'/ident)
    if p.name=='validation.json' and ident in (TROLLEY,PALLET):
     target=dest/(ident+'.validation.json');shutil.copy2(p,target)
    assert sha(p)==sha(target),p
 for kind,lib in LIBS.items():
  for p in (O/'libraries'/kind).rglob('*'):
   if p.is_file():
    for dest in (lib/'Current',lib/'Releases'/RELEASES[kind]):assert sha(p)==sha(dest/p.relative_to(O/'libraries'/kind)),p
 rows=json.loads((O/'publication-backup/manifest.json').read_text())
 for row in rows:row['after']=sha(row['destination'])
 dump(O/'publication-report.json',{'installed':True,'files':rows,'masters':{i:str(p/(i+'.blend')) for i,p in DESTS.items()},'cache_inputs':[str(MOD/'Assets'/(i+'.ast')) for i in (*IDS,WIND)],'in_game_tested':False,'publication_recovery':'Final protected-file check normalized Windows separators; all target/source hashes independently verified'})
 native.cache(O);print('VERIFIED_PUBLISHED',len(rows))
if __name__=='__main__':globals()[sys.argv[1]]()
