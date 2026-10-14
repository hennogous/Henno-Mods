"""Resolve appended sack images to its source package and refresh image buffers."""
import bpy
from pathlib import Path
BASE=Path(r'C:\Users\Shadow\Desktop\Codex\CSC_Storage_L\delivery-01')
ROOT=Path(r'C:\Users\Shadow\Desktop\Working Files\3D Art\Props\Bakers\Bakers_Flour_FINAL\textures')
bpy.ops.wm.open_mainfile(filepath=str(BASE/'CSC_TAILORS_Storage_Delivery.blend'))
obj=bpy.data.objects['REVIEW_Closed_Sack_TipUpright']
for mat in obj.data.materials:
 for n in mat.node_tree.nodes:
  if n.type=='TEX_IMAGE' and n.image:
   im=n.image;candidate=ROOT/Path(im.filepath).name
   print('SACK_IMAGE',im.name,im.filepath,'->',str(candidate),candidate.is_file())
   assert candidate.is_file(),candidate
   im.filepath=str(candidate);im.reload()
bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'CSC_TAILORS_Storage_Delivery.blend'))
