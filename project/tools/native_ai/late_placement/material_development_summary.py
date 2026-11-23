"""Measure physical CSC supplier work from the passive planning observer.

The history holds Quarter/material pairs. A single improvement can serve
several pairs, so de-duplicate physical work separately from role totals.
First observations, land purchases and newly visible deposits contribute to
endpoint supply without being counted as Builder work.
"""

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path
import re


RECORD = re.compile(r'\bCSC_PLANNING_(MATERIAL_STATE|MATERIAL_WATCH_ENDED|FINISH)\t(.*)')
BUYER_RECORD = re.compile(r'\bCSC_PLANNING_SUPPLIER_BUYER(_POLL)?\t(.*)')
RECEIPT = re.compile(r'\bCSC_AI_MATERIAL_DEVELOPMENT_RECEIPT turn=(\d+) version=(\d+) ({.*})')
OFFER = re.compile(r'\bCSC_AI_MATERIAL_(RESEARCH|REQUEST|WORKER)_OFFER (.*)')
SERVICE_QUOTE = re.compile(r'\bCSC_AI_MATERIAL_SERVICE_QUOTE (.*)')
COMMITTED_BUYER = re.compile(r'\bCSC_AI_MATERIAL_COMMITTED_BUYER (.*)')
IMPROVEMENT = re.compile(r'\bCSC_AI_BAKERS_BUILDERS turn=(\d+) allowances=\d+ previous=({.*})')
RESERVATION = re.compile(r'^Reserving plot (\d+) (\d+)$')
ROLES = ('BAKERS/base', 'BAKERS/specialty', 'TAILORS/base', 'TAILORS/specialty')
SETUP_FIELDS = ('map', 'map_size', 'map_seed', 'game_seed', 'endpoint', 'csc', 'ce', 'extra_mods')
SOURCE_FIELDS = ('map_signature', 'original_ai', 'starts', 'units')
GAME_CORE = 'GameCore_XP2_FinalRelease.dll'
CE_CORE = 'GameCore_XP2_CE_AI_FinalRelease.dll'
RESEARCH_FIELDS = ('player', 'matched_rows', 'first_topic', 'before_q8', 'delta_q8',
                   'stock_goal', 'guided_goal', 'guided_step')
BUILDER_FIELDS = ('player', 'job_city', 'plot', 'improvement', 'unit', 'stock_value',
                  'guided_value', 'contract')
WORKER_FIELDS = ('player', 'city', 'plot', 'improvement', 'unit', 'controller', 'turn', 'reserved')
IMPROVEMENT_FIELDS = ('player', 'city', 'plot', 'improvement', 'stock_q8', 'guided_q8')


def material_roles(row):
    for column, role in (('base', 'base'), ('spec', 'specialty')):
        if row[column] == 'true':
            yield f'{row["quarter"]}/{role}'


def eligible(row):
    return (row['owner'] == row['player'] and row['district'] == '-1'
            and row['visible'] == 'true' and row['revealed'] == 'true')


def work_counts(history, role):
    relevant = [row for row in history if role == 'all' or role in row['roles']]
    new = [row['plot'] for row in relevant if row['action'] == 'new']
    repaired = [row['plot'] for row in relevant if row['action'] == 'repair']
    return dict(new_events=len(new), new_plots=len(set(new)), repair_events=len(repaired),
                repaired_plots=len(set(repaired)), distinct_worked_plots=len(set(new) | set(repaired)))


def in_buyer_group(role, group):
    return group == 'all' or role == group or role.endswith('/' + group)


