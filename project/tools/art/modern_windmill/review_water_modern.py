"""Disposable saved-AST review showing the full riverside foundation and drive."""
import bpy,sys,json,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[4]
OUT=Path(sys.argv[sys.argv.index('--')+1])
sys.path.insert(0,str(ROOT/'project/tools/blender'))
from ae_asset_render_blender import Builder
jobfile=max((OUT/'render-1/CSC_BAKERS_Water_Mill_Modern').glob('*/job.json'),key=lambda p:p.stat().st_mtime)
job=json.loads(jobfile.read_text());review=OUT/'full-review';review.mkdir(exist_ok=True);job['output']=str(review)
bpy.ops.wm.read_factory_settings(use_empty=True)
b=Builder(job,'icon');b.assemble(job['root'],root=True);bpy.context.view_layer.update();b.setup()
sc=b.scene;sc.render.resolution_x=sc.render.resolution_y=1200;sc.render.resolution_percentage=100;sc.cycles.samples=48
cam=sc.camera;cam.data.type='ORTHO';cam.data.ortho_scale=200;cam.data.shift_x=cam.data.shift_y=0
target=Vector((-22,0,13));cam.location=target+Vector((175,-255,170));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
sc.use_nodes=False;sc.render.image_settings.media_type='IMAGE';sc.render.image_settings.file_format='PNG';sc.render.image_settings.color_mode='RGBA';sc.render.image_settings.color_depth='8'
sc.render.filepath=str(OUT/'images/Modern_Water_Mill_Review.png');bpy.ops.render.render(write_still=True)
# Keep a useful standalone review, explicitly not an editable model source.
bpy.ops.wm.save_as_mainfile(filepath=str(review/'Modern_Water_Mill_Review.blend'))
print('FULL_REVIEW_READY',flush=True)
# Bounded source diagnostics for checking reused intake transforms/normals.
path=OUT/'masters/CSC_BAKERS_Water_Mill_Modern/CSC_BAKERS_Water_Mill_Modern.blend'
bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False);bpy.context.window.scene=bpy.data.scenes['Export'];bpy.context.view_layer.update()
for o in bpy.context.scene.objects:
    if o.type=='MESH' and 'Intake_' in o.name:
        pts=[o.matrix_world@v.co for v in o.data.vertices]
        print(o.name,'bounds',[[round(f(p[i] for p in pts),2) for i in range(3)] for f in (min,max)],'normals',[[round(x,2) for x in o.matrix_world.to_3x3()@p.normal] for p in o.data.polygons] if 'Roof' in o.name else '')
