"""Plan/apply a permanent, reversible AI metadata reset of the user's own CSC.

Default prints a read-only plan. --apply changes only installed modinfo and
Settings XML; all gameplay, art, legacy file bytes and Files entries remain.
This is not a transient experiment deployment or a rollback of saved history.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT/'project/tools/ai_baseline'), str(Path(__file__).resolve().parent)]
from full_game_controller.windows_process import native_inventory
from archive_legacy_tuning import AI_ACTIONS, AI_CRITERIA, settings_without_ai, settings_text_without_ai

MOD_ID = 'c5e66bd1-d804-443b-ac3d-1917a20dba3c'
MODINFO = 'Civ Supply Chains.modinfo'
FILTER = 'Lua_UI/AI/CSC_AI_UIFilter.lua'


def digest(data): return hashlib.sha256(data).hexdigest()


def safe(base, relative):
    base = Path(base).resolve(); path = base/relative; result = path.resolve()
    if result == base or not result.is_relative_to(base): raise ValueError('Path escapes declared directory: '+str(path))
    for parent in (path, *path.parents):
        if parent == base: break
        if parent.is_symlink() or (hasattr(parent, 'is_junction') and parent.is_junction()):
            raise ValueError('Linked metadata/art paths need separate review: '+str(parent))
    return result


def full_manifest(base):
    base = Path(base).resolve()
    return {str(p.relative_to(base)).replace('\\', '/'): dict(sha256=digest(safe(base, p.relative_to(base)).read_bytes()), bytes=p.stat().st_size)
            for p in sorted(base.rglob('*')) if p.is_file()}


def semantic(node):
    return (node.tag, tuple(sorted(node.attrib.items())), (node.text or '').strip(), tuple(semantic(c) for c in node))


def remove_named_children(text, section, ids):
    boundary = re.search(r'(?s)(<'+section+r'\b[^>]*>)(.*?)(</'+section+r'>)', text)
    if boundary is None: raise ValueError('Missing installed section: '+section)
    removed = []
    def child(match):
        node = ET.fromstring(match.group(0).strip())
        if node.attrib.get('id') in ids:
            removed.append(node.attrib['id']); return ''
        return match.group(0)
    body = re.sub(r'(?ms)^[ \t]*<(?P<tag>\w+)\b[^>]*?(?:/\s*>|>.*?</(?P=tag)>)[ \t]*(?:\r?\n|$)', child, boundary.group(2))
    if set(removed) != ids or len(removed) != len(ids): raise ValueError('Unexpected installed action/criterion set')
    if section == 'InGameActions':
        newline = '\r\n' if '\r\n' in text else '\n'
        compatibility = ('    <ImportFiles id="CSC_YieldFilter_Compatibility">'+newline+
            '      <Properties><LoadOrder>480</LoadOrder></Properties>'+newline+
            '      <File>'+FILTER+'</File>'+newline+'    </ImportFiles>'+newline)
        body = newline+compatibility+body.lstrip('\r\n')
    return text[:boundary.start(2)] + body + text[boundary.end(2):]


def transform_modinfo(raw):
    before = ET.fromstring(raw)
    if before.tag != 'Mod' or before.attrib.get('id', '').lower() != MOD_ID:
        raise ValueError('Only the explicitly identified own CSC mod is supported')
    actions, criteria = before.find('InGameActions'), before.find('ActionCriteria')
    if actions is None or criteria is None: raise ValueError('Installed action sections absent')
    if {a.attrib.get('id') for a in actions if a.attrib.get('id', '').startswith('CSC_AI_')} != AI_ACTIONS:
        raise ValueError('Require exactly the reviewed15legacy AI actions')
    if {c.attrib.get('id') for c in criteria if c.attrib.get('id', '').startswith('CSC_AI_')} != AI_CRITERIA:
        raise ValueError('Require exactly the reviewed3legacy AI criteria')
    if any(a.attrib.get('id') == 'CSC_YieldFilter_Compatibility' for a in actions):
        raise ValueError('Installed reset already present; no replay')
    text = remove_named_children(raw.decode('utf-8-sig'), 'InGameActions', AI_ACTIONS)
    text = remove_named_children(text, 'ActionCriteria', AI_CRITERIA)
    after = ET.fromstring(text)
    expected = copy.deepcopy(before)
    for node in list(expected.find('InGameActions')):
        if node.attrib.get('id') in AI_ACTIONS: expected.find('InGameActions').remove(node)
    for node in list(expected.find('ActionCriteria')):
        if node.attrib.get('id') in AI_CRITERIA: expected.find('ActionCriteria').remove(node)
    compat = ET.fromstring('<ImportFiles id="CSC_YieldFilter_Compatibility"><Properties><LoadOrder>480</LoadOrder></Properties><File>'+FILTER+'</File></ImportFiles>')
    expected.find('InGameActions').insert(0, compat)
    if semantic(after) != semantic(expected): raise ValueError('Non-AI mod identity/actions/props/Files changed')
    for section in ('FrontEndActions', 'InGameActions'):
        for action in after.find(section):
            if any((c.text or '') in AI_CRITERIA for c in action.findall('Criteria')):
                raise ValueError('Kept action still depends on a retired criterion')
    return text.encode('utf-8')


def output_path(installed, output):
    output = Path(output).resolve(); installed = Path(installed).resolve()
    permitted = (Path.home()/'Desktop/Codex', ROOT/'project/archive', Path.home()/'.codex/visualizations')
    if not any(output.is_relative_to(p.resolve()) for p in permitted): raise ValueError('Use designated Codex output or project archive/staging directory')
    if output == installed or output.is_relative_to(installed) or installed.is_relative_to(output):
        raise ValueError('Backup output must be separate from the installed package')
    return output


def build_plan(installed, output):
    installed = Path(installed).resolve(); output = output_path(installed, output)
    if not installed.is_dir() or installed.name != 'Civ Supply Chains': raise ValueError('Explicit own CSC directory required')
    if not safe(installed, FILTER).is_file(): raise ValueError('Kept shared yield filter is absent')
    before = full_manifest(installed)
    originals = {MODINFO: safe(installed, MODINFO).read_bytes(), 'Settings/Settings.xml': safe(installed, 'Settings/Settings.xml').read_bytes()}
    proposed = {MODINFO: transform_modinfo(originals[MODINFO]),
                'Settings/Settings.xml': settings_without_ai(originals['Settings/Settings.xml'].decode('utf-8-sig')).encode('utf-8')}
    optional = 'Settings/Settings_Text.xml'
    if safe(installed, optional).is_file():
        originals[optional] = safe(installed, optional).read_bytes()
        proposed[optional] = settings_text_without_ai(originals[optional].decode('utf-8-sig')).encode('utf-8')
    records = [dict(path=p, before_sha256=digest(originals[p]), after_sha256=digest(proposed[p]),
                    before_bytes=len(originals[p]), after_bytes=len(proposed[p])) for p in proposed]
    expected = copy.deepcopy(before)
    for record in records: expected[record['path']] = dict(sha256=record['after_sha256'], bytes=record['after_bytes'])
    plan = dict(schema=1, operation='permanent-user-requested-CSC-AI-reset', installed=str(installed), output=str(output), mod_id=MOD_ID,
                stage='planned', changed_files=records, before_manifest=before, expected_after_manifest=expected,
                removed_actions=sorted(AI_ACTIONS), removed_criteria=sorted(AI_CRITERIA),
                retained_import='CSC_YieldFilter_Compatibility', files_removed=0, modinfo_Files_list_preserved=True,
                non_AI_actions_properties_resources_deep_equivalent=True, source_package_copied=False,
                saved_history_rollback_claimed=False, native_inventory_required_at_apply=True)
    return plan, originals, proposed


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2)+'\n', encoding='utf-8')


def atomic_replace(base, relative, data):
    path = safe(base, relative); temporary = safe(base, relative+'.clean-ai.tmp')
    if temporary.exists(): raise ValueError('Unreconciled metadata temporary file')
    temporary.write_bytes(data)
    if digest(temporary.read_bytes()) != digest(data): raise IOError('Temporary metadata verification failed')
    temporary.replace(path)


def no_owners(inventory):
    if inventory(): raise RuntimeError('Native/Tuner/research owner present; no installed changes')


def apply(installed, output, *, inventory=native_inventory):
    no_owners(inventory)
    plan, originals, proposed = build_plan(installed, output)
    installed, output = Path(plan['installed']), Path(plan['output'])
    if output.exists(): raise ValueError('Use a fresh output directory; no reset replay')
    output.mkdir(parents=True, exist_ok=False); write_json(output/'plan.json', plan)
    for path, raw in originals.items():
        backup = safe(output, 'before/'+path); backup.parent.mkdir(parents=True, exist_ok=True); backup.write_bytes(raw)
        if digest(backup.read_bytes()) != digest(raw): raise IOError('Installed backup verification failed')
    if full_manifest(installed) != plan['before_manifest']: raise RuntimeError('Installed package changed before reset')
    no_owners(inventory); plan['stage'] = 'backups-verified'; write_json(output/'plan.json', plan)
    for record in plan['changed_files']:
        no_owners(inventory)
        if digest(safe(installed, record['path']).read_bytes()) != record['before_sha256']:
            raise RuntimeError('Installed metadata changed; preserve the new edit')
        atomic_replace(installed, record['path'], proposed[record['path']])
    actual = full_manifest(installed)
    if actual != plan['expected_after_manifest']: raise RuntimeError('Unexpected non-AI/package byte change')
    no_owners(inventory)
    plan['stage'] = 'applied'; plan['after_manifest'] = actual; write_json(output/'plan.json', plan)
    write_json(output/'result.json', dict(verified=True, permanent_reset=True, files_changed=len(proposed), files_removed=0,
               installed=str(installed), backup=str(output), all_other_bytes_preserved=True, native_owners_absent=True))
    return plan


def restore(installed, output, *, inventory=native_inventory):
    no_owners(inventory)
    installed = Path(installed).resolve(); output = output_path(installed, output)
    plan = json.loads((output/'plan.json').read_text(encoding='utf-8-sig'))
    if plan['installed'] != str(installed) or plan['output'] != str(output) or plan['mod_id'] != MOD_ID:
        raise ValueError('Restore owner/path mismatch')
    if ET.fromstring(safe(installed, MODINFO).read_bytes()).attrib.get('id', '').lower() != MOD_ID:
        raise ValueError('Installed mod identity changed')
    before_restore = full_manifest(installed); expected = copy.deepcopy(before_restore); backups = {}
    for record in plan['changed_files']:
        path = record['path']; raw = safe(output, 'before/'+path).read_bytes()
        if digest(raw) != record['before_sha256']: raise ValueError('Installed backup hash mismatch')
        current = digest(safe(installed, path).read_bytes())
        if current not in (record['before_sha256'], record['after_sha256']):
            raise RuntimeError('Unknown later metadata edit; refusing overwrite: '+path)
        backups[path] = raw; expected[path] = dict(sha256=digest(raw), bytes=len(raw))
    for path, raw in backups.items():
        no_owners(inventory)
        if digest(safe(installed, path).read_bytes()) != before_restore[path]['sha256']:
            raise RuntimeError('Metadata changed during restore; preserve edit')
        atomic_replace(installed, path, raw)
    if full_manifest(installed) != expected: raise RuntimeError('Restore changed unrelated installed bytes')
    no_owners(inventory)
    write_json(output/'restored.json', dict(verified=True, files=len(backups), all_other_current_bytes_preserved=True, backups_retained=True))
    return dict(restored=True, files=len(backups), installed=str(installed), output=str(output))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--installed', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    group = parser.add_mutually_exclusive_group(); group.add_argument('--apply', action='store_true'); group.add_argument('--restore', action='store_true')
    args = parser.parse_args()
    value = apply(args.installed, args.output) if args.apply else restore(args.installed, args.output) if args.restore else build_plan(args.installed, args.output)[0]
    print(json.dumps(value, indent=2))


if __name__ == '__main__': main()
