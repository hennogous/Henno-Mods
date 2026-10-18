"""Validate Cafe sources/native readback, publish only vacant atlas cells and standalone assets."""
from cafe_atlas import *
import os,math,importlib.util,subprocess,xml.etree.ElementTree as ET
import numpy as np
from PIL import Image,ImageDraw,ImageFont
MOD=ROOT/'Civ Supply Chains'
IDS=['CSC_BAKERS_Cafe_Chair','CSC_BAKERS_Cafe_Counter','CSC_BAKERS_Cafe_Brewing_Set','CSC_BAKERS_Cafe_Pastry_Tray','CSC_BAKERS_Cafe_Table_Service','CSC_BAKERS_Cafe_Reading_Set','CSC_ALL_Garden_Wall_Curve','CSC_ALL_Stage_4_Cobble_Decals','CSC_ALL_Oval_Table','CSC_ALL_Flour_Sack_Closed']
def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def txt(e,p):
    n=e.find(p);return n.get('text',n.text or '') if n is not None else ''
def parse(path):
    chunks=path.read_text().split('mesh:"');assert len(chunks)==2
    name,body=chunks[1].split('"',1);_,body=body.split('vertices\n',1);v,t=body.split('triangles\n',1)
    return name,np.array([[float(x) for x in l.split()[:18]] for l in v.strip().splitlines()]),[[int(x) for x in l.split()] for l in t.split('\nend')[0].strip().splitlines()]
def checks():
    results=[]
    for ident in IDS:
        val=json.loads((OUT/(ident+'-validation.json')).read_text());assert val['automated_pass'] and val['source_sha256']==sha(SOURCE/(ident+'.blend'))
        a,va,ta=parse(OUT/(ident+'.cn6'));b,vb,tb=parse(OUT/(ident+'-roundtrip.cn6'));assert a==b and ta==tb and va.shape==vb.shape
        err=float(np.max(np.abs(va-vb)));assert err<1e-4 and np.isfinite(va).all()
        exp=json.loads((OUT/(ident+'-export.json')).read_text());assert len(va)==exp['vertices']
        ast=ET.parse(OUT/(ident+'.ast'));geo=ET.parse(OUT/(ident+'.geo'))
        assert len(ast.findall('m_GeometrySet/m_ModelInstances/Element'))==1 and len(geo.findall('m_Meshes/Element'))==1
        mat='CSC_ALL_Stage_4_Cobble_Decals' if 'Cobble' in ident else 'CSC_ALL_Props_01'
        for row in ast.findall('.//m_GroupStates/Element'):
            values={txt(e,'m_ParamName'):e for e in row.findall('m_Values/m_Values/Element')}
            assert txt(values['Material'],'m_ObjectName')==mat
            assert txt(values['Visible'],'m_bValue')==str(txt(row,'m_StateName') in ('Worked','Unworked')).lower()
        results.append(dict(asset=ident,vertices=len(va),triangles=len(ta),roundtrip_max_error=err,source_validated=True))
    return results
