"""Review renders only; never save camera changes into the authored master."""
import bpy,sys,math,json,runpy
from pathlib import Path
from mathutils import Matrix,Vector
OUT=Path(sys.argv[sys.argv.index('--')+1]);ROOT=Path(__file__).resolve().parents[4]
runpy.run_path(str(ROOT/'project/tools/art/modern_windmill/render_concept_angle.py'),run_name='__main__')
sc=bpy.data.scenes['Review'];cam=sc.camera
frame=Matrix.Rotation(math.radians(42.3),4,'Z')@Matrix.Translation(Vector((-101,-126,0)))
sc.render.resolution_x=sc.render.resolution_y=1024;sc.cycles.samples=24
for name,point,direction,scale in [
    ('entrance_roof',(-30,-5,40),(-3,-4,2.8),118),
    ('intake',(51.222,-105.259,18),(3,-4,2.5),58),
    ('rear',(10,-28,45),(3,4,3),220),
    ('top',(5,-38,0),(.001,.001,1),210)]:
    target=frame@Vector(point);offset=frame.to_3x3()@Vector(direction).normalized()*500
    cam.location=target+offset;cam.rotation_euler=(-offset).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale
    sc.render.filepath=str(OUT/f'modern_v7_{name}.png');bpy.ops.render.render(write_still=True)
checks={}
for o in bpy.data.scenes['Export'].objects:
    if o.type=='MESH' and ('Foundation' in o.name or 'Support_Foot' in o.name):checks[o.name]=min((o.matrix_world@v.co).z for v in o.data.vertices)
assert all(z<=-29.99 for z in checks.values()),checks
(OUT/'foundation-check.json').write_text(json.dumps(checks,indent=2))
print('REVIEW_COMPLETE',flush=True)
