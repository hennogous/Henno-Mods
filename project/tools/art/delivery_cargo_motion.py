"""Current storage reset and optional closed-sack attachment motion."""
import math
from pathlib import Path
from mathutils import Matrix,Vector

TIP_BONE='Cargo_TipUpright'
# Measured clear corner of the placed v10 storage shell; update with any placement refit.
RESET_CORNER_XY=(-31.02756118774414,131.50839233398438)
SACK_SCALE=1.0

def load_sack_points():
 path=Path(r'C:\Users\Shadow\Desktop\Working Files\3D Art\Props\Bakers\Bakers_Flour_FINAL\CSC_ALL_Flour_Sack_Closed.cn6')
 lines=path.read_text().splitlines();a=lines.index('vertices')+1;b=next(i for i in range(a,len(lines)) if lines[i].startswith('triangles'))
 return [Vector(tuple(map(float,line.split()[:3]))) for line in lines[a:b]]

def smooth(x):
 x=max(0,min(1,x));return x*x*(3-2*x)

def reset_pose(stored,t):
 target=stored.copy();target.translation.x,target.translation.y=RESET_CORNER_XY
 below=target.copy();below.translation.z=-100
 pose=stored.copy()
 if t<42.6:return pose
 if t<45.5:pose.translation=stored.translation.lerp(target.translation,smooth((t-42.6)/2.9))
 else:pose.translation=target.translation.lerp(below.translation,smooth((t-45.5)/1.5))
 return pose

def tip_pose(cargo,t,points):
 # Lay along the sled's local X axis, then stand upright over the first 3s of lift.
 angle=math.pi/2*(1-smooth((t-28)/3)) if t<47 else math.pi/2*smooth((t-47)/9)
 rotation=Matrix.Rotation(angle,4,'Y')
 rotated=[rotation@p*SACK_SCALE for p in points]
 lo=Vector(tuple(min(p[i] for p in rotated) for i in range(3)))
 hi=Vector(tuple(max(p[i] for p in rotated) for i in range(3)))
 offset=Vector((-(lo.x+hi.x)/2,-(lo.y+hi.y)/2,-lo.z))
 return cargo@Matrix.Translation(offset)@rotation
