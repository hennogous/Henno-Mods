"""Does an inactive/active strategy gate a trait-owned civic preference?

Two fresh CSC-only cases have byte-identical native SQL and the same preferred
civic. Only the Lua strategy condition returns false/true. This tests an AND
gate; static trait success alone cannot establish conditional research guidance.
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
from fixed_research_trial import inventory
from paired_standard import HERE, read, sha
from run import ROOT, write

VERSION = 'civic-unlock-dual-trait-strategy-gate-v2-empty-map-safe'
LIST = 'CSC_TEST_CIVIC_DUAL_GATE'
STRATEGY = 'STRATEGY_CSC_TEST_CIVIC_DUAL_GATE'


def overlay():
    return base.overlay(False) + """
INSERT OR IGNORE INTO AiListTypes (ListType) VALUES ('CSC_TEST_CIVIC_DUAL_GATE');
DELETE FROM AiLists WHERE ListType='CSC_TEST_CIVIC_DUAL_GATE';
INSERT INTO AiLists (ListType,LeaderType,System) VALUES
 ('CSC_TEST_CIVIC_DUAL_GATE','TRAIT_LEADER_LUDWIG','Civics');
INSERT INTO AiFavoredItems (ListType,Item,Favored,Value) VALUES
 ('CSC_TEST_CIVIC_DUAL_GATE','CIVIC_DIVINE_RIGHT',1,0);
INSERT OR IGNORE INTO Types (Type,Kind) VALUES ('STRATEGY_CSC_TEST_CIVIC_DUAL_GATE','KIND_VICTORY_STRATEGY');
INSERT OR IGNORE INTO Strategies (StrategyType,VictoryType,NumConditionsNeeded) VALUES
 ('STRATEGY_CSC_TEST_CIVIC_DUAL_GATE',NULL,1);
DELETE FROM StrategyConditions WHERE StrategyType='STRATEGY_CSC_TEST_CIVIC_DUAL_GATE';
INSERT INTO StrategyConditions (StrategyType,ConditionFunction,StringValue,ThresholdValue) VALUES
 ('STRATEGY_CSC_TEST_CIVIC_DUAL_GATE','Call Lua Function','CSC_TestDualCivicGate',1);
INSERT OR IGNORE INTO Strategy_Priorities (StrategyType,ListType) VALUES
 ('STRATEGY_CSC_TEST_CIVIC_DUAL_GATE','CSC_TEST_CIVIC_DUAL_GATE');
"""


def callback(active):
    return ("""
