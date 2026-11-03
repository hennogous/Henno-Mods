"""Create and independently verify the new native asset; does not install project files."""
import sys,json,copy,subprocess,math,shutil,hashlib
from pathlib import Path
import xml.etree.ElementTree as E
from PIL import Image
ROOT=Path(__file__).resolve().parents[4];MOD=ROOT/'Civ Supply Chains'
OUT=Path(sys.argv[1]);STAGE=OUT/'staged';NAME='CSC_BAKERS_Wind_Mill_Modern'
sys.path[:0]=[str(ROOT/'project/tools/blender/scene_export'),str(ROOT/'project/tools/blender')]
import export_scene as exp
from render_ae_asset import Resolver,Assembly,DEFAULT_SDK,helper
for folder in ['Assets','Geometries','Materials','Textures','CN6']:(STAGE/folder).mkdir(parents=True,exist_ok=True)
def read(p):return E.parse(p).getroot()
def save(r,p):exp.write_xml(p,r)
def text(r,p,v):r.find(p).set('text',v)
models=[json.loads((OUT/p).read_text()) for p in ['model.json','state_model.json']]
native=[];exe,_=helper(OUT/'native-reader')
converter=ROOT/'project/tools/cn6libs/CN6ToFGX.exe'
for m in models:
    ident=m['asset_id'];cn6=STAGE/'CN6'/(ident+'.cn6');fgx=STAGE/'Geometries'/(ident+'.fgx')
    exp.write_cn6(cn6,m);save(exp.geometry(m,read(MOD/'Geometries/CSC_Level_1_S.geo')),STAGE/'Geometries'/(ident+'.geo'))
    result=subprocess.run([str(converter),str(cn6),str(fgx),'2'],cwd=converter.parent,capture_output=True,text=True)
    (OUT/(ident+'-conversion.log')).write_text(result.stdout+result.stderr);assert result.returncode==0
    dest=OUT/(ident+'-native.json');subprocess.run([str(exe),str(exe.parent),str(fgx),str(dest)],cwd=exe.parent,check=True,capture_output=True)
    raw=json.loads(dest.read_text());assert len(raw['meshes'])==len(m['meshes'])
    for a,b in zip(m['meshes'],raw['meshes']):
        assert b['boneBindings']==['Bone'],b['boneBindings']
        assert len(a['vertices'])==len(b['vertices']) and len(a['triangles'])==len(b['triangles'])
        assert all(len(v['uv'])==2 and len(v['uv2'])==2 and len(v['uv3'])==2 for v in b['vertices'])
        native.append({'mesh':b['name'],'vertices':len(b['vertices']),'triangles':len(b['triangles']),'bindings':b['boneBindings'],'uv_channels':3})

# One generated material family plus a state-specific geometry AO binding.
for ident in [NAME,NAME+'_CON+PIL']:
    r=read(MOD/'Materials/CSC_BAKERS_E.mtl');text(r,'m_Name',ident)
    mapping={exp.SLOTS[k]:NAME+'_'+k for k in ('B','N','G','M','E')};mapping['AO']=ident+'_AO'
    for row in r.findall('m_CookParams/m_Values/Element'):
        param=exp.txt(row,'m_ParamName')
        if param in mapping:row.find('m_ObjectName').set('text',mapping[param])
        if param in ('Opacity','LightMap','TintMask'):row.find('m_ObjectName').set('text','')
    save(r,STAGE/'Materials'/(ident+'.mtl'))
