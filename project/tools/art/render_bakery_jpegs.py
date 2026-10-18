"""Fresh Blender JPEG reviews with a camera-only neutral background."""
import bpy,sys
from pathlib import Path
root=Path(sys.argv[sys.argv.index('--')+1]);pairs=[]
for parent in ([] if '--closeups-only' in sys.argv else ['CSC_BAKERS_Bakery_2'] if '--alternate-only' in sys.argv else ['CSC_BAKERS_Bakery'] if '--standard-only' in sys.argv else ['CSC_BAKERS_Bakery','CSC_BAKERS_Bakery_2']):
 search=root/('review-alternate' if parent.endswith('_2') else 'review-standard') if (root/'review-standard').exists() or (root/'review-alternate').exists() else root
 candidates=list(search.rglob(parent+'_sv.blend'));assert len(candidates)==1,candidates;pairs.append((candidates[0],root/(parent+'_Review.jpg')))
sys.path.insert(0,str(Path(__file__).parent))
from bakery_props_atlas import SOURCE
source=SOURCE/'CSC_BAKERS_Bakery_Prop_Kit.blend'
if '--alternate-only' not in sys.argv and '--standard-only' not in sys.argv and '--closeups-only' not in sys.argv:pairs.append((source,root/'Bakery_Prop_Kit_Review.jpg'))
if '--closeups-only' in sys.argv:
 for ident in ['CSC_BAKERS_Bread_Basket_Round','CSC_BAKERS_Bread_Cart']:pairs.append((SOURCE/(ident+'.blend'),root/(ident+'_Review.jpg')))
for path,dest in pairs:
 bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False);scene=bpy.data.scenes.get('Review') or bpy.context.scene;bpy.context.window.scene=scene
 if scene.world and scene.world.use_nodes:
  nt=scene.world.node_tree;out=next(n for n in nt.nodes if n.type=='OUTPUT_WORLD');old=out.inputs[0].links[0].from_socket;bg=nt.nodes.new('ShaderNodeBackground');bg.inputs[0].default_value=(.78,.77,.74,1);bg.inputs[1].default_value=1;lp=nt.nodes.new('ShaderNodeLightPath');mix=nt.nodes.new('ShaderNodeMixShader');nt.links.new(lp.outputs['Is Camera Ray'],mix.inputs[0]);nt.links.new(old,mix.inputs[1]);nt.links.new(bg.outputs[0],mix.inputs[2]);nt.links.new(mix.outputs[0],out.inputs[0])
 scene.render.film_transparent=False;scene.render.use_multiview=False
 scene.render.image_settings.media_type='IMAGE'
 scene.render.image_settings.views_format='INDIVIDUAL'
 scene.render.image_settings.file_format='JPEG';scene.render.image_settings.color_mode='RGB';scene.render.image_settings.quality=95;scene.render.filepath=str(dest);bpy.ops.render.render(write_still=True)
 print('FRESH JPEG',dest)
