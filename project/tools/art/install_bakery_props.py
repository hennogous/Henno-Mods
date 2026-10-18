"""Scoped Bakery prop installation and canonical shared atlas r025 publication."""
from bakery_props_atlas import *
import xml.etree.ElementTree as ET,subprocess,importlib.util,os,tempfile,copy
from PIL import Image
MOD=ROOT/'Civ Supply Chains'
IDS=['CSC_BAKERS_Peel','CSC_BAKERS_Dough_Set','CSC_BAKERS_Bread_Basket_Round','CSC_BAKERS_Bread_Basket_Oval','CSC_BAKERS_Bread_Basket_Long','CSC_BAKERS_Bread_Cart','CSC_BAKERS_Oven_v2']
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def txt(e,p):
 n=e.find(p);return n.get('text',n.text or '') if n is not None else ''
def canonical(e):return (e.tag,tuple(sorted(e.attrib.items())),(e.text or '').strip(),tuple(canonical(c) for c in e))
def atomic(src,dest):
 dest.parent.mkdir(exist_ok=True,parents=True);temp=dest.with_name(dest.name+'.bakery-tmp');shutil.copy2(src,temp);os.replace(temp,dest)
def native_checks():
 parser=module('bakery_native',ROOT/'project/tools/art/install_tailor_garment_rack.py');results=[]
 for ident in IDS:
  v=json.loads((OUT/(ident+'-validation.json')).read_text());assert v['automated_pass'] and v['source_sha256']==sha(SOURCE/(ident+'.blend'))
  a,va,ta=parser.parse(OUT/(ident+'.cn6'));b,vb,tb=parser.parse(OUT/(ident+'-roundtrip.cn6'));assert a==b and ta==tb
  err=float(np.max(np.abs(np.array(va)-np.array(vb))));assert err<1e-4;exp=json.loads((OUT/(ident+'-export.json')).read_text());assert len(va)==exp['vertices']
  assert all(len(row)==18 and all(math.isfinite(x) for x in row) for row in va)
  for row in ET.parse(OUT/(ident+'.ast')).findall('.//m_GroupStates/Element'):
   values={txt(e,'m_ParamName'):e for e in row.findall('m_Values/m_Values/Element')};assert txt(values['Material'],'m_ObjectName')=='CSC_ALL_Props_01';assert txt(values['Visible'],'m_bValue')==str(txt(row,'m_StateName') in ('Worked','Unworked')).lower()
  results.append(dict(asset=ident,vertices=len(va),triangles=len(ta),native_max_error=err,source_validated=True))
 return results
