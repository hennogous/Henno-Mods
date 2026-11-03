"""Add the verified new mill and Modern-era rows; retain exact prior project bytes in backups."""
import sys,json,shutil,hashlib,os
from pathlib import Path
import xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[4];MOD=ROOT/'Civ Supply Chains';OUT=Path(sys.argv[1]);NAME='CSC_BAKERS_Wind_Mill_Modern'
MASTER=Path.home()/'Desktop/Working Files/3D Art/BAKERS/Wind Mill/modern'
assert json.loads((OUT/'staging-validation.json').read_text())['passed']
assert json.loads((OUT/'source-validation.json').read_text())['error_count']==0
assert json.loads((OUT/'state-source-validation.json').read_text())['error_count']==0
assert json.loads((OUT/'cook-check/result.json').read_text())['exit_code']==0
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
payload={}
for p in (OUT/'staged').rglob('*'):
    if p.suffix not in ('.ast','.geo','.fgx','.mtl','.tex','.dds'):continue
    dest=MOD/p.relative_to(OUT/'staged');assert not dest.exists(),'New asset collision: '+str(dest)
    data=p.read_bytes()
    if p.suffix=='.tex':
        r=E.fromstring(data);r.find('m_SourceFilePath').set('text',str(MASTER/'textures'/(p.stem+'.png')));data=E.tostring(r,encoding='utf-8',xml_declaration=True)
    payload[dest]=data
assert not (MASTER/(NAME+'.blend')).exists(),'Master already exists'
for suffix in ('','_CON+PIL'):payload[MASTER/(NAME+suffix+'.blend')]=(OUT/(NAME+suffix+'.blend')).read_bytes()
for p in (OUT/'textures').glob(NAME+'*.png'):payload[MASTER/'textures'/p.name]=p.read_bytes()
for name in ('uv_contract.json','texture_provenance.json'):payload[MASTER/name]=(OUT/name).read_bytes()
source=Path(json.loads((OUT/'texture_provenance.json').read_text())['source']);payload[MASTER/'sources/ImageGen_Atlas.png']=source.read_bytes()
for p in (OUT/'staged/CN6').glob('*.cn6'):payload[MASTER/p.name]=p.read_bytes()
landmarks=MOD/'ArtDefs/CSC_Landmarks.artdef';raw=landmarks.read_bytes();assert NAME.encode() not in raw
additions=[]
for oldname,newname,oldasset,priority in [('01 Ancient: Wind Mill','06 Modern: Wind Mill','CSC_BAKERS_Wind_Mill',2),('01 Ancient: Wind Mill 2','06 Modern: Wind Mill 2','CSC_BAKERS_Wind_Mill_2',3)]:
    marker=f'<m_Name text="{oldname}"/>'.encode();assert raw.count(marker)==1
    idx=raw.index(marker);start=raw.rfind(b'\n'+b'\t'*6+b'<Element>',0,idx)
    end=raw.index(b'\n'+b'\t'*6+b'</Element>',idx)+len(b'\n'+b'\t'*6+b'</Element>')
    assert start>=0
    block=raw[start:end];E.fromstring(block.strip())
    clone=block.replace(b'<m_ElementName text="DEFAULT"/>',b'<m_ElementName text="ARTERA_MODERN"/>',1)
    clone=clone.replace(f'<m_EntryName text="{oldasset}"/>'.encode(),f'<m_EntryName text="{NAME}"/>'.encode())
    clone=clone.replace(marker,f'<m_Name text="{newname}"/>'.encode())
    clone=clone.replace(f'<m_nValue>{priority-2}</m_nValue>'.encode(),f'<m_nValue>{priority}</m_nValue>'.encode())
    E.fromstring(clone.strip());additions.append((end,clone))
patched=raw
for at,block in sorted(additions,reverse=True):patched=patched[:at]+block+patched[at:]
E.fromstring(patched);assert patched.count(NAME.encode())==2
payload[landmarks]=patched
xlp=MOD/'XLPs/CSC_Tilebases.xlp';raw=xlp.read_bytes();assert NAME.encode() not in raw
entry=f'<Element>\n      <m_EntryID text="{NAME}"/>\n      <m_ObjectName text="{NAME}"/>\n    </Element>\n  </m_Entries>'.encode()
payload[xlp]=raw.replace(b'</m_Entries>',entry);E.fromstring(payload[xlp])
project=MOD/'Civ Supply Chains.civ6proj';raw=project.read_bytes()
newfiles=[p for p in payload if p.is_relative_to(MOD) and not p.exists()]
items='\n  <ItemGroup>\n'+''.join('    <Content Include="'+str(p.relative_to(MOD))+'">\n      <SubType>Content</SubType>\n    </Content>\n' for p in newfiles)+'  </ItemGroup>\n'
payload[project]=raw.replace(b'</Project>',items.encode()+b'</Project>');E.fromstring(payload[project])
protected={str(p):sha(p) for p in (MOD/'Assets').glob('*.ast')}
backup=OUT/'publication-backup';backup.mkdir(exist_ok=True);records=[]
for i,(p,data) in enumerate(payload.items()):
    record={'destination':str(p),'before_sha256':sha(p) if p.exists() else None,'after_sha256':hashlib.sha256(data).hexdigest()}
    if p.exists():saved=backup/f'{i:03}-{p.name}';shutil.copy2(p,saved);record['backup']=str(saved)
    records.append(record)
(backup/'manifest.json').write_text(json.dumps(records,indent=2))
for record,(p,data) in zip(records,payload.items()):
    assert (sha(p) if p.exists() else None)==record['before_sha256'],'Concurrent edit: '+str(p)
    p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_name(p.name+'.modern-mill-tmp');tmp.write_bytes(data);os.replace(tmp,p)
assert all(sha(Path(p))==h for p,h in protected.items())
(OUT/'installation-report.json').write_text(json.dumps({'installed':True,'asset':NAME,'master':str(MASTER),'protected_existing_assets':len(protected),'era':'ARTERA_MODERN: Modern, Atomic, Information; Expansion era mappings inherited','modern_service_policy':'Both existing service states use this first modern prototype; gameplay and historical service assets unchanged','files':records,'in_game_tested':False},indent=2))
print('INSTALLED',NAME,'files',len(payload),'existing ASTs preserved',len(protected))
