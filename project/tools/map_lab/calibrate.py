"""Calibrate offline resource emulation against read-only native phase captures.

Replay of recorded RNG is diagnostic: it is not an offline Civ RNG implementation.
The phase snapshots isolate start normalization from resource placement.
"""
import argparse
from collections import Counter, defaultdict
import copy
import hashlib
import json
from pathlib import Path
import re
import sqlite3
from offline import OfflineWorld, read, write


def extract(log):
    text = log.read_text(encoding='utf-8', errors='replace')
    if 'CSC_CAL_END' not in text: return None
    block = text[text.rfind('CSC_CAL_BEGIN'):]
    if 'CSC_CAL_END' not in block: return None
    chunks = defaultdict(dict)
    for kind, part, payload in re.findall(r'CSC_CAL_DATA\t([^\t]+)\t(\d+)\t([^\r\n]*)', block):
        chunks[kind][int(part)] = payload
    raw = {k: ''.join(parts[i] for i in sorted(parts)) for k, parts in chunks.items()}
    output = {}
    for phase in ('pre', 'resources', 'starts'):
        rows = [r.split('|') for r in raw[phase].split(';') if r]
        assert len(rows) == 3404 and all(len(r) == 7 for r in rows), (phase, len(rows))
        output[phase] = rows
    output['rng'] = [r.split('|', 2) for r in raw['rng'].split(';') if r]
    output['lua_version'] = re.search(r'CSC_CAL_BEGIN[^\r\n]*(Lua [\d.]+)', block).group(1) if re.search(r'CSC_CAL_BEGIN[^\r\n]*(Lua [\d.]+)', block) else None
    output['placements'] = [r.split('|') for r in raw.get('placements', '').split(';') if r]
    output['adjacency'] = [r.split('|') for r in raw.get('adjacency', '').split(';') if r]
    output['sorts'] = [r.split('|') for r in raw.get('sorts', '').split(';') if r]
    output['eligibility'] = [r.split('|') for r in raw.get('eligibility', '').split(';') if r]
    output['continent_order'] = [int(i) for i in raw['continents'].strip(';').split('|')]
    output['continent_plots'] = {}
    for key, payload in raw.items():
        if key.startswith('plots_'):
            values = [int(i) for i in payload.strip(';').split('|')]
            expected = [int(r[0]) for r in output['pre'] if int(r[4]) == int(key[6:])]
            if set(values) == set(expected): output['continent_plots'][key[6:]] = values
    return output


def phase_map(native, rows):
    data = copy.deepcopy(native)
    for p, r in zip(data['plots'], rows):
        assert p['index'] == int(r[0])
        p['terrain'] = r[1]
        for field, value in [('feature', r[2]), ('resource', r[3])]:
            if value: p[field] = value
            else: p.pop(field, None)
        p.update(continent=int(r[4]), river=r[5] == '1', lake=r[6] == '1')
    return data


