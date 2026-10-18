"""Add generated straight cobbles to free shared slot30, preserving occupied pixels."""
from cafe_atlas import *
import subprocess, xml.etree.ElementTree as ET
import numpy as np
from PIL import Image, ImageFilter
ID='CSC_ALL_Stage_4_Cobble_Decals'
SLOT=30
NAME='cafe_straight_cobbles'
RELEASE_ID='2026-10-17_Shared_01_r034'
GEN=Path('C:/Users/Shadow/.codex/generated_images/01a149b7-e357-7eb1-b5f3-f085ee00cccf/exec-ec1fa6d9-7c45-41ca-bedd-0554b19306cf.png')
MOD=ROOT/'Civ Supply Chains'

def stage():
    assert not STAGE.exists()
    shutil.copytree(SHARED/'Current',STAGE)
    baseline={str(p.relative_to(SHARED/'Current')):sha(p) for p in (SHARED/'Current').rglob('*') if p.is_file()}
    (OUT/'atlas-baseline.json').write_text(json.dumps(dict(pointer=json.loads((SHARED/'CURRENT.json').read_text()),files=baseline),indent=2))
    manifest=json.loads((STAGE/'atlas/manifest.json').read_text())
    assert SLOT not in {r['slot'] for r in manifest['regions']}
    raw=STAGE/'atlas/sources/cafe_straight_cobbles_imagegen.png';shutil.copy2(GEN,raw)
    shutil.copy2(raw,SOURCE/'textures/CSC_Cafe_Straight_Cobbles_Source.png')
    shutil.copy2(ROOT/'project/tools/art/cafe_new_cobbles_prompt.txt',STAGE/'atlas/sources/cafe_straight_cobbles_prompt.txt')
    b=Image.open(raw).convert('RGB').resize((120,120),Image.Resampling.LANCZOS)
    h=np.asarray(b.convert('L').filter(ImageFilter.GaussianBlur(.6)),dtype=float)/255
    dy,dx=np.gradient(h);n=np.stack((-dx*.6,dy*.6,np.ones_like(h)),axis=2);n/=np.linalg.norm(n,axis=2,keepdims=True)
    maps={'B':b,'N':Image.fromarray(np.uint8(np.clip((n*.5+.5)*255,0,255))),'G':Image.new('RGB',(120,120),(20,20,20)),'M':Image.new('RGB',(120,120),(0,0,0))}
    x,y=SLOT%8*128,SLOT//8*128;sources={}
    for k,patch in maps.items():
        src=STAGE/'atlas/sources'/f'{NAME}_{k}_packed.png';patch.save(src);sources[k]=src.relative_to(STAGE/'atlas').as_posix()
        target=STAGE/'textures'/f'CSC_Props_Shared_01_{k}.png';im=Image.open(target).convert('RGB')
        im.paste(Image.fromarray(np.pad(np.array(patch),((4,4),(4,4),(0,0)),mode='edge')),(x,y));im.save(target)
    manifest['regions'].append(dict(id=SLOT,slot=SLOT,name=NAME,family='shared_paving',bounds=[x+4,y+4,x+124,y+124],sources=sources,provenance='Built-in ImageGen exec-ec1fa6d9; source in sources/cafe_straight_cobbles_imagegen.png; straight orthographic running bond, technical normal/scalar companions.'))
    manifest['reserved_slots']=[s for s in manifest['reserved_slots'] if s!=SLOT]
    manifest.update(content_revision=34,cafe_revision=RELEASE_ID,change_note='ImageGen straight cobbles added to verified empty surface slot30; occupied surfaces and all AO unchanged.')
    manifest['production_sha256']={k:sha(STAGE/'textures'/f'CSC_Props_Shared_01_{k}.png') for k in 'BNGM'}
    (STAGE/'atlas/manifest.json').write_text(json.dumps(manifest,indent=2))
    hashes={p.name:sha(p) for p in (STAGE/'textures').glob('*.png')}
    subprocess.run([sys.executable,STAGE/'scripts/pack_cafe_additions.py'],check=True)
    assert all(sha(STAGE/'textures'/name)==h for name,h in hashes.items()),'Rebuild changed unrelated maps'
    for k in 'BNGM':shutil.copy2(STAGE/'textures'/f'CSC_Props_Shared_01_{k}.png',SOURCE/'textures'/f'CSC_Props_Shared_01_{k}.png')
    print('Staged ImageGen cobbles in free slot30; deterministic rebuild passed.')

