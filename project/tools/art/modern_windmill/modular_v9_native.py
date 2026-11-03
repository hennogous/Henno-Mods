"""Selective native integration for the modular modern mill, preserving unrelated AE work."""
import sys,json,copy,shutil,subprocess,math,hashlib,os,time
from pathlib import Path
import xml.etree.ElementTree as E
from PIL import Image
from modular_v9 import ROOT,ART,SOURCE,OLD,BASE,SILO,TROLLEY,PALLET,BMAT,PMAT,BTEX,PTEX,texname,sha,dump
MOD=ROOT/'Civ Supply Chains'
sys.path[:0]=[str(ROOT/'project/tools/blender/scene_export'),str(ROOT/'project/tools/blender')]
import export_scene as exp
from render_ae_asset import Resolver,Assembly,DEFAULT_SDK,helper

def read(p):return E.parse(p).getroot()
def save(p,r):exp.write_xml(p,r)
def text(r,p,s):r.find(p).set('text',s)
def semantic(r):return (r.tag,dict(r.attrib),(r.text or '').strip(),[semantic(c) for c in r])

def fresh_asset(ident,model,template):
    r=copy.deepcopy(template);text(r,'m_Name',ident);text(r,'m_Description',ident.replace('_',' '))
    b=r.find('m_BehaviorData');text(b,'m_dsgName','Standard_Landmark')
    for path in ('m_referenceGeometryNames','m_behaviorDataSets/m_animationBindings/m_Bindings','m_behaviorDataSets/m_timelineBindings/m_Bindings','m_behaviorDataSets/m_timelines/m_Timelines','m_behaviorDataSets/m_attachmentPoints/m_Points'):
        n=b.find(path)
        if n is not None:n.clear()
    E.SubElement(b.find('m_referenceGeometryNames'),'Element',{'text':ident})
    ms=r.find(exp.MODELS);ms.clear()
    ms.append(exp.model_instance(model,{m['name']:m['name'] for mesh in model['meshes'] for m in mesh['materials']},('Worked','Unworked')))
    for row in r.findall('m_CookParams/m_Values/Element'):
        if exp.txt(row,'m_ParamName')=='CullingMode':row.find('m_Value').set('text','PERMANENT')
    return r

