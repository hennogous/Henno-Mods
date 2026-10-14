"""Render the loading-bay finish at normal speed from the open side."""
from pathlib import Path
source=Path(__file__).with_name('preview_storage_delivery.py').read_text()
exec(source[:source.index("frames=OUT/'preview-frames'")])
s.frame_set(1261);rig=bpy.data.objects['CSC_Storage_Crane_Rig']
landing=(rig.matrix_world@rig.pose.bones['Cargo'].matrix).translation.copy()
s.frame_set(841);pickup=(rig.matrix_world@rig.pose.bones['Cargo'].matrix).translation.copy()
inward=landing-pickup;inward.z=0;inward.normalize()
target=landing+Vector((0,0,5));cam.location=target-inward*150+Vector((0,0,75))
cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=110
s.render.resolution_x=660;s.render.resolution_y=660
frames=OUT/'cargo-preview-frames';frames.mkdir(exist_ok=True)
for i,f in enumerate(range(1201,1412,3)):
 s.frame_set(f);s.render.filepath=str(frames/f'{i:04d}.png');bpy.ops.render.render(write_still=True)
print('CARGO_PREVIEW_COMPLETE')
