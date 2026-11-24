"""Trace a specified pair through the two arms of a matched short replay."""

import argparse
from collections import Counter, defaultdict
import csv
import json
from pathlib import Path
import re

from anchored_connection_results import (
    CUSTOMER_RECEIPT, DISTRICT_TITLE, PROSPECTIVE_SUBSTITUTE,
    customer_land_purchases, foundation_order, supplier_history,
)
from planning_results import parse


PLAN = re.compile(r'CSC_AI_PROSPECTIVE_CONNECTION ([^\r\n]+)')


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def trace_arm(folder, targets, player, names, width=None, city_labels=None):
    completion = read_json(folder / 'complete.json')
    if not (completion['verified'] and read_json(folder / 'session-closed.json')['verified']):
        raise ValueError(f'Incomplete replay arm {folder}')
    log = (folder / 'Lua.log').read_text(encoding='utf-8-sig')
    wanted = set((city, plot) for city, _, plot in targets)
    stages = defaultdict(list)
    for name, pattern in (('proposals', PLAN), ('observed_substitutes', PROSPECTIVE_SUBSTITUTE)):
        stages[name] = []
        related = 'related_' + name
        stages[related] = []
        for payload in pattern.findall(log):
            row = {key: int(value) for key, value in (word.split('=', 1) for word in payload.split())}
            if row['player'] != player:
                continue
            quarter = row['quarterCity'], row['quarter'], row['quarterPlot']
            customer = row['customerCity'], row['customer'], row['customerPlot']
            if quarter == targets[0] and customer == targets[1]:
                stages[name].append(row)
            elif (quarter[0], quarter[2]) in wanted or (customer[0], customer[2]) in wanted:
                # A different district or an alternate on either footprint
                # is useful for diagnosis, but does not count as this offer.
                stages[related].append(row)
    # The native scout records both fresh net and final-cache reads. Use an
    # eligible cache value preceding the winner to calculate a score gap.
    # An unpriced cell or a later read supplies no counterfactual result.
    last_cache = {}
    for match in CUSTOMER_RECEIPT.finditer(log):
        row = json.loads(match[2])
        if row['player'] != player:
            continue
        observed = int(re.search(r'observedTurn=(\d+)', match[0])[1])
        ordinal = int(match[1])
        city, plot, district = row['city'], row['plot'], row['district']
        key = row['generation'], row['version'], city, district, plot
        if row['k'] == 'cache' and row['eligible'] == 1:
            last_cache[key] = ordinal, row['result']
        if row['k'] in ('net', 'final') and row['base'] != row['result'] and (city, plot) in wanted:
            stages['value_changes'].append(dict(observed_turn=observed, plot=plot, city=city,
                district=names.get(district, str(district)), stage=row['k'],
                before_q8=row['base'], after_q8=row['result'], eligible=row['eligible']))
        if row['k'] == 'best' and row['eligible'] == 1:
            for target_city, target_type, target_plot in targets:
                if city != target_city:
                    continue
                score = last_cache.get((row['generation'], row['version'], city, target_type, target_plot))
                target_score = score[1] if score and score[0] < ordinal else None
                stages['comparisons'].append(dict(observed_turn=observed, version=row['version'],
                    target_district=names.get(target_type, str(target_type)), target_plot=target_plot,
                    target_q8=target_score, winner=names.get(district, str(district)), winner_plot=plot,
                    winner_q8=row['result'], reported_reservation_id=row['reservationId'],
                    target_selected=(district, plot) == (target_type, target_plot),
                    recorded_gap_q8=row['result']-target_score if target_score is not None else None))
    observations = parse(log, 'CSC_PLANNING_')
    native_ids = defaultdict(set)
    for row in observations:
        if row['kind'] not in ('FOUNDATION', 'COMPLETION', 'FIRST_OBSERVED') or row.get('player') != player:
            continue
        if (row['city'], row['plot']) in wanted and row['kind'] in ('FOUNDATION', 'COMPLETION'):
            stages['construction'].append(row)
        target = row['city'], row['district'], row['plot']
        if target in targets and row.get('districtID') is not None:
            native_ids[target].add(row['districtID'])
    if city_labels:
        traces = {'City '+label: city for city, label in city_labels.items()}
        orders = {(city_labels[city], names[district]) for city, district, _ in targets if city in city_labels}
        with (folder / 'AI_Behavior_Trees.csv').open(encoding='utf-8-sig', newline='') as stream:
            for row in csv.reader(stream, skipinitialspace=True):
                if len(row) < 7 or row[1] != str(player) or row[2] not in traces or row[3:6] != [
                        'Build City District', 'SUCCESS', 'Reserve Plot']:
                    continue
                reserve = re.fullmatch(r'Reserving plot (\d+) (\d+)', row[6])
                if reserve:
                    plot = int(reserve[1])+int(reserve[2])*width
                    city = traces[row[2]]
                    if (city, plot) in wanted:
                        stages['successful_reservations'].append(dict(turn=int(row[0]), city=city, plot=plot))
        with (folder / 'AI_CityBuild.csv').open(encoding='utf-8-sig', newline='') as stream:
            for row in csv.reader(stream, skipinitialspace=True):
                if (len(row) >= 9 and row[1] == str(player) and (row[2], row[8]) in orders
                        and row[4].startswith('CONTRACT ')):
                    stages['city_type_contracts'].append(dict(turn=int(row[0]), city=row[2],
                        contract=row[4], status=row[5], district=row[8]))
    services = read_json(folder / 'observed-services.json')
    quarter_ids, customer_ids = (native_ids[target] for target in targets)
    # GameEffects names a live district object, not a tile. Join the observed
    # owner and both native IDs to the physical ledger before crediting a pair.
    pair_services = [link for link in services['chains'] if link['player'] == player
                     and link['source'] in quarter_ids and link['customer'] in customer_ids]

    quarter_city, quarter_type, quarter_plot = targets[0]
    customer_city, customer_type, customer_plot = targets[1]
    quarter = names.get(quarter_type, '').removeprefix('DISTRICT_CSC_').removesuffix('_QUARTER')
    relations = [row for row in observations if row['kind'] == 'RELATION'
                 and row['player'] == player and row['city'] == quarter_city
                 and row['quarter'] == quarter and row['quarterPlot'] == quarter_plot
                 and (row['neighbourCity'], row['neighbourDistrict'], row['neighbourPlot']) == targets[1]
                 and row.get('present') and row.get('quarterComplete') and row.get('neighbourComplete')
                 and row.get('role') in ('customer', 'sales', 'goodsProvider')]
    first_link = min(relations, key=lambda row: row['turn'], default=None)
    final_turn = completion.get('turn')
    supplies = None
    land = None
    if final_turn is not None:
        material_rows = [row for row in observations if
                         (row['kind'] == 'MATERIAL_STATE' and row['quarterPlot'] == quarter_plot
                          and row['quarter'] == quarter)
                         or (row['kind'] == 'MATERIAL_WATCH_ENDED'
                             and row['identity'].startswith(f'{quarter_plot}:'))]
        if material_rows:
            supplies = supplier_history(material_rows, {player}, final_turn)
        if 'CSC_CUSTOMER_LAND_WATCH_INSTALLED' in log:
            with (folder / 'AI_Behavior_Trees.csv').open(encoding='utf-8-sig', newline='') as stream:
                audit = customer_land_purchases(log, observations, {player}, final_turn,
                                               csv.reader(stream, skipinitialspace=True))
            spending = []
            buying_city = (city_labels or {}).get(customer_city)
            for row in audit['purchases']:
                if (row['city'], row['plot']) != (customer_city, customer_plot):
                    continue
                if not any(kind == customer_type for kind, _ in row['quotes']):
                    continue
                # The base audit matches tile coordinates and player. The
                # named city resolves competing requests for the same plot.
                confirmed = [turn for turn, _, status, city in row['request_history']
                             if buying_city and city == 'City ' + buying_city and status == 'Accepted']
                spending.append(dict(row, buying_city_request_turn=max(confirmed, default=None)))
            land = dict(
                spending=spending,
                completed_on_purchased_plot=[row for row in audit['completed_partners_on_purchased_land']
                                             if (row['city'], row['district'], row['plot']) == targets[1]
                                             and (row['quarter'], row['quarter_plot']) == (quarter, quarter_plot)],
            )
    return dict(stages, services=services, exact_pair_services=pair_services, exact_pair_first_completed_link=first_link,
                exact_pair_build_order=foundation_order(first_link) if first_link is not None else None,
                quarter_materials=supplies, exact_customer_land=land)


