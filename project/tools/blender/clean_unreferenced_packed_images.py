"""Stage and verify only the audited zero-user packed-image removals.

Use background Blender matching the source format. This stage never overwrites
source files; commit_verified_texture_cleanup.py installs the verified copies.
"""
import argparse
from array import array
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import traceback

import bpy

spec = importlib.util.spec_from_file_location('audit', Path(__file__).with_name('audit_packed_texture_storage.py'))
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def identity(value):
    return (type(value).__name__, value.name, value.library.filepath if value.library else None)


def scalar(value):
    if isinstance(value, bpy.types.ID):
        return identity(value)
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    try:
        return [scalar(item) for item in value]
    except TypeError:
        return str(type(value))


def properties(value):
    result = {}
    for prop in value.bl_rna.properties:
        if prop.identifier == 'rna_type' or prop.is_readonly:
            continue
        try:
            content = getattr(value, prop.identifier)
            if prop.type != 'COLLECTION':
                result[prop.identifier] = scalar(content)
        except (AttributeError, TypeError, ValueError):
            continue
    try:
        result['custom'] = {key: scalar(value[key]) for key in value.keys()}
    except TypeError:
        pass
    return result


def tree_snapshot(tree):
    if tree is None:
        return None
    return {'nodes': {node.name: {'type': node.bl_idname, 'properties': properties(node),
                                'inputs': [(socket.identifier, scalar(getattr(socket, 'default_value', None)))
                                           for socket in node.inputs]}
                      for node in tree.nodes},
            'links': sorted((link.from_node.name, link.from_socket.identifier,
                             link.to_node.name, link.to_socket.identifier) for link in tree.links)}


def collection_hash(collection, attr, width=1, kind='f'):
    buffer = array(kind, [0]) * (len(collection) * width)
    collection.foreach_get(attr, buffer)
    return hashlib.sha256(buffer.tobytes()).hexdigest()


def mesh_snapshot(mesh):
    result = {'vertices': collection_hash(mesh.vertices, 'co', 3),
              'edges': collection_hash(mesh.edges, 'vertices', 2, 'i'),
              'loops': collection_hash(mesh.loops, 'vertex_index', 1, 'i'),
              'polygons': {attr: collection_hash(mesh.polygons, attr, 1, 'i')
                           for attr in ['loop_start', 'loop_total', 'material_index']},
              'smooth': [polygon.use_smooth for polygon in mesh.polygons],
              'uv': {layer.name: collection_hash(layer.data, 'uv', 2) for layer in mesh.uv_layers},
              'materials': [identity(mat) if mat else None for mat in mesh.materials],
              'shape_keys': {key.name: collection_hash(key.data, 'co', 3)
                             for key in mesh.shape_keys.key_blocks} if mesh.shape_keys else None,
              'weights': [[(group.group, group.weight) for group in vertex.groups] for vertex in mesh.vertices]}
    attributes = {}
    for attr in mesh.attributes:
        if attr.data_type == 'BOOLEAN':
            attributes[attr.name] = (attr.data_type, attr.domain, [element.value for element in attr.data])
            continue
        shapes = {'FLOAT': ('value', 1, 'f'), 'INT': ('value', 1, 'i'), 'BOOLEAN': ('value', 1, 'i'),
                  'FLOAT_VECTOR': ('vector', 3, 'f'), 'FLOAT2': ('vector', 2, 'f'),
                  'FLOAT_COLOR': ('color', 4, 'f'), 'BYTE_COLOR': ('color', 4, 'f')}
        if attr.data_type in shapes:
            name, width, kind = shapes[attr.data_type]
            attributes[attr.name] = (attr.data_type, attr.domain, collection_hash(attr.data, name, width, kind))
    result['attributes'] = attributes
    return result


def snapshot(excluded_images):
    objects = {}
    for obj in bpy.data.objects:
        objects[obj.name] = {'properties': properties(obj),
                             'transforms': [[round(value, 7) for row in getattr(obj, matrix) for value in row]
                                            for matrix in ['matrix_basis', 'matrix_parent_inverse']],
                             'data': identity(obj.data) if obj.data else None,
                             'material_slots': [(slot.link, identity(slot.material) if slot.material else None)
                                                for slot in obj.material_slots],
                             'modifiers': [(modifier.name, modifier.type, properties(modifier)) for modifier in obj.modifiers],
                             'constraints': [(constraint.name, constraint.type, properties(constraint)) for constraint in obj.constraints],
                             'groups': [(group.name, group.index) for group in obj.vertex_groups]}
    images = {}
    for image in bpy.data.images:
        if image.name in excluded_images:
            continue
        packed = list(image.packed_files)
        payloads = [item.packed_file for item in packed if item.packed_file]
        if not payloads and image.packed_file:
            payloads = [image.packed_file]
        images[image.name] = {'filepath': image.filepath, 'source': image.source,
                             'colorspace': image.colorspace_settings.name,
                             'alpha_mode': image.alpha_mode, 'fake_user': image.use_fake_user,
                             'packed': sorted((item.size, hashlib.sha256(item.data).hexdigest()) for item in payloads)}
    return {'objects': objects, 'meshes': {mesh.name: mesh_snapshot(mesh) for mesh in bpy.data.meshes},
            'materials': {mat.name: {'properties': properties(mat), 'nodes': tree_snapshot(mat.node_tree)}
                          for mat in bpy.data.materials},
            'groups': {group.name: tree_snapshot(group) for group in bpy.data.node_groups},
            'worlds': {world.name: {'properties': properties(world), 'nodes': tree_snapshot(world.node_tree)}
                       for world in bpy.data.worlds},
            'scenes': {scene.name: {'objects': sorted(obj.name for obj in scene.objects),
                                    'camera': scene.camera.name if scene.camera else None,
                                    'world': scene.world.name if scene.world else None,
                                    'properties': properties(scene), 'render': properties(scene.render),
                                    'view': properties(scene.view_settings)} for scene in bpy.data.scenes},
            'armatures': {rig.name: [(bone.name, bone.parent.name if bone.parent else None,
                                     list(bone.head_local), list(bone.tail_local)) for bone in rig.bones]
                          for rig in bpy.data.armatures},
            'actions': {action.name: properties(action) for action in bpy.data.actions}, 'images': images}


