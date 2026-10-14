"""Install the verified added attachment bone and cargo clip; preserve the AST."""
import hashlib,json,os,re,shutil,time
from pathlib import Path
import xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[3];MOD=ROOT/'Civ Supply Chains'
BASE=Path(r'C:\Users\Shadow\Desktop\Codex\CSC_Storage_L');DEL=BASE/'delivery-01';OUT=BASE/'delivery-reset-20261010'
check=json.loads((DEL/'native-check.json').read_text())
assert check['combined_donkey'] and check['master_clip']['duration']==68
assert max(check['master_vertex_errors'].values())<.2 and check['donkey_error_at_previous_scale']<.4
assert max(v for row in check['attachment_matrix_errors'].values() for v in row.values())<.08
for name in ('native-hidden-reset-check.json','native-sack-hidden-reset-check.json'):
 report=json.loads((OUT/name).read_text());assert not report['slide_collisions'] and not report['visible_drop_frames']
assert not json.loads((OUT/'tip-clearance-check.json').read_text())['collisions']
asset=MOD/'Assets/CSC_TAILORS_Storage_L.ast';asset_bytes=asset.read_bytes()
geo=MOD/'Geometries/CSC_ALL_Delivery.geo';original=geo.read_bytes();prod=E.fromstring(original)
new=E.parse(DEL/'CSC_TEST_TAILORS_Delivery_Master_Model.geo').getroot()
bones=[e.get('text') for e in new.findall('m_Bones/Element')]
assert [b for b in bones if b!='Cargo_TipUpright']==[e.get('text') for e in prod.findall('m_Bones/Element')]
assert new.find('m_ModelName').get('text')==prod.find('m_ModelName').get('text')=='CSC_ALL_Delivery_Rig'
def tree_value(node):
 return (node.tag,dict(node.attrib),(node.text or '').strip(),[tree_value(c) for c in node])
assert tree_value(new.find('m_Meshes'))==tree_value(prod.find('m_Meshes'))
replacement=b'<m_Bones>\n'+b''.join(('\t\t<Element text="'+b+'"/>\n').encode() for b in bones)+b'\t</m_Bones>'
updated,count=re.subn(rb'<m_Bones>[\s\S]*?</m_Bones>',replacement,original);assert count==1
payload={geo:updated,MOD/'Geometries/CSC_ALL_Delivery.fgx':(DEL/'CSC_TEST_TAILORS_Delivery_Master_Model.fgx').read_bytes(),
 MOD/'Animations/CSC_ALL_Delivery.fgx':(DEL/'CSC_TEST_TAILORS_Delivery_Master.fgx').read_bytes()}
backup=OUT/('production-backup-'+time.strftime('%Y%m%d-%H%M%S'));backup.mkdir()
for target in list(payload)+[asset,MOD/'Animations/CSC_ALL_Delivery.anm']:
 dest=backup/target.relative_to(MOD);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(target,dest)
for target,data in payload.items():target.write_bytes(data)
assert asset.read_bytes()==asset_bytes
anm=MOD/'Animations/CSC_ALL_Delivery.anm';os.utime(anm,None)
cachepath=Path(os.environ['APPDATA'])/'AssetCloud/mod-Civ Supply Chains-asset-deps.json'
raw=cachepath.read_bytes();cache=json.loads(raw.decode('utf-8-sig'))
keys={'Civ Supply Chains/'+p.relative_to(MOD).as_posix():p for p in list(payload)+[anm]}
for row in cache['Files']:
 p=keys.get(row['Filename'].replace('\\','/'))
 if p:row.update(Timestamp=int(p.stat().st_mtime*10000000)+116444736000000000,Filesize=p.stat().st_size)
assert cachepath.read_bytes()==raw
(backup/cachepath.name).write_bytes(raw);cachepath.write_text(json.dumps(cache,separators=(',',':')),encoding='utf-8')
result={'installed':True,'backup':str(backup),'asset_preserved_sha256':hashlib.sha256(asset_bytes).hexdigest(),
 'files':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in payload},'bone_count':len(bones),'new_bone':'Cargo_TipUpright','retired_test_assets_reinstalled':False}
(OUT/'production-check.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
