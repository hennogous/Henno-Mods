import bpy,sys,json
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).parent))
from build_bakery_props import SOURCE,OUT,V
p=SOURCE/'CSC_BAKERS_Bread_Cart.blend'
with V.suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(p),load_ui=False,use_scripts=False)
s=bpy.data.scenes['Review'];bpy.context.window.scene=s;s.render.resolution_x=600;s.render.resolution_y=600;s.render.film_transparent=False
nt=s.world.node_tree;out=next(n for n in nt.nodes if n.type=='OUTPUT_WORLD');old=out.inputs[0].links[0].from_socket;bg=nt.nodes.new('ShaderNodeBackground');bg.inputs[0].default_value=(.75,.74,.7,1);bg.inputs[1].default_value=1;lp=nt.nodes.new('ShaderNodeLightPath');mix=nt.nodes.new('ShaderNodeMixShader');nt.links.new(lp.outputs['Is Camera Ray'],mix.inputs[0]);nt.links.new(old,mix.inputs[1]);nt.links.new(bg.outputs[0],mix.inputs[2]);nt.links.new(mix.outputs[0],out.inputs[0])
center=Vector((5,0,16));s.camera.data.ortho_scale=65
for label,direction in [('hero',(1.2,-1.6,1.1)),('top',(0,0,2)),('rear',(-1.5,1.5,.7)),('side',(0,-2,.1))]:
 s.camera.location=center+Vector(direction)*50;s.camera.rotation_euler=(center-s.camera.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(OUT/('cart-'+label+'.png'));bpy.ops.render.render(write_still=True)
print('CART MULTIVIEW READY')
