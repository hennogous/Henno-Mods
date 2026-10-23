"""Stage and publish sail-only cloth weathering in a protected shared atlas slot."""
import sys,json,shutil,hashlib,subprocess,importlib.util,struct
from pathlib import Path
import numpy as np
from PIL import Image,ImageFilter
ROOT=Path(__file__).resolve().parents[3];MOD=ROOT/'Civ Supply Chains'
ART=Path.home()/'Desktop/Working Files/3D Art';LIB=ART/'Textures/CSC_Props'
SOURCE=ART/'BAKERS/Wind Mill/tower';NAME='CSC_BAKERS_Wind_Mill_Tower';RUIN=NAME+'_CON+PIL'
OUT=Path(sys.argv[1]);STAGE=OUT/'staged';ATLAS=OUT/'atlas-release';RELEASE='2026-10-22_Shared_01_r042'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
def stage():
    OUT.mkdir(parents=True,exist_ok=True)
    for folder in ['Textures','Assets','Geometries']:(STAGE/folder).mkdir(parents=True,exist_ok=True)
    assert json.loads((LIB/'CURRENT.json').read_text())['release'].endswith('r041')
    shutil.copytree(LIB/'Current',OUT/'before-library');shutil.copytree(LIB/'Current',ATLAS)
    shutil.copy2(LIB/'CURRENT.json',OUT/'before-CURRENT.json')
    paths=[SOURCE/(NAME+'.blend'),SOURCE/(NAME+'.cn6'),MOD/'Geometries'/(NAME+'.fgx')]
    paths += [MOD/'Textures'/('CSC_Props_Shared_01_'+k+'.dds') for k in 'BNGM']
    rows=[]
    for n,p in enumerate(paths):
        backup=OUT/'before'/str(n)/p.name;backup.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,backup)
        src=OUT/'masters'/p.name if p.suffix=='.blend' else STAGE/('Geometries' if p.suffix in ['.cn6','.fgx'] else 'Textures')/p.name
        rows.append(dict(source=str(src),destination=str(p),backup=str(backup),before=sha(p)))
    write(OUT/'install-plan.json',rows)
    protected=[SOURCE/(RUIN+'.blend'),SOURCE/(RUIN+'.cn6'),MOD/'Geometries'/(RUIN+'.fgx'),MOD/'Geometries'/(RUIN+'.geo'),MOD/'Animations'/(NAME+'_Turn.fgx'),MOD/'Animations'/(NAME+'_Turn.anm'),ART/'Textures/CSC_Atlas_AO2.png',MOD/'Textures/CSC_Props_Shared_01_AO.dds']
    protected += [MOD/'Assets'/(s+'.ast') for s in [NAME,'CSC_BAKERS_Wind_Mill','CSC_BAKERS_Wind_Mill_2']]
    write(OUT/'protected.json',{str(p):sha(p) for p in protected})
    for p in protected:
        if p.suffix=='.ast':shutil.copy2(p,STAGE/'Assets'/p.name)
    shutil.copy2(MOD/'Geometries'/(NAME+'.geo'),STAGE/'Geometries'/(NAME+'.geo'))
    manifest=json.loads((ATLAS/'atlas/manifest.json').read_text());assert 39 in manifest['reserved_slots'] and not any(r['slot']==39 for r in manifest['regions'])
    original=Path(sys.argv[3]);shutil.copy2(original,ATLAS/'atlas/sources/windmill_weathered_canvas_ImageGen.png')
    base=Image.open(original).convert('RGB').resize((120,120),Image.Resampling.LANCZOS)
    # Derive fine relief only; broad albedo stains must not become dents.
    gray=base.convert('L');hi=np.asarray(gray,dtype=float)-np.asarray(gray.filter(ImageFilter.GaussianBlur(3)),dtype=float)
    dy,dx=np.gradient(hi/255);normal=np.dstack((-dx*3,dy*3,np.ones_like(dx)))
    normal/=np.linalg.norm(normal,axis=2,keepdims=True)
    maps=dict(B=base,N=Image.fromarray(np.rint((normal+1)*127.5).clip(0,255).astype('uint8')),G=Image.new('RGB',(120,120),(8,8,8)),M=Image.new('RGB',(120,120)))
    sources={}
    for k,patch in maps.items():
        dst=ATLAS/'atlas/sources'/('windmill_weathered_canvas_'+k+'.png');patch.save(dst);sources[k]=dst.relative_to(ATLAS/'atlas').as_posix()
        for size in [1024,2048]:
            p=ATLAS/'textures'/('CSC_Props_Shared_01_'+k+'.png') if size==1024 else ATLAS/'atlas'/('CSC_Props_Shared_01_v2_'+k+'_Master2048.png')
            im=Image.open(p).convert('RGB');old=np.array(im);scale=size//1024;px=patch.resize((120*scale,120*scale),Image.Resampling.LANCZOS)
            im.paste(Image.fromarray(np.pad(np.array(px),((4*scale,4*scale),(4*scale,4*scale),(0,0)),mode='edge')),(896*scale,512*scale));im.save(p)
            mask=np.zeros((size,size),bool);mask[512*scale:640*scale,896*scale:1024*scale]=True;assert np.array_equal(old[~mask],np.array(im)[~mask])
    manifest['regions'].append(dict(id=39,slot=39,name='windmill_weathered_canvas',family='textile_rope',bounds=[900,516,1020,636],sources=sources,provenance='ImageGen edit of existing ivory cloth: sun fading, edge grime, stitched seams and one subtle repair. Normal from high-pass fabric detail; matte G=8, M=0. Original ImageGen PNG retained.'))
    manifest['reserved_slots'].remove(39);manifest['content_revision']=42;manifest['change_note']='Weathered sail canvas in previously unused slot39; existing ivory and all occupied swatches unchanged.'
    manifest['production_sha256']={k:sha(ATLAS/'textures'/('CSC_Props_Shared_01_'+k+'.png')) for k in 'BNGM'};write(ATLAS/'atlas/manifest.json',manifest)
    lib=json.loads((ATLAS/'library.json').read_text());lib.update(release=RELEASE,content_revision=42,snapshot_path='Releases/'+RELEASE,surface_status='Windmill weathered canvas in slot39; all earlier surface and AO allocations preserved.')
    lib['files']={p.relative_to(ATLAS).as_posix():sha(p) for p in ATLAS.rglob('*') if p.is_file() and p.name!='library.json'};write(ATLAS/'library.json',lib)
    spec=importlib.util.spec_from_file_location('conv',ROOT/'project/tools/blender/scene_export/export_scene.py');conv=importlib.util.module_from_spec(spec);spec.loader.exec_module(conv)
    (OUT/'scalar').mkdir(exist_ok=True)
    for k in 'BNGM':
        src=ATLAS/'textures'/('CSC_Props_Shared_01_'+k+'.png');scalar=k in 'GM';fmt='R8_UNORM' if scalar else 'R8G8B8A8_UNORM'
        if scalar:
            scalar_path=OUT/'scalar'/src.name;Image.open(src).getchannel('R').save(scalar_path);src=scalar_path
        subprocess.run([str(ROOT/'project/tools/directxtex/texconv.exe'),'-nologo','-y','-m','0','-f',fmt,'--ignore-srgb','-o',str(STAGE/'Textures'),str(src)],check=True)
        dds=STAGE/'Textures'/(src.stem+'.dds');desc=dict(size=[1024,1024],format=fmt,slot=k)
        if scalar:conv.normalize_ao_dds(dds,desc,MOD/'Textures/CSC_Atlas_AO2.dds')
        conv.validate_dds(dds,desc);shutil.copy2(MOD/'Textures'/(src.stem+'.tex'),STAGE/'Textures'/(src.stem+'.tex'))
    print('WEATHERED_CANVAS_STAGED',flush=True)

