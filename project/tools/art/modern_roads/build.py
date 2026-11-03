"""Build editable five-exit Quarter road layout and reusable decal modules."""
import bpy,sys,json,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[4]
sys.path[:0]=[str(ROOT/'project/tools/blender'),str(ROOT/'project/tools/blender/scene_export')]
from csc_scene_validation import suspend_csc_repairs,validate_current_scene
import decode_blend as dec
O=Path.home()/'Desktop/Codex/Quarter-Roads-Modern/draft-03-roundabout'
D=Path.home()/'Desktop/Working Files/3D Art/Decals/CSC_ALL_Modern_Roads'
assert not (D/'CSC_ALL_Modern_Roundabout_Kit.blend').exists(), 'Initial generator only: edit the current saved masters; do not regenerate them.'
J=json.loads((D/'atlas-layout.json').read_text());cells=J['cells'];center=Vector(J['roundabout']['center'])
bpy.ops.wm.read_factory_settings(use_empty=True);starter=bpy.context.scene
world=bpy.data.worlds.new('Review daylight');world.use_nodes=True
bg=world.node_tree.nodes.get('Background');bg.inputs['Color'].default_value=(.7,.8,1,1);bg.inputs['Strength'].default_value=.65
mats={}
for era in ['Industrial','Modern']:
 m=bpy.data.materials.new('CSC_Roads_'+era+'_01');m.use_nodes=True;nt=m.node_tree;p=nt.nodes.get('Principled BSDF');p.inputs['Roughness'].default_value=.94
 uv=nt.nodes.new('ShaderNodeUVMap');uv.uv_map='UV1'
 for suffix in ['B','H']:
  img=bpy.data.images.load(str(D/'textures'/f'CSC_Roads_{era}_01_{suffix}.png'));img.filepath='//textures/'+Path(img.filepath).name
  t=nt.nodes.new('ShaderNodeTexImage');t.image=img;nt.links.new(uv.outputs['UV'],t.inputs['Vector']);t.extension='EXTEND'
  if suffix=='B':nt.links.new(t.outputs['Color'],p.inputs['Base Color']);nt.links.new(t.outputs['Alpha'],p.inputs['Alpha'])
  else:
   img.colorspace_settings.name='Non-Color';b=nt.nodes.new('ShaderNodeBump');b.inputs['Strength'].default_value=.65;b.inputs['Distance'].default_value=.5;nt.links.new(t.outputs['Color'],b.inputs['Height']);nt.links.new(b.outputs['Normal'],p.inputs['Normal'])
 mats[era]=m
base=bpy.data.collections.new('STONE - complete network')
groups={k:bpy.data.collections.new('TARMAC - '+k) for k in ['Core','NW','NE','E','SE','SW','Connector']}
context=bpy.data.collections.new('REVIEW - ground and lights');export=bpy.data.collections.new('EXPORT - lifted projection geometry')
bpy.context.scene.collection.children.link(base)
rigdata=bpy.data.armatures.new('Static decal rig');rig=bpy.data.objects.new('CSC_Roads_Static',rigdata);base.objects.link(rig);export.objects.link(rig)
bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT');bone=rigdata.edit_bones.new('Bone');bone.head=(0,0,0);bone.tail=(0,0,10);bpy.ops.object.mode_set(mode='OBJECT');rig.select_set(False)
def uv(cell,u,v):
 a,b,c,d=cells[cell]['rect'];return ((a+.5+(c-a-1)*u)/512,1-(d-.5-(d-b-1)*v)/512)
modules=[]
def mesh(name,verts,faces,uvs,group):
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();me.materials.append(mats['Industrial'])
 for channel in ['UV1','UV2','UV3']:
  layer=me.uv_layers.new(name=channel)
  for poly,coords in zip(me.polygons,uvs):
   for li,co in zip(poly.loop_indices,coords):layer.data[li].uv=co
 for era in ['Industrial','Modern']:
  ob=bpy.data.objects.new(name+'_'+era,me);ob.location.z=(.04 if era=='Industrial' else .08)+len(modules)*.001;ob.visible_shadow=False;ob['review_only']=True;ob['module']=group
  ob.material_slots[0].link='OBJECT';ob.material_slots[0].material=mats[era]
  (base if era=='Industrial' else groups[group]).objects.link(ob)
  vg=ob.vertex_groups.get('Bone') or ob.vertex_groups.new(name='Bone');vg.add(list(range(len(me.vertices))),1,'REPLACE')
  mod=ob.modifiers.new('Static','ARMATURE');mod.object=rig
  # Separate projection copy; never export ground preview or review context.
  proj=ob.copy();proj.name='CSC_Projection_'+name+'_'+era;proj.location.z=20;proj['review_only']=False;proj['export_role']='fixed_geometry';proj['asset_class']='road_decal';proj['decal_states']='Worked,Unworked';export.objects.link(proj)
 modules.append({'name':name,'group':group,'vertices':len(verts),'triangles':sum(len(f)-2 for f in faces)})
