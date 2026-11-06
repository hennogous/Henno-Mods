"""Matched stock replay of one Bakers district bid during natural civic research."""

import argparse
from collections import Counter
from pathlib import Path
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
from scout import pilot_unlocks, sample_world


def choose_bid(trace, world):
    """Build a plan from the first usable winner and a fresh calculation."""
    def pair(receipt):
        return receipt['player'], receipt['city'], receipt['plot']

    fresh = Counter(pair(receipt) for receipt in trace['records']
                    if receipt['kind'] == 'calculation' and receipt['tree'] == -1)
    calculations = {}
    plans = []
    for receipt in trace['records']:
        city = (receipt['player'], receipt['city'])
        if receipt['kind'] == 'calculation':
            calculations.setdefault(city, {})[receipt['plot']] = receipt
            continue
        if receipt['district'] < 0:
            continue
        for calc in calculations.pop(city, {}).values():
            if calc['tree'] != -1 or fresh[pair(calc)] != 1 or not calc['sameCell'] or min(calc['before'], calc['native']) <= 0:
                continue
            target = next(site for site in world['candidates'] if
                          (site['player'], site['city'], site['plot']) == (*city, calc['plot']))
            same = (receipt['district'], receipt['plot']) == (target['district'], target['plot'])
            delta = receipt['score'] - calc['native'] + 256
            if same or 0 < delta <= 200000:
                pulse = None if same else dict(before=calc['before'], native=calc['native'], delta=delta)
                plans.append(dict(target=target, control_winner=receipt, pulse=pulse))
    # Follow a viable native Bakers choice when one exists. For a diagnostic
    # bid, favor more Base supply and use the smallest pulse among comparable sites.
    return min(plans, key=lambda p: (p['pulse'] is not None, -len(p['target']['base']), p['target']['feature'] != -1,
                                    p['pulse']['delta'] if p['pulse'] else 0), default=None)


