"""Rear views of the reimported FGX model and unchanged clip, with backface culling."""
import bpy
from pathlib import Path
from mathutils import Vector
OUT=Path(r'C:\Users\Shadow\Desktop\Codex\CSC_Storage_L\delivery-01')
for event in ('load_post','depsgraph_update_post'):
    for cb in list(getattr(bpy.app.handlers,event)):
        if cb.__module__.rsplit('.',1)[-1]=='csc_scene_tools':getattr(bpy.app.handlers,event).remove(cb)
bpy.ops.wm.open_mainfile(filepath=str(OUT/'CSC_TAILORS_Delivery_Native_Export.blend'))
auth=bpy.data.scenes['Export'];bpy.context.window.scene=auth;auth.frame_set(811)
direction=bpy.data.objects['CSC_Delivery_Donkey_Rig'].matrix_world.to_3x3().copy()
material=bpy.data.objects['CSC_Delivery_Donkey_Mesh'].data.materials[0]
material.use_backface_culling=True
s=bpy.data.scenes['Native_Check'];bpy.context.window.scene=s;s.frame_set(811)
mesh=next(o for o in s.objects if o.type=='MESH' and 'Donkey' in o.name)
mesh.data.materials.clear();mesh.data.materials.append(material)
for o in s.objects:
    if o.type=='MESH':o.hide_render=o!=mesh
bpy.context.view_layer.update()
e=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh()
points=[e.matrix_world@v.co for v in m.vertices];e.to_mesh_clear()
lo=Vector(tuple(min(p[i] for p in points) for i in range(3)));hi=Vector(tuple(max(p[i] for p in points) for i in range(3)))
target=(lo+hi)/2
cam=bpy.data.objects.new('Runner_Review_Camera',bpy.data.cameras.new('Runner_Review_Camera'));s.collection.objects.link(cam);s.camera=cam
cam.data.type='ORTHO';cam.data.ortho_scale=82;cam.data.clip_end=5000
sun=bpy.data.objects.new('Runner_Review_Sun',bpy.data.lights.new('Runner_Review_Sun','SUN'));s.collection.objects.link(sun)
sun.data.energy=2.3;sun.rotation_euler=(.35,-.6,-.5)
s.world=bpy.data.worlds.new('Runner_Review_World');s.world.use_nodes=True
s.world.node_tree.nodes['Background'].inputs[0].default_value=(.3,.35,.4,1)
s.world.node_tree.nodes['Background'].inputs[1].default_value=.65
bpy.ops.mesh.primitive_plane_add(size=500,location=(target.x,target.y,lo.z-.1))
ground=bpy.context.object;ground.name='Runner_Review_Ground'
mat=bpy.data.materials.new('Runner_Review_Ground');mat.diffuse_color=(.22,.25,.18,1);ground.data.materials.append(mat)
s.render.engine='BLENDER_EEVEE'
s.render.resolution_x=850;s.render.resolution_y=760;s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX'
for side in (-1,1):
    cam.location=target+direction@Vector((105,side*70,57))
    cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
    s.render.filepath=str(OUT/('runner-repaired-rear-'+('left' if side==-1 else 'right')+'.png'))
    bpy.ops.render.render(write_still=True)
print('NATIVE_RUNNER_PREVIEW_COMPLETE')
