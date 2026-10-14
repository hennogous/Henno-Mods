"""Bake isolated native export copies and validate the converted delivery models."""
import bpy,json,subprocess,sys
from pathlib import Path
from mathutils import Matrix,Vector
from civ6_animation import core,backend
import io_export_cn6 as cn6
OUT=Path(r'C:\Users\Shadow\Desktop\Codex\CSC_Storage_L\delivery-01')
NEXUS=r'C:\Program Files (x86)\CivNexus6_Release-1.3.3\CivNexus6'
SAMPLES=[1,113,151,163,301,601,721,811,841,901,991,1081,1201,1261,1279,1300,1321,1366,1411,1561,1617,1629,1701,1741,1891,2041]
ATTACH_BONES=('Cargo','Cargo_TipUpright','DonkeyPath')
ATTACH_SAMPLES=set(SAMPLES)|set(range(841,932))|set(range(1261,1412))
C=Matrix(((0,1,0,0),(0,0,1,0),(1,0,0,0),(0,0,0,1)))
for event in ('load_post','depsgraph_update_post'):
 for cb in list(getattr(bpy.app.handlers,event)):
  if cb.__module__.rsplit('.',1)[-1]=='csc_scene_tools':getattr(bpy.app.handlers,event).remove(cb)
bpy.ops.wm.open_mainfile(filepath=str(OUT/'CSC_TAILORS_Storage_Delivery.blend'))
source=bpy.data.scenes['Export'];bpy.context.window.scene=source
master=bpy.data.objects['CSC_Storage_Crane_Rig'];donkey=bpy.data.objects['CSC_Delivery_Donkey_Rig']
body_scale=float(donkey['delivery_body_scale'])
crane=[o for o in source.objects if o.type=='MESH' and 'Crane' in o.name]
dm=bpy.data.objects['CSC_Delivery_Donkey_Mesh']
def vertices(o):
 e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();v=[e.matrix_world@p.co for p in m.vertices];e.to_mesh_clear();return v
expected={};body_expected={};attachments={};poses={}
for f in ([811] if '--bind-only' in sys.argv else range(1,2042)):
 source.frame_set(f);bpy.context.view_layer.update()
 poses[f]={b.name:master.matrix_world@b.matrix@(Matrix.Identity(4) if b.name in ATTACH_BONES else Matrix.Scale(1/master.matrix_world.to_scale().x,4)) for b in master.pose.bones}
 poses[f].update({'Donkey_'+b.name:donkey.matrix_world@b.matrix@Matrix.Scale(1/body_scale,4) for b in donkey.pose.bones})
 if f in SAMPLES:
  expected[f]=[p for o in crane for p in vertices(o)]
  body_expected[f]=vertices(dm)
 if f in ATTACH_SAMPLES:attachments[f]={n:poses[f][n].copy() for n in ATTACH_BONES if n in poses[f]}
source.frame_set(31);bpy.context.view_layer.update();P=master.matrix_world.copy()
B=Matrix.LocRotScale(donkey.matrix_world.translation,donkey.matrix_world.to_quaternion(),Vector((body_scale,)*3))
body_mesh_transform=B@donkey.matrix_world.inverted()@dm.matrix_world
scene=bpy.data.scenes.new('Native_Master');scene.render.fps=30;scene.frame_start=1;scene.frame_end=2041
rig=bpy.data.objects.new('CSC_ALL_Delivery_Rig',master.data.copy());scene.collection.objects.link(rig)
rig.data.transform(P);rig.data.pose_position='POSE';bpy.context.window.scene=scene
rig.select_set(True);bpy.context.view_layer.objects.active=rig;bpy.ops.object.mode_set(mode='EDIT')
for n in (n for n in ATTACH_BONES if n in rig.data.edit_bones):
 b=rig.data.edit_bones[n];head=b.head.copy();length=b.length;b.matrix=Matrix.Translation(head)@C;b.length=length
for original in sorted(donkey.data.bones,key=lambda b:len(b.parent_recursive)):
 b=rig.data.edit_bones.new('Donkey_'+original.name)
 b.head=B@original.head_local;b.tail=B@original.tail_local
 m=B@original.matrix_local;b.matrix=Matrix.LocRotScale(m.translation,m.to_quaternion(),Vector((1,1,1)));b.length=original.length*body_scale
 b.parent=rig.data.edit_bones['Donkey_'+original.parent.name] if original.parent else rig.data.edit_bones['DonkeyPath']
bpy.ops.object.mode_set(mode='OBJECT')
rig.animation_data_create();rig.animation_data.action=bpy.data.actions.new('Delivery_Master_Native')
ordered=sorted(rig.pose.bones,key=lambda b:len(b.parent_recursive))
for b in ordered:b.rotation_mode='QUATERNION'
for f,original in poses.items():
 targets={n:m@C if n in ATTACH_BONES else m for n,m in original.items()}
 for b in ordered:
  rest=b.bone.matrix_local
  local=b.parent.bone.matrix_local.inverted()@rest if b.parent else rest
  desired=targets[b.parent.name].inverted()@targets[b.name] if b.parent else targets[b.name]
  b.matrix_basis=local.inverted()@desired
  for prop in ('location','rotation_quaternion','scale'):b.keyframe_insert(prop,frame=f)
sys.path.insert(0,str(Path(__file__).resolve().parent))
from delivery_pose_adjustments import linearize_baked_keys
linearize_baked_keys(rig)
meshes=[]
for o in crane:
 c=o.copy();c.data=o.data.copy();c.animation_data_clear();c.parent=None;c.data.transform(o.matrix_world);c.matrix_world=Matrix.Identity(4)
 c.name=o.name+'_Delivery';scene.collection.objects.link(c)
 for m in list(c.modifiers):c.modifiers.remove(m)
 if 'Mount_Hardware' in c.name:
  c.vertex_groups.clear();c.vertex_groups.new(name='Root').add(list(range(len(c.data.vertices))),1,'REPLACE')
 c.modifiers.new('Delivery rig','ARMATURE').object=rig;c.parent=rig;meshes.append(c)
