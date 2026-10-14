"""Close-up review of the workshop exit and return."""
from pathlib import Path
source=Path(__file__).with_name('preview_storage_delivery.py').read_text()
exec(source[:source.index("frames=OUT/'preview-frames'")])
target=Vector((-43,-177,12));cam.location=target+Vector((-210,-235,255))
cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=165
s.render.resolution_x=800;s.render.resolution_y=720
frames=OUT/'workshop-preview-frames';frames.mkdir(exist_ok=True)
for i,f in enumerate(list(range(1,362,5))+list(range(1441,1742,5))):
 s.frame_set(f);s.render.filepath=str(frames/f'{i:04d}.png');bpy.ops.render.render(write_still=True)
print('WORKSHOP_PREVIEW_COMPLETE')
