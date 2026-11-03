"""Read-only Firaxis construction-material and scaffold inventory."""
import sys,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT/'project/tools/blender'))
from render_ae_asset import read_xml,txt,values,Resolver,Assembly,DEFAULT_SDK,prepare_geometry,PRESETS
OUT=Path.home()/'Desktop/Codex/modern-l1-states-20261028';r=Resolver(ROOT/'Civ Supply Chains',DEFAULT_SDK)
paths=[p for p in DEFAULT_SDK.rglob('*.ast') if 'Modern' in p.name and any(x in p.name for x in ('Market','Factory','Bank','Library','Workshop','Barracks','CityCenter'))]
paths+=[r.resolve('PROP_Scaffold_'+x,'.ast') for x in 'ABC']
rows=[]
for p in paths:
 root=read_xml(p);record={'asset':p.stem,'source':str(p),'construction':[]}
 for m in root.findall('m_GeometrySet/m_ModelInstances/Element'):
  for s in m.findall('m_GroupStates/Element'):
   v=values(s)
   if txt(s,'m_StateName')=='Construction' and v.get('Visible')=='true':record['construction'].append({'geo':txt(m,'m_GeoName'),'mesh':txt(s,'m_MeshName'),'group':txt(s,'m_GroupName'),'material':v.get('Material')})
 rows.append(record)
(OUT/'scaffold-survey.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows,indent=2))
for ident in ('DIS_COM_Market_Modern','PROP_Scaffold_A','PROP_Scaffold_B','PROP_Scaffold_C'):
 a=Assembly(r,'Construction');root=a.asset(r.resolve(ident,'.ast'));folder=OUT/'scaffold-survey'/ident;folder.mkdir(parents=True,exist_ok=True);prepare_geometry(a,OUT/'render-cache',folder)
 job={'root':root,'assets':a.assets,'geometries':a.geometries,'materials':a.materials,'excluded':a.excluded,'warnings':a.warnings,'settings':{'presets':PRESETS,'resolution':700,'samples':24,'camera_class':'auto','render_emission_enabled':False,'state':'Construction'},'output':str(folder)}
 (folder/'job.json').write_text(json.dumps(job,indent=2))
