"""Replay one exact Online turn for the late placement write and two corrections."""

import argparse
import csv
import io
import json
from pathlib import Path
import shutil
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
STUDY = HERE.parent / 'mill_building_study'
sys.path[:0] = [str(ROOT / 'project/tools/ai_baseline'), str(HERE.parent)]
from full_game_controller.environment import (
    archive_sources, configure, flags, launch, manifest, prove_loaded_module, restore_preferences, write_json,
)
from full_game_controller.log_capture import capture_log_baseline, read_log_delta
from full_game_controller.probe import make_probe_controller
from full_game_controller.session import NativeSession
from full_game_controller.windows_process import HeldProcess, native_inventory
from mill_building_study.driver import GAME_SHA, lua, parse, sha
from mill_building_study.analyze import analyze
from calibrate import calibrate

ID = 'd0f3a2ab-4fa6-4a7a-bf9b-b82a66fe2a09'
SAVE_SHA = 'df5d20f351e24921460a6a15d1087acca016b83cf0d4b150b3b26877ea5d1739'
# The control and pulse use no expected-building guard. Their archived writer
# predates the correction to read raw building values at aggregation entry.
PULSE_WRITER_SHA = 'cb23467f8e04a0e9dea7d27d7e9b6bd1a752949114a81d6e846040c25f9ae9af'
PLOT = 1210
DISTRICT = 36
BASE = dict(player=1, city=65536, district=DISTRICT, plot=PLOT)
LOGS = ('AI_CityBuild.csv', 'AI_Behavior_Trees.csv', 'City_BuildQueue.csv')
POLICY = ROOT / 'Civ Supply Chains/Lua_UI/AI/CSC_AI_QuarterPlacement.lua'


def read(path):
    return Path(path).read_text(encoding='utf-8-sig')


def load(path):
    return json.loads(read(path))


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def inspect_source(world, archived):
    require(world['turn'] == 1 and world['player0']['human'] is True, 'Wrong checkpoint clock or human identity')
    require(world['sourceValidation']['valid'] and world['observerConfig'] == archived['observerConfig'],
            'Current rules or target mapping differs from original study')
    target = world['targets'][0]
    site = target['candidate']
    require(target['player'] == 1 and target['city'] == 65536 and target['human'] is False and target['major'] is True,
            'Target is not the original major AI city')
    require(site == archived['targets'][0]['candidate'] and site['index'] == PLOT and site['owner'] == 1 and
            site['hills'] is False and site['river'] is False and site['riverEdges'] == 0 and site['district'] == -1 and
            site['revealed'] is True and any(r['index'] == DISTRICT and r['legal'] is True for r in site['adjacency']),
            'Expected legal flat inland candidate is absent')


def verify_main_policy(c, out, world, calibration):
    target = world['targets'][0]['candidate']
    site = dict(districtType=calibration['district'], legal=True, hills=target['hills'], riverEdges=target['riverEdges'])
    buildings = {r['building']: dict(rawQ8=r['raw_q8'], rootCreditsQ8={}) for r in calibration['buildings']}
    for root in calibration['root_receipts']:
        buildings[root['building']]['rootCreditsQ8'][root['modifier']] = root['credit_q8']
    forecast = dict(beforeQ8=calibration['before_aggregation_q8'], nativeQ8=calibration['expected_native_q8'],
                    buildings=buildings)
    code = (read(POLICY) + '\nlocal delta=CSC_AI_QuarterPlacement.BakersAdjustment(' + lua(site) + ',' + lua(forecast) +
            ');print("CSC_LATE_POLICY_Q8="..tostring(assert(delta)))')
    delta = parse(c.cmd(code, 'GameCore_Tuner', 'evaluate-main-CSC-policy'), 'CSC_LATE_POLICY_Q8')
    require(delta == calibration['delta_q8'], 'Main CSC policy differs from independent native accounting')
    write_json(out / 'main-policy-receipt.json', dict(verified=True, delta_q8=delta, sha256=sha(POLICY),
               context='GameCore_Tuner', input=dict(site=site, forecast=forecast)))
    return delta


