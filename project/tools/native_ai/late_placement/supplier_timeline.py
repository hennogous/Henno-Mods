"""Join one supplier replay's archived evidence without inferring worker identity."""

from log_intelligence import records
from material_loss_intelligence import clear_targets, unit_operations

from driver import load, read, write_json


def write_supplier_timeline(root, states, target, trace, checkpoints):
    scope_path = root / 'pasture-recovery-scope.json'
    if not scope_path.is_file() or not states or trace is None:
        return
    scope = load(scope_path)
    start, end = states[0]['city']['turn'], states[-1]['city']['turn']
    player, plot = target['player'], scope['plot']
    tile = f"{scope['x']} {scope['y']}"
    events = [dict(source='native', time='interval-start', turn=row['boundary'], event=row)
              for row in trace['records']]
    for row in states:
        neighbor = next(value for value in row['neighbors'] if value['plot'] == plot)
        events.append(dict(source='state', time='inactive-boundary', turn=row['city']['turn'], supplier=neighbor,
                           operation=row['operation'], effects=row['effects']))

    tree_file = root / 'AI_Behavior_Trees.csv'
    targets = {}
    if tree_file.is_file():
        trees = read(tree_file)
        rows = [(turn, row, raw) for turn, _, row, raw in records(trees, start, end, {player}) if len(row) >= 7]
        touching = {(turn, row[2], row[3]) for turn, row, _ in rows
                    if (row[5], row[6]) in (('Reserve Plot', f'Reserving plot {tile}'),
                                            ('Move Unit', f'Moving unit to {tile}'))}
        nodes = {'Decode Trigger', 'Reserve Plot', 'Find Available Unit', 'Build Unit', 'Move Unit',
                 'Clear Plot', 'Build Improvement'}
        for turn, row, raw in rows:
            city_job = row[2:4] == ['City LOC_CITY_NAME_BOSTON', 'Build City Improvement']
            if row[5] in nodes and (city_job or (turn, row[2], row[3]) in touching):
                events.append(dict(source='tree', time='logged-turn', turn=turn, row=row[2:], raw=raw))
        if scope.get('width'):
            for row in clear_targets(trees, start, end, {player}, scope['width']):
                targets.setdefault((row['turn'], row['unit']), set()).add(row['plot'])

    unit_file = root / 'UnitOperations.log'
    if unit_file.is_file():
        for row in unit_operations(read(unit_file), start, end, {player}):
            if row['unit_type'] == 'UNIT_BUILDER' and row['operation'] in (
                    'UNITOPERATION_BUILD_IMPROVEMENT', 'UNITOPERATION_REPAIR', 'UNITOPERATION_HARVEST_RESOURCE'):
                plots = targets.get((row['turn'], row['unit']))
                linked = plots == {plot} and row['operation'] == 'UNITOPERATION_HARVEST_RESOURCE'
                events.append(dict(source='unit-log', time='logged-turn', turn=row['turn'],
                                   association='unique-tree-clear-target' if linked else 'player-only', event=row))

    events.sort(key=lambda row: row['turn'])
    write_json(root / 'supplier-timeline.json', dict(scope=scope, start=start, end=end, events=events,
                                                    native_fault=trace['fault'], checkpoints=checkpoints))
