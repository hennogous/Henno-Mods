"""Author the Tailors' donkey-to-storage delivery sequence from current sources."""
import bpy, json, sys, math, hashlib
import xml.etree.ElementTree as ET
import bisect
from pathlib import Path
from mathutils import Matrix, Vector
from mathutils import Quaternion
sys.path.insert(0,str(Path(__file__).resolve().parent))
from delivery_pose_adjustments import adjust_pose
from delivery_cargo_motion import TIP_BONE,reset_pose,tip_pose,load_sack_points

ART=Path(r'C:\Users\Shadow\Desktop\Working Files\3D Art')
OUT=Path(r'C:\Users\Shadow\Desktop\Codex\CSC_Storage_L\delivery-01')
OUT.mkdir(parents=True,exist_ok=True)
BODY_SCALE=1.0
PRODUCTION_ASSET=Path(__file__).resolve().parents[3]/'Civ Supply Chains/Assets/CSC_TAILORS_Storage_L.ast'
_asset=ET.parse(PRODUCTION_ASSET).getroot()
_cargo=next(p for p in _asset.findall('.//m_Points/Element') if p.find('m_BoneName').get('text')=='Cargo')
CARGO_SCALE=float(_cargo.findtext('m_scale'))
if '--cargo-scale' in sys.argv:CARGO_SCALE=float(sys.argv[sys.argv.index('--cargo-scale')+1])
GAIT_STRIDE=12*BODY_SCALE/.65
SOURCES={
 'crane':ART/'Storage/Storage_L/CSC_Storage_L_Crane.blend',
 'storage':ART/'Storage/Storage_L/CSC_Storage_L.blend',
 'workshop':ART/'TAILORS/Textile Workshop/revision-11-pantry-interiors-shared-ao/CSC_TAILORS_Textile_Workshop_FINAL.blend',
 'road':ART/'Quarters/Road Layout.blend',
 'road_decal':ART/'Quarters/CSC_ALL_Classical_Base_02_Road_Decals.blend',
 'donkey':Path(r'C:\Users\Shadow\Desktop\Codex\Civ6-animation-research-20261007\IMP_Mine_AN_Sledge_Geo-animation-study.blend')}
PANTRY=Path(r"C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization VI SDK Assets\Civ6\pantry")
for event in ('load_post','depsgraph_update_post'):
 for cb in list(getattr(bpy.app.handlers,event)):
  if cb.__module__.rsplit('.',1)[-1]=='csc_scene_tools':getattr(bpy.app.handlers,event).remove(cb)

def bounds(o):
 p=[o.matrix_world@Vector(v) for v in o.bound_box]
 return [[min(v[i] for v in p) for i in range(3)],[max(v[i] for v in p) for i in range(3)]]

def append_scene(label,destination):
 path=SOURCES[label];oldimages=set(bpy.data.images)
 with bpy.data.libraries.load(str(path),link=False) as (src,dst):
  name='Review' if 'Review' in src.scenes else src.scenes[0]
  dst.scenes=[name]
 imported=dst.scenes[0];objects=[]
 for o in list(imported.objects):
  if o.type in ('MESH','ARMATURE','EMPTY','CURVE'):
   destination.collection.objects.link(o);objects.append(o)
   o['delivery_source']=label;o['review_only']=True;o['csc_export_exclude']=True
 for im in set(bpy.data.images)-oldimages:
  if im.source=='FILE':
   candidate=Path(bpy.path.abspath(im.filepath))
   if not candidate.is_file():candidate=path.parent/im.filepath.removeprefix('//')
   if not candidate.is_file():
    inv=json.loads((OUT/'sources.json').read_text())[label]['images']
    candidate=next((Path(x['path']) for x in inv if im.name.startswith(x['name'])),candidate)
   im.filepath=str(candidate.resolve())
 bpy.data.scenes.remove(imported)
 return objects

