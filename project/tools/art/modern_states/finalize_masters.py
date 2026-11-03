"""Save validated editable masters beside current artwork, linked to shared Current."""
import bpy,sys,json,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT/'project/tools/blender'))
from csc_scene_validation import suspend_csc_repairs,validate_current_scene
ART=Path.home()/'Desktop/Working Files/3D Art';OUT=Path.home()/'Desktop/Codex/modern-l1-states-20261028'
targets={'CSC_Level_1_S_Modern_CON+PIL':ART/'Level 1/modern/CON+PIL/revision-01','CSC_BAKERS_Mill_Silo_Modern_CON+PIL':ART/'BAKERS/Wind Mill/modern/CON+PIL/revision-01','CSC_BAKERS_Water_Mill_Modern_CON+PIL':ART/'BAKERS/Water Mill/modern/CON+PIL/revision-01'}
report=[]
with suspend_csc_repairs():
 for ident,folder in targets.items():
  source=OUT/'masters'/ident/(ident+'.blend');dest=folder/(ident+'.blend');assert not dest.exists();folder.mkdir(parents=True,exist_ok=True)
  bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False);bpy.context.window.scene=bpy.data.scenes['Export']
  for im in bpy.data.images:
   if not im.filepath:continue
   name=Path(im.filepath).name
   if name.startswith('CSC_Atlas_Modern') or name.startswith('CSC_Props_Modern_01'):
    lib='CSC_Buildings_Modern' if name.startswith('CSC_Atlas_Modern') else 'CSC_Props_Modern';p=ART/'Textures'/lib/'Current/textures'/name
    if p.exists():im.filepath=str(p);im.reload()
  for o in bpy.context.scene.objects:
   if o.type=='MESH' and o.get('state_group')=='WindTieIn':o.hide_render=True;o.hide_set(True)
  bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(dest),relative_remap=False)
  bpy.ops.wm.open_mainfile(filepath=str(dest),load_ui=False,use_scripts=False);bpy.context.window.scene=bpy.data.scenes['Export'];validation=validate_current_scene();assert validation['automated_pass'];(folder/'validation.json').write_text(json.dumps(validation,indent=2))
  shutil.copy2(OUT/'staged/CN6'/(ident+'.cn6'),folder/(ident+'.cn6'));shutil.copy2(OUT/'masters'/ident/'timber-UV-audit.json',folder/'timber-UV-audit.json')
  report.append({'asset':ident,'blend':str(dest),'validation':validation['status'],'warnings':validation['warning_count']})
(OUT/'final-masters.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
