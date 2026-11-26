"""Read a finished timing pair and summarise the work already logged by CSC.

The engine clocks compare matched turns. The workload counters cover each
whole publication, including turns excluded from the end-to-end timing.
This reader never talks to a running game.
"""

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import re
from statistics import mean, median


EVENT = re.compile(r'\bCSC_AI_([A-Z][A-Z_0-9]+)\s+turn=(\d+)')
CLOCK = re.compile(r'\bCSC_GUIDANCE_CLOCK\s+(\d+)')
FIELD = re.compile(r'\b([A-Za-z][A-Za-z0-9]*)=(-?\d+)(?=[\s,}]|$)')
RECEIPTS = {'ECONOMY_RECEIPT', 'CONNECTION_RECEIPT', 'CUSTOMER_RECEIPT', 'FRONTIER_RECEIPT'}


def read_work(log, endpoint):
    turns = defaultdict(Counter)
    seat_seconds = defaultdict(Counter)
    previous_quote = {}
    ranked = defaultdict(dict)
    last_clock = None
    lines, sizes = Counter(), Counter()
    with log.open('rb') as source:
        for data in source:
            line = data.decode('utf-8', errors='replace')
            mark = CLOCK.search(line)
            if mark:
                last_clock = int(mark[1])
                continue
            match = EVENT.search(line)
            if not match:
                continue
            kind, turn = match[1], int(match[2])
            if not 1 <= turn <= endpoint:
                continue
            lines[kind] += 1
            sizes[kind] += len(data)
            row = {name: int(value) for name, value in FIELD.findall(line[match.end():])}
            clock = turns[turn]
            if kind == 'PROCESSING':
                assert row['wallMicros'] >= 0
                # The clock observer was installed after the publisher. Check
                # actual event order before ascribing a span to interval t.
                if last_clock is not None:
                    assert turn == last_clock + 1
                clock['publisher_us'] += row['wallMicros']
                clock['publications'] += row['published']
            elif kind == 'PLAYER_PROCESSING':
                seat_seconds[turn][row['player']] += row['wallMicros'] / 1e6
                clock['seat_lua_clock_us'] += row['luaClockMicros']
            elif kind == 'JOINT_WORK':
                for field in ('worlds', 'evaluations', 'cacheHits', 'budgetFailures', 'unknown',
                              'routeHits', 'routeMisses', 'routeOverflow'):
                    clock[field] += row[field]
            elif kind == 'ECONOMY_PLAN':
                for field in ('evaluated', 'final', 'quotes'):
                    clock[field] += row[field]
            elif kind == 'QUARTER_WORLD':
                key = tuple(row[field] for field in ('player', 'city', 'district', 'plot'))
                old = previous_quote.get(key)
                if old and old[0] == turn - 1:
                    clock['repeat_sites'] += 1
                    clock['same_bid'] += old[1] == row['bidQ8']
                previous_quote[key] = turn, row['bidQ8']
                clock['quarter_worlds'] += 1
                clock['chains_in_quarter_worlds'] += row['chains']
                clock['nonzero_service_marginals'] += row['serviceQ8'] != 0
            elif kind == 'SPATIAL_BID':
                scope = tuple(row[field] for field in ('player', 'city', 'district'))
                ranked[turn, scope][row['rank']] = row['plot']
            elif kind == 'PLAN_JOURNAL':
                for field in ('records', 'pages', 'confirmed'):
                    clock[field] += row[field]
            elif kind in RECEIPTS:
                receipt = json.loads(line.split('result=', 1)[1])
                clock['staged_receipts'] += int(receipt.get('staged') == 1)
            elif kind == 'BAKERS_DISTRICTS':
                n = row['entries']
                clock['packet_entries'] += n
                clock['peak_entries'] = max(n, clock['peak_entries'])
                # Every successful stage_entry checks each prior key. Count
                # those comparisons separately from native lookups during play.
                clock['staging_key_checks'] += n * (n - 1) // 2
            elif kind == 'SPATIAL_WORK':
                for field in ('maps', 'adjacencyReads', 'options', 'nativeSiteQuotes', 'unavailableSiteQuotes'):
                    clock[field] += row[field]
                elapsed_ms = float(re.search(r'\beconomyMs=(-?[\d.]+)', line)[1])
                if elapsed_ms > 0:
                    clock['quarter_bids_positive_clock_ms'] += elapsed_ms
                else:
                    clock['quarter_bids_without_positive_tick'] += 1
    # Ranks are CSC proposals before packet trimming. Compare only scopes
    # present on adjacent turns so a founding, expiry or first-ever offer
    # cannot be counted as a successful prediction from yesterday's list.
    for (turn, scope), current in ranked.items():
        prior = ranked.get((turn - 1, scope))
        if prior and 1 in current:
            turns[turn]['repeat_rankings'] += 1
            turns[turn]['leader_stayed_first'] += current[1] == prior[1]
            turns[turn]['leader_was_top_two'] += current[1] in prior.values()
    return turns, seat_seconds, lines, sizes


def review(root):
    comparison = json.loads((root / 'comparison.json').read_text(encoding='utf-8-sig'))
    endpoint, arms = comparison['endpoint'], comparison['arms']
    turns, seats, lines, sizes = read_work(Path(arms['on']['evidence']) / 'Lua.log', endpoint)
    assert all(turns[t]['publications'] == 1 for t in range(1, endpoint + 1))
    common = comparison['shared_clean_turns']
    def clocks(arm, interval):
        return [arms[arm]['clean_seconds_by_turn'][str(t)] for t in interval]
    bands = []
    for first in range(1, endpoint + 1, 50):
        last = min(first + 49, endpoint)
        interval = [t for t in common if first <= t <= last]
        whole = [turns[t] for t in range(first, last + 1)]
        bands.append(dict(turns=[first, last], shared=len(interval),
                          off=mean(clocks('off', interval)), on=mean(clocks('on', interval)),
                          publisher=mean(r['publisher_us'] for r in whole) / 1e6,
                          matched_publisher=mean(turns[t + 1]['publisher_us'] for t in interval) / 1e6,
                          worlds_per_turn=mean(r['worlds'] for r in whole),
                          evaluations_per_turn=mean(r['evaluations'] for r in whole),
                          chains_per_quarter_world=sum(r['chains_in_quarter_worlds'] for r in whole)
                          / max(1, sum(r['quarter_worlds'] for r in whole))))
    total, player = Counter(), Counter()
    receipt_visits = 0
    for t, row in turns.items():
        total.update(row)
        player.update(seats[t])
        # ObserveNativeChoices reads the same previous packet as reportReceipts.
        receipt_visits += row['records'] * row['staged_receipts']
    total['peak_entries'] = max(r['peak_entries'] for r in turns.values())
    return dict(bands=bands, common=len(common), totals=total, exact_receipt_record_visits=receipt_visits,
                player_seconds=player, player_share=sum(player.values()) / (total['publisher_us'] / 1e6),
                matched_publisher=mean(turns[t + 1]['publisher_us'] for t in common) / 1e6,
                medians={arm: median(clocks(arm, common)) for arm in arms},
                tagged_lines=sum(lines.values()), tagged_bytes=sum(sizes.values()),
                largest_logs={k: dict(lines=lines[k], bytes=size) for k, size in sizes.most_common(8)})


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    print(json.dumps(review(parser.parse_args().root), indent=2))
