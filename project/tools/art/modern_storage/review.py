"""Assembled review proposals with shared flour props; no runtime assembly writes."""
import bpy,bmesh,sys,json,math
from pathlib import Path
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[4];A=Path.home()/'Desktop/Working Files/3D Art';O=Path.home()/'Desktop/Codex/modern-storage-v1-20261029'
sys.path.insert(0,str(ROOT/'project/tools/blender'));from csc_scene_validation import suspend_csc_repairs
masters=json.loads((O/'masters.json').read_text());lookup={r['group']:r for r in masters}
def append(path,group,position,angle=0,scale=1):
 with bpy.data.libraries.load(str(path),link=False) as (src,dst):dst.objects=src.objects
 obs=[o for o in dst.objects if o and o.type=='MESH' and o.get('export_role') in ('fixed_geometry','building_geometry')];pts=[]
 sourcepts=[ob.matrix_world@v.co for ob in obs for v in ob.data.vertices]
 shift=Vector((0,0,0))
 if group in ('Stock','LoftStock','TruckStock'):
  shift=Vector(((min(v.x for v in sourcepts)+max(v.x for v in sourcepts))/2,(min(v.y for v in sourcepts)+max(v.y for v in sourcepts))/2,min(v.z for v in sourcepts)))
 for ob in obs:
  original=ob.matrix_world.copy();ob.parent=None;ob.modifiers.clear();ob.matrix_world=Matrix.Translation(position)@Matrix.Rotation(angle,4,'Z')@Matrix.Scale(scale,4)@Matrix.Translation(-shift)@original;ob['module']=group;ob['review_only']=True
  review.collection.objects.link(ob);pts.extend(ob.matrix_world@v.co for v in ob.data.vertices)
 for ob in dst.objects:
  if ob and ob not in obs and not ob.users_scene:bpy.data.objects.remove(ob)
 print('PLACED',group,[[round(min(v[i] for v in pts),2),round(max(v[i] for v in pts),2)] for i in range(3)],flush=True)
 return obs
for size in ('M','L'):
 path=Path(lookup[size]['blend'])
 with suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
 review=bpy.data.scenes['Review'];bpy.context.window.scene=review
 # Review file does not masquerade as an export master.
 review['proposal_only']=True;review['placement_authority']='Review proposal; AE remains authority after installation'
 props=A/'BAKERS/Props/Modern/revision-02'
 append(props/'CSC_BAKERS_Flour_Pallet_Modern.blend','Stock',(-60,9,1.4),scale=.8)
 append(props/'CSC_BAKERS_Flour_Pallet_Modern.blend','Stock',(-58,-21,1.4),scale=.8)
 append(props/'CSC_BAKERS_Flour_Trolley_Modern.blend','Stock',(-40,28,1.4),angle=math.pi/2,scale=.8)
 append(Path(lookup['Drum']['blend']),'Drum',(-69,30,1.4))
 if size=='L':append(Path(lookup['Hoist']['blend']),'Hoist',(-42,-16,64))
 # A modest painted-backed loft stock silhouette is reused cargo, not new mesh detail.
 if size=='L':append(props/'CSC_BAKERS_Flour_Pallet_Modern.blend','LoftStock',(-30,0,38),scale=.68)
 for im in bpy.data.images:
  if im.source=='FILE' and im.filepath:
   fn=im.filepath.replace('\\','/').split('/')[-1]
   if (path.parent/'textures'/fn).exists():im.filepath=str(path.parent/'textures'/fn);im.reload()
 review.render.resolution_x=review.render.resolution_y=1200;review.cycles.samples=40;review.use_nodes=False;review.render.image_settings.file_format='PNG';review.render.image_settings.color_mode='RGBA';review.render.image_settings.color_depth='8';review.render.image_settings.media_type='IMAGE'
 target=Vector((-22,-3,36));review.camera.location=target+Vector((-150,-220,155));review.camera.rotation_euler=(target-review.camera.location).to_track_quat('-Z','Y').to_euler();review.camera.data.ortho_scale=181
 uncut={}
 def clip():
  for ob in review.objects:
   if ob.type=='MESH' and ob.get('module')==size:
    uncut[ob.name]=ob.data;ob.data=ob.data.copy();b=bmesh.new();b.from_mesh(ob.data);bmesh.ops.bisect_plane(b,geom=list(b.verts)+list(b.edges)+list(b.faces),plane_co=(0,0,0),plane_no=(0,0,1),clear_inner=True);b.to_mesh(ob.data);b.free()
 def save(name):
  bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(path.parent/name))
 def render(name):
  clip();review.render.filepath=str(O/'review'/name);bpy.ops.render.render(write_still=True)
  for name,me in uncut.items():bpy.data.objects[name].data=me
  uncut.clear()
 save(f'CSC_BAKERS_Storage_{size}_Modern_Review.blend');render(size+'_Standard.png')
 if size=='M':append(Path(lookup['PalletJack']['blend']),'PalletJack',(-40,-26,1.4),angle=-math.pi/2)
 else:
  append(Path(lookup['Truck']['blend']),'Truck',(-61,-57,0))
  append(props/'CSC_BAKERS_Flour_Pallet_Modern.blend','TruckStock',(-53,-57,8),scale=.55)
 for im in bpy.data.images:
  if im.source=='FILE' and im.filepath:
   fn=im.filepath.replace('\\','/').split('/')[-1]
   if (path.parent/'textures'/fn).exists():im.filepath=str(path.parent/'textures'/fn);im.reload()
 save(f'CSC_BAKERS_Storage_{size}_Modern_2_Review.blend');render(size+'_Dispatch.png')
 # Reverse view verifies roof closures, rear walls and foundation coverage.
 review.camera.location=target+Vector((150,210,150));review.camera.rotation_euler=(target-review.camera.location).to_track_quat('-Z','Y').to_euler();render(size+'_Rear.png')
print('REVIEWS_READY',flush=True)
