"""Editable Bakery masters, self-AO, native exports and saved-file validation."""
import bpy,math,json,sys,shutil,copy,subprocess,hashlib,importlib.util
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).parent))
from bakery_props_atlas import ROOT,OUT,STAGE,SOURCE,RELEASE
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
C=module('coach_shapes',ROOT/'project/tools/art/build_fashion_coach.py')
C.REGIONS={r['name']:r['bounds'] for r in json.loads((STAGE/'atlas/manifest.json').read_text())['regions']}
V=module('bakery_validator',ROOT/'project/tools/blender/csc_scene_validation.py')
E=module('bakery_cn6',ROOT/'project/tools/scripts/io_export_cn6_b4.py')
IDS=['CSC_BAKERS_Peel','CSC_BAKERS_Dough_Set','CSC_BAKERS_Bread_Basket_Round','CSC_BAKERS_Bread_Basket_Oval','CSC_BAKERS_Bread_Basket_Long','CSC_BAKERS_Bread_Cart','CSC_BAKERS_Oven_v2']
def setup(ident):
 global export,review,mat,rig
 bpy.ops.wm.read_factory_settings(use_empty=True);export=bpy.context.scene;export.name='Export';review=bpy.data.scenes.new('Review')
 C.export=export;C.review=review;C.PARTS=[];C.ID=ident
 mat=bpy.data.materials.new('CSC_ALL_Props_01');mat['civ_material']='CSC_ALL_Props_01';mat.use_nodes=True;mat.surface_render_method='DITHERED'
 nt=mat.node_tree;nt.nodes.clear();bs=nt.nodes.new('ShaderNodeBsdfPrincipled');bs.inputs['Roughness'].default_value=.8;out=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(bs.outputs[0],out.inputs[0])
 for k in ['B','N','G','M','AO','O']:
  im=bpy.data.images.load(str(SOURCE/'textures'/f'CSC_Props_Shared_01_{k}.png'),check_existing=True);im.colorspace_settings.name='sRGB' if k=='B' else 'Non-Color'
  node=nt.nodes.new('ShaderNodeTexImage');node.image=im;node.label=k;uv=nt.nodes.new('ShaderNodeUVMap');uv.uv_map='UV2' if k=='AO' else 'UV1';nt.links.new(uv.outputs[0],node.inputs[0])
  if k=='B':base=node
  if k=='AO':ao=node
  if k=='O':nt.links.new(node.outputs[0],bs.inputs['Alpha'])
  if k=='N':normal=nt.nodes.new('ShaderNodeNormalMap');nt.links.new(node.outputs[0],normal.inputs[1]);nt.links.new(normal.outputs[0],bs.inputs['Normal'])
 mix=nt.nodes.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=.5;nt.links.new(base.outputs[0],mix.inputs[1]);nt.links.new(ao.outputs[0],mix.inputs[2]);nt.links.new(mix.outputs[0],bs.inputs['Base Color']);C.mat=mat
 rd=bpy.data.armatures.new(ident+'_Rig');rig=bpy.data.objects.new(ident+'_Rig',rd);export.collection.objects.link(rig);review.collection.objects.link(rig)
 bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT');bone=rd.edit_bones.new('Bone');bone.head=(0,0,0);bone.tail=(0,0,1);bpy.ops.object.mode_set(mode='OBJECT');rig.select_set(False)
 for scene in [export,review]:
  scene.render.engine='CYCLES';scene.cycles.samples=32;scene.world=bpy.data.worlds.new(scene.name+'_World');scene.world.use_nodes=True;bg=scene.world.node_tree.nodes.get('Background');bg.inputs[0].default_value=(.7,.8,1,1);bg.inputs[1].default_value=.65
  scene.view_settings.view_transform='AgX' if scene==export else 'Standard';scene.view_settings.exposure=.35 if scene==export else -.1;scene['atlas_release']=RELEASE
 light=bpy.data.lights.new('Review_Key','SUN');light.energy=3.2;light.angle=math.radians(6);light.color=(1,.92,.8);ob=bpy.data.objects.new('Review_Key',light);review.collection.objects.link(ob);ob.rotation_euler=Vector((300,280,-500)).to_track_quat('-Z','Y').to_euler()
 cam=bpy.data.cameras.new('Review_Camera');ob=bpy.data.objects.new('Review_Camera',cam);review.collection.objects.link(ob);cam.type='ORTHO';review.camera=ob;review.render.resolution_x=800;review.render.resolution_y=800;review.render.resolution_percentage=100;review.render.film_transparent=True
