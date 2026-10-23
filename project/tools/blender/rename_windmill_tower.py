"""Rename the current tower datablocks and retime its full rotation to eight seconds."""
import bpy,bmesh,json,sys,hashlib
from pathlib import Path
OUT=Path(sys.argv[sys.argv.index('--')+1]);ROOT=Path(__file__).resolve().parents[3]
OLD='CSC_BAKERS_Wind_Mill_'+'Plaster'+'_Tower';NEW='CSC_BAKERS_Wind_Mill_Tower'
ART=Path.home()/'Desktop/Working Files/3D Art';SOURCE=ART/'BAKERS/Wind Mill'/('plaster'+'-tower')
def rename(s):return s.replace(OLD,NEW).replace('plaster'+'-tower','tower').replace('plaster'+'_tower','tower')
def signature(ob):return dict(vertices=[list(v.co) for v in ob.data.vertices],faces=[list(f.vertices) for f in ob.data.polygons],uvs=[[list(v.uv) for v in u.data] for u in ob.data.uv_layers],weights=[[(g.group,g.weight) for g in v.groups] for v in ob.data.vertices])
rows=[]
for suffix in ['', '_CON+PIL']:
 p=SOURCE/(OLD+suffix+'.blend');rows.append(dict(path=str(p),sha=hashlib.sha256(p.read_bytes()).hexdigest()))
 bpy.ops.wm.open_mainfile(filepath=str(p),load_ui=False,use_scripts=False)
 if bpy.context.object and bpy.context.object.mode!='OBJECT':bpy.ops.object.mode_set(mode='OBJECT')
 bpy.context.window.scene=bpy.data.scenes['Export'];scene=bpy.context.scene;scene.frame_set(1)
 objects=[o for o in scene.objects if o.type=='MESH'];before={rename(o.name):signature(o) for o in objects};rig=bpy.data.objects[OLD+suffix]
 for collection in [bpy.data.objects,bpy.data.meshes,bpy.data.armatures,bpy.data.actions,bpy.data.materials,bpy.data.images,bpy.data.collections,bpy.data.scenes,bpy.data.node_groups]:
  for item in collection:
   item.name=rename(item.name)
   for k in list(item.keys()):
    if isinstance(item[k],str):item[k]=rename(item[k])
 for arm in bpy.data.armatures:
  for bone in arm.bones:bone.name=rename(bone.name)
 for im in bpy.data.images:
  if im.source=='FILE':im.filepath=rename(str(Path(bpy.path.abspath(im.filepath)).resolve()))
 if not suffix:
  action=rig.animation_data.action;curves=[]
  for layer in action.layers:
   for strip in layer.strips:
    for bag in strip.channelbags:curves.extend(bag.fcurves)
  assert curves
  for curve in curves:
   for key in curve.keyframe_points:
    for v in [key.co,key.handle_left,key.handle_right]:v.x=1+(v.x-1)*.8
   curve.update()
  assert abs(action.frame_range[0]-1)<.001 and abs(action.frame_range[1]-241)<.001,list(action.frame_range)
  for s in bpy.data.scenes:s.frame_start=1;s.frame_end=241;s.render.fps=30;s.render.fps_base=1;s['animation_notes']='One full sail rotation in eight seconds, linear loop.'
 for s in bpy.data.scenes:s['asset_id']=NEW+suffix;s['atlas_release']='2026-10-22_Shared_01_r041'
 assert before=={o.name:signature(o) for o in objects}
 bpy.ops.object.select_all(action='DESELECT')
 for o in [rig,*objects]:o.select_set(True)
 bpy.context.view_layer.objects.active=rig;bpy.context.preferences.filepaths.save_version=0
 dest=OUT/'masters'/(NEW+suffix+'.blend');dest.parent.mkdir(parents=True,exist_ok=True);bpy.ops.wm.save_as_mainfile(filepath=str(dest),relative_remap=False)
 if not suffix:
  sys.path.insert(0,str(Path.home()/'.codex/skills/civ6-art/scripts'));from civ6_animation import core
  clip=OUT/'staged/Animations'/(NEW+'_Turn.fgx');clip.parent.mkdir(parents=True,exist_ok=True)
  result=core.export_animation(str(clip),rig,r'C:\Program Files (x86)\CivNexus6_Release-1.3.3\CivNexus6',1,241,overwrite=True)
  (OUT/'animation-export.json').write_text(json.dumps(result,indent=2))
 # Preserve the export-only hard corners on the tower.
 tower=next(o for o in objects if o.name.endswith('_Tower') or o.name.endswith('_Shell'));tower.data=tower.data.copy();bm=bmesh.new();bm.from_mesh(tower.data);bmesh.ops.split_edges(bm,edges=[e for e in bm.edges if len(e.link_faces)==2 and e.calc_face_angle()>.01]);bm.to_mesh(tower.data);bm.free()
 sys.path.insert(0,str(ROOT/'project/tools/scripts'));import io_export_cn6_b4
 cn6=OUT/'staged/Geometries'/(NEW+suffix+'.cn6');cn6.parent.mkdir(parents=True,exist_ok=True);io_export_cn6_b4.do_export(str(cn6),True,True)
(OUT/'inspection.json').write_text(json.dumps(rows,indent=2));print('RENAMED_AND_RETIMED',flush=True)