def atlas():
    baseline=json.loads((OUT/'atlas-baseline.json').read_text());assert json.loads((SHARED/'CURRENT.json').read_text())==baseline['pointer']
    assert all(sha(SHARED/'Current'/p)==h for p,h in baseline['files'].items()),'Live atlas changed since audit'
    for k in 'BNGM':
        a=np.array(Image.open(SHARED/'Current/textures'/f'CSC_Props_Shared_01_{k}.png').convert('RGB'));b=np.array(Image.open(STAGE/'textures'/f'CSC_Props_Shared_01_{k}.png').convert('RGB'));mask=np.ones((1024,1024),bool)
        for slot in range(10,16):x,y=slot%8*128,slot//8*128;mask[y:y+128,x:x+128]=False
        assert np.array_equal(a[mask],b[mask])
    a=np.array(Image.open(SHARED/'Current/textures/CSC_Props_Shared_01_AO.png').convert('RGB'));b=np.array(Image.open(STAGE/'textures/CSC_Props_Shared_01_AO.png').convert('RGB'));mask=np.ones((2048,2048),bool)
    for ident in IDS[:7]:
        x,y,x1,y1=json.loads((OUT/(ident+'-export.json')).read_text())['ao_cell'];mask[y:y1,x:x1]=False
    assert np.array_equal(a[mask],b[mask])
    for p in (STAGE/'textures').glob('*.png'):
        if p.name not in [f'CSC_Props_Shared_01_{k}.png' for k in ['B','N','G','M','AO']]:assert sha(p)==sha(SHARED/'Current/textures'/p.name)
    # Store exact baseline and technical cell images for a byte-reproducible release rebuild.
    base=STAGE/'atlas/sources/cafe-r031-baseline';base.mkdir(exist_ok=True)
    for k in ['B','N','G','M','AO']:shutil.copy2(SHARED/'Current/textures'/f'CSC_Props_Shared_01_{k}.png',base/f'CSC_Props_Shared_01_{k}.png')
    m=json.loads((STAGE/'atlas/manifest.json').read_text())
    for r in m['regions']:
        if r['name'].startswith('cafe_'):
            for k in 'BNGM':
                p=STAGE/'atlas/sources'/f"{r['name']}_{k}_packed.png";Image.open(STAGE/'textures'/f'CSC_Props_Shared_01_{k}.png').crop(r['bounds']).save(p);r['sources'][k]=p.relative_to(STAGE/'atlas').as_posix()
    (STAGE/'atlas/manifest.json').write_text(json.dumps(m,indent=2))
    rebuild='''from pathlib import Path
import json
from PIL import Image
import numpy as np
root=Path(__file__).resolve().parents[1]
m=json.loads((root/'atlas/manifest.json').read_text())
for k in 'BNGM':
 im=Image.open(root/'atlas/sources/cafe-r031-baseline'/('CSC_Props_Shared_01_'+k+'.png')).convert('RGB')
 for r in m['regions']:
  if not r['name'].startswith('cafe_'):continue
  p=Image.open(root/'atlas'/r['sources'][k]).convert('RGB')
  im.paste(Image.fromarray(np.pad(np.array(p),((4,4),(4,4),(0,0)),mode='edge')),(r['slot']%8*128,r['slot']//8*128))
 im.save(root/'textures'/('CSC_Props_Shared_01_'+k+'.png'))
im=Image.open(root/'atlas/sources/cafe-r031-baseline/CSC_Props_Shared_01_AO.png').convert('RGB')
m=json.loads((root/'atlas/quarter-ao-manifest.json').read_text())
family=next(f for f in m['pages'][0]['quarters'][0]['families'] if f['family']=='Stage4')
for a in family['allocations']:im.paste(Image.open(root/a['source']).convert('RGB'),a['cell'][:2])
im.save(root/'textures/CSC_Props_Shared_01_AO.png')
'''
    (STAGE/'scripts/pack_cafe_additions.py').write_text(rebuild)
    hashes={p.name:sha(p) for p in (STAGE/'textures').glob('*.png')};subprocess.run([sys.executable,STAGE/'scripts/pack_cafe_additions.py'],check=True);assert all(sha(STAGE/'textures'/n)==h for n,h in hashes.items())
    lib=json.loads((STAGE/'library.json').read_text());lib.update(release=RELEASE,accepted_on='2026-10-17',content_revision=32,snapshot_path='Releases/'+RELEASE,surface_status='Six ImageGen Cafe surfaces in formerly empty cells10..15. All occupied pixels preserved.',AO_status='Seven isolated Cafe self-AO allocations in previously empty Bakers Stage4. All other AO pixels preserved.',review_status='Saved-source, native conversion and assistant visual checks; AE cook and game review pending.')
    lib['rebuild']['cafe_additions']='python scripts/pack_cafe_additions.py'
    for ident in IDS:lib['source_FINAL_sha256']['BAKERS/Cafe_Regular_20261017/'+ident+'.blend']=sha(SOURCE/(ident+'.blend'))
    lib['files']={p.relative_to(STAGE).as_posix():sha(p) for p in STAGE.rglob('*') if p.is_file() and p.name!='library.json'};(STAGE/'library.json').write_text(json.dumps(lib,indent=2))
    dd=OUT/'dds';dd.mkdir(exist_ok=True);converter=module('cafe_dds',ROOT/'project/tools/blender/scene_export/export_scene.py')
    for k in ['B','N','G','M','AO']:
        name='CSC_Props_Shared_01_'+k;fmt=ET.parse(MOD/'Textures'/(name+'.tex')).findtext('m_ExportSettings/ePixelformat').removeprefix('PF_');size=list(Image.open(STAGE/'textures'/(name+'.png')).size)
        args=[str(ROOT/'project/tools/directxtex/texconv.exe'),'-nologo','-y','-m','0','-f',fmt,'-o',str(dd),'--ignore-srgb']+(['-srgb'] if k=='B' else [])+[str(STAGE/'textures'/(name+'.png'))]
        r=subprocess.run(args,capture_output=True,text=True);assert r.returncode==0;(OUT/(name+'-dds.log')).write_text(r.stdout+r.stderr);spec=dict(format=fmt,size=size,slot=k)
        if fmt=='R8_UNORM':converter.normalize_ao_dds(dd/(name+'.dds'),spec,MOD/'Textures/CSC_Props_Shared_01_AO.dds')
        converter.validate_dds(dd/(name+'.dds'),spec)
