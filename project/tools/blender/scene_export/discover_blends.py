"""Read export metadata from every requested blend without modifying sources."""
import bpy
import hashlib
import json
from pathlib import Path
import sys


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    request, output = map(Path, sys.argv[sys.argv.index('--') + 1:])
    rows = []
    for value in json.loads(request.read_text())['files']:
        path = Path(value)
        row = {'path': str(path)}
        try:
            before = digest(path)
            bpy.ops.wm.open_mainfile(filepath=str(path), load_ui=False, use_scripts=False)
            scenes = [s for s in bpy.data.scenes if s.get('csc_export')]
            if not scenes:
                scenes = [bpy.data.scenes['Export']] if 'Export' in bpy.data.scenes else []
            if not scenes and len(bpy.data.scenes) == 1:
                scenes = list(bpy.data.scenes)
            if len(scenes) != 1:
                raise ValueError('Provide one Export scene or one scene with csc_export metadata')
            scene = scenes[0]
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
