"""Scoped first AE installation, native checks, immutable atlas publication."""
import sys,json,copy,shutil,subprocess,math,hashlib,os
from pathlib import Path
import xml.etree.ElementTree as E
from PIL import Image
import numpy as np
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT/'project/tools/art/modern_windmill'))
import modular_v9_native as n
exp=n.exp;MOD=n.MOD;ART=Path.home()/'Desktop/Working Files/3D Art';O=Path.home()/'Desktop/Codex/modern-bakery-ae-20261028';DST=O/'staged'
BASE='CSC_Level_2_Modern';SHELTER=BASE+'_Workshop';BAKERY='CSC_BAKERS_Bakery_Modern'
AO={'Building':('building',[1024,0,1536,512]),'Workshop':('building',[1536,0,1792,256]),'FlowerBox':('props',[512,0,768,256]),'Sign':('props',[768,0,1024,256]),'Oven':('props',[512,256,768,512]),'Rack':('props',[768,256,1024,512]),'Display':('props',[512,512,768,768]),'Trays':('props',[768,512,896,640]),'Truck':('props',[512,768,1024,1024])}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2))
def library(kind):return ART/'Textures'/('CSC_Buildings_Modern' if kind=='building' else 'CSC_Props_Modern')
def run(cmd,log,cwd=None):
 r=subprocess.run([str(v) for v in cmd],cwd=cwd,capture_output=True,text=True);log.write_text(r.stdout+r.stderr);assert r.returncode==0,(cmd,r.stdout[-1000:],r.stderr[-1000:])
def material_map(model):return {mat['name']:mat.get('external',mat['name']) for m in model['meshes'] for mat in m['materials']}
def instance(model):return exp.model_instance(model,material_map(model),('Worked','Unworked'))