def stage(out):
    dst=out/'staged'
    for f in ('Assets','Geometries','Materials','Textures','CN6','XLPs'):(dst/f).mkdir(parents=True,exist_ok=True)
    # Frozen existing assembly/dependencies, with concurrent edit protection at publication.
    baseline={p.relative_to(MOD).as_posix():sha(p) for d in ('Assets','ArtDefs','XLPs') for p in (MOD/d).glob('*') if p.is_file()}
    baseline['Civ Supply Chains.civ6proj']=sha(MOD/'Civ Supply Chains.civ6proj')
    dump(out/'baseline.json',baseline)
    for folder in ('Assets','Geometries','Materials','Textures'):
        for p in (MOD/folder).glob(OLD+'*'):
            if p.is_file():shutil.copy2(p,dst/folder/p.name)
    exe,_=helper(out/'native-reader');converter=ROOT/'project/tools/cn6libs/CN6ToFGX.exe';native=[];models={}
    for ident in (BASE,SILO,TROLLEY,PALLET):
        m=json.loads((out/'models'/(ident+'.json')).read_text());models[ident]=m
        for mesh in m['meshes']:
            for mat in mesh['materials']:
                for info in mat['images'].values():info['sha256']=sha(info['path'])
        dump(out/'models'/(ident+'.json'),m)
        cn6=dst/'CN6'/(ident+'.cn6');fgx=dst/'Geometries'/(ident+'.fgx')
        exp.write_cn6(cn6,m);save(dst/'Geometries'/(ident+'.geo'),exp.geometry(m,read(MOD/'Geometries/CSC_Level_1_S.geo')))
        r=subprocess.run([str(converter),str(cn6),str(fgx),'2'],cwd=converter.parent,capture_output=True,text=True)
        (out/(ident+'-conversion.log')).write_text(r.stdout+r.stderr);assert r.returncode==0,r.stdout+r.stderr
        npath=out/(ident+'-native.json');subprocess.run([str(exe),str(exe.parent),str(fgx),str(npath)],cwd=exe.parent,check=True,capture_output=True)
        n=json.loads(npath.read_text());assert len(n['meshes'])==len(m['meshes']);err=0
        for a,b in zip(m['meshes'],n['meshes']):
            assert a['name']==b['name'] and a['triangles']==b['triangles'];assert b['boneBindings']==['Bone']
            assert len(a['vertices'])==len(b['vertices'])
            for v,w in zip(a['vertices'],b['vertices']):
                values=w['position']+w['normal']+w['tangent']+w['binormal']+w['uv']+w['uv2']+w['uv3']
                err=max(err,max(abs(x-y) for x,y in zip(v,values)));assert err<1e-4
                assert w['boneWeights']==[255,0,0,0,0,0,0,0] and w['boneIndices']==[0]*8
        native.append({'asset':ident,'vertices':sum(len(x['vertices']) for x in n['meshes']),'triangles':sum(len(x['triangles']) for x in n['meshes']),'maximum_component_error':err,'bone_bindings_uvs_topology_pass':True})
    for ident,kind in ((BMAT,'building'),(PMAT,'props')):
        r=read(MOD/'Materials'/(OLD+'.mtl'));text(r,'m_Name',ident)
        mapping={exp.SLOTS[ch]:texname(kind,ch) for ch in ('B','N','G','M','E','AO')}
        for row in r.findall('m_CookParams/m_Values/Element'):
            param=exp.txt(row,'m_ParamName')
            if param in mapping:row.find('m_ObjectName').set('text',mapping[param])
        save(dst/'Materials'/(ident+'.mtl'),r)
    for kind in ('building','props'):
        for ch in ('B','N','G','M','E','AO'):
            p=out/'textures'/(texname(kind,ch)+'.png');size=Image.open(p).size;src=p;fmt='R8_UNORM' if ch in ('AO','G','M') else 'R8G8B8A8_UNORM'
            if ch in ('AO','G','M'):
                src=out/'scalar'/p.name;src.parent.mkdir(exist_ok=True);Image.open(p).convert('RGB').getchannel('R').save(src)
            cmd=[str(ROOT/'project/tools/directxtex/texconv.exe'),'-nologo','-y','-m','0','-f',fmt,'--ignore-srgb','-o',str(dst/'Textures')]
            if ch in ('B','E'):cmd+=['-srgb']
            r=subprocess.run(cmd+[str(src)],capture_output=True,text=True);assert r.returncode==0,r.stdout+r.stderr
            spec={'slot':ch,'size':list(size),'format':fmt};dds=dst/'Textures'/(p.stem+'.dds')
            if ch in ('AO','G','M'):exp.normalize_ao_dds(dds,spec,MOD/'Textures/CSC_Props_Shared_01_AO.dds')
            exp.validate_dds(dds,spec)
            r=read(MOD/'Textures'/f'{OLD}_{ch}.tex');text(r,'m_Name',p.stem);text(r,'m_SourceFilePath',str(p));text(r,'m_DataFiles/Element/m_RelativePath',p.stem+'.dds')
            r.find('m_Width').text=str(size[0]);r.find('m_Height').text=str(size[1]);r.find('m_NumMipMaps').text=str(int(math.log2(max(size))))
            save(dst/'Textures'/(p.stem+'.tex'),r)
    template=read(MOD/'Assets'/(OLD+'.ast'))
    for ident,m in models.items():save(dst/'Assets'/(ident+'.ast'),fresh_asset(ident,m,template))
    # Base-only reusable asset uses the existing shared Level 1 shell/scaffolding.
    # Mill retains its existing state geometry and state material verbatim.
    base=read(dst/'Assets'/(BASE+'.ast'))
    state=exp.shared_model_from_geo(MOD,'CSC_Level_1_S_CON+PIL',lambda g:'Pillage_Construction_01' if g=='Pillage_Construction_01' else 'CSC_BAKERS_E', lambda g:('Construction',) if g=='Pillage_Construction_01' else ('Construction','Pillaged'))
    base.find(exp.MODELS).append(state)
    E.SubElement(base.find('m_BehaviorData/m_referenceGeometryNames'),'Element',{'text':'CSC_Level_1_S_CON+PIL'})
    save(dst/'Assets'/(BASE+'.ast'),base)
    mill=copy.deepcopy(template);instances=mill.find(exp.MODELS)
    original=next(x for x in instances if exp.txt(x,'m_Name')==OLD);instances.remove(original)
    for ident in (BASE,SILO):
        m=models[ident];visible={x['name']:() if x['name'].endswith('_SiloSideSupports') else ('Worked','Unworked') for x in m['meshes']}
        instances.append(exp.model_instance(m,{mat['name']:mat['name'] for x in m['meshes'] for mat in x['materials']},visible))
    refs=mill.find('m_BehaviorData/m_referenceGeometryNames')
    for node in list(refs):
        if node.get('text')==OLD:refs.remove(node)
    for ident in (BASE,SILO):E.SubElement(refs,'Element',{'text':ident})
    points=mill.find('m_BehaviorData/m_behaviorDataSets/m_attachmentPoints/m_Points')
    for a in json.loads((out/'masters.json').read_text()):
        if a['asset_id'] not in (TROLLEY,PALLET):continue
        row,issues=exp.attachment(a,exp.csc_binding(a['asset_id'],MOD/'XLPs/CSC_Tilebases.xlp'),BASE,{});assert not issues,issues
        for v in row.findall('m_CookParams/m_Values/Element'):
            if exp.txt(v,'m_ParamName')=='Cull Mode':v.find('m_Value').set('text','PERMANENT')
        # Bind to the actual static Bone, not the skeleton root name.
        text(row,'m_BoneName','Bone');points.append(row)
    save(dst/'Assets'/(OLD+'.ast'),mill)
    assert semantic(next(x for x in mill.find(exp.MODELS) if exp.txt(x,'m_Name')==OLD+'_CON+PIL'))==semantic(next(x for x in template.find(exp.MODELS) if exp.txt(x,'m_Name')==OLD+'_CON+PIL'))
    # Copy the local dependency closure only; SDK resources remain native pantry dependencies.
    resolver=Resolver(MOD,DEFAULT_SDK)
    for p in dst.rglob('*'):
        if p.is_file():resolver.index[p.name.casefold()]={p}
    visited=set()
    def deps(p):
        if p in visited:return
        visited.add(p)
        if p.suffix not in ('.ast','.mtl','.geo','.tex'):return
        r=read(p);todo=[]
        for n in r.findall('.//m_GeoName'):todo.append(resolver.resolve(n.get('text'),'.geo',p))
        for row in r.findall('.//Element'):
            name=exp.txt(row,'m_ObjectName');kind=exp.txt(row,'m_eObjectType')
            if name and kind in ('MATERIAL','TEXTURE'):todo.append(resolver.resolve(name,'.mtl' if kind=='MATERIAL' else '.tex',p))
            if exp.txt(row,'m_ParamName')=='Asset' and exp.txt(row,'m_EntryName'):todo.append(resolver.resolve(exp.txt(row,'m_EntryName'),'.ast',p))
        for n in r.findall('.//m_DataFiles/Element/m_RelativePath'):todo.append(p.parent/n.get('text'))
        for q in todo:
            if q.is_relative_to(MOD):
                target=dst/q.relative_to(MOD);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(q,target)
            deps(q)
    for ident in (*models,OLD):deps(dst/'Assets'/(ident+'.ast'))
    for p in dst.rglob('*'):
        if p.is_file():resolver.index[p.name.casefold()]={p}
    checks=[]
    for state in ('Worked','Unworked','Construction','Pillaged','Unbuilt'):
        a=Assembly(resolver,state);key=a.asset(dst/'Assets'/(OLD+'.ast'));record=a.assets[key]
        counts={m['name'] if 'name' in m else str(i):len(m['groups']) for i,m in enumerate(record['models'])}
        child_groups=sum(len(m['groups']) for k,v in a.assets.items() if k!=key for m in v['models'])
        assert child_groups==(2 if state in ('Worked','Unworked') else 0),(state,child_groups)
        checks.append({'state':state,'main_groups':counts,'prop_groups':child_groups})
    newfiles=[]
    for folder in ('Assets','Geometries','Materials','Textures'):
        for p in (dst/folder).iterdir():
            target=MOD/folder/p.name
            if not target.exists() or sha(p)!=sha(target):
                assert not target.exists() or target==MOD/'Assets'/(OLD+'.ast'),('Unexpected existing dependency change',target)
                newfiles.append(p.relative_to(dst).as_posix())
    dump(out/'staging-validation.json',{'passed':True,'native':native,'states':checks,'publish_files':newfiles,'preserved_existing_state':True,'source_hash':sha(SOURCE)})
    print('STAGED',len(newfiles),'files',flush=True)