def prepare_release():
 # Assert unmodified live baseline, and preserve all pixels outside named additions.
 baseline=json.loads((OUT/'live-atlas-baseline.json').read_text());assert all(sha(LIB/'Current'/p)==h for p,h in baseline.items())
 old=json.loads((LIB/'Current/atlas/manifest.json').read_text());new=json.loads((STAGE/'atlas/manifest.json').read_text());added=[r for r in new['regions'] if r['name'] not in {r['name'] for r in old['regions']}]
 for k in 'BNGM':
  before=np.array(Image.open(LIB/'Current/textures'/f'CSC_Props_Shared_01_{k}.png').convert('RGB'));after=np.array(Image.open(STAGE/'textures'/f'CSC_Props_Shared_01_{k}.png').convert('RGB'));mask=np.ones((1024,1024),bool)
  for r in added:x,y=r['slot']%8*128,r['slot']//8*128;mask[y:y+128,x:x+128]=False
  assert np.array_equal(before[mask],after[mask])
 op=Image.open(STAGE/'textures/CSC_Props_Shared_01_O.png')
 for r in old['regions']:
  x,y=r['slot']%8*128,r['slot']//8*128;assert op.crop((x,y,x+128,y+128)).getextrema()==(255,255)
 before=np.array(Image.open(LIB/'Current/textures/CSC_Props_Shared_01_AO.png').convert('RGB'));after=np.array(Image.open(STAGE/'textures/CSC_Props_Shared_01_AO.png').convert('RGB'));mask=np.ones((2048,2048),bool)
 for ident in IDS:
  x,y,x1,y1=json.loads((OUT/(ident+'-export.json')).read_text())['ao_cell'];mask[y:y1,x:x1]=False
 assert np.array_equal(before[mask],after[mask])
 # Reproducible additions preserve a baseline with exact accepted pixels, including hand edits.
 base=STAGE/'atlas/sources/bakery-r024-baseline';base.mkdir(exist_ok=True)
 for k in ['B','N','G','M','AO','E']:shutil.copy2(LIB/'Current/textures'/f'CSC_Props_Shared_01_{k}.png',base/f'CSC_Props_Shared_01_{k}.png')
 shutil.copy2(STAGE/'textures/CSC_Props_Shared_01_O.png',STAGE/'atlas/sources/bakery-opacity-mask.png')
 rebuild='''from pathlib import Path
import json
from PIL import Image
import numpy as np
root=Path(__file__).resolve().parents[1]
m=json.loads((root/'atlas/manifest.json').read_text())
for k in ['B','N','G','M']:
 im=Image.open(root/'atlas/sources/bakery-r024-baseline'/('CSC_Props_Shared_01_'+k+'.png')).convert('RGB')
 for r in m['regions']:
  if not r['name'].startswith('bakery_'):continue
  p=Image.open(root/'atlas'/r['sources'][k]).convert('RGB').resize((120,120),Image.Resampling.LANCZOS)
  im.paste(Image.fromarray(np.pad(np.array(p),((4,4),(4,4),(0,0)),mode='edge')),(r['slot']%8*128,r['slot']//8*128))
 im.save(root/'textures'/('CSC_Props_Shared_01_'+k+'.png'))
Image.open(root/'atlas/sources/bakery-opacity-mask.png').save(root/'textures/CSC_Props_Shared_01_O.png')
im=Image.open(root/'atlas/sources/bakery-r024-baseline/CSC_Props_Shared_01_AO.png').convert('RGB')
m=json.loads((root/'atlas/quarter-ao-manifest.json').read_text())
for a in m['pages'][0]['quarters'][0]['families'][1].get('allocations',[]):
 im.paste(Image.open(root/a['source']).convert('RGB'),a['cell'][:2])
im.save(root/'textures/CSC_Props_Shared_01_AO.png')
'''
 (STAGE/'scripts/pack_bakery_additions.py').write_text(rebuild)
 hashes={p.name:sha(p) for p in (STAGE/'textures').glob('*.png')};subprocess.run([sys.executable,STAGE/'scripts/pack_bakery_additions.py'],check=True);assert all(sha(STAGE/'textures'/p)==h for p,h in hashes.items())
 lib=json.loads((STAGE/'library.json').read_text());lib.update(release=RELEASE,accepted_on='2026-10-16',content_revision=25,snapshot_path='Releases/'+RELEASE,surface_status='Bakery patches in previously free cells; all old occupied pixels unchanged.',AO_status='Seven isolated Bakery self-AO cells in Bakers Stage3; all other pixels unchanged.',review_status='Saved-source/native checks and assistant review; AE cook and game acceptance pending')
 lib['runtime_bindings']['opacity']='textures/CSC_Props_Shared_01_O.png';lib['rebuild']['bakery_additions']='python scripts/pack_bakery_additions.py'
 for ident in IDS:lib['source_FINAL_sha256']['BAKERS/Bakery/revision-01-prop-kit/'+ident+'.blend']=sha(SOURCE/(ident+'.blend'))
 lib['files']={p.relative_to(STAGE).as_posix():sha(p) for p in STAGE.rglob('*') if p.is_file() and p.name!='library.json'};(STAGE/'library.json').write_text(json.dumps(lib,indent=2))
 # DDS conversion uses existing formats and normalized Firaxis scalar header.
 converter=module('bakery_dds',ROOT/'project/tools/blender/scene_export/export_scene.py');dd=OUT/'dds';dd.mkdir(exist_ok=True)
 for k in ['B','N','G','M','AO','O']:
  name='CSC_Props_Shared_01_'+k;tex=ET.parse(MOD/'Textures'/('CSC_Props_Shared_01_AO.tex' if k=='O' else name+'.tex'));fmt=tex.findtext('m_ExportSettings/ePixelformat').removeprefix('PF_');size=list(Image.open(STAGE/'textures'/(name+'.png')).size)
  args=[str(ROOT/'project/tools/directxtex/texconv.exe'),'-nologo','-y','-m','0','-f',fmt,'-o',str(dd),'--ignore-srgb']+(['-srgb'] if k=='B' else [])+[str(STAGE/'textures'/(name+'.png'))];r=subprocess.run(args,capture_output=True,text=True);assert r.returncode==0;(OUT/(name+'-dds.log')).write_text(r.stdout+r.stderr)
  spec=dict(format=fmt,size=size,slot=k)
  if fmt=='R8_UNORM':converter.normalize_ao_dds(dd/(name+'.dds'),spec,MOD/'Textures/CSC_Props_Shared_01_AO.dds')
  converter.validate_dds(dd/(name+'.dds'),spec)
  if k=='O':
   root=tex.getroot();root.find('m_Name').set('text',name);root.find('m_ClassName').set('text','Generic_OPAC');root.find('m_ClassName').text=None;root.find('m_SourceFilePath').set('text',str(LIB/'Current/textures'/(name+'.png')));root.find('m_DataFiles/Element/m_RelativePath').set('text',name+'.dds');root.find('m_Width').text='1024';root.find('m_Height').text='1024';root.find('m_ExportSettings/eFilterType').text='FT_BOX';ET.indent(root,space='  ');tex.write(OUT/(name+'.tex'),encoding='utf-8',xml_declaration=True)
 return dict(old_occupied_surface_pixels_preserved=True,all_nonallocated_AO_pixels_preserved=True,old_opacity_255=True,rebuild_hashes_match=True,new_regions=[r['name'] for r in added])
