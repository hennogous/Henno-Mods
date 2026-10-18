import bpy,sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from bakery_props_atlas import SOURCE,OUT
bpy.ops.wm.open_mainfile(filepath=str(SOURCE/'CSC_BAKERS_Oven_v2.blend'),load_ui=False,use_scripts=False);rows=[]
for o in bpy.data.scenes['Export'].objects:
 if o.type!='MESH':continue
 for p in o.data.polygons:
  uv1=[list(o.data.uv_layers[0].data[l].uv) for l in p.loop_indices];uv3=[list(o.data.uv_layers[2].data[l].uv) for l in p.loop_indices]
  if any(.378<u<.497 and .003<v<.122 for u,v in uv1) or any(u>.1 for u,v in uv3):rows.append(dict(face=p.index,vertices=[list(o.matrix_world@o.data.vertices[v].co) for v in p.vertices],UV1=uv1,UV3=uv3))
(OUT/'opening-face-inspection.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows))
