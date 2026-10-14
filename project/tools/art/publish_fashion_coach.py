"""Atlas packing and guarded publication for the Fashion House coach."""
from pathlib import Path
import json,hashlib,shutil,sys,subprocess,importlib.util,xml.etree.ElementTree as ET,os,tempfile,struct
from PIL import Image
import numpy as np
from fashion_coach_atlas import ROOT,LIB,OUT,STAGE,sha
ID='CSC_TAILORS_Fashion_Coach'
RELEASE='2026-10-13_Shared_01_r023'
MOD=ROOT/'Civ Supply Chains'

def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def pack_ao():
    raw=Image.open(OUT/'coach-raw-AO1024x512.png').convert('RGB')
    path=STAGE/'atlas/sources'/f'{ID}_AO256x128.png'
    raw.resize((256,128),Image.Resampling.LANCZOS).save(path)
    shutil.copy2(OUT/'coach-raw-AO1024x512.png',STAGE/'atlas/sources'/f'{ID}_RawAO1024x512.png')
    m=json.loads((STAGE/'atlas/quarter-ao-manifest.json').read_text())
    f=m['pages'][0]['quarters'][1]['families'][2]
    assert all(c['cell']==[1280,896,1536,1024] for c in f['allocations'] if c['id']==ID)
    f['allocations']=[c for c in f['allocations'] if c['id']!=ID]
    f['allocations'].append(dict(id=ID,cell=[1280,896,1536,1024],source=f'atlas/sources/{ID}_AO256x128.png',raw_source=f'atlas/sources/{ID}_RawAO1024x512.png',source_sha256=sha(path),bake='Cycles CPU 128 samples; self AO only; 1024x512 raw to 256x128, 8px raw dilation; 4% vertical/2% horizontal inset; no tone adjustment',reuse='Rigid isolated coach, no ground or building occluder'))
    (STAGE/'atlas/quarter-ao-manifest.json').write_text(json.dumps(m,indent=2))
    before=np.asarray(Image.open(LIB/'Current/textures/CSC_Props_Shared_01_AO.png').convert('RGB'))
    subprocess.run([sys.executable,ROOT/'project/tools/blender/pack_csc_prop_ao.py',STAGE],check=True)
    after=np.asarray(Image.open(STAGE/'textures/CSC_Props_Shared_01_AO.png').convert('RGB'))
    mask=np.ones(before.shape[:2],bool);mask[896:1024,1280:1536]=False
    assert np.array_equal(before[mask],after[mask])
    print('AO PACKED: prior live pixels preserved')

