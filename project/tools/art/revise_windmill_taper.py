"""Stage and publish the tapered tower and its corrected Firaxis GEO wrapper."""
import sys,json,shutil,subprocess,importlib.util,hashlib,os
from pathlib import Path
from PIL import Image
from windmill_tower_integrate import ROOT,MOD,NAME,AO,MATS,helper,review,read_xml,save,field,validate_native_groups,cn6_material_names
OUT=Path(sys.argv[2]); SOURCE=Path.home()/'Desktop/Working Files/3D Art/BAKERS/Wind Mill/tower'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def prepare():
    files=[(OUT/'new-tower'/(NAME+'.blend'),SOURCE/(NAME+'.blend')),
        (OUT/'staged/Geometries'/(NAME+'.cn6'),SOURCE/(NAME+'.cn6')),
        (OUT/'staged-textures'/(AO+'.png'),SOURCE/(AO+'.png')),
        (OUT/'staged/Geometries'/(NAME+'.fgx'),MOD/'Geometries'/(NAME+'.fgx')),
        (OUT/'staged/Geometries'/(NAME+'.geo'),MOD/'Geometries'/(NAME+'.geo')),
        (OUT/'staged/Textures'/(AO+'.dds'),MOD/'Textures'/(AO+'.dds'))]
    backup=OUT/'before';backup.mkdir(exist_ok=True);rows=[]
    for i,(src,dst) in enumerate(files):
        b=backup/(str(i)+'-'+dst.name);assert not b.exists();shutil.copy2(dst,b)
        rows.append(dict(source=str(src),destination=str(dst),backup=str(b),before=sha(dst)))
    (OUT/'install-plan.json').write_text(json.dumps(rows,indent=2))
    protected=list((MOD/'Assets').glob('*.ast'))+list((MOD/'Materials').glob('*.mtl'))
    protected+=list((MOD/'Textures').glob('CSC_Atlas_*'))+[MOD/'Animations'/(NAME+'_Turn.fgx')]
    (OUT/'protected.json').write_text(json.dumps({str(p):sha(p) for p in protected},indent=2))
    logs=Path(os.environ['APPDATA'])/'AssetEditor/1.1/Logs'
    shutil.copy2(logs/'7d571ff8-e530-46ae-a4c0-ab59892065db.log',OUT/'ae-failure-before.log')
    exe,_=helper(OUT/'cache')
    subprocess.run([str(exe),str(exe.parent),str(OUT/'staged/Geometries'/(NAME+'.fgx')),str(OUT/'tower-native.json')],cwd=exe.parent,check=True)
    raw=json.loads((OUT/'tower-native.json').read_text());old=json.loads((OUT.parent/'wide-sails/tower-native.json').read_text())
    assert raw['models']==old['models'];assert raw['meshes'][0]==old['meshes'][0]
    def attributes(mesh):return {tuple(tuple(v[k]) for k in ['uv','uv2','uv3','boneIndices','boneWeights']) for v in mesh['vertices']}
    assert attributes(raw['meshes'][1])==attributes(old['meshes'][1])
    geo=read_xml(MOD/'Geometries'/(NAME+'.geo'))
    material_names=cn6_material_names(OUT/'staged/Geometries'/(NAME+'.cn6'))
    # Native class name must be double-dot; never serialize a normalized legacy tag.
    geo.tag='AssetObjects..GeometryInstance'
    for row,mesh in zip(geo.findall('m_Meshes/Element'),raw['meshes']):
        assert row.find('m_Name').get('text')==mesh['name']
        row.find('m_nVertexCount').text=str(len(mesh['vertices']))
        row.find('m_nPrimitiveCount').text=str(len(mesh['triangles']))
        for group in row.findall('m_Groups/Element'):
            mi=material_names[mesh['name']].index(group.find('m_Name').get('text'));indices=[i for i,t in enumerate(mesh['triangles']) if t[3]==mi]
            assert indices==list(range(min(indices),max(indices)+1))
            group.find('m_nFirstPrim').text=str(min(indices));group.find('m_nPrims').text=str(len(indices))
    save(geo,OUT/'staged/Geometries'/(NAME+'.geo'))
    scalar=OUT/'scalar';scalar.mkdir(exist_ok=True);png=scalar/(AO+'.png')
    Image.open(OUT/'staged-textures'/png.name).convert('RGB').getchannel('R').save(png)
    ddsdir=OUT/'staged/Textures';ddsdir.mkdir(exist_ok=True)
    subprocess.run([str(ROOT/'project/tools/directxtex/texconv.exe'),'-nologo','-y','-m','0','-f','R8_UNORM','--ignore-srgb','-o',str(ddsdir),str(png)],check=True)
    spec=importlib.util.spec_from_file_location('export_scene',ROOT/'project/tools/blender/scene_export/export_scene.py');conv=importlib.util.module_from_spec(spec);spec.loader.exec_module(conv)
    desc={'format':'R8_UNORM','size':[512,512],'slot':'AO'}
    conv.normalize_ao_dds(ddsdir/(AO+'.dds'),desc,MOD/'Textures/CSC_Atlas_AO2.dds');conv.validate_dds(ddsdir/(AO+'.dds'),desc)
    (OUT/'staged/Assets').mkdir(exist_ok=True)
    for suffix in ('','_2'):shutil.copy2(MOD/'Assets'/('CSC_BAKERS_Wind_Mill'+suffix+'.ast'),OUT/'staged/Assets'/('CSC_BAKERS_Wind_Mill'+suffix+'.ast'))
    shutil.copy2(OUT.parent/'native-animation-transforms.npz',OUT/'native-animation-transforms.npz')
    shutil.copy2(OUT.parent/'wide-sails/validate-motion.py',OUT/'validate-motion.py')
    review(OUT)
    (OUT/'native-geometry-checks.json').write_text(json.dumps(dict(tower_and_rig_unchanged=True,uvs_and_weights_preserved=True,
        meshes={m['name']:len(m['vertices']) for m in raw['meshes']},geo_type=geo.tag),indent=2))

