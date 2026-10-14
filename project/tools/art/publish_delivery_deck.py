"""Install only the verified deck model; keep all clip/AST/descriptor bytes."""
import hashlib,json,os,shutil,time
from pathlib import Path
import xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[3];MOD=ROOT/'Civ Supply Chains'
BASE=Path(r'C:\Users\Shadow\Desktop\Codex\CSC_Storage_L');DEL=BASE/'delivery-01';OUT=BASE/'delivery-deck-20261010'
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
check=json.loads((DEL/'native-check.json').read_text());repair=json.loads((OUT/'deck-repair-check.json').read_text())
assert check['combined_donkey'] and check['master_clip']['duration']==68
assert max(check['master_vertex_errors'].values())<.2 and check['donkey_error_at_previous_scale']<.4
assert max(v for row in check['attachment_matrix_errors'].values() for v in row.values())<.08
assert json.loads((OUT/'deck-validation.json').read_text())['maximum_yaw_error_degrees']<.15
assert digest(DEL/'CSC_TEST_TAILORS_Delivery_Master.fgx')==digest(MOD/'Animations/CSC_ALL_Delivery.fgx')==repair['clip_sha256']
assert not json.loads((DEL/'storage-clearance-check.json').read_text())['building_surface_intersections']
geo=MOD/'Geometries/CSC_ALL_Delivery.geo';src=E.parse(DEL/'CSC_TEST_TAILORS_Delivery_Master_Model.geo').getroot();dst=E.parse(geo).getroot()
def value(node):return (node.tag,dict(node.attrib),(node.text or '').strip(),[value(c) for c in node])
for tag in ('m_Meshes','m_Bones','m_ModelName'):assert value(src.find(tag))==value(dst.find(tag)),tag
preserved=[geo,MOD/'Assets/CSC_TAILORS_Storage_L.ast',MOD/'Animations/CSC_ALL_Delivery.fgx',MOD/'Animations/CSC_ALL_Delivery.anm']
before={str(p):digest(p) for p in preserved}
target=MOD/'Geometries/CSC_ALL_Delivery.fgx';backup=OUT/('production-backup-'+time.strftime('%Y%m%d-%H%M%S'));backup.mkdir()
shutil.copy2(target,backup/target.name)
target.write_bytes((DEL/'CSC_TEST_TAILORS_Delivery_Master_Model.fgx').read_bytes());os.utime(geo,None)
cachepath=Path(os.environ['APPDATA'])/'AssetCloud/mod-Civ Supply Chains-asset-deps.json';raw=cachepath.read_bytes();cache=json.loads(raw.decode('utf-8-sig'))
paths={'Civ Supply Chains/'+p.relative_to(MOD).as_posix():p for p in (target,geo)}
for row in cache['Files']:
 p=paths.get(row['Filename'].replace('\\','/'))
 if p:row.update(Timestamp=int(p.stat().st_mtime*10000000)+116444736000000000,Filesize=p.stat().st_size)
assert cachepath.read_bytes()==raw
(backup/cachepath.name).write_bytes(raw);cachepath.write_text(json.dumps(cache,separators=(',',':')),encoding='utf-8')
assert before=={str(p):digest(p) for p in preserved}
report={'installed':True,'backup':str(backup),'preserved':before,'model_sha256':digest(target),'retired_test_assets_reinstalled':False}
(OUT/'production-check.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
