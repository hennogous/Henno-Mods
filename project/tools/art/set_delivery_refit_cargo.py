"""Apply the measured cargo fit to authoring previews; native cargo is an AST attachment."""
import bpy,json,hashlib
from pathlib import Path
BASE=Path(r'C:\Users\Shadow\Desktop\Codex\CSC_Storage_L');OUT=BASE/'delivery-refit-20261009'
ROOT=Path(r'C:\Users\Shadow\Desktop\Working Files\3D Art\Storage\Storage_L')
scale=json.loads((OUT/'cargo-fit-check.json').read_text())['selected_scale'];assert scale==.8
for event in ('load_post','depsgraph_update_post'):
 for cb in list(getattr(bpy.app.handlers,event)):
  if cb.__module__.rsplit('.',1)[-1]=='csc_scene_tools':getattr(bpy.app.handlers,event).remove(cb)
for path in (BASE/'delivery-01/CSC_TAILORS_Storage_Delivery.blend',ROOT/'CSC_Storage_L_Crane.blend'):
 bpy.ops.wm.open_mainfile(filepath=str(path));bpy.context.window.scene=bpy.data.scenes['Export'];bpy.context.scene.frame_set(151)
 bale=next(o for o in bpy.context.scene.objects if o.type=='MESH' and 'Textile_Bale' in o.name)
 bpy.context.view_layer.update();old=bale.matrix_world.to_scale()
 assert max(old)-min(old)<1e-5
 bale.parent.scale*=scale/old.x;bpy.context.view_layer.update()
 assert max(abs(v-scale) for v in bale.matrix_world.to_scale())<1e-5
 for text in bpy.data.texts:
  if text.name.startswith('START HERE'):
   body=text.as_string();text.clear();text.write(body.replace('uniform scale 1.0','uniform scale 0.8').replace('widened workshop turn','tightened workshop turn'))
 bpy.context.window.scene=bpy.data.scenes['Review'];bpy.ops.wm.save_as_mainfile(filepath=str(path))
p=BASE/'delivery-01/authoring-check.json';r=json.loads(p.read_text());r['cargo_scale']=scale
r['source_hashes']['crane']=hashlib.sha256((ROOT/'CSC_Storage_L_Crane.blend').read_bytes()).hexdigest()
r['cargo_fit_check']=str(OUT/'cargo-fit-check.json');p.write_text(json.dumps(r,indent=2))
print('CARGO_SIZE_SET',scale)