textures={}
for p in sorted((OUT/'textures').glob(NAME+'*.png')):
    ch=p.stem.rsplit('_',1)[1];size=list(Image.open(p).size);fmt='R8_UNORM' if ch in ('AO','G','M') else 'R8G8B8A8_UNORM'
    source=p
    if ch in ('AO','G','M'):
        source=OUT/'scalar-conversion'/p.name;source.parent.mkdir(exist_ok=True);Image.open(p).convert('RGB').getchannel('R').save(source)
    cmd=[str(ROOT/'project/tools/directxtex/texconv.exe'),'-nologo','-y','-m','0','-f',fmt,'--ignore-srgb','-o',str(STAGE/'Textures')]
    if ch in ('B','E'):cmd+=['-srgb']
    result=subprocess.run(cmd+[str(source)],capture_output=True,text=True);assert result.returncode==0,result.stdout+result.stderr
    spec={'slot':ch,'size':size,'format':fmt};dds=STAGE/'Textures'/(p.stem+'.dds')
    if ch in ('AO','G','M'):exp.normalize_ao_dds(dds,spec,MOD/'Textures/CSC_Props_Shared_01_AO.dds')
    exp.validate_dds(dds,spec)
    template=MOD/'Textures'/('CSC_Atlas_B_BAKERS.tex' if ch=='B' else 'CSC_Props_Shared_01_AO.tex' if ch=='AO' else 'CSC_Atlas_'+ch+'.tex')
    r=read(template);text(r,'m_Name',p.stem);text(r,'m_SourceFilePath',str(p));text(r,'m_DataFiles/Element/m_RelativePath',p.stem+'.dds')
    r.find('m_Width').text=str(size[0]);r.find('m_Height').text=str(size[1]);r.find('m_NumMipMaps').text=str(int(math.log2(max(size))))
    save(r,STAGE/'Textures'/(p.stem+'.tex'));textures[p.stem]=spec

asset=read(MOD/'Assets/CSC_BAKERS_Flour_Closed.ast');text(asset,'m_Name',NAME);text(asset,'m_Description','Modern-era flour mill with integrated silo, elevator and sheltered stock')
behavior=asset.find('m_BehaviorData');text(behavior,'m_dsgName','Standard_Landmark')
for path in ['m_referenceGeometryNames','m_behaviorDataSets/m_animationBindings/m_Bindings','m_behaviorDataSets/m_timelineBindings/m_Bindings','m_behaviorDataSets/m_timelines/m_Timelines','m_behaviorDataSets/m_attachmentPoints/m_Points']:
    node=behavior.find(path)
    if node is not None:node.clear()
for model in models:E.SubElement(behavior.find('m_referenceGeometryNames'),'Element',{'text':model['asset_id']})
instances=asset.find(exp.MODELS);instances.clear()
for i,model in enumerate(models):
    visible=('Worked','Unworked') if i==0 else {model['meshes'][0]['name']:('Construction','Pillaged'),model['meshes'][1]['name']:('Construction',)}
    instances.append(exp.model_instance(model,{m['name']:model['asset_id'] for mesh in model['meshes'] for m in mesh['materials']},visible))
for row in asset.findall('m_CookParams/m_Values/Element'):
    if exp.txt(row,'m_ParamName')=='CullingMode':row.find('m_Value').set('text','PERMANENT')
save(asset,STAGE/'Assets'/(NAME+'.ast'))
resolver=Resolver(MOD,DEFAULT_SDK)
for p in STAGE.rglob('*'):
    if p.suffix in ['.ast','.geo','.fgx','.mtl','.tex','.dds']:resolver.index[p.name.casefold()]={p}
states=[]
for state,counts in [('Worked',[2,0]),('Unworked',[2,0]),('Construction',[0,2]),('Pillaged',[0,1]),('Unbuilt',[0,0])]:
    a=Assembly(resolver,state);key=a.asset(STAGE/'Assets'/(NAME+'.ast'));actual=[len(m['groups']) for m in a.assets[key]['models']]
    assert actual==counts,(state,actual);states.append({'state':state,'visible_groups':actual})
(OUT/'staging-validation.json').write_text(json.dumps({'native':native,'textures':textures,'states':states,'passed':True},indent=2))
print('STAGED_AND_VERIFIED',json.dumps(native),json.dumps(states))
