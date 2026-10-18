"""Inspect the relocated master without rebuilding user geometry."""
import bpy,sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from cafe_atlas import OUT,ART,sha
import importlib.util
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
path=ART/'Decals/CSC_ALL_Stage_4_Cobble_Decals.blend'
bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
if '--repair-paths' in sys.argv:
    geometry=lambda:[(o.name,[list(row) for row in o.matrix_world],[list(v.co) for v in o.data.vertices],[[list(d.uv) for d in u.data] for u in o.data.uv_layers]) for o in bpy.data.objects if o.type=='MESH']
    before=geometry()
    for im in bpy.data.images:
        if im.source!='FILE':continue
        target=path.parent/im.name if im.name.startswith('CSC_ALL_Stage_4_') else ART/'Textures/CSC_Props/Current/textures'/im.name
        assert target.exists(),str(target)
        im.filepath=bpy.path.relpath(str(target));im.reload()
    bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(path))
    bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
    assert before==geometry(),'Geometry or UVs changed during image-path repair'
images=[dict(name=i.name,path=bpy.path.abspath(i.filepath),exists=Path(bpy.path.abspath(i.filepath)).exists()) for i in bpy.data.images if i.source=='FILE']
V=module('cafe_fit_validator',Path(__file__).resolve().parents[1]/'blender/csc_scene_validation.py')
report=V.validate_current_scene();report.update(source=str(path),source_sha256=sha(path),images=images)
(OUT/'relocated-master-validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(dict(automated_pass=report['automated_pass'],images=images),indent=2))
