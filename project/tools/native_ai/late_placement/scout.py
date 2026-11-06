"""Find and archive one natural Online checkpoint for the delayed Bakers bid."""

import argparse
from pathlib import Path
import shutil

from driver import (
    HERE, ID, STUDY, HOTFIX_SHA, XP2_IMAGE_SIZE, HeldProcess, NativeSession,
    archive_sources, configure, flags, launch, load, make_probe_controller,
    manifest, native_inventory, parse, prove_loaded_module, read, require,
    restore_preferences, sha, write_json,
)
from full_game_controller.checkpoint import save_inactive_boundary


def pilot_unlocks(pilot):
    if pilot is None:
        return {}, {}
    require(load(pilot / 'restoration.json')['verified'] and load(pilot / 'scout-result.json')['native_writes'] == 0,
            'Pilot must be a restored read-only natural run')
    states = {}
    unlocks = {}
    for path in sorted((pilot / 'scans').glob('*.json')):
        state = load(path)
        for player in state['civics']:
            fields = {k: player[k] for k in ('player', 'current', 'known', 'codeOfLaws')}
            states[(state['turn'], player['player'])] = fields
            if player['known']:
                unlocks.setdefault(player['player'], state['turn'])
    return states, unlocks


def sample_world(controller, turn, path, pilot=None, *, allow_unlocked=False):
    query = ('CSC_BAKERS_ALLOW_UNLOCKED=true;\n' if allow_unlocked else 'CSC_BAKERS_ALLOW_UNLOCKED=false;\n')
    state = parse(controller.cmd(query + read(HERE / 'scout.lua'), 'GameCore_Tuner', f'bakers-scout-{turn}'),
                  'CSC_BAKERS_SCOUT')
    require(state['turn'] == turn and state['speed'] == 'GAMESPEED_ONLINE', 'Scout clock or speed changed')
    ui = parse(controller.cmd(read(HERE / 'civic_progress.lua'), 'PlotInfo', f'bakers-civic-progress-{turn}'),
               'CSC_CIVIC_PROGRESS')
    state['ui'] = ui
    active = {}
    states, unlocks = pilot if pilot else ({}, {})
    for player in state['civics']:
        pid = player['player']
        if allow_unlocked and player['known'] and player['codeOfLaws']:
            active[pid] = dict(method='naturally-unlocked', eta=0)
            continue
        if player['known'] or not player['codeOfLaws'] or player['current'] != state['craftsmanship']:
            continue
        facts = ui['players'].get(str(pid), {})
        progress = facts.get('progress', -1) if ui['turn'] == turn else -1
        estimate = player['liveEta']
        if progress > 0 and 1 <= estimate <= 4:
            active[pid] = dict(method='native-gameplay-estimate', eta=estimate)
        elif estimate < 0 and progress > 0 and 1 <= facts.get('eta', -1) <= 4:
            active[pid] = dict(method='native-ui-estimate', eta=facts['eta'])
        elif estimate < 0 and (progress < 0 or facts.get('eta', -1) < 0):
            # Fallback timing comes from an earlier no-write run on the same
            # setup. It stays distinct from a current native research value.
            selection = {key: player[key] for key in ('player', 'current', 'known', 'codeOfLaws')}
            unlock = unlocks.get(pid, turn)
            if states.get((turn, pid)) == states.get((turn - 1, pid)) == selection and 1 <= unlock - turn <= 4:
                active[pid] = dict(method='natural-pilot-unlock', eta=unlock - turn, pilotUnlock=unlock)
    state['surveySites'] = state['candidates']
    state['candidates'] = [dict(site, readiness=active[site['player']]) for site in state['surveySites']
                           if site['player'] in active]
    if allow_unlocked:
        state['allowUnlocked'] = True
    write_json(path, state)
    return state


