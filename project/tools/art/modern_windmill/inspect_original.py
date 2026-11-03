"""Read-only inventory of the user-selected historical master."""
import bpy,json,sys
from pathlib import Path
from mathutils import Vector
source=Path(sys.argv[sys.argv.index('--')+1]);out=Path(sys.argv[sys.argv.index('--')+2]);out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source))
rows=[]
for o in bpy.data.objects:
    if o.type not in ('MESH','ARMATURE','EMPTY'):continue
    row={'name':o.name,'type':o.type,'scenes':[s.name for s in bpy.data.scenes if o.name in s.objects],'parent':o.parent.name if o.parent else None,'properties':{k:str(v) for k,v in o.items()},'matrix':[list(r) for r in o.matrix_world],'hidden':o.hide_render}
    if o.type=='MESH':
        co=[o.matrix_world@v.co for v in o.data.vertices]
        row.update(vertices=len(o.data.vertices),faces=len(o.data.polygons),materials=[m.name if m else None for m in o.data.materials],uvs=[l.name for l in o.data.uv_layers],bounds=[[min(v[a] for v in co) for a in range(3)],[max(v[a] for v in co) for a in range(3)]])
    rows.append(row)
report={'source':str(source),'scenes':[{ 'name':s.name,'camera':s.camera.name if s.camera else None} for s in bpy.data.scenes],'objects':rows,'images':[{'name':im.name,'path':bpy.path.abspath(im.filepath),'packed':bool(im.packed_file)} for im in bpy.data.images]}
(out/'original-inventory.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