def stage(record, index, output):
    source = Path(record['path'])
    if audit.file_hash(source) != record['sha256']:
        raise ValueError('Source changed since the audit; re-audit required')
    with source.open('rb') as stream:
        header = stream.read(12)
    old_format = header == b'BLENDER-v301'
    if old_format != (bpy.app.version[:2] == (3, 1)):
        raise ValueError('Wrong Blender version for source')
    bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False, use_scripts=False)
    targets = [row for row in record['images'] if row['category'] == 'unreferenced']
    names = {row['name'] for row in targets}
    for row in targets:
        image = bpy.data.images.get(row['name'])
        if image is None or image.library or max(0, image.users - int(image.use_fake_user)) != 0:
            raise ValueError('Image now has actual users: ' + row['name'])
        if audit.packed_size(image) != row['packed_bytes'] or image.filepath != row['filepath']:
            raise ValueError('Image contents differ from audited selection: ' + row['name'])
    # Saving normally drops unused materials too. Explicitly retain those authoring
    # datablocks so this cleanup cannot also consume the unapproved material group.
    retained_orphans = []
    for collection_name in ['materials', 'meshes', 'curves', 'armatures', 'actions', 'node_groups', 'worlds']:
        for block in getattr(bpy.data, collection_name):
            if block.library is None and block.users == 0 and not block.use_fake_user:
                block.use_fake_user = True
                retained_orphans.append((collection_name, block.name))
    for image in bpy.data.images:
        if image.name not in names and image.library is None and image.users == 0 and not image.use_fake_user:
            image.use_fake_user = True
            retained_orphans.append(('images', image.name))
    before = snapshot(names)
    for name in names:
        bpy.data.images.remove(bpy.data.images[name])
    bpy.context.preferences.filepaths.save_version = 0
    original_autopack = bpy.data.use_autopack
    destination = output / 'staged' / (str(index).zfill(3) + '.blend')
    bpy.ops.wm.save_as_mainfile(filepath=str(destination), copy=True,
                               check_existing=False, relative_remap=False,
                               compress=not header.startswith(b'BLENDER'))
    bpy.ops.wm.open_mainfile(filepath=str(destination), load_ui=False, use_scripts=False)
    after = snapshot(names)
    # Match JSON representation so tuples/lists in nested ID properties compare equally.
    before_json = json.dumps(before, sort_keys=True)
    after_json = json.dumps(after, sort_keys=True)
    if before_json != after_json:
        before_path = output / ('mismatch-' + str(index) + '-before.json')
        before_path.write_text(json.dumps(before, indent=2), encoding='utf-8')
        (output / ('mismatch-' + str(index) + '-after.json')).write_text(json.dumps(after, indent=2), encoding='utf-8')
        raise ValueError('Preservation comparison failed: ' + str(before_path))
    if any(bpy.data.images.get(name) is not None for name in names):
        raise ValueError('An audited unused image remains in the staged copy')
    if audit.file_hash(source) != record['sha256']:
        raise ValueError('Source changed while preparing staged copy')
    return {'source': str(source), 'staged': str(destination), 'source_sha256': record['sha256'],
            'clean_sha256': audit.file_hash(destination), 'original_bytes': source.stat().st_size,
            'clean_bytes': destination.stat().st_size, 'removed_images': sorted(names),
            'removed_packed_bytes': sum(row['packed_bytes'] for row in targets),
            'blender': bpy.app.version_string, 'preservation_verified': True,
            'original_autopack': original_autopack, 'retained_orphan_datablocks': retained_orphans}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--summary', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--old-format', action='store_true')
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    output = args.output.resolve()
    (output / 'staged').mkdir(parents=True, exist_ok=True)
    targets = [record for record in json.loads(args.summary.read_text(encoding='utf-8'))['candidates']
               if record['unreferenced_packed_bytes']]
    results = []
    missing = []
    for index, record in enumerate(targets):
        if not Path(record['path']).exists():
            missing.append(record['path'])
            continue
        with Path(record['path']).open('rb') as stream:
            old = stream.read(12) == b'BLENDER-v301'
        if old != args.old_format:
            continue
        try:
            result = stage(record, index, output)
            results.append(result)
            print('VERIFIED', record['relative_path'], flush=True)
        except Exception:
            (output / ('failure-' + str(index) + '.json')).write_text(json.dumps(
                {'path': record['path'], 'error': traceback.format_exc()}, indent=2), encoding='utf-8')
            raise
    suffix = 'old' if args.old_format else 'new'
    (output / ('staged-' + suffix + '.json')).write_text(json.dumps(results, indent=2), encoding='utf-8')
    (output / ('missing-' + suffix + '.json')).write_text(json.dumps(missing, indent=2), encoding='utf-8')
    print('Staged and verified', len(results), 'files')


if __name__ == '__main__':
    main()
