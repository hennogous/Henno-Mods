"""Day/night review of the actual saved placement-refined Bakery assemblies."""
import bpy,json,sys,copy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];O=Path.home()/'Desktop/Codex/modern-bakery-placement-20261028';sys.path.insert(0,str(ROOT/'project/tools/blender'))
from ae_asset_render_blender import Builder
for ident in ('CSC_BAKERS_Bakery_Modern','CSC_BAKERS_Bakery_Modern_2','CSC_BAKERS_Bakery_2'):
 for mode in (('day',) if ident=='CSC_BAKERS_Bakery_2' else ('day','night')):
  run=O/ident/mode;run.mkdir(exist_ok=True);job=json.loads((O/ident/'job.json').read_text());job['output']=str(run)
  bpy.ops.wm.read_factory_settings(use_empty=True);b=Builder(job,'icon');b.assemble(job['root'],root=True);bpy.context.view_layer.update();b.clip_foundation();b.setup();s=b.scene
  if mode=='night':
   for mat in bpy.data.materials:
    matches=[v for v in job['materials'].values() if v['id']==mat.get('ae_material')]
    if not matches or not matches[0]['textures'].get('Emissive'):continue
    spec=matches[0]['textures']['Emissive'];nodes,links=mat.node_tree.nodes,mat.node_tree.links
    bs=next(n for n in nodes if n.type=='BSDF_PRINCIPLED');uv=nodes.new('ShaderNodeUVMap');uv.uv_map='UV3';im=nodes.new('ShaderNodeTexImage');im.image=b.image(spec,'Emissive')
    links.new(uv.outputs['UV'],im.inputs['Vector']);links.new(im.outputs['Color'],bs.inputs['Emission Color']);bs.inputs['Emission Strength'].default_value=1
   for light in bpy.data.lights:light.energy*=.055;light.color=(.57,.68,1)
   bg=next(n for n in s.world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs['Color'].default_value=(.2,.3,.55,1);bg.inputs['Strength'].default_value=.12
  s.use_nodes=False;s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.image_settings.color_depth='8';s.render.filepath=str(run/'render.png');bpy.ops.render.render(write_still=True)
  bpy.ops.wm.save_as_mainfile(filepath=str(run/'review.blend'));print('RENDERED',ident,mode,flush=True)
