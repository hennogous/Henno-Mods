"""T1: Real Strategy's ORIGINAL Ludwig civic preference, present vs absent.

Fresh matched worlds with the whole Real Strategy package held constant. The
target is Divine Right, an original government-unlock favorite. No substitute
strategy condition, research setter, progress grant or live Workshop edit.
"""
import argparse
import csv
import hashlib
import json
import os
import re
import shutil
import sqlite3
import time
import traceback
import zlib
from pathlib import Path

import strategy_research_trial as prior
from civic_unlock_score_trial import score_rows
from fixed_research_trial import inventory
from improvement_research_trial import ResearchRunner
from paired_standard import HERE, read, sha
from run import ROOT, write

VERSION = 'civic-unlock-t1-original-rst-ludwig-divine-right-v1b'
RST_ID = '99d9ddfe-85fb-2d92-1893-92a015b5899a'
RST = Path('C:/Program Files (x86)/Steam/steamapps/workshop/content/289070/1617282434')
TARGET = 'CIVIC_DIVINE_RIGHT'
LIST = 'LudwigCivics'
TRAIT = 'TRAIT_LEADER_LUDWIG'
CALLBACK_AUDIT = b"\nCSC_RESEARCH_PROBE_NATIVE={version='rst-original-list-v1',calls={},first_true={},errors={}};print('CSC_TEST_RST_OBSERVER_READY');\n"


def overlay(on):
    # Only list cleanup from the previous control; NO always-true conditions.
    text = (HERE / 'strategy_research_control.sql').read_text(encoding='utf-8').split('INSERT OR IGNORE INTO Types')[0]
    text += "\nDELETE FROM AiFavoredItems WHERE Item='CIVIC_DIVINE_RIGHT';\n"
    if on:
        text += "INSERT INTO AiFavoredItems (ListType,Item,Favored,Value) VALUES ('LudwigCivics','CIVIC_DIVINE_RIGHT',1,0);\n"
    return text


def native_check(db, arm, patch, source, with_rst=True):
    assert db.execute("SELECT LeaderType,AgendaType,System FROM AiLists WHERE ListType=?", (LIST,)).fetchall() == [(TRAIT, None, 'Civics')]
    expected = [(LIST, 1, 0)] if arm == 'on' else []
    assert db.execute('SELECT ListType,Favored,Value FROM AiFavoredItems WHERE Item=?', (TARGET,)).fetchall() == expected
    assert db.execute("SELECT TraitType FROM LeaderTraits WHERE LeaderType='LEADER_LUDWIG' AND TraitType=?", (TRAIT,)).fetchall() == [(TRAIT,)]
    # Original RST context is required. No always-true replacement is present.
    if with_rst:
        assert db.execute("SELECT StringValue FROM StrategyConditions WHERE StrategyType='STRATEGY_NAVAL' AND ConditionFunction='Call Lua Function'").fetchall() == [('ActiveStrategyNaval',)]
    else:
        assert db.execute("SELECT COUNT(*) FROM GlobalParameters WHERE Name='RST_VERSION_MAJOR'").fetchone()[0] == 0
    assert db.execute("SELECT COUNT(*) FROM StrategyConditions WHERE StringValue='CSC_TestResearchAlways'").fetchone()[0] == 0
    for table in ('AiLists', 'AiListTypes', 'AiFavoredItems', 'Strategy_Priorities'):
        assert db.execute(f"SELECT COUNT(*) FROM {table} WHERE ListType LIKE 'CSC_AI_SERVICE_%' OR ListType LIKE 'CSC_AI_FIXED_SERVICE_%' OR ListType='CSC_TEST_RESEARCH_LIST'").fetchone()[0] == 0
    assert db.execute("SELECT DefaultValue FROM PseudoYields WHERE PseudoYieldType='PSEUDOYIELD_IMPROVEMENT'").fetchone()[0] == 90
    assert db.execute("SELECT Value FROM AiFavoredItems WHERE ListType='UnitPriorityBoosts' AND Item='UNIT_BUILDER'").fetchall() == [(50,)]
    before = inventory(db)
    db.create_function('Make_Hash', 1, lambda s: zlib.crc32(s.encode()))
    db.executescript(source + '\n' + patch)
    assert before == inventory(db), 'CSC source + test overlay replay changed native tables'
    return {'passed': True, 'arm': arm, 'original_list': LIST, 'trait': TRAIT,
            'target_rows': expected, 'rst_original_naval_callback': with_rst,
            'no_test_activation_override': True, 'replay_identical': True, 'inventory': before}


