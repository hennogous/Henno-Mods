"""Concept C candidate: original L3 silhouette, painted room skins and separate props."""
import bpy,bmesh,json,math,sys
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[4];A=Path.home()/'Desktop/Working Files/3D Art';O=Path.home()/'Desktop/Codex/modern-cafe-v1-20261029';T=O/'textures'
sys.path.insert(0,str(ROOT/'project/tools/blender'))
from csc_scene_validation import suspend_csc_repairs
bpy.ops.wm.read_factory_settings(use_empty=True);review=bpy.context.scene;review.name='Review';export=bpy.data.scenes.new('Export')
for sc in (review,export):
 sc['asset_id']='CSC_Level_3_Modern';sc.render.engine='CYCLES';sc.cycles.samples=48;sc.render.threads_mode='FIXED';sc.render.threads=6;sc.view_settings.view_transform='Standard' if sc==review else 'AgX';sc.view_settings.exposure=-.1 if sc==review else .35
w=bpy.data.worlds.new('Review World');w.use_nodes=True;w.node_tree.nodes['Background'].inputs[0].default_value=(.7,.8,1,1);w.node_tree.nodes['Background'].inputs[1].default_value=.65;review.world=export.world=w
sun=bpy.data.objects.new('Review_Key',bpy.data.lights.new('Review_Key','SUN'));review.collection.objects.link(sun);sun.data.energy=3.2;sun.data.color=(1,.92,.8);sun.data.angle=math.radians(6);sun.rotation_euler=(Vector((0,0,0))-Vector((-300,-280,500))).to_track_quat('-Z','Y').to_euler()
arm=bpy.data.armatures.new('CSC_Cafe_Rig');rig=bpy.data.objects.new('CSC_Cafe_Rig',arm);review.collection.objects.link(rig);export.collection.objects.link(rig);bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT');bone=arm.edit_bones.new('Bone');bone.tail=(0,0,5);bpy.ops.object.mode_set(mode='OBJECT');rig.select_set(False)
def material(name,prefix,interior=False):
 m=bpy.data.materials.new(name);m.use_nodes=True;ns=m.node_tree.nodes;ls=m.node_tree.links;bs=ns.get('Principled BSDF');bs.inputs['Roughness'].default_value=.67;maps={}
 for ch in ('B','N','E') if interior else ('B','N','G','M','AO','E','O'):
  fn=prefix+('_B_BAKERS' if ch=='B' and prefix!='CSC_Props_Modern_01' else '_E_BAKERS' if ch=='E' and prefix!='CSC_Props_Modern_01' else '_'+ch)+'.png';path=T/fn
  if not path.exists():continue
  im=bpy.data.images.load(str(path),check_existing=True);im.colorspace_settings.name='sRGB' if ch in ('B','E') else 'Non-Color';node=ns.new('ShaderNodeTexImage');node.name=node.label=ch;node.image=im;uv=ns.new('ShaderNodeUVMap');uv.uv_map='UV2' if ch=='AO' else 'UV3' if ch=='E' else 'UV1';ls.new(uv.outputs[0],node.inputs['Vector']);maps[ch]=node
 if 'AO' in maps:
  mix=ns.new('ShaderNodeMixRGB');mix.name='AO_Multiply';mix.blend_type='MULTIPLY';mix.inputs[0].default_value=.5;ls.new(maps['B'].outputs[0],mix.inputs[1]);ls.new(maps['AO'].outputs[0],mix.inputs[2]);ls.new(mix.outputs[0],bs.inputs['Base Color'])
 else:ls.new(maps['B'].outputs[0],bs.inputs['Base Color'])
 norm=ns.new('ShaderNodeNormalMap');norm.uv_map='UV1';ls.new(maps['N'].outputs[0],norm.inputs['Color']);ls.new(norm.outputs[0],bs.inputs['Normal'])
 if 'E' in maps:ls.new(maps['E'].outputs[0],bs.inputs['Emission Color']);bs.inputs['Emission Strength'].default_value=0
 if 'G' in maps:
  inv=ns.new('ShaderNodeMath');inv.operation='SUBTRACT';inv.inputs[0].default_value=1;ls.new(maps['G'].outputs[0],inv.inputs[1]);ls.new(inv.outputs[0],bs.inputs['Roughness'])
 if 'M' in maps:ls.new(maps['M'].outputs[0],bs.inputs['Metallic'])
 if 'O' in maps:ls.new(maps['O'].outputs[0],bs.inputs['Alpha']);m.surface_render_method='DITHERED'
 return m
