"""Publish the editable saved master with Current texture links, then reload-check it."""
import bpy,json,sys,shutil,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT/'project/tools/blender'))
from csc_scene_validation import suspend_csc_repairs,validate_current_scene
A=Path.home()/'Desktop/Working Files/3D Art';O=Path.home()/'Desktop/Codex/modern-l2-states-20261029';ID='CSC_Level_2_Modern_CON+PIL'
source=O/'masters'/ID/(ID+'.blend');folder=A/'Level 2/modern/CON+PIL/revision-01';dest=folder/(ID+'.blend')
assert json.loads((O/'publication-report.json').read_text())['installed'];assert not dest.exists();folder.mkdir(parents=True,exist_ok=True)
with suspend_csc_repairs():
 bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False);bpy.context.window.scene=bpy.data.scenes['Export']
 for im in bpy.data.images:
  if not im.filepath:continue
  name=Path(im.filepath).name
  if name.startswith('CSC_Atlas_Modern'):
   p=A/'Textures/CSC_Buildings_Modern/Current/textures'/name
   if p.exists():im.filepath=str(p);im.reload()
 bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(dest),relative_remap=False)
 bpy.ops.wm.open_mainfile(filepath=str(dest),load_ui=False,use_scripts=False);bpy.context.window.scene=bpy.data.scenes['Export'];validation=validate_current_scene();assert validation['automated_pass'];(folder/'validation.json').write_text(json.dumps(validation,indent=2))
 shutil.copy2(O/'staged/CN6'/(ID+'.cn6'),folder/(ID+'.cn6'));shutil.copy2(O/'masters'/ID/'timber-UV-audit.json',folder/'timber-UV-audit.json')
 report={'blend':str(dest),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'native_source':str(folder/(ID+'.cn6')),'validation':validation['status'],'vertices':validation['counts']['main_vertices'],'no_extension':True}
 (O/'final-master.json').write_text(json.dumps(report,indent=2));print('FINAL_MASTER_SAVED_RELOADED',report,flush=True)