def publish():
    from publish_cafe_props import module
    from verify_cafe_install import decode_top
    assert json.loads((OUT/'install-report.json').read_text())['installed']
    baseline=json.loads((OUT/'atlas-baseline.json').read_text())
    assert json.loads((SHARED/'CURRENT.json').read_text())==baseline['pointer']
    assert all(sha(SHARED/'Current'/p)==h for p,h in baseline['files'].items())
    x,y=SLOT%8*128,SLOT//8*128;mask=np.ones((1024,1024),bool);mask[y:y+128,x:x+128]=False
    changed={f'textures/CSC_Props_Shared_01_{k}.png' for k in 'BNGM'}
    for rel,h in baseline['files'].items():
        rel=Path(rel).as_posix()
        if rel in changed:
            a=np.array(Image.open(SHARED/'Current'/rel).convert('RGB'));b=np.array(Image.open(STAGE/rel).convert('RGB'));assert np.array_equal(a[mask],b[mask])
        elif rel not in ['atlas/manifest.json','library.json']:assert sha(STAGE/rel)==h,rel
    backup=OUT/'before-atlas';backup.mkdir(exist_ok=True)
    converter=module('cafe_cobble_dds',ROOT/'project/tools/blender/scene_export/export_scene.py')
    for k in 'BNGM':
        name='CSC_Props_Shared_01_'+k;target=MOD/'Textures'/(name+'.dds');shutil.copy2(target,backup/target.name)
        fmt=ET.parse(MOD/'Textures'/(name+'.tex')).findtext('m_ExportSettings/ePixelformat').removeprefix('PF_')
        args=[str(ROOT/'project/tools/directxtex/texconv.exe'),'-nologo','-y','-m','0','-f',fmt,'-o',str(OUT),'--ignore-srgb']+(['-srgb'] if k=='B' else [])+[str(STAGE/'textures'/(name+'.png'))]
        result=subprocess.run(args,capture_output=True,text=True);assert result.returncode==0
        (OUT/(name+'-dds.log')).write_text(result.stdout+result.stderr)
        spec=dict(format=fmt,size=[1024,1024],slot=k)
        if fmt=='R8_UNORM':converter.normalize_ao_dds(OUT/(name+'.dds'),spec,target)
        converter.validate_dds(OUT/(name+'.dds'),spec)
        decoded=decode_top(OUT/(name+'.dds'));expected=np.array(Image.open(STAGE/'textures'/(name+'.png')).convert('L' if decoded.ndim==2 else 'RGB'))
        assert np.max(np.abs(decoded.astype(int)-expected.astype(int)))<=1
    lib=json.loads((STAGE/'library.json').read_text());lib.update(release=RELEASE_ID,content_revision=34,snapshot_path='Releases/'+RELEASE_ID,surface_status='ImageGen orthographic cobbles in previously empty slot30. All previous surfaces and AO preserved.')
    lib['source_FINAL_sha256']['BAKERS/Cafe_Regular_20261017/'+ID+'.blend']=sha(SOURCE/(ID+'.blend'))
    lib['files']={p.relative_to(STAGE).as_posix():sha(p) for p in STAGE.rglob('*') if p.is_file() and p.name!='library.json'}
    (STAGE/'library.json').write_text(json.dumps(lib,indent=2))
    release=SHARED/'Releases'/RELEASE_ID;assert not release.exists()
    shutil.copy2(SHARED/'CURRENT.json',backup/'CURRENT.json')
    shutil.copytree(STAGE,release);shutil.copytree(STAGE,SHARED/'Current',dirs_exist_ok=True)
    (SHARED/'CURRENT.json').write_text(json.dumps(dict(release=RELEASE_ID,current='Current',manifest='Current/library.json',snapshot='Releases/'+RELEASE_ID,updated_on='2026-10-17',library_sha256=sha(STAGE/'library.json')),indent=2))
    for k in 'BNGM':
        name='CSC_Props_Shared_01_'+k;target=MOD/'Textures'/(name+'.dds');shutil.copy2(OUT/(name+'.dds'),target)
        actual=decode_top(target);expected=np.array(Image.open(STAGE/'textures'/(name+'.png')).convert('L' if actual.ndim==2 else 'RGB'));assert np.max(np.abs(actual.astype(int)-expected.astype(int)))<=1
    for p in STAGE.rglob('*'):
        if p.is_file():assert sha(p)==sha(SHARED/'Current'/p.relative_to(STAGE))==sha(release/p.relative_to(STAGE))
    report=dict(release=RELEASE_ID,slot=SLOT,occupied_surface_pixels_preserved=True,all_AO_opacity_emission_unchanged=True,rebuild_hashes_match=True,generated_source=str(SHARED/'Current/atlas/sources/cafe_straight_cobbles_imagegen.png'),installed=True)
    (OUT/'atlas-install-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))

if __name__=='__main__':
    if sys.argv[1]=='stage':stage()
    elif sys.argv[1]=='publish':publish()
