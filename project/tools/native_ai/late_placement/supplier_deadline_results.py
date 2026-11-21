"""Measure supplier timing from two ordinary runs with the same passive census.

Survey turns are start-of-turn. Native tree actions land after that survey.
A reservation or assignment is evidence on a mapped plot. The working census
is the separate check that the plot actually gained a compatible improvement.
"""

import argparse
from bisect import bisect_right
from collections import Counter, defaultdict
import csv
import json
from pathlib import Path
import re


BUYER = re.compile(r'\bCSC_PLANNING_SUPPLIER_BUYER(_POLL)?\t(.+)')
POSITION = re.compile(r'Reserving plot (\d+) (\d+)')
PREPARATION = re.compile(r'\bCSC_AI_MATERIAL_PREPARATION\s+(.+)')


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def read_surveys(log, first, last):
    pending, surveys = defaultdict(list), {}
    for line in log:
        event = BUYER.search(line)
        if not event:
            continue
        row = dict(field.split('=', 1) for field in event[2].rstrip('\r\n').split('\t'))
        turn = int(row['turn'])
        if not first <= turn <= last:
            continue
        key = turn, row['source']
        if event[1]:
            batch = pending.pop(key, [])
            keys = {(r['player'], r['quarterPlot'], r['role']) for r in batch}
            if len(keys) != len(batch) or len(batch) != int(row['buyers']):
                raise ValueError(f'Incomplete buyer survey on {turn}')
            surveys[turn] = batch
        else:
            if 'legalPlots' not in row or 'workingPlots' not in row:
                raise ValueError('Buyer survey lacks exact supplier plots')
            pending[key].append(row)
    if pending or set(surveys) != set(range(first, last + 1)):
        raise ValueError('Incomplete survey coverage')
    return surveys


def exact_plots(row, key):
    plots = {int(value) for value in row[key + 'Plots'].split(',') if value}
    if len(plots) != int(row[key]):
        raise ValueError(f'Malformed {key} plot list')
    return plots


def with_early_preparation(surveys, log):
    """Add exact pre-unlock eligibility witnessed by accepted policy packets.

    A preparation offer requires a legal plot and a missing first supplier.
    Keep this treatment-only view alongside the common queue-eligible clock.
    The common view remains the direct comparison against the older policy.
    """
    offers = defaultdict(set)
    for line in log:
        event = PREPARATION.search(line)
        if event:
            row = dict(field.split('=', 1) for field in event[1].split())
            if int(row['deltaQ8']) > 0:
                key = int(row['turn']), row['player'], row['quarter'], row['class']
                offers[key].add(int(row['plot']))
    augmented = {}
    for turn, batch in surveys.items():
        augmented[turn] = []
        for row in batch:
            key = turn, row['player'], row['quarterPlot'], row['role']
            plots = offers.get(key)
            if plots and not exact_plots(row, 'legal') and not row.get('constructing') and row['buyerReady']!='true':
                row = dict(row, legal=str(len(plots)), legalPlots=','.join(map(str, sorted(plots))))
            augmented[turn].append(row)
    return augmented


def read_tree_events(log, players, width, last):
    current, events = {}, defaultdict(list)
    for row in csv.reader(log, skipinitialspace=True):
        if len(row) < 7 or row[1] not in players or row[3] != 'Build City Improvement':
            continue
        turn, player, city, _, state, step, detail = row[:7]
        turn = int(turn)
        if turn >= last:
            continue
        key = player, city
        if step == 'Reserve Plot' and state == 'SUCCESS':
            match = POSITION.fullmatch(detail.strip())
            current.pop(key, None)
            if match:
                plot = int(match[1]) + width * int(match[2])
                current[key] = plot, turn
                events[player, plot].append((turn, 'reserved', turn))
        elif ((step == 'Find Available Unit' and state == 'SUCCESS')
              or (step == 'Move Unit' and state in ('RUNNING', 'SUCCESS'))):
            reservation = current.get(key)
            if reservation is not None:
                plot, reserved = reservation
                events[player, plot].append((turn, 'assigned', reserved))
    return events


