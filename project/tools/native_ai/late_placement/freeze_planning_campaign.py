"""Freeze an observational campaign without sweeping unrelated workspace edits in.

The accepted previous full-run gameplay/art package supplies content. Only the
main CSC AI modules and the passive UI fact bridge are overlaid from this tree.
Workshop content stays installed/read-only and is separately pinned by the
controller. This script does not launch a game or install a mod.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil


def freeze(base, source, output):
    base, source, output = (Path(p).resolve() for p in (base, source, output))
    if output.exists() or not all((base / name).is_dir() for name in ('CE', 'CSC')):
        raise ValueError('Require accepted CE/CSC base and a new output directory')
    output.mkdir(parents=True)
    for name in ('CE', 'CSC'):
        shutil.copytree(base / name, output / name)
    overlays = list((source / 'Lua_UI/AI').glob('*.lua'))
    overlays.append(source / 'Lua_UI/Adjacencies/CSC_AdjacencyUI.lua')
    hashes = {}
    for path in overlays:
        relative = path.relative_to(source)
        shutil.copyfile(path, output / 'CSC' / relative)
        hashes[relative.as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    (output / 'freeze.json').write_text(json.dumps(dict(
        base=str(base), source=str(source), overlays=hashes,
        unrelated_workspace_content_included=False), indent=2)+'\n', encoding='utf-8')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('base', 'source', 'output'):
        parser.add_argument('--'+name, type=Path, required=True)
    args = parser.parse_args()
    freeze(args.base, args.source, args.output)