def publish(out):
    checks=json.loads((out/'staging-validation.json').read_text());assert checks['passed']
    for ident in (BASE,SILO,TROLLEY,PALLET):
        assert json.loads((out/'masters'/ident/'validation.json').read_text())['automated_pass'],ident
    cook=json.loads((out/'cook-check/result.json').read_text());assert cook['exit_code']==0 and cook['blps']
    assert sha(SOURCE)==checks['source_hash']
    baseline=json.loads((out/'baseline.json').read_text());assert all((MOD/k).exists() and sha(MOD/k)==v for k,v in baseline.items()),'Concurrent AE/project edit'
    payload={};destinations={BASE:ART/'Level 1/modern/revision-01-modular',SILO:ART/'BAKERS/Wind Mill/modern/revision-09-modular',TROLLEY:ART/'BAKERS/Props/Modern/revision-01',PALLET:ART/'BAKERS/Props/Modern/revision-01'}
    release='2026-10-27_Modern_r001';libraries={kind:ART/'Textures'/('CSC_Buildings_Modern' if kind=='building' else 'CSC_Props_Modern') for kind in ('building','props')}
    for lib in libraries.values():assert not lib.exists(),('Library already exists',lib)
    for ident,dest in destinations.items():
        folder=out/'masters'/ident
        assert not (dest/(ident+'.blend')).exists()
        for p in folder.rglob('*'):
            if p.is_file() and p.suffix!='.blend1':payload[dest/p.relative_to(folder)]=p.read_bytes()
        payload[dest/(ident+'.cn6')]=(out/'staged/CN6'/(ident+'.cn6')).read_bytes()
    for kind,lib in libraries.items():
        maps={}
        for ch in ('B','N','G','M','E','AO'):
            name=texname(kind,ch)+'.png';data=(out/'textures'/name).read_bytes();maps[name]=hashlib.sha256(data).hexdigest()
            for where in ('Current',f'Releases/{release}'):payload[lib/where/'textures'/name]=data
        manifest={'library':lib.name,'release':release,'layout':'building_2x2_stage_quadrants' if kind=='building' else 'historical_shared_8x8_surface_2x2_quarter_AO','source':str(SOURCE),'source_sha256':sha(SOURCE),'maps':maps,'allocation_manifest':'atlas-plan.json','rebuild_tool':'scripts/rebuild_modern_atlases.py','status':'approved V8 artwork repacked; modular V9 native conversion and isolated cook verified'}
        for where in ('Current',f'Releases/{release}'):
            payload[lib/where/'library.json']=json.dumps(manifest,indent=2).encode()
            payload[lib/where/'atlas-plan.json']=(out/'atlas-plan.json').read_bytes()
            for ch in ('B','N','G','M'):payload[lib/where/'sources'/f'{OLD}_{ch}.png']=(SOURCE.parent/'textures'/f'{OLD}_{ch}.png').read_bytes()
            payload[lib/where/'scripts/rebuild_modern_atlases.py']=Path(__file__).with_name('rebuild_modern_atlases.py').read_bytes()
            for ident,(page,_) in __import__('modular_v9').AO.items():
                if page==kind:payload[lib/where/'bakes'/(ident+'.png')]=(out/'bakes'/(ident+'.png')).read_bytes()
        payload[lib/'CURRENT.json']=json.dumps({'release':release,'current':'Current','snapshot':f'Releases/{release}','manifest':'Current/library.json'},indent=2).encode()
    for rel in checks['publish_files']:
        p=out/'staged'/rel;data=p.read_bytes()
        if p.suffix=='.tex':
            r=E.fromstring(data);kind='props' if p.stem.startswith(PTEX) else 'building';text(r,'m_SourceFilePath',str(libraries[kind]/'Current/textures'/(p.stem+'.png')));data=E.tostring(r,encoding='utf-8',xml_declaration=True)
        payload[MOD/rel]=data
    xlp=MOD/'XLPs/CSC_Tilebases.xlp';raw=xlp.read_bytes();newids=[BASE,SILO,TROLLEY,PALLET]
    assert all(i.encode() not in raw for i in newids)
    insert=''.join(f'\n    <Element><m_EntryID text="{i}"/><m_ObjectName text="{i}"/></Element>' for i in newids)
    payload[xlp]=raw.replace(b'</m_Entries>',insert.encode()+b'\n  </m_Entries>');E.fromstring(payload[xlp])
    project=MOD/'Civ Supply Chains.civ6proj';raw=project.read_bytes();newpaths=[p for p in payload if p.is_relative_to(MOD) and not p.exists()]
    xml='\n  <ItemGroup>\n'+''.join('    <Content Include="'+str(p.relative_to(MOD))+'"><SubType>Content</SubType></Content>\n' for p in newpaths)+'  </ItemGroup>\n'
    payload[project]=raw.replace(b'</Project>',xml.encode()+b'</Project>');E.fromstring(payload[project])
    rows=[];backup=out/'publication-backup';backup.mkdir(exist_ok=True)
    for i,(p,data) in enumerate(payload.items()):
        row={'destination':str(p),'before':sha(p) if p.exists() else None,'after':hashlib.sha256(data).hexdigest()}
        if p.exists():q=backup/f'{i:04}-{p.name}';shutil.copy2(p,q);row['backup']=str(q)
        rows.append(row)
    dump(backup/'manifest.json',rows)
    for row,(p,data) in zip(rows,payload.items()):
        assert (sha(p) if p.exists() else None)==row['before'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);assert sha(p)==row['after']
    changed={p.relative_to(MOD).as_posix() for p in payload if p.is_relative_to(MOD)}
    assert all(sha(MOD/k)==v for k,v in baseline.items() if k not in changed)
    dump(out/'publication-report.json',{'installed':True,'files':rows,'masters':{k:str(v/(k+'.blend')) for k,v in destinations.items()},'libraries':{k:str(v) for k,v in libraries.items()},'old_source_unchanged':sha(SOURCE)==checks['source_hash'],'ArtDefs_unchanged':True,'historical_assets_unchanged':True,'in_game_tested':False})
    print('PUBLISHED',len(rows),'files',flush=True)

