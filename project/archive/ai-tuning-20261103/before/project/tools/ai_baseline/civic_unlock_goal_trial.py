"""T2 native district-prerequisite goal: original civic binding versus disconnected.

Disposable CSC-only fixture, not a gameplay proposal. Bakers requires Divine
Right in BOTH arms. Germany's population-seven fixture city has a free third
slot and an empty owned land tile. Only node8/Desired Civics differs.
No research API setters or invented trigger/list payloads are used.
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

VERSION = 'civic-unlock-t2-native-district-civic-goal-v1'
TREE = 'Build City District'
DISTRICT = 'DISTRICT_CSC_BAKERS_QUARTER'
LIST = 'CSC_TEST_GOAL_DISTRICT_DEMAND'
ROUNDS = 20
EXTRA = """
do
 local pid,c=1,chosen[1]
 local city
 for _,candidate in Players[pid]:GetCities():Members() do
  if candidate:GetX()==c:GetX() and candidate:GetY()==c:GetY() then city=candidate;break end
 end
 assert(city,'Missing original fixture city')
 city:ChangePopulation(7-city:GetPopulation())
 local free
 for _,p in ipairs(Map.GetAdjacentPlots(c:GetX(),c:GetY())) do
  if p:GetOwner()==pid and not p:IsWater() and not p:IsImpassable() and p:GetDistrictType()==-1 and p:GetResourceType()==-1 then free=p;break end
 end
 assert(free,'No free third-district plot')
 TerrainBuilder.SetFeatureType(free,-1)
 assert(city:GetPopulation()==7 and free:GetDistrictType()==-1 and free:GetResourceType()==-1)
 print('CSC_GOAL_FREE_SLOT',pid,city:GetID(),free:GetIndex(),city:GetPopulation())
end
"""


def overlay(arm):
    tag = "'Needed Civic'" if arm == 'on' else 'NULL'
    return base.overlay(False) + f"""
UPDATE Districts SET PrereqCivic='CIVIC_DIVINE_RIGHT' WHERE DistrictType='{DISTRICT}';
INSERT OR IGNORE INTO AiListTypes (ListType) VALUES ('{LIST}');
DELETE FROM AiLists WHERE ListType='{LIST}';
INSERT INTO AiLists (ListType,LeaderType,System) VALUES ('{LIST}','TRAIT_LEADER_LUDWIG','Districts');
DELETE FROM AiFavoredItems WHERE ListType='{LIST}';
INSERT INTO AiFavoredItems (ListType,Item,Favored,Value) VALUES ('{LIST}','{DISTRICT}',1,0);
UPDATE TreeData SET Tag={tag},DefaultData=NULL
 WHERE TreeName='{TREE}' AND NodeId=8 AND DefnId=6;
