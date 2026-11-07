"""Audit a closed Boston retention run against a duration in game turns."""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re


BOSTON_PLAYER = 3
GRANARY = 'BUILDING_GRANARY'
WATER_MILL = 'BUILDING_CSC_BAKERS_WATER_MILL'


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def yields_healthy(state):
    """Cross-check the chain and its yields from the independent interval sample."""
    city, effects = state['city'], state['effects']
    granary, mill = effects['buildings'][GRANARY], effects['buildings'][WATER_MILL]
    return (effects['turn'] == city['turn'] and state['operation']['operating']
            and state['operation']['mill'] == WATER_MILL and city['cityOwner'] == BOSTON_PLAYER
            and city['buildings'][GRANARY]['plot'] == 795 and city['buildings'][WATER_MILL]['plot'] == 721
            and granary['food'] >= effects['granaryBaseFood'] + 1
            and mill['production'] >= 1 and mill['gold'] >= 1)


def segment(root, through=None):
    result = read(root / 'result.json')
    states = read(root / 'states.json')
    start, end = result['start'], through if through is not None else result['turn']
    if not start < end <= result['turn']:
        raise ValueError('Requested segment falls outside its run')
    intervals = [read(path) for path in sorted((root / 'retention').glob('*.json'))]
    intervals = [interval for interval in intervals if interval['end'] <= end]
    cursor = start
    phases = Counter()
    interruptions = []
    for interval in intervals:
        if interval['start'] != cursor or interval['end'] <= cursor:
            raise ValueError('Invalid interval boundary in the evidence')
        receipt = interval['receipt']
        rows = [[int(turn), int(player), status] for turn, player, status in
                re.findall(r'CSC_RETENTION (\d+) (\d+) (\w+)', receipt)]
        if ('CSC_RETENTION_FAULT' in receipt or rows != interval['observations']
                or re.findall(r'CSC_RETENTION_COUNT (\d+)', receipt) != [str(len(rows))]):
            raise ValueError('Incomplete or mismatched raw turn receipt')
        cursor = interval['end']
        for turn, player, state in rows:
            if not interval['start'] <= turn < cursor:
                raise ValueError('Player observation falls outside its interval')
            phases[(turn, player)] += 1
            if state != 'working':
                interruptions.append(dict(turn=turn, player=player, state=state))
    missing = [turn for turn in range(start, end) if phases[(turn, BOSTON_PLAYER)] != 1]
    states = [state for state in states if state['city']['turn'] <= end]
    healthy_yields = all(yields_healthy(state) for state in states)
    boundaries = [start, *(interval['end'] for interval in intervals)]
    ui_boundaries_match = [state['city']['turn'] for state in states] == boundaries
    restored = read(root / 'restoration.json')['verified'] and read(root / 'session-closed.json')['verified']
    checkpoint = result['checkpoint'] if through is None else read(root / 'checkpoints' / f'{end:03}.json')
    save_verified = bool(checkpoint and checkpoint['verified'] and checkpoint['turn'] == end
                         and hashlib.sha256(Path(checkpoint['archive']).read_bytes()).hexdigest() == checkpoint['sha256'])
    guard_clean = read(root / 'farm-trace-frozen.json')['fault'] is None and result['native_writes'] == 0
    passed = (cursor == end and not interruptions and not missing
              and healthy_yields and ui_boundaries_match and restored and save_verified and guard_clean
              and (through is not None or result['stop'] == 'retention-endpoint'))
    healthy_turns = (interruptions[0]['turn'] if interruptions else end) - start
    return dict(passed=passed, start=start, end=end, elapsed_turns=end - start,
                turns_before_first_recorded_interruption=healthy_turns,
                player_phase_samples=sum(phases.values()), missing_or_repeated_boston_turns=missing,
                first_interruption=interruptions[0] if interruptions else None,
                ui_boundaries_match=ui_boundaries_match, all_interval_yields_healthy=healthy_yields,
                restoration_verified=restored, save_verified=save_verified, guard_clean=guard_clean,
                farm_rejections=result['farm_rejections'])


def audit(root, duration, prefix=None):
    current = segment(root)
    segments = [current]
    if prefix:
        join = current['start']
        earlier = segment(prefix, through=join)
        source = read(root / 'session-load-input.json')
        checkpoint = read(prefix / 'checkpoints' / f'{join:03}.json')
        original = next(state for state in read(prefix / 'states.json') if state['city']['turn'] == join)
        reloaded = read(root / 'states.json')[0]
        if source['sha256'] != checkpoint['sha256'] or source['turn'] != join or reloaded != original:
            raise ValueError('The replay did not reload the exact working prefix checkpoint')
        segments.insert(0, earlier)
    start, end = segments[0]['start'], current['end']
    passed = end - start >= duration and all(item['passed'] for item in segments)
    return dict(passed=passed, start=start, end=end, elapsed_turns=end - start, required_turns=duration,
                segments=segments)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run', type=Path)
    parser.add_argument('--prefix', type=Path, help='Closed run that produced the exact resumed checkpoint')
    parser.add_argument('--duration', type=int, default=150)
    args = parser.parse_args()
    if args.duration <= 0:
        parser.error('Duration must be positive')
    receipt = audit(args.run, args.duration, args.prefix)
    print(json.dumps(receipt, indent=2))
    raise SystemExit(0 if receipt['passed'] else 1)
