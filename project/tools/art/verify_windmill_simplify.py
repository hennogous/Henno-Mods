"""Audit native output, canonical surface/AO bounds and installed files."""
import sys,json,hashlib,struct
from pathlib import Path
import numpy as np
from PIL import Image
OUT=Path(sys.argv[1]);ROOT=Path(__file__).resolve().parents[3];MOD=ROOT/'Civ Supply Chains';NAME='CSC_BAKERS_Wind_Mill_Tower';RUIN=NAME+'_CON+PIL';LIB=Path.home()/'Desktop/Working Files/3D Art/Textures/CSC_Props'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
installed='--installed' in sys.argv;oldlib=OUT/'before-library' if installed else LIB/'Current';newlib=OUT/'atlas-release';report={}
for k in 'BNGM':
 a=np.array(Image.open(oldlib/'textures'/('CSC_Props_Shared_01_'+k+'.png')).convert('RGB'));b=np.array(Image.open(newlib/'textures'/('CSC_Props_Shared_01_'+k+'.png')).convert('RGB'));mask=np.zeros((1024,1024),bool);mask[512:640,768:896]=True;assert np.array_equal(a[~mask],b[~mask])
 if k in 'BN':assert (a[mask]!=b[mask]).any()
report['outside_surface_slot38_preserved']=True
a=np.array(Image.open(oldlib/'textures/CSC_Props_Shared_01_AO.png').convert('RGB'));b=np.array(Image.open(newlib/'textures/CSC_Props_Shared_01_AO.png').convert('RGB'));mask=np.zeros((2048,2048),bool);mask[128:512,:512]=True;mask[:128,384:512]=True;assert np.array_equal(a[~mask],b[~mask]);assert (b[:128,384:512]==255).all()
report['unused_window_AO_reclaimed']=True
plan=json.loads((OUT/'install-plan.json').read_text());quarter=next(r for r in plan if r['destination'].endswith('CSC_Atlas_AO2.png'));a=np.array(Image.open(quarter['backup']).convert('RGB'));b=np.array(Image.open(quarter['source']).convert('RGB'));mask=np.zeros((1024,1024),bool);mask[976:1020,516:580]=True;mask[976:1020,584:648]=True;assert np.array_equal(a[~mask],b[~mask])
counts={}
for name in [NAME,RUIN]:
 raw=json.loads((OUT/(name+'-native.json')).read_text());counts[name]={m['name']:dict(vertices=len(m['vertices']),triangles=len(m['triangles'])) for m in raw['meshes']}
 for m in raw['meshes']:
  assert m['boneBindings']==(['Sails'] if m['name'].endswith('_Sails') else ['Root'])
  assert len(m['groups'])==1 and m['groups'][0]['count']==len(m['triangles'])
  assert all(v['boneIndices'][0]==0 and v['boneWeights'][0]==255 and sum(v['boneWeights'])==255 for v in m['vertices'])
report['native_counts']=counts
code=Path(__file__).with_name('verify_windmill_wood.py').read_text();code=code[code.index('def fnv(s):'):code.index('if installed:')].replace('cook-wood','cook-simplify');exec(compile(code,'cooked_formats','exec'));report['cooked_formats']=cooked
for p,h in json.loads((OUT/'baseline.json').read_text()).items():
 if Path(p).suffix in ['.ast','.fgx']:assert sha(p)==h,p
assert len(json.loads((OUT/'source-edit-preservation.json').read_text()))==5
report['source_edit_preservation_verified']=True
if installed:
 for r in plan:
  if sha(r['source'])!=sha(r['destination']):
   assert Path(r['destination']).suffix=='.dds';a=np.array(Image.open(r['source']).convert('RGB'));b=np.array(Image.open(r['destination']).convert('RGB'));assert np.array_equal(a,b),r['destination']
 for p in newlib.rglob('*'):
  if p.is_file():assert sha(p)==sha(LIB/'Current'/p.relative_to(newlib))==sha(LIB/'Releases/2026-10-22_Shared_01_r040'/p.relative_to(newlib))
 report['installed_verified']=True
(OUT/('final-verification.json' if installed else 'prepublication-verification.json')).write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
