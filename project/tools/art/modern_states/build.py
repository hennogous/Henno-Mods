"""Current worked geometry -> reusable modern construction/pillage masters.

Surface artwork is reused verbatim. Only independent geometry AO is baked.
"""
import bpy,bmesh,sys,math,json,hashlib
from pathlib import Path
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[4]
sys.path[:0]=[str(ROOT/'project/tools/blender/scene_export'),str(ROOT/'project/tools/blender')]
import decode_blend as dec
from csc_scene_validation import suspend_csc_repairs,validate_current_scene
ART=Path.home()/'Desktop/Working Files/3D Art'; OUT=Path.home()/'Desktop/Codex/modern-l1-states-20261028'
F=Matrix.Rotation(math.radians(42.3),4,'Z')@Matrix.Translation(Vector((-101,-126,0)))
W=Matrix.Translation(Vector((-34,20.5,6.15)))
BASE='CSC_Level_1_S_Modern';SILO='CSC_BAKERS_Mill_Silo_Modern';WATER='CSC_BAKERS_Water_Mill_Modern'
SOURCES={BASE:ART/'Level 1/modern/revision-04-painted-kit'/f'{BASE}.blend',SILO:ART/'BAKERS/Wind Mill/modern/revision-10-painted-kit'/f'{SILO}.blend',WATER:ART/'BAKERS/Water Mill/modern/revision-02-painted-kit'/f'{WATER}.blend'}
AO={BASE:('building',[0,512,512,1024]),SILO:('props',[0,512,512,768])}
def dump(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2,default=str))
def channel(kind,ch):return ('CSC_Atlas_Modern_B_BAKERS' if ch=='B' else 'CSC_Atlas_Modern_'+ch) if kind=='building' else 'CSC_Props_Modern_01_'+ch
def current(kind):return ART/'Textures'/('CSC_Buildings_Modern' if kind=='building' else 'CSC_Props_Modern')/'Current'
def material_setup(mat,kind):
 for n in mat.node_tree.nodes:
  ch=n.label or n.name
  if n.type=='TEX_IMAGE' and ch in ('B','N','G','M','E','AO'):
   p=(OUT/'textures' if ch=='AO' else current(kind)/'textures')/(channel(kind,ch)+'.png')
   n.image=bpy.data.images.load(str(p),check_existing=False);n.image.colorspace_settings.name='sRGB' if ch in ('B','E') else 'Non-Color'
 for n in mat.node_tree.nodes:
  if n.type=='BSDF_PRINCIPLED':n.inputs['Emission Strength'].default_value=0
def freeze(o):
 m=o.matrix_world.copy();o.data=o.data.copy();o.parent=None;o.modifiers.clear();o.matrix_world=Matrix.Identity(4);o.data.transform(m)
def group(o):
 if o.name in ('DIS_CTY_Watermill_AN_Base','Water_Mill_Floor'):return 'RiverFoundation'
 if o.get('state_scaffold')=='silo_side':return 'ScaffoldSiloSide'
 if o.get('state_scaffold'):return 'Scaffold'
 if o.get('wind_tie_in'):return 'WindTieIn'
 if (any(t in o.name for t in ('Shelter_Header','Shelter_Brace','Shelter_Side_Bearer','State_Shelter_Ridge','State_Shelter_Rafter_A_-64','State_Shelter_Rafter_B_-64')) or (('-65' in o.name) and ('Support_Foot' in o.name or 'Shelter_Support' in o.name))):return 'SiloFrontFrame'
 if o.get('optional_silo_side_support'):return 'SiloSideSupports'
 if 'Shelter' in o.name or 'Support_Foot' in o.name:return 'Shelter'
 return 'Building'
def skin(o,rig,ident):
 o.parent=rig;o.matrix_parent_inverse=Matrix.Identity(4);o.matrix_world=Matrix.Identity(4)
 o.vertex_groups.clear();g=o.vertex_groups.new(name='Bone');g.add(list(range(len(o.data.vertices))),1,'REPLACE')
 m=o.modifiers.new('Static Bone','ARMATURE');m.object=rig
 o['export_role']='building_geometry';o['source_asset_id']=ident;o['state_group']=group(o)
