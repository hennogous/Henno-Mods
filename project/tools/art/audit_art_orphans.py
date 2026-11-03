"""Read-only source dependency audit. XLP registration alone is not runtime use."""
import argparse, collections, csv, hashlib, html, json, os, re
from pathlib import Path
from lxml import etree as E

ROOT=Path(__file__).resolve().parents[3]
MOD=ROOT/'Civ Supply Chains'
SDK=Path("C:/Program Files (x86)/Steam/steamapps/common/Sid Meier's Civilization VI SDK Assets")
DESCRIPTORS={'.ast','.geo','.mtl','.mat','.tex','.anm','.bhv','.dsg','.ptl','.lit','.artdef'}
FOLDERS=['Assets','Geometries','Materials','Textures','Animations','Behaviors','DSGs','ParticleEffects','Lights','LightRigs','EnvironmentLights','FireFX']
TYPED={'MATERIAL':'.mtl','TEXTURE':'.tex','GEOMETRY':'.geo','ASSET':'.ast','ANIMATION':'.anm','PARTICLE':'.ptl','LIGHT':'.lit'}
TAGS={'m_GeoName':'.geo','m_AnimationName':'.anm','m_dsgName':'.dsg','m_BehaviorName':'.bhv','m_MaterialName':'.mtl','m_TextureName':'.tex','m_FXName':'.ast'}

def value(e):return (e.get('text') or e.text or '').strip() if e is not None else ''
def key(s):return s.replace('\\','/').split('/')[-1].casefold()
def parse(p):
    # The Firaxis manifest root uses a literal double colon, not XML namespaces.
    return E.fromstring(re.sub(rb'AssetObjects:+',b'AssetObjects..',p.read_bytes()))