def run(args):
    out = args.output.resolve()
    installed = args.mods.resolve() / 'CSC Mill Building Study'
    require(not out.exists() and not installed.exists() and not native_inventory(),
            'Fresh output and no other Civ or Tuner owner required')
    require(sha(args.dll) == HOTFIX_SHA, 'Exact patched stock GameCore required')
    retired = args.study / 'retired-study-package'
    package = manifest(retired)
    original = load(args.study / 'run-03/content-before.json')
    require(original[str(installed)] == package, 'Isolated CSC package differs from the study archive')
    untouched = {p: manifest(p) for p in original if Path(p) != installed}
    out.mkdir(parents=True)
    setup = STUDY / 'game_setup.lua'
    pilot = pilot_unlocks(args.pilot)
    paths = [setup, HERE / 'scout.lua', HERE / 'civic_progress.lua', Path(__file__), HERE / 'driver.py', args.binary, args.dll]
    if args.pilot:
        require(sha(setup) == load(args.pilot / 'source-pins.json')[str(setup.resolve())], 'Pilot setup differs')
        paths.extend([args.pilot / 'scout-result.json', args.pilot / 'restoration.json',
                      *sorted((args.pilot / 'scans').glob('*.json'))])
    pins = {str(path.resolve()): sha(path) for path in paths}
    write_json(out / 'source-pins.json', pins)
    write_json(out / 'source-archive.json', archive_sources(pins, out / 'source-version'))
    shutil.copytree(retired, installed)

    def verify():
        require(manifest(installed) == package and all(manifest(p) == v for p, v in untouched.items()),
                'Installed content changed')
        require(all(sha(path) == digest for path, digest in pins.items()), 'Pinned input changed')

    c = make_probe_controller(out, user_root=args.user_root)
    c.study_endpoint = 25
    c.allow_observer_warning_dismissal = c.allow_observer_first_meet_dismissal = True
    c.allow_observer_congress_review = True
    session = NativeSession(out, c, inventory=native_inventory, hold=HeldProcess, write=write_json)
    checkpoint = None

    def sample(turn):
        return sample_world(c, turn, out / 'scans' / f'{turn:02d}.json', pilot)

    try:
        session.start(lambda: launch(args, out))
        session.wait_context('MainMenu')
        configure(c, out, 'BASIC', csc_id=ID)
        require({k for k, v in flags(c, 'exclusive-content')['mods'].items() if v} == {ID},
                'Only the isolated CSC package is expected')
        session.issue_once('host-natural-online', read(setup), 'MainMenu')
        session.ready_after_issue(1, ('GameCore_Tuner', 'PlotInfo', 'CSC_AdjacencyGameplay'),
                                  eligibility=lambda: True)
        prove_loaded_module(session.owner, dict(path=str(args.dll.resolve()), sha256=HOTFIX_SHA,
                                                image_size=XP2_IMAGE_SIZE), out / 'loaded-module.json')
        initial = sample(1)
        require(len(initial['civics']) == 5 and not any(p['known'] for p in initial['civics']),
                'Expected five original AIs with Craftsmanship locked')
        c.play(5)
        for turn in range(5, c.study_endpoint + 1):
            state = sample(turn)
            if state['candidates']:
                checkpoint = save_inactive_boundary(c, turn=turn, name='CSC_BAKERS_NATURAL',
                                                      native_directory=args.saves, archive=out / 'source.Civ6Save')
                write_json(out / 'checkpoint.json', checkpoint)
                break
            if turn < c.study_endpoint:
                c.play(turn + 1)
        write_json(out / 'scout-result.json', dict(checkpoint=checkpoint, end_turn=turn,
                                                   pilot=str(args.pilot.resolve()) if args.pilot else None,
                                                   candidate_count=len(state['candidates']), native_writes=0))
    finally:
        if session.owner is not None and session.owner.poll() is None:
            session.close(restore_preferences=lambda: restore_preferences(c, out)
                          if (out / 'original-preferences.json').exists() else None,
                          restore_package=verify)
        require(not native_inventory(), 'Native owner remains. Preserve the temporary package.')
        verify()
        destination = out / 'retired-study-copy'
        require(installed.parent == args.mods.resolve() and destination.parent == out,
                'Package retirement path mismatch')
        installed.rename(destination)
        write_json(out / 'restoration.json', dict(verified=manifest(destination) == package, owners_absent=True))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('study', 'output', 'mods', 'saves', 'user-root', 'binary', 'dll'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--pilot', type=Path)
    run(parser.parse_args())
