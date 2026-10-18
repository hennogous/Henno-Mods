"""Read-only final oven rear review, preserving the validated source file."""
import bpy,sys,hashlib
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).parent))
from build_bakery_props import SOURCE,OUT,V
p=SOURCE/'CSC_BAKERS_Oven_v2.blend';before=hashlib.sha256(p.read_bytes()).hexdigest()
with V.suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(p),load_ui=False,use_scripts=False)
for im in bpy.data.images:
 if im.source=='FILE' and im.users and Path(bpy.path.abspath(im.filepath)).exists():im.reload()
s=bpy.data.scenes['Review'];parts=[o for o in bpy.data.scenes['Export'].objects if o.type=='MESH'];points=[o.matrix_world@v.co for o in parts for v in o.data.vertices];lo=Vector([min(p[i] for p in points) for i in range(3)]);hi=Vector([max(p[i] for p in points) for i in range(3)]);center=(lo+hi)*.5;size=max(hi-lo)
s.camera.location=center+Vector((-1.2,1.6,1.1))*size;s.camera.rotation_euler=(center-s.camera.location).to_track_quat('-Z','Y').to_euler();bpy.context.window.scene=s;s.render.filepath=str(OUT/'CSC_BAKERS_Oven_v2-rear.png');bpy.ops.render.render(write_still=True)
assert hashlib.sha256(p.read_bytes()).hexdigest()==before
print('Final rear refreshed; validated source unchanged')
