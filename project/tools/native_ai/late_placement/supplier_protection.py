"""Match the district choice that threatened Boston's adjacent Bakers Base."""

import argparse
import json
from pathlib import Path
import re
import shutil
import sys
import time

from driver import (
    HERE, ID, LOGS, STUDY, HOTFIX_SHA, XP2_IMAGE_SIZE, HeldProcess, NativeSession,
    archive_sources, capture_log_baseline, configure, flags, launch, load, lua,
    make_probe_controller, manifest, native_inventory, parse, prove_loaded_module,
    read, read_log_delta, require, restore_preferences, sha, write_json,
)
from full_game_controller.checkpoint import save_inactive_boundary


def protected_plots(neighbors):
    """Protect the last deposit and the last working supplier independently."""
    protected = set()
    for material in ('Base', 'Spec'):
        for field in ('deposit', 'working'):
            sites = [row['plot'] for row in neighbors if row['class'] == material and row[field]]
            if len(sites) == 1:
                protected.add(sites[0])
    return sorted(protected)


def calibration(trace, target):
    matches = [r for r in trace['records'] if r['kind'] == 'calculation' and r['tree'] == -1]
    winners = [r for r in trace['records'] if r['kind'] == 'winner']
    require(len(matches) == len(winners) == 1, 'Expected one fresh free calculation and selector')
    calc, winner = matches[0], winners[0]
    require(calc['sameCell'] and min(calc['before'], calc['native']) > 0
            and (winner['district'], winner['plot'], winner['score']) == (target['district'], target['plot'], calc['native']),
            'Control did not choose Campus on the protected deposit')
    alternative = winner['alternative']
    require(alternative and alternative['plot'] not in target['protectedPlots'], 'No owned positive safe competitor')
    delta = alternative['score'] - 256 - calc['native']
    require(-200000 <= delta < 0 and calc['native'] + delta > 0, 'Expected a bounded positive-to-positive deduction')
    return dict(before=calc['before'], native=calc['native'], delta=delta, reservation=calc['reservation'])


def run_arm(args, out, source, digest, turn, quarter, trace_code, probe, spec, frida, verify, control=None):
    controller = make_probe_controller(out, user_root=args.user_root)
    controller.study_endpoint = args.through
    controller.allow_observer_warning_dismissal = controller.allow_observer_first_meet_dismissal = True
    controller.allow_observer_congress_review = True
    session = NativeSession(out, controller, inventory=native_inventory, hold=HeldProcess, write=write_json)
    attached = script = trace = start = None
    states, messages = [], []
    boundaries = {}

    def sample(expected):
        raw = controller.cmd(probe, 'GameCore_Tuner', f'bakers-supplier-{expected}')
        world = parse(raw, 'CSC_BAKERS_SUPPLY_WORLD')
        city = parse(raw, 'CSC_NATURAL_FOLLOWTHROUGH')
        neighbors = [json.loads(value) for value in re.findall(r'CSC_BAKERS_SUPPLIER=([^\r\n]+)', raw)]
        require(city['turn'] == world['turn'] == expected and len({row['plot'] for row in neighbors}) == 6,
                'Expected exact six-neighbor census')
        result = dict(world=world, city=city, neighbors=neighbors, conditions=parse(raw, 'CSC_NATURAL_CHAIN'))
        states.append(result)
        write_json(out / 'states.json', states)
        return result

    def observe_source():
        nonlocal start
        start = sample(turn)
        require(start['city']['complete'] and start['city']['owner'] == start['city']['cityOwner'] == quarter['player'],
                'Exact completed Quarter required at the pre-decision boundary')
        if control:
            require(start == control['source'], 'Protection source differs from the control')
        return True

    def freeze():
        nonlocal trace
        if script is not None and trace is None:
            trace = script.exports_sync.freeze()
            write_json(out / 'trace-frozen.json', trace)

    verify()
    try:
        session.start(lambda: launch(args, out))
        session.wait_context('MainMenu')
        configure(controller, out, 'BASIC', csc_id=ID)
        require({key for key, enabled in flags(controller, 'isolated-package')['mods'].items() if enabled} == {ID},
                'Expected only isolated CSC')
        session.load_once(source, sha256=digest, native_directory=args.saves, turn=turn,
                          contexts=('GameCore_Tuner', 'PlotInfo', 'CSC_AdjacencyGameplay'), eligibility=observe_source)
        prove_loaded_module(session.owner, spec, out / 'loaded-module.json')
        critical = protected_plots(start['neighbors'])
        base = [row for row in start['neighbors'] if row['class'] == 'Base' and row['deposit']]
        require(len(base) == 1 and base[0]['plot'] in quarter['base'] and (base[0]['working'] or base[0]['developable']),
                'Target must be the last compatible Base deposit and currently developable or working')
        protected = base[0]['plot']
        target = dict(player=quarter['player'], city=quarter['city'], district=start['world']['campus'],
                      plot=protected, protectedPlots=critical)
        attached = frida.attach(session.owner.pid)
        script = attached.create_script(trace_code)
        script.on('message', lambda value, data: messages.append(value))
        script.load()
        require(script.exports_sync.init(spec) == 2, 'Expected two hooks')
        boundaries = {name: capture_log_baseline(args.user_root / 'Logs' / name) for name in (*LOGS, 'AI_Research.csv')}
        write_json(out / 'log-boundaries.json', {name: b.evidence() for name, b in boundaries.items()})
        script.exports_sync.prepare(start['world'], [target], control['pulse'] if control else None)
        script.exports_sync.start()
        current = turn + 1
        controller.play(current)
        freeze()
        require(trace['fault'] is None and not messages and trace['pending'] == 0 and trace['writes'] == int(bool(control)),
                'Protected selector trace did not qualify')
        if control:
            chosen = [row for row in trace['records'] if row['kind'] == 'winner' and row['writes'] == 1]
            require(len(chosen) == 1 and chosen[0]['district'] >= 0 and chosen[0]['plot'] not in critical,
                    'Native selector did not choose a different, safe site')
        pulse = control['pulse'] if control else calibration(trace, target)
        write_json(out / 'decision.json', dict(target=target, pulse=pulse))
        while True:
            state = sample(current)
            row = next(row for row in state['neighbors'] if row['plot'] == protected)
            retained = row['deposit'] and row['resource'] == base[0]['resource'] and state['city']['complete']
            if not retained or current == controller.study_endpoint:
                break
            current = min(current + 2, controller.study_endpoint)
            controller.play(current)
        next_save = None
        if control and retained:
            next_save = save_inactive_boundary(controller, turn=current, name='CSC_BAKERS_PROTECTED',
                                               native_directory=args.saves, archive=out / 'protected.Civ6Save')
            write_json(out / 'protected-checkpoint.json', next_save)
        result = dict(source=start, pulse=pulse, retained=retained, turn=current, checkpoint=next_save,
                      target=target, final=state)
        write_json(out / 'result.json', result)
    finally:
        if session.owner is not None and session.owner.poll() is None:
            try:
                session.close(restore_preferences=lambda: restore_preferences(controller, out)
                              if (out / 'original-preferences.json').exists() else None,
                              restore_package=verify, before_menu=freeze)
            finally:
                while attached is not None and not session.closed and session.owner.poll() is None:
                    time.sleep(1)
        write_json(out / 'frida-messages.json', messages)
        for name, boundary in boundaries.items():
            log = args.user_root / 'Logs' / name
            if log.is_file():
                _, data = read_log_delta(log, boundary)
                (out / name).write_bytes(data)
    require(session.closed and not messages, 'Closed, verified supplier experiment required')
    return result


