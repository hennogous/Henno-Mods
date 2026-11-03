"""Candidate assembly uses native historical context; never feeds back into saved ASTs."""
import bpy,json,sys,math,shutil,bmesh
from pathlib import Path
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[4];A=Path.home()/'Desktop/Working Files/3D Art';O=Path.home()/'Desktop/Codex/modern-cafe-v1-20261029';D=A/'BAKERS/Cafe/modern/revision-01-garden'
sys.path.insert(0,str(ROOT/'project/tools/blender'));from csc_scene_validation import suspend_csc_repairs
from ae_asset_render_blender import Builder
with suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(O/'Local_Models.blend'),load_ui=False,use_scripts=False)
review=bpy.data.scenes['Review'];bpy.context.window.scene=review;R=Matrix.Rotation(math.radians(-28.26),4,'Z')
positions={'Counter':(146,123,0),'Parasol':(63,90,0),'Valance':(162.6,137.8,22.8),'Van':(145,48,0)}
for ob in list(review.objects):
 if ob.type=='MESH' and ob.get('module') in positions:
  ob.matrix_world=R@Matrix.Translation(positions[ob['module']])
  if ob.get('module')=='Valance':ob.matrix_world=ob.matrix_world@Matrix.Rotation(math.pi/2,4,'Z')
for image in bpy.data.images:
 if image.source=='FILE' and image.filepath:
  name=image.filepath.replace('\\','/').split('/')[-1]
  if (D/'textures'/name).is_file():image.filepath=str(D/'textures'/name);image.reload()
job=json.loads(next((O/'historical').rglob('job.json')).read_text());b=Builder(job,'sv');b.assemble(job['root'],root=True);review.name='Review'
context=[];omitted=[]
for ob,rec in zip(b.objects,b.mapping):
 if rec['root'] or rec['asset'] in ('CSC_ALL_Workbench_Narrow','DIS_PRD_Barrel','DIS_COM_Crate','CSC_BAKERS_Flour_Closed'):
  omitted.append(rec);bpy.data.objects.remove(ob,do_unlink=True);continue
 ob['review_only']=True;ob['reuse_reference']='Saved historical Cafe AST';context.append(rec)
 # Native source geometry remains a reference; no copy enters any export master.
pts=[{'asset':ob.get('ae_asset'),'bounds':[[min((R.inverted()@ob.matrix_world@v.co)[i] for v in ob.data.vertices) for i in range(3)],[max((R.inverted()@ob.matrix_world@v.co)[i] for v in ob.data.vertices) for i in range(3)]]} for ob in review.objects if ob.type=='MESH' and ob.get('ae_asset')]
(O/'context-bounds.json').write_text(json.dumps(pts,indent=2));(O/'native-context.json').write_text(json.dumps({'reused':context,'omitted_in_proposal':omitted,'placements':positions},indent=2))
# Clip foundations for pixels only; save full skirts in both editable review files.
uncut={}
for ob in review.objects:
 if ob.type=='MESH' and ob.get('module')=='Building' and not ob.get('painted_interior'):
  uncut[ob.name]=ob.data
  ob.data=ob.data.copy();bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=(0,0,0),plane_no=(0,0,1),clear_inner=True);bm.to_mesh(ob.data);bm.free()
def save_review(path):
 clipped={}
 for name,mesh in uncut.items():clipped[name]=bpy.data.objects[name].data;bpy.data.objects[name].data=mesh
 bpy.ops.wm.save_as_mainfile(filepath=str(path))
 for name,mesh in clipped.items():bpy.data.objects[name].data=mesh
review['asset_id']='CSC_BAKERS_Cafe_Modern_2';review['proposal_only']=True;review['runtime_installation']='not installed';review['placement_authority']='Proposal; saved historical garden references; no live AST changed'
review.use_nodes=False;review.render.image_settings.media_type='IMAGE';review.render.image_settings.file_format='PNG';review.render.image_settings.color_mode='RGBA';review.render.image_settings.color_depth='8';review.cycles.samples=40
review.camera.data.ortho_scale=225;target=R@Vector((100,119,48));review.camera.location=target+R.to_3x3()@Vector((125,-230,170));review.camera.rotation_euler=(target-review.camera.location).to_track_quat('-Z','Y').to_euler()
path=D/'CSC_BAKERS_Cafe_Modern_2_Review.blend';save_review(path);review.render.filepath=str(O/'review/Cafe_Alternate_Day.png');bpy.ops.render.render(write_still=True)
for ob in review.objects:
 if ob.get('module')=='Van':ob.hide_render=True;ob.hide_set(True)
review['asset_id']='CSC_BAKERS_Cafe_Modern';save_review(D/'CSC_BAKERS_Cafe_Modern_Review.blend');review.render.filepath=str(O/'review/Cafe_Standard_Day.png');bpy.ops.render.render(write_still=True)
# Lighting demonstrations are disposable; never save nighttime settings in masters.
review.world=review.world.copy();review.world.node_tree.nodes['Background'].inputs[0].default_value=(.28,.4,.65,1);review.world.node_tree.nodes['Background'].inputs[1].default_value=.15
sun=bpy.data.objects['Review_Key'];sun.data.energy=.4;sun.data.color=(.55,.66,1)
for ma in bpy.data.materials:
 if ma.use_nodes and ma.name.startswith(('CSC_BAKERS_Modern','CSC_BAKERS_Interiors_Modern')):
  for node in ma.node_tree.nodes:
   if node.type=='BSDF_PRINCIPLED':node.inputs['Emission Strength'].default_value=1
review.render.filepath=str(O/'review/Cafe_Standard_Night.png');bpy.ops.render.render(write_still=True)
for ob in review.objects:
 if ob.get('module')=='Van':ob.hide_render=False;ob.hide_set(False)
review.render.filepath=str(O/'review/Cafe_Alternate_Night.png');bpy.ops.render.render(write_still=True)
print('CAFE_REVIEWS_RENDERED',flush=True)
