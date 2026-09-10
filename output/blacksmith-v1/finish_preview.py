import bpy, os
from mathutils import Vector
OUT='/Users/henno.gous/Play/Henno-Mods/output/blacksmith-v1'
scene=bpy.context.scene
for ob in scene.objects:
    if ob.type!='MESH' or ob.name.endswith('_Bldg'):continue
    if ob.name.startswith('70 |'):
        for v in ob.data.vertices:v.co.z-=.08
    if ob.name[:2] in ['60','61','62','63','64']:
        for v in ob.data.vertices:
            v.co=Vector((1.02,-1.1,.05))+(v.co-Vector((1.02,-1.1,.05)))*1.10+Vector((-.08,-.24,-.05))
used={m for ob in scene.objects if ob.type=='MESH' for m in ob.data.materials if m}
for m in used:
    if 'oak structure' in m.name:
        m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.09,.047,.023,1)
    if 'clay roof' in m.name:
        for node in m.node_tree.nodes:
            if node.type=='TEX_BRICK':
                node.inputs['Color1'].default_value=(.38,.095,.033,1)
                node.inputs['Color2'].default_value=(.52,.18,.058,1)
    if 'warm grey masonry' in m.name:
        for node in m.node_tree.nodes:
            if node.type=='TEX_BRICK':
                node.inputs['Color1'].default_value=(.225,.213,.175,1)
                node.inputs['Color2'].default_value=(.34,.315,.26,1)
scene.cycles.use_denoising=True
scene.render.filepath=os.path.join(OUT,'blacksmith-render-v1.png')
# Keep the export-check duplicate aligned with the revised source props.
ob=next(o for o in scene.objects if o.name.endswith('_Bldg'))
for v in ob.data.vertices:
    p=v.co/30
    if -.73<p.x<-.12 and -1.91<p.y<-1.31 and .079<p.z<.701:
        v.co.z-=.08*30
    elif .59<p.x<1.79 and -1.47<p.y<-.73 and .049<p.z<1.10:
        v.co=(Vector((1.02,-1.1,.05))+(p-Vector((1.02,-1.1,.05)))*1.10+Vector((-.08,-.24,-.05)))*30
# Rerun the same CN6 export after these position-only edits.
import importlib.util
spec=importlib.util.spec_from_file_location('cn6_export','/Users/henno.gous/Play/Henno-Mods/project/tools/scripts/io_export_cn6_b4.py');ex=importlib.util.module_from_spec(spec);spec.loader.exec_module(ex)
col=ob.users_collection[0];col.hide_viewport=False
bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);ob.parent.select_set(True);bpy.context.view_layer.objects.active=ob
ex.do_export(os.path.join(OUT,'CSC_BLACKSMITH_Workshop_v1.cn6'),True,True)
col.hide_viewport=True
for area in bpy.context.screen.areas:
    if area.type=='VIEW_3D':
        area.spaces.active.region_3d.view_perspective='CAMERA'
        area.spaces.active.region_3d.view_camera_zoom=5
        area.spaces.active.shading.type='MATERIAL'
        area.spaces.active.overlay.show_overlays=False
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,'CSC_BLACKSMITH_Workshop_v1.blend'))
