"""Observe the first Mill unlock in the completed Boston Bakers checkpoint."""

import argparse
from pathlib import Path
import shutil

from driver import (
    HERE, ID, LOGS, HOTFIX_SHA, XP2_IMAGE_SIZE, HeldProcess, NativeSession,
    archive_sources, capture_log_baseline, configure, flags, launch, load, lua,
    make_probe_controller, manifest, native_inventory, parse, prove_loaded_module,
    read, read_log_delta, require, restore_preferences, sha, write_json,
)
from full_game_controller.checkpoint import save_inactive_boundary


def run(args):
    match, out = args.match.resolve(), args.output.resolve()
    installed = args.mods.resolve() / 'CSC Mill Building Study'
    require(not out.exists() and not installed.exists() and not native_inventory(),
            'Fresh output and no other Civ or Tuner owner required')
    require(load(match / 'restoration.json')['verified'] and sha(args.dll) == HOTFIX_SHA,
            'Closed match and exact stock GameCore required')
    treatment = load(match / 'result.json')['treatment']
    target = treatment['plan']['target']
    final = treatment['followthrough'][-1]
    supplier_types = {base['plot']: base['resource'] for base in final['base']}
    require(treatment['trace']['writes'] == 1 and final['complete'], 'Completed matched Quarter required')
    checkpoint = load(match / 'treatment/completed-checkpoint.json')
    source, digest, start = Path(checkpoint['native_save']), checkpoint['sha256'], checkpoint['turn']
    require(checkpoint['verified'] and source.parent == args.saves.resolve()
            and sha(source) == sha(Path(checkpoint['archive'])) == digest, 'Exact completed save required')
    require(start == final['turn'] and start < args.through <= 100, 'Expected a later Online100 endpoint')
    retired = match / 'retired-study-copy'
    package = manifest(retired)
    original = load(args.study / 'run-03/content-before.json')
    require(package == original[str(installed)], 'Archived CSC package identity mismatch')
    untouched = {path: manifest(path) for path in original if path != str(installed)}
    plot_probe, chain_probe = HERE / 'natural_followthrough.lua', HERE / 'natural_chain.lua'
    inputs = (args.dll, args.binary, source, plot_probe, chain_probe, Path(__file__), HERE / 'driver.py')
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
    session = NativeSession(out, controller, inventory=native_inventory, hold=HeldProcess, write=write_json)
    spec = dict(path=str(args.dll.resolve()), sha256=HOTFIX_SHA, image_size=XP2_IMAGE_SIZE)
    source_code = 'CSC_BAKERS_TARGET=' + lua(target) + ';\n' + read(plot_probe) + '\n' + read(chain_probe)
    names = (*LOGS, 'AI_Research.csv')
    boundaries = {}
    states = []

    def sample(turn):
        raw = controller.cmd(source_code, 'GameCore_Tuner', f'bakers-stage2-{turn}')
        city = parse(raw, 'CSC_NATURAL_FOLLOWTHROUGH')
        require(city['turn'] == turn, 'Stage 2 observation clock changed')
        state = dict(city=city, conditions=parse(raw, 'CSC_NATURAL_CHAIN'))
        states.append(state)
        write_json(out / 'states.json', states)
        return state

    def eligibility():
        state = sample(start)
        stable = ('owner', 'cityOwner', 'district', 'complete', 'buildings', 'base')
        require(all(state['city'][key] == final[key] for key in stable), 'Reloaded Quarter differs from completion')
        return True

    try:
        session.start(lambda: launch(args, out))
        session.wait_context('MainMenu')
        configure(controller, out, 'BASIC', csc_id=ID)
        require({key for key, enabled in flags(controller, 'isolated-package')['mods'].items() if enabled} == {ID},
                'Expected only isolated CSC')
        session.load_once(source, sha256=digest, native_directory=args.saves, turn=start,
                          contexts=('GameCore_Tuner', 'PlotInfo', 'CSC_AdjacencyGameplay'), eligibility=eligibility)
        prove_loaded_module(session.owner, spec, out / 'loaded-module.json')
        boundaries = {name: capture_log_baseline(args.user_root / 'Logs' / name) for name in names}
        write_json(out / 'log-boundaries.json', {name: b.evidence() for name, b in boundaries.items()})
        turn, state = start, states[0]
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
            if not retained or mill_ready or technology_ready or turn == args.through:
                break
            turn = min(turn + 3, args.through)
            controller.play(turn)
            state = sample(turn)
        stopped = 'endpoint'
        if not retained:
            stopped = 'supplier-or-quarter-lost'
        elif mill_ready:
            stopped = 'mill-available'
        elif technology_ready:
            stopped = 'mill-technology-unlocked'
        next_save = None
        if retained and turn > start:
            next_save = save_inactive_boundary(controller, turn=turn, name='CSC_BAKERS_STAGE2',
                                               native_directory=args.saves, archive=out / 'stage2.Civ6Save')
        write_json(out / 'result.json', dict(stop=stopped, turn=turn, native_writes=0, state=state, checkpoint=next_save))
    finally:
        if session.owner is not None and session.owner.poll() is None:
            session.close(restore_preferences=lambda: restore_preferences(controller, out)
                          if (out / 'original-preferences.json').exists() else None, restore_package=verify)
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
    run(parser.parse_args())
