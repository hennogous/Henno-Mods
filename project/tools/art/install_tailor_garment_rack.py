"""Validate and install the extracted Tailor clothing rack; preserve AE assemblies."""
from pathlib import Path
import hashlib
import json
import os
import re
import shutil
import sys
import time
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[3]
MOD=ROOT/'Civ Supply Chains'
OUT=Path(r'C:\Users\Shadow\Desktop\Codex\Tailor-wall-garment-rack-20261013')
ID='CSC_TAILORS_Tailor_Garment_Rack'
CACHE=Path(os.environ['APPDATA'])/'AssetCloud/mod-Civ Supply Chains-asset-deps.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def text(node,path):
    value=node.find(path)
    return value.get('text',value.text or '') if value is not None else ''
def parse(p):
    chunks=p.read_text().split('mesh:"'); assert len(chunks)==2
    name,body=chunks[1].split('"',1)
    _,body=body.split('vertices\n',1)
    vertices,body=body.split('triangles\n',1)
    return name,[[float(x) for x in l.split()[:18]] for l in vertices.strip().splitlines()],[[int(x) for x in l.split()] for l in body.split('\nend')[0].strip().splitlines()]

def register_cache():
    raw=CACHE.read_bytes();cache=json.loads(raw.decode('utf-8-sig'))
    index={(Path(r['Filename']).suffix.lower(),Path(r['Filename'].replace('\\','/')).stem.casefold()):r['Filename'].replace('\\','/') for r in cache['Files']}
    for p in MOD.rglob('*'):
        if p.is_file() and p.suffix in ('.mtl','.geo','.tex','.ast'):
            index[(p.suffix,p.stem.casefold())]=p.relative_to(ROOT).as_posix()
    records={r['Filename'].replace('\\','/'):r for r in cache['Files']}
    for folder,ext,entity_type in [('Assets','.ast',0),('Geometries','.geo',2)]:
        p=MOD/folder/(ID+ext);root=ET.parse(p).getroot();key=p.relative_to(ROOT).as_posix()
        deps=set()
        for n in root.findall('.//m_GeoName'):
            deps.add(index[('.geo',n.get('text').casefold())])
        for n in root.findall('.//Element'):
            name=text(n,'m_ObjectName');kind=text(n,'m_eObjectType')
            if name and kind in ('MATERIAL','TEXTURE'):
                deps.add(index[('.mtl' if kind=='MATERIAL' else '.tex',name.replace('\\','/').split('/')[-1].casefold())])
        for n in root.findall('.//m_DataFiles/Element/m_RelativePath'):
            deps.add((p.parent/n.get('text')).relative_to(ROOT).as_posix())
        record=dict(Filename=key,Timestamp=int(p.stat().st_mtime*10000000)+116444736000000000,
                    Status=0,Type=2,EntityType=entity_type,EntityClass=text(root,'m_ClassName'),
                    Filesize=p.stat().st_size,Tags=[],Stats={})
        if key in records:records[key].update(record)
        else:cache['Files'].append(record)
        cache['Dependencies'][key]=sorted(deps)
    backup=OUT/('assetcloud-before-'+time.strftime('%H%M%S')+'.json')
    backup.write_bytes(raw)
    assert CACHE.read_bytes()==raw,'AssetCloud changed; retry with latest cache'
    cache['Timestamp']=int(time.time()*10000000)+116444736000000000
    CACHE.write_text(json.dumps(cache,separators=(',',':')))
    print('AssetCloud registered: '+ID)

def main():
    if '--register-cache' in sys.argv:return register_cache()
    validation=json.loads((OUT/'saved-validation.json').read_text());assert validation['automated_pass']
    a,va,ta=parse(OUT/(ID+'.cn6'));b,vb,tb=parse(OUT/(ID+'-roundtrip.cn6'))
    assert a==b==ID and len(va)==len(vb)==312 and ta==tb
    errors=[max(abs(x[i]-y[i]) for x,y in zip(va,vb)) for i in range(18)]
    assert max(errors)<1e-4,errors
    ast=ET.parse(OUT/(ID+'.ast')).getroot();geo=ET.parse(OUT/(ID+'.geo')).getroot()
    assert text(ast,'m_ClassName')=='TileBase' and text(geo,'m_ClassName')=='LandmarkModel'
    assert len(ast.findall('m_GeometrySet/m_ModelInstances/Element'))==1
    assert len(geo.findall('m_Meshes/Element'))==1
    rows=ast.findall('.//m_GroupStates/Element');assert len(rows)==5
    for row in rows:
        visible=next(n.find('m_bValue').text for n in row.findall('m_Values/m_Values/Element') if text(n,'m_ParamName')=='Visible')
        assert visible==str(text(row,'m_StateName') in ('Worked','Unworked')).lower()
        assert text(row,'m_MeshName')==ID
    protected={p:sha(p) for p in (MOD/'Assets').glob('*.ast') if p.stem!=ID}
    backup=OUT/'before-install';backup.mkdir(exist_ok=True)
    files=[]
    for folder,ext in [('Assets','.ast'),('Geometries','.geo'),('Geometries','.fgx')]:
        dest=MOD/folder/(ID+ext);source=OUT/(ID+ext)
        assert not dest.exists() or sha(dest)==sha(source), 'Asset already differs; inspect before replacing'
        files.append((source,dest))
    xlp=MOD/'XLPs/CSC_Tilebases.xlp';raw=xlp.read_bytes()
    insert=('\t\t<Element>\n\t\t\t<m_EntryID text="'+ID+'"/>\n\t\t\t<m_ObjectName text="'+ID+'"/>\n\t\t</Element>\n').encode()
    assert raw.count(b'\t</m_Entries>')==1
    updated=raw if ID.encode() in raw else raw.replace(b'\t</m_Entries>',insert+b'\t</m_Entries>')
    ET.fromstring(updated)
    if not (backup/xlp.name).exists():shutil.copy2(xlp,backup/xlp.name)
    for source,dest in files:
        if not dest.exists():shutil.copy2(source,dest)
    if raw!=updated:xlp.write_bytes(updated)
    # Existing XLP owns packaging; no duplicate ModBuddy Content rows are needed.
    assert all(sha(p)==s for p,s in protected.items())
    assert all(sha(source)==sha(dest) for source,dest in files)
    entries=ET.parse(xlp).findall('m_Entries/Element')
    assert sum(text(e,'m_EntryID')==ID for e in entries)==1
    report=dict(asset_id=ID,installed=True,files=[str(d) for s,d in files],
        xlp=str(xlp),native_readback_max_error=max(errors),vertices=len(va),triangles=len(ta),
        authoring_validation_pass=True,existing_ae_assemblies_unchanged=len(protected),
        visible_states=['Worked','Unworked'],hidden_states=['Construction','Pillaged','Unbuilt'],
        cook_tested=False,in_game_tested=False)
    (OUT/'install-report.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
