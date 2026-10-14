"""Patch only cargo animation; preserve current donkey/crane keys and user sources."""
import bpy,json,sys,shutil,hashlib
from pathlib import Path
from mathutils import Matrix,Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from delivery_cargo_motion import TIP_BONE,reset_pose,tip_pose,SACK_SCALE
BASE=Path(r'C:\Users\Shadow\Desktop\Codex\CSC_Storage_L');DEL=BASE/'delivery-01';OUT=BASE/'delivery-reset-20261010'
OUT.mkdir(exist_ok=True);backup=OUT/'before-cargo-motion'
if not backup.exists():
 backup.mkdir()
 for name in ('CSC_TAILORS_Storage_Delivery.blend','CSC_TAILORS_Delivery_Native_Export.blend','CSC_TEST_TAILORS_Delivery_Master_Model.fgx','CSC_TEST_TAILORS_Delivery_Master_Model.geo','CSC_TEST_TAILORS_Delivery_Master.fgx','CSC_TEST_TAILORS_Delivery_Master.anm','native-check.json','authoring-check.json'):
  shutil.copy2(DEL/name,backup/name)
bpy.ops.wm.open_mainfile(filepath=str(backup/'CSC_TAILORS_Storage_Delivery.blend'))
s=bpy.data.scenes['Export'];review=bpy.data.scenes['Review'];bpy.context.window.scene=s
rig=bpy.data.objects['CSC_Storage_Crane_Rig'];old={}
for f in range(1,2042):
 s.frame_set(f);old[f]={b.name:(rig.matrix_world@b.matrix).copy() for b in rig.pose.bones}
stored=old[1261]['Cargo'];below=reset_pose(stored,47)
old_below=old[1411]['Cargo']
source=Path(r'C:\Users\Shadow\Desktop\Working Files\3D Art\Props\Bakers\Bakers_Flour_FINAL\CSC_ALL_Flour_Sack_Closed.blend')
oldimages=set(bpy.data.images)
with bpy.data.libraries.load(str(source),link=False) as (a,b):b.scenes=['Export' if 'Export' in a.scenes else a.scenes[0]]
temp=b.scenes[0];sack=next(o for o in temp.objects if o.type=='MESH')
points=[sack.matrix_world@v.co for v in sack.data.vertices]
preview=sack.copy();preview.data=sack.data.copy();preview.data.transform(sack.matrix_world);preview.parent=None;preview.matrix_world=Matrix.Identity(4)
for mod in list(preview.modifiers):preview.modifiers.remove(mod)
preview.vertex_groups.clear();preview.name='REVIEW_Closed_Sack_TipUpright';review.collection.objects.link(preview)
preview['review_only']=True;preview['csc_export_exclude']=True
for im in set(bpy.data.images)-oldimages:
 if im.source=='FILE':
  candidate=source.parent/'textures'/Path(im.filepath).name
  assert candidate.is_file(),candidate
  im.filepath=str(candidate);im.reload()
bpy.data.scenes.remove(temp)
bpy.context.window.scene=s;bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig
bpy.ops.object.mode_set(mode='EDIT');bone=rig.data.edit_bones.new(TIP_BONE);bone.head=(0,0,0);bone.tail=(0,2,0);bone.parent=rig.data.edit_bones['Root'];bpy.ops.object.mode_set(mode='OBJECT')
rig.pose.bones[TIP_BONE].rotation_mode='QUATERNION';inv=rig.matrix_world.inverted();max_unchanged=0
for f in range(1,2042):
 s.frame_set(f);t=(f-1)/30;cargo=old[f]['Cargo'].copy()
 if 42<t<=47:cargo=reset_pose(stored,t)
 elif 47<t<56:
  # Keep the existing home destination, orientation and underground timing.
  from delivery_cargo_motion import smooth
  cargo.translation+=(below.translation-old_below.translation)*(1-smooth((t-47)/9))
 for name,pose in [('Cargo',cargo),(TIP_BONE,tip_pose(cargo,t,points))]:
  pb=rig.pose.bones[name];pb.matrix=inv@pose
  for prop in ('location','rotation_quaternion','scale'):pb.keyframe_insert(prop,frame=f)
 bpy.context.view_layer.update()
 for name,previous in old[f].items():
  if name=='Cargo':continue
  current=rig.matrix_world@rig.pose.bones[name].matrix
  max_unchanged=max(max_unchanged,max(abs(current[i][j]-previous[i][j]) for i in range(4) for j in range(4)))
from delivery_pose_adjustments import linearize_baked_keys
linearize_baked_keys(rig)
preview.parent=rig;preview.parent_type='BONE';preview.parent_bone=TIP_BONE;preview.matrix_parent_inverse=Matrix.Identity(4)
preview.matrix_basis=Matrix.Translation((0,-2,0))@Matrix.Scale(SACK_SCALE,4);preview.hide_render=True
rig['cargo_rotation_bone']=TIP_BONE;rig['cargo_rotation_asset']='CSC_BAKERS_Flour_Closed';rig['cargo_rotation_attachment_scale']=SACK_SCALE
text=bpy.data.texts.new('Cargo attachment options')
text.write('Cargo: unchanged upright delivery, e.g. textile bale at scale 0.8.\nCargo_TipUpright: closed flour sack at scale 1.0, attachment position/rotation zero. Sideways on sled; upright over first 3s of lift.\nDifferent prop shapes/scales may need placement tuning. Optional REVIEW_Closed_Sack_TipUpright is hidden by default.\nBoth cargo paths slide directly to the right-hand corner before dropping below grade.\n')
bpy.context.window.scene=review;review.frame_set(1261);preview.hide_set(True)
bpy.ops.wm.save_as_mainfile(filepath=str(DEL/'CSC_TAILORS_Storage_Delivery.blend'))
assert max_unchanged<.0001,max_unchanged
report={'unchanged_crane_and_donkey_path_max_error':max_unchanged,'tip_bone':TIP_BONE,'sack_asset':'CSC_BAKERS_Flour_Closed','sack_scale':SACK_SCALE,
 'sack_source':str(source),'sack_points':[list(p) for p in points],'reset_target':list(below.translation),'authored_sha256':hashlib.sha256((DEL/'CSC_TAILORS_Storage_Delivery.blend').read_bytes()).hexdigest()}
(OUT/'cargo-motion-check.json').write_text(json.dumps(report,indent=2));print('CARGO_MOTION_UPDATED',max_unchanged)
