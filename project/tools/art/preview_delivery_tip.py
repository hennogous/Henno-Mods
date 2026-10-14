"""Preview the optional sack bone with the production closed-sack model shape."""
from pathlib import Path
source=Path(__file__).with_name('preview_storage_delivery.py').read_text()
exec(source[:source.index("frames=OUT/'preview-frames'")])
sack=bpy.data.objects['REVIEW_Closed_Sack_TipUpright'];sack.hide_render=False;sack.hide_set(False)
bale=next(o for o in bpy.data.scenes['Export'].objects if o.type=='MESH' and 'Textile_Bale' in o.name);bale.hide_render=True
rig=bpy.data.objects['CSC_Storage_Crane_Rig'];s.frame_set(841)
pickup=(rig.matrix_world@rig.pose.bones['Cargo'].matrix).translation.copy()
s.frame_set(1261);landing=(rig.matrix_world@rig.pose.bones['Cargo'].matrix).translation.copy()
inside=landing-pickup;inside.z=0;inside.normalize()
target=pickup+Vector((0,0,20));cam.location=target-inside*135+Vector((0,0,65))
cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=105
s.render.resolution_x=660;s.render.resolution_y=660
frames=OUT/'tip-preview-frames';frames.mkdir(exist_ok=True)
for i,f in enumerate(range(781,1022,3)):
 s.frame_set(f);s.render.filepath=str(frames/f'{i:04d}.png');bpy.ops.render.render(write_still=True)
print('TIP_PREVIEW_COMPLETE')
