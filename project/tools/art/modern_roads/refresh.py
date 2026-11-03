"""Check saved art masters and re-render after external texture updates."""
import bpy,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT/'project/tools/blender'))
from csc_scene_validation import suspend_csc_repairs,validate_current_scene
O=Path.home()/'Desktop/Codex/Quarter-Roads-Modern/draft-03-roundabout';D=Path.home()/'Desktop/Working Files/3D Art/Decals/CSC_ALL_Modern_Roads'
paths=[Path(r['blend']) for r in json.loads((O/'masters.json').read_text())]+[D/'CSC_ALL_Modern_Roundabout_Kit.blend'];reports=[]
for path in paths:
 with suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
 r=validate_current_scene();assert r['automated_pass'],r['findings'];reports.append({'id':path.stem,'automated_pass':True,'counts':r['counts']})
(O/'final-saved-validation.json').write_text(json.dumps(reports,indent=2))
for name,fn in [('01 - Industrial paving','01_Stone'),('Review','02_First_building'),('03A - East destination','03A_East'),('03B - Southwest destination','03B_Southwest'),('04 - All routes','04_All_tarmac')]:
 s=bpy.data.scenes[name];s.render.filepath=str(O/(fn+'.png'));bpy.ops.render.render(write_still=True,scene=name)
print('SAVED_MASTERS_CHECKED_AND_RENDERED',len(reports))
