"""Verify the saved source remains static, weighted, and exportable with three UVs."""
import bpy,json,sys
from pathlib import Path
import io_export_cn6 as cn6
OUT=Path(r'C:\Users\Shadow\Desktop\Codex\CSC_Storage_L\interior-20261008')
SOURCE=Path(r'C:\Users\Shadow\Desktop\Working Files\3D Art\Storage\Storage_L\CSC_Storage_L.blend')
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));s=bpy.data.scenes['Export'];bpy.context.window.scene=s
obj=bpy.data.objects['CSC_Storage_L_Bldg'];rig=bpy.data.objects['CSC_Storage_L']
assert [u.name for u in obj.data.uv_layers]==['UV1','UV2','UV3']
root=obj.vertex_groups.find('Root')
assert all(any(g.group==root and abs(g.weight-1)<1e-7 for g in v.groups) for v in obj.data.vertices)
for image in bpy.data.images:
 if image.source=='FILE':assert Path(bpy.path.abspath(image.filepath)).exists(),image.filepath
cn6.csc_do_export_selected(str(OUT/'CSC_Storage_L.cn6'),[rig,obj])
report={'source':str(SOURCE),'source_vertices':len(obj.data.vertices),'source_faces':len(obj.data.polygons),'uv_layers':[u.name for u in obj.data.uv_layers],'all_vertices_root_weighted':True,'texture_paths_exist':True,'cn6_exported':True}
(OUT/'export-check.json').write_text(json.dumps(report,indent=2));print('INTERIOR_EXPORT_PASS',report)
