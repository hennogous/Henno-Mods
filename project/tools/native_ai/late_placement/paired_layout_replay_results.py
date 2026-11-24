"""Trace a specified pair through the two arms of a matched short replay."""

import argparse
from collections import Counter, defaultdict
import csv
import json
from pathlib import Path
import re

from anchored_connection_results import CUSTOMER_RECEIPT, DISTRICT_TITLE
from planning_results import parse


PLAN = re.compile(r'CSC_AI_PROSPECTIVE_CONNECTION ([^\r\n]+)')


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def trace_arm(folder, targets, player, names, width=None, city_labels=None):
    if not all(read_json(folder / name)['verified'] for name in ('complete.json', 'session-closed.json')):
        raise ValueError(f'Incomplete replay arm {folder}')
    log = (folder / 'Lua.log').read_text(encoding='utf-8-sig')
    wanted = set((city, plot) for city, _, plot in targets)
    stages = defaultdict(list)
    proposals = []
    for payload in PLAN.findall(log):
        row = {key: int(value) for key, value in (word.split('=', 1) for word in payload.split())}
        if row['player'] == player and ((row['quarterCity'], row['quarterPlot']) in wanted
                                      or (row['customerCity'], row['customerPlot']) in wanted):
            proposals.append(row)
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
    for row in parse(log, 'CSC_PLANNING_'):
        if row['kind'] in ('FOUNDATION', 'COMPLETION') and row.get('player') == player:
            if (row['city'], row['plot']) in wanted:
                stages['construction'].append(row)
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
    return dict(proposals=proposals, **stages, services=read_json(folder / 'observed-services.json'))


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
