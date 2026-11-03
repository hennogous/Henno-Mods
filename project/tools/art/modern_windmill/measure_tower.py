import bpy, sys, json, math
from pathlib import Path
from mathutils import Matrix,Vector
src=Path.home()/'Desktop/Working Files/3D Art/BAKERS/Wind Mill/CSC_BAKERS_Wind_Mill.blend'
bpy.ops.wm.open_mainfile(filepath=str(src))
ob=bpy.data.objects['CSC_BAKERS_Wind_Mill_Tower_Tower']
pts=[ob.matrix_world@v.co for v in ob.data.vertices]
frame=Matrix.Rotation(math.radians(42.3),4,'Z')@Matrix.Translation(Vector((-101,-126,0)))
rings={}
for p in pts:rings.setdefault(round(p.z,1),[]).append(p)
rows=[]
for z,ps in sorted(rings.items()):
    if len(ps)<6:continue
    lo=[min(v[i] for v in ps) for i in range(2)];hi=[max(v[i] for v in ps) for i in range(2)]
    c=Vector(((lo[0]+hi[0])/2,(lo[1]+hi[1])/2,0))
    rows.append({'z':z,'n':len(ps),'center_world':list(c),'center_house':list(frame.inverted()@c),'size':[hi[i]-lo[i] for i in range(2)]})
print(json.dumps(rows,indent=2))
