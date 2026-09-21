"""Targeted September 2026 workbench atlas repair; run through Blender.

Stages corrected copies and a preservation report. --install-sources installs
those verified copies with backups; geometry, placements, UV2 and UV3 are locked.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys

import bpy

IDENT = 'CSC_ALL_Workbench_Narrow'


def signature():
    records = []
    for ob in bpy.data.objects:
        record = [ob.name, list(map(list, ob.matrix_world)),
                  list(map(list, ob.matrix_basis)), ob.parent.name if ob.parent else None]
        if ob.type == 'MESH':
            record += [[list(v.co) for v in ob.data.vertices],
                       [list(p.vertices) for p in ob.data.polygons],
                       [[list(d.uv) for d in u.data] for u in ob.data.uv_layers[1:]]]
        records.append(record)
    return hashlib.sha256(json.dumps(records, sort_keys=True).encode()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--library', type=Path, required=True)
    parser.add_argument('--scenes', type=Path, required=True)
    parser.add_argument('--atlas', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--install-sources', action='store_true')
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    sources = [args.library / (IDENT + '.blend')]
    sources += sorted(args.scenes.glob('CSC_TAILORS_Textile_Workshop*FINAL.blend'))
    args.output.mkdir(parents=True, exist_ok=True)
    report = []
    region = next(r for r in json.loads((args.atlas / 'atlas/manifest.json').read_text())['regions']
                  if r['name'] == 'dark_timber')
    assert region['bounds'] == [132, 4, 252, 124]
    for source in sources:
        bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False, use_scripts=False)
        targets = {o.data for o in bpy.data.objects if o.type == 'MESH' and
                   (o.data.name == IDENT or o.get('source_asset_id') == IDENT or o.name == IDENT)}
        if not targets:
            continue
        before = signature()
        for mesh in targets:
            uv = mesh.uv_layers[0].data
            lo = [min(d.uv[i] for d in uv) for i in range(2)]
            hi = [max(d.uv[i] for d in uv) for i in range(2)]
            # Keep all chart proportions and orientation, centered inside padded paint.
            factor = min((120 / 1024) / (hi[i] - lo[i]) for i in range(2))
            center = [192 / 1024, 1 - 64 / 1024]
            for d in uv:
                d.uv = [center[i] + (d.uv[i] - (lo[i] + hi[i]) / 2) * factor for i in range(2)]
            for mat in mesh.materials:
                mat['civ_material'] = 'CSC_ALL_Props_01'
                mat['source_material_id'] = 'CSC_ALL_Props_01'
                bindings = json.loads(mat.get('effective_texture_bindings', '{}'))
                for slot, suffix in [('BaseColor', 'B'), ('Normal', 'N'), ('Gloss', 'G'), ('Metalness', 'M')]:
                    bindings[slot] = 'CSC_Props_Shared_01_' + suffix
                mat['effective_texture_bindings'] = json.dumps(bindings, sort_keys=True)
                for node in mat.node_tree.nodes if mat.use_nodes else []:
                    if node.type == 'TEX_IMAGE' and node.image:
                        for suffix in ('B', 'N', 'G', 'M'):
                            if 'CSC_Atlas_Props_' + suffix in node.image.name:
                                path = args.atlas / 'textures' / ('CSC_Props_Shared_01_' + suffix + '.png')
                                assert path.is_file(), path
                                node.image = bpy.data.images.load(str(path), check_existing=True)
                                node.image.colorspace_settings.name = 'sRGB' if suffix == 'B' else 'Non-Color'
        assert signature() == before, 'Geometry, transforms or other UV channels changed'
        target = args.output / source.name
        bpy.ops.wm.save_as_mainfile(filepath=str(target), relative_remap=False)
        bpy.ops.wm.open_mainfile(filepath=str(target), load_ui=False, use_scripts=False)
        assert signature() == before, 'Saved source preservation failed'
        report.append({'source': str(source), 'corrected': str(target), 'preserved_sha256': before,
                       'mesh_count': len(targets), 'region': region['bounds']})
    assert len(report) == 3, report
    (args.output / 'repair-report.json').write_text(json.dumps(report, indent=2))
    if args.install_sources:
        backup = args.output / 'originals'
        backup.mkdir(exist_ok=False)
        for row in report:
            shutil.copy2(row['source'], backup / Path(row['source']).name)
            shutil.copy2(row['corrected'], row['source'])
    print('WORKBENCH_REPAIR_OK', json.dumps(report))


if __name__ == '__main__':
    main()
