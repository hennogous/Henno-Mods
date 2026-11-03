"""Validate and publish the narrowly scoped historical mill animation repair."""
import sys,json,hashlib,subprocess,importlib.util,shutil
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree
from storage_pivot_trial import ROOT,MOD,helper,parse,txt,MODELS,BINDINGS
from bundle_windmill_tower import readmotion
OUT=Path.home()/'Desktop/Codex/windmill-animation-repair-20261030'
OLD=Path.home()/'Desktop/Codex/Windmill-bundled-tower-20261026'
NAME='CSC_BAKERS_Wind_Mill'
NATIVE=NAME+'_Tower'
SOURCE=Path.home()/'Desktop/Working Files/3D Art/BAKERS/Wind Mill'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2),encoding='utf-8')

def check():
    exe,_=helper(OUT/'cache')
    for phase in ['before','candidate']:
        fgx=OUT/phase/(NAME+'.fgx');dest=fgx.with_suffix('.json')
        subprocess.run([str(exe),str(exe.parent),str(fgx),str(dest)],cwd=exe.parent,capture_output=True,check=True)
    before=json.loads((OUT/'before'/(NAME+'.json')).read_text());after=json.loads((OUT/'candidate'/(NAME+'.json')).read_text())
    assert before['models'][0]['name']==NAME
    assert after['models'][0]['name']==NATIVE
    geometry=[]
    for m in before['meshes']:
        n=next(x for x in after['meshes'] if x['name']==m['name'])
        assert m['boneBindings']==n['boneBindings']
        assert len(m['vertices'])==len(n['vertices']) and m['triangles']==n['triangles']
        assert m['groups']==n['groups']
        pack=lambda mesh:np.array([[v for k in ['position','normal','tangent','binormal','uv','uv2','uv3','boneIndices','boneWeights'] for v in vertex[k]] for vertex in mesh['vertices']])
        error=float(abs(pack(m)-pack(n)).max());assert error<.0001,(m['name'],error)
        geometry.append(dict(mesh=m['name'],maximum_attribute_error=error,vertices=len(n['vertices']),bindings=n['boneBindings']))
    bb=before['models'][0]['bones'];ab=after['models'][0]['bones']
    assert len(bb)==len(ab)
    for i,(b,a) in enumerate(zip(bb,ab)):
        assert a['name']==(NATIVE if i==0 else b['name'])
        assert a['parent']==b['parent']
        assert max(abs(np.array(a['inverseWorld'])-b['inverseWorld']))<.0001
        for k in ['position','orientation','scaleShear']:assert max(abs(np.array(a['local'][k])-b['local'][k]))<.0001
    spec=importlib.util.spec_from_file_location('backend',Path.home()/'.codex/skills/civ6-art/scripts/civ6_animation/backend.py')
    backend=importlib.util.module_from_spec(spec);spec.loader.exec_module(backend)
    clip=MOD/'Animations'/(NATIVE+'_Turn.fgx')
    assert sha(clip)=='09bf8707e529f37a6dac0cddc4677cd30fc8e7460bd9ee68e84e4e0a3fc50d6e'
    result=backend.run(r'C:\Program Files (x86)\CivNexus6_Release-1.3.3\CivNexus6','extract',OUT/'candidate'/(NAME+'.fgx'),clip,OUT/'motion',30,0,0)
    write(OUT/'sampling-result.json',result)
    motion=readmotion(OUT/'motion/clip.na2');reference=readmotion(OLD/'motion-after/clip.na2')
    previous=json.loads((OLD/'native-after'/(NAME+'.json')).read_text())
    prior_bones={b['name']:b for b in previous['models'][0]['bones']}
    current_bones={b['name']:b for b in ab}
    errors={};motion_spans={}
    for mesh in after['meshes']:
        bone=mesh['boneBindings'][0];v=np.array([[*v['position'],1] for v in mesh['vertices']]).T
        actual=motion[bone]@np.array(current_bones[bone]['inverseWorld']).reshape(4,4).T@v
        expected=reference[bone]@np.array(prior_bones[bone]['inverseWorld']).reshape(4,4).T@v
        assert len(actual)==241
        errors[mesh['name']]=float(abs(actual-expected).max())
        motion_spans[mesh['name']]=float(abs(actual-actual[0]).max())
    assert max(errors.values())<.001,errors
    assert motion_spans[NATIVE+'_Sails']>30,motion_spans
    assert motion_spans[NAME.replace('CSC_BAKERS_Wind_Mill','CSC_Level_1_S_Bldg')]<.001
    assert motion_spans[NATIVE+'_Tower']<.001
    assets=[]
    for name in [NAME,NAME+'_2']:
        ast=MOD/'Assets'/(name+'.ast');r=parse(ast)
        assert NAME in [txt(m,'m_GeoName') for m in r.findall(MODELS+'/Element')]
        assert any(txt(b,'m_SlotName')=='WORKED_A' and txt(b,'m_AnimationName')==NATIVE+'_Turn' for b in r.findall(BINDINGS+'/Element'))
        assets.append(dict(asset=name,sha256=sha(ast)))
    write(OUT/'verification.json',dict(geometry=geometry,frames=241,clip_sha256=sha(clip),maximum_vertex_motion_error=errors,motion_spans=motion_spans,assets=assets,internal_name_before=NAME,internal_name_after=NATIVE))
    print(json.dumps(dict(geometry=geometry,motion_errors=errors,motion_spans=motion_spans),indent=2))
    # Isolated package uses all current dependencies but just the two consumers.
    baseline={}
    for folder in ['Assets','Geometries','Animations','Materials','Textures','XLPs','ArtDefs']:
        for p in (MOD/folder).rglob('*'):
            if p.is_file():baseline[p.relative_to(MOD).as_posix()]=sha(p)
    write(OUT/'baseline.json',baseline)
    pantry=OUT/'cook-after/pantry'
    # Refer to the live mod as a read-only fallback pantry; only overrides need copying.
    for ext in ['.fgx','.geo']:
        dst=pantry/'Geometries'/(NAME+ext);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(OUT/'candidate'/(NAME+ext),dst)
    xlp=parse(MOD/'XLPs/CSC_Tilebases.xlp');entries=xlp.find('m_Entries')
    for e in list(entries):
        if txt(e,'m_EntryID') not in [NAME,NAME+'_2']:entries.remove(e)
    assert len(entries)==2
    from storage_pivot_trial import save
    save(xlp,pantry/'XLPs/CSC_Tilebases.xlp')
    import cleanup_art_orphans as cleanup
    # Its generic cooker doesn't include the mod fallback. Use same command,
    # with the live source after our override and before SDK pantries.
    cooker=next(Path('C:/Program Files (x86)/Steam/steamapps/common').glob('*Civilization VI SDK/AssetModTools/Cooker'))
    results=OUT/'cook-after/results';results.mkdir(parents=True,exist_ok=True)
    cmd=[str(cooker/'Civ6AssetCooker_FinalRelease.exe'),'--absolute_paths','--no_mt','--mode','XLP','--platform','Windows','--shaders',str(cooker),'--pantry',str(pantry),'--pantry',str(MOD)]
    for p in ['Civ6/pantry','Civ6/DLC/Shared/pantry','Civ6/DLC/Expansion1/pantry','Civ6/DLC/Expansion2/pantry']:cmd+=['--pantry',str(cleanup.audit.SDK/p)]
    cmd+=['--stewpot',str(results/'BLPs'),'--config',str(cooker/'Civ6.cfg'),'--log_path',str(results),str(pantry/'XLPs/CSC_Tilebases.xlp')]
    write(results/'command.json',cmd)
    with (results/'stdout.log').open('w') as f:r=subprocess.run(cmd,cwd=results,stdout=f,stderr=subprocess.STDOUT,timeout=180)
    assert r.returncode==0,r.returncode
    import bundle_windmill_tower as bundled
    bundled.OUT=OUT;bundled.cooked_check()
    write(results/'result.json',dict(exit_code=r.returncode,blps=[str(p) for p in results.rglob('*.blp')]))
    print('BOTH_ASSETS_COOK_PASS')

