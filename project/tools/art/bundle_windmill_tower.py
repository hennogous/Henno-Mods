"""Combine each saved Wind Mill building/tower layout, retaining its native clip."""
import sys,json,copy,hashlib,subprocess,importlib.util,shutil,os,time,re,struct,contextlib,io
from pathlib import Path
import numpy as np
from storage_pivot_trial import ROOT,MOD,helper,parse,save,txt,POINTS,MODELS,BINDINGS,point_matrix
from scipy.spatial.transform import Rotation
from lxml import etree as E
OUT=Path('C:/Users/Shadow/Desktop/Codex/Windmill-bundled-tower-20261026')
ART=Path('C:/Users/Shadow/Desktop/Working Files/3D Art')
DEST=ART/'BAKERS/Wind Mill'
TOWER='CSC_BAKERS_Wind_Mill_Tower'
PARENTS=['CSC_BAKERS_Wind_Mill','CSC_BAKERS_Wind_Mill_2']
ARCHIVE=Path('C:/Users/Shadow/Desktop/Archive/CSC-windmill-tower-bundled-20261026')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2),encoding='utf-8')
def readmotion(path):
    lines=[l.strip() for l in path.read_text().splitlines() if l.strip() and not l.startswith('//')]
    count=int(lines[1].split(':')[1]);nb=int(lines[5].split(':')[1]);i=6;tracks={}
    for _ in range(nb):
        name=lines[i];i+=1;tracks[name]=np.array([list(map(float,l.split())) for l in lines[i:i+count]]).reshape(count,4,4).transpose(0,2,1);i+=count
    return tracks
def localmatrix(b):
    m=np.eye(4);m[:3,:3]=Rotation.from_quat(b['local']['orientation']).as_matrix();m[:3,3]=b['local']['position'];return m
def makebone(name,parent,m):
    return dict(name=name,parent=parent,local=dict(position=m[:3,3].tolist(),orientation=Rotation.from_matrix(m[:3,:3]).as_quat().tolist(),scaleShear=np.eye(3).flatten().tolist()))
def inspect():
    OUT.mkdir(exist_ok=True);exe,_=helper(OUT/'cache');report={};geos=set()
    for name in [*PARENTS,TOWER]:
        r=parse(MOD/'Assets'/(name+'.ast'));models=[];points=[]
        for m in r.findall(MODELS+'/Element'):
            geos.add(txt(m,'m_GeoName'));models.append(dict(instance=txt(m,'m_Name'),geo=txt(m,'m_GeoName'),states=[dict(mesh=txt(g,'m_MeshName'),group=txt(g,'m_GroupName'),state=txt(g,'m_StateName'),values={txt(v,'m_ParamName'):(v.findtext('m_bValue') or (v.find('m_ObjectName').get('text') if v.find('m_ObjectName') is not None else '')) for v in g.findall('m_Values/m_Values/Element')}) for g in m.findall('m_GroupStates/Element')]))
        for p in r.findall(POINTS+'/Element'):
            entry=p.find('.//m_EntryName')
            if entry is not None and entry.get('text')==TOWER:points.append(dict(name=txt(p,'m_Name'),bone=txt(p,'m_BoneName'),model=txt(p,'m_ModelInstanceName'),matrix=point_matrix(p).tolist()))
        report[name]=dict(models=models,tower_points=points,bindings=[dict(slot=txt(b,'m_SlotName'),animation=txt(b,'m_AnimationName')) for b in r.findall(BINDINGS+'/Element')])
    for name in sorted(geos):
        p=OUT/'native-before'/(name+'.json');p.parent.mkdir(exist_ok=True)
        subprocess.run([str(exe),str(exe.parent),str(MOD/'Geometries'/(name+'.fgx')),str(p)],cwd=exe.parent,check=True,capture_output=True)
        raw=json.loads(p.read_text());print(name,[(m['name'],len(m['vertices']),m['boneBindings']) for m in raw['meshes']],[(b['name'],b['parent'],b['local']) for b in raw['models'][0]['bones']])
    write(OUT/'inspection.json',report)
    write(OUT/'protected.json',{str(p):sha(p) for folder in ['Assets','Geometries','Materials','Textures','Animations','ArtDefs','XLPs'] for p in (MOD/folder).glob('*') if p.is_file()})
    spec=importlib.util.spec_from_file_location('backend',Path.home()/'.codex/skills/civ6-art/scripts/civ6_animation/backend.py');backend=importlib.util.module_from_spec(spec);spec.loader.exec_module(backend)
    print(backend.run(r'C:\Program Files (x86)\CivNexus6_Release-1.3.3\CivNexus6','extract',MOD/'Geometries'/(TOWER+'.fgx'),MOD/'Animations'/(TOWER+'_Turn.fgx'),OUT/'motion-before',30,0,0))

