"""Verify native luxury experiment evidence, paired geography and continent sums."""
import argparse
import hashlib
import json
from pathlib import Path
import re
from analyze import read


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(out, reference, partial=False):
    analysis = read(out / 'analysis.json')
    paths = sorted(out.glob('luxuries-*/map-*/complete.json'))
    assert partial or len(paths) == 15, len(paths)
    checked = []; controls = []
    for path in paths:
        folder = path.parent; settings = read(folder / 'settings.json'); data = read(folder / 'map.json')
        if partial and 'luxury_types_per_continent' not in settings: continue
        count = settings['luxury_types_per_continent']
        assert count in (4, 5, 6) and settings['group'] == f'luxuries-{count}'
        assert data['turn'] == 1 and len(data['plots']) == 3404 and (data['width'], data['height']) == (74, 46)
        assert settings['speed'] == 'GAMESPEED_ONLINE' and settings['resource_setting'] == 3
        assert settings['csc'] and not settings['tar'] and settings['animal_resources'] == 1
        assert not read(path)['saved']
        markers = re.findall(r'CSC_LUXURY_STUDY_COUNT\s+(\d+)', (folder / 'logs/Lua.log').read_text(encoding='utf-8', errors='replace'))
        assert markers and int(markers[-1]) == count
        lua_log = (folder / 'logs/Lua.log').read_text(encoding='utf-8', errors='replace')
        latest_generation = lua_log[lua_log.rfind('Generating Continents Map'):]
        assert 'Runtime Error:' not in latest_generation, 'Lua error in the captured generation'
        mods = (folder / 'enabled-mods.txt').read_text(encoding='utf-8')
        assert 'c5e66bd1-d804-443b-ac3d-1917a20dba3c' in mods
        # Runtime community-mod assertions are captured in the command, and TAR's
        # strategic-harvest SQL supplies an independent database fingerprint.
        assert 'RESOURCE_IRON' not in {r['resource'] for r in data['harvests']}
        errors = [l for l in (folder / 'logs/Database.log').read_text(encoding='utf-8', errors='replace').splitlines() if '[Gameplay]' in l and 'ERROR' in l]
        assert not errors, errors
        for i, p in enumerate(data['plots']):
            assert p['index'] == i and p['x'] == i % 74 and p['y'] == i // 74
            assert isinstance(p['continent'], int) and isinstance(p['river'], bool) and isinstance(p['lake'], bool)
            for n in p['neighbors']: assert i in data['plots'][n]['neighbors']
        summary = next(m for m in analysis['maps'] if m['group'] == settings['group'] and m['map'] == settings['map_number'])
        whole = summary['continents'][0]; regions = summary['continents'][1:]
        assert whole['land_tiles'] == sum(c['land_tiles'] for c in regions)
        for q in whole['quarters']:
            for metric in ('land_base', 'land_both', 'common_clearable_base', 'common_clearable_both', 'harvest_aware_base', 'harvest_aware_both'):
                assert q[metric] == sum(next(r for r in c['quarters'] if r['quarter'] == q['quarter'])[metric] for c in regions)
            assert q['common_clearable_both'] <= q['common_clearable_base'] <= q['land_base']
        if count == 4:
            old = read(reference / 'vanilla-abundant' / f"map-{settings['map_number']:02d}" / 'map.json')
            same = {k: sum(a.get(k) == b.get(k) for a, b in zip(data['plots'], old['plots'])) for k in ('terrain', 'feature', 'resource')}
            assert all(v == 3404 for v in same.values()), same
            controls.append({'map': settings['map_number'], **same})
        checked.append({'group': settings['group'], 'map': settings['map_number'], 'continents': len(regions), 'gameplay_sql_errors': len(errors), 'source_sha256': sha(folder / 'map.json')})
    for row in analysis['paired_terrain_comparisons']:
        assert row['same_terrain'] == row['plots'] and row['same_continent'] == row['plots'], row
        # Starting-position normalization follows resources and may alter a feature.
    original = read(out / 'map-script-provenance.json')
    assert sha(Path(original['original'])) == original['original_sha256']
    assert sha(Path(original['experiment'])) == original['experiment_sha256']
    installed = Path.home() / "Documents/My Games/Sid Meier's Civilization VI/Mods/Civ Supply Chains"
    hashes = read(out / 'installed-gameplay-hashes.json')
    assert all(sha(installed / p) == digest for p, digest in hashes.items())
    result = {'passed': True, 'maps': len(checked), 'tiles': len(checked) * 3404, 'controls_match_prior_survey': controls,
              'paired_geography': analysis['paired_terrain_comparisons'], 'unchanged_installed_csc_files': len(hashes), 'checked': checked}
    (out / 'validation.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in result.items() if k not in ('checked', 'paired_geography', 'controls_match_prior_survey')}))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--output', type=Path, required=True)
    p.add_argument('--reference', type=Path, required=True); p.add_argument('--allow-partial', action='store_true')
    a = p.parse_args(); verify(a.output, a.reference, a.allow_partial)
