"""Compare completed, matched normal games in the Builder scheduler matrix."""
import argparse
import csv
from pathlib import Path
import statistics

from driver import read, write_json
from full_game_observation import archive_censuses
from full_game_results import economy, summarize
from material_development_summary import (SOURCE_FIELDS, analyse_run, binary_identities,
                                          publisher_timing)
from material_scheduler_campaign import ARMS, PUBLISHER, load, observed_boundary
from planning_results import analyse as placement_results
from processing_time_summary import summarise as timing_summary
from storekeeper_runtime import audit as audit_storekeeper


def pooled(results):
    totals = {}
    for arm in ARMS:
        runs = [seed[arm] for seed in results.values()]
        seats = sum(run['original_ai_seats'] for run in runs)
        combined = {}
        for key in runs[0]['measures']:
            values = [run['measures'][key] for run in runs]
            if any(value is None for value in values):
                combined[key] = None
            elif key.endswith('_per_original_seat'):
                combined[key] = sum(v * run['original_ai_seats'] for v, run in zip(values, runs)) / seats
            elif key.endswith('_max'):
                combined[key] = max(values)
            elif key.endswith('_mean'):
                clocks = [run['guidance_timing']['turns'] for run in runs]
                combined[key] = sum(value * count for value, count in zip(values, clocks)) / sum(clocks)
            elif key != 'median_turns_to_restore':
                combined[key] = sum(values)
        delays = [episode['turns_to_restore'] for run in runs
                  for episode in run['material']['buyer_readiness']['recoveries'] if episode['restored'] is not None]
        combined['median_turns_to_restore'] = statistics.median(delays) if delays else None
        for group in runs[0]['material']['buyer_readiness']['counts']:
            total = combined[f'eligible_buyers:{group}']
            combined[f'on_time_share:{group}'] = combined[f'on_time_buyers:{group}'] / total if total else None
        totals[arm] = combined
    return totals


def run_outcomes(run, endpoint, *, terminal=True):
    source = load(run / 'source.json')
    if terminal:
        result = load(run / 'result.json')
        if not result['closed'] or result['reached'] != endpoint:
            raise ValueError(f'No verified endpoint at turn {endpoint} in {run}')
        storekeeper = result['storekeeper']
        timing = publisher_timing(run)
    else:
        log = read(run / 'Lua.log')
        if not (run / f'full-census-{endpoint}.json').exists():
            archive_censuses(log, run)
        storekeeper = audit_storekeeper(log, set(source['original_ai']), before_turn=endpoint,
                                      expected_turns=range(2, endpoint))
        sample = timing_summary(log, last=endpoint)
        timing = dict(sample['publisher_wall'], failed_publications=sample['failed_attempts'])
    material = analyse_run(run, endpoint, require_finished=terminal)
    readiness = material['buyer_readiness']
    if not readiness['verified']:
        raise ValueError(f'Incomplete supplier buyer census in {run}: {readiness["missing_turns"]}')
    placement = placement_results(run, through=None if terminal else endpoint)
    seats = len(source['original_ai'])
    trends = []
    for turn in range(25, endpoint + 1, 25):
        census = run / f'full-census-{turn}.json'
        yields, by_player = economy(census)
        trends.append(dict(turn=turn, quarters=summarize(census), economy=yields, by_player=by_player))

    measures = {}
    for group, counts in material['counts'].items():
        for name, count in counts.items():
            if name != 'working_share':
                measures[f'{name}:{group}'] = count
    for group, counts in readiness['counts'].items():
        for name, count in counts.items():
            if name != 'rate':
                measures[f'{name}_buyers:{group}'] = count
    recoveries = readiness['recoveries']
    repaired = [r['turns_to_restore'] for r in recoveries if r['restored'] is not None]
    measures.update(supplier_outages=len(recoveries), supplier_restorations=len(repaired),
                    median_turns_to_restore=statistics.median(repaired) if repaired else None,
                    unresolved_outages=sum(r['restored'] is None and r['unavailable'] is None for r in recoveries),
                    buyer_became_unavailable=sum(r['unavailable'] is not None for r in recoveries),
                    prepared_while_building=sum(bool(r['work']) for r in readiness['prepared_during_construction']),
                    working_supply_losses=placement['working_supplier_loss_events'],
                    storekeeper_chains=len(storekeeper['active_turns']),
                    storekeeper_active_turns=sum(row['turns'] for row in storekeeper['active_turns']),
                    storekeeper_sampled_turns=len(storekeeper['sampled_turns']))
    for family, counts in trends[-1]['quarters'].items():
        for metric in ('placed', 'complete', 'base', 'spec', 'both', 'base_improved', 'spec_improved',
                       'both_improved', 'customer_any_completed', 'base_improved_customer2_working',
                       'stage2_physical',
                       *(f'{term}{stage}{suffix}' for stage in (2, 3, 4) for term, suffix in
                         (('producer', '_working'), ('mapped_customer', '_with_working_building'),
                          ('service', '_property')))):
            measures[f'{metric}:{family}'] = counts[metric]
        for metric in ('foundations', 'at_least3', 'at_least4'):
            measures[f'{metric}:{family}'] = placement['quarter_quality_at_foundation'][family][metric]
    for key in ('production', 'gross_gold', 'net_gold', 'food', 'population', 'cities'):
        measures[f'{key}_per_original_seat'] = trends[-1]['economy'][key] / seats
    measures.update({name: material['worker_followthrough'][scope]['updates'] for name, scope in
                     (('worker_start_updates', 'workerStart'), ('worker_finish_updates', 'workerFinish'))})
    measures['worker_offers'] = material['worker_followthrough']['published_offers']
    measures['observed_work_after_finish_sample'] = sum(
        row['later_plot_work'] is not None for row in material['worker_followthrough']['workerFinish']['samples'])
    measures['improvement_score_writes'] = material['improvement_scoring']['score_writes']
    measures.update(publisher_ms_total=timing['total_ms'],
                    publisher_ms_mean=timing['average_ms'], publisher_ms_max=timing['max_ms'])
    return dict(measures=measures, trends=trends, placement=placement, material=material, guidance_timing=timing,
                storekeeper=storekeeper, original_ai_seats=seats)


