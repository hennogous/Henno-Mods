"""Bounded T3 probe of shipped LUA Script Condition and contract retirement.

Diagnostic prerequisite and fixture inherited from T2. No release changes.
The gate uses the official Civ Royale callback shape (targetInfo.Extra), with
predeclared time phases. This is callback/lifetime feasibility, not material
guidance or a natural-performance trial.
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

import civic_unlock_goal_trial as goal
import civic_unlock_rst_trial as base
from fixed_research_trial import inventory
from paired_standard import HERE, read, sha
from run import ROOT, write

VERSION = 'civic-unlock-t3-native-lua-condition-lifetime-v2-limit1'
TREE = goal.TREE
FUNCTION = 'CSC_TestNativeCivicGate'
ROUNDS = 16  # 71-86: ON71-73, OFF74-77, ON78-81, OFF82-86.
REFERENCE = Path.home() / 'Desktop/Codex/csc-civic-unlocks-20261020/t2-district-goal-v1/on/native-gameplay.sqlite'
CALLBACK = b"""
CSC_RESEARCH_PROBE_NATIVE={version='rst-original-list-v1',experiment_version='native-goal-gate-probe-v2-limit1',calls={},first_true={},errors={},gate_calls={},payloads={}};
local G=CSC_RESEARCH_PROBE_NATIVE;
local function shallow(value,depth)
 local kind=type(value);
 if kind=='number' or kind=='string' or kind=='boolean' then return value end;
 if kind~='table' then return '<'..kind..'>' end;
 if depth<=0 then return '<table>' end;
 local out,n={},0;
 for key,v in pairs(value) do n=n+1;if n>20 then break end;out[tostring(key)]=shallow(v,depth-1) end;
 return out;
