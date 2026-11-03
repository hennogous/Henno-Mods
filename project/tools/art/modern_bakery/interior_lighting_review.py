"""Saved-AST daylight and explicitly emissive night diagnostics."""
import sys,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];O=Path.home()/'Desktop/Codex/modern-interior-lighting-20261028';sys.path.insert(0,str(ROOT/'project/tools/blender'))
SPECS=['before-day','after-day','after-night']
def prepare():
 from render_ae_asset import Resolver,Assembly,DEFAULT_SDK,prepare_geometry,PRESETS
 for label in SPECS:
  r=Resolver(ROOT/'Civ Supply Chains',DEFAULT_SDK)
  if label!='before-day':
   for p in (O/'staged').rglob('*'):
    if p.is_file():r.index[p.name.casefold()]={p}
  path=(ROOT/'Civ Supply Chains' if label=='before-day' else O/'staged')/'Assets/CSC_BAKERS_Bakery_Modern_2.ast'
  a=Assembly(r,'Worked');key=a.asset(path);run=O/'review'/label;run.mkdir(parents=True,exist_ok=True)
  prepare_geometry(a,O/'render-cache',run)
  settings={'presets':PRESETS,'resolution':1000,'samples':40,'camera_class':'L2','fixed_camera':json.loads((ROOT/'project/tools/blender/ae_render_camera_presets.json').read_text())['classes']['L2'],'render_emission_enabled':False,'state':'Worked'}
  job={'root':key,'assets':a.assets,'geometries':a.geometries,'materials':a.materials,'excluded':a.excluded,'warnings':a.warnings,'settings':settings,'output':str(run)}
  (run/'job.json').write_text(json.dumps(job,indent=2))
def render():
 import bpy
 from ae_asset_render_blender import Builder
 for label in SPECS:
  run=O/'review'/label;job=json.loads((run/'job.json').read_text());bpy.ops.wm.read_factory_settings(use_empty=True);b=Builder(job,'icon');b.assemble(job['root'],root=True);bpy.context.view_layer.update();b.clip_foundation();b.setup();s=b.scene
  if label=='after-night':
   for mat in bpy.data.materials:
    matches=[v for v in job['materials'].values() if v['id']==mat.get('ae_material')]
    if not matches or not matches[0]['textures'].get('Emissive'):continue
    spec=matches[0]['textures']['Emissive'];nodes,links=mat.node_tree.nodes,mat.node_tree.links
    bs=next(n for n in nodes if n.type=='BSDF_PRINCIPLED');uv=nodes.new('ShaderNodeUVMap');uv.uv_map='UV3';im=nodes.new('ShaderNodeTexImage');im.image=b.image(spec,'Emissive')
    links.new(uv.outputs['UV'],im.inputs['Vector']);links.new(im.outputs['Color'],bs.inputs['Emission Color']);bs.inputs['Emission Strength'].default_value=1
   for light in bpy.data.lights:light.energy*=0.055;light.color=(0.57,0.68,1)
   bg=next(n for n in s.world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs['Color'].default_value=(0.2,0.3,0.55,1);bg.inputs['Strength'].default_value=0.12
  s.use_nodes=False;s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.image_settings.color_depth='8';s.render.filepath=str(run/'render.png');bpy.ops.render.render(write_still=True);bpy.ops.wm.save_as_mainfile(filepath=str(run/'review.blend'));print('RENDERED',label,flush=True)
if __name__=='__main__':render() if '--' in sys.argv else prepare()
