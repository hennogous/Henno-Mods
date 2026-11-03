"""Publish split cloth geometry and only its existing shared-props AO cell."""
import sys,json,shutil,hashlib,subprocess,importlib.util
from pathlib import Path
import xml.etree.ElementTree as E
import numpy as np
from PIL import Image
import weather_windmill_sails as delivery
from windmill_tower_integrate import helper,read_xml,txt,field,save,validate_native_groups,cn6_material_names
ROOT=delivery.ROOT;MOD=delivery.MOD;ART=delivery.ART;LIB=delivery.LIB;SOURCE=delivery.SOURCE
OUT=delivery.OUT;STAGE=delivery.STAGE;ATLAS=delivery.ATLAS;NAME=delivery.NAME;RUIN=delivery.RUIN
RELEASE='2026-10-24_Shared_01_r043';sha=delivery.sha;write=delivery.write
def stage():
    assert json.loads((LIB/'CURRENT.json').read_text())['release']=='2026-10-22_Shared_01_r042'
    for folder in ['Assets','Geometries','Textures','Animations']:(STAGE/folder).mkdir(parents=True,exist_ok=True)
    shutil.copytree(LIB/'Current',OUT/'before-library');shutil.copytree(LIB/'Current',ATLAS);shutil.copy2(LIB/'CURRENT.json',OUT/'before-CURRENT.json')
    changed=[(OUT/'masters'/(NAME+'.blend'),SOURCE/(NAME+'.blend')),(STAGE/'Geometries'/(NAME+'.cn6'),SOURCE/(NAME+'.cn6'))]
    changed += [(STAGE/'Geometries'/(NAME+ext),MOD/'Geometries'/(NAME+ext)) for ext in ['.fgx','.geo']]
    changed += [(STAGE/'Textures/CSC_Props_Shared_01_AO.dds',MOD/'Textures/CSC_Props_Shared_01_AO.dds')]
    rows=[]
    for i,(src,dst) in enumerate(changed):
        backup=OUT/'before-installed'/str(i)/dst.name;backup.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(dst,backup)
        rows.append(dict(source=str(src),destination=str(dst),backup=str(backup),before=sha(dst)))
    write(OUT/'install-plan.json',rows)
    protected=[SOURCE/(RUIN+'.blend'),SOURCE/(RUIN+'.cn6'),MOD/'Geometries'/(RUIN+'.fgx'),MOD/'Geometries'/(RUIN+'.geo'),MOD/'Animations'/(NAME+'_Turn.fgx'),MOD/'Animations'/(NAME+'_Turn.anm'),ART/'Textures/CSC_Atlas_AO2.png',MOD/'Textures/CSC_Atlas_AO2.dds']
    protected += [MOD/'Textures'/('CSC_Props_Shared_01_'+k+'.dds') for k in 'BNGM']
    protected += [MOD/'Assets'/(s+'.ast') for s in [NAME,'CSC_BAKERS_Wind_Mill','CSC_BAKERS_Wind_Mill_2']]
    write(OUT/'protected.json',{str(p):sha(p) for p in protected})
    for p in protected:
        if p.suffix=='.ast':shutil.copy2(p,STAGE/'Assets'/p.name)
        elif p.parent.name=='Animations':shutil.copy2(p,STAGE/'Animations'/p.name)
    # AO stays in the existing sail allocation. All unrelated pixels are protected.
    bake=json.loads((OUT/'authoring-report.json').read_text())['bakes'][0];assert bake['cell']==[0,128,512,512]
    patch=Image.open(bake['raw_bake']).convert('RGB').resize((512,384),Image.Resampling.LANCZOS)
    src=ATLAS/'atlas/sources'/(NAME+'_Sails_AO.png');patch.save(src);shutil.copy2(bake['raw_bake'],ATLAS/'atlas/sources'/(NAME+'_Sails_AO2x.png'))
    atlaspath=ATLAS/'textures/CSC_Props_Shared_01_AO.png';atlas=Image.open(atlaspath).convert('RGB');before=np.array(atlas);atlas.paste(patch,(0,128));atlas.save(atlaspath)
    mask=np.zeros((2048,2048),bool);mask[128:512,0:512]=True;assert np.array_equal(before[~mask],np.array(atlas)[~mask])
    manifestpath=ATLAS/'atlas/quarter-ao-manifest.json';manifest=json.loads(manifestpath.read_text())
    alloc=next(a for f in manifest['pages'][0]['quarters'][0]['families'] for a in f.get('allocations',[]) if a['id']==NAME+'_Sails');assert alloc['cell']==bake['cell']
    alloc.update(source_sha256=sha(src),bake='Cycles128 samples,16 AO rays, local self-AO; two separate cloth panels and three exposed thick rungs per blade; 2x supersampling',ao_distance=10)
    manifest['status']=RELEASE+': split sail cloth and exposed rungs rebaked; all other AO cells and surface swatches preserved.';manifest['pages'][0]['sha256']=sha(atlaspath);write(manifestpath,manifest)
    spec=importlib.util.spec_from_file_location('packer',ATLAS/'scripts/pack_quarter_ao.py');packer=importlib.util.module_from_spec(spec);spec.loader.exec_module(packer)
    expected=atlas.tobytes();packer.pack(ATLAS);assert Image.open(atlaspath).convert('RGB').tobytes()==expected
    lib=json.loads((ATLAS/'library.json').read_text());lib.update(release=RELEASE,accepted_on='2026-10-24',content_revision=43,snapshot_path='Releases/'+RELEASE,AO_status=manifest['status'])
    lib['source_approved_blend_sha256'][str(SOURCE/(NAME+'.blend'))]=sha(OUT/'masters'/(NAME+'.blend'))
    lib['files']={p.relative_to(ATLAS).as_posix():sha(p) for p in ATLAS.rglob('*') if p.is_file() and p.name!='library.json'};write(ATLAS/'library.json',lib)
    for k in 'BNGM':assert sha(ATLAS/'textures'/('CSC_Props_Shared_01_'+k+'.png'))==sha(LIB/'Current/textures'/('CSC_Props_Shared_01_'+k+'.png'))
    spec=importlib.util.spec_from_file_location('conv',ROOT/'project/tools/blender/scene_export/export_scene.py');conv=importlib.util.module_from_spec(spec);spec.loader.exec_module(conv)
    (OUT/'scalar').mkdir(exist_ok=True);scalar=OUT/'scalar'/atlaspath.name;Image.open(atlaspath).getchannel('R').save(scalar)
    subprocess.run([str(ROOT/'project/tools/directxtex/texconv.exe'),'-nologo','-y','-m','0','-f','R8_UNORM','--ignore-srgb','-o',str(STAGE/'Textures'),str(scalar)],check=True)
    dds=STAGE/'Textures/CSC_Props_Shared_01_AO.dds';desc=dict(format='R8_UNORM',size=[2048,2048],slot='AO');conv.normalize_ao_dds(dds,desc,MOD/'Textures/CSC_Atlas_AO2.dds');conv.validate_dds(dds,desc)
    shutil.copy2(MOD/'Textures/CSC_Props_Shared_01_AO.tex',STAGE/'Textures/CSC_Props_Shared_01_AO.tex')
    assert np.array_equal(np.array(Image.open(MOD/'Textures'/dds.name).convert('RGB'))[:,:,0][~mask],np.array(Image.open(dds).convert('RGB'))[:,:,0][~mask])
    # Actual saved FGX readback drives GEO counts and proves a single binding per mesh.
    exe,_=helper(OUT/'cache')
    for label,p in [('before',MOD/'Geometries'/(NAME+'.fgx')),('after',STAGE/'Geometries'/(NAME+'.fgx'))]:
        subprocess.run([str(exe),str(exe.parent),str(p),str(OUT/(label+'-native.json'))],cwd=exe.parent,check=True)
    before=json.loads((OUT/'before-native.json').read_text());after=json.loads((OUT/'after-native.json').read_text());assert before['models']==after['models']
    assert before['meshes'][0]==after['meshes'][0],'Tower changed'
    names=cn6_material_names(STAGE/'Geometries'/(NAME+'.cn6'));geo=read_xml(MOD/'Geometries'/(NAME+'.geo'));geo.find('m_Meshes').clear();checks=[]
    for m in after['meshes']:
        validate_native_groups(m);binding='Sails' if m['name'].endswith('_Sails') else 'Root';assert m['boneBindings']==[binding]
        assert all(v['boneIndices'][0]==0 and v['boneWeights'][0]==255 and sum(v['boneWeights'])==255 for v in m['vertices'])
        row=E.SubElement(geo.find('m_Meshes'),'Element');field(row,'m_Name',m['name']);groups=E.SubElement(row,'m_Groups')
        for group in m['groups']:
            g=E.SubElement(groups,'Element');field(g,'m_Name',names[m['name']][group['material']]);E.SubElement(g,'m_nFirstPrim').text=str(group['first']);E.SubElement(g,'m_nPrims').text=str(group['count'])
        for k,v in [('m_nBoundBoneCount',1),('m_nPrimitiveCount',len(m['triangles'])),('m_nVertexCount',len(m['vertices']))]:E.SubElement(row,k).text=str(v)
        checks.append(dict(mesh=m['name'],vertices=len(m['vertices']),triangles=len(m['triangles']),bindings=m['boneBindings']))
    save(geo,STAGE/'Geometries'/(NAME+'.geo'));shutil.copy2(OUT/'after-native.json',OUT/'tower-native.json')
    write(OUT/'native-check.json',dict(bone_counts_match=True,tower_and_skeleton_unchanged=True,meshes=checks))
    subprocess.run([sys.executable,str(ROOT/'project/tools/art/readback_windmill_ground_animation.py'),str(OUT)],check=True)
    p=OUT/'validate-motion.py';p.write_text(p.read_text().replace("'duration_seconds':10","'duration_seconds':8"))
    print('SPLIT_SAILS_STAGED',checks,flush=True)
def install():
    for r in json.loads((OUT/'inspection.json').read_text()):assert sha(r['path'])==r['sha']
    assert json.loads((OUT/'sail-clearance.json').read_text())=={}
    anim=json.loads((OUT/'native-animation-validation.json').read_text());assert anim['frames_checked']==241 and anim['duration_seconds']==8
    delivery.RELEASE=RELEASE;delivery.install('split')
    current=json.loads((LIB/'CURRENT.json').read_text());current['updated_on']='2026-10-24';write(LIB/'CURRENT.json',current)
    p=OUT/'publication-report.json';r=json.loads(p.read_text());r.pop('animation_ao_conpil_and_placements_unchanged',None)
    r.update(animation_conpil_tower_and_placements_unchanged=True,sail_AO_rebaked_in_existing_cell=True,all_surface_textures_unchanged=True,panels_per_blade=2,exposed_structural_rungs_per_blade=3);write(p,r)
    print('SPLIT_SAILS_INSTALLED')
if __name__=='__main__':globals()[sys.argv[2]]()
