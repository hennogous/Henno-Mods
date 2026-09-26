"""Blender-only, read-only scene decoder. Run through export_scene.py decode."""
import bpy
import bmesh
import hashlib
import json
import math
import sys
from pathlib import Path
from mathutils import Matrix


_RELOCATED_IMAGES = set()


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def mesh_signature(mesh):
    data = {'vertices':[list(v.co) for v in mesh.vertices],
            'polygons':[list(p.vertices) for p in mesh.polygons],
            'uvs':[[list(d.uv) for d in u.data] for u in mesh.uv_layers]}
    return hashlib.sha256(json.dumps(data,sort_keys=True).encode()).hexdigest()


def mesh_layout_signature(mesh):
    """Guard the AO/material layout when only vertex positions are edited."""
    data = {'polygons': [list(p.vertices) for p in mesh.polygons],
            'polygon_materials': [p.material_index for p in mesh.polygons],
            'uvs': [[list(d.uv) for d in u.data] for u in mesh.uv_layers],
            'materials': [m.name if m else None for m in mesh.materials]}
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()


def matrix_key(value):
    # Reparenting an imported component through an attachment empty introduces
    # harmless float32 round-off (typically 1e-5) when Blender reconstructs its
    # matrix.  Compare at Civ-scale placement precision, while still catching
    # authored rotation/scale/offset changes.
    return tuple(round(cell, 4) for row in value for cell in row)


def mesh_component_signature(mesh, local_matrix):
    data = {'mesh': mesh_signature(mesh), 'matrix': matrix_key(local_matrix)}
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()


def matrices_close(left, right, tolerance=1e-4):
    return max(abs(a - b) for row_left, row_right in zip(left, right)
               for a, b in zip(row_left, row_right)) <= tolerance


def components_match(left, right):
    """Compare a mesh assembly as a multiset with float-tolerant transforms."""
    if len(left) != len(right):
        return False
    remaining = list(right)
    for component in left:
        match = next((index for index, candidate in enumerate(remaining)
                      if component['mesh_signature'] == candidate['mesh_signature']
                      and matrices_close(component['matrix'], candidate['matrix'])), None)
        if match is None:
            return False
        remaining.pop(match)
    return True


def matrix_collections_match(left, right):
    """Compare unordered matrices without quantization-boundary false failures."""
    if len(left) != len(right):
        return False
    remaining = list(right)
    for value in left:
        match = next((index for index, candidate in enumerate(remaining)
                      if matrices_close(value, candidate)), None)
        if match is None:
            return False
        remaining.pop(match)
    return True


def matrix(m):
    return [list(r) for r in m]


def material(mat):
    if not mat:
        raise ValueError('Empty material slot')
    result = {'name': mat.name, 'images': {}}
    if mat.get('civ_material'):
        result['external'] = mat['civ_material']
    if mat.get('civ_ao_texture'):
        result['ao_texture'] = str(mat['civ_ao_texture'])
    for n in mat.node_tree.nodes if mat.use_nodes else []:
        if n.type != 'TEX_IMAGE' or not n.image:
            continue
        im = n.image
        key = n.label or n.name
        if result.get('external') and (not result.get('ao_texture') or key != 'AO'):
            continue
        if key not in ('B', 'N', 'AO', 'G', 'M', 'E', 'O', 'T'):
            continue
        p = Path(bpy.path.abspath(im.filepath)).resolve()
        if im.packed_file:
            raise ValueError(f'{mat.name}: external image is packed: {p}')
        if not p.is_file():
            # Final handoff folders are copied between Mac and Windows. Blender
            # can retain the sending host's absolute image path even though the
            # self-contained bundle has the same file beside it in textures/.
            # Resolve that exact basename read-only; never search outside the
            # active blend bundle or rewrite the source file.
            fallback = (Path(bpy.data.filepath).resolve().parent / 'textures' /
                        Path(im.filepath).name).resolve()
            if not fallback.is_file():
                raise ValueError(f'{mat.name}: external image missing: {p}; '
                                 f'bundle fallback also missing: {fallback}')
            relocation = (str(p), str(fallback))
            if relocation not in _RELOCATED_IMAGES:
                print(f'Relocated transferred image: {p} -> {fallback}')
                _RELOCATED_IMAGES.add(relocation)
            p = fallback
        if key in result['images']:
            raise ValueError(f'{mat.name}: ambiguous image slot {key}')
        result['images'][key] = {'path': str(p), 'sha256': digest(p), 'size': list(im.size)}
    if result.get('ao_texture') and 'AO' not in result['images']:
        raise ValueError(f'{mat.name}: civ_ao_texture requires an external image node labelled AO')
    return result