class RSTRunner(prior.StrategyRunner):
    def select_mods(self, tar):
        assert not tar
        # config() first disables all other community mods, as in prior trials.
        super().select_mods(False)
        if not self.original_rst:
            return
        self.active_mods = self.cmd(
            "local h;for _,m in ipairs(Modding.GetInstalledMods()) do if string.lower(m.Id)=='" + RST_ID + "' then h=m.Handle end end;assert(h,'Real Strategy not installed');Modding.EnableMod(h,true);for _,m in ipairs(Modding.GetInstalledMods()) do if m.Enabled then if not m.Official then local id=string.lower(m.Id);assert(id=='" + RST_ID + "' or id=='c5e66bd1-d804-443b-ac3d-1917a20dba3c','Unexpected community mod '..id) end;print('CSC_RST_ENABLED',m.Id,m.Name,m.Official) end end;",
            'MainMenu', 'enable-original-rst', wait=5)

    def pin_sources(self):
        super().pin_sources()
        path = self.out / 'tuning-source-hashes.json'
        pins = read(path)
        pins[str(Path(__file__))] = sha(Path(__file__))
        pins[str(HERE / 'civic_unlock_score_trial.py')] = sha(HERE / 'civic_unlock_score_trial.py')
        for f in RST.rglob('*'):
            if f.is_file() and '.git' not in f.relative_to(RST).parts:
                pins[str(f)] = sha(f)
        write(path, pins)

    def archive_version(self):
        ResearchRunner.archive_version(self)
        path = self.out / 'source-version/version.json'
        v = read(path)
        workshop = {}
        for f in RST.rglob('*'):
            if f.is_file() and '.git' not in f.relative_to(RST).parts:
                rel = f.relative_to(RST)
                target = path.parent / 'workshop-real-strategy' / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(f, target)
                workshop[str(rel)] = sha(target)
        v.update(code_version=VERSION, test='T1', arm=self.arm, workshop_files=workshop,
                 research={'target': TARGET, 'list': LIST, 'trait': TRAIT, 'favored': 1,
                           'value': 0, 'present': self.arm == 'on', 'primary_player': 1,
                           'original_rst_context': self.original_rst, 'no_current_civic_reset': True},
                 analyzed_rounds=self.rounds,
                 common_overlay='Remove CSC research lists and all other target favorites; CSC baseline constants retained by CSC load3500 after RST.')
        write(path, v)
        (path.parent / 'applied-overlay.sql').write_text(self.overlay, encoding='utf-8')

    def finish_preflight(self, i):
        self.reset_logs = set()
        for name, old in self.offsets.items():
            p = prior.LOGS / name
            if p.exists():
                b = p.read_bytes()
                if len(b) < old['bytes'] or hashlib.sha256(b[:old['bytes']]).hexdigest() != old['hash']:
                    self.reset_logs.add(name)
        write(self.out / 'native-log-offsets.json', {'before_host': self.offsets, 'reset_detected_during_load': sorted(self.reset_logs)})
        self.cmd("assert(CSC_RESEARCH_PROBE_NATIVE and CSC_RESEARCH_PROBE_NATIVE.version=='rst-original-list-v1');assert(PlayerConfigurations[1]:GetLeaderTypeName()=='LEADER_LUDWIG','Expected exact roster leader Ludwig');assert(not Players[1]:GetCulture():HasCivic(GameInfo.Civics.CIVIC_DIVINE_RIGHT.Index));", 'CSC_AI_Research', 'probe-loaded')
        # Real Strategy's UI context publishes its gameplay bridge; check actual loading.
        if self.original_rst:
            self.cmd("assert(ExposedMembers.RST and type(ExposedMembers.RST.PlayerGetNumTechsResearched)=='function','Real Strategy bridge missing');", 'PlotInfo', 'rst-bridge-loaded')
        cache = Path.home() / 'AppData/Local/Firaxis Games/Sid Meier\'s Civilization VI/Cache/DebugGameplay.sqlite'
        src = sqlite3.connect(cache.as_uri() + '?mode=ro', uri=True)
        db = sqlite3.connect(':memory:')
        src.backup(db)
        src.close()
        dst = sqlite3.connect(self.out / 'native-gameplay.sqlite')
        db.backup(dst)
        dst.close()
        result = native_check(db, self.arm, self.overlay, (ROOT / 'Civ Supply Chains' / prior.SQL).read_text(encoding='utf-8'), self.original_rst)
        write(self.out / 'native-database-validation.json', result)
        settings = read(self.out / 'game-01/settings.json')
        settings.update(code_version=VERSION, test='T1', arm=self.arm, target=TARGET,
                        target_player=1, original_rst_package=self.original_rst,
                        analyzed_turns=[71, 70 + self.rounds], target_turn=72 + self.rounds)
        write(self.out / 'game-01/settings.json', settings)

    def observe(self):
        fixture = getattr(self, 'fixture_path', HERE / 'strategy_research_fixture.lua').read_text(encoding='utf-8')
        if getattr(self, 'fixture_extra', None):
            fixture += '\n' + self.fixture_extra
        fixture_output = self.cmd(fixture, 'CSC_AdjacencyGameplay', 'probe-opportunity-fixture', wait=5)
        if getattr(self, 'fixture_extra', None):
            (self.out / 'fixture-extra-output.txt').write_text(fixture_output, encoding='utf-8')
        text = self.cmd('local old=CSCBASE.checkpoints[71];CSCBASE.checkpoints[71]=nil;CSCBASE.snapshot(71);CSCBASE.checkpoints[71]=old;', 'CSC_AdjacencyGameplay', 'probe-fixture-census', wait=3)
        payload = json.loads(re.search(r'CSCBASE_SNAPSHOT=([^\r\n]+)', text)[1])
        assert payload['turn'] == 71 and not payload['errors']
        write(self.out / 'fixture-census.json', payload)
        if getattr(self, 'fixture_reference', None):
            # Lua pairs() does not order Quarter option groups. Preserve raw
            # evidence; compare only that documented unordered collection by key.
            reference = read(self.fixture_reference)
            def canonical_fixture(value):
                value = json.loads(json.dumps(value))
                if isinstance(value.get('options'), list):
                    keys = [(row['player'], row['city'], row['quarter']) for row in value['options']]
                    assert len(keys) == len(set(keys)), 'Duplicate Quarter options'
                    value['options'].sort(key=lambda row: (row['player'], row['city'], row['quarter']))
                return value
            assert canonical_fixture(payload) == canonical_fixture(reference), 'Fixture censuses differ'
        if hasattr(self, 'after_fixture'):
            self.after_fixture()
        self.cmd((HERE / 'strategy_research_observer.lua').read_text(encoding='utf-8'), 'CSC_AI_Research', 'probe-observer-install', wait=4)
        self.observer_active = True
        initial = self.export_probe()
        assert initial['initial'][0]['player'] == 1
        assert TARGET not in initial['initial'][0]['new_completed']
        self.cmd('Automation.SetActive(false);AutoplayManager.SetDisableAssertsForAutoplay(true);AutoplayManager.SetTurns(' + str(self.rounds + 1) + ');AutoplayManager.SetReturnAsPlayer(0);AutoplayManager.SetObserveAsPlayer(-1);AutoplayManager.SetActive(true);', 'GameCore_Tuner', 'probe-autoplay', wait=4)
        self.say(f'T1/{self.arm}: native autoplay started, original {LIST}/{TARGET}, {self.rounds} analyzed rounds.')
        deadline, last_turn, last_change = time.monotonic() + 3600, 71, time.monotonic()
        while time.monotonic() < deadline:
            time.sleep(20)
            text = self.cmd("print('CSC_TEST_PROGRESS',Game.GetCurrentGameTurn(),AutoplayManager.IsActive());", 'GameCore_Tuner', 'research-probe-poll')
            turn, active = re.findall(r'CSC_TEST_PROGRESS\s+(\d+)\s+(true|false)', text)[-1]
            turn = int(turn)
            if turn != last_turn:
                last_turn, last_change = turn, time.monotonic()
            data = self.export_probe()
            assert not data['errors'] and not data['native']['errors']
            write(self.out / 'live-status.json', {'status': 'running', 'test': 'T1', 'arm': self.arm, 'turn': turn, 'observations_saved': len(data['history']), 'updated_unix': time.time()})
            if active == 'false':
                break
            if time.monotonic() - last_change > 600:
                raise RuntimeError('Native autoplay stalled ten minutes')
        else:
            raise RuntimeError('Bounded native trial runtime exceeded')
        data = self.export_probe()
        write(self.out / 'observations-raw.json', data)
        selected = [r for r in data['history'] if 71 <= r['turn'] < 71 + self.rounds]
        keys = {(r['turn'], r['player']) for r in selected}
        expected = {(t, p) for t in range(71, 71 + self.rounds) for p in range(1, 6)}
        assert len(keys) == len(selected)
        defeats = {r['player']: r['turn'] for r in data['defeats']}
        missing = expected - keys
        assert all(p in defeats and t >= defeats[p] for t, p in missing), sorted(missing)
        assert turn >= 71 + self.rounds
        observations = {'history': selected, 'completions': [r for r in data['completions'] if 71 <= r['turn'] < 71 + self.rounds], 'initial': data['initial'], 'native': data['native'], 'defeats': data['defeats']}
        write(self.out / 'observations.json', observations)
        write(self.out / 'observation-validation.json', {'passed': True, 'actual_endpoint': turn, 'analyzed_turns': [71, 70 + self.rounds], 'observations': len(selected), 'expected_uncensored': 5 * self.rounds, 'censored_pairs': sorted(missing), 'no_research_setters': True})
        self.snapshot(1, turn)
        self.save_checkpoint(1, turn)
        self.archive_native_logs()
        # Scope errors to this run. RST script execution must also be present.
        lua = (self.out / 'native-logs/Lua.log').read_text(errors='replace')
        rst_loaded = 'Loading RealStrategy.lua from Real Strategy version' in lua
        assert rst_loaded == self.original_rst, 'Unexpected Real Strategy script loading state'
        errors = [line[:500] for line in lua.splitlines() if 'Runtime Error:' in line or 'Gameplay ERROR' in line]
        write(self.out / 'native-script-validation.json', {'passed': not errors, 'rst_loaded': rst_loaded, 'errors': errors[:10]})
        assert not errors, errors[:3]
        self.check_installed()
        for name in ('tuning-source-hashes.json', 'controller-source-hashes.json'):
            for file, digest in read(self.out / name).items():
                assert sha(Path(file)) == digest, file
        self.actual_endpoint = turn
        return observations