def parents():
 changes=[];fit=json.loads((OUT/'oven-parent-transform.json').read_text());angle=math.atan2(fit['rotation'][1][0],fit['rotation'][0][0])
 for ident in ['CSC_BAKERS_Bakery','CSC_BAKERS_Bakery_2']:
  path=MOD/'Assets'/(ident+'.ast');raw=path.read_bytes();shutil.copy2(path,OUT/'before-install'/path.name);ast=ET.fromstring(raw);points=ast.find('.//m_attachmentPoints/m_Points');before={txt(p,'m_Name'):canonical(p) for p in points};removed=[]
  for p in list(points):
   name=txt(p,'m_Name');asset=next((txt(e,'m_EntryName') for e in p.findall('m_CookParams/m_Values/Element') if txt(e,'m_ParamName')=='Asset'),'')
   # Preserve fixed original sales stand/table. Expanded duplicate sales installations are superseded by mobile cart.
   discard=asset=='CSC_BAKERS_Bread'
   if ident.endswith('_2') and name in ['newAttachmentPoint_3','newAttachmentPoint_4','newAttachmentPoint_5','newAttachmentPoint_10','newAttachmentPoint_18','newAttachmentPoint_20','newAttachmentPoint_29','newAttachmentPoint_31','newAttachmentPoint_32']:discard=True
   if discard:removed.append(dict(name=name,asset=asset));points.remove(p)
  template=copy.deepcopy(next(p for p in points if any(txt(e,'m_ParamName')=='Asset' for e in p.findall('m_CookParams/m_Values/Element'))))
  positions=[('CSC_ALL_Workbench_Wide',(-207,-83,0),0,1),('CSC_BAKERS_Dough_Set',(-207,-83,14.08),0,1),('CSC_BAKERS_Peel',(-201,-87,14.18),math.pi/2,1),('CSC_BAKERS_Bread_Basket_Round',(-174,-85,11.8),-.8,.65),('CSC_BAKERS_Bread_Basket_Oval',(-165,-89,11.8),-.8,.65),('CSC_BAKERS_Bread_Basket_Long',(-170,-92,11.8),-.8,.65),('CSC_BAKERS_Oven_v2',fit['translation'],angle,.5)]
  if ident.endswith('_2'):positions.append(('CSC_BAKERS_Bread_Cart',(-111,-127,0),-.5,1))
  added=[]
  for asset,pos,rot,scale in positions:
   p=copy.deepcopy(template);name='BakeryProp_'+asset.removeprefix('CSC_');p.find('m_Name').set('text',name)
   for e in p.findall('m_CookParams/m_Values/Element'):
    if txt(e,'m_ParamName')=='Asset':e.find('m_EntryName').set('text',asset)
    if txt(e,'m_ParamName')=='Cull Mode':e.find('m_Value').set('text','PERMANENT')
   for axis,value in zip('xyz',pos):p.find('m_position/'+axis).text=f'{value/10:.9f}'
   for axis,value in zip('xyz',[0,0,-rot]):p.find('m_orientation/'+axis).text=f'{value:.9f}'
   p.find('m_scale').text=str(scale);p.find('m_ModelInstanceName').set('text','CSC_BAKERS_Bakery');p.find('m_BoneName').set('text','CSC_BAKERS_Bakery');points.append(p);added.append(dict(name=name,asset=asset,blender_position=pos,blender_z_radians=rot,scale=scale))
  hidden=[]
  for row in ast.findall('.//m_GroupStates/Element'):
   if txt(row,'m_MeshName')=='CSC_BAKERS_Oven_Bldg':
    for e in row.findall('m_Values/m_Values/Element'):
     if txt(e,'m_ParamName')=='Visible':e.find('m_bValue').text='false'
    hidden.append(txt(row,'m_StateName'))
  after={txt(p,'m_Name'):canonical(p) for p in points};assert all(after[n]==v for n,v in before.items() if n not in {r['name'] for r in removed})
  ET.indent(ast,space='\t');ET.ElementTree(ast).write(path,encoding='utf-8',xml_declaration=True)
  changes.append(dict(parent=ident,removed=removed,added=added,hidden_old_oven_states=hidden,unrelated_attachments_preserved=True,before_sha256=hashlib.sha256(raw).hexdigest(),after_sha256=sha(path)))
 return changes
