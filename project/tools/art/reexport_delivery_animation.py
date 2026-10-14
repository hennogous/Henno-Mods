"""Retry native animation conversion from the already-baked export scene."""
import bpy,json,sys,inspect
from pathlib import Path
from civ6_animation import core,backend
from mathutils import Matrix
OUT=Path(r'C:\Users\Shadow\Desktop\Codex\CSC_Storage_L\delivery-01')
NEXUS=r'C:\Program Files (x86)\CivNexus6_Release-1.3.3\CivNexus6'
SAMPLES=[1,113,151,163,301,601,721,811,841,901,991,1081,1201,1261,1321,1561,1617,1629,1701,1741,1891,2041]
def vertices(o):
 e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();v=[e.matrix_world@p.co for p in m.vertices];e.to_mesh_clear();return v
bpy.ops.wm.open_mainfile(filepath=str(OUT/'CSC_TAILORS_Storage_Delivery.blend'))
s=bpy.data.scenes['Export'];bpy.context.window.scene=s
master=bpy.data.objects['CSC_Storage_Crane_Rig'];dm=bpy.data.objects['CSC_Delivery_Donkey_Mesh']
body_scale=float(bpy.data.objects['CSC_Delivery_Donkey_Rig']['delivery_body_scale'])
crane=[o for o in s.objects if o.type=='MESH' and 'Crane' in o.name]
expected={};body_expected={};attachments={}
for f in SAMPLES:
 s.frame_set(f);expected[f]=[p for o in crane for p in vertices(o)];body_expected[f]=vertices(dm)
 attachments[f]={n:master.matrix_world@master.pose.bones[n].matrix for n in ('DonkeyPath','Cargo')}
bpy.ops.wm.open_mainfile(filepath=str(OUT/'CSC_TAILORS_Delivery_Native_Export.blend'))
scene=bpy.data.scenes['Native_Master'];bpy.context.window.scene=scene
rig=next(o for o in scene.objects if o.type=='ARMATURE')
sys.path.insert(0,str(Path(__file__).resolve().parent))
from delivery_pose_adjustments import linearize_baked_keys
linearize_baked_keys(rig)
model='CSC_TEST_TAILORS_Delivery_Master_Model';clip='CSC_TEST_TAILORS_Delivery_Master'
report=core.export_animation(OUT/(clip+'.fgx'),rig,NEXUS,1,2041,include_model=False,overwrite=True)
backend.run(NEXUS,'extract',OUT/(model+'.fgx'),OUT/(clip+'.fgx'),OUT/'Master-sampled',30,0,0)
source=Path(__file__).with_name('export_storage_delivery.py').read_text()
exec(source[source.index("sample=core.parse_na2"):])
