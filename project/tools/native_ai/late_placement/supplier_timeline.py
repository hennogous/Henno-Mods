"""Join one supplier replay's archived evidence without inferring worker identity."""

import argparse
import json
from pathlib import Path
import re

from driver import load, parse, read, require, write_json

from log_intelligence import records
from material_loss_intelligence import clear_targets, unit_operations


def write_supplier_timeline(root, states, target, trace, checkpoints, *, scope=None):
    if scope is None:
        scope_path = root / 'pasture-recovery-scope.json'
        if not scope_path.is_file():
            return
        scope = load(scope_path)
    if not states:
        return
    start, end = states[0]['city']['turn'], states[-1]['city']['turn']
    player, plot = target['player'], scope['plot']
    tile = f"{scope['x']} {scope['y']}"
    events = [dict(source='native', time='interval-start', turn=row['boundary'], event=row)
              for row in trace['records']] if trace else []
    for row in states:
        neighbor = next(value for value in row['neighbors'] if value['plot'] == plot)
        events.append(dict(source='state', time='inactive-boundary', turn=row['city']['turn'], supplier=neighbor,
                           operation=row['operation'], effects=row['effects']))

    tree_file = root / 'AI_Behavior_Trees.csv'
    targets = {}
    builder_contracts = set()
    if tree_file.is_file():
        trees = read(tree_file)
        rows = [(turn, row, raw) for turn, _, row, raw in records(trees, start, end, {player}) if len(row) >= 7]
        touching = {(turn, row[2], row[3]) for turn, row, _ in rows
                    if (row[5], row[6]) in (('Reserve Plot', f'Reserving plot {tile}'),
                                            ('Move Unit', f'Moving unit to {tile}'))}
        nodes = {'Decode Trigger', 'Reserve Plot', 'Find Available Unit', 'Build Unit', 'Move Unit',
                 'Clear Plot', 'Build Improvement', 'Cancel Contract'}
        for turn, row, raw in rows:
            city_job = row[2:4] == ['City LOC_CITY_NAME_BOSTON', 'Build City Improvement']
            if row[5] in nodes and (city_job or (turn, row[2], row[3]) in touching):
                events.append(dict(source='tree', time='logged-turn', turn=turn, row=row[2:], raw=raw))
            if city_job and row[5] in ('Contract Manager Decorator', 'Cancel Contract'):
                contract = re.search(r'\bcontract (\d+)\b', row[6], re.I)
                if contract:
                    builder_contracts.add(int(contract[1]))
        if scope.get('width'):
            for row in clear_targets(trees, start, end, {player}, scope['width']):
                targets.setdefault((row['turn'], row['unit']), set()).add(row['plot'])

    contract_file = root / 'AI_CityBuild.csv'
    if contract_file.is_file() and builder_contracts:
        for turn, _, row, raw in records(read(contract_file), start, end, {player}):
            if 'UNIT_BUILDER' not in row or 'Build City Improvement' not in row:
                continue
            # The contract ID joins the tree and production records. A city
            # accepting a request does not identify the eventual worker.
            contract = re.search(r'\bCONTRACT (\d+)\b', raw)
            if contract and int(contract[1]) in builder_contracts:
                events.append(dict(source='city-build', time='logged-turn', turn=turn,
                                   contract=int(contract[1]), row=row[2:], raw=raw))

    unit_file = root / 'UnitOperations.log'
    if unit_file.is_file():
        for row in unit_operations(read(unit_file), start, end, {player}):
            if row['unit_type'] == 'UNIT_BUILDER' and row['operation'] in (
                    'UNITOPERATION_BUILD_IMPROVEMENT', 'UNITOPERATION_REPAIR', 'UNITOPERATION_HARVEST_RESOURCE'):
                plots = targets.get((row['turn'], row['unit']))
                linked = plots == {plot} and row['operation'] == 'UNITOPERATION_HARVEST_RESOURCE'
                events.append(dict(source='unit-log', time='logged-turn', turn=row['turn'],
                                   association='unique-tree-clear-target' if linked else 'player-only', event=row))

    lua_log = root / 'Lua.log'
    if lua_log.is_file():
        for line in read(lua_log).splitlines():
            publication = re.search(r'CSC_AI_BAKERS_(BUILDERS|WONDERS|HARVEST) turn=(\d+) .*?previous=(\{.*\})', line)
            if publication:
                events.append(dict(source='ce-publication', time='publication-turn', turn=int(publication[2]),
                                   capability=publication[1], previous=json.loads(publication[3]), raw=line))

    events.sort(key=lambda row: row['turn'])
    write_json(root / 'supplier-timeline.json', dict(scope=scope, start=start, end=end, events=events,
                                                    native_trace_available=trace is not None,
                                                    native_fault=trace['fault'] if trace else None, checkpoints=checkpoints))


def write_matched_timelines(root, scope):
    """Read closed arms and link their own evidence to the verified source hash."""
    first = None
    inputs = []
    for name in ('control', 'treatment'):
        arm = root / name
        require(load(arm / 'session-closed.json')['verified'] and load(arm / 'restoration.json')['verified'],
                f'Expected a closed {name} arm')
        result = load(arm / 'result.json')
        states = [result['source'], *load(arm / 'observations.json')]
        turn = states[0]['city']['turn']
        digest = load(arm / 'session-load-input.json')['sha256']
        source = (digest, states[0])
        require(first is None or source == first, 'The arms have different starting evidence')
        first = source
        command = next((arm / 'commands').glob(f'*-bakers-supplier-{turn}.txt'))
        world = parse(read(command), 'CSC_BAKERS_SUPPLY_WORLD')
        scoped = dict(scope, width=world['width'])
        checkpoints = [dict(turn=turn, sha256=digest, role='matched-source')]
        archives = arm / 'decision-saves/archive.json'
        if archives.is_file():
            checkpoints.extend(load(archives))
        trace_file = arm / 'pasture-recovery-trace-frozen.json'
        trace = load(trace_file) if trace_file.is_file() else None
        require(trace is None or (not trace['active'] and not trace['fault']), f'Incomplete {name} native trace')
        inputs.append((arm, states, scoped, trace, checkpoints))
    for arm, states, scoped, trace, checkpoints in inputs:
        write_supplier_timeline(arm, states, scoped, trace, checkpoints, scope=scoped)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Join both closed CE supplier replay timelines')
    parser.add_argument('pair', type=Path)
    parser.add_argument('--scope', type=Path, required=True, help='Target coordinates and identity from the stock observer')
    args = parser.parse_args()
    write_matched_timelines(args.pair, load(args.scope))
