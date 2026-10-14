"""Publish the checked source-only building edit and verify a normal CN6 export."""
import bpy,json,hashlib,shutil
from pathlib import Path
from mathutils import Vector
import io_export_cn6 as cn6
ROOT=Path(r'C:\Users\Shadow\Desktop\Working Files\3D Art\Storage\Storage_L')
SOURCE=ROOT/'CSC_Storage_L.blend'
OUT=Path(r'C:\Users\Shadow\Desktop\Codex\CSC_Storage_L\foundation-scale-20261009')
MOD=Path(__file__).resolve().parents[3]/'Civ Supply Chains'
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
edit=json.loads((OUT/'edit-check.json').read_text());validation=json.loads((OUT/'validation.json').read_text())
assert validation['automated_pass'] and validation['error_count']==0 and validation['warning_count']==0
assert digest(SOURCE)==edit['source_sha256'],'User source changed since staging'
assert digest(OUT/'CSC_Storage_L.blend')==validation['source_sha256']
protected=[ROOT/'CSC_Storage_L_Crane.blend',ROOT/'Delivery/CSC_TAILORS_Storage_Delivery.blend',ROOT/'CSC_Storage_L_CON+PIL.blend',
           MOD/'Geometries/CSC_ALL_Delivery.fgx',MOD/'Animations/CSC_ALL_Delivery.fgx',MOD/'Assets/CSC_TAILORS_Storage_L.ast']
hashes={str(p):digest(p) for p in protected}
backup=OUT/'before-foundation-scale.blend';assert not backup.exists();shutil.copy2(SOURCE,backup)
shutil.copy2(OUT/'CSC_Storage_L.blend',SOURCE)
for event in ('load_post','depsgraph_update_post'):
 for cb in list(getattr(bpy.app.handlers,event)):
  if cb.__module__.rsplit('.',1)[-1]=='csc_scene_tools':getattr(bpy.app.handlers,event).remove(cb)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));s=bpy.data.scenes['Export'];bpy.context.window.scene=s
o=bpy.data.objects['CSC_Storage_L_Bldg'];m=o.data;rig=bpy.data.objects['CSC_Storage_L']
source=json.loads((OUT/'source.json').read_text());before=next(x for x in source['objects'] if x['name']==o.name)
pivot=Vector(edit['pivot'])
assert len(m.vertices)==1874 and len(m.polygons)==474
for i,p in enumerate(before['vertices']):assert (m.vertices[i].co-(pivot+(Vector(p)-pivot)*.9)).length<.00003
for i,face in enumerate(before['faces']):
 assert list(m.polygons[i].vertices)==face
 for name,uvs in before['uvs'].items():
  assert [list(m.uv_layers[name].data[j].uv) for j in m.polygons[i].loop_indices]==uvs[i]
for index in edit['extension_faces']:
 p=m.polygons[index];zs=[m.vertices[i].co.z for i in p.vertices]
 assert abs(max(zs))<1e-6 and abs(min(zs)-edit['foundation_bottom_after'])<.00001
root=o.vertex_groups['Root'].index
assert all(any(w.group==root and abs(w.weight-1)<1e-7 for w in v.groups) for v in m.vertices)
for im in bpy.data.images:
 if im.source=='FILE':assert Path(bpy.path.abspath(im.filepath)).is_file(),im.filepath
cn6.csc_do_export_selected(str(OUT/'CSC_Storage_L.cn6'),[rig,o])
assert digest(SOURCE)==validation['source_sha256']
assert hashes=={str(p):digest(p) for p in protected}
drop=Path(r'C:\Users\Shadow\Desktop\Working Files\Dropzone')
for name in ('Building','Front-Entrance','Side-Entrance'):shutil.copy2(OUT/(name+'.png'),drop/('Storage-L-Foundation-09-'+name+'.png'))
report={'saved':str(SOURCE),'source_sha256':digest(SOURCE),'backup':str(backup),'source_vertices':len(m.vertices),
 'prepared_export_vertices':validation['counts']['main_vertices'],'retained_uvs_verified':True,'normal_cn6_export_passed':True,
 'protected_files_unchanged':hashes,'runtime_assets_exported':False}
(OUT/'saved-source-check.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
