import bpy,json,numpy as np
from pathlib import Path
out=Path(r'C:\Users\Shadow\Desktop\Codex\Bakery-redo-20261016\production')
pts=[]
for path in [r'C:\Users\Shadow\Desktop\Working Files\3D Art\Props\Bakers\CSC_BAKERS_Oven_v2.blend',r'C:\Users\Shadow\Desktop\Working Files\3D Art\Level 2\Bakers\CSC_BAKERS_Bakery.blend']:
 bpy.ops.wm.open_mainfile(filepath=path,load_ui=False,use_scripts=False);o=bpy.data.objects['CSC_BAKERS_Oven_Bldg'];pts.append(np.array([list(o.matrix_world@v.co) for v in o.data.vertices]))
a,b=pts;aa=a-a.mean(0);bb=b-b.mean(0);u,s,vt=np.linalg.svd(aa.T@bb);r=vt.T@u.T;scale=float(np.linalg.norm(bb)/np.linalg.norm(aa));t=b.mean(0)-scale*r@a.mean(0)
result=dict(scale=scale,rotation=r.tolist(),translation=t.tolist(),residual=float(np.max(np.abs((scale*(r@a.T)).T+t-b))),native_mesh_bounds=[b.min(0).tolist(),b.max(0).tolist()]);(out/'oven-parent-transform.json').write_text(json.dumps(result,indent=2));print(result)
