"""Small synthetic dependency-graph checks; no source blends are opened or saved."""
import base64
import importlib.util
import json
from pathlib import Path
import sys
import bpy

spec = importlib.util.spec_from_file_location('audit', Path(__file__).with_name('audit_packed_texture_storage.py'))
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)
checks = []


def check(value, label):
    assert value, label
    checks.append(label)


image = bpy.data.images.new('Active image', width=2, height=2)
unused = bpy.data.images.new('Disconnected image', width=2, height=2)
material = bpy.data.materials.new('Graph test')
material.use_nodes = True
tree = material.node_tree
tree.nodes.clear()
output = tree.nodes.new('ShaderNodeOutputMaterial')
emission = tree.nodes.new('ShaderNodeEmission')
texture = tree.nodes.new('ShaderNodeTexImage')
texture.image = image
disconnected = tree.nodes.new('ShaderNodeTexImage')
disconnected.image = unused
tree.links.new(texture.outputs['Color'], emission.inputs['Color'])
tree.links.new(emission.outputs[0], output.inputs['Surface'])
key = image.as_pointer()
check(audit.output_images(tree, {'OUTPUT_MATERIAL'}) == {key}, 'Connected image retained; disconnected image excluded')
second = tree.nodes.new('ShaderNodeOutputMaterial')
second.is_active_output = True
check(not audit.output_images(tree, {'OUTPUT_MATERIAL'}), 'Inactive material output excluded')
output.is_active_output = True
tree.nodes.remove(second)

group = bpy.data.node_groups.new('Nested graph', 'ShaderNodeTree')
group.interface.new_socket(name='Color', in_out='OUTPUT', socket_type='NodeSocketColor')
group_output = group.nodes.new('NodeGroupOutput')
inner_texture = group.nodes.new('ShaderNodeTexImage')
inner_texture.image = image
group.links.new(inner_texture.outputs['Color'], group_output.inputs['Color'])
instance = tree.nodes.new('ShaderNodeGroup')
instance.node_tree = group
tree.links.new(instance.outputs['Color'], emission.inputs['Color'])
check(audit.output_images(tree, {'OUTPUT_MATERIAL'}) == {key}, 'Nested group image dependency retained')
group.interface.new_socket(name='Color input', in_out='INPUT', socket_type='NodeSocketColor')
group_input = group.nodes.new('NodeGroupInput')
group.links.new(group_input.outputs['Color input'], group_output.inputs['Color'])
tree.links.new(texture.outputs['Color'], instance.inputs['Color input'])
check(audit.output_images(tree, {'OUTPUT_MATERIAL'}) == {key}, 'Group input resolves to parent connection')

invert = tree.nodes.new('ShaderNodeInvert')
tree.links.new(texture.outputs['Color'], invert.inputs['Color'])
tree.links.new(invert.outputs['Color'], emission.inputs['Color'])
invert.mute = True
check(audit.output_images(tree, {'OUTPUT_MATERIAL'}) == {key}, 'Muted node follows its internal bypass')
tree.links.new(texture.outputs['Color'], emission.inputs['Color'])
texture.mute = True
check(not audit.output_images(tree, {'OUTPUT_MATERIAL'}), 'Muted texture does not contribute its image')
texture.mute = False

world = bpy.data.worlds.new('World graph test')
world.use_nodes = True
env = world.node_tree.nodes.new('ShaderNodeTexEnvironment')
env.image = image
background = next(n for n in world.node_tree.nodes if n.type == 'BACKGROUND')
world.node_tree.links.new(env.outputs['Color'], background.inputs['Color'])
check(key in audit.output_images(world.node_tree, {'OUTPUT_WORLD'}), 'World lighting dependency retained')
geometry = bpy.data.node_groups.new('Geometry material test', 'GeometryNodeTree')
set_material = geometry.nodes.new('GeometryNodeSetMaterial')
set_material.inputs['Material'].default_value = material
check(material.as_pointer() in audit.geometry_materials(geometry), 'Geometry-node material references retained')
packed = bpy.data.images.new('Packed file test', width=1, height=1)
packed.source = 'FILE'
packed.filepath = '//synthetic-test.png'
payload = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII=')
packed.pack(data=payload, data_len=len(payload))
check(audit.packed_size(packed) == len(payload), 'Packed payload is measured exactly')
result = {'passed': True, 'checks': checks, 'count': len(checks), 'blender': bpy.app.version_string}
destination = Path(sys.argv[sys.argv.index('--') + 1])
destination.write_text(json.dumps(result, indent=2), encoding='utf-8')
print(json.dumps(result))
