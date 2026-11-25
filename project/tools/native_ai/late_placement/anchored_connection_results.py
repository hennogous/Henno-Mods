"""Compare physical Quarter/customer links and their recorded opportunities."""

import argparse
from collections import Counter, defaultdict
from decimal import Decimal
import csv
import json
from pathlib import Path
import re
from statistics import median

from planning_results import parse
from processing_time_summary import launch_to_endpoint_wall, summarise


OPPORTUNITY = re.compile(
    r'CSC_AI_CONNECTION_OPPORTUNITY turn=(\d+) player=(\d+) identity='
    r'(quarterFirst|customerFirst):(\d+):([0234]):([A-Z_]+):(\d+):(\d+):(\d+)')
WONDER_OPPORTUNITY = re.compile(
    r'CSC_AI_WONDER_CONNECTION_OPPORTUNITY turn=(\d+) player=(\d+) order=(quarterFirst|customerFirst) '
    r'quarter=([A-Z_]+) anchor=(\d+) building=(BUILDING_[A-Z0-9_]+) city=\d+ plot=(\d+)')
STRONG_LAYOUT = re.compile(
    r'CSC_AI_STRONG_QUARTER_LAYOUT turn=(\d+) player=(\d+) city=(\d+) district=(\d+) plot=(\d+) '
    r'customerCity=(\d+) customerDistrict=(-?\d+) customerPlot=(\d+) stage=([0234]) '
    r'existing=(true|false) extraBase=(true|false) specialty=(true|false)')
PROSPECTIVE_SUBSTITUTE = re.compile(r'CSC_AI_PROSPECTIVE_SUBSTITUTE ([^\r\n]+)')
PRICED_PAIR = re.compile(r'CSC_AI_PROSPECTIVE_CONNECTION turn=(\d+) player=(\d+) quarterCity=(\d+) '
                         r'quarter=(\d+) quarterPlot=(\d+) customerCity=(\d+) customer=(\d+) customerPlot=(\d+)')
QUARTER_TITLE = re.compile(r'CSC_DISTRICT_CATALOGUE\t(\d+)\tDISTRICT_CSC_([A-Z_]+)_QUARTER\t')
QUARTER_RECEIPT = re.compile(r'CSC_QUARTER_WATCH_(WRITE|BEST)\t([^\r\n]+)')
DISTRICT_TITLE = re.compile(r'CSC_DISTRICT_CATALOGUE\t(\d+)\t([^\t\r\n]+)')
CUSTOMER_BID = re.compile(r'CSC_AI_(?:CUSTOMER_(?:FUTURE|ECONOMIC|PROSPECTIVE)_BID|CONNECTION_COMPLETION) ([^\r\n]+)')
CUSTOMER_RECEIPT = re.compile(r'CSC_CUSTOMER_WATCH_NATIVE [^\r\n]*? ordinal=(\d+) record=(\{[^\r\n]+\})')
CUSTOMER_LAND_OFFER = re.compile(
    r'CSC_AI_CUSTOMER_LAND_OFFER turn=(\d+) player=(\d+) city=(\d+) district=(\d+) '
    r'plot=(\d+) invoice=(\d+)(?: bidQ8=(-?\d+)(?: version=(\d+))?)?')


def layout_identity(row):
    return tuple(row.get(key) for key in ('player', 'city', 'quarter', 'quarterPlot',
                                           'neighbourCity', 'neighbourDistrict', 'neighbourPlot'))


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
        # A linked reference publishes its completion credit without an
        # ECONOMIC_BID line. Customer-first completion credits belong to the
        # Quarter's final score, which has its own native write receipt.
        if row.get('order') == 'customerFirst':
            continue
        credit = int(row['deltaQ8'] if 'deltaQ8' in row else row['creditQ8'])
        if len(published) == 1 and credit > 0 and int(row['player']) in players:
            version = next(iter(published))
            customers.add((version, *(int(row[k]) for k in ('player', 'city', 'district', 'plot'))))
    paid_customers = set()
    for match in CUSTOMER_LAND_OFFER.finditer(log):
        turn, player, city, district, plot, _ = map(int, match.groups()[:6])
        if (player in players and match[7] and int(match[7]) > 0
                and match[8] and int(match[8]) in versions.get(turn, ())):
            paid_customers.add((int(match[8]), player, city, district, plot))

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

    priced_customers = customers | paid_customers
    if priced_customers:
        positive = set()
        for match in CUSTOMER_RECEIPT.finditer(log):
            row = json.loads(match[2])
            key = tuple(row[k] for k in ('version', 'player', 'city', 'district', 'plot'))
            group = (row['generation'], *key[:3])
            if group not in decisions or key not in priced_customers:
                continue
            cell = (row['generation'], *key)
            if row['k'] == 'net':
                if row['result'] > row['base'] and row['eligible'] == 1:
                    positive.add(cell)
                else:
                    positive.discard(cell)
            if row['k'] == 'cache' and row['result'] > 0 and row['eligible'] == 1 and cell in positive:
                kind = 'customerLand' if key in paid_customers else 'customer'
                decisions[group].append((int(match[1]), kind, *key[3:], row['result']))

    outcomes = defaultdict(Counter)
    lost_to = defaultdict(Counter)
    losses = []
    footprint_losses = []
    for (generation, version, player, city), events in sorted(decisions.items()):
        cells = defaultdict(dict)
        for ordinal, kind, district, plot, score in sorted(events):
            if kind != 'winner':
                cells[kind, district][plot] = score
                continue
            for (bid_kind, bid_district), plots in cells.items():
                def loss_at(bid_plot, bid_score):
                    return dict(kind=bid_kind, generation=generation, version=version,
                        player=player, city=city, ordinal=ordinal, district=names.get(bid_district, str(bid_district)),
                        plot=bid_plot, score_q8=bid_score, winner=names.get(district, str(district)),
                        winner_plot=plot, winner_q8=score, gap_q8=score-bid_score)

                # A planned footprint can be occupied even when another tile
                # is the stronger bid for its district. Audit that physical
                # contest separately from the district-level comparison.
                same_plot = plots.get(plot)
                if district >= 0 and district != bid_district and same_plot is not None and score >= same_plot:
                    footprint_losses.append(loss_at(plot, same_plot))
                # Each district/type contributes its strongest observed site
                # once in this decision. Counting its alternative tiles would
                # turn a single missed investment into several apparent losses.
                bid_score = max(plots.values())
                bid_plot = min(p for p, value in plots.items() if value == bid_score)
                if district == bid_district and plots.get(plot) == score:
                    outcomes[bid_kind]['exact_win'] += 1
                elif district >= 0 and score > bid_score:
                    loss = loss_at(bid_plot, bid_score)
                    outcomes[bid_kind]['outscored'] += 1
                    lost_to[bid_kind][loss['winner']] += 1
                    losses.append(loss)
                else:
                    outcomes[bid_kind]['other_or_unresolved'] += 1
    return dict(outcomes={k: dict(v) for k, v in outcomes.items()},
                lost_to={k: dict(v) for k, v in lost_to.items()}, losses=losses,
                footprint_losses=footprint_losses)


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
        existing, extra_base, specialty = match.groups()[9:]
        if player not in players or turn > through or existing == 'true':
            continue
        key = (player, city, district, plot, buyer, customer, target, stage)
        supply = 'BASE_AND_SPECIALTY' if specialty == 'true' else 'TWO_BASE' if extra_base == 'true' else 'ONE_BASE'
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
        elif (row['kind'] == 'RELATION' and row.get('role') in ('customer', 'goodsProvider') and row.get('present')
              and row.get('quarterComplete') and row.get('neighbourComplete')):
            relation = tuple(row.get(k) for k in ('player', 'city', 'quarter', 'quarterPlot', 'neighbourCity',
                                                   'neighbourDistrict', 'neighbourPlot'))
            relation += (0 if row['role'] == 'goodsProvider' else row.get('stage'),)
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