def cache(out):
    report=json.loads((out/'publication-report.json').read_text());assert report['installed']
    p=Path(os.environ['APPDATA'])/'AssetCloud/mod-Civ Supply Chains-asset-deps.json';raw=p.read_bytes();data=json.loads(raw.decode('utf-8-sig'))
    records={r['Filename'].replace('\\','/'):r for r in data['Files']};index={(Path(k).suffix.lower(),Path(k).stem.casefold()):k for k in records}
    for folder in ('Assets','Geometries','Materials','Textures'):
        for f in (MOD/folder).iterdir():
            if f.is_file():index[(f.suffix.lower(),f.stem.casefold())]=f.relative_to(ROOT).as_posix()
    types={'.ast':0,'.mtl':1,'.geo':2,'.tex':3};changed=[]
    for row in report['files']+[{'destination':p} for p in report.get('cache_inputs',[])]:
        f=Path(row['destination']);ext=f.suffix
        if not f.is_relative_to(MOD) or ext not in ('.ast','.mtl','.geo','.tex','.fgx','.dds'):continue
        k=f.relative_to(ROOT).as_posix();r=records.get(k)
        if r is None:
            r={'Filename':k,'Status':0,'Type':2 if ext in types else 3 if ext=='.dds' else 4,'EntityType':types.get(ext,12),'EntityClass':'','Tags':[],'Stats':{}};data['Files'].append(r)
        r.update(Timestamp=int(f.stat().st_mtime*10000000)+116444736000000000,Filesize=f.stat().st_size)
        if ext in types:
            xml=read(f);r['EntityClass']=exp.txt(xml,'m_ClassName');deps=set()
            for n in xml.findall('.//m_GeoName'):deps.add(index[('.geo',n.get('text').casefold())])
            for n in xml.findall('.//Element'):
                name=exp.txt(n,'m_ObjectName');kind=n.findtext('m_eObjectType','')
                if name and kind in ('MATERIAL','TEXTURE'):deps.add(index[('.mtl' if kind=='MATERIAL' else '.tex',name.replace('\\','/').split('/')[-1].casefold())])
                if exp.txt(n,'m_ParamName')=='Asset' and exp.txt(n,'m_EntryName'):deps.add(index[('.ast',exp.txt(n,'m_EntryName').casefold())])
            for n in xml.findall('.//m_DataFiles/Element/m_RelativePath'):deps.add((f.parent/n.get('text')).relative_to(ROOT).as_posix())
            data['Dependencies'][k]=sorted(deps)
        changed.append(k)
    assert p.read_bytes()==raw;(out/'assetcloud-before.json').write_bytes(raw);data['Timestamp']=int(time.time()*10000000)+116444736000000000
    tmp=p.with_name(p.name+'.modern-v9-tmp');tmp.write_text(json.dumps(data,separators=(',',':')),encoding='utf-8');os.replace(tmp,p)
    dump(out/'assetcloud-registration.json',{'updated':changed});print('CACHE_UPDATED',len(changed))

if __name__=='__main__':globals()[sys.argv[1]](Path(sys.argv[2]))
