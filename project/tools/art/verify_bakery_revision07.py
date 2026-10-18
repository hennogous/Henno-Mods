from install_bakery_props import *
import struct
old=LIB/'Releases/2026-10-17_Shared_01_r030'
for k in ['AO','O','E']:
 assert sha(old/'textures'/('CSC_Props_Shared_01_'+k+'.png'))==sha(LIB/'Current/textures'/('CSC_Props_Shared_01_'+k+'.png'))
report=json.loads((OUT/'revision-install-report.json').read_text());checks=[]
for name,h in report['parent_ASTs_bytewise_preserved'].items():assert sha(MOD/'Assets'/name)==h
for ident in IDS:
 validation=json.loads((OUT/(ident+'-validation.json')).read_text());assert validation['automated_pass'] and sha(SOURCE/(ident+'.blend'))==validation['source_sha256']
 for f,e in [('Assets','.ast'),('Geometries','.geo'),('Geometries','.fgx')]:assert sha(OUT/(ident+e))==sha(MOD/f/(ident+e))
 rows=[l.split() for l in (OUT/(ident+'-roundtrip.cn6')).read_text().split('vertices\n')[1].split('triangles\n')[0].strip().splitlines()]
 assert all(len(r)==34 and sum(int(x) for x in r[26:])==255 and sum(int(x)!=0 for x in r[26:])==1 for r in rows)
 assert all(int(r[18+next(i for i,v in enumerate(r[26:]) if int(v))])==1 for r in rows)
 entries=sum(txt(e,'m_EntryID')==ident for e in ET.parse(MOD/'XLPs/CSC_Tilebases.xlp').findall('m_Entries/Element'));assert entries<=1
 if entries==0:assert ident in ['CSC_BAKERS_Bread_Basket_Round','CSC_BAKERS_Bread_Basket_Oval']
 checks.append(dict(asset=ident,vertices=len(rows),source_validation_pass=True,installed_parity=True,three_uv_channels=True,single_Bone_weight255=True,xlp_entry_count=entries,registration_status="registered" if entries else "externally unregistered; preserved"))
lib=json.loads((LIB/'Current/library.json').read_text());assert lib['release']==RELEASE;assert all(sha(LIB/'Current'/p)==h and sha(LIB/'Releases'/RELEASE/p)==h for p,h in lib['files'].items())
assert all(sha(p)==sha(SOURCE/'textures'/p.name) for p in (STAGE/'textures').glob('*.png'))
kv=json.loads((OUT/'kit-validation.json').read_text());assert kv['automated_pass'] and kv['source_sha256']==sha(SOURCE/'CSC_BAKERS_Bakery_Prop_Kit.blend')
renders=[]
for parent in ['CSC_BAKERS_Bakery']:
 p=next((OUT/('review-alternate' if parent.endswith('_2') else 'review-standard')).rglob(parent+'_sv.blend'));ob=json.loads((p.parent/'objects.json').read_text());assert not ob['outside_frame_objects'];renders.append(str(p))
for p in (OUT/'dds').glob('*.dds'):
 a=p.read_bytes();b=(MOD/'Textures'/p.name).read_bytes();w=struct.unpack_from('<I',a,16)[0];h=struct.unpack_from('<I',a,12)[0];bpp=struct.unpack_from('<I',a,88)[0]//8;assert a[128:128+w*h*bpp]==b[128:128+w*h*bpp]
final=dict(release=RELEASE,external_registration_changes=["CSC_BAKERS_Bread_Basket_Round","CSC_BAKERS_Bread_Basket_Oval"],AO_O_E_bytewise_unchanged=True,checks=checks,library_hashes_match=True,portable_textures_match=True,kit_validated=True,current_standard_AST_bytes_preserved=True,alternate_externally_deleted=True,installed_texture_full_resolution_pixels_match=True,source_compliance=json.loads((OUT/'user-revision-source-audit.json').read_text()),saved_AST_render_snapshots=renders,cook_tested=False,in_game_tested=False)
(OUT/'final-verification.json').write_text(json.dumps(final,indent=2));print('FINAL R031 VERIFIED')
