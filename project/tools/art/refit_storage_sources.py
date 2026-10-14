"""Anchor the narrow front and apply the same size change to the crane source."""
import bpy,json,shutil,hashlib
from pathlib import Path
from mathutils import Matrix,Vector
BASE=Path(r'C:\Users\Shadow\Desktop\Codex\CSC_Storage_L')
OUT=BASE/'delivery-refit-20261009';ROOT=Path(r'C:\Users\Shadow\Desktop\Working Files\3D Art\Storage\Storage_L')
for event in ('load_post','depsgraph_update_post'):
 for cb in list(getattr(bpy.app.handlers,event)):
  if cb.__module__.rsplit('.',1)[-1]=='csc_scene_tools':getattr(bpy.app.handlers,event).remove(cb)
M=Matrix(json.loads((BASE/'interior-20261008/source-transform.json').read_text())['matrix'])
pivot=Vector((M.translation.x,M.translation.y,0));front=M@Vector((0,-50.85509490966797,0));front.z=0
A=Matrix.Translation(front)@Matrix.Scale(.9,4)@Matrix.Translation(-front)
B=Matrix.Translation(pivot)@Matrix.Scale(.9,4)@Matrix.Translation(-pivot)
shift=A@B.inverted()
backup=OUT/'before-refit';backup.mkdir(exist_ok=False)
for name in ('CSC_Storage_L.blend','CSC_Storage_L_Crane.blend'):shutil.copy2(ROOT/name,backup/name)
for name in ('delivery-context.blend','CSC_TAILORS_Storage_Delivery.blend','CSC_TAILORS_Delivery_Native_Export.blend','authoring-check.json','native-check.json','CSC_TEST_TAILORS_Delivery_Master_Model.fgx','CSC_TEST_TAILORS_Delivery_Master_Model.geo','CSC_TEST_TAILORS_Delivery_Master.fgx','CSC_TEST_TAILORS_Delivery_Master.anm'):
 shutil.copy2(BASE/'delivery-01'/name,backup/name)
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'CSC_Storage_L.blend'))
o=bpy.data.objects['CSC_Storage_L_Bldg'];before=[v.co.copy() for v in o.data.vertices]
o.data.transform(shift);o['storage_resize_pivot']=list(front);o['storage_front_anchor']='Narrow gabled end; original front wall plane held at the road setback.'
# Check the complete original front plane, not merely its centre point.
newM=A@M;normal=(M.to_3x3()@Vector((0,-1,0))).normalized()
assert abs((newM@Vector((10,-50.85509490966797,0))-front).dot(normal))<.00003
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'CSC_Storage_L.blend'))
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'CSC_Storage_L_Crane.blend'))
placement=bpy.data.objects['Crane_Placement'];oldP=placement.matrix_world.copy();placement.matrix_world=A@oldP
# Keep the standalone preview load's size while its hook follows the smaller crane.
attachment=next(o for o in bpy.data.objects if o.name.startswith('Attach_CSC_ALL_Textile_Bale'))
attachment.scale/= .9
placement['storage_refit_scale']=.9;placement['storage_refit_anchor']=list(front)
newP=placement.matrix_world.copy()
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'CSC_Storage_L_Crane.blend'))
report={'anchor':'narrow gabled front','front_world':list(front),'scale':.9,'building_shift_from_previous_turn':list(shift.translation),
 'world_transform_from_pre_resize':[list(r) for r in A],'original_building_transform':[list(r) for r in M],
 'new_building_transform':[list(r) for r in newM],'old_crane_matrix':[list(r) for r in oldP],'new_crane_matrix':[list(r) for r in newP],
 'front_plane_preserved':True,'donkey_scale':1.,'backup':str(backup)}
(OUT/'source-refit-check.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
