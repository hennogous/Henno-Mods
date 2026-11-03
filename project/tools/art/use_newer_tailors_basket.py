"""Promote the authored Shared_01 basket; retire its redundant legacy atlas cells."""
import sys,json,shutil,subprocess,os,time,importlib.util
from pathlib import Path
import numpy as np
from PIL import Image
from storage_pivot_trial import ROOT,MOD,helper,parse,save,txt
from migrate_legacy_prop_atlas import sha,write
OUT=Path('C:/Users/Shadow/Desktop/Codex/Tailors-newer-basket-20261026')
ART=Path('C:/Users/Shadow/Desktop/Working Files/3D Art')
LIB=ART/'Textures/CSC_Props'
STAGE=OUT/'atlas-release'
ARCHIVE=Path('C:/Users/Shadow/Desktop/Archive/CSC-older-tailors-basket-20261026')
NAME='CSC_TAILORS_Basket'
SOURCE=ART/'TAILORS/Textile Workshop/revision-11-pantry-interiors-shared-ao'/f'{NAME}.blend'
DEST=ART/'Props/Tailors'/f'{NAME}.blend'
RELEASE='2026-10-26_Shared_01_r046'

def prepare():
    OUT.mkdir(exist_ok=True);assert not STAGE.exists()
    shutil.copytree(LIB/'Current',STAGE)
    baseline={str(p):sha(p) for folder in ['Assets','Geometries','Materials','Textures','XLPs','ArtDefs'] for p in (MOD/folder).rglob('*') if p.is_file()}
    baseline.update({str(p):sha(p) for p in (LIB/'Current').rglob('*') if p.is_file()})
    baseline.update({str(p):sha(p) for p in [SOURCE,DEST,LIB/'CURRENT.json']})
    write(OUT/'baseline.json',baseline)
    old=LIB/'Releases/2026-10-24_Shared_01_r044'
    checks=[]
    for k in ['B','N','G','M','T','AO']:
        box=(1408,384,1536,512) if k=='AO' else (128,640,256,768)
        rel=Path('textures')/f'CSC_Props_Shared_01_{k}.png'
        im=Image.open(STAGE/rel).convert('RGBA');before=np.array(im)
        patch=Image.open(old/rel).convert('RGBA').crop(box) if k!='T' else Image.new('RGBA',(128,128),(0,0,0,255))
        im.paste(patch,box[:2]);im.save(STAGE/rel)
        mask=np.ones(before.shape[:2],bool);x,y,x1,y1=box;mask[y:y1,x:x1]=False
        assert np.array_equal(before[mask],np.array(im)[mask]);checks.append(k)
        if k!='AO':
            rel=Path('atlas')/f'CSC_Props_Shared_01_v2_{k}_Master2048.png';box=(256,1280,512,1536)
            im=Image.open(STAGE/rel).convert('RGBA')
            patch=Image.open(old/rel).convert('RGBA').crop(box) if k!='T' else Image.new('RGBA',(256,256),(0,0,0,255))
            im.paste(patch,box[:2]);im.save(STAGE/rel)
    m=json.loads((STAGE/'atlas/manifest.json').read_text())
    removed=[r for r in m['regions'] if r['name']=='legacy_tailors_basket'];assert len(removed)==1 and removed[0]['slot']==41
    m['regions']=[r for r in m['regions'] if r not in removed];m['reserved_slots']=sorted(set(m['reserved_slots']+[41]))
    m.update(content_revision=46,change_note='Newer authored basket reuses existing surfaces and original AO; redundant legacy surface slot 41 freed.')
    m['production_sha256']={k:sha(STAGE/'textures'/f'CSC_Props_Shared_01_{k}.png') for k in ['B','N','G','M','T']}
    write(STAGE/'atlas/manifest.json',m)
    a=json.loads((STAGE/'atlas/quarter-ao-manifest.json').read_text());count=0
    for page in a['pages']:
        for q in page['quarters']:
            for f in q['families']:
                items=f.get('allocations',[]);count+=sum(i['id']==NAME+'_RuntimeMigration' for i in items)
                f['allocations']=[i for i in items if i['id']!=NAME+'_RuntimeMigration']
    assert count==1;a['status']=RELEASE+': original authored basket AO retained; redundant migration AO cell freed.'
    write(STAGE/'atlas/quarter-ao-manifest.json',a)
    p=STAGE/'atlas/basket-well-migration.json';mapping=json.loads(p.read_text())
    mapping['surface']=[r for r in mapping['surface'] if r['slot']!=41];del mapping['AO'][NAME];write(p,mapping)
    removed_paths=['atlas/'+v for v in removed[0]['sources'].values()]+[f'atlas/sources/{NAME}_legacy_AO128.png']
    for rel in removed_paths:
        p=(STAGE/rel).resolve();assert p.is_relative_to(STAGE.resolve());p.unlink()
    write(OUT/'removed-library-files.json',removed_paths)
    before={p.name:sha(p) for p in (STAGE/'textures').glob('*.png')}
    subprocess.run([sys.executable,str(STAGE/'scripts/pack_basket_well.py')],check=True)
    assert all(sha(STAGE/'textures'/n)==h for n,h in before.items())
    write(OUT/'atlas-preservation.json',dict(unchanged_outside_reclaimed_cells=checks,surface_slot=41,AO_cell=[1408,384,1536,512],rebuild_exact=True))
    (OUT/'staged/Geometries').mkdir(parents=True);(OUT/'masters').mkdir()
    textures()
    sys.path.insert(0,str(ROOT/'project/tools/blender'))
    from render_ae_asset import Resolver,Assembly,DEFAULT_SDK
    r=Resolver(MOD,DEFAULT_SDK)
    for p in (OUT/'staged/Textures').glob('*'):r.index[p.name.casefold()]={p}
    a=Assembly(r);a.material('CSC_ALL_Props_01',{},MOD,False);write(OUT/'materials.json',a.materials)
    print('Prepared reclaimed surface/AO cells; unrelated pixels unchanged; overlay rebuild exact.')

