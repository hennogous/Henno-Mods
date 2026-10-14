"""Assemble, validate and optionally install the separate storage animation AE trial.

python this.py --output <build_storage_crane_ae output> [--install]
Only named CSC_TEST assets are generated. Existing art, library geometry and gameplay
bindings are unchanged; installation adds XLP/Content entries and AssetCloud records.
"""
import argparse,copy,hashlib,json,os,re,shutil,subprocess,time
from pathlib import Path
import xml.etree.ElementTree as E
from PIL import Image

ROOT=Path(__file__).resolve().parents[3];MOD=ROOT/'Civ Supply Chains'
PANTRY=Path(r"C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization VI SDK Assets\Civ6\pantry")
CACHE=Path(os.environ['APPDATA'])/'AssetCloud/mod-Civ Supply Chains-asset-deps.json'
parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);parser.add_argument('--install',action='store_true');args=parser.parse_args()
OUT=Path(args.output).resolve();STAGE=OUT/'package';STAGE.mkdir(exist_ok=True)
for name in ('Assets','Geometries','Animations','Materials','Textures'):(STAGE/name).mkdir(exist_ok=True)
def write_xml(root,path):
 E.indent(root,space='  ');E.ElementTree(root).write(path,encoding='utf-8',xml_declaration=True)
def text(root,path,value):root.find(path).set('text',value)
def param(root,name):return next(e for e in root.findall('m_CookParams/m_Values/Element') if e.find('m_ParamName').get('text')==name)

for stem,folder,exts in [('CSC_TEST_Storage_Crane_Lift_Model','Geometries',('.fgx','.geo')),('CSC_TEST_Storage_Shell','Geometries',('.fgx','.geo')),('CSC_TEST_Storage_Crane_Lift','Animations',('.fgx','.anm'))]:
 for ext in exts:
  target=STAGE/folder/(stem+ext);shutil.copy2(OUT/(stem+ext),target)
  if ext=='.geo':target.write_text(target.read_text().replace('AssetObjects:','AssetObjects..'))
  if stem=='CSC_TEST_Storage_Shell' and ext=='.geo':
   shell_geo=E.parse(target).getroot()
   for value in shell_geo.findall('m_Meshes/Element/m_nBoundBoneCount'):value.text='0'
   write_xml(shell_geo,target) # Format 2 is static: do not report the source CN6 weights as native bindings.

# Neutral AO avoids sampling the unrelated static UV2 atlas on the one-UV rig.
# Atlas base/normal/gloss/metalness/opacity are reused without recolouring.
white='CSC_TEST_Crane_White_AO';png=OUT/(white+'.png');Image.new('L',(4,4),255).save(png)
r=subprocess.run([str(ROOT/'project/tools/directxtex/texconv.exe'),'-nologo','-y','-f','R8_UNORM','-m','1','-o',str(STAGE/'Textures'),str(png)],capture_output=True,text=True)
(OUT/'texture-conversion.log').write_text(r.stdout+r.stderr);assert r.returncode==0,r.stderr
tex=E.parse(MOD/'Textures/CSC_Atlas_AO2.tex').getroot();text(tex,'m_Name',white);text(tex,'m_SourceFilePath','');text(tex,'m_DataFiles/Element/m_RelativePath',white+'.dds')
for key,val in [('m_Height','4'),('m_Width','4'),('m_NumMipMaps','1')]:tex.find(key).text=val
tex.find('m_ExportSettings/bUseMips').text='false';write_xml(tex,STAGE/'Textures'/(white+'.tex'))
mat=E.parse(MOD/'Materials/CSC_TAILORS_NE.mtl').getroot();text(mat,'m_Name','CSC_TEST_Storage_Crane_Material');param(mat,'AO').find('m_ObjectName').set('text',white)
write_xml(mat,STAGE/'Materials/CSC_TEST_Storage_Crane_Material.mtl')

template=E.parse(PANTRY/'Assets/PROP_Crane_LG_Stone.ast').getroot()
mine=E.parse(PANTRY/'Assets/IMP_Mine_AN_01.ast').getroot()
def model_instance(geo_path,material,worked_only):
 geo=E.parse(geo_path).getroot();model=E.Element('Element')
 E.SubElement(model,'m_Name',text=geo.find('m_ModelName').get('text'));E.SubElement(model,'m_GeoName',text=geo.find('m_Name').get('text'))
 states=E.SubElement(model,'m_GroupStates');base=template.find('m_GeometrySet/m_ModelInstances/Element/m_GroupStates/Element')
 for mesh in geo.findall('m_Meshes/Element'):
  for group in mesh.findall('m_Groups/Element'):
   for state in ('Worked','Unworked','Pillaged','Construction','Unbuilt'):
    row=copy.deepcopy(base);text(row,'m_MeshName',mesh.find('m_Name').get('text'));text(row,'m_GroupName',group.find('m_Name').get('text'));text(row,'m_StateName',state)
    for p in row.findall('m_Values/m_Values/Element'):
     n=p.find('m_ParamName').get('text')
     if n=='Material':p.find('m_ObjectName').set('text',material)
     if n=='Visible':p.find('m_bValue').text=str(state=='Worked' or (state=='Unworked' and not worked_only)).lower()
    states.append(row)
 return model

