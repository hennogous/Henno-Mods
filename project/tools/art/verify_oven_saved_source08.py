import bpy,sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from build_bakery_props import *
def read(path):
 with V.suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
 return {o.name:dict(vertices=[list(v.co) for v in o.data.vertices],polygons=[list(p.vertices) for p in o.data.polygons],matrix=[list(r) for r in o.matrix_world],weights=[[(g.group,g.weight) for g in v.groups] for v in o.data.vertices],UV1=[list(v.uv) for v in o.data.uv_layers[0].data],UV2=[list(v.uv) for v in o.data.uv_layers[1].data],UV3=[list(v.uv) for v in o.data.uv_layers[2].data]) for o in bpy.data.scenes['Export'].objects if o.type=='MESH'}
rows=[]
for ident in IDS:
 a=read(SOURCE.parent/'revision-07-prop-kit'/(ident+'.blend'));b=read(SOURCE/(ident+'.blend'));changed=0
 assert a.keys()==b.keys()
 for name,x in a.items():
  y=b[name];changed+=sum(u!=v for u,v in zip(x['UV3'],y['UV3']))
  if ident.endswith('Oven_v2'):x.pop('UV3');y.pop('UV3')
  assert x==y,(ident,name)
 assert (changed>0)==ident.endswith('Oven_v2')
 rows.append(dict(asset=ident,all_geometry_UV1_UV2_weights_transforms_exact=True,changed_UV3_loops=changed))
(OUT/'saved-source-preservation.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows))