def stage_release():
    exp=json.loads((OUT/'export-report.json').read_text());assert exp['exported_vertices']<=1000
    validation=json.loads((OUT/'saved-validation.json').read_text());assert validation['automated_pass']
    assert validation['source_sha256']==sha(OUT/(ID+'.blend')),'Revalidate the final saved source'
    native=module('rack_parser',ROOT/'project/tools/art/install_tailor_garment_rack.py')
    a,va,ta=native.parse(OUT/(ID+'.cn6'));b,vb,tb=native.parse(OUT/(ID+'-roundtrip.cn6'))
    assert a==b==ID and len(va)==len(vb)==exp['exported_vertices'] and ta==tb
    residual=float(np.max(np.abs(np.array(va)-np.array(vb))));assert residual<1e-4,residual
    assert np.isfinite(np.asarray(va)).all()
    assert all(0<=i<len(va) for t in ta for i in t[:3])
    ast=ET.parse(OUT/(ID+'.ast')).getroot();geo=ET.parse(OUT/(ID+'.geo')).getroot()
    assert len(geo.findall('m_Meshes/Element'))==1
    assert geo.findtext('m_Meshes/Element/m_nVertexCount')==str(len(va))
    rows=ast.findall('.//m_GroupStates/Element');assert len(rows)==5
    for row in rows:
        state=row.find('m_StateName').get('text')
        values={v.find('m_ParamName').get('text'):v for v in row.findall('m_Values/m_Values/Element')}
        assert values['Visible'].findtext('m_bValue')==str(state in ('Worked','Unworked')).lower()
        assert values['Material'].find('m_ObjectName').get('text')=='CSC_ALL_Props_01'
        assert row.find('m_MeshName').get('text')==ID
    assert any(e.find('m_Value') is not None and e.find('m_Value').get('text')=='PERMANENT' for e in ast.findall('m_CookParams/m_Values/Element'))
    # Full source and exact prompt retained with the deterministic patch sources.
    shutil.copy2(OUT/'coach-paint-source.png',STAGE/'atlas/sources/coach-paint-source.png')
    (STAGE/'atlas/sources/coach-paint-provenance.json').write_text(json.dumps(dict(tool='Built-in image_gen',source='coach-paint-source.png',prompt='Create a flat orthographic base-color texture sheet for a low-poly Civilization VI aristocratic burgundy fashion coach. Square 1024x1024, opaque. Four equal square quadrants exactly 512 pixels each, no gaps, no labels, no text, no perspective. Top left: rich claret lacquered wooden coach panel, broad calm burgundy field with a restrained delicate antique-gold double-line inset rectangular border and elegant fine gold foliate scrollwork only near the bottom corners, center unadorned burgundy. Top right: dark charcoal black leather roof covering, restrained painted leather texture, very subtle long parallel seams, no buttons, no ornaments. Bottom left: a coach window framed in antique gold and claret at edges, dark warm recessed interior and two ivory silk curtains gathered toward the bottom sides, softly shaded vertical folds, a visible dark center gap, symmetrical, perfectly frontal, fill quadrant. Bottom right: warm antique gold/brass material swatch with restrained brushed painted grain, calm ochre gold, no white hot highlights. Art style digitally hand-painted strategy game texture, rich clear material color, selected abbreviated marks, subtle material variation, no photography, no scene shadow, no gradient spotlight, no artificial noise, clean fixed region boundaries. Texture surface only, not a rendering of a coach. Fine details must remain readable after each quadrant is reduced to 120 pixels.',processing='Four quadrants cropped at actual midpoint, packed to 120px interiors in slots 5,6,7,50 with 4px padding; companion normal flat, gloss and metalness semantic constant patches.'),indent=2))
    lib=json.loads((STAGE/'library.json').read_text())
    lib.update(release=RELEASE,accepted_on='2026-10-13',content_revision=23,snapshot_path='Releases/'+RELEASE,
        surface_status='Coach panel, leather, curtained window and antique brass added to slots 5,6,7,50; all older occupied rectangles unchanged.',
        AO_status='Coach AO rebaked after Henno requested removal of fine decorative geometry. All other r022 pixels, including Henno edits, preserved.',
        review_status='Assistant visual and static checks completed; Henno AE/in-game appearance review pending.')
    lib['source_FINAL_sha256']['Fashion Coach/revision-02/'+ID+'.blend']=sha(OUT/(ID+'.blend'))
    for n in ['validation.json','surface-validation.json']:
        (STAGE/n).write_text(json.dumps(dict(release=RELEASE,previous_occupied_surface_regions_preserved=True,henno_live_ao_pixels_preserved=True,coach_ao_cell=[1280,896,1536,1024],native_readback_max_error=residual,exported_vertices=len(va),saved_blend_validation_pass=True),indent=2))
    lib['files']={p.relative_to(STAGE).as_posix():sha(p) for p in STAGE.rglob('*') if p.is_file() and p.name!='library.json'}
    (STAGE/'library.json').write_text(json.dumps(lib,indent=2))
    ddsdir=OUT/'dds';ddsdir.mkdir(exist_ok=True)
    converter=module('dds_tools',ROOT/'project/tools/blender/scene_export/export_scene.py')
    for slot in ['B','N','G','M','AO']:
        name='CSC_Props_Shared_01_'+slot
        tex=ET.parse(MOD/'Textures'/(name+'.tex'))
        fmt=tex.findtext('m_ExportSettings/ePixelformat').removeprefix('PF_')
        size=list(Image.open(STAGE/'textures'/(name+'.png')).size)
        args=[str(ROOT/'project/tools/directxtex/texconv.exe'),'-nologo','-y','-m','0','-f',fmt,'-o',str(ddsdir),'--ignore-srgb']
        if slot=='B':args+=['-srgb']
        args+=[str(STAGE/'textures'/(name+'.png'))]
        r=subprocess.run(args,capture_output=True,text=True);(OUT/(name+'-dds.log')).write_text(r.stdout+r.stderr);assert r.returncode==0,r.stderr
        dest=ddsdir/(name+'.dds');spec={'format':fmt,'size':size,'slot':slot}
        if fmt=='R8_UNORM':converter.normalize_ao_dds(dest,spec,MOD/'Textures'/(name+'.dds'))
        converter.validate_dds(dest,spec)
        if fmt=='R8_UNORM':
            pix=np.frombuffer(dest.read_bytes(),np.uint8,offset=128,count=size[0]*size[1]).reshape(size[1],size[0])
            assert np.array_equal(pix,np.array(Image.open(STAGE/'textures'/(name+'.png')).convert('RGB'))[:,:,0])
    (OUT/'preinstall-report.json').write_text(json.dumps(dict(native_readback_max_error=residual,vertices=len(va),triangles=len(ta),dds_checked=True,authoring_pass=True),indent=2))
    print('RELEASE STAGED',RELEASE,len(va),'vertices',len(ta),'triangles')

