"""Read-only source audit, run in a separate background Blender.

Trace material/world output dependencies through nested groups. Measure storage
with matched temporary resaves; only temporary copies lose unused packed data.
Never save a source blend, unpack to disk, render, or execute embedded scripts.
"""
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import sys
import time
import traceback

import bpy

AUDIT_VERSION = 2


def matching_socket(socket, original, candidates):
    candidates = list(candidates)
    identifier = getattr(socket, 'identifier', None)
    if identifier:
        match = next((s for s in candidates if getattr(s, 'identifier', None) == identifier), None)
        if match is not None:
            return match
    names = [s for s in candidates if s.name == socket.name]
    if len(names) == 1:
        return names[0]
    index = list(original).index(socket)
    return candidates[index] if index < len(candidates) else None


def output_images(tree, output_types):
    """Conservative upstream dependency graph; both branches of mixes are retained."""
    if tree is None:
        return set()
    images = set()
    visited = set()

    def input_links(socket, frames):
        if socket is None:
            return
        for link in socket.links:
            if getattr(link, 'is_valid', True) and not getattr(link, 'is_muted', False):
                walk(link.from_socket, frames)

    def walk(socket, frames):
        key = (socket.as_pointer(), tuple(node.as_pointer() for node in frames))
        if key in visited:
            return
        visited.add(key)
        node = socket.node
        if node.mute:
            for link in node.internal_links:
                if link.to_socket == socket:
                    input_links(link.from_socket, frames)
            return
        if node.type == 'GROUP' and node.node_tree:
            outputs = [n for n in node.node_tree.nodes if n.type == 'GROUP_OUTPUT']
            active = [n for n in outputs if getattr(n, 'is_active_output', False)]
            for out in active or outputs:
                target = matching_socket(socket, node.outputs, out.inputs)
                input_links(target, frames + (node,))
            return
        if node.type == 'GROUP_INPUT' and frames:
            parent = frames[-1]
            target = matching_socket(socket, node.outputs, parent.inputs)
            input_links(target, frames[:-1])
            return
        image = getattr(node, 'image', None)
        if isinstance(image, bpy.types.Image):
            images.add(image.as_pointer())
        for input_socket in node.inputs:
            input_links(input_socket, frames)

    outputs = [n for n in tree.nodes if n.type in output_types]
    active = [n for n in outputs if getattr(n, 'is_active_output', False)]
    for node in active or outputs:
        for socket in node.inputs:
            input_links(socket, ())
    return images


def node_images(tree, seen=None):
    if not tree:
        return set()
    seen = set() if seen is None else seen
    if tree.as_pointer() in seen:
        return set()
    seen.add(tree.as_pointer())
    result = set()
    for node in tree.nodes:
        image = getattr(node, 'image', None)
        if isinstance(image, bpy.types.Image):
            result.add(image.as_pointer())
        if node.type == 'GROUP':
            result.update(node_images(node.node_tree, seen))
    return result


def packed_size(image):
    files = list(image.packed_files)
    packed = [item.packed_file for item in files if item.packed_file]
    if not packed and image.packed_file:
        packed = [image.packed_file]
    unique = {item.as_pointer(): item for item in packed}
    return sum(item.size for item in unique.values())


def geometry_materials(tree, seen=None):
    if not tree:
        return set()
    seen = set() if seen is None else seen
    if tree.as_pointer() in seen:
        return set()
    seen.add(tree.as_pointer())
    materials = set()
    for node in tree.nodes:
        for socket in node.inputs:
            value = getattr(socket, 'default_value', None)
            if isinstance(value, bpy.types.Material):
                materials.add(value.as_pointer())
        if node.type == 'GROUP':
            materials.update(geometry_materials(node.node_tree, seen))
    return materials


def file_hash(path):
    result = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            result.update(block)
    return result.hexdigest()


