import bpy,sys,json,hashlib
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).parent))
from build_bakery_props import *
path=SOURCE/'CSC_BAKERS_Oven_v2.blend'
with V.suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
mesh=next(o for o in bpy.data.scenes['Export'].objects if o.type=='MESH')
for mat in mesh.data.materials:
 nt=mat.node_tree;bs=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED');uv=nt.nodes.new('ShaderNodeUVMap');uv.name='Legacy_Emission_UV3';uv.uv_map=mesh.data.uv_layers[2].name
 tex=nt.nodes.new('ShaderNodeTexImage');tex.name='Legacy_Coals_Emission';tex.image=bpy.data.images.load(str(SOURCE/'textures/CSC_Atlas_E.png'),check_existing=True);tex.image.colorspace_settings.name='sRGB';nt.links.new(uv.outputs['UV'],tex.inputs['Vector']);nt.links.new(tex.outputs['Color'],bs.inputs['Emission Color']);bs.inputs['Emission Strength'].default_value=1
for s in bpy.data.scenes:s['runtime_emissive_texture']='CSC_Atlas_E'
bpy.ops.file.make_paths_relative();bpy.ops.wm.save_as_mainfile(filepath=str(path))
with V.suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
r=V.validate_current_scene();r['source_sha256']=hashlib.sha256(path.read_bytes()).hexdigest();assert r['automated_pass'];(OUT/'CSC_BAKERS_Oven_v2-validation.json').write_text(json.dumps(r,indent=2));e=json.loads((OUT/'CSC_BAKERS_Oven_v2-export.json').read_text());e['source_sha256']=r['source_sha256'];(OUT/'CSC_BAKERS_Oven_v2-export.json').write_text(json.dumps(e,indent=2))
s=bpy.data.scenes['Review'];bpy.context.window.scene=s;center=Vector((0,0,43));s.camera.location=center+Vector((-130,-180,95));s.camera.rotation_euler=(center-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=120;s.render.resolution_x=850;s.render.resolution_y=850;s.render.resolution_percentage=100;s.render.image_settings.file_format='JPEG';s.render.image_settings.color_mode='RGB';s.render.image_settings.quality=95;s.render.filepath=str(OUT/'Oven_Legacy_Coals_Diagnostic.jpg');bpy.ops.render.render(write_still=True)
for o in s.objects:
 if o.type!='MESH':continue
 for mat in o.data.materials:
  if not mat or not mat.use_nodes:continue
  nt=mat.node_tree;out=next((n for n in nt.nodes if n.type=='OUTPUT_MATERIAL'),None)
  if not out:continue
  em=nt.nodes.new('ShaderNodeEmission');em.inputs['Color'].default_value=(0,0,0,1);em.inputs['Strength'].default_value=1;tex=nt.nodes.get('Legacy_Coals_Emission')
  if tex:nt.links.new(tex.outputs['Color'],em.inputs['Color'])
  nt.links.new(em.outputs[0],out.inputs['Surface'])
s.world.color=(0,0,0)
if s.world.use_nodes:
 for n in s.world.node_tree.nodes:
  if n.type=='BACKGROUND':n.inputs['Color'].default_value=(0,0,0,1);n.inputs['Strength'].default_value=0
s.view_settings.view_transform='Standard';s.render.filepath=str(OUT/'Oven_Emission_Only.jpg');bpy.ops.render.render(write_still=True)