def main():
 results=native_checks();atlas=prepare_release();backup=OUT/'before-install';backup.mkdir(exist_ok=True)
 protected={str(p):sha(p) for p in (MOD/'Assets').glob('*.ast') if p.stem not in IDS+['CSC_BAKERS_Bakery','CSC_BAKERS_Bakery_2']}
 for ident in IDS:
  for folder,ext in [('Assets','.ast'),('Geometries','.geo'),('Geometries','.fgx')]:
   dest=MOD/folder/(ident+ext)
   if dest.exists():shutil.copy2(dest,backup/dest.name)
   atomic(OUT/(ident+ext),dest)
 for p in (OUT/'dds').glob('*.dds'):
  dest=MOD/'Textures'/p.name
  if dest.exists():shutil.copy2(dest,backup/dest.name)
  atomic(p,dest)
 atomic(OUT/'CSC_Props_Shared_01_O.tex',MOD/'Textures/CSC_Props_Shared_01_O.tex')
 mtl=MOD/'Materials/CSC_ALL_Props_01.mtl';shutil.copy2(mtl,backup/mtl.name);text=mtl.read_text();tree=ET.fromstring(text)
 for e in tree.findall('m_CookParams/m_Values/Element'):
  if txt(e,'m_ParamName')=='Opacity':assert txt(e,'m_ObjectName')=='';e.find('m_ObjectName').set('text','CSC_Props_Shared_01_O')
 ET.indent(tree,space='\t');ET.ElementTree(tree).write(mtl,encoding='utf-8',xml_declaration=True)
 xlp=MOD/'XLPs/CSC_Tilebases.xlp';raw=xlp.read_bytes();shutil.copy2(xlp,backup/xlp.name)
 for ident in IDS:
  if ident.encode() not in raw:raw=raw.replace(b'\t</m_Entries>',f'\t\t<Element>\n\t\t\t<m_EntryID text="{ident}"/>\n\t\t\t<m_ObjectName text="{ident}"/>\n\t\t</Element>\n\t</m_Entries>'.encode())
 ET.fromstring(raw);xlp.write_bytes(raw)
 parent_changes=parents();assert all(sha(Path(p))==h for p,h in protected.items())
 release=LIB/'Releases'/RELEASE;assert not release.exists();shutil.copytree(LIB/'Current',backup/'Current');shutil.copy2(LIB/'CURRENT.json',backup/'CURRENT.json');shutil.copytree(STAGE,release);shutil.copytree(STAGE,LIB/'Current',dirs_exist_ok=True)
 (LIB/'CURRENT.json').write_text(json.dumps(dict(release=RELEASE,current='Current',manifest='Current/library.json',snapshot='Releases/'+RELEASE,updated_on='2026-10-16',library_sha256=sha(LIB/'Current/library.json')),indent=2))
 cache=module('bakery_cache',ROOT/'project/tools/art/install_tailor_garment_rack.py');cache.OUT=OUT
 for ident in IDS:cache.ID=ident;cache.register_cache()
 (OUT/'install-report.json').write_text(json.dumps(dict(assets=results,atlas=atlas,atlas_release=RELEASE,parent_changes=parent_changes,unrelated_asset_count=len(protected),cook_tested=False,in_game_tested=False),indent=2));print('BAKERY INSTALLED',RELEASE)
if __name__=='__main__':main()
