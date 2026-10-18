"""Stage only effective visible emission flags; byte-preserve all other AST text."""
from bakery_props_atlas import *
import xml.etree.ElementTree as ET,re
MOD=ROOT/'Civ Supply Chains';dest=OUT/'emissive-state-mitigation';dest.mkdir(exist_ok=True);before=dest/'before';after=dest/'after';before.mkdir(exist_ok=True);after.mkdir(exist_ok=True)
audit=json.loads((OUT/'legacy-emissive-audit-before.json').read_text());hit={(r['geometry'],r['mesh']) for r in audit['meshes'] if r['emissive_triangles'] and r['geometry']!='CSC_BAKERS_Oven_v2'}
def txt(n,p):
 e=n.find(p);return e.get('text',e.text or '') if e is not None else ''
rows=[];checked=[]
for p in (MOD/'Assets').glob('*.ast'):
 raw=p.read_bytes();s=raw.decode('utf-8-sig');root=ET.fromstring(s);allbool=list(root.iter('m_bValue'));changes=[]
 for model in root.findall('.//m_ModelInstances/Element'):
  geo=txt(model,'m_GeoName')
  for g in model.findall('m_GroupStates/Element'):
   mesh=txt(g,'m_MeshName')
   if (geo,mesh) not in hit:continue
   vals={txt(v,'m_ParamName'):v for v in g.findall('m_Values/m_Values/Element')}
   if txt(vals.get('Material',ET.Element('x')),'m_ObjectName')!='CSC_ALL_Props_01':continue
   visible=txt(vals.get('Visible',ET.Element('x')),'m_bValue');em=txt(vals.get('EmissiveEnabled',ET.Element('x')),'m_bValue')
   assert visible in ('true','false') and em in ('true','false'),(p,geo,mesh,visible,em)
   checked.append(dict(asset=p.stem,geometry=geo,mesh=mesh,state=txt(g,'m_StateName'),visible=visible,emissive=em))
   if visible=='true' and em=='true':changes.append(dict(geometry=geo,mesh=mesh,state=txt(g,'m_StateName'),bool_index=allbool.index(vals['EmissiveEnabled'].find('m_bValue')),before='true',after='false'))
 if not changes:continue
 matches=list(re.finditer(r'<m_bValue>(true|false)</m_bValue>',s));assert len(matches)==len(allbool)
 edited=s
 for c in sorted(changes,key=lambda c:c['bool_index'],reverse=True):
  m=matches[c['bool_index']];assert m.group(1)=='true';edited=edited[:m.start(1)]+'false'+edited[m.end(1):]
 out=(b'\xef\xbb\xbf' if raw.startswith(b'\xef\xbb\xbf') else b'')+edited.encode('utf-8');(before/p.name).write_bytes(raw);(after/p.name).write_bytes(out)
 # Reverse the staged flag values in XML and require full semantic identity.
 tree=ET.fromstring(edited);bs=list(tree.iter('m_bValue'))
 for c in changes:bs[c['bool_index']].text='true'
 assert ET.tostring(tree)==ET.tostring(root)
 rows.append(dict(asset=p.stem,before_sha256=sha(before/p.name),after_sha256=sha(after/p.name),changes=changes,all_other_semantics_preserved=True))
(dest/'report.json').write_text(json.dumps(dict(assets=rows,checked_states=checked,runtime_writes=False),indent=2));print(json.dumps(dict(affected_assets=len(rows),changed_flags=sum(len(r['changes']) for r in rows),assets=[r['asset'] for r in rows])))
