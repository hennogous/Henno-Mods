"""C1: do dormant CivicModifiers enter native civic research valuation?

Fresh matched four-round CSC-only worlds. Identical independent scoring-probe
definitions in both arms; only two CivicModifiers attachments differ. The
subject gate follows RH's Ancient/pre-Medieval/Future-Civic/AI shape and remains
false in the Medieval fixture. No research setters, economic grants or goals.
"""
import argparse
import json
import os
import re
import shutil
import sqlite3
import time
import traceback
import zlib
from pathlib import Path

import civic_unlock_rst_trial as base
from fixed_research_trial import inventory
from paired_standard import HERE, read, sha
from run import ROOT, SAVES, write

VERSION = 'civic-modifiers-dormant-production-food-v1'
TEST = 'C1-dormant-civic-modifier'
ROUNDS = 4
PREFIX = 'CSC_TEST_CIVIC_MODIFIER_'
MODS = (PREFIX + 'PRODUCTION', PREFIX + 'FOOD')
MODIFIER_YIELDS = ('YIELD_PRODUCTION', 'YIELD_FOOD')
PAIR_TABLE = 'CivicModifiers'
PAIR_COLUMNS = 'CivicType,ModifierId'
GUARD_REQUIREMENT_COUNT = 4


def baseline_source_path(rel):
    """Default live source; resumable studies may explicitly pin an archive."""
    return ROOT / 'Civ Supply Chains' / rel


def pair_additions():
    return {(base.TARGET, m) for m in MODS}


def callback_bytes(arm):
    return base.CALLBACK_AUDIT
REFERENCE = Path.home() / 'Desktop/Codex/csc-civic-unlocks-20261020/t2-district-goal-v1/off/native-gameplay.sqlite'
RH_CIVICS = base.RST.parent / '3792072489/core/Strategies/Supporting_Systems/RH_Civics.sql'
RH_CONGRESS = RH_CIVICS.with_name('RH_Congress.sql')


def overlay(arm):
    text = base.overlay(False) + """
INSERT OR IGNORE INTO Requirements (RequirementId,RequirementType,Inverse) VALUES
 ('CSC_TEST_CIVIC_MODIFIER_AI','REQUIREMENT_PLAYER_IS_AI',0),
 ('CSC_TEST_CIVIC_MODIFIER_ANCIENT','REQUIREMENT_PLAYER_ERA_AT_LEAST',0),
 ('CSC_TEST_CIVIC_MODIFIER_BEFORE_MEDIEVAL','REQUIREMENT_PLAYER_ERA_AT_LEAST',1),
 ('CSC_TEST_CIVIC_MODIFIER_FUTURE','REQUIREMENT_PLAYER_HAS_CIVIC',0);
INSERT OR IGNORE INTO RequirementArguments (RequirementId,Name,Value) VALUES
 ('CSC_TEST_CIVIC_MODIFIER_ANCIENT','EraType','ERA_ANCIENT'),
 ('CSC_TEST_CIVIC_MODIFIER_BEFORE_MEDIEVAL','EraType','ERA_MEDIEVAL'),
 ('CSC_TEST_CIVIC_MODIFIER_FUTURE','CivicType','CIVIC_FUTURE_CIVIC');
INSERT OR IGNORE INTO RequirementSets (RequirementSetId,RequirementSetType) VALUES
 ('CSC_TEST_CIVIC_MODIFIER_DORMANT','REQUIREMENTSET_TEST_ALL');
INSERT OR IGNORE INTO RequirementSetRequirements (RequirementSetId,RequirementId) VALUES
 ('CSC_TEST_CIVIC_MODIFIER_DORMANT','CSC_TEST_CIVIC_MODIFIER_AI'),
 ('CSC_TEST_CIVIC_MODIFIER_DORMANT','CSC_TEST_CIVIC_MODIFIER_ANCIENT'),
 ('CSC_TEST_CIVIC_MODIFIER_DORMANT','CSC_TEST_CIVIC_MODIFIER_BEFORE_MEDIEVAL'),
 ('CSC_TEST_CIVIC_MODIFIER_DORMANT','CSC_TEST_CIVIC_MODIFIER_FUTURE');
INSERT OR IGNORE INTO Modifiers (ModifierId,ModifierType,SubjectRequirementSetId) VALUES
 ('CSC_TEST_CIVIC_MODIFIER_PRODUCTION','MODIFIER_PLAYER_CAPITAL_CITY_ADJUST_CITY_YIELD_CHANGE','CSC_TEST_CIVIC_MODIFIER_DORMANT'),
 ('CSC_TEST_CIVIC_MODIFIER_FOOD','MODIFIER_PLAYER_CAPITAL_CITY_ADJUST_CITY_YIELD_CHANGE','CSC_TEST_CIVIC_MODIFIER_DORMANT');
INSERT OR IGNORE INTO ModifierArguments (ModifierId,Name,Value) VALUES
 ('CSC_TEST_CIVIC_MODIFIER_PRODUCTION','YieldType','YIELD_PRODUCTION'),
 ('CSC_TEST_CIVIC_MODIFIER_PRODUCTION','Amount',100),
 ('CSC_TEST_CIVIC_MODIFIER_FOOD','YieldType','YIELD_FOOD'),
 ('CSC_TEST_CIVIC_MODIFIER_FOOD','Amount',100);
DELETE FROM CivicModifiers WHERE ModifierId LIKE 'CSC_TEST_CIVIC_MODIFIER_%';
"""
    if arm == 'on':
        text += "\nINSERT INTO CivicModifiers (CivicType,ModifierId) VALUES\n"
        text += ',\n'.join("('" + base.TARGET + "','" + m + "')" for m in MODS) + ';\n'
    return text