for name,shell in [('CSC_TEST_Storage_Crane',False),('CSC_TEST_Storage_L_Animated',True)]:
 asset=copy.deepcopy(template);text(asset,'m_Name',name);text(asset,'m_Description','AE animation trial: textile bale lift; Worked only; 12-second one-way delivery, reset at loop seam.')
 text(asset,'m_BehaviorData/m_dsgName','Standard_LandmarkNoRandomOffset')
 for node in asset.findall('.//m_AnimationName'):node.set('text','CSC_TEST_Storage_Crane_Lift')
 asset.find('.//m_Timelines/Element/m_fDuration').text='12.000001'
 points=asset.find('.//m_Points');points.clear();point=copy.deepcopy(mine.find('.//m_Points/Element'))
 text(point,'m_Name','Textile_Bale_Load');text(point,'m_BoneName','Load');text(point,'m_ModelInstanceName','CSC_TEST_Crane_Rig');point.find('m_scale').text='0.75'
 for axis in ('x','y','z'):point.find('m_position/'+axis).text='0';point.find('m_orientation/'+axis).text='0'
 p=param(point,'Asset')
 for key,val in [('m_EntryName','CSC_ALL_Textile_Bale'),('m_XLPPath','csc_tilebases.xlp'),('m_BLPPackage','Landmarks/CSC_Tilebases')]:text(p,key,val)
 param(point,'RandomizeAnims').find('m_bValue').text='false';points.append(point)
 models=asset.find('m_GeometrySet/m_ModelInstances');models.clear()
 models.append(model_instance(STAGE/'Geometries/CSC_TEST_Storage_Crane_Lift_Model.geo','CSC_TEST_Storage_Crane_Material',True))
 if shell:models.append(model_instance(STAGE/'Geometries/CSC_TEST_Storage_Shell.geo','CSC_TAILORS_NE',False))
 # Keep any asset-level AO/lighting overrides neutral: materials own their maps.
 for p in asset.findall('m_CookParams/m_Values/Element'):
  if p.find('m_ParamName').get('text') in ('AO','LightMap','EmissionMap') and p.find('m_ObjectName') is not None:p.find('m_ObjectName').set('text','')
 write_xml(asset,STAGE/'Assets'/(name+'.ast'))

# Resolve names against current project files and SDK catalog entries before installation.
cache=json.loads(CACHE.read_text(encoding='utf-8-sig'));index={}
for p in MOD.rglob('*'):
 if p.is_file():index[(p.suffix.lower(),p.stem.casefold())]=p.relative_to(ROOT).as_posix()
for entry in cache['Files']:
 key=entry['Filename'].replace('\\','/');p=Path(key)
 index.setdefault((p.suffix.lower(),p.stem.casefold()),key)
payload=[p for p in STAGE.rglob('*') if p.is_file()]
for p in payload:index[(p.suffix.lower(),p.stem.casefold())]='Civ Supply Chains/'+p.relative_to(STAGE).as_posix()
def resolve(name,ext):
 key=(ext,name.replace('\\','/').split('/')[-1].casefold())
 if key in index:return index[key]
 if ext=='.dsg' and (PANTRY/'DSGs'/(name+'.dsg')).exists():return 'Civ6/pantry/DSGs/'+name+'.dsg'
 raise ValueError('Unresolved dependency '+name+ext)