def context_scene():
 bpy.ops.wm.open_mainfile(filepath=str(SOURCES['crane']))
 for im in bpy.data.images:
  if im.source=='FILE':im.filepath=bpy.path.abspath(im.filepath)
 review=bpy.data.scenes['Review'];bpy.context.window.scene=review
 objects={label:append_scene(label,review) for label in ('storage','workshop','road_decal')}
 # Decals encode projection height; show their actual painted footprints at grade.
 for o in objects['road_decal']:
  if o.type=='MESH':
   if '_ANC' in o.name and any(x.type=='MESH' and x.name.replace('_CLA','_ANC')==o.name for x in objects['road_decal']):o.hide_render=True
   mat=o.matrix_world.copy();o.parent=None;o.matrix_world=mat
   o.data.transform(o.matrix_world);o.matrix_world=Matrix.Identity(4)
   for v in o.data.vertices:v.co.z=.08
 bpy.ops.mesh.primitive_plane_add(size=740,location=(0,0,-.15));ground=bpy.context.object
 ground.name='REVIEW_Ground';ground['review_only']=True;ground['csc_export_exclude']=True
 mat=bpy.data.materials.new('REVIEW_Grass');mat.diffuse_color=(.09,.14,.06,1);mat.use_nodes=True
 mat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.09,.14,.06,1)
 ground.data.materials.append(mat)
 camera=bpy.data.objects.new('Delivery_Plan_Camera',bpy.data.cameras.new('Delivery_Plan_Camera'))
 review.collection.objects.link(camera);camera.data.type='ORTHO';camera.data.ortho_scale=660
 camera.location=(0,0,800);camera.rotation_euler=(0,0,0);review.camera=camera
 review.render.resolution_x=1100;review.render.resolution_y=1100;review.render.resolution_percentage=100
 review.render.image_settings.file_format='PNG';review.render.filepath=str(OUT/'layout-top.png')
 review.frame_set(1)
 return review,objects

if '--context' in sys.argv:
 review,objects=context_scene()
 bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'delivery-context.blend'))
 bpy.ops.render.render(write_still=True)
 report={label:[{'name':o.name,'bounds':bounds(o),'matrix':[list(r) for r in o.matrix_world]} for o in obs if o.type=='MESH'] for label,obs in objects.items()}
 (OUT/'layout.json').write_text(json.dumps(report,indent=2))

def donkey_material(mesh):
 mat=bpy.data.materials.new('IMP_Mine_Base');mat.use_nodes=True
 nodes=mat.node_tree.nodes;links=mat.node_tree.links;shader=nodes.get('Principled BSDF')
 image=nodes.new('ShaderNodeTexImage');image.image=bpy.data.images.load(str(PANTRY/'Textures/IMP_Mine_Base_B.dds'))
 links.new(image.outputs['Color'],shader.inputs['Base Color']);shader.inputs['Roughness'].default_value=.85
 mesh.data.materials.clear();mesh.data.materials.append(mat)

if '--donkey-profile' in sys.argv:
 bpy.ops.wm.open_mainfile(filepath=str(SOURCES['donkey']))
 rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');mesh=next(o for o in bpy.data.objects if o.type=='MESH')
 donkey_material(mesh);s=bpy.context.scene;s.frame_set(1)
 data={}
 for group in mesh.vertex_groups:
  pts=[v.co for v in mesh.data.vertices if any(g.group==group.index and g.weight>.5 for g in v.groups)]
  if pts:data[group.name]={'count':len(pts),'bounds':[[min(v[i] for v in pts) for i in range(3)],[max(v[i] for v in pts) for i in range(3)]]}
 (OUT/'donkey-profile.json').write_text(json.dumps(data,indent=2))
 cam=bpy.data.objects.new('ProfileCamera',bpy.data.cameras.new('ProfileCamera'));s.collection.objects.link(cam)
 cam.location=(-70,-95,60);cam.rotation_euler=(Vector((3,-5,10))-cam.location).to_track_quat('-Z','Y').to_euler()
 cam.data.type='ORTHO';cam.data.ortho_scale=85;s.camera=cam
 lamp=bpy.data.objects.new('ProfileLight',bpy.data.lights.new('ProfileLight','SUN'));s.collection.objects.link(lamp);lamp.data.energy=2;lamp.rotation_euler=(.5,-.6,-.5)
 s.render.engine='CYCLES';s.cycles.samples=16;s.render.resolution_x=800;s.render.resolution_y=600;s.render.resolution_percentage=100
 s.render.filepath=str(OUT/'donkey-profile.png');s.render.image_settings.file_format='PNG';bpy.ops.render.render(write_still=True)