bm=material('CSC_BAKERS_Modern','CSC_Atlas_Modern');pm=material('CSC_Props_Modern_01','CSC_Props_Modern_01');im=material('CSC_BAKERS_Interiors_Modern','CSC_Interiors_Modern',True)
R=Matrix.Rotation(math.radians(-28.26),4,'Z');meshes=[];GROUP='Building';mat=bm
def bind(ob,group):
 ob['module']=group;ob['export_role']='building_geometry' if group=='Building' else 'fixed_geometry';ob['source_asset_id']='CSC_Level_3_Modern' if group=='Building' else 'CSC_BAKERS_Cafe_'+group+'_Modern'
 ob.vertex_groups.clear();vg=ob.vertex_groups.new(name='Bone');vg.add(list(range(len(ob.data.vertices))),1,'REPLACE');ob.modifiers.clear();mod=ob.modifiers.new('Static binding','ARMATURE');mod.object=rig
 for sc in (review,export):
  if ob.name not in sc.objects:sc.collection.objects.link(ob)
 meshes.append(ob)
with bpy.data.libraries.load(str(A/'Level 3/CSC_Level_3.blend'),link=False) as (src,dst):dst.objects=['CSC_Level_3_Bldg']
body=dst.objects[0];body.name='CSC_Fixed_L3_Historical_Silhouette';body.parent=None;body.matrix_world=Matrix.Identity(4)
b=bmesh.new();b.from_mesh(body.data);bmesh.ops.delete(b,geom=[f for f in b.faces if f.material_index==1],context='FACES');b.to_mesh(body.data);b.free();body.data.materials.clear();body.data.materials.append(bm)
while len(body.data.uv_layers)>3:body.data.uv_layers.remove(body.data.uv_layers[-1])
while len(body.data.uv_layers)<3:body.data.uv_layers.new()
for i,n in enumerate(('UV1','UV2','UV3')):body.data.uv_layers[i].name=n
for i,d in enumerate(body.data.uv_layers[2].data):d.uv=body.data.uv_layers[0].data[i].uv
bind(body,'Building')
def uvmap(slot,u,v):
 if mat==im:return ((slot%4*256+6+u*244)/1024,1-(slot//4*256+6+(1-v)*244)/1024)
 slot=44 if slot==1 else slot
 return ((slot%8*128+3+u*122)/1024,1-(slot//8*128+3+(1-v)*122)/1024)
def mesh(name,verts,faces,slots=0,uvs=None):
 m=bpy.data.meshes.new(name);m.from_pydata(verts,[],faces);m.update();ob=bpy.data.objects.new('CSC_Fixed_'+name,m);m.materials.append(mat)
 for n in ('UV1','UV2','UV3'):m.uv_layers.new(name=n)
 for p in m.polygons:
  slot=slots if isinstance(slots,int) else slots[p.index];axis=max(range(3),key=lambda a:abs(p.normal[a]));aa,bb=((1,2),(0,2),(0,1))[axis];co=[(m.vertices[i].co[aa],m.vertices[i].co[bb]) for i in p.vertices];lo=[min(c[i] for c in co) for i in (0,1)];hi=[max(c[i] for c in co) for i in (0,1)]
  for j,k in enumerate(p.loop_indices):
   u,v=uvs[p.index][j] if uvs else [(co[j][a]-lo[a])/max(hi[a]-lo[a],.001) for a in (0,1)];m.uv_layers[0].data[k].uv=uvmap(slot,u,v);m.uv_layers[1].data[k].uv=(.99,.99);m.uv_layers[2].data[k].uv=m.uv_layers[0].data[k].uv if mat==im else (.02,.02)
 bind(ob,GROUP);return ob
def box(name,lo,hi,slot):
 x,y,z=lo;X,Y,Z=hi;return mesh(name,[(x,y,z),(X,y,z),(X,Y,z),(x,Y,z),(x,y,Z),(X,y,Z),(X,Y,Z),(x,Y,Z)],[(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)],slot)
def panel(name,vs,slot):return mesh(name,vs,[(0,1,2,3)],slot,[[(0,0),(1,0),(1,1),(0,1)]])
def cyl(name,c,r,depth,slot,axis='Z',segments=12):
 vs=[]
 for q in (-depth/2,depth/2):
  for j in range(segments):
   a=j*math.tau/segments;v=(r*math.cos(a),r*math.sin(a),q)
   if axis=='Y':v=(v[0],q,v[1])
   vs.append(tuple(c[k]+v[k] for k in range(3)))
 faces=[tuple(range(segments-1,-1,-1)),tuple(range(segments,segments*2))]+[(i,(i+1)%segments,(i+1)%segments+segments,i+segments) for i in range(segments)];return mesh(name,vs,faces,slot)
# Four inset room skins: rear/side/floor paintings, no furnishings geometry.
mat=im
for i,(x0,x1) in enumerate(((49.8,67.4),(69.0,86.4),(88.5,105.7),(109.5,128.5))):
 y0=112.4;y1=118.0;z0=7.5;z1=35
 vs=[(x0,y0,z0),(x1,y0,z0),(x1,y0,z1),(x0,y0,z1),(x0,y1,z0),(x1,y1,z0),(x1,y1,z1),(x0,y1,z1)];faces=[(4,5,6,7),(0,4,7,3),(5,1,2,6),(0,1,5,4),(3,7,6,2)]
 ob=mesh('Cafe_Interior_Skin_'+str(i),[R@Vector(v) for v in vs],faces,[4 if i%2==0 else 5,5,5,6,5],[[(0,0),(1,0),(1,1),(0,1)]]*5)
 b=bmesh.new();b.from_mesh(ob.data);target=R@Vector(((x0+x1)/2,(y0+y1)/2,(z0+z1)/2))
 for f in b.faces:
  if f.normal.dot(target-f.calc_center_median())<0:f.normal_flip()
 b.to_mesh(ob.data);b.free();ob['painted_interior']=True;ob['furnishing_geometry']=False
# Counter is positioned under the preserved right shelter, in the old counter envelope.
mat=pm;GROUP='Counter'
box('Cafe_Counter_Base',(-11,-7,-2),(11,7,11),3);box('Cafe_Counter_Worktop',(-11.8,-7.5,11),(11.8,7.5,12.5),18)
box('Espresso_Machine',(-10,-4,12.5),(1,3,23.5),1);panel('Espresso_Painted_Face',[(-10,-4.02,12.5),(1,-4.02,12.5),(1,-4.02,23.5),(-10,-4.02,23.5)],40)
box('Pastry_Cabinet',(2,-5,12.5),(11,4,25),1);panel('Pastry_Painted_Face',[(2,-5.02,12.5),(11,-5.02,12.5),(11,-5.02,25),(2,-5.02,25)],41)
# Short striped valance under the shelter's front lip; structural roof retained.
GROUP='Valance';mesh('Cafe_Striped_Valance',[(-22,0,0),(22,0,0),(22,0,3),(-22,0,3),(-22,.6,0),(22,.6,0),(22,.6,3),(-22,.6,3)],[(0,1,2,3),(4,7,6,5),(0,4,5,1),(3,2,6,7),(1,5,6,2),(0,3,7,4)],28)
GROUP='Parasol';cyl('Parasol_Pole',(0,0,16),.65,32,18,segments=8)
vs=[(0,0,35)]+[(13*math.cos(j*math.tau/12),13*math.sin(j*math.tau/12),29) for j in range(12)]+[(13*math.cos(j*math.tau/12),13*math.sin(j*math.tau/12),28.2) for j in range(12)]
fs=[];slots=[]
for j in range(12):fs.append((0,1+j,1+(j+1)%12));slots.append(1 if j%2==0 else 3);fs.append((1+j,13+j,13+(j+1)%12,1+(j+1)%12));slots.append(1 if j%2==0 else 3)
fs.append(tuple(range(24,12,-1)));slots.append(3);mesh('Garden_Parasol_Canopy',vs,fs,slots)
# A small coffee-serving van; broad simple body shapes with painted machinery.
GROUP='Van'
box('Van_Chassis',(-22,-9,4),(22,9,8),10);box('Van_Green_Lower',(-21,-10,7),(22,10,14),1)
box('Van_Cream_Service_Body',(-7,-10,14),(22,10,28),3);box('Van_Cream_Roof',(-8,-10.7,27),(22.7,10.7,29),3)
mesh('Van_Cab',[(-23,-10,9),(-7,-10,9),(-7,10,9),(-23,10,9),(-21,-10,18),(-15,-10,26),(-7,-10,27),(-7,10,27),(-15,10,26),(-21,10,18)],[(0,1,2,3),(0,4,5,6,1),(3,2,7,8,9),(4,9,8,5),(5,8,7,6),(1,6,7,2),(0,3,9,4)],3)
panel('Van_Cab_Side',[(-20.5,-10.04,10),(-7.1,-10.04,10),(-7.1,-10.04,25.8),(-14.7,-10.04,25)],33)
panel('Van_Windscreen',[(-21.04,-8,18.3),(-21.04,8,18.3),(-15.2,8,25.8),(-15.2,-8,25.8)],45)
panel('Van_Grille_Lights',[(-23.06,9,8),(-23.06,-9,8),(-21.06,-9,18),(-21.06,9,18)],32)
panel('Van_Coffee_Hatch',[(-5.8,-10.04,14.5),(20.8,-10.04,14.5),(20.8,-10.04,26),(-5.8,-10.04,26)],40)
panel('Van_Pastry_Menu',[(13,-10.08,14.6),(21,-10.08,14.6),(21,-10.08,25.8),(13,-10.08,25.8)],41)
box('Van_Service_Shelf',(-6,-14,13.5),(22,-9.5,15),18)
panel('Van_Cup_Emblem',[(-3,-10.07,7.2),(6,-10.07,7.2),(6,-10.07,13.3),(-3,-10.07,13.3)],43)
mesh('Van_Striped_Awning',[(-7,-16,26),(23,-16,26),(23,-10,29),(-7,-10,29),(-7,-16,24.5),(23,-16,24.5),(23,-10,27.5),(-7,-10,27.5)],[(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(3,2,6,7),(0,3,7,4)],28)
for x in (-14,15):
 for y in (-10,10):cyl('Van_Wheel',(x,y,5),5,3,35,axis='Y')
box('Van_Front_Bumper',(-24,-10,6),(-22,10,8),2)
for ob in meshes:
 if ob.name in ('CSC_Fixed_Van_Cream_Service_Body','CSC_Fixed_Van_Cream_Roof'):
  bpy.context.view_layer.objects.active=ob;bevel=ob.modifiers.new('Broad body corner chamfers','BEVEL');bevel.width=1.2;bevel.segments=2;bpy.ops.object.modifier_apply(modifier=bevel.name)
  ob.vertex_groups['Bone'].add(list(range(len(ob.data.vertices))),1,'REPLACE')
# AO bake each independent model in local coordinates. Never bake painted normals.
alloc={'Building':([0,1024,512,1536],bm),'Counter':([0,768,256,1024],pm),'Van':([256,768,512,1024],pm),'Parasol':([896,512,1024,640],pm),'Valance':([896,640,1024,768],pm)}
for group,(rect,ma) in alloc.items():
 sel=[o for o in meshes if o.get('module')==group and not o.get('painted_interior')];bpy.ops.object.select_all(action='DESELECT')
 for ob in meshes:ob.hide_render=ob not in sel
 for ob in sel:ob.select_set(True);ob.data.uv_layers.active_index=1;ob.data.uv_layers[1].active_render=True
 bpy.context.view_layer.objects.active=sel[0];bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=math.radians(70),island_margin=.02,area_weight=.8,scale_to_bounds=True);bpy.ops.object.mode_set(mode='OBJECT')
 ns=ma.node_tree.nodes;ls=ma.node_tree.links;bs=ns.get('Principled BSDF');node=ns['AO'];old=node.image;ao=bpy.data.images.new(group+'_AO',width=512,height=512,alpha=False);ao.colorspace_settings.name='Non-Color';node.image=ao;ns.active=node;restore=[(l.from_socket,l.to_socket) for sl in ('Base Color','Normal') for l in bs.inputs[sl].links]
 for sl in ('Base Color','Normal'):
  for l in list(bs.inputs[sl].links):ls.remove(l)
 review.render.bake.margin=8;bpy.ops.object.bake(type='AO',uv_layer='UV2');ao.filepath_raw=str(O/'bakes'/f'{group}.png');ao.file_format='PNG';ao.save();node.image=old
 for a,b in restore:ls.new(a,b)
 x0,y0,x1,y1=rect
 for ob in sel:
  for d in ob.data.uv_layers[1].data:d.uv=((x0+4+d.uv.x*(x1-x0-8))/2048,1-(y1-4-d.uv.y*(y1-y0-8))/2048)
  ob.data.uv_layers.active_index=0;ob.data.uv_layers[0].active_render=True;ob.select_set(False)
 print('BAKED',group,flush=True)
for ob in meshes:ob.hide_render=False
review['proposal_only']=True;review['concept']='C - Garden Cafe';review['interior_policy']='Painted B/N/E room skins; no modeled furnishings';review['source_L3_silhouette_preserved']=True
cam=bpy.data.objects.new('Review_Camera',bpy.data.cameras.new('Review_Camera'));review.collection.objects.link(cam);review.camera=cam;target=R@Vector((100,119,48));cam.location=target+R.to_3x3()@Vector((125,-230,170));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=210
review.render.resolution_x=review.render.resolution_y=1200;review.render.resolution_percentage=100;review.render.film_transparent=True
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(O/'Local_Models.blend'))
(O/'AO_allocations.json').write_text(json.dumps({k:v[0] for k,v in alloc.items()},indent=2));print('CAFE_MODELS_READY',flush=True)
