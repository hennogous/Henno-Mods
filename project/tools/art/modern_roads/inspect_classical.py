"""Read the live classical master; derive external road centerlines from fade UVs."""
import bpy,json,sys,hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT/'project/tools/blender'))
from csc_scene_validation import suspend_csc_repairs
O=Path.home()/'Desktop/Codex/Quarter-Roads-Modern/draft-03-roundabout'
source=Path.home()/'Desktop/Working Files/3D Art/Quarters/CSC_ALL_Classical_Base_05_Road_Decals.blend'
with suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
objects=[];anchors={};names={'NW':'001','NE':'004','E':'003','SE':'005','SW':'006'}
for ob in bpy.data.objects:
 if ob.type!='MESH':continue
 row={'name':ob.name,'vertices':[list(ob.matrix_world@v.co) for v in ob.data.vertices],'faces':[list(p.vertices) for p in ob.data.polygons],'uvs':[list(x.uv) for x in ob.data.uv_layers.active.data],'materials':[m.name for m in ob.data.materials]};objects.append(row)
 for route,num in names.items():
  if ob.name==f'CSC_Road_Fade.{num}_CLA#M':
   verts=[Vector(v) for v in row['vertices']];inner=(verts[0]+verts[3])/2;outer=(verts[1]+verts[2])/2;direction=(outer-inner).normalized()
   anchors[route]={'source_object':ob.name,'inner':list(inner)[:2],'outer':list(outer)[:2],'outward':list(direction)[:2],'card_width':(verts[3]-verts[0]).length}
assert len(anchors)==5
j={'source':str(source),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'objects':objects,'anchors':anchors,'omitted':'Fade.002 is the old sixth, bottom-left spur; explicit new brief has five exits.'}
(O/'classical-live.json').write_text(json.dumps(j,indent=2));print(json.dumps(anchors,indent=2))
