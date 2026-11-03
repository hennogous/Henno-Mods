import bpy,sys,json,math
from pathlib import Path
from collections import Counter
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[4];O=Path.home()/'Desktop/Codex/modern-cafe-v1-20261029'
sys.path.insert(0,str(ROOT/'project/tools/blender'))
from csc_scene_validation import suspend_csc_repairs
with suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(Path.home()/'Desktop/Working Files/3D Art/Level 3/CSC_Level_3.blend'),load_ui=False,use_scripts=False)
ob=next(o for o in bpy.data.objects if o.type=='MESH');m=ob.data
norms=Counter()
for p in m.polygons:
 if abs(p.normal.z)<.02:norms[round(math.degrees(math.atan2(p.normal.y,p.normal.x)),2)]+=p.area
print('WALL_NORMALS',norms.most_common(10),flush=True)
data={'vertices':[list(v.co) for v in m.vertices],'faces':[{'v':list(p.vertices),'normal':list(p.normal),'area':p.area,'mat':p.material_index,'uv':[list(m.uv_layers[0].data[i].uv) for i in p.loop_indices]} for p in m.polygons],'materials':[]}
for ma in m.materials:
 data['materials'].append({'name':ma.name,'images':[(n.name,bpy.path.abspath(n.image.filepath)) for n in ma.node_tree.nodes if n.type=='TEX_IMAGE' and n.image]})
(O/'historical-mesh.json').write_text(json.dumps(data))
print('MATERIALS',data['materials'],flush=True)
