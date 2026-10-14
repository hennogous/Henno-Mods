"""Inspect the requested dress's material mapping without modifying sources."""
import bpy,json
from pathlib import Path
ROOT=Path(r'C:\Users\Shadow\Desktop\Working Files\3D Art\TAILORS\Fashion House\revision-12-garden-path')
OUT=Path(r'C:\Users\Shadow\Desktop\Codex\Fashion-dress-mustard-20261013')
OUT.mkdir(parents=True,exist_ok=True)
report={}
for name in ['CSC_TAILORS_Fashion_House_Fitting','CSC_TAILORS_Fashion_House']:
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/(name+'.blend')),load_ui=False,use_scripts=False)
    result=[]
    for o in bpy.data.objects:
        if o.type!='MESH' or not any(s in o.name for s in ['Front_Ivory_Gown_Bell','Ivory_Rounded_Sleeve']):continue
        uv=o.data.uv_layers[0]
        slots={}
        for p in o.data.polygons:
            a=[uv.data[i].uv for i in p.loop_indices];u=sum(x.x for x in a)/len(a);v=sum(x.y for x in a)/len(a)
            slot=int(u*8)+int((1-v)*8)*8;slots[str(slot)]=slots.get(str(slot),0)+1
        result.append(dict(name=o.name,scenes=[s.name for s in o.users_scene],vertices=len(o.data.vertices),slots=slots,images=[bpy.path.abspath(n.image.filepath) for m in o.data.materials if m and m.use_nodes for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image]))
    report[name]=result
(OUT/'inspection.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