def new_mesh(name,verts,faces,tile,mat,frame=F,kind='building',region=None):
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();ob=bpy.data.objects.new(name,me);scene.collection.objects.link(ob);review.collection.objects.link(ob);me.materials.append(mat)
 uv=me.uv_layers.new(name='UV1')
 for poly in me.polygons:
  normal=poly.normal;axis=max(range(3),key=lambda a:abs(normal[a]));axes=[a for a in range(3) if a!=axis]
  if region==(0,256,128,65):
   # This painted wood patch has horizontal grain: U must follow the member's
   # longest local dimension before the beam is rotated into its final placement.
   ext={a:max(v[a] for v in verts)-min(v[a] for v in verts) for a in axes};axes.sort(key=lambda a:ext[a],reverse=True)
  co=[Vector(verts[me.loops[i].vertex_index]) for i in poly.loop_indices];lo=[min(v[a] for v in co) for a in axes];hi=[max(v[a] for v in co) for a in axes]
  # Use matching world sampling; brick ~5.5 units per course. Timber grain follows each member.
  span=[min(.94,(hi[j]-lo[j])/70) for j in range(2)]
  if region==(0,256,128,65):span[1]=min(.94,(hi[1]-lo[1])/35)
  if region:cx,cy,cw,ch=region
  else:cx=(tile%(4 if kind=='building' else 8))*128;cy=(tile//(4 if kind=='building' else 8))*128;cw=ch=128
  for i,v in zip(poly.loop_indices,co):
   xy=[(v[a]-lo[j])/max(hi[j]-lo[j],1e-5) for j,a in enumerate(axes)]
   uv.data[i].uv=((cx+4+xy[0]*span[0]*(cw-8))/1024,1-(cy+4+(1-xy[1])*span[1]*(ch-8))/1024)
 me.uv_layers.new(name='UV2');u3=me.uv_layers.new(name='UV3')
 for d in u3.data:d.uv=(.02,.02)
 if region==(0,256,128,65):ob['timber_grain']='U follows longest member axis; V across grain; small end faces use compact wood sample'
 me.transform(frame);objects.append(ob);return ob
def box(name,c,size,tile=8,mat=None,frame=F,kind='building',region=None):
 x,y,z=c;a,b,d=[s/2 for s in size];v=[(x+i*a,y+j*b,z+k*d) for i,j,k in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
 return new_mesh(name,v,[(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)],tile,mat or material,frame,kind,region)
def beam(name,a,b,width=3.2):
 a,b=Vector(a),Vector(b);delta=b-a;r=delta.to_track_quat('Z','Y').to_matrix().to_4x4();o=box(name,(0,0,0),(width,width,delta.length),region=(0,256,128,65),frame=Matrix.Identity(4));o.data.transform(F@Matrix.Translation((a+b)/2)@r);return o
def strip(name,points,width,bottom=35.5,tile=0):
 # Closed thick wall along a polyline with a stepped/broken top, no zero-thickness surfaces.
 vs=[]
 for x,y,h in points:vs.extend([(x-width/2,y-width/2,bottom),(x+width/2,y+width/2,bottom),(x-width/2,y-width/2,h),(x+width/2,y+width/2,h)])
 # x-directed and y-directed strips need the perpendicular thickness axis.
 alongx=abs(points[-1][0]-points[0][0])>abs(points[-1][1]-points[0][1])
 vs=[]
 for x,y,h in points:
  dx,dy=(0,width/2) if alongx else (width/2,0)
  vs.extend([(x-dx,y-dy,bottom),(x+dx,y+dy,bottom),(x-dx,y-dy,h),(x+dx,y+dy,h)])
 faces=[(0,1,3,2)]
 for j in range(len(points)-1):
  k=4*j;n=k+4;faces.extend([(k,n,n+2,k+2),(k+1,k+3,n+3,n+1),(k+2,n+2,n+3,k+3),(k,k+1,n+1,n)])
 k=4*(len(points)-1);faces.append((k,k+2,k+3,k+1));ob=new_mesh(name,vs,faces,tile,material)
 # Orientation changes with the strip axis. Closed shells must have consistent
 # outward winding before AO; a negative-volume wall bakes black from inside.
 bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert bm.calc_volume(signed=True)>0;assert all(e.is_contiguous for e in bm.edges);bm.to_mesh(ob.data);bm.free();return ob
def scaffold(ident,center,scale):
 source=ART/'Level 1/CSC_Level_1_S_CON+PIL.blend'
 with bpy.data.libraries.load(str(source),link=False) as (a,b):b.objects=['Scaffolding']
 o=b.objects[0];scene.collection.objects.link(o);review.collection.objects.link(o);bpy.context.view_layer.update();freeze(o)
 pts=[F.inverted()@v.co for v in o.data.vertices];cx=(min(v.x for v in pts)+max(v.x for v in pts))/2;cy=(min(v.y for v in pts)+max(v.y for v in pts))/2
 for v,p in zip(o.data.vertices,pts):v.co=F@(Vector(((p.x-cx)*scale,(p.y-cy)*scale,p.z*scale))+Vector(center))
 o.name=ident+'_Scaffolding';o['state_scaffold']=True;o['civ_visible_states']=json.dumps(['Construction'])
 o.data.materials[0]['civ_material']='Pillage_Construction_01'
 # Existing authored static scaffold, native surface/UVs preserved; no animated pantry mesh conversion.
 while len(o.data.uv_layers)<3:o.data.uv_layers.new(name='UV'+str(len(o.data.uv_layers)+1))
 for i,u in enumerate(o.data.uv_layers):u.name='UV'+str(i+1)
 objects.append(o)
 if ident==BASE:
  # Preserve both native timber scaffold sections on the full shelter; the
  # right-hand section intersects the silo and is separately hidden on Wind.
  other=o.copy();other.data=o.data.copy();other.name=ident+'_Scaffolding_SiloSide';other['state_scaffold']='silo_side';scene.collection.objects.link(other);review.collection.objects.link(other);objects.append(other)
  for item,keep_right in ((o,False),(other,True)):
   bm=bmesh.new();bm.from_mesh(item.data);delete=[p for p in bm.faces if ((F.inverted()@p.calc_center_median()).x>15)!=keep_right];bmesh.ops.delete(bm,geom=delete,context='FACES')
   bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS');bm.to_mesh(item.data);bm.free();item.data.update()
def bake(base):
 kind,rect=AO[base];obs=[o for o in objects if not o.get('state_scaffold') and not o.get('wind_tie_in')]
 bpy.ops.object.select_all(action='DESELECT')
 for o in obs:o.select_set(True);o.data.uv_layers.active_index=1;o.data.uv_layers[1].active_render=True
 bpy.context.view_layer.objects.active=obs[0];bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=math.radians(70),island_margin=.018,area_weight=.5,scale_to_bounds=True);bpy.ops.object.mode_set(mode='OBJECT')
 w,h=rect[2]-rect[0],rect[3]-rect[1];im=bpy.data.images.new(base+'_STATE_AO',width=w,height=h,alpha=False);im.colorspace_settings.name='Non-Color'
 ns=material.node_tree.nodes;node=next(n for n in ns if n.type=='TEX_IMAGE' and (n.label or n.name)=='AO');old=node.image;node.image=im;ns.active=node
 for o in objects:
  if o.get('state_scaffold') or o.get('wind_tie_in'):o.hide_render=True
 links=material.node_tree.links;normal_links=[(l.from_socket,l.to_socket) for n in ns if n.type=='BSDF_PRINCIPLED' for l in n.inputs['Normal'].links]
 for n in ns:
  if n.type=='BSDF_PRINCIPLED':
   for l in list(n.inputs['Normal'].links):links.remove(l)
 scene.render.engine='CYCLES';scene.cycles.samples=128;scene.render.bake.margin=6
 bpy.ops.object.bake(type='AO',uv_layer='UV2');p=OUT/'bakes'/(base+'_CON+PIL.png');p.parent.mkdir(exist_ok=True);im.filepath_raw=str(p);im.file_format='PNG';im.save();node.image=old
 for a,b in normal_links:links.new(a,b)
 for o in obs:
  for u in o.data.uv_layers[1].data:u.uv=(rect[0]/2048+u.uv.x*w/2048,1-rect[3]/2048+u.uv.y*h/2048)
  o.data.uv_layers.active_index=0;o.data.uv_layers[0].active_render=True
 for o in objects:
  if o.get('wind_tie_in'):
   source=bpy.data.objects['State_Shelter_Ridge' if o.name=='State_Wind_Ridge' else 'CSC_Fixed_Shelter_Side_Bearer_'+o.name.split('_')[-1]]
   assert len(source.data.uv_layers[1].data)==len(o.data.uv_layers[1].data)
   for a,b in zip(o.data.uv_layers[1].data,source.data.uv_layers[1].data):a.uv=b.uv
 for o in objects:o.hide_render=False
def save_decode(base):
 ident=base+'_CON+PIL';rig.name=ident;rig.data.name=ident
 for o in objects:skin(o,rig,ident)
 scene['asset_id']=ident;scene['con_pil_retake']='Current worked footprint, open shell; scaffold Construction only.'
 scene['kind']='building';scene['asset_kind']='building'
 for im in bpy.data.images:
  if im.filepath:im.filepath=str(Path(bpy.path.abspath(im.filepath)).resolve())
 meshes=[]
 for g in sorted({group(o) for o in objects}):
  ms=[dec.decode_mesh(o,o.matrix_world) for o in objects if group(o)==g];meshes.append(dec.merge_meshes(ident+'_'+g,ms))
 dump(OUT/'models'/(ident+'.json'),{'asset_id':ident,'kind':'building','meshes':meshes})
 folder=OUT/'masters'/ident;folder.mkdir(parents=True,exist_ok=True)
 bpy.context.window.scene=scene;bpy.context.preferences.filepaths.save_version=0
 bpy.ops.wm.save_as_mainfile(filepath=str(folder/(ident+'.blend')),relative_remap=False)
 dump(folder/'validation.json',validate_current_scene())
 timber=[]
 for o in objects:
  if not o.get('timber_grain'):continue
  uv=o.data.uv_layers[0];checks=[]
  for p in o.data.polygons:
   pairs=[(i,p.loop_indices[(j+1)%len(p.loop_indices)]) for j,i in enumerate(p.loop_indices)]
   longest=max(pairs,key=lambda ij:(o.data.vertices[o.data.loops[ij[0]].vertex_index].co-o.data.vertices[o.data.loops[ij[1]].vertex_index].co).length)
   i,j=longest;length=(o.data.vertices[o.data.loops[i].vertex_index].co-o.data.vertices[o.data.loops[j].vertex_index].co).length
   if length>5:
    delta=uv.data[i].uv-uv.data[j].uv;assert abs(delta.y)<1e-5 and abs(delta.x)>1e-5,(o.name,p.index,list(delta));checks.append({'face':p.index,'pixels_per_unit':round(abs(delta.x)*1024/length,3)})
  timber.append({'object':o.name,'long_faces':checks,'grain_aligned':True})
 dump(folder/'timber-UV-audit.json',timber)
 print('AUTHORED',ident,[(m['name'],len(m['vertices']),len(m['triangles'])) for m in meshes],flush=True)

with suspend_csc_repairs():
 for base in (BASE,SILO):
  bpy.ops.wm.open_mainfile(filepath=str(SOURCES[base]),load_ui=False,use_scripts=False);scene=bpy.data.scenes['Export'];review=bpy.data.scenes['Review'];bpy.context.window.scene=scene;bpy.context.view_layer.update();rig=next(o for o in scene.objects if o.type=='ARMATURE');rig.matrix_world=Matrix.Identity(4);objects=[]
  kind=AO[base][0];material=bpy.data.materials['CSC_BAKERS_Modern' if kind=='building' else 'CSC_Props_Modern_01'];material_setup(material,kind)
  if base==BASE:
   keep=lambda n: any(t in n for t in ('Foundation','Front_Lower','Rear_Lower','End_Lower','Entrance_','Support_Foot','Shelter_Support','Shelter_Header','Shelter_Brace','Shelter_Side_Bearer'))
  else:keep=lambda n:any(t in n for t in ('Silo_Foundation','Silo_Foot_Rim','Elevator_Foundation','Intake_Foundation'))
  for o in list(bpy.data.objects):
   if o.type!='MESH':continue
   if o in scene.objects.values() and keep(o.name):freeze(o);objects.append(o)
   else:bpy.data.objects.remove(o,do_unlink=True)
  if base==BASE:
   # Current lower shell retained exactly; upper remains and rafters replace complete walls/roof.
   for y in (-23,23):
    box('State_RingBeam_'+str(y),(0,y,34),(84,3,4),5)
   for x in (-41,41):box('State_RingBeam_End_'+str(x),(x,0,34),(3,44,4),5)
   strip('State_Brick_Front',[(-42,-23,59),(-26,-23,55),(-16,-23,42),(3,-23,38),(20,-23,43),(42,-23,58)],2.5)
   strip('State_Brick_Rear',[(-42,23,61),(-18,23,60),(-3,23,45),(12,23,41),(28,23,57),(42,23,61)],2.5)
   strip('State_Brick_Entrance',[(-41,-22,59),(-41,-9,58),(-41,1,45),(-41,13,52),(-41,22,61)],2.5)
   strip('State_Brick_End',[(41,-22,58),(41,-8,53),(41,7,42),(41,22,61)],2.5)
   # Interior masonry lining behind the single surface ground-floor blocks.
   for y in (-22.7,22.7):box('State_Inner_Stone_'+str(y),(0,y,16),(80,1,32),1)
   box('State_Inner_Stone_End',(40,0,16),(1,44,32),1)
   for x in (-38,1,38):
    beam('State_Rafter_A_'+str(x),(x,-23,61.3),(x,0,74),3)
    beam('State_Rafter_B_'+str(x),(x,0,74),(x,23,61.3),3)
    if x!=1:beam('State_Tie_'+str(x),(x,-23,60),(x,23,60),3)
   for x in (-38,38):
    for y in (-23,23):beam('State_Upper_Post_'+str(x)+'_'+str(y),(x,y,34),(x,y,61.3),3)
   beam('State_Ridge',(-41,0,74),(41,0,74),3.5)
   for y in (-64,-30):
    beam('State_Shelter_Rafter_A_'+str(y),(2,y,39),(22,y,51),3)
    beam('State_Shelter_Rafter_B_'+str(y),(22,y,51),(42,y,39),3)
   beam('State_Shelter_Ridge',(22,-66,51),(22,-26,51),3.5)
   for x in (3,41):
    o=box('State_Wind_Side_Bearer_'+str(x),(x,-38.5,38.2),(3.6,23,3.6),4);o['wind_tie_in']=True
   o=beam('State_Wind_Ridge',(22,-49,51),(22,-26,51),3.5);o['wind_tie_in']=True
   scaffold(base,(11,-56,0),.83)
  else:
   # Current silo's 16-sided shell: original centre/radius, thick open rim and deep footing.
   cx,cy=22.030,-76.075;n=16;hs=[63,63,60,47,43,46,52,69,72,69,64,54,42,39,49,58];vs=[]
   for radius,top in ((24,False),(24,True),(21.7,False),(21.7,True)):
    for i in range(n):
     a=math.pi/2+i*2*math.pi/n;vs.append((cx+radius*math.cos(a),cy+radius*math.sin(a),hs[i] if top else 16))
   fs=[]
   for i in range(n):
    j=(i+1)%n;fs.extend([(i,j,n+j,n+i),(2*n+j,2*n+i,3*n+i,3*n+j),(n+i,n+j,3*n+j,3*n+i)])
   ob=new_mesh('State_Silo_Open_Shell',vs,fs,3,material,kind='props')
   # Preserve painted sheet sampling around circumference, no wheat graphic repeated per panel.
   for p in ob.data.polygons:
    for li in p.loop_indices:
     idx=ob.data.loops[li].vertex_index;v=vs[idx];u=(idx%n)/(n-1);z=(v[2]-16)/59
     ob.data.uv_layers[0].data[li].uv=((3*128+5+u*118)/1024,1-(5+(1-z)*118)/1024)
   box('State_Elevator_Stump',(51.206,-92.633,27),(13,12,42),9,material,kind='props')
   scaffold(base,(24,-119,0),.60)
  bake(base);save_decode(base)
 # Water derivative uses the same reusable shell, transformed into its existing frame.
 bpy.ops.wm.open_mainfile(filepath=str(OUT/'masters'/(BASE+'_CON+PIL')/(BASE+'_CON+PIL.blend')),load_ui=False,use_scripts=False)
 scene=bpy.data.scenes['Export'];review=bpy.data.scenes['Review'];bpy.context.window.scene=scene;rig=next(o for o in scene.objects if o.type=='ARMATURE');objects=[o for o in scene.objects if o.type=='MESH']
 for o in objects:freeze(o);o.data.transform(W@F.inverted())
 with bpy.data.libraries.load(str(SOURCES[WATER]),link=False) as (a,b):b.objects=['DIS_CTY_Watermill_AN_Base','Water_Mill_Floor']
 for o in b.objects:
  scene.collection.objects.link(o);review.collection.objects.link(o);bpy.context.view_layer.update();freeze(o);objects.append(o)
  for mat in o.data.materials:material_setup(mat,'props')
 save_decode(WATER)
 dump(OUT/'authoring.json',{'sources':{k:{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for k,p in SOURCES.items()},'AO':AO,'water_transform':[list(r) for r in W@F.inverted()],'worked_sources_untouched':True})
