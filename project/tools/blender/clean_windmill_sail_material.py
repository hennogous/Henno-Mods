"""Remove the unused plaster slot from the rotor's native topology groups."""
import bpy,sys,json,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];OUT=Path(sys.argv[sys.argv.index('--')+1]);NAME='CSC_BAKERS_Wind_Mill_Tower'
source=OUT/'new-tower'/(NAME+'.blend')
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
scene=bpy.data.scenes['Export'];bpy.context.window.scene=scene;scene.frame_set(1)
rotor=bpy.data.objects[NAME+'_Sails'];mesh=rotor.data
assert len(mesh.materials)==2 and all(f.material_index==1 for f in mesh.polygons)
before=dict(vertices=[tuple(v.co) for v in mesh.vertices],uvs=[[tuple(v.uv) for v in u.data] for u in mesh.uv_layers])
mesh.materials.pop(index=0)
assert len(mesh.materials)==1 and mesh.materials[0].name=='CSC_BAKERS_Wind_Mill_Sails' and all(f.material_index==0 for f in mesh.polygons)
assert before==dict(vertices=[tuple(v.co) for v in mesh.vertices],uvs=[[tuple(v.uv) for v in u.data] for u in mesh.uv_layers])
archive=OUT/'before-group-cleanup';archive.mkdir(exist_ok=True)
for p in [source,OUT/'staged/Geometries'/(NAME+'.cn6'),OUT/'staged/Geometries'/(NAME+'.fgx'),OUT/'tower-native.json']:
    assert not (archive/p.name).exists();shutil.copy2(p,archive/p.name)
bpy.ops.wm.save_as_mainfile(filepath=str(source),relative_remap=False)
bpy.ops.object.select_all(action='DESELECT')
for ob in scene.objects:
    if ob.type in ['MESH','ARMATURE']:ob.select_set(True)
bpy.context.view_layer.objects.active=bpy.data.objects[NAME]
sys.path.insert(0,str(ROOT/'project/tools/scripts'));import io_export_cn6_b4
io_export_cn6_b4.do_export(str(OUT/'staged/Geometries'/(NAME+'.cn6')),True,True)
print('Removed unused sail material slot; geometry and UVs unchanged.')
