import sys,json,shutil,hashlib,subprocess,copy
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(Path(__file__).parent));import integrate as i
n=i.n;exp=i.exp;MOD=i.MOD;O=Path.home()/'Desktop/Codex/modern-l1-ao-fix-20261028';D=O/'staged';A=i.ART;LIB=A/'Textures/CSC_Buildings_Modern';NAME='CSC_Atlas_Modern_AO';IDS=(i.BASE,i.SILO,i.WIND,i.WATER)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2))
def stage():
 for folder in ('Assets','Geometries','Materials','Textures','CN6'):(D/folder).mkdir(parents=True,exist_ok=True)
 baseline={str(p.relative_to(MOD)):sha(p) for f in ('Assets','Geometries','Materials','Textures','ArtDefs','XLPs') for p in (MOD/f).glob('*') if p.is_file()};dump(O/'baseline.json',baseline)
 old=Image.open(LIB/'Current/textures'/(NAME+'.png')).convert('RGB');updated=old.copy();updated.paste(Image.open(O/'corrected-building-state-AO.png').convert('RGB'),(0,512));updated.paste(Image.open(O/'wind-tie-in-AO.png').convert('RGB'),(512,512));check=updated.copy()
 for rect in ((0,512,512,1024),(512,512,640,640)):check.paste(old.crop(rect),rect[:2])
 assert check.tobytes()==old.tobytes(),'Unrelated AO pixels changed'
 (O/'textures').mkdir(exist_ok=True);updated.save(O/'textures'/(NAME+'.png'));(O/'scalar').mkdir(exist_ok=True);scalar=O/'scalar'/(NAME+'.png');updated.getchannel('R').save(scalar)
 i.run([ROOT/'project/tools/directxtex/texconv.exe','-nologo','-y','-m','0','-f','R8_UNORM','--ignore-srgb','-o',D/'Textures',scalar],O/'dds-conversion.log');spec={'slot':'AO','size':[2048,2048],'format':'R8_UNORM'};exp.normalize_ao_dds(D/'Textures'/(NAME+'.dds'),spec,MOD/'Textures/CSC_Props_Shared_01_AO.dds');exp.validate_dds(D/'Textures'/(NAME+'.dds'),spec)
 exe,_=n.helper(O/'native-reader');converter=ROOT/'project/tools/cn6libs/CN6ToFGX.exe';checks=[]
 for base in (i.BASE,i.WATER):
  ident=base+'_CON+PIL';m=json.loads((O/'models'/(ident+'.json')).read_text());cn6=D/'CN6'/(ident+'.cn6');fgx=D/'Geometries'/(ident+'.fgx');exp.write_cn6(cn6,m);n.save(D/'Geometries'/(ident+'.geo'),exp.geometry(m,n.read(MOD/'Geometries'/(ident+'.geo'))));i.run([converter,cn6,fgx,'2'],O/(ident+'-convert.log'),converter.parent);p=O/(ident+'-native.json');i.run([exe,exe.parent,fgx,p],O/(ident+'-read.log'),exe.parent);raw=json.loads(p.read_text());error=0
  for x,y in zip(m['meshes'],raw['meshes']):
   assert x['name']==y['name'] and x['triangles']==y['triangles'] and y['boneBindings']==['Bone'];assert len(x['vertices'])==len(y['vertices'])
   for v,w in zip(x['vertices'],y['vertices']):
    error=max(error,max(abs(a-b) for a,b in zip(v,w['position']+w['normal']+w['tangent']+w['binormal']+w['uv']+w['uv2']+w['uv3'])));assert w['boneWeights']==[255,0,0,0,0,0,0,0] and w['boneIndices']==[0]*8
  assert error<1e-4;checks.append({'asset':ident,'native_readback_max_error':error})
 for ident in IDS:shutil.copy2(MOD/'Assets'/(ident+'.ast'),D/'Assets'/(ident+'.ast'))
 from render_ae_asset import read_xml
 r=n.Resolver(MOD,n.DEFAULT_SDK)
 for p in D.rglob('*'):
  if p.is_file():r.index[p.name.casefold()]={p}
 seen=set()
 def deps(p):
  if p in seen:return
  seen.add(p)
  if p.suffix not in ('.ast','.geo','.mtl','.tex'):return
  root=read_xml(p);todo=[]
  for a in root.findall('.//m_GeoName'):todo.append(r.resolve(a.get('text'),'.geo',p))
  for a in root.findall('.//Element'):
   name=exp.txt(a,'m_ObjectName');kind=a.findtext('m_eObjectType','')
   if name and kind in ('MATERIAL','TEXTURE'):todo.append(r.resolve(name,'.mtl' if kind=='MATERIAL' else '.tex',p))
   if exp.txt(a,'m_ParamName')=='Asset' and exp.txt(a,'m_EntryName'):todo.append(r.resolve(exp.txt(a,'m_EntryName'),'.ast',p))
  for a in root.findall('.//m_DataFiles/Element/m_RelativePath'):todo.append(p.parent/a.get('text'))
  for q in todo:
   if q.is_relative_to(MOD):
    target=D/q.relative_to(MOD)
    if not target.exists():target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(q,target)
   deps(q)
 for ident in IDS:deps(D/'Assets'/(ident+'.ast'))
 changes=[str(p.relative_to(D)) for f in ('Assets','Geometries','Materials','Textures') for p in (D/f).iterdir() if sha(p)!=sha(MOD/p.relative_to(D))];assert all(p.endswith(('_CON+PIL.fgx','_CON+PIL.geo',NAME+'.dds')) for p in changes)
 dump(O/'stage-report.json',{'passed':True,'native':checks,'publish_files':changes,'outside_state_AO_cell_identical':True,'ASTs_byte_unchanged':True});print('STAGED',changes)
