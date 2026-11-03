"""Give each road/surface module a clean editable master and validate saved files."""
import bpy,sys,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];sys.path[:0]=[str(ROOT/'project/tools/blender'),str(ROOT/'project/tools/blender/scene_export')]
from csc_scene_validation import suspend_csc_repairs,validate_current_scene
import decode_blend as dec
O=Path.home()/'Desktop/Codex/Quarter-Roads-Modern/draft-03-roundabout'
D=Path.home()/'Desktop/Working Files/3D Art/Decals/CSC_ALL_Modern_Roads'
assert not list((D/'modules').glob('*.blend')), 'Initial packaging only: current module masters must be edited in place.'
kit=D/'CSC_ALL_Modern_Roundabout_Kit.blend';(D/'modules').mkdir(exist_ok=True)
records=json.loads((O/'masters.json').read_text());reports=[]
for record in records:
 with suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(kit),load_ui=False,use_scripts=False)
 ident=record['id'];source=ident.replace('CSC_Road_','CSC_Projection_');preview=bpy.data.objects[source.replace('CSC_Projection_','')];rig=bpy.data.objects['CSC_Roads_Static'];target=bpy.data.objects.get(source)
 if target is None:
  target=preview.copy();target.name=source;target.location.z=20;target['review_only']=False;target['export_role']='fixed_geometry';target['asset_class']='road_decal';target['decal_states']='Worked,Unworked'
 material=target.material_slots[0].material;me=target.data.copy();me.materials.clear();me.materials.append(material);target.data=me;preview.data=me
 for ob in [target,preview]:ob.material_slots[0].link='DATA';ob.material_slots[0].material=material
 for s in list(bpy.data.scenes):
  if s.name not in ['Review','Export']:bpy.data.scenes.remove(s)
 for name,objects in [('Export',[target,rig]),('Review',[preview,rig])]:
  scene=bpy.data.scenes[name]
  for c in list(scene.collection.children):scene.collection.children.unlink(c)
  c=bpy.data.collections.new(ident+'_'+name);scene.collection.children.link(c)
  for ob in objects:c.objects.link(ob)
  scene['asset_id']=ident
  if name=='Review':scene.collection.children.link(bpy.data.collections['REVIEW - ground and lights'])
 for img in bpy.data.images:
  if img.source=='FILE':img.filepath='//../textures/'+Path(bpy.path.abspath(img.filepath)).name
 bpy.context.window.scene=bpy.data.scenes['Review']
 readme=bpy.data.texts['START HERE'];readme.clear();readme.write('Independent road decal module. Review is the ground-level preview; Export contains the matching projection mesh at Z20, static rig and no context. Edit shared mesh data to keep projection and preview synchronized. UV1/2/3 use the paired 512px atlases. Register DecalGeometry with Worked/Unworked visibility. Native projection/material/terrain appearance still requires integration testing. Placement stays in Quarter coordinates so the modules align when attached without offsets.\n')
 path=D/'modules'/(ident+'.blend');bpy.ops.wm.save_as_mainfile(filepath=str(path),relative_remap=False)
 with suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
 r=validate_current_scene();assert r['automated_pass'],(ident,r['findings']);reports.append({'id':ident,'automated_pass':True,'counts':r['counts']});record['blend']=str(path)
 target=bpy.data.objects[source];m=dec.decode_mesh(target,target.matrix_world);m['name']=ident
 for material in m['materials']:material['external']=material['name']
 model={'asset_id':ident,'kind':'decal','meshes':[m]};(O/'models'/(ident+'.json')).write_text(json.dumps(model))
# The layout master opens on first-building state; its clean Export is stone base.
with suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(kit),load_ui=False,use_scripts=False)
s=bpy.data.scenes['Export']
for c in list(s.collection.children):s.collection.children.unlink(c)
c=bpy.data.collections.new('EXPORT - complete Industrial base');s.collection.children.link(c);c.objects.link(bpy.data.objects['CSC_Roads_Static'])
for ob in bpy.data.objects:
 if ob.name.startswith('CSC_Projection_') and ob.name.endswith('_Industrial'):c.objects.link(ob)
bpy.data.texts['START HERE'].clear();bpy.data.texts['START HERE'].write('Review = first-building surface state. 01 = all stone. 03A/03B = independent optional building branches. 04 = all tarmac. Export = complete Industrial stone base only. For modular surface changes use the separately validated files in modules/. Both surface variants remain available in their named collections. Ground preview and projection share mesh data. Use mesh edits to synchronize them. Geometry retains Quarter coordinates; projection lift20 is a candidate, not verified in game. All 512px B/H/FOW/S textures are external in textures/. No runtime registrations modified.\n')
bpy.context.window.scene=bpy.data.scenes['Review'];bpy.ops.wm.save_as_mainfile(filepath=str(kit))
with suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(kit),load_ui=False,use_scripts=False)
r=validate_current_scene();assert r['automated_pass'];reports.append({'id':kit.stem,'automated_pass':True,'counts':r['counts']})
(O/'masters.json').write_text(json.dumps(records,indent=2));(O/'final-saved-validation.json').write_text(json.dumps(reports,indent=2));print('ALL_SAVED_MASTERS_PASS',len(reports))