def buyer_timelines(polls, players, endpoint, window=15):
    """Measure from the first live buyer with legal supply, including zero Builders.

    Exclude openings near the endpoint from the fixed-window denominator even
    when they succeed early. Report recoveries only while the buyer and a
    legal material stay available. A lost buyer ends that recovery episode.
    """
    missing = sorted(set(range(1, endpoint + 1)) - polls.keys())
    if missing:
        return {'verified': False, 'missing_turns': missing}
    buyers, episodes, pending, prepared = {}, [], {}, []
    previous_construction = {}
    previous = {}
    for turn in sorted(polls):
        current, construction = {}, {}
        for row in polls[turn]:
            player = int(row['player'])
            if player not in players or int(row['legal']) == 0:
                continue
            key = player, int(row['quarterPlot']), f'{row["quarter"]}/{row["role"]}'
            working = int(row['working']) > 0
            if row['buyerReady'] != 'true':
                if subject := row.get('constructing'):
                    construction[key] = subject, working
                    if working and previous_construction.get(key) == (subject, False):
                        prepared.append(dict(player=player, plot=key[1], role=key[2], buyer=subject, when=turn,
                                             suppliers=[int(plot) for plot in row.get('workingPlots', '').split(',') if plot]))
                continue
            current[key] = working
            buyer = buyers.setdefault(key, dict(player=player, plot=key[1], role=key[2],
                                                opened=turn, first_working=None))
            if working and buyer['first_working'] is None:
                buyer['first_working'] = turn
            if not working and previous.get(key):
                episode = dict(player=player, plot=key[1], role=key[2], lost=turn, restored=None, unavailable=None)
                episodes.append(episode)
                pending[key] = episode
        for key, episode in list(pending.items()):
            if current.get(key):
                episode['restored'] = turn
                episode['turns_to_restore'] = turn - episode['lost']
                del pending[key]
            elif key not in current:
                episode['unavailable'] = turn
                del pending[key]
        previous, previous_construction = current, construction

    counts = {}
    for role in ('all', 'base', 'specialty', *ROLES):
        cohort = [buyer for buyer in buyers.values() if in_buyer_group(buyer['role'], role)]
        mature = [buyer for buyer in cohort if buyer['opened'] + window <= endpoint]
        on_time = sum(buyer['first_working'] is not None and buyer['first_working'] <= buyer['opened'] + window
                      for buyer in mature)
        counts[role] = dict(eligible=len(mature), on_time=on_time, late_openings=len(cohort) - len(mature),
                            rate=on_time / len(mature) if mature else None,
                            working_at_endpoint=sum(working for key, working in previous.items()
                                                    if in_buyer_group(key[2], role)))
    return {'verified': True, 'window': window, 'counts': counts, 'buyers': list(buyers.values()),
            'recoveries': episodes, 'prepared_during_construction': prepared}


def add_construction_work(readiness, history):
    # A working deposit acquired from another player also satisfies supply
    # readiness. Claim physical work only when the material watch saw a new
    # improvement or repair on that exact site between the two queue polls.
    work = defaultdict(list)
    for event in history:
        work[event['player'], event['plot']].append(event)
    for entry in readiness.get('prepared_during_construction', ()):
        entry['work'] = [event for plot in entry['suppliers'] for event in work[entry['player'], plot]
                         if event['turn'] in (entry['when'] - 1, entry['when'])
                         and entry['role'] in event['roles'] and entry['plot'] in event['quarter_plots']]
    return readiness


