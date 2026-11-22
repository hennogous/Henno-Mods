"""Aggregate verified Service recipient-turns from the passive UI watcher."""
from collections import Counter, defaultdict
from hashlib import sha256
import json
from pathlib import Path
import re


SERVICE_LINK = re.compile(r'CSC_MILESTONE_SERVICE_LINK\t(\d+)\t(\d+)\t(\w+)\t([234])\t(\w+)\t(\d+)\t(\d+)')
SERVICE_END = re.compile(r'CSC_MILESTONE_SERVICE_END\t(\d+)\t(\d+)\t(\d+)')
UNLOCK = re.compile(r'CSC_MILESTONE_UNLOCK\t(\d+)\t(\d+)\t(tech|civic)\t(\w+)')


def stage_census(rows):
    """Count distinct physical hosts separately from their Quarter links."""
    quarters = {}
    producers = set()
    materials = set()
    customers = set()
    population_exchanges = set()
    for kind, payload in rows:
        fields = payload.split('\t')
        if kind == 'QUARTER':
            quarter, player, _, plot, complete, pillaged, *_ = fields
            quarters[plot] = (quarter, player, complete == 'true', pillaged == 'true')
        elif kind == 'PRODUCER':
            plot, stage, building, status = fields
            producers.add((plot, int(stage), building, status == '2'))
        elif kind == 'MATERIAL':
            plot, material_plot, material_class, _, operating = fields
            materials.add((plot, material_plot, material_class, operating == 'true'))
        elif kind == 'CUSTOMER':
            plot, host, stage, district, complete, status = fields
            if status != '0':
                customers.add((plot, host, int(stage), district, complete == 'true' and status == '2'))
        elif kind == 'POPULATION_EXCHANGE':
            plot, host, stage, transaction, _, _ = fields
            population_exchanges.add((plot, host, int(stage), transaction))
    result = {}
    for quarter in sorted({record[0] for record in quarters.values()}):
        built = {plot for plot, record in quarters.items() if record[0] == quarter and record[2]}
        working = {plot for plot in built if not quarters[plot][3]}
        result[quarter] = dict(quarters_built=len(built), quarters_working=len(working),
            supply={kind: dict(adjacent=sum(plot in built and c == kind for plot, _, c, _ in materials),
                              working=sum(plot in built and c == kind and active for plot, _, c, active in materials))
                    for kind in ('BASE', 'SPEC')},
            stages=[_count_stage(stage, built, working, producers, customers, population_exchanges) for stage in (2, 3, 4)])
    return result


def _count_stage(stage, built, working, producers, customers, population_exchanges):
    stage_producers = [(plot, active) for plot, found, _, active in producers if found == stage and plot in built]
    stage_customers = [(plot, host, district, active) for plot, host, found, district, active in customers
                       if found == stage and plot in built]
    active_producers = {plot for plot, active in stage_producers if active and plot in working}
    return dict(stage=stage, producers=len(stage_producers), working_producers=len(active_producers),
                customer_hosts=len({host for _, host, _, _ in stage_customers}),
                working_customer_hosts=len({host for _, host, _, active in stage_customers if active}),
                wonders=len({host for _, host, district, _ in stage_customers if district == 'DISTRICT_WONDER'}),
                physical_exchange_pairs=sum(plot in active_producers and active for plot, _, _, active in stage_customers),
                positive_population_exchanges=sum(plot in built and found == stage
                                                 for plot, _, found, _ in population_exchanges))


def service_durations(log, start, end):
    if 'CSC_MILESTONE_SERVICE_FAULT' in log:
        raise ValueError('Native Service observer fault')
    snapshots, ambiguous_turns = {}, {}
    pending = defaultdict(set)
    unlocks = []
    for line in log.splitlines():
        unlock = UNLOCK.search(line)
        if unlock and start <= int(unlock[1]) < end:
            unlocks.append(dict(turn=int(unlock[1]), player=int(unlock[2]), kind=unlock[3], topic=unlock[4]))
        link = SERVICE_LINK.search(line)
        if link:
            turn, player, quarter, stage, service, source, customer = link.groups()
            pending[int(turn)].add((player, quarter, stage, service, source, customer))
        boundary = SERVICE_END.search(line)
        if boundary:
            turn, count, unreadable = map(int, boundary.groups())
            if not start <= turn < end:
                continue
            links = pending.pop(turn, set())
            if len(links) != count or turn in snapshots or turn in ambiguous_turns:
                raise ValueError(f'Incomplete native Service observation at turn {turn}')
            if unreadable:
                # The native roster may temporarily have fewer active child
                # copies than roots. Keep that clock out of the denominator
                # while retaining all verified observations on other turns.
                ambiguous_turns[turn] = unreadable
            else:
                snapshots[turn] = links
    turns_by_chain = defaultdict(list)
    for turn, links in sorted(snapshots.items()):
        for key in links:
            turns_by_chain[key].append(turn)
    totals = Counter()
    chains = []
    for (player, quarter, stage, service, source, customer), turns in sorted(turns_by_chain.items()):
        totals[quarter, stage] += len(turns)
        chains.append(dict(player=int(player), quarter=quarter, stage=int(stage), service=service,
                           source=int(source), customer=int(customer), first=turns[0], last=turns[-1],
                           active_turns=len(turns), turns=turns))
    unlocks.sort(key=lambda row: (row['turn'], row['player'], row['kind'], row['topic']))
    return dict(observed_turns=sorted(snapshots), missing_turns=sorted(set(range(start, end)) - snapshots.keys()),
                ambiguous_turns=ambiguous_turns,
                totals=[dict(quarter=q, stage=int(s), active_link_turns=n) for (q, s), n in sorted(totals.items())],
                chains=chains, unlocked=unlocks)


