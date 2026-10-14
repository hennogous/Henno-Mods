"""Package and register the isolated Tailors delivery trial; production ArtDefs stay unchanged."""
import argparse,copy,json,os,shutil,time,re
from pathlib import Path
import xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[3];MOD=ROOT/'Civ Supply Chains'
OUT=Path(r'C:\Users\Shadow\Desktop\Codex\CSC_Storage_L\delivery-01');STAGE=OUT/'package'
CACHE=Path(os.environ['APPDATA'])/'AssetCloud/mod-Civ Supply Chains-asset-deps.json'
PANTRY=Path(r"C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization VI SDK Assets\Civ6\pantry")
p=argparse.ArgumentParser();p.add_argument('--install',action='store_true');args=p.parse_args()
checks=json.loads((OUT/'native-check.json').read_text())
assert max(checks['master_vertex_errors'].values())<.2
assert checks['donkey_error_at_previous_scale']<.4
assert checks['combined_donkey'] and abs(checks['master_clip']['duration']-68)<.001
STAGE=OUT/'package-revision-08'
for folder in ('Assets','Geometries','Animations'):(STAGE/folder).mkdir(parents=True,exist_ok=True)
for part in ('Master',):
 for suffix,folder in (('_Model.fgx','Geometries'),('_Model.geo','Geometries'),('.fgx','Animations'),('.anm','Animations')):
  name='CSC_TEST_TAILORS_Delivery_'+part+suffix;shutil.copy2(OUT/name,STAGE/folder/name)
template=E.parse(MOD/'Assets/CSC_TEST_Storage_Crane.ast').getroot()
model_template=template.find('m_GeometrySet/m_ModelInstances/Element')
point_template=template.find('.//m_Points/Element')
def text(root,path,value):root.find(path).set('text',value)
def param(root,name):return next(e for e in root.findall('m_CookParams/m_Values/Element') if e.find('m_ParamName').get('text')==name)
def write(root,path):E.indent(root,space='  ');E.ElementTree(root).write(path,encoding='utf-8',xml_declaration=True)
def model(geo,material,instance=None):
 root=E.fromstring(geo.read_text().replace('AssetObjects:','AssetObjects..'));m=copy.deepcopy(model_template)
 text(m,'m_Name',instance or root.find('m_ModelName').get('text'));text(m,'m_GeoName',root.find('m_Name').get('text'))
 states=m.find('m_GroupStates');base={e.find('m_StateName').get('text'):copy.deepcopy(e) for e in states};states.clear()
 for mesh in root.findall('m_Meshes/Element'):
  for group in mesh.findall('m_Groups/Element'):
   for state,row in base.items():
    r=copy.deepcopy(row);text(r,'m_MeshName',mesh.find('m_Name').get('text'));text(r,'m_GroupName',group.find('m_Name').get('text'))
    for value in r.findall('m_Values/m_Values/Element'):
     name=value.find('m_ParamName').get('text')
     if name=='Material':value.find('m_ObjectName').set('text','IMP_Mine_Base' if 'Donkey' in mesh.find('m_Name').get('text') else material)
     if name=='Visible':value.find('m_bValue').text=str(state=='Worked').lower()
    states.append(r)
 return m
def point(name,bone,instance,asset,scale):
 p=copy.deepcopy(point_template);text(p,'m_Name',name);text(p,'m_BoneName',bone);text(p,'m_ModelInstanceName',instance);p.find('m_scale').text=str(scale)
 for tag in ('m_position','m_orientation'):
  for axis in 'xyz':p.find(tag+'/'+axis).text='0'
 text(param(p,'Asset'),'m_EntryName',asset);param(p,'RandomizeAnims').find('m_bValue').text='false'
 return p
