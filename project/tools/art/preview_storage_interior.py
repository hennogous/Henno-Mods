"""Render intact and temporary roof-cutaway views; never alter the source roof."""
import bpy,bmesh,json,re
from pathlib import Path
from mathutils import Vector,Matrix
OUT=Path(r'C:\Users\Shadow\Desktop\Codex\CSC_Storage_L\interior-20261008')
bpy.ops.wm.open_mainfile(filepath=str(OUT/'CSC_Storage_L_Interior.blend'))
s=bpy.data.scenes['Review'];bpy.context.window.scene=s
o=bpy.data.objects['CSC_Storage_L_Bldg'];M=Matrix(json.loads((OUT/'source-transform.json').read_text())['matrix']);inv=M.inverted()
s.render.engine='BLENDER_WORKBENCH';s.display.render_aa='16'
sh=s.display.shading;sh.light='STUDIO';sh.color_type='TEXTURE';sh.show_shadows=True;sh.show_cavity=True
sh.cavity_type='BOTH';sh.curvature_ridge_factor=1.2;sh.curvature_valley_factor=1.1
sh.background_type='WORLD';s.world.color=(.7,.7,.7);s.render.film_transparent=False
if hasattr(sh,'show_backface_culling'):sh.show_backface_culling=True
for mat in bpy.data.materials:
 if not mat.use_nodes:continue
 nodes=[n for n in mat.node_tree.nodes if n.type=='TEX_IMAGE' and n.image]
 base=next((n for n in nodes if re.search(r'(_B[._]|Base.?Col|Albedo|Diffuse)',n.image.name+' '+n.image.filepath,re.I)),None)
 if base:mat.node_tree.nodes.active=base
for ob in s.objects:
 if ob.type=='MESH':ob.data.uv_layers.active_index=0
s.view_settings.view_transform='Standard';s.view_settings.look='None';s.view_settings.exposure=1
s.render.resolution_x=1000;s.render.resolution_y=900;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
cam=s.camera;cam.data.type='ORTHO';cam.data.ortho_scale=160;cam.data.clip_end=5000
def view(label,point,target):
 cam.location=M@Vector(point);aim=M@Vector(target);cam.rotation_euler=(aim-cam.location).to_track_quat('-Z','Y').to_euler()
 s.render.filepath=str(OUT/(label+'.png'));bpy.ops.render.render(write_still=True)
view('01-intact-openings',(-170,-200,160),(2,3,45))
bm=bmesh.new();bm.from_mesh(o.data)
remove=[f for f in bm.faces if min((inv@v.co).z for v in f.verts)>70 and max((inv@v.co).z for v in f.verts)>74]
bmesh.ops.delete(bm,geom=remove,context='FACES');bm.to_mesh(o.data);bm.free()
view('02-roof-cutaway',(-135,-170,220),(2,3,49))
view('03-roof-cutaway-reverse',(170,180,230),(2,3,49))
for mat in o.data.materials:
 nodes=[n for n in mat.node_tree.nodes if n.type=='TEX_IMAGE' and n.image and 'CSC_Atlas_AO2' in n.image.name]
 if nodes:mat.node_tree.nodes.active=nodes[0];nodes[0].image.reload()
o.data.uv_layers.active_index=1;sh.light='FLAT';sh.show_shadows=False;sh.show_cavity=False;s.view_settings.exposure=0
view('04-interior-ao',(-135,-170,220),(2,3,49))
# Historical evidence: original source, shown with a temporary roof cutaway.
bpy.ops.wm.open_mainfile(filepath=r'C:\Users\Shadow\Desktop\Working Files\3D Art\Storage\Storage_L\CSC_Storage_L.pre-ao.blend')
s=bpy.context.scene;s.render.engine='BLENDER_WORKBENCH';s.display.shading.color_type='SINGLE';s.display.shading.single_color=(.55,.55,.55);s.display.shading.show_cavity=True;s.display.shading.show_xray=False
o=bpy.data.objects['CSC_Storage_L_Bldg'];bm=bmesh.new();bm.from_mesh(o.data)
bmesh.ops.delete(bm,geom=[f for f in bm.faces if min(v.co.z for v in f.verts)>54],context='FACES');bm.to_mesh(o.data);bm.free()
data=bpy.data.cameras.new('Inspection');cam=bpy.data.objects.new('Inspection',data);s.collection.objects.link(cam);s.camera=cam
M=Matrix.Identity(4);cam.data.type='ORTHO';cam.data.ortho_scale=150
s.render.resolution_x=1000;s.render.resolution_y=900;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
view('00-original-upper-floor',(-140,-170,190),(0,0,35))
print('INTERIOR_PREVIEW_COMPLETE')
