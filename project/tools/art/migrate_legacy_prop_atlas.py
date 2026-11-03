"""Basket/well migration: preserve native geometry and reuse existing paint."""
import sys,json,shutil,subprocess,hashlib,copy,importlib.util,os,time
from pathlib import Path
import numpy as np
from PIL import Image
from storage_pivot_trial import ROOT,MOD,helper,parse,save,txt
OUT=Path('C:/Users/Shadow/Desktop/Codex/Basket-Well-shared-atlas-20261026')
ART=Path('C:/Users/Shadow/Desktop/Working Files/3D Art')
LIB=ART/'Textures/CSC_Props'
NAMES=['CSC_TAILORS_Basket','CSC_ALL_Well','CSC_ALL_Well_PIL']
STAGE=OUT/'atlas-release'
RELEASE='2026-10-26_Shared_01_r045'
PATCHES=[dict(name='legacy_tintable_well_timber',slot=40,box=[352,0,616,256]),
 dict(name='legacy_tailors_basket',slot=41,box=[878,810,962,889]),
 dict(name='legacy_well_limestone',slot=42,box=[832,302,980,462]),
 dict(name='legacy_well_dark_interior',slot=43,box=[648,256,780,465])]
AO_CELLS={'CSC_TAILORS_Basket':[1408,384,1536,512],'CSC_ALL_Well':[896,128,1024,256],'CSC_ALL_Well_PIL':[512,256,640,384]}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2),encoding='utf-8')
def inspect():
    OUT.mkdir(exist_ok=True);exe,_=helper(OUT/'cache');report={}
    for name in NAMES:
        dest=OUT/'native-before'/(name+'.json');dest.parent.mkdir(exist_ok=True)
        subprocess.run([str(exe),str(exe.parent),str(MOD/'Geometries'/(name+'.fgx')),str(dest)],cwd=exe.parent,check=True,capture_output=True)
        raw=json.loads(dest.read_text());meshes=[]
        for m in raw['meshes']:
            meshes.append(dict(name=m['name'],vertices=len(m['vertices']),groups=m['groups'],bindings=m['boneBindings'],uvs={k:[np.min([v[k] for v in m['vertices']],axis=0).tolist(),np.max([v[k] for v in m['vertices']],axis=0).tolist()] for k in ['uv','uv2','uv3']}))
        report[name]=meshes
    for n in ['CSC_Atlas_Props_B','CSC_Atlas_Props_B_T','CSC_Atlas_Props_T','CSC_Atlas_Props_AO']:
        Image.open(MOD/'Textures'/(n+'.dds')).save(OUT/(n+'.png'))
    write(OUT/'native-inspection.json',report);print(json.dumps(report,indent=2))

