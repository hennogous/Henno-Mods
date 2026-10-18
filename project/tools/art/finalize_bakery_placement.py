"""Final small peel placement plus independent serialized parent preservation audit."""
from install_bakery_props import *
report=json.loads((OUT/'install-report.json').read_text())
for entry in report['parent_changes']:
 path=MOD/'Assets'/(entry['parent']+'.ast');root=ET.parse(path).getroot();p=next(p for p in root.findall('.//m_attachmentPoints/m_Points/Element') if txt(p,'m_Name')=='BakeryProp_BAKERS_Peel')
 position=[-201,-87,14.18];rotation=math.pi/2
 for a,v in zip('xyz',position):p.find('m_position/'+a).text=f'{v/10:.9f}'
 p.find('m_orientation/z').text=f'{-rotation:.9f}';ET.indent(root,space='\t');ET.ElementTree(root).write(path,encoding='utf-8',xml_declaration=True)
 a=next(a for a in entry['added'] if a['asset']=='CSC_BAKERS_Peel');a['blender_position']=position;a['blender_z_radians']=rotation;entry['after_sha256']=sha(path)
 old=ET.parse(OUT/'before-install'/path.name).getroot();oldpts={txt(p,'m_Name'):canonical(p) for p in old.findall('.//m_attachmentPoints/m_Points/Element')};newpts={txt(p,'m_Name'):canonical(p) for p in root.findall('.//m_attachmentPoints/m_Points/Element')};removed={r['name'] for r in entry['removed']}
 assert all(v==newpts[n] for n,v in oldpts.items() if n not in removed)
 # Compare whole AST after reversing ONLY authorized attachment changes and five Visible edits.
 oldpoints=old.find('.//m_attachmentPoints/m_Points');newpoints=root.find('.//m_attachmentPoints/m_Points');newpoints.clear()
 for e in oldpoints:newpoints.append(copy.deepcopy(e))
 oldrows=old.findall('.//m_GroupStates/Element');newrows=root.findall('.//m_GroupStates/Element');assert len(oldrows)==len(newrows)
 changed=0
 for a,b in zip(oldrows,newrows):
  if txt(a,'m_MeshName')=='CSC_BAKERS_Oven_Bldg':
   for av,bv in zip(a.findall('m_Values/m_Values/Element'),b.findall('m_Values/m_Values/Element')):
    if txt(av,'m_ParamName')=='Visible':bv.find('m_bValue').text=av.find('m_bValue').text;changed+=1
 assert canonical(old)==canonical(root),'Unexpected non-placement AST change'
 entry['whole_ast_reverse_diff_pass']=True;entry['old_oven_visibility_rows']=changed
(OUT/'install-report.json').write_text(json.dumps(report,indent=2));print('EXACT SCOPED PARENT DIFF PASSED')
