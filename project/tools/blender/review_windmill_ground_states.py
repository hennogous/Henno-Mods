"""Check rebased rotor clearance and render terrain-clipped review copies."""
import bpy,bmesh,json,sys
from pathlib import Path
from mathutils import Vector
OUT=Path(sys.argv[sys.argv.index('--')+1]);ROOT=Path(__file__).resolve().parents[3]
source=(ROOT/'project/tools/blender/review_windmill_motion.py').read_text().split('# A tighter hero framing')[0]
source=source.replace("OUT/'review/sv/", "OUT/'review-Worked/sv/").replace('90.94731','63.74731')
exec(compile(source,'clearance','exec'))
assert not collisions
for state in ('Worked','Construction','Pillaged'):
    bpy.ops.wm.open_mainfile(filepath=str(OUT/f'review-{state}/sv/CSC_BAKERS_Wind_Mill_sv.blend'),load_ui=False,use_scripts=False)
    scene=bpy.context.scene
    for ob in scene.objects:
        if ob.type!='MESH':continue
        bm=bmesh.new();bm.from_mesh(ob.data)
        normal=(ob.matrix_world.transposed().to_3x3()@Vector((0,0,1))).normalized()
        bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=ob.matrix_world.inverted()@Vector((0,0,0)),plane_no=normal,clear_inner=True)
        bm.to_mesh(ob.data);bm.free();ob.data.update()
    scene.camera.data.ortho_scale*=.78
    scene.render.resolution_x=1000;scene.render.resolution_y=1000;scene.render.resolution_percentage=100;scene.cycles.samples=40
    scene.render.image_settings.media_type='IMAGE';scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_depth='8'
    scene.compositing_node_group=None
    scene.render.filepath=str(OUT/('Windmill-'+state+'.png'));bpy.ops.render.render(write_still=True)
print('STATE_PREVIEWS_COMPLETE',flush=True)
