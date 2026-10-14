"""Publish an isolated mustard textile and UV-only Fashion House dress edit."""
from pathlib import Path
import json,hashlib,shutil,subprocess,sys,copy,importlib.util,os,struct
from PIL import Image
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
LIB=Path(r'C:\Users\Shadow\Desktop\Working Files\3D Art\Textures\CSC_Props')
OUT=Path(r'C:\Users\Shadow\Desktop\Codex\Fashion-dress-mustard-20261013')
SOURCE=Path(r'C:\Users\Shadow\Desktop\Working Files\3D Art\TAILORS\Fashion House\revision-12-garden-path')
STAGE=OUT/'atlas-release'
MOD=ROOT/'Civ Supply Chains'
RELEASE='2026-10-13_Shared_01_r024'
GEN=Path(r'C:\Users\Shadow\.codex\generated_images\01a1364e-bf69-7d52-975a-263678e15aa4\exec-719f0c1f-3868-4e8c-a735-6ca8cf91fbef.png')
NAMES=['CSC_TAILORS_Fashion_House_Fitting','CSC_TAILORS_Fashion_House']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,data):p.write_text(json.dumps(data,indent=2))
def stage():
    assert not STAGE.exists()
    shutil.copytree(LIB/'Current',STAGE)
    write(OUT/'baseline.json',{p.relative_to(LIB/'Current').as_posix():sha(p) for p in (LIB/'Current').rglob('*') if p.is_file()})
    protected=list((MOD/'Assets').glob('*.ast'))+list((MOD/'Geometries').glob('*.geo'))+[MOD/'XLPs/CSC_Tilebases.xlp',MOD/'Materials/CSC_ALL_Props_01.mtl']
    write(OUT/'protected.json',{str(p):sha(p) for p in protected})
    m=json.loads((STAGE/'atlas/manifest.json').read_text());assert not any(r['slot']==28 for r in m['regions'])
    old=next(r for r in m['regions'] if r['slot']==23)
    new=copy.deepcopy(old);new.update(id=max(r['id'] for r in m['regions'])+1,name='embroidered_mustard',slot=28,bounds=[516,388,636,508])
    for k in 'BNGM':
        target=STAGE/'atlas/sources'/f'embroidered_mustard_{k}.png'
        shutil.copy2(GEN if k=='B' else STAGE/'atlas'/old['sources'][k],target)
        new['sources'][k]='sources/'+target.name
    m['regions'].append(new);write(STAGE/'atlas/manifest.json',m)
    write(STAGE/'atlas/sources/embroidered_mustard_provenance.json',dict(tool='Built-in image_gen',edit_target='embroidered_ivory_B.png',colour_reference='ochre_B.png',prompt='Precise color edit of Image 1, a flat cloth texture for an existing 3D dress. Image 1 is the EDIT TARGET and exact pattern/layout authority. Image 2 is a COLOUR REFERENCE ONLY. Change the ivory background cloth in Image 1 to rich muted mustard yellow/ochre matching the overall hue and brightness of Image 2. Preserve the three existing vertical embroidered borders, their exact positions, widths, and all leaf motifs and weave detail. Make the embroidery a lighter warm antique gold/cream so it remains quietly visible against mustard cloth. Do not copy the folds from image 2, do not add folds, rearrange patterns, change scale, move borders, add embellishment, or add lighting. Retain square, flat edge-to-edge texture, no perspective. This must remain the same textile design with a changed fabric colour.',companions='Existing ivory embroidery N/G/M retained; same textile construction, colour-only change. Sleeves reuse existing ochre region22.'))
    subprocess.run([sys.executable,STAGE/'scripts/pack_atlas.py'],check=True)
    for k in 'BNGM':
        a=np.asarray(Image.open(STAGE/'textures'/f'CSC_Props_Shared_01_{k}.png').convert('RGB'))
        b=np.asarray(Image.open(LIB/'Current/textures'/f'CSC_Props_Shared_01_{k}.png').convert('RGB'))
        mask=np.ones(a.shape[:2],bool);mask[384:512,512:640]=False
        assert np.array_equal(a[mask],b[mask]),k
    for n in ['CSC_Props_Shared_01_AO.png','CSC_Props_Shared_02_AO.png','CSC_Props_Shared_01_E.png']:
        assert sha(STAGE/'textures'/n)==sha(LIB/'Current/textures'/n)
    for name in NAMES:
        dest=OUT/'before-source'/(name+'.blend');dest.parent.mkdir(exist_ok=True);shutil.copy2(SOURCE/dest.name,dest)
    shutil.copytree(SOURCE/'textures',OUT/'before-source/textures')
    shutil.copytree(SOURCE/'textures',OUT/'textures')
    for k in 'BNGM':shutil.copy2(STAGE/'textures'/f'CSC_Props_Shared_01_{k}.png',OUT/'textures'/f'CSC_Props_Shared_01_{k}.png')
    print('Staged one new cloth region; all previous pixels and AO unchanged.')