def decode_mesh(ob, transform, require_weights=True):
    # Only static, fully weighted geometry is supported. Never repair source data silently.
    if len(ob.data.uv_layers) != 3:
        raise ValueError(f'{ob.name}: expected exactly three UV layers')
    if any(m.type != 'ARMATURE' for m in ob.modifiers):
        raise ValueError(f'{ob.name}: evaluate/resolve non-armature modifiers before export')
    if require_weights:
        bones = {g.index for g in ob.vertex_groups if g.name != 'VERTEX_KEYS'}
        for v in ob.data.vertices:
            weights = [g.weight for g in v.groups if g.group in bones and g.weight > 0]
            if len(weights) != 1 or abs(weights[0] - 1) > 1e-5:
                raise ValueError(f'{ob.name}: vertex {v.index} is not statically weighted at 1')
    if transform.determinant() <= 0:
        raise ValueError(f'{ob.name}: singular or mirrored geometry transform unsupported')
    mesh = ob.data.copy()
    try:
        # User-authored props can contain n-gons. Tangent calculation accepts only
        # tris/quads; triangulate those faces on this temporary export copy.
        if any(len(p.vertices) > 4 for p in mesh.polygons):
            bm = bmesh.new()
            try:
                bm.from_mesh(mesh)
                bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4])
                bm.to_mesh(mesh)
            finally:
                bm.free()
        mesh.transform(transform)
        mesh.calc_loop_triangles()
        mesh.calc_tangents(uvmap=mesh.uv_layers[0].name)
        materials = [material(m) for m in mesh.materials]
        # Match the established CSC CN6 exporter: preserve topology identity and
        # split only where one of the three UV sets differs.  Per-corner normal,
        # tangent and bitangent values are averaged for each authored source
        # vertex.  Keying by the complete corner frame inflated imported Civ
        # meshes at every hard/smoothed edge (for example 448 authored Tailor
        # vertices became 1,881 export vertices).
        frames = {}
        for polygon in mesh.polygons:
            for loop_index in polygon.loop_indices:
                loop = mesh.loops[loop_index]
                frame = (tuple(loop.normal), tuple(loop.tangent), tuple(loop.bitangent))
                frames.setdefault(loop.vertex_index, []).append(frame)
        averaged_frames = {}
        for vertex_index, values in frames.items():
            averaged_frames[vertex_index] = [
                sum(frame[part][axis] for frame in values) / len(values)
                for part in range(3) for axis in range(3)
            ]
        vertices, faces, lookup = [], [], {}
        # Sort by material so GEO group primitive ranges match CN6 triangle order.
        for tri in sorted(mesh.loop_triangles, key=lambda t: t.material_index):
            if tri.material_index >= len(materials):
                raise ValueError(f'{ob.name}: missing material')
            face = []
            for li in tri.loops:
                loop = mesh.loops[li]
                uv = [x for layer in mesh.uv_layers for x in (layer.data[li].uv.x, 1-layer.data[li].uv.y)]
                row = list(mesh.vertices[loop.vertex_index].co) + averaged_frames[loop.vertex_index] + uv
                if not all(math.isfinite(x) for x in row):
                    raise ValueError(f'{ob.name}: nonfinite vertex frame')
                key = (loop.vertex_index,) + tuple(round(x, 8) for x in uv)
                if key not in lookup:
                    lookup[key] = len(vertices)
                    vertices.append(row)
                face.append(lookup[key])
            faces.append(face + [tri.material_index])
        return {'name': ob.name, 'role': ob.get('export_role', ''), 'vertices': vertices,
                'triangles': faces, 'materials': materials, 'source_matrix_world': matrix(ob.matrix_world)}
    finally:
        bpy.data.meshes.remove(mesh)


