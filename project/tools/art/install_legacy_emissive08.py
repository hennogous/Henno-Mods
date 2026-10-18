"""Mitigation-first direct legacy E binding; no textures, XLP, placement or geometry edits."""
from bakery_props_atlas import *
import xml.etree.ElementTree as ET
MOD=ROOT/'Civ Supply Chains';d=OUT/'emissive-state-mitigation';report=json.loads((d/'report.json').read_text());audit=json.loads((OUT/'legacy-emissive-audit-after.json').read_text());hit={(r['geometry'],r['mesh']) for r in audit['meshes'] if r['emissive_triangles'] and r['geometry']!='CSC_BAKERS_Oven_v2'}
def txt(n,p):
 e=n.find(p);return e.get('text',e.text or '') if e is not None else ''
def effective():
 bad=[]
 for p in (MOD/'Assets').glob('*.ast'):
  for m in ET.parse(p).findall('.//m_ModelInstances/Element'):
   for g in m.findall('m_GroupStates/Element'):
    if (txt(m,'m_GeoName'),txt(g,'m_MeshName')) not in hit:continue
    v={txt(x,'m_ParamName'):x for x in g.findall('m_Values/m_Values/Element')}
    if txt(v.get('Material',ET.Element('x')),'m_ObjectName')=='CSC_ALL_Props_01' and txt(v.get('Visible',ET.Element('x')),'m_bValue')=='true' and txt(v.get('EmissiveEnabled',ET.Element('x')),'m_bValue')!='false':bad.append((p.name,txt(g,'m_StateName')))
 return bad
assert json.loads((LIB/'CURRENT.json').read_text())['release']==RELEASE
assert sha(MOD/'Geometries/CSC_BAKERS_Oven_v2.fgx')==sha(OUT/'before/CSC_BAKERS_Oven_v2.fgx')
assert (MOD/'Geometries/CSC_BAKERS_Oven_v2.geo').read_bytes()==(OUT/'CSC_BAKERS_Oven_v2.geo').read_bytes()
for r in report['assets']:assert sha(MOD/'Assets'/(r['asset']+'.ast'))==r['before_sha256'],r['asset']
mtl=MOD/'Materials/CSC_ALL_Props_01.mtl';old=mtl.read_bytes();assert old.count(b'CSC_Props_Shared_01_E')==1;new=old.replace(b'CSC_Props_Shared_01_E',b'CSC_Atlas_E');(OUT/'before/CSC_ALL_Props_01.mtl').write_bytes(old)
baseline={p.relative_to(MOD).as_posix():sha(p) for folder in ['Assets','Materials','Textures','Geometries','XLPs'] for p in (MOD/folder).glob('*') if p.is_file()};(OUT/'preinstall-runtime-hashes.json').write_text(json.dumps(baseline,indent=2));library={p.relative_to(LIB/'Current').as_posix():sha(p) for p in (LIB/'Current').rglob('*') if p.is_file()}
# First remove emission from conflicting states, preserving their prior black-E appearance.
for r in report['assets']:
 p=MOD/'Assets'/(r['asset']+'.ast');assert sha(p)==r['before_sha256'];p.write_bytes((d/'after'/p.name).read_bytes())
assert not effective(),effective()
# Only now activate existing legacy texture and UV3-adjusted oven.
assert mtl.read_bytes()==old;mtl.write_bytes(new)
shutil.copy2(OUT/'CSC_BAKERS_Oven_v2.fgx',MOD/'Geometries/CSC_BAKERS_Oven_v2.fgx')
assert not effective();assert library=={p.relative_to(LIB/'Current').as_posix():sha(p) for p in (LIB/'Current').rglob('*') if p.is_file()}
allowed={'Materials/CSC_ALL_Props_01.mtl','Geometries/CSC_BAKERS_Oven_v2.fgx'}|{'Assets/'+r['asset']+'.ast' for r in report['assets']};changed=[k for k,h in baseline.items() if sha(MOD/k)!=h];assert set(changed)==allowed,(changed,allowed)
(OUT/'installation-report.json').write_text(json.dumps(dict(release_unchanged=RELEASE,changed_runtime_files=changed,mitigated_assets=len(report['assets']),mitigated_flags=sum(len(r['changes']) for r in report['assets']),unintended_effective_emission=[],library_all_files_unchanged=True,textures_XLPs_unchanged=True,oven_geo_unchanged=True,installed_oven_sha256=sha(MOD/'Geometries/CSC_BAKERS_Oven_v2.fgx')),indent=2));print('INSTALLED',len(changed),'files; 49 emission flags mitigated before material switch; all textures and library unchanged')
