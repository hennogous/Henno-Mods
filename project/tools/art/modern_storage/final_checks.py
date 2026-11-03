"""Validate exact delivered files and record full review-scene geometry counts."""
import bpy,json,sys,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];O=Path.home()/'Desktop/Codex/modern-storage-v1-20261029';sys.path[:0]=[str(ROOT/'project/tools/blender'),str(ROOT/'project/tools/blender/scene_export')]
from csc_scene_validation import suspend_csc_repairs,validate_current_scene
import decode_blend as dec
records=json.loads((O/'masters.json').read_text());reports=[]
paths=[Path(r['blend']) for r in records]
for r in records:
 if r['group'] in ('M','L'):paths+=list(Path(r['blend']).parent.glob('*_Review.blend'))
for path in paths:
 with suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
 result=validate_current_scene();assert result['automated_pass'],(str(path),result['findings'])
 s=bpy.data.scenes['Review'];bpy.context.window.scene=s;bpy.context.view_layer.update();counts={}
 for ob in s.objects:
  if ob.type=='MESH' and not ob.hide_render:
   m=dec.decode_mesh(ob,ob.matrix_world);group=ob.get('module','unlabelled');counts[group]=counts.get(group,0)+len(m['vertices'])
 reports.append({'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'saved_file_automated_pass':True,'visible_exported_vertices_by_group':counts,'visible_scene_vertices':sum(counts.values())})
(O/'final-saved-validation.json').write_text(json.dumps(reports,indent=2));print('ALL_FINAL_SAVED_FILES_PASS',len(reports),flush=True)