def comparable_services(stock, combined):
    """Compare only clocks with a complete native observation in both arms."""
    common = set(stock['observed_turns']) & set(combined['observed_turns'])
    if not common:
        raise ValueError('No common verified Service observations in the pair')

    def side(reading):
        counts = defaultdict(lambda: dict(chains=0, turns=0))
        for chain in reading['chains']:
            observed = len(common.intersection(chain['turns']))
            if observed:
                key = (chain['quarter'], chain['stage'])
                counts[key]['chains'] += 1
                counts[key]['turns'] += observed
        return [dict(quarter=q, stage=s, **counts[q, s]) for q, s in sorted(counts)]

    return dict(common_turns=sorted(common), stock=side(stock), combined=side(combined))


def verify_policy(native, database, performance, *, untuned):
    """Use the actual loaded SQL and native receipts to establish the arm's policy."""
    if native['ready'] != 1 or native['faults']:
        raise ValueError('Native district scorer was unavailable or faulted')
    if untuned:
        if (any(native[key] for key in ('enabled', 'version', 'entries', 'matched', 'changed'))
                or any(database[key] for key in ('links', 'rules', 'yields', 'biases'))
                or performance['publication_attempts']):
            raise ValueError('Stock arm shows active CSC guidance')
    elif (native['enabled'] != 1 or native['version'] <= 0 or not database['links']
          or not performance['published_packets']):
        raise ValueError('Combined arm lacks native policy or loaded customer guidance')


