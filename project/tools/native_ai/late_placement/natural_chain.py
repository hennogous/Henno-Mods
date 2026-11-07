"""Observe native Bakers construction, operation, and retention from matched saves."""

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
from survey_retention import run_survey


def operating(state, target):
    """Separate physical supply, ordinary realized yields, and the Service."""
    city, conditions, effects = state['city'], state['conditions'], state['effects']
    neighbor = {row['plot']: row for row in state['neighbors']}
    mill = next((key for key, value in city['buildings'].items()
                 if key.endswith('_MILL') and value['present'] and not value['pillaged'] and value['plot'] == target['plot']), None)
    granary = city['buildings']['BUILDING_GRANARY']
    customer = granary['present'] and not granary['pillaged'] and granary['plot'] in neighbor \
        and neighbor[granary['plot']]['owner'] == target['player']
    supply = any(row['class'] == 'Base' and row['working'] for row in state['neighbors'])
    current_ui = effects['turn'] == city['turn']
    food = effects['buildings']['BUILDING_GRANARY']['food']
    production = effects['buildings'][mill]['production'] if mill else None
    exchange = (current_ui and mill is not None and customer and food is not None
                and food >= effects['granaryBaseFood'] + 1 and production is not None and production >= 1)
    growth = conditions['serviceGrowth'] or effects['serviceGrowthProperty']
    service = bool(conditions['feudalism'] and conditions['serviceMarker'] and growth and growth > 0)
    return dict(mill=mill, customer=customer, workingBase=supply, exchange=exchange,
                storekeeper=service, operating=bool(supply and exchange and service))


def mill_repair_plan(control, digest, start):
    require(load(control / 'restoration.json')['verified']
            and load(control / 'session-closed.json')['verified']
            and load(control / 'session-load-input.json')['sha256'] == digest,
            'Repair control must be closed, restored and matched to the source save')
    result = load(control / 'result.json')
    scope = load(control / 'mill-repair-scope.json')
    trace = load(control / 'mill-repair-trace-frozen.json')
    require(result['native_writes'] == 0 and not scope.get('repairBid') and not trace['fault'] and not trace['active'],
            'Expected a frozen stock control')
    # Use an executed alternative so its score also passed the native
    # unit/project checks. Stay one whole native utility unit above it.
    events = [row for row in trace['records'] if row['boundary'] == start]
    chosen = {row['pass']: row['offer'] for row in events
              if row['kind'] == 'contract-execute' and row['accepted']}
    lost = [(row['after'], chosen[row['pass']]) for row in events if row['kind'] == 'contract-update'
            and row['after']['building'] == scope['mill'] and row['pass'] in chosen
            and 0 < row['after']['q8'] < chosen[row['pass']]['q8']]
    require(len(lost) == 1, 'Need one eligible repair offer that lost to an executed contract')
    (repair, winner), = lost
    return dict(id=repair['id'], boundary=start, expectedQ8=repair['q8'], floorQ8=winner['q8'] + 256)


