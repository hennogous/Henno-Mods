"""Read-only CSC scene-authoring checks, shared by the add-on and exporter.

Blender CLI: blender -b --python csc_scene_validation.py -- --blend scene.blend
             --output /absolute/report.json
Pure rules in validate_snapshot can be tested without Blender.
"""
import argparse
from contextlib import contextmanager
import hashlib
import json
import math
from pathlib import Path
import sys

VERSION = 4
ATTACHMENT_ROLES = {'reused_attachment', 'custom_attachment'}
FIXED_ROLES = {'building_geometry', 'fixed_geometry'}
VISUAL_CHECKS = {
    'ROAD_CLEARANCE': 'Review actual opaque road footprints from above; props must stay off roads unless explicitly requested.',
    'AO_QUALITY': 'Review mapped AO at game scale, including sheltered surfaces; verify atlas allocations and release provenance.',
    'STATE_ALIGNMENT': 'Compare intact and CON+PIL placement, solid-prop debris, visibility states and terrain behavior.',
    'COMPOSITION': 'Compare the approved concept, silhouette, garment readability and density at game scale.',
    'DOUBLE_SIDED_SURFACES': 'Check privacy screens and other thin surfaces from both sides; duplicated faces must have opposite normals.',
}


def validate_snapshot(snapshot):
    """Return errors, advisory warnings and review requirements; never mutate the snapshot."""
    findings = []
    def add(code, message, objects=(), severity='error'):
        findings.append(dict(code=code, severity=severity, message=message, objects=list(objects)))
    objects = {o['name']: o for o in snapshot.get('objects', [])}
    scenes = snapshot.get('scenes', {})
    for name in ('Export', 'Review'):
        if name not in scenes:
            add('MISSING_SCENE', f'Missing {name} scene.')
    export = [o for o in objects.values() if 'Export' in o.get('scenes', [])]
    roots = [o for o in export if o['type'] == 'EMPTY' and o.get('instance_id')]
    root_names = {o['name'] for o in roots}
    seen = set()
    for root in roots:
        ident = root['instance_id']
        if ident in seen:
            add('DUPLICATE_INSTANCE', f'Duplicate instance_id {ident}.', [root['name']])
        seen.add(ident)
        if root.get('role') not in ATTACHMENT_ROLES or not root.get('source_asset_id'):
            add('CONTROLLER_METADATA', 'Controller needs an attachment role and source_asset_id.', [root['name']])
        children = [objects[n] for n in root.get('children', []) if n in objects]
        meshes = [o for o in children if o['type'] == 'MESH']
        if not meshes:
            add('EMPTY_ATTACHMENT', 'Attachment has no direct mesh children.', [root['name']])
        for child in meshes:
            if 'Export' not in child.get('scenes', []):
                add('CHILD_NOT_EXPORTED', 'Controller child is absent from Export.', [child['name']])
            if child.get('instance_id') != ident or child.get('source_asset_id') != root.get('source_asset_id'):
                add('CHILD_IDENTITY', 'Child asset/instance identity differs from its controller.', [child['name']])
    def ancestors(ob):
        visited = {ob['name']}
        parent = ob.get('parent')
        while parent and parent in objects and parent not in visited:
            visited.add(parent)
            yield objects[parent]
            parent = objects[parent].get('parent')
    def visible(ob):
        return not ob.get('excluded') and not any(p.get('excluded') for p in ancestors(ob))
    def native(ident):
        return bool(ident) and not ident.startswith('CSC_')
    direct, attached, bespoke_attached = [], [], []
    for ob in objects.values():
        chain = list(ancestors(ob))
        owner = next((p for p in chain if p['name'] in root_names), None)
        in_export = 'Export' in ob.get('scenes', [])
        if in_export and ob.get('role') in ATTACHMENT_ROLES and not ob.get('instance_id'):
            add('CONTROLLER_METADATA', 'Attachment controller is missing instance_id.', [ob['name']])
        if ob['type'] != 'MESH' or not visible(ob):
            continue
        is_prop = bool(ob.get('role') in FIXED_ROLES | {'attachment_geometry', 'reused_asset'} or
                       ob.get('library_source') or owner)
        if 'Review' in ob.get('scenes', []) and is_prop and not in_export and not ob.get('review_only'):
            add('REVIEW_ONLY_PROP', 'Visible prop appears in Review but is absent from Export.', [ob['name']])
        if not in_export:
            continue
        if ob.get('review_only') or ob['name'].startswith('REVIEW_'):
            add('REVIEW_IN_EXPORT', 'Review-only geometry leaked into Export.', [ob['name']])
        # Provenance cannot be erased by relabeling the surrounding custom asset.
        provenance = ob.get('library_source') or ob.get('source_geometry_id') or ob.get('source_asset_id')
        if native(provenance) and (not owner or owner.get('source_asset_id') != provenance or
                                   owner.get('role') != 'reused_attachment'):
            add('PANTRY_BUNDLED', f'Pantry source {provenance} must remain a native attachment; do not bundle it in CSC geometry.', [ob['name']])
        if owner:
            attached.append(ob)
            # Terrain-following hierarchy does not exempt one-off authored art.
            reusable = native(owner.get('source_asset_id')) or (
                owner.get('reuse_approved') is True and
                owner.get('reuse_scope') in ('shared', 'quarter') and
                bool(owner.get('reuse_reference')))
            if not reusable:
                bespoke_attached.append(ob)
            if ob.get('parent') != owner['name']:
                add('NESTED_COMPONENT', 'Attachment meshes must be direct controller children.', [ob['name']])
        elif ob.get('role') in FIXED_ROLES or ob['name'].startswith('CSC_Fixed_'):
            direct.append(ob)
            if ob.get('uv_layers') != 3:
                add('UV_CHANNELS', 'Direct geometry needs exactly three UV channels.', [ob['name']])
            if not ob.get('static_weights', False):
                add('STATIC_WEIGHTS', 'Direct geometry vertices need one static weight of 1.', [ob['name']])
        else:
            add('UNCLASSIFIED_MESH', 'Export mesh has no valid geometry role or attachment controller.', [ob['name']])
        if ob.get('unsupported_modifiers'):
            add('MODIFIERS', 'Resolve unsupported export modifiers.', [ob['name']])
        if not ob.get('materials'):
            add('MISSING_MATERIAL', 'Mesh has no material.', [ob['name']])
    for ob in export:
        if not visible(ob):
            continue
        if ob['type'] in ('MESH', 'EMPTY', 'ARMATURE'):
            scale = ob.get('scale', [1, 1, 1])
            if len(scale) != 3 or not all(math.isfinite(v) and v > 0 for v in scale) or ob.get('determinant', 1) <= 0:
                add('INVALID_TRANSFORM', 'Placement must be finite, nonsingular and not mirrored.', [ob['name']])
            elif max(scale) - min(scale) > max(1, max(scale)) * 1e-5:
                add('NONUNIFORM_SCALE', 'Placements must use uniform scale.', [ob['name']])
            if ob.get('shear', 0) > 1e-5:
                add('SHEAR', 'Placement contains shear.', [ob['name']])
        if ob['type'] == 'LIGHT':
            add('EXPORT_LIGHT', 'Export must contain no light objects.', [ob['name']])
    budget = snapshot.get('main_geometry_maximum', 2200)
    if type(budget) is not int or budget <= 0:
        add('INVALID_BUDGET', 'main_geometry_maximum must be a positive integer.'); budget = 2200
    direct_count = sum(o.get('export_vertices', 0) for o in direct)
    attachment_count = sum(o.get('export_vertices', 0) for o in attached)
    bespoke_count = sum(o.get('export_vertices', 0) for o in bespoke_attached)
    # Bespoke projected decals live outside Export, in their separate masters.
    # Count the tagged composition objects once, not an unchecked numeric allowance.
    decals = [o for o in objects.values() if o['type'] == 'MESH' and
              o.get('budget_role') == 'bespoke_decal' and 'Review' in o.get('scenes', []) and
              'Export' not in o.get('scenes', []) and visible(o)]
    decal_count = sum(o.get('export_vertices', 0) for o in decals)
    budget_count = direct_count + bespoke_count + decal_count
    if budget_count > budget:
        add('MAIN_BUDGET', f'Building budget {budget_count} exceeds the design target {budget}: direct {direct_count} + bespoke attachments {bespoke_count} + bespoke decals {decal_count}. Only reusable attachments are excluded. Advisory only; export is allowed.', severity='warning')
    if any(r.get('reuse_approved') for r in roots if visible(r) and not native(r.get('source_asset_id'))):
        add('REUSE_CLASSIFICATION', 'Verify each CSC reuse exemption against its approval and reuse_reference; a potential library candidate is not automatically reusable.', severity='review')
    for image in snapshot.get('images', []):
        if not image['exists'] and not image.get('packed'):
            add('MISSING_TEXTURE', f'Texture is missing: {image["path"]}', image.get('objects', []))
        if image.get('packed'):
            add('PACKED_TEXTURE', 'Unpack texture to the portable textures directory before export.', image.get('objects', []))
    for name, scene in scenes.items():
        if name not in ('Export', 'Review'):
            continue
        world = scene.get('world')
        if not world or world.get('dynamic'):
            add('WORLD_LIGHT', f'{name} needs the prescribed connected Background world light.')
        elif abs(world['strength'] - .65) > 1e-5 or any(abs(a-b) > 1e-5 for a,b in zip(world['color'], [.7,.8,1])):
            add('WORLD_LIGHT', f'{name} world must use RGB (0.7, 0.8, 1.0), strength 0.65.')
        expected = ('AgX', .35) if name == 'Export' else ('Standard', -.1)
        if (scene.get('engine') != 'CYCLES' or scene.get('view_transform') != expected[0] or
                abs(scene.get('exposure', 99) - expected[1]) > 1e-5 or abs(scene.get('gamma', 0)-1) > 1e-5):
            add('COLOR_MANAGEMENT', f'{name} must use Cycles/{expected[0]}, exposure {expected[1]}, gamma 1.')
        if name == 'Review':
            key = scene.get('review_key')
            if (not key or key.get('type') != 'SUN' or abs(key.get('energy', 0)-3.2)>1e-5 or
                    any(abs(a-b)>1e-5 for a,b in zip(key.get('color', []), [1,.92,.8])) or
                    abs(key.get('angle', 0)-math.radians(6))>1e-5 or not key.get('shadows')):
                add('REVIEW_KEY', 'Review_Key must be a shadow-casting Sun, energy 3.2, RGB (1, 0.92, 0.8), angle 6 degrees.')
    # Terrain support must be validated before conversion, not only at AST writing.
    by_id = {r['instance_id']: r for r in roots}
    for root in roots:
        if not visible(root):
            continue
        support = root.get('support', 'ground'); mode = root.get('terrain_follow', 'pivot')
        if mode not in ('pivot', 'shared-support-pivot'):
            add('TERRAIN_MODE', 'Use explicit pivot or shared-support-pivot terrain mode.', [root['name']])
        chain = {root['instance_id']}; target = support
        while target not in ('ground', 'building'):
            if target in chain or target not in by_id:
                add('SUPPORT_REFERENCE', 'Missing or cyclic attachment support.', [root['name']]); break
            chain.add(target); target = by_id[target].get('support', 'ground')
        if mode == 'shared-support-pivot':
            ref = by_id.get(support)
            if not ref or any(abs(a-b) > 1e-4 for a,b in zip(root.get('position', []), ref.get('position', []))):
                add('SUPPORT_PIVOT', 'Shared-support pivots must coincide in XYZ.', [root['name']])
        elif support != 'ground':
            add('SUPPORT_HEIGHT', 'Supported prop needs an explicit shared-height attachment arrangement.', [root['name']])
    for code, message in VISUAL_CHECKS.items():
        add(code, message, severity='review')
    add('NATIVE_SOURCE_PARITY', 'Full export decode must verify every attachment against its canonical library/custom master.', severity='review')
    errors = sum(f['severity'] == 'error' for f in findings)
    return dict(schema_version=VERSION, status='failed' if errors else 'review_required',
                automated_pass=not errors, error_count=errors,
                warning_count=sum(f['severity'] == 'warning' for f in findings), source=snapshot.get('source'),
                counts={'main_vertices': direct_count, 'main_maximum': budget,
                        'budget_vertices': budget_count, 'bespoke_attachment_vertices': bespoke_count,
                        'bespoke_decal_vertices': decal_count,
                        'reused_attachment_vertices': attachment_count - bespoke_count,
                        'attachment_vertices': attachment_count, 'attachment_instances':sum(visible(r) for r in roots),
                        'visible_export_vertices':direct_count + attachment_count,
                        'visible_scene_vertices':direct_count + attachment_count + decal_count}, findings=findings)


