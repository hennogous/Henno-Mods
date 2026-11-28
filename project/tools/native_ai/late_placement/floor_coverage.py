"""Compare terrain cues on the actual legal alternatives captured at each city review."""
import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass
from itertools import combinations, permutations
import json
from pathlib import Path


@dataclass
class Site:
    plot: int
    rank: int
    unknown: int
    counts: dict

    def delta(self, terrains, weight):
        # A hidden neighbor can match either rewarded terrain, at most once.
        matches = self.unknown + sum(self.counts.get(key, 0) for key in terrains)
        return weight * matches - self.unknown - sum(self.counts.values())


def target(sites, patterns, weight):
    best = None
    for keys in patterns:
        if any(s.delta(keys, weight) >= 0 for s in sites if not s.rank):
            continue
        for s in sites:
            if not s.rank:
                continue
            delta = s.delta(keys, weight)
            if delta >= 0 and (best is None or (s.rank, delta) > best[:2]):
                best = s.rank, delta, s.plot, keys
    return best


def decode(field):
    sites = []
    for item in filter(None, field.split('|')):
        plot, rank, unknown, counts = item.split(':')
        values = dict(pair.split('=') for pair in counts.split(',') if pair)
        counts = {(k if k.startswith('TERRAIN_') else 'TERRAIN_'+k):int(v) for k,v in values.items()}
        sites.append(Site(int(plot), int(rank), int(unknown), counts))
    return sites


def third_target(sites, keys):
    """One or two positive terms, with the remaining terms negative. No floor."""
    best = None
    for terms in combinations(keys,3):
        for solo in terms:
            pair=[k for k in terms if k!=solo]
            for sign in (1,-1):
                def balance(s):
                    v=s.counts.get(solo,0)-sum(s.counts.get(k,0) for k in pair)
                    return sign*v+s.unknown
                if any(balance(s)>0 for s in sites if not s.rank):
                    continue
                for s in sites:
                    value=balance(s)
                    if s.rank and value>0 and (best is None or (s.rank,value)>best[:2]):
                        best=s.rank,value,s.plot,terms,solo,sign
    return best


def compare(log, eligible):
    counts = Counter()
    distinct = defaultdict(set)
    def tally(label, player, city, quarter, plot=None):
        counts[label] += 1
        distinct[label, 'cities'].add((player, city))
        distinct[label, 'city_quarters'].add((player, city, quarter))
        if plot is not None:
            distinct[label, 'targets'].add((quarter, plot))
    for line in log:
        _, sep, fields = line.partition('CSC_LAYOUT_GEOMETRY\t')
        if not sep:
            continue
        turn, player, city, quarter, captured, data = fields.rstrip('\r\n').split('\t')
        key = player, city, quarter
        # Civ's original single-line observer clipped log entries at 2047
        # characters. Even a syntactically valid tail can omit a weak rival.
        if len(line.rstrip('\r\n'))>=2047:
            tally('clipped_reviews_excluded', *key)
            continue
        sites = decode(data)
        tally('reviews', *key)
        if not any(s.rank for s in sites):
            continue
        tally('supplied', *key)
        if all(s.rank for s in sites):
            continue
        keys = sorted(eligible.intersection(k for s in sites if s.rank for k in s.counts))
        single = target(sites, ((k,) for k in keys), 6)
        expected = single[2] if single else -1
        if expected != int(captured):
            raise ValueError(f'Single-cue reproduction failed at {turn} {key}: {expected} vs {captured}')
        if single:
            tally('current_single', *key, single[2])
            tally('through_two_terms', *key, single[2])
            tally('through_three_terms', *key, single[2])
            continue
        # A second terrain can affect only rivals and provide zero matches at
        # the target. Include those terrains for an honest two-weight test.
        keys = sorted(eligible.intersection(k for s in sites if s.plot>=0 for k in s.counts))
        pair = target(sites, combinations(keys, 2), 3)
        if pair:
            tally('through_two_terms', *key, pair[2])
            tally('through_three_terms', *key, pair[2])
            tally('additional_pair', *key, pair[2])
            tally('additional_' + quarter, *key, pair[2])
            if pair[1] > 0:
                tally('additional_above_ordinary', *key, pair[2])
            continue
        best=None
        for a,b in permutations(keys,2):
            def balance(s):
                return s.counts.get(a,0)+s.unknown-s.counts.get(b,0)
            if any(balance(s)>0 for s in sites if not s.rank):
                continue
            for s in sites:
                value=balance(s)
                if s.rank and value>0 and (best is None or (s.rank,value)>best[:2]):
                    best=s.rank,value,s.plot
        if best:
            tally('through_two_terms', *key, best[2])
            tally('through_three_terms', *key, best[2])
            tally('additional_signed_'+quarter, *key, best[2])
            continue
        third=third_target(sites,keys)
        if third:
            tally('through_three_terms', *key, third[2])
            tally('additional_third_'+quarter, *key, third[2])
    return {k:dict(reviews=v, **{s:len(distinct[k,s]) for s in ('cities','city_quarters','targets')})
            for k,v in counts.items()}


if __name__ == '__main__':
    import sqlite3
    from contextlib import closing
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('log', type=Path)
    parser.add_argument('gameplay_database', type=Path)
    args = parser.parse_args()
    with closing(sqlite3.connect(args.gameplay_database.as_uri()+'?mode=ro', uri=True)) as db:
        eligible = {r[0] for r in db.execute('SELECT TerrainType FROM Terrains WHERE NOT Water AND NOT Impassable')}
    with args.log.open(encoding='utf-8-sig', errors='replace') as lines:
        print(json.dumps(compare(lines, eligible), indent=2))
