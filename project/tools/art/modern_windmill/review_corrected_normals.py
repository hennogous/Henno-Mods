"""Diagnostic render suite from saved AE assemblies and converted normal textures."""
import bpy,sys,json,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[4];O=Path.home()/'Desktop/Codex/modern-normal-correction-20261027'
sys.path.insert(0,str(ROOT/'project/tools/blender'))
from ae_asset_render_blender import Builder
tag=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'wind'
ident='CSC_BAKERS_Wind_Mill_Modern' if tag=='wind' else 'CSC_BAKERS_Water_Mill_Modern'
jf=max((O/'render'/ident).glob('*/job.json'),key=lambda p:p.stat().st_mtime);basejob=json.loads(jf.read_text())
for variant in ('B-only','neutral-off-A','neutral-on-A','neutral-off-B','neutral-on-B','combined'):
 bpy.ops.wm.read_factory_settings(use_empty=True);job=dict(basejob);folder=O/'diagnostics'/tag/variant;folder.mkdir(parents=True,exist_ok=True);job['output']=str(folder)
 b=Builder(job,'icon');b.assemble(job['root'],root=True)
 if tag=='wind':b.clip_foundation()
 bpy.context.view_layer.update();b.setup();s=b.scene;s.cycles.samples=24;s.render.resolution_x=s.render.resolution_y=900;s.render.resolution_percentage=100
 if tag=='water':
  cam=s.camera;target=Vector((-22,0,13));cam.data.type='ORTHO';cam.data.ortho_scale=200;cam.data.shift_x=cam.data.shift_y=0;cam.location=target+Vector((175,-255,170));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
 else:s.camera.data.lens*=.9
 if variant.startswith('neutral'):
  for mat in b.materials.values():
   ns=mat.node_tree.nodes;ls=mat.node_tree.links;bs=next(n for n in ns if n.type=='BSDF_PRINCIPLED')
   for name in ('Base Color','Roughness','Metallic'):
    for l in list(bs.inputs[name].links):ls.remove(l)
   bs.inputs['Base Color'].default_value=(.32,.32,.32,1);bs.inputs['Roughness'].default_value=.85;bs.inputs['Metallic'].default_value=0
   if '-off-' in variant:
    for l in list(bs.inputs['Normal'].links):ls.remove(l)
  for o in list(s.objects):
   if o.type=='LIGHT':bpy.data.objects.remove(o,do_unlink=True)
  ld=bpy.data.lights.new('Diagnostic_Sun','SUN');ld.energy=2;ld.angle=math.radians(6);lo=bpy.data.objects.new('Diagnostic_Sun',ld);s.collection.objects.link(lo)
  direction=Vector((-240,-280,160) if variant.endswith('A') else (250,180,160));lo.rotation_euler=(-direction).to_track_quat('-Z','Y').to_euler()
  for n in s.world.node_tree.nodes:
   if n.type=='BACKGROUND':n.inputs['Color'].default_value=(1,1,1,1);n.inputs['Strength'].default_value=.18
 if variant=='B-only':
  for mat in b.materials.values():
   ns=mat.node_tree.nodes;ls=mat.node_tree.links;out=next(n for n in ns if n.type=='OUTPUT_MATERIAL');tex=next((n for n in ns if n.type=='TEX_IMAGE' and n.label=='BaseColor'),None)
   em=ns.new('ShaderNodeEmission');em.inputs['Strength'].default_value=1
   if tex:ls.new(tex.outputs['Color'],em.inputs['Color'])
   ls.new(em.outputs[0],out.inputs['Surface'])
 s.use_nodes=False;s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.image_settings.color_depth='8';s.render.filepath=str(O/'diagnostics'/(tag+'-'+variant+'.png'));bpy.ops.render.render(write_still=True);print('REVIEW',tag,variant,flush=True)
