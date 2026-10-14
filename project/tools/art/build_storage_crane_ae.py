"""Build an isolated AE crane trial from the approved animation revision (Blender 5).

blender -b --python-exit-code 1 --python this.py -- --output <generated folder>
Does not change the source blend or production assets. Install with the companion script.
"""
import argparse, json, sys, subprocess
from pathlib import Path
import bpy
from mathutils import Matrix, Vector
from civ6_animation import core, backend
import io_export_cn6 as cn6

args=argparse.ArgumentParser();args.add_argument('--output',required=True)
out=Path(args.parse_args(sys.argv[sys.argv.index('--')+1:]).output).resolve();out.mkdir(parents=True,exist_ok=True)
repo=Path(__file__).resolve().parents[3]
source=Path(r'C:\Users\Shadow\Desktop\Codex\CSC_Storage_L\revision-01-crane-animation\CSC_Storage_L_Crane_Animation.blend')
nexus=r'C:\Program Files (x86)\CivNexus6_Release-1.3.3\CivNexus6'
for name in ('load_post','depsgraph_update_post'):
 for cb in list(getattr(bpy.app.handlers,name)):
  if cb.__module__.rsplit('.',1)[-1]=='csc_scene_tools':getattr(bpy.app.handlers,name).remove(cb)
bpy.ops.wm.open_mainfile(filepath=str(source));bpy.context.window.scene=bpy.data.scenes['Export'];scene=bpy.context.scene
rig=bpy.data.objects['CSC_Storage_Crane_Rig'];rig.data.pose_position='REST';scene.frame_set(1)
original_meshes=[o for o in scene.objects if o.type=='MESH' and o.name.startswith('CSC_Fixed_')]
static=[];moving=[]
for o in original_meshes:
 c=o.copy();c.data=o.data.copy();c.data.transform(o.matrix_world);c.matrix_world=Matrix.Identity(4)
 (moving if 'Crane' in o.name else static).append(c)
arm=rig.data.copy();action=rig.animation_data.action
for o in list(bpy.data.objects):
 if o not in static+moving:bpy.data.objects.remove(o,do_unlink=True)
rig=bpy.data.objects.new('CSC_TEST_Crane_Rig',arm);scene.collection.objects.link(rig);rig.animation_data_create();rig.animation_data.action=action
rig.animation_data.action_slot=action.slots[0]
rig.data.pose_position='POSE';rig.select_set(True);bpy.context.view_layer.objects.active=rig
# Give the otherwise unweighted Load attachment a native identity basis. CN6 and
# FBX apply the same cyclic bone-basis conversion; inverse it on this export copy.
bpy.ops.object.mode_set(mode='EDIT');bone=arm.edit_bones['Load'];head=bone.head.copy();length=bone.length
correction=Matrix(((0,1,0,0),(0,0,1,0),(1,0,0,0),(0,0,0,1)))
bone.matrix=Matrix.Translation(head)@correction;bone.length=length
bpy.ops.object.mode_set(mode='OBJECT')
for c in moving:
 scene.collection.objects.link(c);c.parent=rig
 for m in list(c.modifiers):c.modifiers.remove(m)
 if c.name.startswith('CSC_Fixed_Crane_Mount_Hardware'):
  c.vertex_groups.clear();c.vertex_groups.new(name='Root').add(list(range(len(c.data.vertices))),1,'REPLACE')
 c.modifiers.new('Animated crane','ARMATURE').object=rig
 c.name=c.name.replace('.001','');c.data.name=c.name
core.export_animation(out/'CSC_TEST_Storage_Crane_Lift.fgx',rig,nexus,1,361,include_model=True,overwrite=True)
expected={}
scene.frame_set(1);ground=rig.pose.bones['Load'].matrix.translation.copy()
scene.frame_set(151);raised=rig.pose.bones['Load'].matrix.translation.copy()
assert abs(ground.z-.2)<1e-4 and abs(raised.z-49.2)<1e-4,(ground,raised)
def vertices(o):
 e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();v=[e.matrix_world@x.co for x in m.vertices];e.to_mesh_clear();return v
