"""Create a positioned crane-only Blender source, preserving the existing action."""
import bpy, json, sys, math, hashlib
from pathlib import Path
from mathutils import Matrix, Vector

ROOT=Path(r'C:\Users\Shadow\Desktop\Working Files\3D Art\Storage\Storage_L')
BUILDING=ROOT/'CSC_Storage_L.blend'
DONOR=Path(r'C:\Users\Shadow\Desktop\Codex\CSC_Storage_L\revision-01-crane-animation\CSC_Storage_L_Crane_Animation.blend')
UV_SOURCE=ROOT/'CSC_Storage_L_before_rig_20261008-114851.blend'
OUT=Path(r'C:\Users\Shadow\Desktop\Codex\CSC_Storage_L\positioned-crane-20261008')
OUT.mkdir(parents=True,exist_ok=True)
for name in ('load_post','depsgraph_update_post'):
 for cb in list(getattr(bpy.app.handlers,name)):
  if cb.__module__.rsplit('.',1)[-1]=='csc_scene_tools':getattr(bpy.app.handlers,name).remove(cb)

def inspect(path):
 bpy.ops.wm.open_mainfile(filepath=str(path))
 return {'scenes':[{ 'name':s.name,'units':s.unit_settings.scale_length,'system':s.unit_settings.system} for s in bpy.data.scenes],
 'objects':[{'name':o.name,'type':o.type,'parent':o.parent.name if o.parent else None,
 'location':list(o.location),'rotation':list(o.rotation_euler),'scale':list(o.scale),'dimensions':list(o.dimensions),
 'matrix':[list(r) for r in o.matrix_world],
 'vertices':len(o.data.vertices) if o.type=='MESH' else 0,
 'materials':[m.name for m in o.data.materials] if o.type=='MESH' else [],
 'props':dict(o.items())} for o in bpy.data.objects]}

if '--inspect' in sys.argv:
 for label,path in [('building',BUILDING),('donor',DONOR)]:
  (OUT/(label+'-inventory.json')).write_text(json.dumps(inspect(path),indent=2,default=str))
 print('CRANE_SOURCES_INSPECTED')

