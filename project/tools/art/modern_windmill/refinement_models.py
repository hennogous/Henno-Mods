"""Propagate the human-edited kit, cut the entrance, and migrate current UV1 users."""
import bpy,bmesh,sys,json,math,shutil
from pathlib import Path
from mathutils import Matrix,Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from modular_v9 import ROOT,ART,BASE,SILO,TROLLEY,PALLET,BMAT,PMAT,sha,dump,texname
WATER='CSC_BAKERS_Water_Mill_Modern'
O=Path.home()/'Desktop/Codex/modern-kit-refinement-20261027'
SOURCES={BASE:ART/'Level 1/modern/revision-03-finished-shelter'/f'{BASE}.blend',WATER:ART/'BAKERS/Water Mill/modern/revision-01'/f'{WATER}.blend',SILO:ART/'BAKERS/Wind Mill/modern/revision-09-modular'/f'{SILO}.blend',TROLLEY:ART/'BAKERS/Props/Modern/revision-01'/f'{TROLLEY}.blend',PALLET:ART/'BAKERS/Props/Modern/revision-01'/f'{PALLET}.blend'}
sys.path[:0]=[str(ROOT/'project/tools/blender'),str(ROOT/'project/tools/blender/scene_export')]
import decode_blend as dec
from csc_scene_validation import suspend_csc_repairs,validate_current_scene
F=Matrix.Rotation(math.radians(42.3),4,'Z')@Matrix.Translation(Vector((-101,-126,0)))
W=Matrix.Translation(Vector((-34,20.5,6.15)))
REMAP={int(k):v for k,v in json.loads((O/'props-remap.json').read_text()).items()}
ALLOC=json.loads((O/'libraries/building/atlas-plan.json').read_text())['AO_allocations']
for d in ('masters','models','bakes'):(O/d).mkdir(exist_ok=True)
MOD=ROOT/'Civ Supply Chains'
if not (O/'baseline.json').exists():dump(O/'baseline.json',{'sources':{str(p):sha(p) for p in SOURCES.values()},'runtime':{str(p.relative_to(MOD)):sha(p) for d in ('Assets','Geometries','Materials','Textures','ArtDefs','XLPs') for p in (MOD/d).iterdir() if p.is_file()},'libraries':{k:{str(p.relative_to(ART/'Textures'/v/'Current')):sha(p) for p in (ART/'Textures'/v/'Current').rglob('*') if p.is_file()} for k,v in [('building','CSC_Buildings_Modern'),('props','CSC_Props_Modern')]}})
def kill(n):
 o=bpy.data.objects.get(n)
 if o:bpy.data.objects.remove(o,do_unlink=True)
def maps_update(scene):
 for mat in {m for o in scene.objects if o.type=='MESH' for m in o.data.materials}:
  kind='building' if mat.name.startswith(BMAT) else 'props'
  for n in mat.node_tree.nodes:
   if n.type!='TEX_IMAGE' or not n.image:continue
   name=Path(n.image.filepath.replace('\\','/')).name
   p=O/'libraries'/kind/'textures'/name
   if p.is_file():
    if n.image.packed_file:n.image.unpack(method='REMOVE')
    n.image.filepath=str(p);n.image.reload()