for f in (1,65,120,151,175,220,245,270,291,321,359):
 scene.frame_set(f);expected[f]=[v for c in moving for v in vertices(c)]
backend.run(nexus,'extract',out/'CSC_TEST_Storage_Crane_Lift_Model.fgx',out/'CSC_TEST_Storage_Crane_Lift.fgx',out/'sampled',30,0,0)
sample=core.parse_na2(out/'sampled/clip.na2')[0];track=sample['tracks']['Load']
attachment_errors=[]
for f in expected:
 scene.frame_set(f)
 # Intended native attachment matrix: preserve Blender head and the swivel only.
 target=rig.pose.bones['Load'].matrix@correction.inverted()
 actual=core.world_matrix(track[f-1])
 attachment_errors.append(max(abs(target[i][j]-actual[i][j]) for i in range(4) for j in range(4)))
for o in list(bpy.data.objects):
 if o not in static:bpy.data.objects.remove(o,do_unlink=True)
converted,_=core.import_native(out/'CSC_TEST_Storage_Crane_Lift.anm',out/'CSC_TEST_Storage_Crane_Lift_Model.fgx',nexus)
errors={}
for f,points in expected.items():
 scene.frame_set(f);actual=[v for o in scene.objects if o.type=='MESH' for v in vertices(o)]
 errors[f]=max(min((a-b).length for b in actual) for a in points)
assert max(errors.values())<.15,errors
assert max(attachment_errors)<.06,attachment_errors
# Export the unchanged building shell with its full three-UV static format.
for o in list(bpy.data.objects):
 if o not in static:bpy.data.objects.remove(o,do_unlink=True)
arm=bpy.data.armatures.new('Storage shell');rig=bpy.data.objects.new('CSC_TEST_Storage_Shell',arm);scene.collection.objects.link(rig)
rig.select_set(True);bpy.context.view_layer.objects.active=rig;bpy.ops.object.mode_set(mode='EDIT')
bone=arm.edit_bones.new('Bone');bone.head=(0,0,0);bone.tail=(0,1,0);bpy.ops.object.mode_set(mode='OBJECT')
for c in static:
 scene.collection.objects.link(c);c.parent=rig
 for m in list(c.modifiers):c.modifiers.remove(m)
 c.vertex_groups.clear();c.vertex_groups.new(name='Bone').add(list(range(len(c.data.vertices))),1,'REPLACE');c.select_set(True)
 c.modifiers.new('Static binding','ARMATURE').object=rig
 c.name=c.name.replace('.001','');c.data.name=c.name
cn6.do_export(str(out/'CSC_TEST_Storage_Shell.cn6'),True,True)
converter=repo/'project/tools/cn6libs/CN6ToFGX.exe'
r=subprocess.run([str(converter),str(out/'CSC_TEST_Storage_Shell.cn6'),str(out/'CSC_TEST_Storage_Shell.fgx'),'2'],cwd=converter.parent,capture_output=True,text=True)
(out/'shell-conversion.log').write_text(r.stdout+r.stderr);assert r.returncode==0,r.stderr
# Use the installed GEO writer so mesh and group names come from the actual CN6.
cn6.csc_write_geo(str(out/'CSC_TEST_Storage_Shell.geo'),'CSC_TEST_Storage_Shell',str(out/'CSC_TEST_Storage_Shell.cn6'),'LandmarkModel')
report={'source':str(source),'crane_meshes':len(moving),'shell_meshes':len(static),'native_vertex_errors':errors,'native_vertex_error_max':max(errors.values()),'attachment_native_matrix_error_max':max(attachment_errors),'attachment_bone':'Load','attachment_position':[0,0,0],'attachment_orientation':[0,0,0],'attachment_scale':.75,'source_modified':False,'ae_playback_verified':False}
(out/'conversion-check.json').write_text(json.dumps(report,indent=2));print('CRANE_AE_CONVERSION_PASS')