if '--alignment' in sys.argv:
 from mathutils.kdtree import KDTree
 bpy.ops.wm.open_mainfile(filepath=str(BUILDING))
 obj=next(o for o in bpy.data.objects if o.type=='MESH')
 points=[obj.matrix_world@v.co for v in obj.data.vertices]
 tree=KDTree(len(points))
 for i,p in enumerate(points):tree.insert(p,i)
 tree.balance()
 bpy.ops.wm.open_mainfile(filepath=str(DONOR))
 points=[o.matrix_world@v.co for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('CSC_Fixed_') and 'Crane' not in o.name for v in o.data.vertices]
 result={}
 for factor in (1,100):
  mat=Matrix.Translation((.3160286*factor,1.658027*factor,0))@Matrix.Rotation(math.radians(20.4866),4,'Z')@Matrix.Scale(.9,4)
  errs=sorted(tree.find(mat@p)[2] for p in points)
  result[str(factor)]={'max':max(errs),'median':errs[len(errs)//2],'mean':sum(errs)/len(errs),'within_001':sum(e<.001 for e in errs),'count':len(errs)}
 (OUT/'alignment-check.json').write_text(json.dumps(result,indent=2))
 print(json.dumps(result))

if '--fit' in sys.argv:
 import numpy as np
 def get_components(path):
  bpy.ops.wm.open_mainfile(filepath=str(path))
  mesh=next(o for o in bpy.data.objects if o.type=='MESH')
  attr=mesh.data.attributes.get('csc_source_component')
  print('MESH',mesh.name,'ATTRIBUTES',list(mesh.data.attributes.keys()),'BOUNDS',[(min((mesh.matrix_world@v.co)[i] for v in mesh.data.vertices),max((mesh.matrix_world@v.co)[i] for v in mesh.data.vertices)) for i in range(3)])
  groups={}
  if attr:
   for v,a in zip(mesh.data.vertices,attr.data):groups.setdefault(a.value,[]).append(list(mesh.matrix_world@v.co))
  return groups
 old=get_components(Path(r'C:\Users\Shadow\Desktop\Codex\CSC_Storage_L\source-rig-20261008\CSC_Storage_L_Rigged.blend'))
 new=get_components(BUILDING)
 a=[];b=[]
 for key in old:
  if key in new and len(new[key])==len(old[key]):a.extend(old[key]);b.extend(new[key])
 if a:
  a=np.array(a);b=np.array(b)
  affine,residual,rank,_=np.linalg.lstsq(np.c_[a,np.ones(len(a))],b,rcond=None)
  errors=np.linalg.norm(np.c_[a,np.ones(len(a))]@affine-b,axis=1)
  rng=np.random.default_rng(20261008);best=(0,None,None)
  for _ in range(120):
   ix=rng.choice(len(a),4,replace=False);aa=np.c_[a[ix],np.ones(4)]
   if np.linalg.matrix_rank(aa)<4:continue
   candidate=np.linalg.solve(aa,b[ix]);error=np.linalg.norm(np.c_[a,np.ones(len(a))]@candidate-b,axis=1)
   count=int(sum(error<.001))
   if count>best[0]:best=(count,candidate,error)
  if best[0]>len(a)*.6:
   good=best[2]<.001
   affine=np.linalg.lstsq(np.c_[a[good],np.ones(sum(good))],b[good],rcond=None)[0]
   errors=np.linalg.norm(np.c_[a[good],np.ones(sum(good))]@affine-b[good],axis=1)
   print('EXACTLY_MATCHED',sum(good),'OF',len(a))
  result={'affine':affine.tolist(),'max_error':float(max(errors)),'matched_vertices':len(a),'scale':[float(np.linalg.norm(row)) for row in affine[:3]],'angle_z':math.degrees(math.atan2(affine[0,1],affine[0,0]))}
  (OUT/'fitted-placement.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))

if '--prepare' in sys.argv:
 target=ROOT/'CSC_Storage_L_Crane.blend'
 assert not target.exists(),'Do not overwrite an existing crane working source'
 building_hash=hashlib.sha256(BUILDING.read_bytes()).hexdigest()
 bpy.ops.wm.open_mainfile(filepath=str(DONOR))
 bpy.context.window.scene=bpy.data.scenes['Export'];scene=bpy.context.scene
 rig=bpy.data.objects['CSC_Storage_Crane_Rig']
 crane=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('CSC_Fixed_Crane_')]
 bale=bpy.data.objects['CSC_ALL_Textile_Bale'];controller=bale.parent
 keep=set(crane+[rig,bale,controller]+[o for o in bpy.data.objects if o.type in ('CAMERA','LIGHT')])
 for o in list(bpy.data.objects):
  if o not in keep:bpy.data.objects.remove(o,do_unlink=True)
 for im in bpy.data.images:
  if im.source=='FILE':im.filepath=bpy.path.abspath(im.filepath)
 # Carry over the user's latest pre-separation crane UV edits, preserving the rig.
 source_names=[o.name for o in crane if o.name!='CSC_Fixed_Crane_Load_Sling']
 with bpy.data.libraries.load(str(UV_SOURCE),link=False) as (src,dst):dst.objects=list(source_names)
 uv_count=0
 for reference,name in zip(dst.objects,source_names):
  obj=bpy.data.objects[name]
  assert len(reference.data.vertices)==len(obj.data.vertices)
  assert [tuple(p.vertices) for p in reference.data.polygons]==[tuple(p.vertices) for p in obj.data.polygons]
  error=max(((reference.matrix_basis@a.co)-(obj.matrix_world@b.co)).length for a,b in zip(reference.data.vertices,obj.data.vertices))
  assert error<1e-5,(name,error)
  for uv in reference.data.uv_layers:
   layer=obj.data.uv_layers.get(uv.name) or obj.data.uv_layers.new(name=uv.name)
   for a,b in zip(uv.data,layer.data):b.uv=a.uv
  uv_count+=1;bpy.data.objects.remove(reference,do_unlink=True)
 # Use the actual current building material, not the earlier trial's material copy.
 with bpy.data.libraries.load(str(BUILDING),link=False) as (src,dst):dst.materials=['CSC_TAILORS_NE']
 material=dst.materials[0];assert material
 old=bpy.data.materials.get('CSC_TAILORS_NE')
 for o in crane:
  o.data.materials.clear();o.data.materials.append(material)
 if old!=material:
  bpy.data.materials.remove(old);material.name='CSC_TAILORS_NE'
 for node in material.node_tree.nodes:
  if node.type=='TEX_IMAGE' and node.image and node.image.source=='FILE':
   p=node.image.filepath
   if p.startswith('//'):node.image.filepath=str((ROOT/p[2:]).resolve())
 # Capture all-frame authoring positions before applying a single assembly transform.
 action=rig.animation_data.action;rig.animation_data.action_slot=action.slots[0]
 rig.data.pose_position='POSE'
 def points():
  deps=bpy.context.evaluated_depsgraph_get();result=[]
  for o in crane+[bale]:
   e=o.evaluated_get(deps);mesh=e.to_mesh()
   result.extend(e.matrix_world@v.co for v in mesh.vertices);e.to_mesh_clear()
  return result
 expected={}
 for frame in range(1,362):scene.frame_set(frame);expected[frame]=points()
 scene.frame_set(1)
 placement=bpy.data.objects.new('Crane_Placement',None)
 placement.empty_display_type='PLAIN_AXES';placement.empty_display_size=10
 for sc in bpy.data.scenes:sc.collection.objects.link(placement)
 for o in crane+[rig]:
  if not o.parent:
   world=o.matrix_world.copy();o.parent=placement;o.matrix_parent_inverse=Matrix.Identity(4);o.matrix_world=world
 # Blender displays metres, with 0.01 metre per model unit in this scene.
 unit=scene.unit_settings.scale_length
 placement.location=(.3160286/unit,1.658027/unit,0)
 placement.rotation_euler.z=math.radians(20.4866);placement.scale=(.9,)*3
 placement['placement_metres']=[.3160286,1.658027,0]
 placement['rotation_degrees_z']=20.4866
 placement['export_role']='placement_control'
 placement['note']='User-specified district placement. Transform export copies together; do not strip this parent for animation export.'
 bpy.context.view_layer.update();transform=placement.matrix_world.copy()
 max_error=0
 for frame in range(1,362):
  scene.frame_set(frame)
  max_error=max(max_error,max((transform@a-b).length for a,b in zip(expected[frame],points())))
 assert max_error<.0001,max_error
 scene.frame_set(1)
 # Reframe the original animation camera around the moved assembly.
 review=bpy.data.scenes['Review'];camera=bpy.data.objects['Animation_Review_Camera']
 camera.matrix_world=transform@camera.matrix_world;camera.scale=(1,1,1);camera.data.ortho_scale*=.9
 review.camera=camera;review.frame_set(1)
 for sc in bpy.data.scenes:sc.frame_start=1;sc.frame_end=361;sc.render.fps=30
 # Repoint source texture paths to the shared working texture folder where available.
 texture_root=ROOT.parents[1]/'Textures'
 for im in bpy.data.images:
  if im.source=='FILE':
   path=Path(bpy.path.abspath(im.filepath));shared=texture_root/path.name
   if shared.is_file():path=shared
   assert path.is_file(),str(path)
   im.filepath=bpy.path.relpath(str(path),start=str(ROOT))
 text=bpy.data.texts.get('START HERE - Crane') or bpy.data.texts.new('START HERE - Crane')
 text.write('CRANE-ONLY WORKING SOURCE\nSelect Crane_Placement to move the complete animated assembly.\n'
  'Scale 0.9; X 0.3160286 m; Y 1.658027 m; Z 0 m; Z rotation 20.4866 degrees.\n'
  'Frames 1-361, 30 FPS. Existing crane action and attached textile bale retained.\n'
  'Crane uses the current building material CSC_TAILORS_NE and all three UV maps.\n'
  'Bale retains its prop-library material. Building source is not included or modified.\n'
  'This is an authoring source. The current native animation exporter requires an\n'
  'identity/unparented export rig: bake the placement consistently into an export copy\n'
  'or apply it once as the AE attachment transform. Do not double-apply the placement.\n'
  'The older one-UV AE crane and missing bale still require integration work.\n')
 bpy.context.window.scene=scene;bpy.ops.object.select_all(action='DESELECT')
 placement.select_set(True);bpy.context.view_layer.objects.active=placement
 # Open at a useful crane/bale framing instead of the original whole-building view.
 from mathutils import Quaternion
 allpts=points();lo=Vector(tuple(min(p[i] for p in allpts) for i in range(3)));hi=Vector(tuple(max(p[i] for p in allpts) for i in range(3)))
 for screen in bpy.data.screens:
  for area in screen.areas:
   if area.type=='VIEW_3D':
    area.spaces.active.region_3d.view_location=(lo+hi)/2
    area.spaces.active.region_3d.view_distance=(hi-lo).length*1.6
 bpy.ops.wm.save_as_mainfile(filepath=str(target),relative_remap=False)
 bpy.ops.wm.open_mainfile(filepath=str(target))
 assert bpy.data.objects['Crane_Placement'].scale.x==bpy.data.objects['Crane_Placement'].scale.y
 assert not any(o.type=='MESH' and o.name.startswith('CSC_Fixed_') and 'Crane' not in o.name for o in bpy.data.objects)
 assert hashlib.sha256(BUILDING.read_bytes()).hexdigest()==building_hash
 report={'file':str(target),'building_unchanged':True,'building_sha256':building_hash,
  'placement_metres':[.3160286,1.658027,0],'scale':.9,'rotation_z_degrees':20.4866,
  'source_crane_uvs_updated':uv_count,'crane_material':'CSC_TAILORS_NE','frames_checked':361,
  'max_motion_transform_error':max_error,'bale_in_blender':True,'ae_bale_verified':False}
 (OUT/'working-source-check.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
 # Render from saved file, with the existing bale visible as a Blender authoring aid.
 bpy.context.window.scene=bpy.data.scenes['Review'];s=bpy.context.scene
 s.render.resolution_x=900;s.render.resolution_y=900;s.render.resolution_percentage=100
 # Tight framing uses a fresh camera aimed at the actual crane/bale bounds.
 centre=(lo+hi)/2;s.camera.location=centre+Vector((-130,-170,100))
 s.camera.rotation_euler=(centre-s.camera.location).to_track_quat('-Z','Y').to_euler()
 s.camera.data.ortho_scale=max((hi-lo).length*1.1,55)
 s.render.filepath=str(OUT/'crane-working-preview.png');s.render.image_settings.file_format='PNG'
 bpy.ops.render.render(write_still=True)