def ring(name,profiles,patch,n=12,scale=(1,1)):
 vs=[];uv=[]
 for j,(r,z) in enumerate(profiles):
  for i in range(n+1):
   t=2*math.pi*i/n;vs.append((scale[0]*r*math.cos(t),scale[1]*r*math.sin(t),z));uv.append((i/n,j/(len(profiles)-1)))
 fs=[(j*(n+1)+i,j*(n+1)+i+1,(j+1)*(n+1)+i+1,(j+1)*(n+1)+i) for j in range(len(profiles)-1) for i in range(n)]
 return C.mesh(name,vs,fs,patch,uv,True)
def loaf(name,loc,dim,patch):
 # Broad silhouette rings only: scoring lives exclusively in paint and normal.
 n=10;vs=[];uv=[]
 for z,r in [(0,.74),(.22,1),(.7,.88),(1,.22)]:
  for i in range(n):
   t=2*math.pi*i/n;x=math.cos(t)*r;y=math.sin(t)*r;vs.append((loc[0]+x*dim[0]/2,loc[1]+y*dim[1]/2,loc[2]+z*dim[2]));uv.append((.5+x*.47,.5+y*.47))
 fs=[tuple(reversed(range(n)))]+[(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i) for j in range(3) for i in range(n)]+[tuple(range(3*n,4*n))]
 return C.mesh(name,vs,fs,patch,uv,True)
def basket(kind,offset=(0,0,0),small=1):
 before=len(C.PARTS)
 # Square wicker tray: three straight segments per side, four true square corners.
 outline=[(1,-1),(1,-1/3),(1,1/3),(1,1),(1/3,1),(-1/3,1),(-1,1),(-1,1/3),(-1,-1/3),(-1,-1),(-1/3,-1),(1/3,-1)]
 profiles=[(.03,.2),(4.5,.2),(5.6,2.8),(5.6,3.4),(5.05,3.4),(4.8,2.9),(4.0,.8),(.03,.8)]
 vertices=[(x*r*1.05,y*r*.75,z) for r,z in profiles for x,y in outline+[outline[0]]]
 faces=[(j*13+i,j*13+i+1,(j+1)*13+i+1,(j+1)*13+i) for j in range(7) for i in range(12)]
 wicker=C.mesh('Wicker_Basket',vertices,faces,'bakery_wicker')
 wicker['tray_outline']='square rectangular straight sides, four right-angle corners'
 # Repeat the weave four times around the circumference, preserving chunky interlacing.
 x,y,x1,y1=C.REGIONS['bakery_wicker']
 for poly in wicker.data.polygons:
  sector=poly.index%12
  for loop in poly.loop_indices:
   vertex=wicker.data.vertices[wicker.data.loops[loop].vertex_index];angle=math.atan2(vertex.co.y,vertex.co.x/1.2)%(2*math.pi)
   u=((sector%3)+(1 if (wicker.data.loops[loop].vertex_index%13)==sector+1 else 0))/3
   v=vertex.co.z/3.4
   wicker.data.uv_layers[0].data[loop].uv=((x+(x1-x)*u)/1024,1-(y+(y1-y)*(1-v))/1024)
 # Henno: baked bread is TEXTURE ONLY, not individual loaf geometry.
 patch={'Round':'bakery_round_crust','Oval':'bakery_oval_bread','Long':'bakery_long_crust'}[kind]
 # One continuous broad pile carrier, no per-loaf topology. Paint supplies every bread.
 pile_outline=[(1,-.7),(1,0),(1,.7),(.7,1),(0,1),(-.7,1),(-1,.7),(-1,0),(-1,-.7),(-.7,-1),(0,-1),(.7,-1)]
 points=[]
 for radius,z in [(5.0,2.95),(5.2,4.6),(4.4,6.7),(3.4,7.5)]:
  points.extend([(pile_outline[i][0]*radius*1.05,pile_outline[i][1]*radius*.75,z) for i in range(12)])
 faces=[tuple(range(36,48))]+[(j*12+i,j*12+(i+1)%12,(j+1)*12+(i+1)%12,(j+1)*12+i) for j in range(3) for i in range(12)]
 ob=C.mesh('Painted_'+kind+'_Bread_Fill',points,faces,patch,[(.5+x/12,.5+y/12) for x,y,z in points])
 # Nearly full top panel: preserve all three dominant painted loaves on the crown.
 crown=ob.data.polygons[0];xs=[ob.data.vertices[v].co.x for v in crown.vertices];ys=[ob.data.vertices[v].co.y for v in crown.vertices];x,y,x1,y1=C.REGIONS[patch]
 for loop in crown.loop_indices:
  v=ob.data.vertices[ob.data.loops[loop].vertex_index].co;u=.015+.97*(v.x-min(xs))/(max(xs)-min(xs));t=.015+.97*(v.y-min(ys))/(max(ys)-min(ys));ob.data.uv_layers[0].data[loop].uv=((x+(x1-x)*u)/1024,1-(y+(y1-y)*(1-t))/1024)
 ob['bread_representation']='one generic raised pile carrier; all individual breads painted'
 # Bottom near-vertical band uses a side-on stack panel; upper mound retains top projection.
 bounds=C.REGIONS['bakery_bread_stack_side'];x,y,x1,y1=bounds
 for poly in ob.data.polygons:
  if poly.index in range(1,37):
   i=(poly.index-1)%12;j=(poly.index-1)//12
   for loop,(u,v) in zip(poly.loop_indices,[((i%3)/3,j/3),((i%3+1)/3,j/3),((i%3+1)/3,(j+1)/3),((i%3)/3,(j+1)/3)]):ob.data.uv_layers[0].data[loop].uv=((x+(x1-x)*u)/1024,1-(y+(y1-y)*(1-v))/1024)
 for o in C.PARTS[before:]:
  for v in o.data.vertices:v.co=Vector(offset)+v.co*small