def run_arm(args, out, source, digest, world, pilot, spec, code, verify, frida, plan=None, *, discover=False):
    controller = make_probe_controller(out, user_root=args.user_root)
    start_turn = world['turn']
    controller.study_endpoint = args.search_through if discover else min(start_turn + 22, 100)
    controller.allow_observer_warning_dismissal = controller.allow_observer_first_meet_dismissal = True
    controller.allow_observer_congress_review = True
    session = NativeSession(out, controller, inventory=native_inventory, hold=HeldProcess, write=write_json)
    attached = script = trace = None
    messages = []
    boundaries = {}
    followthrough = []

    def observe_source():
        current = sample_world(controller, start_turn, out / 'source-world.json', pilot,
                               allow_unlocked=world.get('allowUnlocked', False))
        # UI can be one phase behind at an inactive boundary. Match the core
        # facts and the qualified candidates, with raw UI receipts kept apart.
        require({k: v for k, v in current.items() if k != 'ui'} == {k: v for k, v in world.items() if k != 'ui'},
                'Loaded checkpoint source facts differ from scout')
        return True

    trace_path = out / 'trace-frozen.json'

    def freeze():
        nonlocal trace
        if script is not None and trace is None:
            trace = script.exports_sync.freeze()
            write_json(trace_path, trace)

    def observe_turn(scope, turn, path):
        nonlocal trace, trace_path
        trace, trace_path = None, path
        targets = [plan['target']] if plan else scope['candidates'][:64]
        script.exports_sync.prepare(scope, targets, plan and plan['pulse'])
        script.exports_sync.start()
        controller.play(turn + 1)
        freeze()
        require(trace['fault'] is None and trace['pending'] == 0 and not messages, 'Native trace failed')
        return trace

    def discover_window():
        # Save the inactive input of each observed decision window. The
        # comparison later reopens the first useful save in both arms.
        for turn in range(start_turn + 1, controller.study_endpoint):
            if controller.last_interval_turn < turn:
                controller.play(turn)
            window = out / 'windows' / f'{turn:02d}'
            scope = sample_world(controller, turn, window / 'world.json', pilot, allow_unlocked=True)
            if not scope['candidates']:
                continue
            checkpoint = save_inactive_boundary(controller, turn=turn, name='CSC_BAKERS_SELECTION',
                                                native_directory=args.saves, archive=window / 'source.Civ6Save')
            write_json(window / 'checkpoint.json', checkpoint)
            receipt = observe_turn(scope, turn, window / 'trace.json')
            require(receipt['writes'] == 0, 'Discovery must remain read-only')
            selected = choose_bid(receipt, scope)
            if selected:
                return dict(checkpoint=checkpoint, world=scope, plan=selected)
        return None

    verify()
    try:
        session.start(lambda: launch(args, out))
        session.wait_context('MainMenu')
        configure(controller, out, 'BASIC', csc_id=ID)
        require({key for key, enabled in flags(controller, 'isolated-package')['mods'].items() if enabled} == {ID},
                'Expected only isolated CSC')
        session.load_once(source, sha256=digest, native_directory=args.saves, turn=start_turn,
                          contexts=('GameCore_Tuner', 'PlotInfo', 'CSC_AdjacencyGameplay'), eligibility=observe_source)
        prove_loaded_module(session.owner, spec, out / 'loaded-module.json')
        attached = frida.attach(session.owner.pid)
        script = attached.create_script(code)
        script.on('message', lambda value, data: messages.append(value))
        script.load()
        require(script.exports_sync.init(spec) == 2, 'Expected two hooks')
        boundaries = {name: capture_log_baseline(args.user_root / 'Logs' / name) for name in LOGS}
        write_json(out / 'log-boundaries.json', {name: value.evidence() for name, value in boundaries.items()})
        def follow_selected(selected):
            turn = start_turn + 1
            target = selected['target']
            probe = 'CSC_BAKERS_TARGET=' + lua(target) + ';\n' + read(HERE / 'natural_followthrough.lua')
            while True:
                facts = parse(controller.cmd(probe, 'GameCore_Tuner', f'bakers-followthrough-{turn}'),
                              'CSC_NATURAL_FOLLOWTHROUGH')
                require(facts['turn'] == turn, 'Follow-through clock changed')
                followthrough.append(facts)
                write_json(out / 'followthrough.json', followthrough)
                if facts['complete'] and (plan or selected['pulse'] is None):
                    save = save_inactive_boundary(controller, turn=turn, name='CSC_BAKERS_FOUNDATION',
                                                  native_directory=args.saves, archive=out / 'completed.Civ6Save')
                    write_json(out / 'completed-checkpoint.json', save)
                if facts['owner'] != target['player'] or facts['cityOwner'] != target['player'] \
                        or facts['complete'] or facts['otherSite'] != -1 or turn == controller.study_endpoint:
                    break
                # Preserve the exact unlock/foundation boundary. Once founded,
                # production can be checked at wider intervals.
                turn = min(turn + (3 if facts['founded'] else 1), controller.study_endpoint)
                controller.play(turn)

        if discover:
            selected = discover_window()
            write_json(out / 'search-result.json', selected)
        else:
            observe_turn(world, start_turn, trace_path)
            if plan:
                target, pulse = plan['target'], plan['pulse']
                require(trace['writes'] == 1 and any(r['kind'] == 'winner' and r['writes'] == 1
                        and all(r[key] == target[key] for key in ('player', 'city', 'plot', 'district'))
                        and r['score'] == pulse['native'] + pulse['delta'] for r in trace['records']),
                        'The diagnostic bid did not reach native district selection')
            else:
                require(trace['writes'] == 0, 'Control must be read-only')
            selected = plan or choose_bid(trace, world)
            write_json(out / 'selected-plan.json', selected)
            if selected:
                follow_selected(selected)
    finally:
        if session.owner is not None and session.owner.poll() is None:
            try:
                session.close(restore_preferences=lambda: restore_preferences(controller, out)
                              if (out / 'original-preferences.json').exists() else None,
                              restore_package=verify, before_menu=freeze)
            finally:
                # Keep callbacks frozen and attached until the held process
                # exits if the supported shutdown times out.
                while attached is not None and not session.closed and session.owner.poll() is None:
                    time.sleep(1)
        write_json(out / 'frida-messages.json', messages)
        for name, boundary in boundaries.items():
            log = args.user_root / 'Logs' / name
            if log.is_file():
                _, data = read_log_delta(log, boundary)
                (out / name).write_bytes(data)
    require(session.closed and not messages, 'Closed session and clean native receipts required')
    return selected if discover else dict(plan=selected, trace=trace, followthrough=followthrough)