def smooth(x):
 x=max(0,min(1,x));return x*x*(3-2*x)

def travel_fraction(t,begin,duration):
 # Ease distance into/out of a stop over half a second. Abrupt velocity changes
 # can overshoot after native curve compression even with per-frame Blender keys.
 u=max(0,min(1,(t-begin)/duration));e=.5/duration
 if u<e:
  q=u/e;return e*(2*q*q-q*q*q)
 if u>1-e:
  q=(1-u)/e;return 1-e*(2*q*q-q*q*q)
 return u

class Route:
 def __init__(self,coords):
  points=[Vector((x,y,0)) for x,y in coords];self.points=[]
  for i in range(len(points)-1):
   a=points[max(0,i-1)];b=points[i];c=points[i+1];d=points[min(len(points)-1,i+2)]
   for j in range(40):
    u=j/40
    self.points.append(.5*((2*b)+(-a+c)*u+(2*a-5*b+4*c-d)*u*u+(-a+3*b-3*c+d)*u*u*u))
  self.points.append(points[-1]);self.lengths=[0]
  for a,b in zip(self.points,self.points[1:]):self.lengths.append(self.lengths[-1]+(b-a).length)
  self.length=self.lengths[-1]
 def sample(self,fraction):
  distance=max(0,min(1,fraction))*self.length;i=max(1,min(len(self.points)-1,bisect.bisect_left(self.lengths,distance)))
  u=(distance-self.lengths[i-1])/max(self.lengths[i]-self.lengths[i-1],1e-8)
  point=self.points[i-1].lerp(self.points[i],u);direction=(self.points[i]-self.points[i-1]).normalized()
  theta=math.atan2(direction.y,direction.x)-math.pi
  # Route points trace the visual centreline, not the donor's off-centre rig origin.
  return point-Matrix.Rotation(theta,3,'Z')@Vector((0,-5.2*BODY_SCALE,0)),theta

def keypose(bone,frame):
 bone.keyframe_insert('location',frame=frame);bone.keyframe_insert('rotation_quaternion',frame=frame);bone.keyframe_insert('scale',frame=frame)

