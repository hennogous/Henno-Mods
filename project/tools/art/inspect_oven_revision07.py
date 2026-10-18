import bpy,sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from bakery_props_atlas import SOURCE,OUT
bpy.ops.wm.open_mainfile(filepath=str(SOURCE/'CSC_BAKERS_Oven_v2.blend'),load_ui=False,use_scripts=False)
rows=[]
for o in bpy.data.scenes['Export'].objects:
 if o.type!='MESH':continue
 for p in o.data.polygons:
  uv=[tuple(o.data.uv_layers[0].data[l].uv) for l in p.loop_indices];slot=[(int(u*8),int((1-v)*8)) for u,v in uv]
  if (2,4) not in slot:continue
  rows.append(dict(face=p.index,normal=list(p.normal),vertices=[list(o.matrix_world@o.data.vertices[v].co) for v in p.vertices],uv=uv))
(OUT/'oven-existing-brick-faces.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows))