def publish():
    pre=json.loads((OUT/'preinstall-report.json').read_text());assert pre['authoring_pass']
    baseline=json.loads((OUT/'live-atlas-baseline.json').read_text())
    assert {Path(p).as_posix() for p in baseline}=={p.relative_to(LIB/'Current').as_posix() for p in (LIB/'Current').rglob('*') if p.is_file()},'Live atlas inventory changed'
    assert all((LIB/'Current'/p).is_file() and sha(LIB/'Current'/p)==h for p,h in baseline.items()),'Live atlas changed during work; reconcile before publishing'
    assert json.loads((LIB/'CURRENT.json').read_text())['release']=='2026-10-05_Shared_01_r021'
    release=LIB/'Releases'/RELEASE;assert not release.exists()
    backup=OUT/'before-publication';backup.mkdir(exist_ok=True)
    shutil.copytree(LIB/'Current',backup/'Current');shutil.copy2(LIB/'CURRENT.json',backup/'CURRENT.json')
    protected={p:sha(p) for p in (MOD/'Assets').glob('*.ast') if p.stem!=ID}
    material=MOD/'Materials/CSC_ALL_Props_01.mtl';material_hash=sha(material)
    files=[]
    for folder,ext in [('Assets','.ast'),('Geometries','.geo'),('Geometries','.fgx')]:
        dest=MOD/folder/(ID+ext);assert not dest.exists();files.append((OUT/(ID+ext),dest))
    for src in (OUT/'dds').glob('*.dds'):
        dest=MOD/'Textures'/src.name;shutil.copy2(dest,backup/src.name);files.append((src,dest))
    xlp=MOD/'XLPs/CSC_Tilebases.xlp';raw=xlp.read_bytes();shutil.copy2(xlp,backup/xlp.name)
    assert ID.encode() not in raw and raw.count(b'\t</m_Entries>')==1
    insert=('\t\t<Element>\n\t\t\t<m_EntryID text="'+ID+'"/>\n\t\t\t<m_ObjectName text="'+ID+'"/>\n\t\t</Element>\n').encode()
    updated=raw.replace(b'\t</m_Entries>',insert+b'\t</m_Entries>');ET.fromstring(updated)
    # Immutable release first, followed by stable Current filenames and pointer.
    shutil.copytree(STAGE,release);shutil.copytree(STAGE,LIB/'Current',dirs_exist_ok=True)
    pointer=dict(release=RELEASE,current='Current',manifest='Current/library.json',snapshot='Releases/'+RELEASE,updated_on='2026-10-13',library_sha256=sha(LIB/'Current/library.json'))
    (LIB/'CURRENT.json').write_text(json.dumps(pointer,indent=2))
    for src,dest in files:shutil.copy2(src,dest)
    xlp.write_bytes(updated)
    source=Path(r'C:\Users\Shadow\Desktop\Working Files\3D Art\Props\Tailors\Fashion Coach\revision-01');assert not source.exists();source.mkdir(parents=True)
    for ext in ['.blend','.cn6']:shutil.copy2(OUT/(ID+ext),source/(ID+ext))
    shutil.copytree(OUT/'textures',source/'textures')
    for name in ['coach-preview.png','export-report.json','saved-validation.json','preinstall-report.json']:shutil.copy2(OUT/name,source/name)
    assert all(sha(p)==h for p,h in protected.items()) and sha(material)==material_hash
    assert all(sha(src)==sha(dest) for src,dest in files)
    manifest=json.loads((release/'library.json').read_text())
    assert all(sha(release/p)==h and sha(LIB/'Current'/p)==h for p,h in manifest['files'].items())
    report=dict(asset_id=ID,source=str(source/(ID+'.blend')),atlas_release=RELEASE,existing_ae_assemblies_preserved=len(protected),material_unchanged=True,vertices=pre['vertices'],triangles=pre['triangles'],native_readback_max_error=pre['native_readback_max_error'],files=[str(d) for s,d in files],cook_tested=False,in_game_tested=False)
    (OUT/'install-report.json').write_text(json.dumps(report,indent=2))
    # Merge only the new asset/geometry dependency records, retaining all AE data.
    cache=module('coach_cache',ROOT/'project/tools/art/install_tailor_garment_rack.py');cache.ID=ID;cache.OUT=OUT;cache.register_cache()
    print('PUBLISHED',json.dumps(report))

