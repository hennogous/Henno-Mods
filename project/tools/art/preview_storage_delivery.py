"""Render a compact full-cycle preview; source animation remains at 30 fps."""
import bpy,time,sys,json,re
from pathlib import Path
from mathutils import Vector
OUT=Path(r'C:\Users\Shadow\Desktop\Codex\CSC_Storage_L\delivery-01')
for event in ('load_post','depsgraph_update_post'):
 for cb in list(getattr(bpy.app.handlers,event)):
  if cb.__module__.rsplit('.',1)[-1]=='csc_scene_tools':getattr(bpy.app.handlers,event).remove(cb)
bpy.ops.wm.open_mainfile(filepath=str(OUT/'CSC_TAILORS_Storage_Delivery.blend'))
s=bpy.data.scenes['Review'];bpy.context.window.scene=s
s.render.engine='BLENDER_WORKBENCH';s.display.render_aa='8'
sh=s.display.shading;sh.light='STUDIO';sh.color_type='TEXTURE';sh.show_shadows=True;sh.show_cavity=False
sh.background_type='WORLD';s.world.color=(.8,.8,.8);s.render.film_transparent=False
for mat in bpy.data.materials:
 if not mat.use_nodes:continue
 images=[n for n in mat.node_tree.nodes if n.type=='TEX_IMAGE' and n.image]
 base=next((n for n in images if re.search(r'(_B[._]|Base.?Col|Albedo|Diffuse)',n.image.name+' '+n.image.filepath,re.I)),None)
 if base:mat.node_tree.nodes.active=base
for o in s.objects:
 if o.type=='MESH' and o.data.uv_layers:o.data.uv_layers.active_index=0
 if o.name=='REVIEW_Ground':
  o.color=(.85,.85,.85,1)
  for mat in o.data.materials:mat.diffuse_color=(.8,.8,.8,1)
s.view_settings.view_transform='Standard';s.view_settings.look='None';s.view_settings.exposure=1;s.view_settings.gamma=1
cam=s.camera;cam.data.type='ORTHO';cam.data.ortho_scale=570;cam.data.clip_end=5000
target=Vector((-25,5,20));cam.location=(-560,-700,650);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
s.render.resolution_x=880;s.render.resolution_y=680;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
frames=OUT/'preview-frames';frames.mkdir(exist_ok=True)
start=time.time()
for i,f in enumerate(range(1,2042,5)):
 s.frame_set(f);s.render.filepath=str(frames/f'{i:04d}.png');bpy.ops.render.render(write_still=True)
 if i%30==0:print('PREVIEW_FRAME',i,'SECONDS',time.time()-start,flush=True)
 if '--one' in sys.argv:break
(OUT/'preview-settings.json').write_text(json.dumps({'source_fps':30,'sample_step':5,'playback_fps':12,'speed':2,'source_seconds':68,'preview_seconds':34}))
print('PREVIEW_COMPLETE',time.time()-start)
