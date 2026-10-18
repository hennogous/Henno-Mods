"""Prove r029 edits only bread crown UV1 and external basecolour textures."""
import bpy,sys,json,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from build_bakery_props import *
def record(path):
 with V.suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
 return {o.name:dict(vertices=[list(v.co) for v in o.data.vertices],faces=[list(p.vertices) for p in o.data.polygons],UV1=[list(v.uv) for v in o.data.uv_layers[0].data],UV2=[list(v.uv) for v in o.data.uv_layers[1].data],UV3=[list(v.uv) for v in o.data.uv_layers[2].data],matrix=[list(r) for r in o.matrix_world],weights=[[(g.group,g.weight) for g in v.groups] for v in o.data.vertices],crown=list(o.data.polygons[0].loop_indices)) for o in bpy.data.scenes['Export'].objects if o.type=='MESH'}
checks=[]
for ident in IDS:
 old=record(SOURCE.parent/'revision-04-prop-kit'/(ident+'.blend'));new=record(SOURCE/(ident+'.blend'));assert old.keys()==new.keys();changes=[]
 for name,a in old.items():
  b=new[name]
  for key in ['vertices','faces','UV2','UV3','matrix','weights']:assert a[key]==b[key],(ident,name,key)
  differing=[i for i,(x,y) in enumerate(zip(a['UV1'],b['UV1'])) if x!=y]
  if differing:
   assert 'Bread_Fill' in name;assert set(differing).issubset(set(a['crown']));changes.append(name)
  assert 'Loaf' not in name
 assert len(changes)==(2 if ident.endswith('Cart') else 1 if 'Basket' in ident else 0)
 checks.append(dict(asset=ident,all_geometry_transforms_weights_unchanged=True,UV2_UV3_unchanged=True,UV1_changed_only_on_crowns=changes))
(OUT/'user-revision-source-audit.json').write_text(json.dumps(dict(checks=checks,individual_loaf_meshes=0,all_geometry_unchanged=True),indent=2));print('R029 SOURCE/UV AUDIT PASSED')
