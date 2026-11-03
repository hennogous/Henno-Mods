import bpy,sys
from pathlib import Path
from mathutils import Vector
O=Path.home()/'Desktop/Codex/modern-level2-v3-details-20261028'
for mode in ('B-only','normal-off-A','normal-on-A','normal-off-B','normal-on-B','combined'):
 bpy.ops.wm.open_mainfile(filepath=str(O/'Decor_Local_Masters.blend'),load_ui=False,use_scripts=False);s=bpy.data.scenes['Review'];bpy.context.window.scene=s
 for ob in list(bpy.data.objects):
  if ob.type=='MESH':
   if ob.get('module') not in ('FlowerBox','Sign'):bpy.data.objects.remove(ob,do_unlink=True)
   elif ob['module']=='Sign':ob.location=(16,0,20)
 for im in bpy.data.images:
  if im.source=='FILE' and im.filepath:im.reload()
 target=Vector((10,0,7));s.camera.location=target+Vector((35,-70,40));s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=64
 s.render.resolution_x=700;s.render.resolution_y=450;s.render.resolution_percentage=100;s.cycles.samples=16;s.use_nodes=False
 mat=bpy.data.materials['CSC_Props_Modern_01'];ns=mat.node_tree.nodes;ls=mat.node_tree.links;bs=ns.get('Principled BSDF')
 if mode=='B-only':
  em=ns.new('ShaderNodeEmission');ls.new(ns['B'].outputs['Color'],em.inputs['Color']);ls.new(em.outputs[0],ns.get('Material Output').inputs['Surface'])
 if mode.startswith('normal'):
  for name in ('Base Color','Roughness','Metallic'):
   for l in list(bs.inputs[name].links):ls.remove(l)
  bs.inputs['Base Color'].default_value=(.32,.32,.32,1);bs.inputs['Roughness'].default_value=.85;bs.inputs['Metallic'].default_value=0
  if '-off-' in mode:
   for l in list(bs.inputs['Normal'].links):ls.remove(l)
  light=s.objects['Review_Key'];light.data.color=(1,1,1);light.data.energy=2;direction=Vector((-240,-280,160) if mode.endswith('A') else (250,180,160));light.rotation_euler=(-direction).to_track_quat('-Z','Y').to_euler()
  for n in s.world.node_tree.nodes:
   if n.type=='BACKGROUND':n.inputs['Color'].default_value=(1,1,1,1);n.inputs['Strength'].default_value=.18
 s.render.filepath=str(O/'review'/('props-'+mode+'.png'));bpy.ops.render.render(write_still=True)
print('DECOR_DIAGNOSTICS_READY')