def native_check(db, arm, patch, source, with_rst=False):
    assert not with_rst
    rows = db.execute("SELECT CivicType,ModifierId FROM CivicModifiers WHERE ModifierId LIKE ? ORDER BY ModifierId", (PREFIX + '%',)).fetchall()
    assert rows == (sorted((base.TARGET, m) for m in MODS) if arm == 'on' else [])
    assert db.execute('SELECT ModifierId,ModifierType,SubjectRequirementSetId FROM Modifiers WHERE ModifierId LIKE ? ORDER BY ModifierId', (PREFIX + '%',)).fetchall() == sorted((m, 'MODIFIER_PLAYER_CAPITAL_CITY_ADJUST_CITY_YIELD_CHANGE', PREFIX + 'DORMANT') for m in MODS)
    assert db.execute('SELECT RequirementSetType FROM RequirementSets WHERE RequirementSetId=?', (PREFIX + 'DORMANT',)).fetchall() == [('REQUIREMENTSET_TEST_ALL',)]
    assert db.execute('SELECT COUNT(*) FROM RequirementSetRequirements WHERE RequirementSetId=?', (PREFIX + 'DORMANT',)).fetchone()[0] == GUARD_REQUIREMENT_COUNT
    assert db.execute('SELECT RequirementType,Inverse FROM Requirements WHERE RequirementId=?', (PREFIX + 'BEFORE_MEDIEVAL',)).fetchall() == [('REQUIREMENT_PLAYER_ERA_AT_LEAST', 1)]
    assert db.execute('SELECT Value FROM RequirementArguments WHERE RequirementId=? AND Name=?', (PREFIX + 'FUTURE', 'CivicType')).fetchall() == [('CIVIC_FUTURE_CIVIC',)]
    assert db.execute('SELECT ModifierId,Name,Value FROM ModifierArguments WHERE ModifierId LIKE ? ORDER BY ModifierId,Name', (PREFIX + '%',)).fetchall() == sorted((m, name, value) for m, y in zip(MODS, MODIFIER_YIELDS) for name, value in [('YieldType', y), ('Amount', '100')])
    assert not db.execute('SELECT * FROM AiFavoredItems WHERE Item=?', (base.TARGET,)).fetchall()
    for table in ('AiLists', 'AiListTypes', 'AiFavoredItems', 'Strategy_Priorities'):
        assert db.execute(f"SELECT COUNT(*) FROM {table} WHERE ListType LIKE 'CSC_AI_SERVICE_%' OR ListType LIKE 'CSC_AI_FIXED_SERVICE_%' OR ListType='CSC_TEST_RESEARCH_LIST'").fetchone()[0] == 0
    assert db.execute("SELECT COUNT(*) FROM GlobalParameters WHERE Name='RST_VERSION_MAJOR'").fetchone()[0] == 0
    assert db.execute("SELECT DefaultValue FROM PseudoYields WHERE PseudoYieldType='PSEUDOYIELD_IMPROVEMENT'").fetchone()[0] == 90
    assert db.execute("SELECT Value FROM AiFavoredItems WHERE ListType='UnitPriorityBoosts' AND Item='UNIT_BUILDER'").fetchall() == [(50,)]
    before = inventory(db)
    db.create_function('Make_Hash', 1, lambda s: zlib.crc32(s.encode()))
    db.executescript(source + '\n' + patch)
    assert inventory(db) == before, 'CSC source/overlay replay changed native definitions'
    return {'passed': True, 'arm': arm, 'target': base.TARGET, 'attachments': rows,
            'gate': 'AI AND Ancient-or-later AND before-Medieval AND Future Civic',
            'replay_identical': True, 'inventory': before}


