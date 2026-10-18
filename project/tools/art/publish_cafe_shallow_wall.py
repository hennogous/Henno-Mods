"""Publish the additional shallow segment and its isolated AO cell only."""
import os
os.environ['CSC_CAFE_OUTPUT']='C:/Users/Shadow/Desktop/Codex/Cafe/revision-03-shallow-wall'
os.environ['CSC_CAFE_RELEASE']='2026-10-17_Shared_01_r033'
import publish_cafe_props as P
from publish_cafe_props import *
from verify_cafe_install import decode_top
ID='CSC_ALL_Garden_Wall_Curve_2';P.IDS=[ID]
def main():
    results=P.checks();previous=json.loads((SHARED/'CURRENT.json').read_text());assert previous==json.loads((OUT/'baseline-CURRENT.json').read_text())
    oldlib=json.loads((SHARED/'Current/library.json').read_text());assert all(sha(SHARED/'Current'/p)==h for p,h in oldlib['files'].items())
    for p in (STAGE/'textures').glob('*.png'):
        if p.name!='CSC_Props_Shared_01_AO.png':assert sha(p)==sha(SHARED/'Current/textures'/p.name)
    before=np.array(Image.open(SHARED/'Current/textures/CSC_Props_Shared_01_AO.png').convert('RGB'));after=np.array(Image.open(STAGE/'textures/CSC_Props_Shared_01_AO.png').convert('RGB'));mask=np.ones((2048,2048),bool);mask[640:768,384:512]=False;assert np.array_equal(before[mask],after[mask])
    hashes={p.name:sha(p) for p in (STAGE/'textures').glob('*.png')};subprocess.run([sys.executable,STAGE/'scripts/pack_cafe_additions.py'],check=True);assert all(sha(STAGE/'textures'/n)==h for n,h in hashes.items())
    lib=json.loads((STAGE/'library.json').read_text());lib.update(release=RELEASE,content_revision=33,snapshot_path='Releases/'+RELEASE,AO_status='Additional 15-degree shared wall: isolated AO cell384,640–512,768. All previous AO and surface pixels unchanged.');lib['source_FINAL_sha256']['BAKERS/Cafe_Regular_20261017/'+ID+'.blend']=sha(SOURCE/(ID+'.blend'));lib['files']={p.relative_to(STAGE).as_posix():sha(p) for p in STAGE.rglob('*') if p.is_file() and p.name!='library.json'};(STAGE/'library.json').write_text(json.dumps(lib,indent=2))
    backup=OUT/'before-install';backup.mkdir(exist_ok=True);protected={p:sha(p) for p in (MOD/'Assets').glob('*.ast')};(backup/'existing-assets-sha256.json').write_text(json.dumps({str(p):h for p,h in protected.items()},indent=2))
    name='CSC_Props_Shared_01_AO';fmt=ET.parse(MOD/'Textures'/(name+'.tex')).findtext('m_ExportSettings/ePixelformat').removeprefix('PF_')
    r=subprocess.run([str(ROOT/'project/tools/directxtex/texconv.exe'),'-nologo','-y','-m','0','-f',fmt,'-o',str(OUT),'--ignore-srgb',str(STAGE/'textures'/(name+'.png'))],capture_output=True,text=True);assert r.returncode==0
    converter=module('shallow_wall_dds',ROOT/'project/tools/blender/scene_export/export_scene.py');spec=dict(format=fmt,size=[2048,2048],slot='AO');converter.normalize_ao_dds(OUT/(name+'.dds'),spec,MOD/'Textures'/(name+'.dds'));converter.validate_dds(OUT/(name+'.dds'),spec)
    for folder,ext in [('Assets','.ast'),('Geometries','.geo'),('Geometries','.fgx')]:
        target=MOD/folder/(ID+ext);assert not target.exists();shutil.copy2(OUT/(ID+ext),target)
    target=MOD/'Textures'/(name+'.dds');shutil.copy2(target,backup/target.name);shutil.copy2(OUT/(name+'.dds'),target)
    xlp=MOD/'XLPs/CSC_Tilebases.xlp';raw=xlp.read_bytes();assert ID.encode() not in raw and raw.count(b'\t</m_Entries>')==1;shutil.copy2(xlp,backup/xlp.name);xlp.write_bytes(raw.replace(b'\t</m_Entries>',f'\t\t<Element>\n\t\t\t<m_EntryID text="{ID}"/>\n\t\t\t<m_ObjectName text="{ID}"/>\n\t\t</Element>\n\t</m_Entries>'.encode()))
    release=SHARED/'Releases'/RELEASE;assert not release.exists();shutil.copytree(STAGE,release);shutil.copytree(STAGE,SHARED/'Current',dirs_exist_ok=True);(SHARED/'CURRENT.json').write_text(json.dumps(dict(release=RELEASE,current='Current',manifest='Current/library.json',snapshot='Releases/'+RELEASE,updated_on='2026-10-17',library_sha256=sha(SHARED/'Current/library.json')),indent=2))
    assert all(sha(p)==h for p,h in protected.items())
    assert np.array_equal(decode_top(MOD/'Textures'/(name+'.dds')),np.array(Image.open(STAGE/'textures'/(name+'.png')).convert('L')))
    path=ART/'Props/CSC_Prop_Library/catalogue.json';shutil.copy2(path,backup/path.name);catalogue=json.loads(path.read_text());assert not any(a['asset_id']==ID for a in catalogue['assets']);exp=json.loads((OUT/(ID+'-export.json')).read_text());lo,hi=exp['bounds'];relative='../Bakers/Cafe_Regular_20261017/'+ID+'.blend'
    catalogue['assets'].append(dict(asset_id=ID,source_pack='CSC',origin='authored_blender',blend_path=relative,blend_file=relative,export_scene='Export',dimensions=[b-a for a,b in zip(lo,hi)],registration_status='installed_native_assets',reuse_scope='shared',reuse_approved=True,status='verified_blender_and_native',blend_sha256=sha(SOURCE/(ID+'.blend')),reuse_notes='15-degree bend, radius192, same arc length/height/thickness/stone as original30-degree segment; own ground pivot and self-AO.',verification=results[0]));path.write_text(json.dumps(catalogue,indent=2))
    report=dict(asset=ID,source=str(SOURCE/(ID+'.blend')),design=json.loads((OUT/'wall-design.json').read_text()),native=results,atlas_release=RELEASE,AO_cell=[384,640,512,768],all_other_atlas_pixels_preserved=True,old_assets_preserved=len(protected),installed=True,cook_tested=False,in_game_tested=False);(OUT/'install-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
if __name__=='__main__':main()
