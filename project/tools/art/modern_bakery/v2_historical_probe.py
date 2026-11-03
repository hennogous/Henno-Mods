import bpy,sys,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];O=Path.home()/'Desktop/Codex/modern-bakery-v2-20261028';ART=Path.home()/'Desktop/Working Files/3D Art'
sys.path.insert(0,str(ROOT/'project/tools/blender'));from csc_scene_validation import suspend_csc_repairs
with suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(ART/'BAKERS/Bakery/revision-09-l2-placement/CSC_BAKERS_Bakery.blend'),load_ui=False,use_scripts=False)
out=[]
for o in bpy.data.scenes['Export'].objects:
 if o.type=='MESH':
  vs=[o.matrix_world@v.co for v in o.data.vertices];out.append({'name':o.name,'role':o.get('export_role'),'asset':o.get('source_asset_id'),'min':[min(v[i] for v in vs) for i in range(3)],'max':[max(v[i] for v in vs) for i in range(3)]})
(O/'historical-bakery-objects.json').write_text(json.dumps(out,indent=2));print(json.dumps(out),flush=True)
