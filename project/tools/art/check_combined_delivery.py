import bpy,json
from pathlib import Path
from civ6_animation import core
OUT=Path(r'C:\Users\Shadow\Desktop\Codex\CSC_Storage_L\delivery-01')
for event in ('load_post','depsgraph_update_post'):
 for cb in list(getattr(bpy.app.handlers,event)):
  if cb.__module__.rsplit('.',1)[-1]=='csc_scene_tools':getattr(bpy.app.handlers,event).remove(cb)
bpy.ops.wm.open_mainfile(filepath=str(OUT/'CSC_TAILORS_Storage_Delivery.blend'))
source=bpy.data.scenes['Export'];bpy.context.window.scene=source
def verts(o):
 e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();p=[e.matrix_world@v.co for v in m.vertices];e.to_mesh_clear();return p
frames=[1,151,301,601,721,811,841,901,991,1081,1201,1261,1321,1561,1741,1891,2041]
expected={}
for f in frames:
 source.frame_set(f);expected[f]=verts(bpy.data.objects['CSC_Delivery_Donkey_Mesh'])
s=bpy.data.scenes.new('Check');bpy.context.window.scene=s
core.import_native(OUT/'CSC_TEST_TAILORS_Delivery_Master.anm',OUT/'CSC_TEST_TAILORS_Delivery_Master_Model.fgx',r'C:\Program Files (x86)\CivNexus6_Release-1.3.3\CivNexus6')
errors={}
for f in frames:
 s.frame_set(f);actual=[v for o in s.objects if o.type=='MESH' and 'Donkey' in o.name for v in verts(o)]
 errors[f]=max(min((a-b).length for b in actual) for a in expected[f])
print('COMBINED_DONKEY_ERRORS',errors)
(OUT/'combined-donkey-check.json').write_text(json.dumps(errors,indent=2))
