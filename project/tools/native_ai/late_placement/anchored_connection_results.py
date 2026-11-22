"""Compare physical Quarter/customer links and their recorded opportunities."""

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import re

from planning_results import parse
from processing_time_summary import summarise


OPPORTUNITY = re.compile(
    r'CSC_AI_CONNECTION_OPPORTUNITY turn=(\d+) player=(\d+) identity='
    r'(quarterFirst|customerFirst):(\d+):([234]):([A-Z_]+):(\d+):(\d+):(\d+)')
WONDER_OPPORTUNITY = re.compile(
    r'CSC_AI_WONDER_CONNECTION_OPPORTUNITY turn=(\d+) player=(\d+) order=(quarterFirst|customerFirst) '
    r'quarter=([A-Z_]+) anchor=(\d+) building=(BUILDING_[A-Z0-9_]+) city=\d+ plot=(\d+)')


def connection_counts(log, original_ai, through, *, observations=None):
    """Join observed legal options to real foundations and completed links.

    Deduplicate stage/venue definitions for a physical pair. Keep ownership
    on the opportunity identity so conquest cannot turn a missed construction
    into a conversion for the original player. Completed links are physical
    and counted once even if subsequently captured.
    """
    options = defaultdict(dict)
    opportunities_by_district = set()
    for turn, pid, order, anchor, _, quarter, city, district, target in OPPORTUNITY.findall(log):
        turn, pid, anchor, city, district, target = map(int, (turn, pid, anchor, city, district, target))
        if pid not in original_ai or turn > through:
            continue
        quarter_plot, customer_plot = (anchor, target) if order == 'quarterFirst' else (target, anchor)
        identity = (pid, order, quarter, quarter_plot, customer_plot)
        # Several legal plots in the same eligible city/type are fallback
        # footprints for one missing partner district, not independent builds.
        group = (pid, order, quarter, anchor, city, district)
        opportunities_by_district.add(group)
        options[identity].setdefault(group, turn)
    if observations is None:
        observations = parse(log, 'CSC_PLANNING_')
    definitions = {row['district']: row['districtType'] for row in observations if row['kind']=='MAPPING'}
    completed = {}
    realized = set()
    realized_by_district = set()
    foundations = defaultdict(list)
    for row in observations:
        if row.get('player') not in original_ai or row.get('turn', 0) > through:
            continue
        if row['kind'] == 'FOUNDATION' and row.get('foundationDateKnown'):
            foundations[row['player'], row['plot']].append((row['turn'], row['district']))
        if row['kind'] != 'RELATION' or row.get('role') != 'customer' or not row.get('present'):
            continue
        if row.get('neighbourDistrict') == 0 or definitions.get(row.get('neighbourDistrict')) == 'DISTRICT_WONDER':
            continue
        if not (row.get('quarterComplete') and row.get('neighbourComplete')):
            continue
        order = {'quarterFirst': 'quarterFirst', 'neighbourFirst': 'customerFirst'}.get(
            row.get('foundationOrder'), 'unknown')
        quarter, qplot, cplot = (row[key] for key in ('quarter', 'quarterPlot', 'neighbourPlot'))
        key = (quarter, qplot, cplot, row['neighbourDistrict'])
        previous = completed.get(key)
        if previous is None or (previous == 'unknown' and order != 'unknown'):
            completed[key] = order
        identity = (row['player'], order, quarter, qplot, cplot)
        if identity in options:
            target_type = row['neighbourDistrict'] if order == 'quarterFirst' else row.get('quarterDistrict')
            # The customer-first option itself names the exact Quarter type.
            # Some earlier relation logs omit that index. The Quarter family
            # was still verified in the physical relationship key.
            other_foundation = row.get('neighbourFoundationTurn' if order == 'quarterFirst'
                                       else 'quarterFoundationTurn')
            target_city = row.get('neighbourCity' if order == 'quarterFirst' else 'city')
            matched = {group for group, seen in options[identity].items()
                       if (target_type is None or group[-1] == target_type)
                       and (target_city is None or group[-2] == target_city)
                       and other_foundation is not None and seen <= other_foundation}
            if matched:
                realized.add(identity)
                realized_by_district.update(matched)
    lost = set()
    for identity, groups in options.items():
        pid, order, _, qplot, cplot = identity
        plot = cplot if order == 'quarterFirst' else qplot
        if identity not in realized and any(turn >= min(groups.values()) and not any(
                district == group[-1] and seen <= turn for group, seen in groups.items())
                for turn, district in foundations[pid, plot]):
            lost.add(identity)

    def by_order_and_quarter(items):
        return dict(Counter(f'{order}:{quarter}' for _, order, quarter, *_ in items))

    counts = dict(opportunities=by_order_and_quarter(options), completed_opportunities=by_order_and_quarter(realized),
                  district_opportunities=by_order_and_quarter(opportunities_by_district),
                  completed_district_opportunities=by_order_and_quarter(realized_by_district),
                  lost_to_other_foundations=by_order_and_quarter(lost),
                  completed_physical_pairs=dict(Counter(f'{order}:{key[0]}' for key, order in completed.items())))
    return counts


