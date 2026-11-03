"""Measured modern storage geometry, separate handling props and independent AO."""
import bpy,bmesh,json,math,sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[4];A=Path.home()/'Desktop/Working Files/3D Art';O=Path.home()/'Desktop/Codex/modern-storage-v1-20261029';T=O/'textures'
sys.path.insert(0,str(ROOT/'project/tools/blender'))
from csc_scene_validation import suspend_csc_repairs
bpy.ops.wm.read_factory_settings(use_empty=True);review=bpy.context.scene;review.name='Review';export=bpy.data.scenes.new('Export')
for sc in (review,export):sc['asset_id']='CSC_Storage_Modern';sc.render.engine='CYCLES';sc.cycles.samples=32;sc.render.threads_mode='FIXED';sc.render.threads=6;sc.view_settings.view_transform='Standard' if sc==review else 'AgX';sc.view_settings.exposure=-.1 if sc==review else .35
w=bpy.data.worlds.new('Review World');w.use_nodes=True;w.node_tree.nodes['Background'].inputs[0].default_value=(.7,.8,1,1);w.node_tree.nodes['Background'].inputs[1].default_value=.65;review.world=export.world=w
sun=bpy.data.objects.new('Review_Key',bpy.data.lights.new('Review_Key','SUN'));review.collection.objects.link(sun);sun.data.energy=3.2;sun.data.color=(1,.92,.8);sun.data.angle=math.radians(6);sun.rotation_euler=(-Vector((-300,-280,500))).to_track_quat('-Z','Y').to_euler()
rig=bpy.data.objects.new('CSC_Storage_Modern',bpy.data.armatures.new('CSC_Storage_Modern'));review.collection.objects.link(rig);export.collection.objects.link(rig);bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT');bone=rig.data.edit_bones.new('Bone');bone.tail=(0,0,5);bpy.ops.object.mode_set(mode='OBJECT');rig.select_set(False)
def material(name,prefix):
 m=bpy.data.materials.new(name);m.use_nodes=True;ns=m.node_tree.nodes;ls=m.node_tree.links;bs=ns.get('Principled BSDF');maps={}
 for ch in ('B','N','G','M','AO','E'):
  fn=prefix+('_B_BAKERS' if ch=='B' and prefix=='CSC_Atlas_Modern' else '_E_BAKERS' if ch=='E' and prefix=='CSC_Atlas_Modern' else '_'+ch)+'.png'
  im=bpy.data.images.load(str(T/fn),check_existing=True);im.colorspace_settings.name='sRGB' if ch in ('B','E') else 'Non-Color';n=ns.new('ShaderNodeTexImage');n.name=n.label=ch;n.image=im;u=ns.new('ShaderNodeUVMap');u.uv_map='UV2' if ch=='AO' else 'UV3' if ch=='E' else 'UV1';ls.new(u.outputs[0],n.inputs['Vector']);maps[ch]=n
 mix=ns.new('ShaderNodeMixRGB');mix.name='AO_Multiply';mix.blend_type='MULTIPLY';mix.inputs[0].default_value=.5;ls.new(maps['B'].outputs[0],mix.inputs[1]);ls.new(maps['AO'].outputs[0],mix.inputs[2]);ls.new(mix.outputs[0],bs.inputs['Base Color'])
 nm=ns.new('ShaderNodeNormalMap');nm.uv_map='UV1';ls.new(maps['N'].outputs[0],nm.inputs['Color']);ls.new(nm.outputs[0],bs.inputs['Normal']);inv=ns.new('ShaderNodeMath');inv.operation='SUBTRACT';inv.inputs[0].default_value=1;ls.new(maps['G'].outputs[0],inv.inputs[1]);ls.new(inv.outputs[0],bs.inputs['Roughness']);ls.new(maps['M'].outputs[0],bs.inputs['Metallic']);ls.new(maps['E'].outputs[0],bs.inputs['Emission Color']);bs.inputs['Emission Strength'].default_value=0
 return m
