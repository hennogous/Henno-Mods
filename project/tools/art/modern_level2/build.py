"""Editable concept-led Level2 base and separable workshop; authoring, not AE placement."""
import bpy,bmesh,math,json,sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[4];O=Path.home()/'Desktop/Codex/modern-level2-v1-20261028'
sys.path[:0]=[str(ROOT/'project/tools/blender'),str(ROOT/'project/tools/blender/scene_export')]
from csc_scene_validation import suspend_csc_repairs,validate_current_scene
import decode_blend as dec
MODE=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'clay'
ID='CSC_Level_2_Modern';meshes=[];MODULE='Building'
COLORS=[(.65,.40,.18,1),(.17,.22,.26,1),(.30,.42,.22,1),(.58,.56,.32,1),(.72,.65,.47,1),(.62,.56,.40,1),(.08,.20,.12,1),(.10,.14,.18,1),(.13,.25,.14,1),(.30,.18,.08,1),(.3,.3,.24,1),(.5,.52,.45,1),(.24,.24,.20,1),(.04,.05,.04,1),(.08,.10,.10,1),(.45,.32,.16,1)]
bpy.ops.wm.read_factory_settings(use_empty=True);review=bpy.context.scene;review.name='Review';export=bpy.data.scenes.new('Export')
for s in (review,export):s['asset_id']=ID;s.render.engine='CYCLES';s.cycles.samples=24;s.view_settings.view_transform='Standard' if s==review else 'AgX';s.view_settings.exposure=-.1 if s==review else .35;s.view_settings.gamma=1
# Preserve the established shared source lighting.
tailor=Path.home()/'Desktop/Working Files/3D Art/TAILORS/Tailor/revision-11-l2-placement/CSC_TAILORS_Tailor.blend'
with bpy.data.libraries.load(str(tailor),link=False) as (src,dst):dst.worlds=['Review World'];dst.objects=['Review_Key']
world=dst.worlds[0];review.world=export.world=world;sun=dst.objects[0];review.collection.objects.link(sun);sun.name='Review_Key'
arm=bpy.data.armatures.new(ID);rig=bpy.data.objects.new(ID,arm);review.collection.objects.link(rig);export.collection.objects.link(rig);bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT');bone=arm.edit_bones.new('Bone');bone.head=(0,0,0);bone.tail=(0,0,5);bpy.ops.object.mode_set(mode='OBJECT');rig.select_set(False)
mat=bpy.data.materials.new('CSC_BAKERS_Modern');mat.use_nodes=True;ns=mat.node_tree.nodes;ls=mat.node_tree.links;bs=ns.get('Principled BSDF');bs.inputs['Roughness'].default_value=.72
maps={}
if MODE!='clay':
 for ch in ('B','N','G','M','AO','E'):
  n=ns.new('ShaderNodeTexImage');n.name=n.label=ch;name='CSC_Atlas_Modern'+('_B_BAKERS' if ch=='B' else '_'+ch)+'.png';n.image=bpy.data.images.load(str(O/'textures'/name));n.image.colorspace_settings.name='sRGB' if ch in ('B','E') else 'Non-Color';uv=ns.new('ShaderNodeUVMap');uv.uv_map='UV2' if ch=='AO' else 'UV3' if ch=='E' else 'UV1';ls.new(uv.outputs['UV'],n.inputs['Vector']);maps[ch]=n
 mix=ns.new('ShaderNodeMixRGB');mix.name='AO_Multiply';mix.blend_type='MULTIPLY';mix.inputs[0].default_value=.5;ls.new(maps['B'].outputs['Color'],mix.inputs[1]);ls.new(maps['AO'].outputs['Color'],mix.inputs[2]);ls.new(mix.outputs[0],bs.inputs['Base Color'])
 normal=ns.new('ShaderNodeNormalMap');normal.uv_map='UV1';ls.new(maps['N'].outputs['Color'],normal.inputs['Color']);ls.new(normal.outputs['Normal'],bs.inputs['Normal'])
 inv=ns.new('ShaderNodeMath');inv.operation='SUBTRACT';inv.inputs[0].default_value=1;ls.new(maps['G'].outputs['Color'],inv.inputs[1]);ls.new(inv.outputs[0],bs.inputs['Roughness']);ls.new(maps['M'].outputs['Color'],bs.inputs['Metallic'])
 # E is retained as authoring data; comparison renders omit emission by convention.
else:bs.inputs['Base Color'].default_value=(.42,.42,.42,1)