def prospective_footprints(log, observations, players, through, competition, *, priced=False):
    """Follow either the spatial shortlist or the pairs actually priced by the candidate."""
    layouts = defaultdict(set)
    pattern = PRICED_PAIR if priced else STRONG_LAYOUT
    for match in pattern.finditer(log):
        turn, player, city, district, plot, buyer, customer, target = map(int, match.groups()[:8])
        if player in players and turn <= through and (priced or match[10] == 'false') and customer >= 0:
            layouts[((player, city, district, plot), (player, buyer, customer, target))].add(turn)
    if not layouts:
        return []

    names = {int(index): title for index, title in DISTRICT_TITLE.findall(log)}
    versions = defaultdict(set)
    foundations, completions, choices = defaultdict(list), defaultdict(list), defaultdict(list)
    city_winners = defaultdict(set)
    offered = defaultdict(set)
    for row in observations:
        kind = row['kind']
        if kind == 'PUBLICATION' and row['accepted']:
            versions[row['pendingTurn']].add(row['version'])
        elif row.get('turn', through + 1) <= through:
            if kind == 'FOUNDATION' and row.get('foundationDateKnown'):
                foundations[row['plot']].append(row)
            if kind == 'COMPLETION' or (kind == 'FOUNDATION' and row.get('complete')):
                identity = tuple(row[k] for k in ('player', 'city', 'district', 'plot'))
                completions[identity].append(row.get('completionTurn', row['turn']))
            if kind == 'NATIVE_BEST' and row.get('player') in players:
                choices[row['player'], row['city'], row['plot']].append(row)
                if row['district'] >= 0 and row['plot'] >= 0:
                    city_winners[row['player'], row['city']].add((row['turn'], row['district'], row['plot']))
            if kind == 'OPPORTUNITY' and row.get('offered') and row.get('player') in players:
                identity = tuple(row[k] for k in ('player', 'city', 'district', 'plot'))
                offered[identity].add(row['version'])
    losses = defaultdict(list)
    for row in competition['footprint_losses']:
        losses[row['player'], row['city'], row['district'], row['plot']].append(row)
    # Read the ordinary cache for the exact modeled sites, including customers
    # that had no positive CSC delta. The separate bid audit still establishes
    # which explicit offers reached the native consumer.
    planned = {target for pair in layouts for target in pair}
    cached = defaultdict(list)
    if planned:
        for match in CUSTOMER_RECEIPT.finditer(log):
            row = json.loads(match[2])
            if row['k'] == 'best' and row['eligible'] == 1 and row['player'] in players:
                observed = re.search(r'observedTurn=(\d+)', match[0])
                if observed and row['district'] >= 0 and row['plot'] >= 0:
                    city_winners[row['player'], row['city']].add((int(observed[1]), row['district'], row['plot']))
            if row['k'] != 'cache' or row['eligible'] != 1:
                continue
            target = tuple(row[key] for key in ('player', 'city', 'district', 'plot'))
            if target in planned:
                cached[row['generation'], row['version'], target].append((int(match[1]), row['result']))
    substitutes = defaultdict(list)
    for payload in PROSPECTIVE_SUBSTITUTE.findall(log):
        row = {key: int(value) for key, value in (field.split('=', 1) for field in payload.split())}
        turn, player = row['turn'], row['player']
        if turn <= through and player in players:
            quarter = player, row['quarterCity'], row['quarter'], row['quarterPlot']
            customer = player, row['customerCity'], row['customer'], row['customerPlot']
            substitutes[quarter, customer].append(dict(turn=turn, versions=sorted(versions[turn]),
                quarter_plot=row['alternateQuarterPlot'], customer_plot=row['alternateCustomerPlot']))

    def footprint(identity, turns, active):
        player, city, district, plot = identity
        name = names.get(district, str(district))
        first = min(turns)
        built = sorted((row for row in foundations[plot]
                        if first <= row.get('foundationTurn', row['turn']) <= through),
                       key=lambda row: row.get('foundationTurn', row['turn']))
        foundation = next(iter(built), None)
        foundation_turn = foundation.get('foundationTurn', foundation['turn']) if foundation else None
        matched = bool(foundation and identity == (foundation['player'], foundation['city'],
                                                   foundation['district'], plot))
        completion = min((turn for turn in completions[identity] if matched and foundation_turn <= turn),
                         default=None)
        choice_rows = [row for row in choices[player, city, plot] if row['version'] in active]
        scored_losses = [row for row in losses[player, city, name, plot] if row['version'] in active]
        nearest = min(scored_losses, key=lambda row: row['gap_q8'], default=None)
        cache_losses = []
        for winner in choice_rows:
            cache = cached.get((winner.get('generation'), winner['version'], identity), ())
            if not cache or winner['district'] < 0 or winner['district'] == district:
                continue
            read = max((cell for cell in cache if cell[0] < winner['nativeOrdinal']), default=None)
            if read is not None and winner['result'] >= read[1]:
                cache_losses.append(dict(turn=winner['turn'], version=winner['version'],
                    winner=names.get(winner['district'], str(winner['district'])), winner_q8=winner['result'],
                    target_q8=read[1], gap_q8=winner['result']-read[1]))
        return dict(player=player, city=city, district=name, plot=plot,
                    native_same_plot_choices=dict(Counter(names.get(row['district'], str(row['district']))
                                                          for row in choice_rows)),
                    exact_same_plot_losses=len(scored_losses), nearest_loss=nearest,
                    cached_same_plot_losses=len(cache_losses),
                    nearest_cached_loss=min(cache_losses, key=lambda row: row['gap_q8'], default=None),
                    matched_completion=completion,
                    first_occupation=None if not foundation else dict(
                        turn=foundation_turn,
                        player=foundation['player'], city=foundation['city'],
                        district=names.get(foundation['district'], str(foundation['district'])),
                        matched=matched))

    result = []
    for (quarter, customer), turns in sorted(layouts.items(), key=lambda item: (min(item[1]), item[0])):
        active = set().union(*(versions[turn] for turn in turns))
        qsite, csite = footprint(quarter, turns, active), footprint(customer, turns, active)
        follow_through = {}
        for role, anchor, target, identity in (('customer', qsite, csite, customer), ('quarter', csite, qsite, quarter)):
            first, second = anchor['first_occupation'], target['first_occupation']
            if not first or not first['matched']:
                continue
            end = second['turn'] if second else through
            player, city, district, plot = identity
            # A short scout and the full-game observer may record the same
            # choice. Count distinct turn/type/plot sightings after foundation.
            # An open plot can lose the district to a different tile even on
            # turns without a fresh CSC bid. The winning choice is observable
            # there, while its margin requires a same-packet losing-cell read.
            observed = sorted(x for x in city_winners[player, city] if first['turn'] < x[0] <= end)
            if end > first['turn']:
                follow_through[role] = dict(observed_choices=len(observed),
                    exact_target=sum(d == district and p == plot for _, d, p in observed),
                    same_type_elsewhere=[dict(observed_turn=t, plot=p) for t, d, p in observed if d == district and p != plot],
                    other_districts=dict(Counter(names.get(d, str(d)) for _, d, _ in observed if d != district)))
        result.append(dict(first_offer=min(turns), last_offer=max(turns), modeled_turns=len(turns),
                           quarter_published=bool(active & offered[quarter]),
                           observed_substitutes=substitutes[quarter, customer],
                           post_foundation_choices=follow_through, quarter=qsite, customer=csite))
    return result