def card(name,cell,pos,size,group):
 x,y=pos;w,h=size
 mesh(name,[(x-w/2,y-h/2,0),(x+w/2,y-h/2,0),(x+w/2,y+h/2,0),(x-w/2,y+h/2,0)],[(0,1,2,3)],[[uv(cell,0,0),uv(cell,1,0),uv(cell,1,1),uv(cell,0,1)]],group)
card('Roundabout','roundabout',center,(208,208),'Core')
def bezier(p0,p1,p2,p3,n=22):return [(1-t)**3*Vector(p0)+3*(1-t)**2*t*Vector(p1)+3*(1-t)*t*t*Vector(p2)+t**3*Vector(p3) for t in [i/n for i in range(n+1)]]
routes={}
anchors=json.loads((O/'classical-live.json').read_text())['anchors']
spec=[('NW',145),('NE',55),('E',-8),('SE',-75),('SW',-140)]
for name,angle in spec:
 d=Vector((math.cos(math.radians(angle)),math.sin(math.radians(angle))));p0=center+d*100
 # Reuse the exact outer classical corridor, including its tangent, at scale1.
 anchor=anchors[name];inner=Vector(anchor['inner']);outer=Vector(anchor['outer']);outward=Vector(anchor['outward'])
 back={'SE':80,'SW':65,'E':50}.get(name,40)
 routes[name]=bezier(p0,p0+d*42,inner-outward*back,inner,40)+[inner.lerp(outer,i/12) for i in range(1,13)]
# Connector joins the actual lower routes, not an invented sixth boundary exit.
a=routes['SW'][34];b=routes['SE'][36]
routes['Connector']=bezier(a,a+Vector((53,-4)),b+Vector((-64,18)),b,24)
def sweep(name,points,group,connector=False):
 # Split at cell repeats so no face interpolates through unrelated atlas cells.
 cumulative=[0]
 for a,b in zip(points,points[1:]):cumulative.append(cumulative[-1]+(b-a).length)
 length=cumulative[-1]
 def at(d):
  for i in range(len(points)-1):
   if d<=cumulative[i+1]+1e-5:
    f=(d-cumulative[i])/max(.001,cumulative[i+1]-cumulative[i]);return points[i].lerp(points[i+1],f)
  return points[-1]
 cuts=sorted(set([0,length]+([min(23,length),max(23,length-55)] if not connector else [])+[i for i in range(168 if connector else 191,int(length),168)]))
 verts=[];faces=[];uvs=[]
 for start,end in zip(cuts,cuts[1:]):
  if end-start<.01:continue
  cell='connector' if connector else ('plain' if start<23-.1 else 'end' if start>=length-55-.1 else 'straight')
  # Each piece remains at nominal width; variable path length is authored in mesh.
  n=max(1,math.ceil((end-start)/5));off=len(verts);width=30 if connector else 36
  for i in range(n+1):
   t=i/n;dist=start+(end-start)*t;p=at(dist);tangent=at(min(length,dist+.3))-at(max(0,dist-.3));tangent.normalize();normal=Vector((-tangent.y,tangent.x))
   for sign in [-1,1]:v=p+normal*width/2*sign;verts.append((v.x,v.y,0))
  for i in range(n):
   k=off+2*i;faces.append((k,k+2,k+3,k+1))
   d0=start+(end-start)*i/n;d1=start+(end-start)*(i+1)/n
   if cell=='end':u0=(d0-(length-55))/55;u1=(d1-(length-55))/55
   elif cell=='plain':u0=d0/78;u1=d1/78
   else:
    phase=0 if connector else 23;block=math.floor((start-phase+.001)/168)*168+phase;u0=(d0-block)/168;u1=(d1-block)/168
   uvs.append([uv(cell,u0,0),uv(cell,u1,0),uv(cell,u1,1),uv(cell,u0,1)])
 mesh(name,verts,faces,uvs,group)
