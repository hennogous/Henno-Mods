"""Remove only zero-area tessellation output; do not alter the user's Blender mesh."""
import json
from pathlib import Path
import numpy as np
O=Path.home()/'Desktop/Codex/modern-bakery-ae-20261028'
p=O/'models/CSC_Level_2_Modern.json';m=json.loads(p.read_text());removed=[]
for mesh in m['meshes']:
 keep=[]
 for i,t in enumerate(mesh['triangles']):
  a,b,c=[np.array(mesh['vertices'][k][:3]) for k in t[:3]]
  if np.linalg.norm(np.cross(b-a,c-a))<1e-8:removed.append({'mesh':mesh['name'],'triangle':i,'coordinates':[list(a),list(b),list(c)]})
  else:keep.append(t)
 mesh['triangles']=keep
assert len(removed)==4
p.write_text(json.dumps(m));(O/'zero-area-export-cleanup.json').write_text(json.dumps(removed,indent=2));print('Removed four zero-area tessellation triangles; saved mesh geometry unchanged')