def supplier_cases(surveys, events, players, window):
    final = max(surveys)
    timelines = defaultdict(dict)
    for turn, batch in sorted(surveys.items()):
        for row in batch:
            if row['player'] in players:
                timelines[row['player'], int(row['quarterPlot']), row['quarter'], row['role']][turn] = row
    outcomes = []
    for (player, quarter_plot, quarter, role), timeline in sorted(timelines.items()):
        opening = next((t for t, row in timeline.items() if row['buyerReady']=='true'), None)
        if opening is None:
            continue
        eligible = next((t for t, row in timeline.items() if exact_plots(row, 'legal')), None)
        deadline = opening + window
        case = dict(player=int(player), quarter_plot=quarter_plot, quarter=quarter, role=role,
                    first_eligible=eligible, opening=opening)
        outcomes.append(case)
        if deadline > final:
            case['cohort'] = 'late_opening'
        elif eligible is None or eligible > deadline:
            case['cohort'] = 'no_legal_supplier_by_deadline'
        elif deadline not in timeline or timeline[deadline]['buyerReady']!='true':
            case['cohort'] = 'interrupted_at_deadline'
        elif exact_plots(timeline[eligible], 'working'):
            case['cohort'] = 'already_working_at_preparation'
        else:
            case['cohort'] = 'needed_work_at_preparation'
            first = {}
            for turn, row in timeline.items():
                if not eligible <= turn <= deadline:
                    continue
                if exact_plots(row, 'working'):
                    first.setdefault('working', turn)
                for plot in exact_plots(row, 'legal'):
                    for event_turn, event, reserved in events.get((player, plot), ()):
                        if event_turn == turn and event_turn < deadline:
                            first.setdefault(event, event_turn + 1)
                            # A Builder can pick up work already reserved
                            # when the buyer becomes eligible. Carry the
                            # observed reservation with that assignment.
                            first['reserved'] = min(first.get('reserved', final+1), reserved+1)
            case['first_observed'] = first
            # A chain can briefly have an improvement and then lose it. Use
            # the actual state at both survey milestones for working supply.
            case['by_opening'] = {event: first.get(event, final + 1) <= opening
                                  for event in ('reserved', 'assigned')}
            case['by_deadline'] = {event: first.get(event, final + 1) <= deadline
                                   for event in ('reserved', 'assigned')}
            case['by_opening']['working'] = bool(exact_plots(timeline[opening], 'working'))
            case['by_deadline']['working'] = bool(exact_plots(timeline[deadline], 'working'))
            case['by_opening']['ever_worked'] = first.get('working', final + 1) <= opening
            case['by_deadline']['ever_worked'] = first.get('working', final + 1) <= deadline
        if eligible is not None and opening < eligible <= deadline <= final:
            # Title transfer or an improvement unlock after the buyer opens
            # can still leave an actionable case before +10. Keep its shorter
            # window visible without silently excluding it from the count.
            case['eligible_after_opening'] = True
    return outcomes


def counts(cases):
    summary = {}
    for key in ('base', 'specialty'):
        role = [case for case in cases if case['role'] == key]
        group = dict(Counter(case['cohort'] for case in role))
        needed = [case for case in role if case['cohort'] == 'needed_work_at_preparation']
        late = [case for case in role if case.get('eligible_after_opening')]
        group['eligible_after_opening'] = dict(Counter(case['cohort'] for case in late))
        group['eligible_after_opening']['working_by_deadline_after_needed_work'] = sum(
            case['by_deadline']['working'] for case in late if case['cohort'] == 'needed_work_at_preparation')
        for stage in ('by_opening', 'by_deadline'):
            group[stage] = {step: sum(case[stage][step] for case in needed)
                            for step in ('reserved', 'assigned', 'working', 'ever_worked')}
        summary[key] = group
    return summary


