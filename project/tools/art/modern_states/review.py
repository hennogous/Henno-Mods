"""Reconstruct staged native ASTs for exact worked/construction/pillaged comparison."""
import sys,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];OUT=Path.home()/'Desktop/Codex/modern-l1-states-20261028';sys.path.insert(0,str(ROOT/'project/tools/blender'))
IDS=('CSC_Level_1_S_Modern','CSC_BAKERS_Wind_Mill_Modern','CSC_BAKERS_Water_Mill_Modern')
def prepare():
 from render_ae_asset import Resolver,Assembly,DEFAULT_SDK,prepare_geometry,PRESETS
 r=Resolver(ROOT/'Civ Supply Chains',DEFAULT_SDK)
 for p in (OUT/'staged').rglob('*'):
  if p.is_file():r.index[p.name.casefold()]={p}
 for ident in IDS:
  for state in ('Worked','Construction','Pillaged'):
   a=Assembly(r,state);root=a.asset(OUT/'staged/Assets'/(ident+'.ast'));run=OUT/'review'/ident/state;run.mkdir(parents=True,exist_ok=True)
   def visible(key):return any(m['groups'] for m in a.assets[key]['models']) or any(visible(x['asset']) for x in a.assets[key]['attachments'])
   for record in a.assets.values():record['attachments']=[x for x in record['attachments'] if visible(x['asset'])]
   prepare_geometry(a,OUT/'render-cache',run)
   job={'root':root,'assets':a.assets,'geometries':a.geometries,'materials':a.materials,'excluded':a.excluded,'warnings':a.warnings,'settings':{'presets':PRESETS,'resolution':700,'samples':24,'camera_class':'auto','render_emission_enabled':False,'state':state},'output':str(run)}
   (run/'job.json').write_text(json.dumps(job,indent=2));print('PREPARED',ident,state,flush=True)
def render():
 import bpy,bmesh
 from mathutils import Matrix,Vector
 from ae_asset_render_blender import Builder
 F=Matrix.Rotation(math.radians(42.3),4,'Z')@Matrix.Translation(Vector((-101,-126,0)))
 for ident in IDS:
  for state in ('Worked','Construction','Pillaged'):
   if state in ('Worked','Pillaged') and (OUT/'review'/ident/state/'render.png').exists():continue
   run=OUT/'review'/ident/state;job=json.loads((run/'job.json').read_text());bpy.ops.wm.read_factory_settings(use_empty=True);b=Builder(job,'icon');b.assemble(job['root'],root=True);bpy.context.view_layer.update();b.clip_foundation()
   for ob,rec in zip(b.objects,b.mapping):
    if rec['root'] and rec['material']=='Pillage_Construction_01':
     bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=ob.matrix_world.inverted()@Vector((0,0,0)),plane_no=Vector((0,0,1)),clear_inner=True);bm.to_mesh(ob.data);bm.free()
   b.setup();s=b.scene
   if ident==IDS[2]:target=Vector((-34,-3,28));direction=Vector((-180,-260,200));scale=210
   else:target=F@Vector((0,-42 if ident==IDS[1] else -20,35));direction=F.to_3x3()@Vector((-180,-260,200));scale=215 if ident==IDS[1] else 175
   cam=s.camera;cam.data.type='ORTHO';cam.data.ortho_scale=scale;cam.location=target+direction;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();s.use_nodes=False;s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.image_settings.color_depth='8';s.render.filepath=str(run/'render.png');bpy.ops.render.render(write_still=True)
   bpy.ops.wm.save_as_mainfile(filepath=str(run/'review.blend'));print('RENDERED',ident,state,flush=True)
if __name__=='__main__':
 if '--' in sys.argv:render()
 else:prepare()