def compare(root, with_rst=True):
    scores = {arm: score_rows(root / arm / 'native-logs/AI_GovtPolicies.csv', 71, 90) for arm in ('off', 'on')}
    common = scores['off'].keys() & scores['on'].keys()
    initial = [k for k in common if k[0] == 71 and k[1] == 1]
    target = [k for k in common if k[1] == 1 and k[2] == TARGET]
    results = {}
    for arm in ('off', 'on'):
        data = read(root / arm / 'observations.json')
        player = [r for r in data['history'] if r['player'] == 1]
        complete = [r for r in data['completions'] if r['player'] == 1]
        initial_target = scores[arm].get((71, 1, TARGET))
        results[arm] = {'initial_target_score': initial_target[0] if initial_target else None,
                        'first_target_selected': next((r['turn'] for r in player if r['civic'] == TARGET), None),
                        'target_completed': next((r['turn'] for r in complete if r['civic'] == TARGET), None),
                        'natural_civic_completions': len(complete),
                        'current_civic_sequence': [r['civic'] for i, r in enumerate(player) if i == 0 or r['civic'] != player[i - 1]['civic']]}
    return {'code_version': VERSION, 'target': TARGET, 'original_list': LIST, 'primary_player': 1,
            'real_strategy_enabled': with_rst,
            'arms': results, 'matched_initial_primary_candidates': len(initial),
            'different_initial_primary_scores': sum(scores['off'][k] != scores['on'][k] for k in initial),
            'matched_primary_target_scores': len(target),
            'different_primary_target_scores': sum(scores['off'][k] != scores['on'][k] for k in target),
            'initial_score_response': results['off']['initial_target_score'] != results['on']['initial_target_score'] if all(results[a]['initial_target_score'] is not None for a in results) else None,
            'limits': ['One original leader preference on one matched seed.',
                       'Whole Real Strategy package held constant; cross-package comparisons descriptive.' if with_rst else 'CSC-only reduction; original vanilla leader list retained, Real Strategy disabled in both arms.',
                       'A logged score response is distinct from changing a natural research choice.']}


