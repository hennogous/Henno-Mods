"""Stage native descriptors, texture DDSs and a placement-preserving AE replacement."""
import copy,json,sys,subprocess,math,shutil,hashlib,importlib.util
from pathlib import Path
import xml.etree.ElementTree as E
from PIL import Image
ROOT=Path(__file__).resolve().parents[3];MOD=ROOT/'Civ Supply Chains'
sys.path.insert(0,str(ROOT/'project/tools/blender'))
from render_ae_asset import read_xml,txt,helper,Resolver,Assembly,prepare_geometry,PRESETS,DEFAULT_SDK
NAME='CSC_BAKERS_Wind_Mill_Tower';OLD='CSC_BAKERS_Wind_Mill_Tower';AO=NAME+'_AO'
MATS=['CSC_BAKERS_Wind_Mill_Plaster','CSC_BAKERS_Wind_Mill_Sails']
ART=Path.home()/'Desktop/Working Files/3D Art'
def save(root,path):
    # The renderer's XML reader normalizes legacy unbound ':' to a single dot.
    # Firaxis's native type loader requires the canonical double-dot spelling.
    if root.tag.startswith('AssetObjects.') and not root.tag.startswith('AssetObjects..'):
        root.tag=root.tag.replace('AssetObjects.','AssetObjects..',1)
    path.parent.mkdir(parents=True,exist_ok=True);E.indent(root,space='  ');E.ElementTree(root).write(path,encoding='utf-8',xml_declaration=True)
def field(root,name,value):E.SubElement(root,name,{'text':str(value)})

def validate_native_groups(mesh):
    used=sorted(set(t[3] for t in mesh['triangles']))
    if used!=list(range(len(mesh['groups']))):
        raise ValueError(f"{mesh['name']}: remove unused material slots before native export")
    if any(g['count']==0 for g in mesh['groups']):
        raise ValueError(f"{mesh['name']}: empty native topology group")

def cn6_material_names(path):
    names={};mesh=None;reading=False
    for line in Path(path).read_text().splitlines():
        if line.startswith('mesh:"'):mesh=line[6:-1];names[mesh]=[];reading=False
        elif line=='materials':reading=True
        elif line=='vertices':reading=False
        elif reading:names[mesh].append(line.strip('"'))
    return names
