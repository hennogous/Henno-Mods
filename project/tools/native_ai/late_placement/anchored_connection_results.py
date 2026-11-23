"""Compare physical Quarter/customer links and their recorded opportunities."""

import argparse
from collections import Counter, defaultdict
import csv
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
STRONG_LAYOUT = re.compile(
    r'CSC_AI_STRONG_QUARTER_LAYOUT turn=(\d+) player=(\d+) city=(\d+) district=(\d+) plot=(\d+) '
    r'customerCity=(\d+) customerDistrict=(-?\d+) customerPlot=(\d+) stage=([234]) '
    r'existing=(true|false) extraBase=(true|false) specialty=(true|false)')
QUARTER_TITLE = re.compile(r'CSC_DISTRICT_CATALOGUE\t(\d+)\tDISTRICT_CSC_([A-Z_]+)_QUARTER\t')
QUARTER_RECEIPT = re.compile(r'CSC_QUARTER_WATCH_(WRITE|BEST)\t([^\r\n]+)')
DISTRICT_TITLE = re.compile(r'CSC_DISTRICT_CATALOGUE\t(\d+)\t([^\t\r\n]+)')
CUSTOMER_BID = re.compile(r'CSC_AI_CUSTOMER_(?:FUTURE|ECONOMIC)_BID ([^\r\n]+)')
CUSTOMER_RECEIPT = re.compile(r'CSC_CUSTOMER_WATCH_NATIVE [^\r\n]*? ordinal=(\d+) record=(\{[^\r\n]+\})')


def bid_competition(log, observations, players, through):
    """Name winners only when a positive CSC cell was observed before selection.

    An overwritten last-write row can fall after a comparison in the same
    packet. Keep such comparisons out of the score-gap sample. For an ordinary
    customer, require a positive native application followed by a cached score
    read. A NetValue delta alone is an earlier input, not the final score.
    """
    names = {int(index): title for index, title in DISTRICT_TITLE.findall(log)}
    versions = defaultdict(set)
    for row in observations:
        if row['kind'] == 'PUBLICATION' and row['accepted'] and row['pendingTurn'] <= through:
            versions[row['pendingTurn']].add(row['version'])
    quarters = {tuple(r[k] for k in ('version', 'player', 'city', 'district', 'plot')): r['bidQ8']
                for r in observations if r['kind'] == 'OPPORTUNITY' and r.get('offered')
                and r['player'] in players and r['turn'] <= through}
    customers = set()
    for match in CUSTOMER_BID.finditer(log):
        row = dict(field.split('=', 1) for field in match[1].split() if '=' in field)
        published = versions.get(int(row['turn']), ())
        if len(published) == 1 and int(row['deltaQ8']) > 0 and int(row['player']) in players:
            version = next(iter(published))
            customers.add((version, *(int(row[k]) for k in ('player', 'city', 'district', 'plot'))))

    decisions = defaultdict(list)
    for row in observations:
        if row['kind'] == 'NATIVE_BEST' and row.get('player') in players and row['turn'] <= through:
            group = tuple(row[k] for k in ('generation', 'version', 'player', 'city'))
            decisions[group].append((row['nativeOrdinal'], 'winner', row['district'], row['plot'], row['result']))
    for match in QUARTER_RECEIPT.finditer(log):
        if match[1] != 'WRITE':
            continue
        row = dict(field.split('=', 1) for field in match[2].split('\t') if '=' in field)
        key = tuple(int(row[k]) for k in ('version', 'player', 'city', 'district', 'plot'))
        group = (int(row['generation']), *key[:3])
        if group in decisions and row['eligible'] == '1' and quarters.get(key) == int(row['result']):
            decisions[group].append((int(row['nativeOrdinal']), 'quarter', *key[3:], int(row['result'])))

    if customers:
        positive = set()
        for match in CUSTOMER_RECEIPT.finditer(log):
            row = json.loads(match[2])
            key = tuple(row[k] for k in ('version', 'player', 'city', 'district', 'plot'))
            group = (row['generation'], *key[:3])
            if group not in decisions or key not in customers:
                continue
            cell = (row['generation'], *key)
            if row['k'] == 'net':
                if row['result'] > row['base'] and row['eligible'] == 1:
                    positive.add(cell)
                else:
                    positive.discard(cell)
            if row['k'] == 'cache' and row['result'] > 0 and row['eligible'] == 1 and cell in positive:
                decisions[group].append((int(match[1]), 'customer', *key[3:], row['result']))

    outcomes = defaultdict(Counter)
    lost_to = defaultdict(Counter)
    losses = []
    for (generation, version, player, city), events in sorted(decisions.items()):
        cells = defaultdict(dict)
        for ordinal, kind, district, plot, score in sorted(events):
            if kind != 'winner':
                cells[kind, district][plot] = score
                continue
            for (bid_kind, bid_district), plots in cells.items():
                # Each district/type contributes its strongest observed site
                # once in this decision. Counting its alternative tiles would
                # turn a single missed investment into several apparent losses.
                bid_score = max(plots.values())
                bid_plot = min(p for p, value in plots.items() if value == bid_score)
                if district == bid_district and plots.get(plot) == score:
                    outcomes[bid_kind]['exact_win'] += 1
                elif district >= 0 and score > bid_score:
                    winner, bidder = names.get(district, str(district)), names.get(bid_district, str(bid_district))
                    outcomes[bid_kind]['outscored'] += 1
                    lost_to[bid_kind][winner] += 1
                    losses.append(dict(kind=bid_kind, generation=generation, version=version,
                        player=player, city=city, ordinal=ordinal, district=bidder, plot=bid_plot,
                        score_q8=bid_score, winner=winner, winner_plot=plot, winner_q8=score,
                        gap_q8=score-bid_score))
                else:
                    outcomes[bid_kind]['other_or_unresolved'] += 1
    return dict(outcomes={k: dict(v) for k, v in outcomes.items()},
                lost_to={k: dict(v) for k, v in lost_to.items()}, losses=losses)


