import bpy,json,sys,hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[4];O=Path.home()/'Desktop/Codex/modern-cafe-v1-20261029';sys.path.insert(0,str(ROOT/'project/tools/blender'))
from csc_scene_validation import suspend_csc_repairs,validate_current_scene
masters=json.loads((O/'masters.json').read_text());reports=[]
for rec in masters:
 p=Path(rec['blend'])
 with suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(p),load_ui=False,use_scripts=False)
 review=bpy.data.scenes['Review'];export=bpy.data.scenes['Export'];bpy.context.window.scene=review
 if rec['id'] not in ('CSC_Level_3_Modern','CSC_Level_2_Modern'):
  pts=[ob.matrix_world@v.co for ob in export.objects if ob.type=='MESH' for v in ob.data.vertices];lo=Vector([min(v[i] for v in pts) for i in range(3)]);hi=Vector([max(v[i] for v in pts) for i in range(3)]);target=(lo+hi)/2;cam=review.camera;cam.location=target+Vector((70,-110,70));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=max(hi-lo)*1.8
 bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(p))
 with suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(p),load_ui=False,use_scripts=False)
 result=validate_current_scene();assert result['automated_pass'],result['findings'];reports.append({'id':rec['id'],'saved_validation':True,'blend_sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
 if rec['id']=='CSC_Level_3_Modern':
  ob=bpy.data.objects['CSC_Fixed_L3_Historical_Silhouette'];pts=[ob.matrix_world@v.co for v in ob.data.vertices];bounds=[[min(v[i] for v in pts) for i in range(3)],[max(v[i] for v in pts) for i in range(3)]];source=json.loads((O/'inspection.json').read_text())['base'][0]['bounds'];assert max(abs(a-b) for row,src in zip(bounds,source) for a,b in zip(row,src))<.0001;reports[-1]['historical_bounds_unchanged']=bounds
(O/'final-saved-validation.json').write_text(json.dumps(reports,indent=2));print('FINAL_SOURCES_VALID',flush=True)
