"""Blender: remap the two authored workshop bench variants without moving them.

Run with --python-exit-code 1 --python SCRIPT -- LIBRARY REVISION REVIEW_OUTPUT.
Backs up every edited source under REVIEW_OUTPUT/backups before saving.
"""
import bpy
import hashlib
import json
from pathlib import Path
import shutil
import sys
from mathutils import Vector

LIBRARY, REVISION, OUTPUT = map(Path, sys.argv[sys.argv.index('--') + 1:])
TARGETS = ('CSC_Attached_Workbench_Long_Narrow', 'CSC_Attached_Seating_Bench')
TEXTURES = LIBRARY.parents[1] / 'Textures/CSC_Props/Current/textures'
OLD_AO = LIBRARY / 'textures/CSC_Atlas_Props_AO.png'
OUTPUT.mkdir(parents=True, exist_ok=True)
REPORT = []


def geometry_signature(mesh):
    data = {'vertices': [list(v.co) for v in mesh.vertices],
            'faces': [list(p.vertices) for p in mesh.polygons],
            'uv2': [list(v.uv) for v in mesh.uv_layers[1].data],
            'uv3': [list(v.uv) for v in mesh.uv_layers[2].data]}
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()


def components(mesh):
    # Weld only for component identification, leaving actual vertices untouched.
    keys = [tuple(round(c, 5) for c in v.co) for v in mesh.vertices]
    parent = {k: k for k in keys}
    def find(k):
        while parent[k] != k:
            parent[k] = parent[parent[k]]
            k = parent[k]
        return k
    for face in mesh.polygons:
        first = find(keys[face.vertices[0]])
        for vi in face.vertices[1:]:
            parent[find(keys[vi])] = first
    result = {}
    for vi, k in enumerate(keys):
        result.setdefault(find(k), []).append(vi)
    return list(result.values())


def remap(mesh):
    before = geometry_signature(mesh)
    assert len(mesh.uv_layers) == 3
    uv = mesh.uv_layers[0]
    bounds = {}
    for indices in components(mesh):
        lo = [min(mesh.vertices[i].co[a] for i in indices) for a in range(3)]
        hi = [max(mesh.vertices[i].co[a] for i in indices) for a in range(3)]
        for i in indices:
            bounds[i] = lo, hi
    for face in mesh.polygons:
        lo, hi = bounds[face.vertices[0]]
        normal_axis = max(range(3), key=lambda a: abs(face.normal[a]))
        axes = [a for a in range(3) if a != normal_axis]
        grain = max(axes, key=lambda a: hi[a] - lo[a])
        across = next(a for a in axes if a != grain)
        length = max(hi[grain] - lo[grain], 1e-8)
        width = max(hi[across] - lo[across], 1e-8)
        # dark_timber: [132,4,252,124], in the 1024px atlas. Additional 1px inset.
        # V follows each component face's longest axis; coplanar triangles agree.
        span_u = 118 / 1024 * min(1.0, width / length)
        for li in face.loop_indices:
            co = mesh.vertices[mesh.loops[li].vertex_index].co
            u = (co[across] - lo[across]) / width
            v = (co[grain] - lo[grain]) / length
            uv.data[li].uv = (192 / 1024 + (u - .5) * span_u, 1 - 123 / 1024 + v * 118 / 1024)
    assert geometry_signature(mesh) == before
    return before


def material(name, uv_names):
    mat = bpy.data.materials.new(name + '_Dark_Timber_Material')
    mat.use_nodes = True
    mat['civ_material'] = 'CSC_ALL_Props_01'
    mat['civ_ao_texture'] = 'CSC_Atlas_Props_AO'
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bs = nodes.new('ShaderNodeBsdfPrincipled')
    links.new(bs.outputs['BSDF'], out.inputs['Surface'])
    uv1 = nodes.new('ShaderNodeUVMap'); uv1.uv_map = uv_names[0]
    uv2 = nodes.new('ShaderNodeUVMap'); uv2.uv_map = uv_names[1]
    images = {}
    for slot in ('B', 'N', 'G', 'M', 'AO'):
        path = OLD_AO if slot == 'AO' else TEXTURES / ('CSC_Props_Shared_01_' + slot + '.png')
        assert path.is_file(), path
        im = bpy.data.images.load(str(path), check_existing=True)
        im.colorspace_settings.name = 'sRGB' if slot == 'B' else 'Non-Color'
        tex = nodes.new('ShaderNodeTexImage'); tex.image = im; tex.label = slot
        links.new((uv2 if slot == 'AO' else uv1).outputs['UV'], tex.inputs['Vector'])
        images[slot] = tex
    mix = nodes.new('ShaderNodeMixRGB'); mix.blend_type = 'MULTIPLY'; mix.inputs[0].default_value = 1
    links.new(images['B'].outputs['Color'], mix.inputs[1]); links.new(images['AO'].outputs['Color'], mix.inputs[2])
    links.new(mix.outputs[0], bs.inputs['Base Color'])
    normal = nodes.new('ShaderNodeNormalMap'); normal.uv_map = uv_names[0]
    links.new(images['N'].outputs['Color'], normal.inputs['Color']); links.new(normal.outputs[0], bs.inputs['Normal'])
    inv = nodes.new('ShaderNodeMath'); inv.operation = 'SUBTRACT'; inv.inputs[0].default_value = 1
    links.new(images['G'].outputs['Color'], inv.inputs[1]); links.new(inv.outputs[0], bs.inputs['Roughness'])
    links.new(images['M'].outputs['Color'], bs.inputs['Metallic'])
    return mat


