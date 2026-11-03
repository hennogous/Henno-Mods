"""Refresh portable bindings after Save As, and render the final review pass."""
import bpy,sys,json
from pathlib import Path
from mathutils import Vector
OUT=Path(sys.argv[sys.argv.index('--')+1]);ASSET='CSC_BAKERS_Wind_Mill_Modern'
bpy.ops.wm.open_mainfile(filepath=str(OUT/(ASSET+'.blend')))
mat=bpy.data.materials[ASSET]
for ch in ('B','N','G','M','E','AO'):
    im=bpy.data.images.load(str(OUT/'textures'/f'{ASSET}_{ch}.png'),check_existing=False);im.colorspace_settings.name='sRGB' if ch in ('B','E') else 'Non-Color'
    mat.node_tree.nodes[ch].image=im;im.filepath='//textures/'+f'{ASSET}_{ch}.png'
for im in list(bpy.data.images):
    if im.users==0:bpy.data.images.remove(im)
s=bpy.data.scenes['Review'];bpy.context.window.scene=s;target=Vector((35,-176,39));cam=s.camera
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/(ASSET+'.blend')),relative_remap=False)
for name,offset in [('house',Vector((190,-310,240))),('doorway',Vector((-300,-180,210))),('rear',Vector((-180,320,240))),('top',Vector((1,-1,500)))]:
    cam.location=target+offset;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(OUT/f'modern_v2_{name}.png');bpy.ops.render.render(write_still=True)
cam.location=target+Vector((190,-310,240));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/(ASSET+'.blend')),relative_remap=False)