def resume_install():
    """Finish after an AE-mapped DDS prevented in-place copying; replace atomically."""
    assert json.loads((LIB/'CURRENT.json').read_text())['release']==RELEASE
    manifest=json.loads((STAGE/'library.json').read_text())
    assert all(sha(LIB/'Current'/p)==h and sha(LIB/'Releases'/RELEASE/p)==h for p,h in manifest['files'].items())
    pre=json.loads((OUT/'preinstall-report.json').read_text())
    backup=OUT/'before-publication'
    protected={p:sha(p) for p in (MOD/'Assets').glob('*.ast') if p.stem!=ID}
    copies=[(OUT/(ID+e),MOD/f/(ID+e)) for f,e in [('Assets','.ast'),('Geometries','.geo'),('Geometries','.fgx')]]
    for src,dest in copies:assert sha(src)==sha(dest)
    for src in (OUT/'dds').glob('*.dds'):
        dest=MOD/'Textures'/src.name
        assert (backup/src.name).exists()
        if sha(src)!=sha(dest):
            fd,tmp=tempfile.mkstemp(prefix=src.stem+'-coach-',suffix='.tmp',dir=dest.parent);os.close(fd)
            try:shutil.copy2(src,tmp);os.replace(tmp,dest)
            finally:
                if Path(tmp).exists():Path(tmp).unlink()
        assert sha(src)==sha(dest)
        copies.append((src,dest))
    xlp=MOD/'XLPs/CSC_Tilebases.xlp';raw=xlp.read_bytes()
    if ID.encode() not in raw:
        assert raw.count(b'\t</m_Entries>')==1
        insert=('\t\t<Element>\n\t\t\t<m_EntryID text="'+ID+'"/>\n\t\t\t<m_ObjectName text="'+ID+'"/>\n\t\t</Element>\n').encode()
        updated=raw.replace(b'\t</m_Entries>',insert+b'\t</m_Entries>');ET.fromstring(updated);xlp.write_bytes(updated)
    source=Path(r'C:\Users\Shadow\Desktop\Working Files\3D Art\Props\Tailors\Fashion Coach\revision-01');source.mkdir(parents=True,exist_ok=True)
    for ext in ['.blend','.cn6']:
        dest=source/(ID+ext);assert not dest.exists() or sha(dest)==sha(OUT/(ID+ext));shutil.copy2(OUT/(ID+ext),dest)
    shutil.copytree(OUT/'textures',source/'textures',dirs_exist_ok=True)
    for name in ['coach-preview.png','export-report.json','saved-validation.json','preinstall-report.json']:shutil.copy2(OUT/name,source/name)
    assert all(sha(p)==h for p,h in protected.items())
    report=dict(asset_id=ID,source=str(source/(ID+'.blend')),atlas_release=RELEASE,existing_ae_assemblies_preserved=len(protected),vertices=pre['vertices'],triangles=pre['triangles'],native_readback_max_error=pre['native_readback_max_error'],files=[str(d) for s,d in copies],atomic_dds_install=True,cook_tested=False,in_game_tested=False)
    (OUT/'install-report.json').write_text(json.dumps(report,indent=2))
    cache=module('coach_cache',ROOT/'project/tools/art/install_tailor_garment_rack.py');cache.ID=ID;cache.OUT=OUT;cache.register_cache()
    print('PUBLISHED',json.dumps(report))

