"""Stage/verify/install only edited intact mill geometry and its six texture maps."""
import sys,json,shutil,subprocess,hashlib,math
from pathlib import Path
import xml.etree.ElementTree as E
from PIL import Image
ROOT=Path(__file__).resolve().parents[4];MOD=ROOT/'Civ Supply Chains';NAME='CSC_BAKERS_Wind_Mill_Modern'
sys.path[:0]=[str(ROOT/'project/tools/blender/scene_export'),str(ROOT/'project/tools/blender')]
import export_scene as exp
from render_ae_asset import Resolver,Assembly,DEFAULT_SDK,helper
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def verify_parity(out):
    model=json.loads((out/'model.json').read_text());native=json.loads((out/'native.json').read_text());largest=0
    for a,b in zip(model['meshes'],native['meshes']):
        assert a['triangles']==b['triangles'],'Triangle topology changed'
        for v,w in zip(a['vertices'],b['vertices']):
            row=w['position']+w['normal']+w['tangent']+w['binormal']+w['uv']+w['uv2']+w['uv3']
            error=max(abs(x-y) for x,y in zip(v,row));largest=max(largest,error);assert error<1e-4,error
            assert w['boneWeights']==[255,0,0,0,0,0,0,0] and w['boneIndices']==[0]*8
    exe,_=helper(out/'native-reader');old=out/'previous-native.json'
    subprocess.run([str(exe),str(exe.parent),str(MOD/'Geometries'/(NAME+'.fgx')),str(old)],cwd=exe.parent,check=True,capture_output=True)
    previous=json.loads(old.read_text());assert previous['models'][0]['placement']==native['models'][0]['placement'],'Native model placement changed'
    (out/'native-parity.json').write_text(json.dumps({'passed':True,'largest_vertex_component_error':largest,'all_positions_normals_tangents_uvs_weights_and_topology_match':True,'previous_native_placement_preserved':True},indent=2))