def summarise(log, players, endpoint, *, require_finished=True, readiness_polls=None):
    state, events, receipts, improvement_packets = {}, {}, {}, {}
    offers = defaultdict(list)
    service_quotes, committed_buyers = [], []
    buyer_polls, buyer_rows = {}, defaultdict(list)
    finish = None
    for line in log:
        match = RECORD.search(line)
        if not match:
            buyer_sample = BUYER_RECORD.search(line)
            if buyer_sample:
                row = dict(field.split('=', 1) for field in buyer_sample[2].rstrip('\r\n').split('\t'))
                turn = int(row['turn'])
                if turn <= endpoint:
                    key = turn, row['source']
                    if buyer_sample[1]:
                        rows = buyer_rows.pop(key, [])
                        identities = {(r['player'], r['quarterPlot'], r['role']) for r in rows}
                        if len(rows) != int(row['buyers']) or len(identities) != len(rows):
                            raise ValueError(f'Incomplete supplier buyer census on turn {turn}')
                        buyer_polls[turn] = rows
                    else:
                        buyer_rows[key].append(row)
                continue
            receipt = RECEIPT.search(line)
            if receipt and int(receipt[1]) <= endpoint:
                sample = json.loads(receipt[3])
                receipts[int(receipt[2])] = {'read_turn': int(receipt[1]), **sample}
            improvement = IMPROVEMENT.search(line)
            if improvement and int(improvement[1]) <= endpoint:
                improvement_packets[int(improvement[1])] = json.loads(improvement[2])
            offer = OFFER.search(line)
            if offer:
                row = dict(field.split('=', 1) for field in offer[2].split())
                plots = row.pop('plots', '')
                row = {key: int(value) for key, value in row.items()}
                if row['turn'] <= endpoint and row['player'] in players:
                    row['plots'] = [int(plot) for plot in plots.split(',') if plot]
                    offers[offer[1]].append(row)
            service = SERVICE_QUOTE.search(line)
            if service:
                fields = dict(field.split('=', 1) for field in service[1].split())
                row = {key: int(value) for key, value in fields.items()}
                if row['turn'] <= endpoint and row['player'] in players:
                    service_quotes.append(row)
            commitment = COMMITTED_BUYER.search(line)
            if commitment:
                fields = dict(field.split('=', 1) for field in commitment[1].split())
                row = {key: value if key in ('class', 'buyer') else int(value) for key, value in fields.items()}
                if row['turn'] <= endpoint and row['player'] in players:
                    committed_buyers.append(row)
            continue
        kind, payload = match.groups()
        row = dict(field.split('=', 1) for field in payload.rstrip('\r\n').split('\t') if '=' in field)
        turn = int(row['turn'])
        if turn > endpoint:
            continue
        if kind == 'FINISH':
            finish = row
            continue
        if kind == 'MATERIAL_WATCH_ENDED':
            state.pop(row['identity'], None)
            continue
        key = f'{row["quarterPlot"]}:{row["materialPlot"]}'
        previous = state.get(key)
        state[key] = row
        if (int(row['player']) not in players or not previous or not eligible(row) or not eligible(previous)
                or row['working'] != 'true' or previous['working'] == 'true'
                or any(row[k] != previous[k] for k in ('player', 'quarter', 'resource', 'owner'))):
            continue
        improvement = row['improvement']
        if previous['compatible'] == 'true' and improvement == previous['improvement'] and previous['pillaged'] == 'true':
            action = 'repair'
        elif improvement != previous['improvement']:
            action = 'new'
        else:
            continue
        physical = (turn, int(row['player']), int(row['materialPlot']), action, improvement)
        event = events.setdefault(physical, {'resource': row['resource'], 'roles': set(), 'quarters': set(),
                                            'improvement_index': int(row['improvementIndex'])})
        event['roles'].update(material_roles(row))
        event['quarters'].add(int(row['quarterPlot']))

    if buyer_rows:
        raise ValueError(f'Unclosed supplier buyer censuses: {sorted(buyer_rows)}')
    if require_finished and (not finish or int(finish['turn']) != endpoint or finish['incomplete'] != 'false'):
        raise ValueError(f'No complete passive observer endpoint at turn {endpoint}: {finish!r}')

    eligible_plots, working_plots = defaultdict(set), defaultdict(set)
    for row in state.values():
        if int(row['player']) not in players or not eligible(row):
            continue
        plot = int(row['materialPlot'])
        for role in material_roles(row):
            for group in (role, 'all'):
                eligible_plots[group].add(plot)
                if row['working'] == 'true':
                    working_plots[group].add(plot)

    rows = []
    for (turn, player, plot, action, improvement), value in sorted(events.items()):
        rows.append({'turn': turn, 'player': player, 'plot': plot, 'action': action,
                     'improvement': improvement, 'resource': value['resource'],
                     'improvement_index': value['improvement_index'],
                     'roles': sorted(value['roles']), 'quarter_plots': sorted(value['quarters'])})
    counts = {}
    for role in ('all', *ROLES):
        total = len(eligible_plots[role])
        working = len(working_plots[role])
        counts[role] = dict(work_counts(rows, role), eligible_plots=total, working_plots=working,
                            working_share=working / total if total else None)
    native = {}
    if receipts:
        packets = list(receipts.values())
        native['packets_read'] = len(packets)
        native['last_capabilities'] = {key: packets[-1].get(key, 0)
                                       for key in ('techReady', 'civicReady', 'builderReady', 'workerReady')}
        if any('workerReady' in p for p in packets):
            native['max_worker_faults'] = max(p.get('workerFaults', 0) for p in packets)
        for key, fields in (('tech', RESEARCH_FIELDS), ('civic', RESEARCH_FIELDS), ('builder', BUILDER_FIELDS),
                            ('workerStart', WORKER_FIELDS), ('workerFinish', WORKER_FIELDS)):
            first_samples = [{'read_turn': p['read_turn'], 'version': p['version'],
                              **dict(zip(fields, p[key + 'First'], strict=True))}
                             for p in packets if p.get(key, 0)]
            native[key] = {'native_receipts': sum(p.get(key, 0) for p in packets), 'first_per_packet': first_samples}
        native['builder']['receipts_by_version'] = {str(p['version']): p.get('builder', 0) for p in packets}
        micros = [p.get('comparisonMicros', 0) for p in packets]
        native['mean_research_comparison_ms_per_packet'] = sum(micros) / len(micros) / 1000
        native['max_research_comparison_ms_per_packet'] = max(micros) / 1000
    improvement = {'score_writes': sum(row['bids'] for row in improvement_packets.values()),
                   'max_fault_count': max((row['faults'] for row in improvement_packets.values()), default=None),
                   'first_positive_per_turn': [{'read_turn': turn,
                                                **dict(zip(IMPROVEMENT_FIELDS, row['firstBid'], strict=True))}
                                               for turn, row in improvement_packets.items() if row['bids']]}
    if readiness_polls is not None:
        readiness_polls.update(buyer_polls)
    readiness = add_construction_work(buyer_timelines(buyer_polls, players, endpoint), rows)
    return {'turn': endpoint, 'players': sorted(players), 'counts': counts, 'work_history': rows, 'native': native,
            'improvement_scoring': improvement, 'offers': dict(offers), 'service_quotes': service_quotes,
            'committed_buyers': committed_buyers, 'buyer_readiness': readiness}


