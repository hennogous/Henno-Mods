"""One exact existing-save interval for an explicit experimental score bridge.

No new world, orders, prerequisite grants, queue clearing or save writes.
Treatment may change one declared native score; disabling is not rollback.
Importing this module performs no game or instrumentation operations.
"""
import argparse
import hashlib
import json
import re
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT/'project/tools/ai_baseline'), str(ROOT/'project/tools/ai_tuning'), str(HERE.parent)]
from full_game_controller.probe import make_probe_controller, write_json
from full_game_controller.session import NativeSession
from full_game_controller.windows_process import HeldProcess, native_inventory
from full_game_controller.log_capture import capture_log_baseline, read_log_delta
from native_session_probe import launch
from native_profile_test import configure, manifest, restore_preferences
from native_probe_artifacts import archive_sources
from observer_host import prove_loaded_module

EXPECTED = '324c51e9ea3531758842e16c69e6cddbefbb226c5b675c3d6e60111646c2e98c'
SAVE_SHA = 'ea818368130273e02e70e31449a6f24a54e34486b8bfa402dd34b62255443e48'
DISTRICT = 'DISTRICT_CSC_BAKERS_QUARTER'
FUNCTIONS = {
    'DistrictNetValue': (0x52a440, '8954241055535657415441554156488d6c24f14881eca0000000448b756f33c0'),
    'CalculateDistrictValues': (0x3dfee0, '4c8bdc41554881eca000000083b9d8040000004c8be90f84ae030000488b91c8'),
    'GetBestDistrict': (0x3e4a50, '48894c24085355564154415541574883ec284c8bea488be9e873be3e00488bb5'),
    'PresentValueOf': (0x3e7f40, '4d63d84c8bd2488bc14183fbff750833c9488bc2890ac34d85c9744d8b81d804'),
}


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path): return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def parse(raw):
    values = re.findall(r'CSC_DISTRICT_EXTENSION_WORLD=([^\r\n]+)', raw)
    if len(values) != 1: raise ValueError('Missing/ambiguous fixture observation')
    return json.loads(values[0])


def validate_source(v):
    if (v['turn'], v['width'], v['height']) != (250, 74, 46) or v['player0'] != dict(human=True, alive=True):
        raise ValueError('Wrong source phase/map/original human identity')
    m, t, p = v['mapping'], v['target'], v['plot']
    if (m['districtType'] != DISTRICT or type(m['districtCount']) is not int
            or not 0 < m['districtCount'] == m['districtIndexLimit'] <= 4096
            or type(m['districtIndex']) is not int or not 0 <= m['districtIndex'] < m['districtIndexLimit']):
        raise ValueError('Invalid loaded district catalog bounds')
    catalog = v['districtCatalog']
    if (len(catalog) != m['districtCount'] or {r['index'] for r in catalog} != set(range(m['districtCount']))
            or [r['type'] for r in catalog if r['index'] == m['districtIndex']] != [DISTRICT]):
        raise ValueError('Unverified native district index mapping')
    if not (t['exists'] is True and t['alive'] is True and t['major'] is True and t['human'] is False
            and (t['player'], t['city'], t['x'], t['y']) == (4, 655369, 42, 42)):
        raise ValueError('Declared original AI city absent or changed')
    if any(d['type'] == DISTRICT for d in t['districts']): raise ValueError('Target Quarter already present')
    if ((p['index'], p['x'], p['y'], p['owner']) != (3076, 42, 41, 4)
            or any(p[k] != -1 for k in ('district', 'feature', 'resource', 'improvement'))
            or p['water'] is not False or p['impassable'] is not False or p['pillaged'] is not False or p['revealed'] is not True):
        raise ValueError('Target clear owned plot changed; no fixture repair')
    if p.get('purchaseCity', dict(player=4, city=655369)) != dict(player=4, city=655369):
        raise ValueError('Plot is assigned to another city')
    if p.get('legal') is False: raise ValueError('Read-only plot legality rejected target')
    if v['assistance']['mode'] != 'OFF' or v['assistance'].get('pending'):
        raise ValueError('Require assistance OFF and no pending work; no callback removal')
    return True


