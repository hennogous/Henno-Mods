import bpy,sys,json,math,bmesh
from pathlib import Path
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[4];O=Path.home()/'Desktop/Codex/modern-bakery-v3-20261028';ART=Path.home()/'Desktop/Working Files/3D Art'
sys.path.insert(0,str(ROOT/'project/tools/blender'));from csc_scene_validation import suspend_csc_repairs
source=ART/'BAKERS/Bakery/modern/revision-02-concept-c/CSC_BAKERS_Bakery_Modern_2_Review.blend'
with suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
occupied={};windows=[]
for ob in bpy.data.scenes['Export'].objects:
 if ob.type!='MESH':continue
 if ob.get('module')=='Building':
  for p in ob.data.polygons:
   uv=sum((ob.data.uv_layers[0].data[k].uv for k in p.loop_indices),Vector((0,0)))/len(p.loop_indices)
   slot=int(uv.x*8)-4+4*int((1-uv.y)*8);occupied.setdefault(slot,[]).append(ob.name)
 if ob.get('module')=='Building' and ('Ground_Window' in ob.name or 'Entrance_Door' in ob.name):
  windows.append({'name':ob.name,'vertices':[list(ob.matrix_world@v.co) for v in ob.data.vertices]})
(O/'window-and-cells.json').write_text(json.dumps({'occupied':{k:sorted(set(v)) for k,v in occupied.items()},'windows':windows},indent=2));print(json.dumps({'occupied':list(occupied),'windows':windows}),flush=True)
# Historical comparison snapshot, normalized rigidly to the modern main-house frame.
with suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(ART/'Level 2/CSC_Level_2.blend'),load_ui=False,use_scripts=False)
s=bpy.data.scenes['Export'];bpy.context.window.scene=s
f=json.loads((Path.home()/'Desktop/Codex/modern-bakery-v2-20261028/historical-footprint.json').read_text());c=f['normalizing_translation'];T=Matrix.Translation(Vector((-c[0],-c[1],0)))@Matrix.Rotation(math.radians(f['normalizing_rotation_degrees']),4,'Z')
for ob in list(s.objects):
 if ob.type=='MESH':
  ob.data=ob.data.copy();ob.data.transform(T@ob.matrix_world);ob.matrix_world=Matrix.Identity(4)
  for m in list(ob.modifiers):ob.modifiers.remove(m)
  bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.0001,plane_co=(0,0,0),plane_no=(0,0,1),clear_inner=True);bm.to_mesh(ob.data);bm.free()
 else:s.objects.unlink(ob) if hasattr(s.objects,'unlink') else None
with bpy.data.libraries.load(str(source),link=False) as (src,dst):dst.objects=['Review_Key'];dst.worlds=['Review World'] if 'Review World' in src.worlds else [src.worlds[0]]
for o in dst.objects:
 if o:s.collection.objects.link(o)
if dst.worlds:s.world=dst.worlds[0]
cam=bpy.data.objects.new('ComparisonCamera',bpy.data.cameras.new('ComparisonCamera'));s.collection.objects.link(cam);s.camera=cam;target=Vector((-4,-15,53));cam.location=target+Vector((230,-300,230));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=185
for m in bpy.data.materials:
 if m.use_nodes:
  for n in m.node_tree.nodes:
   if n.type=='BSDF_PRINCIPLED':n.inputs['Emission Strength'].default_value=0
s.render.engine='CYCLES';s.cycles.samples=32;s.render.resolution_x=s.render.resolution_y=1100;s.render.resolution_percentage=100;s.render.film_transparent=True;s.view_settings.view_transform='Standard';s.view_settings.exposure=-.1;s.use_nodes=False
s.render.filepath=str(O/'review/historical.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(O/'Historical_Comparison_Snapshot.blend'))
