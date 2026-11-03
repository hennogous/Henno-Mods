import bpy,sys,json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT/'project/tools/blender'))
from ae_asset_render_blender import Builder
OUT=Path.home()/'Desktop/Codex/modern-l1-states-20261028/scaffold-survey'
for folder in OUT.iterdir():
 if not (folder/'job.json').exists():continue
 job=json.loads((folder/'job.json').read_text());bpy.ops.wm.read_factory_settings(use_empty=True);b=Builder(job,'icon');b.assemble(job['root'],root=True);bpy.context.view_layer.update();b.setup();s=b.scene
 ps=[o.matrix_world@v.co for o in b.objects for v in o.data.vertices];lo=Vector(tuple(min(p[i] for p in ps) for i in range(3)));hi=Vector(tuple(max(p[i] for p in ps) for i in range(3)));target=(lo+hi)/2
 s.camera.data.type='ORTHO';s.camera.data.ortho_scale=max(hi-lo)*1.6;s.camera.location=target+Vector((160,-240,180));s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler();s.use_nodes=False;s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.image_settings.color_depth='8';s.render.filepath=str(folder/'render.png');bpy.ops.render.render(write_still=True)
