import bpy,sys
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).parent))
from bakery_props_atlas import SOURCE,OUT
bpy.ops.wm.open_mainfile(filepath=str(SOURCE/'CSC_BAKERS_Oven_v2.blend'),load_ui=False,use_scripts=False);s=bpy.data.scenes['Review'];bpy.context.window.scene=s
for im in bpy.data.images:
 if im.source=='FILE' and im.users:im.reload()
nt=s.world.node_tree;out=next(n for n in nt.nodes if n.type=='OUTPUT_WORLD');old=out.inputs[0].links[0].from_socket;bg=nt.nodes.new('ShaderNodeBackground');bg.inputs[0].default_value=(.78,.77,.74,1);lp=nt.nodes.new('ShaderNodeLightPath');mix=nt.nodes.new('ShaderNodeMixShader');nt.links.new(lp.outputs['Is Camera Ray'],mix.inputs[0]);nt.links.new(old,mix.inputs[1]);nt.links.new(bg.outputs[0],mix.inputs[2]);nt.links.new(mix.outputs[0],out.inputs[0]);s.render.film_transparent=False;s.render.resolution_x=900;s.render.resolution_y=900;s.render.resolution_percentage=100;s.cycles.samples=24;s.render.image_settings.media_type='IMAGE';s.render.image_settings.views_format='INDIVIDUAL';s.render.image_settings.file_format='JPEG';s.render.image_settings.color_mode='RGB';s.render.image_settings.quality=95
for name,offset,transform in [('Hero',(130,-180,130),'AgX'),('Bright',(130,-180,130),'Standard'),('Top',(0,-.01,220),'Standard'),('High',(100,-150,260),'Standard'),('Rear',(-130,180,150),'Standard')]:
 target=Vector((0,0,40));s.camera.location=target+Vector(offset);s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=110;s.view_settings.view_transform=transform;s.view_settings.exposure=0;s.render.filepath=str(OUT/('Oven_'+name+'.jpg'));bpy.ops.render.render(write_still=True)