def textures():
 # Merge only allocated new regions onto the CURRENT libraries, retaining the L1 AO repair.
 candidates=O/'textures';final=O/'merged-textures';final.mkdir(exist_ok=True);changes=[]
 for kind in ('building','props'):
  current=library(kind)/'Current';manifest=json.loads((current/'library.json').read_text())
  for name,h in manifest['maps'].items():assert sha(current/'textures'/name)==h
  prefix='CSC_Atlas_Modern' if kind=='building' else 'CSC_Props_Modern_01'
  for ch in ('B','N','G','M','AO','E')+ (('O',) if kind=='building' else ()):
   name=prefix+('_B_BAKERS' if kind=='building' and ch=='B' else '_'+ch)+'.png';candidate=Image.open(candidates/name).convert('RGB')
   old=Image.open(current/'textures'/name).convert('RGB') if (current/'textures'/name).exists() else Image.new('RGB',candidate.size,'white')
   assert old.size==candidate.size;new=old.copy()
   if ch=='AO':
    rects=[rect for page,rect in AO.values() if page==kind]
   elif kind=='building':rects=[tuple(int(v*old.width/1024) for v in (512,0,1024,512))]
   elif ch=='E':rects=[]
   else:rects=[(i%8*128,i//8*128,(i%8+1)*128,(i//8+1)*128) for i in range(24,39)]
   for rect in rects:new.paste(candidate.crop(rect),rect)
   if ch=='AO' and kind=='building':
    patch=Image.open(O/'bakes/Building.png').convert('RGB').resize((504,504),Image.Resampling.LANCZOS)
    new.paste(Image.fromarray(np.pad(np.array(patch),((4,4),(4,4),(0,0)),mode='edge')),(1024,0))
   mask=np.zeros((old.height,old.width),bool)
   for x,y,X,Y in rects:mask[y:Y,x:X]=True
   assert np.array_equal(np.array(old)[~mask],np.array(new)[~mask]);new.save(final/name)
   changes.append({'name':name,'family':kind,'channel':ch,'rectangles':rects,'outside_pixels_unchanged':True,'before':sha(current/'textures'/name) if (current/'textures'/name).exists() else None,'after':sha(final/name)})
   fmt='R8_UNORM' if ch in ('AO','G','M','O') else 'R8G8B8A8_UNORM';source=final/name
   if ch in ('AO','G','M','O'):
    source=O/'scalar'/name;source.parent.mkdir(exist_ok=True);new.getchannel('R').save(source)
   cmd=[ROOT/'project/tools/directxtex/texconv.exe','-nologo','-y','-m','0','-f',fmt,'--ignore-srgb','-o',DST/'Textures']
   if ch in ('B','E'):cmd+=['-srgb']
   run(cmd+[source],O/(name+'-convert.log'))
   spec={'slot':ch,'size':list(new.size),'format':fmt};dds=DST/'Textures'/(Path(name).stem+'.dds')
   if ch in ('AO','G','M','O'):exp.normalize_ao_dds(dds,spec,MOD/'Textures/CSC_Props_Shared_01_AO.dds')
   exp.validate_dds(dds,spec)
   template=MOD/'Textures'/(Path(name).stem+'.tex')
   if ch=='O':template=n.DEFAULT_SDK/'Civ6/pantry/Textures/Ancient_dirt_base_op.tex'
   r=n.read(template);n.text(r,'m_Name',Path(name).stem);n.text(r,'m_SourceFilePath',str(current/'textures'/name));n.text(r,'m_DataFiles/Element/m_RelativePath',dds.name)
   r.find('m_Width').text=str(new.width);r.find('m_Height').text=str(new.height);r.find('m_NumMipMaps').text=str(int(math.log2(new.width)))
   n.save(DST/'Textures'/(Path(name).stem+'.tex'),r)
 dump(O/'texture-checks.json',changes)

def stage():
 for f in ('Assets','Geometries','Materials','Textures','CN6','ArtDefs','XLPs'):(DST/f).mkdir(parents=True,exist_ok=True)
 baseline={p.relative_to(MOD).as_posix():sha(p) for f in ('Assets','Geometries','Materials','Textures','ArtDefs','XLPs') for p in (MOD/f).glob('*') if p.is_file()};dump(O/'baseline.json',baseline)
 masters=json.loads((O/'masters.json').read_text());models={}
 for row in masters:
  ident=row['id'];assert json.loads(Path(row['blend']).with_name(ident+'-validation.json').read_text())['automated_pass']
  model=json.loads((O/'models'/(ident+'.json')).read_text());models[ident]=model
  shutil.copy2(O/'native'/(ident+'.fgx'),DST/'Geometries'/(ident+'.fgx'));shutil.copy2(O/'native'/(ident+'.cn6'),DST/'CN6'/(ident+'.cn6'))
  n.save(DST/'Geometries'/(ident+'.geo'),exp.geometry(model,n.read(MOD/'Geometries/CSC_Level_1_S.geo')))
 textures()
 mat=n.read(MOD/'Materials/CSC_BAKERS_Modern.mtl')
 for row in mat.findall('m_CookParams/m_Values/Element'):
  if exp.txt(row,'m_ParamName')=='Opacity':row.find('m_ObjectName').set('text','CSC_Atlas_Modern_O')
 n.save(DST/'Materials/CSC_BAKERS_Modern.mtl',mat)
 template=n.read(MOD/'Assets/CSC_BAKERS_Wind_Mill_Modern.ast');historical=n.read(MOD/'Assets/CSC_BAKERS_Bakery.ast')
 state=copy.deepcopy(next(m for m in historical.find(exp.MODELS) if exp.txt(m,'m_Name')=='CSC_Level_2_CON+PIL'))
 def append_model(r,m):
  r.find(exp.MODELS).append(copy.deepcopy(m));E.SubElement(r.find('m_BehaviorData/m_referenceGeometryNames'),'Element',{'text':exp.txt(m,'m_GeoName')})
 for ident,model in models.items():
  assert not (MOD/'Assets'/(ident+'.ast')).exists(),('Existing assembly requires selective integration',ident)
  r=n.fresh_asset(ident,model,template);r.find(exp.MODELS).clear();r.find(exp.MODELS).append(instance(model))
  if ident==BASE:append_model(r,state)
  n.save(DST/'Assets'/(ident+'.ast'),r)
 placements=json.loads((O/'placements.json').read_text())
 for ident in (BAKERY,BAKERY+'_2'):
  assert not (MOD/'Assets'/(ident+'.ast')).exists(),('Existing AE assembly',ident)
  r=n.fresh_asset(ident,models[BASE],template);n.text(r,'m_Name',ident);n.text(r,'m_Description','Modern Bakery'+(' with delivery truck' if ident.endswith('_2') else ''))
  r.find(exp.MODELS).clear();r.find('m_BehaviorData/m_referenceGeometryNames').clear()
  for m in (instance(models[BASE]),instance(models[SHELTER]),state):append_model(r,m)
  # Retain shared L2 building/passage debris only; historical prop-scene debris is excluded.
  debris=copy.deepcopy(next(m for m in historical.find(exp.MODELS) if exp.txt(m,'m_GeoName')=='CSC_BAKERS_Bakery_PIL_Decals'))
  for row in list(debris.find('m_GroupStates')):
   if exp.txt(row,'m_GroupName')!='Ruin_Debris_Decal':debris.find('m_GroupStates').remove(row)
  # All GEO groups need state rows; unwanted prop debris is explicitly hidden.
  source=next(m for m in historical.find(exp.MODELS) if exp.txt(m,'m_GeoName')=='CSC_BAKERS_Bakery_PIL_Decals')
  for row in source.find('m_GroupStates'):
   if exp.txt(row,'m_GroupName')=='Ruin_Debris_Decal':continue
   row=copy.deepcopy(row)
   for v in row.findall('m_Values/m_Values/Element'):
    if exp.txt(v,'m_ParamName')=='Visible':v.find('m_bValue').text='false'
   debris.find('m_GroupStates').append(row)
  append_model(r,debris)
  for row in masters:
   group=row['group'];asset=row['id']
   if group in ('Building','Workshop') or group=='Truck' and not ident.endswith('_2'):continue
   a={**placements[group],'asset_id':asset,'instance_id':group,'support':'ground'}
   att,issues=exp.attachment(a,exp.csc_binding(asset,MOD/'XLPs/CSC_Tilebases.xlp'),BASE,{})
   assert not issues; n.text(att,'m_BoneName','Bone')
   for v in att.findall('m_CookParams/m_Values/Element'):
    if exp.txt(v,'m_ParamName')=='Cull Mode':v.find('m_Value').set('text','PERMANENT')
   r.find('m_BehaviorData/m_behaviorDataSets/m_attachmentPoints/m_Points').append(att)
  n.save(DST/'Assets'/(ident+'.ast'),r)
 # Dependency closure: never overwrite staged new maps with old installed copies.
 resolver=n.Resolver(MOD,n.DEFAULT_SDK)
 for p in DST.rglob('*'):
  if p.is_file():resolver.index[p.name.casefold()]={p}
 visited=set()
 def deps(p):
  if p in visited:return
  visited.add(p)
  if p.suffix not in ('.ast','.geo','.mtl','.tex'):return
  r=n.read(p);todo=[]
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
 for p in list((DST/'Assets').glob('*.ast')):deps(p)
 checks=[]
 for p in DST.rglob('*'):
  if p.is_file():resolver.index[p.name.casefold()]={p}
 for ident in (BAKERY,BAKERY+'_2'):
  for st in ('Worked','Unworked','Construction','Pillaged','Unbuilt'):
   a=n.Assembly(resolver,st);key=a.asset(DST/'Assets'/(ident+'.ast'));child=sum(len(m['groups']) for k,v in a.assets.items() if k!=key for m in v['models'])
   assert child==(7 if ident.endswith('_2') else 6) if st in ('Worked','Unworked') else child==0
   checks.append({'asset':ident,'state':st,'visible_prop_groups':child,'main_models':a.assets[key]['models']})
 # Preserve existing service SelectionRule; Modern priority is above both historical rows.
 path=MOD/'ArtDefs/CSC_Landmarks.artdef';raw=path.read_bytes();patches=[]
 for oldname,newname,oldasset,newasset,priority in [('02 Medieval: Bakery','06 Modern: Bakery','CSC_BAKERS_Bakery',BAKERY,2),('02 Medieval: Bakery 2','06 Modern: Bakery 2','CSC_BAKERS_Bakery_2',BAKERY+'_2',3)]:
  marker=f'<m_Name text="{oldname}"/>'.encode();assert raw.count(marker)==1 and newasset.encode() not in raw
  pos=raw.index(marker);start=raw.rfind(b'\n'+b'\t'*6+b'<Element>',0,pos);end=raw.index(b'\n'+b'\t'*6+b'</Element>',pos)+len(b'\n'+b'\t'*6+b'</Element>');block=raw[start:end];r=E.fromstring(block.strip())
  era=next(row for row in r.findall('m_Fields/m_Values/Element') if exp.txt(row,'m_ParamName')=='Tag_Era');assert exp.txt(era,'m_ElementName')=='DEFAULT'
  clone=block.replace(b'<m_ElementName text="DEFAULT"/>',b'<m_ElementName text="ARTERA_MODERN"/>',1).replace(f'<m_EntryName text="{oldasset}"/>'.encode(),f'<m_EntryName text="{newasset}"/>'.encode()).replace(marker,f'<m_Name text="{newname}"/>'.encode()).replace(f'<m_nValue>{priority-2}</m_nValue>'.encode(),f'<m_nValue>{priority}</m_nValue>'.encode())
  E.fromstring(clone.strip());patches.append((end,clone))
 for at,block in sorted(patches,reverse=True):raw=raw[:at]+block+raw[at:]
 E.fromstring(raw);(DST/'ArtDefs/CSC_Landmarks.artdef').write_bytes(raw)
 xlp=n.read(MOD/'XLPs/CSC_Tilebases.xlp');exp.merge_xlp(xlp,[*models,BAKERY,BAKERY+'_2']);n.save(DST/'XLPs/CSC_Tilebases.xlp',xlp)
 changed=[p.relative_to(DST).as_posix() for f in ('Assets','Geometries','Materials','Textures','ArtDefs','XLPs') for p in (DST/f).iterdir() if p.is_file() and (not (MOD/p.relative_to(DST)).exists() or sha(p)!=sha(MOD/p.relative_to(DST)))]
 dump(O/'staging-validation.json',{'passed':True,'publish_files':changed,'states':checks,'shared_state':'Existing historical L2 CON+PIL retained for first AE review','native':json.loads((O/'native-validation.json').read_text())})
 print('STAGED',len(changed),'files',flush=True)

def publish():
 checks=json.loads((O/'staging-validation.json').read_text());assert checks['passed'];cook=json.loads((O/'cook-check/result.json').read_text());assert cook['exit_code']==0 and cook['blps']
 base=json.loads((O/'baseline.json').read_text());assert all(sha(MOD/p)==h for p,h in base.items()),'Concurrent project edit; restage'
 edit=json.loads((O/'user-edits.json').read_text());assert sha(edit['source'])==edit['sha256'],'New human save; re-export'
 payload={};releases={'building':'2026-10-28_Modern_r010','props':'2026-10-28_Modern_r006'};masters=json.loads((O/'masters.json').read_text())
 for kind,release in releases.items():
  lib=library(kind);cur=lib/'Current';snap=lib/'Releases'/release;assert not snap.exists()
  for p in cur.rglob('*'):
   if p.is_file():payload[snap/p.relative_to(cur)]=p.read_bytes()
  manifest=json.loads((cur/'library.json').read_text());manifest.update(previous_release=manifest['release'],release=release,status='Modern L2/Bakery first AE installation; final human bargeboard edits and fresh geometry AO',source=edit['source'],source_sha256=edit['sha256'],rebuild_tool='scripts/rebuild_published.py')
  plan=json.loads((cur/'atlas-plan.json').read_text());plan.setdefault('modern_level2',{})['installed_assets']=[r['id'] for r in masters]
  for row in masters:
   page,rect=AO[row['group']];plan['AO_allocations'][row['id']]=[page,rect]
  plan['building']['stage_3_cells']={'0':'brick','1':'stone','2':'green roof','3':'cream wood','4':'cream','5':'upper window','6':'glazed door','7':'chimney','8':'green wood','11':'interior rear shelves','12':'interior side wall','13':'dark mouth','14':'ground window','15':'interior floor'}
  plan['props']['additional_cells']={str(k):v for k,v in zip(range(24,39),['flowerbox','blank hex sign','oven front','bread tray top','striped canopy','bakery sign','empty tray','loaf crust','truck front','cab side','cargo bread logo','tyre hub','round loaves tray','baguettes tray','rolls croissants tray'])}
  updates={}
  for row in json.loads((O/'texture-checks.json').read_text()):
   if row['family']!=kind:continue
   p=O/'merged-textures'/row['name'];updates['textures/'+p.name]=p.read_bytes();updates['sources/published-registered/'+p.name]=p.read_bytes();manifest['maps'][p.name]=sha(p)
  updates['library.json']=json.dumps(manifest,indent=2).encode();updates['atlas-plan.json']=json.dumps(plan,indent=2).encode()
  updates['scripts/rebuild_published.py']=b"from pathlib import Path\nimport shutil\np=Path(__file__).resolve().parents[1]\nfor f in (p/'sources/published-registered').glob('*.png'):shutil.copy2(f,p/'textures'/f.name)\n"
  updates['sources/ae-install/user-edits.json']=(O/'user-edits.json').read_bytes();updates['sources/ae-install/texture-checks.json']=(O/'texture-checks.json').read_bytes()
  provenance=ART/'BAKERS/Bakery/modern/revision-03-height-interiors/texture-sources'
  for p in provenance.rglob('*'):
   if p.is_file() and p.suffix!='.blend':updates['sources/bakery-v3/'+p.relative_to(provenance).as_posix()]=p.read_bytes()
  if kind=='building':updates['bakes/CSC_Level_2_Modern.png']=(O/'bakes/Building.png').read_bytes()
  for rel,data in updates.items():payload[cur/rel]=data;payload[snap/rel]=data
  payload[lib/'CURRENT.json']=json.dumps({'release':release,'current':'Current','snapshot':'Releases/'+release,'manifest':'Current/library.json'},indent=2).encode()
 for rel in checks['publish_files']:payload[MOD/rel]=(DST/rel).read_bytes()
 # Source model texture snapshots must resolve to exactly the installed atlas release.
 for folder in {Path(r['blend']).parent for r in masters}|{O}:
  for p in (O/'merged-textures').glob('*.png'):payload[folder/'textures'/p.name]=p.read_bytes()
 backup=O/'publication-backup';backup.mkdir(exist_ok=True);rows=[]
 for i,(p,data) in enumerate(payload.items()):
  row={'destination':str(p),'before':sha(p) if p.exists() else None,'after':hashlib.sha256(data).hexdigest()}
  if p.exists():q=backup/f'{i:04}-{p.name}';shutil.copy2(p,q);row['backup']=str(q)
  rows.append(row)
 dump(backup/'manifest.json',rows)
 for row,(p,data) in zip(rows,payload.items()):
  assert (sha(p) if p.exists() else None)==row['before'];p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_name(p.name+'.bakery-install-tmp');tmp.write_bytes(data);os.replace(tmp,p);assert sha(p)==row['after']
 changed=set(checks['publish_files']);assert all(sha(MOD/p)==h for p,h in base.items() if p not in changed)
 assert all(sha(MOD/p)==h for p,h in base.items() if p.startswith('Assets/'))
 dump(O/'publication-report.json',{'installed':True,'files':rows,'releases':releases,'all_existing_ASTs_byte_identical':True,'art_era':'ARTERA_MODERN','service_rule_preserved':True,'game_deployment':False,'in_game_tested':False})
 print('INSTALLED',BAKERY,BAKERY+'_2',len(rows),'files',flush=True)

def resume_after_texture_watch():
 """AE watches canonical PNGs and reimports DDS/TEX while they are published.

 Resume only this documented race: unrelated or semantic source edits abort.
 The backed-up manifest remains the original transaction record.
 """
 rows=json.loads((O/'publication-amended.json' if (O/'publication-amended.json').exists() else O/'publication-backup/manifest.json').read_text());events=[]
 edit=json.loads((O/'user-edits.json').read_text());assert sha(edit['source'])==edit['sha256']
 for i,row in enumerate(rows):
  p=Path(row['destination']);actual=sha(p) if p.exists() else None
  if actual==row['after']:continue
  if row.get('source_override') and not p.is_relative_to(MOD):
   assert actual in row['allowed_previous'],('Unreviewed edit after texture approval',p)
   data=Path(row['source_override']).read_bytes();assert hashlib.sha256(data).hexdigest()==row['after'];p.write_bytes(data);continue
  if p.is_relative_to(MOD):
   staged=DST/p.relative_to(MOD);assert staged.is_file() and sha(staged)==row['after']
   if actual!=row['before']:
    assert p.suffix in ('.dds','.tex') and p.parent==MOD/'Textures' and p.stem.startswith(('CSC_Atlas_Modern','CSC_Props_Modern_01')),(p,actual)
    if p.suffix=='.tex':
     before=n.read(Path(row['backup']));live=n.read(p)
     for r in (before,live):
      for tag in ('m_ImportedTime','m_ExportedTime'):
       if r.find(tag) is not None:r.find(tag).text='0'
     assert n.semantic(before)==n.semantic(live),('Semantic texture edit',p)
    backup=O/'watcher-reimport-backup'/p.name;backup.parent.mkdir(exist_ok=True);shutil.copy2(p,backup);events.append({'path':str(p),'watcher_sha256':actual,'backup':str(backup)})
   data=staged.read_bytes()
  else:
   assert actual==row['before'] and p.parent.name=='textures',('Unexpected pending publication',p)
   candidate=O/'merged-textures'/p.name;assert sha(candidate)==row['after'];data=candidate.read_bytes()
  p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_name(p.name+'.bakery-install-tmp');tmp.write_bytes(data);os.replace(tmp,p);assert sha(p)==row['after']
 base=json.loads((O/'baseline.json').read_text());changed=set(json.loads((O/'staging-validation.json').read_text())['publish_files']);watcher_metadata=[]
 for rel,h in base.items():
  p=MOD/rel
  if rel in changed or sha(p)==h:continue
  if p.suffix=='.dds' and p.stem.startswith(('CSC_Atlas_Modern','CSC_Props_Modern_01')):
   staged=DST/rel;assert staged.exists() and sha(staged)==h
   assert np.array_equal(np.array(Image.open(p).convert('RGBA')),np.array(Image.open(staged).convert('RGBA'))),('Changed companion pixels',p)
   q=O/'watcher-reimport-backup'/p.name;shutil.copy2(p,q);shutil.copy2(staged,p);events.append({'path':str(p),'reason':'AE re-encoded unchanged companion DDS; pixels identical','backup':str(q)});continue
  # AE also updates export timestamps on unchanged companion TEX descriptors.
  assert p.suffix=='.tex' and p.stem.startswith(('CSC_Atlas_Modern','CSC_Props_Modern_01')),('Unrelated change',p)
  staged=DST/rel;assert staged.exists()
  a=n.read(p);b=n.read(staged)
  for r in (a,b):
   for tag in ('m_ImportedTime','m_ExportedTime'):
    if r.find(tag) is not None:r.find(tag).text='0'
  assert n.semantic(a)==n.semantic(b);watcher_metadata.append(rel)
 assert all(sha(MOD/p)==h for p,h in base.items() if p.startswith('Assets/'))
 dump(O/'publication-report.json',{'installed':True,'files':rows,'releases':{'building':'2026-10-28_Modern_r010','props':'2026-10-28_Modern_r006'},'all_existing_ASTs_byte_identical':True,'art_era':'ARTERA_MODERN','service_rule_preserved':True,'game_deployment':False,'in_game_tested':False,'AE_watcher_reimports':events,'AE_timestamp_only_updates':watcher_metadata})
 print('INSTALL_COMPLETE; native-tested DDS restored after AE canonical-source auto-reimport',flush=True)

def accept_user_basecolour():
 name='CSC_Atlas_Modern_B_BAKERS.png';cur=library('building')/'Current';src=cur/'textures'/name
 approved=O/'sources/User_Edited_Atlas_B.png';assert not approved.exists();shutil.copy2(src,approved)
 im=Image.open(approved);assert im.size==(1024,1024)
 shutil.copy2(approved,O/'merged-textures'/name)
 run([ROOT/'project/tools/directxtex/texconv.exe','-nologo','-y','-m','0','-f','R8G8B8A8_UNORM','--ignore-srgb','-srgb','-o',DST/'Textures',O/'merged-textures'/name],O/'user-B-convert.log')
 dds=DST/'Textures/CSC_Atlas_Modern_B_BAKERS.dds';exp.validate_dds(dds,{'slot':'B','size':[1024,1024],'format':'R8G8B8A8_UNORM'})
 rows=json.loads((O/'publication-backup/manifest.json').read_text());overrides=O/'user-amendment';overrides.mkdir(exist_ok=True)
 for i,row in enumerate(rows):
  p=Path(row['destination']);data=None
  if p==MOD/'Textures'/dds.name:data=dds.read_bytes()
  elif p.name==name and p.parent.name=='textures' and 'Releases' not in p.parts:data=approved.read_bytes()
  elif p==cur/'sources/published-registered'/name:data=approved.read_bytes()
  elif p==cur/'library.json':
   m=json.loads(p.read_text());m['maps'][name]=sha(approved);m['status']='Final human base-colour edit accepted during AE installation; r011 publication follows';data=json.dumps(m,indent=2).encode()
  if data is not None:
   q=overrides/f'{i:03}-{p.name}';q.write_bytes(data);row['allowed_previous']=[row['before'],row['after'],sha(approved)];row['after']=sha(q);row['source_override']=str(q)
 dump(O/'publication-amended.json',rows);dump(O/'accepted-user-texture.json',{'source':str(src),'snapshot':str(approved),'sha256':sha(approved),'authorization':'User: Yes—keep my newer texture','dimensions':list(im.size)})
 print('Accepted and converted human base-colour texture',flush=True)

def publish_user_texture_release():
 lib=library('building');cur=lib/'Current';release='2026-10-28_Modern_r011';snap=lib/'Releases'/release;assert not snap.exists()
 accepted=json.loads((O/'accepted-user-texture.json').read_text());assert sha(accepted['source'])==accepted['sha256']
 manifest=json.loads((cur/'library.json').read_text());manifest.update(previous_release=manifest['release'],release=release,status='Henno base-colour edit retained over first Bakery AE install',human_texture_source=accepted)
 assert manifest['maps']['CSC_Atlas_Modern_B_BAKERS.png']==accepted['sha256']
 for name,h in manifest['maps'].items():assert sha(cur/'textures'/name)==h
 shutil.copytree(cur,snap);dump(snap/'library.json',manifest);dump(cur/'library.json',manifest);dump(lib/'CURRENT.json',{'release':release,'current':'Current','snapshot':'Releases/'+release,'manifest':'Current/library.json'})
 report=json.loads((O/'publication-report.json').read_text());report['releases']['building']=release;report['human_texture_retained']=accepted;dump(O/'publication-report.json',report)
 print('PUBLISHED_HUMAN_TEXTURE',release,flush=True)

def merge_user_l1_and_bakery():
 """Keep the human's L1 edit; add Bakery artwork to their still-empty TR quadrant."""
 lib=library('building');cur=lib/'Current';release='2026-10-28_Modern_r012';snap=lib/'Releases'/release;assert not snap.exists()
 accepted=json.loads((O/'accepted-user-texture.json').read_text());source=Path(accepted['source']);assert sha(source)==accepted['sha256']
 before=Image.open(source).convert('RGBA');a=np.array(before);assert np.all(a[:512,512:,:3]==128) and np.all(a[:512,512:,3]==255),'TR is no longer blank; reassess human edit'
 old=Image.open(lib/'Releases/2026-10-28_Modern_r010/textures/CSC_Atlas_Modern_B_BAKERS.png').convert('RGBA');merged=before.copy();merged.paste(old.crop((512,0,1024,512)),(512,0))
 mask=np.ones((1024,1024),bool);mask[:512,512:]=False;assert np.array_equal(np.array(merged)[mask],a[mask])
 png=O/'merged-textures/CSC_Atlas_Modern_B_BAKERS.png';merged.save(png)
 run([ROOT/'project/tools/directxtex/texconv.exe','-nologo','-y','-m','0','-f','R8G8B8A8_UNORM','--ignore-srgb','-srgb','-o',DST/'Textures',png],O/'merged-human-B-convert.log')
 dds=DST/'Textures/CSC_Atlas_Modern_B_BAKERS.dds';exp.validate_dds(dds,{'slot':'B','size':[1024,1024],'format':'R8G8B8A8_UNORM'})
 shutil.copytree(cur,snap);manifest=json.loads((cur/'library.json').read_text());manifest.update(previous_release=manifest['release'],release=release,status='Human L1 B edits preserved pixel-exact; Bakery artwork restored only into their empty top-right quadrant')
 manifest['maps'][png.name]=sha(png);manifest['human_texture_merge']={'human_snapshot':accepted,'restored_rect':[512,0,1024,512],'bakery_source_release':'2026-10-28_Modern_r010','outside_rect_RGBA_identical':True}
 for folder in (cur,snap):
  shutil.copy2(png,folder/'textures'/png.name);shutil.copy2(png,folder/'sources/published-registered'/png.name);dump(folder/'library.json',manifest)
 dump(lib/'CURRENT.json',{'release':release,'current':'Current','snapshot':'Releases/'+release,'manifest':'Current/library.json'})
 masters=json.loads((O/'masters.json').read_text())
 for folder in {Path(r['blend']).parent for r in masters}|{O}:shutil.copy2(png,folder/'textures'/png.name)
 report=json.loads((O/'publication-report.json').read_text());report['releases']['building']=release;report['human_texture_merge']=manifest['human_texture_merge']
 for row in report['files']:
  p=Path(row['destination'])
  if p==MOD/'Textures'/dds.name:row['after']=sha(dds)
  elif p.name==png.name and 'Releases' not in p.parts and p.parent.name in ('textures','published-registered'):row['after']=sha(png)
 dump(O/'publication-report.json',report);dump(O/'human-texture-merge.json',manifest['human_texture_merge'])
 print('MERGED_HUMAN_L1_AND_BAKERY',release,flush=True)

def finish_merged_runtime():
 p=DST/'Textures/CSC_Atlas_Modern_B_BAKERS.dds';shutil.copy2(p,MOD/'Textures'/p.name)
 assert sha(MOD/'Textures'/p.name)==sha(p);print('INSTALLED_MERGED_DDS',flush=True)

def preserve_live_prop_edit():
 lib=library('props');cur=lib/'Current';release='2026-10-28_Modern_r007';snap=lib/'Releases'/release;assert not snap.exists()
 p=cur/'textures/CSC_Props_Modern_01_B.png';human=Image.open(p).convert('RGBA');prior=Image.open(lib/'Releases/2026-10-28_Modern_r006/textures'/p.name).convert('RGBA')
 a=np.array(human);b=np.array(prior);changed=[i for i in range(64) if not np.array_equal(a[i//8*128:(i//8+1)*128,i%8*128:(i%8+1)*128],b[i//8*128:(i//8+1)*128,i%8*128:(i%8+1)*128])]
 assert set(changed)<={0,1,9},('New texture edit beyond observed mill cells',changed)
 snapshot=O/'sources/User_Edited_Props_B.png';shutil.copy2(p,snapshot);shutil.copy2(p,O/'merged-textures'/p.name)
 run([ROOT/'project/tools/directxtex/texconv.exe','-nologo','-y','-m','0','-f','R8G8B8A8_UNORM','--ignore-srgb','-srgb','-o',DST/'Textures',O/'merged-textures'/p.name],O/'human-props-B-convert.log')
 dds=DST/'Textures'/p.with_suffix('.dds').name;exp.validate_dds(dds,{'slot':'B','size':[1024,1024],'format':'R8G8B8A8_UNORM'})
 manifest=json.loads((cur/'library.json').read_text());manifest.update(previous_release=manifest['release'],release=release,status='Human mill prop colour edits retained during Bakery installation',human_colour_cells=changed);manifest['maps'][p.name]=sha(p)
 shutil.copy2(p,cur/'sources/published-registered'/p.name);shutil.copytree(cur,snap);dump(cur/'library.json',manifest);dump(snap/'library.json',manifest);dump(lib/'CURRENT.json',{'release':release,'current':'Current','snapshot':'Releases/'+release,'manifest':'Current/library.json'})
 masters=json.loads((O/'masters.json').read_text())
 for folder in {Path(r['blend']).parent for r in masters}|{O}:shutil.copy2(p,folder/'textures'/p.name)
 assert sha(p)==sha(snapshot);shutil.copy2(dds,MOD/'Textures'/dds.name)
 r=json.loads((O/'publication-report.json').read_text());r['releases']['props']=release;r['human_prop_texture']={'source':str(p),'snapshot':str(snapshot),'sha256':sha(p),'changed_cells':changed,'new_Bakery_cells_unchanged':True}
 for row in r['files']:
  q=Path(row['destination'])
  if q==MOD/'Textures'/dds.name:row['after']=sha(dds)
 dump(O/'publication-report.json',r);print('HUMAN_PROP_EDITS_PRESERVED',changed,flush=True)

if __name__=='__main__':globals()[sys.argv[1]]()