def publish_revision():
    """Install the requested simplified revision, preserving the prior delivery."""
    assert json.loads((LIB/'CURRENT.json').read_text())['release']=='2026-10-13_Shared_01_r022'
    pre=json.loads((OUT/'preinstall-report.json').read_text())
    validation=json.loads((OUT/'saved-validation.json').read_text())
    assert validation['automated_pass'] and validation['source_sha256']==sha(OUT/(ID+'.blend'))
    prior=LIB/'Releases/2026-10-13_Shared_01_r022'
    prior_manifest=json.loads((prior/'library.json').read_text())
    assert all(sha(LIB/'Current'/p)==h for p,h in prior_manifest['files'].items()),'New live atlas edits require reconciliation'
    backup=OUT/'before-r023';assert not backup.exists();backup.mkdir()
    shutil.copy2(LIB/'CURRENT.json',backup/'CURRENT.json')
    protected={p:sha(p) for p in (MOD/'Assets').glob('*.ast') if p.stem!=ID}
    copies=[(OUT/(ID+e),MOD/f/(ID+e)) for f,e in [('Assets','.ast'),('Geometries','.geo'),('Geometries','.fgx')]]
    copies += [(p,MOD/'Textures'/p.name) for p in (OUT/'dds').glob('*.dds')]
    for src,dest in copies:shutil.copy2(dest,backup/dest.name)
    release=LIB/'Releases'/RELEASE;assert not release.exists();shutil.copytree(STAGE,release)
    shutil.copytree(STAGE,LIB/'Current',dirs_exist_ok=True)
    (LIB/'CURRENT.json').write_text(json.dumps(dict(release=RELEASE,current='Current',manifest='Current/library.json',snapshot='Releases/'+RELEASE,updated_on='2026-10-13',library_sha256=sha(LIB/'Current/library.json')),indent=2))
    for src,dest in copies:
        if sha(src)!=sha(dest):
            fd,tmp=tempfile.mkstemp(prefix=src.stem+'-coach-',suffix='.tmp',dir=dest.parent);os.close(fd)
            try:shutil.copy2(src,tmp);os.replace(tmp,dest)
            finally:
                if Path(tmp).exists():Path(tmp).unlink()
        assert sha(src)==sha(dest)
    source=Path(r'C:\Users\Shadow\Desktop\Working Files\3D Art\Props\Tailors\Fashion Coach\revision-02');assert not source.exists();source.mkdir(parents=True)
    for ext in ['.blend','.cn6']:shutil.copy2(OUT/(ID+ext),source/(ID+ext))
    shutil.copytree(OUT/'textures',source/'textures')
    for name in ['coach-preview.png','export-report.json','saved-validation.json','preinstall-report.json']:shutil.copy2(OUT/name,source/name)
    assert all(sha(p)==h for p,h in protected.items())
    manifest=json.loads((release/'library.json').read_text())
    assert all(sha(release/p)==h and sha(LIB/'Current'/p)==h for p,h in manifest['files'].items())
    report=dict(asset_id=ID,source=str(source/(ID+'.blend')),atlas_release=RELEASE,existing_ae_assemblies_preserved=len(protected),vertices=pre['vertices'],triangles=pre['triangles'],native_readback_max_error=pre['native_readback_max_error'],files=[str(d) for s,d in copies],atomic_install=True,removed_fine_trim_geometry=True,cook_tested=False,in_game_tested=False)
    (OUT/'install-report.json').write_text(json.dumps(report,indent=2))
    cache=module('coach_cache',ROOT/'project/tools/art/install_tailor_garment_rack.py');cache.ID=ID;cache.OUT=OUT;cache.register_cache()
    print('PUBLISHED',json.dumps(report))