deps={};descriptors={};type_ext={'MATERIAL':'.mtl','TEXTURE':'.tex','GEOMETRY':'.geo'}
for p in payload:
 if p.suffix not in ('.ast','.geo','.anm','.mtl','.tex'):continue
 root=E.parse(p).getroot();key='Civ Supply Chains/'+p.relative_to(STAGE).as_posix();descriptors[key]=root;refs=set()
 for e in root.findall('.//m_DataFiles/Element/m_RelativePath'):
  file=p.parent/e.get('text');assert file.exists(),file;refs.add(str(Path(key).parent/e.get('text')).replace('\\','/'))
 for e in root.findall('.//Element'):
  obj=e.find('m_ObjectName');kind=e.find('m_eObjectType')
  if obj is not None and kind is not None and obj.get('text') and kind.text in type_ext:refs.add(resolve(obj.get('text'),type_ext[kind.text]))
 for tag,ext in [('m_GeoName','.geo'),('m_AnimationName','.anm'),('m_EntryName','.ast'),('m_dsgName','.dsg')]:
  for e in root.findall('.//'+tag):
   if e.get('text'):refs.add(resolve(e.get('text'),ext))
 deps[key]=sorted(refs)

model=E.parse(STAGE/'Geometries/CSC_TEST_Storage_Crane_Lift_Model.geo').getroot()
assert model.find("m_Bones/Element[@text='Load']") is not None
assert sum(int(e.text) for e in model.findall('.//m_nBoundBoneCount'))>0
assert E.parse(STAGE/'Animations/CSC_TEST_Storage_Crane_Lift.anm').find('m_ClassName').get('text')=='Landmark'
checks=json.loads((OUT/'conversion-check.json').read_text());assert checks['native_vertex_error_max']<.15 and checks['attachment_native_matrix_error_max']<.06
report={'assets':['CSC_TEST_Storage_Crane','CSC_TEST_Storage_L_Animated'],'dependencies':deps,'files':[p.relative_to(STAGE).as_posix() for p in payload],'conversion':checks,'installed':False,'ae_playback_verified':False,'production_artdefs_changed':False}

if args.install:
 backup=OUT/('backup-'+time.strftime('%Y%m%d-%H%M%S'));backup.mkdir()
 def save(path,data):
  if path.exists():
   rel=path.relative_to(ROOT) if path.is_relative_to(ROOT) else Path('AssetCloud')/path.name
   dest=backup/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,dest)
  path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
 for p in payload:save(MOD/p.relative_to(STAGE),p.read_bytes())
 xlp=MOD/'XLPs/CSC_TileBases.xlp';xml=xlp.read_text(encoding='utf-8-sig');add=[]
 for name in report['assets']:
  if f'<m_EntryID text="{name}"' not in xml:add.append(f'    <Element>\n      <m_EntryID text="{name}" />\n      <m_ObjectName text="{name}" />\n    </Element>\n')
 if add:save(xlp,xml.replace('  </m_Entries>',''.join(add)+'  </m_Entries>').encode())
 assert all(e in xlp.read_text() for e in report['assets'])
 project=MOD/'Civ Supply Chains.civ6proj';xml=project.read_text(encoding='utf-8-sig');content=[]
 for p in payload:
  rel=str(p.relative_to(STAGE)).replace('/','\\')
  if f'Include="{rel}"' not in xml:content.append(f'    <Content Include="{rel}">\n      <SubType>Content</SubType>\n    </Content>\n')
 if content:save(project,xml.replace('  <Import Project=', '  <ItemGroup>\n'+''.join(content)+'  </ItemGroup>\n  <Import Project=',1).encode())
 # Read latest cache at the last moment; preserve every unrelated record.
 raw=CACHE.read_bytes();cache=json.loads(raw.decode('utf-8-sig'));records={e['Filename'].replace('\\','/'):e for e in cache['Files']}
 types={'.ast':0,'.mtl':1,'.geo':2,'.tex':3,'.anm':4}
 for key,root in descriptors.items():
  path=ROOT/key;record={'Filename':key,'Timestamp':int(path.stat().st_mtime*10000000)+116444736000000000,'Status':0,'Type':2,'EntityType':types[path.suffix],'EntityClass':root.find('m_ClassName').get('text'),'Filesize':path.stat().st_size,'Tags':[e.get('text') for e in root.findall('m_Tags/Element')],'Stats':{}}
  if key in records:records[key].update(record)
  else:cache['Files'].append(record)
  cache['Dependencies'][key]=deps[key]
 cache['Timestamp']=int(time.time()*10000000)+116444736000000000
 assert CACHE.read_bytes()==raw,'AssetCloud changed during registration; rerun to merge safely.'
 save(CACHE,json.dumps(cache,separators=(',',':')).encode())
 E.parse(xlp);E.parse(project)
 assert all((MOD/p.relative_to(STAGE)).read_bytes()==p.read_bytes() for p in payload)
 report.update(installed=True,backup=str(backup),registered_in_assetcloud=True)
(OUT/'asset-package-check.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:report[k] for k in ('assets','installed','ae_playback_verified')},indent=2))