def textures():
    spec=importlib.util.spec_from_file_location('dds',ROOT/'project/tools/blender/scene_export/export_scene.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    dest=OUT/'staged/Textures';dest.mkdir(exist_ok=True)
    for k in ['B','N','G','M','T','AO']:
        name=f'CSC_Props_Shared_01_{k}';src=STAGE/'textures'/(name+'.png');scalar=k in ['G','M','AO'];fmt='R8_UNORM' if scalar else 'R8G8B8A8_UNORM'
        args=[str(ROOT/'project/tools/directxtex/texconv.exe'),'-nologo','-y','-m','0','-f',fmt,'--ignore-srgb','-o',str(dest)]+(['-srgb'] if k=='B' else [])+[str(src)]
        result=subprocess.run(args,capture_output=True,text=True);assert result.returncode==0,result.stdout+result.stderr
        desc=dict(format=fmt,size=list(Image.open(src).size),slot=k)
        if scalar:mod.normalize_ao_dds(dest/(name+'.dds'),desc,MOD/'Textures/CSC_Props_Shared_01_AO.dds')
        mod.validate_dds(dest/(name+'.dds'),desc)
        a=np.array(Image.open(src).convert('RGBA'));b=np.array(Image.open(dest/(name+'.dds')).convert('RGBA'))
        assert np.array_equal(a[:,:,0] if scalar else a,b[:,:,0] if scalar else b)
        shutil.copy2(MOD/'Textures'/(name+'.tex'),dest/(name+'.tex'))

def convert():
    src=OUT/'source-export'/f'{NAME}.cn6';target=OUT/'staged/Geometries'/src.name
    lines=src.read_text().splitlines();inside=False
    for i,line in enumerate(lines):
        if line=='vertices':inside=True;continue
        if line=='triangles':inside=False
        if not inside:continue
        values=line.split();assert len(values)==34
        active=[values[18+j] for j in range(8) if int(values[26+j])>0];assert active
        for j in range(8):
            if int(values[26+j])==0:values[18+j]=active[0]
        lines[i]=' '.join(values)
    target.write_text('\n'.join(lines)+'\n')
    exe=ROOT/'project/tools/cn6libs/CN6ToFGX.exe'
    r=subprocess.run([str(exe),str(target),str(target.with_suffix('.fgx')),'2'],cwd=exe.parent,capture_output=True,text=True)
    (OUT/'conversion.log').write_text(r.stdout+r.stderr);assert r.returncode==0,r.stdout+r.stderr
    exe,_=helper(OUT/'cache');dest=OUT/'native-after.json'
    subprocess.run([str(exe),str(exe.parent),str(target.with_suffix('.fgx')),str(dest)],cwd=exe.parent,check=True,capture_output=True)
    raw=json.loads(dest.read_text());assert len(raw['meshes'])==1
    mesh=raw['meshes'][0];assert mesh['boneBindings']==['Bone'],mesh['boneBindings']
    from scipy.spatial import cKDTree
    block=target.read_text().split('vertices\n')[1].split('triangles\n')[0]
    a=np.array([[float(x) for x in line.split()[:18]] for line in block.strip().splitlines()])
    b=np.array([[x for k in ['position','normal','tangent','binormal','uv','uv2','uv3'] for x in v[k]] for v in mesh['vertices']])
    error=max(cKDTree(a).query(b)[0].max(),cKDTree(b).query(a)[0].max());assert len(a)==len(b) and error<.0002
    uv2=np.array([v['uv2'] for v in mesh['vertices']])*2048
    assert np.all(uv2>=[1280,384]) and np.all(uv2<=[1408,512])
    uv=np.array([v['uv'] for v in mesh['vertices']])*1024
    assert not np.any((uv[:,0]>=128)&(uv[:,0]<=256)&(uv[:,1]>=640)&(uv[:,1]<=768))
    from lxml import etree as E
    geo=parse(MOD/'Geometries'/f'{NAME}.geo')
    g=geo.find('m_Meshes/Element');g.find('m_Name').set('text',mesh['name'])
    for key,val in [('m_nBoundBoneCount',len(mesh['boneBindings'])),('m_nVertexCount',len(b)),('m_nPrimitiveCount',len(mesh['triangles']))]:g.find(key).text=str(val)
    group=g.find('m_Groups/Element');group.find('m_Name').set('text','CSC_ALL_Props_01');group.find('m_nFirstPrim').text='0';group.find('m_nPrims').text=str(len(mesh['triangles']))
    bones=geo.find('m_Bones');bones.clear()
    for bone in raw['models'][0]['bones']:E.SubElement(bones,'Element',text=bone['name'])
    geo.find('m_ModelName').set('text',raw['models'][0]['name'])
    save(geo,target.with_suffix('.geo'))
    ast=parse(MOD/'Assets'/f'{NAME}.ast')
    for e in ast.findall('.//m_MeshName'):assert e.get('text')=='CSC_ALL_Basket';e.set('text',mesh['name'])
    group=txt(g.find('m_Groups/Element'),'m_Name')
    for e in ast.findall('.//m_GroupName'):assert e.get('text')=='Material.001';e.set('text',group)
    # Instance identity and every state/placement setting intentionally retained.
    save(ast,OUT/'staged/Assets'/f'{NAME}.ast')
    write(OUT/'native-validation.json',dict(vertices=len(b),triangles=len(mesh['triangles']),bindings=mesh['boneBindings'],export_error=float(error),original_AO_reused=True))
    print('Native export/readback verified',len(b),'vertices',len(mesh['triangles']),'triangles')

def finalize():
    lib=json.loads((STAGE/'library.json').read_text());lib.update(release=RELEASE,content_revision=46,snapshot_path='Releases/'+RELEASE,
        surface_status='Newer basket reuses existing surfaces; legacy slot 41 available again.',AO_status='Newer basket uses original allocation; migration cell [1408,384,1536,512] available again.')
    lib['basket_well_migration']['source_masters']['Props/Tailors/CSC_TAILORS_Basket.blend']=sha(OUT/'masters'/f'{NAME}.blend')
    lib['basket_replacement']=dict(source=str(SOURCE),source_sha256=sha(SOURCE),reclaimed_surface_slot=41,reclaimed_AO_cell=[1408,384,1536,512],AE_placements_preserved=True)
    lib['files']={p.relative_to(STAGE).as_posix():sha(p) for p in STAGE.rglob('*') if p.is_file() and p.name!='library.json'};write(STAGE/'library.json',lib)
    import audit_art_orphans as audit
    for phase in ['before','after']:
        pantry=OUT/('cook-'+phase)/'pantry'
        for folder in audit.FOLDERS+['XLPs','ArtDefs']:
            for p in (MOD/folder).rglob('*'):
                if p.is_file():
                    dst=pantry/p.relative_to(MOD);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dst)
        if phase=='after':
            for p in (OUT/'staged').rglob('*'):
                if p.suffix in ['.ast','.geo','.fgx','.mtl','.tex','.dds']:
                    dst=pantry/p.relative_to(OUT/'staged');dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dst)
    print('Cook snapshots ready')

