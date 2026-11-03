"""Short CSC-only connectivity test for civic preferences.

All list registrations and one always-active experimental strategy are identical
in five fresh worlds. Only the location of ONE Divine Right favorite changes.
This is a score diagnostic, not a completed-unlock or dynamic-gating claim.
"""
import argparse
import json
import os
import re
import sqlite3
import time
import traceback
import zlib
from pathlib import Path

import civic_unlock_rst_trial as base
from civic_unlock_score_trial import score_rows
from fixed_research_trial import inventory
from paired_standard import HERE, read, sha
from run import ROOT, write

VERSION = 'civic-unlock-binding-original-direct-generic-strategy-v1'
ARMS = ('control', 'original', 'direct', 'generic', 'strategy')
LISTS = {'original': 'LudwigCivics', 'direct': 'CSC_TEST_CIVIC_BIND_DIRECT',
         'generic': 'CSC_TEST_CIVIC_BIND_GENERIC', 'strategy': 'CSC_TEST_CIVIC_BIND_STRATEGY'}
STRATEGY = 'STRATEGY_CSC_TEST_CIVIC_BINDING'
CALLBACK = b"""
CSC_RESEARCH_PROBE_NATIVE={version='rst-original-list-v1',experiment_version='civic-binding-v1',calls={},first_true={},errors={}};
GameEvents.CSC_TestCivicBindingActive.Add(function(pid,which)
 local r=CSC_RESEARCH_PROBE_NATIVE;local key=tostring(pid)..':'..tostring(which);
 r.calls[key]=(r.calls[key] or 0)+1;
 local active=pid==1 and PlayerManager.IsAlive(pid) and not Players[pid]:IsHuman();
 if active and not r.first_true[key] then r.first_true[key]=Game.GetCurrentGameTurn() end;
 return active;
end);
print('CSC_CIVIC_BINDING_CALLBACK_READY');
"""


def overlay(arm):
    text = base.overlay(False)
    text += """
DELETE FROM AiLists WHERE ListType IN ('CSC_TEST_CIVIC_BIND_DIRECT','CSC_TEST_CIVIC_BIND_GENERIC','CSC_TEST_CIVIC_BIND_STRATEGY');
INSERT OR IGNORE INTO AiListTypes (ListType) VALUES
 ('CSC_TEST_CIVIC_BIND_DIRECT'),('CSC_TEST_CIVIC_BIND_GENERIC'),('CSC_TEST_CIVIC_BIND_STRATEGY');
INSERT OR IGNORE INTO AiLists (ListType,LeaderType,System) VALUES
 ('CSC_TEST_CIVIC_BIND_DIRECT','TRAIT_LEADER_LUDWIG','Civics'),
 ('CSC_TEST_CIVIC_BIND_GENERIC','TRAIT_LEADER_MAJOR_CIV','Civics'),
 ('CSC_TEST_CIVIC_BIND_STRATEGY',NULL,'Civics');
INSERT OR IGNORE INTO Types (Type,Kind) VALUES ('STRATEGY_CSC_TEST_CIVIC_BINDING','KIND_VICTORY_STRATEGY');
INSERT OR IGNORE INTO Strategies (StrategyType,VictoryType,NumConditionsNeeded) VALUES ('STRATEGY_CSC_TEST_CIVIC_BINDING',NULL,1);
DELETE FROM StrategyConditions WHERE StrategyType='STRATEGY_CSC_TEST_CIVIC_BINDING';
INSERT INTO StrategyConditions (StrategyType,ConditionFunction,StringValue,ThresholdValue) VALUES
 ('STRATEGY_CSC_TEST_CIVIC_BINDING','Call Lua Function','CSC_TestCivicBindingActive',1);
INSERT OR IGNORE INTO Strategy_Priorities (StrategyType,ListType) VALUES
 ('STRATEGY_CSC_TEST_CIVIC_BINDING','CSC_TEST_CIVIC_BIND_STRATEGY');
"""
    if arm != 'control':
        text += "INSERT INTO AiFavoredItems (ListType,Item,Favored,Value) VALUES ('" + LISTS[arm] + "','CIVIC_DIVINE_RIGHT',1,0);\n"
    return text


