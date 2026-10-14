"""Install a checked topology-only repair; preserve every animation and user AST."""
import hashlib,json,os,re,shutil,time
from pathlib import Path
import xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[3];MOD=ROOT/'Civ Supply Chains'
OUT=Path(r'C:\Users\Shadow\Desktop\Codex\CSC_Storage_L\delivery-01')
check=json.loads((OUT/'native-check.json').read_text())
repair=json.loads((OUT/'runner-repair-check.json').read_text())
assert check['combined_donkey'] and check['master_clip']['duration']==68
assert max(check['master_vertex_errors'].values())<.2 and check['donkey_error_at_previous_scale']<.4
assert max(v for r in check['attachment_matrix_errors'].values() for v in r.values())<.08
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert digest(OUT/'CSC_TEST_TAILORS_Delivery_Master.fgx')==repair['clip_sha256']
assert digest(MOD/'Animations/CSC_ALL_Delivery.fgx')==repair['clip_sha256']
preserve=[MOD/'Assets/CSC_TAILORS_Storage_L.ast',MOD/'Animations/CSC_ALL_Delivery.fgx',MOD/'Animations/CSC_ALL_Delivery.anm']
preserved={str(p):digest(p) for p in preserve}
source=OUT/'CSC_TEST_TAILORS_Delivery_Master_Model.geo';source_root=E.parse(source).getroot()
targets=[MOD/'Geometries/CSC_ALL_Delivery.geo',MOD/'Geometries/CSC_TEST_TAILORS_Delivery_Master_Model.geo']
payload={};differences={}
def structure(element):
    return (element.tag,element.attrib,(element.text or '').strip(),[structure(c) for c in element])
for target in targets:
    raw=target.read_bytes();root=E.fromstring(raw)
    assert [b.get('text') for b in root.findall('m_Bones/Element')]==[b.get('text') for b in source_root.findall('m_Bones/Element')]
    assert root.find('m_ModelName').get('text')==source_root.find('m_ModelName').get('text')
    existing=root.findall('m_Meshes/Element');new=source_root.findall('m_Meshes/Element')
    assert len(existing)==len(new)
    changes=[]
    for a,b in zip(existing,new):
        name=a.find('m_Name').get('text');assert name==b.find('m_Name').get('text')
        assert a.findtext('m_nBoundBoneCount')==b.findtext('m_nBoundBoneCount')
        assert [e.get('text') for e in a.findall('m_Groups/Element/m_Name')]==[e.get('text') for e in b.findall('m_Groups/Element/m_Name')]
        if name!='CSC_ALL_Delivery_Donkey':
            assert structure(a)==structure(b)
            continue
        for xpath in ('m_nVertexCount','m_nPrimitiveCount','m_Groups/Element/m_nPrims'):
            old=int(a.findtext(xpath));updated=int(b.findtext(xpath))
            # Twelve source vertices are restored; the measured native output
            # additionally has six more seam-split vertices than the old export.
            assert (old,updated)==((490,508) if xpath=='m_nVertexCount' else (414,426)),(xpath,old,updated)
            changes.append((xpath,old,updated))
        # Replace only this mesh block. Keep all production geometry metadata.
        start=re.search(rb'<Element>\s*<m_Name text="CSC_ALL_Delivery_Donkey"',raw).start()
        end=raw.index(b'</m_Meshes>',start)
        block=raw[start:end]
        for xpath,old,updated in changes:
            tag=xpath.split('/')[-1]
            old_value=f'<{tag}>{old}</{tag}>'.encode();new_value=f'<{tag}>{updated}</{tag}>'.encode()
            assert block.count(old_value)==1
            block=block.replace(old_value,new_value)
        raw=raw[:start]+block+raw[end:]
    assert len(changes)==3
    payload[target]=raw
    payload[target.with_suffix('.fgx')]=(OUT/'CSC_TEST_TAILORS_Delivery_Master_Model.fgx').read_bytes()
    differences[str(target)]=changes
backup=OUT/('runner-install-backup-'+time.strftime('%Y%m%d-%H%M%S'));backup.mkdir()
cache_path=Path(os.environ['APPDATA'])/'AssetCloud/mod-Civ Supply Chains-asset-deps.json'
cache_raw=cache_path.read_bytes();cache=json.loads(cache_raw.decode('utf-8-sig'))
for target in payload:
    dest=backup/target.parent.name/target.name;dest.parent.mkdir(exist_ok=True);shutil.copy2(target,dest)
for target,data in payload.items():target.write_bytes(data)
changed={'Civ Supply Chains/'+p.relative_to(MOD).as_posix():p for p in payload}
for row in cache['Files']:
    p=changed.get(row['Filename'].replace('\\','/'))
    if p:row.update(Timestamp=int(p.stat().st_mtime*10000000)+116444736000000000,Filesize=p.stat().st_size)
assert cache_path.read_bytes()==cache_raw,'AssetCloud changed during update'
(backup/cache_path.name).write_bytes(cache_raw);cache_path.write_text(json.dumps(cache,separators=(',',':')),encoding='utf-8')
assert preserved=={str(p):digest(p) for p in preserve}
report={'installed':True,'backup':str(backup),'preserved':preserved,'descriptor_changes':differences,'files':{str(p):digest(p) for p in payload}}
(OUT/'runner-install-check.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
