"""Publish the verified coordinated atlas/UV/animated-asset update with rollback."""
import json,sys,os,shutil,time,hashlib,copy
from pathlib import Path
import numpy as np
from PIL import Image
import xml.etree.ElementTree as E
from windmill_tower_integrate import ROOT,MOD,ART,NAME,OLD,AO,MATS
from windmill_tower_integrate import read_xml,txt,Resolver,Assembly,DEFAULT_SDK
OUT=Path(sys.argv[1]);STAGE=OUT/'staged'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def pixels(path,scalar=False):
    a=np.asarray(Image.open(path).convert('RGBA'));return a[:,:,:1] if scalar else a[:,:,:3]

assert json.loads((OUT/'tower-source-validation.json').read_text())['error_count']==0
assert len(json.loads((OUT/'native-migration-validation.json').read_text()))==9
assert len(json.loads((OUT/'source-migration-validation.json').read_text()))==12
assert json.loads((OUT/'native-animation-validation.json').read_text())['frames_checked']==301
assert json.loads((OUT/'sail-clearance.json').read_text())=={}
baseline=json.loads((OUT/'integration-baseline.json').read_text())
assert all(sha(Path(p))==h for p,h in baseline.items()),'AE assembly/XLP changed during final review'
for name,record in json.loads((OUT/'atlas-consumers.json').read_text())['geometries'].items():
    assert sha(MOD/f'Geometries/{name}.fgx')==record['native_hash'],name+' changed since audit'
layout=json.loads((OUT/'atlas-migration.json').read_text());checks={}
for old in (OUT/'before-textures').glob('*'):
    assert sha(ART/'Textures'/old.name)==sha(old),'Canonical texture changed: '+old.name
    name=old.stem;scalar=name.rsplit('_',1)[1] in ['G','M','O']
    a=pixels(MOD/'Textures'/(name+'.dds'),scalar);b=pixels(STAGE/'Textures'/(name+'.dds'),scalar)
    assert np.array_equal(a[:512],b[:512]) and np.array_equal(a[512:,:512],b[512:,:512]),name+' other quadrants changed'
    desired=pixels(OUT/'staged-textures'/(name+'.png'),scalar);assert np.array_equal(b,desired),name+' DDS pixels changed'
    checks[name]={'other_three_quadrants_unchanged':True,'runtime_top_mip_matches_staging':True}
for name in ['CSC_Atlas_B_BAKERS','CSC_Atlas_B_BAKERS_2','CSC_Atlas_B_TAILORS','CSC_Atlas_B_TAILORS_2']:
    assert sha(ART/'Textures'/(name+'.xcf'))==sha(OUT/'before-xcf'/(name+'.xcf'))
    a=pixels(OUT/'staged-xcf'/(name+'-composite.png'));b=pixels(OUT/'staged-textures'/(name+'.png'))
    assert np.array_equal(a[512:,512:],b[512:,512:]) and np.max(abs(a.astype(int)-b.astype(int)))<=1
    old=pixels(OUT/'before-textures'/(name+'.dds'))
    for r in layout['regions']:
        x,y,x1,y1=r['source'];u,v,u1,v1=r['destination'];assert np.array_equal(old[y:y1,x:x1],b[v:v1,u:u1]),(name,r['id'])
resolver=Resolver(MOD,DEFAULT_SDK)
for p in STAGE.rglob('*'):
    if p.suffix in ['.ast','.geo','.fgx','.dds','.tex','.mtl','.anm']:resolver.index[p.name.casefold()]={p}
state_checks=[]
for state in ['Worked','Unworked','Construction','Pillaged','Unbuilt']:
    assembly=Assembly(resolver,state);key=assembly.asset(STAGE/f'Assets/{NAME}.ast');model=assembly.assets[key]['models'][0]
    assert len(model['groups'])==(3 if state in ['Worked','Unworked'] else 0),(state,model)
    state_checks.append({'state':state,'visible_groups':len(model['groups'])})
for suffix in ['', '_2']:
    before=(OUT/f'before/Assets/CSC_BAKERS_Wind_Mill{suffix}.ast').read_bytes();after=(STAGE/f'Assets/CSC_BAKERS_Wind_Mill{suffix}.ast').read_bytes()
    assert after==before.replace(OLD.encode(),NAME.encode())