def prospective_footprint_counts(layouts):
    """Summarize distinct physical pairs even when several stages share them."""
    counts, occupied, scored_losses = defaultdict(Counter), defaultdict(set), defaultdict(set)
    for pair in layouts:
        quarter, customer = pair['quarter'], pair['customer']
        family = quarter['district']
        count = counts[family]
        count['modeled_pairs'] += 1
        count['pairs_with_quarter_offer'] += pair['quarter_published']
        for role, follow in pair.get('post_foundation_choices', {}).items():
            count[role + '_pending_after_partner_founded'] += 1
            count[role + '_with_later_city_choice'] += follow['observed_choices'] > 0
            count[role + '_selected_elsewhere_after_partner_founded'] += bool(follow['same_type_elsewhere'])
        built = []
        for role, target in (('quarter', quarter), ('customer', customer)):
            if target['native_same_plot_choices'].get(target['district']):
                count[role + '_selected'] += 1
            occupation = target['first_occupation']
            if occupation and occupation['matched']:
                count[role + '_founded'] += 1
                built.append(occupation['turn'])
            elif occupation:
                identity = (role, target['player'], target['city'], target['district'], target['plot'])
                occupied[family].add(identity)
                if target['exact_same_plot_losses'] or target['cached_same_plot_losses']:
                    scored_losses[family].add(identity)
        if all(target['matched_completion'] is not None for target in (quarter, customer)):
            count['pairs_completed'] += 1
            order = 'same_turn'
            if built[0] != built[1]:
                order = 'quarter_first' if built[0] < built[1] else 'customer_first'
            count['completed_' + order] += 1
            count['turns_between_foundations_' + order] += abs(built[0] - built[1])
            count['turns_from_first_foundation_to_both_complete_' + order] += (
                max(quarter['matched_completion'], customer['matched_completion']) - min(built))
    for family, count in counts.items():
        count['distinct_footprints_occupied_by_other'] = len(occupied[family])
        count['distinct_footprints_lost_after_scored_contest'] = len(scored_losses[family])
    return {family: dict(values) for family, values in counts.items()}


def common_layout_report(log, observations, players, through, *, endpoint_pairs=None):
    """Both policies log their top two Quarter bids and ordinary owned partner sites.

    Count each physical pair once at its first qualifying observation. Future-only
    +1 and paid partners have separate candidate diagnostics. Founding and a live
    completed relationship must agree on cities as well as coordinates.
    The optional endpoint facts count the same completed layouts that
    still have a working Base under the original owner and cities.
    """
    titles = {int(i): title for i,title in QUARTER_TITLE.findall(log)}
    layouts = {}
    for match in re.finditer(r'CSC_AI_SPATIAL_BID ([^\r\n]+)', log):
        fields = dict(item.split('=',1) for item in match[1].split() if '=' in item)
        turn,player = int(fields['turn']),int(fields['player'])
        if player not in players or turn > through or float(fields['adjacency']) < 2:
            continue
        quarter = titles.get(int(fields['district']))
        if quarter is None:
            continue
        for n in ('1','2'):
            partner_city = int(fields.get('customerCity'+n,-1))
            if partner_city >= 0:
                key = (player,int(fields['city']),quarter,int(fields['plot']),partner_city,
                       int(fields['customerType'+n]),int(fields['customerPlot'+n]))
                layouts.setdefault(key,turn)
    foundations, linked = {}, {}
    for r in observations:
        if r.get('player') not in players or r.get('turn',0)>through:
            continue
        if r['kind']=='FOUNDATION' and r.get('foundationDateKnown'):
            key = (r['player'],r['city'],r['district'],r['plot'])
            foundations.setdefault(key,r.get('foundationTurn',r['turn']))
        elif (r['kind']=='RELATION' and r.get('present') and r.get('quarterComplete') and r.get('neighbourComplete')
              and r.get('role') in ('customer','goodsProvider','sales')):
            key = layout_identity(r)
            if r['turn'] >= layouts.get(key, 0):
                linked.setdefault(key,r['turn'])
    district_ids = {name: i for i,name in titles.items()}
    counts = defaultdict(Counter)
    targets = defaultdict(set)
    retained = {pair['layout'] for pair in endpoint_pairs or () if pair['working_base']}
    retained_buyers = {pair['layout'] for pair in endpoint_pairs or () if pair['working_base'] and pair['working_buyer']}
    for key,seen in layouts.items():
        player,city,quarter,plot,buyer,customer,target=key
        q=foundations.get((player,city,district_ids[quarter],plot))
        p=foundations.get((player,buyer,customer,target))
        if (q is not None and q<seen) or (p is not None and p<seen):
            continue
        order=('unstarted' if q is None and p is None else 'quarterFirst' if p is None or q is not None and q<p
               else 'partnerFirst' if q is None or p<q else 'sameTurn')
        count=counts[f'{quarter}:{order}']
        count['eligible_pairs']+=1
        if endpoint_pairs is not None:
            count.setdefault('completed_with_working_base_at_endpoint', 0)
            count.setdefault('completed_with_working_base_and_buyer_at_endpoint', 0)
        if order in ('quarterFirst', 'partnerFirst'):
            quarter_site = (player, city, district_ids[quarter], plot)
            customer_site = (player, buyer, customer, target)
            first, second = (quarter_site, customer_site) if order == 'quarterFirst' else (customer_site, quarter_site)
            targets[quarter, order, first, second[:3]].add(second[3])
        if p is not None and q is not None:
            count['both_founded']+=1
            count['total_turns_between_foundations']+=abs(p-q)
            if key in linked and linked[key]>=max(q,p):
                count['both_completed_adjacent']+=1
                count['total_turns_to_completed_pair_from_first_foundation']+=linked[key]-min(p,q)
                if key in retained:
                    count['completed_with_working_base_at_endpoint']+=1
                    count['completed_with_working_base_and_buyer_at_endpoint']+=key in retained_buyers
    return ({key:dict(value) for key,value in sorted(counts.items())},
            anchored_target_results(targets, foundations, linked, district_ids))


