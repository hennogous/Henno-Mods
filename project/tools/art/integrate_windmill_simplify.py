"""Publish UV-edited windowless masters and geometry-baked sail joint maps."""
import sys,json,shutil,subprocess,importlib.util
from pathlib import Path
import numpy as np
from PIL import Image
source=Path(__file__).with_name('integrate_windmill_angular.py').read_text()
source=source[:source.rindex("if __name__=='__main__':")]
source=source.replace('2026-10-22_Shared_01_r038','2026-10-22_Shared_01_r040').replace('content_revision=38','content_revision=40')
source=source.replace('six planar braced tower faces; tower AO rebaked in existing cells, sails and other allocations preserved.','windowless tower AO rebaked; sail joints baked to normals, unused window timber AO cells reclaimed.')
source=source.replace('Henno requested broader flat tower faces matching the timber concept on 22 October 2026.','Henno requested simpler sail joints, preserved UV edits, window removal AO and both native re-exports on 22 October 2026.')
source=source.replace('cook-angular','cook-simplify').replace('ANGULAR_REVISION','SIMPLIFIED_REVISION')
source=source.replace('wall_UV1_remapped_per_face=True,UV3_preserved=True','user_tower_UV1_preserved=True,sail_joint_UV1_remapped=True,UV3_preserved=True')
exec(compile(source,str(__file__),'exec'))
base_stage=stage

