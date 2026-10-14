"""Local clearance poses for the original-size donor in the delivery scene."""
import math,bisect
from mathutils import Matrix,Vector
class RecordedRoute:
 def __init__(self,points,scale):
  self.points=[Vector(p) for p in points];self.scale=scale;self.lengths=[0]
  for a,b in zip(self.points,self.points[1:]):self.lengths.append(self.lengths[-1]+(b-a).length)
  self.length=self.lengths[-1]
 def sample(self,fraction):
  distance=max(0,min(1,fraction))*self.length;i=max(1,min(len(self.points)-1,bisect.bisect_left(self.lengths,distance)))
  u=(distance-self.lengths[i-1])/max(self.lengths[i]-self.lengths[i-1],1e-8)
  point=self.points[i-1].lerp(self.points[i],u);direction=(self.points[i]-self.points[i-1]).normalized()
  theta=math.atan2(direction.y,direction.x)-math.pi
  return point-Matrix.Rotation(theta,3,'Z')@Vector((0,-5.2*self.scale,0)),theta
def smooth(x):
 x=max(0,min(1,x));return x*x*(3-2*x)
def linearize_baked_keys(rig):
 # Keep quaternion signs continuous so conversion cannot interpolate a long spin.
 action=rig.animation_data.action
 curves=[fc for layer in action.layers for strip in layer.strips for bag in strip.channelbags for fc in bag.fcurves]
 for fc in curves:
  for key in fc.keyframe_points:key.interpolation='LINEAR'
 for bone in rig.pose.bones:
  path=bone.path_from_id('rotation_quaternion')
  channels=sorted([fc for fc in curves if fc.data_path==path],key=lambda fc:fc.array_index)
  if len(channels)!=4:continue
  previous=None
  for keys in zip(*(fc.keyframe_points for fc in channels)):
   values=[key.co.y for key in keys]
   if previous is not None and sum(a*b for a,b in zip(previous,values))<0:
    values=[-v for v in values]
    for key,value in zip(keys,values):key.co.y=value
   previous=values
  for fc in channels:fc.update()
def adjust_pose(donkey,pos,theta,body_scale,route,fraction,door,inward):
 # Lower the neck while the head passes the workshop arch; never scale the body.
 head=pos+Matrix.Rotation(theta,3,'Z')@Vector((-25,-5.2,29))*body_scale
 depth=(head-door).dot(inward);side=(head-door).dot(Vector((inward.y,-inward.x,0)))
 duck=smooth((48-abs(depth))/17)*smooth((40-abs(side))/15)
 b=donkey.pose.bones['Neck'];m=b.matrix.copy();pivot=m.translation
 b.matrix=Matrix.Translation(pivot)@Matrix.Rotation(-math.radians(42)*duck,4,'Y')@Matrix.Translation(-pivot)@m
