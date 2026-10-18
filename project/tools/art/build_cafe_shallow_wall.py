"""Equal-length 15-degree companion to the existing 30-degree garden wall."""
import os,sys,math,json
from pathlib import Path
os.environ['CSC_CAFE_OUTPUT']='C:/Users/Shadow/Desktop/Codex/Cafe/revision-03-shallow-wall'
os.environ['CSC_CAFE_RELEASE']='2026-10-17_Shared_01_r033'
sys.path.insert(0,str(Path(__file__).parent))
import build_cafe_props as C
ID='CSC_ALL_Garden_Wall_Curve_2'
C.setup(ID);C.author('CSC_ALL_Garden_Wall_Curve')
# Preserve arc length and cross-section while changing only the curvature.
for ob in C.PARTS:
    for v in ob.data.vertices:
        x,y,z=v.co;old_angle=math.atan2(x,y+96);offset=math.hypot(x,y+96)-96
        radius=192+offset;angle=old_angle*.5
        v.co=(radius*math.sin(angle),radius*math.cos(angle)-192,z)
    ob['wall_angle_degrees']=15;ob['wall_radius']=192;ob['wall_arc_length']=96*math.pi/6
C.finish(ID,8,ao_index=7)
(C.OUT/'wall-design.json').write_text(json.dumps(dict(asset=ID,original='CSC_ALL_Garden_Wall_Curve',radius=192,angle_degrees=15,arc_length=96*math.pi/6,height=20,buried_footing=4,body_thickness=5,coping_thickness=6.5,original_unchanged=True),indent=2))
