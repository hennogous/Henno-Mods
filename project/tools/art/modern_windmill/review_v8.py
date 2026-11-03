"""Concept-matched and construction-detail review for the corrected roof revision."""
import bpy,sys,math,json,runpy
from pathlib import Path
from mathutils import Matrix,Vector
OUT=Path(sys.argv[sys.argv.index('--')+1]);ROOT=Path(__file__).resolve().parents[4]
runpy.run_path(str(ROOT/'project/tools/art/modern_windmill/render_concept_angle.py'),run_name='__main__')
(OUT/'modern_v5_concept_angle.png').replace(OUT/'modern_v8_concept_angle.png')
sc=bpy.data.scenes['Review'];cam=sc.camera;sc.render.resolution_x=sc.render.resolution_y=1024;sc.cycles.samples=24
frame=Matrix.Rotation(math.radians(42.3),4,'Z')@Matrix.Translation(Vector((-101,-126,0)))
for name,point,direction,scale in [('roof_detail',(-28,0,64),(-3,-4,2.8),95),('silo_detail',(30,-80,83),(-3,-4,2.8),105),('rear',(10,-28,50),(3,4,3),225)]:
    target=frame@Vector(point);offset=frame.to_3x3()@Vector(direction).normalized()*500
    cam.location=target+offset;cam.rotation_euler=(-offset).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale
    sc.render.filepath=str(OUT/f'modern_v8_{name}.png');bpy.ops.render.render(write_still=True)
checks={}
for o in bpy.data.scenes['Export'].objects:
    if o.type=='MESH' and ('Foundation' in o.name or 'Support_Foot' in o.name):checks[o.name]=min((o.matrix_world@v.co).z for v in o.data.vertices)
assert all(z<=-29.99 for z in checks.values()),checks
(OUT/'foundation-check.json').write_text(json.dumps(checks,indent=2));print('V8_REVIEW_COMPLETE',flush=True)
