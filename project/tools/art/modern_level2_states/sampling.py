import bpy,json
from pathlib import Path
P=Path.home()/'Desktop/Working Files/3D Art/Level 2/modern/revision-06-ae/CSC_Level_2_Modern.blend'
bpy.ops.wm.open_mainfile(filepath=str(P),load_ui=False,use_scripts=False)
for name in ('CSC_Fixed_Ground_Front','CSC_Fixed_Upper_Front'):
 o=bpy.data.objects[name];rows=[];uv=o.data.uv_layers[0]
 for p in o.data.polygons:
  for i,j in zip(p.loop_indices,list(p.loop_indices)[1:]+[p.loop_indices[0]]):
   a,b=[o.matrix_world@o.data.vertices[o.data.loops[k].vertex_index].co for k in (i,j)];length=(a-b).length
   if length>1:rows.append(round((uv.data[i].uv-uv.data[j].uv).length*1024/length,3))
 print('SAMPLING',name,sorted(set(rows)))
