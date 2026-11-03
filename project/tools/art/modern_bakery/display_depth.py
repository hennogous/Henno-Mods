"""Scope the bread-display depth correction to its master and native geometry."""
import json,sys,hashlib,shutil,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(Path(__file__).parent))
import placement_refinement as p
O=Path.home()/'Desktop/Codex/modern-bakery-display-depth-20261029';p.O=O
A=Path.home()/'Desktop/Working Files/3D Art';SRC=A/'BAKERS/Bakery/modern/revision-04-ae';ID='CSC_BAKERS_Bread_Display_Modern'
def dump(path,data):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(data,indent=2))
def prepare():
 p.prepare();MOD=ROOT/'Civ Supply Chains'
 dump(O/'baseline.json',{str(q.relative_to(MOD)):hashlib.sha256(q.read_bytes()).hexdigest() for f in ('Assets','Geometries','Textures','Materials','ArtDefs','XLPs') for q in (MOD/f).iterdir() if q.is_file()})
def inspect():
 import bpy
 p.measure();sys.path.insert(0,str(ROOT/'project/tools/blender'));from csc_scene_validation import suspend_csc_repairs
 with suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(SRC/(ID+'.blend')),load_ui=False,use_scripts=False)
 rows=[]
 for o in bpy.data.scenes['Export'].objects:
  if o.type!='MESH':continue
  pts=[o.matrix_world@v.co for v in o.data.vertices]
  rows.append({'name':o.name,'bounds':[[min(v[i] for v in pts) for i in range(3)],[max(v[i] for v in pts) for i in range(3)]],'matrix':[list(r) for r in o.matrix_world],'module':o.get('module'),'microAO_slot':o.get('microAO_slot'),'material':[m.name for m in o.data.materials]})
 dump(O/'source-inspection.json',rows);print(json.dumps(rows,indent=2))
