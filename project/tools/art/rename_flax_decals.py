"""Guarded rename of the active flax decal assets and their material bindings."""
import contextlib,copy,hashlib,io,json,os,re,shutil,sys,time
from pathlib import Path
from lxml import etree as E
import audit_art_orphans as audit
from storage_pivot_trial import ROOT,MOD

OUT=Path('C:/Users/Shadow/Desktop/Codex/Flax-decal-rename-20261026')
ARCHIVE=Path('C:/Users/Shadow/Desktop/Archive/CSC-flax-decal-rename-20261026')
CACHE=Path(os.environ['APPDATA'])/'AssetCloud/mod-Civ Supply Chains-asset-deps.json'
OLD_MATERIAL='IMP_Farm_CSC_Flax_Decals'
NEW_MATERIAL='CSC_IMP_Farm_Flax_Decals'
TEXT_EXTS=audit.DESCRIPTORS|{'.xlp','.xml','.sql','.lua','.civ6proj','.modinfo','.dep'}

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2),encoding='utf-8')
def replacer(mapping):
    pattern=re.compile(rb'(?<![A-Za-z0-9_])(?:'+b'|'.join(re.escape(k.encode()) for k in sorted(mapping,key=len,reverse=True))+rb')(?![A-Za-z0-9_])')
    return lambda data:pattern.sub(lambda m:mapping[m.group().decode()].encode(),data)
def active_files():
    return [p for p in MOD.rglob('*') if p.is_file() and not any(x.lower() in {'archive','obj','bin','.git'} for x in p.relative_to(MOD).parts)]

def prepare():
    assert not OUT.exists();OUT.mkdir(parents=True)
    sources=sorted((MOD/'Assets').glob('IMP_Farm_CSC_Flax_Decal_*.ast'));assert len(sources)==16
    mapping={p.stem:p.stem.replace('IMP_Farm_CSC_Flax_','CSC_IMP_Farm_Flax_',1) for p in sources}
    mapping[OLD_MATERIAL]=NEW_MATERIAL;replace=replacer(mapping)
    for p in sources:assert not p.with_name(mapping[p.stem]+p.suffix).exists()
    old=audit.parse(MOD/'Materials'/(OLD_MATERIAL+'.mtl'));new=audit.parse(MOD/'Materials'/(NEW_MATERIAL+'.mtl'))
    old.find('m_Name').set('text',NEW_MATERIAL)
    assert E.tostring(old)==E.tostring(new),'Material settings differ; review before replacing'
    retired=['Materials/'+OLD_MATERIAL+'.mtl'];changes=[];files=active_files()
    baseline={p.relative_to(MOD).as_posix():sha(p) for p in files}
    for p in files:
        rel=p.relative_to(MOD).as_posix()
        if rel in retired or p.suffix.lower() not in TEXT_EXTS:continue
        data=p.read_bytes();updated=replace(data)
        if updated==data:continue
        dest=p.with_name(mapping[p.stem]+p.suffix) if p in sources else p
        target=OUT/'staged'/dest.relative_to(MOD);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(updated)
        if p.suffix.lower() not in {'.sql','.lua'}:audit.parse(target)
        changes.append(dict(old=rel,new=dest.relative_to(MOD).as_posix()))
    renamed=[c for c in changes if c['old']!=c['new']];assert len(renamed)==16
    assert any(c['new']=='XLPs/CSC_Tilebases.xlp' for c in changes)
    assert any(c['new']=='ArtDefs/CSC_Farms.artdef' for c in changes)
    with contextlib.redirect_stdout(io.StringIO()):audit.run(OUT/'audit-before',False)
    # Snapshot both packages without changing the live project or installed game.
    folders=set(audit.FOLDERS+['XLPs','ArtDefs'])
    for phase in ['before','after']:
        for p in files:
            rel=p.relative_to(MOD)
            if rel.parts[0] not in folders:continue
            if phase=='after' and (rel.as_posix() in retired or rel.as_posix() in {c['old'] for c in renamed}):continue
            dest=OUT/('cook-'+phase)/'pantry'/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
        if phase=='after':
            for p in (OUT/'staged').rglob('*'):
                if p.is_file():
                    dest=OUT/'cook-after/pantry'/p.relative_to(OUT/'staged');dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
    write(OUT/'plan.json',dict(mapping=mapping,changes=changes,retired=retired,baseline=baseline,cache_sha=sha(CACHE),material_settings_identical=True))
    print(json.dumps(dict(assets_renamed=len(renamed),updated_files=len(changes),references=[c['new'] for c in changes if c['old']==c['new']],retired=retired),indent=2))

