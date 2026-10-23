"""Bake projecting sail joints onto simple rails; retain the latest user edits."""
import bpy,bmesh,json,sys,hashlib,shutil,math
from pathlib import Path
from mathutils import Vector
OUT=Path(sys.argv[sys.argv.index('--')+1]);ROOT=Path(__file__).resolve().parents[3]
ART=Path.home()/'Desktop/Working Files/3D Art';SOURCE=ART/'BAKERS/Wind Mill/tower'
NAME='CSC_BAKERS_Wind_Mill_Tower';RUIN=NAME+'_CON+PIL';report=[];baseline=[]
RIGHT=Vector((math.sqrt(3)/2,-.5,0));BACK=Vector((.5,math.sqrt(3)/2,0));HUB=Vector((26.99117,-41.48987,63.74731))
for folder in ['masters','before','bakes','staged/Geometries']:(OUT/folder).mkdir(parents=True,exist_ok=True)
source=(ROOT/'project/tools/blender/revise_windmill_shared_materials.py').read_text()
exec(compile(source[source.index('def bake_material'):source.index('def material')],'shared_bake','exec'))
sys.path.insert(0,str(ROOT/'project/tools/scripts'));import io_export_cn6_b4

def signature(ob):
 return dict(vertices=[tuple(v.co) for v in ob.data.vertices],faces=[tuple(f.vertices) for f in ob.data.polygons],UV1=[tuple(v.uv) for v in ob.data.uv_layers['UV1'].data],UV3=[tuple(v.uv) for v in ob.data.uv_layers['UV3'].data])

def joint_uv(me,local=False):
 # Eight independent longitudinal strips: four faces of each rail.
 for f in me.polygons:
  ids=[me.loops[i].vertex_index for i in f.loop_indices]
  if not all(i<456 and i%114<16 for i in ids):continue
  blade=ids[0]//114;rail=(ids[0]%114)//8;corners=[(i%114)%8 for i in ids]
  face=next((j for j,s in enumerate([{0,1,2,3},{4,5,6,7},{1,2,5,6},{0,3,4,7}]) if set(corners)==s),None)
  if face is None:continue
  strip=rail*4+face
  for li,c in zip(f.loop_indices,corners):
   v=1 if c in [2,3,6,7] else 0;u=(1 if c in [1,2,5,6] else 0) if face<2 else (1 if c>=4 else 0)
   x=strip*15+2+11*u;y=2+116*v
   me.uv_layers['UV1'].data[li].uv=(x/120,y/120) if local else ((772+x)/1024,1-(636-y)/1024)

def bake_joints(sails):
 scene=bpy.context.scene
 high=sails.copy();high.data=sails.data.copy();high.name='Joint bake high';high.parent=None;high.matrix_world=sails.matrix_world.copy();high.modifiers.clear();scene.collection.objects.link(high)
 bm=bmesh.new();bm.from_mesh(high.data);bm.verts.ensure_lookup_table();bmesh.ops.delete(bm,geom=[v for v in bm.verts if v.index>=114 or 64<=v.index<82],context='VERTS');bm.to_mesh(high.data);bm.free()
 bevel=high.modifiers.new('Small joint bevel for normal projection','BEVEL');bevel.width=.18;bevel.segments=2
 high.data.materials[0]=high.data.materials[0].copy();hm=high.data.materials[0]
 low=sails.copy();low.data=sails.data.copy();low.name='Joint bake low';low.parent=None;low.matrix_world=sails.matrix_world.copy();low.modifiers.clear();scene.collection.objects.link(low)
 joint_uv(low.data,True)
 bm=bmesh.new();bm.from_mesh(low.data);bm.verts.ensure_lookup_table();bmesh.ops.delete(bm,geom=[v for v in bm.verts if v.index>=16],context='VERTS')
 # End caps keep the existing wood mapping and are not part of this bake.
 bmesh.ops.delete(bm,geom=[f for f in bm.faces if {v.index%8 for v in f.verts} in [{0,1,4,5},{2,3,6,7}]],context='FACES');bm.to_mesh(low.data);bm.free()
 lm=bpy.data.materials.new('Joint bake target');lm.use_nodes=True;low.data.materials.clear();low.data.materials.append(lm)
 low.data.uv_layers.active_index=0;low.data.uv_layers['UV1'].active_render=True
 scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=64;scene.render.bake.use_selected_to_active=True;scene.render.bake.use_cage=False;scene.render.bake.cage_extrusion=1.6;scene.render.bake.max_ray_distance=3.2;scene.render.bake.margin=6;scene.render.bake.use_clear=False
 for other in scene.objects:
  if other.type=='MESH':other.hide_render=other not in [high,low]
 bpy.ops.object.select_all(action='DESELECT');high.select_set(True);low.select_set(True);bpy.context.view_layer.objects.active=low
 nodes=hm.node_tree.nodes;links=hm.node_tree.links;output=next(n for n in nodes if n.type=='OUTPUT_MATERIAL');original=output.inputs['Surface'].links[0].from_socket
 emit=nodes.new('ShaderNodeEmission')
 for channel in ['N','B','G','M']:
  im=bpy.data.images.new('Sail_joint_'+channel,width=480,height=480,alpha=False,float_buffer=True);im.generated_color=(.5,.5,1,1) if channel=='N' else (0,0,0,1);im.colorspace_settings.name='sRGB' if channel=='B' else 'Non-Color'
  target=lm.node_tree.nodes.new('ShaderNodeTexImage');target.image=im;lm.node_tree.nodes.active=target
  if channel=='N':
   links.new(original,output.inputs['Surface']);scene.render.bake.normal_space='TANGENT';bpy.ops.object.bake(type='NORMAL')
  else:
   tex=nodes.get(channel);assert tex and tex.type=='TEX_IMAGE',channel
   links.new(tex.outputs['Color'],emit.inputs['Color']);links.new(emit.outputs[0],output.inputs['Surface']);bpy.ops.object.bake(type='EMIT')
  im.file_format='PNG';im.filepath_raw=str(OUT/'bakes'/('sail_joints_'+channel+'.png'));im.save();print('JOINT_MAP_BAKED',channel,flush=True)
 bpy.data.objects.remove(high,do_unlink=True);bpy.data.objects.remove(low,do_unlink=True)
 for other in scene.objects:
  if other.type=='MESH':other.hide_render=False
 scene.render.bake.use_selected_to_active=False