def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def prepare_release():
    a=(OUT/'before.cn6').read_text().splitlines();b=(OUT/'after.cn6').read_text().splitlines()
    assert len(a)==len(b);mesh='';vertices=False;changes=0
    for x,y in zip(a,b):
        if x.startswith('mesh:'):mesh=x
        if x=='vertices':vertices=True
        if x=='triangles':vertices=False
        if x==y:continue
        if x.startswith('//'):continue
        assert vertices and ('Front_Ivory_Gown_Bell' in mesh or 'Ivory_Rounded_Sleeve' in mesh),(mesh,x,y)
        old=x.split();new=y.split();assert len(old)==len(new)
        assert old[:12]==new[:12] and old[14:]==new[14:],mesh
        gown='Gown_Bell' in mesh
        assert abs(float(new[12])-float(old[12])-(-.375 if gown else .75))<1e-6
        assert abs(float(new[13])-float(old[13])-(.125 if gown else -.125))<1e-6
        changes+=1
    assert changes==141,changes
    validation=json.loads((OUT/'source-validation.json').read_text())
    for name in NAMES:assert validation[name]['sha256']==sha(OUT/(name+'.blend'))
    lib=json.loads((STAGE/'library.json').read_text())
    lib.update(release=RELEASE,accepted_on='2026-10-13',content_revision=24,snapshot_path='Releases/'+RELEASE,
      surface_status='Mustard embroidery added in previously unused slot28; all prior pixels preserved. Fashion House gown uses28, sleeves reuse ochre22.',
      AO_status='All r023 AO bytes unchanged. Colour-only dress UV1 update; UV2 untouched.',
      review_status='Saved source/native readback parity and assistant close-up visual checks passed; AE/game appearance review pending.')
    for name in NAMES:lib['source_FINAL_sha256']['Fashion House/revision-12-garden-path/'+name+'.blend']=sha(OUT/(name+'.blend'))
    proof=dict(release=RELEASE,previous_surface_pixels_preserved=True,all_AO_unchanged=True,native_vertices_with_only_UV0_changes=changes,all_native_geometry_rig_topology_other_UVs_unchanged=True,source_saved_parity_verified=True)
    for n in ['validation.json','surface-validation.json']:write(STAGE/n,proof)
    lib['files']={p.relative_to(STAGE).as_posix():sha(p) for p in STAGE.rglob('*') if p.is_file() and p.name!='library.json'}
    write(STAGE/'library.json',lib)
    ddsdir=OUT/'dds';ddsdir.mkdir(exist_ok=True)
    converter=module('dds_tools',ROOT/'project/tools/blender/scene_export/export_scene.py')
    for k in 'BNGM':
        name='CSC_Props_Shared_01_'+k;fmt='R8_UNORM' if k in 'GM' else 'R8G8B8A8_UNORM'
        args=[str(ROOT/'project/tools/directxtex/texconv.exe'),'-nologo','-y','-m','0','-f',fmt,'-o',str(ddsdir),'--ignore-srgb']
        if k=='B':args+=['-srgb']
        r=subprocess.run(args+[str(STAGE/'textures'/(name+'.png'))],capture_output=True,text=True);assert r.returncode==0,r.stderr
        path=ddsdir/(name+'.dds');spec=dict(format=fmt,size=[1024,1024],slot=k)
        if k in 'GM':converter.normalize_ao_dds(path,spec,MOD/'Textures'/path.name)
        converter.validate_dds(path,spec)
    write(OUT/'prepublication.json',proof);print('Verified native UV-only change on 141 existing vertices; release and DDS staged.')
def atomic_copy(src,dest):
    tmp=dest.with_name(dest.name+'.mustard-tmp');assert not tmp.exists();shutil.copy2(src,tmp);os.replace(tmp,dest)