bm=material('CSC_BAKERS_Modern','CSC_Atlas_Modern');pm=material('CSC_Props_Modern_01','CSC_Props_Modern_01');meshes=[];GROUP='M';MAT=bm
def uv(slot,u,v):
 x,y=(512+slot%4*128,512+slot//4*128) if MAT==bm else (slot%8*128,slot//8*128)
 return ((x+3+u*122)/1024,1-(y+3+(1-v)*122)/1024)
def mesh(name,vs,fs,slot,uvs=None):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();ob=bpy.data.objects.new('CSC_Fixed_'+GROUP+'_'+name,me);me.materials.append(MAT)
 for n in ('UV1','UV2','UV3'):me.uv_layers.new(name=n)
 for p in me.polygons:
  axis=max(range(3),key=lambda a:abs(p.normal[a]));aa,bb=((1,2),(0,2),(0,1))[axis];coords=[(me.vertices[i].co[aa],me.vertices[i].co[bb]) for i in p.vertices];lo=[min(c[i] for c in coords) for i in (0,1)];hi=[max(c[i] for c in coords) for i in (0,1)]
  for j,k in enumerate(p.loop_indices):
   u,v=uvs[p.index][j] if uvs else [(coords[j][a]-lo[a])/max(hi[a]-lo[a],.001) for a in (0,1)];s=slot if isinstance(slot,int) else slot[p.index];me.uv_layers[0].data[k].uv=uv(s,u,v);me.uv_layers[1].data[k].uv=(.99,.99);me.uv_layers[2].data[k].uv=me.uv_layers[0].data[k].uv if MAT==bm and s==5 else (.02,.02)
 b=bmesh.new();b.from_mesh(me);bmesh.ops.recalc_face_normals(b,faces=list(b.faces));bmesh.ops.split_edges(b,edges=[e for e in b.edges if len(e.link_faces)==2 and e.calc_face_angle()>math.radians(40)]);b.to_mesh(me);b.free()
 vg=ob.vertex_groups.new(name='Bone');vg.add(list(range(len(me.vertices))),1,'REPLACE');mod=ob.modifiers.new('Static binding','ARMATURE');mod.object=rig
 ob['module']=GROUP;ob['export_role']='building_geometry' if GROUP in ('M','L') else 'fixed_geometry';ob['source_asset_id']='CSC_Storage_'+GROUP+'_Modern'
 for sc in (review,export):sc.collection.objects.link(ob)
 meshes.append(ob);return ob
def box(name,lo,hi,slot):
 x,y,z=lo;X,Y,Z=hi;return mesh(name,[(x,y,z),(X,y,z),(X,Y,z),(x,Y,z),(x,y,Z),(X,y,Z),(X,Y,Z),(x,Y,Z)],[(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)],slot)
def beam(name,a,b,w,d,slot):
 a=Vector(a);b=Vector(b);direction=(b-a).normalized();side=direction.cross(Vector((0,0,1)))
 if side.length<.01:side=Vector((1,0,0))
 side.normalize();other=direction.cross(side).normalized();vs=[p+side*i*w/2+other*j*d/2 for p in (a,b) for i,j in ((-1,-1),(1,-1),(1,1),(-1,1))]
 ob=mesh(name,vs,[(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)],slot)
 # Grain runs along member length on every long face; ends use quiet short grain.
 for p in ob.data.polygons:
  for k in p.loop_indices:
   co=ob.data.vertices[ob.data.loops[k].vertex_index].co;u=(co-a).dot(direction)/(b-a).length;v=.5+(co-a).dot(side)/max(w,.01);ob.data.uv_layers[0].data[k].uv=uv(slot,max(0,min(1,u)),max(.05,min(.95,v)))
 return ob
def prism(name,top,depth,slot,coords=None):
 n=len(top);vs=top+[(x,y,z-depth) for x,y,z in top];fs=[tuple(range(n)),tuple(range(2*n-1,n-1,-1))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)];ob=mesh(name,vs,fs,slot)
 if coords:
  for p in ob.data.polygons:
   if p.index<2:
    for k in p.loop_indices:ob.data.uv_layers[0].data[k].uv=uv(slot,*coords(ob.data.vertices[ob.data.loops[k].vertex_index].co))
 return ob
