"""Refresh only this delivery's AssetCloud entries and dependencies."""
import json,os,sys,time,copy
from pathlib import Path
from windmill_tower_integrate import ROOT,MOD,read_xml,txt,NAME
OUT=Path(sys.argv[1]);report=json.loads((OUT/'publication-report.json').read_text());assert report['installed']
CACHE=Path(os.environ['APPDATA'])/'AssetCloud/mod-Civ Supply Chains-asset-deps.json'
raw=CACHE.read_bytes();cache=json.loads(raw.decode('utf-8-sig'));records={r['Filename'].replace('\\','/'):r for r in cache['Files']}
index={(Path(k).suffix.lower(),Path(k).stem.casefold()):k for k in records}
for folder in ['Assets','Geometries','Animations','Materials','Textures']:
    for p in (MOD/folder).iterdir():
        if p.is_file():index[(p.suffix.lower(),p.stem.casefold())]=p.relative_to(ROOT).as_posix()
changed=[]
entity_types={'.ast':0,'.mtl':1,'.geo':2,'.tex':3,'.anm':4}
for item in report['files']:
    p=Path(item['destination'])
    if not p.is_relative_to(MOD) or p.suffix not in ['.ast','.geo','.fgx','.mtl','.tex','.dds','.anm']:continue
    key=p.relative_to(ROOT).as_posix();ext=p.suffix
    row=records.get(key)
    if row is None:
        row={'Filename':key,'Status':0,'Type':2 if ext in entity_types else (3 if ext=='.dds' else 4),'EntityType':entity_types.get(ext,12),'EntityClass':'','Tags':[],'Stats':{}}
        cache['Files'].append(row);records[key]=row
    row.update(Timestamp=int(p.stat().st_mtime*10000000)+116444736000000000,Filesize=p.stat().st_size)
    if ext in entity_types:
        root=read_xml(p);row['EntityClass']=txt(root,'m_ClassName');deps=set()
        for n in root.findall('.//m_GeoName'):
            deps.add(index[('.geo',n.get('text').casefold())])
        for n in root.findall('.//m_AnimationName'):
            if n.get('text'):deps.add(index[('.anm',n.get('text').casefold())])
        for n in root.findall('.//Element'):
            name=txt(n,'m_ObjectName');kind=txt(n,'m_eObjectType')
            if name and kind in ['MATERIAL','TEXTURE']:
                deps.add(index[('.mtl' if kind=='MATERIAL' else '.tex',name.replace('\\','/').split('/')[-1].casefold())])
            if txt(n,'m_ParamName')=='Asset':
                name=txt(n,'m_EntryName')
                if name:deps.add(index[('.ast',name.casefold())])
        for n in root.findall('.//m_DataFiles/Element/m_RelativePath'):deps.add((p.parent/n.get('text')).relative_to(ROOT).as_posix())
        cache['Dependencies'][key]=sorted(deps)
    changed.append(key)
assert CACHE.read_bytes()==raw,'AssetCloud changed while preparing focused refresh'
(OUT/'assetcloud-before.json').write_bytes(raw);cache['Timestamp']=int(time.time()*10000000)+116444736000000000
tmp=CACHE.with_name(CACHE.name+'.windmill-tmp');tmp.write_text(json.dumps(cache,separators=(',',':')),encoding='utf-8');os.replace(tmp,CACHE)
(OUT/'assetcloud-registration.json').write_text(json.dumps({'updated':changed,'new_asset':NAME,'animation_dependency_registered':True},indent=2))
print('AE browser refreshed:',len(changed),'files')
