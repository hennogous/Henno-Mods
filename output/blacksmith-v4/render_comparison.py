import bpy,os
from mathutils import Vector
OUT='/Users/henno.gous/Play/Henno-Mods/output/blacksmith-v4'
v4=bpy.data.scenes['CSC_BLACKSMITH_Workshop_v4'];v3=bpy.data.scenes['CSC_BLACKSMITH_Workshop_v3']
sc=bpy.data.scenes.new('Blacksmith | shape comparison');bpy.context.window.scene=sc
sc.world=v4.world.copy();sc.render.engine='CYCLES';sc.cycles.samples=48;sc.cycles.use_denoising=True
sc.view_settings.view_transform='AgX';sc.view_settings.look='AgX - Medium High Contrast';sc.view_settings.exposure=-.30
sc.render.resolution_x=1600;sc.render.resolution_y=900;sc.render.resolution_percentage=100
sc.render.image_settings.file_format='PNG';sc.render.filepath=OUT+'/shape-comparison-v3-v4.png'
clay=bpy.data.materials.new('Comparison | clay');clay.use_nodes=True
bs=clay.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.46,.43,.38,1);bs.inputs['Roughness'].default_value=.9
for old in v4.objects:
    if old.type in ['LIGHT','CAMERA'] or old.name.startswith('Preview ground'):
        cp=old.copy();cp.data=old.data.copy();sc.collection.objects.link(cp)
        if cp.type=='LIGHT' and cp.data.type=='POINT':cp.hide_render=True
        if cp.type=='CAMERA':sc.camera=cp;cp.data.ortho_scale=490
right=sc.camera.rotation_euler.to_quaternion()@Vector((1,0,0))
for scene,side in [(v3,-1),(v4,1)]:
    source=next(o for o in scene.objects if o.type=='MESH' and o.name.endswith('_Bldg'))
    cp=source.copy();cp.data=source.data.copy();cp.parent=None;cp.modifiers.clear();sc.collection.objects.link(cp);cp.location=right*(side*117)
    cp.data.materials.clear();cp.data.materials.append(clay)
    for p in cp.data.polygons:p.material_index=0
labelmat=bpy.data.materials.new('Comparison | label');labelmat.diffuse_color=(.06,.055,.05,1);labelmat.use_nodes=True
labelbs=labelmat.node_tree.nodes.get('Principled BSDF');labelbs.inputs['Base Color'].default_value=(.06,.055,.05,1)
for side,label in [(-1,'V3  /  BEFORE'),(1,'V4  /  HEAVIER FORMS')]:
    curve=bpy.data.curves.new(label,'FONT');curve.body=label;curve.align_x='CENTER';curve.size=6.0
    ob=bpy.data.objects.new(label,curve);sc.collection.objects.link(ob)
    # Place labels in a camera-facing plane near the bottom of the frame.
    q=sc.camera.rotation_euler.to_quaternion();target=Vector((0,0,78))
    ob.location=target+q@Vector((side*117,-116,55));ob.rotation_euler=sc.camera.rotation_euler;curve.materials.append(labelmat)
bpy.ops.render.render(write_still=True)
# A real 256px render checks that the new forms remain readable at map scale.
bpy.context.window.scene=v4;v4.cycles.samples=48
v4.render.resolution_x=v4.render.resolution_y=256;v4.render.filepath=OUT+'/blacksmith-thumbnail-v4.png'
bpy.ops.render.render(write_still=True)
