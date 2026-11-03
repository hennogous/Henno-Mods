"""Saved-model paint and normal acceptance views, with independent light directions."""
import bpy,bmesh,json,sys,math,os
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[4];O=Path.home()/'Desktop/Codex/modern-storage-v1-20261029';sys.path.insert(0,str(ROOT/'project/tools/blender'));from csc_scene_validation import suspend_csc_repairs
for rec in json.loads((O/'masters.json').read_text()):
 if rec['group'] not in os.environ.get('CSC_STORAGE_DIAGNOSTIC_GROUPS','M,L').split(','):continue
 with suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=rec['blend'],load_ui=False,use_scripts=False)
 s=bpy.data.scenes['Review'];bpy.context.window.scene=s;s.cycles.samples=16;s.render.resolution_x=s.render.resolution_y=800;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.image_settings.media_type='IMAGE';s.use_nodes=False
 target=Vector((-13,-7,37));s.camera.location=target+Vector((-140,-220,130));s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=161
 for ob in s.objects:
  if ob.type=='MESH':
   b=bmesh.new();b.from_mesh(ob.data);bmesh.ops.bisect_plane(b,geom=list(b.verts)+list(b.edges)+list(b.faces),plane_co=(0,0,0),plane_no=(0,0,1),clear_inner=True);b.to_mesh(ob.data);b.free()
 ma=bpy.data.materials['CSC_BAKERS_Modern'];ns=ma.node_tree.nodes;ls=ma.node_tree.links;bs=ns.get('Principled BSDF');out=ns.get('Material Output');em=ns.new('ShaderNodeEmission');ls.new(ns['B'].outputs[0],em.inputs[0]);ls.new(em.outputs[0],out.inputs['Surface'])
 def render(label):s.render.filepath=str(O/'review'/f"{rec['group']}_{label}.png");bpy.ops.render.render(write_still=True)
 render('B_Only');ls.new(bs.outputs[0],out.inputs['Surface'])
 for slot in ('Base Color','Roughness','Metallic'):
  for link in list(bs.inputs[slot].links):ls.remove(link)
 bs.inputs['Base Color'].default_value=(.45,.45,.45,1);bs.inputs['Roughness'].default_value=.8;bs.inputs['Metallic'].default_value=0;normal=next(iter(bs.inputs['Normal'].links)).from_socket
 for i,direction in enumerate(((-300,-180,300),(180,-300,250))):
  bpy.data.objects['Review_Key'].rotation_euler=(-Vector(direction)).to_track_quat('-Z','Y').to_euler()
  for link in list(bs.inputs['Normal'].links):ls.remove(link)
  render('N_Off_'+str(i));ls.new(normal,bs.inputs['Normal']);render('N_On_'+str(i))
 # AO diagnosis under unlit output.
 ls.new(ns['AO'].outputs[0],em.inputs[0]);ls.new(em.outputs[0],out.inputs['Surface']);render('AO_Only')
print('DIAGNOSTICS_READY',flush=True)