def run(args):
    match, out = args.match.resolve(), args.output.resolve()
    installed = args.mods.resolve() / 'CSC Mill Building Study'
    require(not out.exists() and not installed.exists() and not native_inventory(),
            'Fresh output and no other Civ or Tuner owner required')
    require(load(match / 'restoration.json')['verified'] and sha(args.dll) == HOTFIX_SHA,
            'Closed match and exact stock GameCore required')
    require(not args.guard_farm or (args.continue_from and args.dependencies),
            'The Farm guard requires the protected continuation and pinned Frida')
    require(not args.filter_farm_candidates or (args.guard_farm and not args.retain_from),
            'Candidate filtering requires the scoped Farm control and is a separate diagnostic')
    require(not args.retain_from or (args.continue_from and args.guard_farm),
            'Retention requires the proven operating branch and Farm guard')
    require(not args.resume_retention or args.retain_from,
            'A retention checkpoint must continue the proven operating branch')
    require(not args.survey_retention or args.resume_retention,
            'The cohort survey requires a verified intermediate checkpoint')
    require(not args.recover_from or (args.continue_from and not args.retain_from and not args.guard_farm),
            'A recovery baseline must observe a closed interruption without native score or Farm interventions')
    require(not args.observe_mill_repair or (args.recover_from and args.dependencies),
            'Mill observation requires the damaged continuation and pinned Frida')
    require(not args.repair_autosave or args.observe_mill_repair,
            'A repair autosave requires the scoped Mill diagnostic')
    require(not args.repair_control or args.repair_autosave,
            'A diagnostic repair bid requires a matched autosave control')
    treatment = load(match / 'result.json')['treatment']
    target = treatment['plan']['target']
    final = treatment['followthrough'][-1]
    require(treatment['trace']['writes'] == 1 and final['complete'], 'Completed matched Quarter required')
    checkpoint = load(match / 'treatment/completed-checkpoint.json')
    retired = match / 'retired-study-copy'
    if args.continue_from:
        protection = args.continue_from.resolve()
        require(load(protection / 'restoration.json')['verified'], 'Expected a closed supplier comparison')
        kept = load(protection / 'result.json')['treatment']
        require(kept['retained'] and kept['target']['plot'] in target['base'], 'Expected the matched protected supplier')
        checkpoint, final = kept['checkpoint'], kept['final']['city']
        retired = protection / 'retired-study-copy'
    retention = resume_state = None
    if args.retain_from:
        reference = args.retain_from.resolve()
        require(load(reference / 'restoration.json')['verified'], 'Expected a closed operating run')
        retention = load(reference / 'result.json')
        require(retention['stop'] == 'retained-stage-2-service' and retention['farm_rejections'] > 0,
                'Expected a verified operating checkpoint')
        checkpoint, final = retention['checkpoint'], retention['state']['city']
        retired = reference / 'retired-study-copy'
        if args.resume_retention:
            checkpoint_path = args.resume_retention.resolve()
            prefix = checkpoint_path.parent.parent
            require(checkpoint_path.parent == prefix / 'checkpoints'
                    and load(prefix / 'restoration.json')['verified'], 'Expected a closed retention run')
            require(load(prefix / 'session-load-input.json')['sha256'] == checkpoint['sha256'],
                    'Retention prefix must begin at the proven operating checkpoint')
            checkpoint = load(checkpoint_path)
            resume_state = next(state for state in load(prefix / 'states.json')
                                if state['city']['turn'] == checkpoint['turn'])
            require(resume_state['operation']['operating'], 'Expected a working retention checkpoint')
            final = resume_state['city']
    autosave_receipt = None
    if args.recover_from:
        reference = args.recover_from.resolve()
        require(load(reference / 'restoration.json')['verified'] and load(reference / 'session-closed.json')['verified'],
                'Expected a closed damaged checkpoint')
        interrupted = load(reference / 'result.json')
        damaged = interrupted['state']
        if args.repair_autosave:
            archive = args.repair_autosave.resolve()
            autosave_receipt = archive.parent / 'archive.json'
            archived = next(row for row in load(autosave_receipt)
                            if Path(row['archive']).resolve() == archive)
            saved_turn = archived['turn']
            digest = archived['sha256']
            require(sha(archive) == digest, 'Repair autosave archive changed')
            damaged = next(row for row in load(reference / 'states.json') if row['city']['turn'] == saved_turn)
        require(interrupted['stop'] in ('retention-interrupted', 'endpoint') and interrupted['native_writes'] == 0
                and not damaged['operation']['operating']
                and damaged['city']['owner'] == target['player'] and damaged['city']['complete']
                and any(row['plot'] in target['base'] and row['deposit'] and not row['working']
                        for row in damaged['neighbors'])
                and any(value['present'] and value['pillaged']
                        for key, value in damaged['city']['buildings'].items() if key.endswith('_MILL')),
                'Expected the observed supplier and Mill damage')
        checkpoint, final = interrupted['checkpoint'], damaged['city']
        retired = reference / 'retired-study-copy'
    supplier_types = {base['plot']: base['resource'] for base in final['base']}
    if autosave_receipt:
        start = saved_turn
        source = args.saves.resolve() / f'CSC_BAKERS_REPAIR_{start}_{digest[:12]}.Civ6Save'
        if not source.exists():
            with archive.open('rb') as saved, source.open('xb') as native:
                shutil.copyfileobj(saved, native)
        require(sha(source) == digest, 'Named repair autosave differs from the archive')
    else:
        source, digest, start = Path(checkpoint['native_save']), checkpoint['sha256'], checkpoint['turn']
        require(checkpoint['verified'] and source.parent == args.saves.resolve()
                and sha(source) == sha(Path(checkpoint['archive'])) == digest, 'Exact completed save required')
    limit = start + 200 if args.survey_retention else (start + 150 if retention else 100)
    if args.recover_from:
        limit = start + 36
    require(start == final['turn'] and start < args.through <= limit,
            'Expected a bounded later endpoint')
    package = manifest(retired)
    original = load(args.study / 'run-03/content-before.json')
    require(package == original[str(installed)], 'Archived CSC package identity mismatch')
    untouched = {path: manifest(path) for path in original if path != str(installed)}
    plot_probe, chain_probe = HERE / 'natural_followthrough.lua', HERE / 'natural_chain.lua'
    effects_probe, supply_probe = HERE / 'operating_effects.lua', HERE / 'supplier_world.lua'
    retention_probe = HERE / 'retention_observer.lua'
    cohort_probe = HERE / 'retention_cohort.lua'
    inputs = [args.dll, args.binary, source, plot_probe, chain_probe, Path(__file__), HERE / 'driver.py']
    if args.continue_from:
        inputs.extend((effects_probe, supply_probe))
    if retention:
        inputs.extend((retention_probe, args.retain_from / 'result.json'))
    if resume_state:
        inputs.extend((checkpoint_path, prefix / 'states.json'))
    if args.survey_retention:
        inputs.extend((cohort_probe, HERE / 'survey_retention.py'))
    if args.recover_from:
        inputs.append(reference / 'result.json')
    if autosave_receipt:
        inputs.extend((archive, autosave_receipt, reference / 'states.json'))
    repair_bid = None
    if args.repair_control:
        control = args.repair_control.resolve()
        repair_bid = mill_repair_plan(control, digest, start)
        inputs.extend(control / name for name in ('result.json', 'restoration.json', 'session-closed.json',
                      'session-load-input.json', 'mill-repair-scope.json', 'mill-repair-trace-frozen.json'))
    baseline = guard_code = None
    trace_name = 'mill-repair' if args.observe_mill_repair else 'farm'
    if args.guard_farm:
        reference = args.guard_farm.resolve()
        require(load(reference / 'restoration.json')['verified'], 'Expected a closed Farm-loss control')
        baseline = resume_state or (retention['state'] if retention else load(reference / 'states.json')[0])
        require(load(reference / 'result.json')['stop'] == 'supplier-or-quarter-lost', 'Expected the observed loss control')
        native = [STUDY / 'observer.js', HERE / 'farm_guard.js']
        inputs.extend((*native, reference / 'states.json', reference / 'UnitOperations.log'))
        guard_code = "'use strict';\nconst CSC_LATE_PLACEMENT_COMPOSITE = true;\n" + '\n'.join(map(read, native))
    elif args.observe_mill_repair:
        native = [STUDY / 'observer.js', HERE / 'mill_repair_observer.js']
        if repair_bid:
            native.append(HERE / 'mill_repair_bid.js')
        inputs.extend(native)
        guard_code = "'use strict';\nconst CSC_LATE_PLACEMENT_COMPOSITE = true;\n" + '\n'.join(map(read, native))
    if guard_code:
        sys.path.insert(0, str(args.dependencies.resolve()))
        import frida
        require(frida.__version__ == '17.24.3' and Path(frida.__file__).resolve().is_relative_to(args.dependencies.resolve()),
                'Exact existing Frida package required')
    pins = {str(path.resolve()): sha(path) for path in inputs}
    out.mkdir(parents=True)
    write_json(out / 'source-pins.json', pins)
    write_json(out / 'source-archive.json', archive_sources(pins, out / 'source-version'))
    shutil.copytree(retired, installed)

    def verify():
        require(manifest(installed) == package and all(manifest(p) == value for p, value in untouched.items()),
                'Installed content changed')
        require(all(sha(path) == expected for path, expected in pins.items()), 'Pinned input changed')

    controller = make_probe_controller(out, user_root=args.user_root)
    controller.study_endpoint = args.through
    controller.allow_observer_warning_dismissal = controller.allow_observer_first_meet_dismissal = True
    controller.allow_observer_congress_review = True
    controller.allow_one_more_turn = args.survey_retention
    session = NativeSession(out, controller, inventory=native_inventory, hold=HeldProcess, write=write_json)
    spec = dict(path=str(args.dll.resolve()), sha256=HOTFIX_SHA, image_size=XP2_IMAGE_SIZE)
    scope = 'CSC_BAKERS_TARGET=' + lua(target) + ';\n'
    source_code = scope + read(plot_probe) + '\n' + read(chain_probe)
    if args.continue_from:
        source_code += '\n' + read(supply_probe)
    names = (*LOGS, 'AI_Research.csv', 'UnitOperations.log', 'Game_RandomEvents.csv', 'AI_Tactical.csv')
    boundaries = {}
    states = []
    attached = script = frozen = None
    messages = []

    def freeze():
        nonlocal frozen
        if script is not None and frozen is None:
            frozen = script.exports_sync.freeze()
            write_json(out / f'{trace_name}-trace-frozen.json', frozen)

    def play(previous, turn):
        if script is not None:
            script.exports_sync.advance(previous)
        controller.play(turn)
        if script is not None:
            trace = script.exports_sync.snapshot()
            write_json(out / f'{trace_name}-trace-live.json', trace)
            require(trace['fault'] is None and not messages, f'{trace_name} trace fault')

    def sample(turn):
        raw = controller.cmd(source_code, 'GameCore_Tuner', f'bakers-stage2-{turn}')
        city = parse(raw, 'CSC_NATURAL_FOLLOWTHROUGH')
        require(city['turn'] == turn, 'Stage 2 observation clock changed')
        state = dict(city=city, conditions=parse(raw, 'CSC_NATURAL_CHAIN'))
        if args.continue_from:
            neighbors = [json.loads(value) for value in re.findall(r'CSC_BAKERS_SUPPLIER=([^\r\n]+)', raw)]
            require(len({row['plot'] for row in neighbors}) == 6, 'Expected all six neighboring plots')
            ui = controller.cmd(scope + read(effects_probe), 'PlotInfo', f'bakers-stage2-effects-{turn}')
            state.update(neighbors=neighbors, effects=parse(ui, 'CSC_BAKERS_EFFECTS'))
            state['operation'] = operating(state, target)
        states.append(state)
        write_json(out / 'states.json', states)
        return state

    def eligibility():
        state = sample(start)
        stable = ('owner', 'cityOwner', 'district', 'complete', 'buildings', 'base')
        require(all(state['city'][key] == final[key] for key in stable), 'Reloaded Quarter differs from completion')
        if baseline is not None:
            require(state == baseline, 'Reloaded source differs from the verified reference')
        if args.recover_from:
            require(state == damaged, 'Reloaded damaged chain differs from the exact interruption')
        return True

    def observe_interval(previous, current):
        receipt = controller.cmd('CSC_BAKERS_RETENTION.export();', 'CSC_AdjacencyGameplay',
                                 f'retention-{previous}-{current}')
        rows = [(int(turn), int(player), status) for turn, player, status in
                re.findall(r'CSC_RETENTION (\d+) (\d+) (\w+)', receipt)]
        count = re.findall(r'CSC_RETENTION_COUNT (\d+)', receipt)
        result = dict(start=previous, end=current, observations=rows, receipt=receipt)
        write_json(out / 'retention' / f'{current:03}.json', result)
        require('CSC_RETENTION_FAULT' not in receipt and count == [str(len(rows))], 'Incomplete turn event receipt')
        owner_turns = {turn for turn, player, _ in rows if player == target['player']}
        require(set(range(previous, current)) <= owner_turns, 'Missing Boston player-turn observations')
        return next((dict(turn=turn, player=player, status=status) for turn, player, status in rows
                     if status != 'working'), None)

    try:
        session.start(lambda: launch(args, out))
        session.wait_context('MainMenu')
        configure(controller, out, 'BASIC', csc_id=ID)
        require({key for key, enabled in flags(controller, 'isolated-package')['mods'].items() if enabled} == {ID},
                'Expected only isolated CSC')
        session.load_once(source, sha256=digest, native_directory=args.saves, turn=start,
                          contexts=('GameCore_Tuner', 'PlotInfo', 'CSC_AdjacencyGameplay'), eligibility=eligibility)
        prove_loaded_module(session.owner, spec, out / 'loaded-module.json')
        if retention and not args.survey_retention:
            receipt = controller.cmd(scope + read(retention_probe), 'CSC_AdjacencyGameplay', 'install-retention-observer')
            require('CSC_RETENTION_INSTALLED' in receipt, 'Retention observer installation failed')
        boundaries = {name: capture_log_baseline(args.user_root / 'Logs' / name) for name in names}
        write_json(out / 'log-boundaries.json', {name: b.evidence() for name, b in boundaries.items()})
        if guard_code:
            if args.observe_mill_repair:
                query = ('print(string.format(\'CSC_MILL_SCOPE={"mill":%d}\','
                         'assert(GameInfo.Buildings.BUILDING_CSC_BAKERS_WATER_MILL).Index));')
                raw = controller.cmd(query, 'GameCore_Tuner', 'native-mill-scope')
                native_scope = dict(parse(raw, 'CSC_MILL_SCOPE'), player=target['player'], city=target['city'])
                if repair_bid:
                    native_scope['repairBid'] = repair_bid
            else:
                query = ('local w,h=Map.GetGridSize(); local farm=assert(GameInfo.Improvements.IMPROVEMENT_FARM).Index;'
                         'print(string.format(\'CSC_FARM_SCOPE={"width":%d,"height":%d,"farm":%d}\',w,h,farm));')
                raw = controller.cmd(query, 'GameCore_Tuner', 'native-farm-scope')
                require(len(target['base']) == 1, 'Guard requires the exact tracked Base')
                native_scope = dict(parse(raw, 'CSC_FARM_SCOPE'), player=target['player'], plot=target['base'][0],
                                    filterCandidates=args.filter_farm_candidates)
            write_json(out / f'{trace_name}-scope.json', native_scope)
            attached = frida.attach(session.owner.pid)
            script = attached.create_script(guard_code)
            script.on('message', lambda value, data: messages.append(value))
            script.load()
            require(script.exports_sync.init(spec, native_scope), f'Expected qualified {trace_name} probe')
        if args.survey_retention:
            run_survey(controller, out, args, start, cohort_probe, play)
            freeze()
            require(frozen['fault'] is None and not messages, 'Farm guard failed before close')
            return
        turn, state = start, states[0]
        operating_since = None
        interruption = None
        while True:
            city, conditions = state['city'], state['conditions']
            owner = target['player']
            retained = (city['owner'] == city['cityOwner'] == owner and city['complete']
                        and any(base['owner'] == owner and base['district'] == -1 and base['resource'] >= 0
                                and base['resource'] == supplier_types[base['plot']]
                                for base in city['base']))
            options = conditions['options']
            mill_ready = any(option['canProduce'] is True or city['buildings'][key]['present']
                             for key, option in options.items() if key.endswith('_MILL'))
            technology_ready = options['BUILDING_CSC_BAKERS_WIND_MILL']['unlocked'] or (
                conditions['river'] and options['BUILDING_CSC_BAKERS_WATER_MILL']['unlocked'])
            if args.continue_from:
                active = state['operation']['operating']
                if active and operating_since is None:
                    operating_since = turn
                if not active:
                    operating_since = None
                done = operating_since is not None and turn >= operating_since + 3
            else:
                done = mill_ready or technology_ready
            if retention:
                done = bool(interruption or not state['operation']['operating'])
            if not retained or done or turn == args.through:
                break
            previous = turn
            turn = min(turn + (8 if retention else 3), args.through)
            play(previous, turn)
            state = sample(turn)
            if retention:
                interruption = observe_interval(previous, turn)
                if not interruption and state['operation']['operating'] and (turn - start) % 24 == 0 and turn < args.through:
                    archive = out / 'checkpoints' / f'{turn:03}.Civ6Save'
                    saved = save_inactive_boundary(controller, turn=turn, name='CSC_BAKERS_RETENTION',
                                                   native_directory=args.saves, archive=archive)
                    write_json(archive.with_suffix('.json'), saved)
        stopped = 'endpoint'
        if retention:
            stopped = 'retention-interrupted' if done or not retained else 'retention-endpoint'
        elif not retained:
            stopped = 'supplier-or-quarter-lost'
        elif args.continue_from and done:
            stopped = 'recovered-stage-2-service' if args.recover_from else 'retained-stage-2-service'
        elif not args.continue_from and mill_ready:
            stopped = 'mill-available'
        elif not args.continue_from and technology_ready:
            stopped = 'mill-technology-unlocked'
        next_save = None
        if retained and turn > start:
            next_save = save_inactive_boundary(controller, turn=turn, name='CSC_BAKERS_STAGE2',
                                               native_directory=args.saves, archive=out / 'stage2.Civ6Save')
        freeze()
        if frozen is not None:
            require(frozen['fault'] is None and not messages and not frozen['active'], f'{trace_name} probe failed before close')
        bids = [row for row in frozen['records'] if row['kind'] == 'repair-bid'] if args.observe_mill_repair else []
        write_json(out / 'result.json', dict(stop=stopped, turn=turn, native_writes=len(bids), state=state,
                                               operating_since=operating_since, checkpoint=next_save,
                                               farm_rejections=frozen.get('rejected', 0) if frozen else 0,
                                               start=start, interruption=interruption))
    finally:
        if session.owner is not None and session.owner.poll() is None:
            try:
                session.close(restore_preferences=lambda: restore_preferences(controller, out)
                              if (out / 'original-preferences.json').exists() else None,
                              restore_package=verify, before_menu=freeze)
            finally:
                while attached is not None and not session.closed and session.owner.poll() is None:
                    time.sleep(1)
        require(not native_inventory(), 'Native owner remains. Preserve the temporary package.')
        for name, boundary in boundaries.items():
            log = args.user_root / 'Logs' / name
            if log.is_file():
                _, data = read_log_delta(log, boundary)
                (out / name).write_bytes(data)
        verify()
        destination = out / 'retired-study-copy'
        require(installed.parent == args.mods.resolve() and destination.parent == out, 'Package retirement path mismatch')
        installed.rename(destination)
        write_json(out / 'restoration.json', dict(verified=manifest(destination) == package, owners_absent=True))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('match', 'study', 'output', 'mods', 'saves', 'user-root', 'binary', 'dll'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--through', type=int, required=True)
    parser.add_argument('--continue-from', type=Path, help='Resume an accepted supplier-protection save through the Service')
    parser.add_argument('--guard-farm', type=Path, help='Block the exact protected Farm candidate from the closed loss control')
    parser.add_argument('--filter-farm-candidates', action='store_true',
                        help='Diagnose rejecting the protected row before native selection')
    parser.add_argument('--dependencies', type=Path, help='Pinned Frida directory for the optional Farm guard')
    parser.add_argument('--retain-from', type=Path, help='Continue an accepted operating save and audit each player turn')
    parser.add_argument('--resume-retention', type=Path, help='Reload a healthy intermediate retention checkpoint')
    parser.add_argument('--survey-retention', action='store_true', help='Track other working Bakers chains in the same world')
    parser.add_argument('--recover-from', type=Path, help='Observe natural recovery after a verified damaged checkpoint')
    parser.add_argument('--observe-mill-repair', action='store_true', help='Trace Boston Mill production choices without writes')
    parser.add_argument('--repair-autosave', type=Path, help='Use an archived autosave that has a matching sampled damage state')
    parser.add_argument('--repair-control', type=Path, help='Derive one guarded bid from a closed autosave control')
    run(parser.parse_args())
