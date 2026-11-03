"""Remove only the eight cross-rungs covered by sail cloth; rebake self-AO."""
import bpy,bmesh,json,sys,math,hashlib,shutil
from pathlib import Path
from mathutils import Vector
OUT=Path(sys.argv[sys.argv.index('--')+1]);ROOT=Path(__file__).resolve().parents[3]
ART=Path.home()/'Desktop/Working Files/3D Art';SOURCE=ART/'BAKERS/Wind Mill/tower'
NAME='CSC_BAKERS_Wind_Mill_Tower';RELEASE='2026-10-24_Shared_01_r044'
for folder in ['masters','before','bakes','staged/Geometries']:(OUT/folder).mkdir(parents=True,exist_ok=True)
p=SOURCE/(NAME+'.blend');shutil.copy2(p,OUT/'before'/p.name)
(OUT/'inspection.json').write_text(json.dumps([dict(path=str(p),sha=hashlib.sha256(p.read_bytes()).hexdigest())],indent=2))
bpy.ops.wm.open_mainfile(filepath=str(p),load_ui=False,use_scripts=False)
if bpy.context.object and bpy.context.object.mode!='OBJECT':bpy.ops.object.mode_set(mode='OBJECT')
bpy.context.window.scene=bpy.data.scenes['Export'];scene=bpy.context.scene;scene.frame_set(1);rig=bpy.data.objects[NAME]
sails=bpy.data.objects[NAME+'_Sails'];me=sails.data;assert len(me.vertices)==462 and len(me.polygons)==420
tower=bpy.data.objects[NAME+'_Tower']
def signature(ob):
 return dict(vertices=[list(v.co) for v in ob.data.vertices],faces=[list(f.vertices) for f in ob.data.polygons],uvs=[[list(v.uv) for v in u.data] for u in ob.data.uv_layers],weights=[[(g.group,g.weight) for g in v.groups] for v in ob.data.vertices])
def face_signature(mesh,f):
 return tuple((tuple(mesh.vertices[mesh.loops[i].vertex_index].co),tuple(mesh.uv_layers['UV1'].data[i].uv),tuple(mesh.uv_layers['UV3'].data[i].uv)) for i in f.loop_indices)
tower_before=signature(tower)
remove={blade*64+i for blade in range(4) for i in list(range(32,40))+list(range(48,56))}
# Confirm these are precisely the two rungs beneath each pair of cloth panels.
RIGHT=Vector((math.sqrt(3)/2,-.5,0));HUB=Vector((26.99117,-41.48987,63.74731))
for blade in range(4):
 angle=math.radians(22.5+blade*90);along=RIGHT*math.sin(angle)+Vector((0,0,1))*math.cos(angle)
 for start,radius in [(32,23.6),(48,39.2)]:
  rs=[(me.vertices[blade*64+i].co-HUB).dot(along) for i in range(start,start+8)]
  assert abs(sum(rs)/8-radius)<.001 and max(rs)-min(rs)<1.56
expected=[face_signature(me,f) for f in me.polygons if not any(v in remove for v in f.vertices)]
expected_weights=[[(g.group,g.weight) for g in v.groups] for v in me.vertices if v.index not in remove]
bm=bmesh.new();bm.from_mesh(me);bm.verts.ensure_lookup_table();bmesh.ops.delete(bm,geom=[bm.verts[i] for i in sorted(remove)],context='VERTS');bm.to_mesh(me);bm.free();me.update()
assert len(me.vertices)==398 and len(me.polygons)==388
assert expected==[face_signature(me,f) for f in me.polygons]
assert expected_weights==[[(g.group,g.weight) for g in v.groups] for v in me.vertices]
report=[];source=(ROOT/'project/tools/blender/revise_windmill_shared_materials.py').read_text()
exec(compile(source[source.index('def bake_material'):source.index('def material')],'shared_bake','exec'))
bake(sails,[(NAME+'_Sails',[0,128,512,512],2048,10)])
assert signature(tower)==tower_before
sails['retained_rungs']='Four per blade, all visible from both sides: radius 8,15.8,31.4,48.2'
sails['removed_hidden_rungs']='Two per blade beneath cloth: radius 23.6 and39.2'
# Reuse the established save/export path, preserving the current rig and all remaining UV1/UV3.
source=Path(__file__).with_name('split_windmill_sails.py').read_text()
tail=source[source.index('for s in bpy.data.scenes:s[\'atlas_release\']'):source.index("(OUT/'authoring-report.json')")]
exec(compile(tail,'save_export','exec'))
(OUT/'authoring-report.json').write_text(json.dumps(dict(bakes=report,removed_rungs=8,rungs_per_blade=4,exposed_structural_rungs_per_blade=3,sail_vertices=398,sail_faces=388,retained_geometry_weights_UV1_UV3_preserved=True,tower_exactly_preserved=True),indent=2))
print('HIDDEN_RUNGS_REMOVED_AND_REBAKED',flush=True)
