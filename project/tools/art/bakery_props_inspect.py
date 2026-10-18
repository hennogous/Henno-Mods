import bpy,json
from pathlib import Path
paths=[r'C:\Users\Shadow\Desktop\Working Files\3D Art\Props\Bakers\CSC_BAKERS_Oven_v2.blend',r'C:\Users\Shadow\Desktop\Working Files\3D Art\Level 2\Bakers\CSC_BAKERS_Bakery.blend']
for p in paths:
 bpy.ops.wm.open_mainfile(filepath=p,load_ui=False,use_scripts=False)
 print('INSPECT',json.dumps({'file':p,'scenes':[s.name for s in bpy.data.scenes],'objects':[{'name':o.name,'type':o.type,'loc':list(o.location),'scale':list(o.scale),'rotation':list(o.rotation_euler),'dims':list(o.dimensions),'verts':len(o.data.vertices) if o.type=='MESH' else 0,'materials':[m.name for m in o.data.materials] if o.type=='MESH' else [],'uv':[u.name for u in o.data.uv_layers] if o.type=='MESH' else []} for o in bpy.data.objects],'images':[(i.name,i.filepath) for i in bpy.data.images]}))
 if 'Oven_v2' in p:
  o=next(o for o in bpy.data.objects if o.type=='MESH')
  print('BOUNDS',[[min((o.matrix_world@v.co)[i] for v in o.data.vertices),max((o.matrix_world@v.co)[i] for v in o.data.vertices)] for i in range(3)],'PARENT',o.parent.name if o.parent else None)
  print('UVFACES',json.dumps([[[round(float(c),4) for c in o.data.uv_layers[0].data[l].uv] for l in p.loop_indices] for p in o.data.polygons]))
