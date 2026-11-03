"""Plan a reversible retirement of legacy CSC AI runtime wiring.

Default is read-only JSON planning. --apply snapshots current bytes (including
dirty/untracked files) before moving or changing anything. --restore restores
those bytes only when current files still match the recorded before/after state.
No game, installation, deployment, git reset or recursive deletion is performed.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import importlib.util
import json
import re
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ARCHIVE = 'project/archive/ai-tuning-20261103'
FILTER = 'Civ Supply Chains/Lua_UI/AI/CSC_AI_UIFilter.lua'
AI_ACTIONS = {
    'CSC_AI_UI', 'CSC_AI_ReportScreen', 'CSC_AI_Text', 'CSC_AI_Profile',
    *('CSC_AI_Mode_Basic_'+s for s in ('DB', 'Research', 'Imports', 'Assistance', 'UI')),
    *('CSC_AI_Mode_RH_0_'+s for s in ('DB', 'Research', 'Imports', 'Assistance', 'UI', 'CustomerRoles')),
}
AI_CRITERIA = {'CSC_AI_Enabled', 'CSC_AI_RH_0', 'CSC_AI_RH_No_0'}
METADATA = ('project/modbuddy/CivSupplyChains.actions.json',
            'Civ Supply Chains/Civ Supply Chains.civ6proj',
            'Civ Supply Chains/Settings/Settings.xml', 'Civ Supply Chains/Settings/Settings_Text.xml')
SOURCE_EXTENSIONS = {'.py', '.lua', '.js', '.sql', '.json', '.md', '.xml', '.txt', '.ps1', '.java', '.bat', '.html'}
SKIP_PARTS = {'__pycache__', '.git', 'node_modules', '.venv', 'venv', '.pytest_cache', '.cache'}
MAX_FILE = 2 * 1024 * 1024
MAX_TOTAL = 100 * 1024 * 1024


def digest(data): return hashlib.sha256(data).hexdigest()


def checked(root, relative):
    """Resolve every source/destination under the explicitly intended workspace."""
    root = root.resolve()
    path = root / relative
    resolved = path.resolve()
    if not resolved.is_relative_to(root) or resolved == root:
        raise ValueError('Path escapes intended workspace: '+str(path))
    # Do not archive through a junction/symlink as if it were ordinary source.
    for parent in (path, *path.parents):
        if parent == root: break
        if parent.is_symlink() or (hasattr(parent, 'is_junction') and parent.is_junction()):
            raise ValueError('Linked source/destination requires explicit review: '+str(parent))
    return resolved


def load_actions_tool(root):
    path = checked(root, 'project/tools/modbuddy/civ6proj_actions.py')
    spec = importlib.util.spec_from_file_location('csc_archive_actions', path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


def runtime_files(root):
    mod = checked(root, 'Civ Supply Chains')
    paths = list((mod/'Data').glob('CSC_AI*.sql'))
    paths += list((mod/'ModSupport').glob('ModSupport_RH_AI*'))
    paths += [p for p in (mod/'Lua_UI/AI').iterdir() if p.is_file()]
    paths += [mod/'Text/CSC_AI_TEXT.sql', checked(root, 'project/localization/CSC_AI_TEXT.md')]
    if not paths or not all(p.is_file() for p in paths): raise ValueError('Incomplete legacy source family')
    return sorted({str(checked(root, p.relative_to(root)).relative_to(root)).replace('\\', '/') for p in paths})


def settings_without_ai(text):
    ET.fromstring(text)
    removed = []
    def row(match):
        node = ET.fromstring(match.group(0).strip())
        if node.attrib.get('ParameterId') in {'CSC_AI_Assistance', 'CSC_AI_Subsidies'}:
            removed.append(node.attrib); return ''
        return match.group(0)
    updated = re.sub(r'(?m)^[ \t]*<Row\b[^>]*?/\s*>[ \t]*(?:\r?\n|$)', row, text)
    if len(removed) != 3: raise ValueError('Expected exactly2AI settings and1dependency')
    ET.fromstring(updated)
    if any('CSC_AI_' in value for node in ET.fromstring(updated).iter() for value in node.attrib.values()):
        raise ValueError('Unexpected remaining AI setting/criteria')
    return updated


def settings_text_without_ai(text):
    tags = {'LOC_CSC_AI_ASSISTANCE_NAME', 'LOC_CSC_AI_ASSISTANCE_DESCRIPTION',
            'LOC_CSC_AI_SUBSIDIES_NAME', 'LOC_CSC_AI_SUBSIDIES_DESCRIPTION'}
    ET.fromstring(text); removed = []
    def block(match):
        node = ET.fromstring(match.group(0).strip())
        if node.attrib.get('Tag') in tags:
            removed.append(node.attrib['Tag']); return ''
        return match.group(0)
    updated = re.sub(r'(?ms)^[ \t]*<Replace\b[^>]*>.*?</Replace>[ \t]*(?:\r?\n|$)', block, text)
    if set(removed) != tags or len(removed) != 4: raise ValueError('Expected exactly4AI option labels')
    ET.fromstring(updated); return updated


def metadata_outputs(root, retired):
    originals = {p: checked(root, p).read_bytes() for p in METADATA}
    data = json.loads(originals[METADATA[0]].decode('utf-8-sig'))
    data = copy.deepcopy(data); blocks = data['blocks']
    found = {a['id'] for a in blocks['inGameActions'] if a['id'].startswith('CSC_AI_')}
    if found != AI_ACTIONS: raise ValueError('Legacy AI action set changed; review plan explicitly')
    blocks['inGameActions'] = [a for a in blocks['inGameActions'] if a['id'] not in AI_ACTIONS]
    if any(a['id'] == 'CSC_YieldFilter_Compatibility' for a in blocks['inGameActions']):
        raise ValueError('Compatibility import already exists')
    blocks['inGameActions'].insert(0, dict(type='ImportFiles', id='CSC_YieldFilter_Compatibility',
                                        properties=dict(LoadOrder='480'), files=['Lua_UI/AI/CSC_AI_UIFilter.lua']))
    criteria_found = {c['attributes']['id'] for c in blocks['actionCriteria'] if c['attributes']['id'] in AI_CRITERIA}
    if criteria_found != AI_CRITERIA: raise ValueError('Expected3legacy AI criteria')
    blocks['actionCriteria'] = [c for c in blocks['actionCriteria'] if c['attributes']['id'] not in AI_CRITERIA]
    for a in blocks['inGameActions'] + blocks['frontEndActions']:
        if set(a.get('criteria', [])) & AI_CRITERIA: raise ValueError('Kept action depends on retired AI criteria')
    project = originals[METADATA[1]].decode('utf-8-sig')
    moved_content = {p.removeprefix('Civ Supply Chains/') for p in retired if p.startswith('Civ Supply Chains/')}
    removed_content = []
    def content(match):
        node = ET.fromstring(match.group(0).strip())
        path = node.attrib['Include'].replace('\\', '/')
        if path in moved_content:
            removed_content.append(path); return ''
        return match.group(0)
    project = re.sub(r'(?ms)^[ \t]*<Content\b[^>]*?(?:/\s*>|>.*?</Content>)[ \t]*(?:\r?\n|$)', content, project)
    # Use the maintained JSON -> CDATA generator, not hand-authored action XML.
    actions_tool = load_actions_tool(root)
    project = actions_tool.patch_project_text(project, data)
    ET.fromstring(project)
    roundtrip = {'schemaVersion': 1, 'blocks': {}}
    for key, meta in actions_tool.BLOCKS.items():
        fragment = actions_tool.parse_xml_fragment(actions_tool.extract_block(project, meta['property']), meta['root'])
        roundtrip['blocks'][key] = (actions_tool.criteria_to_json(fragment) if key == 'actionCriteria'
                                    else actions_tool.actions_to_json(fragment))
    if actions_tool.canonical_data(roundtrip) != actions_tool.canonical_data(data):
        raise ValueError('Generated actions did not round-trip')
    output = {METADATA[0]: (json.dumps(data, indent=2)+'\n').encode('utf-8'), METADATA[1]: project.encode('utf-8'),
              METADATA[2]: settings_without_ai(originals[METADATA[2]].decode('utf-8-sig')).encode('utf-8'),
              METADATA[3]: settings_text_without_ai(originals[METADATA[3]].decode('utf-8-sig')).encode('utf-8')}
    return originals, output, sorted(removed_content)


def operational_sources(root):
    included, skipped = [], []
    for folder in ('project/tools/ai_baseline', 'project/tools/ai_tuning'):
        for p in checked(root, folder).rglob('*'):
            if not p.is_file() or any(part in SKIP_PARTS for part in p.parts): continue
            if p.suffix.lower() not in SOURCE_EXTENSIONS: continue
            relative = str(p.relative_to(root)).replace('\\', '/')
            checked(root, relative)
            if p.stat().st_size > MAX_FILE: skipped.append(relative)
            else: included.append(relative)
    return sorted(included), sorted(skipped)


def build_plan(root=ROOT):
    root = root.resolve(); archive = checked(root, ARCHIVE)
    if archive.exists(): raise ValueError('Archive destination already exists; no overwrite/replay')
    runtime = runtime_files(root)
    if FILTER not in runtime: raise ValueError('Shared yield filter is missing')
    retired = [p for p in runtime if p != FILTER]
    originals, outputs, removed_content = metadata_outputs(root, retired)
    tools, skipped = operational_sources(root)
    provenance = {'project/tools/native_ai/archive_legacy_tuning.py', 'project/tools/modbuddy/civ6proj_actions.py'}
    paths = sorted(set(runtime) | set(METADATA) | set(tools) | provenance)
    records = []
    for path in paths:
        raw = checked(root, path).read_bytes()
        operation = 'modify' if path in outputs else 'move' if path in retired else 'retain' if path == FILTER else 'copy-only'
        records.append(dict(path=path, operation=operation, bytes=len(raw), before_sha256=digest(raw),
                            after_sha256=digest(outputs[path]) if path in outputs else None if operation == 'move' else digest(raw)))
    if sum(r['bytes'] for r in records) > MAX_TOTAL: raise ValueError('Source snapshot exceeds100MiB review bound')
    status = subprocess.run(['git', '-C', str(root), 'status', '--porcelain=v1', '--untracked-files=all', '--',
                             'Civ Supply Chains/Data/CSC_AI*', 'Civ Supply Chains/Lua_UI/AI/',
                             'Civ Supply Chains/ModSupport/ModSupport_RH_AI*', *METADATA],
                            capture_output=True, text=True, check=True).stdout
    plan = dict(schema=1, workspace=str(root), archive=ARCHIVE, stage='planned-current-byte-snapshot',
                runtime_inputs=len(runtime), moved_runtime_and_localization=len(retired), metadata_files=len(outputs),
                removed_actions=sorted(AI_ACTIONS), removed_criteria=sorted(AI_CRITERIA),
                compatibility_import='CSC_YieldFilter_Compatibility', removed_content=removed_content,
                operational_tools_copy_only=len(tools), skipped_oversized_code_files=skipped,
                dirty_untracked_status=status, records=records,
                preserve=['actual Quarter gameplay and ordinary ModSupport', 'bundled adjacency engine',
                          'independent resource-map assistance', 'shared controller and new native bridge',
                          'research/evidence/knowledge base', 'old tools stay at original paths for historical imports'],
                effects='future loaded rules/runtime wiring only; does not undo saved map/treasury/research/cache history')
    return plan, outputs


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2)+'\n', encoding='utf-8')


def replace_bytes(root, relative, data):
    path = checked(root, relative); path.parent.mkdir(parents=True, exist_ok=True)
    temporary = checked(root, relative+'.archive-prep.tmp')
    if temporary.exists(): raise ValueError('Unreconciled temporary file: '+str(temporary))
    temporary.write_bytes(data)
    if digest(temporary.read_bytes()) != digest(data): raise IOError('Temporary byte verification failed')
    temporary.replace(path)


def apply(root=ROOT):
    root = root.resolve(); plan, outputs = build_plan(root); archive = checked(root, ARCHIVE)
    # Prove the complete declared before-state before creating any snapshot.
    for record in plan['records']:
        if digest(checked(root, record['path']).read_bytes()) != record['before_sha256']:
            raise RuntimeError('Source changed during planning: '+record['path'])
    archive.mkdir(parents=True, exist_ok=False)
    write_json(archive/'manifest.json', plan)
    for record in plan['records']:
        original = checked(root, record['path'])
        backup = checked(root, ARCHIVE+'/before/'+record['path']); backup.parent.mkdir(parents=True, exist_ok=True)
        raw = original.read_bytes()
        if digest(raw) != record['before_sha256']: raise RuntimeError('Source changed before backup: '+record['path'])
        backup.write_bytes(raw)
        if digest(backup.read_bytes()) != record['before_sha256']: raise IOError('Backup verification failed')
    # No source moves/edits occur until every declared current-byte backup passes.
    for record in plan['records']:
        if digest(checked(root, record['path']).read_bytes()) != record['before_sha256']:
            raise RuntimeError('Source changed after backup; no further changes: '+record['path'])
    plan['stage'] = 'snapshots-verified'; write_json(archive/'manifest.json', plan)
    for record in plan['records']:
        path = record['path']; original = checked(root, path)
        if record['operation'] in ('move', 'modify') and sha_file(original) != record['before_sha256']:
            raise RuntimeError('Source changed immediately before mutation: '+path)
        if record['operation'] == 'move':
            target = checked(root, ARCHIVE+'/retired/'+path); target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists(): raise ValueError('Retired target already exists')
            original.replace(target)
        elif record['operation'] == 'modify': replace_bytes(root, path, outputs[path])
    for record in plan['records']:
        original = checked(root, record['path'])
        if record['operation'] == 'move':
            if original.exists() or sha_file(checked(root, ARCHIVE+'/retired/'+record['path'])) != record['before_sha256']:
                raise RuntimeError('Move verification failed')
        elif sha_file(original) != record['after_sha256']: raise RuntimeError('After-state verification failed')
    plan['stage'] = 'applied'; write_json(archive/'manifest.json', plan)
    return plan


def sha_file(path): return digest(path.read_bytes())


def restore(root=ROOT):
    root = root.resolve(); archive = checked(root, ARCHIVE); plan = json.loads((archive/'manifest.json').read_text())
    if plan['workspace'] != str(root) or plan['archive'] != ARCHIVE: raise ValueError('Archive workspace mismatch')
    changes = [r for r in plan['records'] if r['operation'] in ('move', 'modify')]
    # Refuse to overwrite any post-archive user edit. Partial application is safe
    # to restore when each file remains in its recorded before/after state.
    for record in changes:
        backup = checked(root, ARCHIVE+'/before/'+record['path'])
        if sha_file(backup) != record['before_sha256']: raise ValueError('Backup hash mismatch')
        original = checked(root, record['path'])
        if original.exists() and sha_file(original) not in {record['before_sha256'], record['after_sha256']}:
            raise RuntimeError('Current user edit must be preserved: '+record['path'])
        if not original.exists() and record['operation'] != 'move': raise RuntimeError('Modified source unexpectedly absent')
    for record in changes:
        replace_bytes(root, record['path'], checked(root, ARCHIVE+'/before/'+record['path']).read_bytes())
    for record in changes:
        if sha_file(checked(root, record['path'])) != record['before_sha256']: raise RuntimeError('Restore verification failed')
    write_json(archive/'restored.json', dict(verified=True, files=len(changes), snapshots_retained=True, no_git_HEAD_used=True))
    return dict(restored=True, files=len(changes), archive=ARCHIVE)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--apply', action='store_true')
    group.add_argument('--restore', action='store_true')
    args = parser.parse_args()
    value = apply() if args.apply else restore() if args.restore else build_plan()[0]
    print(json.dumps(value, indent=2))


if __name__ == '__main__': main()
