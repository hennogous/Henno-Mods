"""Bake only the new interior into reserved charts of a staged shared AO copy."""
import bpy,bmesh,json
from pathlib import Path
OUT=Path(r'C:\Users\Shadow\Desktop\Codex\CSC_Storage_L\interior-20261008')
bpy.ops.wm.open_mainfile(filepath=str(OUT/'CSC_Storage_L_Interior.blend'))
s=bpy.data.scenes['Export'];bpy.context.window.scene=s;o=bpy.data.objects['CSC_Storage_L_Bldg']
image=next(i for i in bpy.data.images if 'CSC_Atlas_AO2' in i.name);image.colorspace_settings.name='Non-Color'
image.reload();pixels=list(image.pixels[:]);stage=bpy.data.images.new('Storage_Interior_AO_Bake',width=image.size[0],height=image.size[1]);stage.colorspace_settings.name='Non-Color';stage.pixels.foreach_set(pixels)
stage.filepath_raw=str(OUT/'shared-ao-bake.png');stage.file_format='PNG'
target=o.copy();target.data=o.data.copy();target.parent=None;s.collection.objects.link(target)
def retain(obj,interior):
 bm=bmesh.new();bm.from_mesh(obj.data);layer=bm.faces.layers.int['storage_interior_part']
 bmesh.ops.delete(bm,geom=[f for f in bm.faces if (f[layer]>0)!=interior],context='FACES');bm.to_mesh(obj.data);bm.free()
retain(target,True);retain(o,False)
target.data.materials.clear();mat=bpy.data.materials.new('Temporary_Interior_AO_Bake');mat.use_nodes=True;target.data.materials.append(mat)
nodes=mat.node_tree.nodes;nodes.clear();tex=nodes.new('ShaderNodeTexImage');tex.image=stage;nodes.active=tex
ao=nodes.new('ShaderNodeAmbientOcclusion');ao.inputs['Distance'].default_value=28;ao.samples=64
em=nodes.new('ShaderNodeEmission');out=nodes.new('ShaderNodeOutputMaterial');mat.node_tree.links.new(ao.outputs['Color'],em.inputs['Color']);mat.node_tree.links.new(em.outputs[0],out.inputs['Surface'])
for p in target.data.polygons:p.material_index=0
target.data.uv_layers.active_index=1;target.data.uv_layers['UV2'].active_render=True
s.render.engine='CYCLES';s.cycles.samples=64;s.cycles.device='CPU';s.render.bake.use_clear=False;s.render.bake.margin=1
for ob in s.objects:ob.select_set(False)
target.hide_render=False;target.hide_viewport=False;target.hide_set(False);target.select_set(True);bpy.context.view_layer.objects.active=target
bpy.ops.object.bake(type='EMIT');stage.save();print('INTERIOR_AO_BAKED',stage.size[:])
