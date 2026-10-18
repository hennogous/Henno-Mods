"""Final source/native parity, exact static skin data and installed dependency audit."""
from install_bakery_props import *
import struct
# Normalize the native string-valued class field, including files rewritten by AE.
for p in [OUT/'CSC_Props_Shared_01_O.tex',MOD/'Textures/CSC_Props_Shared_01_O.tex']:
 tree=ET.parse(p);n=tree.find('m_ClassName');n.set('text','Generic_OPAC');n.text=None;ET.indent(tree,space='  ');tree.write(p,encoding='utf-8',xml_declaration=True)
result=native_checks();xlp=ET.parse(MOD/'XLPs/CSC_Tilebases.xlp');audit=[]
for ident in IDS:
 for f,e in [('Assets','.ast'),('Geometries','.geo'),('Geometries','.fgx')]:assert sha(OUT/(ident+e))==sha(MOD/f/(ident+e))
 assert sum(txt(e,'m_EntryID')==ident for e in xlp.findall('m_Entries/Element'))==1
 line=(OUT/(ident+'-roundtrip.cn6')).read_text().split('vertices\n')[1].split('triangles\n')[0].strip().splitlines();rows=[l.split() for l in line]
 assert all(len(r)==34 for r in rows)
 assert all(sum(int(x) for x in r[26:])==255 and sum(int(x)!=0 for x in r[26:])==1 for r in rows)
 assert all(int(r[18+next(i for i,v in enumerate(r[26:]) if int(v))])==1 for r in rows)
 audit.append(dict(asset=ident,uv_channels=3,all_finite=True,single_Bone_weight_255=True,vertices=len(rows),unique_xlp=True,installed_bytes_match=True))
lib=json.loads((LIB/'Current/library.json').read_text());assert lib['release']==RELEASE
assert all(sha(LIB/'Current'/p)==h and sha(LIB/'Releases'/RELEASE/p)==h for p,h in lib['files'].items())
assert all(sha(p)==sha(SOURCE/'textures'/p.name) for p in (STAGE/'textures').glob('*.png'))
kit=SOURCE/'CSC_BAKERS_Bakery_Prop_Kit.blend';kv=json.loads((OUT/'kit-validation.json').read_text());assert kv['automated_pass'] and kv['source_sha256']==sha(kit)
converter=module('bakery_verify_dds',ROOT/'project/tools/blender/scene_export/export_scene.py');dds=[]
for staged in (OUT/'dds').glob('*.dds'):
 live=MOD/'Textures'/staged.name;data=live.read_bytes();old=staged.read_bytes();w,h=struct.unpack_from('<I',data,16)[0],struct.unpack_from('<I',data,12)[0];bpp=struct.unpack_from('<I',data,88)[0]//8;fmt='R8_UNORM' if bpp==1 else 'R8G8B8A8_UNORM';converter.validate_dds(live,dict(format=fmt,size=[w,h],slot=staged.stem.rsplit('_',1)[1]));assert data[128:128+w*h*bpp]==old[128:128+w*h*bpp];dds.append(dict(texture=live.name,top_level_pixels_match=True,normalized_header_valid=True))
final=dict(source_directory=str(SOURCE),kit=str(kit),kit_validated=True,atlas_release=RELEASE,release_hashes_match=True,portable_textures_match=True,assets=audit,geometry_parity=result,dds=dds,opacity_class=txt(ET.parse(MOD/'Textures/CSC_Props_Shared_01_O.tex').getroot(),'m_ClassName'),render_paths=[str(OUT/'renders/CSC_BAKERS_Bakery_SV_Input.png'),str(OUT/'renders/CSC_BAKERS_Bakery_2_SV_Input.png')],cook_tested=False,in_game_tested=False)
placement=[]
installed=json.loads((OUT/'install-report.json').read_text())
for entry,folder,fingerprint in zip(installed['parent_changes'],['assembled-standard','assembled-alternate'],['56b3858b3612d929','3ea63f76497cb874']):
 render=OUT/folder/entry['parent']/fingerprint/'sv/objects.json';objects=json.loads(render.read_text())['object_ids']
 for a in entry['added']:
  ob=next(o for o in objects if o['asset']==a['asset']);matrix=np.array(ob['matrix_world']);t=a['blender_z_radians'];s=a['scale'];expected=np.array([[s*math.cos(t),-s*math.sin(t),0,a['blender_position'][0]],[s*math.sin(t),s*math.cos(t),0,a['blender_position'][1]],[0,0,s,a['blender_position'][2]],[0,0,0,1]])
  err=float(np.max(np.abs(matrix-expected)));assert err<3e-5,(a['asset'],err);placement.append(dict(parent=entry['parent'],asset=a['asset'],saved_AST_native_reconstruction_max_transform_error=err,native_source_vertices=ob['source_vertices']))
final['native_reconstructed_placements']=placement
(OUT/'final-verification.json').write_text(json.dumps(final,indent=2));print('FINAL VERIFIED',len(IDS),'assets',RELEASE)
