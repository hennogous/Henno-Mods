"""Convert validated Storage S/M CN6s, verify native round trips, then install."""
import bpy
import io_export_cn6 as cn6
import hashlib, json, re, shutil, subprocess
import importlib.util
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np

REPO=Path(__file__).resolve().parents[3]
MOD=REPO/'Civ Supply Chains'
OUT=Path(r'C:\Users\Shadow\Desktop\Codex\CSC_Storage_SM\ao-rebake-20261012')
EXPORT=OUT/'production-exports'
LIBS=REPO/'project/tools/cn6libs'

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def run(command,cwd,label):
    result=subprocess.run([str(a) for a in command],cwd=str(cwd),capture_output=True,text=True,
        creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    (EXPORT/(label+'.log')).write_text(result.stdout+result.stderr)
    assert result.returncode==0,(label,result.stdout,result.stderr)
    print(label,result.stdout[-250:],flush=True)

def parse(path):
    text=path.read_text();meshes={}
    for chunk in text.split('mesh:"')[1:]:
        name,body=chunk.split('"',1)
        material,body=body.split('vertices\n',1)
        vertices,body=body.split('triangles\n',1)
        triangles=body.split('\nend')[0].strip()
        meshes[name]=dict(materials=re.findall(r'^"(.*)"$',material,re.M),
            vertices=np.array([[float(x) for x in line.split()[:18]] for line in vertices.strip().splitlines()]),
            triangles=np.array([[int(x) for x in line.split()[:3]] for line in triangles.splitlines()]))
    return meshes

def main():
    EXPORT.mkdir(parents=True,exist_ok=True)
    records=json.loads((OUT/'export-check.json').read_text())
    source_ao=Path(r'C:\Users\Shadow\Desktop\Working Files\3D Art\Textures\CSC_Atlas_AO2.png')
    assert sha(source_ao)==sha(OUT/'CSC_Atlas_AO2.png'),'Shared atlas changed since bake'
    report=[]
    for record in records:
        source=Path(record['source']);original_cn6=Path(record['cn6']);name=source.stem
        assert sha(source)==record['source_sha256'],'Blend changed since checked CN6 export'
        staged=EXPORT/(name+'.cn6');shutil.copy2(original_cn6,staged)
        fgx=EXPORT/(name+'.fgx');geo=EXPORT/(name+'.geo')
        run([LIBS/'CN6ToFGX.exe',staged,fgx,2],LIBS,name+'-convert')
        summaries,vcount,tcount=cn6.csc_write_geo(str(geo),name,str(staged),'LandmarkModel')
        geo.write_text(geo.read_text().replace('AssetObjects:','AssetObjects..'))
        tree=ET.parse(geo)
        assert tree.find('m_ClassName').get('text')=='LandmarkModel'
        roundtrip=EXPORT/(name+'-roundtrip.cn6')
        run([LIBS/'FGXToCN6.exe',fgx,roundtrip],LIBS,name+'-inspect')
        expected=parse(staged);actual=parse(roundtrip)
        assert set(expected)==set(actual),'FGX changed mesh names'
        errors={}
        for mesh,a in expected.items():
            b=actual[mesh]
            # Static LandmarkModel FGX has no material names; runtime groups are
            # defined by the GEO and assigned in AST. The native reader returns
            # an empty list for both the existing and newly converted FGX.
            assert not b['materials'] or a['materials']==b['materials'],(name,mesh,'material groups differ')
            geo_mesh=next(n for n in tree.findall('m_Meshes/Element') if n.find('m_Name').get('text')==mesh)
            assert [g.find('m_Name').get('text') for g in geo_mesh.findall('m_Groups/Element')]==a['materials']
            assert a['vertices'].shape==b['vertices'].shape,(name,mesh,'vertex counts differ')
            assert np.array_equal(a['triangles'],b['triangles']),(name,mesh,'triangles differ')
            residual=np.max(np.abs(a['vertices']-b['vertices']),axis=0)
            assert max(residual)<1e-4,(name,mesh,residual)
            errors[mesh]=dict(vertices=len(a['vertices']),triangles=len(a['triangles']),
                position_error=float(max(residual[:3])),uv1_error=float(max(residual[12:14])),
                uv2_error=float(max(residual[14:16])),uv3_error=float(max(residual[16:18])),groups=a['materials'])
        report.append(dict(name=name,source=str(source),source_sha256=sha(source),meshes=errors,
            vertices=vcount,triangles=tcount,fgx_sha256=sha(fgx),geo_sha256=sha(geo)))
    run([REPO/'project/tools/directxtex/texconv.exe','-f','R8_UNORM','-m','0','-y','-o',EXPORT,source_ao],REPO,'ao-dds')
    dds=EXPORT/'CSC_Atlas_AO2.dds';assert dds.is_file() and dds.stat().st_size>1000000
    # AE's attachment cooker cannot encode texconv's raw R8 header (format 1009).
    # Reuse the scene exporter's established Firaxis header normalization while
    # retaining every rebaked pixel and mip level. Validate before installation.
    spec=importlib.util.spec_from_file_location('csc_scene_export_dds',
        REPO/'project/tools/blender/scene_export/export_scene.py')
    dds_tools=importlib.util.module_from_spec(spec);spec.loader.exec_module(dds_tools)
    texture={'format':'R8_UNORM','size':[1024,1024],'slot':'AO'}
    pixels=dds.read_bytes()[128:]
    dds_tools.normalize_ao_dds(dds,texture,MOD/'Textures/CSC_Atlas_AO.dds')
    dds_tools.validate_dds(dds,texture)
    assert dds.read_bytes()[128:]==pixels,'AO header normalization changed mip pixels'
    backup=EXPORT/'before-install';backup.mkdir(exist_ok=True)
    # Back up every exact destination before any installation.
    copies=[]
    for record in report:
        name=record['name']
        for suffix in ('.fgx','.geo'):
            copies.append((EXPORT/(name+suffix),MOD/'Geometries'/(name+suffix)))
        copies.append((EXPORT/(name+'.cn6'),Path(record['source']).with_suffix('.cn6')))
    copies.append((dds,MOD/'Textures'/dds.name))
    asset=MOD/'Assets/CSC_BAKERS_Storage_S.ast'
    for _,dest in copies:
        if dest.exists():
            target=backup/dest.name
            assert not target.exists(),'Backup already exists; review before repeating install'
            shutil.copy2(dest,target)
    shutil.copy2(asset,backup/asset.name)
    raw=asset.read_bytes()
    pattern=rb'<m_GroupName text="CSC_Storage_S"/>(\s*<m_MeshName text="CSC_Storage_S_Bdg"/>)'
    patched,count=re.subn(pattern,rb'<m_GroupName text="CSC_TAILORS_NE"/>\1',raw)
    assert count==5,('Unexpected Bakers S group binding count',count)
    # Verify this patch only changes group identifiers for the intact mesh.
    assert patched.replace(b'<m_GroupName text="CSC_TAILORS_NE"/>',b'<m_GroupName text="CSC_Storage_S"/>')==raw
    for staged,dest in copies:shutil.copy2(staged,dest)
    asset.write_bytes(patched)
    for staged,dest in copies:assert sha(staged)==sha(dest),'Installed file differs'
    bindings=[]
    groups={r['name']:{mesh:set(data['groups']) for mesh,data in r['meshes'].items()} for r in report}
    for path in MOD.joinpath('Assets').glob('*.ast'):
        body=path.read_text()
        if not any('text="'+name+'"' in body for name in groups):continue
        root=ET.fromstring(body)
        for model in root.iter('Element'):
            geo_name=model.find('m_GeoName')
            if geo_name is None or geo_name.get('text') not in groups:continue
            name=geo_name.get('text');checked=[]
            for state in model.findall('m_GroupStates/Element'):
                mesh=state.find('m_MeshName');group=state.find('m_GroupName')
                if mesh is None or mesh.get('text') not in groups[name]:continue
                assert group.get('text') in groups[name][mesh.get('text')],(path.name,name,mesh.get('text'),group.get('text'))
                material=[]
                for val in state.findall('m_Values/m_Values/Element'):
                    param=val.find('m_ParamName')
                    if param is not None and param.get('text')=='Material':
                        material.append(val.find('m_ObjectName').get('text'))
                for mat in material:
                    if mat.startswith('CSC_'):
                        mtl=MOD/'Materials'/(mat+'.mtl');assert mtl.exists(),mat
                        assert 'CSC_Atlas_AO2' in mtl.read_text(),(mat,'shared AO missing')
                checked.append(dict(mesh=mesh.get('text'),group=group.get('text'),
                    state=state.find('m_StateName').get('text'),materials=material))
            assert checked,(path.name,name,'No real mesh groups bound')
            bindings.append(dict(asset=path.name,geometry=name,states=checked))
    result=dict(models=report,installed=[dict(path=str(dest),sha256=sha(dest)) for _,dest in copies],
        asset_group_binding_patch=dict(path=str(asset),rows=count),bindings=bindings,
        source_blends_unchanged=all(sha(Path(r['source']))==r['source_sha256'] for r in records),
        cooked=False,in_game_tested=False)
    assert result['source_blends_unchanged']
    (EXPORT/'export-install-report.json').write_text(json.dumps(result,indent=2))
    print('STORAGE_SM_EXPORT_INSTALL_PASS',len(copies),'installed files',len(bindings),'asset model bindings',flush=True)

if __name__=='__main__':main()