def inspect(path, root, scratch):
    started = time.monotonic()
    original_stat = path.stat()
    original_hash = file_hash(path)
    bpy.ops.wm.open_mainfile(filepath=str(path), load_ui=False, use_scripts=False)
    bpy.context.preferences.filepaths.save_version = 0
    bpy.data.use_autopack = False
    assigned = set()
    # Every object/material slot and every scene is protected, including hidden
    # authoring variants and unused face slots. This deliberately errs toward use.
    for obj in bpy.data.objects:
        for slot in obj.material_slots:
            if slot.material:
                assigned.add(slot.material.as_pointer())
        for modifier in obj.modifiers:
            assigned.update(geometry_materials(getattr(modifier, 'node_group', None)))
            if modifier.type == 'NODES':
                for key in modifier.keys():
                    if isinstance(modifier[key], bpy.types.Material):
                        assigned.add(modifier[key].as_pointer())
    for scene in bpy.data.scenes:
        for layer in scene.view_layers:
            if layer.material_override:
                assigned.add(layer.material_override.as_pointer())

    active_images = set()
    material_refs = defaultdict(list)
    export_refs = set()
    for material in bpy.data.materials:
        refs = node_images(material.node_tree) if material.use_nodes else set()
        is_assigned = material.as_pointer() in assigned
        connected = output_images(material.node_tree, {'OUTPUT_MATERIAL'}) if material.use_nodes else set()
        if is_assigned:
            active_images.update(connected)
        for image in refs:
            material_refs[image].append({'material': material.name, 'assigned': is_assigned,
                                         'connected': image in connected})
        # CSC export slots can intentionally be disconnected from Blender shading.
        if material.get('civ_material') or material.get('civ_ao_texture'):
            export_refs.update(refs)

    other_refs = set()
    for world in bpy.data.worlds:
        if world.use_nodes:
            if any(scene.world == world for scene in bpy.data.scenes):
                active_images.update(output_images(world.node_tree, {'OUTPUT_WORLD'}))
            other_refs.update(node_images(world.node_tree))
    for scene in bpy.data.scenes:
        other_refs.update(node_images(getattr(scene, 'node_tree', None)))
        other_refs.update(node_images(getattr(scene, 'compositing_node_group', None)))
    for texture in bpy.data.textures:
        image = getattr(texture, 'image', None)
        if image:
            other_refs.add(image.as_pointer())
    for obj in bpy.data.objects:
        if isinstance(obj.data, bpy.types.Image):
            other_refs.add(obj.data.as_pointer())
        for modifier in obj.modifiers:
            # Geometry-node materials/images are protected even if their output
            # cannot be established statically without evaluating the modifier.
            group = getattr(modifier, 'node_group', None)
            other_refs.update(node_images(group))
            for key in modifier.keys() if modifier.type == 'NODES' else []:
                value = modifier[key]
                if isinstance(value, bpy.types.Image):
                    other_refs.add(value.as_pointer())

    images = []
    unused = []
    unreferenced = []
    for image in bpy.data.images:
        if image.library:
            continue  # Packed bytes belong to the linked library, not this file.
        size = packed_size(image)
        if not size:
            continue
        key = image.as_pointer()
        real_users = max(0, image.users - int(image.use_fake_user))
        if key in active_images:
            category = 'active_shading'
        elif key in other_refs:
            category = 'other_render_or_reference_use'
        elif real_users == 0:
            category = 'unreferenced'
            unreferenced.append(image)
            unused.append(image)
        elif material_refs[key]:
            category = 'disconnected_or_unassigned_material'
            unused.append(image)
        else:
            category = 'other_datablock_use'
        images.append({'name': image.name, 'filepath': image.filepath,
                       'packed_bytes': size, 'category': category,
                       'users': real_users, 'fake_user': image.use_fake_user,
                       'possible_export_use': key in export_refs,
                       'materials': material_refs[key]})

    result = {'audit_version': AUDIT_VERSION, 'path': str(path), 'relative_path': str(path.relative_to(root)),
              'backup': path.suffix.lower() != '.blend', 'file_bytes': original_stat.st_size,
              'images': images, 'packed_bytes': sum(i['packed_bytes'] for i in images),
              'candidate_packed_bytes': sum(i['packed_bytes'] for i in images if i['category'] in
                                            {'unreferenced', 'disconnected_or_unassigned_material'}),
              'unreferenced_packed_bytes': sum(i['packed_bytes'] for i in images if i['category'] == 'unreferenced'),
              'not_active_shading_bytes': sum(i['packed_bytes'] for i in images if i['category'] != 'active_shading'),
              'measured_candidate_saving': 0, 'measured_unreferenced_saving': 0}
    if unused:
        # A normal resave can drop zero-user images on its own. Keep their image
        # IDs in both controls so the paired difference isolates packed payloads.
        for image in bpy.data.images:
            if image.library is None and packed_size(image):
                image.use_fake_user = True
        with path.open('rb') as source:
            compressed = source.read(7) != b'BLENDER'
        temporary = scratch / 'measurement.blend'
        if temporary.resolve() == path.resolve():
            raise ValueError('Refusing to save over source')

        def size_after_save():
            bpy.ops.wm.save_as_mainfile(filepath=str(temporary), copy=True,
                                       check_existing=False, relative_remap=False, compress=compressed)
            size = temporary.stat().st_size
            temporary.unlink()
            return size

        try:
            baseline = size_after_save()
            for image in unreferenced:
                image.unpack(method='REMOVE')
            conservative = size_after_save() if unreferenced else baseline
            for image in unused:
                if image not in unreferenced:
                    image.unpack(method='REMOVE')
            cleaned = size_after_save()
            result.update({'compression': compressed, 'matched_baseline_bytes': baseline,
                           'matched_unreferenced_clean_bytes': conservative,
                           'matched_candidate_clean_bytes': cleaned,
                           'measured_candidate_saving': max(0, baseline - cleaned),
                           'measured_unreferenced_saving': max(0, baseline - conservative)})
        except Exception:
            result['measurement_error'] = traceback.format_exc()
    after = path.stat()
    result['source_unchanged'] = (after.st_size == original_stat.st_size and
                                  after.st_mtime_ns == original_stat.st_mtime_ns and
                                  file_hash(path) == original_hash)
    result['sha256'] = original_hash
    result['seconds'] = round(time.monotonic() - started, 3)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--limit', type=int)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    root = args.root.resolve()
    output = args.output.resolve()
    if output == root or root in output.parents:
        raise ValueError('Output must be outside source tree')
    output.mkdir(parents=True, exist_ok=True)
    scratch = output / 'temporary-measurement'
    scratch.mkdir(exist_ok=True)
    record_path = output / 'files.jsonl'
    completed = set()
    if record_path.exists():
        for line in record_path.read_text(encoding='utf-8').splitlines():
            record = json.loads(line)
            if 'error' not in record and record.get('audit_version') == AUDIT_VERSION:
                completed.add(record['path'])
    paths = sorted((p for p in root.rglob('*') if p.is_file() and
                    (p.suffix.lower() == '.blend' or
                     (p.suffix.lower().startswith('.blend') and p.suffix[6:].isdigit()))),
                   key=lambda p: p.stat().st_size, reverse=True)
    (output / 'inventory.json').write_text(json.dumps([{'path': str(p), 'bytes': p.stat().st_size}
                                                      for p in paths], indent=2), encoding='utf-8')
    pending = [p for p in paths if str(p) not in completed]
    if args.limit:
        pending = pending[:args.limit]
    for index, path in enumerate(pending):
        (output / 'progress.json').write_text(json.dumps({'current': str(path), 'completed': len(completed),
                                                          'total': len(paths), 'started_at': time.time()}), encoding='utf-8')
        try:
            result = inspect(path, root, scratch)
        except Exception:
            result = {'path': str(path), 'error': traceback.format_exc()}
        with record_path.open('a', encoding='utf-8') as stream:
            stream.write(json.dumps(result) + '\n')
        completed.add(str(path))
        print('AUDIT', len(completed), '/', len(paths), path.name, flush=True)
    (output / 'progress.json').write_text(json.dumps({'completed': len(completed), 'total': len(paths),
                                                      'finished': True}), encoding='utf-8')


if __name__ == '__main__':
    main()
