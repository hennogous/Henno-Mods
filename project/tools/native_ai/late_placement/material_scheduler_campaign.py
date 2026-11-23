"""Run a preselected three-arm Builder scheduler matrix via the shared controller.

The setup plan and first arm's arguments are external evidence. Each later
arm must match the opening map, starts and units of its seed's first arm.
No observer here issues game commands or overlaps native session ownership.
"""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys

from driver import manifest, write_json
from material_development_summary import verify_finish


HERE = Path(__file__).resolve().parent
PUBLISHER = Path('Lua_UI/AI/CSC_AI_BakersGameplay.lua')
FINISH_ON = b'CSC_AI_TEST_LAST_SUPPLIER_FINISH = true\n'
FINISH_OFF = b'CSC_AI_TEST_LAST_SUPPLIER_FINISH = false\n'
ARMS = ('tuning-no-scheduler', 'no-tuning', 'tuning-with-scheduler')


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def qualify_packages(base, scheduler):
    original = manifest(base)
    candidate = manifest(scheduler)
    changed = [name for name in original if original[name] != candidate.get(name)]
    if original.keys() != candidate.keys() or changed != [str(PUBLISHER)]:
        raise ValueError('CSC scheduler package must differ at exactly the publisher')
    off = (base / PUBLISHER).read_bytes()
    on = (scheduler / PUBLISHER).read_bytes()
    if off.startswith(FINISH_OFF):
        source = off[len(FINISH_OFF):]
        verified = on == FINISH_ON + source or (
            on == source and b'CSC_AI_TEST_LAST_SUPPLIER_FINISH~=false' in source)
    else:
        # Pre-default benchmarks preserve their archived control publisher.
        verified = b'CSC_AI_TEST_LAST_SUPPLIER_FINISH==true' in off and on == FINISH_ON + off
    if not verified:
        raise ValueError('CSC scheduler package has changes beyond the finishing switch')


def observed_boundary(output, endpoint):
    """Keep natural observer defeats as right-censored games in the seed set."""
    if (output / 'full-game-observation-complete.json').is_file():
        verify_finish(output, 1, endpoint)
        return endpoint
    failure = load(output / 'failure.json')
    if 'Original observer eliminated' not in failure['error']:
        raise ValueError(f'Game driver fault in {output}; see failure.json')
    close = load(output / 'session-closed.json')
    last = load(output / 'full-game-last-boundary.json')
    if not close['verified'] or close['native_exit_code'] or not last['verified'] or last['endpoint'] != endpoint:
        raise ValueError(f'No complete or naturally censored outcome in {output}')
    return last['turn']


def run(root, template, scheduler):
    root = root.resolve(strict=True)
    plan = load(root / 'plan.json')
    args = load(template)
    positions = {flag: args.index(flag) + 1 for flag in
                 ('--output', '--map', '--map-seed', '--game-seed', '--csc',
                  '--through', '--interval-minutes')}
    base = Path(args[positions['--csc']]).resolve(strict=True)
    qualify_packages(base, scheduler)
    endpoint = plan['endpoint']
    if plan['arms'] != list(ARMS) or (endpoint, plan['interval_minutes']) != (250, 15):
        raise ValueError('Unexpected three-arm test plan')
    state = {'plan': plan, 'complete': [], 'observer_eliminated': {}, 'active': None}

    def record():
        temp = root / 'campaign-progress.tmp'
        write_json(temp, state)
        temp.replace(root / 'campaign-progress.json')

    for seed in plan['seeds']:
        map_name = seed['map']
        for arm in ARMS:
            name = f'{map_name.lower()}-{arm}'
            output = root / name
            if not output.exists():
                state.update(active=name, free_bytes=shutil.disk_usage(root).free)
                record()
                options = args.copy()
                values = {'--output': output, '--map': map_name,
                          '--map-seed': seed['map_seed'], '--game-seed': seed['game_seed'],
                          '--csc': scheduler if arm == ARMS[2] else base,
                          '--through': endpoint, '--interval-minutes': plan['interval_minutes']}
                for flag, value in values.items():
                    options[positions[flag]] = str(value)
                if arm != ARMS[0]:
                    options.extend(('--reference-source', str(root / f'{map_name.lower()}-{ARMS[0]}' / 'source.json')))
                if arm == 'no-tuning':
                    options.append('--untuned')
                write_json(root / f'{name}-args.json', options)
                with (root / f'{name}-driver.log').open('w', encoding='utf-8') as log:
                    child = subprocess.run([sys.executable, '-u', str(HERE / 'ce_bakers_fresh.py'), *options],
                                           stdout=log, stderr=subprocess.STDOUT)
                if child.returncode and not (output / 'failure.json').exists():
                    state['failure'] = {'run': name, 'exit_code': child.returncode}
                    record()
                    raise RuntimeError(f'Game driver stopped during {name}. Inspect its log before resuming.')
            try:
                boundary = observed_boundary(output, endpoint)
            except (OSError, ValueError, KeyError) as error:
                state['failure'] = {'run': name, 'error': str(error)}
                record()
                raise
            protocol = load(output / 'protocol.json')
            if ((protocol['map'], protocol['map_seed'], protocol['game_seed']) !=
                    (map_name, seed['map_seed'], seed['game_seed'])
                    or protocol['untuned'] != (arm == 'no-tuning')):
                raise ValueError(f'Unexpected setup in {output}')
            if boundary == endpoint:
                state['complete'].append(name)
            else:
                state['observer_eliminated'][name] = boundary
            state['active'] = None
            record()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('root', 'template', 'scheduler'):
        parser.add_argument('--' + name, type=Path, required=True)
    run(**vars(parser.parse_args()))