def face(name,vs,slot):return mesh(name,vs,[tuple(range(len(vs)))],slot,[[(0,0),(1,0),(1,1),(0,1)]])
def facade(name,axis,pos,a,b,z0,z1,hole=None,slot=0):
 # Thick wall rectangles around a real door; one global mapping per facade.
 parts=[(a,b,z0,z1)] if hole is None else [(a,hole[0],z0,z1),(hole[1],b,z0,z1),(hole[0],hole[1],hole[2],z1)]
 for i,(l,r,bot,top) in enumerate(parts):
  if r-l<.01 or top-bot<.01:continue
  ob=box(name+str(i),(pos-1.5,l,bot) if axis==0 else (l,pos-1.5,bot),(pos+1.5,r,top) if axis==0 else (r,pos+1.5,top),slot)
  for p in ob.data.polygons:
   if abs(p.normal[axis])>.9:
    for k in p.loop_indices:
     co=ob.data.vertices[ob.data.loops[k].vertex_index].co;u=(co[1-axis]-a)/(b-a);v=(co.z-z0)/64;ob.data.uv_layers[0].data[k].uv=uv(slot,u,v)
def door(name,axis,pos,width,height,bottom=0):
 # Leave the aperture open; painted open leaves sit against the outer wall.
 if axis==0:
  box(name+'JambA',(pos-2.2,-width/2-3,bottom),(pos+2.2,-width/2,bottom+height),4);box(name+'JambB',(pos-2.2,width/2,bottom),(pos+2.2,width/2+3,bottom+height),4);box(name+'Lintel',(pos-2.2,-width/2-3,bottom+height),(pos+2.2,width/2+3,bottom+height+3),4)
  for side in (-1,1):box(name+'Leaf'+str(side),(pos-2.6,side*width/2+(-9 if side<0 else 0),bottom+.4),(pos-1.8,side*width/2+(0 if side<0 else 9),bottom+height-.5),6)
 else:
  for x in (-width/2-3,width/2):box(name+'Jamb'+str(x),(x,pos-2.2,bottom),(x+3,pos+2.2,bottom+height),4)
  box(name+'Lintel',(-width/2-3,pos-2.2,bottom+height),(width/2+3,pos+2.2,bottom+height+3),4)
  for side in (-1,1):box(name+'Leaf'+str(side),(side*width/2+(-8 if side<0 else 0),pos-2.5,bottom+.4),(side*width/2+(0 if side<0 else 8),pos-1.7,bottom+height-.5),6)
def rooflarge():
 # True equal-eave valley intersections; branch ridge 5 units below main ridge.
 z=lambda x:86-24*abs(x)/35
 left=[(-35,-47,z(-35)),(0,-47,86),(0,47,86),(-35,47,62),(-35,28,62),(-35*5/24,0,81),(-35,-28,62)]
 prism('Main_Roof_West',left,2,2,lambda p:((p.y+47)/94,(p.x+35)/35));prism('Main_Roof_East',[(0,-47,86),(35,-47,62),(35,47,62),(0,47,86)],2,2,lambda p:((p.y+47)/94,(35-p.x)/35))
 for s in (-1,1):prism('Loading_Gable_Roof'+str(s),[(-44,0,81),(-35*5/24,0,81),(-35,s*28,62),(-44,s*28,62)],2,2,lambda p:((p.x+44)/(44-35*5/24),1-abs(p.y)/28))
 beam('Main_Ridge',(0,-49,87),(0,49,87),4.2,3.8,3);beam('Loading_Ridge',(-46,0,82),(-6.6,0,82),3.8,3.6,3)
 for y in (-47,47):
  for s in (-1,1):
   beam('Main_Barge',(0,y,86),(s*36,y,61.5),3.5,3.3,3);beam('Barge_Wood_Underside',(0,y,83.9),(s*36,y,59.4),2.7,.9,8)
 for s in (-1,1):
  beam('Loading_Barge',(-44,0,81),(-44,s*29,61.3),3.4,3.1,3);beam('Loading_Wood_Underside',(-44,0,78.8),(-44,s*29,59.1),2.6,.9,8)
 beam('East_Eave',(35,-47,60.8),(35,47,60.8),2.8,3.8,3)
 for s in (-1,1):beam('West_Eave',(-35,s*28,60.8),(-35,s*47,60.8),2.8,3.8,3);beam('Wing_Eave',(-44,s*28,60.8),(-35,s*28,60.8),2.8,3.8,3)
 # Close both main gables and the smaller left loading gable.
 for y in (-43,43):mesh('Main_Gable',[(-31,y-1,61),(31,y-1,61),(0,y-1,84),(-31,y+1,61),(31,y+1,61),(0,y+1,84)],[(0,1,2),(3,5,4),(0,3,4,1),(1,4,5,2),(2,5,3,0)],0)
 mesh('Left_Gable',[(-41,-24,61),(-41,24,61),(-41,0,79),(-39,-24,61),(-39,24,61),(-39,0,79)],[(0,1,2),(3,5,4),(0,3,4,1),(1,4,5,2),(2,5,3,0)],0)
