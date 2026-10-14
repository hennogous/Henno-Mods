"""Restore donor runner faces while preserving authored motion and the cargo deck."""
import bpy, bmesh, json, sys, shutil, hashlib
from pathlib import Path
from collections import Counter
sys.path.insert(0,str(Path(__file__).resolve().parent))
from delivery_sled_geometry import remove_native_payload
OUT=Path(r'C:\Users\Shadow\Desktop\Codex\CSC_Storage_L\delivery-01')
SOURCE=Path(r'C:\Users\Shadow\Desktop\Codex\Civ6-animation-research-20261007\IMP_Mine_AN_Sledge_Geo-animation-study.blend')
backup=OUT/'before-runner-repair-09';backup.mkdir(exist_ok=True)
for name in ('CSC_TAILORS_Storage_Delivery.blend','CSC_TAILORS_Delivery_Native_Export.blend',
             'native-check.json','CSC_TEST_TAILORS_Delivery_Master_Model.fgx',
             'CSC_TEST_TAILORS_Delivery_Master_Model.geo','CSC_TEST_TAILORS_Delivery_Master.fgx',
             'CSC_TEST_TAILORS_Delivery_Master.anm'):
    if not (backup/name).exists():shutil.copy2(OUT/name,backup/name)
assert (OUT/'CSC_TAILORS_Storage_Delivery.blend').read_bytes()==(backup/'CSC_TAILORS_Storage_Delivery.blend').read_bytes(),'Repair already applied or source changed'
for event in ('load_post','depsgraph_update_post'):
    for cb in list(getattr(bpy.app.handlers,event)):
        if cb.__module__.rsplit('.',1)[-1]=='csc_scene_tools':getattr(bpy.app.handlers,event).remove(cb)
bpy.ops.wm.open_mainfile(filepath=str(OUT/'CSC_TAILORS_Storage_Delivery.blend'))
bpy.context.window.scene=bpy.data.scenes['Export']
dm=bpy.data.objects['CSC_Delivery_Donkey_Mesh']
def signatures(o):
    m=o.data;uv=m.uv_layers[0]
    def corner(li):
        v=m.vertices[m.loops[li].vertex_index]
        weights=tuple(sorted((o.vertex_groups[g.group].name,round(g.weight,6)) for g in v.groups if o.vertex_groups[g.group].name!='_VERTEX_KEYS'))
        return (tuple(round(x,5) for x in v.co),tuple(round(x,6) for x in uv.data[li].uv),weights)
    result=Counter()
    for p in m.polygons:
        corners=[corner(li) for li in p.loop_indices]
        result[min(tuple(corners[i:]+corners[:i]) for i in range(len(corners)))]+=1
    return result
before=signatures(dm);old_count=len(dm.data.vertices)
old_coordinates=[v.co.copy() for v in dm.data.vertices]
# Keep the existing deck, including its UVs and skin weights.
deck=dm.copy();deck.data=dm.data.copy();bpy.context.scene.collection.objects.link(deck)
for mod in list(deck.modifiers):deck.modifiers.remove(mod)
world=dm.matrix_world.copy();deck.parent=None;deck.matrix_world=world
ids={v.index for v in deck.data.vertices if abs(v.co.z-7)<1e-5 or abs(v.co.z-9)<1e-5}
assert len(ids)==8 and ids==set(range(old_count-8,old_count)),ids
bm=bmesh.new();bm.from_mesh(deck.data);bm.verts.ensure_lookup_table()
bmesh.ops.delete(bm,geom=[v for v in bm.verts if v.index not in ids],context='VERTS');bm.to_mesh(deck.data);bm.free()
assert len(deck.data.polygons)==6
with bpy.data.libraries.load(str(SOURCE),link=False) as (src,dst):
    dst.objects=['IMP_Mine_AN_Sledge_Mesh#M']
original=dst.objects[0]
assert [g.name for g in original.vertex_groups]==[g.name for g in dm.vertex_groups]
report=remove_native_payload(original)
materials=list(dm.data.materials)
dm.data=original.data.copy();dm.data.materials.clear()
for mat in materials:dm.data.materials.append(mat)
bpy.data.objects.remove(original,do_unlink=True)
bpy.ops.object.select_all(action='DESELECT');dm.select_set(True);deck.select_set(True)
bpy.context.view_layer.objects.active=dm;bpy.ops.object.join()
# Joining under the animated parent introduces ~1e-5 local-coordinate roundoff.
# Keep the exact existing coordinates wherever the original vertex survives.
maximum_snap=0
for v in dm.data.vertices:
    nearest=min(old_coordinates,key=lambda p:(p-v.co).length_squared)
    distance=(nearest-v.co).length
    if distance<.0001:
        maximum_snap=max(maximum_snap,distance);v.co=nearest
after=signatures(dm)
assert not before-after,'Previously surviving faces, UVs or weights changed'
assert sum((after-before).values())==12
assert len(dm.data.vertices)==old_count+12
report.update(restored_vertices=12,restored_triangles=12,previous_vertices=old_count,
              repaired_vertices=len(dm.data.vertices),previous_faces=sum(before.values()),
              repaired_faces=sum(after.values()),existing_faces_uvs_weights_preserved=True,maximum_join_roundoff=maximum_snap,
              backup=str(backup),clip_sha256=hashlib.sha256((OUT/'CSC_TEST_TAILORS_Delivery_Master.fgx').read_bytes()).hexdigest())
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'CSC_TAILORS_Storage_Delivery.blend'))
(OUT/'runner-repair-check.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
