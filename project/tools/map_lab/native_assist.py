"""Fresh native maps plus the shared CSC helper backed by live native APIs.

This is a FireTuner-driven prototype of a post-initialization resource pass,
not an installed Lua startup mod. Selection/RNG remain the preview's Python
implementation; every habitat decision comes from Civ and every deposit is
checked and placed through native APIs. No turns are advanced.
"""
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
import sys
import time
import traceback

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'map_survey'))
from assist import Helper, Rules, SEED, read
from continent_analysis import continent_census
from analyze import analyze_map, write_csv
from build import render

spec = importlib.util.spec_from_file_location('csc_native_assist_survey', HERE.parent / 'map_survey/run.py')
survey = importlib.util.module_from_spec(spec); spec.loader.exec_module(survey)
Survey, write, sha, LOGS = survey.Survey, survey.write, survey.sha, survey.LOGS


class NativeRules:
    def __init__(self, rows, eligible):
        self.resources = rows
        self.eligible = {r: set(indices) for r, indices in eligible.items()}

    def can_place(self, p, resource, plots):
        return not p.get('resource') and p['index'] in self.eligible[resource]


class NativeSurvey(Survey):
    def cmd(self, code, state='GameCore_Tuner', label='command', wait=2, check=True):
        # Retry only reads or failures known to happen before command dispatch.
        for attempt in range(8):
            try: return super().cmd(code, state, label, wait, check)
            except (RuntimeError, KeyError, OSError, EOFError) as exc:
                before_send = isinstance(exc, KeyError) or str(exc) == 'No responsive tuner states'
                read_only = label == 'ready' or label.startswith(('dump-', 'actual-', 'eligibility-'))
                if attempt == 7 or not (before_send or read_only): raise
                if attempt == 0: self.say(f'Transient console reload during {label}; safe retry')
                time.sleep(2)

    def menu(self):
        # Survey.start_map has just exported the untouched map and copied logs.
        if self.pending_folder:
            folder = self.pending_folder
            self.pending_folder = None  # never reapply on cleanup
            self.assist_current(folder)
        super().menu()

    def dump(self, label):
        text = self.cmd((HERE.parent / 'map_survey/dump.lua').read_text(encoding='utf-8'),
                        'CSC_AdjacencyGameplay', 'dump-' + label, wait=5)
        found = re.search(r'CSCMAP_SURVEY=([^\r\n]+)', text); assert found
        data = json.loads(found.group(1)); assert data['turn'] == 1
        return data

    def assist_current(self, folder):
        i = self.number
        control = next(m for m in self.bundle['maps'] if m['group'] == 'luxuries-4' and m['number'] == i)
        preview = next(m for m in self.bundle['maps'] if m['group'] == 'csc-assist' and m['number'] == i)
        before = read(folder / 'map.json'); settings = read(folder / 'settings.json')
        comparison = {key: sum(p.get(key) != q.get(key) for p, q in zip(before['plots'], control['data']['plots']))
                      for key in ('terrain', 'feature', 'resource', 'continent', 'river', 'lake', 'district', 'owner', 'neighbors')}
        write(folder / 'control-comparison.json', comparison)
        assert not any(comparison.values()), 'Fresh map differs from paired native control: ' + str(comparison)
        assert before['material_tags'] == control['data']['material_tags'], 'CSC material tags changed'
        shutil.copy2(folder / 'map.json', folder / 'before.json')
        _, _, summary = analyze_map(folder, read(HERE.parent / 'map_survey/materials.json'))
        assert summary['resolved_definitions'] == control['definitions']
        definitions = summary['resolved_definitions']
        mapped = sorted({r for d in definitions.values() for kind in ('base', 'spec') for r in d[kind].get('resources', [])})
        names = '{' + ','.join(json.dumps(r) for r in mapped) + '}'
        # One read-only sweep of native eligibility. No writes and no RNG draws.
        code = '''assert(Game.GetCurrentGameTurn()==1);assert(ResourceBuilder and ResourceBuilder.CanHaveResource);
local types=''' + names + ''';local entries={};local freq={};local checked=0;
for _,name in ipairs(types) do local r=GameInfo.Resources[name];if r and r.Frequency>0 then
 local allowed={};for i=0,Map.GetPlotCount()-1 do local p=Map.GetPlotByIndex(i);
 if not p:IsWater() and not p:IsImpassable() and p:GetDistrictType()==-1 and p:GetResourceType()==-1 then
  checked=checked+1;if ResourceBuilder.CanHaveResource(p,r.Index) then allowed[#allowed+1]=tostring(i) end
 end end;entries[#entries+1]='"'..name..'":['..table.concat(allowed,',')..']';freq[#freq+1]='"'..name..'":'..r.Frequency;
end end;print('CSCH_ELIGIBILITY={'..table.concat(entries,',')..'}');print('CSCH_FREQUENCY={'..table.concat(freq,',')..'}');print('CSCH_CHECKED',checked);
local occupied={};for i=0,Map.GetPlotCount()-1 do local p=Map.GetPlotByIndex(i);local imp=GameInfo.Improvements[p:GetImprovementType()];if imp then occupied[#occupied+1]='"'..i..'":"'..imp.ImprovementType..'"' end end;print('CSCH_IMPROVEMENTS={'..table.concat(occupied,',')..'}');'''
        text = self.cmd(code, 'GameCore_Tuner', f'eligibility-{i}', wait=4)
        eligible = json.loads(re.search(r'CSCH_ELIGIBILITY=([^\r\n]+)', text).group(1))
        frequencies = json.loads(re.search(r'CSCH_FREQUENCY=([^\r\n]+)', text).group(1))
        checked = int(re.search(r'CSCH_CHECKED\s+(\d+)', text).group(1))
        improvements = json.loads(re.search(r'CSCH_IMPROVEMENTS=([^\r\n]+)', text).group(1))
        write(folder / 'native-eligibility.json', {'eligible': eligible, 'frequencies': frequencies, 'checks': checked, 'improvements': improvements})
        source = {**copy.deepcopy(control), 'data': before, 'settings': settings,
                  'continents': continent_census(before, definitions), 'source_sha256': sha(folder / 'before.json')}
        native_rules = NativeRules({r: {'Frequency': n} for r, n in frequencies.items()}, eligible)
        plan = Helper(source, native_rules, self.seed).run()
        write(folder / 'native-plan.json', plan)
        offline = Rules(self.database)
        mismatch = [{'resource': r, 'plot': p['index'], 'native': p['index'] in native_rules.eligible[r], 'improvement': improvements.get(str(p['index']))}
                    for r in native_rules.resources for p in before['plots']
                    if not p['water'] and not p['impassable'] and not p.get('district') and not p.get('resource')
                    and offline.can_place(p, r, before['plots']) != (p['index'] in native_rules.eligible[r])]
        write(folder / 'eligibility-comparison.json', {'checks': checked, 'mismatches': mismatch})
        additions = plan['assistance']['additions']
        # All proposals are checked before any mutation. The native setter is
        # then checked again per deposit, with exact resource readback.
        rows = '{' + ','.join('{i=' + str(a['plot']) + ',r=' + json.dumps(a['resource']) + '}' for a in additions) + '}'
        apply = '''assert(Game.GetCurrentGameTurn()==1);assert(not Game:GetProperty('CSC_HELPER_NATIVE_TEST_APPLIED'));
local deposits=''' + rows + ''';
for _,a in ipairs(deposits) do local p=Map.GetPlotByIndex(a.i);local r=GameInfo.Resources[a.r];assert(r and p:GetResourceType()==-1 and ResourceBuilder.CanHaveResource(p,r.Index),'Preflight rejected '..a.r..' at '..a.i) end;
for _,a in ipairs(deposits) do local p=Map.GetPlotByIndex(a.i);local r=GameInfo.Resources[a.r];assert(ResourceBuilder.CanHaveResource(p,r.Index),'Recheck rejected '..a.r..' at '..a.i);ResourceBuilder.SetResourceType(p,r.Index,1);assert(p:GetResourceType()==r.Index,'Placement readback failed');print('CSCH_PLACED',a.i,a.r) end;
Game:SetProperty('CSC_HELPER_NATIVE_TEST_APPLIED',true);print('CSCH_APPLIED',#deposits,Game.GetCurrentGameTurn());'''
        self.cmd(apply, 'GameCore_Tuner', f'apply-helper-{i}', wait=4)
        after = self.dump(f'after-helper-{i}')
        expected = plan['data']['plots']
        assert after['plots'] == expected, 'Native final plots differ from accepted plan'
        changes = {a['plot']: a['resource'] for a in additions}
        for p, q in zip(before['plots'], after['plots']):
            if p['index'] in changes:
                assert not p.get('resource') and q['resource'] == changes[p['index']]
                assert {k: v for k, v in p.items() if k != 'resource'} == {k: v for k, v in q.items() if k != 'resource'}
            else: assert p == q
        write(folder / 'map.json', after)
        census = continent_census(after, definitions)
        site_keys = ('land_both', 'common_clearable_both', 'harvest_aware_both')
        delta = [{'continent': c['id'], 'quarter': q['quarter'], **{k: q[k] - next(r for r in next(o for o in preview['continents'] if o['id'] == c['id'])['quarters'] if r['quarter'] == q['quarter'])[k] for k in site_keys}}
                 for c in census for q in c['quarters']]
        preview_tiles = sum(p.get('resource') != q.get('resource') for p, q in zip(after['plots'], preview['data']['plots']))
        entry = {**plan, 'id': f'csc-helper-native-{i}', 'group': 'csc-helper-native',
                 'groupLabel': 'CSC helper · Civ API test', 'data': after, 'continents': census,
                 'reference': census[0]['quarters'], 'settings': {**settings, 'helper_seed': self.seed},
                 'source_sha256': sha(folder / 'map.json'),
                 'provenance': {'native': True, 'kind': 'native-assistance', 'seed': self.seed,
                                'warning': 'Native Civ test: shared Python selection logic with live Civ eligibility and placement APIs, applied at turn 1 after initialization. This validates the prototype; automatic mod startup ordering is not tested.'},
                 'native_comparison': {'preview_id': preview['id'], 'resource_tile_differences': preview_tiles,
                                       'eligibility_checks': checked, 'eligibility_mismatches': len(mismatch),
                                       'deposits': len(additions), 'site_deltas': delta,
                                       'control_tile_differences': comparison}}
        write(folder / 'viewer-map.json', entry)
        for name in ('Database.log', 'Modding.log', 'Lua.log'):
            if (LOGS / name).exists(): shutil.copy2(LOGS / name, folder / 'logs' / name)
        db_log = (folder / 'logs/Database.log').read_text(encoding='utf-8', errors='replace')
        assert '[Gameplay] ERROR' not in db_log, 'Gameplay database errors'
        write(folder / 'complete.json', {'status': 'complete', 'native_helper_verified': True, 'turn': 1,
                                        'plots': len(after['plots']), 'deposits': len(additions),
                                        'preview_tile_differences': preview_tiles, 'eligibility_mismatches': len(mismatch)})
        self.say(f'Map {i}: helper verified, {len(additions)} deposits, {len(mismatch)} eligibility differences, {preview_tiles} resource tiles differ from preview')