def install(results):
    backup=OUT/'before-install';backup.mkdir(exist_ok=True);protected={p:sha(p) for p in (MOD/'Assets').glob('*.ast')}
    (backup/'existing-assets-sha256.json').write_text(json.dumps({str(p):h for p,h in protected.items()},indent=2))
    copies=[]
    for ident in IDS:
        for folder,ext in [('Assets','.ast'),('Geometries','.geo'),('Geometries','.fgx')]:
            target=MOD/folder/(ident+ext);src=OUT/(ident+ext);assert not target.exists() or sha(target)==sha(src),'Existing asset differs: '+str(target);copies.append((src,target))
    for p in (OUT/'dds').glob('*.dds'):copies.append((p,MOD/'Textures'/p.name))
    # Reuse the user's exact square artwork; a new material leaves the old Stage3 layout mask alone.
    material_id='CSC_ALL_Stage_4_Cobble_Decals';mtl=ET.parse(MOD/'Materials/CSC_ALL_Stage_3_Cobbles_Sq.mtl')
    mtl.find('m_Name').set('text',material_id);mtl.find('m_Description').set('text','L3-aligned courtyard; existing square cobbles with feathered layout alpha.')
    for v in mtl.findall('m_CookParams/m_Values/Element'):
        if txt(v,'m_ParamName')=='Heightmap':v.find('m_ObjectName').set('text','CSC_ALL_Stage_4_Cobbles_H' if (MOD/'Textures/CSC_ALL_Stage_4_Cobbles_H.tex').exists() else '')
        if txt(v,'m_ParamName')=='BaseColor':v.find('m_ObjectName').set('text','CSC_ALL_Stage_4_Cobbles_B')
    ET.indent(mtl,space='  ');mtl.write(OUT/(material_id+'.mtl'),encoding='utf-8',xml_declaration=True)
    target=MOD/'Materials'/(material_id+'.mtl');assert not target.exists() or sha(target)==sha(OUT/(material_id+'.mtl'));copies.append((OUT/(material_id+'.mtl'),target))
    name='CSC_ALL_Stage_4_Cobbles_B';tex=ET.parse(MOD/'Textures/CSC_ALL_Stage_3_Cobbles_Sq_B.tex');tex.find('m_Name').set('text',name);tex.find('m_SourceFilePath').set('text',str(SOURCE/'textures'/(name+'.png')));tex.find('m_DataFiles/Element/m_RelativePath').set('text',name+'.dds');tex.write(OUT/(name+'.tex'),encoding='utf-8',xml_declaration=True)
    size=list(Image.open(SOURCE/'textures'/(name+'.png')).size)
    tex.find('m_Width').text=str(size[0]);tex.find('m_Height').text=str(size[1]);tex.find('m_NumMipMaps').text=str(int(math.log2(max(size))))
    tex.write(OUT/(name+'.tex'),encoding='utf-8',xml_declaration=True)
    r=subprocess.run([str(ROOT/'project/tools/directxtex/texconv.exe'),'-nologo','-y','-m','0','-f','R8G8B8A8_UNORM','-o',str(OUT),'--ignore-srgb','-srgb',str(SOURCE/'textures'/(name+'.png'))],capture_output=True,text=True);assert r.returncode==0
    converter=module('cafe_decal_dds',ROOT/'project/tools/blender/scene_export/export_scene.py');converter.validate_dds(OUT/(name+'.dds'),dict(format='R8G8B8A8_UNORM',size=size,slot='B'))
    for ext in ['.tex','.dds']:
        target=MOD/'Textures'/(name+ext);assert not target.exists() or sha(target)==sha(OUT/(name+ext));copies.append((OUT/(name+ext),target))
    xlp=MOD/'XLPs/CSC_Tilebases.xlp';raw=xlp.read_bytes();updated=raw
    for ident in IDS:
        if ident.encode() not in updated:
            assert updated.count(b'\t</m_Entries>')==1
            updated=updated.replace(b'\t</m_Entries>',f'\t\t<Element>\n\t\t\t<m_EntryID text="{ident}"/>\n\t\t\t<m_ObjectName text="{ident}"/>\n\t\t</Element>\n\t</m_Entries>'.encode())
    ET.fromstring(updated)
    for src,dest in copies:
        if dest.exists():shutil.copy2(dest,backup/dest.name)
        tmp=dest.with_name(dest.name+'.cafe-tmp');shutil.copy2(src,tmp);os.replace(tmp,dest)
    shutil.copy2(xlp,backup/xlp.name);xlp.write_bytes(updated)
    release=SHARED/'Releases'/RELEASE;assert not release.exists();shutil.copy2(SHARED/'CURRENT.json',backup/'CURRENT.json');shutil.copytree(STAGE,release);shutil.copytree(STAGE,SHARED/'Current',dirs_exist_ok=True)
    (SHARED/'CURRENT.json').write_text(json.dumps(dict(release=RELEASE,current='Current',manifest='Current/library.json',snapshot='Releases/'+RELEASE,updated_on='2026-10-17',library_sha256=sha(SHARED/'Current/library.json')),indent=2))
    assert all(sha(p)==h for p,h in protected.items())
    # AE may regenerate DDS headers/mip chains when Current is updated; verify pixels in that case.
    from verify_cafe_install import decode_top
    for src,dest in copies:
        if sha(src)!=sha(dest):
            assert src.suffix=='.dds' and np.array_equal(decode_top(src),decode_top(dest)),str(dest)
    entries=ET.parse(xlp).findall('m_Entries/Element');assert all(sum(txt(e,'m_EntryID')==ident for e in entries)==1 for ident in IDS)
    report=dict(release=RELEASE,assets=results,source_directory=str(SOURCE),existing_ae_assemblies_bytewise_preserved=len(protected),surface_slots=list(range(10,16)),occupied_surface_pixels_preserved=True,other_AO_pixels_preserved=True,opacity_emission_sheet02_unchanged=True,atlas_rebuild_hashes_match=True,installed=True,cook_tested=False,in_game_tested=False,placement='Review proposal only; AE owns final positions and duplicates.')
    (OUT/'install-report.json').write_text(json.dumps(report,indent=2));print('CAFE PUBLISHED',RELEASE,flush=True)
def contact():
    canvas=Image.new('RGB',(1500,1080),(238,233,221));d=ImageDraw.Draw(canvas)
    for i,ident in enumerate(IDS):
        tile=Image.open(OUT/(ident+'-preview.png')).convert('RGBA');tile.thumbnail((280,440));x=(i%5)*300+(300-tile.width)//2;y=(i//5)*540+20;canvas.paste(tile,(x,y),tile)
        label=ident.removeprefix('CSC_BAKERS_Cafe_').removeprefix('CSC_ALL_').replace('_',' ');d.text(((i%5)*300+12,(i//5)*540+490),label,fill=(45,39,31))
    canvas.save(OUT/'Cafe_Prop_Contact_Sheet.png')
if __name__=='__main__':
    results=checks();(OUT/'native-verification.json').write_text(json.dumps(results,indent=2));contact()
    if '--install' in sys.argv:atlas();install(results)
    print(json.dumps(results,indent=2))