def publish():
 report=json.loads((O/'stage-report.json').read_text());assert report['passed'];assert json.loads((O/'cook-check/result.json').read_text())['exit_code']==0;baseline=json.loads((O/'baseline.json').read_text());assert all(sha(MOD/p)==h for p,h in baseline.items());rows=json.loads((O/'repair-report.json').read_text());assert all(sha(r['source'])==r['before_sha256'] for r in rows)
 payload={MOD/p:(D/p).read_bytes() for p in report['publish_files']};release='2026-10-28_Modern_r009';cur=LIB/'Current';snap=LIB/'Releases'/release;assert not snap.exists()
 for p in cur.rglob('*'):
  if p.is_file():payload[snap/p.relative_to(cur)]=p.read_bytes()
 manifest=json.loads((cur/'library.json').read_text());manifest.update(release=release,previous_release=manifest['release'],status='CON/PIL upper wall winding repaired; geometry-only 128-sample AO; existing UV2 allocation and all other artwork unchanged');manifest['maps'][NAME+'.png']=sha(O/'textures'/(NAME+'.png'))
 config=json.loads((cur/'state-ao.json').read_text());config['previous_release']='2026-10-28_Modern_r008';config['patches'].append({'file':'bakes/Wind_TieIn_AO.png','rect':[512,512,640,640]});plan=json.loads((cur/'atlas-plan.json').read_text());plan['AO_allocations']['CSC_Level_1_S_Modern_CON+PIL_WindTieIn']=['building',[512,512,640,640]]
 updates={'textures/'+NAME+'.png':(O/'textures'/(NAME+'.png')).read_bytes(),'bakes/'+i.BASE+'_CON+PIL.png':(O/'corrected-building-state-AO.png').read_bytes(),'sources/previous-state-AO.png':(cur/'textures'/(NAME+'.png')).read_bytes(),'state-ao.json':json.dumps(config,indent=2).encode(),'library.json':json.dumps(manifest,indent=2).encode()}
 updates['atlas-plan.json']=json.dumps(plan,indent=2).encode();updates['bakes/Wind_TieIn_AO.png']=(O/'wind-tie-in-AO.png').read_bytes()
 for rel,data in updates.items():payload[cur/rel]=data;payload[snap/rel]=data
 payload[LIB/'CURRENT.json']=json.dumps({'release':release,'current':'Current','snapshot':'Releases/'+release,'manifest':'Current/library.json'},indent=2).encode()
 for row in rows:
  path=Path(row['source']);folder=O/'masters'/row['asset'];payload[path]=(folder/path.name).read_bytes();payload[path.with_suffix('.cn6')]=(D/'CN6'/path.with_suffix('.cn6').name).read_bytes();payload[path.parent/'validation.json']=(folder/'validation.json').read_bytes()
 backup=O/'backup';backup.mkdir(exist_ok=True);records=[]
 for j,(p,data) in enumerate(payload.items()):
  record={'destination':str(p),'before':sha(p) if p.exists() else None,'after':hashlib.sha256(data).hexdigest()}
  if p.exists():q=backup/f'{j:03}-{p.name}';shutil.copy2(p,q);record['backup']=str(q)
  records.append(record)
 dump(backup/'manifest.json',records)
 for r,(p,data) in zip(records,payload.items()):assert (sha(p) if p.exists() else None)==r['before'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);assert sha(p)==r['after']
 dump(O/'publication-report.json',{'installed':True,'files':records,'release':release,'ASTs_unchanged':True});n.cache(O);print('PUBLISHED',len(records))
def verify():
 report=json.loads((O/'publication-report.json').read_text());native=report.get('native_mip_regeneration',[])
 for row in report['files']:
  p=Path(row['destination']);actual=sha(p)
  if actual==row['after']:continue
  assert p==MOD/'Textures'/(NAME+'.dds'),('Unexpected post-publication change',p)
  a=(D/'Textures'/p.name).read_bytes();b=p.read_bytes();assert len(a)==len(b) and a[:128+2048*2048]==b[:128+2048*2048]
  native.append({'file':str(p),'published':row['after'],'native':actual,'base_pixels_and_header_identical':True});row['published_sha256']=row['after'];row['after']=actual;shutil.copy2(p,D/'Textures'/p.name)
 report['native_mip_regeneration']=native;dump(O/'publication-report.json',report)
 baseline=json.loads((O/'baseline.json').read_text());changed=set(json.loads((O/'stage-report.json').read_text())['publish_files'])
 for rel,h in baseline.items():
  p=MOD/rel
  if rel in changed or sha(p)==h:continue
  assert p==MOD/'Textures'/(NAME+'.tex'),('Unexpected other change',p)
  before=n.read(D/rel);after=n.read(p)
  for root in (before,after):root.find('m_ExportedTime').text='0'
  assert n.semantic(before)==n.semantic(after),'Texture configuration changed beyond native export timestamp'
  report['native_texture_export_timestamp']={'file':str(p),'before':h,'after':sha(p),'configuration_unchanged':True};shutil.copy2(p,D/rel)
 dump(O/'publication-report.json',report)
 print('VERIFIED',len(report['files']),'published files; all other mod assets unchanged; native mip updates',len(native))
if __name__=='__main__':globals()[sys.argv[1]]()