def prepare():
    info=json.loads((OUT/'inspection.json').read_text());T=np.array(info[PARENTS[0]]['tower_points'][0]['matrix']);s=np.linalg.norm(T[:3,0]);R=T[:3,:3]/s
    assert np.max(abs(R.T@R-np.eye(3)))<1e-6
    mount=T.copy();mount[:3,:3]=R
    tracks=readmotion(OUT/'motion-before/clip.na2');local=np.linalg.inv(tracks['Root'])@tracks['Sails']
    assert np.max(abs(local[:,:3,3]-local[0,:3,3]))<.0001,'Existing clip contains sail translation; cannot use fixed pivot offset'
    assert np.max(abs(tracks['Root']-tracks['Root'][0]))<.00001
    materials={};jobs=[]
    from render_ae_asset import Resolver,Assembly,DEFAULT_SDK
    resolver=Resolver(MOD,DEFAULT_SDK);assembly=Assembly(resolver)
    for suffix in ['', '_CON+PIL']:
        name=PARENTS[0]+suffix;base='CSC_Level_1_S'+suffix;tower=TOWER+suffix
        a=json.loads((OUT/'native-before'/(base+'.json')).read_text());b=json.loads((OUT/'native-before'/(tower+'.json')).read_text())
        raw=copy.deepcopy(a);model=raw['models'][0];model['name']=tower
        # Granny binds the unchanged clip by its original model/track-group name.
        bones=[makebone(tower,-1,np.eye(4)),makebone(base,0,np.eye(4))]
        for bone in a['models'][0]['bones'][1:]:
            n=copy.deepcopy(bone);n['parent']+=1;bones.append(n)
        mount_index=len(bones);bones.append(makebone('Windmill_Tower_Mount',0,mount))
        original=b['models'][0]['bones'];root=copy.deepcopy(original[1]);assert root['name']=='Root' and np.max(np.abs(root['local']['position']))<1e-8
        root['parent']=mount_index;root_index=len(bones);bones.append(root)
        if not suffix:
            sails=copy.deepcopy(original[2]);assert sails['name']=='Sails'
            offset=np.eye(4);offset[:3,3]=(s-1)*np.array(sails['local']['position'])
            offset_index=len(bones);bones.append(makebone('Windmill_Sail_Pivot_Offset',root_index,offset))
            sails['parent']=offset_index;bones.append(sails)
        world=[]
        for bone in bones:
            m=localmatrix(bone);m=world[bone['parent']]@m if bone['parent']>=0 else m;world.append(m);bone['inverseWorld']=np.linalg.inv(m).T.flatten().tolist()
        model['bones']=bones
        for mesh in b['meshes']:
            mesh=copy.deepcopy(mesh)
            for v in mesh['vertices']:
                v['position']=(T@np.r_[v['position'],1])[:3].tolist()
                for key in ['normal','tangent','binormal']:v[key]=(R@v[key]).tolist()
            raw['meshes'].append(mesh)
        model['meshBindings']=[m['name'] for m in raw['meshes']]
        geo=parse(MOD/'Geometries'/(base+'.geo'))
        for m in parse(MOD/'Geometries'/(tower+'.geo')).findall('m_Meshes/Element'):geo.find('m_Meshes').append(copy.deepcopy(m))
        geo.find('m_Bones').clear()
        for bone in bones:E.SubElement(geo.find('m_Bones'),'Element',text=bone['name'])
        for key in ['m_Name','m_Description']:geo.find(key).set('text',name)
        geo.find('m_ModelName').set('text',tower)
        geo.find('m_DataFiles/Element/m_RelativePath').set('text',name+'.fgx')
        dest=OUT/'staged/Geometries'/(name+'.json');write(dest,raw);save(geo,dest.with_suffix('.geo'))
        # Saved group bindings, including construction/pillage visibility, are authoritative.
        groups={txt(m,'m_Name'):[txt(g,'m_Name') for g in m.findall('m_Groups/Element')] for m in geo.findall('m_Meshes/Element')};bindings={}
        for astname,geoname in [(PARENTS[0],base),(TOWER,tower)]:
            ast=parse(MOD/'Assets'/(astname+'.ast'));mi=next(m for m in ast.findall(MODELS+'/Element') if txt(m,'m_GeoName')==geoname)
            for g in mi.findall('m_GroupStates/Element'):
                for v in g.findall('m_Values/m_Values/Element'):
                    if txt(v,'m_ParamName')=='Material' and txt(v,'m_ObjectName'):
                        key=assembly.material(txt(v,'m_ObjectName'),{},MOD,False);bindings.setdefault(txt(g,'m_MeshName'),{})[txt(g,'m_GroupName')]=key
        jobs.append(dict(name=name,native=str(dest),groups=groups,materials=bindings,source=str(DEST/(name+'.blend'))))
    write(OUT/'geometry-jobs.json',jobs);write(OUT/'materials.json',assembly.materials)
    tower_ast=parse(MOD/'Assets'/(TOWER+'.ast'))
    for name in PARENTS:
        ast=parse(MOD/'Assets'/(name+'.ast'));points=ast.find(POINTS)
        removed=[p for p in points if p.find('.//m_EntryName') is not None and p.find('.//m_EntryName').get('text')==TOWER];assert len(removed)==1
        points.remove(removed[0])
        for suffix in ['', '_CON+PIL']:
            mi=next(m for m in ast.findall(MODELS+'/Element') if txt(m,'m_GeoName')=='CSC_Level_1_S'+suffix)
            mi.find('m_GeoName').set('text',PARENTS[0]+suffix)
            tm=next(m for m in tower_ast.findall(MODELS+'/Element') if txt(m,'m_GeoName')==TOWER+suffix)
            for g in tm.findall('m_GroupStates/Element'):mi.find('m_GroupStates').append(copy.deepcopy(g))
        bindings=ast.find(BINDINGS)
        for old in list(bindings):
            if txt(old,'m_SlotName')=='WORKED_A':assert not txt(old,'m_AnimationName');bindings.remove(old)
        for b in tower_ast.findall(BINDINGS+'/Element'):bindings.append(copy.deepcopy(b))
        refs=ast.find('m_BehaviorData/m_referenceGeometryNames');refs.clear()
        for suffix in ['', '_CON+PIL']:E.SubElement(refs,'Element',text=PARENTS[0]+suffix)
        save(ast,OUT/'staged/Assets'/(name+'.ast'))
    write(OUT/'standardization.json',dict(chosen_layout='regular Wind Mill',matrix=T.tolist(),scale=s,previous_expanded_matrix=info[PARENTS[1]]['tower_points'][0]['matrix'],original_animation_unchanged=True,fixed_pivot_offset=True))
    print('Prepared two shared combined models; both variants use regular placement; original animation tracks retained.')

