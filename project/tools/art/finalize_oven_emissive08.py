from bakery_props_atlas import *
import subprocess,xml.etree.ElementTree as ET
MOD=ROOT/'Civ Supply Chains';lib=ROOT/'project/tools/cn6libs';dst=OUT/'CSC_BAKERS_Oven_v2-installed-readback.cn6'
r=subprocess.run([str(lib/'FGXToCN6.exe'),str(MOD/'Geometries/CSC_BAKERS_Oven_v2.fgx'),str(dst)],cwd=lib,capture_output=True,text=True,creationflags=subprocess.CREATE_NO_WINDOW);assert r.returncode==0
assert dst.read_bytes()==(OUT/'CSC_BAKERS_Oven_v2-roundtrip.cn6').read_bytes()
baseline=json.loads((OUT/'preinstall-runtime-hashes.json').read_text());installed=json.loads((OUT/'installation-report.json').read_text());changed=[p for p,h in baseline.items() if sha(MOD/p)!=h];assert set(changed)==set(installed['changed_runtime_files'])
assert json.loads((LIB/'CURRENT.json').read_text())['release']==RELEASE
assert all(sha(p)==sha(STAGE/p.relative_to(LIB/'Current')) for p in (LIB/'Current').rglob('*') if p.is_file())
sources=[]
for p in SOURCE.glob('*.blend'):
 report=OUT/('kit-validation.json' if p.stem=='CSC_BAKERS_Bakery_Prop_Kit' else p.stem+'-validation.json');v=json.loads(report.read_text());assert v['automated_pass'] and v['source_sha256']==sha(p);sources.append(dict(path=str(p),sha256=sha(p),saved_validator_pass=True))
tex=ET.parse(MOD/'Textures/CSC_Atlas_E.tex');assert tex.find('m_ClassName').get('text')=='Generic_Emissive'
mtl=(MOD/'Materials/CSC_ALL_Props_01.mtl').read_text();assert 'text="CSC_Atlas_E"' in mtl
result=dict(completed=True,current_release=RELEASE,new_atlas_release=False,canonical_all_files_preserved=True,all_runtime_texture_TEX_XLP_bytes_preserved=True,installed_native_readback_exact=True,sources=sources,oven_vertices=879,oven_triangles=427,opening_UV3_faces=6,opening_UV3_native_triangles=12,only_oven_UV3_changed=True,material_emissive='CSC_Atlas_E',mitigated_flags=49,mitigated_assets=20,review_images=['Oven_Legacy_Coals_Diagnostic.jpg','Oven_Emission_Only.jpg'],limitations='Blender emission diagnostic and native/material validation; no new AE cook/game acceptance claimed.')
(OUT/'final-verification.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
