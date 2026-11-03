"""Change only room UV3 and image references in the current saved masters."""
import bpy,json,sys,hashlib,shutil
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[4];O=Path.home()/'Desktop/Codex/modern-interior-lighting-20261028';ART=Path.home()/'Desktop/Working Files/3D Art'
sys.path[:0]=[str(ROOT/'project/tools/blender'),str(ROOT/'project/tools/blender/scene_export')]
from csc_scene_validation import suspend_csc_repairs,validate_current_scene
import decode_blend as dec
sources=[ART/'Level 2/modern/revision-06-ae/CSC_Level_2_Modern.blend']+[ART/'BAKERS/Bakery/modern/revision-04-ae'/name for name in ('CSC_BAKERS_Bakery_Modern_Review.blend','CSC_BAKERS_Bakery_Modern_2_Review.blend')]
def fingerprint(ob):return ([list(v.co) for v in ob.data.vertices],[list(p.vertices) for p in ob.data.polygons],[list(d.uv) for d in ob.data.uv_layers[0].data],[list(d.uv) for d in ob.data.uv_layers[1].data],[list(r) for r in ob.matrix_world])
rows=[]
for source in sources:
 folder=O/'masters'/source.stem;folder.mkdir(parents=True,exist_ok=True);shutil.copy2(source,folder/'source-before.blend');shutil.copytree(source.parent/'textures',folder/'textures',dirs_exist_ok=True)
 for name in ('CSC_Atlas_Modern_B_BAKERS.png','CSC_Atlas_Modern_E_BAKERS.png'):shutil.copy2(O/'textures'/name,folder/'textures'/name)
 with suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
 export=bpy.data.scenes['Export'];before={ob.name:fingerprint(ob) for ob in export.objects if ob.type=='MESH'};changed=[]
 for ob in export.objects:
  if ob.type!='MESH' or 'Inset_Interior_' not in ob.name:continue
  assert ob.get('module')=='Building';ob.data=ob.data.copy()
  for poly in ob.data.polygons:
   coords=[ob.data.uv_layers[0].data[k].uv for k in poly.loop_indices];u=sum(p.x for p in coords)/len(coords);v=sum(p.y for p in coords)/len(coords);slot=int(u*8)-4+4*int((1-v)*8);target={11:8,12:9,15:10}[slot]
   sx=512+slot%4*128;sy=slot//4*128;dx=256+target%4*64;dy=target//4*64
   for k in poly.loop_indices:
    uv=ob.data.uv_layers[0].data[k].uv;a=(uv.x*1024-sx-2)/124;b=((1-uv.y)*1024-sy-2)/124
    ob.data.uv_layers[2].data[k].uv=((dx+2+a*60)/512,1-(dy+2+b*60)/512)
  changed.append(ob.name)
 assert len(changed)==3,(source,changed)
 assert all(fingerprint(export.objects[name])==value for name,value in before.items())
 for mat in bpy.data.materials:
  if not mat.use_nodes:continue
  for node in mat.node_tree.nodes:
   if node.type!='TEX_IMAGE' or not node.image:continue
   name=node.image.filepath.replace('\\','/').split('/')[-1]
   if name=='CSC_Atlas_Modern_E.png':name='CSC_Atlas_Modern_E_BAKERS.png'
   if (folder/'textures'/name).is_file():
    if node.image.packed_file:node.image.unpack(method='REMOVE')
    node.image.filepath='//textures/'+name
 path=folder/source.name;bpy.ops.wm.save_as_mainfile(filepath=str(path),relative_remap=False)
 with suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
 validation=validate_current_scene();(folder/'validation.json').write_text(json.dumps(validation,indent=2));assert validation['automated_pass']
 rows.append({'source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'prepared':str(path),'changed_room_objects':changed,'geometry_UV1_UV2_placements_exact':True})
 if source.stem=='CSC_Level_2_Modern':
  bpy.context.window.scene=bpy.data.scenes['Export'];bpy.context.view_layer.update();model={'asset_id':'CSC_Level_2_Modern','kind':'building','meshes':[dec.merge_meshes('CSC_Level_2_Modern',[dec.decode_mesh(ob,ob.matrix_world) for ob in bpy.context.scene.objects if ob.type=='MESH'])]}
  for mesh in model['meshes']:
   for m in mesh['materials']:m['external']='CSC_BAKERS_Modern'
   kept=[]
   for t in mesh['triangles']:
    a,b,c=[Vector(mesh['vertices'][k][:3]) for k in t[:3]]
    if (b-a).cross(c-a).length>1e-7:kept.append(t)
   mesh['triangles']=kept
  (O/'models').mkdir(exist_ok=True);(O/'models/CSC_Level_2_Modern.json').write_text(json.dumps(model))
(O/'authoring.json').write_text(json.dumps(rows,indent=2));(O/'masters.json').write_text(json.dumps([{'id':'CSC_Level_2_Modern','blend':rows[0]['prepared']}],indent=2));print('UV3_ONLY_PREPARED',flush=True)
