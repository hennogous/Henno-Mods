"""Matched review framing from saved assemblies; production camera presets untouched."""
import bpy,sys,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];O=Path(sys.argv[sys.argv.index('--')+1]) if '--' in sys.argv else Path.home()/'Desktop/Codex/modern-kit-refinement-20261027'
sys.path.insert(0,str(ROOT/'project/tools/blender'))
from ae_asset_render_blender import Builder
for ident,folder in [('CSC_BAKERS_Wind_Mill','historical-render'),('CSC_BAKERS_Wind_Mill_Modern','render')]:
 jf=max((O/folder/ident).glob('*/job.json'),key=lambda p:p.stat().st_mtime);job=json.loads(jf.read_text());job['output']=str(O/'comparison-review'/ident)
 Path(job['output']).mkdir(parents=True,exist_ok=True)
 bpy.ops.wm.read_factory_settings(use_empty=True);b=Builder(job,'icon');b.assemble(job['root'],root=True);b.clip_foundation();bpy.context.view_layer.update();b.setup();s=b.scene
 s.camera.data.lens*=.78;s.cycles.samples=32;s.render.resolution_x=s.render.resolution_y=1024;s.render.resolution_percentage=100
 s.use_nodes=False;s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.image_settings.color_depth='8';s.render.filepath=str(O/'images'/(ident+'_Comparison.png'));bpy.ops.render.render(write_still=True)
