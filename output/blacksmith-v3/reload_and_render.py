import bpy,os
OUT='/Users/henno.gous/Play/Henno-Mods/output/blacksmith-v3'
sc=bpy.data.scenes['CSC_BLACKSMITH_Workshop_v3'];bpy.context.window.scene=sc
obj=next(o for o in sc.objects if o.type=='MESH' and o.name.endswith('_Bldg'))
for node in obj.data.materials[0].node_tree.nodes:
    if node.type=='TEX_IMAGE':
        filename=os.path.basename(node.image.filepath)
        node.image.filepath='//Textures/'+filename
        assert os.path.exists(OUT+'/Textures/'+filename),filename
        node.image.reload()
bpy.ops.wm.save_as_mainfile(filepath=OUT+'/CSC_BLACKSMITH_Workshop_v3.blend',relative_remap=False)
bpy.ops.render.render(write_still=True)
sc.render.resolution_x=256;sc.render.resolution_y=256;sc.cycles.samples=64
sc.render.filepath=OUT+'/blacksmith-thumbnail-v3.png'
bpy.ops.render.render(write_still=True)
