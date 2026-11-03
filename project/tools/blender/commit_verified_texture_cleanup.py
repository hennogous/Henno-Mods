"""Install checked copies transactionally; retain receipts, not full-size backups."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import time


def sha(path):
    result = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            result.update(block)
    return result.hexdigest()


def safe_file(path, root):
    absolute = path.absolute()
    resolved = path.resolve(strict=True)
    if root not in resolved.parents or absolute != resolved:
        raise ValueError('File outside the named root, or reached through a link: ' + str(path))
    for parent in [path] + list(path.parents):
        if parent == root:
            break
        if parent.is_symlink() or (hasattr(parent, 'is_junction') and parent.is_junction()):
            raise ValueError('Linked path: ' + str(parent))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--source-root', type=Path, required=True)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    output = args.output.resolve(strict=True)
    root = args.source_root.resolve(strict=True)
    rows = json.loads((output / 'staged-old.json').read_text(encoding='utf-8'))
    rows += json.loads((output / 'staged-new.json').read_text(encoding='utf-8'))
    if len({row['source'] for row in rows}) != len(rows):
        raise ValueError('Duplicate source files')
    for row in rows:
        source, staged = Path(row['source']), Path(row['staged'])
        safe_file(source, root)
        safe_file(staged, output)
        if not row['preservation_verified'] or sha(source) != row['source_sha256'] or sha(staged) != row['clean_sha256']:
            raise ValueError('A source or staged file changed: ' + str(source))
        if row['clean_bytes'] >= row['original_bytes']:
            raise ValueError('Cleaned file does not save storage: ' + str(source))
    missing = set()
    for suffix in ['old', 'new']:
        missing.update(json.loads((output / ('missing-' + suffix + '.json')).read_text(encoding='utf-8')))
    result = {'files': len(rows), 'removed_images': sum(len(row['removed_images']) for row in rows),
              'saved_bytes': sum(row['original_bytes'] - row['clean_bytes'] for row in rows),
              'already_missing': sorted(missing), 'applied': False, 'entries': rows}
    if not args.apply:
        print(json.dumps({key: value for key, value in result.items() if key != 'entries'}, indent=2))
        return
    recovery = output / 'temporary-recovery'
    recovery.mkdir(exist_ok=False)
    installed = []
    checkpoint = output / 'cleanup-receipt.json'
    try:
        for index, row in enumerate(rows):
            source, staged = Path(row['source']), Path(row['staged'])
            if sha(source) != row['source_sha256']:
                raise ValueError('Source changed immediately before replacement: ' + str(source))
            backup = recovery / (str(index).zfill(3) + '.blend')
            shutil.copy2(source, backup)
            if sha(backup) != row['source_sha256']:
                raise ValueError('Recovery copy failed verification')
            os.replace(staged, source)
            installed.append((row, backup))
            if sha(source) != row['clean_sha256']:
                raise ValueError('Installed file failed byte-for-byte verification')
            result['installed_so_far'] = len(installed)
            checkpoint.write_text(json.dumps(result, indent=2), encoding='utf-8')
        for row, backup in installed:
            if sha(Path(row['source'])) != row['clean_sha256']:
                raise ValueError('Installed source changed during final verification')
    except Exception:
        for row, backup in reversed(installed):
            if sha(Path(row['source'])) != row['clean_sha256']:
                raise RuntimeError('Concurrent source change; preserving recovery copies at ' + str(recovery))
            os.replace(backup, row['source'])
        result['rolled_back'] = True
        checkpoint.write_text(json.dumps(result, indent=2), encoding='utf-8')
        raise
    result['applied'] = True
    result['verified_at'] = time.time()
    checkpoint.write_text(json.dumps(result, indent=2), encoding='utf-8')
    # All originals are now replaced by individually reopened, checked and hashed
    # cleaned files. Delete only the explicitly verified temporary recovery files.
    for row, backup in installed:
        safe_file(backup, output)
        if sha(backup) != row['source_sha256']:
            raise ValueError('Recovery copy changed; preserving it')
        backup.unlink()
    if any(recovery.iterdir()):
        raise ValueError('Unexpected recovery files; preserving them')
    recovery.rmdir()
    result['temporary_originals_removed'] = True
    checkpoint.write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps({key: value for key, value in result.items() if key != 'entries'}, indent=2))


if __name__ == '__main__':
    main()
