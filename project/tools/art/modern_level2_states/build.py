"""Build a main-only modern L2 state shell; reuse the validated L1 bake/export helpers."""
import bpy,bmesh,json,sys,hashlib,types,math
from pathlib import Path
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[4]
A=Path.home()/'Desktop/Working Files/3D Art';O=Path.home()/'Desktop/Codex/modern-l2-states-20261029'
BASE='CSC_Level_2_Modern';ID=BASE+'_CON+PIL';SRC=A/'Level 2/modern/revision-06-ae'/(BASE+'.blend')
T=Matrix(json.loads((Path.home()/'Desktop/Codex/modern-bakery-ae-20261028/registration.json').read_text())['matrix'])
# Load definitions only: do not run the old L1 production recipe.
helper=ROOT/'project/tools/art/modern_states/build.py';source=helper.read_text().split('\nwith suspend_csc_repairs():')[0]
source=source.replace('(0,256,128,65)','(640,256,128,128)').replace('cx=(tile%','cx=512+(tile%').replace('/35)','/70)')
b=types.ModuleType('state_helpers');b.__file__=str(helper);exec(compile(source,str(helper),'exec'),b.__dict__)
b.F=T;b.OUT=O;b.BASE=BASE;b.AO={BASE:('building',[1024,512,1536,1024])}
b.new_mesh.__defaults__=(T,'building',None);b.box.__defaults__=(8,None,T,'building',None)
O.mkdir(parents=True,exist_ok=True);(O/'textures').mkdir(exist_ok=True)
from shutil import copy2
copy2(A/'Textures/CSC_Buildings_Modern/Current/textures/CSC_Atlas_Modern_AO.png',O/'textures/CSC_Atlas_Modern_AO.png')

def clean_normals(o,solid=False):
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0002)
 bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=.0001)
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
 if solid:
  assert all(e.is_contiguous for e in bm.edges),o.name
  assert bm.calc_volume(signed=True)>0,o.name
 bm.to_mesh(o.data);bm.free();o.data.update()

def masonry_sampling(o,brick):
 # Tile within the assigned atlas cell at the worked model's measured sampling:
 # 124 px / 32 units horizontally; upper storey uses 124 / 30.0444 vertically.
 # Cuts are UV boundaries only; the visible silhouette does not change.
 dz=30.04442596435547 if brick else 32;origins=(-40,-29,32 if brick else 0);steps=(32,32,dz)
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.transform(bm,matrix=T.inverted(),verts=list(bm.verts))
 for axis in range(3):
  lo=min(v.co[axis] for v in bm.verts);hi=max(v.co[axis] for v in bm.verts);step=steps[axis];origin=origins[axis]
  for k in range(math.floor((lo-origin)/step)+1,math.ceil((hi-origin)/step)):
   co=Vector((0,0,0));co[axis]=origin+k*step;normal=Vector((0,0,0));normal[axis]=1
   bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=co,plane_no=normal,dist=.0001,clear_inner=False,clear_outer=False)
 uv=bm.loops.layers.uv['UV1'];cellx=512 if brick else 640
 for p in bm.faces:
  axis=max(range(3),key=lambda i:abs(p.normal[i]));axes=[i for i in range(3) if i!=axis];center=p.calc_center_median();base=[origins[i]+math.floor((center[i]-origins[i])/steps[i])*steps[i] for i in axes]
  for l in p.loops:
   a,c=[max(0,min(1,(l.vert.co[i]-base[j])/steps[i])) for j,i in enumerate(axes)]
   l[uv].uv=((cellx+2+124*a)/1024,1-(126-124*c)/1024)
 bmesh.ops.transform(bm,matrix=T,verts=list(bm.verts));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_contiguous for e in bm.edges);assert bm.calc_volume(signed=True)>0
 bm.to_mesh(o.data);bm.free();o.data.update();o['masonry_sampling']='Matches worked: U 3.875 px/unit; V '+str(124/dz)

