import bpy,bmesh,sys
from pathlib import Path
from mathutils import Vector
O=Path.home()/'Desktop/Codex/modern-bakery-v3-20261028';ART=Path.home()/'Desktop/Working Files/3D Art'
variants=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['combined','delivery','rear','AO','windows-flat','windows-depth','windows-angle2','display-B','display-normal-A','display-normal-B','display-normal-off']
for variant in variants:
 bpy.ops.wm.open_mainfile(filepath=str(O/('CSC_BAKERS_Bakery_Modern_2_Review.blend' if variant=='delivery' else 'CSC_BAKERS_Bakery_Modern_Review.blend')),load_ui=False,use_scripts=False)
 s=bpy.data.scenes['Review'];bpy.context.window.scene=s
 for im in bpy.data.images:
  if im.source=='FILE' and im.filepath:im.reload()
 for ob in list(s.objects):
  if ob.type!='MESH':continue
  ob.data=ob.data.copy();bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=.00001,plane_co=ob.matrix_world.inverted()@Vector((0,0,0)),plane_no=ob.matrix_world.to_3x3().transposed()@Vector((0,0,1)),clear_inner=True);bm.to_mesh(ob.data);bm.free()
  if variant.startswith('display-'):ob.hide_render=ob.get('module')!='Display'
 for mat in bpy.data.materials:
  if not mat.use_nodes:continue
  ns=mat.node_tree.nodes;ls=mat.node_tree.links;bs=ns.get('Principled BSDF')
  if not bs:continue
  bs.inputs['Emission Strength'].default_value=0
  if variant=='windows-flat' and ns.get('O'):
   ns['B'].image=bpy.data.images.load(str(ART/'BAKERS/Bakery/modern/revision-02-concept-c/textures/CSC_Atlas_Modern_B_BAKERS.png'))
   for link in list(bs.inputs['Alpha'].links):ls.remove(link)
   bs.inputs['Alpha'].default_value=1
  if variant in ('AO','display-B'):
   ch='AO' if variant=='AO' else 'B'
   if ch in ns:
    em=ns.new('ShaderNodeEmission');ls.new(ns[ch].outputs['Color'],em.inputs['Color']);ls.new(em.outputs[0],ns.get('Material Output').inputs['Surface'])
  if 'normal' in variant:
   for slot in ('Base Color','Roughness','Metallic'):
    for l in list(bs.inputs[slot].links):ls.remove(l)
   bs.inputs['Base Color'].default_value=(.4,.4,.4,1);bs.inputs['Roughness'].default_value=.85;bs.inputs['Metallic'].default_value=0
   if variant.endswith('off'):
    for l in list(bs.inputs['Normal'].links):ls.remove(l)
 if variant=='delivery':s.camera.data.ortho_scale=211
 if variant=='rear':
  target=Vector((-4,-15,53));s.camera.location=target+Vector((-230,300,230));s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler()
 if variant.startswith('windows'):
  target=Vector((40,4,18));s.camera.location=target+Vector((115,65,32) if variant.endswith('angle2') else (115,-60,35));s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=62
 if variant.startswith('display-'):
  target=Vector((10,-37,16));s.camera.location=target+Vector((60,-110,70));s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=65
 if 'normal' in variant:
  l=s.objects['Review_Key'];l.data.color=(1,1,1);l.data.energy=2;direction=Vector((250,180,160) if variant.endswith('B') else (-240,-280,160));l.rotation_euler=(-direction).to_track_quat('-Z','Y').to_euler()
  for n in s.world.node_tree.nodes:
   if n.type=='BACKGROUND':n.inputs['Color'].default_value=(1,1,1,1);n.inputs['Strength'].default_value=.2
 s.render.engine='CYCLES';s.cycles.samples=40;s.render.resolution_x=s.render.resolution_y=1100;s.render.resolution_percentage=100;s.render.film_transparent=True;s.use_nodes=False;s.render.filepath=str(O/'review'/f'{variant}.png');bpy.ops.render.render(write_still=True);print('REVIEW',variant,flush=True)
