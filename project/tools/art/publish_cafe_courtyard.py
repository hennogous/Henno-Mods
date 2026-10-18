"""Focused, backed-up replacement of the Cafe courtyard; preserve AE assemblies."""
from cafe_atlas import *
import subprocess, struct, xml.etree.ElementTree as ET
import numpy as np
from PIL import Image
ID='CSC_ALL_Stage_4_Cobble_Decals'
TEX='CSC_ALL_Stage_4_Cobbles_B'
MOD=ROOT/'Civ Supply Chains'
CAT=ART/'Props/CSC_Prop_Library/catalogue.json'

def prepare():
    OUT.mkdir(parents=True,exist_ok=True)
    backup=OUT/'before-fix';backup.mkdir(exist_ok=False)
    files=[SOURCE/(ID+'.blend'),SOURCE/'textures'/(TEX+'.png'),CAT,
           MOD/'Geometries'/(ID+'.geo'),MOD/'Geometries'/(ID+'.fgx'),
           MOD/'Materials'/(ID+'.mtl'),MOD/'Textures'/(TEX+'.tex'),MOD/'Textures'/(TEX+'.dds')]
    for p in files:shutil.copy2(p,backup/p.name)
    protected=list((MOD/'Assets').glob('*.ast'))+list((MOD/'XLPs').glob('*.xlp'))
    protected += [p for p in (SHARED/'Current').rglob('*') if p.is_file()]+[SHARED/'CURRENT.json']
    (OUT/'baseline.json').write_text(json.dumps(dict(files={str(p):sha(p) for p in files},protected={str(p):sha(p) for p in protected}),indent=2))
    print('Backed up previous master, texture, runtime files and catalogue.')

def rgba_dds(path):
    raw=path.read_bytes();h,w=struct.unpack_from('<II',raw,12)
    _,flags,fourcc,bits,r,g,b,a=struct.unpack_from('<8I',raw,76)
    if raw[84:88]==b'DX10':
        assert struct.unpack_from('<I',raw,128)[0] in [28,29]
        return np.frombuffer(raw[148:148+w*h*4],np.uint8).reshape(h,w,4)
    assert bits==32 and a!=0
    pixels=np.frombuffer(raw[128:128+w*h*4],'<u4').reshape(h,w)
    return np.stack([((pixels&mask)>>((mask&-mask).bit_length()-1)).astype(np.uint8) for mask in [r,g,b,a]],axis=-1)

