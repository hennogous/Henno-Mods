"""Compare stand footprints and complete saved ASTs without changing placements."""
import sys,json,math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from display_depth import ROOT,O,ID,dump
sys.path.insert(0,str(ROOT/'project/tools/blender'))
JOBS=[('historical','CSC_BAKERS_Bakery_2',False),('before','CSC_BAKERS_Bakery_Modern_2',False),('after','CSC_BAKERS_Bakery_Modern_2',True)]
def prepare():
 from render_ae_asset import Resolver,Assembly,DEFAULT_SDK,prepare_geometry,PRESETS
 for label,ident,staged in JOBS:
  r=Resolver(ROOT/'Civ Supply Chains',DEFAULT_SDK)
  if staged:
   for p in (O/'staged').rglob('*'):
    if p.is_file():r.index[p.name.casefold()]={p}
  a=Assembly(r,'Worked');key=a.asset((O/'staged' if staged else ROOT/'Civ Supply Chains')/'Assets'/(ident+'.ast'));run=O/'review'/label;run.mkdir(parents=True,exist_ok=True);prepare_geometry(a,O/'render-cache',run)
  camera=json.loads((ROOT/'project/tools/blender/ae_render_camera_presets.json').read_text())['classes']['L2'];camera['icon']['lens']*=.82
  settings={'presets':PRESETS,'resolution':1000,'samples':40,'camera_class':'L2','fixed_camera':camera,'render_emission_enabled':False,'state':'Worked'}
  dump(run/'job.json',{'root':key,'assets':a.assets,'geometries':a.geometries,'materials':a.materials,'excluded':a.excluded,'warnings':a.warnings,'settings':settings,'output':str(run)})
def render():
 import bpy
 from mathutils import Matrix,Vector
 from ae_asset_render_blender import Builder
 frame=Matrix.Rotation(.626573,4,'Z');target=frame.inverted()@Vector((-86,-132,13));direction=frame.inverted().to_3x3()@Vector((65,-100,90));measurements={}
 for label,ident,staged in JOBS:
  run=O/'review'/label;job=json.loads((run/'job.json').read_text());bpy.ops.wm.read_factory_settings(use_empty=True);b=Builder(job,'icon');b.assemble(job['root'],root=True);bpy.context.view_layer.update();b.clip_foundation();b.setup();s=b.scene;s.use_nodes=False;s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.image_settings.color_depth='8';s.render.filepath=str(run/'scene.png')
  if not (run/'scene.png').exists():bpy.ops.render.render(write_still=True)
  selected=[]
  for ob in b.objects:
   path=ob.get('ae_semantic_path','');keep=('/CSC_ALL_Stand/' in path or '/DIS_COM_Table/' in path) if label=='historical' else '/CSC_Attach_Display/' in path
   ob.hide_render=not keep
   if keep:selected.append(ob)
  pts=[frame@ob.matrix_world@v.co for ob in selected for v in ob.data.vertices];bounds=[[min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]];measurements[label]=bounds
  cam=s.camera;cam.data.type='ORTHO';cam.data.ortho_scale=85;cam.location=target+direction;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(run/'stand.png');bpy.ops.render.render(write_still=True)
  cam.data.ortho_scale=65;cam.location=target+Vector((0,0,120));cam.rotation_euler=frame.inverted().to_euler();cam.rotation_euler.x=0;cam.rotation_euler.y=0;cam.rotation_euler.z=-.626573;s.render.filepath=str(run/'top.png')
  if not (run/'top.png').exists():bpy.ops.render.render(write_still=True)
  bpy.ops.wm.save_as_mainfile(filepath=str(run/'review.blend'));print('RENDERED',label,flush=True)
 dump(O/'render-measurements.json',measurements)
 assert abs((measurements['after'][1][0]-measurements['after'][0][0])-(measurements['before'][1][0]-measurements['before'][0][0]))<.001
 assert abs((measurements['after'][1][1]-measurements['after'][0][1])-(measurements['historical'][1][1]-measurements['historical'][0][1]))<.001
 assert abs(measurements['after'][1][1]-measurements['before'][1][1])<.001
if __name__=='__main__':render() if '--' in sys.argv else prepare()
