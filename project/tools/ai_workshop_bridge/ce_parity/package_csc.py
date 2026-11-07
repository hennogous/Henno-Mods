"""Build an isolated CSC carrier-test dependency; never deploy or rebuild art.

Copy the installed package's registered assets and give the copy a distinct ID.
The default overlays four adjacency files. The Bakers option also registers the
main CSC publisher and its separate CE dependency from explicit inputs.
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
BAKERS_ACTIONS = {'CSC_AI_PlacementModules', 'CSC_AI_BakersGameplay', 'CSC_AdjacencyUIBridge'}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inventory(root):
    return {p.relative_to(root).as_posix(): digest(p)
            for p in sorted(root.rglob('*')) if p.is_file()}


def build(installed, source, output, *, mod_id=TEST_ID, ce_dependency=None, bakers_actions=None):
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
    # Validate inputs before copying; any output is a disposable local artifact.
    if any(name not in before for name in OVERLAYS):
        raise ValueError('Installed package lacks an expected registered adjacency file')
    if (ce_dependency is None) != (bakers_actions is None):
        raise ValueError('Bakers packaging needs both the action source and CE identity')
    extra = set()
    action_digest = None
    if bakers_actions:
        ce_dependency = str(uuid.UUID(ce_dependency))
        if ce_dependency in (mod_id, ORIGINAL_ID):
            raise ValueError('Expected a separate CE dependency')
        action_digest = digest(bakers_actions)
        definitions = json.loads(bakers_actions.read_text(encoding='utf-8-sig'))['blocks']['inGameActions']
        actions = [action for action in definitions if action['id'] in BAKERS_ACTIONS]
        if len(actions) != len(BAKERS_ACTIONS) or {action['id'] for action in actions} != BAKERS_ACTIONS:
            raise ValueError('Expected exactly the canonical Bakers actions')
        root = tree.getroot()
        ingame = root.find('InGameActions')
        files = root.find('Files')
        dependencies = root.find('Dependencies')
        if ingame is None or files is None or dependencies is None:
            raise ValueError('Installed package is missing manifest sections')
        for old in list(ingame):
            if old.get('id') in BAKERS_ACTIONS:
                ingame.remove(old)
        if not any(dep.get('id', '').lower() == ce_dependency for dep in dependencies):
            ET.SubElement(dependencies, 'Mod', id=ce_dependency, title='Community Extension (local test)')
        registered = {node.text for node in files.findall('File')}
        for action in actions:
            node = ET.SubElement(ingame, action['type'], id=action['id'])
            properties = ET.SubElement(node, 'Properties')
            for key, value in action['properties'].items():
                ET.SubElement(properties, key).text = value
            for name in action['files']:
                relative = Path(name)
                if (relative.is_absolute() or relative.drive or '..' in relative.parts
                        or not (source / relative).resolve().is_relative_to(source)):
                    raise ValueError('Bakers action references a file outside CSC')
                ET.SubElement(node, 'File').text = name
                if name not in registered:
                    ET.SubElement(files, 'File').text = name
                    registered.add(name)
                extra.add(name)
    overlays = {name: digest(source / name) for name in sorted(set(OVERLAYS) | extra)}
    shutil.copytree(installed, output)
    for name in overlays:
        target = output / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source / name, target)
    tree.getroot().set('id', mod_id)
    tree.getroot().set('version', '1')
    tree.find('Properties/Name').text = 'CSC carrier regression (local test)'
    ET.indent(tree, space='  ')
    tree.write(output / manifests[0].name, encoding='utf-8', xml_declaration=True)
    if inventory(installed) != before:
        raise RuntimeError('Reference CSC changed during the snapshot')
    if any(digest(source / name) != value for name, value in overlays.items()):
        raise RuntimeError('Overlay source changed during the snapshot')
    if bakers_actions and digest(bakers_actions) != action_digest:
        raise RuntimeError('Bakers action source changed during the snapshot')
    receipt = dict(mod_id=mod_id, reference=str(installed), reference_files=before,
                   overlay_source=str(source), overlays=overlays,
                   files=inventory(output), reference_unchanged=True,
                   installed=False, native_validated=False)
    if bakers_actions:
        receipt.update(ce_dependency=ce_dependency, action_source=str(bakers_actions),
                       action_sha256=action_digest, main_publisher=True)
    (output.parent / (output.name + '-receipt.json')).write_text(
        json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    return receipt


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--installed-csc', type=Path, required=True)
    parser.add_argument('--source', type=Path, default=ROOT / 'Civ Supply Chains')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--mod-id', default=TEST_ID)
    parser.add_argument('--ce-dependency')
    parser.add_argument('--bakers-actions', type=Path)
    args = parser.parse_args()
    result = build(args.installed_csc, args.source, args.output, mod_id=args.mod_id,
                   ce_dependency=args.ce_dependency, bakers_actions=args.bakers_actions)
    print(json.dumps(dict(package=str(args.output), mod_id=result['mod_id'],
                          files=len(result['files']), reference_unchanged=True)))
