"""Publish the coordinated smaller storage/crane and tested cargo fit."""
import hashlib,json,os,re,shutil,time
from pathlib import Path
import xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[3];MOD=ROOT/'Civ Supply Chains'
BASE=Path(r'C:\Users\Shadow\Desktop\Codex\CSC_Storage_L');OUT=BASE/'delivery-refit-20261009';DEL=BASE/'delivery-01'
parse=lambda p:E.fromstring(p.read_text().replace('AssetObjects:','AssetObjects..'))
check=json.loads((DEL/'native-check.json').read_text());author=json.loads((DEL/'authoring-check.json').read_text())
assert check['combined_donkey'] and check['master_clip']['duration']==68
assert max(check['master_vertex_errors'].values())<.2 and check['donkey_error_at_previous_scale']<.4
assert max(v for r in check['attachment_matrix_errors'].values() for v in r.values())<.08
assert author['body_scale']==1 and author['cargo_scale']==.8
assert json.loads((OUT/'building-validation.json').read_text())['automated_pass']
fit=json.loads((OUT/'cargo-fit-check.json').read_text());assert fit['selected_scale']==.8
assert not json.loads((DEL/'storage-clearance-check.json').read_text())['building_surface_intersections']
def identity(root):
 return {'bones':[b.get('text') for b in root.findall('m_Bones/Element')],
         'model':root.find('m_ModelName').get('text'),
         'meshes':[(m.find('m_Name').get('text'),[(g.find('m_Name').get('text')) for g in m.findall('m_Groups/Element')]) for m in root.findall('m_Meshes/Element')]}
for name,source in [('CSC_Storage_L',OUT/'CSC_Storage_L.geo'),('CSC_ALL_Delivery',DEL/'CSC_TEST_TAILORS_Delivery_Master_Model.geo')]:
 assert identity(parse(MOD/'Geometries'/(name+'.geo')))==identity(parse(source)),name+' binding identity changed'
oldgeo=parse(MOD/'Geometries/CSC_ALL_Delivery.geo');newgeo=parse(DEL/'CSC_TEST_TAILORS_Delivery_Master_Model.geo')
for a,b in zip(oldgeo.findall('m_Meshes/Element'),newgeo.findall('m_Meshes/Element')):
 for tag in ('m_nVertexCount','m_nPrimitiveCount','m_nBoundBoneCount'):assert a.findtext(tag)==b.findtext(tag),(tag,a.findtext(tag),b.findtext(tag))
asset=MOD/'Assets/CSC_TAILORS_Storage_L.ast';original=asset.read_bytes()
pattern=rb'(<m_BoneName text="Cargo"\s*/>[\s\S]*?<m_scale>)([^<]+)(</m_scale>)'
updated,count=re.subn(pattern,lambda m:m[1]+b'0.800000'+m[3],original)
assert count==1
payload={MOD/'Geometries/CSC_Storage_L.fgx':(OUT/'CSC_Storage_L.fgx').read_bytes(),
         MOD/'Geometries/CSC_Storage_L.geo':(OUT/'CSC_Storage_L.geo').read_bytes(),
         MOD/'Geometries/CSC_ALL_Delivery.fgx':(DEL/'CSC_TEST_TAILORS_Delivery_Master_Model.fgx').read_bytes(),
         MOD/'Animations/CSC_ALL_Delivery.fgx':(DEL/'CSC_TEST_TAILORS_Delivery_Master.fgx').read_bytes(),asset:updated}
backup=OUT/('production-backup-'+time.strftime('%Y%m%d-%H%M%S'));backup.mkdir()
for p in payload:
 dest=backup/p.relative_to(MOD);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
assert asset.read_bytes()==original,'AST changed during preparation'
for p,data in payload.items():p.write_bytes(data)
unchanged_descriptors=[MOD/'Geometries/CSC_ALL_Delivery.geo',MOD/'Animations/CSC_ALL_Delivery.anm']
for p in unchanged_descriptors:
 dest=backup/p.relative_to(MOD);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest);os.utime(p,None)
cachepath=Path(os.environ['APPDATA'])/'AssetCloud/mod-Civ Supply Chains-asset-deps.json'
raw=cachepath.read_bytes();cache=json.loads(raw.decode('utf-8-sig'))
keys={'Civ Supply Chains/'+p.relative_to(MOD).as_posix():p for p in list(payload)+unchanged_descriptors}
for row in cache['Files']:
 p=keys.get(row['Filename'].replace('\\','/'))
 if p:row.update(Timestamp=int(p.stat().st_mtime*10000000)+116444736000000000,Filesize=p.stat().st_size)
assert cachepath.read_bytes()==raw
(backup/cachepath.name).write_bytes(raw);cachepath.write_text(json.dumps(cache,separators=(',',':')),encoding='utf-8')
result={'installed':True,'backup':str(backup),'ast_only_change':'Cargo attachment scale to 0.8; other asset settings preserved',
        'files':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in payload},'retired_test_files_reinstalled':False}
(OUT/'production-refit-check.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
