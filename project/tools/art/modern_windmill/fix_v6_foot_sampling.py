"""Keep small structural footings on the same stone scale without adding UV split geometry."""
import bpy,sys,math
from pathlib import Path
from mathutils import Vector,Matrix
OUT=Path(sys.argv[sys.argv.index('--')+1]);ASSET='CSC_BAKERS_Wind_Mill_Modern'
bpy.ops.wm.open_mainfile(filepath=str(OUT/(ASSET+'.blend')))
frame=Matrix.Rotation(math.radians(42.3),4,'Z')@Matrix.Translation(Vector((-101,-126,0)));inv=frame.inverted()
for ob in bpy.data.scenes['Export'].objects:
    if ob.type!='MESH' or not ('Support_Foot' in ob.name or ob.name in ('CSC_Fixed_Elevator_Foundation','CSC_Fixed_Intake_Foundation')):continue
    pts=[inv@v.co for v in ob.data.vertices];lo=[min(v[a] for v in pts) for a in range(3)]
    for p in ob.data.polygons:
        n=inv.to_3x3()@p.normal;axis=max(range(3),key=lambda a:abs(n[a]));a=1 if axis==0 else 0
        for li in p.loop_indices:
            v=pts[ob.data.loops[li].vertex_index];u=(v[a]-lo[a])/84;vv=max(0,v.z)/32
            ob.data.uv_layers['UV1'].data[li].uv=((1+.025+.95*u)/4,1-(.025+.95*(1-vv))/4)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/(ASSET+'.blend')),relative_remap=False)
ROOT=Path(__file__).resolve().parents[4]
sys.argv=[str(ROOT/'project/tools/art/modern_windmill/render_concept_angle.py'),'--',str(OUT)]
exec(compile((ROOT/'project/tools/art/modern_windmill/render_concept_angle.py').read_text(),'<matched final render>','exec'))
