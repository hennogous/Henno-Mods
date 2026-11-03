"""Scoped interior-lighting integration; preserve AE assemblies and user textures."""
import sys,json,shutil,subprocess,hashlib,math,os
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'project/tools/art/modern_windmill'))
import modular_v9_native as n
sys.path.insert(0,str(ROOT/'project/tools/blender'))
from render_ae_asset import read_xml
O=Path.home()/'Desktop/Codex/modern-interior-lighting-20261028';MOD=n.MOD;D=O/'staged'
ART=Path.home()/'Desktop/Working Files/3D Art';LIB=ART/'Textures/CSC_Buildings_Emissive';BLIB=ART/'Textures/CSC_Buildings_Modern'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2))
def stage():
 for f in ('Assets','Materials','Textures','Geometries'):(D/f).mkdir(parents=True,exist_ok=True)
 exe,_=n.helper(O/'native-reader');old=O/'native/previous-main.json'
 subprocess.run([str(exe),str(exe.parent),str(MOD/'Geometries/CSC_Level_2_Modern.fgx'),str(old)],cwd=exe.parent,check=True,capture_output=True)
 before=json.loads(old.read_text());after=json.loads((O/'native/CSC_Level_2_Modern.json').read_text());uvchanges=0
 assert len(before['meshes'])==len(after['meshes'])
 for a,b in zip(before['meshes'],after['meshes']):
  assert a['triangles']==b['triangles'] and a['boneBindings']==b['boneBindings'] and len(a['vertices'])==len(b['vertices'])
  for v,w in zip(a['vertices'],b['vertices']):
   uvchanges+=v['uv3']!=w['uv3']
   for k in v:
    if k=='uv3':continue
    assert len(v[k])==len(w[k]) and max([abs(x-y) for x,y in zip(v[k],w[k])]+[0])<1e-5,(k,v[k],w[k])
 assert uvchanges>0
 changed=['Geometries/CSC_Level_2_Modern.fgx'];shutil.copy2(O/'native/CSC_Level_2_Modern.fgx',D/changed[0])
 for ident in ('CSC_Atlas_Modern_B_BAKERS','CSC_Atlas_Modern_E_BAKERS','CSC_Atlas_E_BAKERS'):
  png=O/'textures'/(ident+'.png');size=Image.open(png).size;historical=ident=='CSC_Atlas_E_BAKERS';channel='B' if ident=='CSC_Atlas_Modern_B_BAKERS' else 'E'
  if historical:shutil.copy2(O/'sources/Effective_Historical_E.dds',D/'Textures'/(ident+'.dds'))
  else:
   cmd=[ROOT/'project/tools/directxtex/texconv.exe','-nologo','-y','-m','0','-f','R8G8B8A8_UNORM','--ignore-srgb','-srgb','-o',D/'Textures',png]
   r=subprocess.run(list(map(str,cmd)),capture_output=True,text=True);(O/(ident+'-convert.log')).write_text(r.stdout+r.stderr);assert r.returncode==0
  if not historical:n.exp.validate_dds(D/'Textures'/(ident+'.dds'),{'slot':channel,'size':list(size),'format':'R8G8B8A8_UNORM'})
  changed.append('Textures/'+ident+'.dds')
  if channel=='E':
   template='CSC_Atlas_E' if historical else 'CSC_Atlas_Modern_E';r=n.read(MOD/'Textures'/(template+'.tex'))
   n.text(r,'m_Name',ident);n.text(r,'m_SourceFilePath',str(LIB/'Current/textures'/png.name));n.text(r,'m_DataFiles/Element/m_RelativePath',ident+'.dds')
   for k,v in [('m_Width',size[0]),('m_Height',size[1]),('m_NumMipMaps',int(math.log2(size[0])))]:r.find(k).text=str(v)
   n.save(D/'Textures'/(ident+'.tex'),r);changed.append('Textures/'+ident+'.tex')
 for ident in ('CSC_BAKERS_E','CSC_BAKERS_E_2','CSC_BAKERS_Modern','CSC_BAKERS_Modern_2'):
  r=n.read(MOD/'Materials'/(ident+'.mtl'));new='CSC_Atlas_Modern_E_BAKERS' if 'Modern' in ident else 'CSC_Atlas_E_BAKERS'
  rows=[x for x in r.findall('m_CookParams/m_Values/Element') if n.exp.txt(x,'m_ParamName')=='Emissive'];assert len(rows)==1
  rows[0].find('m_ObjectName').set('text',new);n.save(D/'Materials'/(ident+'.mtl'),r);changed.append('Materials/'+ident+'.mtl')
 for ident in ('CSC_BAKERS_Bakery_Modern','CSC_BAKERS_Bakery_Modern_2','CSC_BAKERS_Wind_Mill_Modern','CSC_BAKERS_Water_Mill_Modern','CSC_BAKERS_Bakery'):
  shutil.copy2(MOD/'Assets'/(ident+'.ast'),D/'Assets'/(ident+'.ast'))
 resolver=n.Resolver(MOD,n.DEFAULT_SDK)
 for p in D.rglob('*'):
  if p.is_file():resolver.index[p.name.casefold()]={p}
 visited=set()
 def deps(p):
  if p in visited:return
  visited.add(p)
  if p.is_relative_to(n.DEFAULT_SDK):return
  if p.suffix not in ('.ast','.geo','.mtl','.tex'):return
  r=read_xml(p);todo=[]
  for x in r.findall('.//m_GeoName'):todo.append(resolver.resolve(x.get('text'),'.geo',p))
  for x in r.findall('.//Element'):
   name=n.exp.txt(x,'m_ObjectName');kind=x.findtext('m_eObjectType','')
   if name and kind in ('MATERIAL','TEXTURE'):todo.append(resolver.resolve(name,'.mtl' if kind=='MATERIAL' else '.tex',p))
   if n.exp.txt(x,'m_ParamName')=='Asset' and n.exp.txt(x,'m_EntryName'):todo.append(resolver.resolve(n.exp.txt(x,'m_EntryName'),'.ast',p))
  for x in r.findall('.//m_DataFiles/Element/m_RelativePath'):
   q=p.parent/x.get('text')
   if not q.exists() and q.is_relative_to(D):q=MOD/q.relative_to(D)
   assert q.exists(),q
   todo.append(q)
  for q in todo:
   if q.is_relative_to(MOD):
    target=D/q.relative_to(MOD)
    if not target.exists():target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(q,target)
   deps(q)
 for p in list((D/'Assets').glob('*.ast')):deps(p)
 dump(O/'staging-validation.json',{'passed':True,'publish_files':changed,'native_UV3_changed_vertices':uvchanges,'native_other_vertex_fields_topology_unchanged':True,'historical_DDS_exact':sha(D/'Textures/CSC_Atlas_E_BAKERS.dds')==sha(MOD/'Textures/CSC_Atlas_E.dds')})
 print('STAGED',len(changed),'files; UV3 changed vertices',uvchanges,flush=True)