def _read_json(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def _recovered_measurements(original, continuation):
    """Join time samples across one verified reload and preserve the raw runs."""
    read = _read_json
    resume = read(continuation/'continuation.json')
    at = resume['at']
    checkpoint = read(original/f'checkpoint-{at}.json')
    archived = original/f'turn-{at}.Civ6Save'
    if (Path(resume['source']).resolve() != original.resolve()
            or resume['source_checkpoint'] != checkpoint
            or not checkpoint['verified'] or checkpoint['turn'] != at
            or sha256(archived.read_bytes()).hexdigest() != checkpoint['sha256']
            or not read(continuation/'source-structure-comparison.json')['verified']
            or not read(original/'session-closed.json')['verified']
            or read(original/'source.json') != read(continuation/'source.json')):
        raise ValueError('Resume does not reproduce the named benchmark checkpoint')
    original_pins, resumed_pins = (read(path/'protocol.json') for path in (original,continuation))
    if (any(original_pins[key] != resumed_pins.get(key) for key in
            ('map', 'map_size', 'map_seed', 'game_seed', 'input_digests', 'extra_mods', 'native_profile',
             'untuned', 'external_policy', 'gameplay_interventions', 'service_observation'))
            or not resumed_pins['natural_continuation'] or resumed_pins['continuation_start'] != at):
        raise ValueError('Continuation changed the benchmark inputs or policy')
    ready = read(original/'session-source-ready.json')
    original_modules, resumed_modules = (read(path/'loaded-modules.json') for path in (original,continuation))
    if (not (ready['verified'] and ready['caller_eligibility_verified'] and ready['turn'] == 1)
            or {name: item['sha256'] for name, item in original_modules.items()} !=
               {name: item['sha256'] for name, item in resumed_modules.items()}):
        raise ValueError('Originally loaded packages or fresh start could not be verified')

    # Slice the abandoned run at the acknowledged save, then use disjoint
    # turn ranges. In particular, neither branch's pre-save boundary activity
    # is used as evidence of post-reload decisions on that turn.
    prefix = (original/'Lua.log').read_text(encoding='utf-8-sig')
    marker = re.compile(r'CSC_EXACT_CHECKPOINT_COMPLETE\t'+re.escape(checkpoint['unique_name'])+r'\ttrue\b')
    matches = list(marker.finditer(prefix))
    if len(matches) != 1:
        raise ValueError('Expected one acknowledged checkpoint in the original log')
    prefix = prefix[:matches[0].end()]
    suffix = (continuation/'Lua.log').read_text(encoding='utf-8-sig')
    clocked = re.compile(r'CSC_MILESTONE_(?:SERVICE_[A-Z_]+|UNLOCK)\s+(\d+)\b'
                         r'|CSC_AI_(?:PROCESSING|PLAYER_PROCESSING|NATIVE_PROCESSING)\s+turn=(\d+)\b')

    def selected(log, first, last):
        for line in log.splitlines():
            match = clocked.search(line)
            if match and first <= int(match[1] or match[2]) < last:
                yield line

    earlier = '\n'.join(selected(prefix, 1, at))
    later = '\n'.join(selected(suffix, at, 251))
    from processing_time_summary import summarise
    verify_policy(read(original/'source.json')['native'], read(original/'loaded-native-customer-database.json'),
                  summarise(earlier), untuned=False)
    census = {str(turn): stage_census(read(original/f'full-census-{turn}.json')['rows'])
              for turn in range(25, at+1, 25)}
    census.update(read(continuation/'stage-census.json'))
    log = earlier + '\n' + later
    return dict(census=census, services=service_durations(log, 1, 250), performance=summarise(log),
                recovery=dict(original=str(original), continuation=str(continuation), at=at,
                              checkpoint_sha256=checkpoint['sha256']))


def campaign_results(root, *, continuations=None):
    """Read finished matched arms and keep their source/output identity checks."""
    root = Path(root)
    read = _read_json
    continuations = continuations or {}
    pins = read(root / 'campaign-inputs.json')
    input_digests = [sha256(json.dumps(pins[key], sort_keys=True).encode()).hexdigest()
                     for key in ('ce', 'csc')]
    extra_digests = {identity: dict(path=item['path'],
        digest=sha256(json.dumps(item['files'], sort_keys=True).encode()).hexdigest())
        for identity, item in pins['extras'].items()}
    ce_dll = 'GameCore_XP2_CE_AI_FinalRelease.dll'
    ce_hash, = (info['sha256'] for path, info in pins['ce'].items()
                if path.replace('\\', '/').endswith('/' + ce_dll))
    expected_modules = {'GameCore_XP2_FinalRelease.dll': pins['gamecore_sha256'], ce_dll: ce_hash}
    result = {}
    for name, (map_seed, game_seed) in pins['seeds'].items():
        stock = root / f'{name.lower()}-stock'
        combined = root / f'{name.lower()}-combined'
        resumed = Path(continuations[name]) if name in continuations else None
        if any(not (side / 'full-game-observation-complete.json').is_file() for side in (stock, resumed or combined)):
            continue
        standard, treatment = (read(side / 'protocol.json') for side in (stock, combined))
        if standard != dict(treatment, untuned=True) or treatment['untuned']:
            raise ValueError(f'{name} arms did not use the same benchmark inputs')
        if (standard['map_seed'], standard['game_seed']) != (map_seed, game_seed):
            raise ValueError(f'{name} pair used a different seed')
        if (standard['input_digests'] != input_digests
                or standard.get('extra_mods', {}) != extra_digests
                or standard['native_profile']['gamecore_sha256'] != pins['gamecore_sha256']):
            raise ValueError(f'{name} pair differs from the frozen campaign packages or GameCore')
        if (not standard['ordinary_setup'] or not standard['fresh_game']
                or standard['external_policy'] or standard['gameplay_interventions']):
            raise ValueError(f'{name} pair did not run as ordinary fresh games')
        original, new = (read(side / 'source.json') for side in (stock, combined))
        if any(original[key] != new[key] for key in ('original_ai', 'map_signature', 'starts', 'units')):
            raise ValueError(f'{name} arms did not start from the same world')
        results = {}
        for label, side in (('stock', stock), ('combined', resumed or combined)):
            is_resumed = label == 'combined' and resumed is not None
            start = read(side/'continuation.json')['at'] if is_resumed else 1
            loaded = read(side / 'loaded-modules.json')
            if any(loaded.get(module, {}).get('sha256') != digest
                   for module, digest in expected_modules.items()):
                raise ValueError(f'{name} {label} loaded a different GameCore or CE build')
            terminal = read(side / 'result.json')
            coverage = read(side / 'full-game-observation-complete.json')
            ready = read(side / 'session-source-ready.json')
            if (terminal['reached'] != 250 or not read(side / 'session-closed.json')['verified']
                    or not (ready['verified'] and ready['caller_eligibility_verified'] and ready['turn'] == start)
                    or not (coverage['verified'] and coverage['start'] == start
                            and coverage['turns'] == list(range(25*(start//25+1), 251, 25)))):
                raise ValueError(f'{name} {label} lacks a verified turn-250 closure')
            performance = read(side / 'ai-processing-time.json')
            verify_policy(read(side / 'native-endpoint.json'), read(side / 'loaded-native-customer-database.json'),
                          performance, untuned=label == 'stock')
            results[label] = (_recovered_measurements(combined, side) if is_resumed else
                              dict(census=read(side/'stage-census.json'),
                                   services=read(side/'observed-services.json'), performance=performance))
        results['aligned_services'] = comparable_services(results['stock']['services'], results['combined']['services'])
        result[name] = results
    return result


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Read verified matched later-stage campaign results')
    parser.add_argument('campaign', type=Path)
    parser.add_argument('--continuation', nargs=2, action='append', metavar=('MAP','DIRECTORY'), default=[],
                        help='Join a verified resumed treatment arm to its original checkpoint prefix')
    args = parser.parse_args()
    print(json.dumps(campaign_results(args.campaign, continuations=dict(args.continuation)), indent=2))