def link_native_receipts(result, city_log):
    """Join the bounded native samples to the originating offer and contract lifecycle.

    Plot work is a separate observation. A queue completion on the same plot
    does not identify which unit eventually built or repaired the supplier.
    """
    native = result['native']
    if not native:
        return
    offers = result['offers']
    research = {(r['version'], r['player'], r['kind'], r['index']): r for r in offers.get('RESEARCH', ())}
    requests = {(r['version'], r['player'], r['city'], r['plot'], r['improvement'], r['unit']): r
                for r in offers.get('REQUEST', ())}
    for kind, index in (('tech', 0), ('civic', 1)):
        for sample in native[kind]['first_per_packet']:
            sample['offer'] = research.get((sample['version'], sample['player'], index, sample['first_topic']))
            sample['changed_goal'] = sample['stock_goal'] != sample['guided_goal']

    contracts = defaultdict(list)
    for sample in native['builder']['first_per_packet']:
        sample['offer'] = requests.get((sample['version'], sample['player'], sample['job_city'],
                                        sample['plot'], sample['improvement'], sample['unit']))
        sample['contract_history'] = []
        earliest = sample['offer']['turn'] if sample['offer'] else sample['read_turn'] - 1
        sample['later_plot_work'] = [event for event in result['work_history']
                                     if event['player'] == sample['player'] and event['plot'] == sample['plot']
                                     and event['improvement_index'] == sample['improvement'] and event['turn'] >= earliest]
        if sample['contract'] >= 0:
            contracts[sample['player'], sample['contract']].append((earliest, sample))
    if not contracts:
        return
    for row in csv.reader(city_log, skipinitialspace=True):
        if len(row) >= 11 and row[6] == 'UNIT_BUILDER' and row[4].startswith('CONTRACT '):
            contract_field, state, value, origin = row[4], row[5], row[9], row[10]
        elif len(row) >= 8 and row[5] == 'UNIT_BUILDER' and row[7].startswith('CONTRACT '):
            # The native chosen-production row records the item and request
            # in different columns from offer and completion rows.
            contract_field, state, value, origin = row[7], 'SELECTED', None, row[6]
        else:
            continue
        turn, player, contract = int(row[0]), int(row[1]), int(contract_field.removeprefix('CONTRACT '))
        if turn > result['turn']:
            continue
        for earliest, sample in contracts.get((player, contract), ()):
            if turn >= earliest:
                sample['contract_history'].append({'turn': turn, 'city': row[2], 'state': state,
                                                   'value': value, 'origin': origin})


def builder_followthrough(result):
    """Count published offers and separate exact receipts from anonymous ones.

    The native API reports a count and one example per packet. If several
    initialized in the same packet, unlinked offers may own those receipts.
    Selected or completed contracts do not identify the worker that did a job.
    """
    offers = result['offers'].get('REQUEST', [])
    builder = result['native'].get('builder', {})
    receipts = builder.get('receipts_by_version', {})
    samples = builder.get('first_per_packet', [])
    exact_versions = Counter(str(row['version']) for row in samples if row.get('offer'))
    matches = []
    for row in samples:
        if not row.get('offer'):
            continue
        history = row.get('contract_history', [])
        selected = next((event for event in history if event['state'] == 'SELECTED'), None)
        if selected:
            outcome = 'purchased' if selected['city'] == 'PURCHASE' else 'selected_for_production'
        elif any(event['state'] == 'COMPLETED' for event in history):
            outcome = 'completion_recorded'
        elif any(event['state'] == 'CANCELLED' for event in history):
            outcome = 'cancelled'
        elif history:
            outcome = 'submitted'
        else:
            outcome = 'initialized'
        later_work = next((event for event in row['later_plot_work']
                           if selected and event['turn'] >= selected['turn']), None)
        matches.append({'offer': row['offer'], 'contract': row['contract'], 'outcome': outcome,
                        'selection': selected, 'later_plot_work': later_work})

    offer_counts = Counter(str(offer['version']) for offer in offers)
    unmatched = sum(max(0, count - receipts[version])
                    for version, count in offer_counts.items() if version in receipts)
    return {'published_offers': len(offers),
            'distinct_jobs': len({tuple(row[key] for key in ('player', 'city', 'plot', 'improvement', 'unit'))
                                  for row in offers}),
            'contingency_offers': sum(row.get('contingency', 0) for row in offers),
            'native_initializations': builder.get('native_receipts', 0),
            'offers_without_initialization_at_least': unmatched,
            'offers_without_packet_readback': sum(count for version, count in offer_counts.items() if version not in receipts),
            'unattributed_initializations': sum(receipts.values()) - sum(exact_versions.values()),
            'exact_matches': matches}