def convert():
    import l2_placement_migration as m
    m.OUT=OUT;args=sys.argv;sys.argv=['bundle','convert']
    try:m.convert()
    finally:sys.argv=args
    spec=importlib.util.spec_from_file_location('backend',Path.home()/'.codex/skills/civ6-art/scripts/civ6_animation/backend.py');backend=importlib.util.module_from_spec(spec);spec.loader.exec_module(backend)
    print(backend.run(r'C:\Program Files (x86)\CivNexus6_Release-1.3.3\CivNexus6','extract',OUT/'staged/Geometries'/(PARENTS[0]+'.fgx'),MOD/'Animations'/(TOWER+'_Turn.fgx'),OUT/'motion-after',30,0,0))
    before=readmotion(OUT/'motion-before/clip.na2');after=readmotion(OUT/'motion-after/clip.na2');T=np.array(json.loads((OUT/'standardization.json').read_text())['matrix'])
    old=json.loads((OUT/'native-before'/(TOWER+'.json')).read_text());new=json.loads((OUT/'native-after'/(PARENTS[0]+'.json')).read_text())
    oldbones={b['name']:b for b in old['models'][0]['bones']};newbones={b['name']:b for b in new['models'][0]['bones']};maximum=0
    for m in old['meshes']:
        n=next(n for n in new['meshes'] if n['name']==m['name']);bone=m['boneBindings'][0]
        a=np.array([[*v['position'],1] for v in m['vertices']]).T;b=np.array([[*v['position'],1] for v in n['vertices']]).T
        expected=T@before[bone]@np.array(oldbones[bone]['inverseWorld']).reshape(4,4).T@a
        actual=after[bone]@np.array(newbones[bone]['inverseWorld']).reshape(4,4).T@b
        error=float(np.max(abs(actual-expected)));maximum=max(maximum,error)
    base=next(m for m in new['meshes'] if m['name']=='CSC_Level_1_S_Bldg');points=np.array([[*v['position'],1] for v in base['vertices']]).T
    base_motion=after['Bone']@np.array(newbones['Bone']['inverseWorld']).reshape(4,4).T@points
    base_error=float(np.max(abs(base_motion-points)));assert base_error<.0005,base_error
    assert maximum<.0005,maximum
    write(OUT/'animation-preservation.json',dict(frames=241,duration_seconds=8,maximum_vertex_error=maximum,base_building_motion_error=base_error,clip_sha256=sha(MOD/'Animations'/(TOWER+'_Turn.fgx')),same_animation_binary=True))
    print('All 241 native animation frames preserved; max transformed vertex error',maximum)

