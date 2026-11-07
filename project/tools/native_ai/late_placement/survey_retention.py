"""Track exact native Bakers chains across a fixed number of autoplay turns."""

import argparse
from collections import Counter
from pathlib import Path
import re

from driver import load, lua, read, require, sha, write_json
from full_game_controller.checkpoint import save_inactive_boundary


KEY = r'\d+(?:/\d+){7}'
DURATION = 150


def identities(receipt, turn):
    keys = re.findall(rf'CSC_COHORT_KEY ({KEY})', receipt)
    headers = re.findall(r'CSC_COHORT_CORE (\d+) (\d+)', receipt)
    require(headers == [(str(turn), str(len(keys)))] and len(set(keys)) == len(keys), 'Incomplete cohort identity receipt')
    return keys


def yields(receipts, turn):
    keys = identities(receipts['core'], turn)
    rows = re.findall(rf'CSC_COHORT_YIELD ({KEY}) ([\d.]+) ([\d.]+)', receipts['ui'])
    headers = re.findall(r'CSC_COHORT_UI (\d+) (\d+)', receipts['ui'])
    require(headers == [(str(turn), str(len(rows)))], 'Incomplete cohort yield receipt')
    require(all(key in keys for key, _, _ in rows), 'UI receipt does not refer to a gameplay chain')
    return {key: [float(food), float(mill_food)] for key, food, mill_food in rows}


def phases(receipt, start, end):
    rows = re.findall(rf'CSC_COHORT_PHASE (\d+) (\d+) ((?:{KEY})(?:,{KEY})*|-)', receipt)
    count = re.findall(r'CSC_COHORT_COUNT (\d+)', receipt)
    require('CSC_COHORT_FAULT' not in receipt and count == [str(len(rows))],
            'Incomplete cohort player-turn receipt')
    result = [(int(turn), int(player), set(keys.split(',')) - {'-'}) for turn, player, keys in rows]
    require({turn for turn, _, _ in result} == set(range(start, end)), 'Missing cohort round')
    require(len({(turn, player) for turn, player, _ in result}) == len(result), 'Repeated cohort player phase')
    return result


def advance(streaks, receipt, ui, start, end):
    """Keep only identities that worked at both endpoints and every phase between."""
    observations = phases(receipt, start, end)
    check_counts = Counter(player for _, player, _ in observations)
    intact = set.intersection(set(ui), *(keys for _, _, keys in observations))
    return {key: streaks.get(key, end) if key in intact and check_counts[int(key.split('/')[0])] == end - start
            else end for key in ui}


def run_survey(controller, out, args, start, probe, play):
    code = read(probe)
    installed = controller.cmd("CSC_BAKERS_COHORT_MODE='gameplay'\n" + code,
                               'CSC_AdjacencyGameplay', 'install-bakers-cohort')
    require('CSC_COHORT_INSTALLED' in installed, 'Cohort observer installation failed')

    def sample(turn):
        core = controller.cmd('CSC_BAKERS_COHORT.snapshot()', 'CSC_AdjacencyGameplay', f'cohort-identities-{turn}')
        scope = "CSC_BAKERS_COHORT_MODE='ui'\nCSC_BAKERS_COHORT_KEYS=" + lua(identities(core, turn)) + '\n'
        ui = controller.cmd(scope + code, 'PlotInfo', f'cohort-yields-{turn}')
        receipts = dict(core=core, ui=ui)
        return yields(receipts, turn), receipts

    turn = start
    current, receipt = sample(start)
    write_json(out / 'cohort-start.json', dict(turn=start, yields=receipt))
    streaks = dict.fromkeys(current, start)
    qualified = []
    while turn < args.through and not qualified:
        previous, turn = turn, min(turn + 8, args.through)
        play(previous, turn)
        observed = controller.cmd('CSC_BAKERS_COHORT.export()', 'CSC_AdjacencyGameplay', f'cohort-phases-{turn}')
        current, receipt = sample(turn)
        streaks = advance(streaks, observed, current, previous, turn)
        write_json(out / 'cohort' / f'{turn:03}.json', dict(start=previous, end=turn, phases=observed, yields=receipt,
                                                          streaks=streaks))
        qualified = sorted(key for key, since in streaks.items() if turn - since >= DURATION)
    checkpoint = save_inactive_boundary(controller, turn=turn, name='CSC_BAKERS_COHORT',
                                         native_directory=args.saves, archive=out / 'cohort.Civ6Save')
    write_json(out / 'cohort-result.json', dict(start=start, end=turn, streaks=streaks,
                                                qualified=qualified, checkpoint=checkpoint))


def audit(root):
    source = load(root / 'cohort-start.json')
    turn = source['turn']
    streaks = dict.fromkeys(yields(source['yields'], turn), turn)
    for path in sorted((root / 'cohort').glob('*.json')):
        interval = load(path)
        require(interval['start'] == turn and turn < interval['end'], 'Invalid cohort boundary')
        ui = yields(interval['yields'], interval['end'])
        streaks = advance(streaks, interval['phases'], ui, turn, interval['end'])
        require(streaks == interval['streaks'], 'Cohort replay audit disagrees with live streaks')
        turn = interval['end']
    result = load(root / 'cohort-result.json')
    checkpoint = result['checkpoint']
    require(checkpoint['verified'] and checkpoint['turn'] == turn and sha(Path(checkpoint['archive'])) == checkpoint['sha256'],
            'Missing exact cohort endpoint')
    require(load(root / 'restoration.json')['verified'] and load(root / 'session-closed.json')['verified'],
            'Unclosed cohort session')
    require(load(root / 'farm-trace-frozen.json')['fault'] is None, 'Cohort native trace fault')
    require(result['start'] == source['turn'] and result['end'] == turn and result['streaks'] == streaks,
            'Cohort result disagrees with evidence')
    qualified = {key: turn - start for key, start in streaks.items() if turn - start >= DURATION}
    require(sorted(qualified) == result['qualified'], 'Cohort result disagrees with qualified chains')
    return dict(end=turn, qualified=qualified)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run', type=Path)
    result = audit(parser.parse_args().run)
    print(result)
    raise SystemExit(0 if result['qualified'] else 1)
