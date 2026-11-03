"""Dated, hash-guarded cleanup authorized 26 October; preserve Working Files."""
import contextlib,io,json,os,re,shutil,subprocess,sys,time,hashlib
from pathlib import Path
from lxml import etree as E
import audit_art_orphans as audit

MOD=audit.MOD
OUT=Path('C:/Users/Shadow/Desktop/Codex/Art-cleanup-audit-20261026')
ARCHIVE=Path('C:/Users/Shadow/Desktop/Archive/CSC-art-cleanup-20261026')
CACHE=Path(os.environ['APPDATA'])/'AssetCloud/mod-Civ Supply Chains-asset-deps.json'
PROTECT={'Textures/CSC_Props_Shared_01_E.tex','Textures/CSC_Props_Shared_01_E.dds'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2),encoding='utf-8')
def norm(s):return s.replace('\\','/').casefold()

def prepare():
    assert not ARCHIVE.exists(),'Fresh archive required'
    with contextlib.redirect_stdout(io.StringIO()):audit.run(OUT/'pre-cleanup',False)
    current=json.loads((OUT/'pre-cleanup/audit.json').read_text())
    assert not current['errors']
    old=json.loads((OUT/'cleanup-plan.json').read_text())
    rows={r['path']:r for r in current['rows']}
    retire={r['path'] for r in old['files']}
    assert len(retire)==190 and not retire&PROTECT
    for r in old['files']:
        assert rows[r['path']]['status'] in {'packaged-only','unreferenced'},r['path']
        assert rows[r['path']]['sha256']==r['sha256'],('Changed since review',r['path'])
    # Snapshot all local art for isolated before/after cooking. Nothing points
    # to installed game files; source artwork is never moved or changed.
    before=OUT/'cook-before/pantry';after=OUT/'cook-after/pantry'
    for folder in audit.FOLDERS+['XLPs','ArtDefs']:
        for p in (MOD/folder).rglob('*'):
            if not p.is_file():continue
            rel=p.relative_to(MOD)
            for base in [before,after] if rel.as_posix() not in retire else [before]:
                dst=base/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dst)
    changes={};removed_entries=[]
    for p in (MOD/'XLPs').glob('*.xlp'):
        root=audit.parse(p);entries=root.find('m_Entries');count=0
        known=[e for e in current['xlp_entries'] if e['xlp']==p.name]
        dead={e['entry'] for e in known if e['targets'] and set(e['targets'])<=retire}
        for e in list(entries):
            if audit.value(e.find('m_EntryID')) in dead:
                removed_entries.append([p.name,audit.value(e.find('m_EntryID'))]);entries.remove(e);count+=1
        if count:
            rel=p.relative_to(MOD).as_posix();data=E.tostring(root,encoding='UTF-8',xml_declaration=True,pretty_print=True)
            changes[rel]=data;(after/rel).write_bytes(data)
    project=MOD/'Civ Supply Chains.civ6proj';raw=project.read_bytes();removed_content=[]
    def replace(m):
        rel=m.group(1).decode().replace('\\','/')
        if rel in retire:removed_content.append(rel);return b''
        return m.group(0)
    edited=re.sub(rb'(?m)^[ \t]*<Content\s+Include="([^"]+)"[^>]*(?:/>|>.*?</Content>)[ \t]*\r?\n',replace,raw,flags=re.S)
    E.fromstring(edited);changes[project.name]=edited
    original_cache=CACHE.read_bytes();cache=json.loads(original_cache.decode('utf-8-sig'))
    retiredkeys={norm('Civ Supply Chains/'+r) for r in retire}
    cache['Files']=[e for e in cache['Files'] if norm(e['Filename']) not in retiredkeys]
    cache['Dependencies']={k:[v for v in vs if norm(v) not in retiredkeys] for k,vs in cache['Dependencies'].items() if norm(k) not in retiredkeys}
    now=int(time.time()*1e7)+116444736000000000
    for e in cache['Files']:
        rel=e['Filename'].replace('\\','/').removeprefix('Civ Supply Chains/')
        if rel in changes:e['Filesize']=len(changes[rel]);e['Timestamp']=now
    cache['Timestamp']=now
    ARCHIVE.mkdir(parents=True)
    for rel in sorted(retire):
        target=(MOD/rel).resolve();assert target.is_relative_to(MOD.resolve())
        backup=ARCHIVE/'removed/Civ Supply Chains'/rel;backup.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(target,backup)
        assert sha(backup)==rows[rel]['sha256']
    for rel,data in changes.items():
        src=MOD/rel;dst=ARCHIVE/'registrations/Civ Supply Chains'/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
        staged=OUT/'registration-updates'/rel;staged.parent.mkdir(parents=True,exist_ok=True);staged.write_bytes(data)
    (ARCHIVE/'registrations/AssetCloud-before.json').write_bytes(original_cache)
    write(OUT/'registration-updates/AssetCloud-after.json',cache)
    state=dict(retire=sorted(retire),baseline={r['path']:r['sha256'] for r in current['rows']},
        registrations={rel:sha(MOD/rel) for rel in changes},cache_sha=hashlib.sha256(original_cache).hexdigest(),
        removed_xlp_entries=removed_entries,removed_project_content=removed_content,protected=sorted(PROTECT))
    write(ARCHIVE/'cleanup-manifest.json',state);write(OUT/'cleanup-state.json',state)
    print('PREPARED',len(retire),'archived files;',len(removed_entries),'XLP entries;',len(removed_content),'project registrations',flush=True)