def author():
 import bpy
 from mathutils import Vector
 sys.path[:0]=[str(ROOT/'project/tools/blender'),str(ROOT/'project/tools/blender/scene_export')]
 from csc_scene_validation import suspend_csc_repairs,validate_current_scene
 import decode_blend as dec
 facts=json.loads((O/'measurements.json').read_text());hist=facts['CSC_BAKERS_Bakery_2'];table=next(r for r in hist if '/DIS_COM_Table/' in r['path']);stand=next(r for r in hist if '/CSC_ALL_Stand/' in r['path']);modern=next(r for r in facts['CSC_BAKERS_Bakery_Modern'] if '/CSC_Attach_Display/' in r['path'])
 scale=modern['matrix'][2][2];counter_depth=(table['frame'][1][1]-table['frame'][0][1])/scale
 total_depth=(max(table['frame'][1][1],stand['frame'][1][1])-min(table['frame'][0][1],stand['frame'][0][1]))/scale
 with suspend_csc_repairs():
  source=SRC/(ID+'.blend');bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False);scene=bpy.data.scenes['Export'];review=bpy.data.scenes['Review'];bpy.context.window.scene=scene;bpy.context.view_layer.update();obs=[o for o in scene.objects if o.type=='MESH'];mat=obs[0].data.materials[0]
  before={o.name:[list(v.co) for v in o.data.vertices] for o in obs};new=[]
  for ob in obs:
   ob.data=ob.data.copy()
   if 'Upright' in ob.name:
    cy=sum(v.co.y for v in ob.data.vertices)/len(ob.data.vertices);delta=-(counter_depth-14) if cy<0 else 0
    for v in ob.data.vertices:v.co.y+=delta
   elif ob.get('microAO_slot'):
    # Add a second row of unchanged painted trays; do not elongate the loaves.
    rear_center=7-7;front_center=7-counter_depth+7
    for v in ob.data.vertices:v.co.y+=front_center
    dup=ob.copy();dup.data=ob.data.copy();dup.name=ob.name+'_Rear';scene.collection.objects.link(dup);review.collection.objects.link(dup)
    for v in dup.data.vertices:v.co.y+=rear_center-front_center
    new.append(dup)
   else:
    rear=8 if 'Canopy' in ob.name else 7;olddepth=18 if 'Canopy' in ob.name else 14;depth=total_depth if 'Canopy' in ob.name else counter_depth
    for v in ob.data.vertices:v.co.y=rear+(v.co.y-rear)*depth/olddepth
   assert all(abs(v.co.x-old[0])<1e-6 and abs(v.co.z-old[2])<1e-6 for v,old in zip(ob.data.vertices,before[ob.name]))
  obs+=new
  # Link current published maps, preserving the oven's latest full-glass emission.
  lib=A/'Textures/CSC_Props_Modern/Current'
  for node in mat.node_tree.nodes:
   if node.type=='TEX_IMAGE' and node.image:
    path=lib/'textures'/Path(node.image.filepath.replace('\\','/')).name
    if path.is_file():node.image=bpy.data.images.load(str(path),check_existing=False);node.image.colorspace_settings.name='sRGB' if node.label in ('B','E') or node.name in ('B','E') else 'Non-Color'
  bpy.ops.object.select_all(action='DESELECT')
  for ob in obs:ob.hide_set(False);ob.hide_render=False;ob.select_set(True);ob.data.uv_layers.active_index=1;ob.data.uv_layers[1].active_render=True
  bpy.context.view_layer.objects.active=obs[0];bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=math.radians(75),island_margin=.018,area_weight=.8,scale_to_bounds=True);bpy.ops.object.mode_set(mode='OBJECT')
  ns=mat.node_tree.nodes;ls=mat.node_tree.links;bs=next(n for n in ns if n.type=='BSDF_PRINCIPLED');node=next(n for n in ns if n.type=='TEX_IMAGE' and (n.label or n.name)=='AO');old=node.image;im=bpy.data.images.new('Display_Depth_AO',width=768,height=768,alpha=False);im.colorspace_settings.name='Non-Color';node.image=im;ns.active=node;restore=[(l.from_socket,l.to_socket) for slot in ('Base Color','Normal') for l in bs.inputs[slot].links]
  for slot in ('Base Color','Normal'):
   for l in list(bs.inputs[slot].links):ls.remove(l)
  scene.render.engine='CYCLES';scene.cycles.samples=128;scene.render.bake.margin=8;bpy.ops.object.bake(type='AO',uv_layer='UV2');(O/'bakes').mkdir(exist_ok=True);im.filepath_raw=str(O/'bakes/Display.png');im.file_format='PNG';im.save();node.image=old
  for a,c in restore:ls.new(a,c)
  micro=[]
  for ob in obs:
   for d in ob.data.uv_layers[1].data:d.uv=((516+d.uv.x*248)/2048,1-(764-d.uv.y*248)/2048)
   ob.data.uv_layers.active_index=0;ob.data.uv_layers[0].active_render=True
   if ob.get('microAO_slot'):
    ob.data.calc_loop_triangles()
    for tr in ob.data.loop_triangles:
     uvs=[list(ob.data.uv_layers[0].data[k].uv) for k in tr.loops]
     if int(sum(u[1] for u in uvs)/3*8)==3 and int(sum(u[0] for u in uvs)/3*8)>=4:micro.append({'slot':ob['microAO_slot'],'UV1':uvs,'UV2':[list(ob.data.uv_layers[1].data[k].uv) for k in tr.loops]})
  dump(O/'microAO-triangles.json',micro)
  folder=O/'masters'/ID;folder.mkdir(parents=True,exist_ok=True);shutil.copytree(SRC/'textures',folder/'textures',dirs_exist_ok=True)
  for q in (lib/'textures').glob('*.png'):shutil.copy2(q,folder/'textures'/q.name)
  bpy.context.preferences.filepaths.save_version=0;path=folder/(ID+'.blend');bpy.ops.wm.save_as_mainfile(filepath=str(path),relative_remap=False)
  bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False);bpy.context.window.scene=bpy.data.scenes['Export'];val=validate_current_scene();dump(folder/'validation.json',val);assert val['automated_pass'],val['findings']
  obs=[ob for ob in bpy.context.scene.objects if ob.type=='MESH'];model={'asset_id':ID,'kind':'prop','meshes':[dec.merge_meshes(ID,[dec.decode_mesh(ob,ob.matrix_world) for ob in obs])]}
  for mesh in model['meshes']:
   for material in mesh['materials']:material['external']='CSC_Props_Modern_01'
  dump(O/'models'/(ID+'.json'),model);rows=[{'source':str(source),'before':hashlib.sha256(source.read_bytes()).hexdigest(),'prepared':str(path)}]
  # Synchronize only display geometry in the optional combined review files;
  # their old scene placements remain proposals, never exported back to AE.
  for name in ('CSC_BAKERS_Bakery_Modern_Review','CSC_BAKERS_Bakery_Modern_2_Review'):
   src=SRC/(name+'.blend');bpy.ops.wm.open_mainfile(filepath=str(src),load_ui=False,use_scripts=False);scene=bpy.data.scenes['Export'];review=bpy.data.scenes['Review'];bpy.context.window.scene=scene
   existing=[ob for ob in scene.objects if ob.type=='MESH' and ob.get('module')=='Display'];transform=existing[0].matrix_world.copy();rig=existing[0].parent
   for ob in existing:bpy.data.objects.remove(ob,do_unlink=True)
   with bpy.data.libraries.load(str(path),link=False) as (a,c):c.objects=[x for x in a.objects if x.startswith('CSC_Fixed_')]
   for ob in c.objects:
    scene.collection.objects.link(ob);review.collection.objects.link(ob);ob.parent=rig;ob.matrix_world=transform
    for modifier in ob.modifiers:
     if modifier.type=='ARMATURE':modifier.object=rig
   dst=O/'masters'/name/(name+'.blend');dst.parent.mkdir(parents=True,exist_ok=True);shutil.copytree(SRC/'textures',dst.parent/'textures',dirs_exist_ok=True)
   for q in (lib/'textures').glob('*.png'):shutil.copy2(q,dst.parent/'textures'/q.name)
   bpy.ops.wm.save_as_mainfile(filepath=str(dst),relative_remap=False);rows.append({'source':str(src),'before':hashlib.sha256(src.read_bytes()).hexdigest(),'prepared':str(dst)})
  dump(O/'authoring.json',rows);dump(O/'masters.json',[{'id':ID,'blend':str(path)}]);dump(O/'proportions.json',{'placed_width_unchanged':modern['frame'][1][0]-modern['frame'][0][0],'placed_depth_before':modern['frame'][1][1]-modern['frame'][0][1],'placed_depth_after':total_depth*scale,'historical_table_depth':counter_depth*scale,'placed_height_unchanged':modern['frame'][1][2]-modern['frame'][0][2],'source_counter_depth':counter_depth,'source_total_depth':total_depth,'AE_uniform_scale_unchanged':scale,'rear_edge_fixed':True,'painted_tray_dimensions_unchanged':True,'tray_count':18})
  print('DEPTH_AUTHORING_COMPLETE',total_depth*scale,counter_depth*scale,flush=True)
def finalize_staged():
 import bpy
 sys.path.insert(0,str(ROOT/'project/tools/blender'));from csc_scene_validation import suspend_csc_repairs,validate_current_scene
 result=[]
 with suspend_csc_repairs():
  for row in json.loads((O/'authoring.json').read_text()):
   path=Path(row['prepared']);bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
   for im in bpy.data.images:
    fn=Path(im.filepath.replace('\\','/')).name
    if fn.startswith('CSC_Props_Modern_01_') and (path.parent/'textures'/fn).is_file():
     if im.packed_file:im.unpack(method='REMOVE')
     im.filepath='//textures/'+fn;im.reload()
   bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(path),relative_remap=False)
   bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False);val=validate_current_scene();dump(path.parent/'validation.json',val);assert val['automated_pass'],val['findings'];result.append({'source':row['source'],'saved_validation':val['status'],'automated_pass':True})
 dump(O/'saved-master-validation.json',result);print('SAVED_MASTERS_VALIDATED',flush=True)
if __name__=='__main__':globals()[sys.argv[-1]]()
