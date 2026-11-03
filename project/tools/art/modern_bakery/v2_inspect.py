import bpy,json,sys,shutil
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[4];ART=Path.home()/'Desktop/Working Files/3D Art';O=Path.home()/'Desktop/Codex/modern-bakery-v2-20261028'
sys.path.insert(0,str(ROOT/'project/tools/blender'));from csc_scene_validation import suspend_csc_repairs
for p in (O,O/'sources',O/'bakes',O/'review',O/'models'):p.mkdir(parents=True,exist_ok=True)
shutil.copytree(ART/'BAKERS/Bakery/modern/revision-01-sheltered-bakery/textures',O/'textures',dirs_exist_ok=True)
rows={}
for label,path in [('historical',ART/'Level 2/CSC_Level_2.blend'),('modern',ART/'Level 2/modern/revision-03-window-boxes-sign/CSC_Level_2_Modern_Review.blend')]:
 with suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
 scene=bpy.data.scenes.get('Export') or bpy.context.scene;bpy.context.window.scene=scene;bpy.context.view_layer.update();rows[label]=[]
 for ob in scene.objects:
  if ob.type!='MESH':continue
  vs=[ob.matrix_world@v.co for v in ob.data.vertices]
  rows[label].append({'name':ob.name,'module':ob.get('module'),'min':[min(v[i] for v in vs) for i in range(3)],'max':[max(v[i] for v in vs) for i in range(3)],'vertices':len(vs),'polys':len(ob.data.polygons)})
(O/'source-inspection.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows),flush=True)
