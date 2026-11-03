import bpy,json,sys,math
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[4];A=Path.home()/'Desktop/Working Files/3D Art';O=Path.home()/'Desktop/Codex/modern-cafe-v1-20261029'
sys.path.insert(0,str(ROOT/'project/tools/blender'));from csc_scene_validation import suspend_csc_repairs
with suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(A/'BAKERS/Cafe/modern/revision-01-garden/CSC_BAKERS_Cafe_Modern_Review.blend'),load_ui=False,use_scripts=False)
s=bpy.data.scenes['Review'];bpy.context.window.scene=s;s.use_nodes=False;s.cycles.samples=32;s.render.resolution_x=s.render.resolution_y=1000;s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.image_settings.color_depth='8'
R=Matrix.Rotation(math.radians(-28.26),4,'Z');target=R@Vector((88,113,23));s.camera.location=target+R.to_3x3()@Vector((12,-120,18));s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=89
for ob in s.objects:
 if ob.type=='MESH' and ob.get('module')!='Building':ob.hide_render=True
s.render.filepath=str(O/'review/Interior_Day_Close.png');bpy.ops.render.render(write_still=True)
links=[]
for ma in bpy.data.materials:
 if ma.use_nodes and ma.name.startswith(('CSC_BAKERS_Modern','CSC_BAKERS_Interiors_Modern')):
  bs=next(n for n in ma.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
  for link in list(bs.inputs['Normal'].links):links.append((ma,link.from_socket,link.to_socket));ma.node_tree.links.remove(link)
s.render.filepath=str(O/'review/Interior_B_Only.png');bpy.ops.render.render(write_still=True)
for ma,a,b in links:ma.node_tree.links.new(a,b)
for ma in bpy.data.materials:
 if ma.use_nodes and ma.name.startswith(('CSC_BAKERS_Modern','CSC_BAKERS_Interiors_Modern')):
  bs=next(n for n in ma.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
  for link in list(bs.inputs['Base Color'].links):ma.node_tree.links.remove(link)
  bs.inputs['Base Color'].default_value=(.45,.45,.45,1)
s.render.filepath=str(O/'review/Interior_N_Only.png');bpy.ops.render.render(write_still=True)
print('PAINT_NORMAL_DIAGNOSTICS_RENDERED',flush=True)
