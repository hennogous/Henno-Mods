"""Review the resized building and both underground arch continuations."""
import bpy,json,re
from pathlib import Path
from mathutils import Vector,Matrix
OUT=Path(r'C:\Users\Shadow\Desktop\Codex\CSC_Storage_L\foundation-scale-20261009')
bpy.ops.wm.open_mainfile(filepath=str(OUT/'CSC_Storage_L.blend'))
s=bpy.data.scenes['Review'];bpy.context.window.scene=s
r=json.loads((OUT/'edit-check.json').read_text());pivot=Vector(r['pivot'])
M=Matrix.Translation(pivot)@Matrix.Scale(.9,4)@Matrix.Translation(-pivot)@Matrix(r['placement_matrix_before'])
s.render.engine='BLENDER_WORKBENCH';s.display.render_aa='16'
sh=s.display.shading;sh.light='STUDIO';sh.color_type='TEXTURE';sh.show_shadows=True;sh.show_cavity=True
sh.cavity_type='BOTH';sh.curvature_ridge_factor=1.1;sh.curvature_valley_factor=1.1
sh.background_type='WORLD';s.world.color=(.65,.65,.65)
if hasattr(sh,'show_backface_culling'):sh.show_backface_culling=True
for mat in bpy.data.materials:
 if not mat.use_nodes:continue
 images=[n for n in mat.node_tree.nodes if n.type=='TEX_IMAGE' and n.image]
 base=next((n for n in images if re.search(r'(_B[._]|Base.?Col|Albedo|Diffuse)',n.image.name+' '+n.image.filepath,re.I)),None)
 if base:mat.node_tree.nodes.active=base
for o in s.objects:
 if o.type=='MESH':o.data.uv_layers.active_index=0
s.view_settings.view_transform='Standard';s.view_settings.look='None';s.view_settings.exposure=1
s.render.resolution_x=1000;s.render.resolution_y=900;s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG';cam=s.camera;cam.data.type='ORTHO';cam.data.clip_end=5000
for label,point,target,size in [('Building',(-170,-220,130),(2,3,40),150),
 ('Front-Entrance',(65,-165,58),(8,-51,7),58),('Side-Entrance',(-150,-60,55),(-36,3,7),58)]:
 cam.location=M@Vector(point);aim=M@Vector(target);cam.rotation_euler=(aim-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=size
 s.render.filepath=str(OUT/(label+'.png'));bpy.ops.render.render(write_still=True)
print('FOUNDATION_PREVIEWS_COMPLETE')