def merge_meshes(name, meshes):
    """Combine fixed building parts in the export stream without editing Blender sources."""
    materials, material_indexes = [], {}
    vertices, triangles, sources = [], [], []
    for mesh in meshes:
        local_to_merged = {}
        for index, item in enumerate(mesh['materials']):
            material_name = item['name']
            if material_name in material_indexes:
                merged_index = material_indexes[material_name]
                if materials[merged_index] != item:
                    raise ValueError(f'{name}: conflicting definitions for material {material_name}')
            else:
                merged_index = len(materials)
                material_indexes[material_name] = merged_index
                materials.append(item)
            local_to_merged[index] = merged_index
        offset = len(vertices)
        vertices.extend(mesh['vertices'])
        triangles.extend([[a + offset, b + offset, c + offset, local_to_merged[material]]
                          for a, b, c, material in mesh['triangles']])
        sources.append({'name': mesh['name'], 'matrix_world': mesh['source_matrix_world']})
    triangles.sort(key=lambda triangle: triangle[3])
    return {'name': name, 'role': 'fixed_geometry', 'vertices': vertices,
            'triangles': triangles, 'materials': materials, 'source_meshes': sources}


def inspect(path, kind, asset_id, scene_name='Export', expected_sha=None):
    before = digest(path)
    if expected_sha and before != expected_sha:
        raise ValueError(f'{path}: changed since discovery; rerun export')
    bpy.ops.wm.open_mainfile(filepath=str(path), load_ui=False, use_scripts=False)
    scene = bpy.data.scenes.get(scene_name)
    if not scene and kind == 'prop' and len(bpy.data.scenes) == 1:
        scene = bpy.data.scenes[0]
    if not scene:
        raise ValueError(f'{path}: no scene {scene_name!r}')
    bpy.context.window.scene = scene
    scene.view_layers[0].update()
    attachments, geometry = [], []
    roots = {o['instance_id']: o for o in scene.objects if o.type == 'EMPTY' and o.get('instance_id')}
    if len(roots) != sum(o.type == 'EMPTY' and bool(o.get('instance_id')) for o in scene.objects):
        raise ValueError('Duplicate attachment instance IDs')
    for instance, o in sorted(roots.items()):
        if o.hide_render or o.get('csc_export_exclude'):
            continue
        if not o.get('source_asset_id'):
            raise ValueError(f'{instance}: missing source_asset_id')
        support = o.get('support', 'ground')
        if support not in ('ground', 'building') and support not in roots:
            raise ValueError(f'{instance}: unknown support {support}')
        pos, quat, scale = o.matrix_world.decompose()
        reconstructed = Matrix.LocRotScale(pos, quat, scale)
        err = max(abs(a-b) for r,s in zip(reconstructed, o.matrix_world) for a,b in zip(r,s))
        children = [child for child in o.children if child.type == 'MESH' and
                    not child.hide_render and not child.get('csc_export_exclude')]
        if not children:
            raise ValueError(f'{instance}: attachment has no direct mesh children')
        component_transforms = bool(o.get('component_transforms', False))
        if component_transforms and o.get('export_role') != 'custom_attachment':
            raise ValueError(f'{instance}: component transforms require an explicit custom attachment master')
        relative_meshes = [(child, o.matrix_world.inverted() @ child.matrix_world)
                           for child in children]
        attachments.append({
            'source_components': [
                {'mesh_signature': mesh_signature(child.data), 'matrix': matrix(relative)}
                for child, relative in relative_meshes],
            'source_mesh_signatures': sorted(mesh_signature(child.data)
                                             for child, _ in relative_meshes),
            'source_component_signatures': sorted(mesh_component_signature(child.data, relative)
                                                  for child, relative in relative_meshes),
            'source_local_matrices': sorted(matrix_key(relative)
                                            for _, relative in relative_meshes),
            'instance_id': instance, 'source_asset_id': o['source_asset_id'],
            'role': o.get('export_role'), 'support': support, 'matrix_world': matrix(o.matrix_world),
            'matrix_relative_support': matrix(roots[support].matrix_world.inverted() @ o.matrix_world) if support in roots else matrix(o.matrix_world),
            'matrix_parent_inverse': matrix(o.matrix_parent_inverse),
            'position': list(pos), 'rotation_degrees': [math.degrees(v) for v in quat.to_euler('XYZ')],
            'scale': list(scale), 'shear_error': err,
            'terrain_follow': str(o.get('terrain_follow', 'pivot')),
            'component_frames': [
                {'component': child.get('source_component', child.data.name),
                 'signature': mesh_signature(child.data),
                 'matrix': matrix(o.matrix_world.inverted() @ child.matrix_world)}
                for child in children] if component_transforms else [],
            'pillaged': bool(o.get('pillaged_visibility', False)),
            'construction': bool(o.get('construction_visibility', False))})
    selected = []
    for o in scene.objects:
        if o.type != 'MESH':
            continue
        if kind == 'building' and (o.hide_render or o.get('csc_export_exclude') or any(
                parent.hide_render or parent.get('csc_export_exclude')
                for parent in parent_chain(o))):
            continue
        role = o.get('export_role', '')
        if o.name.startswith('REVIEW_'):
            raise ValueError(f'Review object leaked into Export: {o.name}')
        if kind == 'building':
            # An attachment child belongs to its reusable asset, even if it
            # carries an old fixed-geometry role from a scene import.
            if any(parent in roots.values() for parent in parent_chain(o)):
                continue
            if role in ('building_geometry', 'fixed_geometry') or o.name.startswith('CSC_Fixed_'):
                selected.append(o)
            else:
                raise ValueError(f'{o.name}: unclassified export mesh')
        elif kind == 'shared_geometry':
            if o.hide_render or o.get('csc_export_exclude') or role != 'state_geometry':
                raise ValueError(f'{o.name}: shared construction geometry must be renderable state_geometry')
            selected.append(o)
        elif kind == 'decal':
            selected.append(o)
        elif kind == 'prop':
            selected.append(o)
    if not selected:
        raise ValueError(f'{path}: no {kind} meshes')
    if kind in ('prop','shared_geometry') and attachments:
        raise ValueError(f'{kind}: nested attachments are not supported')
    for o in sorted(selected, key=lambda o:o.name):
        for parent in parent_chain(o):
            if parent.type == 'ARMATURE':
                if parent.animation_data and parent.animation_data.action:
                    raise ValueError(f'{o.name}: animated armature unsupported')
                if any(any(abs(a-b)>1e-6 for a,b in zip(row, ref)) for bone in parent.pose.bones for row,ref in zip(bone.matrix_basis, Matrix.Identity(4))):
                    raise ValueError(f'{o.name}: non-rest pose unsupported')
        # Shared construction geometry is baked to a new static identity skeleton;
        # source vertex-group weights are not serialized into this CN6 stream.
        geometry.append(decode_mesh(o, o.matrix_world, require_weights=kind!='shared_geometry'))
    if kind == 'building':
        fixed = [mesh for mesh in geometry if (mesh['role'] == 'fixed_geometry'
                 or mesh['name'].startswith('CSC_Fixed_')) and 'leanto' not in mesh['name'].casefold()]
        if len(fixed) > 1:
            primary = [mesh for mesh in geometry if mesh not in fixed]
            geometry = primary + [merge_meshes(asset_id + '_Fixed', fixed)]
    if digest(path) != before:
        raise ValueError(f'Source file changed while decoding: {path}')
    return {'asset_id': asset_id, 'kind': kind, 'source': str(path), 'source_sha256': before,
            'component_frames': [
                {'component': ob.get('source_component', ob.data.name),
                 'signature': mesh_signature(ob.data), 'matrix': matrix(ob.matrix_world)}
                for ob in selected] if kind == 'prop' else [],
            'meshes': geometry, 'attachments': attachments}