def verify_live():
    install=json.loads((OUT/'install-report.json').read_text());source=Path(install['source'])
    validation=json.loads((OUT/'saved-validation.json').read_text())
    assert validation['automated_pass'] and sha(source)==validation['source_sha256']
    assert all(sha(p)==sha(source.parent/'textures'/p.name) for p in (OUT/'textures').glob('*.png'))
    manifest=json.loads((LIB/'Current/library.json').read_text())
    assert manifest['release']==RELEASE and all(sha(LIB/'Current'/p)==h for p,h in manifest['files'].items())
    converter=module('live_dds_tools',ROOT/'project/tools/blender/scene_export/export_scene.py')
    textures=[]
    for staged in (OUT/'dds').glob('*.dds'):
        live=MOD/'Textures'/staged.name;old=staged.read_bytes();new=live.read_bytes()
        w,h=struct.unpack_from('<I',new,16)[0],struct.unpack_from('<I',new,12)[0]
        bpp=struct.unpack_from('<I',new,88)[0]//8;slot=staged.stem.rsplit('_',1)[1]
        fmt='R8_UNORM' if bpp==1 else 'R8G8B8A8_UNORM'
        converter.validate_dds(live,dict(format=fmt,size=[w,h],slot=slot))
        n=w*h*bpp;assert old[128:128+n]==new[128:128+n],staged.name
        tex=ET.parse(live.with_suffix('.tex'))
        assert tex.findtext('m_ExportSettings/ePixelformat')=='PF_'+fmt
        assert Path(tex.find('m_SourceFilePath').get('text'))==LIB/'Current/textures'/(staged.stem+'.png')
        textures.append(dict(name=staged.name,full_resolution_pixels_identical=True,format=fmt,dimensions=[w,h],complete_mips=True,ae_reimported=old!=new,installed_sha256=sha(live)))
    for folder,ext in [('Assets','.ast'),('Geometries','.geo'),('Geometries','.fgx')]:assert sha(OUT/(ID+ext))==sha(MOD/folder/(ID+ext))
    entries=ET.parse(MOD/'XLPs/CSC_Tilebases.xlp').findall('m_Entries/Element')
    assert sum(e.find('m_EntryID').get('text')==ID for e in entries)==1
    result=dict(source_unchanged_after_validation=True,portable_textures_match=True,release_hashes_match=True,native_geometry_matches=True,vertices=install['vertices'],triangles=install['triangles'],textures=textures,ae_reimport_note='AE rewrote DDS headers/lower mips; every full-resolution pixel remains identical to checked staged output. This does not establish asset appearance or package cooking.')
    (OUT/'final-live-verification.json').write_text(json.dumps(result,indent=2))
    print('FINAL VERIFIED:',install['vertices'],'vertices,',install['triangles'],'triangles;',RELEASE,'; all live full-resolution texture pixels match')

if __name__=='__main__':
    if '--pack-ao' in sys.argv:pack_ao()
    elif '--stage-release' in sys.argv:stage_release()
    elif '--publish' in sys.argv:publish()
    elif '--resume-install' in sys.argv:resume_install()
    elif '--publish-revision' in sys.argv:publish_revision()
    elif '--verify-live' in sys.argv:verify_live()
