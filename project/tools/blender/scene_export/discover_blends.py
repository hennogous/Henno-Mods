"""Read export metadata from every requested blend without modifying sources."""
import bpy
import hashlib
import json
from pathlib import Path
import sys


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def export_scene(scenes):
    candidates = []
    for scene in scenes:
        metadata = scene.get('csc_export')
        if metadata:
            metadata = json.loads(metadata) if isinstance(metadata, str) else metadata.to_dict()
            if not isinstance(metadata, dict):
                raise ValueError('csc_export must be a JSON object')
            if metadata.get('kind') != 'ignore':
                candidates.append(scene)
    if not candidates:
        candidates = [scene for scene in scenes if scene.name == 'Export']
    if not candidates and len(scenes) == 1:
        candidates = list(scenes)
    if len(candidates) != 1:
        raise ValueError('Provide one Export scene or one scene with csc_export metadata')
    return candidates[0]


def main():
    request, output = map(Path, sys.argv[sys.argv.index('--') + 1:])
    rows = []
    for value in json.loads(request.read_text())['files']:
        path = Path(value)
        row = {'path': str(path)}
        try:
            before = digest(path)
            bpy.ops.wm.open_mainfile(filepath=str(path), load_ui=False, use_scripts=False)
            scene = export_scene(bpy.data.scenes)
            metadata = scene.get('csc_export', '{}')
            metadata = json.loads(metadata) if isinstance(metadata, str) else metadata.to_dict()
            if not isinstance(metadata, dict):
                raise ValueError('csc_export must be a JSON object')
            row.update(scene=scene.name, metadata=metadata, sha256=before,
                       handoff_role=scene.get('handoff_role', ''),
                       legacy_decal=scene.get('PIL_geometry', ''),
                       armatures=[o.name for o in scene.objects if o.type == 'ARMATURE'],
                       meshes=[{'name': o.name, 'role': o.get('export_role', ''),
                                'asset_id': o.get('source_asset_id', '')}
                               for o in scene.objects if o.type == 'MESH'])
            if digest(path) != before:
                raise ValueError('Source changed during discovery')
        except Exception as error:
            row['error'] = str(error)
        rows.append(row)
    output.write_text(json.dumps(rows, indent=2) + '\n')
    print(f'Inspected {len(rows)} blend files; sources not saved.')


if __name__ == '__main__':
    main()