payload={}
for p in STAGE.rglob('*'):
    if p.suffix not in ['.ast','.geo','.fgx','.dds','.tex','.mtl','.anm']:continue
    if p.suffix=='.tex' and p.stem.startswith('CSC_Atlas_'):continue # Existing AE metadata remains byte-identical.
    payload[MOD/p.relative_to(STAGE)]=p.read_bytes()
for row in json.loads((OUT/'source-migration.json').read_text()):
    dest=Path(row['source']);assert sha(dest)==row['before_sha256'];payload[dest]=Path(row['staged']).read_bytes()
for row in json.loads((OUT/'source-cn6-migration.json').read_text()):
    dest=Path(row['source']);assert sha(dest)==sha(OUT/'before-sources'/dest.relative_to(ART));payload[dest]=Path(row['staged']).read_bytes()
for p in (OUT/'staged-xcf').glob('*.xcf'):payload[ART/'Textures'/p.name]=p.read_bytes()
for old in (OUT/'before-textures').glob('*'):
    new=(OUT/'staged-textures'/old.name) if old.suffix=='.png' else OUT/'canonical-dds'/old.name
    payload[ART/'Textures'/old.name]=new.read_bytes()
dest=ART/'BAKERS/Wind Mill/tower';assert not (dest/(NAME+'.blend')).exists(),'New master already exists'
for p in [OUT/'new-tower'/(NAME+'.blend'),STAGE/'Geometries'/(NAME+'.cn6'),OUT/'staged-textures'/(AO+'.png')]:payload[dest/p.name]=p.read_bytes()
for p in (STAGE/'Animations').glob('*'):
    if p.suffix in ['.fbx','.json']:payload[dest/p.name]=p.read_bytes()
generated=Path(layout['tower_plaster']['source']);payload[dest/'sources/Plaster_ImageGen.png']=generated.read_bytes()
payload[dest/'atlas-migration.json']=(OUT/'atlas-migration.json').read_bytes()
payload[ART/'Textures/Storage_Tower_v3_layout.json']=(OUT/'atlas-migration.json').read_bytes()
xlp=MOD/'XLPs/CSC_Tilebases.xlp';raw=xlp.read_bytes();assert NAME.encode() not in raw
insertion=f'<Element>\n      <m_EntryID text="{NAME}"/>\n      <m_ObjectName text="{NAME}"/>\n    </Element>\n  </m_Entries>'.encode()
payload[xlp]=raw.replace(b'</m_Entries>',insertion);E.fromstring(payload[xlp])
project=MOD/'Civ Supply Chains.civ6proj';raw=project.read_bytes()
new_runtime=[p for p in payload if p.is_relative_to(MOD) and not p.exists()]
items='\n  <ItemGroup>\n'+''.join('    <Content Include="'+str(p.relative_to(MOD))+'">\n      <SubType>Content</SubType>\n    </Content>\n' for p in new_runtime)+'  </ItemGroup>\n'
payload[project]=raw.replace(b'</Project>',items.encode()+b'</Project>');E.fromstring(payload[project])
protected={p:sha(p) for p in (MOD/'Assets').glob('*.ast') if p not in payload}
backup=OUT/'publication-backup';backup.mkdir(exist_ok=True);records=[]
for i,(path,data) in enumerate(payload.items()):
    entry={'destination':str(path),'before_sha256':sha(path) if path.exists() else None,'after_sha256':hashlib.sha256(data).hexdigest()}
    if path.exists():
        saved=backup/f'{i:03}-{path.name}';shutil.copy2(path,saved);entry['backup']=str(saved)
    records.append(entry)
(backup/'manifest.json').write_text(json.dumps(records,indent=2))
written=[]
try:
    for record,(path,data) in zip(records,payload.items()):
        assert (sha(path) if path.exists() else None)==record['before_sha256'],'File changed before publication: '+str(path)
        path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_name(path.name+'.windmill-tmp');tmp.write_bytes(data);os.replace(tmp,path);written.append(record)
except Exception:
    for record in reversed(written):
        path=Path(record['destination'])
        if 'backup' in record:shutil.copy2(record['backup'],path)
        elif path.exists():path.unlink()
    raise
assert all(sha(p)==h for p,h in protected.items())
(OUT/'publication-report.json').write_text(json.dumps({'installed':True,'files':records,'texture_checks':checks,'states':state_checks,'unrelated_AST_files_preserved':len(protected),'new_native_vertices':1982,'in_game_tested':False,'cook_tested':False},indent=2))
print('PUBLISHED',len(payload),'files; protected',len(protected),'unrelated AE assemblies; exact before/after backup manifest:',backup/'manifest.json',flush=True)
