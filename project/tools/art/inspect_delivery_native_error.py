"""Locate round-trip differences against the baked native export copy."""
import bpy,json
from pathlib import Path
from civ6_animation import core
OUT=Path(r'C:\Users\Shadow\Desktop\Codex\CSC_Storage_L\delivery-01')
NEXUS=r'C:\Program Files (x86)\CivNexus6_Release-1.3.3\CivNexus6'
bpy.ops.wm.open_mainfile(filepath=str(OUT/'CSC_TAILORS_Delivery_Native_Export.blend'))
s=bpy.data.scenes['Native_Master'];bpy.context.window.scene=s;s.frame_set(1081)
rig=next(o for o in s.objects if o.type=='ARMATURE')
body=next(o for o in s.objects if o.type=='MESH' and 'Donkey' in o.name)
def vertices(o):
 e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();v=[e.matrix_world@p.co for p in m.vertices];e.to_mesh_clear();return v
expected=vertices(body);bones={b.name:b.matrix.copy() for b in rig.pose.bones}
sample=core.parse_na2(OUT/'Master-sampled/clip.na2')[0]
raw={n:core.bone_matrix(v[1080]) for n,v in sample['tracks'].items() if n in bones}
s2=bpy.data.scenes.new('Inspect');bpy.context.window.scene=s2
converted,_=core.import_native(OUT/'CSC_TEST_TAILORS_Delivery_Master.anm',OUT/'CSC_TEST_TAILORS_Delivery_Master_Model.fgx',NEXUS)
s2.frame_set(1081);target=next(o for o in s2.objects if o.type=='MESH' and 'Donkey' in o.name);actual=vertices(target)
rows=sorted([(min((a-b).length for b in actual),i) for i,a in enumerate(expected)],reverse=True)[:8]
report={'worst_vertices':[{'error':err,'vertex':i,'weights':[(body.vertex_groups[g.group].name,g.weight) for g in body.data.vertices[i].groups]} for err,i in rows],
 'bone_errors':{b.name:{'translation':(b.matrix.translation-bones[b.name].translation).length,'matrix':max(abs(b.matrix[i][j]-bones[b.name][i][j]) for i in range(4) for j in range(4)),
 'raw_translation':(raw[b.name].translation-bones[b.name].translation).length,'raw_matrix':max(abs(raw[b.name][i][j]-bones[b.name][i][j]) for i in range(4) for j in range(4))} for b in converted.pose.bones if b.name in bones}}
(OUT/'native-error-diagnostic.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
