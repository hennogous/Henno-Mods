"""T0: native civic-score calibration; three fresh, matched, disposable worlds.

Only PSEUDOYIELD_CIVIC DefaultValue differs (0/reference/50). Reuses the proven
framed observer, fresh-start preflight, read retries and preference restoration.
Never changes current research, grants progress, or retries a mutation.
"""
import argparse
import csv
import json
import os
import sqlite3
import time
import traceback
import zlib
from pathlib import Path

import strategy_research_trial as prior
from fixed_research_trial import inventory
from improvement_research_trial import ResearchRunner
from paired_standard import HERE, read, sha
from run import ROOT, write

VERSION = 'civic-unlock-t0-score-control-v1'
REFERENCE = ROOT / 'project/tools/ai_baseline/strategy_research_control.sql'
NATIVE_REFERENCE = Path.home() / 'Desktop/Codex/csc-ai-clean-strategies-20261020/research/custom/native-gameplay.sqlite'


def overlay(value):
    return REFERENCE.read_text(encoding='utf-8') + (
        "\nUPDATE PseudoYields SET DefaultValue=" + str(value) +
        " WHERE PseudoYieldType='PSEUDOYIELD_CIVIC';\n")


def native_check(db, phase, arm, patch, source):
    value = {'zero': 0, 'reference': 5, 'high': 50}[arm]
    assert db.execute("SELECT DefaultValue FROM PseudoYields WHERE PseudoYieldType='PSEUDOYIELD_CIVIC'").fetchall() == [(value,)]
    for table in ('AiListTypes', 'AiLists', 'AiFavoredItems', 'Strategy_Priorities'):
        assert db.execute(f"SELECT COUNT(*) FROM {table} WHERE ListType LIKE 'CSC_AI_SERVICE_%' OR ListType LIKE 'CSC_AI_FIXED_SERVICE_%' OR ListType='CSC_TEST_RESEARCH_LIST'").fetchone()[0] == 0
    assert db.execute("SELECT COUNT(*) FROM AiFavoredItems WHERE Item='CIVIC_NAVAL_TRADITION'").fetchone()[0] == 0
    assert db.execute("SELECT DefaultValue FROM PseudoYields WHERE PseudoYieldType='PSEUDOYIELD_IMPROVEMENT'").fetchone()[0] == 90
    assert db.execute("SELECT Value FROM AiFavoredItems WHERE ListType='UnitPriorityBoosts' AND Item='UNIT_BUILDER'").fetchall() == [(50,)]
    before = inventory(db)
    db.create_function('Make_Hash', 1, lambda s: zlib.crc32(s.encode()))
    db.executescript(source + '\n' + patch)
    assert before == inventory(db), 'Source/overlay replay changed native tables'
    return {'passed': True, 'phase': phase, 'arm': arm, 'civic_default': value,
            'named_civic_preferences': False, 'replay_identical': True, 'inventory': before}


class ScoreRunner(prior.StrategyRunner):
    def pin_sources(self):
        super().pin_sources()
        path = self.out / 'tuning-source-hashes.json'
        pins = read(path)
        pins[str(Path(__file__))] = sha(Path(__file__))
        write(path, pins)

    def archive_version(self):
        ResearchRunner.archive_version(self)
        path = self.out / 'source-version/version.json'
        version = read(path)
        version.update(code_version=VERSION, test='T0', arm=self.arm,
                       research={'parameter': 'PSEUDOYIELD_CIVIC.DefaultValue',
                                 'value': self.civic_default, 'named_preferences': False,
                                 'no_current_civic_reset': True},
                       analyzed_rounds=self.rounds, separate_citybuild_calibration=False)
        write(path, version)
        (path.parent / 'applied-overlay.sql').write_text(self.overlay, encoding='utf-8')