def finalize():
    from scipy.spatial import cKDTree
    exe,_=helper(OUT/'cache');checks=[]
    for job in json.loads((OUT/'geometry-jobs.json').read_text()):
        name=job['name'];cn6=OUT/'source-export'/(name+'.cn6');fgx=cn6.with_suffix('.fgx');converter=ROOT/'project/tools/cn6libs/CN6ToFGX.exe'
        r=subprocess.run([str(converter),str(cn6),str(fgx),'2'],cwd=converter.parent,capture_output=True,text=True);assert r.returncode==0,r.stdout+r.stderr
        dest=cn6.with_suffix('.json');subprocess.run([str(exe),str(exe.parent),str(fgx),str(dest)],cwd=exe.parent,capture_output=True,check=True)
        source=json.loads(dest.read_text());native=json.loads((OUT/'native-after'/(name+'.json')).read_text());errors=[]
        assert source['models'][0]['name']==native['models'][0]['name']
        for m in native['meshes']:
            n=next(n for n in source['meshes'] if n['name']==m['name']);assert set(n['boneBindings'])==set(m['boneBindings'])
            pack=lambda mesh:np.array([[v for k in ['position','normal','tangent','binormal','uv','uv2','uv3'] for v in vertex[k]] for vertex in mesh['vertices']])
            a,b=pack(m),pack(n);error=max(cKDTree(a).query(b)[0].max(),cKDTree(b).query(a)[0].max());assert error<.0003,(m['name'],error)
            assert len(a)==len(b) and len(m['triangles'])==len(n['triangles']);errors.append(float(error))
        for b in native['models'][0]['bones']:
            s=next(x for x in source['models'][0]['bones'] if x['name']==b['name']);assert np.max(abs(np.array(s['inverseWorld'])-b['inverseWorld']))<.0003,(b['name'],s,b)
        checks.append(dict(name=name,source_native_error=max(errors),vertices=sum(len(m['vertices']) for m in native['meshes']),bones=len(native['models'][0]['bones'])))
    write(OUT/'saved-source-native-parity.json',checks)
    # Preserve all extra attachments; only the old tower point is absorbed.
    state_checks=[]
    for name in PARENTS:
        before=parse(MOD/'Assets'/(name+'.ast'));after=parse(OUT/'staged/Assets'/(name+'.ast'))
        oldpoints=[p for p in before.findall(POINTS+'/Element') if not any(e.get('text')==TOWER for e in p.findall('.//m_EntryName'))]
        assert [E.tostring(p) for p in oldpoints]==[E.tostring(p) for p in after.findall(POINTS+'/Element')]
        for m in after.findall(MODELS+'/Element'):
            original=next(x for x in before.findall(MODELS+'/Element') if txt(x,'m_Name')==txt(m,'m_Name'))
            previous=original.findall('m_GroupStates/Element');current=m.findall('m_GroupStates/Element')
            assert [E.tostring(g) for g in previous]==[E.tostring(g) for g in current[:len(previous)]]
        state_checks.append(dict(asset=name,other_attachments_unchanged=len(oldpoints),base_states_unchanged=True))
    write(OUT/'assembly-preservation.json',state_checks)
    xlp=parse(MOD/'XLPs/CSC_Tilebases.xlp');entries=xlp.find('m_Entries');removed=[e for e in entries if txt(e,'m_EntryID')==TOWER];assert len(removed)==1
    entries.remove(removed[0]);save(xlp,OUT/'staged/XLPs/CSC_Tilebases.xlp')
    retired=['Assets/'+TOWER+'.ast']+[f'Geometries/{TOWER}{suffix}{ext}' for suffix in ['', '_CON+PIL'] for ext in ['.geo','.fgx']]
    project=MOD/'Civ Supply Chains.civ6proj';data=project.read_bytes();updated=data
    for rel in retired:
        token=rel.replace('/','\\').encode();updated=re.sub(rb'[ \t]*<Content Include="'+re.escape(token)+rb'">.*?</Content>\s*',b'',updated,flags=re.S)
    additions=[]
    for job in json.loads((OUT/'geometry-jobs.json').read_text()):
        for ext in ['.geo','.fgx']:
            rel='Geometries\\'+job['name']+ext
            if rel.encode() not in updated:additions.append('    <Content Include="'+rel+'"><SubType>Content</SubType></Content>\r\n')
    updated=updated.replace(b'</Project>',('  <ItemGroup>\r\n'+''.join(additions)+'  </ItemGroup>\r\n</Project>').encode());E.fromstring(updated)
    (OUT/'staged'/project.name).write_bytes(updated)
    # Only the two chosen parent ASTs may currently consume the retiring wrapper.
    for p in (MOD/'Assets').glob('*.ast'):
        if p.stem in [*PARENTS,TOWER]:continue
        r=parse(p);assert not any(e.get('text')==TOWER for e in r.findall('.//m_EntryName')),p
        assert not any(e.get('text') in [TOWER,TOWER+'_CON+PIL'] for e in r.findall('.//m_GeoName')),p
    import audit_art_orphans as audit
    with contextlib.redirect_stdout(io.StringIO()):audit.run(OUT/'audit-before',False)
    for phase in ['before','after']:
        pantry=OUT/('cook-'+phase)/'pantry'
        for folder in audit.FOLDERS+['XLPs','ArtDefs']:
            for p in (MOD/folder).rglob('*'):
                if not p.is_file():continue
                rel=p.relative_to(MOD)
                if phase=='after' and rel.as_posix() in retired:continue
                dst=pantry/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dst)
        if phase=='after':
            for p in (OUT/'staged').rglob('*'):
                if p.suffix in ['.ast','.geo','.fgx','.xlp']:
                    dst=pantry/p.relative_to(OUT/'staged');dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dst)
    write(OUT/'retire.json',retired);write(OUT/'project-before.json',dict(path=str(project),sha=sha(project)))
    print('Saved sources reproduce native geometry/skeleton; original props and states preserved; cook packages ready.',checks)

