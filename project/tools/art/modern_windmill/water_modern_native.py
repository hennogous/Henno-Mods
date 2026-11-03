"""Selective native integration for the finished shelter and modern Water Mill."""
import sys,json,copy,shutil,subprocess,math
from pathlib import Path
import xml.etree.ElementTree as E
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parent))
from water_modern import ROOT,ART,BASE,SILO,WATER,DESTS,LIBS,RELEASES,sha,dump
import modular_v9_native as native
exp=native.exp;MOD=native.MOD;OLD='CSC_BAKERS_Water_Mill';WIND='CSC_BAKERS_Wind_Mill_Modern'

def stage(out):
    dst=out/'staged'
    for d in ('Assets','Geometries','Materials','Textures','XLPs','CN6','ArtDefs'):(dst/d).mkdir(parents=True,exist_ok=True)
    converter=ROOT/'project/tools/cn6libs/CN6ToFGX.exe';exe,_=native.helper(out/'native-reader');checks=[];models={}
    for ident in (BASE,WATER):
        model=json.loads((out/'models'/(ident+'.json')).read_text());models[ident]=model
        for mesh in model['meshes']:
            for mat in mesh['materials']:
                for im in mat['images'].values():im['sha256']=sha(im['path'])
        dump(out/'models'/(ident+'.json'),model)
        cn6=dst/'CN6'/(ident+'.cn6');fgx=dst/'Geometries'/(ident+'.fgx')
        exp.write_cn6(cn6,model);native.save(dst/'Geometries'/(ident+'.geo'),exp.geometry(model,native.read(MOD/'Geometries'/(BASE+'.geo'))))
        r=subprocess.run([str(converter),str(cn6),str(fgx),'2'],cwd=converter.parent,capture_output=True,text=True);(out/(ident+'-conversion.log')).write_text(r.stdout+r.stderr);assert r.returncode==0
        npath=out/(ident+'-native.json');subprocess.run([str(exe),str(exe.parent),str(fgx),str(npath)],cwd=exe.parent,check=True,capture_output=True)
        decoded=json.loads(npath.read_text());assert len(decoded['meshes'])==len(model['meshes']);err=0
        for a,b in zip(model['meshes'],decoded['meshes']):
            assert a['name']==b['name'] and a['triangles']==b['triangles'] and b['boneBindings']==['Bone'] and len(a['vertices'])==len(b['vertices'])
            for v,w in zip(a['vertices'],b['vertices']):
                values=w['position']+w['normal']+w['tangent']+w['binormal']+w['uv']+w['uv2']+w['uv3']
                err=max(err,max(abs(x-y) for x,y in zip(v,values)));assert err<1e-4
                assert w['boneWeights']==[255,0,0,0,0,0,0,0] and w['boneIndices']==[0]*8
        checks.append({'asset':ident,'native_max_error':err,'vertices':sum(len(m['vertices']) for m in model['meshes']),'triangles':sum(len(m['triangles']) for m in model['meshes'])})
    # Shared base groups retain exact identities and all current assembly settings.
    shutil.copy2(MOD/'Assets'/(BASE+'.ast'),dst/'Assets'/(BASE+'.ast'))
    shutil.copy2(MOD/'Assets'/(WIND+'.ast'),dst/'Assets'/(WIND+'.ast'))
    water=native.read(MOD/'Assets'/(OLD+'.ast'));native.text(water,'m_Name',WATER);native.text(water,'m_Description','Modern riverside flour mill')
    ms=water.find(exp.MODELS);oldmain=next(m for m in ms if exp.txt(m,'m_Name')==OLD);index=list(ms).index(oldmain);ms.remove(oldmain)
    mapping={mat['name']:mat['name'] for mesh in models[WATER]['meshes'] for mat in mesh['materials']}
    ms.insert(index,exp.model_instance(models[WATER],mapping,('Worked','Unworked')))
    b=water.find('m_BehaviorData');native.text(b,'m_dsgName','Standard_Landmark')
    refs=b.find('m_referenceGeometryNames')
    for n in refs:
        if n.get('text')==OLD:n.set('text',WATER)
    pts=b.find('m_behaviorDataSets/m_attachmentPoints/m_Points')
    for p in list(pts):
        owner=exp.txt(p,'m_ModelInstanceName')
        binding=next((v for v in p.findall('m_CookParams/m_Values/Element') if exp.txt(v,'m_ParamName')=='Asset'),None)
        if binding is not None and exp.txt(binding,'m_EntryName')==OLD+'_Wheel':pts.remove(p);continue
        if owner==OLD:native.text(p,'m_ModelInstanceName',WATER);native.text(p,'m_BoneName','Bone')
    for placement in json.loads((out/'placements.json').read_text()):
        row,issues=exp.attachment(placement,exp.csc_binding(placement['asset_id'],MOD/'XLPs/CSC_Tilebases.xlp'),WATER,{})
        assert not issues,issues;native.text(row,'m_BoneName','Bone')
        for v in row.findall('m_CookParams/m_Values/Element'):
            if exp.txt(v,'m_ParamName')=='Cull Mode':v.find('m_Value').set('text','PERMANENT')
        pts.append(row)
    # Firaxis already uses this wake for its water mill. Reuse its FX trigger/schema.
    pantry=native.DEFAULT_SDK/'Civ6/pantry'
    aww=native.read(pantry/'Assets/DIS_CTY_AWW.ast')
    dataset=b.find('m_behaviorDataSets')
    for path in ('m_animationBindings/m_Bindings','m_timelineBindings/m_Bindings','m_timelines/m_Timelines'):dataset.find(path).clear()
    row=E.SubElement(dataset.find('m_timelineBindings/m_Bindings'),'Element')
    E.SubElement(row,'m_SlotName',{'text':'WORKED_A'});E.SubElement(row,'m_TimelineName',{'text':'WORKED_A'})
    timeline=copy.deepcopy(next(t for t in aww.findall('.//m_Timelines/Element') if exp.txt(t,'m_Name')=='WORKED_FLOW_LEFT_A'))
    native.text(timeline,'m_Name','WORKED_A');native.text(timeline,'m_AnimationName','');timeline.find('m_fDuration').text='4.000000'
    for trig in list(timeline.find('m_Triggers')):
        if exp.txt(trig,'m_FXName')!='FX_Rock2_Wake':timeline.find('m_Triggers').remove(trig)
        else:native.text(trig,'m_AttachmentPointName','FX_Turbine_Outlet')
    dataset.find('m_timelines/m_Timelines').append(timeline)
    anchor=copy.deepcopy(next(p for p in aww.findall('.//m_Points/Element') if exp.txt(p,'m_Name')=='FX_Water_Turb_01'))
    native.text(anchor,'m_Name','FX_Turbine_Outlet');native.text(anchor,'m_BoneName','Bone');native.text(anchor,'m_ModelInstanceName',WATER)
    for axis,value in zip('xyz',(3.9,2.05,-2.3)):anchor.find('m_position/'+axis).text=str(value)
    for axis in 'xyz':anchor.find('m_orientation/'+axis).text='0.000000'
    anchor.find('m_scale').text='0.650000';pts.append(anchor)
    native.save(dst/'Assets'/(WATER+'.ast'),water)
    # Two AO sheets only. Their surface channels and permanent identities do not change.
    for kind in ('building','props'):
        name='CSC_Atlas_Modern_AO' if kind=='building' else 'CSC_Props_Modern_01_AO'
        p=out/'libraries'/kind/'textures'/(name+'.png');scalar=out/'scalar';scalar.mkdir(exist_ok=True)
        Image.open(p).convert('RGB').getchannel('R').save(scalar/p.name)
        subprocess.run([str(ROOT/'project/tools/directxtex/texconv.exe'),'-nologo','-y','-m','0','-f','R8_UNORM','--ignore-srgb','-o',str(dst/'Textures'),str(scalar/p.name)],capture_output=True,check=True)
        size=list(Image.open(p).size);spec={'slot':'AO','size':size,'format':'R8_UNORM'};dds=dst/'Textures'/(name+'.dds')
        exp.normalize_ao_dds(dds,spec,MOD/'Textures/CSC_Props_Shared_01_AO.dds');exp.validate_dds(dds,spec)
        r=native.read(MOD/'Textures'/(name+'.tex'));r.find('m_Width').text=str(size[0]);r.find('m_Height').text=str(size[1]);r.find('m_NumMipMaps').text=str(int(math.log2(size[0])));native.text(r,'m_SourceFilePath',str(LIBS[kind]/'Current/textures'/p.name));native.save(dst/'Textures'/(name+'.tex'),r)
    # Explicit recursive dependency closure includes invisible states and decals.
    resolver=native.Resolver(MOD,native.DEFAULT_SDK)
    for p in dst.rglob('*'):
        if p.is_file():resolver.index[p.name.casefold()]={p}
    seen=set()
    def deps(p):
        if p in seen:return
        seen.add(p)
        if p.suffix not in ('.ast','.geo','.mtl','.tex'):return
        from render_ae_asset import read_xml
        r=read_xml(p);todo=[]
        for n in r.findall('.//m_GeoName'):todo.append(resolver.resolve(n.get('text'),'.geo',p))
        for n in r.findall('.//Element'):
            name=exp.txt(n,'m_ObjectName');kind=n.findtext('m_eObjectType','')
            if name and kind in ('MATERIAL','TEXTURE'):todo.append(resolver.resolve(name,'.mtl' if kind=='MATERIAL' else '.tex',p))
            if exp.txt(n,'m_ParamName')=='Asset' and exp.txt(n,'m_EntryName'):todo.append(resolver.resolve(exp.txt(n,'m_EntryName'),'.ast',p))
        for n in r.findall('.//m_DataFiles/Element/m_RelativePath'):todo.append(p.parent/n.get('text'))
        for q in todo:
            if q.is_relative_to(MOD):
                dest=dst/q.relative_to(MOD)
                if not dest.exists():dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(q,dest)
            deps(q)
    for ident in (BASE,WATER,WIND):deps(dst/'Assets'/(ident+'.ast'))
    shutil.copy2(MOD/'XLPs/CSC_Tilebases.xlp',dst/'XLPs/CSC_Tilebases.xlp')
    xlp=native.read(dst/'XLPs/CSC_Tilebases.xlp');assert not any(exp.txt(e,'m_EntryID')==WATER for e in xlp.findall('m_Entries/Element'))
    e=E.SubElement(xlp.find('m_Entries'),'Element');E.SubElement(e,'m_EntryID',{'text':WATER});E.SubElement(e,'m_ObjectName',{'text':WATER});native.save(dst/'XLPs/CSC_Tilebases.xlp',xlp)
    for p in dst.rglob('*'):
        if p.is_file():resolver.index[p.name.casefold()]={p}
    states=[]
    for ident in (BASE,WATER,WIND):
        for state in ('Worked','Unworked','Construction','Pillaged','Unbuilt'):
            a=native.Assembly(resolver,state);key=a.asset(dst/'Assets'/(ident+'.ast'));states.append({'asset':ident,'state':state,'visible_groups':sum(len(m['groups']) for rec in a.assets.values() for m in rec['models'])})
    # Mirror the existing modern-era pattern for Water Mill only; no other row edits.
    art=MOD/'ArtDefs/CSC_Landmarks.artdef';raw=art.read_bytes();r=E.fromstring(raw);parents={c:p for p in r.iter() for c in p}
    source=next(e for e in r.iter('Element') if e.find('m_Name') is not None and exp.txt(e,'m_Name')=='06 Modern: Wind Mill')
    clone=copy.deepcopy(source)
    for n in clone.iter():
        if 'text' in n.attrib:n.set('text',n.get('text').replace('WIND_MILL','WATER_MILL').replace('Wind_Mill','Water_Mill').replace('Wind Mill','Water Mill'))
    parents[source].insert(list(parents[source]).index(source)+1,clone)
    native.save(dst/'ArtDefs/CSC_Landmarks.artdef',r)
    changed=[]
    for folder in ('Assets','Geometries','Textures','XLPs','ArtDefs'):
        for p in (dst/folder).iterdir():
            target=MOD/folder/p.name
            if not target.exists() or sha(p)!=sha(target):changed.append(p.relative_to(dst).as_posix())
    allowed={f'Geometries/{i}.{ext}' for i in (BASE,WATER) for ext in ('geo','fgx')}|{f'Textures/{n}.{ext}' for n in ('CSC_Atlas_Modern_AO','CSC_Props_Modern_01_AO') for ext in ('tex','dds')}|{f'Assets/{WATER}.ast','XLPs/CSC_Tilebases.xlp','ArtDefs/CSC_Landmarks.artdef'}
    assert set(changed)<=allowed,(set(changed)-allowed)
    dump(out/'staging-validation.json',{'passed':True,'native':checks,'states':states,'publish_files':changed,'existing_assemblies_unchanged':True,'fx':{'name':'FX_Rock2_Wake','basis':'Firaxis DIS_CTY_AWW WORKED_FLOW_LEFT_A native trigger','anchor':[39,20.5,-23],'scale':.65,'preview':'not evaluated by Blender; in-game placement review required'}})
    print('STAGED',len(changed),'files')

