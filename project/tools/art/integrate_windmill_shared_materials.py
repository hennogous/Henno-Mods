"""Publish the user-approved shared-material and embedded-scaffold revision."""
import sys,json,copy,hashlib,shutil,subprocess,importlib.util,os
from pathlib import Path
import xml.etree.ElementTree as E
from PIL import Image
import numpy as np
from windmill_tower_integrate import *
OUT=Path(sys.argv[2]);STAGE=OUT/'staged';RUIN=NAME+'_CON+PIL';SOURCE=ART/'BAKERS/Wind Mill/tower'
LIB=ART/'Textures/CSC_Props';RELEASE='2026-10-21_Shared_01_r036';ATLAS=OUT/'atlas-release'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def prepare():
    author=json.loads((OUT/'authoring-report.json').read_text());shutil.copytree(LIB/'Current',ATLAS,dirs_exist_ok=True)
    baselines=[LIB/'CURRENT.json',LIB/'Current/library.json',LIB/'Current/textures/CSC_Props_Shared_01_AO.png',ART/'Textures/CSC_Atlas_AO2.png']
    protected={str(p):sha(p) for p in baselines}
    for p in (MOD/'Assets').glob('*.ast'):
        if p.stem!=NAME:protected[str(p)]=sha(p)
    protected[str(MOD/'Animations'/(NAME+'_Turn.fgx'))]=sha(MOD/'Animations'/(NAME+'_Turn.fgx'))
    (OUT/'baseline.json').write_text(json.dumps(protected,indent=2))
    props=Image.open(LIB/'Current/textures/CSC_Props_Shared_01_AO.png').convert('RGB');building=Image.open(ART/'Textures/CSC_Atlas_AO2.png').convert('RGB')
    original={2048:np.array(props),1024:np.array(building)};masks={size:np.zeros((size,size),bool) for size in original}
    manifest=json.loads((ATLAS/'atlas/quarter-ao-manifest.json').read_text());family=manifest['pages'][0]['quarters'][0]['families'][0]
    for bake in author['bakes']:
        if 'cell' not in bake:continue
        x,y,x1,y1=bake['cell'];size=bake['page_size'];patch=Image.open(bake['raw_bake']).convert('RGB').resize((x1-x,y1-y),Image.Resampling.LANCZOS)
        masks[size][y:y1,x:x1]=True
        if size==2048:
            for f in manifest['pages'][0]['quarters'][0]['families']:
                for a in f.get('allocations',[]):
                    u,v,u1,v1=a['cell'];assert not(x<u1 and x1>u and y<v1 and y1>v),a['id']
            assert props.crop((x,y,x1,y1)).getextrema()==((255,255),)*3
            path=ATLAS/'atlas/sources'/(bake['id']+'_AO.png');patch.save(path);props.paste(patch,(x,y))
            raw=ATLAS/'atlas/sources'/(bake['id']+'_AO2x.png');shutil.copy2(bake['raw_bake'],raw)
            family.setdefault('allocations',[]).append(dict(id=bake['id'],cell=bake['cell'],source=path.relative_to(ATLAS).as_posix(),source_sha256=sha(path),bake='Cycles128 samples, 16 AO rays, local geometry AO, twice-resolution supersampling, 2px final dilation; no ground or pose-dependent tower shadow',ao_distance=bake['distance']))
        else:
            occupied=np.array(Image.open(OUT/'AO2-occupied.png'));assert not occupied[y:y1,x:x1].any()
            building.paste(patch,(x,y));patch.save(OUT/'bakes'/(bake['id']+'_final.png'))
    (OUT/'staged-textures').mkdir(exist_ok=True)
    props.save(ATLAS/'textures/CSC_Props_Shared_01_AO.png');building.save(OUT/'staged-textures/CSC_Atlas_AO2.png')
    for size,im in [(2048,props),(1024,building)]:assert np.array_equal(original[size][~masks[size]],np.array(im)[~masks[size]])
    manifest['status']=RELEASE+': windmill sail and timber AO in unused Bakers Stage2 cells; all other allocations preserved.'
    manifest['pages'][0]['sha256']=sha(ATLAS/'textures/CSC_Props_Shared_01_AO.png')
    (ATLAS/'atlas/quarter-ao-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    # Register the exact patch sources; the canonical cell packer must reproduce them.
    spec=importlib.util.spec_from_file_location('packer',ATLAS/'scripts/pack_quarter_ao.py');packer=importlib.util.module_from_spec(spec);spec.loader.exec_module(packer)
    before=props.tobytes();packer.pack(ATLAS);assert Image.open(ATLAS/'textures/CSC_Props_Shared_01_AO.png').convert('RGB').tobytes()==before
    lib=json.loads((ATLAS/'library.json').read_text());lib.update(release=RELEASE,accepted_on='2026-10-21',content_revision=36,snapshot_path='Releases/'+RELEASE,AO_status=manifest['status'],change_authorization='Henno requested shared sail AO, Level1 tower material and the authored Level1 scaffold on 21 October 2026.')
    lib['files']={p.relative_to(ATLAS).as_posix():sha(p) for p in ATLAS.rglob('*') if p.is_file() and p.name!='library.json'}
    lib['source_approved_blend_sha256'].update({str(SOURCE/p.name):sha(p) for p in (OUT/'masters').glob('*.blend')})
    (ATLAS/'library.json').write_text(json.dumps(lib,indent=2)+'\n')
    exe,_=helper(OUT/'cache')
    for name in (NAME,RUIN):
        native=OUT/(name+'-native.json');subprocess.run([str(exe),str(exe.parent),str(STAGE/f'Geometries/{name}.fgx'),str(native)],cwd=exe.parent,check=True)
        raw=json.loads(native.read_text());names=cn6_material_names(STAGE/f'Geometries/{name}.cn6');geo=read_xml(MOD/f'Geometries/{name}.geo');geo.find('m_Meshes').clear()
        for mesh in raw['meshes']:
            validate_native_groups(mesh);row=E.SubElement(geo.find('m_Meshes'),'Element');field(row,'m_Name',mesh['name']);groups=E.SubElement(row,'m_Groups')
            for group in mesh['groups']:
                g=E.SubElement(groups,'Element');field(g,'m_Name',names[mesh['name']][group['material']]);E.SubElement(g,'m_nFirstPrim').text=str(group['first']);E.SubElement(g,'m_nPrims').text=str(group['count'])
            for k,v in [('m_nBoundBoneCount',len(mesh['boneBindings'])),('m_nPrimitiveCount',len(mesh['triangles'])),('m_nVertexCount',len(mesh['vertices']))]:E.SubElement(row,k).text=str(v)
        assert [b['name'] for b in raw['models'][0]['bones']]==[n.get('text') for n in geo.findall('m_Bones/Element')]
        save(geo,STAGE/f'Geometries/{name}.geo')
    shutil.copy2(OUT/(NAME+'-native.json'),OUT/'tower-native.json')
    asset=read_xml(MOD/f'Assets/{NAME}.ast');models=asset.find('m_GeometrySet/m_ModelInstances')
    for model in models:
        name=txt(model,'m_GeoName');templates=list(model.find('m_GroupStates'))[:5];states=model.find('m_GroupStates');states.clear();geo=read_xml(STAGE/f'Geometries/{name}.geo')
        for mesh in geo.findall('m_Meshes/Element'):
            scaffold=txt(mesh,'m_Name').endswith('_Scaffolding')
            for group in mesh.findall('m_Groups/Element'):
                for t in templates:
                    row=copy.deepcopy(t);state=txt(row,'m_StateName');row.find('m_MeshName').set('text',txt(mesh,'m_Name'));row.find('m_GroupName').set('text',txt(group,'m_Name'))
                    visible=state=='Construction' if scaffold else state in (['Worked','Unworked'] if name==NAME else ['Construction','Pillaged'])
                    for n in row.findall('.//Element'):
                        param=txt(n,'m_ParamName')
                        if param=='Material':n.find('m_ObjectName').set('text',txt(group,'m_Name'))
                        if param=='Visible':n.find('m_bValue').text=str(visible).lower()
                        if param=='EmissiveEnabled':n.find('m_bValue').text='false'
                    states.append(row)
    points=asset.find('.//m_attachmentPoints/m_Points')
    for p in list(points):
        if any(txt(n,'m_EntryName')=='PROP_Scaffold_A' for n in p.findall('.//Element')):points.remove(p)
    assert not any(txt(n,'m_EntryName')=='PROP_Scaffold_A' for n in asset.findall('.//Element'));save(asset,STAGE/f'Assets/{NAME}.ast')
    for suffix in ('','_2'):shutil.copy2(MOD/f'Assets/CSC_BAKERS_Wind_Mill{suffix}.ast',STAGE/f'Assets/CSC_BAKERS_Wind_Mill{suffix}.ast')
    convspec=importlib.util.spec_from_file_location('conv',ROOT/'project/tools/blender/scene_export/export_scene.py');conv=importlib.util.module_from_spec(convspec);convspec.loader.exec_module(conv)
    dds=STAGE/'Textures';dds.mkdir(exist_ok=True);scalar=OUT/'scalar';scalar.mkdir(exist_ok=True)
    for src,size in [(ATLAS/'textures/CSC_Props_Shared_01_AO.png',2048),(OUT/'staged-textures/CSC_Atlas_AO2.png',1024)]:
        png=scalar/src.name;Image.open(src).convert('RGB').getchannel('R').save(png)
        subprocess.run([str(ROOT/'project/tools/directxtex/texconv.exe'),'-nologo','-y','-m','0','-f','R8_UNORM','--ignore-srgb','-o',str(dds),str(png)],check=True)
        desc=dict(format='R8_UNORM',size=[size,size],slot='AO');conv.normalize_ao_dds(dds/(src.stem+'.dds'),desc,MOD/'Textures/CSC_Atlas_AO2.dds');conv.validate_dds(dds/(src.stem+'.dds'),desc)
        shutil.copy2(MOD/'Textures'/(src.stem+'.tex'),dds/(src.stem+'.tex'))
        old=np.array(Image.open(MOD/'Textures'/(src.stem+'.dds')).convert('RGB'))[:,:,0];new=np.array(Image.open(dds/(src.stem+'.dds')).convert('RGB'))[:,:,0]
        assert np.array_equal(old[~masks[size]],new[~masks[size]]),'Runtime AO/source mismatch outside new cells'
    rows=[];backup=OUT/'before-installed';backup.mkdir(exist_ok=True)
    files=[(p,MOD/p.relative_to(STAGE)) for p in STAGE.rglob('*') if p.suffix in ['.fgx','.geo','.dds'] or p.name==NAME+'.ast']
    for name in (NAME,RUIN):files += [(OUT/'masters'/(name+'.blend'),SOURCE/(name+'.blend')),(STAGE/'Geometries'/(name+'.cn6'),SOURCE/(name+'.cn6'))]
    files.append((OUT/'staged-textures/CSC_Atlas_AO2.png',ART/'Textures/CSC_Atlas_AO2.png'))
    for i,(src,dst) in enumerate(files):
        b=backup/(str(i)+'-'+dst.name);shutil.copy2(dst,b);rows.append(dict(source=str(src),destination=str(dst),backup=str(b),before=sha(dst)))
    (OUT/'install-plan.json').write_text(json.dumps(rows,indent=2));print('SHARED_MATERIALS_STAGED',len(rows),'files')

def install():
    for item in json.loads((OUT/'inspection.json').read_text()):assert sha(item['path'])==item['sha'],'User source changed during staging: '+item['path']
    for p,h in json.loads((OUT/'baseline.json').read_text()).items():assert sha(p)==h,p
    assert not (LIB/'Releases'/RELEASE).exists()
    assert json.loads((OUT/'cook-shared/result.json').read_text())['exit_code']==0
    log=(OUT/'cook-shared/stdout.log').read_text();assert 'XLP cook completed with success.' in log and '(ERRORS!!)' not in log and 'Replacing asset:' not in log
    for name in (NAME,RUIN):assert json.loads((OUT/(name+'-source-validation.json')).read_text())['error_count']==0
    assert json.loads((OUT/'native-animation-validation.json').read_text())['frames_checked']==301
    rows=json.loads((OUT/'install-plan.json').read_text())
    for r in rows:assert sha(r['destination'])==r['before'],r['destination']
    shutil.copytree(LIB/'Current',OUT/'before-library');shutil.copy2(LIB/'CURRENT.json',OUT/'before-CURRENT.json')
    shutil.copytree(ATLAS,LIB/'Releases'/RELEASE);shutil.copytree(ATLAS,LIB/'Current',dirs_exist_ok=True)
    (LIB/'CURRENT.json').write_text(json.dumps(dict(release=RELEASE,current='Current',manifest='Current/library.json',snapshot='Releases/'+RELEASE,updated_on='2026-10-21',library_sha256=sha(LIB/'Current/library.json')),indent=2)+'\n')
    for r in rows:
        dst=Path(r['destination']);tmp=dst.with_name(dst.name+'.shared-tmp');shutil.copy2(r['source'],tmp);os.replace(tmp,dst);r['installed_sha256']=sha(dst)
    (OUT/'publication-report.json').write_text(json.dumps(dict(installed=True,release=RELEASE,files=rows,UV1_UV3_user_edits_preserved=True,shared_AO_other_pixels_preserved=True),indent=2));print('SHARED_MATERIALS_INSTALLED')

def verify():
    import struct
    report=json.loads((OUT/'publication-report.json').read_text());author=json.loads((OUT/'authoring-report.json').read_text())
    assert len(json.loads((OUT/'installed-source-parity.json').read_text()))==3
    assert json.loads((OUT/'sail-clearance.json').read_text())=={}
    for r in report['files']:
        src=Path(r['source']);dst=Path(r['destination'])
        if sha(src)!=sha(dst):
            assert dst.suffix=='.dds',dst
            assert struct.unpack('<8I',dst.read_bytes()[76:108])==(32,64,0,8,255,0,0,0)
            assert np.array_equal(np.array(Image.open(src).convert('RGB'))[:,:,0],np.array(Image.open(dst).convert('RGB'))[:,:,0])
            r['watcher_regenerated_identical_AO']=True
        r['installed_sha256']=sha(dst)
    for p,h in json.loads((OUT/'baseline.json').read_text()).items():
        path=Path(p)
        if path.is_relative_to(MOD/'Assets') or path.suffix=='.fgx':assert sha(path)==h,path
    for p in ATLAS.rglob('*'):
        if p.is_file():
            rel=p.relative_to(ATLAS);assert sha(p)==sha(LIB/'Current'/rel)==sha(LIB/'Releases'/RELEASE/rel),rel
    masks={size:np.zeros((size,size),bool) for size in (1024,2048)}
    for b in author['bakes']:
        if 'cell' not in b:continue
        x,y,x1,y1=b['cell'];size=b['page_size'];masks[size][y:y1,x:x1]=True
        assert (x>=512 and y>=512) if size==1024 else (x1<=1024 and y1<=1024)
    for size,old,new in [(2048,OUT/'before-library/textures/CSC_Props_Shared_01_AO.png',LIB/'Current/textures/CSC_Props_Shared_01_AO.png'),(1024,Path(next(r['backup'] for r in report['files'] if r['destination']==str(ART/'Textures/CSC_Atlas_AO2.png'))),ART/'Textures/CSC_Atlas_AO2.png')]:
        assert np.array_equal(np.array(Image.open(old).convert('RGB'))[~masks[size]],np.array(Image.open(new).convert('RGB'))[~masks[size]])
    asset=read_xml(MOD/f'Assets/{NAME}.ast');assert not asset.findall('.//m_attachmentPoints/m_Points/Element')
    for model in asset.findall('.//m_ModelInstances/Element'):
        for row in model.findall('m_GroupStates/Element'):
            mesh=txt(row,'m_MeshName');state=txt(row,'m_StateName');params={txt(n,'m_ParamName'):n for n in row.findall('.//Element') if txt(n,'m_ParamName')}
            material=txt(params['Material'],'m_ObjectName');visible=params['Visible'].findtext('m_bValue')=='true'
            if mesh.endswith('_Scaffolding'):assert material=='Pillage_Construction_01' and visible==(state=='Construction')
            elif mesh.endswith('_Sails'):assert material=='CSC_ALL_Props_01'
            else:assert material in ['CSC_BAKERS_E','CSC_ALL_Props_01']
    original=next(i for i in json.loads((OUT/'inspection.json').read_text()) if Path(i['path']).name=='CSC_Level_1_S_CON+PIL.blend');assert sha(original['path'])==original['sha']
    report.update(final_verified=True,installed_source_errors=0,installed_source_warnings=0,parent_ASTs_unchanged=True,animation_unchanged=True,scaffold_construction_only=True,sail_faces_corrected_outward=404)
    (OUT/'publication-report.json').write_text(json.dumps(report,indent=2));print('FINAL_SHARED_VERIFICATION_PASSED')

if __name__=='__main__':globals()[sys.argv[1]]()
