"""Refresh companion CN6s and make the new editable master use canonical textures."""
import bpy,json,sys,shutil,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'project/tools/scripts'));import io_export_cn6_b4
OUT=Path(sys.argv[sys.argv.index('--')+1]);ART=Path.home()/'Desktop/Working Files/3D Art';NAME='CSC_BAKERS_Wind_Mill_Tower'
tower_only='--tower-only' in sys.argv
records=[]
for row in ([] if tower_only else json.loads((OUT/'source-migration.json').read_text())):
    source=Path(row['source']);cn6=source.with_suffix('.cn6')
    if not cn6.exists():continue
    bpy.ops.wm.open_mainfile(filepath=row['staged'],load_ui=False,use_scripts=False)
    if 'Export' in bpy.data.scenes:bpy.context.window.scene=bpy.data.scenes['Export']
    if bpy.context.object and bpy.context.object.mode!='OBJECT':bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    rigs=[o for o in bpy.context.scene.objects if o.type=='ARMATURE']
    for ob in bpy.context.scene.objects:
        if ob.type in ['ARMATURE','MESH']:ob.hide_set(False);ob.select_set(True)
    if not rigs:raise ValueError('Missing export rig: '+str(source))
    bpy.context.view_layer.objects.active=rigs[0]
    target=OUT/'staged-sources'/cn6.relative_to(ART);io_export_cn6_b4.do_export(str(target),True,True)
    backup=OUT/'before-sources'/cn6.relative_to(ART);backup.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(cn6,backup)
    records.append({'source':str(cn6),'staged':str(target)})
if not tower_only:(OUT/'source-cn6-migration.json').write_text(json.dumps(records,indent=2))
path=OUT/'new-tower'/(NAME+'.blend');bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
destination=ART/'BAKERS/Wind Mill/tower'
destination.mkdir(parents=True,exist_ok=True)
shutil.copy2(OUT/'staged-textures'/(NAME+'_AO.png'),destination/(NAME+'_AO.png'))
for im in bpy.data.images:
    absolute=Path(bpy.path.abspath(im.filepath)).resolve()
    if im.name.startswith(NAME+'_AO'):
        if im.packed_file:im.unpack(method='REMOVE')
        im.filepath=str(destination/(NAME+'_AO.png'))
    elif absolute.parent==OUT/'staged-textures':
        im.filepath=str(ART/'Textures'/(Path(im.filepath).stem+'.dds'))
    elif im.source=='FILE':im.filepath=str(absolute)
review=bpy.data.scenes['Review'];camera=bpy.data.objects.get('Review_Camera')
if camera is None:
    camera=bpy.data.objects.new('Review_Camera',bpy.data.cameras.new('Review_Camera'));review.collection.objects.link(camera)
center=Vector((36.99,-24.17,76));camera.location=center+Vector((110,-180,100));camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=150;review.camera=camera
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':area.spaces.active.region_3d.view_location=center;area.spaces.active.region_3d.view_distance=160
bpy.context.scene.frame_set(1);bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(path),relative_remap=False)
print('SOURCE_FINALIZED',len(records),'companion CN6 exports and one new editable animated master')
