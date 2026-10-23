"""Keep the base's front scaffold locally while hiding its shared two-part group."""
import bpy,bmesh,json,sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[3];OUT=Path(sys.argv[sys.argv.index('--')+1]);NAME='CSC_BAKERS_Wind_Mill_Tower';RUIN=NAME+'_CON+PIL'
bpy.ops.wm.open_mainfile(filepath=str(OUT/'review-Construction/sv/CSC_BAKERS_Wind_Mill_sv.blend'),load_ui=False,use_scripts=False)
scaffolds=[o for o in bpy.context.scene.objects if o.type=='MESH' and 'Scaffolding/' in o.get('ae_semantic_path','')]
base=next(o for o in scaffolds if NAME not in o.get('ae_semantic_path',''))
tower=next(o for o in scaffolds if NAME in o.get('ae_semantic_path',''))
transform=tower.matrix_world.inverted()@base.matrix_world
bpy.ops.wm.open_mainfile(filepath=str(OUT/'masters'/(RUIN+'.blend')),load_ui=False,use_scripts=False)
scene=bpy.data.scenes['Export'];bpy.context.window.scene=scene;rig=bpy.data.objects[RUIN]
path=Path.home()/'Desktop/Working Files/3D Art/Level 1/CSC_Level_1_S_CON+PIL.blend'
with bpy.data.libraries.load(str(path),link=False) as (src,dst):dst.objects=['Scaffolding']
ob=dst.objects[0];scene.collection.objects.link(ob);bpy.data.scenes['Review'].collection.objects.link(ob)
ob.name=RUIN+'_Base_Scaffolding';ob.data=ob.data.copy();ob.modifiers.clear();ob.parent=None
bm=bmesh.new();bm.from_mesh(ob.data);rear=[v for v in bm.verts if v.co.x>52.7771]
assert len(rear)>0
bmesh.ops.delete(bm,geom=rear,context='VERTS');bm.to_mesh(ob.data);bm.free();ob.data.transform(transform);ob.data.update()
ob.matrix_world.identity();ob.vertex_groups.clear();g=ob.vertex_groups.new(name='Root');g.add(list(range(len(ob.data.vertices))),1,'REPLACE')
if 'originalTangentsBinormals' in ob.data:del ob.data['originalTangentsBinormals']
ob.parent=rig;mod=ob.modifiers.new('Tower skeleton','ARMATURE');mod.object=rig
ob['role']='building_geometry';ob['export_role']='building_geometry';ob['source_asset_id']=RUIN;ob['source_mesh']='Scaffolding';ob['source_blend']=str(path);ob['retained_section']='front base scaffold, exact saved AE world placement'
ob.data.materials[0]=bpy.data.objects[RUIN+'_Scaffolding'].data.materials[0]
objects=[o for o in scene.objects if o.type=='MESH'];bpy.ops.object.select_all(action='DESELECT')
for o in [rig,*objects]:o.select_set(True)
bpy.context.view_layer.objects.active=rig;bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'masters'/(RUIN+'.blend')),relative_remap=False)
sys.path.insert(0,str(ROOT/'project/tools/scripts'));import io_export_cn6_b4
io_export_cn6_b4.do_export(str(OUT/'staged/Geometries'/(RUIN+'.cn6')),True,True)
(OUT/'scaffold-placement.json').write_text(json.dumps(dict(transform=[list(r) for r in transform],retained_vertices=len(ob.data.vertices),retained_faces=len(ob.data.polygons)),indent=2))
