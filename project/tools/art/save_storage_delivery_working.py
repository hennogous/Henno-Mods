"""Save the separate authored delivery beside the user's unchanged source files."""
import bpy
from pathlib import Path
from mathutils import Vector
OUT=Path(r'C:\Users\Shadow\Desktop\Codex\CSC_Storage_L\delivery-01')
DEST=Path(r'C:\Users\Shadow\Desktop\Working Files\3D Art\Storage\Storage_L\Delivery')
DEST.mkdir(exist_ok=True)
for event in ('load_post','depsgraph_update_post'):
 for cb in list(getattr(bpy.app.handlers,event)):
  if cb.__module__.rsplit('.',1)[-1]=='csc_scene_tools':getattr(bpy.app.handlers,event).remove(cb)
bpy.ops.wm.open_mainfile(filepath=str(OUT/'CSC_TAILORS_Storage_Delivery.blend'))
for im in bpy.data.images:
 if im.source=='FILE':im.filepath=bpy.path.abspath(im.filepath)
s=bpy.data.scenes['Review'];bpy.context.window.scene=s;s.frame_set(1)
cam=s.camera;cam.data.clip_end=5000;cam.data.ortho_scale=570
cam.location=(-560,-700,650);cam.rotation_euler=(Vector((-25,5,20))-cam.location).to_track_quat('-Z','Y').to_euler()
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':
   area.spaces.active.clip_end=5000;v=area.spaces.active.region_3d
   v.view_location=(-25,5,20);v.view_distance=550;v.view_rotation=cam.rotation_euler.to_quaternion();v.view_perspective='ORTHO'
bpy.ops.wm.save_as_mainfile(filepath=str(DEST/'CSC_TAILORS_Storage_Delivery.blend'))
print('WORKING_SOURCE_SAVED')
