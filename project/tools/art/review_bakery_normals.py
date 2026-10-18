"""Read-only matched normal strength 0/1 renders from saved revision sources."""
import bpy,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from bakery_props_atlas import SOURCE,OUT
for ident in (['CSC_BAKERS_Bread_Basket_Round'] if '--bread-only' in sys.argv else ['CSC_BAKERS_Oven_v2','CSC_BAKERS_Bread_Basket_Round','CSC_BAKERS_Bread_Cart']):
 bpy.ops.wm.open_mainfile(filepath=str(SOURCE/(ident+'.blend')),load_ui=False,use_scripts=False)
 scene=bpy.data.scenes['Review'];bpy.context.window.scene=scene
 for im in bpy.data.images:
  if im.source=='FILE' and im.users:im.reload()
 if scene.world and scene.world.use_nodes:
  nt=scene.world.node_tree;out=next(n for n in nt.nodes if n.type=='OUTPUT_WORLD');old=out.inputs[0].links[0].from_socket;bg=nt.nodes.new('ShaderNodeBackground');bg.inputs[0].default_value=(.78,.77,.74,1);lp=nt.nodes.new('ShaderNodeLightPath');mix=nt.nodes.new('ShaderNodeMixShader');nt.links.new(lp.outputs['Is Camera Ray'],mix.inputs[0]);nt.links.new(old,mix.inputs[1]);nt.links.new(bg.outputs[0],mix.inputs[2]);nt.links.new(mix.outputs[0],out.inputs[0])
 scene.render.resolution_x=900;scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.cycles.samples=32;scene.render.film_transparent=False
 scene.render.image_settings.media_type='IMAGE';scene.render.image_settings.views_format='INDIVIDUAL';scene.render.image_settings.file_format='JPEG';scene.render.image_settings.color_mode='RGB';scene.render.image_settings.quality=95
 if '--neutral' in sys.argv:
  for mat in bpy.data.materials:
   if mat.use_nodes:
    for node in mat.node_tree.nodes:
     if node.type=='BSDF_PRINCIPLED':
      for link in list(node.inputs['Base Color'].links):mat.node_tree.links.remove(link)
      node.inputs['Base Color'].default_value=(.45,.45,.45,1)
 for strength in [0,1]:
  for mat in bpy.data.materials:
   if mat.use_nodes:
    for n in mat.node_tree.nodes:
     if n.type=='NORMAL_MAP':n.inputs['Strength'].default_value=strength
  scene.render.filepath=str(OUT/(ident+('_Neutral' if '--neutral' in sys.argv else '')+('_Normal_On.jpg' if strength else '_Normal_Off.jpg')));bpy.ops.render.render(write_still=True)