def oven():
 # Preserve original mesh and object/parent transforms in the editable master.
 path=r'C:\Users\Shadow\Desktop\Working Files\3D Art\Props\Bakers\CSC_BAKERS_Oven_v2.blend'
 with bpy.data.libraries.load(path,link=False) as (src,dst):dst.objects=list(src.objects)
 obs=[o for o in dst.objects if o];oldmesh=next(o for o in obs if o.type=='MESH')
 for o in obs:export.collection.objects.link(o);review.collection.objects.link(o)
 oldmesh['export_role']='fixed_geometry';oldmesh['source_asset_id']=C.ID;oldmesh.data.materials.clear();oldmesh.data.materials.append(mat);C.PARTS=[oldmesh]
 bpy.context.view_layer.update();mesh=oldmesh.data;uv=mesh.uv_layers[0];old=[tuple(v.uv) for v in uv.data];seams=[]
 for p in mesh.polygons:
  us=[old[l][0] for l in p.loop_indices];vs=[old[l][1] for l in p.loop_indices];u=sum(us)/len(us);v=sum(vs)/len(vs)
  if .49<u<.64 and .53<v<.75:
   patch='bakery_brick';points=[oldmesh.matrix_world@mesh.vertices[mesh.loops[l].vertex_index].co for l in p.loop_indices]
   ang=[(math.atan2(q.y,q.x)/(2*math.pi))%1 for q in points]
   if max(ang)-min(ang)>.5:ang=[a+1 if a<.5 else a for a in ang]
   # Wrap at rear seam per polygon; vertically common course spacing across faces.
   shift=math.floor(min(ang));coords=[((a-shift)*.98+.01,.04+q.z/88*.92) for a,q in zip(ang,points)]
   coords=[(max(.005,min(.995,a)),max(.005,min(.995,b))) for a,b in coords];seams.append(p.index)
  else:
   if u>.79 and v<.25:patch='bakery_fire';box=(819,812,880,860)
   elif v>.75:patch='bakery_logs';box=(607,0,785,253)
   elif u>.78:patch='masonry';box=(778,256,1024,465)
   elif u>.63:patch='charcoal';box=(648,256,778,465)
   elif u>.205:patch='bakery_light_stone';box=(205,256,368,465)
   else:patch='bakery_dark_stone';box=(0,256,205,465)
   coords=[((old[l][0]*1024-box[0])/(box[2]-box[0]),1-((1-old[l][1])*1024-box[1])/(box[3]-box[1])) for l in p.loop_indices]
  x,y,x1,y1=C.REGIONS[patch]
  for l,(a,b) in zip(p.loop_indices,coords):uv.data[l].uv=((x+(x1-x)*a)/1024,1-(y+(y1-y)*(1-b))/1024)
 (OUT/'oven-remap.json').write_text(json.dumps(dict(original_source=path,editable_vertices=len(mesh.vertices),brick_faces=seams,shape_unchanged=True,mapping='shared world-height courses and cylindrical angle; legacy stone/log/fire regions affine-mapped'),indent=2))