def stage():
    # Reclaim obsolete window/axle material AO cells in the same protected release.
    authorpath=OUT/'authoring-report.json';author=json.loads(authorpath.read_text())
    for name,cell in [(NAME,[384,0,448,128]),(RUIN,[448,0,512,128])]:
        im=OUT/'bakes'/(name+'_Timber_empty.png');Image.new('RGB',(128,256),'white').save(im)
        author['bakes'].append(dict(id=name+'_Timber',cell=cell,page_size=2048,raw_bake=str(im),distance=0))
    authorpath.write_text(json.dumps(author,indent=2))
    base_stage()
    manifest_path=ATLAS/'atlas/manifest.json';manifest=json.loads(manifest_path.read_text());slot=38
    assert slot in manifest['reserved_slots'] and not any(r['slot']==slot for r in manifest['regions'])
    sources={};texture_files=[];mask=np.zeros((1024,1024),bool);mask[512:640,768:896]=True
    for k in 'BNGM':
        raw=OUT/'bakes'/('sail_joints_'+k+'.png');dst=ATLAS/'atlas/sources'/('windmill_sail_joints_'+k+'.png')
        patch=Image.open(raw).convert('RGB').resize((120,120),Image.Resampling.LANCZOS)
        if k=='N':
            a=np.array(patch,dtype=float)/127.5-1;a/=np.maximum(np.linalg.norm(a,axis=2,keepdims=True),1e-8);patch=Image.fromarray(np.rint((a+1)*127.5).clip(0,255).astype('uint8'))
        patch.save(dst);sources[k]=dst.relative_to(ATLAS/'atlas').as_posix();shutil.copy2(raw,ATLAS/'atlas/sources'/('windmill_sail_joints_'+k+'_bake480.png'))
        for size in [1024,2048]:
            path=ATLAS/'textures'/('CSC_Props_Shared_01_'+k+'.png') if size==1024 else ATLAS/'atlas'/('CSC_Props_Shared_01_v2_'+k+'_Master2048.png')
            im=Image.open(path).convert('RGB');old=np.array(im);scale=size//1024
            px=patch.resize((120*scale,120*scale),Image.Resampling.LANCZOS)
            padded=Image.fromarray(np.pad(np.array(px),((4*scale,4*scale),(4*scale,4*scale),(0,0)),mode='edge'));im.paste(padded,(768*scale,512*scale));im.save(path)
            m=np.repeat(np.repeat(mask,scale,axis=0),scale,axis=1);assert np.array_equal(old[~m],np.array(im)[~m])
        texture_files.append(ATLAS/'textures'/('CSC_Props_Shared_01_'+k+'.png'))
    manifest['regions'].append(dict(id=slot,slot=slot,name='windmill_sail_joints',family='wood',bounds=[772,516,892,636],sources=sources,provenance='Selected-to-active Cycles normal and B/G/M bake from the existing ImageGen-textured windmill rail/rung/tie geometry; 480px source, eight rail-side strips. No newly drawn artwork.'))
    manifest['reserved_slots'].remove(slot);manifest['content_revision']=40;manifest['change_note']='Sail projecting joints baked into verified free slot38; all other swatches preserved.'
    manifest['production_sha256']={k:sha(ATLAS/'textures'/('CSC_Props_Shared_01_'+k+'.png')) for k in 'BNGM'}
    manifest_path.write_text(json.dumps(manifest,indent=2)+'\n')
    ao_path=ATLAS/'atlas/quarter-ao-manifest.json';ao=json.loads(ao_path.read_text())
    for family in ao['pages'][0]['quarters'][0]['families']:
        family['allocations']=[a for a in family.get('allocations',[]) if a['id'] not in [NAME+'_Timber',RUIN+'_Timber']]
    ao_path.write_text(json.dumps(ao,indent=2)+'\n')
    spec=importlib.util.spec_from_file_location('packer',ATLAS/'scripts/pack_quarter_ao.py');packer=importlib.util.module_from_spec(spec);spec.loader.exec_module(packer)
    before=Image.open(ATLAS/'textures/CSC_Props_Shared_01_AO.png').tobytes();packer.pack(ATLAS);assert Image.open(ATLAS/'textures/CSC_Props_Shared_01_AO.png').tobytes()==before
    libpath=ATLAS/'library.json';lib=json.loads(libpath.read_text());lib['surface_status']='Existing ImageGen wood/rope detail geometry-baked into free slot38 for simplified windmill rails.'
    lib['files']={p.relative_to(ATLAS).as_posix():sha(p) for p in ATLAS.rglob('*') if p.is_file() and p.name!='library.json'};libpath.write_text(json.dumps(lib,indent=2)+'\n')
    spec=importlib.util.spec_from_file_location('conv',ROOT/'project/tools/blender/scene_export/export_scene.py');conv=importlib.util.module_from_spec(spec);spec.loader.exec_module(conv)
    rows=json.loads((OUT/'install-plan.json').read_text())
    for src in texture_files:
        k=src.stem[-1];scalar=k in 'GM';fmt='R8_UNORM' if scalar else 'R8G8B8A8_UNORM';input_path=src
        if scalar:
            input_path=OUT/'scalar'/src.name;Image.open(src).getchannel('R').save(input_path)
        subprocess.run([str(ROOT/'project/tools/directxtex/texconv.exe'),'-nologo','-y','-m','0','-f',fmt,'--ignore-srgb','-o',str(STAGE/'Textures'),str(input_path)],check=True)
        dds=STAGE/'Textures'/(src.stem+'.dds');desc=dict(size=[1024,1024],format=fmt,slot=k)
        if scalar:conv.normalize_ao_dds(dds,desc,MOD/'Textures/CSC_Atlas_AO2.dds')
        conv.validate_dds(dds,desc);shutil.copy2(MOD/'Textures'/(src.stem+'.tex'),STAGE/'Textures'/(src.stem+'.tex'))
        dest=MOD/'Textures'/dds.name;backup=OUT/'before-installed'/('surface-'+dds.name);shutil.copy2(dest,backup)
        rows.append(dict(source=str(dds),destination=str(dest),backup=str(backup),before=sha(dest)))
    rows=[r for r in rows if sha(r['source'])!=r['before']];(OUT/'install-plan.json').write_text(json.dumps(rows,indent=2));print('SIMPLIFY_STAGED',len(rows))

if __name__=='__main__':globals()[sys.argv[1]]()
