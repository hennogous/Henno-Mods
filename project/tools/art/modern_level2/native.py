"""Native-format checks for the first authoring version; no live mod/AE mutations."""
import sys,json,subprocess,shutil,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT/'project/tools/art/modern_windmill'))
import modular_v9_native as n
O=Path.home()/'Desktop/Codex/modern-level2-v1-20261028';D=Path.home()/'Desktop/Working Files/3D Art/Level 2/modern/revision-01-concept-base'
O=Path(os.environ.get('CSC_LEVEL2_OUTPUT',str(O)));D=Path(os.environ.get('CSC_LEVEL2_MASTERS',str(D)))
(O/'native').mkdir(exist_ok=True);exe,_=n.helper(O/'native-reader');converter=ROOT/'project/tools/cn6libs/CN6ToFGX.exe';report=[]
for ident in os.environ.get('CSC_LEVEL2_NATIVE_IDS','CSC_Level_2_Modern,CSC_Level_2_Modern_Workshop').split(','):
 m=json.loads((O/'models'/(ident+'.json')).read_text());cn6=O/'native'/(ident+'.cn6');fgx=O/'native'/(ident+'.fgx');n.exp.write_cn6(cn6,m)
 r=subprocess.run([str(converter),str(cn6),str(fgx),'2'],cwd=converter.parent,capture_output=True,text=True);assert r.returncode==0,r.stdout+r.stderr
 path=O/'native'/(ident+'.json');subprocess.run([str(exe),str(exe.parent),str(fgx),str(path)],cwd=exe.parent,capture_output=True,check=True);native=json.loads(path.read_text());err=0
 for a,b in zip(m['meshes'],native['meshes']):
  assert a['triangles']==b['triangles'] and len(a['vertices'])==len(b['vertices']) and b['boneBindings']==['Bone']
  for v,w in zip(a['vertices'],b['vertices']):
   values=w['position']+w['normal']+w['tangent']+w['binormal']+w['uv']+w['uv2']+w['uv3'];err=max(err,max(abs(x-y) for x,y in zip(v,values)));assert w['boneWeights']==[255,0,0,0,0,0,0,0] and w['boneIndices']==[0]*8
 assert err<1e-4,err
 destinations={r['id']:Path(r['blend']).parent for r in json.loads((O/'masters.json').read_text())} if (O/'masters.json').exists() else {}
 shutil.copy2(cn6,destinations.get(ident,D)/cn6.name);report.append({'id':ident,'native_geometry_UVs_topology_weights':True,'max_component_error':err})
(O/'native-validation.json').write_text(json.dumps(report,indent=2));print('NATIVE_CHECKS_PASS',report)