def native_check(db, arm, patch, source, with_rst=False):
    assert not with_rst
    expected = [] if arm == 'control' else [(LISTS[arm], 1, 0)]
    assert db.execute("SELECT ListType,Favored,Value FROM AiFavoredItems WHERE Item='CIVIC_DIVINE_RIGHT'").fetchall() == expected
    for key, trait in (('direct', 'TRAIT_LEADER_LUDWIG'), ('generic', 'TRAIT_LEADER_MAJOR_CIV'), ('strategy', None)):
        assert db.execute('SELECT LeaderType,AgendaType,System FROM AiLists WHERE ListType=?', (LISTS[key],)).fetchall() == [(trait, None, 'Civics')]
    assert db.execute("SELECT LeaderType,AgendaType,System FROM AiLists WHERE ListType='LudwigCivics'").fetchall() == [('TRAIT_LEADER_LUDWIG', None, 'Civics')]
    assert db.execute("SELECT TraitType FROM LeaderTraits WHERE LeaderType='LEADER_LUDWIG' AND TraitType='TRAIT_LEADER_LUDWIG'").fetchall() == [('TRAIT_LEADER_LUDWIG',)]
    assert db.execute('SELECT ConditionFunction,StringValue,ThresholdValue FROM StrategyConditions WHERE StrategyType=?', (STRATEGY,)).fetchall() == [('Call Lua Function', 'CSC_TestCivicBindingActive', 1)]
    assert db.execute('SELECT ListType FROM Strategy_Priorities WHERE StrategyType=?', (STRATEGY,)).fetchall() == [(LISTS['strategy'],)]
    assert db.execute("SELECT COUNT(*) FROM GlobalParameters WHERE Name='RST_VERSION_MAJOR'").fetchone()[0] == 0
    for table in ('AiLists', 'AiListTypes', 'AiFavoredItems', 'Strategy_Priorities'):
        assert db.execute(f"SELECT COUNT(*) FROM {table} WHERE ListType LIKE 'CSC_AI_SERVICE_%' OR ListType LIKE 'CSC_AI_FIXED_SERVICE_%' OR ListType='CSC_TEST_RESEARCH_LIST'").fetchone()[0] == 0
    assert db.execute("SELECT DefaultValue FROM PseudoYields WHERE PseudoYieldType='PSEUDOYIELD_IMPROVEMENT'").fetchone()[0] == 90
    assert db.execute("SELECT Value FROM AiFavoredItems WHERE ListType='UnitPriorityBoosts' AND Item='UNIT_BUILDER'").fetchall() == [(50,)]
    before = inventory(db)
    db.create_function('Make_Hash', 1, lambda s: zlib.crc32(s.encode()))
    db.executescript(source + '\n' + patch)
    assert inventory(db) == before
    return {'passed': True, 'arm': arm, 'favorite': expected, 'common_registrations': True,
            'native_strategy_binding': True, 'replay_identical': True, 'inventory': before}