def install():
    import publish_cafe_props as P
    P.IDS=[ID];results=P.checks()
    baseline=json.loads((OUT/'baseline.json').read_text())
    protected_now={p:sha(p) for p in baseline['protected']}
    concurrent_saves=[p for p,h in baseline['protected'].items() if protected_now[p]!=h]
    # A user can save another AE assembly while this decal is being rendered.
    # Those ASTs are outside this publisher's write set: preserve their latest bytes.
    assert all(Path(p).parent==MOD/'Assets' and Path(p).stem!=ID for p in concurrent_saves),'Protected atlas/XLP/decal changed; reassess before install.'
    expected=np.asarray(Image.open(SOURCE/'textures'/(TEX+'.png')).convert('RGBA'))
    for p,h in baseline['files'].items():
        if p in [str(SOURCE/(ID+'.blend')),str(SOURCE/'textures'/(TEX+'.png'))] or sha(p)==h:continue
        path=Path(p)
        if path==MOD/'Textures'/(TEX+'.dds'):
            assert np.max(np.abs(rgba_dds(path).astype(int)-expected.astype(int)))<=1
        elif path==MOD/'Textures'/(TEX+'.tex'):
            before=ET.parse(OUT/'before-fix'/path.name);after=ET.parse(path)
            # The active AE watcher legitimately rewrites dimensions, time and formatting.
            for key in ['m_Height','m_Width','m_NumMipMaps','m_ExportedTime']:
                before.find(key).text=after.find(key).text='watcher'
            def semantic(root):return [(e.tag,(e.text or '').strip(),e.attrib) for e in root.iter()]
            assert semantic(before)==semantic(after),'Unexpected texture settings changed'
        else:raise AssertionError(p)
        shutil.copy2(path,OUT/('watcher-before-install-'+path.name))
    # The mesh/group names are unchanged, so retain the existing standalone AST as well.
    def groups(p):return [(P.txt(e,'m_MeshName'),P.txt(e,'m_GroupName'),P.txt(e,'m_StateName')) for e in ET.parse(p).findall('.//m_GroupStates/Element')]
    assert groups(OUT/(ID+'.ast'))==groups(MOD/'Assets'/(ID+'.ast'))
    material=ET.parse(MOD/'Materials'/(ID+'.mtl'))
    material.find('m_Description').set('text','L3-aligned courtyard; warm ImageGen limestone, shared atlas slot31 source, preserved feathered layout alpha.')
    material.write(OUT/(ID+'.mtl'),encoding='utf-8',xml_declaration=True)
    tex=ET.parse(MOD/'Textures'/(TEX+'.tex'))
    for key,val in [('m_Width','512'),('m_Height','512'),('m_NumMipMaps','9')]:tex.find(key).text=val
    tex.find('m_Description').set('text','Warm ImageGen limestone registered to facade; courtyard alpha unchanged, 7-unit inward feather.')
    tex.write(OUT/(TEX+'.tex'),encoding='utf-8',xml_declaration=True)
    r=subprocess.run([str(ROOT/'project/tools/directxtex/texconv.exe'),'-nologo','-y','-m','0','-f','R8G8B8A8_UNORM','-o',str(OUT),'--ignore-srgb','-srgb',str(SOURCE/'textures'/(TEX+'.png'))],capture_output=True,text=True)
    (OUT/'texture-export.log').write_text(r.stdout+r.stderr);assert r.returncode==0
    converter=P.module('courtyard_dds',ROOT/'project/tools/blender/scene_export/export_scene.py')
    converter.validate_dds(OUT/(TEX+'.dds'),dict(format='R8G8B8A8_UNORM',size=[512,512],slot='B'))
    actual=rgba_dds(OUT/(TEX+'.dds'));assert np.max(np.abs(actual.astype(int)-expected.astype(int)))<=1
    assert np.array_equal(actual[:,:,3],expected[:,:,3])
    copies=[(OUT/(ID+ext),MOD/folder/(ID+ext)) for ext,folder in [('.geo','Geometries'),('.fgx','Geometries'),('.mtl','Materials')]]
    copies += [(OUT/(TEX+ext),MOD/'Textures'/(TEX+ext)) for ext in ['.tex','.dds']]
    for src,dst in copies:
        tmp=dst.with_name(dst.name+'.courtyard-tmp');shutil.copy2(src,tmp);os.replace(tmp,dst)
    cat=json.loads(CAT.read_text());entry=next(a for a in cat['assets'] if a['asset_id']==ID)
    from cafe_courtyard import BOUNDS
    entry.update(dimensions=[BOUNDS[2]-BOUNDS[0],BOUNDS[3]-BOUNDS[1],0],blend_sha256=sha(SOURCE/(ID+'.blend')),pivot='Generic L3 coordinate frame; attach at position/rotation zero, scale one.',reuse_notes='512px feathered courtyard. Cobble rows aligned to facade; screen-right paving reaches road, rear depth halved. Rectangular support is fully transparent outside courtyard.',verification=results[0])
    CAT.write_text(json.dumps(cat,indent=2))
    assert all(sha(p)==h for p,h in protected_now.items())
    assert all(sha(src)==sha(dst) for src,dst in copies)
    assert np.array_equal(rgba_dds(MOD/'Textures'/(TEX+'.dds'))[:,:,3],expected[:,:,3])
    report=dict(assets=results,installed=True,texture_size=[512,512],dds_rgba_max_error=int(np.max(np.abs(actual.astype(int)-expected.astype(int)))),dds_alpha_exact=True,
                protected_assets_xlps_atlas_preserved=True,concurrent_ae_assembly_saves_preserved=concurrent_saves,source_directory=str(SOURCE),default_position=[0,0,0],default_rotation=[0,0,0],default_scale=1,
                placement='Geometry now shares generic L3 baked XY frame. Existing attachment edits were not changed.',
                cook_tested=False,in_game_tested=False)
    (OUT/'install-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))

if __name__=='__main__':
    if sys.argv[1]=='prepare':prepare()
    elif sys.argv[1]=='install':install()