def export_vertex_count(mesh):
    keys = set()
    for polygon in mesh.polygons:
        for i in polygon.loop_indices:
            keys.add((mesh.loops[i].vertex_index,) + tuple(round(v, 8) for uv in mesh.uv_layers for v in uv.data[i].uv))
    return len(keys)


def collect_snapshot():
    import bpy
    from mathutils import Matrix
    memberships = {}
    for scene in bpy.data.scenes:
        for obj in scene.objects:
            memberships.setdefault(obj.name, []).append(scene.name)
    snapshot = {'source': bpy.data.filepath, 'objects': [], 'scenes': {}, 'images': []}
    export = bpy.data.scenes.get('Export')
    snapshot['main_geometry_maximum'] = export.get('main_geometry_maximum', 2200) if export else 2200
    image_users = {}
    for ob in bpy.data.objects:
        row = {'name':ob.name, 'type':ob.type, 'scenes':memberships.get(ob.name, []),
               'parent':ob.parent.name if ob.parent else None, 'children':[c.name for c in ob.children],
               'role':ob.get('export_role'), 'instance_id':ob.get('instance_id'),
               'source_asset_id':ob.get('source_asset_id'), 'library_source':ob.get('library_source'),
               'source_geometry_id':ob.get('source_geometry_id'), 'review_only':bool(ob.get('review_only')),
               'reuse_approved':bool(ob.get('reuse_approved')), 'reuse_scope':ob.get('reuse_scope'),
               'reuse_reference':ob.get('reuse_reference'),
               'budget_role':ob.get('budget_role'),
               'excluded':bool(ob.hide_render or ob.get('csc_export_exclude')),
               'support':ob.get('support','ground'), 'terrain_follow':ob.get('terrain_follow','pivot')}
        pos, rot, scale = ob.matrix_world.decompose()
        reconstructed = Matrix.LocRotScale(pos, rot, scale)
        row.update(position=list(pos), scale=list(scale), determinant=ob.matrix_world.determinant(),
                   shear=max(abs(a-b) for r,s in zip(reconstructed,ob.matrix_world) for a,b in zip(r,s)))
        if ob.type == 'MESH':
            groups = {g.index for g in ob.vertex_groups if g.name != 'VERTEX_KEYS'}
            weights = [[g.weight for g in v.groups if g.group in groups and g.weight > 0] for v in ob.data.vertices]
            row.update(export_vertices=export_vertex_count(ob.data), uv_layers=len(ob.data.uv_layers),
                       static_weights=all(len(w)==1 and abs(w[0]-1)<1e-5 for w in weights),
                       unsupported_modifiers=[m.type for m in ob.modifiers if m.type!='ARMATURE'],
                       materials=[m.name for m in ob.data.materials if m])
            if set(row['scenes']) & {'Export','Review'} and not row['excluded']:
                for mat in ob.data.materials:
                    for node in mat.node_tree.nodes if mat and mat.use_nodes else []:
                        if node.type=='TEX_IMAGE' and node.image and node.image.source=='FILE':
                            image_users.setdefault(node.image.name, {'image':node.image, 'objects':set()})['objects'].add(ob.name)
        snapshot['objects'].append(row)
    for usage in image_users.values():
        im = usage['image']; path = Path(bpy.path.abspath(im.filepath, library=im.library))
        snapshot['images'].append({'path':str(path), 'packed':bool(im.packed_file),
                                   'exists':path.is_file(), 'objects':sorted(usage['objects'])})
    for scene in bpy.data.scenes:
        if scene.name not in ('Export','Review'):
            continue
        world = None
        if scene.world and scene.world.use_nodes:
            outputs = [n for n in scene.world.node_tree.nodes if n.type=='OUTPUT_WORLD' and n.is_active_output]
            links = list(outputs[0].inputs['Surface'].links) if outputs else []
            node = links[0].from_node if links else None
            if node and node.type=='BACKGROUND':
                world = {'color':list(node.inputs['Color'].default_value)[:3],
                         'strength':node.inputs['Strength'].default_value,
                         'dynamic':bool(node.inputs['Color'].is_linked or node.inputs['Strength'].is_linked)}
        snapshot['scenes'][scene.name] = {'world':world, 'engine':scene.render.engine,
            'view_transform':scene.view_settings.view_transform, 'exposure':scene.view_settings.exposure,
            'gamma':scene.view_settings.gamma}
        key = scene.objects.get('Review_Key')
        if key and key.type == 'LIGHT':
            snapshot['scenes'][scene.name]['review_key'] = dict(
                type=key.data.type, energy=key.data.energy, color=list(key.data.color),
                angle=key.data.angle, shadows=key.data.use_shadow)
    return snapshot