def check():
    from windmill_tower_integrate import helper,read_xml,txt,validate_native_groups
    exe,_=helper(OUT/'cache')
    for label,path in [('before',MOD/'Geometries'/(NAME+'.fgx')),('after',STAGE/'Geometries'/(NAME+'.fgx'))]:
        subprocess.run([str(exe),str(exe.parent),str(path),str(OUT/(label+'-native.json'))],cwd=exe.parent,check=True)
    before=json.loads((OUT/'before-native.json').read_text());after=json.loads((OUT/'after-native.json').read_text());assert before['models']==after['models']
    changed=0;geo=read_xml(STAGE/'Geometries'/(NAME+'.geo'));assert geo.tag=='AssetObjects..GeometryInstance'
    for a,b in zip(before['meshes'],after['meshes']):
        assert len(a['vertices'])==len(b['vertices']);assert a['triangles']==b['triangles'];assert a['boneBindings']==b['boneBindings'];validate_native_groups(b)
        g=next(x for x in geo.findall('m_Meshes/Element') if txt(x,'m_Name')==b['name']);assert int(g.findtext('m_nBoundBoneCount'))==len(b['boneBindings'])==1
        for v,w in zip(a['vertices'],b['vertices']):
            av=dict(v);bv=dict(w)
            if av['uv']!=bv['uv']:
                assert b['name'].endswith('_Sails');assert np.allclose(np.array(bv['uv'])-av['uv'],[.875,.125],atol=2e-6)
                changed+=1
            av.pop('uv');bv.pop('uv')
            # A UV translation preserves the tangent directions, allowing converter rounding.
            for k in ['tangent','binormal']:
                assert np.allclose(av.pop(k),bv.pop(k),atol=.0001)
            assert av==bv
    assert changed>0;write(OUT/'native-check.json',dict(uv1_vertices_remapped=changed,geometry_skeleton_weights_uv2_uv3_unchanged=True,vertices=sum(len(m['vertices']) for m in after['meshes']),bone_counts_match=True))
    print('NATIVE_CLOTH_UV_TRANSLATION_VERIFIED',changed)