def bake(scene,ident):
 keep=[o for o in scene.objects if o.type=='MESH'];bpy.ops.object.select_all(action='DESELECT')
 for o in keep:o.hide_set(False);o.hide_render=False;o.select_set(True);o.data.uv_layers.active_index=1
 bpy.context.view_layer.objects.active=keep[0];bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=math.radians(75),island_margin=.012,area_weight=.8,scale_to_bounds=True);bpy.ops.object.mode_set(mode='OBJECT')
 im=bpy.data.images.new(ident+'_AO_Refined',width=1024,height=1024,alpha=False);im.colorspace_settings.name='Non-Color';restore=[]
 for mat in {o.data.materials[0] for o in keep}:
  nodes=mat.node_tree.nodes;bs=next(n for n in nodes if n.type=='BSDF_PRINCIPLED');n=next(n for n in nodes if n.type=='TEX_IMAGE' and (n.label or n.name)=='AO');old=n.image;edges=[(l.from_socket,l.to_socket) for s in ('Base Color','Normal') for l in list(bs.inputs[s].links)]
  for s in ('Base Color','Normal'):
   for l in list(bs.inputs[s].links):mat.node_tree.links.remove(l)
  n.image=im;nodes.active=n;restore.append((mat,n,old,edges))
 scene.render.engine='CYCLES';scene.cycles.samples=32;scene.render.bake.margin=8
 bpy.ops.object.bake(type='AO',uv_layer='UV2');im.filepath_raw=str(O/'bakes'/(ident+'.png'));im.file_format='PNG';im.save()
 for mat,n,old,edges in restore:
  n.image=old
  for a,b in edges:mat.node_tree.links.new(a,b)
 for o in keep:
  key=ident if ident==BASE else ident+('_Building' if o.data.materials[0].name.startswith(BMAT) else '_Machinery');_,(x0,y0,x1,y1)=ALLOC[key]
  for d in o.data.uv_layers[1].data:d.uv=((x0+4+d.uv.x*(x1-x0-8))/2048,1-(y1-4-d.uv.y*(y1-y0-8))/2048)
  o.data.uv_layers.active_index=0;o.select_set(False)
def save(ident,scene,review):
 folder=O/'masters'/ident;(folder/'textures').mkdir(parents=True,exist_ok=True)
 for mat in {m for o in scene.objects if o.type=='MESH' for m in o.data.materials}:
  for n in mat.node_tree.nodes:
   if n.type=='TEX_IMAGE' and n.image:
    p=Path(bpy.path.abspath(n.image.filepath))
    if not p.is_file():continue
    shutil.copy2(p,folder/'textures'/p.name);n.image.filepath='//textures/'+p.name
 bpy.context.window.scene=review;bpy.ops.wm.save_as_mainfile(filepath=str(folder/(ident+'.blend')),relative_remap=False)
 bpy.ops.wm.open_mainfile(filepath=str(folder/(ident+'.blend')),load_ui=False,use_scripts=False)
 report=validate_current_scene();dump(folder/'validation.json',report);assert report['automated_pass'],report
 bpy.context.window.scene=bpy.data.scenes['Export'];bpy.context.view_layer.update();groups={}
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  label=('SiloSideSupports' if o.get('optional_silo_side_support') else 'Shelter' if 'Shelter_' in o.name or 'Support_Foot_' in o.name else 'Building') if ident==BASE else ('Building' if o.data.materials[0].name.startswith(BMAT) else 'Machinery') if ident==WATER else 'Geometry'
  if ident==SILO and o.get('surface_tiles') and any(x in o.name for x in ('Sack_','Visible_Pallet.')):label='Stock'
  groups.setdefault(label,[]).append(dec.decode_mesh(o,o.matrix_world))
 # Preserve existing native group identities for independently exported props.
 if ident not in (BASE,WATER):
  import xml.etree.ElementTree as E
  geo=E.parse(MOD/'Geometries'/(ident+'.geo')).getroot()
  print('PROP_GROUP',ident,[x.attrib for x in geo.iter() if x.tag=='m_Name'],flush=True)
  label='Geometry'
 model={'asset_id':ident,'kind':'building' if ident in (BASE,WATER) else 'prop','meshes':[dec.merge_meshes(ident+'_'+k,v) for k,v in groups.items()]}
 # Canonical source decoder records from earlier delivery establish exact group names.
 if ident not in (BASE,WATER):
  old=ROOT/'Civ Supply Chains/Geometries'/(ident+'.geo')
  import xml.etree.ElementTree as E
  g=E.parse(old).getroot();names=[n.get('text') for n in g.findall('m_Meshes/Element/m_Name')]
  if names and len(names)==len(model['meshes']):
   for m,n in zip(model['meshes'],names):m['name']=n
 dump(O/'models'/(ident+'.json'),model);print('SAVED',ident,sum(len(m['vertices']) for m in model['meshes']),flush=True)