def cook():
    import cleanup_art_orphans as c
    c.OUT=OUT;c.cook(sys.argv[2])

def publish():
    plan=json.loads((OUT/'plan.json').read_text());replace=replacer(plan['mapping'])
    assert not ARCHIVE.exists()
    for phase in ['before','after']:
        r=json.loads((OUT/('cook-'+phase)/'results/result.json').read_text());assert r['exit_code']==0 and r['blps']
    for rel,h in plan['baseline'].items():assert sha(MOD/rel)==h,('Source changed during preparation',rel)
    assert sha(CACHE)==plan['cache_sha'],'AE cache changed during preparation'
    raw=CACHE.read_bytes();cache=json.loads(raw.decode('utf-8-sig'));dead='Civ Supply Chains/Materials/'+OLD_MATERIAL+'.mtl'
    cache['Files']=[e for e in cache['Files'] if e['Filename'].replace('\\','/')!=dead]
    cache['Dependencies']={k:v for k,v in cache['Dependencies'].items() if k.replace('\\','/')!=dead}
    def rename_tree(obj):
        if isinstance(obj,str):return replace(obj.encode()).decode()
        if isinstance(obj,list):return [rename_tree(v) for v in obj]
        if isinstance(obj,dict):return {rename_tree(k):rename_tree(v) for k,v in obj.items()}
        return obj
    cache=rename_tree(cache);now=int(time.time()*1e7)+116444736000000000;cache['Timestamp']=now
    changed={c['new'] for c in plan['changes']}
    for e in cache['Files']:
        rel=e['Filename'].replace('\\','/').removeprefix('Civ Supply Chains/')
        if rel in changed:e.update(Timestamp=now,Filesize=(OUT/'staged'/rel).stat().st_size)
    for c in plan['changes']:
        if c['new'].startswith('Assets/'):
            key='Civ Supply Chains/'+c['new']
            assert len([e for e in cache['Files'] if e['Filename'].replace('\\','/')==key])==1,key
    assert any(e['Filename'].replace('\\','/')=='Civ Supply Chains/Materials/'+NEW_MATERIAL+'.mtl' for e in cache['Files'])
    ARCHIVE.mkdir(parents=True);backups={}
    for rel in sorted({c['old'] for c in plan['changes']}|set(plan['retired'])):
        src=MOD/rel;dst=ARCHIVE/'mod-before'/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
        assert sha(src)==sha(dst);backups[rel]=sha(dst)
    shutil.copy2(CACHE,ARCHIVE/'AssetCloud-before.json');write(ARCHIVE/'backup-manifest.json',backups)
    for c in plan['changes']:
        src=OUT/'staged'/c['new'];dst=MOD/c['new'];shutil.copy2(src,dst)
    for rel in plan['retired']+[c['old'] for c in plan['changes'] if c['old']!=c['new']]:
        p=(MOD/rel).resolve();assert p.is_relative_to(MOD.resolve()) and sha(p)==backups[rel];p.unlink()
    CACHE.write_text(json.dumps(cache,separators=(',',':')),encoding='utf-8')
    write(OUT/'installed.json',dict(archive=str(ARCHIVE),changes=plan['changes'],retired=plan['retired']))
    print('Installed 16 renamed flax assets, updated references and AE index; old duplicate material archived.')

