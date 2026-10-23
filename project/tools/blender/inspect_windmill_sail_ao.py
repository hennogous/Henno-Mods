"""Read sail geometry and UV charts for an AO overlap diagnosis."""
import bpy,json,sys
from pathlib import Path
out=Path(sys.argv[sys.argv.index('--')+1]);out.mkdir(parents=True,exist_ok=True)
source=Path.home()/'Desktop/Working Files/3D Art/BAKERS/Wind Mill/tower/CSC_BAKERS_Wind_Mill_Tower.blend'
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
ob=bpy.data.objects['CSC_BAKERS_Wind_Mill_Tower_Sails'];me=ob.data;me.calc_loop_triangles()
data=dict(vertices=[list(v.co) for v in me.vertices],polygons=[dict(id=f.index,verts=list(f.vertices),normal=list(f.normal),uv1=[list(me.uv_layers['UV1'].data[i].uv) for i in f.loop_indices],uv2=[list(me.uv_layers['UV2'].data[i].uv) for i in f.loop_indices]) for f in me.polygons],triangles=[dict(face=t.polygon_index,verts=list(t.vertices),uv=[list(me.uv_layers['UV2'].data[i].uv) for i in t.loops]) for t in me.loop_triangles])
(out/'sail-source.json').write_text(json.dumps(data))
print('SAIL_INSPECTED',len(me.vertices),len(me.polygons))