def run(args):
    out, scout = args.output.resolve(), args.scout.resolve()
    installed = args.mods.resolve() / 'CSC Mill Building Study'
    require(not out.exists() and not installed.exists() and not native_inventory(),
            'Fresh output and no other Civ or Tuner owner required')
    require(sha(args.dll) == HOTFIX_SHA and load(scout / 'restoration.json')['verified'],
            'Exact patched GameCore and closed scout required')
    def checked_source(checkpoint):
        source = Path(checkpoint['native_save'])
        digest = checkpoint['sha256']
        require(checkpoint['verified'] and source.parent == args.saves.resolve()
                and sha(source) == sha(Path(checkpoint['archive'])) == digest, 'Checkpoint identity mismatch')
        return source, digest

    checkpoint = load(scout / 'checkpoint.json')
    source, digest = checked_source(checkpoint)
    world = load(scout / 'scans' / f"{checkpoint['turn']:02d}.json")
    require(world['candidates'] and world['speed'] == 'GAMESPEED_ONLINE', 'No qualified Bakers site')
    require(args.search_through is None or world['turn'] + 1 < args.search_through <= 100,
            'Discovery endpoint must allow a later turn within Online100')
    pilot_path = load(scout / 'scout-result.json')['pilot']
    pilot = pilot_unlocks(Path(pilot_path) if pilot_path else None)
    retired = scout / 'retired-study-copy'
    package = manifest(retired)
    original = load(args.study / 'run-03/content-before.json')
    require(original[str(installed)] == package, 'Archived package differs from study')
    untouched = {path: manifest(path) for path in original if Path(path) != installed}
    spec = dict(path=str(args.dll.resolve()), sha256=HOTFIX_SHA, image_size=XP2_IMAGE_SIZE)
    sys.path.insert(0, str(args.dependencies.resolve()))
    import frida
    require(frida.__version__ == '17.24.3' and Path(frida.__file__).resolve().is_relative_to(args.dependencies.resolve()),
            'Exact existing Frida package required')
    observer, probe = STUDY / 'observer.js', HERE / 'natural_bid.js'
    controller_files = HERE.parents[1] / 'ai_baseline/full_game_controller'
    inputs = [args.binary, args.dll, source, observer, probe, Path(__file__), HERE / 'driver.py', HERE / 'scout.py',
              HERE / 'scout.lua', HERE / 'civic_progress.lua', HERE / 'natural_followthrough.lua',
              *controller_files.glob('*.py'), *controller_files.glob('*.lua')]
    if pilot_path:
        inputs.extend(sorted((Path(pilot_path) / 'scans').glob('*.json')))
    pins = {str(path.resolve()): sha(path) for path in inputs}
    out.mkdir(parents=True)
    write_json(out / 'source-pins.json', pins)
    write_json(out / 'source-archive.json', archive_sources(pins, out / 'source-version'))
    shutil.copytree(retired, installed)
    code = "'use strict';\nconst CSC_LATE_PLACEMENT_COMPOSITE = true;\n" + read(observer) + '\n' + read(probe)

    def verify():
        require(manifest(installed) == package and all(manifest(p) == value for p, value in untouched.items()),
                'Installed content changed')
        require(all(sha(path) == digest for path, digest in pins.items()), 'Pinned input changed')

    def arm(name, plan=None, *, discover=False):
        directory = out / name
        directory.mkdir()
        return run_arm(args, directory, source, digest, world, pilot, spec, code, verify, frida, plan, discover=discover)

    try:
        if args.search_through:
            found = arm('discovery', discover=True)
            if found is None:
                write_json(out / 'result.json', dict(outcome='no-qualified-selector-window'))
                return
            checkpoint, world = found['checkpoint'], found['world']
            source, digest = checked_source(checkpoint)
            pins[str(source)] = digest
            pins[checkpoint['archive']] = digest
            write_json(out / 'source-pins.json', pins)
        control = arm('control')
        write_json(out / 'result.json', dict(control=control))
        if control['plan'] and control['plan']['pulse']:
            ready = control['plan']['target']['readiness']['method'] == 'naturally-unlocked'
            known = next((r['turn'] for r in control['followthrough'] if r['craftsmanship']), None)
            require(known is not None and (ready or 1 <= known - world['turn'] <= 6),
                    'Control did not naturally complete Craftsmanship with time remaining in the preparation window')
            treatment = arm('treatment', control['plan'])
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
    for name in ('scout', 'study', 'output', 'mods', 'saves', 'user-root', 'binary', 'dll', 'dependencies'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--search-through', type=int, help='Find a later native selector window before comparing arms')
    run(parser.parse_args())