def failed_district_requests(build_rows, queue_rows, players, district_types, through):
    """Identify items receiving production while a district request was pending."""
    owners, requests, failed = defaultdict(set), {}, []
    for row in build_rows:
        if len(row) < 3 or not row[0].isdigit() or not row[1].isdigit():
            continue
        turn, player, city = int(row[0]), int(row[1]), row[2]
        if turn > through:
            continue
        owners[turn, city].add(player)
        if len(row) < 9 or player not in players or not row[4].startswith('CONTRACT '):
            continue
        contract, status, district = row[4], row[5], row[8]
        if district not in district_types:
            continue
        key = (player, city, contract)
        if status == 'SUBMITTED':
            requests.setdefault(key, turn)
        elif status in {'FAILED', 'CANCELLED', 'COMPLETED'} and key in requests:
            submitted = requests.pop(key)
            if status != 'COMPLETED':
                failed.append(dict(player=player, city=city, contract=contract, district=district,
                                   submitted=submitted, ended=turn, status=status))

    production = defaultdict(set)
    for row in queue_rows:
        if len(row) < 4 or not row[0].isdigit():
            continue
        turn, city, item = int(row[0]), row[1], row[3]
        owned = owners.get((turn, city), ())
        if item and row[2] and len(owned) == 1 and float(row[2]) > 0:
            production[next(iter(owned)), city, turn].add(item)
    for row in failed:
        row['concurrent_production_turns'] = dict(Counter(
            item for turn in range(row['submitted'], row['ended'] + 1)
            for item in production.get((row['player'], row['city'], turn), ()) if item != row['district']))
    return failed