def main():
    global VERSION
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--csc-only', action='store_true')
    args = parser.parse_args()
    if args.csc_only:
        VERSION = 'civic-unlock-t1-minimal-csc-ludwig-divine-right-v2'
    args.output.mkdir(parents=True, exist_ok=False)
    original_db = Path.home() / 'Desktop/Codex/csc-civic-unlocks-20261020/t1-native-rst-context-after-v1.sqlite'
    with sqlite3.connect(original_db.as_uri() + '?mode=ro', uri=True) as original_context:
        assert original_context.execute("SELECT l.LeaderType,l.System,i.Favored,i.Value FROM AiLists l JOIN AiFavoredItems i USING(ListType) WHERE l.ListType='LudwigCivics' AND i.Item='CIVIC_DIVINE_RIGHT'").fetchall() == [('TRAIT_LEADER_LUDWIG','Civics',1,0)]
    prior.VERSION = VERSION
    originals = {rel: (prior.INSTALLED / rel).read_bytes() for rel in (prior.SQL, prior.LUA)}
    for rel, content in originals.items():
        assert content == (ROOT / 'Civ Supply Chains' / rel).read_bytes()
        p = args.output / 'original-installed' / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(content)
    runner, reference = None, None
    write(args.output / 'job-status.json', {'status': 'starting', 'test': 'T1', 'pid': os.getpid(), 'code_version': VERSION})
    try:
        for arm in ('off', 'on'):
            patch = overlay(arm == 'on')
            for rel, content in originals.items():
                assert (ROOT / 'Civ Supply Chains' / rel).read_bytes() == content
            (prior.INSTALLED / prior.SQL).write_bytes(originals[prior.SQL] + b'\n' + patch.encode())
            (prior.INSTALLED / prior.LUA).write_bytes(originals[prior.LUA] + CALLBACK_AUDIT)
            runner = RSTRunner(args.output / arm)
            runner.original_rst = not args.csc_only
            runner.phase, runner.arm, runner.rounds, runner.overlay, runner.keep_game = 'rst', arm, 20, patch, False
            runner.captures = Path.home() / 'Desktop/Codex/csc-implemented-native-20261016'
            runner.baseline = Path.home() / 'Desktop/Codex/csc-ai-paired-standard-20261016'
            runner.previous = Path.home() / 'Desktop/Codex/csc-ai-improvement-research-20261019/trial-v1b'
            if arm == 'on':
                runner.fixture_reference = args.output / 'off/fixture-census.json'
            runner.pin_sources()
            runner.archive_version()
            write(args.output / 'active-stage.json', {'test': 'T1', 'arm': arm, 'output': str(runner.out), 'pid': os.getpid()})
            write(args.output / 'job-status.json', {'status': 'running', 'test': 'T1', 'arm': arm, 'pid': os.getpid(), 'updated_unix': time.time()})
            runner.wait('MainMenu', 180)
            runner.config()
            runner.start_pair(1)
            current = [read(runner.out / 'game-01/initial-map.json'), read(runner.out / 'game-01/turn-071.json'), read(runner.out / 'original-preferences.json')]
            if reference is None:
                reference = current
            else:
                assert current == reference, 'Paired initial world/census/preferences differ'
                before = read(args.output / 'off/native-database-validation.json')['inventory']
                after = read(runner.out / 'native-database-validation.json')['inventory']
                assert {k for k in before if before[k] != after[k]} == {'AiFavoredItems'}
                a = sqlite3.connect(args.output / 'off/native-gameplay.sqlite')
                b = sqlite3.connect(runner.out / 'native-gameplay.sqlite')
                av, bv = set(a.execute('SELECT * FROM AiFavoredItems')), set(b.execute('SELECT * FROM AiFavoredItems'))
                assert not av - bv and len(bv - av) == 1
                write(args.output / 'paired-preflight.json', {'passed': True, 'initial_world_census_preferences_identical': True, 'native_changed_tables': ['AiFavoredItems'], 'added_rows': [list(r) for r in bv - av]})
            write(runner.out / 'paired-preflight.json', {'passed': True, 'arm': arm, 'initial_parity': True})
            runner.observe()
            runner.menu()
            runner.restore_verified()
            write(runner.out / 'complete.json', {'passed': True, 'test': 'T1', 'arm': arm, 'actual_endpoint': runner.actual_endpoint})
        result = compare(args.output, not args.csc_only)
        write(args.output / 'comparison.json', result)
        (args.output / 'report.md').write_text('# Original Real Strategy civic preference\n\n' + json.dumps(result, indent=2) + '\n', encoding='utf-8')
        write(args.output / 'job-status.json', {'status': 'complete', 'test': 'T1', 'initial_score_response': result['initial_score_response'], 'updated_unix': time.time()})
    except BaseException as exc:
        write(args.output / 'failure.json', {'error': str(exc), 'traceback': traceback.format_exc()})
        if runner:
            try:
                if getattr(runner, 'observer_active', False):
                    runner.export_probe()
                runner.archive_failure()
            except Exception:
                pass
            try:
                runner.states()
                if 'PlotInfo' in runner.state:
                    runner.menu()
                if (runner.out / 'original-preferences.json').exists():
                    runner.restore_verified()
            except Exception as cleanup:
                write(args.output / 'cleanup-required.json', {'error': str(cleanup)})
        write(args.output / 'job-status.json', {'status': 'failed', 'test': 'T1', 'error': str(exc), 'updated_unix': time.time()})
        raise
    finally:
        for rel, content in originals.items():
            (prior.INSTALLED / rel).write_bytes(content)
        write(args.output / 'installed-restored.json', {'verified': all((prior.INSTALLED / rel).read_bytes() == v for rel, v in originals.items()), 'source_unchanged': all((ROOT / 'Civ Supply Chains' / rel).read_bytes() == v for rel, v in originals.items())})


if __name__ == '__main__':
    main()