def run_arm(a, out, plan, source, spec, archived, prior, verify, frida, calibration=None):
    c = make_probe_controller(out, user_root=a.user_root)
    c.study_endpoint = 2
    c.allow_observer_warning_dismissal = c.allow_observer_first_meet_dismissal = True
    c.allow_observer_congress_review = True
    session = NativeSession(out, c, inventory=native_inventory, hold=HeldProcess, write=write_json)
    attached = script = None
    initialized = False
    frozen = None
    boundaries = {}
    messages = []
    world = None

    def observe_source():
        nonlocal world
        c.cmd("assert(Game.GetCurrentGameTurn()==1 and Players[0]:IsHuman());"
              "assert(GameInfo.Yields.YIELD_CSC_AI_PLACEMENT==nil and GameInfo.CSC_AI_Profile==nil);"
              "assert(type(CE_AIDistrictScoresBegin)=='nil');"
              "local speed=GameConfiguration.GetGameSpeedType();"
              "assert(speed=='GAMESPEED_ONLINE' or GameInfo.GameSpeeds[speed].GameSpeedType=='GAMESPEED_ONLINE');",
              'GameCore_Tuner', 'source-identity')
        targets = [{k: t[k] for k in ('player', 'city', 'plot')} for t in archived['targets']]
        code = 'CSC_MILL_STUDY_CONFIG=' + lua(dict(targets=targets)) + ';\n' + read(STUDY / 'world.lua')
        world = parse(c.cmd(code, 'GameCore_Tuner', 'source-world', wait=30), 'CSC_MILL_BUILDING_WORLD')
        write_json(out / 'source-world.json', world)
        inspect_source(world, archived)
        if prior is not None:
            require(world == prior, 'Treatment source facts differ from baseline')
        return True

    def freeze():
        nonlocal frozen
        if initialized and frozen is None:
            frozen = script.exports_sync.freeze()
            write_json(out / 'trace-frozen.json', frozen)

    try:
        verify()
        session.start(lambda: launch(a, out))
        session.wait_context('MainMenu')
        configure(c, out, 'BASIC', csc_id=ID)
        require({k for k, v in flags(c, 'isolated-package')['mods'].items() if v} == {ID}, 'Expected only isolated CSC')
        session.load_once(source, sha256=SAVE_SHA, native_directory=source.parent, turn=1,
                          contexts=('GameCore_Tuner', 'PlotInfo', 'CSC_AdjacencyGameplay'), eligibility=observe_source)
        if calibration is not None:
            plan['delta'] = verify_main_policy(c, out, world, calibration)
        prove_loaded_module(session.owner, spec, out / 'loaded-module.json')
        attached = frida.attach(session.owner.pid)
        code = "'use strict';\nconst CSC_LATE_PLACEMENT_COMPOSITE = true;\n" + read(STUDY / 'observer.js') + '\n' + read(HERE / 'write.js')
        script = attached.create_script(code)
        script.on('message', lambda value, data: messages.append(value))
        script.load()
        config = dict(world['observerConfig'], latePlan=plan)
        status = script.exports_sync.init(spec, config)
        initialized = status['installed'] is True and status['hooks'] == 6
        require(initialized, 'Late probe hook installation incomplete')
        write_json(out / 'plan.json', plan)
        boundaries = {name: capture_log_baseline(a.user_root / 'Logs' / name) for name in LOGS}
        write_json(out / 'log-boundaries.json', {name: b.evidence() for name, b in boundaries.items()})
        script.exports_sync.start()
        c.play(2)
        freeze()
    finally:
        if session.owner is not None and session.owner.poll() is None:
            try:
                session.close(restore_preferences=lambda: restore_preferences(c, out)
                              if (out / 'original-preferences.json').exists() else None,
                              restore_package=verify, before_menu=freeze)
            finally:
                # Keep native instrumentation resident if graceful closure fails.
                while attached is not None and not session.closed and session.owner.poll() is None:
                    time.sleep(1)
        write_json(out / 'frida-messages.json', messages)
    require(session.closed and not messages and frozen and frozen['frozen'] and not frozen['stopReason'],
            'Expected closed process and complete frozen observation')
    late = frozen['late']
    require(late['hooks'] == 2 and not late['errors'] and late['active'] == 0 and
            late['writes'] == int(plan['delta'] != 0), 'Late hook fault or write count mismatch')

    deltas = {}
    for name, boundary in boundaries.items():
        log = a.user_root / 'Logs' / name
        if log.is_file():
            _, data = read_log_delta(log, boundary)
            (out / name).write_bytes(data)
            deltas[name] = data
    request_rows = [list(map(str.strip, row)) for row in csv.reader(io.StringIO(
        deltas['AI_CityBuild.csv'].decode('utf-8-sig', errors='replace')))]
    requests = [row for row in request_rows if row[:3] == ['1', '1', 'LOC_CITY_NAME_DELHI'] and 'SUBMITTED' in row]
    calculations = [r for r in late['records'] if r['kind'] == 'calculation']
    require(len(calculations) == 1, 'Exactly one fresh target calculation required')
    require(late['records'][0] == calculations[0], 'Target consumer ran before fresh calculation')
    winner = next(r for r in late['records'] if r['kind'] == 'winner')
    result = dict(calculation=calculations[0], winner=winner, requests=requests,
                  present_values=[r for r in late['records'] if r['kind'] == 'presentValue'])
    trace = dict(frozen, config=world['observerConfig'])
    accounting = analyze(trace, world)
    write_json(out / 'analysis.json', accounting)
    require(accounting['ok'], 'Native building ledger did not reconcile')
    result['calibration'] = calibrate(accounting)
    write_json(out / 'result.json', result)
    return result, world