CSC_RESEARCH_PROBE_NATIVE={version='rst-original-list-v1',experiment_version='dual-gate-v1',gate_active=GATE,calls={},first_true={},errors={}};
GameEvents.CSC_TestDualCivicGate.Add(function(pid,which)
 local r=CSC_RESEARCH_PROBE_NATIVE;local key=tostring(pid)..':'..tostring(which);
 r.calls[key]=(r.calls[key] or 0)+1;
 local active=r.gate_active and pid==1 and PlayerManager.IsAlive(pid) and not Players[pid]:IsHuman();
 if active and not r.first_true[key] then r.first_true[key]=Game.GetCurrentGameTurn() end;
 return active;
end);
print('CSC_DUAL_CIVIC_GATE_READY',CSC_RESEARCH_PROBE_NATIVE.gate_active);
""".replace('GATE', str(active).lower(), 1)).encode()


def native_check(db, arm, patch, source, with_rst=False):
    assert not with_rst
    assert db.execute("SELECT ListType,Favored,Value FROM AiFavoredItems WHERE Item='CIVIC_DIVINE_RIGHT'").fetchall() == [(LIST, 1, 0)]
    assert db.execute('SELECT LeaderType,AgendaType,System FROM AiLists WHERE ListType=?', (LIST,)).fetchall() == [('TRAIT_LEADER_LUDWIG', None, 'Civics')]
    assert db.execute('SELECT ConditionFunction,StringValue,ThresholdValue FROM StrategyConditions WHERE StrategyType=?', (STRATEGY,)).fetchall() == [('Call Lua Function', 'CSC_TestDualCivicGate', 1)]
    assert db.execute('SELECT ListType FROM Strategy_Priorities WHERE StrategyType=?', (STRATEGY,)).fetchall() == [(LIST,)]
    assert db.execute("SELECT COUNT(*) FROM GlobalParameters WHERE Name='RST_VERSION_MAJOR'").fetchone()[0] == 0
    assert db.execute("SELECT DefaultValue FROM PseudoYields WHERE PseudoYieldType='PSEUDOYIELD_IMPROVEMENT'").fetchone()[0] == 90
    assert db.execute("SELECT Value FROM AiFavoredItems WHERE ListType='UnitPriorityBoosts' AND Item='UNIT_BUILDER'").fetchall() == [(50,)]
    for table in ('AiLists', 'AiListTypes', 'AiFavoredItems', 'Strategy_Priorities'):
        assert db.execute(f"SELECT COUNT(*) FROM {table} WHERE ListType LIKE 'CSC_AI_SERVICE_%' OR ListType LIKE 'CSC_AI_FIXED_SERVICE_%' OR ListType='CSC_TEST_RESEARCH_LIST'").fetchone()[0] == 0
    before = inventory(db)
    db.create_function('Make_Hash', 1, lambda s: zlib.crc32(s.encode()))
    db.executescript(source + '\n' + patch)
    assert inventory(db) == before
    return {'passed': True, 'arm': arm, 'trait_and_strategy_bound': True,
            'identical_native_definitions_expected': True, 'replay_identical': True, 'inventory': before}


class DualRunner(base.RSTRunner):
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
        v.update(code_version=VERSION, test='T1-dual-gate', arm=self.arm,
                 research={'target': base.TARGET, 'list': LIST, 'trait': 'TRAIT_LEADER_LUDWIG',
                           'strategy': STRATEGY, 'favored': 1, 'value': 0,
                           'gate_active': self.arm == 'on', 'primary_player': 1,
                           'no_current_civic_reset': True}, analyzed_rounds=self.rounds)
        write(path, v)

    def observe(self):
        data = super().observe()
        active = self.arm == 'on'
        assert data['native']['gate_active'] is active
        assert data['native']['calls'].get('1:1', 0) > 0, 'Condition was never evaluated'
        log = (self.out / 'native-logs/AI_Victories.csv').read_text(errors='replace')
        following = re.findall(r'^\s*(\d+),\s*1,\s*' + STRATEGY + r',\s*Following\s*$', log, re.M)
        assert bool(following) is active, 'Native Following differs from intended gate'
        # Empty Lua tables serialize as []; populated string-key maps as objects.
        first_true = data['native']['first_true'] or {}
        assert isinstance(first_true, dict)
        assert ('1:1' in first_true) is active
        write(self.out / 'strategy-activation-validation.json', {
            'passed': True, 'expected_active': active, 'callback_invocations': data['native']['calls']['1:1'],
            'first_callback_true': first_true.get('1:1'),
            'first_native_following': min(map(int, following)) if following else None})
        return data


def preflight(path):
    original = Path.home() / 'Desktop/Codex/csc-civic-unlocks-20261020/t1-minimal-csc-v2/off/native-gameplay.sqlite'
    src = sqlite3.connect(original.as_uri() + '?mode=ro', uri=True)
    db = sqlite3.connect(':memory:')
    src.backup(db)
    db.create_function('Make_Hash', 1, lambda s: zlib.crc32(s.encode()))
    patch = overlay()
    db.executescript(patch)
    result = native_check(db, 'both', patch, (ROOT / 'Civ Supply Chains' / base.prior.SQL).read_text(encoding='utf-8'))
    write(path, {k: v for k, v in result.items() if k != 'inventory'})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--preflight-only', action='store_true')
    parser.add_argument('--continue-study', action='store_true',
                        help='Reuse independently recovered OFF; run only missing ON.')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=args.continue_study)
    preflight(args.output / ('offline-native-preflight-v2.json' if args.continue_study else 'offline-native-preflight.json'))
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
        if args.continue_study:
            assert p.read_bytes() == content, 'Original installed source differs'
        else:
            p.write_bytes(content)
    runner, reference = None, None
    if args.continue_study:
        assert read(args.output / 'off-offline-recovery-audit.json')['passed']
        assert read(args.output / 'off/complete.json')['passed']
        assert read(args.output / 'off/preferences-restored.json')['verified']
        assert read(args.output / 'off/strategy-activation-validation.json')['expected_active'] is False
        assert not (args.output / 'on').exists(), 'Do not overwrite or replay ON'
        off = args.output / 'off'
        version = read(off / 'source-version/version.json')
        for key, folder in (('source_files', 'repository'), ('installed_files', 'installed'),
                            ('workshop_files', 'workshop-real-strategy')):
            for rel, digest in version[key].items():
                assert sha(off / 'source-version' / folder / rel) == digest, rel
        archived = off / 'source-version/repository/project/tools/ai_baseline/civic_unlock_dual_gate_trial.py'
        old = {'__name__': 'archived_dual_gate', '__file__': str(archived)}
        exec(compile(archived.read_text(encoding='utf-8'), str(archived), 'exec'), old)
        assert old['overlay']() == overlay(), 'Native overlay changed during controller repair'
        for active in (False, True):
            assert old['callback'](active) == callback(active), 'Native callback changed during repair'
        reference = [read(off / 'game-01/initial-map.json'), read(off / 'game-01/turn-071.json'),
                     read(off / 'original-preferences.json'), read(off / 'native-database-validation.json')['inventory']]
    write(args.output / 'job-status.json', {'status': 'starting', 'test': 'T1-dual-gate', 'pid': os.getpid(), 'code_version': VERSION})
    try:
        for arm in (('on',) if args.continue_study else ('off', 'on')):
            for rel, content in originals.items():
                assert (ROOT / 'Civ Supply Chains' / rel).read_bytes() == content
            patch = overlay()
            (base.prior.INSTALLED / base.prior.SQL).write_bytes(originals[base.prior.SQL] + b'\n' + patch.encode())
            (base.prior.INSTALLED / base.prior.LUA).write_bytes(originals[base.prior.LUA] + callback(arm == 'on'))
            runner = DualRunner(args.output / arm)
            runner.original_rst = False
            runner.phase, runner.arm, runner.rounds, runner.overlay, runner.keep_game = 'dual-gate', arm, 8, patch, False
            runner.captures = Path.home() / 'Desktop/Codex/csc-implemented-native-20261016'
            runner.baseline = Path.home() / 'Desktop/Codex/csc-ai-paired-standard-20261016'
            runner.previous = Path.home() / 'Desktop/Codex/csc-ai-improvement-research-20261019/trial-v1b'
            if arm == 'on':
                runner.fixture_reference = args.output / 'off/fixture-census.json'
            runner.pin_sources()
            runner.archive_version()
            write(args.output / 'active-stage.json', {'test': 'T1-dual-gate', 'arm': arm, 'output': str(runner.out), 'pid': os.getpid()})
            write(args.output / 'job-status.json', {'status': 'running', 'test': 'T1-dual-gate', 'arm': arm, 'pid': os.getpid(), 'updated_unix': time.time()})
            runner.wait('MainMenu', 180)
            runner.config()
            runner.start_pair(1)
            state = [read(runner.out / 'game-01/initial-map.json'), read(runner.out / 'game-01/turn-071.json'), read(runner.out / 'original-preferences.json'), read(runner.out / 'native-database-validation.json')['inventory']]
            if reference is None:
                reference = state
            else:
                assert state == reference, 'Expected identical fresh native world/census/preferences/SQL'
            write(runner.out / 'paired-preflight.json', {'passed': True, 'arm': arm, 'native_sql_identical': True, 'world_census_preferences_equal': True, 'only_treatment': 'Lua condition false/true'})
            runner.observe()
            runner.menu()
            runner.restore_verified()
            write(runner.out / 'complete.json', {'passed': True, 'arm': arm, 'actual_endpoint': runner.actual_endpoint, 'analyzed_rounds': 8})
        result = base.compare(args.output, False)
        result.update(code_version=VERSION, test='T1-dual-gate', analyzed_rounds=8,
                      only_treatment='Lua condition false/true; native SQL identical',
                      condition_validation={arm: read(args.output / arm / 'strategy-activation-validation.json') for arm in ('off', 'on')})
        result['controller_recovery'] = {'off_reused_without_replay': args.continue_study,
                                        'native_run_versions': {arm: read(args.output / arm / 'source-version/version.json')['code_version'] for arm in ('off', 'on')}}
        write(args.output / 'comparison.json', result)
        (args.output / 'report.md').write_text('# Trait plus strategy civic gate\n\n' + json.dumps(result, indent=2) + '\n', encoding='utf-8')
        write(args.output / 'job-status.json', {'status': 'complete', 'test': 'T1-dual-gate', 'initial_score_response': result['initial_score_response'], 'updated_unix': time.time()})
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
        write(args.output / 'job-status.json', {'status': 'failed', 'test': 'T1-dual-gate', 'error': str(exc), 'updated_unix': time.time()})
        raise
    finally:
        for rel, content in originals.items():
            (base.prior.INSTALLED / rel).write_bytes(content)
        write(args.output / 'installed-restored.json', {'verified': all((base.prior.INSTALLED / rel).read_bytes() == content for rel, content in originals.items()), 'source_unchanged': all((ROOT / 'Civ Supply Chains' / rel).read_bytes() == content for rel, content in originals.items())})


if __name__ == '__main__':
    main()