end;
GameEvents.CSC_TestNativeCivicGate.Add(function(targetInfo,...)
 local turn=Game.GetCurrentGameTurn();
 local enabled=turn<74 or (turn>=78 and turn<82);
 G.calls.native=(G.calls.native or 0)+1;
 if #G.payloads<12 then G.payloads[#G.payloads+1]={turn=turn,payload=shallow(targetInfo,2),kind=type(targetInfo),arguments=shallow({...},2),argument_count=select('#',...)} end;
 local ok,err=pcall(function() targetInfo.Extra=enabled and 1 or 0 end);
 if not ok then G.errors[#G.errors+1]={turn=turn,error=tostring(err)};return false end;
 if #G.gate_calls<2000 then G.gate_calls[#G.gate_calls+1]={turn=turn,enabled=enabled} end;
 return true;
end);
print('CSC_NATIVE_GOAL_GATE_READY');
"""


def literal(value):
    if value is None:
        return 'NULL'
    if isinstance(value, int):
        return str(value)
    return "'" + str(value).replace("'", "''") + "'"


def gated_tree_sql():
    """Use shipped typed inputs; add no guessed list serialization or API."""
    db = sqlite3.connect(REFERENCE.as_uri() + '?mode=ro', uri=True)
    original = db.execute('SELECT NodeId,JumpTo,NodeType FROM BehaviorTreeNodes WHERE TreeName=? ORDER BY NodeId', (TREE,)).fetchall()
    original_data = db.execute('SELECT DefnId,NodeId,Tag,DefaultData,ParentTag FROM TreeData WHERE TreeName=? ORDER BY NodeId,DefnId', (TREE,)).fetchall()
    assert original[8] == (8, 0, 'Add Goal Tech')
    assert original[7] == (7, 9, 'Contract Manager Decorator')

    def remap(node):
        return 11 if node == 8 else node + 4 if node >= 9 else node

    nodes = [(TREE, remap(n), remap(j) if j else 0, kind) for n, j, kind in original]
    # Manager -> Priority -> Concurrent(condition, civic goal), fallback tech-only.
    # Inactive condition must not suppress ordinary technology prerequisites.
    nodes += [(TREE, 8, 13, 'Priority'), (TREE, 9, 12, 'Concurrent'),
              (TREE, 10, 0, 'LUA Script Condition'), (TREE, 12, 0, 'Add Goal Tech')]
    # v1 demonstrated retained requests bypassing the condition while the
    # shipped manager waited eight turns. Bound that lifetime to one turn.
    data = [(d, remap(n), TREE, tag, '1' if n == 7 and d == 2 else default, parent)
            for d, n, tag, default, parent in original_data]
    data += [(d, 12, TREE, None if d == 6 else tag, default, parent)
             for d, n, tag, default, parent in original_data if n == 8]
    data += [(0, 9, TREE, None, '0', None), (0, 10, TREE, None, FUNCTION, None)]
    sql = f"DELETE FROM TreeData WHERE TreeName='{TREE}';\nDELETE FROM BehaviorTreeNodes WHERE TreeName='{TREE}';\n"
    sql += 'INSERT INTO BehaviorTreeNodes (TreeName,NodeId,JumpTo,NodeType) VALUES\n'
    sql += ',\n'.join('(' + ','.join(map(literal, row)) + ')' for row in sorted(nodes, key=lambda x: x[1])) + ';\n'
    sql += 'INSERT INTO TreeData (DefnId,NodeId,TreeName,Tag,DefaultData,ParentTag) VALUES\n'
    sql += ',\n'.join('(' + ','.join(map(literal, row)) + ')' for row in sorted(data, key=lambda x: (x[1], x[0]))) + ';\n'
    return sql


def overlay():
    return goal.overlay('on') + gated_tree_sql()


def native_check(db, arm, patch, source, with_rst=False):
    assert not with_rst
    assert db.execute('SELECT PrereqCivic FROM Districts WHERE DistrictType=?', (goal.DISTRICT,)).fetchall() == [(base.TARGET,)]
    assert db.execute('SELECT NodeId,NodeType,JumpTo FROM BehaviorTreeNodes WHERE TreeName=? AND NodeId BETWEEN 7 AND 12 ORDER BY NodeId', (TREE,)).fetchall() == [
        (7, 'Contract Manager Decorator', 13), (8, 'Priority', 13), (9, 'Concurrent', 12),
        (10, 'LUA Script Condition', 0), (11, 'Add Goal Tech', 0), (12, 'Add Goal Tech', 0)]
    assert db.execute('SELECT Tag,DefaultData FROM TreeData WHERE TreeName=? AND NodeId=10 AND DefnId=0', (TREE,)).fetchall() == [(None, FUNCTION)]
    assert db.execute('SELECT NodeId,Tag FROM TreeData WHERE TreeName=? AND NodeId IN (11,12) AND DefnId=6 ORDER BY NodeId', (TREE,)).fetchall() == [(11, 'Needed Civic'), (12, None)]
    assert db.execute('SELECT NodeId,Tag FROM TreeData WHERE TreeName=? AND NodeId IN (11,12) AND DefnId=4 ORDER BY NodeId', (TREE,)).fetchall() == [(11, 'Needed Tech'), (12, 'Needed Tech')]
    assert db.execute('SELECT DefaultData FROM TreeData WHERE TreeName=? AND NodeId=7 AND DefnId=2', (TREE,)).fetchall() == [('1',)]
    assert not db.execute('SELECT * FROM AiFavoredItems WHERE Item=?', (base.TARGET,)).fetchall()
    assert db.execute("SELECT DefaultValue FROM PseudoYields WHERE PseudoYieldType='PSEUDOYIELD_IMPROVEMENT'").fetchone()[0] == 90
    assert db.execute("SELECT Value FROM AiFavoredItems WHERE ListType='UnitPriorityBoosts' AND Item='UNIT_BUILDER'").fetchall() == [(50,)]
    assert db.execute("SELECT COUNT(*) FROM GlobalParameters WHERE Name='RST_VERSION_MAJOR'").fetchone()[0] == 0
    before = inventory(db)
    db.create_function('Make_Hash', 1, lambda s: zlib.crc32(s.encode()))
    db.executescript(source + '\n' + patch)
    assert inventory(db) == before, 'Gate source replay changed definitions'
    return {'passed': True, 'replay_identical': True, 'shipped_lua_condition_type': True,
            'native_tech_fallback_retained': True, 'inventory': before}


class GateRunner(goal.GoalRunner):
    def pin_sources(self):
        super().pin_sources()
        p = self.out / 'tuning-source-hashes.json'
        pins = read(p)
        pins[str(Path(__file__))] = sha(Path(__file__))
        # The native tree source is a frozen, independently audited reference.
        pins[str(REFERENCE)] = sha(REFERENCE)
        write(p, pins)

    def archive_version(self):
        super().archive_version()
        p = self.out / 'source-version/version.json'
        v = read(p)
        v['research']['rounds'] = ROUNDS
        v['research'].update(node=11, contract_manager_turn_limit=1)
        v.update(code_version=VERSION, test='T3-native-gate-lifetime-probe', analyzed_rounds=ROUNDS,
                 phases={'71-73': True, '74-77': False, '78-81': True, '82-86': False},
                 limits=['Time-gated native request calibration; not Quarter-material eligibility.',
                         'One bounded lifetime follow-up: manager limit8 to1; callback argument instrumentation only otherwise.',
                         'Synthetic prerequisite retained from T2; never deployed.',
                         'No distinct control world; lifecycle/score observations are within one world.'])
        write(p, v)
        (p.parent / 'native-tree-reference-sha256.txt').write_text(sha(REFERENCE) + '\n', encoding='utf-8')


def preflight(path):
    src = sqlite3.connect(REFERENCE.as_uri() + '?mode=ro', uri=True)
    db = sqlite3.connect(':memory:')
    src.backup(db)
    db.create_function('Make_Hash', 1, lambda s: zlib.crc32(s.encode()))
    patch = overlay()
    db.executescript(patch)
    result = native_check(db, 'on', patch, (ROOT / 'Civ Supply Chains' / base.prior.SQL).read_text(encoding='utf-8'))
    nodes = db.execute('SELECT NodeId,JumpTo FROM BehaviorTreeNodes WHERE TreeName=?', (TREE,)).fetchall()
    assert sorted(n for n, j in nodes) == list(range(39))
    assert all(j == 0 or n < j <= 39 for n, j in nodes)
    write(path, {k: v for k, v in result.items() if k != 'inventory'})


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
    base.VERSION = base.prior.VERSION = goal.VERSION = VERSION
    originals = {rel: (base.prior.INSTALLED / rel).read_bytes() for rel in (base.prior.SQL, base.prior.LUA)}
    for rel, content in originals.items():
        assert content == (ROOT / 'Civ Supply Chains' / rel).read_bytes()
        p = args.output / 'original-installed' / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(content)
    runner = None
    try:
        patch = overlay()
        (base.prior.INSTALLED / base.prior.SQL).write_bytes(originals[base.prior.SQL] + b'\n' + patch.encode())
        (base.prior.INSTALLED / base.prior.LUA).write_bytes(originals[base.prior.LUA] + CALLBACK)
        runner = GateRunner(args.output / 'probe')
        runner.original_rst = False
        runner.phase, runner.arm, runner.rounds, runner.overlay, runner.keep_game = 'native-gate', 'on', ROUNDS, patch, False
        runner.fixture_extra = goal.EXTRA
        runner.captures = Path.home() / 'Desktop/Codex/csc-implemented-native-20261016'
        runner.baseline = Path.home() / 'Desktop/Codex/csc-ai-paired-standard-20261016'
        runner.previous = Path.home() / 'Desktop/Codex/csc-ai-improvement-research-20261019/trial-v1b'
        runner.pin_sources()
        runner.archive_version()
        write(args.output / 'active-stage.json', {'test': 'T3-native-gate-lifetime-probe', 'output': str(runner.out), 'pid': os.getpid()})
        write(args.output / 'job-status.json', {'status': 'running', 'test': 'T3-native-gate-lifetime-probe', 'pid': os.getpid(), 'code_version': VERSION, 'updated_unix': time.time()})
        runner.wait('MainMenu', 180)
        runner.config()
        runner.start_pair(1)
        data = runner.observe()
        write(args.output / 'callback-and-lifetime-evidence.json', {
            'callback_invocations': data['native']['calls'].get('native', 0),
            'payloads': data['native']['payloads'], 'gate_calls': data['native']['gate_calls'],
            'actual_endpoint': runner.actual_endpoint,
            'note': 'Analyze native goals and candidate scores by preregistered phase before concluding cancellation.'})
        runner.menu()
        runner.restore_verified()
        write(args.output / 'job-status.json', {'status': 'complete', 'test': 'T3-native-gate-lifetime-probe', 'callback_invocations': data['native']['calls'].get('native', 0), 'updated_unix': time.time()})
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
        write(args.output / 'job-status.json', {'status': 'failed', 'test': 'T3-native-gate-lifetime-probe', 'error': str(exc), 'updated_unix': time.time()})
        raise
    finally:
        for rel, content in originals.items():
            (base.prior.INSTALLED / rel).write_bytes(content)
        write(args.output / 'installed-restored.json', {'verified': all((base.prior.INSTALLED / rel).read_bytes() == content for rel, content in originals.items()), 'source_unchanged': all((ROOT / 'Civ Supply Chains' / rel).read_bytes() == content for rel, content in originals.items())})


if __name__ == '__main__':
    main()
