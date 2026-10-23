"""Stage the grounded tower, shared ruin shell and native construction scaffold."""
import copy,hashlib,importlib.util,json,os,re,shutil,subprocess,sys
from pathlib import Path
import xml.etree.ElementTree as E
from PIL import Image
from windmill_tower_integrate import *
OUT=Path(sys.argv[2]);STAGE=OUT/'staged';RUIN=NAME+'_CON+PIL'
SOURCE=ART/'BAKERS/Wind Mill/tower'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def prepare():
    exe,_=helper(OUT/'cache')
    for name in (NAME,RUIN):
        native=OUT/(name+'-native.json')
        subprocess.run([str(exe),str(exe.parent),str(STAGE/f'Geometries/{name}.fgx'),str(native)],cwd=exe.parent,check=True)
        raw=json.loads(native.read_text());materials=cn6_material_names(STAGE/f'Geometries/{name}.cn6')
        geo=read_xml(MOD/f'Geometries/{NAME}.geo');geo.tag='AssetObjects..GeometryInstance';geo.find('m_Meshes').clear();geo.find('m_Bones').clear()
        for m in raw['meshes']:
            validate_native_groups(m)
            row=E.SubElement(geo.find('m_Meshes'),'Element');field(row,'m_Name',m['name']);groups=E.SubElement(row,'m_Groups')
            for group in m['groups']:
                g=E.SubElement(groups,'Element');field(g,'m_Name',materials[m['name']][group['material']])
                E.SubElement(g,'m_nFirstPrim').text=str(group['first']);E.SubElement(g,'m_nPrims').text=str(group['count'])
            for k,v in [('m_nBoundBoneCount',len(m['boneBindings'])),('m_nPrimitiveCount',len(m['triangles'])),('m_nVertexCount',len(m['vertices']))]:E.SubElement(row,k).text=str(v)
        for b in raw['models'][0]['bones']:field(geo.find('m_Bones'),'Element',b['name'])
        for k in ['m_ModelName','m_Name','m_Description']:geo.find(k).set('text',name)
        geo.find('m_DataFiles/Element/m_RelativePath').set('text',name+'.fgx');save(geo,STAGE/f'Geometries/{name}.geo')
        scalar=OUT/'scalar';scalar.mkdir(exist_ok=True);png=scalar/(name+'_AO.png')
        Image.open(OUT/'staged-textures'/png.name).convert('RGB').getchannel('R').save(png)
        dest=STAGE/'Textures';dest.mkdir(exist_ok=True)
        subprocess.run([str(ROOT/'project/tools/directxtex/texconv.exe'),'-nologo','-y','-m','0','-f','R8_UNORM','--ignore-srgb','-o',str(dest),str(png)],check=True)
        spec=importlib.util.spec_from_file_location('export_scene',ROOT/'project/tools/blender/scene_export/export_scene.py');conv=importlib.util.module_from_spec(spec);spec.loader.exec_module(conv)
        desc={'format':'R8_UNORM','size':[512,512],'slot':'AO'}
        conv.normalize_ao_dds(dest/(name+'_AO.dds'),desc,MOD/'Textures/CSC_Atlas_AO2.dds');conv.validate_dds(dest/(name+'_AO.dds'),desc)
        tex=read_xml(MOD/f'Textures/{AO}.tex');tex.find('m_Name').set('text',name+'_AO');tex.find('m_SourceFilePath').set('text',str(SOURCE/(name+'_AO.png')))
        tex.find('m_DataFiles/Element/m_RelativePath').set('text',name+'_AO.dds');save(tex,dest/(name+'_AO.tex'))
    shutil.copy2(OUT/(NAME+'-native.json'),OUT/'tower-native.json')
    for mat in MATS:
        root=read_xml(MOD/f'Materials/{mat}.mtl');root.find('m_Name').set('text',mat+'_Ruin')
        for node in root.findall('.//Element'):
            if txt(node,'m_ParamName')=='AO':node.find('m_ObjectName').set('text',RUIN+'_AO')
        save(root,STAGE/f'Materials/{mat}_Ruin.mtl')
    asset=read_xml(MOD/f'Assets/{NAME}.ast');models=asset.find('m_GeometrySet/m_ModelInstances');template=models.find('Element')
    ruin=copy.deepcopy(template);ruin.find('m_Name').set('text',RUIN);ruin.find('m_GeoName').set('text',RUIN)
    templates=list(template.find('m_GroupStates'))[:5];states=ruin.find('m_GroupStates');states.clear()
    geo=read_xml(STAGE/f'Geometries/{RUIN}.geo')
    for mesh in geo.findall('m_Meshes/Element'):
        for group in mesh.findall('m_Groups/Element'):
            for t in templates:
                row=copy.deepcopy(t);state=txt(row,'m_StateName');row.find('m_MeshName').set('text',txt(mesh,'m_Name'));row.find('m_GroupName').set('text',txt(group,'m_Name'))
                for v in row.findall('m_Values/m_Values/Element'):
                    param=txt(v,'m_ParamName')
                    if param=='Material':v.find('m_ObjectName').set('text',txt(group,'m_Name'))
                    if param=='Visible':v.find('m_bValue').text=str(state in ['Construction','Pillaged']).lower()
                    if param=='EmissiveEnabled':v.find('m_bValue').text='false'
                    if param=='BurnMaterial':v.find('m_ObjectName').set('text','DefaultBurnMaterial' if state=='Pillaged' else '')
                states.append(row)
    models.append(ruin);field(asset.find('m_BehaviorData/m_referenceGeometryNames'),'Element',RUIN)
    parent=read_xml(MOD/'Assets/CSC_BAKERS_Wind_Mill.ast')
    point=next(p for p in parent.findall('.//m_Points/Element') if txt(p,'m_Name')=='newAttachmentPoint_11');point=copy.deepcopy(point)
    for k,v in [('m_Name','Construction_Scaffold'),('m_BoneName',NAME),('m_ModelInstanceName',NAME)]:point.find(k).set('text',v)
    point.find('m_scale').text='1.45'
    for axis,value in zip('xyz',(3.699117,-2.416936192431123,.09715)):point.find('m_position/'+axis).text=str(value)
    for axis in 'xyz':point.find('m_orientation/'+axis).text='0'
    for v in point.findall('m_CookParams/m_Values/Element'):
        param=txt(v,'m_ParamName')
        if param=='Asset':
            for k,value in [('m_EntryName','PROP_Scaffold_A'),('m_XLPPath','tilebases.xlp'),('m_BLPPackage','landmarks/tilebases')]:v.find(k).set('text',value)
        if param=='TerrainFollowMode':v.find('m_Value').set('text','Average Height')
    asset.find('.//m_attachmentPoints/m_Points').append(point);save(asset,STAGE/f'Assets/{NAME}.ast')
    for suffix in ('','_2'):
        p=MOD/f'Assets/CSC_BAKERS_Wind_Mill{suffix}.ast';before=p.read_bytes()
        assert before.count(b'<z>-3.128043</z>')==1
        changed=before.replace(b'<z>-3.128043</z>',b'<z>-0.136043</z>')
        (STAGE/'Assets'/p.name).write_bytes(changed)
    project=MOD/'Civ Supply Chains.civ6proj';content=project.read_bytes();new=[]
    for p in sorted(STAGE.rglob('*')):
        if p.suffix not in ['.ast','.geo','.fgx','.anm','.mtl','.dds','.tex']:continue
        rel=str(p.relative_to(STAGE));marker=('Include="'+rel+'"').encode()
        if marker not in content:new.append('    <Content Include="'+rel+'">\r\n      <SubType>Content</SubType>\r\n    </Content>\r\n')
    pos=content.rfind(b'  </ItemGroup>');assert pos>0
    (STAGE/project.name).write_bytes(content[:pos]+''.join(new).encode()+content[pos:])
    rows=[];backup=OUT/'before';backup.mkdir(exist_ok=True)
    files=[(p,MOD/p.relative_to(STAGE)) for p in STAGE.rglob('*') if p.suffix in ['.ast','.geo','.fgx','.anm','.mtl','.dds','.tex','.civ6proj']]
    for name in (NAME,RUIN):files.extend([(OUT/'masters'/(name+'.blend'),SOURCE/(name+'.blend')),(STAGE/'Geometries'/(name+'.cn6'),SOURCE/(name+'.cn6')),(OUT/'staged-textures'/(name+'_AO.png'),SOURCE/(name+'_AO.png'))])
    for i,(src,dst) in enumerate(files):
        b=backup/(str(i)+'-'+dst.name);assert not b.exists()
        if dst.exists():shutil.copy2(dst,b)
        rows.append(dict(source=str(src),destination=str(dst),backup=str(b) if dst.exists() else None,before=sha(dst) if dst.exists() else None))
    (OUT/'install-plan.json').write_text(json.dumps(rows,indent=2));print('Staged',len(rows),'files')

