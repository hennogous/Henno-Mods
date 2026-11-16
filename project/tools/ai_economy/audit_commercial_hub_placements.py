"""Offline Hub/Quarter footprint audit; never connect to a running game.

Join the completed run's foundation/choice records to the passive district
history and a previously archived native map survey. Candidate ownership comes
from same-turn Quarter opportunity reads, not from later territorial expansion.
This identifies plausible alternative footprints; it does not reconstruct a
missing historical native legality test, adjacency quote or losing score cell.
Endpoint terrain/resources are explicitly labelled as endpoint observations.
Ordinary-adjacency reconstructions belong in the accompanying dated report.
"""
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import re


def fields(line):
    return dict(re.findall(r'(\w+)=([^\s]+)', line))


def audit(run, survey):
    run, survey = Path(run), Path(survey)
    results = json.loads((run / 'planning-results.json').read_text(encoding='utf-8'))
    hubs = [c for c in results['constructions'] if c['districtType'] == 'DISTRICT_COMMERCIAL_HUB'
            and c['player'] in range(1, 6)]
    plots, cities, paths = {}, {}, []
    for line in survey.read_text(encoding='utf-8').splitlines():
        if 'CSC_COAST_MAP\t' in line:
            f = line.split('CSC_COAST_MAP\t', 1)[1].split('\t')
            plots[int(f[0])] = f
        elif 'CSC_COAST_CITY\t' in line:
            f = line.split('CSC_COAST_CITY\t', 1)[1].split('\t')
            cities[int(f[0]), int(f[1])] = f
        elif 'CSC_COAST_BASE\t' in line:
            f = line.split('CSC_COAST_BASE\t', 1)[1].split('\t')
            for pair in f[6].split(',') if len(f) > 6 and f[6] else []:
                q, water = map(int, pair.split(':'))
                paths.append((int(f[0]), q, water))
    width = max(int(p[1]) for p in plots.values()) + 1

    def distance(a, b):
        x, y = map(int, plots[a][1:3]); u, v = map(int, plots[b][1:3])
        # The recorded Continents world wraps east/west, not north/south.
        dr = y - v
        return min(max(abs(dq), abs(dr), abs(dq + dr)) for dq in
                   [x - (y-y % 2)//2 - (u+shift) + (v-v % 2)//2
                    for shift in (-width, 0, width)])

    # Validate parity/wrap conventions against actual native adjacent-plot paths
    # archived by the survey, rather than a test that mirrors this formula.
    assert paths and all(distance(base, q) == distance(q, water) == 1
                         for base, q, water in paths)
    histories, opportunities, offers = defaultdict(list), {}, []
    clocks = {(c['player'], c['city'], (c.get('nativeChoice') or {}).get('turn', c['foundationTurn']))
              for c in hubs}
    player_clocks = {(pid, turn) for pid, _, turn in clocks}
    event_names = {'FOUNDATION', 'FIRST_OBSERVED', 'OWNERSHIP', 'COMPLETION',
                   'COMPLETION_REVERSED', 'PILLAGED', 'REPAIRED', 'REMOVED'}
    for line in (run / 'Lua.log').open(encoding='utf-8', errors='replace'):
        match = re.search(r'CSC_PLANNING_([A-Z_]+)\t', line)
        if match and match[1] in event_names | {'OPPORTUNITY'}:
            f = fields(line[match.end():]); t = int(f['turn'])
            if match[1] in event_names:
                f['event'] = match[1]; histories[int(f['plot'])].append(f)
            elif (int(f['player']), t) in player_clocks:
                opportunities[int(f['player']), int(f['city']), t, int(f['plot'])] = f
        elif 'CSC_AI_CUSTOMER_FUTURE_BID ' in line:
            f = fields(line)
            if f.get('district') == '6': offers.append(f)

    def state(plot, turn):
        prior = [f for f in histories.get(plot, []) if int(f['turn']) <= turn]
        return max(prior, key=lambda f: (int(f['turn']), int(f['sequence']))) if prior else None

    scopes = defaultdict(list)
    for (pid, city, turn, plot), f in opportunities.items():
        scopes[pid, turn, plot].append(dict(city=city, owner=int(f['owner']),
                                          frontier=f.get('frontier'), protected=f.get('protected')))
    rows = []
    for hub in hubs:
        pid, city, target = hub['player'], hub['city'], hub['plot']
        turn = (hub.get('nativeChoice') or {}).get('turn', hub['foundationTurn'])
        city_row = cities[pid, city]
        center = next(i for i, f in plots.items() if f[1:3] == city_row[3:5])
        quarters = []
        for plot in histories:
            s = state(plot, turn)
            if s and s['event'] != 'REMOVED' and s.get('districtType', '').startswith('DISTRICT_CSC_') \
                    and s.get('player') == str(pid) and s.get('complete') == 'true' \
                    and distance(center, plot) <= 4:
                quarters.append(plot)
        candidates = {}
        for q in quarters:
            for plot, f in plots.items():
                if plot == target: continue
                if distance(plot, q) != 1 or distance(center, plot) > 3: continue
                if f[5] == 'true' or f[7] == 'true': continue  # fixed water/impassable geography
                s = state(plot, turn)
                if s and s['event'] != 'REMOVED': continue
                # An unexplained endpoint footprint cannot establish vacancy
                # at the decision. A recorded later foundation can do so.
                if not s and f[10] != 'NONE' and not any(h['event'] == 'FOUNDATION'
                                                       for h in histories.get(plot, [])): continue
                op = opportunities.get((pid, city, turn, plot))
                row = candidates.setdefault(plot, dict(plot=plot, quarters=[],
                    endpoint_resource=f[11], endpoint_feature=f[4], endpoint_district=f[10],
                    endpoint_owner=int(f[8]), endpoint_city=int(f[9]),
                    same_turn_opportunity=op, historical_native_hub_legality='unrecorded',
                    same_turn_city_scopes=scopes.get((pid, turn, plot), []),
                    historical_hub_adjacency='unrecorded', historical_hub_total='unrecorded'))
                row['quarters'].append(q)
        rows.append(dict(player=pid, city=city, name=city_row[2], plot=target, choice_turn=turn,
            foundation_turn=hub['foundationTurn'], chosen_gold=hub['uiAdjacency']['YIELD_GOLD'],
            chosen_utility=(hub.get('nativeChoice') or {}).get('totalQ8', 0)/256,
            nearby_completed_quarters=sorted(quarters),
            chosen_adjacent_quarters=[q for q in quarters if distance(q, target) == 1],
            alternative_footprints=list(candidates.values()),
            lua_hub_offers_in_choice_window=[f for f in offers if int(f['player']) == pid
                and int(f['city']) == city and abs(int(f['turn'])-turn) <= 1]))
    return dict(run=str(run), survey=str(survey), endpoint=250, tracked_ai=[1,2,3,4,5],
        map_geometry_verified_native_paths=len(paths), east_west_wrap=True,
        lua_sha256=hashlib.sha256((run/'Lua.log').read_bytes()).hexdigest(),
        survey_sha256=hashlib.sha256(survey.read_bytes()).hexdigest(), hubs=rows)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--survey', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.run, args.survey)
    args.output.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(f"Audited {len(result['hubs'])} Hub foundations; geometry matches "
          f"{result['map_geometry_verified_native_paths']} native paths")