def prospective_layouts(log, observations, players, through):
    """Follow early mapped layouts through publication, writes and construction.

    The planning log precedes packet acceptance. Join exact Quarter cells via
    the published packet and the native value. Count actual matching district
    pairs separately from native best-site receipts. A native decision can
    use a retained request and complete without a new best-site lookup.
    """
    layouts = {}
    by_turn = defaultdict(set)
    for match in STRONG_LAYOUT.finditer(log):
        turn, player, city, district, plot, buyer, customer, target, stage = map(int, match.groups()[:9])
        existing, _, specialty = match.groups()[9:]
        if player not in players or turn > through or existing == 'true':
            continue
        key = (player, city, district, plot, buyer, customer, target, stage)
        supply = 'BASE_AND_SPECIALTY' if specialty == 'true' else 'TWO_BASE'
        layouts.setdefault(key, (turn, supply))
        by_turn[turn, player, city, district, plot].add(key)

    if not layouts:
        return {}

    quarters = {int(district): title for district, title in QUARTER_TITLE.findall(log)}
    packets = defaultdict(set)
    first_foundation = {}
    completed = set()
    links = defaultdict(list)
    for key in layouts:
        player, city, district, plot, buyer, customer, target, stage = key
        links[player, city, quarters.get(district), plot, buyer, customer, target, stage].append(key)
    for row in observations:
        if row.get('turn', 0) > through or row.get('player') not in players:
            continue
        if row['kind'] == 'OPPORTUNITY' and row['offered']:
            key = tuple(row[k] for k in ('turn', 'player', 'city', 'district', 'plot'))
            for layout in by_turn.get(key, ()):
                packets[(row['version'], *key[1:], row['bidQ8'])].add(layout)
        elif row['kind'] == 'FOUNDATION' and row.get('foundationDateKnown'):
            cell = tuple(row[k] for k in ('player', 'city', 'district', 'plot'))
            turn = row.get('foundationTurn', row['turn'])
            first_foundation[cell] = min(turn, first_foundation.get(cell, turn))
        elif (row['kind'] == 'RELATION' and row.get('role') == 'customer' and row.get('present')
              and row.get('quarterComplete') and row.get('neighbourComplete')):
            relation = tuple(row.get(k) for k in ('player', 'city', 'quarter', 'quarterPlot', 'neighbourCity',
                                                   'neighbourDistrict', 'neighbourPlot', 'stage'))
            for key in links.get(relation, ()):
                other_foundation = row.get('neighbourFoundationTurn')
                quarter_foundation = row.get('quarterFoundationTurn')
                if (other_foundation is not None and quarter_foundation is not None
                        and layouts[key][0] <= min(other_foundation, quarter_foundation)):
                    completed.add(key)

    outcomes = {'WRITE': set(), 'BEST': set()}
    for match in QUARTER_RECEIPT.finditer(log):
        kind, payload = match.groups()
        row = dict(field.split('=', 1) for field in payload.split('\t') if '=' in field)
        if row['eligible'] == '1':
            key = tuple(int(row[k]) for k in ('version', 'player', 'city', 'district', 'plot', 'result'))
            outcomes[kind].update(packets.get(key, ()))
    publish = set().union(*packets.values())
    result = defaultdict(Counter)
    for key, (first, supply) in layouts.items():
        quarter = quarters.get(key[2], str(key[2]))
        group = result[f'{quarter}:{supply}']
        group['layouts'] += 1
        group['published'] += key in publish
        group['native_score_write'] += key in outcomes['WRITE']
        group['native_best'] += key in outcomes['BEST']
        group['quarter_founded'] += first <= first_foundation.get(key[:4], -1)
        group['completed_pair'] += key in completed
    return {key: dict(counts) for key, counts in result.items()}


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
        if row.get('turn', 0) > through:
            continue
        if row['kind'] == 'FOUNDATION' and row.get('foundationDateKnown'):
            foundations[row['plot']].append((row['turn'], row['player'], row.get('city'), row['district']))
        if row.get('player') not in original_ai:
            continue
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
    lost, lost_to_foreign_build = set(), set()
    for identity, groups in options.items():
        pid, order, _, qplot, cplot = identity
        plot = cplot if order == 'quarterFirst' else qplot
        if identity in realized:
            continue
        first_seen = min(groups.values())
        for turn, owner, city, district in foundations[plot]:
            if turn < first_seen:
                continue
            if owner != pid:
                lost_to_foreign_build.add(identity)
                lost.add(identity)
            elif not any(district == group[-1] and (city is None or city == group[-2]) and seen <= turn
                         for group, seen in groups.items()):
                lost.add(identity)

    def by_order_and_quarter(items):
        return dict(Counter(f'{order}:{quarter}' for _, order, quarter, *_ in items))

    counts = dict(opportunities=by_order_and_quarter(options), completed_opportunities=by_order_and_quarter(realized),
                  district_opportunities=by_order_and_quarter(opportunities_by_district),
                  completed_district_opportunities=by_order_and_quarter(realized_by_district),
                  lost_to_other_foundations=by_order_and_quarter(lost),
                  lost_to_foreign_foundations=by_order_and_quarter(lost_to_foreign_build),
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
    build_log, queue_log = root / 'AI_CityBuild.csv', root / 'City_BuildQueue.csv'
    failed_requests = None
    if build_log.is_file() and queue_log.is_file():
        types = {r['districtType'] for r in observations if r['kind'] == 'MAPPING' and r['role'] == 'customer'}
        types.update(f'DISTRICT_CSC_{title}_QUARTER' for _, title in QUARTER_TITLE.findall(log))
        with build_log.open(encoding='utf-8-sig', newline='') as builds, queue_log.open(encoding='utf-8-sig', newline='') as queue:
            failed_requests = failed_district_requests(csv.reader(builds, skipinitialspace=True),
                csv.reader(queue, skipinitialspace=True), players, types, through)
    return dict(counts=counts, timing=timing['publisher_wall'],
                native_managed_timing=timing['native_managed_cell_wall'],
                endpoint_suppliers=dict(supply), supplier_losses=dict(supplier_losses),
                supplier_history=supplier_history(observations, players, through),
                prospective_layouts=prospective_layouts(log, observations, players, through),
                bid_competition=bid_competition(log, observations, players, through),
                failed_district_requests=failed_requests,
                wonder_connections=wonder_connections(log, observations, players, through))


if __name__ == '__main__':
    options = argparse.ArgumentParser(description=__doc__)
    options.add_argument('run', type=Path, nargs='+')
    args = options.parse_args()
    print(json.dumps({str(run): run_result(run) for run in args.run}, indent=2))
