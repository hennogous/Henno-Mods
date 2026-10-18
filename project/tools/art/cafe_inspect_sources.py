"""Read source geometry and reuse candidates; write only a review inventory."""
import bpy, json, sys, math
from pathlib import Path
from mathutils import Vector
OUT=Path(sys.argv[sys.argv.index('--')+1]);OUT.mkdir(parents=True,exist_ok=True)
ART=Path(r'C:\Users\Shadow\Desktop\Working Files\3D Art')
paths=[ART/'Props/CSC_Prop_Library'/f'{n}.blend' for n in ['CSC_ALL_Oval_Table','CSC_ALL_Chair_Upholstered_Claret','DIS_COM_Table']]
paths += [ART/'Level 3/CSC_Level_3.blend',ART/'Decals/CSC_ALL_Cobble_Card.blend']
report=[]
for path in paths:
 bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
 s=bpy.data.scenes.get('Review') or bpy.context.scene;bpy.context.window.scene=s
 meshes=[o for o in s.objects if o.type=='MESH' and not o.hide_render]
 row={'path':str(path),'scenes':[s.name for s in bpy.data.scenes],'objects':[]}
 for o in meshes:
  points=[o.matrix_world@v.co for v in o.data.vertices]
  row['objects'].append({'name':o.name,'bounds':[[min(p[i] for p in points),max(p[i] for p in points)] for i in range(3)],'matrix':[list(r) for r in o.matrix_world],'uv':[u.name for u in o.data.uv_layers],'verts':len(o.data.vertices),'materials':[m.name for m in o.data.materials if m]})
 row['images']=[{'name':im.name,'path':im.filepath,'packed':bool(im.packed_file)} for im in bpy.data.images if im.source=='FILE']
 if 'Level 3' in str(path):
  o=meshes[0];row['ground_faces']=[{'p':p.index,'center':list(p.center),'verts':[list(o.data.vertices[i].co) for i in p.vertices]} for p in o.data.polygons if abs(p.normal.z)<.2 and p.center.z<45]
 if 'CSC_Prop_Library' in str(path):
  pts=[o.matrix_world@v.co for o in meshes for v in o.data.vertices];lo=Vector([min(p[i] for p in pts) for i in range(3)]);hi=Vector([max(p[i] for p in pts) for i in range(3)]);c=(lo+hi)/2;size=max(hi-lo)
  cam=bpy.data.objects.new('Inspect_Cam',bpy.data.cameras.new('Inspect_Cam'));s.collection.objects.link(cam);cam.data.type='ORTHO';cam.data.ortho_scale=size*1.6;cam.location=c+Vector((1,-1.6,1.2))*size;cam.rotation_euler=(c-cam.location).to_track_quat('-Z','Y').to_euler();s.camera=cam
  s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=True;s.render.resolution_x=s.render.resolution_y=512;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.film_transparent=False
  if not any(o.type=='LIGHT' for o in s.objects):
   ld=bpy.data.lights.new('Inspect_Sun','SUN');ld.energy=3;ob=bpy.data.objects.new('Inspect_Sun',ld);s.collection.objects.link(ob);ob.rotation_euler=Vector((300,280,-500)).to_track_quat('-Z','Y').to_euler()
  s.world=bpy.data.worlds.new('Inspect_World');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.7,.8,1,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.65
  # Repair external image paths only in the unsaved review copy.
  for im in bpy.data.images:
   if im.source!='FILE' or im.packed_file:continue
   p=Path(bpy.path.abspath(im.filepath))
   if not p.exists():
    matches=list((ART/'Props/CSC_Prop_Library').rglob(Path(im.filepath.replace('\\','/')).name))
    if matches:im.filepath=str(matches[0]);im.reload()
  s.render.filepath=str(OUT/(path.stem+'.png'));bpy.ops.render.render(write_still=True)
 report.append(row)
(OUT/'source-inventory.json').write_text(json.dumps(report,indent=2))
print('CAFE SOURCE INSPECTION COMPLETE',flush=True)