def common_layout_conversion(log, observations, players, through):
    """Exact-tile projection retained for callers comparing earlier reports."""
    return common_layout_report(log, observations, players, through)[0]


def anchored_target_results(targets, foundations, linked, district_ids):
    """What happened once one surveyed tile received its intended district?

    Two suggested Hub plots for the same Quarter and buying city are one
    investment decision. A Hub across the river can satisfy that decision on
    a different tile. Require the observer's completed gameplay relationship
    in both original cities before giving credit for that alternate.
    """
    built_by_type = defaultdict(dict)
    for site, turn in foundations.items():
        built_by_type[site[:3]][site[3]] = turn
    links = defaultdict(set)
    for player, city, quarter, plot, buyer, customer, target in linked:
        if quarter not in district_ids:
            continue
        q = (player, city, district_ids[quarter], plot)
        c = (player, buyer, customer, target)
        links[q, c[:3]].add(c)
        links[c, q[:3]].add(q)

    outcomes = defaultdict(Counter)
    realized = {}
    for (quarter, order, first, second_type), planned_plots in targets.items():
        completed = links[first, second_type]
        built = built_by_type[second_type]
        if completed:
            exact = any(site[3] in planned_plots for site in completed)
            outcome = 'completed_on_surveyed_tiles' if exact else 'completed_on_other_adjacent_tile'
            for site in completed:
                q, c = (first, site) if order == 'quarterFirst' else (site, first)
                # The same completed pair can satisfy two surveys, one from
                # each side. Its actual order comes from its two foundations.
                realized[quarter, q, c] = foundations.get(q), foundations.get(c)
        elif not built:
            outcome = 'second_type_never_founded_in_city'
        elif planned_plots.intersection(built):
            outcome = 'both_founded_without_observed_completed_link'
        elif min(built.values()) < foundations[first]:
            outcome = 'second_type_already_elsewhere_when_first_tile_founded'
        else:
            outcome = 'second_type_founded_elsewhere_without_completed_link'
        outcomes[f'{quarter}:{order}'][outcome] += 1

    actual = defaultdict(Counter)
    for (quarter, _, _), (q, c) in realized.items():
        if q is None or c is None:
            order = 'unknown'
        elif q == c:
            order = 'sameTurn'
        else:
            order = 'quarterFirst' if q < c else 'partnerFirst'
        actual[quarter][order] += 1
    return dict(targets_by_first_surveyed_tile={k:dict(v) for k,v in sorted(outcomes.items())},
                distinct_completed_pairs_by_actual_order={k:dict(v) for k,v in sorted(actual.items())})


def completed_substitute_pairs(priced, observations, through):
    """Join an advertised alternate to a completed pair retaining the other planned district.

    Each backup log carries two independent plot hints. Combining them into a
    single new pair could invent a layout that nobody evaluated. Require one
    unchanged leg, the original cities and types, and a live completed relation.
    """
    expected = defaultdict(dict)
    for layout in priced:
        quarter, partner = layout['quarter'], layout['customer']
        for alternate in layout['observed_substitutes']:
            variants = ((alternate['quarter_plot'], partner['plot'], 'partner'),
                        (quarter['plot'], alternate['customer_plot'], 'quarter'))
            for x, y, retained in variants:
                if min(x, y) < 0 or (x, y) == (quarter['plot'], partner['plot']):
                    continue
                key = (quarter['player'], quarter['city'], quarter['district'], x,
                       partner['city'], partner['district'], y)
                seen = expected[key]
                seen[retained] = min(seen.get(retained, alternate['turn']), alternate['turn'])
    if not expected:
        return []
    names = {r['district']: r['districtType'] for r in observations if r['kind'] == 'MAPPING'}
    completed = {}
    for row in observations:
        if (row['kind'] != 'RELATION' or row['turn'] > through or not row.get('present')
                or not row.get('quarterComplete') or not row.get('neighbourComplete')
                or row.get('role') not in ('customer', 'sales', 'goodsProvider')):
            continue
        key = (row['player'], row.get('city'), f"DISTRICT_CSC_{row['quarter']}_QUARTER", row['quarterPlot'],
               row.get('neighbourCity'), names.get(row['neighbourDistrict']), row['neighbourPlot'])
        turns = {'quarter': row.get('quarterFoundationTurn'), 'partner': row.get('neighbourFoundationTurn')}
        if any(t is None or t < 0 or t > row['turn'] for t in turns.values()):
            continue
        # The reused footprint was empty at the proposal. An existing mapped
        # district can serve as the alternate on the other side of the pair.
        offers = [t for retained, t in expected.get(key, {}).items() if t <= turns[retained]]
        if not offers:
            continue
        if key not in completed or row['turn'] < completed[key]['both_complete_by']:
            completed[key] = dict(player=key[0], quarter_city=key[1], quarter=row['quarter'], quarter_plot=key[3],
                partner_city=key[4], partner=key[5], partner_plot=key[6], alternate_seen=min(offers),
                quarter_founded=turns['quarter'], partner_founded=turns['partner'], both_complete_by=row['turn'])
    return [completed[key] for key in sorted(completed)]


def foundation_order(row):
    """Recover build order when a checkpoint already contained one district."""
    order = row.get('foundationOrder')
    if order in ('quarterFirst', 'neighbourFirst', 'sameTurn'):
        return order
    # An earlier sighting proves this side already existed by that turn. An
    # initial census seeing both districts on the same turn cannot order them.
    for seen, founded, earlier in (('quarterFirstSeen','neighbourFoundationTurn','quarterFirst'),
                                   ('neighbourFirstSeen','quarterFoundationTurn','neighbourFirst')):
        if row.get(seen) is not None and row.get(founded) is not None and 0 <= row[seen] < row[founded]:
            return earlier
    return 'unknown'


