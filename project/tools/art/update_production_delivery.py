"""Publish verified delivery binaries while preserving the user's production AST."""
import hashlib,json,os,shutil,time
from pathlib import Path
import xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[3];MOD=ROOT/'Civ Supply Chains'
OUT=Path(r'C:\Users\Shadow\Desktop\Codex\CSC_Storage_L\delivery-01')
check=json.loads((OUT/'native-check.json').read_text())
assert check['combined_donkey'] and check['master_clip']['duration']==68
assert max(check['master_vertex_errors'].values())<.2 and check['donkey_error_at_previous_scale']<.4
assert max(v for row in check['attachment_matrix_errors'].values() for v in row.values())<.08
assert json.loads((OUT/'authoring-check.json').read_text())['body_scale']==1.0
asset=MOD/'Assets/CSC_TAILORS_Storage_L.ast';asset_data=asset.read_bytes()
source_geo=E.parse(OUT/'CSC_TEST_TAILORS_Delivery_Master_Model.geo').getroot()
prod_geo=E.parse(MOD/'Geometries/CSC_ALL_Delivery.geo').getroot()
def meshes(root):
 return [(e.find('m_Name').get('text'),e.findtext('m_nVertexCount'),e.findtext('m_nPrimitiveCount'),e.findtext('m_nBoundBoneCount'),
          [(g.find('m_Name').get('text'),g.findtext('m_nPrims')) for g in e.findall('m_Groups/Element')]) for e in root.findall('m_Meshes/Element')]
assert meshes(source_geo)==meshes(prod_geo),'Geometry descriptor changed; update requires review of that difference'
assert [b.get('text') for b in source_geo.findall('m_Bones/Element')]==[b.get('text') for b in prod_geo.findall('m_Bones/Element')]
assert source_geo.find('m_ModelName').get('text')==prod_geo.find('m_ModelName').get('text')
assert b'CSC_ALL_Delivery_Donkey' in asset_data and b'<m_BoneName text="Cargo"' in asset_data
payload={MOD/'Geometries/CSC_ALL_Delivery.fgx':OUT/'CSC_TEST_TAILORS_Delivery_Master_Model.fgx',
 MOD/'Animations/CSC_ALL_Delivery.fgx':OUT/'CSC_TEST_TAILORS_Delivery_Master.fgx'}
backup=OUT/('production-update-backup-'+time.strftime('%Y%m%d-%H%M%S'));backup.mkdir()
for target,source in payload.items():
 dest=backup/target.parent.name/target.name;dest.parent.mkdir(exist_ok=True);shutil.copy2(target,dest)
 shutil.copy2(source,target)
assert asset.read_bytes()==asset_data,'Production asset changed during update'
cache_path=Path(os.environ['APPDATA'])/'AssetCloud/mod-Civ Supply Chains-asset-deps.json'
raw=cache_path.read_bytes();cache=json.loads(raw.decode('utf-8-sig'));changed={}
for target in payload:
 for path in (target,target.with_suffix('.geo' if target.parent.name=='Geometries' else '.anm')):
  if path not in payload:
   dest=backup/path.parent.name/path.name;shutil.copy2(path,dest);os.utime(path,None)
  changed['Civ Supply Chains/'+path.relative_to(MOD).as_posix()]=path
for row in cache['Files']:
 path=changed.get(row['Filename'].replace('\\','/'))
 if path:row.update(Timestamp=int(path.stat().st_mtime*10000000)+116444736000000000,Filesize=path.stat().st_size)
assert cache_path.read_bytes()==raw,'AssetCloud changed during metadata refresh'
(backup/cache_path.name).write_bytes(raw);cache_path.write_text(json.dumps(cache,separators=(',',':')),encoding='utf-8')
report={'installed':True,'asset_preserved_sha256':hashlib.sha256(asset_data).hexdigest(),'backup':str(backup),
 'native_files':{str(t):hashlib.sha256(t.read_bytes()).hexdigest() for t in payload},'descriptors_preserved':True}
(OUT/'production-update-check.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
