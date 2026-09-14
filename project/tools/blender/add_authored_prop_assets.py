"""Add verified authored Blender props to a mixed pantry/CSC library.

Copies only declared blends and textures; existing files must be identical.
Keeps native entries and their source records. No game assets are registered here.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def add_assets(library, additions, audit):
    catalogue_path = library / 'catalogue.json'
    original = json.loads(catalogue_path.read_text())
    incoming = json.loads((additions / 'catalogue.json').read_text())['assets']
    existing = {row['asset_id']: row for row in original['assets']}
    files = {}
    for row in incoming:
        if row.get('origin') != 'authored_blender' or row.get('verification', {}).get('status') != 'passed':
            raise ValueError('Only verified authored props may be added: ' + row['asset_id'])
        if row['asset_id'] in existing:
            raise ValueError('Asset identity already catalogued; handle updates explicitly: ' + row['asset_id'])
        for relative in [row['blend_path']] + ['textures/' + name for name in row['textures']]:
            path = Path(relative)
            if path.is_absolute() or '..' in path.parts:
                raise ValueError('Dependency must be library relative: ' + relative)
            source, target = additions / path, library / path
            if not source.is_file():
                raise FileNotFoundError(source)
            if target.exists() and digest(target) != digest(source):
                raise ValueError('Different file already exists: ' + str(target))
            files[relative] = (source, target)
    before = {p.name: digest(p) for p in library.glob('*.blend')}
    for source, target in files.values():
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            shutil.copy2(source, target)
    original['assets'].extend(incoming)
    original.setdefault('authored_contract', {}).update(
        geometry='Authored entries contain local contact pivots, identity source transforms, UV1/UV2/UV3 and a static Bone rig. Building placements retain unapplied transforms.',
        runtime='registration_status records Windows integration; verified_blender does not mean registered or terrain-tested.',
        source_refresh='The pantry converter preserves origin=authored_blender entries. Handle shared-asset updates explicitly.')
    catalogue_path.write_text(json.dumps(original, indent=2) + '\n')
    verification_path = library / 'verification.json'
    verification = json.loads(verification_path.read_text()) if verification_path.exists() else []
    verification.extend(row['verification'] for row in incoming)
    verification_path.write_text(json.dumps(verification, indent=2) + '\n')
    for name, sha in before.items():
        assert digest(library / name) == sha
    assert all(digest(source) == digest(target) for source, target in files.values())
    result = {'added_assets': [r['asset_id'] for r in incoming], 'library_total': len(original['assets']),
              'copied_or_matched_files': len(files), 'existing_blends_unchanged': len(before),
              'all_destination_hashes_match': True, 'runtime_registration_performed': False}
    audit.parent.mkdir(parents=True, exist_ok=True)
    audit.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--library', type=Path, required=True)
    parser.add_argument('--additions', type=Path, required=True)
    parser.add_argument('--audit', type=Path, required=True)
    args = parser.parse_args()
    add_assets(args.library.resolve(), args.additions.resolve(), args.audit.resolve())
