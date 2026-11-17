"""Audit one district offer against a closed game's native decision journal.

Diagnostic only: archived main-CSC proposals -> CE score writes -> actual joint
district selections -> requests/physical foundations. This never connects to a
game or changes policy. Native scores are Q8 (256 per utility); adjacency is a
separate physical rating. A published offer is not substituted for a consumed
score. The exact comparison requires a same-generation write before the winner's
journal ordinal. Missing coverage stays unknown rather than borrowing a later
write or an earlier packet's cached value.
"""
import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import re


def fields(line):
    result = {}
    for key, value in re.findall(r'(\w+)=([^\s]+)', line):
        result[key] = int(value) if re.fullmatch(r'-?\d+', value) else value
    return result


def join_decisions(best, selections, writes):
    """Pair two independent streams by order AND identity, then join fresh cells.

    CE drains can label a comparison on the next round. The native observer has
    the actual call turn. Require an ordered bijection of district/plot/value;
    equal numbers on nearby turns alone cannot identify a decision. The export
    retains only the last final write per cell/drain, so a write after a winner
    is insufficient to reconstruct that comparison and is deliberately omitted.
    """
    if len(best) != len(selections):
        raise ValueError('Native selection and CE winner stream coverage differs')
    comparisons = []
    for journal, call in zip(best, selections):
        if (journal['district'], journal['plot'], journal['result']) != (
                call['district'], call['plot'], call['totalQ8']):
            raise ValueError('Native selection and CE winner stream order/identity differs')
        if journal['observedTurn'] < call['turn']:
            raise ValueError('CE drain precedes its native call')
        prior = [row for row in writes if row['generation'] == journal['generation']
                 and row['nativeOrdinal'] < journal['nativeOrdinal']]
        write = max(prior, key=lambda row: row['nativeOrdinal']) if prior else None
        comparisons.append(dict(
            callTurn=call['turn'], observedTurn=journal['observedTurn'],
            generation=journal['generation'], version=journal['version'],
            winnerDistrict=call['district'], winnerPlot=call['plot'], winnerQ8=call['totalQ8'],
            winnerOrdinal=journal['nativeOrdinal'], exactFreshWrite=write is not None,
            candidateQ8=write['result'] if write else None,
            candidateNativeBeforeQ8=write.get('base') if write else None,
            candidateReservation=write.get('reservationId') if write else None,
            # eligible describes the native plot row, not all later CanZone gates.
            nativeRowEligible=write.get('eligible') if write else None,
            writeOrdinal=write['nativeOrdinal'] if write else None))
    return comparisons