for name,points in routes.items():sweep(name,points,name,name=='Connector')
# Flat muted grass is context only; no road pattern is procedurally painted.
me=bpy.data.meshes.new('Ground');me.from_pydata([(-800,-800,-.12),(800,-800,-.12),(800,800,-.12),(-800,800,-.12)],[],[(0,1,2,3)])
ob=bpy.data.objects.new('REVIEW_Ground',me);context.objects.link(ob);ob['review_only']=True
m=bpy.data.materials.new('REVIEW_Ground');m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.075,.095,.045,1);p.inputs['Roughness'].default_value=1;me.materials.append(m)
camdata=bpy.data.cameras.new('Overhead');cam=bpy.data.objects.new('Overhead',camdata);context.objects.link(cam);cam.location=(-7,-15,900);camdata.type='ORTHO';camdata.ortho_scale=650;camdata.clip_end=2000
ld=bpy.data.lights.new('Review_Key','SUN');ld.energy=3.2;ld.color=(1,.92,.8);ld.angle=math.radians(6);sun=bpy.data.objects.new('Review_Key',ld);sun.rotation_euler=(.4,-.3,-.6);context.objects.link(sun)
def scene(name,active=(),isexport=False):
 s=bpy.data.scenes.new(name);s.world=world;s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.transparent_max_bounces=64;s.cycles.use_denoising=True;s.render.resolution_x=1200;s.render.resolution_y=1200;s.render.resolution_percentage=100
 s.view_settings.view_transform='AgX' if isexport else 'Standard';s.view_settings.exposure=.35 if isexport else -.1;s.view_settings.gamma=1;s['asset_id']='CSC_ALL_Modern_Roundabout_Kit';s['status']='Authoring candidate; native projection/game coverage unverified'
 s.collection.children.link(export if isexport else base)
 if not isexport:
  s.collection.children.link(context);s.camera=cam
  for k in active:s.collection.children.link(groups[k])
 return s
first=['Core','NW','NE','SE']
review=scene('Review',first);scene('01 - Industrial paving');scene('03A - East destination',first+['E']);scene('03B - Southwest destination',first+['SW','Connector']);scene('04 - All routes',list(groups));scene('Export',isexport=True)
text=bpy.data.texts.new('START HERE')
text.write('Five exits and one smaller lower connector. Review opens at first-building tarmac. 03A/03B are independent alternatives, not sequential building stages. Export is a MODULE LIBRARY with both surface variants; do not export it as a single asset. Select one named module + surface per native asset. Ground previews and lifted projection meshes share mesh data. Edit mesh geometry to keep both synchronized. Projection lift20 is a candidate requiring native terrain verification. Native materials must use Decal_BaseColor, FOWColor, Heightmap alpha and Spec with Worked/Unworked visibility. No shader-only endpoint fades: masks are in B alpha. All artwork snapshots external, identical UV layouts on both 512px pages. No runtime assets changed.\n')
bpy.context.window.scene=review;bpy.data.scenes.remove(starter)
path=D/'CSC_ALL_Modern_Roundabout_Kit.blend';bpy.ops.wm.save_as_mainfile(filepath=str(path))
with suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
r=validate_current_scene();(O/'saved-scene-validation.json').write_text(json.dumps(r,indent=2));assert r['automated_pass'],r['findings']
# Independent native-format model descriptions, before conversion/readback.
(O/'models').mkdir(exist_ok=True);masters=[]
for ob in bpy.data.scenes['Export'].objects:
 if ob.type!='MESH':continue
 m=dec.decode_mesh(ob,ob.matrix_world);ident=ob.name.replace('CSC_Projection_','CSC_Road_');m['name']=ident
 for material in m['materials']:material['external']=material['name']
 model={'asset_id':ident,'kind':'decal','meshes':[m]};(O/'models'/(ident+'.json')).write_text(json.dumps(model));masters.append({'id':ident,'blend':str(path)})
(O/'masters.json').write_text(json.dumps(masters,indent=2));(D/'layout-modules.json').write_text(json.dumps({'modules':modules,'routes':{k:[list(v) for v in vs] for k,vs in routes.items()},'projection_lift':20},indent=2))
for name,fn in [('01 - Industrial paving','01_Stone'),('Review','02_First_building'),('03A - East destination','03A_East'),('03B - Southwest destination','03B_Southwest'),('04 - All routes','04_All_tarmac')]:
 if '--no-render' in sys.argv:break
 s=bpy.data.scenes[name];s.render.filepath=str(O/(fn+'.png'));bpy.ops.render.render(write_still=True,scene=name)
print('ROUNDABOUT_BUILD_PASS',str(path),flush=True)