def deck(length):
 box('Receiving_Deck',(-80,-length,-18),(-33,length,1.4),7)
 # Sparse posts/one rail; no ground-side rail across the loading access.
 for y in (length,):
  for x in (-79,-56,-34):box('Rail_Post',(x-1,y-1,-5),(x+1,y+1,12),10)
  beam('Rail',(-79,y,11),(-34,y,11),1.6,1.9,10)
 for y in (-length,0):box('Outer_Rail_Post',(-80,y-1,-5),(-78,y+1,12),10)
 beam('Outer_Rail',(-79,-length,11),(-79,length,11),1.6,1.9,10)
def buildbuilding(size):
 global GROUP,MAT
 GROUP=size;MAT=bm
 if size=='M':
  for axis,pos in ((0,-31),(1,-39)):
   facade('Footing',axis,pos,-39 if axis==0 else -31,39 if axis==0 else 31,-22,18,( -11,11,30),1)
   facade('Brick',axis,pos,-39 if axis==0 else -31,39 if axis==0 else 31,18,46,(-11,11,30),0);door('Entry',axis,pos,22,30)
  facade('RearFoot',0,31,-39,39,-22,18,slot=1);facade('RearBrick',0,31,-39,39,18,46,slot=0);facade('BackFoot',1,39,-31,31,-22,18,slot=1);facade('BackBrick',1,39,-31,31,18,46,slot=0)
  for y in (-39,39):mesh('Gable', [(-31,y-1,46),(31,y-1,46),(0,y-1,77),(-31,y+1,46),(31,y+1,46),(0,y+1,77)],[(0,1,2),(3,5,4),(0,3,4,1),(1,4,5,2),(2,5,3,0)],0)
  for s in (-1,1):prism('Roof'+str(s),[(0,-44,79),(s*36,-44,46),(s*36,44,46),(0,44,79)],2,2,lambda p:((p.y+44)/88,1-abs(p.x)/36))
  beam('Ridge',(0,-46,80),(0,46,80),4.5,4,3)
  for y in (-44,44):
   for s in (-1,1):beam('Barge',(0,y,79),(s*36,y,46),3.6,3.5,3);beam('Barge_Wood',(0,y,76.8),(s*36,y,43.8),2.6,.9,8)
  for s in (-1,1):beam('Eave',(s*35,-44,44.8),(s*35,44,44.8),3.2,4,3)
  face('Back_Window',[(-8,40.6,24),(8,40.6,24),(8,40.6,38),(-8,40.6,38)],5);deck(37)
 else:
  facade('FrontGround',1,-43,-31,31,-18,37,(-11,11,27),1);door('GroundDoor',1,-43,22,27)
  facade('LeftGround',0,-31,-43,43,-18,37,(-12,12,29),1);facade('RightGround',0,31,-43,43,-18,37,slot=1);facade('RearGround',1,43,-31,31,-18,37,slot=1)
  facade('FrontUpper',1,-43,-31,31,38,62,slot=0);facade('RightUpper',0,31,-43,43,38,62,slot=0);facade('RearUpper',1,43,-31,31,38,62,slot=0)
  facade('WingFront',1,-25,-40,-30,38,62,slot=0);facade('WingBack',1,25,-40,-30,38,62,slot=0)
  facade('LoadingWall',0,-40,-25,25,38,62,(-12,12,61),0);door('LoadingDoor',0,-40,24,22,39)
  facade('LeftNorth',0,-31,25,43,38,62,slot=0);facade('LeftSouth',0,-31,-43,-25,38,62,slot=0)
  box('Front_StringCourse',(-33,-45,36),(33,-41,39),4);box('Right_StringCourse',(29,-41,36),(33,41,39),4);box('Back_StringCourse',(-33,41,36),(33,45,39),4);box('Loading_Threshold',(-44,-26,36),(-29,26,39),4)
  box('Left_South_StringCourse',(-33,-41,36),(-29,-26,39),4);box('Left_North_StringCourse',(-33,26,36),(-29,41,39),4)
  face('Front_Window',[(-12,-44.6,42),(12,-44.6,42),(12,-44.6,61),(-12,-44.6,61)],5);face('Rear_Window',[(12,44.6,43),(-12,44.6,43),(-12,44.6,60),(12,44.6,60)],5)
  rooflarge();deck(41)
 # Complete shallow floors/ceiling inside real openings; do not cap underground apertures.
 box('Interior_Floor',(-29,-37,-1),(29,37,0),7)
 if size=='L':box('Loft_Floor',(-40,-25,35),(29,25,37),8)
