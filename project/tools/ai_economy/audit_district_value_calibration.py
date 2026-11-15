"""Read-only calibration audit of archived district observations.

This is an offline report generator, never live policy. Native foundation
samples are selected/built investments; Quarter publications include losing
offers and repeat over turns. Keep those cohorts, placement clocks and the
prospective Mill rating separate so the output cannot imply a universal score
multiplier. Native values are Q8 utility, divided by 256 only for presentation.
"""

import argparse
from collections import defaultdict
import hashlib
import importlib.util
import json
from pathlib import Path
import statistics
import sqlite3


YIELDS = {
    'DISTRICT_CAMPUS': 'YIELD_SCIENCE',
    'DISTRICT_COMMERCIAL_HUB': 'YIELD_GOLD',
    'DISTRICT_HARBOR': 'YIELD_GOLD',
    'DISTRICT_HOLY_SITE': 'YIELD_FAITH',
    'DISTRICT_INDUSTRIAL_ZONE': 'YIELD_PRODUCTION',
    'DISTRICT_THEATER': 'YIELD_CULTURE',
}


def stats(values):
    return dict(n=len(values), median=statistics.median(values) if values else None,
                minimum=min(values) if values else None,
                maximum=max(values) if values else None)


def period(turn):
    return '001-075' if turn <= 75 else '076-150' if turn <= 150 else '151-250'


def fields(line, marker):
    return dict(token.split('=', 1) for token in line.split(marker, 1)[1].split()
                if '=' in token)


def read(path, inputs):
    data = path.read_bytes()
    inputs.append(dict(path=str(path), sha256=hashlib.sha256(data).hexdigest()))
    return json.loads(data)


def native_audit(control_root, inputs):
    groups = defaultdict(lambda: defaultdict(list))
    counts = {}
    for arm in ('continents250-01', 'pangaea250-01', 'fractal250-01'):
        rows = read(control_root / arm / 'planning-results.json', inputs)['constructions']
        rows = [r for r in rows if r['kind'] == 'FOUNDATION' and 1 <= r['player'] <= 5]
        counts[arm] = len(rows)
        for row in rows:
            district = row['districtType']
            if district not in YIELDS:
                continue
            ui = row.get('uiAdjacency') or {}
            if not ui.get('available') or not ui.get('footprintMatches'):
                continue
            adjacency = ui[YIELDS[district]]
            # Old records have an invalid raw foundationTurn. The observed
            # UI-event turn is the qualified placement clock in these controls.
            key = (district, adjacency, period(row['turn']))
            group = groups[key]
            group['foundations'].append(row['turn'])
            for source in ('nativeChoice', 'nativePlacement'):
                native = row.get(source) or {}
                if native.get('scoreStatus') == 'read' and isinstance(native.get('totalQ8'), int):
                    group[source].append(native['totalQ8'] / 256)
            if row.get('nativeChoiceAgeTurns') is not None:
                group['choiceAgeTurns'].append(row['nativeChoiceAgeTurns'])
    return dict(foundations_by_arm=counts, strata=[
        dict(district=k[0], adjacency=k[1], period=k[2], foundations=len(v['foundations']),
             choice=stats(v['nativeChoice']), before_placement=stats(v['nativePlacement']),
             choice_age_turns=stats(v['choiceAgeTurns']))
        for k, v in sorted(groups.items())])


