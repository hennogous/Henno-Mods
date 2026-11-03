import sys,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT/'project/tools/blender'));O=Path.home()/'Desktop/Codex/modern-l1-ao-fix-20261028';WIND='CSC_BAKERS_Wind_Mill_Modern';WATER='CSC_BAKERS_Water_Mill_Modern'
def prepare():
 from render_ae_asset import Resolver,Assembly,DEFAULT_SDK,prepare_geometry,PRESETS
 for tag,ident,staged in [('before',WIND,False),('after',WIND,True),('water',WATER,True)]:
  r=Resolver(ROOT/'Civ Supply Chains',DEFAULT_SDK)
  if staged:
   for p in (O/'staged').rglob('*'):
    if p.is_file():r.index[p.name.casefold()]={p}
  a=Assembly(r,'Construction');root=a.asset((O/'staged' if staged else ROOT/'Civ Supply Chains')/'Assets'/(ident+'.ast'))
  def visible(key):return any(m['groups'] for m in a.assets[key]['models']) or any(visible(x['asset']) for x in a.assets[key]['attachments'])
  for record in a.assets.values():record['attachments']=[x for x in record['attachments'] if visible(x['asset'])]
  folder=O/'review'/tag;folder.mkdir(parents=True,exist_ok=True);prepare_geometry(a,O/'render-cache',folder)
  job={'root':root,'assets':a.assets,'geometries':a.geometries,'materials':a.materials,'warnings':a.warnings,'excluded':a.excluded,'settings':{'presets':PRESETS,'resolution':850,'samples':32,'camera_class':'auto'},'output':str(folder)};(folder/'job.json').write_text(json.dumps(job,indent=2))
def render():
 import bpy,bmesh
 from mathutils import Matrix,Vector
 from ae_asset_render_blender import Builder
 F=Matrix.Rotation(math.radians(42.3),4,'Z')@Matrix.Translation(Vector((-101,-126,0)))
 for tag in ('before','after','water'):
  folder=O/'review'/tag;job=json.loads((folder/'job.json').read_text());bpy.ops.wm.read_factory_settings(use_empty=True);b=Builder(job,'icon');b.assemble(job['root'],root=True);bpy.context.view_layer.update();b.clip_foundation();b.setup();s=b.scene
  for ob,rec in zip(b.objects,b.mapping):
   if rec['root'] and rec['material']=='Pillage_Construction_01':
    bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=ob.matrix_world.inverted()@Vector((0,0,0)),plane_no=Vector((0,0,1)),clear_inner=True);bm.to_mesh(ob.data);bm.free()
  target=Vector((-34,-3,28)) if tag=='water' else F@Vector((0,-42,35));direction=Vector((-180,-260,200));direction=direction if tag=='water' else F.to_3x3()@direction;cam=s.camera;cam.data.type='ORTHO';cam.data.ortho_scale=210;cam.location=target+direction;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();s.use_nodes=False;s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.image_settings.color_depth='8'
  if tag=='after':s.render.filepath=str(folder/'colour.png');bpy.ops.render.render(write_still=True)
  for mat in b.materials.values():
   ns=mat.node_tree.nodes;links=mat.node_tree.links;output=next(n for n in ns if n.type=='OUTPUT_MATERIAL');emit=ns.new('ShaderNodeEmission');emit.inputs['Color'].default_value=(1,1,1,1);emit.inputs['Strength'].default_value=1;ao=next((n for n in ns if n.type=='TEX_IMAGE' and n.label=='AO'),None)
   if ao:
    split=ns.new('ShaderNodeSeparateColor');split.mode='RGB';links.new(ao.outputs['Color'],split.inputs[0]);links.new(split.outputs['Red'],emit.inputs['Color'])
   links.new(emit.outputs[0],output.inputs['Surface'])
  s.render.filepath=str(folder/'AO-only.png');bpy.ops.render.render(write_still=True)
  if tag=='after':
   direction=F.to_3x3()@Vector((180,260,200));cam.location=target+direction;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(folder/'AO-back.png');bpy.ops.render.render(write_still=True)
if __name__=='__main__':render() if '--' in sys.argv else prepare()