def stage(out):
    dest=out/'staged'
    for folder in ('Assets','Geometries','Materials','Textures','CN6'):
        (dest/folder).mkdir(parents=True,exist_ok=True)
        if folder!='CN6':
            for p in (MOD/folder).glob(NAME+'*'):shutil.copy2(p,dest/folder/p.name)
    model=json.loads((out/'model.json').read_text())
    cn6=dest/'CN6'/(NAME+'.cn6');fgx=dest/'Geometries'/(NAME+'.fgx')
    exp.write_cn6(cn6,model);exp.write_xml(dest/'Geometries'/(NAME+'.geo'),exp.geometry(model,E.parse(MOD/'Geometries'/(NAME+'.geo')).getroot()))
    converter=ROOT/'project/tools/cn6libs/CN6ToFGX.exe'
    r=subprocess.run([str(converter),str(cn6),str(fgx),'2'],cwd=converter.parent,capture_output=True,text=True)
    (out/'conversion.log').write_text(r.stdout+r.stderr);assert r.returncode==0,r.stdout+r.stderr
    exe,_=helper(out/'native-reader');native=out/'native.json'
    subprocess.run([str(exe),str(exe.parent),str(fgx),str(native)],cwd=exe.parent,check=True,capture_output=True)
    actual=json.loads(native.read_text());assert len(actual['meshes'])==len(model['meshes'])
    checks=[]
    for a,b in zip(model['meshes'],actual['meshes']):
        assert a['name']==b['name'];assert b['boneBindings']==['Bone']
        assert len(a['vertices'])==len(b['vertices']) and len(a['triangles'])==len(b['triangles'])
        assert all(len(v[k])==2 for v in b['vertices'] for k in ('uv','uv2','uv3'))
        checks.append({'name':b['name'],'vertices':len(b['vertices']),'triangles':len(b['triangles']),'bindings':b['boneBindings']})
    changed=['Geometries/'+NAME+'.fgx','Geometries/'+NAME+'.geo'];textures={}
    for ch in ('B','N','G','M','E','AO'):
        p=out/'textures'/f'{NAME}_{ch}.png';size=list(Image.open(p).size);fmt='R8_UNORM' if ch in ('AO','G','M') else 'R8G8B8A8_UNORM';source=p
        if ch in ('AO','G','M'):
            source=out/'scalar-conversion'/p.name;source.parent.mkdir(exist_ok=True);Image.open(p).convert('RGB').getchannel('R').save(source)
        cmd=[str(ROOT/'project/tools/directxtex/texconv.exe'),'-nologo','-y','-m','0','-f',fmt,'--ignore-srgb','-o',str(dest/'Textures')]
        if ch in ('B','E'):cmd+=['-srgb']
        r=subprocess.run(cmd+[str(source)],capture_output=True,text=True);assert r.returncode==0,r.stdout+r.stderr
        spec={'slot':ch,'size':size,'format':fmt};dds=dest/'Textures'/(p.stem+'.dds')
        if ch in ('AO','G','M'):exp.normalize_ao_dds(dds,spec,MOD/'Textures/CSC_Props_Shared_01_AO.dds')
        exp.validate_dds(dds,spec)
        tex=dest/'Textures'/(p.stem+'.tex');root=E.parse(tex).getroot()
        root.find('m_SourceFilePath').set('text',str(p));root.find('m_Width').text=str(size[0]);root.find('m_Height').text=str(size[1]);root.find('m_NumMipMaps').text=str(int(math.log2(max(size))))
        exp.write_xml(tex,root);textures[ch]=spec
        changed.extend(['Textures/'+p.stem+'.dds','Textures/'+p.stem+'.tex'])
    resolver=Resolver(MOD,DEFAULT_SDK)
    for p in dest.rglob('*'):
        if p.suffix in ('.ast','.geo','.fgx','.mtl','.tex','.dds'):resolver.index[p.name.casefold()]={p}
    states=[]
    for state,counts in [('Worked',[2,0]),('Unworked',[2,0]),('Construction',[0,2]),('Pillaged',[0,1]),('Unbuilt',[0,0])]:
        a=Assembly(resolver,state);key=a.asset(dest/'Assets'/(NAME+'.ast'));seen=[len(m['groups']) for m in a.assets[key]['models']];assert seen==counts,(state,seen)
        states.append({'state':state,'visible_groups':seen})
    assert sha(dest/'Assets'/(NAME+'.ast'))==sha(MOD/'Assets'/(NAME+'.ast'))
    report={'passed':True,'native':checks,'textures':textures,'states':states,'publish_files':changed,'ast_preserved':True,'state_geometry_preserved':True}
    (out/'staging-validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
def install(out):
    baseline=json.loads((out/'baseline.json').read_text());staged=json.loads((out/'staging-validation.json').read_text())
    baseline['files']={k.replace('\\','/'):v for k,v in baseline['files'].items()}
    baseline['protected']=[k.replace('\\','/') for k in baseline['protected']]
    validation=json.loads((out/'source-validation.json').read_text())
    assert validation['automated_pass'],validation
    assert staged['passed'];cook=json.loads((out/'cook-check/result.json').read_text());assert cook['exit_code']==0 and cook['blps']
    verify_parity(out)
    assert sha(baseline['source'])==baseline['source_sha256'],'User source changed during export'
    for rel,h in baseline['files'].items():assert sha(MOD/rel)==h,('Concurrent edit',rel)
    report=[]
    for rel in staged['publish_files']:
        assert rel in baseline['files'];target=MOD/rel;backup=out/'backup'/rel;backup.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(target,backup)
    try:
        for rel in staged['publish_files']:
            source=out/'staged'/rel;target=MOD/rel;shutil.copy2(source,target);assert sha(source)==sha(target)
            report.append({'path':str(target),'before':baseline['files'][rel],'after':sha(target)})
        for rel in baseline['protected']:assert sha(MOD/rel)==baseline['files'][rel]
    except Exception:
        for rel in staged['publish_files']:shutil.copy2(out/'backup'/rel,MOD/rel)
        raise
    (out/'installation.json').write_text(json.dumps({'installed':True,'source_unchanged':True,'assembly_and_wiring_unchanged':True,'files':report},indent=2));print('INSTALLED',len(report),'files; source, AST, ArtDefs and packaging preserved.')
if __name__=='__main__':
    mode,out=sys.argv[1:];{'stage':stage,'install':install}[mode](Path(out))