def prepare():
    assert not STAGE.exists()
    shutil.copytree(LIB/'Current',STAGE)
    write(OUT/'library-before.json',{p.relative_to(LIB/'Current').as_posix():sha(p) for p in (LIB/'Current').rglob('*') if p.is_file()})
    baseline={}
    for folder in ['Assets','Materials','Textures','Geometries','XLPs']:
        for p in (MOD/folder).glob('*'):
            if p.is_file():baseline[str(p)]=sha(p)
    write(OUT/'runtime-before.json',baseline)
    surface=json.loads((STAGE/'atlas/manifest.json').read_text())
    assert all(p['slot'] in surface['reserved_slots'] and p['slot'] not in [r['slot'] for r in surface['regions']] for p in PATCHES)
    # Existing paint only: remap bounded donor rectangles together across every
    # channel; reserved cells are the sole altered surface pixels.
    originals={k:Image.open(MOD/'Textures'/('CSC_Atlas_Props_'+('B_T' if k=='B' else k)+'.dds')).convert('RGBA') for k in ['B','N','G','M','T','AO']}
    originals['basket_B']=Image.open(MOD/'Textures/CSC_Atlas_Props_B.dds').convert('RGBA')
    for patch in PATCHES:
        slot=patch['slot'];x=(slot%8)*128;y=(slot//8)*128
        patch['bounds']=[x+4,y+4,x+124,y+124]
        sources={}
        for channel in ['B','N','G','M','T']:
            donor=originals['basket_B'] if channel=='B' and slot==41 else originals[channel]
            im=donor.crop(patch['box']).resize((120,120),Image.Resampling.LANCZOS if channel!='T' else Image.Resampling.NEAREST)
            if channel in ['G','M']:im=im.getchannel('R').convert('RGBA')
            src=STAGE/'atlas/sources'/(patch['name']+'_'+channel+'.png');im.save(src);sources[channel]='sources/'+src.name
            target=STAGE/'textures'/('CSC_Props_Shared_01_'+channel+'.png')
            atlas=Image.open(target).convert('RGBA') if target.exists() else Image.new('RGBA',(1024,1024),(0,0,0,255))
            padded=Image.fromarray(np.pad(np.array(im),((4,4),(4,4),(0,0)),mode='edge'))
            atlas.paste(padded,(x,y));atlas.save(target)
        surface['regions'].append(dict(id=max(r['id'] for r in surface['regions'])+1,name=patch['name'],family='legacy_reuse',slot=slot,bounds=patch['bounds'],sources=sources,provenance='Rectified/resampled existing CSC legacy paint; no new artwork',donor_box=patch['box']))
        surface['reserved_slots'].remove(slot)
    aom=json.loads((STAGE/'atlas/quarter-ao-manifest.json').read_text());allocated=[]
    for page in aom['pages']:
        if page['id']=='CSC_Props_Shared_01_AO':
            for quarter in page['quarters']:
                for family in quarter['families']:
                    allocated += [a.get('cell',a.get('bounds')) for a in family.get('allocations',[])]
    ao=Image.open(STAGE/'textures/CSC_Props_Shared_01_AO.png').convert('RGBA');jobs=[];mapping={}
    staged=OUT/'staged';(staged/'Geometries').mkdir(parents=True,exist_ok=True)
    for name in NAMES:
        raw=json.loads((OUT/'native-before'/(name+'.json')).read_text())
        olduv2=np.array([v['uv2'] for m in raw['meshes'] for v in m['vertices']])*1024
        box=np.r_[np.floor(olduv2.min(0))-2,np.ceil(olduv2.max(0))+2].astype(int).tolist()
        cell=AO_CELLS[name];x,y,x1,y1=cell
        assert all(not (x<b[2] and x1>b[0] and y<b[3] and y1>b[1]) for b in allocated if b)
        bounds=[x+4,y+4,x+124,y+124]
        patch=originals['AO'].getchannel('R').crop(box).resize((120,120),Image.Resampling.LANCZOS).convert('RGBA')
        ao.paste(Image.fromarray(np.pad(np.array(patch),((4,4),(4,4),(0,0)),mode='edge')),(x,y))
        aofile=STAGE/'atlas/sources'/(name+'_legacy_AO128.png');ao.crop(cell).save(aofile)
        for page in aom['pages']:
            if page['id']=='CSC_Props_Shared_01_AO':
                for quarter in page['quarters']:
                    for family in quarter['families']:
                        b=family['bounds']
                        if x>=b[0] and y>=b[1] and x1<=b[2] and y1<=b[3]:family.setdefault('allocations',[]).append(dict(id=name+'_RuntimeMigration',cell=cell,source='atlas/sources/'+aofile.name,reuse='Preserved legacy isolated AO; original earlier authoring allocations untouched'))
        for mesh in raw['meshes']:
            for v in mesh['vertices']:
                uv=np.array(v['uv'])*1024
                region=PATCHES[1] if name=='CSC_TAILORS_Basket' else PATCHES[0] if uv[1]<256 else PATCHES[2] if uv[0]>800 else PATCHES[3]
                old=np.array(region['box']);dest=np.array(region['bounds']);assert np.all(uv>=old[:2]) and np.all(uv<=old[2:]),(name,uv,old)
                v['uv']=((dest[:2]+(uv-old[:2])/(old[2:]-old[:2])*(dest[2:]-dest[:2]))/1024).tolist()
                u=np.array(v['uv2'])*1024;v['uv2']=((np.array(bounds[:2])+(u-box[:2])/(np.array(box[2:])-box[:2])*120)/2048).tolist()
                # Emissive UV3 stays untouched: both replacement materials keep
                # the existing CSC_Atlas_E binding and per-state emission flags.
        path=staged/'Geometries'/(name+'.json');write(path,raw);shutil.copy2(MOD/'Geometries'/(name+'.geo'),path.with_suffix('.geo'))
        mapping[name]=dict(AO_source_box=box,AO_cell=cell)
        jobs.append(dict(name=name,native=str(path),source=str(ART/'Props/Tailors/CSC_TAILORS_Basket.blend' if name=='CSC_TAILORS_Basket' else ART/'Props'/('CSC_ALL_is_Well'+('_PIL' if name.endswith('_PIL') else '')+'.blend'))))
    ao.save(STAGE/'textures/CSC_Props_Shared_01_AO.png')
    surface.update(content_revision=45,change_note='Four reused legacy basket/well surfaces; tint mask added; existing occupied texels unchanged.')
    aom['status']=RELEASE+': basket/well legacy AO added in three verified unoccupied cells.'
    write(STAGE/'atlas/manifest.json',surface);write(STAGE/'atlas/quarter-ao-manifest.json',aom);write(OUT/'mapping.json',dict(surface=PATCHES,AO=mapping))
    # Prove all previously occupied and unrelated surface/AO pixels unchanged.
    checks=[]
    for k in ['B','N','G','M','AO']:
        a=np.array(Image.open(LIB/'Current/textures'/('CSC_Props_Shared_01_'+k+'.png')).convert('RGBA'));b=np.array(Image.open(STAGE/'textures'/('CSC_Props_Shared_01_'+k+'.png')).convert('RGBA'))
        mask=np.ones(a.shape[:2],bool)
        rects=list(AO_CELLS.values()) if k=='AO' else [[(p['slot']%8)*128,(p['slot']//8)*128,(p['slot']%8+1)*128,(p['slot']//8+1)*128] for p in PATCHES]
        for x,y,x1,y1 in rects:mask[y:y1,x:x1]=False
        assert np.array_equal(a[mask],b[mask]),k;checks.append(dict(channel=k,previous_pixels_unchanged=True))
    write(OUT/'atlas-preservation.json',checks)
    for name in ['CSC_TAILORS_Basket','CSC_ALL_is_Well']:
        r=parse(MOD/'Assets'/(name+'.ast'))
        for node in r.findall('.//m_ObjectName'):
            if node.get('text')=='CSC_ALL_Props_E':node.set('text','CSC_ALL_Props_01')
            elif node.get('text')=='CSC_ALL_Props_ET':node.set('text','CSC_ALL_Props_01_T')
        save(r,staged/'Assets'/(name+'.ast'))
    mat=parse(MOD/'Materials/CSC_ALL_Props_01.mtl');mat.find('m_Name').set('text','CSC_ALL_Props_01_T')
    next(e for e in mat.findall('m_CookParams/m_Values/Element') if txt(e,'m_ParamName')=='TintMask').find('m_ObjectName').set('text','CSC_Props_Shared_01_T')
    save(mat,staged/'Materials/CSC_ALL_Props_01_T.mtl')
    write(OUT/'geometry-jobs.json',jobs);write(OUT/'variant-sources.json',[])
    print('PREPARED four surfaces, three AO cells; all prior atlas pixels preserved')

def textures():
    spec=importlib.util.spec_from_file_location('shared_dds',ROOT/'project/tools/blender/scene_export/export_scene.py');conv=importlib.util.module_from_spec(spec);spec.loader.exec_module(conv)
    dest=OUT/'staged/Textures';dest.mkdir(exist_ok=True)
    for k in ['B','N','G','M','AO','T']:
        name='CSC_Props_Shared_01_'+k;source=STAGE/'textures'/(name+'.png');size=Image.open(source).size
        scalar=k in ['G','M','AO'];fmt='R8_UNORM' if scalar else 'R8G8B8A8_UNORM'
        args=[str(ROOT/'project/tools/directxtex/texconv.exe'),'-nologo','-y','-m','0','-f',fmt,'--ignore-srgb','-o',str(dest)]
        if k=='B':args+=['-srgb']
        result=subprocess.run(args+[str(source)],capture_output=True,text=True);assert result.returncode==0,result.stdout+result.stderr
        desc=dict(format=fmt,size=list(size),slot=k)
        if scalar:conv.normalize_ao_dds(dest/(name+'.dds'),desc,MOD/'Textures/CSC_Props_Shared_01_AO.dds')
        conv.validate_dds(dest/(name+'.dds'),desc)
        a=np.array(Image.open(source).convert('RGBA'));b=np.array(Image.open(dest/(name+'.dds')).convert('RGBA'));assert np.array_equal(a[:,:,0] if scalar else a,b[:,:,0] if scalar else b)
        template=MOD/'Textures'/('CSC_Atlas_Props_T.tex' if k=='T' else name+'.tex');r=parse(template)
        r.find('m_Name').set('text',name);r.find('m_SourceFilePath').set('text',str(LIB/'Current/textures'/(name+'.png')))
        r.find('m_DataFiles/Element/m_RelativePath').set('text',name+'.dds')
        save(r,dest/(name+'.tex'))
    print('Six runtime maps validated, scalar DDS headers normalized')

def jobs():
    sys.path.insert(0,str(ROOT/'project/tools/blender'))
    from render_ae_asset import Resolver,Assembly,DEFAULT_SDK
    r=Resolver(MOD,DEFAULT_SDK)
    for p in (OUT/'staged').rglob('*'):
        if p.suffix in ['.ast','.mtl','.tex','.dds','.geo']:r.index[p.name.casefold()]={p}
    a=Assembly(r);materials={};geometry_jobs=json.loads((OUT/'geometry-jobs.json').read_text());before={}
    for job in geometry_jobs:
        name=job['name'];descriptor=parse(MOD/'Geometries'/(name+'.geo'))
        ident='CSC_ALL_Props_01' if 'Basket' in name else 'CSC_ALL_Props_01_T'
        k=a.material(ident,{},MOD,False);job['groups']={};job['materials']={}
        for m in descriptor.findall('m_Meshes/Element'):
            mesh=txt(m,'m_Name');groups=[txt(g,'m_Name') for g in m.findall('m_Groups/Element')]
            job['groups'][mesh]=groups;job['materials'][mesh]={g:k for g in groups}
        old=Assembly(Resolver(MOD,DEFAULT_SDK));oldkey=old.material('CSC_ALL_Props_E' if 'Basket' in name else 'CSC_ALL_Props_ET',{},MOD,False)
        before[name]=old.materials[oldkey]
    write(OUT/'materials.json',a.materials);write(OUT/'before-materials.json',before);write(OUT/'geometry-jobs.json',geometry_jobs)
    shutil.copy2(ROOT/'project/tools/blender/ae_render_camera_presets.json',OUT/'staged/ae_render_camera_presets.json')
    print('Prepared three source jobs and before/after material records')

def convert():
    import l2_placement_migration as migration
    migration.OUT=OUT;old=sys.argv;sys.argv=['migration','convert']
    try:migration.convert()
    finally:sys.argv=old
    checks=[]
    for name in NAMES:
        before=json.loads((OUT/'native-before'/(name+'.json')).read_text());after=json.loads((OUT/'native-after'/(name+'.json')).read_text())
        for a,b in zip(before['meshes'],after['meshes']):
            assert a['triangles']==b['triangles'] and len(a['vertices'])==len(b['vertices'])
            for k in ['position','normal','tangent','binormal','uv3']:
                assert np.max(abs(np.array([v[k] for v in a['vertices']])-np.array([v[k] for v in b['vertices']])))<1e-5,(name,k)
        checks.append(dict(geometry=name,only_UV1_and_UV2_changed=True))
    write(OUT/'geometry-preservation.json',checks)

def finalize():
    from scipy.spatial import cKDTree
    checks=[]
    for row in json.loads((OUT/'source-build-report.json').read_text()):
        raw=json.loads((OUT/'staged/Geometries'/(row['name']+'.json')).read_text())
        parts=(OUT/'source-export'/(row['name']+'.cn6')).read_text().split('mesh:"')[1:]
        assert len(parts)==len(raw['meshes'])
        for part in parts:
            name,body=part.split('"',1);block=body.split('vertices\n',1)[1].split('triangles\n',1)[0]
            a=np.array([[float(x) for x in line.split()[:18]] for line in block.strip().splitlines()]);mesh=next(m for m in raw['meshes'] if m['name']==name)
            b=np.array([[x for k in ['position','normal','tangent','binormal','uv','uv2','uv3'] for x in v[k]] for v in mesh['vertices']])
            assert len(a)==len(b);error=max(cKDTree(a).query(b)[0].max(),cKDTree(b).query(a)[0].max());assert error<.0002,error
            checks.append(dict(source=row['name'],export_error=float(error)))
    # Assert only the requested material names changed in the two ASTs.
    for name in ['CSC_TAILORS_Basket','CSC_ALL_is_Well']:
        a=parse(MOD/'Assets'/(name+'.ast'));b=parse(OUT/'staged/Assets'/(name+'.ast'))
        for e in a.findall('.//m_ObjectName'):
            e.set('text',{'CSC_ALL_Props_E':'CSC_ALL_Props_01','CSC_ALL_Props_ET':'CSC_ALL_Props_01_T'}.get(e.get('text'),e.get('text')))
        from lxml import etree as E
        assert E.tostring(a)==E.tostring(b),name
    write(OUT/'saved-source-export-parity.json',checks)
    # A portable overlay rebuild uses only saved patches and allocations.
    recipe='''from pathlib import Path
import json
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[1]
m=json.loads((root/'atlas/manifest.json').read_text())
for channel in ['B','N','G','M','T']:
 p=root/'textures'/('CSC_Props_Shared_01_'+channel+'.png')
 page=Image.open(p).convert('RGBA') if p.exists() else Image.new('RGBA',(1024,1024),(0,0,0,255))
 for region in m['regions']:
  if region.get('family')!='legacy_reuse':continue
  patch=Image.open(root/'atlas'/region['sources'][channel]).convert('RGBA')
  page.paste(Image.fromarray(np.pad(np.array(patch),((4,4),(4,4),(0,0)),mode='edge')),(region['slot']%8*128,region['slot']//8*128))
 page.save(p)
mapping=json.loads((root/'atlas/basket-well-migration.json').read_text())
p=root/'textures/CSC_Props_Shared_01_AO.png';page=Image.open(p).convert('RGBA')
for name,entry in mapping['AO'].items():page.paste(Image.open(root/'atlas/sources'/(name+'_legacy_AO128.png')),tuple(entry['AO_cell'][:2]))
page.save(p)
'''
    write(STAGE/'atlas/basket-well-migration.json',json.loads((OUT/'mapping.json').read_text()))
    recipepath=STAGE/'scripts/pack_basket_well.py';recipepath.write_text(recipe,encoding='utf-8')
    hashes={p.name:sha(p) for p in (STAGE/'textures').glob('*.png')}
    subprocess.run([sys.executable,str(recipepath)],check=True)
    assert all(sha(STAGE/'textures'/n)==h for n,h in hashes.items()),'Rebuild must reproduce exact PNGs'
    surface=json.loads((STAGE/'atlas/manifest.json').read_text())
    surface['production_files']['T']='textures/CSC_Props_Shared_01_T.png'
    surface['production_sha256']={k:sha(STAGE/'textures'/('CSC_Props_Shared_01_'+k+'.png')) for k in ['B','N','G','M','T']}
    write(STAGE/'atlas/manifest.json',surface)
    for k in ['B','N','G','M','T']:
        master=STAGE/'atlas'/('CSC_Props_Shared_01_v2_'+k+'_Master2048.png')
        im=Image.open(master).convert('RGBA') if master.exists() else Image.new('RGBA',(2048,2048),(0,0,0,255))
        for patch in PATCHES:
            src=Image.open(STAGE/'atlas/sources'/(patch['name']+'_'+k+'.png')).convert('RGBA').resize((240,240),Image.Resampling.NEAREST if k=='T' else Image.Resampling.LANCZOS)
            im.paste(Image.fromarray(np.pad(np.array(src),((8,8),(8,8),(0,0)),mode='edge')),((patch['slot']%8)*256,(patch['slot']//8)*256))
        im.save(master)
    lib=json.loads((STAGE/'library.json').read_text());lib.update(release=RELEASE,accepted_on='2026-10-26',content_revision=45,snapshot_path='Releases/'+RELEASE,
        surface_status='Basket/well legacy paint in four verified free cells; every previous pixel preserved.',AO_status='Three preserved legacy AO patches in verified free cells; other AO unchanged.',review_status='Saved-source/native parity and paired visual review passed; cook evidence in migration folder.')
    lib['runtime_bindings']['tint_mask']='textures/CSC_Props_Shared_01_T.png';lib['rebuild']['basket_well']='python scripts/pack_basket_well.py'
    lib['files']={p.relative_to(STAGE).as_posix():sha(p) for p in STAGE.rglob('*') if p.is_file() and p.name!='library.json'}
    write(STAGE/'library.json',lib)
    retire=['Materials/CSC_ALL_Props_E.mtl','Materials/CSC_ALL_Props_ET.mtl']+[f'Textures/CSC_Atlas_Props_{k}{ext}' for k in ['B','B_T','N','AO','M','G','T'] for ext in ['.tex','.dds']]
    write(OUT/'retire.json',retire)
    import audit_art_orphans as audit
    for phase in ['before','after']:
        pantry=OUT/('cook-'+phase)/'pantry'
        for folder in audit.FOLDERS+['XLPs','ArtDefs']:
            for p in (MOD/folder).rglob('*'):
                if not p.is_file():continue
                rel=p.relative_to(MOD)
                if phase=='after' and rel.as_posix() in retire:continue
                dst=pantry/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dst)
        if phase=='after':
            for p in (OUT/'staged').rglob('*'):
                if p.suffix not in ['.ast','.geo','.fgx','.mtl','.tex','.dds']:continue
                dst=pantry/p.relative_to(OUT/'staged');dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dst)
    print('Saved masters reproduce native UVs; atlas rebuild exact; cook snapshots prepared')

def cook():
    import cleanup_art_orphans as cleanup
    cleanup.OUT=OUT;cleanup.cook(sys.argv[2])

def publish():
    import re
    from lxml import etree as E
    archive=Path('C:/Users/Shadow/Desktop/Archive/CSC-basket-well-atlas-20261026');assert not archive.exists()
    for phase in ['before','after']:
        r=json.loads((OUT/('cook-'+phase)/'results/result.json').read_text());assert r['exit_code']==0 and r['blps']
    baseline=json.loads((OUT/'runtime-before.json').read_text())
    for path,h in baseline.items():assert sha(Path(path))==h,('Changed while preparing',path)
    library_before=json.loads((OUT/'library-before.json').read_text())
    assert all(sha(LIB/'Current'/p)==h for p,h in library_before.items())
    assert json.loads((LIB/'CURRENT.json').read_text())['release']=='2026-10-24_Shared_01_r044'
    retire=json.loads((OUT/'retire.json').read_text());newfiles={p.relative_to(OUT/'staged').as_posix():p for p in (OUT/'staged').rglob('*') if p.suffix in ['.ast','.geo','.fgx','.mtl','.tex','.dds']}
    project=MOD/'Civ Supply Chains.civ6proj';project_before=project.read_bytes()
    def strip(m):return b'' if m.group(1).decode().replace('\\','/') in retire else m.group(0)
    updated=re.sub(rb'(?m)^[ \t]*<Content\s+Include="([^"]+)"[^>]*(?:/>|>.*?</Content>)[ \t]*\r?\n',strip,project_before,flags=re.S)
    additions=[]
    for rel in ['Materials/CSC_ALL_Props_01_T.mtl','Textures/CSC_Props_Shared_01_T.tex','Textures/CSC_Props_Shared_01_T.dds']:
        include=rel.replace('/','\\')
        if ('Include="'+include+'"').encode() not in updated:additions.append('    <Content Include="'+include+'"><SubType>Content</SubType></Content>\r\n')
    updated=updated.replace(b'</Project>',('  <ItemGroup>\r\n'+''.join(additions)+'  </ItemGroup>\r\n</Project>').encode());E.fromstring(updated)
    cachepath=Path(os.environ['APPDATA'])/'AssetCloud/mod-Civ Supply Chains-asset-deps.json';cachebytes=cachepath.read_bytes();cache=json.loads(cachebytes.decode('utf-8-sig'))
    dead={'Civ Supply Chains/'+p for p in retire};cache['Files']=[e for e in cache['Files'] if e['Filename'].replace('\\','/') not in dead]
    cache['Dependencies']={k:[d for d in ds if d.replace('\\','/') not in dead] for k,ds in cache['Dependencies'].items() if k.replace('\\','/') not in dead}
    idx={(Path(e['Filename']).suffix.casefold(),Path(e['Filename']).stem.casefold()):e['Filename'].replace('\\','/') for e in cache['Files']}
    idx.update({(Path(rel).suffix.casefold(),Path(rel).stem.casefold()):'Civ Supply Chains/'+rel for rel in newfiles})
    records={e['Filename'].replace('\\','/'):e for e in cache['Files']};now=int(time.time()*1e7)+116444736000000000
    for rel,p in newfiles.items():
        key='Civ Supply Chains/'+rel
        if p.suffix not in ['.ast','.geo','.mtl','.tex']:continue
        r=parse(p);deps=[]
        for e in r.findall('.//Element'):
            kind=e.find('m_eObjectType');name=e.find('m_ObjectName')
            if kind is not None and name is not None and name.get('text'):
                ext={'MATERIAL':'.mtl','TEXTURE':'.tex'}.get(kind.text)
                if ext:deps.append(idx[(ext,name.get('text').replace('\\','/').split('/')[-1].casefold())])
        for e in r.findall('.//m_GeoName'):
            if e.get('text'):deps.append(idx[('.geo',e.get('text').casefold())])
        for e in r.findall('m_DataFiles/Element/m_RelativePath'):deps.append('Civ Supply Chains/'+str(Path(rel).parent/e.get('text')).replace('\\','/'))
        cache['Dependencies'][key]=sorted(set(deps))
        if key in records:records[key].update(Timestamp=now,Filesize=p.stat().st_size)
        else:
            template=copy.deepcopy(next(e for e in cache['Files'] if Path(e['Filename']).suffix==p.suffix))
            template.update(Filename=key,Timestamp=now,Filesize=p.stat().st_size,EntityClass=txt(r,'m_ClassName'),Tags=[],Stats={});cache['Files'].append(template)
    cache['Timestamp']=now
    archive.mkdir(parents=True)
    def backup(src,rel):
        if src.exists():dst=archive/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst);assert sha(src)==sha(dst)
    for rel in set(retire)|set(newfiles):backup(MOD/rel,Path('mod-before')/rel)
    backup(project,Path('registrations')/project.name);backup(cachepath,Path('registrations/AssetCloud-before.json'))
    shutil.copytree(LIB/'Current',archive/'atlas-before/Current');backup(LIB/'CURRENT.json',Path('atlas-before/CURRENT.json'))
    rows=json.loads((OUT/'source-build-report.json').read_text())
    for row in rows:
        dst=Path(row['destination']);backup(dst,Path('sources-before')/dst.relative_to(ART))
    assert project.read_bytes()==project_before and cachepath.read_bytes()==cachebytes
    release=LIB/'Releases'/RELEASE;assert not release.exists();shutil.copytree(STAGE,release)
    for rel,p in newfiles.items():shutil.copy2(p,MOD/rel)
    for rel in retire:
        p=(MOD/rel).resolve();assert p.is_relative_to(MOD.resolve()) and sha(p)==sha(archive/'mod-before'/rel);p.unlink()
    project.write_bytes(updated);cachepath.write_text(json.dumps(cache,separators=(',',':')),encoding='utf-8')
    shutil.copytree(STAGE,LIB/'Current',dirs_exist_ok=True)
    write(LIB/'CURRENT.json',dict(release=RELEASE,current='Current',manifest='Current/library.json',snapshot='Releases/'+RELEASE,updated_on='2026-10-26',library_sha256=sha(LIB/'Current/library.json')))
    for row in rows:
        src=Path(row['source']);dst=Path(row['destination']);shutil.copy2(src,dst)
        for p in (src.parent/'textures').glob('*.png'):
            target=dst.parent/'textures'/p.name;target.parent.mkdir(exist_ok=True)
            if target.exists():assert sha(target)==sha(p),('Hashed snapshot collision',target)
            else:shutil.copy2(p,target)
        export=dst.parent/'exports'/row['name'];export.mkdir(parents=True,exist_ok=True)
        for ext in ['.cn6','.fgx','.geo']:
            target=export/(row['name']+ext);backup(target,Path('sources-before')/target.relative_to(ART));shutil.copy2(OUT/'staged/Geometries'/(row['name']+ext),target)
    write(OUT/'install-report.json',dict(archive=str(archive),release=RELEASE,retired=retire,updated=list(newfiles),masters=rows))
    print('PUBLISHED',RELEASE,'three masters; sixteen legacy files archived')

def verify():
    import contextlib,io
    import audit_art_orphans as audit
    report=json.loads((OUT/'install-report.json').read_text());baseline=json.loads((OUT/'runtime-before.json').read_text())
    changed={str(MOD/p) for p in report['updated']+report['retired']};unchanged=0
    for p,h in baseline.items():
        if p not in changed:assert sha(Path(p))==h,p;unchanged+=1
    for rel in report['retired']:assert not (MOD/rel).exists() and (Path(report['archive'])/'mod-before'/rel).exists()
    for rel in report['updated']:
        live=MOD/rel;staged=OUT/'staged'/rel
        if live.suffix=='.dds':
            assert np.array_equal(np.array(Image.open(live)),np.array(Image.open(staged))),rel
        else:assert sha(live)==sha(staged),rel
    for row in report['masters']:
        assert sha(Path(row['source']))==sha(Path(row['destination']))
        for p in (Path(row['source']).parent/'textures').glob('*.png'):assert sha(p)==sha(Path(row['destination']).parent/'textures'/p.name)
    # Complete release metadata with the installed editable masters and cook proof.
    lib=json.loads((STAGE/'library.json').read_text())
    lib['basket_well_migration']=dict(native_geometry_preserved=True,AE_placements_preserved=True,prior_atlas_pixels_preserved=True,cook_before_after_pass=True,
        source_masters={str(Path(r['destination']).relative_to(ART)):sha(Path(r['destination'])) for r in report['masters']})
    for base in [STAGE,LIB/'Current',LIB/'Releases'/RELEASE]:write(base/'library.json',lib)
    current=json.loads((LIB/'CURRENT.json').read_text());current['library_sha256']=sha(LIB/'Current/library.json');write(LIB/'CURRENT.json',current)
    for rel,h in lib['files'].items():assert sha(LIB/'Current'/rel)==h and sha(LIB/'Releases'/RELEASE/rel)==h,rel
    # Include the new DDS payload record as well as its TEX entity in AE's index.
    cp=Path(os.environ['APPDATA'])/'AssetCloud/mod-Civ Supply Chains-asset-deps.json';cache=json.loads(cp.read_text(encoding='utf-8-sig'));key='Civ Supply Chains/Textures/CSC_Props_Shared_01_T.dds'
    if not any(e['Filename'].replace('\\','/')==key for e in cache['Files']):
        e=copy.deepcopy(next(e for e in cache['Files'] if e['Filename'].replace('\\','/')=='Civ Supply Chains/Textures/CSC_Props_Shared_01_N.dds'))
        e.update(Filename=key,Filesize=(MOD/'Textures/CSC_Props_Shared_01_T.dds').stat().st_size,Timestamp=int(time.time()*1e7)+116444736000000000)
        cache['Files'].append(e);cache['Timestamp']=e['Timestamp'];cp.write_text(json.dumps(cache,separators=(',',':')),encoding='utf-8')
    with contextlib.redirect_stdout(io.StringIO()):audit.run(OUT/'post-migration-audit',False)
    audited=json.loads((OUT/'post-migration-audit/audit.json').read_text());assert not audited['errors']
    assert all('CSC_ALL_Props_E' not in r['path'] and 'CSC_Atlas_Props_' not in r['path'] for r in audited['rows'])
    statuses={r['path']:r['status'] for r in audited['rows']}
    assert statuses['Materials/CSC_ALL_Props_01_T.mtl']=='runtime' and statuses['Textures/CSC_Props_Shared_01_T.tex']=='runtime'
    old_bytes=sum((Path(report['archive'])/'mod-before'/p).stat().st_size for p in report['retired'])
    added_bytes=sum((MOD/p).stat().st_size for p in report['updated'] if str(MOD/p) not in baseline)
    cooked={p:json.loads((OUT/('cook-'+p)/'results/result.json').read_text())['blps'][0]['bytes'] for p in ['before','after']}
    result=dict(release=RELEASE,unchanged_runtime_files=unchanged,three_installed_masters_match=True,old_materials_and_textures_retired=True,shared_emissive_preserved=True,
        net_removed_runtime_files=len(report['retired'])-3,retired_bytes=old_bytes,new_file_bytes=added_bytes,cooked_package_bytes=cooked,
        unresolved=audited['unresolved'],native_game_review=False)
    write(OUT/'final-verification.json',result);write(Path(report['archive'])/'completed.json',result)
    print(json.dumps(result,indent=2))

def receipts():
    report=json.loads((OUT/'install-report.json').read_text());archive=Path(report['archive'])
    for name in ['final-verification.json','install-report.json','geometry-preservation.json','atlas-preservation.json','saved-source-export-parity.json','installed-source-validation.json','mapping.json']:
        shutil.copy2(OUT/name,archive/name)
    for phase in ['before','after']:
        dst=archive/'cook-evidence'/phase;dst.mkdir(parents=True,exist_ok=True)
        for name in ['command.json','result.json','stdout.log']:shutil.copy2(OUT/('cook-'+phase)/'results'/name,dst/name)
    (archive/'README.txt').write_text('''Basket and shared well atlas migration — 26 October 2026

Published 2026-10-26_Shared_01_r045 to CSC_Props/Current and Releases.
Basket now binds CSC_ALL_Props_01. Shared well, including its pillaged mesh,
binds CSC_ALL_Props_01_T with the new CSC_Props_Shared_01_T tint mask.
Existing paint reused in four free cells (40–43); original occupied pixels
and all other AO allocations unchanged. Original tint mask copied with the
wood patch. No new artwork generated. Three native geometries changed UV1/UV2
only; mesh positions, topology, normals, emission UVs and AE placements kept.

Both old materials and seven legacy TEX/DDS pairs are archived under mod-before.
Shared CSC_Atlas_E and reserved CSC_Props_Shared_01_E remain in use/preserved.
Net CSC reduction: one material, six texture families, thirteen files.
Raw source-file saving approximately 16 MiB; cooked Tilebases saving 1,536 bytes.
XLP entry count unchanged. Both isolated native cooks succeeded.

Three editable masters updated in place:
Working Files/3D Art/Props/Tailors/CSC_TAILORS_Basket.blend
Working Files/3D Art/Props/CSC_ALL_is_Well.blend
Working Files/3D Art/Props/CSC_ALL_is_Well_PIL.blend
Each has local texture snapshots and an exports/<geometry>/ folder.
Original masters are in sources-before. Original shared library in atlas-before.

All 520 unaffected runtime art files are hash-verified unchanged. Installed
masters reopened and validated; saved CN6 exports reproduce the migrated native
data. Paired renders preserve appearance, including a green tint preview.
Native in-game tint/appearance review has not been performed.

One pre-existing Bakers Classical Base09 attachment still uses the older
CSC_BAKERS_Well asset with missing same-name material. This task does not change
that separate assembly or its placement.

Restoration: merge selected original mod files and registrations back, and
restore original masters/atlas only after checking for subsequent edits.
Do not blindly overwrite a later shared-library release or AE cache.
''',encoding='utf-8')
    print('Archive evidence and restoration notes saved')
if __name__=='__main__':globals()[sys.argv[1]]()
