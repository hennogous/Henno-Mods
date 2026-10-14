"""Synchronize saved Blender rig identities after the verified native rename."""
import bpy,json,shutil
from pathlib import Path
BASE=Path(r'C:\Users\Shadow\Desktop\Codex\CSC_Storage_L\delivery-01')
OUT=BASE/'production-rig-rename'
OLD='CSC_TEST_TAILORS_Delivery_Rig';NEW='CSC_ALL_Delivery_Rig'
paths=[BASE/'CSC_TAILORS_Delivery_Native_Export.blend',BASE/'CSC_TAILORS_Storage_Delivery.blend',
       Path(r'C:\Users\Shadow\Desktop\Working Files\3D Art\Storage\Storage_L\Delivery\CSC_TAILORS_Storage_Delivery.blend')]
for event in ('load_post','depsgraph_update_post'):
    for cb in list(getattr(bpy.app.handlers,event)):
        if cb.__module__.rsplit('.',1)[-1]=='csc_scene_tools':getattr(bpy.app.handlers,event).remove(cb)
def poses():
    result={}
    for scene in bpy.data.scenes:
        rigs=[o for o in scene.objects if o.type=='ARMATURE']
        if not rigs:continue
        bpy.context.window.scene=scene
        for frame in (1,811,1701):
            scene.frame_set(frame);bpy.context.view_layer.update()
            for o in rigs:
                for i,b in enumerate(o.pose.bones):
                    result[(scene.name,frame,o.as_pointer(),i)]=o.matrix_world@b.matrix
    return result
reports=[]
for index,path in enumerate(paths):
    bpy.ops.wm.open_mainfile(filepath=str(path));before=poses();changes=[]
    for collection in (bpy.data.objects,bpy.data.armatures):
        for item in collection:
            if item.name==OLD or item.name.startswith(OLD+'.'):
                changes.append(item.name);item.name=item.name.replace(OLD,NEW,1)
            for key in list(item.keys()):
                if isinstance(item[key],str) and OLD in item[key]:
                    changes.append(item.name+':'+key);item[key]=item[key].replace(OLD,NEW)
    for arm in bpy.data.armatures:
        for bone in arm.bones:
            if bone.name==OLD:changes.append(arm.name+':bone');bone.name=NEW
    for o in bpy.data.objects:
        for group in o.vertex_groups:
            if group.name==OLD:changes.append(o.name+':group');group.name=NEW
    # Bone renaming updates most action paths automatically; cover layered slots.
    for action in bpy.data.actions:
        for layer in action.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    for curve in bag.fcurves:
                        if OLD in curve.data_path:
                            changes.append(action.name+':channel');curve.data_path=curve.data_path.replace(OLD,NEW)
    after=poses();assert before.keys()==after.keys()
    error=max(abs(before[k][i][j]-after[k][i][j]) for k in before for i in range(4) for j in range(4))
    assert error<1e-6,(path,error)
    if changes:
        backup=OUT/f'blend-backup-{index}-{path.name}';assert not backup.exists();shutil.copy2(path,backup)
        bpy.ops.wm.save_as_mainfile(filepath=str(path))
    reports.append({'path':str(path),'changes':changes,'maximum_pose_matrix_difference':error})
(OUT/'blend-check.json').write_text(json.dumps(reports,indent=2));print(json.dumps(reports))