def commitment_followthrough(result):
    """Follow work from the first sampled offer while its own buyer was building."""
    jobs = {}
    for offer in result['committed_buyers']:
        key = tuple(offer[k] for k in ('player', 'buyerCity', 'quarter', 'plot', 'improvement', 'class', 'buyer'))
        jobs.setdefault(key, []).append(offer)
    work = defaultdict(list)
    for event in result['work_history']:
        work[event['player'], event['plot'], event['improvement_index']].append(event)
    rows = []
    for offers in jobs.values():
        first = offers[0]
        history = work[first['player'], first['plot'], first['improvement']]
        later = next((event for event in history if event['turn'] >= first['turn']
                      and first['quarter'] in event['quarter_plots']), None)
        rows.append({'first_offer': first, 'last_offer_turn': offers[-1]['turn'], 'offers': len(offers),
                     'first_work': later, 'turns_to_work': later['turn'] - first['turn'] if later else None})
    return rows


def worker_followthrough(result):
    """Connect earlier native updates to live offers and later physical observations."""
    identity = ('version', 'player', 'city', 'plot', 'improvement', 'unit')
    offers = {tuple(row[key] for key in identity): row for row in result['offers'].get('WORKER', ())}
    work = defaultdict(list)
    for event in result['work_history']:
        work[event['player'], event['plot'], event['improvement_index']].append(event)
    evidence = {}
    for phase in ('workerStart', 'workerFinish'):
        receipt = result['native'].get(phase, {})
        rows = []
        for sample in receipt.get('first_per_packet', ()):
            offer = offers.get(tuple(sample[key] for key in identity))
            observations = work[sample['player'], sample['plot'], sample['improvement']]
            completed = next((event for event in observations if event['turn'] >= sample['turn']), None)
            rows.append(dict(receipt=sample, offer=offer, later_plot_work=completed))
        evidence[phase] = dict(updates=receipt.get('native_receipts', 0), samples=rows)
    return dict(published_offers=len(offers), faults=result['native'].get('max_worker_faults'), **evidence)


def trace_work_trees(log, requests, width, endpoint):
    """Follow the last successful plot reservation in each ordinary city tree.

    Join by player and plot from the first offer in either arm. The shipped
    log gives a tile for the reservation, but does not identify the recruited
    unit or prove that the reserved improvement is the one CSC requested.
    """
    owner_since = {str(owner) for owner, _ in requests}
    reservations, traces = {}, defaultdict(list)
    steps = {'Reserve Plot', 'Find Available Unit', 'Build Unit', 'Protect Unit',
             'Move Unit', 'Build Improvement'}
    for row in csv.reader(log, skipinitialspace=True):
        if (len(row) < 7 or row[1] not in owner_since or not row[2].startswith('City ')
                or row[3] != 'Build City Improvement' or row[4] == 'READY' or row[5] not in steps):
            continue
        turn_text, player_text, tree, _, state, step, detail = row[:7]
        turn, player = int(turn_text), int(player_text)
        if turn > endpoint:
            continue
        key = player, tree
        if step == 'Reserve Plot' and state == 'SUCCESS':
            pos = RESERVATION.fullmatch(detail)
            reservations[key] = int(pos[1]) + width * int(pos[2]) if pos else None
        plot = reservations.get(key)
        start = requests.get((player, plot))
        if start is not None and turn >= start:
            traces[player, plot].append({'turn': turn, 'tree': tree, 'state': state, 'step': step, 'detail': detail})
    return [{'player': player, 'plot': plot, 'first_offer_turn': start, 'events': traces[player, plot]}
            for (player, plot), start in sorted(requests.items())]


def read_json(run, name):
    return json.loads((run / name).read_text(encoding='utf-8-sig'))


