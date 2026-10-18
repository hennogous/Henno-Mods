"""Derive and install a registered Cafe decal height map using the existing AE contract."""
import os,sys,json,shutil,subprocess,time,copy
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image,ImageFilter
from cafe_atlas import ROOT,SOURCE,sha
from publish_cafe_props import module
from publish_cafe_courtyard import rgba_dds

OUT=Path(os.environ.get('CSC_CAFE_HEIGHT_OUTPUT','C:/Users/Shadow/Desktop/Codex/Cafe/revision-07-heightmap'))
MOD=ROOT/'Civ Supply Chains'
ID='CSC_ALL_Stage_4_Cobble_Decals'
NAME='CSC_ALL_Stage_4_Cobbles_H'
CACHE=Path(os.environ['APPDATA'])/'AssetCloud/mod-Civ Supply Chains-asset-deps.json'

def main():
    OUT.mkdir(parents=True,exist_ok=True);backup=OUT/'before-install';backup.mkdir(exist_ok=True)
    material=MOD/'Materials'/(ID+'.mtl');mat_before=material.read_bytes()
    for folder,extensions in [(MOD/'Textures',['.tex','.dds']),(SOURCE/'textures',['.png','.dds'])]:
        for ext in extensions:
            old=folder/(NAME+ext)
            if old.exists():shutil.copy2(old,backup/(('source-' if folder==SOURCE/'textures' else 'runtime-')+old.name))
    shutil.copy2(material,backup/material.name)
    protected=list((MOD/'Assets').glob('*.ast'))+[MOD/'Geometries'/(ID+e) for e in ['.geo','.fgx']]
    protected += [MOD/'Textures'/('CSC_ALL_Stage_4_Cobbles_B'+e) for e in ['.tex','.dds']]
    protected += [SOURCE/(ID+'.blend'),SOURCE/'textures/CSC_ALL_Stage_4_Cobbles_B.png']
    protected={str(p):sha(p) for p in protected}
    src=SOURCE/'textures/CSC_ALL_Stage_4_Cobbles_B.png';base=Image.open(src).convert('RGBA');a=np.array(base);assert base.size==(512,512)
    # Local closing suppresses the stones' buff/grey colour differences. Only dark
    # grooves and restrained fine surface relief are interpreted as recesses.
    luma=base.convert('RGB').convert('L').filter(ImageFilter.GaussianBlur(.35))
    closing=luma.filter(ImageFilter.MaxFilter(7)).filter(ImageFilter.MinFilter(7))
    recess=np.clip((np.array(closing,dtype=float)-np.array(luma,dtype=float)-2)/22,0,1)
    height=np.uint8(np.rint(99-13*recess))
    height=np.asarray(Image.fromarray(height).filter(ImageFilter.GaussianBlur(.4))).copy()
    height[a[:,:,3]==0]=86
    rgba=np.dstack([height,height,height,a[:,:,3]])
    assert np.array_equal(rgba[:,:,3],a[:,:,3]) and height.min()>=86 and height.max()<=99
    source_h=SOURCE/'textures'/(NAME+'.png');Image.fromarray(rgba).save(source_h)
    contrast=np.uint8(np.clip((height.astype(float)-86)/13*255,0,255));Image.fromarray(contrast).save(OUT/'Height_Contrast_Preview.png')
    shutil.copy2(source_h,OUT/source_h.name)
    result=subprocess.run([str(ROOT/'project/tools/directxtex/texconv.exe'),'-nologo','-y','-m','0','-f','R8G8B8A8_UNORM','--ignore-srgb','-if','CUBIC','-o',str(OUT),str(source_h)],capture_output=True,text=True)
    (OUT/'dds-export.log').write_text(result.stdout+result.stderr);assert result.returncode==0,result.stdout+result.stderr
    dds=OUT/(NAME+'.dds');conv=module('cafe_height_dds',ROOT/'project/tools/blender/scene_export/export_scene.py')
    conv.validate_dds(dds,dict(format='R8G8B8A8_UNORM',size=[512,512],slot='H'))
    assert np.array_equal(rgba_dds(dds),rgba),'Height or alpha changed in DDS export'
    source_dds=SOURCE/'textures'/(NAME+'.dds');shutil.copy2(dds,source_dds)
    template=MOD/'Textures/CSC_ALL_Stage_3_Cobbles_Sq_H.tex';tex=ET.parse(template)
    tex.find('m_Name').set('text',NAME);tex.find('m_SourceFilePath').set('text',str(source_dds));tex.find('m_DataFiles/Element/m_RelativePath').set('text',NAME+'.dds')
    for tag,value in [('m_Height','512'),('m_Width','512'),('m_NumMipMaps','9'),('m_ExportedTime','0')]:tex.find(tag).text=value
    tex.find('m_Description').set('text','Registered warm limestone relief; RGB heights86..99, base-colour alpha copied exactly. Original square-cobble height settings preserved.')
    tex.write(OUT/(NAME+'.tex'),encoding='utf-8',xml_declaration=True)
    mat=ET.ElementTree(ET.fromstring(mat_before));values=mat.findall('m_CookParams/m_Values/Element')
    slot=next(e for e in values if e.find('m_ParamName').get('text')=='Heightmap');assert slot.find('m_ObjectName').get('text') in ['',NAME]
    slot.find('m_ObjectName').set('text',NAME);mat.write(OUT/(ID+'.mtl'),encoding='utf-8',xml_declaration=True)
    assert material.read_bytes()==mat_before,'Material changed while staging'
    for ext in ['.tex','.dds']:shutil.copy2(OUT/(NAME+ext),MOD/'Textures'/(NAME+ext))
    shutil.copy2(OUT/(ID+'.mtl'),material)
    # Register the new texture and dependency without rebuilding other cache records.
    raw=CACHE.read_bytes();cache=json.loads(raw.decode('utf-8-sig'));(backup/'asset-deps.json').write_bytes(raw)
    texture_key=(MOD/'Textures'/(NAME+'.tex')).relative_to(ROOT).as_posix();material_key=material.relative_to(ROOT).as_posix()
    templates={r['Filename']:r for r in cache['Files']}
    row=copy.deepcopy(templates['Civ Supply Chains/Textures/CSC_ALL_Stage_3_Cobbles_Sq_H.tex'])
    row.update(Filename=texture_key,Stats={'Height':512,'Width':512,'Depth':1,'Mip Count':9})
    for key,path,record in [(texture_key,MOD/'Textures'/(NAME+'.tex'),row),(material_key,material,copy.deepcopy(templates[material_key]))]:
        record.update(Timestamp=int(path.stat().st_mtime*10000000)+116444736000000000,Filesize=path.stat().st_size,Status=0)
        existing=next((r for r in cache['Files'] if r['Filename']==key),None)
        if existing:existing.update(record)
        else:cache['Files'].append(record)
    cache['Dependencies'][texture_key]=[str(source_dds),(MOD/'Textures'/(NAME+'.dds')).relative_to(ROOT).as_posix()]
    cache['Dependencies'][material_key]=sorted(set(cache['Dependencies'].get(material_key,[])+[texture_key]))
    cache['Timestamp']=int(time.time()*10000000)+116444736000000000
    assert CACHE.read_bytes()==raw,'AE cache changed while registering; retain runtime files and retry cache only'
    CACHE.write_text(json.dumps(cache,separators=(',',':')))
    assert np.array_equal(rgba_dds(MOD/'Textures'/(NAME+'.dds')),rgba)
    now=ET.parse(material);assert next(e for e in now.findall('m_CookParams/m_Values/Element') if e.find('m_ParamName').get('text')=='Heightmap').find('m_ObjectName').get('text')==NAME
    assert all(sha(p)==h for p,h in protected.items()),'Protected model/layout/colour changed'
    report=dict(material=ID,height_texture=NAME,installed=True,size=[512,512],RGB_range=[int(height.min()),int(height.max())],alpha_identical_to_base=True,DDS_exact_RGBA=True,
        source=str(source_h),source_DDS=str(source_dds),base_sha256=sha(src),settings_template=str(template),cache_registered=True,geometry_assembly_basecolour_preserved=True,AE_visual_review=False,
        derivation='Technical local closing minus luminance detects recessed mortar while suppressing broad stone colour differences; height constrained to existing86..99 range. No new artwork.')
    (OUT/'install-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))

if __name__=='__main__':main()
