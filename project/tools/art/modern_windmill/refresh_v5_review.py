import bpy,sys,json,ast
from pathlib import Path
from mathutils import Matrix
ROOT=Path(__file__).resolve().parents[4];OUT=Path(sys.argv[sys.argv.index('--')+1]);ASSET='CSC_BAKERS_Wind_Mill_Modern'
SOURCE=Path.home()/'Desktop/Working Files/3D Art/BAKERS/Wind Mill/CSC_BAKERS_Wind_Mill.blend'
bpy.ops.wm.open_mainfile(filepath=str(OUT/(ASSET+'.blend')))
review=bpy.data.scenes['Review'];light=next(o for o in review.objects if o.type=='LIGHT')
light_settings=(tuple(light.rotation_euler),light.data.energy,tuple(light.data.color),light.data.angle)
world_settings=(tuple(review.world.node_tree.nodes['Background'].inputs['Color'].default_value),review.world.node_tree.nodes['Background'].inputs['Strength'].default_value)
presets=json.loads((ROOT/'project/tools/blender/ae_render_camera_presets.json').read_text())['classes']['L1']
tree=ast.parse((Path(__file__).parent/'build_v5_position.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='configure'],type_ignores=[]),'<comparison setup>','exec'))
for label in ('modern_v5','historical'):
    if label=='historical':bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
    review=bpy.data.scenes['Review'];configure(review)
    # Source-model comparison overscan only, not a replacement production preset.
    # The historical sail tips exceed L1 icon registration; widen both views equally.
    review.camera.data.lens*=.8;review.camera.data.shift_y*=.8
    for ob in review.objects:
        if ob.name.startswith('REVIEW_Ground'):
            if max(abs(v.co.x) for v in ob.data.vertices)<1000:
                for v in ob.data.vertices:v.co.x*=10;v.co.y*=10
    review.render.filepath=str(OUT/(label+'_icon_angle.png'))
    if label=='modern_v5':bpy.ops.wm.save_as_mainfile(filepath=str(OUT/(ASSET+'.blend')),relative_remap=False)
    bpy.ops.render.render(write_still=True)