with b.suspend_csc_repairs():
 bpy.ops.wm.open_mainfile(filepath=str(SRC),load_ui=False,use_scripts=False)
 b.scene=bpy.data.scenes['Export'];b.review=bpy.data.scenes['Review'];bpy.context.window.scene=b.scene;bpy.context.view_layer.update()
 b.rig=next(o for o in b.scene.objects if o.type=='ARMATURE');b.rig.matrix_world=Matrix.Identity(4);b.objects=[]
 b.material=bpy.data.objects['CSC_Fixed_Ground_East'].data.materials[0]
 b.material['civ_material']='CSC_BAKERS_Modern';b.material_setup(b.material,'building')
 keep=[o for o in b.scene.objects if o.type=='MESH' and (o.name.startswith('CSC_Fixed_Foundation_') or o.name.startswith('CSC_Fixed_Ground_'))]
 for o in list(bpy.data.objects):
  if o.type!='MESH':continue
  if o not in keep:bpy.data.objects.remove(o,do_unlink=True);continue
  b.freeze(o);b.objects.append(o)
  for u in o.data.uv_layers[2].data:u.uv=(.02,.02)
 # Join adjoining lower walls before thickening. The actual door/window holes
 # and underground footing from the worked source stay in exactly the same place.
 # Worked sheets have T junctions at the inset-window cuts. Rebuild their planar
 # topology on the identical bounds/openings rather than thickening invalid edges.
 for o in list(b.objects):bpy.data.objects.remove(o,do_unlink=True)
 b.objects=[]
 for name,axis,fixed,span,holes in [('East',0,40,29,[(-20,0,0,30),(10,23,10,28)]),('West',0,-40,29,[]),('Front',1,-29,40,[]),('Rear',1,29,40,[(6,22,10,28)])]:
  us=sorted(set([-span,span]+[x for h in holes for x in h[:2]]));zs=sorted(set([-30,0,32]+[z for h in holes for z in h[2:]]));vs=[];fs=[]
  for u in us:
   for z in zs:vs.append((fixed,u,z) if axis==0 else (u,fixed,z))
  for i in range(len(us)-1):
   for j in range(len(zs)-1):
    uc=(us[i]+us[i+1])/2;zc=(zs[j]+zs[j+1])/2
    if any(a<uc<c and d<zc<e for a,c,d,e in holes):continue
    k=i*len(zs)+j;l=(i+1)*len(zs)+j;fs.append((k,l,l+1,k+1))
  shell=b.new_mesh('State_Current_Lower_'+name,vs,fs,1,b.material)
  for p in shell.data.polygons:
   local=T.inverted()@p.center;n=T.to_3x3().inverted()@p.normal
   if n.x*local.x+n.y*local.y<0:p.flip()
  shell.data.update();bpy.ops.object.select_all(action='DESELECT');shell.select_set(True);bpy.context.view_layer.objects.active=shell
  mod=shell.modifiers.new('Closed inward wall thickness','SOLIDIFY');mod.thickness=2.4;mod.offset=-1;mod.use_even_offset=True
  bpy.ops.object.modifier_apply(modifier=mod.name);clean_normals(shell,True)
 # An open ring replaces the original full cornice slab: no horizontal floor
 # blocks the entrance or fills the open ruined interior.
 for o in list(b.objects):
  if 'Cornice' in o.name:b.objects.remove(o);bpy.data.objects.remove(o,do_unlink=True)
 for y in (-29,29):b.box('State_Cornice_'+str(y),(0,y,32.5),(82,3,3),4)
 for x in (-40,40):b.box('State_Cornice_End_'+str(x),(x,0,32.5),(3,55,3),4)
 # Broken / unfinished upper walls keep the current modern building footprint.
 b.strip('State_Brick_Front',[(-40,-28,61),(-31,-28,61),(-23,-28,48),(-12,-28,39),(3,-28,40),(16,-28,51),(28,-28,57),(40,-28,62)],2,bottom=34)
 b.strip('State_Brick_Rear',[(-40,28,62),(-21,28,60),(-9,28,48),(6,28,42),(21,28,43),(30,28,57),(40,28,62)],2,bottom=34)
 b.strip('State_Brick_West',[(-39,-27,62),(-39,-14,65),(-39,-5,76),(-39,2,80),(-39,12,66),(-39,27,62)],2,bottom=34)
 b.strip('State_Brick_Entrance',[(39,-27,62),(39,-17,57),(39,-7,42),(39,5,40),(39,17,54),(39,27,62)],2,bottom=34)
 # Chunky structural members, with longitudinal raw-wood UVs in L2 cell 9.
 for y in (-28,28):b.beam('State_Eave_'+str(y),(-40,y,62),(40,y,62),3)
 for x in (-38,0,38):
  b.beam('State_Rafter_A_'+str(x),(x,-28,63),(x,0,104.2),3.2)
  b.beam('State_Rafter_B_'+str(x),(x,0,104.2),(x,28,63),3.2)
  b.beam('State_Tie_'+str(x),(x,-28,62),(x,28,62),3.2)
  if x!=0:b.beam('State_Kingpost_'+str(x),(x,0,62),(x,0,103),3)
 b.beam('State_Ridge',(-41,0,104.2),(41,0,104.2),3.5)
 for x in (-38,38):
  for y in (-28,28):b.beam('State_Corner_Post_'+str(x)+'_'+str(y),(x,y,34),(x,y,62),3)
 # Retain native scaffold surface/UVs. Place its two independent sections along
 # main-building walls only, with uniform scaling and no extension scaffold.
 with bpy.data.libraries.load(str(A/'Level 2/CSC_Level_2_CON+PIL.blend'),link=False) as (a,c):c.objects=['Scaffolding']
 original=c.objects[0];b.scene.collection.objects.link(original);bpy.context.view_layer.update();b.freeze(original)
 for side in (-1,1):
  o=original.copy();o.data=original.data.copy();b.scene.collection.objects.link(o);b.review.collection.objects.link(o)
  bm=bmesh.new();bm.from_mesh(o.data);faces=[p for p in bm.faces if (T.inverted()@p.calc_center_median()).y*side<0]
  bmesh.ops.delete(bm,geom=faces,context='FACES');bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS');bm.to_mesh(o.data);bm.free()
  points=[T.inverted()@v.co for v in o.data.vertices];lo=Vector([min(p[i] for p in points) for i in range(3)]);hi=Vector([max(p[i] for p in points) for i in range(3)])
  center=(lo+hi)/2;scale=.84
  # Keep nearest rail at least 4 units outside the wall, bottom buried 4 units.
  yc=side*(33+(hi.y-lo.y)*scale/2)
  for v,p in zip(o.data.vertices,points):v.co=T@Vector(((p.x-center.x)*scale,yc+(p.y-center.y)*scale,(p.z-lo.z)*scale-4))
  o.name='State_Scaffold_'+str(side);o['state_scaffold']=True;o['civ_visible_states']=json.dumps(['Construction']);o.data.materials[0]['civ_material']='Pillage_Construction_01'
  while len(o.data.uv_layers)<3:o.data.uv_layers.new(name='UV'+str(len(o.data.uv_layers)+1))
  for i,u in enumerate(o.data.uv_layers):u.name='UV'+str(i+1)
  b.objects.append(o)
 bpy.data.objects.remove(original,do_unlink=True)
 for o in b.objects:
  if not o.get('state_scaffold'):clean_normals(o,True)
  if o.name.startswith('State_Current_Lower_') or o.name.startswith('State_Brick_'):masonry_sampling(o,o.name.startswith('State_Brick_'))
 b.bake(BASE);b.save_decode(BASE)
 # Native binding must use the canonical material even when Blender suffixes it.
 model_path=O/'models'/(ID+'.json');model=json.loads(model_path.read_text())
 for m in model['meshes']:
  for mat in m['materials']:mat['external']='Pillage_Construction_01' if 'Scaffold' in m['name'] else 'CSC_BAKERS_Modern'
 model_path.write_text(json.dumps(model,indent=2))
 b.dump(O/'authoring.json',{'sources':{BASE:{'path':str(SRC),'sha256':hashlib.sha256(SRC.read_bytes()).hexdigest()}},'AO':b.AO,'frame':[list(r) for r in T],'extension_included':False,'floor_included':False,'worked_source_untouched':True})
 bpy.ops.wm.open_mainfile(filepath=str(O/'masters'/ID/(ID+'.blend')),load_ui=False,use_scripts=False)
 validation=b.validate_current_scene();b.dump(O/'masters'/ID/'validation.json',validation);assert validation['automated_pass'],validation
 print('L2_STATE_SAVED_AND_RELOADED',flush=True)
