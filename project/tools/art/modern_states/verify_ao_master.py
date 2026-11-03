import bpy,bmesh,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT/'project/tools/blender'))
from csc_scene_validation import suspend_csc_repairs,validate_current_scene
O=Path.home()/'Desktop/Codex/modern-l1-ao-fix-20261028';result=[]
with suspend_csc_repairs():
 for row in json.loads((O/'repair-report.json').read_text()):
  p=Path(row['source']);bpy.ops.wm.open_mainfile(filepath=str(p),load_ui=False,use_scripts=False);bpy.context.window.scene=bpy.data.scenes['Export'];walls=[]
  for o in bpy.context.scene.objects:
   if o.type=='MESH' and o.name.startswith('State_Brick_'):
    bm=bmesh.new();bm.from_mesh(o.data);assert all(e.is_contiguous for e in bm.edges) and bm.calc_volume(signed=True)>0;bm.free();walls.append(o.name)
  v=validate_current_scene();assert v['automated_pass'];(O/(row['asset']+'-saved-validation.json')).write_text(json.dumps(v,indent=2));result.append({'source':str(p),'outward_contiguous_walls':walls,'automated_pass':True})
(O/'final-saved-checks.json').write_text(json.dumps(result,indent=2));print('SAVED_MASTERS_PASS')