if '--author' in sys.argv:
 import bmesh
 hashes={k:hashlib.sha256(p.read_bytes()).hexdigest() for k,p in SOURCES.items()}
 bpy.ops.wm.open_mainfile(filepath=str(OUT/'delivery-context.blend'))
 export=bpy.data.scenes['Export'];review=bpy.data.scenes['Review'];bpy.context.window.scene=export
 rig=bpy.data.objects['CSC_Storage_Crane_Rig'];rig.data.pose_position='POSE'
 placement=rig.parent;P=rig.matrix_world.copy()
 crane=[o for o in export.objects if o.type=='MESH' and 'Crane' in o.name]
 bale=next(o for o in export.objects if o.type=='MESH' and 'Textile_Bale' in o.name);cargo_controller=bale.parent
 old_action=rig.animation_data.action;old_action.use_fake_user=True
 samples={}
 for f in (1,151,175,291,321):
  export.frame_set(f);samples[f]={b.name:b.matrix_basis.copy() for b in rig.pose.bones}
 export.frame_set(1)
 pickup_xy=(P@rig.pose.bones['Load'].matrix).translation.copy()
 # Native donkey body rig/geometry; hold its local gait separately from route motion.
 obs=append_scene('donkey',export)
 donkey=next(o for o in obs if o.type=='ARMATURE');dm=next(o for o in obs if o.type=='MESH')
 donkey.name='CSC_Delivery_Donkey_Rig';dm.name='CSC_Delivery_Donkey_Mesh'
 for o in (donkey,dm):
  review.collection.objects.link(o);o['review_only']=False;o['csc_export_exclude']=False
 dm['export_role']='building_geometry';dm['source_asset_id']='IMP_Mine_Sledge';dm['delivery_derived_native']=True
 donkey_material(dm)
 gait=donkey.animation_data.action
 if not gait or gait.frame_range.y>35:gait=bpy.data.actions.get('Action.001')
 assert gait and gait.frame_range.y<=35
 donkey.animation_data.action=gait
 if gait.slots:donkey.animation_data.action_slot=gait.slots[0]
 gait.use_fake_user=True;donkey.data.pose_position='POSE'
 gait_basis=[]
 for f in range(1,31):
  export.frame_set(f);gait_basis.append({b.name:b.matrix_basis.copy() for b in donkey.pose.bones})
 # Select whole cargo components: some right-runner vertices also use Cart.
 from delivery_sled_geometry import remove_native_payload,align_loading_deck
 remove_native_payload(dm)
 # A simple deck is part of the derived sled, weighted to its original Cart bone.
 bpy.ops.mesh.primitive_cube_add(size=1);deck=bpy.context.object;deck.name='Delivery_Sled_Deck'
 deck.location=(18.5,-5.2,8);deck.dimensions=(20,16,2)
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 deck.data.materials.append(dm.data.materials[0]);vg=deck.vertex_groups.new(name='Cart');vg.add(list(range(len(deck.data.vertices))),1,'REPLACE')
 # Sample a timber region from the native sled's own atlas.
 uv=deck.data.uv_layers.active
 for p in deck.data.polygons:
  for i,li in enumerate(p.loop_indices):uv.data[li].uv=((.54,.73),(.65,.73),(.65,.77),(.54,.77))[i]
 bpy.ops.object.select_all(action='DESELECT');dm.select_set(True);deck.select_set(True);bpy.context.view_layer.objects.active=dm;bpy.ops.object.join()
 align_loading_deck(dm,list(range(len(dm.data.vertices)-8,len(dm.data.vertices))))
 for sc in bpy.data.scenes:
  if dm.name not in sc.objects and sc.name=='Review':sc.collection.objects.link(dm)
 export.frame_set(1)
 # Store a deck-centred offset in native Cart bone coordinates.
 cart_offset=donkey.pose.bones['Cart'].matrix.inverted()@Vector((18.5,-5.2,9.25))
 # Master carries all route/cargo/crane tracks; the body clip only bends the donkey.
 rig.animation_data_clear();bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig
 bpy.ops.object.mode_set(mode='EDIT')
 sack_points=load_sack_points()
 for name in ('DonkeyPath','Cargo',TIP_BONE):
  b=rig.data.edit_bones.new(name);b.head=(0,0,0);b.tail=(0,2,0);b.parent=rig.data.edit_bones['Root']
 bpy.ops.object.mode_set(mode='OBJECT')
 rig.animation_data_create();rig.animation_data.action=bpy.data.actions.new('CSC_TAILORS_Delivery_Master')
 donkey.animation_data_clear();donkey.animation_data_create();donkey.animation_data.action=bpy.data.actions.new('CSC_TAILORS_Delivery_Donkey_Gait')
 for b in list(rig.pose.bones)+list(donkey.pose.bones):b.rotation_mode='QUATERNION'
 # Bone-parent followers with inverse tail translation; keep payload as an AE attachment.
 donkey.parent=rig;donkey.parent_type='BONE';donkey.parent_bone='DonkeyPath'
 donkey.matrix_parent_inverse=Matrix.Identity(4);donkey.matrix_basis=Matrix.Translation((0,-2,0))@Matrix.Scale(BODY_SCALE,4)
 donkey['delivery_body_scale']=BODY_SCALE
 cargo_controller.parent=rig;cargo_controller.parent_type='BONE';cargo_controller.parent_bone='Cargo'
 cargo_controller.matrix_parent_inverse=Matrix.Identity(4);cargo_controller.matrix_basis=Matrix.Translation((0,-2,0))@Matrix.Scale(CARGO_SCALE,4)
 cargo_controller['bone_name']='Cargo';cargo_controller['source_asset_id']='CSC_ALL_Textile_Bale'
 # Final approach travels south, keeping the donkey clear of the west wall.
 stop_theta=math.pi/2
 for b in donkey.pose.bones:b.matrix_basis=gait_basis[0][b.name]
 bpy.context.view_layer.update()
 local_cart=donkey.pose.bones['Cart'].matrix@cart_offset
 stop=pickup_xy-(Matrix.Rotation(stop_theta,3,'Z')@(local_cart*BODY_SCALE));stop.z=0
 # Measured outer jambs, rather than an estimated point near the front props.
 door=Vector((-22.361,-189.7365,0));inward=Vector((.742,.670,0)).normalized()
 door_angle=math.atan2(inward.y,inward.x);lateral=Vector((0,-5.2*BODY_SCALE,0))
 def door_point(depth,outgoing):
  return tuple((door+inward*depth)[:2])
 # Alpha-weighted centre of the actual road decal, checked against exported FGX.
 # The upper bend is farther east than the earlier visual approximation.
 road=[(-57,-170),(-54.24,-160),(-45.98,-140),(-40.41,-120),(-36.83,-100),(-35.58,-80),(-35.63,-60),(-38.92,-40),(-43.60,-20),(-50.5,0),(-60.04,20),(-64.88,30),(-70.91,40),(-78.18,50),(-88.85,60),(-105.38,70)]
 stop_center=stop+Matrix.Rotation(stop_theta,3,'Z')@lateral
 # Full-size sled must clear the opening completely before the turn.
 workshop_turn=[(-65,-217),(-71,-204),(-66,-187),(-60,-177)]
 # Leave the upper-left branch earlier to reserve its outer edge for prop scenes.
 # Keep the final straight southward approach so the sled meets the same hook.
 loading=[(-120,83),(-127,95),(-127,114),(-119,132),(-105,144),(-94,146),(stop_center.x,stop_center.y+16),(stop_center.x,stop_center.y+8),(stop_center.x,stop_center.y)]
 coords=[door_point(d,True) for d in (60,42,28,14,0,-14,-28,-44)]+workshop_turn+road+loading
 outbound=Route(coords)
 # Already facing the return direction: continue straight onto the road.
 backcoords=[(stop_center.x,stop_center.y),(stop_center.x,105),(-88,85),(-89,74)]+list(reversed(road[:-1]))+list(reversed(workshop_turn))+[door_point(d,False) for d in (-44,-28,-14,0,14,28,42,60)]
 inbound=Route(backcoords)
 start,angle_start=outbound.sample(0);stop_point,_=outbound.sample(1);angle_stop=stop_theta
 low=samples[1]['Hoist'].to_translation();high=samples[151]['Hoist'].to_translation();deposit=samples[321]['Hoist'].to_translation()
 final_swivel=samples[291]['Swivel'].to_quaternion()
 cargo_record={};route_record={};attachment_error=0
 for f in range(1,2042):
  export.frame_set(f)
  t=(f-1)/30
  if t<2:pos,theta=outbound.sample(0);phase=0
  elif t<24:
   u=travel_fraction(t,2,22);pos,theta=outbound.sample(u);phase=(u*outbound.length/GAIT_STRIDE)%1
   if t>23.5:
    before=theta;theta+=math.atan2(math.sin(angle_stop-theta),math.cos(angle_stop-theta))*smooth((t-23.5)/.5)
    pos+=(Matrix.Rotation(before,3,'Z')-Matrix.Rotation(theta,3,'Z'))@lateral
  elif t<33:pos,theta=stop_point.copy(),angle_stop;phase=0
  elif t<58:
   u=travel_fraction(t,33,25);pos,theta=inbound.sample(u);phase=(u*inbound.length/GAIT_STRIDE)%1
  else:
   # The animal is fully hidden before any loop reset or change of orientation.
   end,angle_end=inbound.sample(1);u=smooth((t-58)/3)
   pos=end.lerp(start,u);theta=angle_end+math.atan2(math.sin(angle_start-angle_end),math.cos(angle_start-angle_end))*u;phase=0
  body_visibility=(.0001+.9999*smooth(t)) if t<1 else ((.0001+.9999*smooth((58-t)/.5)) if t>57.5 else 1)
  # Blend into the same neutral gait pose at departure/arrival to prevent pops.
  gi=int(phase*30)%30;gn=(gi+1)%30;blend=phase*30-gi
  fade=1
  for end in (24,58):
   if end-.5<t<end:fade=smooth((end-t)/.5)
  for begin in (2,33):
   if begin<t<begin+.5:fade=smooth((t-begin)/.5)
  for b in donkey.pose.bones:
   a=gait_basis[gi][b.name];c=gait_basis[gn][b.name]
   loc=a.to_translation().lerp(c.to_translation(),blend);rot=a.to_quaternion().slerp(c.to_quaternion(),blend);scale=a.to_scale().lerp(c.to_scale(),blend)
   base=gait_basis[0][b.name];loc=base.to_translation().lerp(loc,fade);rot=base.to_quaternion().slerp(rot,fade);scale=base.to_scale().lerp(scale,fade)
   b.matrix_basis=Matrix.LocRotScale(loc,rot,scale);keypose(b,f)
  path_world=Matrix.Translation(pos)@Matrix.Rotation(theta,4,'Z')@Matrix.Scale(body_visibility,4)
  rig.pose.bones['DonkeyPath'].matrix=P.inverted()@path_world
  keypose(rig.pose.bones['DonkeyPath'],f)
  bpy.context.view_layer.update()
  current_route=outbound if 2<t<24 else (inbound if 33<t<58 else None)
  fraction=travel_fraction(t,2,22) if 2<t<24 else (travel_fraction(t,33,25) if 33<t<58 else 0)
  adjust_pose(donkey,pos,theta,BODY_SCALE,current_route,fraction,door,inward)
  for name in ('Neck','Sledge_R'):keypose(donkey.pose.bones[name],f)
  bpy.context.view_layer.update()
  cart_world=donkey.matrix_world@(donkey.pose.bones['Cart'].matrix@cart_offset)
  if f==721:pickup_height=cart_world.z
  if t<24:pickup_height=cart_world.z
  pickup_hoist=low+Vector((0,0,(pickup_height-pickup_xy.z)/P.to_scale().z))
  if t<24:h=high;trolley=0;swivel=Quaternion()
  elif t<27:h=high.lerp(pickup_hoist,smooth((t-24)/3));trolley=0;swivel=Quaternion()
  elif t<28:h=pickup_hoist;trolley=0;swivel=Quaternion()
  elif t<34:
   u=smooth((t-28)/6);h=pickup_hoist.lerp(high,u);trolley=4*u;swivel=Quaternion()
  elif t<35:h=high;trolley=4;swivel=Quaternion()
  elif t<40:
   u=smooth((t-35)/5);h=high;trolley=4*(1-u);swivel=Quaternion().slerp(final_swivel,u)
  elif t<42:h=high.lerp(deposit,smooth((t-40)/2));trolley=0;swivel=final_swivel
  elif t<44:h=deposit.lerp(high+Vector((0,0,10)),smooth((t-42)/2));trolley=0;swivel=final_swivel
  elif t<47:
   u=smooth((t-44)/3);h=(high+Vector((0,0,10))).lerp(high,u);trolley=0;swivel=final_swivel.slerp(Quaternion(),u)
  else:h=high;trolley=0;swivel=Quaternion()
  rig.pose.bones['Hoist'].location=h;rig.pose.bones['Trolley'].location=(trolley,0,0);rig.pose.bones['Swivel'].rotation_quaternion=swivel
  for name in ('Hoist','Trolley','Swivel'):keypose(rig.pose.bones[name],f)
  bpy.context.view_layer.update()
  load_world=P@rig.pose.bones['Load'].matrix
  if t<=28:
   cargo_world=Matrix.Translation(cart_world)@Matrix.Rotation(theta,4,'Z')@Matrix.Scale(body_visibility,4)
  elif t<=42:
   yaw=angle_stop+swivel.to_euler().z
   cargo_world=Matrix.Translation(load_world.translation)@Matrix.Rotation(yaw,4,'Z')
  elif t<58:
   # Withdraw behind the bay wall, reset below grade, then rise inside the workshop.
   # Continuous hidden motion avoids a one-frame teleport being smeared by native compression.
   hidden=reset_pose(stored,45.5)
   below=hidden.copy();below.translation.z=-100
   home=Matrix.Translation(cart_world)@Matrix.Rotation(angle_start,4,'Z')
   underground=home.copy();underground.translation.z=-100
   if t<47:cargo_world=reset_pose(stored,t)
   elif t<56:
    u=smooth((t-47)/9)
    # Use the fixed home point; the donkey is still returning during this interval.
    home_point=start+Matrix.Rotation(angle_start,3,'Z')@(local_cart*BODY_SCALE)
    cargo_world=Matrix.LocRotScale(below.translation.lerp(Vector((home_point.x,home_point.y,-100)),u),below.to_quaternion().slerp(home.to_quaternion(),u),Vector((1,1,1)))
   else:
    home_point=start+Matrix.Rotation(angle_start,3,'Z')@(local_cart*BODY_SCALE)
    cargo_world=Matrix.Translation(Vector((home_point.x,home_point.y,-100)).lerp(home_point,smooth((t-56)/2)))@Matrix.Rotation(angle_start,4,'Z')@Matrix.Scale(body_visibility,4)
  else:
   home_point=start+Matrix.Rotation(angle_start,3,'Z')@(local_cart*BODY_SCALE)
   cargo_world=Matrix.Translation(home_point)@Matrix.Rotation(angle_start,4,'Z')@Matrix.Scale(.0001,4)
  if abs(t-42)<.0001:stored=cargo_world.copy()
  rig.pose.bones['Cargo'].matrix=P.inverted()@cargo_world;keypose(rig.pose.bones['Cargo'],f)
  rig.pose.bones[TIP_BONE].matrix=P.inverted()@tip_pose(cargo_world,t,sack_points);keypose(rig.pose.bones[TIP_BONE],f)
  cargo_record[f]=list(cargo_world.translation);route_record[f]=list(pos)
  if 28<t<=42:attachment_error=max(attachment_error,(cargo_world.translation-load_world.translation).length)
 for action in (rig.animation_data.action,donkey.animation_data.action):
  action.use_fake_user=True
  for layer in action.layers:
   for strip in layer.strips:
    for bag in strip.channelbags:
     for curve in bag.fcurves:
      for key in curve.keyframe_points:key.interpolation='LINEAR'
 for sc in (export,review):
  sc.frame_start=1;sc.frame_end=2041;sc.render.fps=30;sc.frame_set(721)
 for label,frame in [('Departure',61),('Arrive / lower hook',721),('Lift load',841),('Donkey returns directly',991),('Swing into storage',1051),('Deposit',1261),('Return completed',1741),('10 second pause ends',2041)]:
  export.timeline_markers.new(label,frame=frame);review.timeline_markers.new(label,frame=frame)
 rig['delivery_duration_seconds']=68;rig['pause_seconds']=10;rig['cargo_bone']='Cargo'
 rig['body_animation']=donkey.animation_data.action.name
 # Road/building objects stay review-only, and do not become moving exported meshes.
 guide=bpy.data.curves.new('Delivery_Route','CURVE');guide.dimensions='3D';sp=guide.splines.new('POLY');sp.points.add(len(outbound.points)-1)
 for p,co in zip(sp.points,outbound.points):p.co=(*co[:2],.3,1)
 route_obj=bpy.data.objects.new('REVIEW_Delivery_Route',guide);review.collection.objects.link(route_obj);route_obj.hide_render=True;route_obj['review_only']=True
 for p in list(bpy.data.texts):
  if p.name.startswith('START HERE'):bpy.data.texts.remove(p)
 bpy.data.texts.new('START HERE - Delivery').write('Tailors delivery: 68 seconds at 30 FPS, including a 10-second pause.\n'
  'Authoring keeps crane and donkey rigs separate; native export bakes both into ONE rig/clip for visibility and synchronized random phase.\n'
  f'AE cargo attachment: Cargo bone, textile bale at uniform scale {CARGO_SCALE}.\n'
 'Donkey and sled are both original Mine scale 1.0; widened workshop turn and head dip. Workshop threshold is pending removal.\n'
  'Review scene includes current workshop, storage and actual road decals; Export holds moving assets only.\n'
  'Original source files are unchanged. Native integration and final route checks are recorded separately.\n')
 bpy.context.window.scene=review
 review.render.filepath=str(OUT/'delivery-pickup-top.png');bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'CSC_TAILORS_Storage_Delivery.blend'))
 bpy.ops.render.render(write_still=True)
 assert all(hashlib.sha256(p.read_bytes()).hexdigest()==hashes[k] for k,p in SOURCES.items())
 report={'duration_seconds':68,'pause_seconds':10,'source_hashes':hashes,'source_files_modified':False,
  'crane_material':'CSC_TAILORS_NE','cargo_bone':'Cargo','body_scale':BODY_SCALE,'cargo_scale':CARGO_SCALE,
  'outbound_length':outbound.length,'return_length':inbound.length,'route_centerlines':{'outbound':[list(p) for p in outbound.points],'return':[list(p) for p in inbound.points],'shared_road':road},'cargo_record':cargo_record,'route_record':route_record,
  'cargo_hook_position_error':attachment_error,'ae_verified':False}
 (OUT/'authoring-check.json').write_text(json.dumps(report,indent=2));print('DELIVERY_AUTHORED')