def connection_counts(log, original_ai, through, *, observations=None):
    """Join observed legal options to real foundations and completed links.

    Deduplicate stage/venue definitions for a physical pair. Keep ownership
    on the opportunity identity so conquest cannot turn a missed construction
    into a conversion for the original player. Completed links are physical
    and counted once even if subsequently captured.
    """
    options = defaultdict(dict)
    opportunities_by_district = set()
    for turn, pid, order, anchor, stage, quarter, city, district, target in OPPORTUNITY.findall(log):
        turn, pid, anchor, city, district, target = map(int, (turn, pid, anchor, city, district, target))
        if pid not in original_ai or turn > through:
            continue
        quarter_plot, customer_plot = (anchor, target) if order == 'quarterFirst' else (target, anchor)
        role = 'goodsProvider' if stage == '0' else 'customer'
        identity = (pid, order, quarter, quarter_plot, customer_plot, role)
        # Several legal plots in the same eligible city/type are fallback
        # footprints for one missing partner district, not independent builds.
        group = (pid, order, quarter, anchor, role, city, district)
        opportunities_by_district.add(group)
        options[identity].setdefault(group, turn)
    if observations is None:
        observations = parse(log, 'CSC_PLANNING_')
    definitions = {row['district']: row['districtType'] for row in observations if row['kind']=='MAPPING'}
    completed = {}
    providers = {}
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
        if row['kind'] != 'RELATION' or row.get('role') not in ('customer','sales','goodsProvider') or not row.get('present'):
            continue
        if row.get('neighbourDistrict') == 0 or definitions.get(row.get('neighbourDistrict')) == 'DISTRICT_WONDER':
            continue
        if not (row.get('quarterComplete') and row.get('neighbourComplete')):
            continue
        order = foundation_order(row)
        if order == 'neighbourFirst':
            order = 'customerFirst'
        quarter, qplot, cplot = (row[key] for key in ('quarter', 'quarterPlot', 'neighbourPlot'))
        key = (quarter, qplot, cplot, row['neighbourDistrict'])
        if row['role'] == 'goodsProvider':
            if key not in providers or providers[key] == 'unknown':
                providers[key] = 'providerFirst' if order == 'customerFirst' else order
        else:
            previous = completed.get(key)
            if previous is None or (previous == 'unknown' and order != 'unknown'):
                completed[key] = order
        role = 'goodsProvider' if row['role'] == 'goodsProvider' else 'customer'
        identity = (row['player'], order, quarter, qplot, cplot, role)
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
        pid, order, _, qplot, cplot, _ = identity
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
                  provider_district_opportunities=by_order_and_quarter(g for g in opportunities_by_district if g[4]=='goodsProvider'),
                  completed_provider_opportunities=by_order_and_quarter(g for g in realized_by_district if g[4]=='goodsProvider'),
                  lost_to_other_foundations=by_order_and_quarter(lost),
                  lost_to_foreign_foundations=by_order_and_quarter(lost_to_foreign_build),
                  completed_physical_pairs=dict(Counter(f'{order}:{key[0]}' for key, order in completed.items())),
                  completed_provider_pairs=dict(Counter(f'{order}:{key[0]}' for key, order in providers.items())))
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


def endpoint_pair_facts(census, observations, players):
    """Retain each current physical link and its supply under the live owner."""
    quarter_hosts, materials = {}, defaultdict(set)
    for kind, payload in census['rows']:
        fields = payload.split('\t')
        if kind == 'QUARTER' and int(fields[1]) in players and fields[4] == 'true':
            quarter_hosts[int(fields[3])] = (fields[0], int(fields[1]), int(fields[2]), fields[5] == 'true')
        elif kind == 'MATERIAL' and fields[4] == 'true':
            materials[int(fields[0])].add(fields[2])

    # The observer emits changes, including removals, keyed by the two tiles
    # and the gameplay rule. Several building stages can share a physical pair.
    active = {}
    names = {}
    for row in observations:
        if row.get('turn', 0) > census['turn']:
            continue
        if row['kind'] == 'MAPPING':
            names[row['district']] = row['districtType']
        elif row['kind'] == 'RELATION_REMOVED':
            active.pop(row['relation'], None)
        elif row['kind'] == 'RELATION':
            key = ':'.join(str(row.get(k, '')) for k in ('quarterPlot','neighbourPlot','role','stage','building'))
            active[key] = row

    pairs = {}
    for row in active.values():
        role = row['role']
        qplot, target = row['quarterPlot'], row['neighbourPlot']
        host = quarter_hosts.get(qplot)
        if (not host or host[:3] != (row['quarter'], row['player'], row['city'])
                or role not in ('customer','sales','goodsProvider') or not row.get('present')
                or not row['quarterComplete'] or not row['neighbourComplete']
                or row['neighbourDistrict'] == 0 or names.get(row['neighbourDistrict']) == 'DISTRICT_WONDER'):
            continue
        # Keep City Lights provider results separate. Customer and sales rows
        # for the same district count once. A pillaged host cannot operate.
        family = 'provider' if role == 'goodsProvider' else 'customer'
        order = foundation_order(row)
        if order == 'neighbourFirst':
            order = 'partnerFirst'
        pair = qplot,target,family
        founded = row.get('quarterFoundationTurn'), row.get('neighbourFoundationTurn')
        gap = abs(founded[0] - founded[1]) if all(type(t) is int and 0 <= t <= census['turn'] for t in founded) else None
        healthy = not (host[3] or row['neighbourPillaged'])
        facts = pairs.setdefault(pair, dict(layout=layout_identity(row), label=f'{host[0]}:{family}:{order}',
            family=family, foundation_gap=gap, working_base=healthy and 'BASE' in materials[qplot],
            working_spec=healthy and 'SPEC' in materials[qplot], mapped_buyer=False, working_buyer=False))
        if role == 'customer':
            facts['mapped_buyer'] = True
            facts['working_buyer'] = facts['working_buyer'] or healthy and row.get('buildingStatus') == 2
    return list(pairs.values())


def summarise_endpoint_pairs(pairs, *, include_timing=False):
    """Count completed pairs, their working suppliers and known foundation intervals."""
    counts = defaultdict(Counter)
    gaps = defaultdict(list)
    for pair in pairs:
        label, gap = pair['label'], pair['foundation_gap']
        counts[label]['completed'] += 1
        if include_timing and gap is not None:
            gaps[label].append(gap)
        if pair['family'] == 'customer':
            counts[label]['mapped_buyer_district' if pair['mapped_buyer'] else 'sales_only_district'] += 1
        if pair['working_base']:
            counts[label]['with_working_base'] += 1
            if pair['working_buyer']:
                counts[label]['with_working_base_and_customer_building'] += 1
            if pair['working_spec']:
                counts[label]['with_working_base_and_spec'] += 1
    result = {label: dict(values) for label, values in sorted(counts.items())}
    if include_timing:
        for label, values in result.items():
            observed = gaps[label]
            values['second_foundation_turns'] = dict(known=len(observed), unknown=values['completed']-len(observed),
                mean=sum(observed)/len(observed) if observed else None, median=median(observed) if observed else None,
                maximum=max(observed, default=None))
    return result


def endpoint_pair_supply(census, observations, players, *, include_timing=False):
    return summarise_endpoint_pairs(endpoint_pair_facts(census, observations, players), include_timing=include_timing)


