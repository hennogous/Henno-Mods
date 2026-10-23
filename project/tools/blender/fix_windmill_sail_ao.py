"""Match both cloth surfaces' triangulation to prevent thin-sheet crossings."""
import bpy,bmesh,json,sys,hashlib,shutil
from pathlib import Path
OUT=Path(sys.argv[sys.argv.index('--')+1]);ROOT=Path(__file__).resolve().parents[3]
ART=Path.home()/'Desktop/Working Files/3D Art';SOURCE=ART/'BAKERS/Wind Mill/tower'
NAME='CSC_BAKERS_Wind_Mill_Tower';RUIN=NAME+'_CON+PIL';report=[];baseline=[]
for folder in ['masters','bakes','staged/Geometries']:(OUT/folder).mkdir(parents=True,exist_ok=True)
for name in [NAME,RUIN]:
    p=SOURCE/(name+'.blend');baseline.append(dict(path=str(p),sha=hashlib.sha256(p.read_bytes()).hexdigest()))
    shutil.copy2(p,OUT/'masters'/p.name)
    shutil.copy2(SOURCE/(name+'.cn6'),OUT/'staged/Geometries'/(name+'.cn6'))
    shutil.copy2(ROOT/'Civ Supply Chains/Geometries'/(name+'.fgx'),OUT/'staged/Geometries'/(name+'.fgx'))
bpy.ops.wm.open_mainfile(filepath=str(SOURCE/(NAME+'.blend')),load_ui=False,use_scripts=False)
scene=bpy.data.scenes['Export'];bpy.context.window.scene=scene;scene.frame_set(1)
ob=bpy.data.objects[NAME+'_Sails'];me=ob.data
before=[tuple(v.co) for v in me.vertices]
bm=bmesh.new();bm.from_mesh(me);bm.verts.ensure_lookup_table()
for blade in range(4):
    for a,b in [(64,68),(65,69),(67,71),(68,72)]:
        for side in [0,9]:
            va,vb=[bm.verts[blade*114+i+side] for i in (a,b)]
            shared=set(va.link_faces)&set(vb.link_faces);assert len(shared)==1 and len(next(iter(shared)).verts)==4
            bmesh.ops.connect_verts(bm,verts=[va,vb],check_degenerate=True)
bm.to_mesh(me);bm.free();me.update();me.calc_loop_triangles()
assert before==[tuple(v.co) for v in me.vertices]
assert len(me.polygons)==468
# Front and back now use precisely corresponding triangles, with 0.3 depth.
triangles={frozenset(t.vertices) for t in me.loop_triangles}
for blade in range(4):
    for t in me.loop_triangles:
        if all(blade*114+64<=i<blade*114+73 for i in t.vertices):assert frozenset(i+9 for i in t.vertices) in triangles
ob['cloth_matching_triangulation']=True
source=(ROOT/'project/tools/blender/revise_windmill_shared_materials.py').read_text()
exec(compile(source[source.index('def bake_material'):source.index('def material')],'shared_bake','exec'))
bake(ob,[(NAME+'_Sails',[0,128,512,512],2048,10)])
objects=[o for o in scene.objects if o.type=='MESH'];rig=bpy.data.objects[NAME]
for o in objects:o.data.uv_layers.active_index=0;o.data.uv_layers['UV1'].active_render=True
for s in bpy.data.scenes:s['atlas_release']='2026-10-22_Shared_01_r039'
bpy.ops.object.select_all(action='DESELECT')
for o in [rig,*objects]:o.select_set(True)
bpy.context.view_layer.objects.active=rig;bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'masters'/(NAME+'.blend')),relative_remap=False)
# Retain the prior export-only tower hard edges exactly.
tower=bpy.data.objects[NAME+'_Tower'];tower.data=tower.data.copy();bm=bmesh.new();bm.from_mesh(tower.data)
bmesh.ops.split_edges(bm,edges=[e for e in bm.edges if len(e.link_faces)==2 and e.calc_face_angle()>.01]);bm.to_mesh(tower.data);bm.free()
sys.path.insert(0,str(ROOT/'project/tools/scripts'));import io_export_cn6_b4
io_export_cn6_b4.do_export(str(OUT/'staged/Geometries'/(NAME+'.cn6')),True,True)
(OUT/'inspection.json').write_text(json.dumps(baseline,indent=2))
(OUT/'authoring-report.json').write_text(json.dumps(dict(bakes=report,cloth_matching_triangles=True,positions_preserved=True,source_vertices=len(me.vertices),source_faces=len(me.polygons)),indent=2))
print('SAIL_CROSSING_FIX_AUTHORED',flush=True)