def supplier_history(observations, players, through):
    """Measure observed continuity of each working, owned material link."""
    ever_working, interrupted = set(), set()
    active = {}
    for row in observations:
        if row.get('turn', 0) > through:
            continue
        if row['kind'] == 'MATERIAL_WATCH_ENDED':
            identity = tuple(map(int, row['identity'].split(':')))
            interrupted.update(active.pop(identity, ()))
        if row['kind'] != 'MATERIAL_STATE':
            continue
        identity = (row['quarterPlot'], row['materialPlot'])
        pid = row['player']
        current = set()
        if pid in players and row['owner'] == pid and row['working']:
            for role in ('base', 'spec'):
                if row[role]:
                    current.add((row['quarter'], role, pid, *identity))
        interrupted.update(active.get(identity, set()) - current)
        ever_working.update(current)
        active[identity] = current

    def counts(items):
        return dict(Counter(f'{quarter}:{role.upper()}' for quarter, role, *_ in items))

    endpoint = set().union(*active.values())
    return dict(ever_working=counts(ever_working), working_at_endpoint=counts(endpoint),
                working_without_observed_loss=counts(endpoint - interrupted),
                working_again_after_loss=counts(endpoint & interrupted))


def wonder_connections(log, observations, players, through):
    """Keep the actual Wonder building identity and find completed venues."""
    offered, completed, converted = {}, {}, set()
    for turn, player, order, quarter, anchor, building, target in WONDER_OPPORTUNITY.findall(log):
        turn, player, anchor, target = map(int, (turn, player, anchor, target))
        if player in players and turn <= through:
            qplot, wplot = (anchor, target) if order == 'quarterFirst' else (target, anchor)
            offered.setdefault((player, order, quarter, building, qplot, wplot), turn)
    for row in observations:
        if (row['kind'] != 'RELATION' or row.get('role') != 'wonderCustomer'
                or row.get('player') not in players or row['turn'] > through
                or not (row.get('quarterComplete') and row.get('neighbourComplete')
                        and row.get('buildingStatus', 0) > 0)):
            continue
        physical = (row['quarter'], row['building'], row['quarterPlot'], row['neighbourPlot'])
        order = {'quarterFirst': 'quarterFirst', 'neighbourFirst': 'customerFirst'}.get(row.get('foundationOrder'), 'unknown')
        if completed.get(physical, 'unknown') == 'unknown':
            completed[physical] = order
        key = (row['player'], order, *physical)
        foundation = row.get('neighbourFoundationTurn' if order == 'quarterFirst' else 'quarterFoundationTurn')
        if key in offered and foundation is not None and offered[key] <= foundation:
            converted.add(key)

    def counts(keys):
        return dict(Counter(f'{order}:{quarter}:{building}' for _, order, quarter, building, *_ in keys))

    return dict(opportunities=counts(offered), completed_opportunities=counts(converted),
                completed_physical_pairs=dict(Counter(f'{order}:{quarter}:{building}'
                    for (quarter, building, _, _), order in completed.items())))


def run_result(root):
    def read(name):
        return json.loads((root / name).read_text(encoding='utf-8-sig'))

    result = read('result.json')
    through = result['reached']
    if through != 250 or not (read('session-closed.json')['verified']
                              and read('full-game-observation-complete.json')['verified']):
        raise ValueError(f'Incomplete qualification arm {root}')
    players = set(read('source.json')['original_ai'])
    log = (root / 'Lua.log').read_text(encoding='utf-8-sig')
    observations = parse(log, 'CSC_PLANNING_')
    counts = connection_counts(log, players, through, observations=observations)
    timing = summarise(log, last=through)
    if (not counts['opportunities'] or timing['unobserved_turns'] or timing['incomplete_wall_turns']
            or timing['failed_attempts']):
        raise ValueError(f'Unqualified opportunity or guidance timing coverage in {root}')
    census = read('full-census-250.json')
    quarters = {row.split('\t')[3]: row.split('\t')[0] for kind, row in census['rows'] if kind == 'QUARTER'}
    supply = Counter()
    for kind, row in census['rows']:
        if kind == 'MATERIAL':
            plot, _, material, _, working = row.split('\t')
            supply[f'{quarters[plot]}:{material}:adjacent'] += 1
            if working == 'true':
                supply[f'{quarters[plot]}:{material}:working'] += 1
    material_tags = read('resource-stack-preflight.json')['groups']
    supplier_losses = Counter()
    for row in observations:
        if row['kind'] != 'MATERIAL_STATE' or row.get('player') not in players or row['turn'] > through:
            continue
        quarter = row['quarter']
        for material in ('BASE', 'SPEC'):
            if row.get('previousResource') not in material_tags.get(f'CLASS_CSC_{quarter}_{material}', []):
                continue
            if row.get('lostWorking'):
                supplier_losses[f'{quarter}:{material}:working_loss'] += 1
            if row.get('lostBase' if material == 'BASE' else 'lostSpec'):
                supplier_losses[f'{quarter}:{material}:material_loss'] += 1
    return dict(counts=counts, timing=timing['publisher_wall'],
                native_managed_timing=timing['native_managed_cell_wall'],
                endpoint_suppliers=dict(supply), supplier_losses=dict(supplier_losses),
                supplier_history=supplier_history(observations, players, through),
                wonder_connections=wonder_connections(log, observations, players, through))


if __name__ == '__main__':
    options = argparse.ArgumentParser(description=__doc__)
    options.add_argument('run', type=Path, nargs='+')
    args = options.parse_args()
    print(json.dumps({str(run): run_result(run) for run in args.run}, indent=2))