def qualify_pulse(baseline, pulse, directory):
    control = baseline['calculation']
    expected = baseline['winner']['score'] + 256
    changed = pulse['calculation']
    require(changed['before'] == control['before'] and changed['native'] == control['native'] and
            changed['final'] == expected and changed['delta'] == expected - control['native'], 'Unmatched score pulse')
    require(pulse['winner'] == dict(kind='winner', district=DISTRICT, plot=PLOT, score=expected, writes=1) and
            any(r['score'] == expected and r['writes'] == 1 for r in pulse['present_values']),
            'Pulse did not reach the native winner and exact plot present value')
    native_build = any('DISTRICT_CSC_BAKERS_QUARTER' in row for row in pulse['requests'])
    tree = [list(map(str.strip, row)) for row in csv.reader(io.StringIO(read(directory / 'AI_Behavior_Trees.csv')))]
    tree = [row for row in tree if len(row) >= 7 and row[:4] == ['1', '1', 'City LOC_CITY_NAME_DELHI', 'Build City District']]
    facts = {
        'decode': any(row[4:7] == ['SUCCESS', 'Decode Trigger',
                      f'District: DISTRICT_CSC_BAKERS_QUARTER; Value: {expected // 256}'] for row in tree),
        'reservation': any(row[4:7] == ['SUCCESS', 'Reserve Plot', 'Reserving plot 26 16'] for row in tree),
        'civic': any(row[4:7] == ['RUNNING', 'Add Goal Tech', 'CIVIC_CRAFTSMANSHIP: Accepted'] for row in tree),
    }
    require(native_build or all(facts.values()), 'Missing Bakers construction request or exact prerequisite plan')
    return dict(native_build_request=native_build, preparation=facts)


def prior_proof(reference, archived, package):
    require(load(reference / 'restoration.json')['verified'] and manifest(reference / 'retired-study-copy') == package,
            'Prior package restoration cannot be verified')
    pins = load(reference / 'source-pins.json')
    archive = {item['source']: item['archive'] for item in load(reference / 'source-archive.json')['archived']}
    for path in (HERE / 'write.js', STUDY / 'observer.js'):
        key = str(path.resolve())
        accepted = {sha(path)}
        if path.name == 'write.js':
            accepted.add(PULSE_WRITER_SHA)
        require(pins[key] in accepted and sha(archive[key]) == pins[key], 'Prior native source archive differs from proof')
    observed = []
    for mode in ('baseline', 'pulse'):
        directory = reference / mode
        require(load(directory / 'session-closed.json')['verified'] and
                load(directory / 'preferences-restored.json')['verified'] and
                load(directory / 'session-load-input.json')['sha256'] == SAVE_SHA and
                load(directory / 'loaded-module.json')['sha256'] == GAME_SHA,
                'Prior native closure or input identity cannot be verified')
        trace = load(directory / 'trace-frozen.json')
        require(trace['frozen'] and not trace['stopReason'] and not trace['late']['errors'] and
                trace['late']['writes'] == int(mode == 'pulse'), 'Prior trace has a fault or unexpected write')
        world = load(directory / 'source-world.json')
        inspect_source(world, archived)
        result = load(directory / 'result.json')
        require(calibrate(load(directory / 'analysis.json')) == result['calibration'] and
                result['calculation'] == next(r for r in trace['late']['records'] if r['kind'] == 'calculation') and
                result['winner'] == next(r for r in trace['late']['records'] if r['kind'] == 'winner') and
                result['present_values'] == [r for r in trace['late']['records'] if r['kind'] == 'presentValue'],
                'Prior result is inconsistent with the trace')
        observed.append((result, world))
    (baseline, world), (pulse, matched_world) = observed
    require(world == matched_world, 'Prior input worlds differ')
    return baseline, world, pulse