def cook():
    import cleanup_art_orphans as c
    c.OUT=OUT;c.cook(sys.argv[2])

def publish():
    assert not ARCHIVE.exists() and not (LIB/'Releases'/RELEASE).exists()
    for phase in ['before','after']:
        r=json.loads((OUT/('cook-'+phase)/'results/result.json').read_text());assert r['exit_code']==0 and r['blps']
    baseline=json.loads((OUT/'baseline.json').read_text())
    for p,h in baseline.items():assert sha(Path(p))==h,('Changed during preparation',p)
    assert json.loads((OUT/'source-validation.json').read_text())['error_count']==0
    files={p.relative_to(OUT/'staged').as_posix():p for p in (OUT/'staged').rglob('*') if p.suffix in ['.fgx','.geo','.ast','.tex','.dds']}
    cachepath=Path(os.environ['APPDATA'])/'AssetCloud/mod-Civ Supply Chains-asset-deps.json'
    cachebytes=cachepath.read_bytes();cache=json.loads(cachebytes.decode('utf-8-sig'))
    now=int(time.time()*1e7)+116444736000000000
    for e in cache['Files']:
        rel=e['Filename'].replace('\\','/').removeprefix('Civ Supply Chains/')
        if rel in files:e.update(Filesize=files[rel].stat().st_size,Timestamp=now)
    cache['Timestamp']=now
    ARCHIVE.mkdir(parents=True)
    archived={}
    def backup(src,rel):
        if not src.is_file():return
        dst=ARCHIVE/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
        assert sha(src)==sha(dst);archived[str(src)]=dict(path=Path(rel).as_posix(),sha256=sha(src))
    for rel in files:backup(MOD/rel,Path('mod-before')/rel)
    backup(cachepath,Path('registrations/AssetCloud-before.json'))
    backup(LIB/'CURRENT.json',Path('atlas-before/CURRENT.json'))
    shutil.copytree(LIB/'Current',ARCHIVE/'atlas-before/Current')
    for p in [DEST,DEST.with_suffix('.blend1')]:backup(p,Path('sources-before')/p.relative_to(ART))
    # Snapshot neighbouring images so the archived master remains portable.
    for p in (DEST.parent/'textures').glob('*'):
        if p.is_file():backup(p,Path('sources-before')/p.relative_to(ART))
    exports=DEST.parent/'exports'/NAME
    for p in exports.glob('*'):
        if p.is_file():backup(p,Path('sources-before')/p.relative_to(ART))
    retired=[DEST.with_suffix('.blend1')]+list((ART/'Props/_archive').glob('CSC_ALL_Basket.*'))+list((ART/'Props/_archive').glob('CSC_ALL_Basket_*.png'))
    retired=[p for p in retired if p.is_file()]
    for p in retired:backup(p,Path('sources-before')/p.relative_to(ART))
    write(ARCHIVE/'archive-manifest.json',archived)
    assert cachepath.read_bytes()==cachebytes
    shutil.copytree(STAGE,LIB/'Releases'/RELEASE)
    for rel,p in files.items():shutil.copy2(p,MOD/rel)
    shutil.copytree(STAGE,LIB/'Current',dirs_exist_ok=True)
    for rel in json.loads((OUT/'removed-library-files.json').read_text()):
        p=(LIB/'Current'/rel).resolve();assert p.is_relative_to((LIB/'Current').resolve())
        assert sha(p)==sha(ARCHIVE/'atlas-before/Current'/rel);p.unlink()
    write(LIB/'CURRENT.json',dict(release=RELEASE,current='Current',manifest='Current/library.json',snapshot='Releases/'+RELEASE,updated_on='2026-10-26',library_sha256=sha(LIB/'Current/library.json')))
    shutil.copy2(OUT/'masters'/f'{NAME}.blend',DEST)
    for p in (OUT/'masters/textures').glob('*.png'):
        dst=DEST.parent/'textures'/p.name
        if dst.exists():assert sha(dst)==sha(p)
        else:shutil.copy2(p,dst)
    exports.mkdir(exist_ok=True)
    for ext in ['.cn6','.fgx','.geo']:shutil.copy2(OUT/'staged/Geometries'/(NAME+ext),exports/(NAME+ext))
    for p in retired:
        p=p.resolve();assert p.is_relative_to(ART.resolve())
        record=archived[str(p)];assert sha(p)==record['sha256'] and sha(ARCHIVE/record['path'])==record['sha256'];p.unlink()
    cachepath.write_text(json.dumps(cache,separators=(',',':')),encoding='utf-8')
    write(OUT/'install-report.json',dict(archive=str(ARCHIVE),release=RELEASE,updated=list(files),archived_sources=[str(p) for p in retired],master=str(DEST)))
    print('Installed newer basket and r046; archived older basket master, exports and original source files.')

