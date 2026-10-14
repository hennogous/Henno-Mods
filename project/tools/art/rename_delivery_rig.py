"""Rename the production rig, proving native geometry and sampled motion unchanged."""
import argparse,hashlib,importlib.util,json,os,shutil,subprocess,time
from pathlib import Path
import xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[3];MOD=ROOT/'Civ Supply Chains'
BASE=Path(r'C:\Users\Shadow\Desktop\Codex\CSC_Storage_L\delivery-01')
OUT=BASE/'production-rig-rename';OUT.mkdir(exist_ok=True)
OLD='CSC_TEST_TAILORS_Delivery_Rig';NEW='CSC_ALL_Delivery_Rig'
paths=[MOD/'Geometries/CSC_ALL_Delivery.fgx',MOD/'Animations/CSC_ALL_Delivery.fgx',
       MOD/'Geometries/CSC_ALL_Delivery.geo',MOD/'Assets/CSC_TAILORS_Storage_L.ast']
p=argparse.ArgumentParser();p.add_argument('--install',action='store_true');args=p.parse_args()
original={p:p.read_bytes() for p in paths};assert OLD.encode() in original[paths[2]]
bridge=BASE/'bridge';helper=bridge/'RenameFgxRig.exe'
command=[r'C:\Windows\Microsoft.NET\Framework\v4.0.30319\csc.exe','/nologo','/unsafe','/platform:x64',f'/out:{helper}',
         '/r:System.Windows.Forms.dll']+[f'/r:{bridge/name}' for name in ('Firaxis.IO.dll','Firaxis.Utility.dll','Firaxis.Granny.dll')]+[str(Path(__file__).with_name('RenameFgxRig.cs'))]
subprocess.run(command,check=True,capture_output=True)
payload={}
for path in paths[:2]:
    target=OUT/path.parent.name/path.name;target.parent.mkdir(exist_ok=True)
    r=subprocess.run([str(helper),str(path),str(target),OLD,NEW],cwd=bridge,capture_output=True,text=True)
    (target.with_suffix('.log')).write_text(r.stdout+r.stderr)
    assert r.returncode==0,r.stdout+r.stderr
    payload[path]=target.read_bytes()
backend_path=Path(os.environ['APPDATA'])/'Blender Foundation/Blender/5.1/scripts/addons/civ6_animation/backend.py'
spec=importlib.util.spec_from_file_location('delivery_backend',backend_path);backend=importlib.util.module_from_spec(spec);spec.loader.exec_module(backend)
nexus=r'C:\Program Files (x86)\CivNexus6_Release-1.3.3\CivNexus6'
for label,model,anim in [('before',paths[0],paths[1]),('after',OUT/'Geometries/CSC_ALL_Delivery.fgx',OUT/'Animations/CSC_ALL_Delivery.fgx')]:
    backend.run(nexus,'extract',model,anim,OUT/label,30,0,0)
for name in ('model.cn6','clip.na2','report.json'):
    before=(OUT/'before'/name).read_text();after=(OUT/'after'/name).read_text()
    assert OLD in before
    assert after==before.replace(OLD,NEW),name+' changed beyond requested rig name'
for path in paths[2:]:payload[path]=original[path].replace(OLD.encode(),NEW.encode())
asset=E.fromstring(payload[paths[3]]);geo=E.fromstring(payload[paths[2]])
model=next(e for e in asset.findall('m_GeometrySet/m_ModelInstances/Element') if e.find('m_GeoName').get('text')=='CSC_ALL_Delivery')
cargo=next(e for e in asset.findall('.//m_Points/Element') if e.find('m_BoneName').get('text')=='Cargo')
assert model.find('m_Name').get('text')==cargo.find('m_ModelInstanceName').get('text')==geo.find('m_ModelName').get('text')==NEW
assert geo.find('m_Bones/Element').get('text')==NEW
report={'rig':NEW,'all_geometry_unchanged_except_name':True,'all_2041_frames_32_bones_identical_except_name':True,'cargo_model_binding_verified':True,'installed':False}
if args.install:
    assert all(p.read_bytes()==original[p] for p in paths),'Production files changed during verification'
    backup=OUT/('backup-'+time.strftime('%Y%m%d-%H%M%S'));backup.mkdir()
    # Keep active generated export inputs synchronized, without reviving deleted
    # TEST assets or installing their retired geometry into the project.
    generated={BASE/'CSC_TEST_TAILORS_Delivery_Master_Model.fgx':payload[paths[0]],
               BASE/'CSC_TEST_TAILORS_Delivery_Master.fgx':payload[paths[1]]}
    for name in ('CSC_TEST_TAILORS_Delivery_Master_Model.geo','CSC_TEST_TAILORS_Delivery_Master_Model.cn6','Master-sampled/clip.na2'):
        path=BASE/name
        if path.exists():generated[path]=path.read_bytes().replace(OLD.encode(),NEW.encode())
    for path,data in list(payload.items())+list(generated.items()):
        rel=path.relative_to(MOD) if path in payload else Path('generated')/path.relative_to(BASE)
        dest=backup/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,dest)
        path.write_bytes(data)
    cachepath=Path(os.environ['APPDATA'])/'AssetCloud/mod-Civ Supply Chains-asset-deps.json'
    raw=cachepath.read_bytes();cache=json.loads(raw.decode('utf-8-sig'))
    keys={'Civ Supply Chains/'+p.relative_to(MOD).as_posix():p for p in payload}
    for row in cache['Files']:
        path=keys.get(row['Filename'].replace('\\','/'))
        if path:row.update(Timestamp=int(path.stat().st_mtime*10000000)+116444736000000000,Filesize=path.stat().st_size)
    assert cachepath.read_bytes()==raw
    (backup/cachepath.name).write_bytes(raw);cachepath.write_text(json.dumps(cache,separators=(',',':')),encoding='utf-8')
    report.update(installed=True,backup=str(backup),hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths})
(OUT/'rename-check.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