buildbuilding('M');buildbuilding('L')
# Consistent masonry sampling on gables; broad manufactured roof panels.
for ob in meshes:
 GROUP=ob['module'];MAT=bm
 if 'Gable' in ob.name and 'Roof' not in ob.name:
  axis=1 if 'Left_Gable' in ob.name else 0;width=48 if axis==1 else 62;base=18 if GROUP=='M' else 38
  for p in ob.data.polygons:
   for k in p.loop_indices:
    co=ob.data.vertices[ob.data.loops[k].vertex_index].co;ob.data.uv_layers[0].data[k].uv=uv(0,(co[axis]+width/2)/width,(co.z-base)/64)
 if 'Roof' in ob.name:
  x0=(512+2*128+3)/1024
  for q in ob.data.uv_layers[0].data:q.uv.x=x0+(q.uv.x-x0)*.64
 if GROUP=='M':
  for q in ob.data.uv_layers[2].data:q.uv=(.02,.02)
MAT=pm
def cyl(name,c,r,depth,slot,axis='Z',n=12):
 vs=[]
 for q in (-depth/2,depth/2):
  for j in range(n):
   a=j*math.tau/n;v=(r*math.cos(a),r*math.sin(a),q)
   if axis=='Y':v=(v[0],q,v[1])
   vs.append(tuple(c[k]+v[k] for k in range(3)))
 return mesh(name,vs,[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],slot)
GROUP='Hoist'
box('Wall_Plate',(-1,-2,-10),(1,2,10),44);beam('Jib',(-1,0,7),(-21,0,7),2.7,2.5,44);beam('Brace',(-1,0,-6),(-17,0,7),1.5,1.8,10)
box('Motor',(-21,-3,3),(-15,3,8),47);beam('Cable',(-18,0,3),(-18,0,-18),.5,.5,10)
beam('HookStem',(-18,0,-18),(-18,0,-20),.7,.7,10);beam('HookToe',(-18,0,-20),(-16,0,-20),.7,.7,10);beam('HookTip',(-16,0,-20),(-16,0,-18.5),.7,.7,10)
GROUP='Drum'
cyl('Body',(0,0,8),5.2,16,48);cyl('Lid',(0,0,16),5.5,1,48);cyl('Foot',(0,0,.5),5.5,1,10);cyl('Bung',(1.5,0,16.8),1,.6,10,n=8)
GROUP='PalletJack'
for y in (-3.5,3.5):box('Fork',(-12,y-1.5,1),(5,y+1.5,2.6),44);cyl('ForkWheel',(-10,y,1),1,2,35,axis='Y',n=8)
box('Pump',(3,-4,1),(8,4,6),44);beam('Handle',(6,0,4),(10,0,19),1,1,10);beam('HandleGrip',(10,-3,19),(10,3,19),1,1,10)
for y in (-2.5,2.5):cyl('SteeringWheel',(6,y,2),2,1.7,35,axis='Y',n=8)
GROUP='Truck'
box('Chassis',(-18,-7,4),(18,7,6.5),10);box('Cab_Lower',(-18,-8,6),(-5,8,12),44)
mesh('Cab',[(-18,-8,10),(-5,-8,10),(-5,8,10),(-18,8,10),(-18,-8,18),(-13,-8,24),(-5,-8,24),(-5,8,24),(-13,8,24),(-18,8,18)],[(0,1,2,3),(0,4,5,6,1),(3,2,7,8,9),(4,9,8,5),(5,8,7,6),(1,6,7,2),(0,3,9,4)],3)
wind=face('Windscreen',[(-18.06,-6.6,18.2),(-18.06,6.6,18.2),(-13.1,6.6,23.6),(-13.1,-6.6,23.6)],32)
front=face('FrontPaint',[(-18.05,7.9,6.6),(-18.05,-7.9,6.6),(-18.05,-7.9,17.8),(-18.05,7.9,17.8)],32)
for ob in (wind,front):
 for k,(u,v) in enumerate(((0,0),(1,0),(1,1),(0,1))):ob.data.uv_layers[0].data[k].uv=uv(32,.10+.80*u,.60+.30*v) if ob==wind else uv(32,u,.02+.53*v)
