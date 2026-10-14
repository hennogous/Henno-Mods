"""Inspect/prepare Henno's current storage source, preserving authored UVs."""
import bpy, json, sys, hashlib, shutil
from datetime import datetime
from mathutils import Matrix
from pathlib import Path

SOURCE=Path(r'C:\Users\Shadow\Desktop\Working Files\3D Art\Storage\Storage_L\CSC_Storage_L.blend')
DONOR=Path(r'C:\Users\Shadow\Desktop\Codex\CSC_Storage_L\revision-01-crane-animation\CSC_Storage_L_Crane_Animation.blend')
OUT=Path(r'C:\Users\Shadow\Desktop\Codex\CSC_Storage_L\source-rig-20261008')
OUT.mkdir(parents=True,exist_ok=True)
for event in ('load_post','depsgraph_update_post'):
 for cb in list(getattr(bpy.app.handlers,event)):
  if cb.__module__.rsplit('.',1)[-1]=='csc_scene_tools':getattr(bpy.app.handlers,event).remove(cb)

def inspect(path):
 bpy.ops.wm.open_mainfile(filepath=str(path))
 return {'file':str(path),'scenes':[{'name':s.name,'objects':[o.name for o in s.objects],'props':dict(s.items())} for s in bpy.data.scenes],
 'objects':[{'name':o.name,'type':o.type,'parent':o.parent.name if o.parent else None,'matrix':[list(r) for r in o.matrix_world],
 'collections':[c.name for c in o.users_collection], 'props':dict(o.items()),
 'verts':len(o.data.vertices) if o.type=='MESH' else None,
 'uvs':[x.name for x in o.data.uv_layers] if o.type=='MESH' else None,
 'materials':[m.name if m else None for m in o.data.materials] if o.type=='MESH' else None,
 'modifiers':[(m.name,m.type) for m in o.modifiers],
 'bones':[{'name':b.name,'parent':b.parent.name if b.parent else None,'matrix':[list(r) for r in b.matrix_local]} for b in o.data.bones] if o.type=='ARMATURE' else None} for o in bpy.data.objects],
 'actions':[a.name for a in bpy.data.actions], 'images':[{'name':i.name,'path':i.filepath} for i in bpy.data.images if i.source=='FILE']}

if '--inspect' in sys.argv:
 for label,path in [('current',SOURCE),('animation',DONOR)]:
  (OUT/(label+'-inventory.json')).write_text(json.dumps(inspect(path),indent=2,default=str))
 print('STORAGE_SOURCE_INSPECTED')

if '--diagnose' in sys.argv:
 for label,path in [('source',SOURCE),('stage',OUT/'CSC_Storage_L_Rigged.blend')]:
  bpy.ops.wm.open_mainfile(filepath=str(path))
  print(label,[(o.name,o.hide_render,o.data.uv_layers.active_index,[(u.name,u.active_render) for u in o.data.uv_layers]) for o in bpy.data.objects if o.type=='MESH'])
  mat=bpy.data.materials['CSC_TAILORS_NE']
  for n in mat.node_tree.nodes:
   print(n.name,n.type,'uv',getattr(n,'uv_map',None),'image',getattr(getattr(n,'image',None),'name',None))
  print('links',[(x.from_node.name,x.from_socket.name,x.to_node.name,x.to_socket.name) for x in mat.node_tree.links])

def digest(path):
 return hashlib.sha256(path.read_bytes()).hexdigest()

def choose_scene(name):
 bpy.context.window.scene=bpy.data.scenes[name]
 return bpy.context.scene

def mesh_snapshot(objects):
 """Compare each face corner, including authored UVs and material, after joining."""
 faces=[]
 for obj in objects:
  mesh=obj.data
  for face in mesh.polygons:
   corners=[]
   for i in face.loop_indices:
    co=obj.matrix_world @ mesh.vertices[mesh.loops[i].vertex_index].co
    corners.append((tuple(round(x,5) for x in co),
                    tuple(tuple(uv.data[i].uv) for uv in mesh.uv_layers)))
   faces.append((obj.data.materials[face.material_index].name,face.use_smooth,tuple(corners)))
 return sorted(faces)

def render_preview(label):
 scene=choose_scene('Review')
 scene.render.resolution_x=1000
 scene.render.resolution_y=1000
 scene.render.resolution_percentage=100
 scene.render.image_settings.file_format='PNG'
 scene.render.filepath=str(OUT/(label+'.png'))
 bpy.ops.render.render(write_still=True)