def publish(out):
    checks=json.loads((out/'staging-validation.json').read_text());assert checks['passed']
    for ident in (BASE,WATER):assert json.loads((out/'masters'/ident/'validation.json').read_text())['automated_pass']
    cook=json.loads((out/'cook-check/result.json').read_text());assert cook['exit_code']==0 and cook['blps']
    base=json.loads((out/'baseline.json').read_text());assert all(sha(Path(k))==v for k,v in base['sources'].items())
    assert all(sha(MOD/k)==v for k,v in base['runtime'].items()),'Concurrent runtime edit'
    assert sha(MOD/'Civ Supply Chains.civ6proj')==base['project']
    for kind,files in base['libraries'].items():assert all(sha(LIBS[kind]/k)==v for k,v in files.items())
    payload={}
    for ident,dest in DESTS.items():
        assert not dest.exists()
        for p in (out/'masters'/ident).rglob('*'):
            if p.is_file() and p.suffix!='.blend1':payload[dest/p.relative_to(out/'masters'/ident)]=p.read_bytes()
        payload[dest/(ident+'.cn6')]=(out/'staged/CN6'/(ident+'.cn6')).read_bytes()
    for kind,lib in LIBS.items():
        release=RELEASES[kind];assert not (lib/'Releases'/release).exists()
        for p in (out/'libraries'/kind).rglob('*'):
            if p.is_file():
                for target in (lib/'Current',lib/'Releases'/release):payload[target/p.relative_to(out/'libraries'/kind)]=p.read_bytes()
        payload[lib/'CURRENT.json']=json.dumps({'release':release,'current':'Current','snapshot':'Releases/'+release,'manifest':'Current/library.json'},indent=2).encode()
    for rel in checks['publish_files']:payload[MOD/rel]=(out/'staged'/rel).read_bytes()
    newpaths=[p for p in payload if p.is_relative_to(MOD) and not p.exists()]
    project=MOD/'Civ Supply Chains.civ6proj';raw=project.read_bytes()
    insert='\n  <ItemGroup>\n'+''.join('    <Content Include="'+str(p.relative_to(MOD))+'"><SubType>Content</SubType></Content>\n' for p in newpaths)+'  </ItemGroup>\n'
    payload[project]=raw.replace(b'</Project>',insert.encode()+b'</Project>');E.fromstring(payload[project])
    backup=out/'publication-backup';backup.mkdir();rows=[]
    for i,(p,data) in enumerate(payload.items()):
        row={'destination':str(p),'before':sha(p) if p.exists() else None}
        if p.exists():q=backup/f'{i:04}-{p.name}';shutil.copy2(p,q);row['backup']=str(q)
        rows.append(row)
    dump(backup/'manifest.json',rows)
    for row,(p,data) in zip(rows,payload.items()):
        assert (sha(p) if p.exists() else None)==row['before'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);row['after']=sha(p)
    changed=set(checks['publish_files']);assert all(sha(MOD/k)==v for k,v in base['runtime'].items() if Path(k).as_posix() not in changed)
    cache_inputs=[str(MOD/'Assets'/(i+'.ast')) for i in (BASE,WIND,SILO,'CSC_BAKERS_Flour_Trolley_Modern','CSC_BAKERS_Flour_Pallet_Modern')]+[str(MOD/'Materials'/(m+'.mtl')) for m in ('CSC_BAKERS_Modern','CSC_Props_Modern_01')]
    dump(out/'publication-report.json',{'installed':True,'files':rows,'cache_inputs':cache_inputs,'masters':{i:str(p/(i+'.blend')) for i,p in DESTS.items()},'existing_ASTs_unchanged':True,'in_game_tested':False})
    native.cache(out);print('PUBLISHED',len(rows),'files')

if __name__=='__main__':globals()[sys.argv[1]](Path(sys.argv[2]))