def run(a):
    study, out = a.study.resolve(), a.output.resolve()
    retired = study / 'retired-study-package'
    installed = a.mods.resolve() / 'CSC Mill Building Study'
    require(not out.exists() and not installed.exists() and not native_inventory(), 'Expected fresh output and no native owner')
    original = load(study / 'run-03/content-before.json')
    package = manifest(retired)
    require(package == original[str(installed)], 'Retired study package bytes changed')
    untouched = {p: manifest(p) for p in original if Path(p) != installed}
    checkpoint = load(study / 'run-03/source-checkpoint.json')
    source = Path(checkpoint['native_save'])
    require(sha(source) == sha(Path(checkpoint['archive'])) == SAVE_SHA and sha(a.dll) == GAME_SHA,
            'Unexpected saved world or native binary')
    archived = load(study / 'run-03/probe/source-world.json')
    spec = load(study / 'observer-spec.json')
    spec['path'] = str(a.dll.resolve())
    sys.path.insert(0, str(a.dependencies.resolve()))
    import frida
    require(frida.__version__ == '17.24.3' and Path(frida.__file__).resolve().is_relative_to(a.dependencies.resolve()),
            'Exact existing Frida package required')
    out.mkdir(parents=True)
    sources = [a.dll, a.binary, source, POLICY, *HERE.glob('*.py'), HERE / 'write.js', *STUDY.glob('*.py'),
               STUDY / 'world.lua', STUDY / 'observer.js',
               *(ROOT / 'project/tools/ai_baseline/full_game_controller').glob('*.py'),
               *(ROOT / 'project/tools/ai_baseline/full_game_controller').glob('*.lua')]
    pins = {str(p.resolve()): sha(p) for p in sources}
    write_json(out / 'source-pins.json', pins)
    write_json(out / 'source-archive.json', archive_sources(pins, out / 'source-version'))
    shutil.copytree(retired, installed)

    def verify():
        require(manifest(installed) == package and all(manifest(p) == v for p, v in untouched.items()),
                'Installed content changed')
        require(all(sha(p) == v for p, v in pins.items()), 'Pinned experiment input changed')

    def arm(plan, prior=None, calibration=None):
        directory = out / plan['mode']
        directory.mkdir()
        return run_arm(a, directory, dict(BASE, **plan), source, spec, archived, prior, verify, frida, calibration)

    try:
        if a.reference:
            baseline, world, pulse = prior_proof(a.reference, archived, package)
            pulse_directory = a.reference / 'pulse'
        else:
            baseline, world = arm(dict(mode='baseline', delta=0))
            calc = baseline['calculation']
            delta = baseline['winner']['score'] - calc['native'] + 256
            pulse, _ = arm(dict(mode='pulse', delta=delta, expectedBefore=calc['before'], expectedNative=calc['native']), world)
            pulse_directory = out / 'pulse'
        calc = baseline['calculation']
        calibration = baseline['calibration']
        require(baseline['winner']['district'] != DISTRICT and
                any('DISTRICT_NEIGHBORHOOD' in row for row in baseline['requests']), 'Baseline did not expose natural control request')
        expected = dict(expectedBefore=calc['before'], expectedNative=calc['native'])
        proof = qualify_pulse(baseline, pulse, pulse_directory)
        write_json(out / 'late-write-proven.json', dict(baseline=baseline, pulse=pulse, proof=proof))
        building_indices = {r['type']: r['index'] for r in world['observerConfig']['buildings']}
        raw = [dict(index=building_indices[r['building']], raw=r['raw_q8']) for r in calibration['buildings']]
        corrected, _ = arm(dict(mode='correction', delta=calibration['delta_q8'], expectedBuildings=raw, **expected),
                           world, calibration)
        require(corrected['calibration'] == calibration and corrected['calculation']['final'] == calibration['corrected_q8'],
                'Correction does not match the measured native contribution')
        require(corrected['winner'] == dict(baseline['winner'], writes=1), 'Calibrated replay changed unrelated district winner')
        write_json(out / 'result.json', dict(baseline=baseline, pulse=pulse, proof=proof, corrected=corrected))
        print(json.dumps(dict(baseline=calc, pulse=pulse['calculation'], corrected=corrected['calculation'])), flush=True)
    finally:
        require(not native_inventory(), 'Native owner remains. Preserve the study package')
        verify()
        destination = out / 'retired-study-copy'
        require(installed.resolve().parent == a.mods.resolve() and destination.parent == out, 'Package retirement path')
        installed.rename(destination)
        write_json(out / 'restoration.json', dict(verified=manifest(destination) == package, owners_absent=True))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('study', 'output', 'mods', 'user-root', 'binary', 'dll', 'dependencies'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--reference', type=Path, help='Reuse closed and verified baseline/pulse evidence for the correction arm')
    run(parser.parse_args())
