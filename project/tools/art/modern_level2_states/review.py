"""Native saved-AST review with fixed L2 icon camera and unlit AO diagnostics."""
import sys,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];O=Path.home()/'Desktop/Codex/modern-l2-states-20261029';sys.path.insert(0,str(ROOT/'project/tools/blender'))
BASE='CSC_Level_2_Modern';JOBS=[(BASE,s) for s in ('Worked','Construction','Pillaged')]+[('CSC_BAKERS_Bakery_Modern_2','Pillaged')]
def prepare():
 from render_ae_asset import Resolver,Assembly,DEFAULT_SDK,prepare_geometry,PRESETS
 r=Resolver(ROOT/'Civ Supply Chains',DEFAULT_SDK)
 for p in (O/'staged').rglob('*'):
  if p.is_file():r.index[p.name.casefold()]={p}
 camera=json.loads((ROOT/'project/tools/blender/ae_render_camera_presets.json').read_text())['classes']['L2']
 for ident,state in JOBS:
  a=Assembly(r,state);key=a.asset(O/'staged/Assets'/(ident+'.ast'))
  def visible(k):return any(m['groups'] for m in a.assets[k]['models']) or any(visible(x['asset']) for x in a.assets[k]['attachments'])
  for rec in a.assets.values():rec['attachments']=[x for x in rec['attachments'] if visible(x['asset'])]
  folder=O/'review'/ident/state;folder.mkdir(parents=True,exist_ok=True);prepare_geometry(a,O/'render-cache',folder)
  job={'root':key,'assets':a.assets,'geometries':a.geometries,'materials':a.materials,'warnings':a.warnings,'excluded':a.excluded,'settings':{'presets':PRESETS,'resolution':950,'samples':40,'camera_class':'L2','fixed_camera':camera,'render_emission_enabled':False,'state':state},'output':str(folder)}
  (folder/'job.json').write_text(json.dumps(job,indent=2));print('PREPARED',ident,state,flush=True)
def render():
 import bpy,bmesh
 from mathutils import Vector
 from ae_asset_render_blender import Builder
 for ident,state in JOBS:
  folder=O/'review'/ident/state;job=json.loads((folder/'job.json').read_text());bpy.ops.wm.read_factory_settings(use_empty=True);b=Builder(job,'icon');b.assemble(job['root'],root=True);bpy.context.view_layer.update();b.clip_foundation()
  for ob,rec in zip(b.objects,b.mapping):
   if rec['root'] and rec['material']=='Pillage_Construction_01':
    bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=ob.matrix_world.inverted()@Vector((0,0,0)),plane_no=Vector((0,0,1)),clear_inner=True);bm.to_mesh(ob.data);bm.free()
  b.setup();s=b.scene;s.use_nodes=False;s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.image_settings.color_depth='8';s.render.filepath=str(folder/'render.png');bpy.ops.render.render(write_still=True)
  bpy.ops.wm.save_as_mainfile(filepath=str(folder/'review.blend'))
  if ident==BASE and state=='Pillaged':
   for mat in b.materials.values():
    ns=mat.node_tree.nodes;links=mat.node_tree.links;out=next(n for n in ns if n.type=='OUTPUT_MATERIAL');em=ns.new('ShaderNodeEmission');em.inputs['Color'].default_value=(1,1,1,1);em.inputs['Strength'].default_value=1;ao=next((n for n in ns if n.type=='TEX_IMAGE' and n.label=='AO'),None)
    if ao:
     split=ns.new('ShaderNodeSeparateColor');split.mode='RGB';links.new(ao.outputs['Color'],split.inputs[0]);links.new(split.outputs['Red'],em.inputs['Color'])
    links.new(em.outputs[0],out.inputs['Surface'])
   s.render.filepath=str(folder/'AO-front.png');bpy.ops.render.render(write_still=True)
   from mathutils import Matrix
   T=Matrix(json.loads((O/'authoring.json').read_text())['frame']);target=T@Vector((0,0,42));cam=s.camera;direction=T.to_3x3()@Vector((-180,250,200));cam.data.type='ORTHO';cam.data.ortho_scale=170;cam.location=target+direction;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(folder/'AO-back.png');bpy.ops.render.render(write_still=True)
  print('RENDERED',ident,state,flush=True)
if __name__=='__main__':render() if '--' in sys.argv else prepare()