def quarter_audit(run, inputs):
    path = run / 'Lua.log'
    inputs.append(dict(path=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    groups = defaultdict(list)
    foundations = []
    with path.open(encoding='utf-8', errors='replace') as source:
        for line in source:
            if 'CSC_PLANNING_OPPORTUNITY\t' in line:
                row = fields(line, 'CSC_PLANNING_OPPORTUNITY\t')
                if (not 1 <= int(row['player']) <= 5 or row.get('offered') != 'true'
                        or int(row.get('bidQ8', 0)) <= 0):
                    continue
                adjacency = float(row['upper'])
                band = '2to3' if 2 <= adjacency < 3 else '3plus' if adjacency >= 3 else 'below2'
                groups[(band, period(int(row['turn'])))].append(int(row['bidQ8']) / 256)
            elif 'CSC_QUARTER_WATCH_SITE' in line:
                row = fields(line, 'CSC_QUARTER_WATCH_SITE')
                if row.get('event') != 'foundation' or not 1 <= int(row['player']) <= 5:
                    continue
                foundations.append(dict(player=int(row['player']), city=int(row['city']),
                    plot=int(row['plot']), turn=int(row['turn']), district=int(row['district']),
                    base=int(row['base']), spec=int(row['spec']),
                    initial_eligible_production=float(row['eligibleProduction']),
                    initial_eligible_gold=float(row['eligibleGold']),
                    prospective_mill_rating=float(row['millForecastTotal']),
                    published_bid_utility=int(row['bidQ8']) / 256))
    return dict(published_bid_strata=[dict(band=k[0], period=k[1], scores=stats(v))
                                     for k, v in sorted(groups.items())],
                foundations=foundations)


def historical_components(root, inputs):
    results = []
    for turn in (155, 160, 180, 200):
        doc = read(root / f'economic-components-{turn}.json', inputs)
        row = next(r for r in doc['records'] if r['plot'] == 2992)
        quote, site = row['quote'], row['site']
        assert sum(s['valueQ8'] for s in quote['streams']) == quote['valueQ8'], 'Incomplete component ledger'
        results.append(dict(turn=turn, production=row['production'],
            starting_adjacency=row['geometry']['base'], prospective_mill_rating=row['geometry']['upper'],
            quarter_ready=site['quarterReady'], economic_utility=quote['valueQ8'] / 256,
            producer_ready=quote['byBuilding'].get('393221:BUILDING_CSC_BAKERS_WATER_MILL'),
            streams=[dict(id=s['id'], yield_type=s['yield'], ready=s['ready'],
                          amount=s['amount'], utility=s['valueQ8']/256) for s in quote['streams']]))
    return results


def native_config(control_root, inputs):
    path = control_root / 'continents250-01/DebugGameplay.sqlite'
    inputs.append(dict(path=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    with sqlite3.connect(path.as_uri() + '?mode=ro', uri=True) as db:
        discount = db.execute("SELECT Value FROM GlobalParameters WHERE Name='AI_DISCOUNT_RATE'").fetchone()[0]
        speeds = dict(db.execute('SELECT GameSpeedType,CostMultiplier FROM GameSpeeds'))
    return dict(base_discount=float(discount), game_speed_cost_multipliers=speeds,
        ordinary_horizon_base=100, online_ordinary_horizon=50, online_discount=4,
        ordinary_horizon_consumer_rva='3e2aa0', initializer_rva='49c7c0',
        speed_linear_rva='36f620', speed_inverse_rva='36f7b0',
        player_discount_reader_rva='4b38f0')


def binary_audit(before, after):
    module_path = Path(__file__).resolve().parents[1] / 'native_ai/late_placement/audit_xp2_hotfix.py'
    spec = importlib.util.spec_from_file_location('xp2_audit', module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    images = (module.Image(before, module.BASELINE_SHA), module.Image(after, module.HOTFIX_SHA))
    assert images[0].section('.text') == images[1].section('.text'), 'Native code changed'
    constants = {}
    for rva in (0x9d62d8, 0x9d62e8, 0x9c8978, 0x9d18b0, 0xa0b7b8, 0x9c1b78):
        assert images[0].at(rva, 4) == images[1].at(rva, 4), f'Constant changed: {rva:x}'
        constants[f'{rva:x}'] = images[0].at(rva, 4).hex()
    return dict(reference_sha256=images[0].sha256, current_sha256=images[1].sha256,
        text_identical=True, text_sha256=hashlib.sha256(images[0].section('.text')).hexdigest(),
        identical_constant_bytes_by_rva=constants)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for arg in ('control-root', 'csc-run', 'components-dir', 'reference-dll', 'current-dll', 'out'):
        parser.add_argument('--' + arg, type=Path, required=True)
    args = parser.parse_args()
    inputs = []
    result = dict(scope='Stock AI; Online; CL/R2/Suk controls; original AI players 1-5',
        cohorts='Native built foundations versus repeated published Quarter offers; no global ratio fit',
        baseline=native_audit(args.control_root, inputs),
        quarters=quarter_audit(args.csc_run, inputs),
        historical_components=historical_components(args.components_dir, inputs),
        native_binary=binary_audit(args.reference_dll, args.current_dll),
        native_configuration=native_config(args.control_root, inputs), inputs=inputs)
    args.out.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(native_foundations=sum(result['baseline']['foundations_by_arm'].values()),
        quarter_foundations=len(result['quarters']['foundations']),
        quarter_positive_publications=sum(r['scores']['n'] for r in result['quarters']['published_bid_strata']),
        output=str(args.out))))


if __name__ == '__main__':
    main()