def combine(bundle_path, out):
    bundle = read(bundle_path)
    entries = []
    for marker in sorted(out.glob('csc-helper-native/map-*/complete.json')):
        if read(marker).get('native_helper_verified'): entries.append(read(marker.parent / 'viewer-map.json'))
    assert len(entries) == 5, 'Five verified native helper maps required'
    bundle['maps'] = [m for m in bundle['maps'] if m['group'] != 'csc-helper-native'] + entries
    bundle['default_group'] = 'csc-helper-native'
    bundle_path.write_text(json.dumps(bundle, separators=(',', ':')), encoding='utf-8')
    render(bundle, bundle_path.with_name('index.html'))
    coverage = []
    for q in entries[0]['definitions']:
        def count(maps, before=False):
            return sum(c['id'] != -1 and next(r for r in c['quarters'] if r['quarter'] == q)['common_clearable_both'] > 0
                       for m in maps for c in (m['assistance']['before_continents'] if before else m['continents']))
        previews = [m for m in bundle['maps'] if m['group'] == 'csc-assist']
        coverage.append({'quarter': q, 'before': count(entries, True), 'preview': count(previews), 'native': count(entries)})
    write_csv(out / 'coverage-comparison.csv', coverage)
    write_csv(out / 'site-comparison.csv', [{'map': m['number'], **row} for m in entries for row in m['native_comparison']['site_deltas']])
    write_csv(out / 'native-additions.csv', [{**{k: v for k, v in a.items() if k != 'coverage_gains'}, 'map': m['number']} for m in entries for a in m['assistance']['additions']])
    write(out / 'analysis.json', {'maps': 5, 'continents': 15, 'coverage': coverage,
                                 'comparisons': [{'map': m['number'], **m['native_comparison']} for m in entries]})


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--bundle', type=Path, required=True)
    p.add_argument('--database', type=Path, required=True)
    p.add_argument('--seed', type=int, default=SEED)
    p.add_argument('--combine-only', action='store_true')
    p.add_argument('--first-only', action='store_true')
    args = p.parse_args()
    if args.combine_only: combine(args.bundle, args.output); return
    r = NativeSurvey(args.output); r.bundle = read(args.bundle); r.database = args.database
    r.seed = args.seed; r.save_maps = False; r.pending_folder = None
    try:
        r.wait('MainMenu'); r.config(); r.select_mods(False)
        write(args.output / 'batch.json', {'status': 'running', 'target_maps': 5, 'helper_seed': args.seed})
        for i in range(1, 6):
            marker = args.output / 'csc-helper-native' / f'map-{i:02d}' / 'complete.json'
            if marker.exists() and read(marker).get('native_helper_verified'): continue
            r.number = i; r.pending_folder = marker.parent
            ref = next(m for m in r.bundle['maps'] if m['group'] == 'luxuries-4' and m['number'] == i)
            r.start_map('csc-helper-native', False, 3, i, ref['settings']['leaders'])
            if args.first_only: break
        done = len([p for p in args.output.glob('csc-helper-native/map-*/complete.json') if read(p).get('native_helper_verified')])
        write(args.output / 'batch.json', {'status': 'complete' if done == 5 else 'partial', 'maps': done, 'turns_advanced': 0})
    except BaseException as exc:
        write(args.output / 'batch.json', {'status': 'interrupted', 'error': str(exc), 'traceback': traceback.format_exc()})
        raise
    finally:
        r.pending_folder = None
        try:
            if 'MainMenu' not in r.states(): r.menu()
            if (args.output / 'original-preferences.json').exists(): r.restore()
        except Exception as exc: r.say('Preferences restoration pending: ' + str(exc))
    if done == 5: combine(args.bundle, args.output)


if __name__ == '__main__': main()