def analyse(root, player, city, district, plot, city_name):
    root = Path(root)
    closed = json.loads((root/'session-closed.json').read_text())
    if not closed['verified'] or closed['native_exit_code'] != 0:
        raise ValueError('Require a cleanly closed source game')
    writes, best, bids, opportunities, receipts, withdrawals = [], [], [], [], {}, []
    markers = ('CSC_QUARTER_WATCH_WRITE\t', 'CSC_PLANNING_NATIVE_BEST\t',
               'CSC_AI_SPATIAL_BID ', 'CSC_PLANNING_OPPORTUNITY\t',
               'CSC_AI_ECONOMY_RECEIPT ', 'CSC_AI_QUARTER_WITHDRAWAL_PROPOSED ')
    for line in (root/'Lua.log').open(encoding='utf-8-sig'):
        marker = next((value for value in markers if value in line), None)
        if marker is None:
            continue
        row = fields(line)
        if (row.get('player'), row.get('city')) != (player, city):
            continue
        if marker == markers[1]:
            best.append(row)
            continue
        if (row.get('district'), row.get('plot')) != (district, plot):
            continue
        if marker == markers[0]:
            writes.append(row)
        elif marker == markers[2]:
            bids.append(row)
        elif marker == markers[3]:
            opportunities.append(row)
        elif marker == markers[5]:
            withdrawals.append(row)
        else:
            value = json.loads(line.split(' result=', 1)[1])
            previous = receipts.setdefault(row['version'], {})
            # Receipt counters accumulate within a packet. Count each native
            # write once even when several readbacks report the same activity.
            for key in ('staged', 'scoreAttempts', 'writes', 'cacheReads', 'siteWins'):
                previous[key] = max(previous.get(key, 0), value.get(key, 0))
    selections = []
    for line in (root/'economy-savings.ndjson').open(encoding='utf-8-sig'):
        row = json.loads(line)
        if (row.get('player'), row.get('city')) == (player, city) and row['kind'] == 'district-selection':
            selections.append(row)
    comparisons = join_decisions(best, selections, writes)
    catalog = {}
    for line in (root/'loaded-district-catalogue.txt').read_text(encoding='utf-8-sig').replace('\0', '').splitlines():
        if 'CSC_DISTRICT_CATALOGUE\t' in line:
            payload = line.split('CSC_DISTRICT_CATALOGUE\t', 1)[1].split('\t')
            catalog[int(payload[0])] = payload[1]
    type_name = catalog[district]
    build_rows = [line for line in (root/'AI_CityBuild.csv').read_text(encoding='utf-8-sig').splitlines()
                  if ', '+str(player)+', '+city_name+',' in line]
    requests = [line for line in build_rows if ', SUBMITTED,' in line and type_name in line]
    first_bid = min((row['turn'] for row in bids), default=None)
    production = Counter()
    for row in csv.reader((root/'City_BuildQueue.csv').open(encoding='utf-8-sig'), skipinitialspace=True):
        if len(row) > 3 and row[1] == city_name and first_bid is not None and int(row[0]) >= first_bid:
            production[row[3]] += 1
    planning = json.loads((root/'planning-results.json').read_text())
    foundations = [dict(turn=row['turn'], district=row['districtType'], plot=row['plot'])
                   for row in planning['constructions'] if (row['player'], row['city']) == (player, city)]
    positive = [row for row in comparisons if row['exactFreshWrite'] and row['candidateQ8'] > 0]
    proposals_by_turn = {row['turn']: row for row in bids}
    quoted = [(row, proposals_by_turn[row['version']]) for row in positive
              if row['version'] in proposals_by_turn]
    first_three = next((row['turn'] for row in opportunities if float(row['direct']) >= 3), None)
    changes, previous = [], None
    for row in opportunities:
        state = (row['owner'], row['direct'], row['offered'])
        if state != previous:
            changes.append({key: row.get(key) for key in ('turn', 'owner', 'direct', 'offered', 'bidQ8')})
        previous = state
    return dict(schema='csc-district-followthrough-v1', root=str(root),
        analysis_implementation_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        target=dict(player=player, city=city, district=district, plot=plot, city_name=city_name),
        summary=dict(native_selections=len(selections),
            district_winners=dict(Counter(catalog[row['district']] for row in selections)),
            target_wins=sum(row['district'] == district and row['plot'] == plot for row in selections),
            exact_fresh_comparisons=sum(row['exactFreshWrite'] for row in comparisons),
            positive_fresh_comparisons=len(positive),
            positive_comparisons_with_higher_winner=sum(row['winnerQ8'] > row['candidateQ8'] for row in positive),
            positive_comparisons_matching_published_value=sum(row['candidateQ8'] == bid['finalQ8'] for row, bid in quoted),
            positive_comparisons_with_binding_cap=sum(bid['capAdjustmentQ8'] < 0 for row, bid in quoted),
            # Arithmetic sensitivity only: removing this one cap would leave
            # other proposals, native choices and later behavior unmeasured.
            uncapped_packet_values_exceeding_recorded_winner=sum(
                bid['finalQ8'] - bid['capAdjustmentQ8'] > row['winnerQ8'] for row, bid in quoted),
            pre_replacement_values_above_recorded_winner=sum(
                row['candidateNativeBeforeQ8'] > row['winnerQ8'] for row in positive),
            native_receipt_writes=sum(row.get('writes', 0) for row in receipts.values()),
            first_positive_bid=first_bid, first_geometry_at_least3=first_three,
            submitted_target_type_requests=len(requests),
            target_foundations=sum(row['district'] == type_name and row['plot'] == plot for row in foundations)),
        comparisons=comparisons, proposals=bids, geometry_changes=changes, withdrawals=withdrawals,
        requests=requests, foundations=foundations, production_samples_after_first_bid=dict(production),
        production_sample_scope='City_BuildQueue names cities without player IDs; use the ownership history when applying this summary to a captured city.',
        district_catalog=catalog,
        input_sha256={name: hashlib.sha256((root/name).read_bytes()).hexdigest() for name in
            ('Lua.log', 'economy-savings.ndjson', 'AI_CityBuild.csv', 'City_BuildQueue.csv',
             'planning-results.json', 'loaded-district-catalogue.txt', 'session-closed.json')},
        scope='Recorded same-generation comparisons; score superiority explains these losses. Other rounds and the merits of competing investments remain separate.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('run', 'output'):
        parser.add_argument('--'+name, type=Path, required=True)
    for name in ('player', 'city', 'district', 'plot'):
        parser.add_argument('--'+name, type=int, required=True)
    parser.add_argument('--city-name', required=True)
    args = parser.parse_args()
    result = analyse(args.run, args.player, args.city, args.district, args.plot, args.city_name)
    args.output.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result['summary'], indent=2))