def score_rows(path, start=71, stop=74):
    result = {}
    with path.open(encoding='utf-8-sig', errors='strict') as stream:
        for row in csv.reader(stream, skipinitialspace=True):
            try:
                turn, pid = int(row[0]), int(row[1])
            except (ValueError, IndexError):
                continue
            if start <= turn <= stop and 1 <= pid <= 5 and len(row) >= 6 and row[2] == 'Civic':
                key = (turn, pid, row[3])
                assert key not in result, ('Duplicate candidate row', key)
                result[key] = tuple(row[4:])
    return result


def score_comparison(output):
    data = {arm: score_rows(output / arm / 'native-logs/AI_GovtPolicies.csv')
            for arm in ('zero', 'reference', 'high')}
    result = {'window': [71, 74], 'candidate_rows': {arm: len(rows) for arm, rows in data.items()},
              'comparisons': {}, 'telemetry_available': all(bool(rows) for rows in data.values())}
    for arm in ('zero', 'high'):
        base, treatment = data['reference'], data[arm]
        common = base.keys() & treatment.keys()
        score_changes = [key for key in common if float(base[key][0]) != float(treatment[key][0])]
        result['comparisons'][arm] = {
            'matched_candidates': len(common), 'different_logged_scores': len(score_changes),
            'only_reference': len(base.keys() - treatment.keys()),
            'only_treatment': len(treatment.keys() - base.keys()),
            'examples': [{'turn': key[0], 'player': key[1], 'civic': key[2],
                          'reference_score': base[key][0], 'treatment_score': treatment[key][0]}
                         for key in sorted(score_changes)[:8]]}
    # Turn71 precedes natural-play divergence and is the primary controlled score comparison.
    initial = {}
    for arm in ('zero', 'high'):
        base, treatment = data['reference'], data[arm]
        keys = [key for key in base.keys() & treatment.keys() if key[0] == 71]
        initial[arm] = {'matched': len(keys), 'score_changes': sum(float(base[k][0]) != float(treatment[k][0]) for k in keys)}
    result['initial_turn_score_comparisons'] = initial
    result['measured_response'] = (any(v['score_changes'] > 0 for v in initial.values())
                                   if result['telemetry_available'] and all(v['matched'] for v in initial.values())
                                   else None)
    result['limits'] = ['CSV scores have limited precision.', 'Broad civic valuation does not target a specific unlock.',
                        'Later scores may reflect diverging natural decisions; initial-turn matches are primary.']
    return result


