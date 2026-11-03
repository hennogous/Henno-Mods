"""Review the actual staged ASTs in fixed historical L2 coordinates."""
import sys,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];O=Path.home()/'Desktop/Codex/modern-bakery-ae-20261028';sys.path.insert(0,str(ROOT/'project/tools/blender'))
SPECS=[('CSC_BAKERS_Bakery_Modern','Worked'),('CSC_BAKERS_Bakery_Modern_2','Worked'),('CSC_BAKERS_Bakery_Modern','Construction'),('CSC_BAKERS_Bakery_Modern','Pillaged')]
def prepare():
 from render_ae_asset import Resolver,Assembly,DEFAULT_SDK,prepare_geometry,PRESETS
 r=Resolver(ROOT/'Civ Supply Chains',DEFAULT_SDK)
 for p in (O/'staged').rglob('*'):
  if p.is_file():r.index[p.name.casefold()]={p}
 for ident,state in SPECS:
  a=Assembly(r,state);key=a.asset(O/'staged/Assets'/(ident+'.ast'));run=O/'native-review'/ident/state;run.mkdir(parents=True,exist_ok=True)
  def visible(key):return any(m['groups'] for m in a.assets[key]['models']) or any(visible(x['asset']) for x in a.assets[key]['attachments'])
  for record in a.assets.values():record['attachments']=[x for x in record['attachments'] if visible(x['asset'])]
  prepare_geometry(a,O/'render-cache',run)
  settings={'presets':PRESETS,'resolution':900,'samples':24,'camera_class':'L2','fixed_camera':json.loads((ROOT/'project/tools/blender/ae_render_camera_presets.json').read_text())['classes']['L2'],'render_emission_enabled':False,'state':state}
  job={'root':key,'assets':a.assets,'geometries':a.geometries,'materials':a.materials,'excluded':a.excluded,'warnings':a.warnings,'settings':settings,'output':str(run)}
  (run/'job.json').write_text(json.dumps(job,indent=2));print('PREPARED',ident,state,flush=True)
def render():
 import bpy
 from ae_asset_render_blender import Builder
 for ident,state in SPECS:
  if (O/'native-review'/ident/state/'render.png').exists():continue
  run=O/'native-review'/ident/state;job=json.loads((run/'job.json').read_text());bpy.ops.wm.read_factory_settings(use_empty=True);b=Builder(job,'icon');b.assemble(job['root'],root=True);bpy.context.view_layer.update();b.clip_foundation();b.setup();s=b.scene
  s.use_nodes=False;s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.image_settings.color_depth='8';s.render.filepath=str(run/'render.png');bpy.ops.render.render(write_still=True);bpy.ops.wm.save_as_mainfile(filepath=str(run/'review.blend'));print('RENDERED',ident,state,flush=True)
if __name__=='__main__':
 if '--' in sys.argv:render()
 else:prepare()