def analyse_run(run, endpoint, *, readiness_polls=None, require_finished=True):
    source = read_json(run, 'source.json')
    with (run / 'Lua.log').open(encoding='utf-8-sig', errors='replace') as log:
        result = summarise(log, set(source['original_ai']), endpoint, readiness_polls=readiness_polls,
                           require_finished=require_finished)
    city_log = run / 'AI_CityBuild.csv'
    if city_log.is_file():
        with city_log.open(encoding='utf-8-sig', errors='replace', newline='') as log:
            link_native_receipts(result, log)
    result['builder_followthrough'] = builder_followthrough(result)
    result['commitment_followthrough'] = commitment_followthrough(result)
    result['worker_followthrough'] = worker_followthrough(result)
    return result


def campaign_identity(run, endpoint, *, continued=False):
    protocol = read_json(run, 'protocol.json')
    ordinary = not continued
    if (protocol['endpoint'] != endpoint or protocol['fresh_game'] is not ordinary
            or protocol['ordinary_setup'] is not ordinary
            or not all(protocol[k] for k in ('harmonised_observation', 'planning_observation'))
            or any(protocol[k] for k in ('untuned', 'external_policy', 'gameplay_interventions'))):
        raise ValueError(f'Unexpected campaign protocol in {run}')
    source = read_json(run, 'source.json')
    setup = {k: protocol[k] for k in SETUP_FIELDS if k != 'extra_mods'}
    setup['extra_mods'] = protocol.get('extra_mods', {})
    return setup, {k: source[k] for k in SOURCE_FIELDS}


def verify_finish(run, start, endpoint):
    close = read_json(run, 'session-closed.json')
    observed = read_json(run, 'full-game-observation-complete.json')
    if (not close['verified'] or close['native_exit_code'] != 0 or not observed['verified']
            or observed['start'] != start or observed['turns'][-1] != endpoint):
        raise ValueError(f'Incomplete campaign segment in {run}')


def binary_identities(run):
    return {k: v['sha256'] for k, v in read_json(run, 'loaded-modules.json').items()}


def publisher_timing(run):
    timing = read_json(run, 'ai-processing-time.json')
    return dict(timing['publisher_wall'], failed_publications=timing['failed_attempts'])


def compare_counts(before, after):
    comparison = {}
    for role, baseline in before.items():
        candidate = after[role]
        change = {key: candidate[key] - value if value is not None and candidate[key] is not None else None
                  for key, value in baseline.items()}
        comparison[role] = {'control': baseline, 'treatment': candidate, 'difference': change}
    return comparison


def compare_buyer_readiness(before, after):
    if not (before['verified'] and after['verified']):
        return {'verified': False}
    total = after['counts']['all']
    return {'verified': True, 'comparison': compare_counts(before['counts'], after['counts']),
            'meets_target': total['eligible'] > 0 and total['on_time'] * 4 >= total['eligible'] * 3}


def dispatch_package_parity(control, treatment, binaries):
    """Require identical gameplay files and tie the one DLL change to live module proof."""
    relative = 'Binaries/Win64/' + CE_CORE
    packages = {}
    for role, run in (('control', control), ('treatment', treatment)):
        manifests = [{name.replace('\\', '/'): item for name, item in row['files'].items()}
                     for row in read_json(run, 'packages.json').values()]
        if len(manifests) != 2 or sum(relative in files for files in manifests) != 1:
            raise ValueError(f'Expected one CE and one CSC manifest in {run}')
        ce = next(files for files in manifests if relative in files)
        csc = next(files for files in manifests if relative not in files)
        if binaries[role].get(CE_CORE) != ce[relative]['sha256']:
            raise ValueError(f'Loaded CE fingerprint differs from its package in {run}')
        packages[role] = (ce, csc)
    before_ce, before_csc = packages['control']
    after_ce, after_csc = packages['treatment']
    if (before_csc != after_csc or before_ce.keys() != after_ce.keys()
            or {name for name in before_ce if before_ce[name] != after_ce[name]} != {relative}):
        raise ValueError('Worker dispatch qualification must change only the CE runtime DLL')
    return {'verified': True, 'changed': relative}