def uvmap(slot,u,v):
 # Stage3 top-right quadrant, 4x4 128px patches; padded sampling.
 return ((512+(slot%4)*128+2+u*124)/1024,1-((slot//4)*128+2+(1-v)*124)/1024)

def mesh(name,verts,faces,slots=0,uvs=None):
 uv_lookup={frozenset(face):dict(zip(face,uvs[i])) for i,face in enumerate(faces)} if uvs else None
 m=bpy.data.meshes.new(name);m.from_pydata(verts,[],faces);m.update();o=bpy.data.objects.new('CSC_Fixed_'+name,m);review.collection.objects.link(o);export.collection.objects.link(o);m.materials.append(mat);o['export_role']='building_geometry';o['source_asset_id']=ID;o['module']=MODULE
 # Recalculate closed construction outward; cards already use explicit front winding.
 if len(faces)>1:
  bm=bmesh.new();bm.from_mesh(m)
  if all(e.is_manifold for e in bm.edges):bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
  bm.to_mesh(m);bm.free()
 for nameuv in ('UV1','UV2','UV3'):m.uv_layers.new(name=nameuv)
 for p in m.polygons:
  slot=slots if isinstance(slots,int) else slots[p.index]
  n=p.normal;axis=max(range(3),key=lambda i:abs(n[i]));a,b=([1,2] if axis==0 else [0,2] if axis==1 else [0,1]);coords=[(m.vertices[m.loops[k].vertex_index].co[a],m.vertices[m.loops[k].vertex_index].co[b]) for k in p.loop_indices]
  lo=[min(c[i] for c in coords) for i in (0,1)];hi=[max(c[i] for c in coords) for i in (0,1)]
  for j,k in enumerate(p.loop_indices):
   u,v=uv_lookup[frozenset(p.vertices)][m.loops[k].vertex_index] if uvs else tuple((coords[j][i]-lo[i])/(32 if slot==0 else max(hi[i]-lo[i],.001)) for i in (0,1))
   m.uv_layers[0].data[k].uv=uvmap(slot,u,v);m.uv_layers[2].data[k].uv=(.02,.02)
 vg=o.vertex_groups.new(name='Bone');vg.add(list(range(len(verts))),1,'REPLACE');mod=o.modifiers.new('Static binding','ARMATURE');mod.object=rig;meshes.append(o);return o

def box(name,lo,hi,slot):
 x,y,z=lo;X,Y,Z=hi
 vs=[(x,y,z),(X,y,z),(X,Y,z),(x,Y,z),(x,y,Z),(X,y,Z),(X,Y,Z),(x,Y,Z)];fs=[(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)]
 if slot not in (0,1,7):return mesh(name,vs,fs,slot)
 vv=[];ff=[];uv=[];coverage=32 if slot!=7 else 24
 for face in fs:
  a,b,c,d=[Vector(vs[j]) for j in face];du=b-a;dv=d-a;w=du.length;h=dv.length;nx=max(1,math.ceil(w/coverage));ny=max(1,math.ceil(h/coverage))
  for j in range(ny):
   for i in range(nx):
    k=len(vv);vv +=[a+du*(i/nx)+dv*(j/ny),a+du*((i+1)/nx)+dv*(j/ny),a+du*((i+1)/nx)+dv*((j+1)/ny),a+du*(i/nx)+dv*((j+1)/ny)];ff.append((k,k+1,k+2,k+3));uv.append([(0,0),(w/nx/coverage,0),(w/nx/coverage,h/ny/coverage),(0,h/ny/coverage)])
 return mesh(name,vv,ff,slot,uv)

def panel(name,p0,p1,p2,p3,slot):return mesh(name,[p0,p1,p2,p3],[(0,1,2,3)],slot,[[(0,0),(1,0),(1,1),(0,1)]])

def wall(name,x0,x1,y,z0,z1,slot,back=False):
 # Multiple aligned patches keep brick course size equal on long and short walls.
 nx=max(1,math.ceil((x1-x0)/32));nz=max(1,round((z1-z0)/32));verts=[];faces=[];uvs=[]
 for j in range(nz):
  for i in range(nx):
   a=x0+(x1-x0)*i/nx;b=x0+(x1-x0)*(i+1)/nx;c=z0+(z1-z0)*j/nz;d=z0+(z1-z0)*(j+1)/nz;k=len(verts);verts +=[(a,y,c),(b,y,c),(b,y,d),(a,y,d)];faces.append((k,k+1,k+2,k+3) if not back else (k+3,k+2,k+1,k));uvs.append([(0,0),((b-a)/32,0),((b-a)/32,1),(0,1)] if not back else [(0,1),((b-a)/32,1),((b-a)/32,0),(0,0)])
 return mesh(name,verts,faces,slot,uvs)

def endwall(name,x,y0,y1,z0,z1,slot):
 o=wall(name,y0,y1,0,z0,z1,slot)
 for v in o.data.vertices:a=v.co.x;v.co.x=x;v.co.y=a
 if x<0:
  for p in o.data.polygons:
   old={o.data.loops[k].vertex_index:o.data.uv_layers[0].data[k].uv.copy() for k in p.loop_indices};p.flip()
   for k in p.loop_indices:o.data.uv_layers[0].data[k].uv=old[o.data.loops[k].vertex_index]
 return o

# Ground shell and upper storey, foundation reaches below terrain on all sides.
for title,z0,z1,slot in [('Foundation',-30,0,1),('Ground',0,32,1),('Upper',32,66,0)]:
 wall(title+'_Front',-40,40,-29,z0,z1,slot);wall(title+'_Rear',-40,40,29,z0,z1,slot,True);endwall(title+'_East',40,-29,29,z0,z1,slot);endwall(title+'_West',-40,-29,29,z0,z1,slot)
box('Ground_Cornice',(-41,-30,31),(41,30,34),4)
profile=[(-34,64),(-27,69),(-19,79),(-10,94),(0,110),(10,94),(19,79),(27,69),(34,64)]
for x in (-40,40):
 polygon=[(-29,66),(29,66)]+[(y,z-2) for y,z in reversed(profile[1:-1])]
 def clip(poly,axis,bound,above):
  result=[]
  for a,b in zip(poly,poly[1:]+poly[:1]):
   ia=a[axis]>=bound if above else a[axis]<=bound;ib=b[axis]>=bound if above else b[axis]<=bound
   if ia:result.append(a)
   if ia!=ib:
    t=(bound-a[axis])/(b[axis]-a[axis]);result.append(tuple(a[k]+t*(b[k]-a[k]) for k in (0,1)))
  return result
 for y0 in (-32,0):
  for z0 in (64,96):
   poly=polygon[:]
   for axis,bound,above in [(0,y0,True),(0,y0+32,False),(1,z0,True),(1,z0+32,False)]:poly=clip(poly,axis,bound,above) if poly else []
   if len(poly)<3:continue
   if x<0:poly.reverse()
   mesh('Brick_Gable_'+str(x),[(x,y,z) for y,z in poly],[tuple(range(len(poly)))],0,[[((y-y0)/32,(z-z0)/32) for y,z in poly]])
 box('Gable_Cream_Crossbeam_'+str(x),(x-1,-29,65),(x+1,29,68),4)
# Main roof split into registered strips: UV V follows the slope and seam direction.
for sign in (-1,1):
 pts=[(abs(y),z) for y,z in profile if y>=0];verts=[];faces=[];uvs=[]
 for i in range(len(pts)-1):
  a,z=pts[i];b,Z=pts[i+1]
  for x0,x1 in [(-44,0),(0,44)]:
   k=len(verts);verts +=[(x0,sign*a,z),(x1,sign*a,z),(x1,sign*b,Z),(x0,sign*b,Z)];faces.append((k,k+1,k+2,k+3));uvs.append([(0,1-a/34),(1,1-a/34),(1,1-b/34),(0,1-b/34)])
 o=mesh('Roof_'+str(sign),verts,faces,2,uvs)
 # Thickness is silhouette geometry, the seams remain in B/N.
 for p in o.data.polygons:
  if p.normal.z<0:
   old={o.data.loops[k].vertex_index:o.data.uv_layers[0].data[k].uv.copy() for k in p.loop_indices};p.flip()
   for k in p.loop_indices:o.data.uv_layers[0].data[k].uv=old[o.data.loops[k].vertex_index]
 for i in range(len(pts)-1):
  a,z=pts[i];b,Z=pts[i+1]
  for x in (-44,44):panel('Roof_Edge', (x,sign*a,z-1.8),(x,sign*b,Z-1.8),(x,sign*b,Z),(x,sign*a,z),8)
 for i in range(len(pts)-1):
  a,z=pts[i];b,Z=pts[i+1];panel('Roof_Underside',(-44,sign*a,z-1.8),(-44,sign*b,Z-1.8),(44,sign*b,Z-1.8),(44,sign*a,z-1.8),8)

def trim(name,x):
 # Swept bargeboard with genuine cross-slope width, matching the concept.
 verts=[]
 for i,(y,z) in enumerate(profile):
  a=Vector(profile[max(0,i-1)]);b=Vector(profile[min(len(profile)-1,i+1)]);t=(b-a).normalized();n=Vector((-t.y,t.x))
  for xx,d in [(x-2,-2.1),(x+2,-2.1),(x+2,2.1),(x-2,2.1)]:verts.append((xx,y+n.x*d,z+n.y*d+.7))
 faces=[(3,2,1,0)]
 for i in range(len(profile)-1):
  for j in range(4):faces.append((4*i+j,4*i+(j+1)%4,4*(i+1)+(j+1)%4,4*(i+1)+j))
 faces.append(tuple(4*(len(profile)-1)+j for j in range(4)));mesh(name,verts,faces,3)
trim('Cream_Bargeboard_Left',-44);trim('Cream_Bargeboard_Right',44)
box('Bold_Ridge',(-48,-2.6,109),(48,2.6,113),3)
for x in (-21,21):
 # Shed dormer cheeks, tall painted inset and shallow metal cap.
 mesh('Dormer_Cheek_'+str(x),[(x-8,-23,78),(x+8,-23,78),(x+8,-23,96),(x-8,-23,96),(x-8,-7,98),(x+8,-7,98)],[(0,1,2,3),(3,2,5,4),(0,3,4),(1,5,2)],8)
 panel('Dormer_Window_'+str(x),(x-7.6,-23.08,78.5),(x+7.6,-23.08,78.5),(x+7.6,-23.08,96),(x-7.6,-23.08,96),5)
 mesh('Dormer_Shed_Roof_'+str(x),[(x-10,-26,96),(x+10,-26,96),(x+10,-6,100),(x-10,-6,100),(x-10,-26,97.8),(x+10,-26,97.8),(x+10,-6,101.8),(x-10,-6,101.8)],[(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)],[8,4,4,4,4,2])
for x in (-21,21):
 panel('Front_Upper_Window_'+str(x),(x-8,-29.08,43),(x+8,-29.08,43),(x+8,-29.08,63),(x-8,-29.08,63),5)
 panel('Rear_Upper_Window_'+str(x),(x+8,29.08,43),(x-8,29.08,43),(x-8,29.08,63),(x+8,29.08,63),5)
for x in (-40.08,40.08):
 if x>0:corners=lambda y0,y1,z0,z1:[(x,y0,z0),(x,y1,z0),(x,y1,z1),(x,y0,z1)]
 else:corners=lambda y0,y1,z0,z1:[(x,y1,z0),(x,y0,z0),(x,y0,z1),(x,y1,z1)]
 panel('Gable_Upper_Window_'+str(x),*corners(-13,13,43,63),5)
 panel('Attic_Window_'+str(x),*corners(-6,6,75,89),5)
 for y in (-13,13):panel('Shopfront_'+str(x)+'_'+str(y),*corners(y-9,y+9,1,29),6)
for x in (-21,21):panel('Front_Ground_Glazing_'+str(x),(x-10,-29.08,1),(x+10,-29.08,1),(x+10,-29.08,29),(x-10,-29.08,29),6)
# Quiet back service door, no decorative props or bakery-specific sign.
panel('Rear_Service_Door', (9,29.08,0),(-9,29.08,0),(-9,29.08,28),(9,29.08,28),8)
box('Chimney_Shaft',(6,6,91),(18,18,120),7);box('Chimney_Cap',(4.8,4.8,119),(19.2,19.2,122),1)
panel('Chimney_Dark_Mouth',(8,8,122.08),(16,8,122.08),(16,16,122.08),(8,16,122.08),13)

MODULE='Workshop'
# Separate low workshop module from the concept. Its open portal has real interior.
box('Workshop_Left_Wall',(-77,-30,-30),(-73,22,35.47),0);box('Workshop_Right_Wall',(-42,-30,-30),(-39,22,35.47),0);box('Workshop_Back_Wall',(-73,19,-30),(-42,22,43.7),0)
for x0,x1 in [(-77,-73),(-42,-39)]:
 for y0,y1 in [(-30,-4),(-4,22)]:
  za=35+(y0+33)*9/57;zb=35+(y1+33)*9/57
  mesh('Workshop_Sloped_Closure',[(x0,y0,35.4),(x1,y0,35.4),(x1,y1,35.4),(x0,y1,35.4),(x0,y0,za),(x1,y0,za),(x1,y1,zb),(x0,y1,zb)],[(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)],0)
box('Workshop_Left_Plinth',(-77.2,-30,-30),(-72.8,22,6),1);box('Workshop_Floor',(-73,-28,-2),(-42,19,0),12)
box('Workshop_Portal_Header',(-77,-30,32),(-39,-26,36),0)
mesh('Workshop_Roof',[(-79,-33,35),(-38,-33,35),(-38,24,44),(-79,24,44),(-79,-33,37),(-38,-33,37),(-38,24,46),(-79,24,46)],[(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)],[8,3,3,3,3,2])
box('Workshop_Portal_Left_Jamb',(-73.8,-30.4,0),(-71.3,-27.5,32),8);box('Workshop_Portal_Right_Jamb',(-44,-30.4,0),(-41.5,-27.5,32),8)
# Review cameras; fixed empty-shell view, no emission.
camdata=bpy.data.cameras.new('Concept_Camera');cam=bpy.data.objects.new('Concept_Camera',camdata);review.collection.objects.link(cam);target=Vector((-12,0,54));cam.location=target+Vector((250,-250,260));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();camdata.type='ORTHO';camdata.ortho_scale=177;review.camera=cam
review.render.resolution_x=review.render.resolution_y=1100;review.render.resolution_percentage=100;review.render.film_transparent=True;review.render.image_settings.file_format='PNG';review.render.image_settings.color_mode='RGBA'
review.render.threads_mode='FIXED';review.render.threads=4
if MODE=='clay':
 for o in meshes:
  bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.0001,plane_co=(0,0,0),plane_no=(0,0,1),clear_inner=True,clear_outer=False);bm.to_mesh(o.data);bm.free()
 (O/'review').mkdir(exist_ok=True);review.render.filepath=str(O/'review/Blockout.png');bpy.ops.render.render(write_still=True)
 cam.location=(-12,0,260);cam.rotation_euler=(0,0,0);review.render.filepath=str(O/'review/Blockout_Top.png');bpy.ops.render.render(write_still=True)
 print('BLOCKOUT_READY',sum(len(o.data.vertices) for o in meshes),flush=True)
else:
 # Independent UV2 unwrap and self AO per reusable module.
 for group,rect in [('Building',(1024,0,1536,512)),('Workshop',(1536,0,1792,256))]:
  selected=[o for o in meshes if o['module']==group]
  bpy.ops.object.select_all(action='DESELECT')
  for o in meshes:o.hide_render=o not in selected
  for o in selected:o.select_set(True);o.data.uv_layers.active_index=1
  bpy.context.view_layer.objects.active=selected[0];bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=math.radians(70),island_margin=.014,area_weight=.8,scale_to_bounds=True);bpy.ops.object.mode_set(mode='OBJECT')
  ao=bpy.data.images.new(group+'_AO',width=1024 if group=='Building' else 512,height=1024 if group=='Building' else 512,alpha=False);ao.colorspace_settings.name='Non-Color';old=maps['AO'].image;maps['AO'].image=ao;ns.active=maps['AO'];review.render.bake.margin=8
  restore=[(l.from_socket,l.to_socket) for slot in ('Base Color','Normal') for l in list(bs.inputs[slot].links)]
  for slot in ('Base Color','Normal'):
   for l in list(bs.inputs[slot].links):ls.remove(l)
  bpy.ops.object.bake(type='AO',uv_layer='UV2');(O/'bakes').mkdir(exist_ok=True);ao.filepath_raw=str(O/'bakes'/(group+'.png'));ao.file_format='PNG';ao.save();maps['AO'].image=old
  for a,b in restore:ls.new(a,b)
  x0,y0,x1,y1=rect
  for o in selected:
   for d in o.data.uv_layers[1].data:d.uv=((x0+4+d.uv.x*(x1-x0-8))/2048,1-(y1-4-d.uv.y*(y1-y0-8))/2048)
   o.data.uv_layers.active_index=0;o.select_set(False)
 for o in meshes:o.hide_render=False
 (O/'models').mkdir(exist_ok=True)
 for group in ('Building','Workshop'):
  ident=ID if group=='Building' else 'CSC_Level_2_Modern_Workshop'
  model={'asset_id':ident,'kind':'building','meshes':[dec.merge_meshes(ident,[dec.decode_mesh(o,o.matrix_world) for o in meshes if o['module']==group])]}
  (O/'models'/(ident+'.json')).write_text(json.dumps(model))
 for n in maps.values():n.image.filepath='//textures/'+Path(n.image.filepath).name
 bpy.ops.object.select_all(action='DESELECT');bpy.context.window.scene=review
 bpy.ops.wm.save_as_mainfile(filepath=str(O/(ID+'_Assembly.blend')),relative_remap=False)
 print('PAINTED_BUILD_READY',flush=True)