class ModifierRunner(base.RSTRunner):
    def pin_sources(self):
        super().pin_sources()
        p = self.out / 'tuning-source-hashes.json'
        pins = read(p)
        for f in (Path(__file__), RH_CIVICS, RH_CONGRESS):
            pins[str(f)] = sha(f)
        write(p, pins)

    def archive_version(self):
        super().archive_version()
        p = self.out / 'source-version/version.json'
        v = read(p)
        v.update(code_version=VERSION, test=TEST, arm=self.arm,
                 research={'target': base.TARGET, 'modifier_ids': MODS, 'attached': self.arm == 'on',
                           'amount_each': 100, 'real_gate_expected': False,
                           'no_favored_items': True, 'no_research_setters': True},
                 analyzed_rounds=ROUNDS)
        examples = {}
        for f in (RH_CIVICS, RH_CONGRESS):
            dest = p.parent / 'rh-readonly-examples' / f.name
            dest.parent.mkdir(exist_ok=True)
            shutil.copy2(f, dest)
            examples[f.name] = sha(dest)
        v['rh_example_hashes'] = examples
        write(p, v)

    def guard_check(self, label):
        code = "local rows={};for pid=1,5 do local c=Players[pid]:GetCulture();local f=c:HasCivic(GameInfo.Civics.CIVIC_FUTURE_CIVIC.Index);local t=c:HasCivic(GameInfo.Civics.CIVIC_DIVINE_RIGHT.Index);assert(not f,'Dormant gate must remain false');print('CSC_DORMANT_GUARD',pid,tostring(f),tostring(t));end;"
        text = self.cmd(code, 'CSC_AI_Research', label, wait=3)
        rows = [(int(p), f == 'true', t == 'true') for p, f, t in re.findall(r'CSC_DORMANT_GUARD\s+(\d+)\s+(true|false)\s+(true|false)', text)]
        assert len(rows) == 5 and all(not f for p, f, t in rows)
        write(self.out / (label + '.json'), {'passed': True, 'players': rows, 'dormant_gate_false': True})

    def observe(self):
        self.guard_check('guard-before')
        data = super().observe()
        self.guard_check('guard-after')
        assert all(row['civic'] != base.TARGET for row in data['completions']), 'Short dormant probe target unexpectedly completed; inspect economic effects before comparison'
        return data

    def preserve_existing_game(self):
        self.states()
        if 'MainMenu' in self.state:
            return
        assert 'PlotInfo' in self.state and 'GameCore_Tuner' in self.state, 'Unknown existing game state'
        self.cmd("assert(not AutoplayManager.IsActive(),'Another autoplay owns the current world');", 'GameCore_Tuner', 'existing-autoplay-check')
        name = 'CSC_before_civic_modifiers_' + time.strftime('%Y%m%d_%H%M%S')
        start = time.time()
        self.cmd("local s={Name='" + name + "',Location=SaveLocations.LOCAL_STORAGE,Type=SaveTypes.SINGLE_PLAYER,IsAutosave=false,IsQuicksave=false};assert(Network.SaveGame(s)~=false);", 'PlotInfo', 'preserve-existing-game', wait=5)
        saved = SAVES / (name + '.Civ6Save')
        for _ in range(20):
            if saved.exists() and saved.stat().st_mtime >= start - 2 and saved.stat().st_size:
                size = saved.stat().st_size
                time.sleep(1)
                if size == saved.stat().st_size:
                    dest = self.out / saved.name
                    shutil.copy2(saved, dest)
                    write(self.out / 'preserved-existing-game.json', {'path': str(saved), 'archived': str(dest), 'sha256': sha(dest)})
                    self.menu()
                    return
            time.sleep(1)
        raise RuntimeError('Existing game not preserved; do not leave it')