def compare_matched(control, treatment, endpoint):
    """Require a closed normal-start pair before comparing its physical outcomes."""
    setup, source = campaign_identity(control, endpoint)
    if (setup, source) != campaign_identity(treatment, endpoint):
        raise ValueError('Campaign arms differ in setup, map or original AI starts')
    binaries = {role: binary_identities(run) for role, run in (('control', control), ('treatment', treatment))}
    if binaries['control'][GAME_CORE] != binaries['treatment'][GAME_CORE]:
        raise ValueError('Campaign arms differ in the base game binary')
    for run in (control, treatment):
        verify_finish(run, 1, endpoint)

    before, after = (analyse_run(run, endpoint) for run in (control, treatment))
    jobs = {}
    for arm in (before, after):
        # A priced improvement can already have an available worker. Follow
        # sampled offers even when the job never requests Builder production.
        priced_jobs = (list(arm['offers'].get('REQUEST', ())) + list(arm['offers'].get('WORKER', ()))
                       + arm['service_quotes'] + arm['committed_buyers'])
        for row in priced_jobs:
            key = row['player'], row['plot']
            jobs[key] = min(jobs.get(key, endpoint), row['turn'])
    if jobs:
        for run, arm in ((control, before), (treatment, after)):
            behavior_log = run / 'AI_Behavior_Trees.csv'
            if behavior_log.is_file():
                with behavior_log.open(encoding='utf-8-sig', errors='replace', newline='') as log:
                    arm['material_job_trace'] = trace_work_trees(log, jobs, source['map_signature'][0], endpoint)
    result = {'setup': setup, 'source': source, 'binaries': binaries,
            'comparison': compare_counts(before['counts'], after['counts']),
            'buyer_readiness': compare_buyer_readiness(before['buyer_readiness'], after['buyer_readiness']),
            'timing': {'control': publisher_timing(control), 'treatment': publisher_timing(treatment)},
            'control': before, 'treatment': after}
    # The ordinary comparison also supports historical policy experiments
    # that changed Lua. The worker-only campaign has a stricter input contract.
    if 'max_worker_faults' in after['native'] and 'max_worker_faults' not in before['native']:
        result['dispatch_package_parity'] = dispatch_package_parity(control, treatment, binaries)
        result['worker_faults'] = after['native']['max_worker_faults']
    return result