def economic_signature(v):
    return {k: v['assistance'].get(k) for k in ('mode', 'TOTALS', 'ERROR_INDEX', 'PURCHASE_INDEX', 'FOUNDATION_INDEX', 'pending', 'turnCycles')}


def validate_spec(spec):
    rows = spec.get('functions', [])
    if (len(rows) != 4 or {r['name']: (r['rva'], r['bytes']) for r in rows} != FUNCTIONS
            or spec.get('sha256') != EXPECTED or spec.get('timestamp') != 1719431003
            or spec.get('image_size') != 12976128):
        raise ValueError('Unreviewed mutating profile/build/fingerprints')


def make_config(initial, mode):
    m = initial['mapping']
    return dict(profile='district-score-extension-v1', mode=mode, deltaQ8=256,
                player=4, city=655369, districtType=DISTRICT, districtIndex=m['districtIndex'],
                districtCount=m['districtCount'], districtIndexLimit=m['districtIndexLimit'],
                plot=3076, plotX=42, plotY=41, mapWidth=74, mapHeight=46,
                maxChanges=1, maxRecords=128, session=7, epoch=1, version=1,
                originalHuman=False, currentHuman=False, mappingVerified=True)


def validate_snapshot(payload, mode):
    stats, rows = payload['stats'], payload['records']
    for key in ('callbacks', 'admitted', 'changed', 'errors', 'records', 'suppressed', 'active', 'mode'):
        if type(stats.get(key)) is not int or stats[key] < 0: raise ValueError('Malformed extension counter: '+key)
    if (not isinstance(rows, list) or len(rows) != stats['records'] or len(rows) > 128
            or any(r.get('k') not in ('net', 'cache', 'best', 'pv') for r in rows)):
        raise ValueError('Malformed bounded extension records')
    if stats['errors'] or stats['active'] or stats['suppressed'] or stats['changed'] > (0 if mode == 'baseline' else 1):
        raise RuntimeError('Extension fault, unfinished invocation, saturation or write budget failure')
    return {kind: sum(r['k'] == kind for r in rows) for kind in ('net', 'cache', 'best', 'pv')}


def baseline_gate(directory):
    """Treatment requires an independently closed, exposed no-write arm."""
    result = read(directory/'result.json')
    payload = read(directory/'boundary-native.json')
    config = read(directory/'extension-config.json')
    initial = read(directory/'source-loaded.json')
    validate_source(initial); counts = validate_snapshot(payload, 'baseline')
    if (result.get('closed') is not True or result.get('native_exit_code') != 0
            or result.get('mode') != 'baseline' or result.get('save_unchanged') is not True
            or result.get('installed_unchanged') is not True or result.get('preferences_restored') is not True
            or config != make_config(initial, 'baseline') or not counts['cache']):
        raise ValueError('Baseline closure, mapping or fresh cache proof missing')
    admitted = [r for r in payload['records'] if r['k'] == 'net' and
                (r['player'], r['city'], r['district'], r['plot']) == (4, 655369, config['districtIndex'], 3076)
                and r['eligible'] == 1 and r['reason'] == 0 and r['base'] == r['result']
                and r['base'] not in (0, -2559744)]
    if not admitted: raise ValueError('Baseline did not expose a qualifying target; no treatment')
    return initial