if '--prepare' in sys.argv:
 source_hash=digest(SOURCE)
 bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
 meshes=sorted([o for o in bpy.data.objects if o.type=='MESH'],key=lambda o:o.name)
 assert len(meshes)==33 and not any(o.type=='ARMATURE' for o in bpy.data.objects)
 before=mesh_snapshot(meshes)
 nverts=sum(len(o.data.vertices) for o in meshes)
 metadata={o.name:dict(o.items()) for o in meshes}
 for im in bpy.data.images:
  if im.source=='FILE': im.filepath=bpy.path.abspath(im.filepath)
 render_preview('01-original')
 scene=choose_scene('Export')
 with bpy.data.libraries.load(str(DONOR),link=False) as (src,dst):
  dst.objects=['CSC_Storage_Crane_Rig']
 rig=dst.objects[0]
 assert rig is not None and rig.matrix_world==Matrix.Identity(4)
 # Keep the donor rig identity as well as bone names/rest matrices for clip matching.
 for sc in bpy.data.scenes:
  sc.collection.objects.link(rig)
 action=rig.animation_data.action
 assert action and action.name=='CSC_Storage_Crane_Lift_Textile_Bale'
 action.use_fake_user=True
 rig.animation_data.action_slot=action.slots[0]
 rig.data.pose_position='REST'
 rig.show_in_front=True
 rig.display_type='WIRE'
 bones=['Root','Swivel','Trolley','Hoist','Load']
 assert list(rig.data.bones.keys())==bones
 component_names=[]
 for ci,obj in enumerate(meshes):
  component_names.append(obj.name)
  assert [x.name for x in obj.data.uv_layers]==['UV1','UV2','UV3']
  assert not obj.modifiers
  metadata[obj.name]['original_vertex_groups']={g.name:[(v.index,x.weight) for v in obj.data.vertices for x in v.groups if x.group==g.index] for g in obj.vertex_groups}
  obj.vertex_groups.clear()
  groups={n:obj.vertex_groups.new(name=n) for n in bones}
  component=obj.data.attributes.new('csc_source_component','INT','POINT')
  for val in component.data: val.value=ci
  suffix=obj.name.removeprefix('CSC_Fixed_Crane_')
  bone=('Swivel' if suffix in ('Swivel_Shaft','Boom','Brace') else
        'Trolley' if suffix=='Rope_Collar' else
        'Hoist' if suffix in ('Pulley','Hook') else 'Root')
  if suffix=='Rope':
   split=(rig.data.bones['Trolley'].head_local.z+rig.data.bones['Hoist'].head_local.z)/2
   for v in obj.data.vertices:
    groups['Trolley' if (obj.matrix_world@v.co).z>split else 'Hoist'].add([v.index],1,'REPLACE')
  else: groups[bone].add(list(range(len(obj.data.vertices))),1,'REPLACE')
  obj.hide_set(False)
  obj.hide_viewport=False
 bpy.ops.object.select_all(action='DESELECT')
 for o in meshes: o.select_set(True)
 combined=bpy.data.objects['CSC_Fixed_Front']
 assert combined.matrix_world==Matrix.Identity(4)
 bpy.context.view_layer.objects.active=combined
 bpy.ops.object.join()
 # Join only unlinks the other objects from the active scene. Remove their
 # surviving Review links too, otherwise the review renders overlapping meshes.
 for name in component_names:
  old=bpy.data.objects.get(name)
  if old is not None and old!=combined: bpy.data.objects.remove(old,do_unlink=True)
 for sc in bpy.data.scenes:
  assert [o for o in sc.objects if o.type=='MESH']==[combined]
 combined.name='CSC_Storage_L_Mesh'
 combined.data.name='CSC_Storage_L_Geometry'
 for key in list(combined.keys()): del combined[key]
 combined['export_role']='building_geometry'
 combined['role']='rigged_building_geometry'
 combined['source_components']=json.dumps(component_names)
 combined.parent=rig
 combined.matrix_parent_inverse=Matrix.Identity(4)
 combined.matrix_world=Matrix.Identity(4)
 mod=combined.modifiers.new('Crane bone deformation','ARMATURE')
 mod.object=rig
 mod.use_deform_preserve_volume=False
 assert len(combined.data.vertices)==nverts
 assert mesh_snapshot([combined])==before, 'Joining changed geometry, UVs, smoothing or materials'
 assert len(combined.data.materials)==1 and combined.data.materials[0].name=='CSC_TAILORS_NE'
 for v in combined.data.vertices:
  assert len(v.groups)==1 and abs(v.groups[0].weight-1)<1e-7
 # Clear obsolete empty component collections, including the old foundation toggle.
 for col in list(bpy.data.collections):
  if not col.objects and not col.children: bpy.data.collections.remove(col)
 bpy.data.texts.new('Storage source components.json').write(json.dumps(metadata,indent=2,default=str))
 bpy.data.texts.new('START HERE - Storage crane').write(
  'One combined mesh, one armature, original material and UV1/UV2/UV3 preserved.\n'
  'Saved in REST position for geometry export. To preview: select the armature,\n'
  'Armature Data Properties > Skeleton > Pose Position, then play frames 1-361.\n'
  'The existing Action is already assigned. Return to Rest Position before model export.\n'
  'Root holds the building; Swivel rotates the arm; Trolley slides the rope collar;\n'
  'Hoist moves hook/pulley; rope endpoints follow Trolley and Hoist.\n'
  'Load is retained for a future attached bale. No bale or slings added to this source.\n'
  'IMPORTANT: standard CivNexus6 3-UV conversion drops skinning. CN6 retains\n'
  'these UVs and weights, but the subsequent model conversion must preserve skinning.\n'
  'The pre-existing AE test package is not validated by this source preparation.\n')
 for sc in bpy.data.scenes:
  sc.frame_start=1;sc.frame_end=361;sc.render.fps=30;sc.frame_set(1)
 render_preview('02-rigged-rest')
 scene=choose_scene('Export')
 rig.data.pose_position='POSE'
 counts={n:0 for n in bones}
 for v in combined.data.vertices: counts[combined.vertex_groups[v.groups[0].group].name]+=1
 static_error=0.0
 moving_span={n:0.0 for n in bones[1:4]}
 first={}
 for frame in range(1,362):
  scene.frame_set(frame)
  bpy.context.view_layer.update()
  evaluated=combined.evaluated_get(bpy.context.evaluated_depsgraph_get())
  for v,ev in zip(combined.data.vertices,evaluated.data.vertices):
   group=combined.vertex_groups[v.groups[0].group].name
   if group=='Root': static_error=max(static_error,(ev.co-v.co).length)
   elif frame==1: first[v.index]=ev.co.copy()
   elif group in moving_span: moving_span[group]=max(moving_span[group],(ev.co-first[v.index]).length)
 assert static_error<1e-5 and all(x>1 for x in moving_span.values())
 for frame in (1,151,291):
  choose_scene('Review').frame_set(frame)
  render_preview('pose-'+str(frame))
 rig.data.pose_position='REST'
 for sc in bpy.data.scenes: sc.frame_set(1)
 choose_scene('Export')
 bpy.ops.object.select_all(action='DESELECT')
 combined.select_set(True);rig.select_set(True)
 bpy.context.view_layer.objects.active=rig
 stage=OUT/'CSC_Storage_L_Rigged.blend'
 bpy.ops.wm.save_as_mainfile(filepath=str(stage))
 # Reload and compare the actual saved delivery, not only the authoring scene.
 bpy.ops.wm.open_mainfile(filepath=str(stage))
 assert mesh_snapshot([bpy.data.objects['CSC_Storage_L_Mesh']])==before
 assert len([o for o in bpy.data.objects if o.type=='MESH'])==1
 assert bpy.data.objects['CSC_Storage_Crane_Rig'].data.pose_position=='REST'
 report={'source_sha256':source_hash,'stage':str(stage),'source_meshes':33,
         'combined_meshes':1,'vertices':nverts,'face_corner_geometry_uv_material_parity':True,
         'bone_vertex_counts':counts,'max_static_vertex_motion':static_error,
         'moving_vertex_spans':moving_span,'frames_checked':361,'saved_reload_verified':True}
 (OUT/'rig-audit.json').write_text(json.dumps(report,indent=2))
 print('SOURCE_RIG_PREPARED '+json.dumps(report))

if '--install' in sys.argv:
 report=json.loads((OUT/'rig-audit.json').read_text())
 assert digest(SOURCE)==report['source_sha256'], 'Source changed during preparation; stop rather than overwrite'
 stamp=datetime.now().strftime('%Y%m%d-%H%M%S')
 backup=SOURCE.with_name(SOURCE.stem+'_before_rig_'+stamp+'.blend')
 shutil.copy2(SOURCE,backup)
 bpy.ops.wm.open_mainfile(filepath=report['stage'])
 for im in bpy.data.images:
  if im.source=='FILE': im.filepath=bpy.path.relpath(im.filepath,start=str(SOURCE.parent))
 bpy.context.preferences.filepaths.save_version=0
 bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE),relative_remap=False)
 report['backup']=str(backup)
 report['installed_sha256']=digest(SOURCE)
 (OUT/'rig-audit.json').write_text(json.dumps(report,indent=2))
 print('SOURCE_RIG_INSTALLED '+str(SOURCE)+' BACKUP '+str(backup))
