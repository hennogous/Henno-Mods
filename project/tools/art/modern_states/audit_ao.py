import bpy,bmesh,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
O=Path.home()/'Desktop/Codex/modern-l1-ao-fix-20261028';O.mkdir(exist_ok=True)
A=Path.home()/'Desktop/Working Files/3D Art'
p=A/'Level 1/modern/CON+PIL/revision-01/CSC_Level_1_S_Modern_CON+PIL.blend'
bpy.ops.wm.open_mainfile(filepath=str(p),load_ui=False,use_scripts=False);bpy.context.window.scene=bpy.data.scenes['Export'];rows=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data);closed=all(e.is_manifold for e in bm.edges);vol=bm.calc_volume(signed=True);bm.free()
 row={'name':o.name,'closed':closed,'volume':vol,'uvs':[(u.name,u.active_render) for u in o.data.uv_layers]};rows.append(row)
 if o.name.startswith('State_'):print(row)
(O/'geometry-audit.json').write_text(json.dumps(rows,indent=2))