def verify():
    plan=json.loads((OUT/'plan.json').read_text());replace=replacer(plan['mapping']);changed={c['old'] for c in plan['changes']}|set(plan['retired'])
    unchanged=0
    for rel,h in plan['baseline'].items():
        if rel not in changed:assert sha(MOD/rel)==h,rel;unchanged+=1
    for c in plan['changes']:
        p=MOD/c['new'];assert sha(p)==sha(OUT/'staged'/c['new'])
        assert p.read_bytes()==replace((ARCHIVE/'mod-before'/c['old']).read_bytes())
        if c['old']!=c['new']:
            assert not (MOD/c['old']).exists();r=audit.parse(p);assert r.find('m_Name').get('text')==p.stem
            names=[e.find('m_ObjectName').get('text') for e in r.findall('.//Element') if e.findtext('m_eObjectType')=='MATERIAL' and e.find('m_ParamName') is not None and e.find('m_ParamName').get('text')=='Material']
            assert NEW_MATERIAL in names and OLD_MATERIAL not in names,(p,names)
    for p in active_files():
        if p.suffix.lower() in TEXT_EXTS:assert replace(p.read_bytes())==p.read_bytes(),('Old identifier remains',p)
    assert not (MOD/'Materials'/(OLD_MATERIAL+'.mtl')).exists()
    before=audit.parse(ARCHIVE/'mod-before/XLPs/CSC_Tilebases.xlp');after=audit.parse(MOD/'XLPs/CSC_Tilebases.xlp')
    count=lambda r:len(r.findall('m_Entries/Element'))
    assert count(before)==count(after)
    ids=[e.get('text') for e in after.findall('.//m_EntryID')];assert len(ids)==len(set(ids))
    cache=json.loads(CACHE.read_text(encoding='utf-8-sig'));encoded=json.dumps(cache).encode();assert replace(encoded)==encoded
    for old,new in plan['mapping'].items():
        if old==OLD_MATERIAL:continue
        key='Civ Supply Chains/Assets/'+new+'.ast';deps=[p.replace('\\','/') for p in cache['Dependencies'][key]]
        assert 'Civ Supply Chains/Materials/'+NEW_MATERIAL+'.mtl' in deps,(key,deps)
    with contextlib.redirect_stdout(io.StringIO()):audit.run(OUT/'audit-after',False)
    a=json.loads((OUT/'audit-before/audit.json').read_text());b=json.loads((OUT/'audit-after/audit.json').read_text())
    assert not b['errors'];assert a['unresolved']==b['unresolved']
    runtime=lambda audit:{r['path'] for r in audit['rows'] if r['status']=='runtime'}
    expected={replace(p.encode()).decode() for p in runtime(a)};assert expected==runtime(b),(expected-runtime(b),runtime(b)-expected)
    result=dict(renamed_assets=16,common_material=NEW_MATERIAL,updated_reference_files=[c['new'] for c in plan['changes'] if c['old']==c['new']],
        xlp_entries_before=count(before),xlp_entries_after=count(after),unaffected_files_hash_verified=unchanged,changes_are_identifiers_only=True,
        material_settings_identical=True,runtime_dependency_graph_preserved=True,old_material_archived=True,cooks_pass=True,unresolved=b['unresolved'])
    write(OUT/'final-verification.json',result);write(ARCHIVE/'completed.json',result)
    shutil.copy2(OUT/'plan.json',ARCHIVE/'plan.json')
    for phase in ['before','after']:
        dst=ARCHIVE/'cook-evidence'/phase;dst.mkdir(parents=True)
        for name in ['command.json','result.json','stdout.log']:shutil.copy2(OUT/('cook-'+phase)/'results'/name,dst/name)
    (ARCHIVE/'README.txt').write_text('Flax decal rename — 26 October 2026\n\n16 active ASTs renamed from IMP_Farm_CSC_Flax_Decal_* to CSC_IMP_Farm_Flax_Decal_*. All use the existing CSC_IMP_Farm_Flax_Decals material. Old duplicate material archived. XLP, Farms ArtDef, nine attached-asset consumers and AE dependency cache updated. Appearance/settings, geometry and textures unchanged; both materials were identical apart from name.\n\nOriginal edited/retired files are in mod-before; the former AE cache is AssetCloud-before.json. Both isolated native cooks and reference audits passed. No installed-game deployment or live visual review. Restore selected files only after checking for later edits.\n',encoding='utf-8')
    print(json.dumps(result,indent=2))

if __name__=='__main__':globals()[sys.argv[1]]()
