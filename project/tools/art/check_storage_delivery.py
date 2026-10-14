"""Inspect evaluated delivery poses and render review stills without editing sources."""
import bpy,json,sys
from pathlib import Path
from mathutils import Vector
OUT=Path(r'C:\Users\Shadow\Desktop\Codex\CSC_Storage_L\delivery-01')
for event in ('load_post','depsgraph_update_post'):
 for cb in list(getattr(bpy.app.handlers,event)):
  if cb.__module__.rsplit('.',1)[-1]=='csc_scene_tools':getattr(bpy.app.handlers,event).remove(cb)
bpy.ops.wm.open_mainfile(filepath=str(OUT/'CSC_TAILORS_Storage_Delivery.blend'))
s=bpy.data.scenes['Review'];bpy.context.window.scene=s
rig=bpy.data.objects['CSC_Storage_Crane_Rig'];donkey=bpy.data.objects['CSC_Delivery_Donkey_Rig']
bale=next(o for o in bpy.data.scenes['Export'].objects if o.type=='MESH' and 'Textile_Bale' in o.name)
dm=bpy.data.objects['CSC_Delivery_Donkey_Mesh']
report={'mesh_parent':dm.parent.name if dm.parent else None,'rig_parent':donkey.parent.name,'frames':{}}
for f in [1,301,601,721,811,841,901,991,1081,1201,1261,1321,1561,1741,1891,2041]:
 s.frame_set(f);bpy.context.view_layer.update()
 def point(r,n):return list((r.matrix_world@r.pose.bones[n].matrix).translation)
 cargo=point(rig,'Cargo');load=point(rig,'Load')
 report['frames'][f]={'cargo':cargo,'load':load,'cart':point(donkey,'Cart'),'donkey':list(donkey.matrix_world.translation),'bale_origin':list(bale.matrix_world.translation),'cargo_load_distance':(Vector(cargo)-Vector(load)).length}
 if '--render' in sys.argv and f in [1,301,721,991,1201,1261,1561,1891]:
  cam=s.camera;cam.data.type='ORTHO';cam.data.ortho_scale=570;cam.data.clip_end=5000
  target=Vector((-25,5,20));cam.location=(-560,-700,650);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
  s.render.resolution_x=1100;s.render.resolution_y=850;s.render.resolution_percentage=100
  s.render.image_settings.file_format='PNG';s.render.filepath=str(OUT/f'pose-{f:04d}.png');bpy.ops.render.render(write_still=True)
(OUT/'evaluated-check.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
