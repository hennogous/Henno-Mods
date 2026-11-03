"""User-requested emission preview; production icon renderer stays unmodified."""
import bpy,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
O=Path(sys.argv[sys.argv.index('--')+1]) if '--' in sys.argv else Path.home()/'Desktop/Codex/modern-normal-correction-20261027/emissive'
sys.path.insert(0,str(ROOT/'project/tools/blender'))
from ae_asset_render_blender import Builder
ident='CSC_BAKERS_Wind_Mill_Modern'
jf=max((O/'render'/ident).glob('*/job.json'),key=lambda p:p.stat().st_mtime)
job=json.loads(jf.read_text());job['output']=str(O/'review');Path(job['output']).mkdir(exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
b=Builder(job,'icon');b.assemble(job['root'],root=True);b.clip_foundation();bpy.context.view_layer.update();b.setup();s=b.scene
for (key,uvcount),m in b.materials.items():
 if m['ae_material']!='CSC_BAKERS_Modern':continue
 nodes,links=m.node_tree.nodes,m.node_tree.links
 uv=nodes.new('ShaderNodeUVMap');uv.uv_map='UV3'
 tex=nodes.new('ShaderNodeTexImage');tex.image=b.image(job['materials'][key]['textures']['Emissive'],'Emissive')
 bs=next(n for n in nodes if n.type=='BSDF_PRINCIPLED')
 links.new(uv.outputs['UV'],tex.inputs['Vector']);links.new(tex.outputs['Color'],bs.inputs['Emission Color']);bs.inputs['Emission Strength'].default_value=2
s.camera.data.lens*=.78;s.cycles.samples=32;s.render.resolution_x=s.render.resolution_y=1024;s.render.resolution_percentage=100
layer=s.view_layers[0];layer.use_pass_emit=True;layer.update_render_passes()
g=bpy.data.node_groups.new('Subtle_window_glow','CompositorNodeTree');s.compositing_node_group=g
g.interface.new_socket(name='Image',in_out='OUTPUT',socket_type='NodeSocketColor')
r=g.nodes.new('CompositorNodeRLayers');r.scene=s
gl=g.nodes.new('CompositorNodeGlare');gl.inputs['Type'].default_value='Fog Glow';gl.inputs['Quality'].default_value='High'
print('GLARE_INPUTS',[(x.name,str(x.default_value)) for x in gl.inputs if hasattr(x,'default_value')],flush=True)
gl.inputs['Threshold'].default_value=.05
if gl.inputs.get('Size'):gl.inputs['Size'].default_value=.12
g.links.new(r.outputs.get('Emission') or r.outputs.get('Emit'),gl.inputs['Image'])
print('GLARE_OUTPUTS',[x.name for x in gl.outputs],flush=True)
mix=g.nodes.new('ShaderNodeMixRGB');mix.blend_type='ADD';mix.inputs[0].default_value=.12
g.links.new(r.outputs['Image'],mix.inputs[1]);g.links.new(gl.outputs.get('Glare') or gl.outputs['Image'],mix.inputs[2])
out=g.nodes.new('NodeGroupOutput');g.links.new(mix.outputs[0],out.inputs['Image'])
s.use_nodes=True;s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.image_settings.color_depth='8'
s.render.filepath=str(O/'review/Modern_Soft_Glow.png');bpy.ops.render.render(write_still=True)