with suspend_csc_repairs():
 for ident,path in SOURCES.items():
  bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False);scene=bpy.data.scenes['Export'];review=bpy.data.scenes['Review'];bpy.context.window.scene=scene;bpy.context.view_layer.update()
  if ident==BASE:
   kill('CSC_Fixed_Door_Recess_Floor');kill('CSC_Fixed_Recess_Back')
   o=bpy.data.objects['CSC_Fixed_House_Foundation'];old=o.data;mat=old.materials[0]
   outline=[(-44,-26),(44,-26),(44,26),(-44,26),(-44,13.34),(-26,13.34),(-26,-13.34),(-44,-13.34)]
   vs=[F@Vector((x,y,z)) for z in (-30,0) for x,y in outline]
   fs=[tuple(reversed(range(8))),tuple(range(8,16))]+[(i,(i+1)%8,(i+1)%8+8,i+8) for i in range(8)]
   # Retain object transform and author the cutout in its local coordinates.
   inv=o.matrix_world.inverted();me=bpy.data.meshes.new('Foundation_open_entrance');me.from_pydata([inv@v for v in vs],[],fs);me.update();me.materials.append(mat);o.data=me
   uv=me.uv_layers.new(name='UV1')
   for p in me.polygons:
    for li in p.loop_indices:
     v=F.inverted()@o.matrix_world@me.vertices[me.loops[li].vertex_index].co
     axis=max(range(3),key=lambda a:abs((F.inverted().to_3x3()@o.matrix_world.to_3x3()@p.normal)[a]));u=(v.x+44)/88 if axis!=0 else (v.y+26)/52;vv=(v.z+30)/64 if axis!=2 else (v.y+26)/52
     uv.data[li].uv=((1+.025+.95*u)/8,1-(.025+.95*(1-vv))/8)
   for n in ('UV2','UV3'):me.uv_layers.new(name=n)
   for d in me.uv_layers[2].data:d.uv=(.02,.02)
   o.vertex_groups.clear();o.vertex_groups.new(name='Bone').add(list(range(len(vs))),1,'REPLACE')
   dump(O/'base-edits.json',{'source':str(path),'source_sha256':sha(path),'removed':['CSC_Fixed_Door_Recess_Floor','CSC_Fixed_Recess_Back'],'foundation':'Entrance notch follows opening down to -30; walls and rest of foundation retained'})
  if ident==WATER:
   rig=next(o for o in scene.objects if o.type=='ARMATURE');old_names={r['name'] for r in json.loads((O/'inspection/base.json').read_text())}
   for o in list(scene.objects):
    if o.type=='MESH' and o.name in old_names:kill(o.name)
   p=O/'masters'/BASE/(BASE+'.blend')
   with bpy.data.libraries.load(str(p),link=False) as (a,b):b.objects=[n for n in a.objects if n.startswith('CSC_Fixed_')]
   for o in b.objects:scene.collection.objects.link(o)
   bpy.context.view_layer.update()
   for o in b.objects:
    old=o.matrix_world.copy();o.parent=rig;o.matrix_world=W@F.inverted()@old;o['source_asset_id']=WATER
    for m in o.modifiers:
     if m.type=='ARMATURE':m.object=rig
    if 'optional_silo_side_support' in o:del o['optional_silo_side_support']
    review.collection.objects.link(o)
    o.data.materials[0]=bpy.data.materials[BMAT]
   kill('CSC_Fixed_Front_Window_-21_17')
  for o in scene.objects:
   if o.type!='MESH':continue
   if o.data.materials[0].name.startswith(PMAT):
    for p in o.data.polygons:
     ds=[o.data.uv_layers[0].data[i] for i in p.loop_indices];cx=sum(d.uv.x for d in ds)/len(ds);cy=sum(1-d.uv.y for d in ds)/len(ds);slot=min(7,int(cy*8))*8+min(7,int(cx*8));assert slot in REMAP,(o.name,slot)
     ns=REMAP[slot]
     for d in ds:d.uv.x+=(ns%8-slot%8)/8;d.uv.y-=(ns//8-slot//8)/8
  maps_update(scene)
  if ident in (BASE,WATER):bake(scene,ident)
  save(ident,scene,review)
