"""Bounded CE/Lua parity exercise using the maintained shared game controller.

Python audits and controls the test only. The installed Lua package computes and
publishes policy itself; this driver installs no Lua, attaches no native probe,
and sends no district orders, yields, grants or policy entries to the game.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / 'project/tools/ai_baseline'),
                str(ROOT / 'project/tools/ai_site_planner/adjacency_policy')]
from full_game_controller.probe import make_probe_controller
from full_game_controller.session import NativeSession
from full_game_controller.windows_process import HeldProcess, native_inventory
from full_game_controller.environment import (launch, configure, flags, manifest,
    restore_preferences, write_json, archive_sources)
from full_game_controller.log_capture import capture_log_baseline, read_log_delta
from full_game_controller.checkpoint import save_inactive_boundary
from full_game_controller.discovery import discover_contexts
from policy import shortlist

CSC = 'c5e66bd1-d804-443b-ac3d-1917a20dba3c'
FORK = 'd0f3a2ab-4fa6-4a7a-bf9b-b82a66fe2a06'
POLICY = 'd0f3a2ab-4fa6-4a7a-bf9b-b82a66fe2a07'
DLL = 'GameCore_XP2_CE_AI_FinalRelease.dll'
GAME_SHA = '324c51e9ea3531758842e16c69e6cddbefbb226c5b675c3d6e60111646c2e98c'
CONTEXT = 'CSC_CE_Policy'
LOGS = ('Lua.log', 'Database.log', 'Modding.log', 'AI_CityBuild.csv',
        'AI_Behavior_Trees.csv', 'City_BuildQueue.csv')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def parse(raw, marker):
    rows = re.findall(re.escape(marker) + r'=([^\r\n]+)', raw)
    if len(rows) != 1:
        raise RuntimeError('Missing/ambiguous receipt ' + marker)
    return json.loads(rows[0])


def audit_plan(state):
    """Same captured facts and same authoritative Python policy, no game write."""
    actual, snapshot = state['plan'], state['snapshot']
    if not isinstance(snapshot, dict) or not isinstance(actual, dict):
        raise RuntimeError('No packaged policy plan/snapshot')
    expected = shortlist(snapshot)
    for field in ('entries', 'selected', 'qualified', 'penalized'):
        if actual[field] != expected[field]:
            raise RuntimeError('Packaged Lua/Python policy differs: ' + field)
    if state['originalAI'] != snapshot['originalAI'] or 0 in state['originalAI']:
        raise RuntimeError('Original human exclusion changed')
    return dict(verified=True, candidates=len(snapshot['candidates']),
                selected=len(actual['selected']), penalized=len(actual['penalized']),
                entries=len(actual['entries']), comparison='actual Lua vs original Python on identical captured facts')


def setup(mode='v2'):
    if mode not in ('v2', 'off'):
        raise ValueError('Explicit policy mode required')
    return """GameConfiguration.SetToDefaults();GameConfiguration.SetRuleSet('RULESET_EXPANSION_2');BuildHeadlessGameSetup();RebuildPlayerParameters(true);GameSetup_RefreshParameters();MapConfiguration.SetScript('Continents.lua');MapConfiguration.SetMapSize('MAPSIZE_SMALL');GameConfiguration.SetParticipatingPlayerCount(6);GameConfiguration.SetValue('CITY_STATE_COUNT',9);GameConfiguration.SetGameSpeedType('GAMESPEED_ONLINE');GameConfiguration.SetHandicapType('DIFFICULTY_PRINCE');GameConfiguration.SetValue('GAME_SYNC_RANDOM_SEED',26131103);MapConfiguration.SetValue('RANDOM_SEED',16131103);MapConfiguration.SetValue('resources',2);GameConfiguration.SetValue('GAMEMODE_MONOPOLIES',false);GameConfiguration.SetStartEra(DB.MakeHash('ERA_ANCIENT'));GameConfiguration.SetValue('CSC_CE_POLICY_MODE','""" + mode + """');for _,pid in ipairs(GameConfiguration.GetParticipatingPlayerIDs())do PlayerConfigurations[pid]:SetLeaderTypeName(nil)end;ReleasePlayerParameters();HideGameSetup();Automation.SetAutoStartEnabled(true);Network.HostGame(ServerType.SERVER_TYPE_NONE);"""


def run(a):
    out = a.output.resolve()
    if out.exists() or native_inventory():
        raise RuntimeError('Fresh output and no existing native/Tuner owner required')
    if not 2 <= a.endpoint <= 100 or (a.lifecycle and a.endpoint < 6):
        raise ValueError('Endpoint2..100; lifecycle exercise requires at least6')
    out.mkdir(parents=True)
    roots = [a.ce, a.package, a.installed, a.stock_ce]
    before = {str(p.resolve()): manifest(p) for p in roots}
    sources = list(HERE.glob('*.py'))
    sources += list((HERE.parent / 'ce_policy').glob('*'))
    sources += list((HERE.parent / 'ce_frontend').glob('*'))
    sources += list((ROOT / 'project/tools/ai_baseline/full_game_controller').glob('*.py'))
    sources += list((ROOT / 'project/tools/ai_baseline/full_game_controller').glob('*.lua'))
    sources += list((ROOT / 'project/tools/ai_site_planner/adjacency_policy').glob('*.py'))
    sources += [ROOT / 'project/tools/ai_site_planner/adjacency_policy/scan.lua']
    pins = {str(p.resolve()): sha(p) for p in sources if p.is_file()}
    write_json(out / 'pins.json', pins)
    write_json(out / 'source-archive.json', archive_sources(pins, out / 'source-version'))
    write_json(out / 'content-before.json', before)
    write_json(out / 'protocol.json', dict(endpoint=a.endpoint, speed='GAMESPEED_ONLINE',
        profile='csc-adjacency-policy-v2', lifecycle=a.lifecycle,
        worlds=2 if a.lifecycle else 1, loads=1 if a.lifecycle else 0,
        map_seed=16131103, game_seed=26131103, frida=False,
        external_policy_publication=False, Python_role='shared controller and offline audit only',
        native_provider='development CE fork', original_CE_modified=False,
        policy_changes=False, benefit_or_matched_history_claimed=False))
    c = make_probe_controller(out, user_root=a.user_root)
    c.study_endpoint = a.endpoint
    c.allow_observer_warning_dismissal = c.allow_observer_first_meet_dismissal = True
    c.allow_observer_congress_review = True
    s = NativeSession(out, c, inventory=native_inventory, hold=HeldProcess, write=write_json)
    error, turn, phase = None, None, 'primary'
    observations, log_baselines = [], {}
    mode, checkpoint, source_before_load = 'v2', None, None

    def verify(*, check_stop=False):
        if any(sha(p) != digest for p, digest in pins.items()):
            raise RuntimeError('Pinned executed source changed')
        if any(manifest(p) != before[str(p.resolve())] for p in roots):
            raise RuntimeError('Installed content changed')
        request = out / 'stop-request.json'
        if check_stop and request.exists():
            value = json.loads(request.read_text(encoding='utf-8-sig'))
            reason = value.get('reason')
            if not isinstance(reason, str) or not reason:
                raise RuntimeError('Malformed boundary stop request')
            write_json(out / 'stop-accepted.json', dict(reason=reason, turn=turn,
                phase=phase, inactive_boundary=True, unix=time.time()))
            raise RuntimeError('Stopped at inactive boundary: ' + reason)

    def capture_logs(label):
        for name, baseline in log_baselines.items():
            path = a.user_root / 'Logs' / name
            if path.exists():
                current, delta = read_log_delta(path, baseline)
                target = out / 'logs' / label / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(current.data)
                write_json(target.with_suffix(target.suffix + '.boundary.json'),
                    dict(initial=baseline.evidence(), current=current.evidence(), delta_bytes=len(delta)))

    def query(label, *, active=True):
        raw = c.cmd('CSC_CE_PolicyReport();', CONTEXT, phase + '-' + label, wait=15)
        state = parse(raw, 'CSC_CE_POLICY_STATE')
        # Preserve a malformed native payload as evidence before decoding it.
        write_json(out / 'observations' / (phase + '-' + label + '-raw.json'),
            dict(phase=phase, label=label, turn=turn, unix=time.time(), state=state))
        native = json.loads(state['native'])
        record = dict(phase=phase, label=label, turn=turn, unix=time.time(),
                      state=state, native=native)
        write_json(out / 'observations' / (phase + '-' + label + '.json'), record)
        observations.append(record)
        if native['ready'] != 1 or native['faults'] or state['failed']:
            raise RuntimeError('CE native/policy capability unhealthy')
        if active:
            if state['disabled'] or not native['enabled']:
                raise RuntimeError('Active policy unexpectedly disabled')
            record['policy_audit'] = audit_plan(state)
            if state['snapshot']['turn'] != turn:
                raise RuntimeError('Packaged scan is stale at the native boundary')
            write_json(out / 'observations' / (phase + '-' + label + '.json'), record)
        elif turn == 100 and mode == 'v2':
            record['policy_audit'] = audit_plan(state)
            if state['snapshot']['turn'] != 100 or native['enabled']:
                raise RuntimeError('Endpoint scan/retirement missing')
            write_json(out / 'observations' / (phase + '-' + label + '.json'), record)
        return record

    def gate():
        c.cmd("assert(Game.GetCurrentGameTurn()==" + str(turn) +
            ");assert(Players[0]:IsHuman());assert(GameInfo.Yields.YIELD_CSC_AI_PLACEMENT==nil and GameInfo.CSC_AI_Profile==nil,'Legacy tuning loaded');assert(GameConfiguration.GetGameSpeedType()=='GAMESPEED_ONLINE' or GameInfo.GameSpeeds[GameConfiguration.GetGameSpeedType()].GameSpeedType=='GAMESPEED_ONLINE');",
            'GameCore_Tuner', phase + '-identity')
        value = query('source-' + str(turn), active=mode == 'v2')
        if mode == 'off' and any(value['native'][k] for k in ('enabled', 'entries', 'version', 'changed')):
            raise RuntimeError('Native policy crossed a context boundary')
        return True

    def play_to(target):
        nonlocal turn
        c.study_endpoint = target
        for current in range(turn + 1, target + 1):
            verify(check_stop=True)
            c.play(current)
            turn = current
            query('turn-' + str(turn), active=mode == 'v2' and turn < 100)
            write_json(out / 'progress.json', dict(phase=phase, turn=turn,
                endpoint=a.endpoint, updated_unix=time.time(), native_pid=s.owner.pid))

    def retire(label):
        c.cmd('assert(CSC_CE_PolicyDisable());', CONTEXT, label + '-disable')
        value = query(label + '-disabled', active=False)
        if value['native']['enabled']:
            raise RuntimeError('Native disable failed')
        capture_logs(label + '-after-freeze')
        s.issue_once(label + '-menu', 'Events.ExitToMainMenu();', 'PlotInfo')
        s.wait_context('MainMenu', 180)

    try:
        verify()
        s.start(lambda: launch(a, out))
        s.wait_context('MainMenu')
        configure(c, out, 'BASIC')
        for identity, label in ((FORK, 'fork'), (POLICY, 'policy')):
            c.cmd("local chosen=nil;for _,m in ipairs(Modding.GetInstalledMods())do if m.Id=='" +
                identity + "'then assert(not chosen,'Duplicate dev package');chosen=m end end;assert(chosen,'Missing dev package');local err=Modding.CanEnableMod(chosen.Handle);assert(err=='OK','Not eligible: '..tostring(err));Modding.EnableMod(chosen.Handle,true);",
                'MainMenu', 'enable-' + label)
            s.wait_context('MainMenu', 90)
        selected = flags(c, 'verify-fork-policy-exclusive')
        if {k for k, v in selected['mods'].items() if v} != {CSC, FORK, POLICY}:
            raise RuntimeError('Unexpected enabled mod set')
        for name in LOGS:
            log_baselines[name] = capture_log_baseline(a.user_root / 'Logs' / name)
        turn = 1
        s.issue_once('host-primary', setup(mode), 'MainMenu')
        s.ready_after_issue(turn, ('GameCore_Tuner', 'PlotInfo', CONTEXT), eligibility=gate, timeout=300)
        code = ('Get-Process -Id ' + str(s.owner.pid) +
            " -ErrorAction Stop | ForEach-Object {$_.Modules} | Where-Object {$_.ModuleName -match 'GameCore_XP2'} | Select-Object ModuleName,FileName | ConvertTo-Json -Compress")
        modules = json.loads(subprocess.check_output(['powershell', '-NoProfile', '-Command', code],
            text=True, creationflags=subprocess.CREATE_NO_WINDOW))
        if isinstance(modules, dict):
            modules = [modules]
        expected = {DLL: sha(a.ce / 'Binaries/Win64' / DLL),
                    'GameCore_XP2_FinalRelease.dll': GAME_SHA}
        if {v['ModuleName'] for v in modules} != set(expected):
            raise RuntimeError('Unexpected loaded native carrier set')
        for module in modules:
            if sha(module['FileName']) != expected[module['ModuleName']]:
                raise RuntimeError('Loaded native binary hash mismatch')
            if module['ModuleName'] == DLL and Path(module['FileName']).resolve() != (a.ce / 'Binaries/Win64' / DLL).resolve():
                raise RuntimeError('Fork loaded from unexpected path')
        write_json(out / 'loaded-modules.json', modules)
        if a.lifecycle:
            play_to(6)
            source_before_load = observations[-1]['state']['snapshot']
            checkpoint = save_inactive_boundary(c, turn=6, name='CE_PARITY_6',
                native_directory=a.save_directory, archive=out / 'checkpoints/turn-6.Civ6Save')
            write_json(out / 'checkpoint.json', checkpoint)
            capture_logs('primary-through-6')
            retire('primary')
            phase, mode, turn = 'fresh-observe', 'off', 1
            s.issue_once('host-observe', setup(mode), 'MainMenu')
            s.ready_after_issue(turn, ('GameCore_Tuner', 'PlotInfo', CONTEXT), eligibility=gate)
            play_to(2)
            capture_logs('fresh-observe-through-2')
            retire('fresh-observe')
            phase, mode, turn = 'reloaded', 'v2', 6
            source = Path(checkpoint['native_save'])
            s.load_once(source, sha256=checkpoint['sha256'], native_directory=source.parent,
                turn=turn, contexts=('GameCore_Tuner', 'PlotInfo', CONTEXT), eligibility=gate)
            # Compare captured scanner facts, not RNG, native caches or entire saves.
            current = observations[-1]['state']['snapshot']
            keys = ('turn', 'speed', 'width', 'height', 'districtCount',
                    'originalAI', 'cities', 'candidates', 'quarters', 'rules')
            def canon(v):
                if isinstance(v, dict):
                    return {k: canon(x) for k, x in v.items()}
                if isinstance(v, list):
                    return sorted((canon(x) for x in v), key=lambda x: json.dumps(x, sort_keys=True))
                return v
            different = [k for k in keys if canon(source_before_load[k]) != canon(current[k])]
            write_json(out / 'reload-scanner-parity.json', dict(verified=not different,
                different_fields=different, scope='Captured scanner facts only; not RNG/cache/full-world parity'))
            if different:
                raise RuntimeError('Save/load scanner facts changed: ' + ','.join(different))
        play_to(a.endpoint)
        capture_logs('at-endpoint')
    except BaseException as failure:
        error = failure
        write_json(out / 'failure.json', dict(error=str(failure), traceback=traceback.format_exc(),
                                             phase=phase, last_turn=turn, no_automatic_replay=True))
    finally:
        if s.owner is not None and s.owner.poll() is None:
            try:
                def freeze():
                    # On setup failure no gameplay context exists; do not invent it.
                    _, states = discover_contexts(required='MainMenu')
                    if CONTEXT in states:
                        c.cmd('assert(CSC_CE_PolicyDisable());', CONTEXT, 'final-disable')
                        capture_logs('final-after-freeze')
                s.close(restore_preferences=lambda: restore_preferences(c, out)
                    if (out / 'original-preferences.json').exists() else None,
                    restore_package=verify, before_menu=freeze)
            except BaseException as failure:
                error = error or failure
                write_json(out / 'cleanup-failure.json', dict(error=str(failure), traceback=traceback.format_exc()))
        capture_logs('closed')
        write_json(out / 'final-inventory.json', native_inventory())
    result = dict(closed=s.closed, phase=phase, endpoint=turn,
        requested_endpoint=a.endpoint, lifecycle_exercised=a.lifecycle,
        observations=len(observations), error=str(error) if error else None,
        installed_unchanged=all(manifest(p) == before[str(p.resolve())] for p in roots),
        frida=False, Python_policy_publication=False, native_orders_or_grants=False,
        stock_CE_has_proposed_API=False, historical_matched_outcome_claimed=False)
    write_json(out / 'result.json', result)
    print(json.dumps(result), flush=True)
    if error:
        raise error


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('output', 'binary', 'user-root', 'ce', 'package', 'installed', 'stock-ce', 'save-directory'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--endpoint', type=int, default=100)
    parser.add_argument('--lifecycle', action='store_true')
    run(parser.parse_args())