def author(ident):
 if ident.endswith('Peel'):
  C.box('Peel_Handle',(0,7.8,.55),(.85,18,.85),'timber');C.mesh('Peel_Blade',[(-3,-5,0),(3,-5,0),(4,-3,0),(3.2,2,0),(-3.2,2,0),(-4,-3,0),(-3,-5,.4),(3,-5,.4),(4,-3,.4),(3.2,2,.4),(-3.2,2,.4),(-4,-3,.4)],[(0,5,4,3,2,1),(6,7,8,9,10,11)]+[(i,(i+1)%6,(i+1)%6+6,i+6) for i in range(6)],'timber')
 elif ident.endswith('Dough_Set'):
  C.quad('Flour_Dusting',[(-11,-6,.035),(11,-6,.035),(11,6,.035),(-11,6,.035)],'bakery_flour')
  for i,(x,y,d) in enumerate([(0,0,8.4),(6,-2.4,4.2),(6.8,2.6,3.78)]):loaf('Dough'+str(i),(x,y,.1),(d,d*.9,d*.42),'bakery_dough')
  ob=ring('Mixing_Bowl',[(.1,.1),(1.5,.1),(2.5,2.5),(2.45,2.8),(2.1,2.8),(1.6,.7),(.1,.6)],'clay',12);ob.location=(-7,1,0)
 elif 'Bread_Basket_' in ident:basket(ident.rsplit('_',1)[1])
 elif ident.endswith('Bread_Cart'):
  timber='bakery_cart_timber'
  C.box('Cart_Bed',(0,0,9.5),(28,17,1.6),timber)
  for y in [-8.5,8.5]:C.box('Cart_Side',(0,y,12),(28,1.2,4.5),timber)
  for x in [-13.5,13.5]:C.box('Cart_End',(x,0,12),(1.2,17,4.5),timber)
  for y in [-10,10]:
   # Substantial twelve-sided wooden rim; six chunky structural spokes.
   n=12;vs=[];uv=[]
   for radius,dy in [(6.3,-.65),(6.3,.65),(5.2,.65),(5.2,-.65),(6.3,-.65)]:
    for i in range(n+1):
     t=i*2*math.pi/n;vs.append((radius*math.cos(t),y+dy,6.3+radius*math.sin(t)));uv.append((i/n,len(vs)//(n+1)/4))
   fs=[]
   for j in range(4):
    for i in range(n):k=j*(n+1)+i;fs.append((k,k+n+1,k+n+2,k+1))
   rim=C.mesh('Cart_Wheel_Rim',vs,fs,timber,uv)
   x0,y0,x1,y1=C.REGIONS['iron']
   for poly in list(rim.data.polygons)[:12]:
    for loop,(u,v) in zip(poly.loop_indices,[(0,0),(0,1),(1,1),(1,0)]):rim.data.uv_layers[0].data[loop].uv=((x0+(x1-x0)*u)/1024,1-(y0+(y1-y0)*(1-v))/1024)
   for i in range(6):
    t=i*math.pi/3;C.rod('Cart_Wheel_Spoke',(.3*math.cos(t),y,6.3+.3*math.sin(t)),(5.5*math.cos(t),y,6.3+5.5*math.sin(t)),.55,timber,4)
   C.rod('Cart_Wheel_Hub',(0,y-.95,6.3),(0,y+.95,6.3),.95,timber,8)
  C.rod('Axle',(0,-10,6.3),(0,10,6.3),.65,'iron',6)
  for y in [-6.8,6.8]:C.box('Handle',(20,y,9.5),(14,1.3,1.3),timber)
  C.box('Support_Leg',(11,0,4.3),(1.5,1.5,8.6),timber)
  for x in [-12.7,12.7]:
   for y in [-7.8,7.8]:C.box('Canopy_Post',(x,y,20.5),(1.4,1.4,17),timber)
  for y in [-7.8,7.8]:C.box('Canopy_Rail',(0,y,28),(27,1.4,1.4),timber)
  verts=[(x,y,z) for x in [-15.5,15.5] for y,z in [(-10.5,29),(0,32),(10.5,29)]];uv=[(0,0),(.5,0),(1,0),(0,1),(.5,1),(1,1)]
  C.mesh('Striped_Canopy',verts,[(0,3,4,1),(1,4,5,2)],'bakery_canopy',uv)
  C.mesh('Canopy_Underside',[(x,y,z-.25) for x,y,z in verts],[(1,4,3,0),(2,5,4,1)],'bakery_canopy',uv)
  for y in [-10.5,10.5]:C.quad('Canopy_Valance',[(-15.5,y,29),(15.5,y,29),(15.5,y,27),(-15.5,y,27)],'bakery_canopy')
  # Wood grain follows each structural member's longest axis, rather than arbitrary cube winding.
  for ob in C.PARTS:
   if not any(ob.name.startswith(n) for n in ['Cart_Bed','Cart_Side','Cart_End','Handle','Support_Leg','Canopy_Post','Canopy_Rail']):continue
   coords=[v.co for v in ob.data.vertices];lo=[min(v[i] for v in coords) for i in range(3)];hi=[max(v[i] for v in coords) for i in range(3)];axis=max(range(3),key=lambda i:hi[i]-lo[i]);x0,y0,x1,y1=C.REGIONS[timber]
   for poly in ob.data.polygons:
    other=max((i for i in range(3) if i!=axis),key=lambda i:max(ob.data.vertices[v].co[i] for v in poly.vertices)-min(ob.data.vertices[v].co[i] for v in poly.vertices))
    for loop in poly.loop_indices:
     v=ob.data.vertices[ob.data.loops[loop].vertex_index].co;u=(v[other]-lo[other])/max(hi[other]-lo[other],.001);t=(v[axis]-lo[axis])/max(hi[axis]-lo[axis],.001);ob.data.uv_layers[0].data[loop].uv=((x0+(x1-x0)*u)/1024,1-(y0+(y1-y0)*(1-t))/1024)
  basket('Round',(-6.3,0,10.4),1);basket('Long',(6.3,0,10.4),1)
 elif ident.endswith('Oven_v2'):oven()
def finish(ident,index):
 parts=C.PARTS;bpy.context.window.scene=export
 for o in bpy.context.selected_objects:o.select_set(False)
 for o in parts:
  if not o.vertex_groups:o.vertex_groups.new(name='Bone').add(list(range(len(o.data.vertices))),1,'REPLACE');o.modifiers.new('Static rig','ARMATURE').object=rig
  o.select_set(True);o.data.uv_layers.active_index=1
 bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=math.radians(78),island_margin=.035,area_weight=.5,correct_aspect=False);bpy.ops.object.mode_set(mode='OBJECT')
 for o in parts:
  for d in o.data.uv_layers[1].data:d.uv=(.035+d.uv.x*.93,.035+d.uv.y*.93)
 image=bpy.data.images.new('Raw_Self_AO',width=256,height=256,alpha=False);image.generated_color=(1,1,1,1);image.colorspace_settings.name='Non-Color';node=mat.node_tree.nodes.new('ShaderNodeTexImage');node.image=image;mat.node_tree.nodes.active=node
 bpy.ops.object.bake(type='AO',use_clear=False,margin=5);image.filepath_raw=str(OUT/(ident+'-AO.png'));image.file_format='PNG';image.save();mat.node_tree.nodes.remove(node);bpy.data.images.remove(image)
 cell=[512+(index%4)*128,(index//4)*128,640+(index%4)*128,128+(index//4)*128]
 for o in parts:
  for d in o.data.uv_layers[1].data:d.uv=((cell[0]+d.uv.x*128)/2048,1-(cell[1]+(1-d.uv.y)*128)/2048)
  o.data.uv_layers.active_index=0;o.data.uv_layers[0].active_render=True
 # Subsequent atlas publication fills these reserved cells; preload current bake for honest previews.
 import subprocess
 subprocess.run([r'C:\Users\Shadow\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe',str(ROOT/'project/tools/art/pack_bakery_ao.py'),ident,json.dumps(cell)],check=True)
 for im in bpy.data.images:
  if im.source=='FILE':im.reload()
 points=[o.matrix_world@v.co for o in parts for v in o.data.vertices];lo=Vector([min(p[i] for p in points) for i in range(3)]);hi=Vector([max(p[i] for p in points) for i in range(3)]);center=(lo+hi)*.5;size=max(hi-lo)
 cam=review.camera;cam.location=center+Vector((1.2,-1.6,1.1))*size;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=size*1.5
 bpy.context.window.scene=review;path=SOURCE/(ident+'.blend');bpy.ops.wm.save_as_mainfile(filepath=str(path));bpy.ops.file.make_paths_relative();bpy.ops.wm.save_as_mainfile(filepath=str(path))
 # Reopen saved source with automatic repair hooks suspended for the delivery gate.
 before=hashlib.sha256(path.read_bytes()).hexdigest()
 with V.suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
 report=V.validate_current_scene();report['source_sha256']=before;(OUT/(ident+'-validation.json')).write_text(json.dumps(report,indent=2));assert report['automated_pass'],V.format_report(report)
 rev=bpy.data.scenes['Review'];bpy.context.window.scene=rev;rev.render.filepath=str(OUT/(ident+'-preview.png'));bpy.ops.render.render(write_still=True)
 if ident.endswith('Oven_v2'):
  rev.camera.location=center+Vector((-1.2,1.6,1.1))*size;rev.camera.rotation_euler=(center-rev.camera.location).to_track_quat('-Z','Y').to_euler();rev.render.filepath=str(OUT/(ident+'-rear.png'));bpy.ops.render.render(write_still=True)
 exp=bpy.data.scenes['Export'];bpy.context.window.scene=exp
 parts=[o for o in exp.objects if o.type=='MESH'];arm=next(o for o in exp.objects if o.type=='ARMATURE' and o.name==ident+'_Rig')
 for o in bpy.context.selected_objects:o.select_set(False)
 copies=[]
 for o in parts:
  c=bpy.data.objects.new(o.name+'_Prepared',o.data.copy());c.data.transform(o.matrix_world);exp.collection.objects.link(c);c.select_set(True);copies.append(c)
 bpy.context.view_layer.objects.active=copies[0];bpy.ops.object.join();joined=copies[0];joined.name=ident;joined.vertex_groups.new(name='Bone').add(list(range(len(joined.data.vertices))),1,'REPLACE');joined.modifiers.new('Static rig','ARMATURE').object=arm
 cn6=OUT/(ident+'.cn6');geo=OUT/(ident+'.geo');fgx=OUT/(ident+'.fgx');E.csc_do_export_selected(str(cn6),[arm,joined]);summary,vertices,triangles=E.csc_write_geo(str(geo),ident,str(cn6),'LandmarkModel');geo.write_text(geo.read_text().replace('AssetObjects:','AssetObjects..'))
 lib=ROOT/'project/tools/cn6libs'
 for args,label in [([lib/'CN6ToFGX.exe',cn6,fgx,2],'conversion'),([lib/'FGXToCN6.exe',fgx,OUT/(ident+'-roundtrip.cn6')],'roundtrip')]:
  r=subprocess.run([str(a) for a in args],cwd=lib,capture_output=True,text=True,creationflags=subprocess.CREATE_NO_WINDOW);(OUT/(ident+'-'+label+'.log')).write_text(r.stdout+r.stderr);assert r.returncode==0
 import xml.etree.ElementTree as ET
 ast=ET.parse(ROOT/'Civ Supply Chains/Assets/CSC_TAILORS_Tailor_Garment_Rack.ast').getroot();ast.find('m_Name').set('text',ident);ast.find('m_Description').set('text','Bakery prop; shared atlas r025; intact states only.')
 model=ast.find('m_GeometrySet/m_ModelInstances/Element');model.find('m_Name').set('text',ident);model.find('m_GeoName').set('text',ident);states=model.find('m_GroupStates');templates={e.find('m_StateName').get('text'):copy.deepcopy(e) for e in states};states.clear()
 for gm in ET.parse(geo).findall('m_Meshes/Element'):
  for group in gm.findall('m_Groups/Element'):
   for state in ('Worked','Unworked','Pillaged','Construction','Unbuilt'):
    row=copy.deepcopy(templates[state]);states.append(row);row.find('m_MeshName').set('text',gm.find('m_Name').get('text'));row.find('m_GroupName').set('text',group.find('m_Name').get('text'))
 ET.indent(ast,space='  ');ET.ElementTree(ast).write(OUT/(ident+'.ast'),encoding='utf-8',xml_declaration=True)
 (OUT/(ident+'-export.json')).write_text(json.dumps(dict(asset_id=ident,vertices=vertices,triangles=triangles,ao_cell=cell,source=str(path),source_sha256=before),indent=2));print('BAKERY EXPORTED',ident,vertices,triangles,flush=True)
def main():
 for i,ident in enumerate(IDS):
  if len(sys.argv)>sys.argv.index('--')+1 if '--' in sys.argv else False:
   if ident not in sys.argv:continue
  setup(ident);author(ident);finish(ident,i)
if __name__=='__main__':main()