def jobs():
    for state in ('Worked','Construction','Pillaged'):
        resolver=Resolver(MOD,DEFAULT_SDK)
        for p in STAGE.rglob('*'):
            if p.suffix.lower() in ['.ast','.geo','.fgx','.dds','.tex','.mtl','.anm']:resolver.index[p.name.casefold()]={p}
        assembly=Assembly(resolver,state=state);key=assembly.asset(STAGE/'Assets/CSC_BAKERS_Wind_Mill.ast')
        run=OUT/('review-'+state);run.mkdir(exist_ok=True);prepare_geometry(assembly,OUT/'cache',run)
        settings=dict(modes=['sv'],presets=PRESETS,resolution=1200,samples=32,icon_texture='runtime',state=state,seed=0,render_emission_enabled=False,camera_class='auto')
        job=dict(root=key,assets=assembly.assets,geometries=assembly.geometries,materials=assembly.materials,excluded=assembly.excluded,warnings=assembly.warnings,settings=settings,output=str(run))
        (run/'job.json').write_text(json.dumps(job,indent=2));print(state,len(assembly.assets),assembly.warnings)

def install():
    result=json.loads((OUT/'cook-grounded/result.json').read_text());log=(OUT/'cook-grounded/stdout.log').read_text()
    assert result['exit_code']==0 and 'XLP cook completed with success.' in log and '(ERRORS!!)' not in log and 'Replacing asset:' not in log
    assert json.loads((OUT/'native-animation-validation.json').read_text())['frames_checked']==301
    rows=json.loads((OUT/'install-plan.json').read_text())
    for r in rows:assert (sha(r['destination']) if Path(r['destination']).exists() else None)==r['before'],r['destination']
    for r in rows:
        dst=Path(r['destination']);dst.parent.mkdir(parents=True,exist_ok=True);tmp=dst.with_name(dst.name+'.ground-tmp');shutil.copy2(r['source'],tmp);os.replace(tmp,dst);r['installed_sha256']=sha(dst)
    (OUT/'publication-report.json').write_text(json.dumps(dict(installed=True,files=rows),indent=2));print('Installed',len(rows),'files with backups')