def publish():
    verification=json.loads((OUT/'verification.json').read_text())
    assert json.loads((OUT/'cook-after/results/result.json').read_text())['exit_code']==0
    assert not (OUT/'installed.json').exists()
    assert sha(SOURCE/(NAME+'.blend'))==sha(OUT/'before'/(NAME+'.blend'))
    baseline=json.loads((OUT/'baseline.json').read_text())
    for rel,h in baseline.items():assert sha(MOD/rel)==h,('Changed during repair',rel)
    for ext in ['.geo','.fgx']:
        assert sha(MOD/'Geometries'/(NAME+ext))==sha(OUT/'before'/(NAME+ext))
        shutil.copy2(OUT/'candidate'/(NAME+ext),MOD/'Geometries'/(NAME+ext))
    shutil.copy2(OUT/'master'/(NAME+'.blend'),SOURCE/(NAME+'.blend'))
    for ext in ['.cn6','.fgx','.geo']:
        dest=SOURCE/'exports'/NAME/(NAME+ext)
        if dest.exists():shutil.copy2(dest,OUT/'before'/('export-'+dest.name))
        dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(OUT/'candidate'/(NAME+ext),dest)
    changed={'Geometries/'+NAME+ext for ext in ['.fgx','.geo']}
    for rel,h in baseline.items():
        if rel not in changed:assert sha(MOD/rel)==h,rel
    write(OUT/'installed.json',dict(repaired_model=NAME,preserved_mod_files=len(baseline)-len(changed),blend_sha256=sha(SOURCE/(NAME+'.blend')),geometry_sha256=sha(MOD/'Geometries'/(NAME+'.fgx')),animation_unchanged=True,ae_assemblies_unchanged=True))
    print('INSTALLED; untouched mod files:',len(baseline)-len(changed))

if __name__=='__main__':globals()[sys.argv[1]]()