class BindingRunner(base.RSTRunner):
    def pin_sources(self):
        super().pin_sources()
        path = self.out / 'tuning-source-hashes.json'
        pins = read(path)
        pins[str(Path(__file__))] = sha(Path(__file__))
        write(path, pins)

    def archive_version(self):
        super().archive_version()
        path = self.out / 'source-version/version.json'
        v = read(path)
        v.update(code_version=VERSION, test='T1-connectivity', arm=self.arm,
                 research={'target': base.TARGET, 'favored': 1, 'value': 0,
                           'owner_route': self.arm, 'list': LISTS.get(self.arm),
                           'primary_player': 1, 'real_strategy_enabled': False,
                           'common_strategy_active_for_primary': True,
                           'no_current_civic_reset': True},
                 analyzed_rounds=self.rounds, diagnostic_only=True)
        write(path, v)

    def observe(self):
        data = super().observe()
        log = (self.out / 'native-logs/AI_Victories.csv').read_text(errors='replace')
        following = re.findall(r'^\s*(\d+),\s*1,\s*' + STRATEGY + r',\s*Following\s*$', log, re.M)
        assert following, 'Experimental strategy not Following for player1'
        assert data['native']['first_true'].get('1:1') is not None
        write(self.out / 'strategy-activation-validation.json', {
            'passed': True, 'primary_player': 1, 'first_native_following': min(map(int, following)),
            'first_callback_true': data['native']['first_true']['1:1'],
            'present_in_all_arms': True, 'not_proof_of_civic_consumption': True})
        return data


def compare(root):
    scores = {arm: score_rows(root / arm / 'native-logs/AI_GovtPolicies.csv', 71, 78) for arm in ARMS}
    result = {'code_version': VERSION, 'target': base.TARGET, 'primary_player': 1,
              'analyzed_rounds': 8, 'arms': {}, 'limits': ['Score connectivity diagnostic; no claim of completed unlocks or dynamic gating.', 'Strategies/callbacks/list registrations identical across all five cases.']}
    control = scores['control']
    for arm in ARMS:
        rows = scores[arm]
        matched = rows.keys() & control.keys()
        primary = [k for k in matched if k[0] == 71 and k[1] == 1]
        other = [k for k in matched if k[0] == 71 and k[1] != 1]
        row = rows.get((71, 1, base.TARGET))
        target = [k for k in matched if k[1] == 1 and k[2] == base.TARGET]
        result['arms'][arm] = {
            'initial_target_score': float(row[0]) if row else None,
            'matched_initial_primary_candidates': len(primary),
            'different_initial_primary_scores': sum(control[k] != rows[k] for k in primary),
            'different_initial_other_player_scores': sum(control[k] != rows[k] for k in other),
            'matched_primary_target_records': len(target),
            'different_primary_target_records': sum(control[k] != rows[k] for k in target),
            'score_response': (float(row[0]) != float(control[(71, 1, base.TARGET)][0])) if row and (71, 1, base.TARGET) in control else None}
    return result