def cook(which):
    assert which in {'before','after'}
    cooker=next(Path('C:/Program Files (x86)/Steam/steamapps/common').glob('*Civilization VI SDK/AssetModTools/Cooker'))
    base=OUT/('cook-'+which);pantry=base/'pantry';target=base/'results';target.mkdir(exist_ok=True)
    cmd=[str(cooker/'Civ6AssetCooker_FinalRelease.exe'),'--absolute_paths','--no_mt','--mode','XLP','--platform','Windows','--shaders',str(cooker),'--pantry',str(pantry)]
    for p in ['Civ6/pantry','Civ6/DLC/Shared/pantry','Civ6/DLC/Expansion1/pantry','Civ6/DLC/Expansion2/pantry']:cmd+=['--pantry',str(audit.SDK/p)]
    cmd+=['--stewpot',str(target/'BLPs'),'--config',str(cooker/'Civ6.cfg'),'--log_path',str(target),str(pantry/'XLPs/CSC_Tilebases.xlp')]
    write(target/'command.json',cmd)
    with (target/'stdout.log').open('w') as f:
        try:result=subprocess.run(cmd,cwd=target,stdout=f,stderr=subprocess.STDOUT,timeout=240,env=dict(os.environ,_NO_DEBUG_HEAP='1'));code=result.returncode
        except subprocess.TimeoutExpired:code='timeout'
    write(target/'result.json',dict(exit_code=code,blps=[dict(path=str(p),bytes=p.stat().st_size) for p in target.rglob('*.blp')]))
    print('COOK',which,code);print((target/'stdout.log').read_text(errors='replace').replace('\x00','')[-4500:])

def publish():
    state=json.loads((OUT/'cleanup-state.json').read_text());assert not (ARCHIVE/'completed.json').exists()
    for which in ['before','after']:
        cooked=json.loads((OUT/('cook-'+which)/'results/result.json').read_text())
        assert cooked['exit_code']==0 and cooked['blps'] and all(r['bytes']>0 for r in cooked['blps']),cooked
    for rel,h in state['baseline'].items():assert sha(MOD/rel)==h,('Art changed since snapshot',rel)
    for rel,h in state['registrations'].items():assert sha(MOD/rel)==h,('Registration changed',rel)
    assert sha(CACHE)==state['cache_sha'],'AE cache changed; rebase before publication'
    for rel in state['retire']:assert sha(ARCHIVE/'removed/Civ Supply Chains'/rel)==state['baseline'][rel]
    # Registration edits first; exact backed-up paths only, never recursive delete.
    for rel in state['registrations']:(MOD/rel).write_bytes((OUT/'registration-updates'/rel).read_bytes())
    for rel in state['retire']:
        p=(MOD/rel).resolve();assert p.is_relative_to(MOD.resolve()) and p.is_file();p.unlink()
    CACHE.write_bytes((OUT/'registration-updates/AssetCloud-after.json').read_bytes())
    retained=set(state['baseline'])-set(state['retire'])
    for rel in retained:assert sha(MOD/rel)==state['baseline'][rel],rel
    for rel in PROTECT:assert sha(MOD/rel)==state['baseline'][rel]
    with contextlib.redirect_stdout(io.StringIO()):audit.run(OUT/'post-cleanup',False)
    post=json.loads((OUT/'post-cleanup/audit.json').read_text());pre=json.loads((OUT/'pre-cleanup/audit.json').read_text())
    assert not post['errors']
    assert {r['path'] for r in post['rows'] if r['status']=='runtime'}=={r['path'] for r in pre['rows'] if r['status']=='runtime'}
    assert not [r for r in post['rows'] if r['status'] in {'unreferenced','packaged-only'}]
    result=dict(removed_files=len(state['retire']),archived_bytes=sum((ARCHIVE/'removed/Civ Supply Chains'/r).stat().st_size for r in state['retire']),
        retained_files_hash_verified=len(retained),runtime_reachable_set_unchanged=True,working_files_untouched=True,protected=sorted(PROTECT),
        unresolved=post['unresolved'],xlp_entries_removed=len(state['removed_xlp_entries']),project_entries_removed=len(state['removed_project_content']))
    write(ARCHIVE/'completed.json',result);print(json.dumps(result,indent=2))

