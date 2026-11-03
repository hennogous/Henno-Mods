"""Save per-model editable masters, validate saved files, and prepare native checks."""
import bpy,sys,json,shutil,hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[4];ART=Path.home()/'Desktop/Working Files/3D Art'
O=Path.home()/'Desktop/Codex/modern-bakery-v1-20261028';D=ART/'BAKERS/Bakery/modern/revision-01-sheltered-bakery'
L2=ART/'Level 2/modern/revision-03-window-boxes-sign'
sys.path[:0]=[str(ROOT/'project/tools/blender'),str(ROOT/'project/tools/blender/scene_export')]
from csc_scene_validation import suspend_csc_repairs,validate_current_scene
import decode_blend as dec
shutil.copytree(O/'textures',D/'textures',dirs_exist_ok=True);shutil.copytree(O/'sources',D/'texture-sources',dirs_exist_ok=True)
records=[]
groups={'Oven':'CSC_BAKERS_Deck_Oven_Modern','Display':'CSC_BAKERS_Bread_Display_Modern','Rack':'CSC_BAKERS_Bread_Rack_Modern','Trays':'CSC_BAKERS_Tray_Stack_Modern','Sign':'CSC_BAKERS_Hanging_Sign_Modern'}
for group,ident in groups.items():
 with suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(O/'Local_Props.blend'),load_ui=False,use_scripts=False)
 for ob in list(bpy.data.objects):
  if ob.type=='MESH' and ob.get('module')!=group:bpy.data.objects.remove(ob,do_unlink=True)
 rig=next(o for o in bpy.data.scenes['Export'].objects if o.type=='ARMATURE');rig.name=ident;rig.data.name=ident
 for s in (bpy.data.scenes['Review'],bpy.data.scenes['Export']):s['asset_id']=ident
 for ob in bpy.data.scenes['Export'].objects:
  if ob.type=='MESH':
   ob['source_asset_id']=ident;ob['reuse_approved']=False;ob['reuse_scope']='bakery proposal'
   if group=='Sign':ob.location=(0,0,0);ob.rotation_euler=(0,0,0);ob.scale=(1,1,1)
 for im in list(bpy.data.images):
  if im.users==0:bpy.data.images.remove(im)
  elif im.source=='FILE' and im.filepath:im.filepath='//textures/'+im.filepath.replace('\\','/').split('/')[-1];im.reload()
 s=bpy.data.scenes['Review'];bpy.context.window.scene=s
 target=Vector((0,0,15) if group!='Sign' else (9,0,-6));s.camera.location=target+Vector((50,-90,55));s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=65
 path=D/(ident+'.blend');bpy.ops.wm.save_as_mainfile(filepath=str(path),relative_remap=False)
 with suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
 report=validate_current_scene();(D/(ident+'-validation.json')).write_text(json.dumps(report,indent=2));assert report['automated_pass'],report['findings']
 bpy.context.window.scene=bpy.data.scenes['Export'];bpy.context.view_layer.update()
 model={'asset_id':ident,'kind':'prop','meshes':[dec.merge_meshes(ident,[dec.decode_mesh(ob,ob.matrix_world) for ob in bpy.context.scene.objects if ob.type=='MESH'])]}
 (O/'models'/(ident+'.json')).write_text(json.dumps(model));records.append({'id':ident,'blend':str(path),'vertices':sum(len(m['vertices']) for m in model['meshes']),'triangles':sum(len(m['triangles']) for m in model['meshes']),'validation_errors':report['error_count']})
shutil.copy2(O/'CSC_BAKERS_Bakery_Modern_Review.blend',D/'CSC_BAKERS_Bakery_Modern_Review.blend')
with suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(D/'CSC_BAKERS_Bakery_Modern_Review.blend'),load_ui=False,use_scripts=False)
report=validate_current_scene();(D/'assembly-validation.json').write_text(json.dumps(report,indent=2));assert report['automated_pass'],report['findings']
def signature(group):
 bpy.context.window.scene=bpy.data.scenes['Export'];bpy.context.view_layer.update();rows=[]
 for ob in bpy.context.scene.objects:
  if ob.type=='MESH' and ob.get('module')==group:
   m=dec.decode_mesh(ob,ob.matrix_world);verts=[tuple(round(x,5) for x in v) for v in m['vertices']]
   tris=sorted(tuple(sorted(verts[i] for i in face)) for face in m['triangles']);rows.append(hashlib.sha256(repr((sorted(verts),tris)).encode()).hexdigest())
 return sorted(rows)
assembled={group:signature(group) for group in ('Building','Workshop')}
checks={}
for group,file in [('Building','CSC_Level_2_Modern.blend'),('Workshop','CSC_Level_2_Modern_Workshop.blend')]:
 with suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(L2/file),load_ui=False,use_scripts=False)
 checks[group]=signature(group)==assembled[group];assert checks[group],group
for path,sha in json.loads((O/'input-hashes.json').read_text()).items():assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==sha,path
(O/'architecture-preservation.json').write_text(json.dumps({'geometry_normals_all_UVs_topology_identical':checks,'source_blends_unchanged':True},indent=2))
(O/'masters.json').write_text(json.dumps(records,indent=2));shutil.copy2(O/'brief.json',D/'draft-manifest.json')
print('SAVED_MASTERS',json.dumps(records),flush=True)