def publish():
 checks=json.loads((O/'staging-validation.json').read_text());assert checks['passed']
 cook=json.loads((O/'cook-check/result.json').read_text());log=(O/'cook-check/stdout.log').read_text(errors='replace').replace('\x00','')
 assert cook['exit_code']==0 and cook['blps'] and 'ERRORS!!' not in log and 'I/O error' not in log
 base=json.loads((O/'baseline.json').read_text());inputs=json.loads((O/'inputs.json').read_text());authoring=json.loads((O/'authoring.json').read_text())
 for item in inputs['sources'].values():assert sha(item['path'])==item['sha256'],('Concurrent source edit',item['path'])
 for row in authoring:assert sha(row['source'])==row['source_sha256'],('Concurrent geometry edit',row['source'])
 for rel in checks['publish_files']:assert (sha(MOD/rel) if (MOD/rel).exists() else None)==base.get(rel),('Concurrent runtime edit',rel)
 cur=BLIB/'Current';release='2026-10-28_Modern_r013';snap=BLIB/'Releases'/release;assert not snap.exists() and not (LIB/'Current').exists()
 payload={};manifest=json.loads((cur/'library.json').read_text());manifest.update(previous_release=manifest['release'],release=release,status='Lighter ImageGen-painted Bakery room cells only; exterior pixels preserved; quarter-specific emissive library',emissive_library='../CSC_Buildings_Emissive')
 bp=O/'textures/CSC_Atlas_Modern_B_BAKERS.png';manifest['maps'][bp.name]=sha(bp)
 # Build a new immutable snapshot from current bytes plus the three-cell edit.
 for p in cur.rglob('*'):
  if p.is_file():payload[snap/p.relative_to(cur)]=p.read_bytes()
 updates={'library.json':json.dumps(manifest,indent=2).encode(),'textures/'+bp.name:bp.read_bytes(),'sources/published-registered/'+bp.name:bp.read_bytes()}
 for p in (O/'sources').glob('Interior*'):updates['sources/interior-lighting/'+p.name]=p.read_bytes()
 updates['sources/interior-lighting/generation-provenance.json']=(O/'sources/generation-provenance.json').read_bytes()
 for rel,data in updates.items():payload[cur/rel]=data;payload[snap/rel]=data
 payload[BLIB/'CURRENT.json']=json.dumps({'release':release,'current':'Current','snapshot':'Releases/'+release,'manifest':'Current/library.json'},indent=2).encode()
 erel='2026-10-28_Emissive_r001';ecur=LIB/'Current';esnap=LIB/'Releases'/erel;plan=json.loads((O/'emissive-plan.json').read_text())
 emanifest={'library':'CSC_Buildings_Emissive','release':erel,'maps':{},'allocation_manifest':'atlas-plan.json','rebuild_tool':'scripts/rebuild_published.py','policy':'One historical and one modern E atlas per Quarter; fixed reusable UV3; no Service variants'}
 for ident in ('CSC_Atlas_E_BAKERS','CSC_Atlas_Modern_E_BAKERS'):
  p=O/'textures'/(ident+'.png');emanifest['maps'][p.name]=sha(p)
  for folder in (ecur,esnap):
   payload[folder/'textures'/p.name]=p.read_bytes();payload[folder/'sources/published-registered'/p.name]=p.read_bytes()
 for folder in (ecur,esnap):
  payload[folder/'atlas-plan.json']=json.dumps(plan,indent=2).encode();payload[folder/'library.json']=json.dumps(emanifest,indent=2).encode()
  payload[folder/'scripts/rebuild_published.py']=b"from pathlib import Path\nimport shutil\np=Path(__file__).resolve().parents[1]\nfor f in (p/'sources/published-registered').glob('*.png'):shutil.copy2(f,p/'textures'/f.name)\n"
  payload[folder/'sources/Effective_Historical_E.dds']=(O/'sources/Effective_Historical_E.dds').read_bytes()
 payload[LIB/'CURRENT.json']=json.dumps({'release':erel,'current':'Current','snapshot':'Releases/'+erel,'manifest':'Current/library.json'},indent=2).encode()
 for row in authoring:
  src=Path(row['source']);prepared=Path(row['prepared']);payload[src]=prepared.read_bytes()
  for name in (bp.name,'CSC_Atlas_Modern_E_BAKERS.png'):payload[src.parent/'textures'/name]=(O/'textures'/name).read_bytes()
  if src.stem=='CSC_Level_2_Modern':payload[src.with_suffix('.cn6')]=(O/'native/CSC_Level_2_Modern.cn6').read_bytes()
 # Add texture content entries without rewriting unrelated ModBuddy metadata.
 proj=MOD/'Civ Supply Chains.civ6proj';raw=proj.read_bytes();newline=b'\r\n' if b'\r\n' in raw else b'\n';lines=[]
 for ident in ('CSC_Atlas_E_BAKERS','CSC_Atlas_Modern_E_BAKERS'):
  for ext in ('dds','tex'):
   path='Textures\\'+ident+'.'+ext;assert path.encode() not in raw;lines.append('    <Content Include="'+path+'"><SubType>Content</SubType></Content>')
 marker=newline+b'  </ItemGroup>';at=raw.index(marker);payload[proj]=raw[:at]+newline+newline.join(s.encode() for s in lines)+raw[at:]
 # Publish runtime last, after watched source PNGs. Never write AST/ArtDefs/XLP.
 for rel in checks['publish_files']:payload[MOD/rel]=(D/rel).read_bytes()
 backup=O/'publication-backup';backup.mkdir(exist_ok=True);rows=[]
 for i,(p,data) in enumerate(payload.items()):
  row={'destination':str(p),'before':sha(p) if p.exists() else None,'after':hashlib.sha256(data).hexdigest()}
  if p.exists():q=backup/f'{i:04}-{p.name}';shutil.copy2(p,q);row['backup']=str(q)
  rows.append(row)
 dump(backup/'manifest.json',rows)
 for row,(p,data) in zip(rows,payload.items()):
  actual=sha(p) if p.exists() else None
  if actual!=row['before']:
   # Only watched B DDS may change after its canonical PNG was updated above.
   assert p==MOD/'Textures/CSC_Atlas_Modern_B_BAKERS.dds',('Concurrent publication edit',p)
   shutil.copy2(p,backup/'watcher-B.dds')
  p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_name(p.name+'.interior-tmp');tmp.write_bytes(data);os.replace(tmp,p)
 dump(O/'publication-report.json',{'installed':True,'files':rows,'building_release':release,'emissive_release':erel,'service_changes':False,'AST_writes':False,'geometry_change':'60 native vertices UV3 only; shapes UV1 UV2 normals topology unchanged','game_deployment':False})
 print('PUBLISHED',len(rows),'files',flush=True)

if __name__=='__main__':globals()[sys.argv[1]]()
