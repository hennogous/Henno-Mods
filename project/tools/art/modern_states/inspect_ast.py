from pathlib import Path
import xml.etree.ElementTree as E
R=Path(__file__).resolve().parents[4];M=R/'Civ Supply Chains'
for ident in ('CSC_Level_1_S_Modern','CSC_BAKERS_Mill_Silo_Modern','CSC_BAKERS_Wind_Mill_Modern','CSC_BAKERS_Water_Mill_Modern'):
 r=E.parse(M/'Assets'/(ident+'.ast')).getroot();print('\nASSET',ident)
 for n in r.findall('.//m_ModelInstances/Element'):
  print('MODEL',n.find('m_Name').get('text'),n.find('m_GeoName').get('text'))
  for s in ('Worked','Construction','Pillaged'):
   rows=[]
   for g in n.findall('m_GroupStates/Element'):
    if g.find('m_StateName').get('text')!=s:continue
    vals={v.find('m_ParamName').get('text'):v for v in g.findall('m_Values/m_Values/Element')}
    if vals['Visible'].findtext('m_bValue')=='true':rows.append((g.find('m_MeshName').get('text'),vals['Material'].find('m_ObjectName').get('text')))
   print(s,rows)
 for a in r.findall('.//m_attachmentPoints/m_Points/Element'):
  print('ATTACH',E.tostring(a,encoding='unicode')[:1300])