def identity(ob):
    if ob.type != 'MESH':
        return None
    for name in TARGETS:
        if ob.get('source_asset_id') == name or ob.name.startswith(name) or any(m and m.name.startswith(name + '_') for m in ob.data.materials):
            return name
    return None


files = [(LIBRARY / (n + '.blend'), 'library') for n in TARGETS]
files += [(p, 'scenes') for p in sorted(REVISION.glob('*.blend')) if 'PIL_Decals' not in p.name]
for path, group in files:
    backup = OUTPUT / 'backups' / group / path.name
    assert not backup.exists(), 'Use a fresh output folder'
    backup.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(path, backup)
    bpy.ops.wm.open_mainfile(filepath=str(path))
    matrices = {ob.name: [list(row) for row in ob.matrix_world] for ob in bpy.data.objects}
    signatures = {}; changed = []; handled = set()
    for ob in bpy.data.objects:
        name = identity(ob)
        if not name or ob.data.as_pointer() in handled:
            continue
        handled.add(ob.data.as_pointer())
        signatures[ob.name] = remap(ob.data)
        mat = material(name, [u.name for u in ob.data.uv_layers])
        ob.data.materials.clear(); ob.data.materials.append(mat)
        for face in ob.data.polygons: face.material_index = 0
        changed.append(ob.name)
    assert changed, path
    assert all(matrices[ob.name] == [list(row) for row in ob.matrix_world] for ob in bpy.data.objects)
    bpy.ops.wm.save_as_mainfile(filepath=str(path), check_existing=False)
    bpy.ops.wm.open_mainfile(filepath=str(path))
    for name, sig in signatures.items():
        ob = bpy.data.objects[name]
        assert geometry_signature(ob.data) == sig
        assert ob.data.materials[0]['civ_material'] == 'CSC_ALL_Props_01'
        assert ob.data.materials[0]['civ_ao_texture'] == 'CSC_Atlas_Props_AO'
        assert all(133/1024-1e-6 <= v.uv.x <= 251/1024+1e-6 and 1-123/1024-1e-6 <= v.uv.y <= 1-5/1024+1e-6 for v in ob.data.uv_layers[0].data)
    assert all(matrices[ob.name] == [list(row) for row in ob.matrix_world] for ob in bpy.data.objects)
    REPORT.append({'source': str(path), 'backup': str(backup), 'objects': changed,
                   'geometry_uv2_uv3_and_transforms_unchanged': True})

catalogue = LIBRARY / 'catalogue.json'
shutil.copy2(catalogue, OUTPUT / 'backups/library/catalogue.json')
data = json.loads(catalogue.read_text())
for entry in data['assets']:
    if entry['asset_id'] in TARGETS:
        entry['reuse_notes'] = 'UV1 remapped to Shared_01 dark_timber; CSC_ALL_Props_01 material. Original UV2 and CSC_Atlas_Props_AO retained through asset AO override. Geometry, pivots and UV3 unchanged.'
        entry['material'] = 'CSC_ALL_Props_01'
        entry['ao_override'] = 'CSC_Atlas_Props_AO'
        entry['textures'] = ['CSC_Props_Shared_01_' + s + '.png' for s in ('B', 'N', 'G', 'M')] + ['CSC_Atlas_Props_AO.png']
catalogue.write_text(json.dumps(data, indent=2) + '\n')
(OUTPUT / 'source-update-report.json').write_text(json.dumps(REPORT, indent=2) + '\n')
print('VERIFIED_DARK_TIMBER_UPDATE', json.dumps(REPORT))
