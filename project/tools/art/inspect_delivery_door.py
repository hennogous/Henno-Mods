import bpy,json
from pathlib import Path
from mathutils import Vector
OUT=Path(r'C:\Users\Shadow\Desktop\Codex\CSC_Storage_L\delivery-01')
bpy.ops.wm.open_mainfile(filepath=str(OUT/'delivery-context.blend'))
o=bpy.data.objects['CSC_TAILORS_Textile_Workshop_Bldg']
pts=[o.matrix_world@v.co for v in o.data.vertices]
pts=sorted(set(tuple(round(c,3) for c in p) for p in pts if p.z<40 and p.z>-1 and p.y<-170 and p.x<15))
(OUT/'door-vertices.json').write_text(json.dumps(pts));print('DOOR_VERTICES',json.dumps(pts))
s=bpy.data.scenes['Review'];bpy.context.window.scene=s;s.frame_set(1)
cam=s.camera;cam.data.clip_end=5000;cam.data.ortho_scale=140;cam.location=(-20,-450,100)
cam.rotation_euler=(Vector((-10,-178,22))-cam.location).to_track_quat('-Z','Y').to_euler()
s.render.resolution_x=900;s.render.resolution_y=700;s.render.filepath=str(OUT/'door-front.png');bpy.ops.render.render(write_still=True)
