"""Render front and rear rotor views from the native saved-assembly reconstruction."""
import bpy,sys,math
from pathlib import Path
from mathutils import Vector
OUT=Path(sys.argv[sys.argv.index('--')+1]);NAME='CSC_BAKERS_Wind_Mill_Tower'
bpy.ops.wm.open_mainfile(filepath=str(OUT/'review-Worked/sv/CSC_BAKERS_Wind_Mill_sv.blend'),load_ui=False,use_scripts=False)
scene=bpy.context.scene;sails=next(o for o in scene.objects if o.type=='MESH' and '/'+NAME+'_Sails/' in o.get('ae_semantic_path',''))
for o in scene.objects:
 if o.type in ['MESH','LIGHT']:o.hide_render=o!=sails
center=sails.matrix_world@Vector((26.99117,-41.48987,63.74731));direction=(sails.matrix_world.to_3x3()@Vector((.5,math.sqrt(3)/2,0))).normalized()
light=bpy.data.lights.new('Rotor review light','SUN');light.energy=2;light.angle=math.radians(20);sun=bpy.data.objects.new(light.name,light);scene.collection.objects.link(sun)
scene.render.resolution_x=700;scene.render.resolution_y=700;scene.render.resolution_percentage=100;scene.cycles.samples=40
scene.render.image_settings.media_type='IMAGE';scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_depth='8';scene.compositing_node_group=None
scene.camera.data.ortho_scale=120
for label,sign in [('Front',-1),('Back',1)]:
 scene.camera.location=center+sign*direction*160
 scene.camera.rotation_euler=(center-scene.camera.location).to_track_quat('-Z','Y').to_euler()
 sun.rotation_euler=scene.camera.rotation_euler
 scene.render.filepath=str(OUT/('Rotor-'+label+'.png'));bpy.ops.render.render(write_still=True)
print('ROTOR_BOTH_SIDES_RENDERED')
