"""Find unused storage-quadrant AO space without repacking other sources."""
import bpy,json,numpy as np
from pathlib import Path
ROOT=Path(r'C:\Users\Shadow\Desktop\Working Files\3D Art\Storage')
OUT=Path(r'C:\Users\Shadow\Desktop\Codex\CSC_Storage_L\interior-20261008')
paths=[ROOT/f'Storage_{size}'/f'CSC_Storage_{size}{suffix}.blend' for size in ('S','M','L') for suffix in ('','_CON+PIL')]
paths += [ROOT/'Storage_L/CSC_Storage_L_Crane.blend',ROOT/'Storage_L/CSC_Storage_L.pre-ao.blend']
paths += [ROOT.parent/'Props/CSC_Storage_LeanTo.blend']
polygons=[];found=[]
for path in paths:
 if not path.exists():continue
 bpy.ops.wm.open_mainfile(filepath=str(path));found.append(str(path))
 for o in bpy.data.objects:
  if o.type!='MESH' or 'UV2' not in o.data.uv_layers:continue
  uv=o.data.uv_layers['UV2']
  materials={i for i,m in enumerate(o.data.materials) if m and m.use_nodes and any(n.type=='TEX_IMAGE' and n.image and 'CSC_Atlas_AO2' in n.image.name for n in m.node_tree.nodes)}
  for p in o.data.polygons:
   if p.material_index in materials:polygons.append([list(uv.data[i].uv) for i in p.loop_indices])
(OUT/'ao-existing-uvs.json').write_text(json.dumps({'polygons':polygons,'inspected_sources':found}));print('AO_UVS_INSPECTED')