def publish():
    proof=json.loads((OUT/'prepublication.json').read_text());assert proof['source_saved_parity_verified']
    baseline=json.loads((OUT/'baseline.json').read_text());assert all(sha(LIB/'Current'/p)==h for p,h in baseline.items())
    assert json.loads((LIB/'CURRENT.json').read_text())['release']=='2026-10-13_Shared_01_r023'
    protected=json.loads((OUT/'protected.json').read_text());assert all(sha(Path(p))==h for p,h in protected.items())
    for name in NAMES:assert sha(SOURCE/(name+'.blend'))==sha(OUT/'before-source'/(name+'.blend'))
    for p in (OUT/'before-source/textures').glob('*'):
        if p.is_file():assert sha(SOURCE/'textures'/p.name)==sha(p)
    backup=OUT/'before-publication';backup.mkdir();shutil.copytree(LIB/'Current',backup/'Current');shutil.copy2(LIB/'CURRENT.json',backup/'CURRENT.json')
    fgx=MOD/'Geometries/CSC_TAILORS_Fashion_House_Fitting.fgx';shutil.copy2(fgx,backup/fgx.name)
    for p in (OUT/'dds').glob('*.dds'):shutil.copy2(MOD/'Textures'/p.name,backup/p.name)
    release=LIB/'Releases'/RELEASE;assert not release.exists();shutil.copytree(STAGE,release)
    shutil.copytree(STAGE,LIB/'Current',dirs_exist_ok=True)
    write(LIB/'CURRENT.json',dict(release=RELEASE,current='Current',manifest='Current/library.json',snapshot='Releases/'+RELEASE,updated_on='2026-10-13',library_sha256=sha(LIB/'Current/library.json')))
    for k in 'BNGM':
        name='CSC_Props_Shared_01_'+k
        atomic_copy(OUT/'dds'/(name+'.dds'),MOD/'Textures'/(name+'.dds'))
        atomic_copy(OUT/'textures'/(name+'.png'),SOURCE/'textures'/(name+'.png'))
    for name in NAMES:atomic_copy(OUT/(name+'.blend'),SOURCE/(name+'.blend'))
    atomic_copy(OUT/fgx.name,fgx)
    assert all(sha(Path(p))==h for p,h in protected.items())
    proof.update(installed=True,protected_AE_files=len(protected),source=str(SOURCE),cook_tested=False,in_game_tested=False)
    write(OUT/'install-report.json',proof);print('Installed mustard gown; all AE assemblies, GEO metadata and placements preserved.')
def verify_live():
    protected=json.loads((OUT/'protected.json').read_text());assert all(sha(Path(p))==h for p,h in protected.items())
    lib=json.loads((LIB/'Current/library.json').read_text());assert lib['release']==RELEASE
    assert all(sha(LIB/'Current'/p)==h and sha(LIB/'Releases'/RELEASE/p)==h for p,h in lib['files'].items())
    for name in NAMES:assert sha(SOURCE/(name+'.blend'))==sha(OUT/(name+'.blend'))
    converter=module('dds_live',ROOT/'project/tools/blender/scene_export/export_scene.py')
    for k in 'BNGM':
        name='CSC_Props_Shared_01_'+k;live=MOD/'Textures'/(name+'.dds');n=1024*1024*(1 if k in 'GM' else 4)
        assert live.read_bytes()[128:128+n]==(OUT/'dds'/live.name).read_bytes()[128:128+n]
        converter.validate_dds(live,dict(format='R8_UNORM' if k in 'GM' else 'R8G8B8A8_UNORM',size=[1024,1024],slot=k))
        assert sha(SOURCE/'textures'/(name+'.png'))==sha(STAGE/'textures'/(name+'.png'))
    assert sha(MOD/'Geometries/CSC_TAILORS_Fashion_House_Fitting.fgx')==sha(OUT/'CSC_TAILORS_Fashion_House_Fitting.fgx')
    write(OUT/'final-verification.json',dict(installed_source_matches_validated_source=True,native_matches_verified=True,atlas_release=RELEASE,all_previous_AE_files_preserved=True,live_DDS_top_mips_match=True,cook_tested=False,in_game_tested=False))
    print('Final live source, native geometry, atlas and runtime textures verified.')
if __name__=='__main__':
    if '--prepare-release' in sys.argv:prepare_release()
    elif '--publish' in sys.argv:publish()
    elif '--verify-live' in sys.argv:verify_live()
    else:stage()
