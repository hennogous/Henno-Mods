import bpy,bmesh,sys,math,os
from pathlib import Path
from mathutils import Vector
O=Path.home()/'Desktop/Codex/modern-bakery-v1-20261028'
O=Path(os.environ.get('CSC_BAKERY_OUTPUT',str(O)))
variants=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['combined','rear','AO','props-B','props-normal-A','props-normal-B']
for variant in variants:
 filename='CSC_BAKERS_Bakery_Modern_2_Review.blend' if variant in ('delivery','truck-B','truck-normal-A','truck-normal-B','truck-AO') else 'CSC_BAKERS_Bakery_Modern_Review.blend'
 path=Path.home()/'Desktop/Working Files/3D Art/Level 2/modern/revision-04-bakery-corrections/CSC_Level_2_Modern_Review.blend' if variant=='reusable' else O/filename
 bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
 s=bpy.data.scenes['Review'];bpy.context.window.scene=s
 for im in bpy.data.images:
  if im.source=='FILE' and im.filepath:im.reload()
 for o in list(s.objects):
  if o.type=='MESH':
   o.data=o.data.copy();bm=bmesh.new();bm.from_mesh(o.data)
   plane=o.matrix_world.inverted()@Vector((0,0,0));normal=o.matrix_world.to_3x3().transposed()@Vector((0,0,1))
   bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.0001,plane_co=plane,plane_no=normal,clear_inner=True,clear_outer=False);bm.to_mesh(o.data);bm.free()
   if variant.startswith('props-'):o.hide_render=o.get('module') not in ('Oven','Display','Rack','Trays')
   if variant.startswith('oven-'):o.hide_render=o.get('module')!='Oven'
   if variant.startswith('truck-'):o.hide_render=o.get('module')!='Truck'
 for mat in bpy.data.materials:
  if not mat.use_nodes:continue
  ns=mat.node_tree.nodes;ls=mat.node_tree.links;bs=ns.get('Principled BSDF')
  if not bs:continue
  bs.inputs['Emission Strength'].default_value=0
  if variant in ('AO','props-B','truck-B','truck-AO'):
   ch='AO' if variant in ('AO','truck-AO') else 'B'
   if ch not in ns:continue
   em=ns.new('ShaderNodeEmission');ls.new(ns[ch].outputs['Color'],em.inputs['Color']);ls.new(em.outputs[0],ns.get('Material Output').inputs['Surface'])
  if 'normal' in variant:
   for name in ('Base Color','Roughness','Metallic'):
    for l in list(bs.inputs[name].links):ls.remove(l)
   bs.inputs['Base Color'].default_value=(.35,.35,.35,1);bs.inputs['Roughness'].default_value=.85;bs.inputs['Metallic'].default_value=0
   if 'off' in variant:
    for l in list(bs.inputs['Normal'].links):ls.remove(l)
 if variant.startswith(('props-','oven-')):
  target=Vector((-11,-48,22));s.camera.location=target+Vector((160,-230,145));s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=128
 if variant.startswith('truck-'):
  target=Vector((-77,-64,13));s.camera.location=target+Vector((60,-100,55));s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=65
 if 'normal' in variant:
  light=s.objects['Review_Key'];light.data.color=(1,1,1);light.data.energy=2
  direction=Vector((-240,-280,160) if variant.endswith('A') else (250,180,160));light.rotation_euler=(-direction).to_track_quat('-Z','Y').to_euler()
  for n in s.world.node_tree.nodes:
   if n.type=='BACKGROUND':n.inputs['Color'].default_value=(1,1,1,1);n.inputs['Strength'].default_value=.2
 if variant=='rear':
  target=Vector((-8,-14,53));s.camera.location=target+Vector((-230,300,230));s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler()
 if variant=='top':s.camera.location=(-4,-15,300);s.camera.rotation_euler=(0,0,0);s.camera.data.ortho_scale=211
 s.cycles.samples=32;s.render.resolution_x=s.render.resolution_y=1100;s.render.resolution_percentage=100;s.use_nodes=False;s.render.film_transparent=True
 s.render.filepath=str(O/'review'/f'{variant}.png');bpy.ops.render.render(write_still=True);print('REVIEW',variant,flush=True)
