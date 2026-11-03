"""Repair existing saved CON/PIL masters in place geometrically, staging first."""
import bpy,bmesh,sys,json,hashlib,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];sys.path[:0]=[str(ROOT/'project/tools/blender'),str(ROOT/'project/tools/blender/scene_export')]
import decode_blend as dec
from csc_scene_validation import suspend_csc_repairs,validate_current_scene
A=Path.home()/'Desktop/Working Files/3D Art';O=Path.home()/'Desktop/Codex/modern-l1-ao-fix-20261028';O.mkdir(exist_ok=True)
BASE='CSC_Level_1_S_Modern_CON+PIL';WATER='CSC_BAKERS_Water_Mill_Modern_CON+PIL'
paths={BASE:A/'Level 1/modern/CON+PIL/revision-01'/(BASE+'.blend'),WATER:A/'BAKERS/Water Mill/modern/CON+PIL/revision-01'/(WATER+'.blend')}
def dump(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2))
def signature(o):
 return sorted(tuple(round(x,5) for x in [*o.data.vertices[o.data.loops[i].vertex_index].co,*o.data.uv_layers[0].data[i].uv,*o.data.uv_layers[1].data[i].uv,*o.data.uv_layers[2].data[i].uv]) for p in o.data.polygons for i in p.loop_indices)
reports=[];tie_uv={}
with suspend_csc_repairs():
 for ident,path in paths.items():
  bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False);scene=bpy.data.scenes['Export'];bpy.context.window.scene=scene;bpy.context.view_layer.update();objects=[o for o in scene.objects if o.type=='MESH'];fixes=[]
  before={o.name:signature(o) for o in objects}
  for o in objects:
   if not o.name.startswith('State_Brick_'):continue
   bm=bmesh.new();bm.from_mesh(o.data);initial={'volume':bm.calc_volume(signed=True),'inconsistent_edges':sum(not e.is_contiguous for e in bm.edges)};bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));after={'volume':bm.calc_volume(signed=True),'inconsistent_edges':sum(not e.is_contiguous for e in bm.edges)};assert after['volume']>0 and after['inconsistent_edges']==0;bm.to_mesh(o.data);bm.free();o.data.update();fixes.append({'object':o.name,'before':initial,'after':after})
  assert all(signature(o)==before[o.name] for o in objects),'Positions or UV corner mapping changed'
  if ident==BASE:
   obs=[o for o in objects if not o.get('state_scaffold') and not o.get('wind_tie_in')];bpy.ops.object.select_all(action='DESELECT');old_uv={o.name:[u.uv.copy() for u in o.data.uv_layers[1].data] for o in obs};hides={o.name:o.hide_render for o in objects}
   for o in objects:o.hide_set(False);o.hide_render=o not in obs
   for o in obs:
    o.select_set(True);o.data.uv_layers.active_index=1;o.data.uv_layers[1].active_render=True
    for u in o.data.uv_layers[1].data:u.uv=(u.uv.x*4,(u.uv.y-.5)*4)
   bpy.context.view_layer.objects.active=obs[0];mat=bpy.data.materials['CSC_BAKERS_Modern'];ns=mat.node_tree.nodes;links=mat.node_tree.links;node=next(n for n in ns if n.type=='TEX_IMAGE' and (n.label or n.name)=='AO');old=node.image;im=bpy.data.images.new('Corrected_State_AO',width=512,height=512,alpha=False);im.colorspace_settings.name='Non-Color';node.image=im;ns.active=node
   normal_links=[(l.from_socket,l.to_socket) for n in ns if n.type=='BSDF_PRINCIPLED' for l in n.inputs['Normal'].links]
   for n in ns:
    if n.type=='BSDF_PRINCIPLED':
     for l in list(n.inputs['Normal'].links):links.remove(l)
   scene.render.engine='CYCLES';scene.cycles.samples=128;scene.render.bake.margin=6;bpy.ops.object.bake(type='AO',uv_layer='UV2');im.filepath_raw=str(O/'corrected-building-state-AO.png');im.file_format='PNG';im.save();node.image=old
   for a,b in normal_links:links.new(a,b)
   for o in obs:
    for u,v in zip(o.data.uv_layers[1].data,old_uv[o.name]):u.uv=v
    o.data.uv_layers.active_index=0;o.data.uv_layers[0].active_render=True
   # Exposed cut ends cannot inherit the full shelter's contact-darkened endcaps.
   ties=[o for o in objects if o.get('wind_tie_in')];bpy.ops.object.select_all(action='DESELECT')
   for o in objects:o.hide_render=bool(o.get('state_scaffold')) or o.get('state_group')=='SiloFrontFrame'
   for o in ties:o.hide_render=False;o.select_set(True);o.data.uv_layers.active_index=1;o.data.uv_layers[1].active_render=True
   bpy.context.view_layer.objects.active=ties[0];bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=1.2,island_margin=.06,scale_to_bounds=True);bpy.ops.object.mode_set(mode='OBJECT')
   tie_image=bpy.data.images.new('Wind_TieIn_AO',width=128,height=128,alpha=False);tie_image.colorspace_settings.name='Non-Color';node.image=tie_image;ns.active=node
   for n in ns:
    if n.type=='BSDF_PRINCIPLED':
     for l in list(n.inputs['Normal'].links):links.remove(l)
   scene.render.bake.margin=4;bpy.ops.object.bake(type='AO',uv_layer='UV2');tie_image.filepath_raw=str(O/'wind-tie-in-AO.png');tie_image.file_format='PNG';tie_image.save();node.image=old
   for a,b in normal_links:links.new(a,b)
   for o in ties:
    for u in o.data.uv_layers[1].data:u.uv=(.25+u.uv.x/16,.6875+u.uv.y/16)
    tie_uv[o.name]=[list(u.uv) for u in o.data.uv_layers[1].data];o.data.uv_layers.active_index=0;o.data.uv_layers[0].active_render=True
   for o in objects:o.hide_render=hides[o.name]
  else:
   for o in objects:
    if o.name in tie_uv:
     for u,v in zip(o.data.uv_layers[1].data,tie_uv[o.name]):u.uv=v
  assert all(signature(o)==before[o.name] for o in objects if not o.get('wind_tie_in')),'Unrelated UVs changed during bake'
  parts=[]
  for g in sorted({o['state_group'] for o in objects}):parts.append(dec.merge_meshes(ident+'_'+g,[dec.decode_mesh(o,o.matrix_world) for o in objects if o['state_group']==g]))
  dump(O/'models'/(ident+'.json'),{'asset_id':ident,'kind':'building','meshes':parts})
  folder=O/'masters'/ident;folder.mkdir(parents=True,exist_ok=True);bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(folder/(ident+'.blend')),relative_remap=False);validation=validate_current_scene();assert validation['automated_pass'];dump(folder/'validation.json',validation)
  reports.append({'asset':ident,'source':str(path),'before_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'wall_repairs':fixes,'wall_positions_and_all_uv_corner_mappings_preserved':True,'wind_tie_in_uv2':'New independent AO [512,512,640,640]; no inherited dark contact caps'})
 dump(O/'repair-report.json',reports)