for name in [NAME,RUIN]:
 p=SOURCE/(name+'.blend');baseline.append(dict(path=str(p),sha=hashlib.sha256(p.read_bytes()).hexdigest()));shutil.copy2(p,OUT/'before'/p.name)
 bpy.ops.wm.open_mainfile(filepath=str(p),load_ui=False,use_scripts=False)
 if bpy.context.object and bpy.context.object.mode!='OBJECT':bpy.ops.object.mode_set(mode='OBJECT')
 scene=bpy.data.scenes['Export'];bpy.context.window.scene=scene;scene.frame_set(1);rig=bpy.data.objects[name]
 tower=next(o for o in scene.objects if o.type=='MESH' and (o.name.endswith('_Tower') or o.name.endswith('_Shell')));before=signature(tower)
 assert len(tower.data.materials)==2 and all(f.material_index==0 for f in tower.data.polygons)
 tower.data.materials.pop(index=1)
 bake(tower,[(name+'_Masonry',[516,976,580,1020] if name==NAME else [584,976,648,1020],1024,14)])
 assert before==signature(tower),'Latest user tower geometry/UV1/UV3 changed'
 if name==NAME:
  sails=bpy.data.objects[NAME+'_Sails'];assert len(sails.data.vertices)==518
  bake_joints(sails);joint_uv(sails.data)
  # Trim rung ends inside the beam joints. Remove hidden end caps and raised ties.
  for blade in range(4):
   angle=math.radians(22.5+90*blade);across=RIGHT*math.cos(angle)-Vector((0,0,1))*math.sin(angle);along=RIGHT*math.sin(angle)+Vector((0,0,1))*math.cos(angle)
   for vi in range(blade*114+16,blade*114+64):
    v=sails.data.vertices[vi];r=(v.co-HUB).dot(along);x=(v.co-HUB).dot(across);half=4.5*2.025*(.6+.4*(r-5.5)/(47.8-5.5))-.825+.04
    v.co+=across*(math.copysign(half,x)-x)
  bm=bmesh.new();bm.from_mesh(sails.data);bm.verts.ensure_lookup_table()
  caps=[f for f in bm.faces if all(v.index<456 and 16<=v.index%114<64 for v in f.verts) and len({(v.index%114-16)//8 for v in f.verts})==1 and {(v.index%114)%8 for v in f.verts} in [{1,2,5,6},{0,3,4,7}]]
  assert len(caps)==48;bmesh.ops.delete(bm,geom=caps,context='FACES_ONLY')
  ties=[v for v in bm.verts if v.index<456 and 82<=v.index%114<114];assert len(ties)==128;bmesh.ops.delete(bm,geom=ties,context='VERTS');bm.to_mesh(sails.data);bm.free();sails.data.update()
  assert len(sails.data.vertices)==390
  sails['joint_details']='High-to-low normal bake; projecting rung ends and raised tie boxes removed'
  bake(sails,[(NAME+'_Sails',[0,128,512,512],2048,10)])
  report.append(dict(sail_source_vertices=390,sail_source_faces=len(sails.data.polygons),removed_tie_vertices=128,removed_rung_end_faces=48,normal_slot=38))
 objects=[o for o in scene.objects if o.type=='MESH']
 for o in objects:o.data.uv_layers.active_index=0;o.data.uv_layers['UV1'].active_render=True
 for s in bpy.data.scenes:s['atlas_release']='2026-10-22_Shared_01_r040'
 bpy.ops.object.select_all(action='DESELECT')
 for o in [rig,*objects]:o.select_set(True)
 bpy.context.view_layer.objects.active=rig;bpy.context.preferences.filepaths.save_version=0
 bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'masters'/(name+'.blend')),relative_remap=False)
 tower.data=tower.data.copy();bm=bmesh.new();bm.from_mesh(tower.data);bmesh.ops.split_edges(bm,edges=[e for e in bm.edges if len(e.link_faces)==2 and e.calc_face_angle()>.01]);bm.to_mesh(tower.data);bm.free()
 cn6=OUT/'staged/Geometries'/(name+'.cn6');io_export_cn6_b4.do_export(str(cn6),True,True)
 # Normalize inactive influence IDs before invoking CivNexus.
 lines=cn6.read_text().splitlines();inside=False
 for i,line in enumerate(lines):
  if line=='vertices':inside=True;continue
  if line=='triangles':inside=False
  if not inside:continue
  fields=line.split();assert len(fields)==34;ids=list(map(int,fields[18:26]));weights=list(map(int,fields[26:34]));active=[b for b,w in zip(ids,weights) if w>0];assert active
  fields[18:26]=[str(b if w else active[0]) for b,w in zip(ids,weights)];lines[i]=' '.join(fields)
 cn6.write_text('\n'.join(lines)+'\n')
(OUT/'inspection.json').write_text(json.dumps(baseline,indent=2));(OUT/'authoring-report.json').write_text(json.dumps(dict(bakes=report,user_tower_geometry_UV1_UV3_preserved=True,unused_tower_material_removed=True),indent=2))
print('SIMPLIFIED_MASTERS_AUTHORED',flush=True)
