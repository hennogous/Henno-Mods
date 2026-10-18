"""Independently check native helper artifacts and replay native-backed decisions."""
import argparse
from collections import Counter
import copy
import json
from pathlib import Path
import re
from native_assist import NativeRules
from assist import Helper, read
from continent_analysis import continent_census
from native_assist import sha, write


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--bundle', type=Path, required=True)
    args = p.parse_args(); bundle = read(args.bundle)
    records = []; total_checks = 0; total_mismatches = 0
    for i in range(1, 6):
        folder = args.output / 'csc-helper-native' / f'map-{i:02d}'
        assert read(folder / 'complete.json')['native_helper_verified']
        before = read(folder / 'before.json'); after = read(folder / 'map.json')
        plan = read(folder / 'native-plan.json'); entry = read(folder / 'viewer-map.json')
        control = next(m for m in bundle['maps'] if m['id'] == f'luxuries-4-{i}')
        assert before['turn'] == after['turn'] == 1
        assert len(before['plots']) == len(after['plots']) == 3404
        assert not any(read(folder / 'control-comparison.json').values())
        assert entry['source_sha256'] == sha(folder / 'map.json')
        before_census = continent_census(before, plan['definitions'])
        assert entry['assistance']['before_continents'] == before_census
        assert entry['continents'] == continent_census(after, plan['definitions'])
        eligibility = read(folder / 'native-eligibility.json')
        preview = next(m for m in bundle['maps'] if m['id'] == f'csc-assist-{i}')
        preview_legal = sum(a['plot'] in eligibility['eligible'][a['resource']] for a in preview['assistance']['additions'])
        rules = NativeRules({r: {'Frequency': f} for r, f in eligibility['frequencies'].items()}, eligibility['eligible'])
        source = {**copy.deepcopy(control), 'data': before, 'settings': read(folder / 'settings.json'),
                  'continents': before_census, 'source_sha256': sha(folder / 'before.json')}
        helper = Helper(source, rules, plan['assistance']['seed']); repeated = helper.run()
        assert repeated == plan, 'Saved native eligibility must reproduce the exact decision trace'
        assert after['plots'] == plan['data']['plots']
        changes = {a['plot']: a for a in entry['assistance']['additions']}
        assert len(changes) <= 10
        assert max(Counter(a['continent'] for a in changes.values()).values(), default=0) <= 4
        for old, new in zip(before['plots'], after['plots']):
            if old['index'] not in changes: assert old == new
            else:
                a = changes[old['index']]
                assert not old.get('resource') and a['resource'] == new['resource']
                assert old['index'] in rules.eligible[a['resource']]
                assert {k: v for k, v in old.items() if k != 'resource'} == {k: v for k, v in new.items() if k != 'resource'}
                assert a['center'] in helper.sites()[a['continent'], a['quarter']]
        old_base = Helper(source, rules).sites(mode='base'); base = helper.sites(mode='base'); both = helper.sites()
        for key, original in helper.baseline_sites.items():
            assert not original or both[key]
            assert not old_base[key] or base[key]
        mismatches = read(folder / 'eligibility-comparison.json')
        starts = set(after.get('starting_plots', []))
        explained = sum(m['plot'] in starts and not m['native'] for m in mismatches['mismatches'])
        if starts: assert explained == len(mismatches['mismatches']), 'Additional unexplained native habitat restrictions'
        # Every intended placement went through the native recheck and readback.
        transcripts = list((args.output / 'commands').glob(f'*-apply-helper-{i}.txt'))
        assert len(transcripts) == 1
        transcript = transcripts[0].read_text(encoding='utf-8')
        applied = {(int(m[0]), m[1]) for m in re.findall(r'CSCH_PLACED\s+(\d+)\s+(RESOURCE_\w+)', transcript)}
        assert applied == {(a['plot'], a['resource']) for a in changes.values()}
        assert re.search(r'CSCH_APPLIED\s+' + str(len(changes)) + r'\s+1', transcript)
        total_checks += eligibility['checks']; total_mismatches += len(mismatches['mismatches'])
        records.append({'map': i, 'deposits': len(changes), 'native_checks': eligibility['checks'],
                        'offline_rule_mismatches': len(mismatches['mismatches']),
                        'starting_plot_flags_captured': bool(starts), 'mismatches_explained_by_starts': explained,
                        'preview_deposits_native_legal': preview_legal, 'preview_deposits': len(preview['assistance']['additions']),
                        'preview_tile_differences': entry['native_comparison']['resource_tile_differences']})
    installed = Path.home() / "Documents/My Games/Sid Meier's Civilization VI/Mods/Civ Supply Chains"
    original = read(args.output / 'installed-gameplay-hashes.json')
    assert all(sha(installed / filename) == digest for filename, digest in original.items())
    prefs = read(args.output / 'preferences-restored.json'); assert prefs['verified']
    result = {'passed': True, 'maps': 5, 'native_tiles': 17020, 'turns_advanced': 0,
              'native_eligibility_checks': total_checks, 'offline_rule_mismatches': total_mismatches,
              'installed_csc_files_unchanged': len(original), 'preferences_verified': prefs,
              'results': records, 'method': 'Shared Python selection/RNG; live native eligibility and native setters at turn 1. Automatic startup mod execution is not tested.'}
    write(args.output / 'validation.json', result)
    print(json.dumps({k: v for k, v in result.items() if k not in ('preferences_verified', 'results')}))


if __name__ == '__main__': main()