def preflight(path):
    src = sqlite3.connect(REFERENCE.as_uri() + '?mode=ro', uri=True)
    source = (ROOT / 'Civ Supply Chains' / base.prior.SQL).read_text(encoding='utf-8')
    results = {}
    for arm in ('off', 'on'):
        db = sqlite3.connect(':memory:')
        src.backup(db)
        db.create_function('Make_Hash', 1, lambda s: zlib.crc32(s.encode()))
        db.executescript(overlay(arm))
        results[arm] = native_check(db, arm, overlay(arm), source)
    assert {k for k in results['off']['inventory'] if results['off']['inventory'][k] != results['on']['inventory'][k]} == ({PAIR_TABLE} if PAIR_TABLE else set())
    write(path, {'passed': True, 'only_native_table_difference': PAIR_TABLE,
                 'cases': {a: {k: v for k, v in x.items() if k != 'inventory'} for a, x in results.items()}})


def comparison(root):
    scores = {a: base.score_rows(root / a / 'native-logs/AI_GovtPolicies.csv', 71, 74) for a in ('off', 'on')}
    common = scores['off'].keys() & scores['on'].keys()
    initial = sorted(k for k in common if k[0] == 71)
    changes = [{'player': k[1], 'civic': k[2], 'off': scores['off'][k][0], 'on': scores['on'][k][0]}
               for k in initial if scores['off'][k] != scores['on'][k]]
    targets = {p: {a: scores[a].get((71, p, base.TARGET)) for a in ('off', 'on')} for p in range(1, 6)}
    db = sqlite3.connect(root / 'on/native-gameplay.sqlite')
    allowed = {base.TARGET}
    while True:
        expanded = allowed | {c for c, p in db.execute('SELECT Civic,PrereqCivic FROM CivicPrereqs') if p in allowed}
        if expanded == allowed:
            break
        allowed = expanded
    return {'code_version': VERSION, 'test': TEST, 'target': base.TARGET,
            'initial_matched_records': len(initial), 'initial_changes': changes, 'initial_targets': targets,
            'target_score_response': any(x['civic'] == base.TARGET for x in changes),
            'conditional_followup_justified': any(x['civic'] == base.TARGET for x in changes) and all(x['civic'] in allowed for x in changes),
            'prerequisite_propagation_allowed': sorted(allowed),
            'matched_records_all_rounds': len(common),
            'different_records_all_rounds': sum(scores['off'][k] != scores['on'][k] for k in common),
            'limits': ['One short matched artificial map; score-consumer calibration, not natural performance.',
                       'Dormant modifier forecasting does not establish respect for material conditions.',
                       'Later world differences are secondary; initial score response is primary.']}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--preflight-only', action='store_true')
    parser.add_argument('--continue-study', action='store_true')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=args.continue_study)
    preflight(args.output / ('offline-native-preflight-v2.json' if args.continue_study else 'offline-native-preflight.json'))
    if args.preflight_only:
        return
    base.native_check = native_check
    base.VERSION = base.prior.VERSION = VERSION
    originals = {rel: (base.prior.INSTALLED / rel).read_bytes() for rel in (base.prior.SQL, base.prior.LUA)}
    for rel, content in originals.items():
        assert content == baseline_source_path(rel).read_bytes(), 'Installed baseline differs from selected source reference: ' + str(rel)
        p = args.output / 'original-installed' / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(content)
    runner, reference = None, None
    write(args.output / 'job-status.json', {'status': 'starting', 'test': TEST,
                                          'pid': os.getpid(), 'code_version': VERSION, 'updated_unix': time.time()})
    try:
        # Preserve a pre-existing live game before altering installed files.
        bootstrap = ModifierRunner(args.output / 'session-preservation')
        bootstrap.preserve_existing_game()
        for arm in ('off', 'on'):
            if args.continue_study and (args.output / arm / 'complete.json').exists():
                assert read(args.output / 'controller-recovery-v2/recovery-audit.json')['passed']
                assert read(args.output / arm / 'complete.json')['passed']
                reference = [read(args.output / arm / p) for p in ('game-01/initial-map.json', 'game-01/turn-071.json', 'original-preferences.json')]
                continue
            patch = overlay(arm)
            for rel, content in originals.items():
                assert baseline_source_path(rel).read_bytes() == content
            (base.prior.INSTALLED / base.prior.SQL).write_bytes(originals[base.prior.SQL] + b'\n' + patch.encode())
            (base.prior.INSTALLED / base.prior.LUA).write_bytes(originals[base.prior.LUA] + callback_bytes(arm))
            runner = ModifierRunner(args.output / arm)
            runner.original_rst = False
            runner.phase, runner.arm, runner.rounds, runner.overlay, runner.keep_game = 'dormant-modifier', arm, ROUNDS, patch, False
            runner.captures = Path.home() / 'Desktop/Codex/csc-implemented-native-20261016'
            runner.baseline = Path.home() / 'Desktop/Codex/csc-ai-paired-standard-20261016'
            runner.previous = Path.home() / 'Desktop/Codex/csc-ai-improvement-research-20261019/trial-v1b'
            if arm == 'on':
                runner.fixture_reference = args.output / 'off/fixture-census.json'
            runner.pin_sources()
            runner.archive_version()
            write(args.output / 'active-stage.json', {'test': TEST, 'arm': arm, 'output': str(runner.out), 'pid': os.getpid()})
            write(args.output / 'job-status.json', {'status': 'running', 'test': TEST, 'arm': arm, 'pid': os.getpid(), 'updated_unix': time.time()})
            runner.wait('MainMenu', 180)
            runner.config()
            runner.start_pair(1)
            state = [read(runner.out / 'game-01/initial-map.json'), read(runner.out / 'game-01/turn-071.json'), read(runner.out / 'original-preferences.json')]
            if reference is None:
                reference = state
            else:
                assert state == reference, 'Initial world/census/preferences differ'
                old = read(args.output / 'off/native-database-validation.json')['inventory']
                new = read(runner.out / 'native-database-validation.json')['inventory']
                assert {k for k in old if old[k] != new[k]} == ({PAIR_TABLE} if PAIR_TABLE else set())
                a = sqlite3.connect(args.output / 'off/native-gameplay.sqlite')
                b = sqlite3.connect(runner.out / 'native-gameplay.sqlite')
                if PAIR_TABLE:
                    av = set(a.execute('SELECT ' + PAIR_COLUMNS + ' FROM ' + PAIR_TABLE))
                    bv = set(b.execute('SELECT ' + PAIR_COLUMNS + ' FROM ' + PAIR_TABLE))
                    assert not av - bv and bv - av == pair_additions()
            write(runner.out / 'paired-preflight.json', {'passed': True, 'only_treatment_table': PAIR_TABLE, 'expected_added_rows': sorted(pair_additions()), 'economic_guard_expected_false': True})
            runner.observe()
            runner.menu()
            runner.restore_verified()
            write(runner.out / 'complete.json', {'passed': True, 'arm': arm, 'actual_endpoint': runner.actual_endpoint, 'analyzed_rounds': ROUNDS})
        result = comparison(args.output)
        write(args.output / 'comparison.json', result)
        (args.output / 'report.md').write_text('# Dormant civic-modifier score control\n\n' + json.dumps(result, indent=2) + '\n', encoding='utf-8')
        write(args.output / 'job-status.json', {'status': 'complete', 'test': TEST, 'target_score_response': result['target_score_response'], 'updated_unix': time.time()})
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
        write(args.output / 'job-status.json', {'status': 'failed', 'test': TEST, 'error': str(exc), 'updated_unix': time.time()})
        raise
    finally:
        for rel, content in originals.items():
            (base.prior.INSTALLED / rel).write_bytes(content)
        write(args.output / 'installed-restored.json', {'verified': all((base.prior.INSTALLED / rel).read_bytes() == content for rel, content in originals.items()), 'source_unchanged': all((ROOT / 'Civ Supply Chains' / rel).read_bytes() == content for rel, content in originals.items()), 'baseline_reference_unchanged': all(baseline_source_path(rel).read_bytes()==content for rel,content in originals.items())})


if __name__ == '__main__':
    main()