def compare_recovered(complete, recovered, capture, endpoint, *, recovered_role='treatment'):
    """Join one arm across a verified reload without reversing treatment and control."""
    from processing_time_summary import summarise as processing_summary

    continuation = read_json(recovered, 'continuation.json')
    original, at = Path(continuation['source']), continuation['at']
    setup, source = campaign_identity(complete, endpoint)
    if ((setup, source) != campaign_identity(original, endpoint)
            or (setup, source) != campaign_identity(recovered, endpoint, continued=True)):
        raise ValueError('Recovered map, settings or original starting world changed')
    if not (0 < at < endpoint and continuation['through'] == endpoint and continuation['material_only']
            and not continuation['new_seed'] and not continuation['gameplay_interventions']
            and read_json(recovered, 'source-structure-comparison.json')['verified']):
        raise ValueError('Recovery lacks a verified unchanged-world continuation')
    checkpoint = read_json(original, f'checkpoint-{at}.json')
    if not checkpoint['verified'] or continuation['source_checkpoint']['sha256'] != checkpoint['sha256']:
        raise ValueError('Recovery checkpoint does not match its normal-start parent')
    runs = dict(control=complete, treatment=recovered) if recovered_role == 'treatment' else dict(
        control=recovered, treatment=complete)
    binaries = {role: binary_identities(run) for role, run in runs.items()}
    if (binaries[recovered_role] != binary_identities(original)
            or binaries['control'][GAME_CORE] != binaries['treatment'][GAME_CORE]
            or read_json(recovered, 'packages.json') != read_json(original, 'packages.json')):
        raise ValueError('Recovery binaries or packages changed')
    verify_finish(complete, 1, endpoint)
    verify_finish(recovered, at, endpoint)
    from planning_continue import source_lifecycle_verified
    if not source_lifecycle_verified(original):
        raise ValueError('Original owner did not complete cleanup')
    preserved = read_json(capture, 'capture.json')
    active = read_json(original, 'live-status.json')
    if (preserved.get('original', str(original)) != str(original)
            or preserved['active_clock']['worker_pid'] != active['worker_pid']
            or preserved.get('checkpoint_sha256', checkpoint['sha256']) != checkpoint['sha256']
            or not preserved['verified_boundary']['verified'] or preserved['verified_boundary']['turn'] < at):
        raise ValueError('Archived prefix does not belong to the recovered source')
    prefix_log = capture/'Lua.log'
    prefix_queue = capture/'AI_CityBuild.csv'
    for path in (prefix_log, prefix_queue):
        with path.open('rb') as log:
            if hashlib.file_digest(log, 'sha256').hexdigest() != preserved['files'][path.name]:
                raise ValueError(f'Archived prefix hash changed for {path.name}')
    prefix_polls, resumed_polls = {}, {}
    players = set(source['original_ai'])
    with prefix_log.open(encoding='utf-8-sig', errors='replace') as log:
        prefix = summarise(log, players, at, require_finished=False, readiness_polls=prefix_polls)
    with prefix_queue.open(encoding='utf-8-sig', errors='replace', newline='') as log:
        link_native_receipts(prefix, log)
    intact = analyse_run(complete, endpoint)
    continued = analyse_run(recovered, endpoint, readiness_polls=resumed_polls)
    # Keep the resumed observation for the restored checkpoint itself. A
    # missing poll still blocks qualification across a verified save seam.
    polls = {turn: rows for turn, rows in prefix_polls.items() if turn < at}
    polls.update({turn: rows for turn, rows in resumed_polls.items() if turn >= at})
    # Each segment starts from physical observations. Join actions, never
    # infer a Builder action from a change in the observer's startup state.
    actions = {}
    for row in prefix['work_history'] + continued['work_history']:
        key = tuple(row[field] for field in ('turn', 'player', 'plot', 'action', 'improvement'))
        event = actions.setdefault(key, row.copy())
        for field in ('roles', 'quarter_plots'):
            event[field] = sorted(set(event[field]) | set(row[field]))
    history = [row for _, row in sorted(actions.items())]
    recovered_readiness = add_construction_work(buyer_timelines(polls, players, endpoint), history)
    counts = {role: dict(row, **work_counts(history, role)) for role, row in continued['counts'].items()}
    segments = [processing_summary(path.read_text(encoding='utf-8-sig', errors='replace'), first=first, last=last)
                for path, first, last in ((prefix_log, 1, at), (recovered/'Lua.log', at+1, endpoint))]
    walls = [row['publisher_wall'] for row in segments]
    turns = sum(row['turns'] for row in walls)
    total = sum(row['total_ms'] for row in walls)
    timing = dict(turns=turns, total_ms=total, average_ms=total/turns if turns else None,
                  max_ms=max((row['max_ms'] for row in walls if row['max_ms'] is not None), default=None),
                  failed_publications=sum(row['failed_attempts'] for row in segments),
                  unobserved_turns=[turn for row in segments for turn in row['unobserved_turns']])
    service_quotes = prefix['service_quotes'] + [row for row in continued['service_quotes'] if row['turn'] > at]
    committed_buyers = prefix['committed_buyers'] + [row for row in continued['committed_buyers'] if row['turn'] > at]
    resumed = dict(counts=counts, work_history=history, service_quotes=service_quotes,
                   committed_buyers=committed_buyers, buyer_readiness=recovered_readiness,
                   original_prefix=prefix, resumed_segment=continued)
    arms = dict(control=intact, treatment=resumed) if recovered_role == 'treatment' else dict(
        control=resumed, treatment=intact)
    before, after = arms['control'], arms['treatment']
    timings = {role: timing if role == recovered_role else publisher_timing(complete) for role in runs}
    result = dict(setup=setup, source=source, binaries=binaries, continuation=continuation,
                  recovered_role=recovered_role, comparison=compare_counts(before['counts'], after['counts']),
                  buyer_readiness=compare_buyer_readiness(before['buyer_readiness'], after['buyer_readiness']),
                  timing=timings, **arms)
    before_native = before.get('native', before.get('resumed_segment', {}).get('native', {}))
    after_native = after.get('native', after.get('resumed_segment', {}).get('native', {}))
    if 'max_worker_faults' in after_native and 'max_worker_faults' not in before_native:
        result['dispatch_package_parity'] = dispatch_package_parity(runs['control'], runs['treatment'], binaries)
        result['worker_faults'] = after_native['max_worker_faults']
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run', type=Path)
    parser.add_argument('--compare-control', type=Path)
    parser.add_argument('--recovery-prefix', type=Path, help='Preserved logs for the normal-start portion of a resumed run')
    parser.add_argument('--recovered-control', action='store_true',
                        help='Apply the recovery prefix to --compare-control instead of the treatment')
    parser.add_argument('--endpoint', type=int, default=250)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    if args.recovered_control and not args.recovery_prefix:
        parser.error('A recovered control requires --recovery-prefix')
    if args.recovery_prefix:
        if not args.compare_control:
            parser.error('A recovered comparison requires --compare-control')
        if args.recovered_control:
            result = compare_recovered(args.run, args.compare_control, args.recovery_prefix,
                                       args.endpoint, recovered_role='control')
        else:
            result = compare_recovered(args.compare_control, args.run, args.recovery_prefix, args.endpoint)
    elif args.compare_control:
        result = compare_matched(args.compare_control, args.run, args.endpoint)
    else:
        result = analyse_run(args.run, args.endpoint)
    args.output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result.get('comparison') or result['counts'], indent=2))


if __name__ == '__main__':
    main()