def run(args):
    args.output.mkdir(parents=True, exist_ok=True)
    profile = args.output / 'rule-profile.sqlite'
    if not profile.exists():
        with sqlite3.connect(args.database.resolve().as_uri() + '?mode=ro', uri=True) as src, sqlite3.connect(profile) as dst: src.backup(dst)
    results = []
    for complete in sorted(args.study.glob('luxuries-*/map-*/complete.json')):
        folder = complete.parent; settings = read(folder / 'settings.json')
        if 'luxury_types_per_continent' not in settings: continue
        captures = extract(folder / 'logs/Lua.log')
        if not captures: continue
        native = read(folder / 'map.json'); initial = phase_map(native, captures['pre'])
        reference = phase_map(native, captures['resources'])
        final = phase_map(native, captures['starts'])
        before = Counter(p.get('resource') for p in reference['plots'] if p.get('resource'))
        after = Counter(p.get('resource') for p in final['plots'] if p.get('resource'))
        row = {'group': settings['group'], 'map': settings['map_number'], 'rng_draws': len(captures['rng']),
               'native_lua_version': captures['lua_version'],
               'pre_resource_tiles': sum(bool(p.get('resource')) for p in initial['plots']),
               'resource_phase_tiles': sum(before.values()), 'post_start_tiles': sum(after.values()),
               'start_changed_resource_tiles': sum(p.get('resource') != q.get('resource') for p, q in zip(reference['plots'], final['plots'])),
               'post_start_to_turn1_resource_changes': sum(p.get('resource') != q.get('resource') for p, q in zip(final['plots'], native['plots'])),
               'start_resource_delta': {k: after[k] - before[k] for k in sorted(before.keys() | after.keys()) if before[k] != after[k]},
               'native_continent_order': captures['continent_order'], 'captured_continent_plot_orders': len(captures['continent_plots'])}
        world = OfflineWorld(initial, profile, args.game_root, args.workshop_root, 12345, 3, args.lua_dependencies, lua_backend=args.lua_backend)
        row['emulator_lua_backend'] = args.lua_backend
        cursor = [0]
        def recorded_random(n, reason=''):
            i = cursor[0]
            if i >= len(captures['rng']): raise RuntimeError(f'Native RNG trace exhausted at draw {i}')
            maximum, value, label = captures['rng'][i]
            if int(n) != int(float(maximum)) or str(reason) != label:
                raise RuntimeError(f'RNG divergence at draw {i}: emulator ({int(n)}, {reason}) vs native ({maximum}, {label})')
            cursor[0] += 1
            return int(value)
        world.lua.globals().OFFLINE_RANDOM = recorded_random
        placements = []
        world.lua.globals().OFFLINE_PLACEMENT = lambda i, r, count: placements.append([str(i), r, str(count), str(cursor[0])])
        sort_cursor = [0]
        if args.reference_sorts and captures['sorts']:
            def reference_sort(t):
                if sort_cursor[0] >= len(captures['sorts']): raise RuntimeError('Native sort trace exhausted')
                _, before_text, after_text = captures['sorts'][sort_cursor[0]]
                before = {int(i): float(score) for i, score in (v.split(':') for v in before_text.split(','))}
                actual = {int(t[i].MapIndex): float(t[i].Score) for i in range(1, len(t) + 1)}
                if before.keys() != actual.keys() or any(abs(actual[i] - score) > 1e-6 for i, score in before.items()):
                    raise RuntimeError(f'Sort input divergence at sort {sort_cursor[0]}')
                sort_cursor[0] += 1
                return world.lua.table_from({int(i): rank for rank, i in enumerate(after_text.split(','))})
            world.lua.globals().OFFLINE_REFERENCE_SORT = reference_sort
            world.lua.execute('''local original=table.sort;table.sort=function(t,compare)
                if type(t[1])=='table' and t[1].MapIndex~=nil and t[1].Score~=nil then
                    local rank=OFFLINE_REFERENCE_SORT(t);original(t,function(a,b)return rank[a.MapIndex]<rank[b.MapIndex] end)
                else original(t,compare) end
            end''')
        try:
            emulated = world.run('stock', settings['luxury_types_per_continent'])
            row['same_resource_tiles_with_recorded_rng'] = sum(p.get('resource') == q.get('resource') for p, q in zip(emulated['plots'], reference['plots']))
            row['rng_trace_consumed'] = cursor[0]
        except Exception as exc:
            row['replay_divergence'] = str(exc).split('\n')[0]
            row['rng_trace_consumed'] = cursor[0]
        row['emulated_placements_before_stop'] = len(placements)
        row['reference_sorts_consumed'] = sort_cursor[0]
        if captures['placements']:
            for i, (actual, expected) in enumerate(zip(placements, captures['placements'])):
                if actual != expected:
                    row['first_placement_difference'] = {'event': i, 'emulator': actual, 'native': expected}
                    break
            else: row['placements_match_prefix'] = len(placements)
        # Independent native API samples expose placement-rule approximation errors.
        world = OfflineWorld(initial, profile, args.game_root, args.workshop_root, 12345, 3, args.lua_dependencies, lua_backend=args.lua_backend)
        world.bootstrap(); mismatches = []; checked = 0
        evaluate = world.lua.eval('function(i,r,existing) local p=Map.GetPlotByIndex(i);p.resource=existing;return ResourceBuilder.CanHaveResource(p,GameInfo.Resources[r].Index) end')
        for index, resource, expected, occupied in captures['eligibility']:
            actual = bool(evaluate(int(index), resource, occupied or None)); checked += 1
            if actual != (expected == '1'):
                p = initial['plots'][int(index)]
                mismatches.append({'plot': int(index), 'resource': resource, 'native': expected == '1', 'emulator': actual,
                                   'terrain': p['terrain'], 'feature': p.get('feature'), 'river': p['river'], 'lake': p['lake'], 'occupied': occupied or None})
        row['eligibility_samples'] = checked; row['eligibility_mismatches'] = len(mismatches)
        occupied = {p['index']: p.get('resource') for p in initial['plots']}; event = 0; adjacency_errors = []
        for index, expected, events in captures['adjacency']:
            while event < int(events):
                plot, resource, _, _ = captures['placements'][event]
                occupied[int(plot)] = None if resource == 'NONE' else resource; event += 1
            actual = sum(bool(occupied[n]) for n in initial['plots'][int(index)]['neighbors'])
            if actual != int(expected): adjacency_errors.append({'plot': int(index), 'native': int(expected), 'neighbor_count': actual, 'placement_events': event})
        row['adjacency_samples'] = len(captures['adjacency']); row['adjacency_mismatches'] = len(adjacency_errors)
        sort_errors = []
        sort_test = world.lua.eval('function(rows) table.sort(rows,function(a,b)return a.Score>b.Score end);local out={};for _,r in ipairs(rows)do out[#out+1]=r.MapIndex end;return table.concat(out,",") end')
        for sort_id, before_text, expected in captures['sorts']:
            parsed = [v.split(':') for v in before_text.split(',')]
            actual = sort_test(world.lua.table_from([world.lua.table_from({'MapIndex': int(i), 'Score': float(s)}) for i, s in parsed]))
            if actual != expected: sort_errors.append({'sort': int(sort_id), 'entries': len(parsed), 'repeated_scores': len(parsed) - len({s for _, s in parsed})})
        row['sort_samples'] = len(captures['sorts']); row['sort_order_mismatches'] = len(sort_errors)
        write(args.output / settings['group'] / f"map-{settings['map_number']:02d}.json", {'summary': row, 'eligibility_mismatches': mismatches, 'adjacency_mismatches': adjacency_errors, 'sort_mismatches': sort_errors, 'capture': captures})
        results.append(row)
    totals = {'native_cases': len(results), 'eligibility_samples': sum(r['eligibility_samples'] for r in results),
              'eligibility_mismatches': sum(r['eligibility_mismatches'] for r in results),
              'adjacency_samples': sum(r['adjacency_samples'] for r in results),
              'adjacency_mismatches': sum(r['adjacency_mismatches'] for r in results),
              'sort_samples': sum(r['sort_samples'] for r in results),
              'sort_order_mismatches': sum(r['sort_order_mismatches'] for r in results),
              'exact_resource_phase_cases': sum(r.get('same_resource_tiles_with_recorded_rng') == 3404 for r in results)}
    write(args.output / 'analysis.json', {**totals, 'terrain_generation_tested': False, 'rng_implementation_tested': False,
          'recorded_native_sort_replay': args.reference_sorts, 'lua_backend': args.lua_backend,
          'rule_profile_sha256': hashlib.sha256(profile.read_bytes()).hexdigest(), 'cases': results})
    print(json.dumps(totals))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('study', 'database', 'game-root', 'workshop-root', 'lua-dependencies', 'output'): p.add_argument('--' + name, type=Path, required=True)
    p.add_argument('--lua-backend', choices=('lua51','lua52','lua53','lua54','lua55','luajit20','luajit21'), default='lua51')
    p.add_argument('--reference-sorts', action='store_true', help='Diagnostic only: replay captured native sort orders as well as RNG')
    run(p.parse_args())
