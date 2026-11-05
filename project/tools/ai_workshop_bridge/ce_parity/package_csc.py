"""Build an isolated CSC carrier-test dependency; never deploy or rebuild art.

Copy the installed package's registered assets, give the copy a distinct mod ID,
and overlay only the four reviewed adjacency source files. This avoids testing
against an intermediate installed Core while leaving the human's mod untouched.
The receipt distinguishes copied installed content from the explicit overlays.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import uuid
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[4]
ORIGINAL_ID = 'c5e66bd1-d804-443b-ac3d-1917a20dba3c'
TEST_ID = 'd0f3a2ab-4fa6-4a7a-bf9b-b82a66fe2a08'
OVERLAYS = tuple('Lua_UI/Adjacencies/CSC_Adjacency' + name for name in
                 ('Schema.sql', 'Processor.sql', 'Modifiers.sql', 'Core.lua'))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inventory(root):
    return {p.relative_to(root).as_posix(): digest(p)
            for p in sorted(root.rglob('*')) if p.is_file()}


def build(installed, source, output, *, mod_id=TEST_ID):
    installed, source = installed.resolve(strict=True), source.resolve(strict=True)
    output = output.resolve()
    mod_id = str(uuid.UUID(mod_id))
    if mod_id == ORIGINAL_ID or output.exists() or any(
            output.is_relative_to(p) for p in (installed, source)):
        raise ValueError('A distinct mod ID and fresh output outside both inputs are required')
    manifests = list(installed.glob('*.modinfo'))
    if len(manifests) != 1:
        raise ValueError('Expected exactly one installed CSC manifest')
    tree = ET.parse(manifests[0])
    if tree.getroot().get('id') != ORIGINAL_ID:
        raise ValueError('Unexpected reference CSC identity')
    before = inventory(installed)
    overlays = {name: digest(source / name) for name in OVERLAYS}
    # Validate inputs before copying; any output is a disposable local artifact.
    if any(name not in before for name in OVERLAYS):
        raise ValueError('Installed package lacks an expected registered adjacency file')
    shutil.copytree(installed, output)
    for name in OVERLAYS:
        shutil.copyfile(source / name, output / name)
    tree.getroot().set('id', mod_id)
    tree.getroot().set('version', '1')
    tree.find('Properties/Name').text = 'CSC carrier regression (local test)'
    ET.indent(tree, space='  ')
    tree.write(output / manifests[0].name, encoding='utf-8', xml_declaration=True)
    if inventory(installed) != before:
        raise RuntimeError('Reference CSC changed during the snapshot')
    if any(digest(source / name) != value for name, value in overlays.items()):
        raise RuntimeError('Overlay source changed during the snapshot')
    receipt = dict(mod_id=mod_id, reference=str(installed), reference_files=before,
                   overlay_source=str(source), overlays=overlays,
                   files=inventory(output), reference_unchanged=True,
                   installed=False, native_validated=False)
    (output.parent / (output.name + '-receipt.json')).write_text(
        json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    return receipt


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--installed-csc', type=Path, required=True)
    parser.add_argument('--source', type=Path, default=ROOT / 'Civ Supply Chains')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--mod-id', default=TEST_ID)
    args = parser.parse_args()
    result = build(args.installed_csc, args.source, args.output, mod_id=args.mod_id)
    print(json.dumps(dict(package=str(args.output), mod_id=result['mod_id'],
                          files=len(result['files']), reference_unchanged=True)))
