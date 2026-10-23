"""Read-only geometry and saved assembly measurements for the timber revision."""
import bpy,sys,json,bmesh
from pathlib import Path
from mathutils import Vector
OUT=Path(sys.argv[sys.argv.index('--')+1]); ART=Path.home()/'Desktop/Working Files/3D Art'
NAME='CSC_BAKERS_Wind_Mill_Tower'; rows=[]
for name in [NAME,NAME+'_CON+PIL']:
    p=ART/'BAKERS/Wind Mill/tower'/(name+'.blend')
    bpy.ops.wm.open_mainfile(filepath=str(p),load_ui=False,use_scripts=False)
    for o in bpy.data.scenes['Export'].objects:
        if o.type!='MESH':continue
        row=dict(name=o.name,verts=len(o.data.vertices),faces=len(o.data.polygons),materials=[m.name for m in o.data.materials],bounds=[[min(v.co[i] for v in o.data.vertices),max(v.co[i] for v in o.data.vertices)] for i in range(3)])
        if 'Scaffolding' in o.name:
            bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.001)
            unseen=set(bm.verts);parts=[]
            while unseen:
                stack=[unseen.pop()];found=[]
                while stack:
                    v=stack.pop();found.append(v)
                    for e in v.link_edges:
                        n=e.other_vert(v)
                        if n in unseen:unseen.remove(n);stack.append(n)
                parts.append(dict(n=len(found),center=list(sum((v.co for v in found),Vector())/len(found)),bounds=[[min(v.co[i] for v in found),max(v.co[i] for v in found)] for i in range(3)]))
            row['components']=parts;bm.free()
        rows.append(row)
OUT.mkdir(parents=True,exist_ok=True);(OUT/'geometry-inspection.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows))