def install():
    assert json.loads((OUT/'sail-clearance.json').read_text())=={}
    assert json.loads((OUT/'source-validation.json').read_text())['error_count']==0
    assert json.loads((OUT/'native-animation-validation.json').read_text())['frames_checked']==301
    cook=OUT/'cook-verified'
    assert json.loads((cook/'result.json').read_text())['exit_code']==0
    log=(cook/'stdout.log').read_text()
    assert 'XLP cook completed with success.' in log and '(ERRORS!!)' not in log and 'Replacing asset:' not in log
    rows=json.loads((OUT/'install-plan.json').read_text());protected=json.loads((OUT/'protected.json').read_text())
    for p,h in protected.items():assert sha(p)==h,p
    for row in rows:assert sha(row['destination'])==row['before'],row['destination']
    for row in rows:
        dst=Path(row['destination']);tmp=dst.with_name(dst.name+'.taper-tmp');shutil.copy2(row['source'],tmp);os.replace(tmp,dst)
        row['installed_sha256']=sha(dst);assert sha(row['source'])==sha(dst)
    for p,h in protected.items():assert sha(p)==h,p
    (OUT/'publication-report.json').write_text(json.dumps(dict(installed=True,files=rows,protected_files_unchanged=len(protected)),indent=2))
    print('Installed six focused files; all protected sources unchanged.')

def finalize_groups():
    exe,_=helper(OUT/'cache')
    subprocess.run([str(exe),str(exe.parent),str(OUT/'staged/Geometries'/(NAME+'.fgx')),str(OUT/'tower-native.json')],cwd=exe.parent,check=True)
    raw=json.loads((OUT/'tower-native.json').read_text());old=json.loads((OUT/'before-group-cleanup/tower-native.json').read_text())
    assert raw['models']==old['models'] and raw['meshes'][0]==old['meshes'][0]
    for a,b in zip(raw['meshes'][1]['vertices'],old['meshes'][1]['vertices']):assert a==b
    assert [t[:3] for t in raw['meshes'][1]['triangles']]==[t[:3] for t in old['meshes'][1]['triangles']]
    geo=read_xml(OUT/'staged/Geometries'/(NAME+'.geo'))
    assert geo.tag=='AssetObjects..GeometryInstance'
    material_names=cn6_material_names(OUT/'staged/Geometries'/(NAME+'.cn6'))
    for m,g in zip(raw['meshes'],geo.findall('m_Meshes/Element')):
        validate_native_groups(m)
        assert [x.find('m_Name').get('text') for x in g.findall('m_Groups/Element')]==material_names[m['name']]
        assert len(m['groups'])==len(material_names[m['name']])
        for native_group,descriptor in zip(m['groups'],g.findall('m_Groups/Element')):
            assert native_group['first']==int(descriptor.findtext('m_nFirstPrim')) and native_group['count']==int(descriptor.findtext('m_nPrims'))
    cook_results=[]
    for mode in ['groups-fixed-1','groups-fixed-2','groups-fixed-3','groups-final']:
        directory=OUT/('cook-'+mode);r=json.loads((directory/'result.json').read_text());log=(directory/'stdout.log').read_text()
        assert r['exit_code']==0 and '(ERRORS!!)' not in log and 'Replacing asset:' not in log
        assert 'XLP cook completed with success.' in log; cook_results.append(r)
    assert json.loads((OUT/'source-validation.json').read_text())['error_count']==0
    report=json.loads((OUT/'publication-report.json').read_text())
    for row in report['files']:
        if sha(row['destination'])==row['installed_sha256']:continue
        # AE's source watcher may regenerate mip/header metadata after PNG save.
        # Accept only the same red AO pixels with the compatible scalar format.
        assert Path(row['destination']).suffix=='.dds',row['destination']
        import struct,numpy as np
        a=Path(row['source']);b=Path(row['destination'])
        assert struct.unpack('<8I',b.read_bytes()[76:108])==(32,64,0,8,255,0,0,0)
        assert np.array_equal(np.array(Image.open(a).convert('RGB'))[:,:,0],np.array(Image.open(b).convert('RGB'))[:,:,0])
        row['watcher_regenerated_identical_ao_pixels']=True;row['installed_sha256']=sha(b)
    for row in report['files']:
        if Path(row['destination']).suffix not in ['.blend','.cn6','.fgx']:continue
        if sha(row['source'])==row['installed_sha256']:continue
        dst=Path(row['destination']);backup=OUT/'before-group-cleanup'/('installed-'+dst.name);assert not backup.exists();shutil.copy2(dst,backup)
        tmp=dst.with_name(dst.name+'.groups-tmp');shutil.copy2(row['source'],tmp);os.replace(tmp,dst)
        row['installed_sha256']=sha(dst);row['before_group_cleanup']=str(backup)
    for p,h in json.loads((OUT/'protected.json').read_text()).items():assert sha(p)==h,p
    report['native_group_parity']=True;report['cook_checks']=cook_results
    report['caveat']='Earlier post-load cooker failures were intermittent. The old-group control also passed three times, so a causal group/crash claim is not established. Live AE acceptance remains pending.'
    (OUT/'publication-report.json').write_text(json.dumps(report,indent=2));print('Native geometry identical; group indices repaired; four successful clean cooks; final source/native files installed.')

if __name__=='__main__':globals()[sys.argv[1]]()