names=[]
for part,asset_name in [('Master','CSC_TEST_TAILORS_Storage_Delivery')]:
 asset=copy.deepcopy(template);text(asset,'m_Name',asset_name)
 text(asset,'m_Description','Tailors delivery revision 8: tighter workshop turns, original-size Mine donkey, sideways cargo slide; one 68-second clip; 10-second rest; random phase per instance.')
 text(asset,'m_BehaviorData/m_dsgName','Standard_Landmark')
 clip='CSC_TEST_TAILORS_Delivery_'+part
 for n in asset.findall('.//m_AnimationName'):n.set('text',clip)
 asset.find('.//m_Timelines/Element/m_fDuration').text='68'
 points=asset.find('.//m_Points');points.clear()
 models=asset.find('m_GeometrySet/m_ModelInstances');models.clear()
 models.append(model(STAGE/'Geometries'/(clip+'_Model.geo'),'CSC_TAILORS_NE' if part=='Master' else 'IMP_Mine_Base'))
 if part=='Master':
  points.append(point('Delivery_Cargo','Cargo','CSC_ALL_Delivery_Rig','CSC_ALL_Textile_Bale',.675))
 write(asset,STAGE/'Assets'/(asset_name+'.ast'));names.append(asset_name)
 if part=='Master':
  # Context asset uses the user's current exported building and workshop at district origin.
  preview=copy.deepcopy(asset);preview_name=asset_name+'_Preview';text(preview,'m_Name',preview_name)
  text(preview,'m_BehaviorData/m_dsgName','Standard_LandmarkNoRandomOffset')
  text(preview,'m_Description','Delivery revision 8: tighter workshop turns and cargo slide; deterministic review from the start.')
  preview.find('m_GeometrySet/m_ModelInstances').append(model(MOD/'Geometries/CSC_Storage_L.geo','CSC_TAILORS_NE','Storage_Context'))
  geo=E.fromstring((MOD/'Geometries/CSC_Storage_L.geo').read_text().replace('AssetObjects:','AssetObjects..'))
  preview.find('.//m_Points').append(point('Workshop_Context',geo.find('m_ModelName').get('text'),'Storage_Context','CSC_TAILORS_Textile_Workshop',1))
  write(preview,STAGE/'Assets'/(preview_name+'.ast'));names.append(preview_name)

for name in names:
 trial=E.parse(STAGE/'Assets'/(name+'.ast')).getroot()
 assert any('Donkey' in n.get('text','') for n in trial.findall('.//m_MeshName')),'Donkey must be direct visible geometry'
 assert not any(n.get('text')=='CSC_TEST_TAILORS_Delivery_Donkey' for n in trial.findall('.//m_EntryName'))
 expected_dsg='Standard_LandmarkNoRandomOffset' if name.endswith('_Preview') else 'Standard_Landmark'
 assert trial.find('m_BehaviorData/m_dsgName').get('text')==expected_dsg

cache=json.loads(CACHE.read_text(encoding='utf-8-sig'));index={}
for p in MOD.rglob('*'):
 if p.is_file():index[(p.suffix.lower(),p.stem.casefold())]=p.relative_to(ROOT).as_posix()
for e in cache['Files']:
 key=e['Filename'].replace('\\','/');p=Path(key);index.setdefault((p.suffix.lower(),p.stem.casefold()),key)
payload=[p for p in STAGE.rglob('*') if p.is_file()]
for p in payload:index[(p.suffix.lower(),p.stem.casefold())]='Civ Supply Chains/'+p.relative_to(STAGE).as_posix()
def resolve(name,ext):
 key=(ext,name.replace('\\','/').split('/')[-1].casefold())
 if key in index:return index[key]
 if ext=='.dsg' and (PANTRY/'DSGs'/(name+'.dsg')).exists():return 'Civ6/pantry/DSGs/'+name+'.dsg'
 raise ValueError('Unresolved dependency '+name+ext)
