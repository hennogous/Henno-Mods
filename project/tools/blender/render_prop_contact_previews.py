"""Render source-library previews without saving or changing the source blends.

Blender --background --factory-startup --python-exit-code 1 --python this.py --
    --library LIB --output OUTPUT [--only ASSET ...] [--force]
Output and Blender TMPDIR should be under the host's approved output directory.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector


def fingerprint(blend, library):
    digest = hashlib.sha256(Path(__file__).read_bytes())
    digest.update(blend.read_bytes())
    for im in sorted(bpy.data.images, key=lambda i: i.name):
        if im.source != 'FILE':
            continue
        path = Path(bpy.path.abspath(im.filepath))
        if not path.is_file():
            raise FileNotFoundError(f'{blend.name}: missing texture {path}')
        digest.update(path.read_bytes())
    return digest.hexdigest()


def render_asset(blend, library, output, force=False):
    bpy.ops.wm.open_mainfile(filepath=str(blend), load_ui=False)
    scene = bpy.context.scene
    signature = fingerprint(blend, library)
    meta_path = output / 'previews' / (blend.stem + '.json')
    if not force and meta_path.exists():
        previous = json.loads(meta_path.read_text())
        if previous.get('fingerprint') == signature and all((output / v['image']).is_file() for v in previous['views']):
            print('CACHED', blend.stem, flush=True)
            return previous

    source_objects = list(scene.objects)
    transforms = {o.name: tuple(tuple(row) for row in o.matrix_world) for o in source_objects}
    meshes = [o for o in source_objects if o.type == 'MESH' and o.visible_get() and not o.hide_render]
    if not meshes:
        raise ValueError(f'{blend.name}: no visible saved-state mesh')
    points = [o.matrix_world @ v.co for o in meshes for v in o.data.vertices]
    lo = Vector(tuple(min(p[i] for p in points) for i in range(3)))
    hi = Vector(tuple(max(p[i] for p in points) for i in range(3)))
    center, dimensions = (lo + hi) / 2, hi - lo
    extent = max(dimensions)
    preview_corrections = []
    # BC4-derived PNGs carry a scalar in red, not grayscale RGB. Correct only
    # the in-memory Blender preview, preserving the source textures and blends.
    for material in bpy.data.materials:
        if not material.use_nodes:
            continue
        nodes, links = material.node_tree.nodes, material.node_tree.links
        for channel in ('AO', 'Gloss', 'Metalness', 'Opacity'):
            texture = nodes.get(channel)
            if not texture or texture.type != 'TEX_IMAGE':
                continue
            outgoing = list(texture.outputs['Color'].links)
            if not outgoing:
                continue
            split = nodes.new('ShaderNodeSeparateColor')
            split.mode = 'RGB'
            links.new(texture.outputs['Color'], split.inputs['Color'])
            for link in outgoing:
                destination = link.to_socket
                links.remove(link)
                links.new(split.outputs['Red'], destination)
            preview_corrections.append(material.name + ': ' + channel + ' uses red channel')
        base = nodes.get('BaseColor')
        shader = nodes.get('Principled BSDF')
        if base and shader:
            if material.get('source_shader') == 'DecalMaterial':
                links.new(base.outputs['Alpha'], shader.inputs['Alpha'])
                preview_corrections.append(material.name + ': base texture alpha used for decal preview')
    # Preserve visibility of state-exclusive components and hidden skeleton refs.
    for o in source_objects:
        if o.type in {'CAMERA', 'LIGHT'}:
            o.hide_render = True

    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 24
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 768
    scene.render.resolution_y = 640
    scene.render.resolution_percentage = 100
    scene.render.pixel_aspect_x = scene.render.pixel_aspect_y = 1
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.render.film_transparent = True
    scene.render.use_file_extension = True
    scene.view_settings.view_transform = 'Standard'
    scene.view_settings.look = 'None'
    scene.view_settings.exposure = 0
    scene.view_settings.gamma = 1
    world = bpy.data.worlds.new('Contact sheet environment')
    world.use_nodes = True
    world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.7, 0.75, 0.8, 1)
    world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.65
    scene.world = world
    camera_data = bpy.data.cameras.new('Contact sheet camera')
    camera = bpy.data.objects.new('Contact sheet camera', camera_data)
    scene.collection.objects.link(camera)
    scene.camera = camera
    camera_data.type = 'ORTHO'
    camera_data.clip_start = 0.01
    camera_data.clip_end = max(5000, extent * 50)
    light_data = bpy.data.lights.new('Contact sheet key', 'SUN')
    light_data.energy = 2.0
    light_data.angle = math.radians(18)
    light = bpy.data.objects.new('Contact sheet key', light_data)
    scene.collection.objects.link(light)
    fill_data = bpy.data.lights.new('Contact sheet fill', 'SUN')
    fill_data.energy = 0.7
    fill_data.angle = math.radians(30)
    fill = bpy.data.objects.new('Contact sheet fill', fill_data)
    scene.collection.objects.link(fill)

    # Elevation is the approved CSC review elevation. Rotate only the camera:
    # choose the broad face for narrow textile racks, with an orthogonal second view.
    azimuth = (math.pi / 2 if dimensions.y > dimensions.x * 1.35 else 0) + math.radians(25)
    result = {'asset_id': blend.stem, 'fingerprint': signature,
              'dimensions': list(dimensions), 'visible_objects': [o.name for o in meshes],
              'state': 'saved Worked preview', 'views': [], 'preview_corrections': preview_corrections}
    for suffix, angle in [('front', azimuth), ('side', azimuth + math.pi / 2)]:
        direction = Vector((math.sin(angle), -math.cos(angle), 0.82)).normalized()
        rotation = (-direction).to_track_quat('-Z', 'Y')
        inverse = rotation.inverted()
        projected = [inverse @ (p - center) for p in points]
        xmin, xmax = min(p.x for p in projected), max(p.x for p in projected)
        ymin, ymax = min(p.y for p in projected), max(p.y for p in projected)
        aim = center + rotation @ Vector(((xmin + xmax) / 2, (ymin + ymax) / 2, 0))
        camera.location = aim + direction * max(300, extent * 6)
        camera.rotation_euler = rotation.to_euler()
        camera_data.ortho_scale = max(xmax - xmin, (ymax - ymin) * 1.2) * 1.20
        light.rotation_euler = (-(direction + rotation @ Vector((-0.65, 0.8, 0)))).to_track_quat('-Z', 'Y').to_euler()
        fill.rotation_euler = (-(direction + rotation @ Vector((1.2, 0.3, 0)))).to_track_quat('-Z', 'Y').to_euler()
        relative = Path('previews') / f'{blend.stem}__{suffix}.png'
        scene.render.filepath = str(output / relative)
        bpy.context.view_layer.update()
        bpy.ops.render.render(write_still=True)
        result['views'].append({'image': relative.as_posix(), 'azimuth_degrees': math.degrees(angle),
                                'elevation_degrees': math.degrees(math.atan(0.82))})
    assert all(transforms[o.name] == tuple(tuple(row) for row in o.matrix_world) for o in source_objects)
    result['source_transforms_preserved'] = True
    meta_path.write_text(json.dumps(result, indent=2) + '\n')
    print('PREVIEW COMPLETE', blend.stem, flush=True)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--library', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--only', nargs='+')
    parser.add_argument('--force', action='store_true')
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    args.library, args.output = args.library.resolve(), args.output.resolve()
    if args.output == args.library or args.library in args.output.parents:
        raise ValueError('Contact-sheet outputs must be separate from the source library')
    (args.output / 'previews').mkdir(parents=True, exist_ok=True)
    blends = sorted(args.library.glob('*.blend'))
    if args.only:
        blends = [p for p in blends if p.stem in args.only]
        if len(blends) != len(set(args.only)):
            raise ValueError('An --only asset was not found')
    results = [render_asset(p, args.library, args.output, args.force) for p in blends]
    (args.output / 'render-run.json').write_text(json.dumps({'assets': results}, indent=2) + '\n')
    print('CONTACT PREVIEWS COMPLETE', len(results), flush=True)


if __name__ == '__main__':
    main()
