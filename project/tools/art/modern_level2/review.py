"""Render the saved authoring assembly, keeping production masters intact."""
import bpy,bmesh,sys,math,json,os
from pathlib import Path
from mathutils import Vector
O=Path.home()/'Desktop/Codex/modern-level2-v1-20261028'
O=Path(os.environ.get('CSC_LEVEL2_OUTPUT',str(O)))
variants=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['combined']
for variant in variants:
 bpy.ops.wm.open_mainfile(filepath=str(O/'CSC_Level_2_Modern_Assembly.blend'),load_ui=False,use_scripts=False);s=bpy.data.scenes['Review'];bpy.context.window.scene=s
 for im in bpy.data.images:
  if im.source=='FILE':im.reload()
 for o in list(s.objects):
  if o.type=='MESH':
   o.data=o.data.copy();bm=bmesh.new();bm.from_mesh(o.data)
   # Clip at world terrain datum, preserving translated wall-mounted props below their own pivot.
   ground=o.matrix_world.inverted()@Vector((0,0,0));normal=o.matrix_world.to_3x3().transposed()@Vector((0,0,1))
   bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.0001,plane_co=ground,plane_no=normal,clear_inner=True,clear_outer=False);bm.to_mesh(o.data);bm.free()
 s.render.resolution_x=s.render.resolution_y=1000;s.cycles.samples=24;s.render.resolution_percentage=100;s.use_nodes=False
 mat=bpy.data.materials['CSC_BAKERS_Modern'];ns=mat.node_tree.nodes;ls=mat.node_tree.links;bs=ns.get('Principled BSDF')
 if variant=='converted':
  for ch in ('B','N','G','M','E'):
   path=O/'native/textures'/('CSC_Atlas_Modern'+('_B_BAKERS' if ch=='B' else '_'+ch)+'.dds');im=bpy.data.images.load(str(path),check_existing=False);im.colorspace_settings.name='sRGB' if ch in ('B','E') else 'Non-Color';ns[ch].image=im
 if variant=='B-only':
  em=ns.new('ShaderNodeEmission');ls.new(ns['B'].outputs['Color'],em.inputs['Color']);ls.new(em.outputs[0],ns.get('Material Output').inputs['Surface'])
 if variant.startswith('neutral'):
  for name in ('Base Color','Roughness','Metallic'):
   for l in list(bs.inputs[name].links):ls.remove(l)
  bs.inputs['Base Color'].default_value=(.32,.32,.32,1);bs.inputs['Roughness'].default_value=.85;bs.inputs['Metallic'].default_value=0
  if 'off' in variant:
   for l in list(bs.inputs['Normal'].links):ls.remove(l)
  light=s.objects['Review_Key'];light.data.color=(1,1,1);light.data.energy=2;direction=Vector((-240,-280,160) if variant.endswith('A') else (250,180,160));light.rotation_euler=(-direction).to_track_quat('-Z','Y').to_euler()
  for n in s.world.node_tree.nodes:
   if n.type=='BACKGROUND':n.inputs['Color'].default_value=(1,1,1,1);n.inputs['Strength'].default_value=.18
 if variant=='rear':
  target=Vector((-12,0,54));s.camera.location=target+Vector((-250,250,220));s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler()
 if variant=='top':s.camera.location=(-12,0,280);s.camera.rotation_euler=(0,0,0)
 (O/'review').mkdir(exist_ok=True);s.render.filepath=str(O/'review'/(variant+'.png'));bpy.ops.render.render(write_still=True);print('REVIEW',variant,flush=True)