def stage(out):
    stage=out/'staged';extract,_=helper(out/'cache')
    native=out/'tower-native.json'
    subprocess.run([str(extract),str(extract.parent),str(stage/f'Geometries/{NAME}.fgx'),str(native)],cwd=extract.parent,check=True,capture_output=True)
    raw=json.loads(native.read_text())
    material_names=cn6_material_names(stage/f'Geometries/{NAME}.cn6')
    geo=read_xml(MOD/f'Geometries/{OLD}.geo');geo.find('m_Meshes').clear();geo.find('m_Bones').clear()
    for m in raw['meshes']:
        validate_native_groups(m)
        row=E.SubElement(geo.find('m_Meshes'),'Element');field(row,'m_Name',m['name']);groups=E.SubElement(row,'m_Groups')
        indices=sorted(set(t[3] for t in m['triangles']))
        for i in indices:
            subset=[j for j,t in enumerate(m['triangles']) if t[3]==i];assert subset==list(range(min(subset),max(subset)+1))
            g=E.SubElement(groups,'Element');field(g,'m_Name',material_names[m['name']][i]);E.SubElement(g,'m_nFirstPrim').text=str(min(subset));E.SubElement(g,'m_nPrims').text=str(len(subset))
        for k,v in [('m_nBoundBoneCount',len(m['boneBindings'])),('m_nPrimitiveCount',len(m['triangles'])),('m_nVertexCount',len(m['vertices']))]:E.SubElement(row,k).text=str(v)
    for b in raw['models'][0]['bones']:field(geo.find('m_Bones'),'Element',b['name'])
    for k in ['m_ModelName','m_Name','m_Description']:geo.find(k).set('text',NAME)
    geo.find('m_DataFiles/Element/m_RelativePath').set('text',NAME+'.fgx');save(geo,stage/f'Geometries/{NAME}.geo')
    for name,template in zip(MATS,['CSC_BAKERS_NE','CSC_ALL_Props_01']):
        mat=read_xml(MOD/f'Materials/{template}.mtl');mat.find('m_Name').set('text',name)
        for row in mat.findall('m_CookParams/m_Values/Element'):
            if txt(row,'m_ParamName')=='AO':row.find('m_ObjectName').set('text',AO)
            if txt(row,'m_ParamName')=='Emissive':row.find('m_ObjectName').set('text','')
        save(mat,stage/f'Materials/{name}.mtl')
    asset=read_xml(MOD/'Assets/CSC_BAKERS_Flour_Closed.ast');asset.find('m_Name').set('text',NAME)
    behavior=asset.find('m_BehaviorData');behavior.find('m_dsgName').set('text','Standard_Landmark')
    field(behavior.find('m_referenceGeometryNames'),'Element',NAME)
    bindings=behavior.find('m_behaviorDataSets/m_animationBindings/m_Bindings');binding=E.SubElement(bindings,'Element');field(binding,'m_SlotName','WORKED_A');field(binding,'m_AnimationName',NAME+'_Turn')
    model=asset.find('m_GeometrySet/m_ModelInstances/Element');model.find('m_Name').set('text',NAME);model.find('m_GeoName').set('text',NAME)
    states=model.find('m_GroupStates');templates=list(states);states.clear()
    for mesh in geo.findall('m_Meshes/Element'):
        for group in mesh.findall('m_Groups/Element'):
            for template in templates:
                row=copy.deepcopy(template);row.find('m_MeshName').set('text',txt(mesh,'m_Name'));row.find('m_GroupName').set('text',txt(group,'m_Name'))
                for v in row.findall('m_Values/m_Values/Element'):
                    param=txt(v,'m_ParamName')
                    if param=='Material':v.find('m_ObjectName').set('text',txt(group,'m_Name'))
                    if param=='Visible':v.find('m_bValue').text='true' if txt(row,'m_StateName') in ['Worked','Unworked','Idle'] else 'false'
                states.append(row)
    for v in asset.findall('m_CookParams/m_Values/Element'):
        if txt(v,'m_ParamName')=='CullingMode':v.find('m_Value').set('text','PERMANENT')
    save(asset,stage/f'Assets/{NAME}.ast')
    protected={}
    for suffix in ['', '_2']:
        src=MOD/f'Assets/CSC_BAKERS_Wind_Mill{suffix}.ast';before=src.read_bytes();assert OLD.encode() in before
        backup=out/'before'/src.relative_to(MOD);backup.parent.mkdir(parents=True,exist_ok=True);backup.write_bytes(before)
        # Exact textual replacement leaves every unrelated AE value byte-identical.
        dest=stage/src.relative_to(MOD);dest.write_bytes(before.replace(OLD.encode(),NAME.encode()))
        protected[str(src)]=hashlib.sha256(before).hexdigest()
    xlp=MOD/'XLPs/CSC_Tilebases.xlp';before=xlp.read_bytes();backup=out/'before/XLPs'/xlp.name;backup.parent.mkdir(exist_ok=True);backup.write_bytes(before)
    root=read_xml(xlp);row=E.SubElement(root.find('m_Entries'),'Element');field(row,'m_EntryID',NAME);field(row,'m_ObjectName',NAME);save(root,stage/'XLPs'/xlp.name);protected[str(xlp)]=hashlib.sha256(before).hexdigest()
    (out/'integration-baseline.json').write_text(json.dumps(protected,indent=2))
    spec=importlib.util.spec_from_file_location('texture_export',ROOT/'project/tools/blender/scene_export/export_scene.py');conv=importlib.util.module_from_spec(spec);spec.loader.exec_module(conv)
    ddsdir=stage/'Textures';ddsdir.mkdir(exist_ok=True)
    for source in (out/'staged-textures').glob('*.png'):
        name=source.stem;channel='AO' if name==AO else ('B' if '_B_' in name else name.rsplit('_',1)[1]);size=512 if channel=='AO' else 1024;scalar=channel in ['G','M','O','AO'];fmt='R8_UNORM' if scalar else 'R8G8B8A8_UNORM'
        cmd=[str(ROOT/'project/tools/directxtex/texconv.exe'),'-nologo','-y','-m','0','-f',fmt,'--ignore-srgb','-o',str(ddsdir)]
        if channel=='B':cmd+=['-srgb']
        conversion_source=source
        if scalar:
            # Civ VI consumes red. A few authored scalar texels have unequal RGB;
            # automatic RGB-to-R8 luminance conversion would alter other Quarters.
            conversion_source=out/'scalar-conversion'/source.name;conversion_source.parent.mkdir(exist_ok=True)
            Image.open(source).convert('RGB').getchannel('R').save(conversion_source)
        result=subprocess.run(cmd+[str(conversion_source)],capture_output=True,text=True);assert result.returncode==0,result.stderr
        desc={'size':[size,size],'format':fmt,'slot':channel};target=ddsdir/(name+'.dds')
        canonical=out/'canonical-dds';canonical.mkdir(exist_ok=True);shutil.copy2(target,canonical/target.name)
        if scalar:conv.normalize_ao_dds(target,desc,MOD/'Textures/CSC_Atlas_AO2.dds')
        conv.validate_dds(target,desc)
        tex=read_xml(MOD/'Textures'/('CSC_Atlas_AO2.tex' if channel=='AO' else name+'.tex'))
        if channel=='AO':
            tex.find('m_Name').set('text',name);tex.find('m_Width').text=tex.find('m_Height').text=str(size);tex.find('m_NumMipMaps').text='9';tex.find('m_SourceFilePath').set('text',str(ART/'BAKERS/Wind Mill/tower'/source.name));tex.find('m_DataFiles/Element/m_RelativePath').set('text',name+'.dds')
        save(tex,ddsdir/(name+'.tex'))
    (out/'tower-native-counts.json').write_text(json.dumps({m['name']:len(m['vertices']) for m in raw['meshes']},indent=2))
    print('STAGED descriptors, 9 textures, two existing assembly replacements;',sum(len(m['vertices']) for m in raw['meshes']),'native vertices')

def review(out):
    resolver=Resolver(MOD,DEFAULT_SDK)
    for p in (out/'staged').rglob('*'):
        if p.suffix.lower() in ['.ast','.geo','.fgx','.dds','.tex','.mtl','.anm']:resolver.index[p.name.casefold()]={p}
    assembly=Assembly(resolver);key=assembly.asset(out/'staged/Assets/CSC_BAKERS_Wind_Mill.ast')
    run=out/'review';run.mkdir(exist_ok=True);prepare_geometry(assembly,out/'cache',run)
    settings={'modes':['sv'],'presets':PRESETS,'resolution':1400,'samples':64,'icon_texture':'runtime','state':'Worked','seed':0,'render_emission_enabled':False,'camera_class':'auto'}
    job=dict(root=key,assets=assembly.assets,geometries=assembly.geometries,materials=assembly.materials,excluded=assembly.excluded,warnings=assembly.warnings,settings=settings,output=str(run))
    (run/'job.json').write_text(json.dumps(job,indent=2));print('REVIEW prepared',len(assembly.assets),'assets',assembly.warnings)

if __name__=='__main__':globals()[sys.argv[1]](Path(sys.argv[2]))