def report(root, player, quarter, customer, city_labels=None):
    setup = read_json(root / 'matched-switch.json')
    if not setup['verified']:
        raise ValueError('The replay arms have no verified matched setup')
    source = Path(read_json(root / 'control' / 'inputs.json')['source'])
    catalogue = (source / 'loaded-district-catalogue.txt').read_text(encoding='utf-8-sig')
    names = {int(index): title for index, title in DISTRICT_TITLE.findall(catalogue)}
    types = {title: index for index, title in names.items()}
    targets = [(city, types[district], plot) for city, district, plot in (quarter, customer)]
    width = read_json(source / 'source.json')['map_signature'][0]
    return {arm: trace_arm(root / arm, targets, player, names, width, city_labels)
            for arm in ('control', 'treatment')}


def cli():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('replay', type=Path)
    parser.add_argument('--player', type=int, required=True)
    for side in ('quarter', 'customer'):
        parser.add_argument('--'+side, nargs=3, required=True, metavar=('CITY', 'DISTRICT_TYPE', 'PLOT'))
    parser.add_argument('--city-label', nargs=2, action='append', default=[], metavar=('CITY', 'LOG_LABEL'),
                        help='Verify reservations and contracts against the named city in the stock logs')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()

    def target(parts):
        city, district, plot = parts
        return int(city), district, int(plot)

    labels = {int(city): label for city, label in args.city_label}
    results = report(args.replay, args.player, target(args.quarter), target(args.customer), labels)
    with args.output.open('x', encoding='utf-8') as stream:
        json.dump(results, stream, indent=2)
        stream.write('\n')
    for side, result in results.items():
        comparisons = Counter((r['target_district'], r['target_selected']) for r in result.get('comparisons', ()))
        print(side, 'paired proposals', len(result['proposals']), 'comparisons', dict(comparisons))


if __name__ == '__main__':
    cli()