def install():
    result=json.loads((OUT/'cook-weathered/result.json').read_text());log=(OUT/'cook-weathered/stdout.log').read_text()
    assert result['exit_code']==0 and 'XLP cook completed with success.' in log and '(ERRORS!!)' not in log and 'Replacing asset:' not in log
    validation=json.loads((OUT/'source-validation.json').read_text());assert validation['error_count']==0 and validation['warning_count']==0
    assert json.loads((OUT/'native-check.json').read_text())['bone_counts_match']
    code=(ROOT/'project/tools/art/verify_windmill_wood.py').read_text();code=code[code.index('def fnv(s):'):code.index('if installed:')].replace('cook-wood','cook-weathered');env=dict(OUT=OUT,NAME=NAME,RUIN=RUIN,struct=struct);exec(compile(code,'cooked_format_check','exec'),env)
    rows=json.loads((OUT/'install-plan.json').read_text())
    for r in rows:assert sha(r['destination'])==r['before'],r['destination']
    for path,digest in json.loads((OUT/'protected.json').read_text()).items():assert sha(path)==digest,path
    for p in (OUT/'before-library').rglob('*'):
        if p.is_file():assert sha(p)==sha(LIB/'Current'/p.relative_to(OUT/'before-library'))
    assert not (LIB/'Releases'/RELEASE).exists();shutil.copytree(ATLAS,LIB/'Releases'/RELEASE);shutil.copytree(ATLAS,LIB/'Current',dirs_exist_ok=True)
    write(LIB/'CURRENT.json',dict(release=RELEASE,current='Current',manifest='Current/library.json',snapshot='Releases/'+RELEASE,updated_on='2026-10-22',library_sha256=sha(LIB/'Current/library.json')))
    for r in rows:shutil.copy2(r['source'],r['destination']);assert sha(r['source'])==sha(r['destination'])
    for p in ATLAS.rglob('*'):
        if p.is_file():assert sha(p)==sha(LIB/'Current'/p.relative_to(ATLAS))==sha(LIB/'Releases'/RELEASE/p.relative_to(ATLAS))
    write(OUT/'publication-report.json',dict(installed=True,verified=True,files=rows,release=RELEASE,cooked_formats=env['cooked'],animation_ao_conpil_and_placements_unchanged=True))
    print('WEATHERED_SAILS_INSTALLED_AND_VERIFIED')
if __name__=='__main__':globals()[sys.argv[2]]()