def plot_buyer_request(requests, typed_requests, city_label):
    """Find the buying city's first accepted handle and what prompted it."""
    matched = [(turn, contract, state) for turn, contract, state, city in requests
               if city == city_label]
    accepted = [(turn, contract) for turn, contract, state in matched if state == 'Accepted']
    earliest = min((turn for turn, _ in accepted), default=None)
    candidates = {contract for turn, contract in accepted if turn == earliest}
    result = dict(buying_city_request_turn=max((turn for turn, _ in accepted), default=None),
                  first_observed_buying_city_acceptance=earliest,
                  first_observed_buying_city_request=None, first_observed_request_district=None,
                  first_observed_buying_city_contract=None)
    if len(candidates) != 1:
        return result
    contract, = candidates
    first = min(turn for turn, number, state in matched
                if number == contract and state in ('Submitted', 'Accepted'))
    names = {district for turn, number, state, city, district in typed_requests
             if city == city_label and number == contract and turn == first
             and state in ('Submitted', 'Accepted')}
    result.update(first_observed_buying_city_request=first,
                  first_observed_buying_city_contract=contract,
                  first_observed_request_district=next(iter(names)) if len(names) == 1 else None)
    return result


def customer_land_purchases(log, observations, players, through, tree_rows):
    """Join a priced offer to the buyer, observed Gold change and later use."""
    offers = defaultdict(list)
    native_offers = []
    versions = defaultdict(set)
    choices = defaultdict(set)
    names = {int(index): title for index, title in DISTRICT_TITLE.findall(log)}
    for row in observations:
        if row['kind'] == 'PUBLICATION' and row['accepted']:
            versions[row['pendingTurn']].add(row['version'])
        if row['kind'] == 'NATIVE_BEST' and row.get('player') in players and row['turn'] <= through:
            key = tuple(row[key] for key in ('version', 'player', 'city', 'district', 'plot'))
            choices[key].add(row.get('observedTurn', row['turn']))
    receipts = {}
    for match in re.finditer(r'CSC_AI_CUSTOMER_RECEIPT turn=\d+ version=(\d+) player=(\d+) city=(\d+) '
                             r'district=(\d+) plot=(\d+) result=(\{[^\r\n]*\})', log):
        try:
            receipt = json.loads(match[6])
        except json.JSONDecodeError:
            continue
        receipts[tuple(map(int, match.groups()[:5]))] = receipt
    for match in CUSTOMER_LAND_OFFER.finditer(log):
        turn, player, city, district, plot, price = map(int, match.groups()[:6])
        if player in players and turn <= through:
            # New logs come after a successful commit and carry the exact
            # version. Legacy proposal logs may precede a failed publication
            # or a trimmed entry. Only a native receipt verifies that cell.
            current = versions.get(turn, ())
            committed = int(match[8]) if match[8] else (next(iter(current)) if len(current) == 1 else None)
            receipt = receipts.get((committed, player, city, district, plot))
            offer = dict(turn=turn, player=player, city=city, district=district, plot=plot,
                         invoice=price, delta_q8=int(match[7]) if match[7] else None,
                         version=committed, logged_after_commit=match[8] is not None, receipt=receipt)
            native_offers.append(offer)
            offers[player, city, plot].append((match.start(), offer))
    treasury = {}
    for turn, player, ordinal, before, after in re.findall(
            r'CSC_CUSTOMER_TREASURY\t(\d+)\t(\d+)\t(\d+)\t([-\d.]+)\t([-\d.]+)', log):
        # Subtract the logged decimal balances before converting for JSON.
        # Binary-float subtraction can turn an exact 40 Gold debit into 39.999….
        treasury[int(player), int(ordinal)] = int(turn), float(Decimal(before) - Decimal(after))
    trees = defaultdict(set)
    request_districts = defaultdict(set)
    tree_context, requested_district = None, None
    for fields in tree_rows:
        if (len(fields) < 7 or not fields[0].strip().isdigit() or not fields[1].strip().isdigit()
                or fields[3].strip() != 'Build City District'):
            tree_context, requested_district = None, None
            continue
        context = int(fields[0]), int(fields[1]), fields[2].strip()
        if context != tree_context:
            tree_context, requested_district = context, None
        node = fields[5].strip()
        if node == 'Decode Trigger':
            trigger = re.match(r'District: (DISTRICT_[A-Z0-9_]+);', fields[6].strip())
            requested_district = trigger[1] if trigger else None
        if node != 'Purchase Plot':
            continue
        # Current XP2 prints coordinates, the retained contract state and its
        # ID here. Repetition is a continuing request. Payment is joined from
        # the independent UI events further below.
        request = re.search(r'Purchase (\d+) (\d+): (Submitted|Accepted|Building|Done) on #(\d+)', fields[6])
        if request:
            x, y, state, contract = request.groups()
            turn, player, city = context
            plot_key = player, int(x), int(y)
            row = turn, int(contract), state, city
            trees[plot_key].add(row)
            if requested_district:
                request_districts[plot_key].add((*row, requested_district))
        # A later request requires its own decoded district. Keep the raw
        # contract state when its tree context cannot identify the type.
        requested_district = None
    founded = defaultdict(list)
    completed_links = defaultdict(dict)
    for row in observations:
        if row['kind'] == 'FOUNDATION' and row.get('foundationDateKnown'):
            founded[row['player'], row['city'], row['plot']].append(
                (row.get('foundationTurn', row['turn']), row['district']))
        if (row['kind'] == 'RELATION' and row.get('present') and row.get('quarterComplete')
                and row.get('neighbourComplete') and row.get('role') in ('customer','sales','goodsProvider')
                and row['turn'] <= through):
            key = row['player'], row['neighbourCity'], row['neighbourPlot'], row['neighbourDistrict']
            pair = row['quarter'], row['quarterPlot']
            completed_links[key].setdefault(pair, row['turn'])
    purchases = []
    observed_purchases = []
    ai_purchases = 0
    district_uses = []
    completed_on_purchased_land = []
    purchase_events = list(re.finditer(
        r'CSC_CUSTOMER_PLOT_PURCHASE\t(\d+)\t(\d+)\t(\d+)\t(\d+)\t(\d+)\t(\d+)\t(\d+)(?:\t([^\r\n]+))?', log))
    purchase_ordinals = {(int(m[2]),int(m[3])) for m in purchase_events}
    for match in purchase_events:
        turn, player, ordinal, city, plot, x, y = map(int, match.groups()[:7])
        buyer_label = 'City ' + match[8].strip() if match[8] and match[8].strip() else None
        key = player, city, plot
        if turn > through or player not in players:
            continue
        ai_purchases += 1
        actual = min(((t,d) for t,d in founded[key] if turn-1 <= t <= through), default=None)
        debits = [treasury[player, i][1] for i in (ordinal-1, ordinal+1)
                  if (player,i) in treasury and treasury[player,i][0] == turn
                  and (player,2*i-ordinal) not in purchase_ordinals]
        requests = sorted(r for r in trees[player,x,y] if r[0] <= min(through,turn+1))
        districts = sorted(r for r in request_districts[player,x,y] if r[0] <= min(through,turn+1))
        buyer = plot_buyer_request(requests, districts, buyer_label)
        # Preserve physical acquisition in both arms even if CSC never bid.
        # Treasury changes and request history are observations, with exact
        # expected-invoice and policy-packet checks retained below.
        observed_purchases.append(dict(turn=turn, player=player, city=city, plot=plot,
                                       treasury_changes=debits, request_history=requests,
                                       request_districts=districts, foundation=actual,
                                       buyer_label=buyer_label, **buyer))
        if actual:
            # Include every district founded by the paying city. This lets us
            # see where the ordinary land path succeeds before a partner exists.
            district_uses.append(dict(player=player, city=city, plot=plot, bought=turn,
                                      founded=actual[0], district=actual[1]))
            # Count organic land purchases in either arm. The buyer city, tile
            # and founded district must all match the completed relationship.
            # Customer and sales roles sometimes describe the same two tiles.
            for (quarter, qplot), linked in completed_links[(*key,actual[1])].items():
                if linked >= actual[0]:
                    completed_on_purchased_land.append(dict(player=player, city=city, plot=plot, quarter=quarter,
                        quarter_plot=qplot, district=actual[1], bought=turn, founded=actual[0], linked=linked))
        # The latest native packet can predate execution of a retained request.
        # Report quote age and every offered type if several wanted the tile.
        prior = [offer for offset, offer in offers.get(key, ())
                 if offset < match.start() and offer['turn'] <= turn + 1]
        if not prior:
            continue
        last_turn = max(offer['turn'] for offer in prior)
        quotes = sorted({(offer['district'], offer['invoice']) for offer in prior if offer['turn'] == last_turn})
        # Keep the full observed request history. A contract already accepted
        # before the first offer can stay accepted until its treasury pays.
        accepted = [r[0] for r in requests if r[2]=='Accepted']
        first = buyer['first_observed_buying_city_request']
        typed_matches = []
        if first is not None and buyer['first_observed_request_district']:
            for offer in prior:
                # Keep the first typed request, exact committed packet and
                # Gold debit together. A later receipt cannot turn a retained
                # contract into an earlier CSC-influenced request.
                offered = offer['turn']
                if (names.get(offer['district']) != buyer['first_observed_request_district']
                        or not first-1 <= offered <= first
                        or offer['version'] not in versions[offered]
                        or not offer['logged_after_commit'] or (offer['receipt'] or {}).get('writes', 0) <= 0
                        or debits.count(offer['invoice']) != 1):
                    continue
                key = offer['version'], player, city, offer['district'], plot
                chosen = sorted(observed for observed in choices.get(key, ()) if first-1 <= observed <= first+1)
                typed_matches.append(dict(turn=offered, version=offer['version'], district=offer['district'],
                                          invoice=offer['invoice'], native_choice_readback_turns=chosen))
        purchases.append(dict(turn=turn, player=player, city=city, plot=plot, quote_turn=last_turn,
                              quotes=quotes, district_request_turn=max(accepted,default=None), request_history=requests,
                              request_districts=districts, earlier_offers=prior, treasury_changes=debits,
                              matching_debit=sum(amount in {cost for _,cost in quotes} for amount in debits)==1,
                              foundation=actual, built_offered_type=bool(actual and any(d==actual[1] for d,_ in quotes)),
                              buyer_label=buyer_label, typed_offer_matches=typed_matches, **buyer))
    return dict(observed='CSC_CUSTOMER_LAND_WATCH_INSTALLED' in log, ai_plot_purchases=ai_purchases,
                districts_on_purchased_plots=district_uses, offered_tiles=len(offers), offers=native_offers, purchases=purchases,
                observed_plot_purchases=observed_purchases,
                completed_partners_on_purchased_land=completed_on_purchased_land)


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
    for fault in ('CSC_AI_ECONOMY_FAILED', 'CSC_AI_PLAN_MEMORY_UNAVAILABLE'):
        if fault in log:
            raise ValueError(f'{fault} in {root}')
    observations = parse(log, 'CSC_PLANNING_')
    counts = connection_counts(log, players, through, observations=observations)
    timing = summarise(log, last=through)
    if (not counts['opportunities'] or timing['unobserved_turns'] or timing['incomplete_wall_turns']
            or timing['failed_attempts']):
        raise ValueError(f'Unqualified opportunity or guidance timing coverage in {root}')
    launch, boundary = 'launch-bootstrap.json', 'live-status.json'
    game_wall = (launch_to_endpoint_wall(read(launch), read(boundary), through)
                 if (root/launch).is_file() and (root/boundary).is_file() else None)
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
        types = {r['districtType'] for r in observations if r['kind'] == 'MAPPING'
                 and r['role'] in ('customer','sales','goodsProvider')
                 and r['districtType'] not in ('DISTRICT_CITY_CENTER','DISTRICT_WONDER')}
        types.update(f'DISTRICT_CSC_{title}_QUARTER' for _, title in QUARTER_TITLE.findall(log))
        with build_log.open(encoding='utf-8-sig', newline='') as builds, queue_log.open(encoding='utf-8-sig', newline='') as queue:
            failed_requests = failed_district_requests(csv.reader(builds, skipinitialspace=True),
                csv.reader(queue, skipinitialspace=True), players, types, through)
    competition = bid_competition(log, observations, players, through)
    trees = root / 'AI_Behavior_Trees.csv'
    if trees.is_file():
        with trees.open(encoding='utf-8-sig',newline='') as rows:
            land = customer_land_purchases(log, observations, players, through, csv.reader(rows,skipinitialspace=True))
    else:
        land = customer_land_purchases(log, observations, players, through, ())
    footprints = prospective_footprints(log, observations, players, through, competition)
    priced = prospective_footprints(log, observations, players, through, competition, priced=True)
    endpoint_pairs = endpoint_pair_facts(census, observations, players)
    common, anchored_targets = common_layout_report(log, observations, players, through, endpoint_pairs=endpoint_pairs)
    return dict(counts=counts, customer_land=land, timing=timing['publisher_wall'], game_wall=game_wall,
                endpoint_pair_supply=summarise_endpoint_pairs(endpoint_pairs, include_timing=True),
                common_layouts=common, anchored_targets=anchored_targets,
                native_managed_timing=timing['native_managed_cell_wall'],
                endpoint_suppliers=dict(supply), supplier_losses=dict(supplier_losses),
                supplier_history=supplier_history(observations, players, through),
                prospective_layouts=prospective_layouts(log, observations, players, through),
                prospective_footprints=footprints, prospective_pair_counts=prospective_footprint_counts(footprints),
                priced_footprints=priced, priced_pair_counts=prospective_footprint_counts(priced),
                completed_substitutes=completed_substitute_pairs(priced, observations, through),
                bid_competition=competition,
                failed_district_requests=failed_requests,
                wonder_connections=wonder_connections(log, observations, players, through))