mesh=dm.copy();mesh.data=dm.data.copy();mesh.parent=None;mesh.matrix_parent_inverse=Matrix.Identity(4);mesh.matrix_world=Matrix.Identity(4)
mesh.data.transform(body_mesh_transform);scene.collection.objects.link(mesh);mesh.name='CSC_ALL_Delivery_Donkey'
for group in mesh.vertex_groups:group.name='Donkey_'+group.name
for m in list(mesh.modifiers):mesh.modifiers.remove(m)
mesh.modifiers.new('Shared delivery rig','ARMATURE').object=rig;mesh.parent=rig;meshes.append(mesh)
scene.frame_set(811);actual=vertices(mesh)
pre_error=max(min((a-b).length for b in actual) for a in body_expected[811])
(OUT/'combined-bind-check.json').write_text(json.dumps({'error':pre_error,'B':[list(r) for r in B],'mesh_transform':[list(r) for r in body_mesh_transform],'source_parent_inverse':[list(r) for r in dm.matrix_parent_inverse]},indent=2))
assert pre_error<.01,('Combined Blender bind mismatch',pre_error)
if '--bind-only' in sys.argv:print('COMBINED_BIND_PASS',pre_error);sys.exit(0)

def export_pair(label,scene,rig,meshes):
 bpy.context.window.scene=scene;scene.frame_set(1);bpy.ops.object.select_all(action='DESELECT')
 rig.select_set(True);bpy.context.view_layer.objects.active=rig
 model='CSC_TEST_TAILORS_Delivery_'+label+'_Model';clip='CSC_TEST_TAILORS_Delivery_'+label
 for o in meshes:
  while len(o.data.uv_layers)<3:
   layer=o.data.uv_layers.new(name='UV'+str(len(o.data.uv_layers)+1))
   for a,b in zip(o.data.uv_layers[0].data,layer.data):b.uv=a.uv
 cn6.csc_do_export_selected(str(OUT/(model+'.cn6')),[rig]+meshes)
 exe=OUT/'bridge/CN6ToFGX.exe'
 r=subprocess.run([str(exe),str(OUT/(model+'.cn6')),str(OUT/(model+'.fgx')),'2','--skinned'],cwd=exe.parent,capture_output=True,text=True)
 (OUT/(label+'-geometry.log')).write_text(r.stdout+r.stderr);assert r.returncode==0,r.stdout+r.stderr
 cn6.csc_write_geo(str(OUT/(model+'.geo')),model,str(OUT/(model+'.cn6')),'LandmarkModel')
 p=OUT/(model+'.geo');p.write_text(p.read_text().replace('AssetObjects:','AssetObjects..'))
 if '--geometry-only' in sys.argv:
  # Geometry repairs keep the already-approved native clip byte-for-byte.
  report=json.loads((OUT/'native-check.json').read_text())['master_clip']
  assert (OUT/(clip+'.fgx')).is_file() and (OUT/(clip+'.anm')).is_file()
 else:
  report=core.export_animation(OUT/(clip+'.fgx'),rig,NEXUS,1,2041,include_model=False,overwrite=True)
 backend.run(NEXUS,'extract',OUT/(model+'.fgx'),OUT/(clip+'.fgx'),OUT/(label+'-sampled'),30,0,0)
 return model,clip,report

bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'CSC_TAILORS_Delivery_Native_Pending.blend'))
model,clip,report=export_pair('Master',scene,rig,meshes)
sample=core.parse_na2(OUT/'Master-sampled/clip.na2')[0]
attachment_error={}
for f,points in attachments.items():
 attachment_error[f]={n:max(abs(m[i][j]-core.world_matrix(sample['tracks'][n][f-1])[i][j]) for i in range(4) for j in range(4)) for n,m in points.items()}
assert max(v for p in attachment_error.values() for v in p.values())<.08,attachment_error
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'CSC_TAILORS_Delivery_Native_Export.blend'))
check=bpy.data.scenes.new('Native_Check');bpy.context.window.scene=check
converted,_=core.import_native(OUT/(clip+'.anm'),OUT/(model+'.fgx'),NEXUS)
errors={};body_errors={}
for f,pts in expected.items():
 check.frame_set(f);actual=[p for o in check.objects if o.type=='MESH' and 'Donkey' not in o.name for p in vertices(o)]
 errors[f]=max(min((a-b).length for b in actual) for a in pts)
 actual_body=[p for o in check.objects if o.type=='MESH' and 'Donkey' in o.name for p in vertices(o)]
 body_errors[f]=max(min((a-b).length for b in actual_body) for a in body_expected[f])
assert max(errors.values())<.2,errors
result={'master_clip':report,'combined_donkey':True,'master_vertex_errors':errors,'donkey_vertex_errors':body_errors,'attachment_matrix_errors':attachment_error,'ae_verified':False,
 'body_scale':body_scale,'donkey_error_at_previous_scale':max(body_errors.values())*.65/body_scale}
# Preserve the previous .4-unit tolerance at .65 donor size, proportional to body size.
# Native FBX conversion is lossy; report both absolute and normalized errors.
assert result['donkey_error_at_previous_scale']<.4,body_errors
(OUT/'native-check.json').write_text(json.dumps(result,indent=2));print('DELIVERY_NATIVE_PASS',json.dumps(result))
bpy.context.window.scene=scene
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'CSC_TAILORS_Delivery_Native_Export.blend'))