def compare(root):
    plan = load(root / 'plan.json')
    boundaries = {seed['map']: {arm: observed_boundary(root / f'{seed["map"].lower()}-{arm}', plan['endpoint'])
                                for arm in ARMS} for seed in plan['seeds']}
    horizon = min(v for arms in boundaries.values() for v in arms.values()) // 25 * 25
    if horizon < 25:
        raise ValueError('One or more games ended before the first common census')
    results, differences, later = {}, {}, {}
    rows = []
    for seed in plan['seeds']:
        label = seed['map']
        results[label] = {}
        identity = None
        base_files = None
        for arm in ARMS:
            run = root / f'{label.lower()}-{arm}'
            source = load(run / 'source.json')
            setup = load(run / 'protocol.json')
            package = load(run / 'packages.json')
            installed = {Path(record['install']).name: record['files'] for record in package.values()}
            files = installed['CSC Bakers Development Mod']
            current = ({name: source[name] for name in SOURCE_FIELDS},
                       binary_identities(run), setup.get('extra_mods'),
                       installed['CSC Bakers Development CE'])
            if identity is None:
                identity = current
                base_files = files
            elif identity != current:
                raise ValueError(f'Opening map, units, leaders or CE/optional mods differ within {label}')
            expected = {str(PUBLISHER)} if arm == ARMS[2] else set()
            if arm == 'no-tuning':
                expected = {str(PUBLISHER), 'Civ Supply Chains.modinfo'}
            changed = {name for name in base_files if files.get(name) != base_files[name]}
            if files.keys() != base_files.keys() or changed != expected:
                raise ValueError(f'Unexpected CSC package changes in {run}')
            if ((setup['map'], setup['map_seed'], setup['game_seed']) != (label, seed['map_seed'], seed['game_seed'])
                    or setup['untuned'] != (arm == 'no-tuning')
                    or setup['external_policy'] or setup['gameplay_interventions']):
                raise ValueError(f'Unexpected setup in {run}')
            if arm == 'no-tuning' and 'CSC_FULL_RUN_CONTROL_CATALOGUE' not in read(run / 'full-game-preflight.txt'):
                raise ValueError(f'Untuned material observation did not initialise its local catalogue in {run}')
            outcome = run_outcomes(run, horizon, terminal=horizon == plan['endpoint'])
            measures = outcome['measures']
            if arm != ARMS[2] and measures['worker_offers']:
                raise ValueError(f'Unexpected scheduling offers in {run}')
            if measures['worker_start_updates']:
                raise ValueError(f'Unexpected broad scheduler in {run}')
            results[label][arm] = outcome
            rows.append(dict(map=label, arm=arm, comparison_turn=horizon,
                             verified_boundary=boundaries[label][arm], **measures))
            if (later_turn := min(boundaries[label].values()) // 25 * 25) > horizon:
                later.setdefault(label, {'turn': later_turn, 'results': {}})['results'][arm] = run_outcomes(
                    run, later_turn, terminal=later_turn == plan['endpoint'])
        difference = {}
        for case, a, b in (('tuning_effect', ARMS[0], 'no-tuning'), ('scheduler_effect', ARMS[2], ARMS[0])):
            first, second = (results[label][arm]['measures'] for arm in (a, b))
            difference[case] = {key: value - second[key] for key, value in first.items()
                                if value is not None and second[key] is not None}
        differences[label] = difference

    write_json(root / 'outcomes.json', dict(plan=plan, comparison_turn=horizon, verified_boundaries=boundaries,
                                          results=results, pooled=pooled(results),
                                          paired_differences=differences, later_matched= later))
    with (root / 'outcomes.csv').open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return rows


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    compare(parser.parse_args().root.resolve(strict=True))