def loadable_layout_endpoint(root, seed, arm):
    """Verify the run's archive and leave a named turn-250 save in Load Game.

    Civ can withhold manual saving on an inactive player turn. The controller
    then archives the held game's autosave before releasing the session. The
    original autosave slot can rotate, so copy from the verified archive and
    keep the player's inspectable copy independent of the research archive.
    """
    from driver import load, sha
    import shutil
    if (root / 'checkpoint.json').exists():
        receipt = load(root / 'checkpoint.json')
        archive, native = (Path(receipt[key]) for key in ('archive', 'native_save'))
        if (receipt['turn'] != 250 or not receipt['verified'] or archive.parent.resolve() != root.resolve()
                or not native.is_file() or sha(archive) != receipt['sha256'] or sha(native) != receipt['sha256']):
            raise ValueError(f'Missing matching archived and Load Game endpoint for {arm}')
        return str(native)

    receipt = load(root / 'completed-via-autosave.json')
    archive, source = Path(receipt['archive']), Path(receipt['source'])
    digest = receipt['sha256']
    if (receipt['status'] != 'archived' or receipt['turn'] != 250 or receipt['verified_turn'] != 250
            or not receipt['native_closed_verified'] or archive.resolve() != (root/'endpoint-autosave/source-250.Civ6Save').resolve()
            or source.parent.name.lower() != 'auto' or not source.parent.parent.is_dir()
            or archive.stat().st_size != receipt['size'] or sha(archive) != digest):
        raise ValueError(f'Unverified turn-250 autosave for {arm}')
    label = 'BASELINE' if arm == 'control' else 'TREATMENT'
    native = source.parent.parent / f'CSC_LAYOUT_{seed}_{label}_T250_{digest[:12]}.Civ6Save'
    try:
        output = native.open('xb')
    except FileExistsError:
        pass
    else:
        try:
            with output, archive.open('rb') as saved:
                shutil.copyfileobj(saved, output)
        except Exception:
            native.unlink()
            raise
    if sha(native) != digest:
        raise ValueError(f'Load Game copy differs from the verified autosave: {native}')
    return str(native)