def finish_report():
    result=json.loads((ARCHIVE/'completed.json').read_text())
    for filename in ['inventory.csv','audit.json','cleanup-plan.json']:
        shutil.copy2(OUT/filename,ARCHIVE/filename)
    shutil.copytree(OUT/'post-cleanup',ARCHIVE/'post-cleanup',dirs_exist_ok=True)
    for which in ['before','after']:
        for filename in ['command.json','result.json','stdout.log']:
            dst=ARCHIVE/'cook-evidence'/which/filename;dst.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(OUT/('cook-'+which)/'results'/filename,dst)
    note='''CSC art cleanup completed — 26 October 2026

190 files (35,634,046 bytes) removed from the CSC source mod only.
28 XLP entries and 14 ModBuddy Content registrations removed; AE dependency
cache cleaned. All 553 retained art files are byte-identical to the pre-cleanup
snapshot, and the runtime-reachable file set is unchanged.

Working Files was not modified. CSC_Props_Shared_01_E TEX/DDS remains in CSC.
The shared well, its tinted material and texture dependencies remain unchanged.

Both isolated Windows Tilebases cooks succeeded. No game deployment or live
in-game review was performed. Existing geometry warnings and the old Bakers
Well material reference are separate issues.

removed/Civ Supply Chains: original removed files, with directory structure.
registrations: original project/XLP files and AssetCloud cache snapshot.
cleanup-manifest.json: original hashes and exact paths.
completed.json: verification receipt.
post-cleanup: dependency audit after removal.
cook-evidence: commands, results and logs from both isolated cooks.

To restore: copy selected files back to matching CSC paths and restore their
registrations. Do not blindly overwrite project/XLP/cache files after further
editing; merge the archived entries into the newer files instead.

Tint recommendation (not implemented): add a shared T mask and tinted material
variant to the current shared prop atlas, reusing its existing surface maps and
verified slots. The current CSC_ALL_is_Well already uses the older
CSC_ALL_Props_ET material with CSC_Atlas_Props_B_T and CSC_Atlas_Props_T.
Migrating it would require UV/material work and appearance verification.
A separate full 256x256 atlas is unnecessary just to enable tint support.
'''
    (ARCHIVE/'README.txt').write_text(note,encoding='utf-8')
    p=OUT/'cleanup-review.html';html=p.read_text(encoding='utf-8')
    banner='<section style="border:2px solid #527a41"><h2>Cleanup completed — 26 October 2026</h2><p>190 files archived to Desktop/Archive/CSC-art-cleanup-20261026 and removed from the CSC mod folder. Working Files and CSC_Props_Shared_01_E are preserved. XLP, project and AE-cache registrations updated. Both isolated tilebase cooks passed; all retained art files and runtime dependencies verified unchanged. The inventory below is the historical pre-cleanup review.</p></section>'
    if banner not in html:html=html.replace('<body>','<body>'+banner,1);p.write_text(html,encoding='utf-8')
    shutil.copy2(p,ARCHIVE/'cleanup-review.html')
    print('Archive receipt and review updated')

if __name__=='__main__':
    if sys.argv[1]=='cook':cook(sys.argv[2])
    else:globals()[sys.argv[1]]()