def offline_preflight(path):
    source = (ROOT / 'Civ Supply Chains' / prior.SQL).read_text(encoding='utf-8')
    cases = {}
    with sqlite3.connect(NATIVE_REFERENCE.as_uri() + '?mode=ro', uri=True) as original:
        assert original.execute("SELECT DefaultValue FROM PseudoYields WHERE PseudoYieldType='PSEUDOYIELD_CIVIC'").fetchone()[0] == 5, 'Reference is not expected vanilla5'
        for arm, value in (('zero', 0), ('reference', 5), ('high', 50)):
            db = sqlite3.connect(':memory:')
            original.backup(db)
            patch = overlay(value)
            db.create_function('Make_Hash', 1, lambda s: zlib.crc32(s.encode()))
            db.executescript(patch)
            cases[arm] = native_check(db, 'score', arm, patch, source)
            db.close()
    for arm in ('zero', 'high'):
        assert {name for name, digest in cases[arm]['inventory'].items()
                if digest != cases['reference']['inventory'][name]} == {'PseudoYields'}
    write(path, {'passed': True, 'only_changed_table': 'PseudoYields',
                 'cases': {arm: {k: v for k, v in case.items() if k != 'inventory'} for arm, case in cases.items()}})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--preflight-only', action='store_true')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    offline_preflight(args.output / 'offline-native-preflight.json')
    if args.preflight_only:
        return
    prior.native_check = native_check
    prior.VERSION = VERSION
    originals = {rel: (prior.INSTALLED / rel).read_bytes() for rel in (prior.SQL, prior.LUA)}
    for rel, content in originals.items():
        assert content == (ROOT / 'Civ Supply Chains' / rel).read_bytes(), ('Source/install mismatch', str(rel))
        destination = args.output / 'original-installed' / rel
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(content)
    runner = None
    reference = None
    write(args.output / 'job-status.json', {'status': 'starting', 'pid': os.getpid(), 'code_version': VERSION})
    try:
        for arm, value in (('reference', 5), ('zero', 0), ('high', 50)):
            for rel, content in originals.items():
                assert (ROOT / 'Civ Supply Chains' / rel).read_bytes() == content
            patch = overlay(value)
            (prior.INSTALLED / prior.SQL).write_bytes(originals[prior.SQL] + b'\n' + patch.encode())
            (prior.INSTALLED / prior.LUA).write_bytes(originals[prior.LUA] + b'\n' + (HERE / 'strategy_research_callbacks.lua').read_bytes())
            runner = ScoreRunner(args.output / arm)
            runner.phase, runner.arm, runner.rounds = 'score', arm, 4
            runner.civic_default, runner.overlay, runner.keep_game = value, patch, False
            runner.captures = Path.home() / 'Desktop/Codex/csc-implemented-native-20261016'
            runner.baseline = Path.home() / 'Desktop/Codex/csc-ai-paired-standard-20261016'
            runner.previous = Path.home() / 'Desktop/Codex/csc-ai-improvement-research-20261019/trial-v1b'
            if arm != 'reference':
                runner.fixture_reference = args.output / 'reference/fixture-census.json'
            runner.pin_sources()
            runner.archive_version()
            write(args.output / 'active-stage.json', {'test': 'T0', 'arm': arm, 'output': str(runner.out), 'pid': os.getpid()})
            write(args.output / 'job-status.json', {'status': 'running', 'test': 'T0', 'arm': arm, 'pid': os.getpid(), 'updated_unix': time.time()})
            runner.wait('MainMenu', 180)
            runner.config()
            runner.start_pair(1)
            values = {'world': read(runner.out / 'game-01/initial-map.json'),
                      'census': read(runner.out / 'game-01/turn-071.json'),
                      'preferences': read(runner.out / 'original-preferences.json')}
            if reference is None:
                reference = values
            else:
                assert reference == values, 'Fresh initial world/census/preferences differ'
                old = read(args.output / 'reference/native-database-validation.json')['inventory']
                new = read(runner.out / 'native-database-validation.json')['inventory']
                assert {k for k in old if old[k] != new[k]} == {'PseudoYields'}
            write(runner.out / 'paired-preflight.json', {'passed': True, 'initial_world_census_preferences_identical': True, 'only_treatment_table': 'PseudoYields'})
            runner.observe()
            runner.menu()
            runner.restore_verified()
            write(runner.out / 'complete.json', {'passed': True, 'arm': arm, 'actual_endpoint': runner.actual_endpoint, 'analyzed_rounds': 4})
        result = score_comparison(args.output)
        write(args.output / 'comparison.json', result)
        (args.output / 'report.md').write_text('# Civic research score control\n\n' +
            'PSEUDOYIELD_CIVIC defaults0/5/50; four analyzed Online rounds per fresh world.\n\n' +
            'Measured initial-score response: ' + str(result['measured_response']) + '\n\n' +
            json.dumps(result['initial_turn_score_comparisons'], indent=2) + '\n', encoding='utf-8')
        write(args.output / 'job-status.json', {'status': 'complete', 'test': 'T0', 'measured_response': result['measured_response'], 'code_version': VERSION, 'updated_unix': time.time()})
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
        write(args.output / 'job-status.json', {'status': 'failed', 'test': 'T0', 'error': str(exc), 'updated_unix': time.time()})
        raise
    finally:
        for rel, content in originals.items():
            (prior.INSTALLED / rel).write_bytes(content)
        write(args.output / 'installed-restored.json', {
            'verified': all((prior.INSTALLED / rel).read_bytes() == content for rel, content in originals.items()),
            'source_unchanged': all((ROOT / 'Civ Supply Chains' / rel).read_bytes() == content for rel, content in originals.items()),
            'hashes': {str(rel): sha(prior.INSTALLED / rel) for rel in originals}})


if __name__ == '__main__':
    main()