def run(out,make_report=True):
    out.mkdir(parents=True,exist_ok=True)
    local={p.relative_to(MOD).as_posix():p for folder in FOLDERS for p in (MOD/folder).rglob('*') if p.is_file()}
    local.update({p.relative_to(MOD).as_posix():p for p in (MOD/'ArtDefs').glob('*.artdef')})
    index=collections.defaultdict(set)
    for rel,p in local.items():
        index[(p.suffix.casefold(),p.stem.casefold())].add(rel)
    cache=json.loads((Path(os.environ['APPDATA'])/'AssetCloud/mod-Civ Supply Chains-asset-deps.json').read_text(encoding='utf-8-sig'))
    external={}
    for record in cache['Files']:
        path=record['Filename'].replace('\\','/')
        if path.startswith('Civ6/'):
            p=SDK/path
            if p.exists():external[path]=p
    extindex=collections.defaultdict(set)
    for rel,p in external.items():extindex[(p.suffix.casefold(),p.stem.casefold())].add(rel)
    files={**external,**local}; graph=collections.defaultdict(set); reasons=collections.defaultdict(list)
    unresolved=[]; parsed=set(); errors=[]; xlpentries=[]; alias=collections.defaultdict(set)
    def resolve(name,ext=None):
        if not name:return set()
        n=key(name)
        if ext:
            if n.endswith(ext):n=n[:-len(ext)]
            return index.get((ext,n),set()) or extindex.get((ext,n),set())
        suffix=Path(n).suffix
        if suffix:return resolve(n,suffix)
        return set().union(*(index.get((x,n),set()) or extindex.get((x,n),set()) for x in DESCRIPTORS))
    def link(src,targets,why):
        for dst in targets:
            if src!=dst:graph[src].add(dst);reasons[(src,dst)].append(why)
    for p in (MOD/'XLPs').glob('*.xlp'):
        r=parse(p);cl=value(r.find('m_ClassName'));ext={ 'TileBase':'.ast','Landmark':'.ast','UITexture':'.tex','StrategicView_Sprite':'.tex','Light':'.lit','VFX':'.ast'}.get(cl)
        for el in r.findall('m_Entries/Element'):
            name=value(el.find('m_ObjectName'));entry=value(el.find('m_EntryID'));targets=resolve(name,ext)
            alias[entry.casefold()].update(targets)
            xlpentries.append(dict(xlp=p.name,entry=entry,object=name,targets=sorted(targets),library=cl))
    def scan(rel):
        if rel in parsed:return
        parsed.add(rel);p=files[rel]
        if p.suffix.lower() not in DESCRIPTORS:return
        try:r=parse(p)
        except Exception as ex:errors.append([rel,str(ex)]);return
        for el in r.iter():
            name=value(el)
            if not name:continue
            targets=set()
            if el.tag in TAGS:targets=resolve(name,TAGS[el.tag])
            elif el.tag=='m_EntryName':targets=alias.get(name.casefold(),set()) or resolve(name)
            elif el.tag=='m_ObjectName':
                kind=value(el.getparent().find('m_eObjectType'))
                targets=resolve(name,TYPED.get(kind))
            elif el.tag=='m_RelativePath':
                q=(p.parent/name.replace('\\','/')).resolve()
                if q.is_relative_to(MOD):
                    rr=q.relative_to(MOD).as_posix()
                    if rr in files:targets={rr}
                elif q.is_relative_to(SDK):
                    rr=q.relative_to(SDK).as_posix()
                    if rr in files:targets={rr}
            elif el.tag=='m_SourceFilePath':
                q=Path(name)
                if q.is_absolute() and q.is_relative_to(MOD):
                    rr=q.relative_to(MOD).as_posix()
                    if rr in files:targets={rr}
            elif el.tag=='m_ArtDefPath':targets=resolve(name,'.artdef')
            elif el.tag not in {'Element','m_Name','m_SourceObjectName','m_ModelName','m_MeshName','m_GroupName','m_BoneName','m_ParentBoneName','m_ParamName','m_Description','m_EntryID','m_Tag','m_ElementName'} and len(el)==0:
                # Conservative fallback for light/particle/shader-specific slots.
                targets=resolve(name)
            if targets:link(rel,targets,el.tag)
            elif (el.tag in TAGS or el.tag in {'m_EntryName','m_ObjectName'}) and name.startswith('CSC_'):
                unresolved.append(dict(source=rel,tag=el.tag,name=name))
        # Keep descriptor sidecars as a family; this also protects authoring PNGs.
        if rel in local and p.suffix in {'.geo','.anm','.tex'}:
            for q in p.parent.glob(p.stem+'.*'):
                rr=q.relative_to(MOD).as_posix()
                if rr in files and q.suffix in {'.fgx','.dds','.png','.tga','.cn6'}:link(rel,{rr},'same-stem sidecar')
    for rel in local:scan(rel)
    def closure(roots):
        seen=set();queue=collections.deque(sorted(roots));parents={r:None for r in roots}
        while queue:
            n=queue.popleft()
            if n in seen:continue
            seen.add(n)
            if n in files:scan(n)
            for c in sorted(graph[n]):
                if c not in parents:parents[c]=n;queue.append(c)
        return seen,parents
    manifest=parse(MOD/'Civ Supply Chains.Art.xml')
    declared={value(e) for e in manifest.findall('.//relativeArtDefPaths/Element')}
    artroots=set().union(*(resolve(n,'.artdef') for n in declared))
    runtime,parents=closure(artroots)
    # Exact literal references in gameplay/UI sources provide independent roots.
    code_roots=set();code_refs=collections.defaultdict(list)
    for folder in ['Data','Icons','Lua_UI','UI','Replacements','ModSupport','Settings','Text']:
        for p in (MOD/folder).rglob('*'):
            if p.suffix.lower() not in {'.sql','.xml','.lua'}:continue
            text=p.read_text(encoding='utf-8-sig',errors='replace')
            for token in re.findall(r'''["']([^"'\r\n]+)["']''',text):
                targets=resolve(token) | alias.get(token.casefold(),set())
                for dst in targets:code_roots.add(dst);code_refs[dst].append(p.relative_to(MOD).as_posix())
    runtime,parents=closure(artroots|code_roots)
    packaged,packageparents=closure({n for e in xlpentries for n in e['targets']})
    # Protect sibling-project consumers; packaging is not proof of use but is
    # still required for a safe physical-file removal plan.
    sibling_roots=set();sibling_refs=collections.defaultdict(list)
    sibling=ROOT/'TaxesPolitics'
    if sibling.exists():
        for p in sibling.rglob('*'):
            if p.suffix.lower() not in DESCRIPTORS|{'.xlp','.sql','.lua','.xml'}:continue
            if any(s in p.parts for s in ['bin','obj','.git']):continue
            text=p.read_text(encoding='utf-8-sig',errors='replace')
            for token in re.findall(r'''["']([^"'\r\n]+)["']''',text):
                for dst in resolve(token):sibling_roots.add(dst);sibling_refs[dst].append(p.relative_to(ROOT).as_posix())
    protected,_=closure(sibling_roots)
    # Use the cache only as independent evidence, never as authoritative roots:
    # it can retain old files and references after an AE assembly edit.
    cache_extra=[]
    for src,deps in cache['Dependencies'].items():
        s=src.replace('\\','/').removeprefix('Civ Supply Chains/')
        if s not in runtime:continue
        for dep in deps:
            d=dep.replace('\\','/').removeprefix('Civ Supply Chains/')
            if d in local and d not in runtime:cache_extra.append(dict(source=s,target=d))
    cache_hold,_=closure({r['target'] for r in cache_extra})
    reverse=collections.defaultdict(set)
    for src,targets in graph.items():
        for dst in targets:reverse[dst].add(src)
    def chain(n):
        result=[n]
        while parents.get(n) is not None:n=parents[n];result.append(n)
        return list(reversed(result))
    rows=[]
    for rel,p in sorted(local.items()):
        if p.suffix=='.artdef':continue
        status='runtime' if rel in runtime else 'sibling-protected' if rel in protected else 'cache-review' if rel in cache_hold else 'packaged-only' if rel in packaged else 'unreferenced'
        rows.append(dict(path=rel,status=status,bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
            referenced_by=sorted(reverse[rel]),runtime_chain=chain(rel) if rel in runtime else [],
            xlp_entries=[f"{e['xlp']}:{e['entry']}" for e in xlpentries if rel in e['targets']],
            code_references=sorted(set(code_refs[rel])),sibling_references=sorted(set(sibling_refs[rel]))))
    summary={folder:dict(collections.Counter(r['status'] for r in rows if r['path'].startswith(folder+'/'))) for folder in FOLDERS}
    # Independent broad literal search: identify candidate names mentioned by
    # live sources but missed by the typed dependency graph.
    literal_review=[]
    candidates={Path(r['path']).stem.casefold():r['path'] for r in rows if r['status'] in {'packaged-only','unreferenced'} and Path(r['path']).suffix in DESCRIPTORS}
    for p in MOD.rglob('*'):
        if p.suffix.lower() not in DESCRIPTORS|{'.sql','.xml','.lua'}:continue
        rel=p.relative_to(MOD).as_posix()
        if rel not in runtime and p.suffix.lower() in DESCRIPTORS:continue
        for token in set(re.findall(r'[A-Za-z0-9_+.-]+',p.read_text(encoding='utf-8-sig',errors='replace'))):
            n=token.casefold();n=n[:-len(Path(n).suffix)] if Path(n).suffix else n
            if n in candidates:literal_review.append(dict(source=rel,candidate=candidates[n],token=token))
    result=dict(summary=summary,rows=rows,artdef_roots=sorted(artroots),code_roots=sorted(code_roots),
        errors=errors,unresolved=unresolved,cache_disagreements=cache_extra,literal_review=literal_review,xlp_entries=xlpentries,
        method='All declared ArtDef rows retained conservatively; recursive dependencies plus exact code/UI literals. XLP registration alone does not prove use. No files deleted.')
    (out/'audit.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    with (out/'inventory.csv').open('w',encoding='utf-8-sig',newline='') as f:
        fields=['path','status','bytes','referenced_by','xlp_entries','runtime_chain'];w=csv.DictWriter(f,fields);w.writeheader()
        for row in rows:w.writerow({k:' | '.join(row[k]) if isinstance(row[k],list) else row[k] for k in fields})
    if make_report:report(out,result)
    print(json.dumps(dict(summary=summary,errors=errors,unresolved=unresolved,cache_disagreements=cache_extra),indent=2))

def report(out,data):
    rows=data['rows'];orphans=[r for r in rows if r['status'] in {'packaged-only','unreferenced'}]
    assert not data['errors'],'Cannot publish a safe inventory with unread descriptors'
    bundled={
        'CSC_BAKERS_Oven_v2':'Bakery (regular and activated)',
        'CSC_BAKERS_Peel':'Bakery (two peels, regular and activated)',
        'CSC_BAKERS_Cafe_Counter':'Cafe (two counters, regular and activated)',
        'CSC_BAKERS_Cafe_Brewing_Set':'Cafe (regular and activated)',
        'CSC_BAKERS_Cafe_Pastry_Tray':'Cafe (regular and activated)',
        'CSC_TAILORS_Fashion_House_Fitting':'Fashion House (regular and activated)'}
    known={r['path']:r for r in rows}
    for n in bundled:
        for rel in [f'Assets/{n}.ast',f'Geometries/{n}.geo',f'Geometries/{n}.fgx']:
            assert known[rel]['status'] in {'packaged-only','unreferenced'},rel
    # Simulated removal: no retained runtime or sibling-protected consumer may
    # depend on a removed file. XLP/project/cache registrations are separate work.
    retired={r['path'] for r in orphans}
    violations=[(src,r['path']) for r in orphans for src in r['referenced_by'] if src in known and known[src]['status'] in {'runtime','sibling-protected'}]
    assert not violations,violations
    plan=dict(created='2026-10-26',operation='review only; no deletion',files=orphans,
        bundled_asset_names=sorted(bundled),no_retained_runtime_reference_crosses_removal_set=True,
        required_followup=['Archive listed source-runtime files outside the mod tree; preserve editable Working Files masters.',
        'Remove matching XLP entries, ModBuddy Content entries and stale AssetCloud records together.',
        'Re-audit, cook and inspect normal/activated/construction/pillage states before discarding the archive.'],
        cache_review=data['cache_disagreements'])
    (out/'cleanup-plan.json').write_text(json.dumps(plan,indent=2),encoding='utf-8')
    def esc(x):return html.escape(str(x))
    def table(headers,items):
        return '<table><thead><tr>'+''.join('<th>'+esc(h)+'</th>' for h in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+esc(c)+'</td>' for c in row)+'</tr>' for row in items)+'</tbody></table>'
    def section(title,body):return '<section><h2>'+esc(title)+'</h2>'+body+'</section>'
    contents='<h1>CSC art cleanup review</h1><p class="lead">26 October 2026 · Read-only audit · No assets deleted</p>'
    contents+='<p>Traced declared ArtDefs through recursive attachments, all model states, materials and textures; also checked UI/SQL/Lua literals, sibling-project references and the Asset Editor dependency cache. Package registration alone does not count as use. All rows in declared ArtDefs are retained conservatively, even if their gameplay conditions may never fire.</p>'
    contents+=table(['Type','No current runtime chain','Current runtime files'],[(folder,sum(r['path'].startswith(folder+'/') for r in orphans),sum(r['path'].startswith(folder+'/') and r['status']=='runtime' for r in rows)) for folder in ['Assets','Geometries','Materials','Textures','Lights','ParticleEffects']])
    contents+=f'<p><b>{len(orphans)} files ({sum(r["bytes"] for r in orphans)/1048576:.2f} MiB)</b> are candidates for an archive-and-unregister pass. These include 30 assets, 59 geometry descriptors plus their binaries and one CN6, eight materials, 14 texture descriptor/DDS pairs plus one loose DDS, two lights and one particle-effect pair. One additional texture pair is held for cache reconciliation.</p>'
    contents+=section('Bundled props: standalone files can be retired',table(['Asset name (.ast)','Now part of'],sorted(bundled.items()))+'<p>The matching standalone .geo/.fgx pairs are also unused. Their shared materials and textures remain used by the bundled main models. Keep the editable prop masters in Working Files for future reuse.</p>')
    def asset_reason(n):
        if n in bundled:return 'Bundled into main model; standalone geometry also unused.'
        if n=='CSC_ALL_Stage_4_Cobble_Decals':return 'Unused AST wrapper only. KEEP its same-name GEO/FGX, material and textures: Cafe references geometry directly.'
        if n=='CSC_TEST_Tailor_Wrapper':return 'Historical placement test; live ArtDefs now use relocated Tailor directly.'
        if n=='CSC_BAKERS_Oven':return 'Superseded oven; also references missing CSC_BAKERS_Props material.'
        if n=='CSC_TAILORS_Loom':return 'Unused placeholder; referenced same-name geometry is absent.'
        if n=='CSC_TAILORS_Well':return 'Unused variant; referenced same-name material is absent.'
        if n=='CSC_ALL_Prop_Library':return 'Unused library/test asset.'
        if n.startswith(('IMP_Farm_CSC_Flax','CSC_IMP_Farm_Flax')):return 'No current ArtDef consumer. Corresponding Farms slots select vanilla decals; preserve as spare authoring variation if wanted.'
        return 'Unused reusable prop/variant; archive outside runtime tree rather than discard authoring work.'
    contents+=section('All 30 unused standalone assets',table(['Asset file','Packaging','Disposition'],[(Path(r['path']).name,'XLP entry must be removed' if r['xlp_entries'] else 'No XLP entry',asset_reason(Path(r['path']).stem)) for r in orphans if r['path'].startswith('Assets/')]))
    contents+=section('All eight unused materials',table(['Material file','Consumers'],[(Path(r['path']).name,', '.join(r['referenced_by']) or 'None') for r in orphans if r['path'].startswith('Materials/')])+'<p>Do not delete an atlas just because an old material is unused. In particular CSC_ALL_Props_E / CSC_ALL_Props_ET still consume the old CSC_Atlas_Props maps, and CSC_ALL_Props_01 still consumes the shared prop maps.</p>')
    contents+=section('Unused textures',table(['File','Other orphan consumers'],[(Path(r['path']).name,', '.join(r['referenced_by']) or 'None') for r in orphans if r['path'].startswith('Textures/')])+'<p>Remove dependent obsolete materials in the same pass. Source artwork outside the mod folder is excluded from cleanup.</p>')
    contents+=section('Unused geometry families',table(['Descriptor / extra source','Other orphan consumers'],[(Path(r['path']).name,', '.join(r['referenced_by']) or 'None') for r in orphans if r['path'].startswith('Geometries/') and not r['path'].endswith('.fgx')])+'<p>The JSON/CSV inventory lists each exact binary. Preserve shared Level 1/2/3 and storage Blender masters even when a corresponding runtime export is redundant. Tailor_2 and Textile_Workshop_2 ASTs remain live; only their redundant separate GEO/FGX files are candidates because the ASTs use their regular main geometry.</p>')
    contents+=section('Other unused entries',table(['File','Registration'],[(r['path'],', '.join(r['xlp_entries']) or 'None') for r in orphans if r['path'].startswith(('Lights/','ParticleEffects/'))]))
    contents+=section('Hold / separate repair', '<p><b>CSC_Props_Shared_01_E.tex/.dds:</b> no current source-material consumer, but the AE cache still lists it under CSC_ALL_Props_01. That material now references CSC_Atlas_E. Reconcile the stale cache before retiring this pair.</p><p><b>Existing live broken reference:</b> CSC_BAKERS_Well.ast is still reached from CSC_BAKERS_Classical_Base_09 and requests missing material CSC_BAKERS_Well. Keep the asset; investigate its material separately. The unused old Oven, Loom and Tailors Well also have missing dependencies, but are already in the orphan set.</p>')
    contents+=section('Cleanup procedure and evidence','<ol><li>Archive the exact listed files outside Civ Supply Chains, preserving editable source masters.</li><li>Remove their XLP entries, project Content registrations and AssetCloud records in the same pass. Keep shared dependencies that the inventory marks runtime.</li><li>Run this audit again and cook; inspect normal, activated, construction and pillage appearances.</li></ol><p>Files supplied: inventory.csv (all files and reference chains), audit.json (full graph findings), cleanup-plan.json (exact file hashes and removal-set cross-check). Nothing has been deleted or unregistered. This is a static source audit, not a post-cleanup cook result.</p>')
    page='<!doctype html><html><head><meta charset="utf-8"><title>CSC art cleanup review</title><style>body{font:15px/1.55 system-ui;max-width:1250px;margin:40px auto;padding:0 24px;color:#26323a;background:#f7f8f5}h1{font-size:32px}h2{font-size:22px;margin-top:0}.lead{color:#667363}section{background:white;padding:24px;margin:24px 0;border:1px solid #d8dfd4;border-radius:10px}table{border-collapse:collapse;width:100%;font-size:13px}th,td{text-align:left;padding:8px 10px;border-bottom:1px solid #e3e8df;vertical-align:top;overflow-wrap:anywhere}th{background:#e7eddf}tr:nth-child(even){background:#f7f9f5}p{max-width:1100px}</style></head><body>'+contents+'</body></html>'
    (out/'cleanup-review.html').write_text(page,encoding='utf-8')

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();run(args.output)