def preflight(output):
    reference = Path.home() / 'Desktop/Codex/csc-civic-unlocks-20261020/t1-minimal-csc-v2/off/native-gameplay.sqlite'
    src = sqlite3.connect(reference.as_uri() + '?mode=ro', uri=True)
    cases = {}
    source = (ROOT / 'Civ Supply Chains' / base.prior.SQL).read_text(encoding='utf-8')
    for arm in ARMS:
        db = sqlite3.connect(':memory:')
        src.backup(db)
        db.create_function('Make_Hash', 1, lambda s: zlib.crc32(s.encode()))
        patch = overlay(arm)
        db.executescript(patch)
        cases[arm] = native_check(db, arm, patch, source)
    for arm in ARMS[1:]:
        assert {k for k in cases[arm]['inventory'] if cases[arm]['inventory'][k] != cases['control']['inventory'][k]} == {'AiFavoredItems'}
    write(output, {'passed': True, 'only_native_table_difference': 'AiFavoredItems',
                   'cases': {arm: {k: v for k, v in value.items() if k != 'inventory'} for arm, value in cases.items()}})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--preflight-only', action='store_true')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    preflight(args.output / 'offline-native-preflight.json')
    if args.preflight_only:
        return
    base.native_check = native_check
    base.VERSION = VERSION
    base.prior.VERSION = VERSION
    originals = {rel: (base.prior.INSTALLED / rel).read_bytes() for rel in (base.prior.SQL, base.prior.LUA)}
    for rel, content in originals.items():
        assert content == (ROOT / 'Civ Supply Chains' / rel).read_bytes()
        p = args.output / 'original-installed' / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(content)
    runner, reference = None, None
    write(args.output / 'job-status.json', {'status': 'starting', 'test': 'T1-connectivity', 'pid': os.getpid(), 'code_version': VERSION})
    try:
        for arm in ARMS:
            for rel, content in originals.items():
                assert (ROOT / 'Civ Supply Chains' / rel).read_bytes() == content
            patch = overlay(arm)
            (base.prior.INSTALLED / base.prior.SQL).write_bytes(originals[base.prior.SQL] + b'\n' + patch.encode())
            (base.prior.INSTALLED / base.prior.LUA).write_bytes(originals[base.prior.LUA] + CALLBACK)
            runner = BindingRunner(args.output / arm)
            runner.original_rst = False
            runner.phase, runner.arm, runner.rounds, runner.overlay, runner.keep_game = 'binding', arm, 8, patch, False
            runner.captures = Path.home() / 'Desktop/Codex/csc-implemented-native-20261016'
            runner.baseline = Path.home() / 'Desktop/Codex/csc-ai-paired-standard-20261016'
            runner.previous = Path.home() / 'Desktop/Codex/csc-ai-improvement-research-20261019/trial-v1b'
            if arm != 'control':
                runner.fixture_reference = args.output / 'control/fixture-census.json'
            runner.pin_sources()
            runner.archive_version()
            write(args.output / 'active-stage.json', {'test': 'T1-connectivity', 'arm': arm, 'output': str(runner.out), 'pid': os.getpid()})
            write(args.output / 'job-status.json', {'status': 'running', 'test': 'T1-connectivity', 'arm': arm, 'pid': os.getpid(), 'updated_unix': time.time()})
            runner.wait('MainMenu', 180)
            runner.config()
            runner.start_pair(1)
            values = [read(runner.out / 'game-01/initial-map.json'), read(runner.out / 'game-01/turn-071.json'), read(runner.out / 'original-preferences.json')]
            if reference is None:
                reference = values
            else:
                assert values == reference, 'Paired initial world/census/preferences differ'
                old = read(args.output / 'control/native-database-validation.json')['inventory']
                new = read(runner.out / 'native-database-validation.json')['inventory']
                assert {k for k in old if old[k] != new[k]} == {'AiFavoredItems'}
                a = sqlite3.connect(args.output / 'control/native-gameplay.sqlite')
                b = sqlite3.connect(runner.out / 'native-gameplay.sqlite')
                av, bv = set(a.execute('SELECT * FROM AiFavoredItems')), set(b.execute('SELECT * FROM AiFavoredItems'))
                assert not av - bv and len(bv - av) == 1
            write(runner.out / 'paired-preflight.json', {'passed': True, 'arm': arm, 'initial_world_census_preferences_equal': True, 'only_treatment': 'One target favored row in selected owner route'})
            runner.observe()
            runner.menu()
            runner.restore_verified()
            write(runner.out / 'complete.json', {'passed': True, 'arm': arm, 'actual_endpoint': runner.actual_endpoint, 'analyzed_rounds': 8})
        result = compare(args.output)
        write(args.output / 'comparison.json', result)
        (args.output / 'report.md').write_text('# Civic preference connectivity\n\n' + json.dumps(result, indent=2) + '\n', encoding='utf-8')
        write(args.output / 'job-status.json', {'status': 'complete', 'test': 'T1-connectivity', 'code_version': VERSION, 'updated_unix': time.time()})
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
        write(args.output / 'job-status.json', {'status': 'failed', 'test': 'T1-connectivity', 'error': str(exc), 'updated_unix': time.time()})
        raise
    finally:
        for rel, content in originals.items():
            (base.prior.INSTALLED / rel).write_bytes(content)
        write(args.output / 'installed-restored.json', {'verified': all((base.prior.INSTALLED / rel).read_bytes() == content for rel, content in originals.items()), 'source_unchanged': all((ROOT / 'Civ Supply Chains' / rel).read_bytes() == content for rel, content in originals.items())})


if __name__ == '__main__':
    main()