def verify():
    report=json.loads((OUT/'install-report.json').read_text());baseline=json.loads((OUT/'baseline.json').read_text());changed={str(MOD/rel) for rel in report['updated']};count=0
    for p,h in baseline.items():
        path=Path(p)
        if path.is_relative_to(MOD) and p not in changed:assert sha(path)==h,p;count+=1
    for rel in report['updated']:assert sha(MOD/rel)==sha(OUT/'staged'/rel)
    assert sha(SOURCE)==baseline[str(SOURCE)] and sha(DEST)==sha(OUT/'masters'/f'{NAME}.blend')
    assert (OUT/'installed-export'/f'{NAME}.cn6').read_bytes()==(OUT/'source-export'/f'{NAME}.cn6').read_bytes()
    lib=json.loads((LIB/'Current/library.json').read_text())
    assert sha(LIB/'Current/library.json')==json.loads((LIB/'CURRENT.json').read_text())['library_sha256']
    for rel,h in lib['files'].items():assert sha(LIB/'Current'/rel)==h and sha(LIB/'Releases'/RELEASE/rel)==h,rel
    for rel in json.loads((OUT/'removed-library-files.json').read_text()):assert not (LIB/'Current'/rel).exists()
    for p in report['archived_sources']:assert not Path(p).exists()
    for p,record in json.loads((ARCHIVE/'archive-manifest.json').read_text()).items():assert sha(ARCHIVE/record['path'])==record['sha256']
    import contextlib,io,audit_art_orphans as audit
    with contextlib.redirect_stdout(io.StringIO()):audit.run(OUT/'post-install-audit',False)
    audited=json.loads((OUT/'post-install-audit/audit.json').read_text());assert not audited['errors']
    # The basket AST changes only mesh/group bindings; all state flags are exact.
    from lxml import etree as E
    a=parse(ARCHIVE/'mod-before/Assets'/f'{NAME}.ast');b=parse(MOD/'Assets'/f'{NAME}.ast')
    for tag in ['m_MeshName','m_GroupName']:
        for old,new in zip(a.findall('.//'+tag),b.findall('.//'+tag)):old.set('text',new.get('text'))
    assert E.tostring(a)==E.tostring(b)
    cooked={phase:json.loads((OUT/('cook-'+phase)/'results/result.json').read_text())['blps'][0]['bytes'] for phase in ['before','after']}
    result=dict(release=RELEASE,unchanged_runtime_files=count,placements_and_state_flags_preserved=True,original_authored_source_preserved=True,
        surface_slot_freed=41,AO_cell_freed=[1408,384,1536,512],native=json.loads((OUT/'native-validation.json').read_text()),
        saved_source_export_exact=True,cooked_bytes=cooked,cooked_bytes_saved=cooked['before']-cooked['after'],unresolved=audited['unresolved'],native_game_review=False)
    write(OUT/'final-verification.json',result);write(ARCHIVE/'completed.json',result)
    for filename in ['install-report.json','atlas-preservation.json','native-validation.json','source-validation.json','installed-source-validation.json']:
        shutil.copy2(OUT/filename,ARCHIVE/filename)
    (ARCHIVE/'README.txt').write_text('Older Tailors basket archived — 26 October 2026\n\nThe active CSC_TAILORS_Basket now uses the newer authored 169-vertex master (351 exported vertices, 260 triangles), preserving the existing AE placements and state flags.\n\nThe superseded canonical master, backup, exports and portable texture snapshots are in sources-before/Props/Tailors. The earlier CSC_ALL_Basket source and paint files were moved from Props/_archive into sources-before/Props/_archive. Historical Textile Workshop revision sources remain untouched. Original runtime basket and changed atlas maps are in mod-before. The prior complete canonical shared atlas is in atlas-before.\n\nPublished shared atlas r046 frees surface slot 41 and AO cell [1408,384,1536,512]. The newer basket uses existing Shared_01 surfaces and its original AO cell [1280,384,1408,512]. Well tint and all other occupied pixels remain unchanged. XLP entries are unchanged. Both isolated native cooks passed; no live in-game review was performed.\n\nRestore selected backed-up files only after checking for later edits; do not blindly overwrite a newer atlas release or dependency cache.\n',encoding='utf-8')
    print(json.dumps(result,indent=2))

if __name__=='__main__':globals()[sys.argv[1]]()