def run(args):
    previous, out = args.replay.resolve(), args.output.resolve()
    installed = args.mods.resolve() / 'CSC Mill Building Study'
    require(not out.exists() and not installed.exists() and not native_inventory(), 'Fresh output and exclusive ownership required')
    require(load(previous / 'restoration.json')['verified'] and sha(args.dll) == HOTFIX_SHA,
            'Expected verified replay and patched stock GameCore')
    checkpoint = load(previous / 'treatment/pre-supplier-checkpoint.json')
    source, digest, turn = Path(checkpoint['native_save']), checkpoint['sha256'], checkpoint['turn']
    require(checkpoint['verified'] and source.parent == args.saves.resolve()
            and sha(source) == sha(Path(checkpoint['archive'])) == digest and turn < args.through <= 100,
            'Expected the exact pre-decision Online save and a later endpoint')
    quarter = load(previous / 'result.json')['treatment']['plan']['target']
    retired = previous / 'retired-study-copy'
    package = manifest(retired)
    original = load(args.study / 'run-03/content-before.json')
    require(package == original[str(installed)], 'Archived package differs from the study')
    untouched = {path: manifest(path) for path in original if path != str(installed)}
    spec = dict(path=str(args.dll.resolve()), sha256=HOTFIX_SHA, image_size=XP2_IMAGE_SIZE)
    sys.path.insert(0, str(args.dependencies.resolve()))
    import frida
    require(frida.__version__ == '17.24.3' and Path(frida.__file__).resolve().is_relative_to(args.dependencies.resolve()),
            'Exact existing Frida package required')
    native = [STUDY / 'observer.js', HERE / 'natural_bid.js']
    lua_files = [HERE / name for name in ('natural_followthrough.lua', 'natural_chain.lua', 'supplier_world.lua')]
    pins = {str(p.resolve()): sha(p) for p in (args.binary, args.dll, source, *native, *lua_files, Path(__file__))}
    out.mkdir(parents=True)
    write_json(out / 'source-pins.json', pins)
    write_json(out / 'source-archive.json', archive_sources(pins, out / 'source-version'))
    shutil.copytree(retired, installed)
    trace_code = "'use strict';\nconst CSC_LATE_PLACEMENT_COMPOSITE = true;\n" + '\n'.join(map(read, native))
    probe = 'CSC_BAKERS_TARGET=' + lua(quarter) + ';\n' + '\n'.join(map(read, lua_files))

    def verify():
        require(manifest(installed) == package and all(manifest(p) == value for p, value in untouched.items()),
                'Installed content changed')
        require(all(sha(path) == expected for path, expected in pins.items()), 'Pinned input changed')

    def arm(name, control=None):
        directory = out / name
        directory.mkdir()
        return run_arm(args, directory, source, digest, turn, quarter, trace_code, probe, spec, frida, verify, control)

    try:
        control = arm('control')
        write_json(out / 'result.json', dict(control=control))
        require(not control['retained'], 'The unmodified arm did not reproduce supplier loss')
        treatment = arm('treatment', control)
        write_json(out / 'result.json', dict(control=control, treatment=treatment))
    finally:
        require(not native_inventory(), 'Native owner remains. Preserve the temporary package.')
        verify()
        destination = out / 'retired-study-copy'
        require(installed.parent == args.mods.resolve() and destination.parent == out, 'Package retirement path mismatch')
        installed.rename(destination)
        write_json(out / 'restoration.json', dict(verified=manifest(destination) == package, owners_absent=True))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('replay', 'study', 'output', 'mods', 'saves', 'user-root', 'binary', 'dll', 'dependencies'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--through', type=int, required=True)
    run(parser.parse_args())