deps={};descriptors={};type_ext={'MATERIAL':'.mtl','TEXTURE':'.tex','GEOMETRY':'.geo'}
for p in payload:
 if p.suffix not in ('.ast','.geo','.anm'):continue
 root=E.parse(p).getroot();key='Civ Supply Chains/'+p.relative_to(STAGE).as_posix();descriptors[key]=root;refs=set()
 for e in root.findall('.//m_DataFiles/Element/m_RelativePath'):
  assert (p.parent/e.get('text')).exists();refs.add(str(Path(key).parent/e.get('text')).replace('\\','/'))
 for e in root.findall('.//Element'):
  obj=e.find('m_ObjectName');kind=e.find('m_eObjectType')
  if obj is not None and kind is not None and obj.get('text') and kind.text in type_ext:refs.add(resolve(obj.get('text'),type_ext[kind.text]))
 for tag,ext in [('m_GeoName','.geo'),('m_AnimationName','.anm'),('m_EntryName','.ast'),('m_dsgName','.dsg')]:
  for e in root.findall('.//'+tag):
   if e.get('text'):refs.add(resolve(e.get('text'),ext))
 deps[key]=sorted(refs)
report={'assets':names,'files':[p.relative_to(STAGE).as_posix() for p in payload],'dependencies':deps,'installed':False,'ae_verified':False,'production_artdefs_changed':False}
if args.install:
 backup=OUT/('install-backup-'+time.strftime('%Y%m%d-%H%M%S'));backup.mkdir()
 def save(path,data):
  if path.exists():
   dest=backup/(path.relative_to(ROOT) if path.is_relative_to(ROOT) else Path('AssetCloud')/path.name);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,dest)
  path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
 for p in payload:save(MOD/p.relative_to(STAGE),p.read_bytes())
 xlp=MOD/'XLPs/CSC_TileBases.xlp';xml=xlp.read_text(encoding='utf-8-sig');add=[]
 for name in names:
  if f'<m_EntryID text="{name}"' not in xml:add.append(f'    <Element>\n      <m_EntryID text="{name}" />\n      <m_ObjectName text="{name}" />\n    </Element>\n')
 if add:
  xml,count=re.subn(r'(?m)^[ \t]*</m_Entries>',''.join(add)+'  </m_Entries>',xml)
  assert count==1,'XLP entry container missing or ambiguous'
  save(xlp,xml.encode())
 registered={e.get('text') for e in E.parse(xlp).findall('.//m_EntryID')}
 assert set(names)<=registered,('Unregistered delivery assets',set(names)-registered)
 project=MOD/'Civ Supply Chains.civ6proj';xml=project.read_text(encoding='utf-8-sig');content=[]
 for p in payload:
  rel=str(p.relative_to(STAGE)).replace('/','\\')
  if f'Include="{rel}"' not in xml:content.append(f'    <Content Include="{rel}">\n      <SubType>Content</SubType>\n    </Content>\n')
 if content:save(project,xml.replace('  <Import Project=','  <ItemGroup>\n'+''.join(content)+'  </ItemGroup>\n  <Import Project=',1).encode())
 raw=CACHE.read_bytes();cache=json.loads(raw.decode('utf-8-sig'));records={e['Filename'].replace('\\','/'):e for e in cache['Files']};types={'.ast':0,'.geo':2,'.anm':4}
 for key,root in descriptors.items():
  path=ROOT/key;record={'Filename':key,'Timestamp':int(path.stat().st_mtime*10000000)+116444736000000000,'Status':0,'Type':2,'EntityType':types[path.suffix],'EntityClass':root.find('m_ClassName').get('text'),'Filesize':path.stat().st_size,'Tags':[e.get('text') for e in root.findall('m_Tags/Element')],'Stats':{}}
  if key in records:records[key].update(record)
  else:cache['Files'].append(record)
  cache['Dependencies'][key]=deps[key]
 cache['Timestamp']=int(time.time()*10000000)+116444736000000000
 assert CACHE.read_bytes()==raw,'AssetCloud changed during registration; rerun to merge safely.'
 save(CACHE,json.dumps(cache,separators=(',',':')).encode());E.parse(xlp);E.parse(project)
 assert all((MOD/p.relative_to(STAGE)).read_bytes()==p.read_bytes() for p in payload)
 report.update(installed=True,backup=str(backup))
(OUT/'asset-package-check.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
