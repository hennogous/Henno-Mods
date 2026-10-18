"""Install only fitted B/H texture pixels; retain relocated source and AE edits."""
import json,shutil,subprocess,xml.etree.ElementTree as ET
import numpy as np
from PIL import Image,ImageFilter
from pathlib import Path
from cafe_atlas import ROOT,OUT,sha,SHARED
from publish_cafe_courtyard import rgba_dds
from publish_cafe_props import module
MOD=ROOT/'Civ Supply Chains';ID='CSC_ALL_Stage_4_Cobble_Decals'

def main():
    job=json.loads((OUT/'ae-job.json').read_text());backup=OUT/'before-install';backup.mkdir(exist_ok=True)
    paths={};tex_hash={}
    for k in 'BH':
        name='CSC_ALL_Stage_4_Cobbles_'+k;tex=MOD/'Textures'/(name+'.tex');tree=ET.parse(tex)
        paths[k]=Path(tree.find('m_SourceFilePath').get('text'));assert paths[k].suffix=='.png'
        assert tree.findtext('m_ExportSettings/ePixelformat')=='PF_R8G8B8A8_UNORM'
        for p in [tex,MOD/'Textures'/(name+'.dds'),paths[k]]:shutil.copy2(p,backup/(('source-' if p==paths[k] else '')+p.name))
        tex_hash[k]=sha(tex)
    assert sha(paths['B'])==sha(OUT/'before-fix/CSC_ALL_Stage_4_Cobbles_B.png'),'Active source changed during fitting'
    mat=MOD/'Materials'/(ID+'.mtl');values=ET.parse(mat).findall('m_CookParams/m_Values/Element')
    assert next(e for e in values if e.find('m_ParamName').get('text')=='Heightmap').find('m_ObjectName').get('text')=='CSC_ALL_Stage_4_Cobbles_H'
    protected=[p for p in MOD.glob('Assets/*.ast')]+[p for p in MOD.glob('XLPs/*.xlp')]+[MOD/'Geometries'/(ID+e) for e in ['.fgx','.geo']]+[mat,paths['B'].parent/(ID+'.blend'),SHARED/'CURRENT.json']
    protected += list((SHARED/'Current').rglob('*.png'))
    hashes={str(p):sha(p) for p in protected}
    import sys
    sys.path.insert(0,str(ROOT/'project/tools/blender'))
    import render_ae_asset as R
    resolver=R.Resolver(MOD,R.DEFAULT_SDK);current=R.Assembly(resolver);current.is_decal=lambda ident,near:False;current.asset(Path(job['root']))
    old=job['assets'][job['root']];new=current.assets[job['root']]
    assert old['models']==new['models'],'Building/decal/road models changed during fitting'
    walls=lambda a:[x for x in a['attachments'] if Path(x['asset']).stem=='CSC_ALL_Stage_4_Wall']
    assert walls(old)==walls(new),'Wall assembly placement changed during fitting'
    wall_key=walls(old)[0]['asset'];assert current.assets[wall_key]==job['assets'][wall_key],'Wall sections changed during fitting'
    base=Image.open(OUT/'CSC_ALL_Stage_4_Cobbles_B.png').convert('RGBA');a=np.array(base)
    luma=base.convert('RGB').convert('L').filter(ImageFilter.GaussianBlur(.35));closing=luma.filter(ImageFilter.MaxFilter(7)).filter(ImageFilter.MinFilter(7))
    recess=np.clip((np.array(closing,dtype=float)-np.array(luma,dtype=float)-2)/22,0,1)
    h=np.asarray(Image.fromarray(np.uint8(np.rint(99-13*recess))).filter(ImageFilter.GaussianBlur(.4))).copy();h[a[:,:,3]==0]=86
    height=np.dstack([h,h,h,a[:,:,3]]);Image.fromarray(height).save(OUT/'CSC_ALL_Stage_4_Cobbles_H.png')
    converter=module('wall_fit_dds',ROOT/'project/tools/blender/scene_export/export_scene.py')
    for k,expected in [('B',a),('H',height)]:
        name='CSC_ALL_Stage_4_Cobbles_'+k
        command=[str(ROOT/'project/tools/directxtex/texconv.exe'),'-nologo','-y','-m','0','-f','R8G8B8A8_UNORM','--ignore-srgb','-o',str(OUT)]+(['-srgb'] if k=='B' else [])+[str(OUT/(name+'.png'))]
        r=subprocess.run(command,capture_output=True,text=True);(OUT/(k+'-dds.log')).write_text(r.stdout+r.stderr);assert r.returncode==0
        converter.validate_dds(OUT/(name+'.dds'),dict(format='R8G8B8A8_UNORM',size=[512,512],slot=k))
        assert np.array_equal(rgba_dds(OUT/(name+'.dds')),expected)
    for p,hsh in hashes.items():assert sha(p)==hsh,'Protected source changed: '+p
    for k in 'BH':
        name='CSC_ALL_Stage_4_Cobbles_'+k
        shutil.copy2(OUT/(name+'.png'),paths[k]);shutil.copy2(OUT/(name+'.dds'),MOD/'Textures'/(name+'.dds'))
    for p,hsh in hashes.items():assert sha(p)==hsh,'Protected source changed: '+p
    for k,expected in [('B',a),('H',height)]:assert np.array_equal(rgba_dds(MOD/'Textures'/('CSC_ALL_Stage_4_Cobbles_'+k+'.dds')),expected)
    report=dict(installed=True,changed_files=[str(paths[k]) for k in 'BH']+[str(MOD/'Textures'/('CSC_ALL_Stage_4_Cobbles_'+k+'.dds')) for k in 'BH'],
                source_master=str(paths['B'].parent/(ID+'.blend')),base_RGB_unchanged=True,height_alpha_matches_base=True,DDS_exact_RGBA=True,
                ASTs_geometry_blend_material_XLPs_shared_atlas_unchanged=True,protected_hashes=hashes,road_clearance_world_units=5,AE_visual_review=False)
    (OUT/'install-report.json').write_text(json.dumps(report,indent=2));print('Installed B/H texture fit; all placements, native geometry, master and atlas preserved.')

if __name__=='__main__':main()
