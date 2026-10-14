"""Read the road decal geometry/UVs used to check delivery path alignment."""
import bpy,json
from pathlib import Path
OUT=Path(r'C:\Users\Shadow\Desktop\Codex\CSC_Storage_L\delivery-01')
bpy.ops.wm.open_mainfile(filepath=str(OUT/'delivery-context.blend'))
s=bpy.data.scenes['Review'];bpy.context.window.scene=s
rows=[]
for o in s.objects:
 if o.type!='MESH' or o.get('delivery_source')!='road_decal':continue
 rows.append({'name':o.name,'hidden':o.hide_render,'vertices':[list(o.matrix_world@v.co) for v in o.data.vertices],
 'polygons':[list(p.vertices) for p in o.data.polygons],
 'uvs':[[list(o.data.uv_layers[0].data[i].uv) for i in p.loop_indices] for p in o.data.polygons],
 'images':[(n.image.name,bpy.path.abspath(n.image.filepath)) for m in o.data.materials if m and m.use_nodes for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image]})
(OUT/'road-reference.json').write_text(json.dumps(rows,indent=2))
print('ROAD_REFERENCE_SAVED')