def validate_current_scene():
    return validate_snapshot(collect_snapshot())


@contextmanager
def suspend_csc_repairs():
    """Saved-file audits must not trigger the add-on's automatic repair hooks."""
    import bpy
    removed = []
    for name in ('load_post', 'depsgraph_update_post'):
        handlers = getattr(bpy.app.handlers, name)
        for index, callback in reversed(list(enumerate(handlers))):
            if callback.__module__.rsplit('.', 1)[-1] == 'csc_scene_tools':
                handlers.remove(callback)
                removed.append((handlers, index, callback))
    try:
        yield
    finally:
        for handlers, index, callback in reversed(removed):
            if callback not in handlers:
                handlers.insert(min(index, len(handlers)), callback)


def format_report(report):
    lines = [f'CSC scene validation: {report["status"]}',
             f'Budget: {report["counts"]["budget_vertices"]}/{report["counts"]["main_maximum"]} vertices '
             f'(direct {report["counts"]["main_vertices"]} + bespoke attachments {report["counts"]["bespoke_attachment_vertices"]} + bespoke decals {report["counts"]["bespoke_decal_vertices"]}); '
             f'reused attachments excluded: {report["counts"]["reused_attachment_vertices"]}. '
             f'All attachments: {report["counts"]["attachment_instances"]} / {report["counts"]["attachment_vertices"]} vertices.']
    for f in report['findings']:
        lines.append(f'{f["severity"].upper()} [{f["code"]}] {f["message"]}' +
                     (' Objects: '+', '.join(f['objects']) if f['objects'] else ''))
    return '\n'.join(lines)+'\n'


def main():
    import bpy
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--blend', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    before = hashlib.sha256(args.blend.read_bytes()).hexdigest()
    with suspend_csc_repairs():
        bpy.ops.wm.open_mainfile(filepath=str(args.blend), load_ui=False, use_scripts=False)
        report = validate_current_scene()
    assert hashlib.sha256(args.blend.read_bytes()).hexdigest() == before, 'Validation changed source blend'
    report['source_sha256'] = before
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    args.output.with_suffix('.txt').write_text(format_report(report), encoding='utf-8')
    print(format_report(report))
    if report['error_count']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