def parent_chain(o):
    p = o.parent
    while p:
        yield p
        p = p.parent


def validate_component_frames(placed, master, label):
    """Allow authored assembly transforms only when its standalone master agrees."""
    by_name = {c['component']: c for c in master}
    if len(by_name) != len(master) or len({c['component'] for c in placed}) != len(placed):
        raise ValueError(f'{label}: duplicate component identity')
    if {c['component'] for c in placed} != set(by_name):
        raise ValueError(f'{label}: component inventory differs from master')
    for c in placed:
        ref = by_name[c['component']]
        if c['signature'] != ref['signature'] or max(
                abs(a-b) for row, target in zip(c['matrix'], ref['matrix'])
                for a,b in zip(row, target)) > 1e-4:
            raise ValueError(f'{label}/{c["component"]}: geometry, UVs or relative placement differs from master')


def source_mesh_components(scene, ident, native_record=None):
    meshes = [o for o in scene.objects if o.type == 'MESH']
    # Match the native importer's assembly, excluding hidden alternate states.
    # Explicit custom masters pass no record and retain their complete assembly.
    if native_record and native_record.get('components'):
        selected = {c['object'] for c in native_record['components']
                    if c.get('default_visible', True)}
        meshes = [o for o in meshes if o.name in selected]
        if not selected or {o.name for o in meshes} != selected:
            raise ValueError(f'{ident}: default-visible catalogue components missing from source')
    return meshes