for y in (-8.04,8.04):face('CabDoor',[(-16.5,y,10),(-5.4,y,10),(-5.4,y,23.5),(-12.8,y,23.5)],33)
box('Bed_Floor',(-4,-8.5,6),(18,8.5,8),18)
for y in (-8.6,7.8):box('Bed_Side',(-4,y,8),(18,y+.8,14),46)
box('Tailgate',(17.5,-8,8),(18.3,8,14),46);box('Headboard',(-4.5,-8,8),(-3.7,8,15),46)
for x in (-11.5,11.5):
 for y in (-8.2,8.2):cyl('Wheel',(x,y,4.2),4.2,2.4,35,axis='Y')
box('Bumper',(-19,-8.6,5.5),(-17.9,8.6,7),2)
# Independent AO islands and bakes for every reusable export master.
plan=json.loads((O/'atlas-plan.json').read_text());alloc=plan['AO']
for group,rect in alloc.items():
 sel=[ob for ob in meshes if ob['module']==group];ma=bm if group in ('M','L') else pm;bpy.ops.object.select_all(action='DESELECT')
 for ob in meshes:ob.hide_render=ob not in sel
 for ob in sel:ob.select_set(True);ob.data.uv_layers.active_index=1;ob.data.uv_layers[1].active_render=True
 bpy.context.view_layer.objects.active=sel[0];bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=math.radians(72),island_margin=.018,area_weight=.8,scale_to_bounds=True);bpy.ops.object.mode_set(mode='OBJECT')
 ns=ma.node_tree.nodes;ls=ma.node_tree.links;bs=ns.get('Principled BSDF');node=ns['AO'];old=node.image;ao=bpy.data.images.new(group+'_AO',width=512,height=512,alpha=False);ao.colorspace_settings.name='Non-Color';node.image=ao;ns.active=node;restore=[]
 for sl in ('Base Color','Normal'):
  for link in list(bs.inputs[sl].links):restore.append((link.from_socket,link.to_socket));ls.remove(link)
 review.render.bake.margin=6;bpy.ops.object.bake(type='AO',uv_layer='UV2');ao.filepath_raw=str(O/'bakes'/f'{group}.png');ao.file_format='PNG';ao.save();node.image=old
 for a,b in restore:ls.new(a,b)
 x0,y0,x1,y1=rect
 for ob in sel:
  for q in ob.data.uv_layers[1].data:q.uv=((x0+4+q.uv.x*(x1-x0-8))/2048,1-(y1-4-q.uv.y*(y1-y0-8))/2048)
  ob.data.uv_layers.active_index=0;ob.data.uv_layers[0].active_render=True;ob.select_set(False)
 print('BAKED',group,flush=True)
for ob in meshes:ob.hide_render=False
cam=bpy.data.objects.new('Review_Camera',bpy.data.cameras.new('Review_Camera'));review.collection.objects.link(cam);review.camera=cam;target=Vector((-15,0,34));cam.location=target+Vector((-150,-220,160));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=170
review.render.resolution_x=review.render.resolution_y=1100;review.render.resolution_percentage=100;review.render.film_transparent=True;review['proposal_only']=True;review['roof_design']='Lower narrower cross gable, coherent common eave, closed valleys';review['truck_dimensions']='37.3 x 18.8 x 24; independent compact master'
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(O/'Local_Models.blend'));print('MODELS_READY',flush=True)