"""


def native_check(db, arm, patch, source, with_rst=False):
    assert not with_rst
    assert db.execute('SELECT PrereqCivic FROM Districts WHERE DistrictType=?', (DISTRICT,)).fetchall() == [(base.TARGET,)]
    assert db.execute('SELECT Tag,DefaultData FROM TreeData WHERE TreeName=? AND NodeId=8 AND DefnId=6', (TREE,)).fetchall() == [('Needed Civic' if arm == 'on' else None, None)]
    assert db.execute('SELECT NodeType FROM BehaviorTreeNodes WHERE TreeName=? AND NodeId=8', (TREE,)).fetchall() == [('Add Goal Tech',)]
    assert db.execute("SELECT DataName,DataType FROM NodeDataDefinitions WHERE NodeType='Add Goal Tech' AND DefnId=6").fetchall() == [('Desired Civics', 'CivicsList')]
    assert db.execute('SELECT Tag FROM TreeData WHERE TreeName=? AND NodeId=1 AND DefnId=7', (TREE,)).fetchall() == [('Needed Civic',)]
    assert not db.execute('SELECT * FROM AiFavoredItems WHERE Item=?', (base.TARGET,)).fetchall()
    assert db.execute('SELECT LeaderType,System FROM AiLists WHERE ListType=?', (LIST,)).fetchall() == [('TRAIT_LEADER_LUDWIG', 'Districts')]
    assert db.execute('SELECT Item,Favored,Value FROM AiFavoredItems WHERE ListType=?', (LIST,)).fetchall() == [(DISTRICT, 1, 0)]
    for table in ('AiLists', 'AiListTypes', 'AiFavoredItems', 'Strategy_Priorities'):
        assert db.execute(f"SELECT COUNT(*) FROM {table} WHERE ListType LIKE 'CSC_AI_SERVICE_%' OR ListType LIKE 'CSC_AI_FIXED_SERVICE_%' OR ListType='CSC_TEST_RESEARCH_LIST'").fetchone()[0] == 0
    assert db.execute("SELECT COUNT(*) FROM GlobalParameters WHERE Name='RST_VERSION_MAJOR'").fetchone()[0] == 0
    assert db.execute("SELECT DefaultValue FROM PseudoYields WHERE PseudoYieldType='PSEUDOYIELD_IMPROVEMENT'").fetchone()[0] == 90
    assert db.execute("SELECT Value FROM AiFavoredItems WHERE ListType='UnitPriorityBoosts' AND Item='UNIT_BUILDER'").fetchall() == [(50,)]
    before = inventory(db)
    db.create_function('Make_Hash', 1, lambda s: zlib.crc32(s.encode()))
    db.executescript(source + '\n' + patch)
    assert inventory(db) == before, 'Source/overlay replay changed definitions'
    return {'passed': True, 'arm': arm, 'entry': TREE, 'node': 8, 'desired_civics_bound': arm == 'on',
            'disposable_shared_prerequisite': base.TARGET, 'replay_identical': True, 'inventory': before}


def goal_evidence(path):
    rows = (path / 'native-logs/AI_Behavior_Trees.csv').read_text(errors='replace').splitlines()
    goal = [line for line in rows if ', ' + TREE + ',' in line and ', Add Goal Tech,' in line]
    target = [line for line in goal if base.TARGET in line]
    accepted = [line for line in target if base.TARGET + ': Accepted' in line]
    demanded = [line for line in rows if ', ' + TREE + ',' in line and ', Decode Trigger,' in line and DISTRICT in line]
    return {'tree_goal_evaluations': len(goal), 'target_goal_records': len(target),
            'target_accepted_records': len(accepted), 'target_district_decode_records': len(demanded),
            'first_target_goal_records': target[:8], 'first_target_district_records': demanded[:5],
            'limit': 'Tree binding changed for every district; target-specific contract identity/cancellation not yet established.'}


class GoalRunner(base.RSTRunner):
    def pin_sources(self):
        super().pin_sources()
        p = self.out / 'tuning-source-hashes.json'
        pins = read(p)
        pins[str(Path(__file__))] = sha(Path(__file__))
        write(p, pins)

    def archive_version(self):
        super().archive_version()
        p = self.out / 'source-version/version.json'
        v = read(p)
        v.update(code_version=VERSION, test='T2-district-goal', arm=self.arm,
                 research={'target': base.TARGET, 'direct_civic_favorites': False,
                           'goal_binding': self.arm == 'on', 'tree': TREE, 'node': 8,
                           'shared_disposable_prerequisite': DISTRICT, 'rounds': ROUNDS})
        write(p, v)
        (p.parent / 'fixture-extra.lua').write_text(EXTRA, encoding='utf-8')

    def observe(self):
        data = super().observe()
        raw = (self.out / 'fixture-extra-output.txt').read_text()
        slots = [list(map(int, row)) for row in re.findall(r'CSC_GOAL_FREE_SLOT\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)', raw)]
        assert len(slots) == 1 and slots[0][0] == 1 and slots[0][3] == 7
        write(self.out / 'goal-fixture-validation.json', {'passed': True, 'slots': slots})
        write(self.out / 'native-goal-evidence.json', goal_evidence(self.out))
        return data


def preflight(output):
    src = sqlite3.connect((Path.home() / 'Desktop/Codex/csc-civic-unlocks-20261020/t1-minimal-csc-v2/off/native-gameplay.sqlite').as_uri() + '?mode=ro', uri=True)
    results = {}
    source = (ROOT / 'Civ Supply Chains' / base.prior.SQL).read_text(encoding='utf-8')
    for arm in ('off', 'on'):
        db = sqlite3.connect(':memory:')
        src.backup(db)
        db.create_function('Make_Hash', 1, lambda s: zlib.crc32(s.encode()))
        db.executescript(overlay(arm))
        results[arm] = native_check(db, arm, overlay(arm), source)
    assert {k for k in results['off']['inventory'] if results['off']['inventory'][k] != results['on']['inventory'][k]} == {'TreeData'}
    write(output, {'passed': True, 'only_native_table_difference': 'TreeData',
                   'cases': {a: {k: v for k, v in x.items() if k != 'inventory'} for a, x in results.items()}})


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
    write(args.output / 'job-status.json', {'status': 'starting', 'test': 'T2-district-goal', 'pid': os.getpid(), 'code_version': VERSION})
    try:
        for arm in ('off', 'on'):
            patch = overlay(arm)
            for rel, content in originals.items():
                assert (ROOT / 'Civ Supply Chains' / rel).read_bytes() == content
            (base.prior.INSTALLED / base.prior.SQL).write_bytes(originals[base.prior.SQL] + b'\n' + patch.encode())
            (base.prior.INSTALLED / base.prior.LUA).write_bytes(originals[base.prior.LUA] + base.CALLBACK_AUDIT)
            runner = GoalRunner(args.output / arm)
            runner.original_rst = False
            runner.phase, runner.arm, runner.rounds, runner.overlay, runner.keep_game = 'district-goal', arm, ROUNDS, patch, False
            runner.fixture_extra = EXTRA
            runner.captures = Path.home() / 'Desktop/Codex/csc-implemented-native-20261016'
            runner.baseline = Path.home() / 'Desktop/Codex/csc-ai-paired-standard-20261016'
            runner.previous = Path.home() / 'Desktop/Codex/csc-ai-improvement-research-20261019/trial-v1b'
            if arm == 'on':
                runner.fixture_reference = args.output / 'off/fixture-census.json'
            runner.pin_sources()
            runner.archive_version()
            write(args.output / 'active-stage.json', {'test': 'T2-district-goal', 'arm': arm, 'output': str(runner.out), 'pid': os.getpid()})
            write(args.output / 'job-status.json', {'status': 'running', 'test': 'T2-district-goal', 'arm': arm, 'pid': os.getpid(), 'updated_unix': time.time()})
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
                assert {k for k in old if old[k] != new[k]} == {'TreeData'}
                a = sqlite3.connect(args.output / 'off/native-gameplay.sqlite')
                b = sqlite3.connect(runner.out / 'native-gameplay.sqlite')
                av, bv = set(a.execute('SELECT * FROM TreeData')), set(b.execute('SELECT * FROM TreeData'))
                assert len(av - bv) == len(bv - av) == 1
                ar, br = next(iter(av - bv)), next(iter(bv - av))
                assert ar[:3] == br[:3] == (6, 8, TREE) and ar[4:] == br[4:]
                assert ar[3] is None and br[3] == 'Needed Civic'
            write(runner.out / 'paired-preflight.json', {'passed': True, 'only_treatment': 'One native Desired Civics binding; all demand/prerequisites/fixture common'})
            runner.observe()
            runner.menu()
            runner.restore_verified()
            write(runner.out / 'complete.json', {'passed': True, 'arm': arm, 'actual_endpoint': runner.actual_endpoint, 'analyzed_rounds': ROUNDS})
        result = base.compare(args.output, False)
        result.update(test='T2-district-goal', code_version=VERSION, analyzed_rounds=ROUNDS,
                      native_goal_evidence={a: read(args.output / a / 'native-goal-evidence.json') for a in ('off', 'on')},
                      limits=['Disposable shared Bakers prerequisite; never a release change.',
                              'Native goal binding changed for all districts, not only Bakers.',
                              'A named native request does not prove CSC Lua request/cancel reachability.'])
        write(args.output / 'comparison.json', result)
        (args.output / 'report.md').write_text('# Native district civic goal\n\n' + json.dumps(result, indent=2) + '\n', encoding='utf-8')
        write(args.output / 'job-status.json', {'status': 'complete', 'test': 'T2-district-goal', 'code_version': VERSION, 'updated_unix': time.time()})
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
        write(args.output / 'job-status.json', {'status': 'failed', 'test': 'T2-district-goal', 'error': str(exc), 'updated_unix': time.time()})
        raise
    finally:
        for rel, content in originals.items():
            (base.prior.INSTALLED / rel).write_bytes(content)
        write(args.output / 'installed-restored.json', {'verified': all((base.prior.INSTALLED / rel).read_bytes() == content for rel, content in originals.items()), 'source_unchanged': all((ROOT / 'Civ Supply Chains' / rel).read_bytes() == content for rel, content in originals.items())})


if __name__ == '__main__':
    main()