def recoveries(surveys, players):
    """Keep outages only while the buyer and a legal adjacent job persist."""
    episodes, active, previous = [], {}, {}
    for turn, batch in sorted(surveys.items()):
        current = {}
        for row in batch:
            if row['player'] not in players or row['buyerReady'] != 'true' or int(row['legal']) <= 0:
                continue
            key = int(row['player']), int(row['quarterPlot']), row['quarter'], row['role']
            working = bool(exact_plots(row, 'working'))
            current[key] = working
            if not working and previous.get(key):
                player, plot, quarter, role = key
                record = dict(player=player, quarter_plot=plot, quarter=quarter, role=role, lost=turn)
                active[key] = record
                episodes.append(record)
        for key, record in list(active.items()):
            if current.get(key):
                record['restored'] = turn
                record['turns_to_restore'] = turn - record['lost']
                del active[key]
            elif key not in current:
                record['interrupted'] = turn
                del active[key]
        previous = current
    return episodes


def production_activity(path, players, last):
    """Attribute physical queue completions through the stock city-turn census.

    Requests can close in more than one city's contract log. Only count
    a completed production row or an actual purchase, once per recorded action.
    The queue census has city names only. Expose unresolved owner cases.
    """
    owners = defaultdict(lambda: defaultdict(set))
    purchases = Counter()
    with (path/'AI_CityBuild.csv').open(encoding='utf-8-sig', errors='replace', newline='') as log:
        for row in csv.reader(log, skipinitialspace=True):
            if len(row) < 7 or not row[0].isdigit() or int(row[0]) > last:
                continue
            turn, player, city = int(row[0]), row[1], row[2]
            if city == 'PURCHASE' and player in players:
                purchases[row[5]] += 1
            elif city != 'PURCHASE' and player.isdigit():
                owners[city][turn].add(player)
    owner_turns = {city: sorted(history) for city, history in owners.items()}
    trained, ambiguous = Counter(), Counter()
    with (path/'City_BuildQueue.csv').open(encoding='utf-8-sig', errors='replace', newline='') as log:
        for row in csv.reader(log, skipinitialspace=True):
            if len(row) < 7 or not row[0].isdigit() or not row[4] or not row[5]:
                continue
            turn, city, _, item, progress, cost, _ = row[:7]
            turn = int(turn)
            if turn > last or not item or float(cost) <= 0 or float(progress) < float(cost):
                continue
            # A quiet turn need not emit a city decision. Carry the latest
            # known owner forward, and expose same-turn name collisions.
            observations = owner_turns.get(city, ())
            index = bisect_right(observations, turn) - 1
            candidates = owners[city][observations[index]] if index >= 0 else set()
            if not candidates or len(candidates) != 1:
                ambiguous[item] += 1
            elif candidates <= players:
                trained[item] += 1
    return {'completed': trained, 'purchased': purchases, 'ambiguous_owner': ambiguous}


def run(path, first, last, window):
    source = load(path/'source.json')
    protocol = load(path/'protocol.json')
    if not (protocol['ordinary_setup'] and protocol['fresh_game'] and protocol['endpoint'] == last
            and not protocol['external_policy'] and not protocol['gameplay_interventions']
            and load(path/'session-closed.json')['verified']):
        raise ValueError(f'Unqualified ordinary run at {path}')
    with (path/'Lua.log').open(encoding='utf-8-sig', errors='replace') as log:
        surveys = read_surveys(log, first, last)
        log.seek(0)
        early = with_early_preparation(surveys, log)
    players = {str(player) for player in source['original_ai']}
    with (path/'AI_Behavior_Trees.csv').open(encoding='utf-8-sig', errors='replace', newline='') as log:
        events = read_tree_events(log, players, source['map_signature'][0], last)
    cases = supplier_cases(surveys, events, players, window)
    result = {'counts': counts(cases), 'cases': cases, 'recoveries': recoveries(surveys, players),
            'production': production_activity(path, players, last),
            'publisher_wall': load(path/'ai-processing-time.json')['publisher_wall']}
    if early != surveys:
        early_cases = supplier_cases(early, events, players, window)
        result['with_early_preparation'] = {'counts': counts(early_cases), 'cases': early_cases}
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run', type=Path)
    parser.add_argument('--last', type=int, default=250)
    parser.add_argument('--first', type=int, default=1)
    parser.add_argument('--window', type=int, default=10)
    args = parser.parse_args()
    print(json.dumps(run(args.run, args.first, args.last, args.window), indent=2))