def paired_full_game_result(control, treatment):
    """Compare matched turn-250 games using their final receipts and archives."""
    from driver import load, sha
    from later_stage_results import comparable_services

    arms = {'control': control, 'treatment': treatment}
    protocols = {}
    saves = {}
    services = {}
    openings = {}
    modules = {}
    for arm, root in arms.items():
        expected = 'off' if arm == 'control' else 'on'
        protocol = load(root / 'protocol.json')
        if (protocol.pop('paired_layout_policy', None) != expected or not protocol['ordinary_setup']
                or not protocol['fresh_game'] or protocol['gameplay_interventions'] or protocol['untuned']
                or not protocol['service_observation']):
            raise ValueError(f'Wrong run protocol for {arm}')
        if arm == 'treatment' and Path(protocol.pop('regression_reference', '')).resolve() != (
                control / 'source.json').resolve():
            raise ValueError('Treatment used a different reference game')
        switch = load(root / 'paired-layout-opening.json')
        if 'layout_defaults' in protocol:
            expected_anchor = arm == 'treatment' or protocol['layout_defaults']['anchored']
            if switch.get('anchored') is not expected_anchor:
                raise ValueError(f'Anchored planner receipt differs from the pinned comparison for {arm}')
        packet = switch['opening']
        if (switch['turn'] != 1 or switch['policy'] != expected or not switch['acknowledged']
                or packet['ready'] != 1 or packet['version'] != 1 or packet['entries'] or packet['faults']):
            raise ValueError(f'Missing turn-one policy receipt for {arm}')
        source = load(root / 'source.json')
        openings[arm] = {key: source[key] for key in ('original_ai', 'map_signature', 'starts', 'units')}
        modules[arm] = {name: row['sha256'] for name, row in load(root / 'loaded-modules.json').items()}
        protocols[arm] = protocol
        saves[arm] = loadable_layout_endpoint(root, protocol['map_seed'], arm)
        services[arm] = load(root / 'observed-services.json')
    if (protocols['control'] != protocols['treatment'] or openings['control'] != openings['treatment']
            or modules['control'] != modules['treatment'] or saves['control'] == saves['treatment']):
        raise ValueError('The full-game arms differ in pins, opening or native binary identity, or share a save')

    # Use only unambiguous Service clocks observed in both arms. This keeps
    # controller sampling gaps from becoming artificial changes in operation.
    operation = comparable_services(services['control'], services['treatment'])
    report = {}
    for arm, root in arms.items():
        result = run_result(root)
        report[arm] = dict(load_game=saves[arm], strong_layouts=result['prospective_pair_counts'],
                           priced_layouts=result['priced_pair_counts'],
                           completed_on_named_substitutes=result['completed_substitutes'],
                           completed_pairs=result['counts']['completed_physical_pairs'],
                           endpoint_pair_supply=result['endpoint_pair_supply'],
                           common_owned_partner_sites=result['common_layouts'],
                           anchored_target_followthrough=result['anchored_targets'],
                           provider_pairs=result['counts']['completed_provider_pairs'],
                           eligible_provider_districts=result['counts']['provider_district_opportunities'],
                           completed_provider_districts=result['counts']['completed_provider_opportunities'],
                           customer_land=result['customer_land'],
                           eligible_missing_partner=result['counts']['district_opportunities'],
                           completed_missing_partner=result['counts']['completed_district_opportunities'],
                           endpoint_suppliers=result['endpoint_suppliers'], supplier_history=result['supplier_history'],
                           supplier_losses=result['supplier_losses'],
                           failed_district_requests=result['failed_district_requests'],
                           # A city can pass over a Quarter for a district on
                           # another tile. Preserve that auction as well as the
                           # narrower same-tile contests in contested_layouts.
                           district_competition={k: result['bid_competition'][k]
                                                 for k in ('outcomes','lost_to','losses')},
                           surveyed_services=operation['stock' if arm == 'control' else 'combined'],
                           guidance_wall=result['timing'], native_managed_wall=result['native_managed_timing'],
                           launch_to_endpoint_wall=result['game_wall'],
                           partner_choices=[dict(quarter_plot=p['quarter']['plot'], quarter=p['quarter']['district'],
                                customer_plot=p['customer']['plot'], customer=p['customer']['district'],
                                player=p['quarter']['player'], choices=p['post_foundation_choices'])
                               for p in (result['priced_footprints'] or result['prospective_footprints'])
                               if any(leg['observed_choices'] for leg in p['post_foundation_choices'].values())],
                           contested_layouts=[pair for pair in (result['priced_footprints'] or result['prospective_footprints']) if any(
                               pair[side]['nearest_loss'] or pair[side]['nearest_cached_loss']
                               for side in ('quarter', 'customer'))])
    data = protocols['control']
    return dict(map=data['map'], map_seed=data['map_seed'], game_seed=data['game_seed'],
                shared_service_turns=len(operation['common_turns']), **report)


if __name__ == '__main__':
    options = argparse.ArgumentParser(description=__doc__)
    options.add_argument('run', type=Path, nargs='+')
    options.add_argument('--paired', action='store_true', help='Verify and compare a full-game control and treatment')
    args = options.parse_args()
    if args.paired:
        if len(args.run) != 2:
            options.error('--paired needs exactly two runs in control, treatment order')
        result = paired_full_game_result(*args.run)
    else:
        result = {str(run): run_result(run) for run in args.run}
    print(json.dumps(result, indent=2))