def main():
    job_path, output = map(Path, sys.argv[sys.argv.index('--')+1:])
    job = json.loads(job_path.read_text())
    library = Path(job['library'])
    catalogue = {a['asset_id']: a for a in json.loads((library/'catalogue.json').read_text())['assets']}
    references = {item['asset_id']: item for item in job.get('references', [])}
    models, buildings = {}, []
    for item in job.get('props', []):
        ident = item['asset_id']
        models[ident] = inspect(Path(item['blend']), 'prop', ident, item.get('scene', 'Export'), item.get('source_sha256'))
    for item in job.get('shared_geometries', []):
        ident = item['geometry_id']
        if ident in models:
            raise ValueError(f'Duplicate model identity: {ident}')
        models[ident] = inspect(Path(item['blend']), 'shared_geometry', ident, item.get('scene', 'Export'), item.get('source_sha256'))
    for item in job['buildings']:
        row = inspect(Path(item['blend']), 'building', item['asset_id'], item.get('scene', 'Export'), item.get('source_sha256'))
        if row['asset_id'] in models:
            raise ValueError(f'Duplicate model identity: {row["asset_id"]}')
        models[row['asset_id']] = row
        buildings.append(row['asset_id'])
        for a in row['attachments']:
            ident = a['source_asset_id']
            if ident in references:
                continue
            if ident in models:
                if models[ident]['kind'] != 'prop':
                    raise ValueError(f'{ident}: attachment identity conflicts with non-prop model')
                continue
            if ident not in catalogue:
                raise ValueError(f'{ident}: absent from reusable catalogue; publish the custom prop first')
            source = catalogue[ident]
            if source.get('origin') == 'authored_blender' and ident not in models:
                # Flat catalogue filenames are stable across hosts.
                path = library / (ident + '.blend')
                models[ident] = inspect(path, 'prop', ident, source.get('export_scene', 'Export'))
    # Native assets always remain verbatim. A CSC-owned, single-mesh prop may use
    # an edited scene mesh as the definition for this batch, provided all divergent
    # placements agree. Existing master-matching placements inherit that definition.
    # No extra identity is registered and AO is not rebaked here.
    reused = {a['source_asset_id'] for ident in buildings for a in models[ident]['attachments']}
    verified = {}
    for ident in sorted(reused):
        if ident in references:
            continue
        source_path = (Path(models[ident]['source']) if ident in models else
                       library / (ident+'.blend'))
        before = digest(source_path)
        bpy.ops.wm.open_mainfile(filepath=str(source_path), load_ui=False, use_scripts=False)
        prop_scene = next((e.get('scene','Export') for e in job.get('props',[])
                           if e['asset_id']==ident), catalogue.get(ident,{}).get('export_scene','Export'))
        scene = bpy.data.scenes.get(prop_scene)
        if scene is None and len(bpy.data.scenes)==1: scene=bpy.data.scenes[0]
        if scene is None: raise ValueError(f'{ident}: no source export scene')
        source_meshes = source_mesh_components(
            scene, ident, catalogue.get(ident) if ident not in models else None)
        signatures = {mesh_signature(o.data) for o in source_meshes}
        layouts = {mesh_layout_signature(o.data) for o in source_meshes}
        component_signatures = sorted(mesh_component_signature(o.data, o.matrix_world)
                                      for o in source_meshes)
        source_components = [
            {'mesh_signature': mesh_signature(o.data), 'matrix': matrix(o.matrix_world)}
            for o in source_meshes]
        local_matrices = sorted(matrix_key(o.matrix_world) for o in source_meshes)
        verified[ident] = {'source':str(source_path), 'sha256':before}
        refs = [(building, a) for building in buildings for a in models[building]['attachments']
                if a['source_asset_id'] == ident]
        for building, placement in refs:
            if placement.get('component_frames'):
                if ident not in models or models[ident]['kind'] != 'prop':
                    raise ValueError(f'{building}/{placement["instance_id"]}: missing explicit custom component master')
                validate_component_frames(placement['component_frames'], models[ident]['component_frames'],
                                          f'{building}/{placement["instance_id"]}')
        for building, attachment in refs:
            if components_match(attachment['source_components'], source_components):
                continue
            if set(attachment['source_mesh_signatures']) <= signatures:
                raise ValueError(f'{building}/{attachment["instance_id"]}: local mesh transforms '
                                 f'diverge from {ident}; preserve the standalone asset assembly')
        divergent = [(building, a) for building, a in refs
                     if not set(a['source_mesh_signatures']) <= signatures]
        if divergent:
            origin = catalogue.get(ident, {}).get('origin')
            source_is_library = source_path.resolve() == (library / (ident + '.blend')).resolve()
            if origin != 'authored_blender' or not ident.startswith('CSC_') or not source_is_library:
                first, a = divergent[0]
                raise ValueError(f'{first}/{a["instance_id"]}: geometry/UVs diverge from {ident}; native assets and explicit local masters must match their source')
            if len(models[ident]['meshes']) != 1 or any(len(a['source_mesh_signatures']) != 1 for _, a in refs):
                raise ValueError(f'{ident}: scene geometry edits require a single-mesh CSC asset')
            if any(not matrix_collections_match(
                    [component['matrix'] for component in a['source_components']],
                    [component['matrix'] for component in source_components])
                   for _, a in divergent):
                raise ValueError(f'{ident}: edited scene geometry changed its asset-local transform')
            variants = {a['source_mesh_signatures'][0] for _, a in divergent}
            if len(variants) != 1:
                raise ValueError(f'{ident}: edited placements use different geometry/UVs; use one reusable definition')
            building, sample = divergent[0]
            bpy.ops.wm.open_mainfile(filepath=models[building]['source'], load_ui=False, use_scripts=False)
            building_scene = bpy.data.scenes.get(next((e.get('scene', 'Export') for e in job['buildings']
                                                      if e['asset_id'] == building), 'Export'))
            root = next((o for o in building_scene.objects if o.type == 'EMPTY' and
                         o.get('instance_id') == sample['instance_id']), None)
            children = [o for o in root.children if o.type == 'MESH' and not o.hide_render
                        and not o.get('csc_export_exclude')] if root else []
            if len(children) != 1:
                raise ValueError(f'{building}/{sample["instance_id"]}: expected one edited mesh')
            child = children[0]
            if mesh_signature(child.data) != next(iter(variants)):
                raise ValueError(f'{building}/{sample["instance_id"]}: edited mesh changed since inspection')
            if mesh_layout_signature(child.data) not in layouts:
                raise ValueError(f'{building}/{sample["instance_id"]}: topology, material or UV layout changed; update the library master and AO deliberately')
            model_mesh_name = models[ident]['meshes'][0]['name']
            edited = decode_mesh(child, Matrix.Identity(4))
            edited['name'] = model_mesh_name
            models[ident]['meshes'] = [edited]
            models[ident]['scene_geometry_edit'] = {
                'building': building, 'instance_id': sample['instance_id'],
                'asset_id': ident, 'master_sha256': before,
                'ao_rebaked': False, 'placements': len(refs),
                'edited_placements': len(divergent),
                'behavior': 'one edited CSC asset definition affects all placements of this ID'}
        if digest(source_path) != before: raise ValueError(f'Library source changed: {source_path}')
    for item in job.get('decals', []):
        ident = item['geometry_id']
        if ident in models: raise ValueError(f'Duplicate model identity: {ident}')
        models[ident] = inspect(Path(item['blend']), 'decal', ident, item.get('scene','Export'), item.get('source_sha256'))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps({'schema_version':1, 'buildings':buildings, 'models':models, 'library_sources':verified}, indent=2)+'\n')
    print(f'Decoded {len(models)} geometries; source blends unchanged: {output}')

if __name__ == '__main__':
    main()
