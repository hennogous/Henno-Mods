import bpy,math,json,bmesh
from pathlib import Path
from mathutils import Vector,Matrix
O=Path.home()/'Desktop/Codex/modern-level2-v3-details-20261028'
p=Path.home()/'Desktop/Working Files/3D Art/Level 2/CSC_Level_2.blend'
bpy.ops.wm.open_mainfile(filepath=str(p),load_ui=False,use_scripts=False);s=bpy.context.scene;o=bpy.data.objects['CSC_Level_2_Bldg']
R=Matrix.Rotation(math.radians(36),4,'Z');points=[R@(o.matrix_world@v.co) for v in o.data.vertices];floor=[v for v in points if v.z<1];lo=Vector([min(v[i] for v in floor) for i in range(3)]);hi=Vector([max(v[i] for v in floor) for i in range(3)]);centre=(lo+hi)/2;centre.z=0
for v,p0 in zip(o.data.vertices,points):v.co=p0-centre
o.matrix_world=Matrix.Identity(4)
print('HISTORICAL_GROUND_BOUNDS',[list(lo-centre),list(hi-centre)],flush=True)
for q in s.objects:
 if q.type=='MESH':q.hide_render=q!=o
mat=o.data.materials[0];ns=mat.node_tree.nodes;ls=mat.node_tree.links;print('MATERIALS',[(m.name,[(n.name,n.image.filepath if n.image else '') for n in m.node_tree.nodes if n.type=='TEX_IMAGE']) for m in o.data.materials],flush=True)
# Preserve material colour but show openings without lighting/props obscuring them.
bs=ns.get('Principled BSDF');em=ns.new('ShaderNodeEmission')
if bs and bs.inputs['Base Color'].links:ls.new(bs.inputs['Base Color'].links[0].from_socket,em.inputs['Color'])
ls.new(em.outputs[0],ns.get('Material Output').inputs['Surface'])
cam=bpy.data.objects.new('Opening_Camera',bpy.data.cameras.new('Opening_Camera'));s.collection.objects.link(cam);s.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=145;s.render.engine='CYCLES';s.cycles.samples=12;s.render.threads_mode='FIXED';s.render.threads=4;s.render.resolution_x=s.render.resolution_y=900;s.render.resolution_percentage=100;s.render.film_transparent=True;s.render.image_settings.file_format='PNG';s.use_nodes=False;s.view_settings.view_transform='Standard';s.view_settings.exposure=0
for label,pos in [('front',(0,-300,52)),('east',(300,0,52)),('rear',(0,300,52)),('west',(-300,0,52))]:
 target=Vector((0,0,52));cam.location=pos;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(O/'review'/('historical-'+label+'.png'));bpy.ops.render.render(write_still=True)
print('HISTORICAL_OPENINGS_RENDERED')
