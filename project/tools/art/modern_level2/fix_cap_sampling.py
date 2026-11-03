"""UV1-only correction; preserve final geometry and baked UV2."""
import bpy
from pathlib import Path
O=Path.home()/'Desktop/Codex/modern-level2-v1-20261028'
bpy.ops.wm.open_mainfile(filepath=str(O/'CSC_Level_2_Modern_Assembly.blend'),load_ui=False,use_scripts=False)
for o in bpy.data.scenes['Export'].objects:
 if o.type!='MESH' or not o.name.startswith('CSC_Fixed_Workshop_Sloped_Closure'):continue
 for p in o.data.polygons:
  axis=max(range(3),key=lambda i:abs(p.normal[i]));a,b=([1,2] if axis==0 else [0,2] if axis==1 else [0,1]);coords=[(o.data.vertices[o.data.loops[k].vertex_index].co[a],o.data.vertices[o.data.loops[k].vertex_index].co[b]) for k in p.loop_indices];lo=[min(c[i] for c in coords) for i in (0,1)]
  for j,k in enumerate(p.loop_indices):
   u,v=[(coords[j][i]-lo[i])/32 for i in (0,1)];o.data.uv_layers[0].data[k].uv=((514+u*124)/1024,1-(2+(1-v)*124)/1024)
bpy.ops.wm.save_as_mainfile(filepath=str(O/'CSC_Level_2_Modern_Assembly.blend'),relative_remap=False)