def cook():
    import cleanup_art_orphans as c
    c.OUT=OUT;c.cook(sys.argv[2])

def cooked_check():
    b=next((OUT/'cook-after/results').rglob('*.blp')).read_bytes();records={}
    def fnv(s):
        n=2166136261
        for c in s.encode():n=((n^c)*16777619)&0xffffffff
        return n
    for fmt,h,stride in [('RigidModel',0x315cfcd9,24),('SkinnedModel',0x6679b170,32)]:
        start=0
        while True:
            off=b.find(struct.pack('<I',h),start)
            if off<0:break
            start=off+4
            if off<24:continue
            size=struct.unpack_from('<I',b,off-24)[0];ident=struct.unpack_from('<I',b,off-16)[0];count=struct.unpack_from('<I',b,off+4)[0]
            if count and size==count*stride:records.setdefault(ident,[]).append(dict(format=fmt,vertices=count,stride=stride))
    result={}
    for suffix in ['', '_CON+PIL']:
        name=PARENTS[0]+suffix;rows=records.get(fnv(name),[]);assert rows and all(r['format']=='RigidModel' for r in rows),(name,rows)
        result[name]=rows
    write(OUT/'cooked-format-check.json',result)

def publish():
    assert not ARCHIVE.exists();cooked_check()
    for phase in ['before','after']:
        r=json.loads((OUT/('cook-'+phase)/'results/result.json').read_text());assert r['exit_code']==0 and r['blps']
    baseline=json.loads((OUT/'protected.json').read_text())
    for p,h in baseline.items():assert sha(Path(p))==h,('Source changed during preparation',p)
    project=json.loads((OUT/'project-before.json').read_text());assert sha(Path(project['path']))==project['sha']
    retired=json.loads((OUT/'retire.json').read_text());files={p.relative_to(OUT/'staged').as_posix():p for p in (OUT/'staged').rglob('*') if p.suffix in ['.ast','.geo','.fgx','.xlp','.civ6proj']}
    cp=Path(os.environ['APPDATA'])/'AssetCloud/mod-Civ Supply Chains-asset-deps.json';cachebytes=cp.read_bytes();cache=json.loads(cachebytes.decode('utf-8-sig'))
    key=lambda rel:'Civ Supply Chains/'+rel
    olddeps=cache['Dependencies'].get(key('Assets/'+TOWER+'.ast'),[]);oldrecords={e['Filename'].replace('\\','/'):copy.deepcopy(e) for e in cache['Files']}
    dead={key(rel) for rel in retired}
    cache['Files']=[e for e in cache['Files'] if e['Filename'].replace('\\','/') not in dead]
    cache['Dependencies']={k:[p for p in v if p.replace('\\','/') not in dead] for k,v in cache['Dependencies'].items() if k.replace('\\','/') not in dead}
    now=int(time.time()*1e7)+116444736000000000;cache['Timestamp']=now
    for suffix in ['', '_CON+PIL']:
        for ext in ['.geo','.fgx']:
            old=key('Geometries/'+TOWER+suffix+ext);new=key('Geometries/'+PARENTS[0]+suffix+ext)
            e=copy.deepcopy(oldrecords[old]);e.update(Filename=new,Timestamp=now,Filesize=(OUT/'staged/Geometries'/(PARENTS[0]+suffix+ext)).stat().st_size)
            cache['Files'].append(e)
        cache['Dependencies'][key('Geometries/'+PARENTS[0]+suffix+'.geo')]=[key('Geometries/'+PARENTS[0]+suffix+'.fgx')]
    for name in PARENTS:
        assetkey=key('Assets/'+name+'.ast');deps=olddeps+cache['Dependencies'][assetkey];updated=[]
        for dep in deps:
            dep=dep.replace('\\','/')
            if dep==key('Assets/'+TOWER+'.ast'):continue
            for suffix in ['', '_CON+PIL']:
                if dep in [key('Geometries/'+base+suffix+'.geo') for base in ['CSC_Level_1_S',TOWER]]:dep=key('Geometries/'+PARENTS[0]+suffix+'.geo')
            updated.append(dep)
        cache['Dependencies'][assetkey]=sorted(set(updated))
    for e in cache['Files']:
        rel=e['Filename'].replace('\\','/').removeprefix('Civ Supply Chains/')
        if rel in files:e.update(Timestamp=now,Filesize=files[rel].stat().st_size)
    assert all(not any(d.replace('\\','/') in dead for d in ds) for ds in cache['Dependencies'].values())
    ARCHIVE.mkdir(parents=True);backups={}
    for rel in set(retired)|set(files):
        p=MOD/rel
        if p.exists():
            dst=ARCHIVE/'mod-before'/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dst);assert sha(p)==sha(dst);backups[rel]=sha(dst)
    shutil.copy2(cp,ARCHIVE/'AssetCloud-before.json');write(ARCHIVE/'backup-manifest.json',backups)
    for row in json.loads((OUT/'source-build-report.json').read_text()):
        dest=Path(row['destination']);assert not dest.exists(),dest
    assert cp.read_bytes()==cachebytes
    for rel,p in files.items():shutil.copy2(p,MOD/rel)
    for rel in retired:
        p=(MOD/rel).resolve();assert p.is_relative_to(MOD.resolve()) and sha(p)==backups[rel];p.unlink()
    cp.write_text(json.dumps(cache,separators=(',',':')),encoding='utf-8')
    for row in json.loads((OUT/'source-build-report.json').read_text()):
        src=Path(row['source']);dst=Path(row['destination']);shutil.copy2(src,dst)
        for p in (src.parent/'textures').glob('*.png'):
            target=dst.parent/'textures'/p.name;target.parent.mkdir(exist_ok=True)
            if target.exists():assert sha(target)==sha(p)
            else:shutil.copy2(p,target)
        export=dst.parent/'exports'/row['name'];export.mkdir(parents=True,exist_ok=True)
        for ext in ['.cn6','.geo','.fgx']:shutil.copy2(OUT/'staged/Geometries'/(row['name']+ext),export/(row['name']+ext))
    # Keep an editable motion reference beside the master and the native clip unchanged.
    anim=DEST/'animation';anim.mkdir(exist_ok=True)
    for ext in ['.anm','.fgx']:shutil.copy2(MOD/'Animations'/(TOWER+'_Turn'+ext),anim/(TOWER+'_Turn'+ext))
    shutil.copy2(OUT/'motion-after/clip.na2',anim/'combined-model-turn.na2')
    write(OUT/'install-report.json',dict(archive=str(ARCHIVE),updated=list(files),retired=retired,masters=json.loads((OUT/'source-build-report.json').read_text())))
    print('Installed shared combined models, both parent ASTs and registry updates; standalone tower and old geometries archived.')

