"""Stage/verify the production donkey mesh rename, preserving the cargo bone link."""
import argparse,hashlib,importlib.util,json,os,shutil,subprocess,time
from pathlib import Path
import xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[3];MOD=ROOT/'Civ Supply Chains'
OUT=Path(r'C:\Users\Shadow\Desktop\Codex\CSC_Storage_L\delivery-01\production-mesh-rename')
OLD='CSC_TEST_TAILORS_Donkey_Mesh';NEW='CSC_ALL_Delivery_Donkey'
GEO=MOD/'Geometries/CSC_ALL_Delivery.geo';FGX=GEO.with_suffix('.fgx')
AST=MOD/'Assets/CSC_TAILORS_Storage_L.ast';ANIM=MOD/'Animations/CSC_ALL_Delivery.fgx'
p=argparse.ArgumentParser();p.add_argument('--install',action='store_true');args=p.parse_args()
OUT.mkdir(exist_ok=True)
paths=[FGX,GEO,AST];original={p:p.read_bytes() for p in paths};anim_hash=hashlib.sha256(ANIM.read_bytes()).hexdigest()
if OLD.encode() not in original[GEO]:raise ValueError('Source mesh name missing; refusing to repeat rename')
helper=OUT.parent/'bridge/RenameFgxMesh.exe';target=OUT/FGX.name
subprocess.run([str(helper),str(FGX),str(target),OLD,NEW],cwd=helper.parent,check=True,capture_output=True)
backend_path=Path(os.environ['APPDATA'])/'Blender Foundation/Blender/5.1/scripts/addons/civ6_animation/backend.py'
spec=importlib.util.spec_from_file_location('delivery_backend',backend_path);backend=importlib.util.module_from_spec(spec);spec.loader.exec_module(backend)
nexus=r'C:\Program Files (x86)\CivNexus6_Release-1.3.3\CivNexus6'
for label,model in [('before',FGX),('after',target)]:backend.run(nexus,'extract',model,ANIM,OUT/label,30,0,0)
before=(OUT/'before/model.cn6').read_text();after=(OUT/'after/model.cn6').read_text()
assert before.count(OLD)==1
assert after==before.replace(OLD,NEW),'Native geometry, UV, skeleton or weights changed beyond mesh name'
assert (OUT/'before/clip.na2').read_bytes()==(OUT/'after/clip.na2').read_bytes(),'Animation sampling changed'
geodata=original[GEO].replace(OLD.encode(),NEW.encode());astdata=original[AST].replace(OLD.encode(),NEW.encode())
geo=E.fromstring(geodata);asset=E.fromstring(astdata)
models={e.find('m_Name').get('text'):e for e in asset.findall('m_GeometrySet/m_ModelInstances/Element')}
cargo=next(e for e in asset.findall('.//m_Points/Element') if e.find('m_BoneName').get('text')=='Cargo')
model=models[cargo.find('m_ModelInstanceName').get('text')]
assert model.find('m_GeoName').get('text')=='CSC_ALL_Delivery'
assert 'Cargo' in {e.get('text') for e in geo.findall('m_Bones/Element')}
assert all(e.get('text')!=OLD for e in asset.findall('.//m_MeshName'))
assert len([e for e in model.findall('.//m_MeshName') if e.get('text')==NEW])==5
(OUT/GEO.name).write_bytes(geodata);(OUT/AST.name).write_bytes(astdata)
report={'mesh':NEW,'geometry_content_unchanged_except_mesh_name':True,'all_animation_samples_identical':True,
 'cargo_binding':{'model_instance':cargo.find('m_ModelInstanceName').get('text'),'geometry':'CSC_ALL_Delivery','bone':'Cargo','scale':cargo.findtext('m_scale')},'cargo_binding_already_correct':True,'installed':False}
if args.install:
 for path in paths:assert path.read_bytes()==original[path],str(path)+' changed while preparing rename'
 backup=OUT/('backup-'+time.strftime('%Y%m%d-%H%M%S'));backup.mkdir()
 for path in paths:
  dest=backup/path.parent.name/path.name;dest.parent.mkdir(exist_ok=True);dest.write_bytes(original[path])
 # Existing dependency edges are unchanged; refresh metadata for changed entities.
 cachepath=Path(os.environ['APPDATA'])/'AssetCloud/mod-Civ Supply Chains-asset-deps.json'
 raw=cachepath.read_bytes();cache=json.loads(raw.decode('utf-8-sig'))
 for path,data in [(FGX,target.read_bytes()),(GEO,geodata),(AST,astdata)]:path.write_bytes(data)
 keys={'Civ Supply Chains/'+p.relative_to(MOD).as_posix():p for p in (GEO,AST)}
 for row in cache['Files']:
  key=row['Filename'].replace('\\','/')
  if key in keys:
   path=keys[key];row.update(Timestamp=int(path.stat().st_mtime*10000000)+116444736000000000,Filesize=path.stat().st_size)
 assert cachepath.read_bytes()==raw,'AssetCloud changed during rename; metadata refresh needs retry'
 (backup/cachepath.name).write_bytes(raw)
 cachepath.write_text(json.dumps(cache,separators=(',',':')),encoding='utf-8')
 report.update(installed=True,backup=str(backup))
assert hashlib.sha256(ANIM.read_bytes()).hexdigest()==anim_hash
(OUT/'rename-check.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