if '--inspect' in sys.argv:
 report={}
 for label,path in SOURCES.items():
  bpy.ops.wm.open_mainfile(filepath=str(path))
  report[label]={'path':str(path),'scenes':[{'name':s.name,'objects':[o.name for o in s.objects],'props':dict(s.items())} for s in bpy.data.scenes],
   'objects':[{'name':o.name,'type':o.type,'parent':o.parent.name if o.parent else None,
    'matrix':[list(r) for r in o.matrix_world],'bounds':bounds(o) if o.type=='MESH' else None,
    'materials':[m.name for m in o.data.materials if m] if o.type=='MESH' else None,
    'vertices':len(o.data.vertices) if o.type=='MESH' else None,'props':dict(o.items()),
    'bones':[{'name':b.name,'parent':b.parent.name if b.parent else None,'head':list(b.head_local)} for b in o.data.bones] if o.type=='ARMATURE' else None}
    for o in bpy.data.objects],
   'actions':[{'name':a.name,'range':list(a.frame_range)} for a in bpy.data.actions],
   'images':[{'name':i.name,'path':bpy.path.abspath(i.filepath)} for i in bpy.data.images if i.source=='FILE']}
 (OUT/'sources.json').write_text(json.dumps(report,indent=2,default=str))
 print('DELIVERY_SOURCES_INSPECTED')
