"""Blender-only, read-only scene decoder. Run through export_scene.py decode."""
import bpy
import bmesh
import hashlib
import json
import math
import sys
from pathlib import Path
from mathutils import Matrix


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
        if im.packed_file or not p.is_file():
            raise ValueError(f'{mat.name}: external image missing or packed: {p}')
        if key in result['images']:
            raise ValueError(f'{mat.name}: ambiguous image slot {key}')
        result['images'][key] = {'path': str(p), 'sha256': digest(p), 'size': list(im.size)}
    if result.get('ao_texture') and 'AO' not in result['images']:
        raise ValueError(f'{mat.name}: civ_ao_texture requires an external image node labelled AO')
    return result


def decode_mesh(ob, transform):
    # Only static, fully weighted geometry is supported. Never repair source data silently.
    if len(ob.data.uv_layers) != 3:
        raise ValueError(f'{ob.name}: expected exactly three UV layers')
    if any(m.type != 'ARMATURE' for m in ob.modifiers):
        raise ValueError(f'{ob.name}: evaluate/resolve non-armature modifiers before export')
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
        vertices, faces, lookup = [], [], {}
        # Sort by material so GEO group primitive ranges match CN6 triangle order.
        for tri in sorted(mesh.loop_triangles, key=lambda t: t.material_index):
            if tri.material_index >= len(materials):
                raise ValueError(f'{ob.name}: missing material')
            face = []
            for li in tri.loops:
                loop = mesh.loops[li]
                uv = [x for layer in mesh.uv_layers for x in (layer.data[li].uv.x, 1-layer.data[li].uv.y)]
                row = list(mesh.vertices[loop.vertex_index].co) + list(loop.normal) + list(loop.tangent) + list(loop.bitangent) + uv
                if not all(math.isfinite(x) for x in row):
                    raise ValueError(f'{ob.name}: nonfinite vertex frame')
                key = tuple(round(x, 7) for x in row)
                if key not in lookup:
                    lookup[key] = len(vertices)
                    vertices.append(row)
                face.append(lookup[key])
            faces.append(face + [tri.material_index])
        return {'name': ob.name, 'role': ob.get('export_role', ''), 'vertices': vertices,
                'triangles': faces, 'materials': materials, 'source_matrix_world': matrix(ob.matrix_world)}
    finally:
        bpy.data.meshes.remove(mesh)


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
        for child in children:
            if max(abs(a-b) for row,ref in zip(o.matrix_world.inverted() @ child.matrix_world, Matrix.Identity(4)) for a,b in zip(row,ref)) > 1e-4:
                raise ValueError(f'{instance}: mesh child has a placement offset; move it to the root')
        attachments.append({'source_mesh_signatures':sorted(mesh_signature(child.data) for child in children), 'instance_id': instance, 'source_asset_id': o['source_asset_id'],
            'role': o.get('export_role'), 'support': support, 'matrix_world': matrix(o.matrix_world),
            'matrix_relative_support': matrix(roots[support].matrix_world.inverted() @ o.matrix_world) if support in roots else matrix(o.matrix_world),
            'matrix_parent_inverse': matrix(o.matrix_parent_inverse),
            'position': list(pos), 'rotation_degrees': [math.degrees(v) for v in quat.to_euler('XYZ')],
            'scale': list(scale), 'shear_error': err,
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
            if role in ('building_geometry', 'fixed_geometry') or o.name.startswith('CSC_Fixed_'):
                selected.append(o)
            elif not any(parent in roots.values() for parent in parent_chain(o)):
                raise ValueError(f'{o.name}: unclassified export mesh')
        elif kind == 'decal':
            selected.append(o)
        elif kind == 'prop':
            selected.append(o)
    if not selected:
        raise ValueError(f'{path}: no {kind} meshes')
    if kind == 'prop' and attachments:
        raise ValueError('Nested asset definitions are not supported')
    for o in sorted(selected, key=lambda o:o.name):
        for parent in parent_chain(o):
            if parent.type == 'ARMATURE':
                if parent.animation_data and parent.animation_data.action:
                    raise ValueError(f'{o.name}: animated armature unsupported')
                if any(any(abs(a-b)>1e-6 for a,b in zip(row, ref)) for bone in parent.pose.bones for row,ref in zip(bone.matrix_basis, Matrix.Identity(4))):
                    raise ValueError(f'{o.name}: non-rest pose unsupported')
        geometry.append(decode_mesh(o, o.matrix_world))
    if digest(path) != before:
        raise ValueError(f'Source file changed while decoding: {path}')
    return {'asset_id': asset_id, 'kind': kind, 'source': str(path), 'source_sha256': before,
            'meshes': geometry, 'attachments': attachments}


def parent_chain(o):
    p = o.parent
    while p:
        yield p
        p = p.parent


def main():
    job_path, output = map(Path, sys.argv[sys.argv.index('--')+1:])
    job = json.loads(job_path.read_text())
    library = Path(job['library'])
    catalogue = {a['asset_id']: a for a in json.loads((library/'catalogue.json').read_text())['assets']}
    models, buildings = {}, []
    for item in job.get('props', []):
        ident = item['asset_id']
        models[ident] = inspect(Path(item['blend']), 'prop', ident, item.get('scene', 'Export'), item.get('source_sha256'))
    for item in job['buildings']:
        row = inspect(Path(item['blend']), 'building', item['asset_id'], item.get('scene', 'Export'), item.get('source_sha256'))
        if row['asset_id'] in models:
            raise ValueError(f'Duplicate model identity: {row["asset_id"]}')
        models[row['asset_id']] = row
        buildings.append(row['asset_id'])
        for a in row['attachments']:
            ident = a['source_asset_id']
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
        source_path = Path(models[ident]['source']) if ident in models else library / (ident+'.blend')
        before = digest(source_path)
        bpy.ops.wm.open_mainfile(filepath=str(source_path), load_ui=False, use_scripts=False)
        prop_scene = next((e.get('scene','Export') for e in job.get('props',[]) if e['asset_id']==ident), catalogue.get(ident,{}).get('export_scene','Export'))
        scene = bpy.data.scenes.get(prop_scene)
        if scene is None and len(bpy.data.scenes)==1: scene=bpy.data.scenes[0]
        if scene is None: raise ValueError(f'{ident}: no source export scene')
        signatures = {mesh_signature(o.data) for o in scene.objects if o.type == 'MESH'}
        layouts = {mesh_layout_signature(o.data) for o in scene.objects if o.type == 'MESH'}
        verified[ident] = {'source':str(source_path), 'sha256':before}
        refs = [(building, a) for building in buildings for a in models[building]['attachments']
                if a['source_asset_id'] == ident]
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