def run(a):
    out = a.output.resolve()
    if out.exists(): raise ValueError('New output directory required; no replay')
    if a.mode not in ('baseline', 'treatment'): raise ValueError('Explicit arm required')
    baseline = getattr(a, 'baseline', None)
    reference = baseline_gate(baseline) if a.mode == 'treatment' and baseline is not None else None
    if a.mode == 'treatment' and reference is None: raise ValueError('Treatment requires --baseline with a qualified closed arm')
    if (sha(a.source) != SAVE_SHA or a.source.suffix != '.Civ6Save'
            or a.source.resolve().parent != a.native_directory.resolve()
            or a.native_directory.resolve() != (Path.home()/'Documents/My Games/Sid Meier\'s Civilization VI/Saves/Single').resolve()):
        raise ValueError('Wrong exact source or native save directory')
    if native_inventory(): raise RuntimeError('Foreign Civ/Tuner/research owner; preserve it')
    spec = read(a.spec); spec['path'] = str(a.dll.resolve()); validate_spec(spec)
    if sha(a.dll) != EXPECTED: raise ValueError('Wrong native binary')
    from district_score_extension.daemon import NativeExtension
    out.mkdir(parents=True)
    installed_before = manifest(a.installed)
    if baseline is not None and installed_before != read(baseline/'installed-before.json'):
        raise ValueError('Installed package differs from baseline; no treatment')
    reader = HERE/'source_snapshot.lua'
    files = [a.binary, a.dll, a.source, a.script, a.spec, reader]
    files += [p for p in HERE.iterdir() if p.is_file() and p.suffix in ('.py', '.js', '.c', '.lua')]
    files += [Path(m.__file__) for m in list(sys.modules.values()) if getattr(m, '__file__', None)
              and Path(m.__file__).suffix == '.py' and Path(m.__file__).is_relative_to(ROOT/'project/tools')]
    files += list((ROOT/'project/tools/ai_baseline/full_game_controller').glob('*.lua'))
    pins = {str(p.resolve()): sha(p) for p in files}
    write_json(out/'installed-before.json', installed_before)
    write_json(out/'source-pins.json', pins)
    write_json(out/'source-archive.json', archive_sources(pins, out/'source-version'))
    dependency_pins = manifest(a.dependencies); write_json(out/'dependency-pins.json', dependency_pins)
    write_json(out/'protocol.json', dict(mode=a.mode, source_turn=250, maximum_endpoint=251, loads=1,
               fresh_worlds=0, deltaQ8=256, maxChanges=1, treated_autosaves_are_clean_reference=False,
               historical_world_reproduction=False, policy='declared current-CSC rebase; no RH, orders, saved edits or assistance callback changes',
               epoch_scope='one immutable single-load window, not a native generation API'))
    r = make_probe_controller(out, user_root=a.user_root)
    r.allow_observer_warning_dismissal = r.allow_observer_first_meet_dismissal = r.allow_observer_congress_review = True
    r.study_endpoint = 251
    session = NativeSession(out, r, inventory=native_inventory, hold=HeldProcess, write=write_json)
    extension = None; attach_attempted = False; initial = None; error = None; logs = {}; coverage = None

    def verify():
        if manifest(a.installed) != installed_before or manifest(a.dependencies) != dependency_pins:
            raise RuntimeError('Installed package/dependencies changed; preserve edits')
        if any(sha(p) != h for p, h in pins.items()): raise RuntimeError('Frozen source/input changed')

    def capture(label):
        value = parse(r.cmd(reader.read_text(encoding='utf-8'), 'GameCore_Tuner', label, wait=35))
        write_json(out/(label+'.json'), value); return value

    def gate():
        nonlocal initial
        initial = capture('source-loaded'); validate_source(initial); verify()
        if reference is not None and initial != reference: raise ValueError('Loaded treatment source differs from baseline')
        return True

    def log_snapshot(label):
        dest = out/'logs'/label; dest.mkdir(parents=True)
        for name, baseline in logs.items():
            path = a.user_root/'Logs'/name
            if name in ('AI_CityBuild.csv', 'AI_Behavior_Trees.csv', 'City_BuildQueue.csv') and not path.exists():
                raise RuntimeError('Required native log absent: '+name)
            if path.exists():
                current, delta = read_log_delta(path, baseline)
                (dest/name).write_bytes(current.data)
                write_json(dest/(name+'.boundary.json'), dict(initial=baseline.evidence(), current=current.evidence(), delta_bytes=len(delta)))

    def freeze():
        if extension is not None and attach_attempted: extension.before_menu()

    try:
        verify(); session.start(lambda: launch(a, out)); session.wait_context('MainMenu')
        configure(r, out, 'BASIC')
        session.load_once(a.source, sha256=SAVE_SHA, native_directory=a.native_directory, turn=250,
                          contexts=('GameCore_Tuner', 'PlotInfo', 'CSC_AdjacencyGameplay'), eligibility=gate)
        config = make_config(initial, a.mode)
        write_json(out/'native-spec.json', spec); write_json(out/'extension-config.json', config)
        proof = prove_loaded_module(session.owner, spec, out/'loaded-module.json')
        extension = NativeExtension(out/'extension', session.owner, script=a.script, spec=out/'native-spec.json',
                    config=out/'extension-config.json', dependencies=a.dependencies, loaded_module=out/'loaded-module.json')
        attach_attempted = True; extension.attach_disabled()
        if capture('source-attached-disabled') != initial: raise RuntimeError('Disabled attachment changed source facts')
        for name in ('AI_CityBuild.csv', 'AI_Behavior_Trees.csv', 'City_BuildQueue.csv', 'Lua.log', 'Database.log'):
            logs[name] = capture_log_baseline(a.user_root/'Logs'/name)
        write_json(out/'source-gate.json', dict(verified=True, turn=250, rebase_declared=True, loaded_module=proof,
                   original_human=False, current_human=False, assistance_OFF=True, no_pending_work=True))
        verify(); extension.start(); r.play(251)
        final = capture('boundary-251')
        if final['turn'] != 251 or economic_signature(final) != economic_signature(initial):
            raise RuntimeError('Wrong endpoint or unexpected CSC assistance effects')
        payload, saturated = extension.snapshot('turn-251')
        write_json(out/'boundary-native.json', payload)
        coverage = validate_snapshot(payload, a.mode)
        if saturated: raise RuntimeError('Saturated extension trace; no complete coverage claim')
        log_snapshot('turn-251')
        write_json(out/'observation-result.json', dict(mode=a.mode, initial=initial, final=final, coverage=coverage,
                   target_net_observed=coverage['net'] > 0, changes=payload['stats']['changed'],
                   missing_target='unobserved' if not coverage['net'] else None,
                   construction_or_changed_choice_proven=False, rollback_claimed=False))
    except BaseException as failure:
        error = failure
        write_json(out/'failure.json', dict(error=str(failure), traceback=traceback.format_exc(), no_automatic_replay=True))
    finally:
        if session.owner is not None and session.owner.poll() is None:
            try:
                session.close(restore_preferences=lambda: restore_preferences(r, out) if (out/'original-preferences.json').exists() else None,
                              restore_package=verify, before_menu=freeze,
                              after_native_exit=extension.after_native_exit if extension and getattr(extension, 'process', None) is not None else lambda: None)
                if logs: log_snapshot('closed')
            except BaseException as failure:
                write_json(out/'cleanup-failure.json', dict(error=str(failure), traceback=traceback.format_exc(), original_error=str(error)))
                if error is None: error = failure
        verify(); write_json(out/'final-inventory.json', native_inventory())
    if error is not None: raise error
    if not session.closed: raise RuntimeError('Native session remains unclosed')
    result = dict(closed=True, native_exit_code=0, intervals=[251], mode=a.mode, coverage=coverage,
                  save_unchanged=sha(a.source) == SAVE_SHA, installed_unchanged=manifest(a.installed) == installed_before,
                  preferences_restored=True, mutation_rollback_claimed=False, efficacy_test=False)
    write_json(out/'result.json', result); print(json.dumps(result))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('output', 'source', 'native-directory', 'binary', 'dll', 'user-root', 'installed', 'dependencies', 'spec', 'script'):
        p.add_argument('--'+name, type=Path, required=True)
    p.add_argument('--mode', choices=('baseline', 'treatment'), required=True)
    p.add_argument('--baseline', type=Path, help='Qualified closed baseline directory required for treatment')
    run(p.parse_args())


if __name__ == '__main__': main()