def verify():
    import audit_art_orphans as audit
    report=json.loads((OUT/'install-report.json').read_text());baseline=json.loads((OUT/'protected.json').read_text());changed={str(MOD/p) for p in report['updated']+report['retired']};count=0
    for p,h in baseline.items():
        if p not in changed:assert sha(Path(p))==h,p;count+=1
    for rel in report['updated']:assert sha(MOD/rel)==sha(OUT/'staged'/rel),rel
    for rel in report['retired']:assert not (MOD/rel).exists() and (ARCHIVE/'mod-before'/rel).exists()
    for row in report['masters']:assert sha(Path(row['source']))==sha(Path(row['destination']))
    assert json.loads((OUT/'installed-source-validation.json').read_text())
    for name in PARENTS:
        ast=parse(MOD/'Assets'/(name+'.ast'));assert {txt(m,'m_GeoName') for m in ast.findall(MODELS+'/Element')}=={PARENTS[0],PARENTS[0]+'_CON+PIL'}
        assert not any(e.get('text')==TOWER for e in ast.findall('.//m_EntryName'))
        assert [txt(b,'m_AnimationName') for b in ast.findall(BINDINGS+'/Element') if txt(b,'m_SlotName')=='WORKED_A']==[TOWER+'_Turn']
    with contextlib.redirect_stdout(io.StringIO()):audit.run(OUT/'audit-after',False)
    before=json.loads((OUT/'audit-before/audit.json').read_text());after=json.loads((OUT/'audit-after/audit.json').read_text());assert not after['errors'] and before['unresolved']==after['unresolved']
    statuses={r['path']:r['status'] for r in after['rows']}
    for suffix in ['', '_CON+PIL']:
        for ext in ['.fgx','.geo']:assert statuses['Geometries/'+PARENTS[0]+suffix+ext]=='runtime'
    assert statuses['Animations/'+TOWER+'_Turn.anm']=='runtime'
    xlp=lambda p:len(parse(p).findall('m_Entries/Element'))
    result=dict(shared_regular_layout=json.loads((OUT/'standardization.json').read_text()),animation=json.loads((OUT/'animation-preservation.json').read_text()),
        authoring_motion=json.loads((OUT/'authoring-motion.json').read_text()),native_source=json.loads((OUT/'saved-source-native-parity.json').read_text()),
        unaffected_runtime_files=count,retired=report['retired'],xlp_entries_before=xlp(ARCHIVE/'mod-before/XLPs/CSC_Tilebases.xlp'),xlp_entries_after=xlp(MOD/'XLPs/CSC_Tilebases.xlp'),
        cooked_formats=json.loads((OUT/'cooked-format-check.json').read_text()),original_animation_files_unchanged=True,game_review=False,unresolved=after['unresolved'])
    write(OUT/'final-verification.json',result);write(ARCHIVE/'completed.json',result)
    for f in ['standardization.json','assembly-preservation.json','animation-preservation.json','authoring-motion.json','saved-source-native-parity.json','installed-source-validation.json','install-report.json']:
        shutil.copy2(OUT/f,ARCHIVE/f)
    for phase in ['before','after']:
        dst=ARCHIVE/'cook-evidence'/phase;dst.mkdir(parents=True)
        for f in ['command.json','result.json','stdout.log']:shutil.copy2(OUT/('cook-'+phase)/'results'/f,dst/f)
    note='''Wind Mill tower bundled — 26 October 2026

Both CSC_BAKERS_Wind_Mill and _2 use the shared dedicated CSC_BAKERS_Wind_Mill
and CSC_BAKERS_Wind_Mill_CON+PIL geometry. The regular AST's latest saved tower
placement is baked into both. Other attachments and base/tower state settings
are preserved. Original component masters under tower/ remain untouched.

CSC_BAKERS_Wind_Mill_Tower.ast and its two standalone GEO/FGX pairs were archived;
its XLP entry and obsolete project registration were removed. The original Turn
ANM/FGX is still required and unchanged. The internal native model identity stays
CSC_BAKERS_Wind_Mill_Tower to match that clip's track group; this is not a separate
runtime asset. Preserve Root/Sails, Windmill_Tower_Mount and the static
Windmill_Sail_Pivot_Offset bone when editing/exporting. The latter accounts for
the uniform scale while allowing the original animation tracks to remain intact.

New editable masters in Working Files/3D Art/BAKERS/Wind Mill have portable
textures, exports and an animation reference folder. Keep these native model
names when exporting. Both source meshes and skeletons round-trip to FGX; all
241 frames were checked against the original motion. Construction/pillage and
full assembly previews were reviewed. Both native cooks passed with 24-byte
RigidModel records, as required by the existing materials. No live AE/game test.

Restoration: check for later edits before restoring selected originals from
mod-before or AssetCloud-before.json. Never blindly overwrite later AE edits.
'''
    (ARCHIVE/'README.txt').write_text(note,encoding='utf-8');(DEST/'Combined-model-notes.txt').write_text(note,encoding='utf-8')
    print(json.dumps(result,indent=2))

if __name__=='__main__':globals()[sys.argv[1]]()
