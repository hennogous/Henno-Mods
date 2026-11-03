"""Candidate-only Bakery migration to the same dedicated interior atlas as Café."""
import bpy,json,sys,shutil,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];A=Path.home()/'Desktop/Working Files/3D Art';O=Path.home()/'Desktop/Codex/modern-cafe-v1-20261029'
sys.path[:0]=[str(ROOT/'project/tools/blender'),str(ROOT/'project/tools/blender/scene_export')]
from csc_scene_validation import suspend_csc_repairs,validate_current_scene
import decode_blend as dec
sources=[(A/'Level 2/modern/revision-06-ae/CSC_Level_2_Modern.blend',A/'Level 2/modern/revision-07-interior-atlas-preview')]+[(A/'BAKERS/Bakery/modern/revision-04-ae'/fn,A/'BAKERS/Bakery/modern/revision-05-interior-atlas-preview') for fn in ('CSC_BAKERS_Bakery_Modern_Review.blend','CSC_BAKERS_Bakery_Modern_2_Review.blend')]
def fingerprint(ob,uv=True):return hashlib.sha256(repr(([tuple(v.co) for v in ob.data.vertices],[tuple(p.vertices) for p in ob.data.polygons],[list(r) for r in ob.matrix_world],[[tuple(d.uv) for d in l.data] for l in ob.data.uv_layers] if uv else [tuple(d.uv) for d in ob.data.uv_layers[1].data])).encode()).hexdigest()
records=[]
for src,folder in sources:
 folder.mkdir(parents=True,exist_ok=True);shutil.copytree(src.parent/'textures',folder/'textures',dirs_exist_ok=True)
 for p in (O/'textures').glob('CSC_Interiors*'):shutil.copy2(p,folder/'textures'/p.name)
 sha=hashlib.sha256(src.read_bytes()).hexdigest()
 with suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(src),load_ui=False,use_scripts=False)
 obs=[o for o in bpy.data.scenes['Export'].objects if o.type=='MESH'];before={o.name:fingerprint(o,'Inset_Interior_' not in o.name) for o in obs}
 with bpy.data.libraries.load(str(A/'Level 3/modern/revision-01-garden/CSC_Level_3_Modern.blend'),link=False) as (a,b):b.materials=['CSC_BAKERS_Interiors_Modern']
 mat=b.materials[0];changed=[]
 for ob in obs:
  if 'Inset_Interior_' not in ob.name:continue
  ob.data=ob.data.copy();ob.data.materials.clear();ob.data.materials.append(mat)
  for p in ob.data.polygons:
   uv=[ob.data.uv_layers[0].data[k].uv for k in p.loop_indices];cx=sum(v.x for v in uv)/len(uv);cy=sum(v.y for v in uv)/len(uv);old=int(cx*8)-4+int((1-cy)*8)*4;slot={11:0,12:1,15:2}[old];sx=512+old%4*128;sy=old//4*128
   for k in p.loop_indices:
    u,v=ob.data.uv_layers[0].data[k].uv;u=(u*1024-sx-2)/124;v=((1-v)*1024-sy-2)/124;new=((slot%4*256+6+u*244)/1024,1-(slot//4*256+6+v*244)/1024);ob.data.uv_layers[0].data[k].uv=new;ob.data.uv_layers[2].data[k].uv=new
  ob['interior_atlas']='CSC_Interiors_Modern';ob['furnishing_geometry']=False;changed.append(ob.name)
 assert len(changed)==3
 assert all(fingerprint(o,'Inset_Interior_' not in o.name)==before[o.name] for o in obs)
 for img in bpy.data.images:
  if img.source=='FILE' and img.filepath:
   name=img.filepath.replace('\\','/').split('/')[-1]
   if (folder/'textures'/name).is_file():
    if img.packed_file:img.unpack(method='REMOVE')
    img.filepath=str(folder/'textures'/name);img.reload()
 path=folder/src.name;bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(path))
 with suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
 val=validate_current_scene();(folder/(src.stem+'-validation.json')).write_text(json.dumps(val,indent=2));assert val['automated_pass'],val['findings'];assert hashlib.sha256(src.read_bytes()).hexdigest()==sha
 records.append({'source':str(src),'candidate':str(path),'unchanged_source_sha256':sha,'changed_room_objects':changed,'all_geometry_UV2_and_nonroom_data_identical':True,'saved_validation':True})
 if src.stem=='CSC_Level_2_Modern':
  bpy.context.window.scene=bpy.data.scenes['Export'];bpy.context.view_layer.update();model={'asset_id':src.stem,'kind':'building','meshes':[dec.merge_meshes(src.stem,[dec.decode_mesh(o,o.matrix_world) for o in bpy.context.scene.objects if o.type=='MESH'])]}
  for m in model['meshes']:
   for ma in m['materials']:ma['external']='CSC_BAKERS_Interiors_Modern' if 'Interiors' in ma['name'] else 'CSC_BAKERS_Modern'
  (O/'models'/(src.stem+'.json')).write_text(json.dumps(model));masters=json.loads((O/'masters.json').read_text());masters=[r for r in masters if r['id']!=src.stem];masters.append({'id':src.stem,'blend':str(path)});(O/'masters.json').write_text(json.dumps(masters,indent=2))
(O/'interior-migration.json').write_text(json.dumps(records,indent=2))
library=A/'Textures/CSC_Interiors_Modern/Candidates/2026-10-29_Garden_v001';(library/'textures').mkdir(parents=True,exist_ok=True)
for p in (O/'textures').glob('CSC_Interiors*'):shutil.copy2(p,library/'textures'/p.name)
plan=json.loads((O/'atlas-plan.json').read_text());plan['interior_migration']=records;plan['publication']='Candidate; no Current/runtime texture changes';(library/'atlas-plan.json').write_text(json.dumps(plan,indent=2))
print('BAKERY_INTERIORS_MIGRATED_IN_THREE_CANDIDATE_MASTERS',flush=True)