def verify():
    import numpy as np,struct
    report=json.loads((OUT/'publication-report.json').read_text())
    for r in report['files']:
        p=Path(r['destination']);source=Path(r['source'])
        if sha(p)!=sha(source):
            if p.suffix=='.tex':
                def semantic(n):return (n.tag,sorted(n.attrib.items()),(n.text or '').strip() if n.tag!='m_ExportedTime' else '',[semantic(c) for c in n])
                assert semantic(read_xml(p))==semantic(read_xml(source)),p
                r['watcher_updated_export_timestamp']=True
            else:
                assert p.suffix=='.dds',p
                assert struct.unpack('<8I',p.read_bytes()[76:108])==(32,64,0,8,255,0,0,0)
                assert np.array_equal(np.array(Image.open(p).convert('RGB'))[:,:,0],np.array(Image.open(source).convert('RGB'))[:,:,0])
                r['watcher_regenerated_identical_ao_pixels']=True
        r['installed_sha256']=sha(p)
        if p.name in ['CSC_BAKERS_Wind_Mill.ast','CSC_BAKERS_Wind_Mill_2.ast']:
            assert p.read_bytes().replace(b'<z>-0.136043</z>',b'<z>-3.128043</z>')==Path(r['backup']).read_bytes()
    validations=[]
    for name in (NAME,RUIN):
        v=json.loads((OUT/(name+'-installed-validation.json')).read_text());assert v['error_count']==0 and v['warning_count']==0;validations.append(v['counts']['main_vertices'])
        raw=json.loads((OUT/(name+'-native.json')).read_text());geo=read_xml(MOD/f'Geometries/{name}.geo');assert geo.tag=='AssetObjects..GeometryInstance'
        assert min(v['position'][2] for m in raw['meshes'] for v in m['vertices'])==-30
    asset=read_xml(MOD/f'Assets/{NAME}.ast');states={}
    for model in asset.findall('.//m_ModelInstances/Element'):
        name=txt(model,'m_GeoName');expected=['Worked','Unworked'] if name==NAME else ['Construction','Pillaged']
        for row in model.findall('m_GroupStates/Element'):
            visible=next(x.findtext('m_bValue') for x in row.findall('.//Element') if txt(x,'m_ParamName')=='Visible')=='true'
            assert visible==(txt(row,'m_StateName') in expected)
        states[name]=expected
    resolver=Resolver(MOD,DEFAULT_SDK);scaffold=read_xml(resolver.resolve('PROP_Scaffold_A','.ast'))
    for row in scaffold.findall('.//m_GroupStates/Element'):
        visible=next(x.findtext('m_bValue') for x in row.findall('.//Element') if txt(x,'m_ParamName')=='Visible')=='true'
        assert visible==(txt(row,'m_StateName')=='Construction')
    assert json.loads((OUT/'sail-clearance.json').read_text())=={}
    report.update(installed_source_errors=0,installed_source_warnings=0,native_vertices=validations,states=states,scaffold_construction_only=True,parent_other_bytes_preserved=True)
    (OUT/'publication-report.json').write_text(json.dumps(report,indent=2));print('Verified installation, source contracts, native bounds, all states, scaffold visibility and both preserved parent ASTs.')

if __name__=='__main__':globals()[sys.argv[1]]()
