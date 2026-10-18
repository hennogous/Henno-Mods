"""Install only r026 geometry/textures; every parent attachment is preserved bytewise."""
from install_bakery_props import *
def main():
 assert RELEASE.endswith('r026');assert json.loads((LIB/'CURRENT.json').read_text())['release'].endswith('r025')
 old=LIB/'Releases/2026-10-16_Shared_01_r025';oldlib=json.loads((old/'library.json').read_text());assert all(sha(LIB/'Current'/p)==h for p,h in oldlib['files'].items())
 results=native_checks();backup=OUT/'before-install';backup.mkdir(exist_ok=True)
 changed_slots=[30,34,61,62]
 for k in 'BNGM':
  a=np.array(Image.open(old/'textures'/f'CSC_Props_Shared_01_{k}.png').convert('RGB'));b=np.array(Image.open(STAGE/'textures'/f'CSC_Props_Shared_01_{k}.png').convert('RGB'));mask=np.ones((1024,1024),bool)
  for slot in changed_slots:x,y=slot%8*128,slot//8*128;mask[y:y+128,x:x+128]=False
  assert np.array_equal(a[mask],b[mask])
 ao_before=np.array(Image.open(old/'textures/CSC_Props_Shared_01_AO.png'));ao_after=np.array(Image.open(STAGE/'textures/CSC_Props_Shared_01_AO.png'));mask=np.ones((2048,2048),bool)
 for ident in IDS[1:6]:
  x,y,x1,y1=json.loads((OUT/(ident+'-export.json')).read_text())['ao_cell'];mask[y:y1,x:x1]=False
 assert np.array_equal(ao_before[mask],ao_after[mask]);assert sha(old/'textures/CSC_Props_Shared_01_O.png')==sha(STAGE/'textures/CSC_Props_Shared_01_O.png')
 texhash={p.name:sha(p) for p in (STAGE/'textures').glob('*.png')};subprocess.run([sys.executable,STAGE/'scripts/pack_bakery_additions.py'],check=True);assert all(sha(STAGE/'textures'/n)==h for n,h in texhash.items())
 lib=json.loads((STAGE/'library.json').read_text());lib.update(release=RELEASE,accepted_on='2026-10-16',content_revision=26,snapshot_path='Releases/'+RELEASE,surface_status='User revision: oven bricks 40x24 versus24x16; all baked bread represented by painted basket-fill surfaces, no individual loaf meshes. New oval arrangement slot30.',AO_status='Dough40% larger; basket/cart self-AO rebaked after loaf geometry removal. All other AO pixels preserved.')
 for ident in IDS:lib['source_FINAL_sha256']['BAKERS/Bakery/revision-02-prop-kit/'+ident+'.blend']=sha(SOURCE/(ident+'.blend'))
 lib['source_FINAL_sha256']['BAKERS/Bakery/revision-02-prop-kit/CSC_BAKERS_Bakery_Prop_Kit.blend']=sha(SOURCE/'CSC_BAKERS_Bakery_Prop_Kit.blend')
 lib['files']={p.relative_to(STAGE).as_posix():sha(p) for p in STAGE.rglob('*') if p.is_file() and p.name!='library.json'};(STAGE/'library.json').write_text(json.dumps(lib,indent=2))
 dd=OUT/'dds';dd.mkdir(exist_ok=True);converter=module('bakery_r026_dds',ROOT/'project/tools/blender/scene_export/export_scene.py')
 for k in ['B','N','G','M','AO']:
  name='CSC_Props_Shared_01_'+k;fmt=ET.parse(MOD/'Textures'/(name+'.tex')).findtext('m_ExportSettings/ePixelformat').removeprefix('PF_');size=list(Image.open(STAGE/'textures'/(name+'.png')).size)
  args=[str(ROOT/'project/tools/directxtex/texconv.exe'),'-nologo','-y','-m','0','-f',fmt,'-o',str(dd),'--ignore-srgb']+(['-srgb'] if k=='B' else [])+[str(STAGE/'textures'/(name+'.png'))];r=subprocess.run(args,capture_output=True,text=True);assert r.returncode==0;(OUT/(name+'-dds.log')).write_text(r.stdout+r.stderr)
  spec=dict(format=fmt,size=size,slot=k)
  if fmt=='R8_UNORM':converter.normalize_ao_dds(dd/(name+'.dds'),spec,MOD/'Textures/CSC_Props_Shared_01_AO.dds')
  converter.validate_dds(dd/(name+'.dds'),spec)
 parents={p:sha(p) for p in (MOD/'Assets').glob('*.ast') if p.stem not in IDS}
 copies=[]
 for ident in IDS[1:6]:
  for folder,ext in [('Assets','.ast'),('Geometries','.geo'),('Geometries','.fgx')]:copies.append((OUT/(ident+ext),MOD/folder/(ident+ext)))
 for p in dd.glob('*.dds'):copies.append((p,MOD/'Textures'/p.name))
 for src,dest in copies:shutil.copy2(dest,backup/dest.name);atomic(src,dest)
 release=LIB/'Releases'/RELEASE;assert not release.exists();shutil.copy2(LIB/'CURRENT.json',backup/'CURRENT.json');shutil.copytree(STAGE,release);shutil.copytree(STAGE,LIB/'Current',dirs_exist_ok=True);(LIB/'CURRENT.json').write_text(json.dumps(dict(release=RELEASE,current='Current',manifest='Current/library.json',snapshot='Releases/'+RELEASE,updated_on='2026-10-16',library_sha256=sha(LIB/'Current/library.json')),indent=2))
 assert all(sha(p)==h for p,h in parents.items());assert all(sha(s)==sha(d) for s,d in copies)
 cache=module('bakery_revision_cache',ROOT/'project/tools/art/install_tailor_garment_rack.py');cache.OUT=OUT
 for ident in IDS[1:6]:cache.ID=ident;cache.register_cache()
 report=dict(release=RELEASE,assets=results,parent_ASTs_bytewise_preserved={p.name:h for p,h in parents.items() if p.stem in ['CSC_BAKERS_Bakery','CSC_BAKERS_Bakery_2']},all_other_assets_preserved=len(parents),changed_surface_slots=changed_slots,all_other_surface_pixels_preserved=True,nonallocated_AO_pixels_preserved=True,opacity_unchanged=True,rebuild_hashes_match=True,peel_separate_asset='CSC_BAKERS_Peel',source_directory=str(SOURCE),kit=str(SOURCE/'CSC_BAKERS_Bakery_Prop_Kit.blend'),cook_tested=False,in_game_tested=False)
 (OUT/'revision-install-report.json').write_text(json.dumps(report,indent=2));print('R026 PUBLISHED',results)
if __name__=='__main__':main()
