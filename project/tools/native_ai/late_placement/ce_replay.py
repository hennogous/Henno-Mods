"""Replay the late-placement pulse through the CE Lua API and shared controller."""

import argparse
import csv
import io
import json
from pathlib import Path
import shutil
import subprocess
from types import SimpleNamespace
import xml.etree.ElementTree as ET

from driver import (
    GAME_SHA, HOTFIX_SHA, ID, PLOT, SAVE_SHA, STUDY, configure, flags, inspect_source, launch,
    load, lua, make_probe_controller, manifest, native_inventory, parse, read,
    require, restore_preferences, sha, write_json, HeldProcess, NativeSession,
    capture_log_baseline, read_log_delta,
)

FORK = 'd0f3a2ab-4fa6-4a7a-bf9b-b82a66fe2a0a'
OLD_FORK = 'd0f3a2ab-4fa6-4a7a-bf9b-b82a66fe2a06'
DLL = 'GameCore_XP2_CE_AI_FinalRelease.dll'
LOGS = ('AI_CityBuild.csv', 'AI_Behavior_Trees.csv')
# Supported MSVC build of the reviewed CE hotfix profile and its Windows DX11
# executable. GameCore code parity does not qualify the executable-side hooks.
HOTFIX_CE_SHA = 'c39a24fd5d1af7e191edeefec10b1d5f8e2280a17c173bc5d944ec313f93118d'
HOTFIX_EXE_SHA = 'd1a0cfd439e7451be515f47595cfa0b6b983f56d1faf4ea434a4ce3b21491ebe'
# Unchanged upstream develop 2986a746 from the same supported build workflow.
CE_BASE_SHA = '18af3c5a0e92d98756a0fdfcd28351bdcbaf1efdcd646ce6a27adfcb995991ad'


def verify_modules(session, fork, output, original_sha):
    command = (f'Get-Process -Id {session.owner.pid} -ErrorAction Stop | ForEach-Object {{$_.Modules}} | '
               "Where-Object {$_.ModuleName -match '^GameCore_XP2'} | Select-Object ModuleName,FileName | ConvertTo-Json -Compress")
    modules = json.loads(subprocess.check_output(['powershell', '-NoProfile', '-Command', command], text=True,
                                                creationflags=subprocess.CREATE_NO_WINDOW))
    if isinstance(modules, dict):
        modules = [modules]
    paths = {row['ModuleName']: Path(row['FileName']).resolve() for row in modules}
    write_json(output / 'loaded-modules.json', {name: {'path': str(path), 'sha256': sha(path)} for name, path in paths.items()})
    require(set(paths) == {DLL, 'GameCore_XP2_FinalRelease.dll'}, 'Unexpected loaded GameCore module set')
    require(paths[DLL] == fork and sha(paths['GameCore_XP2_FinalRelease.dll']) == original_sha,
            'Unexpected proxy or original GameCore identity')


def read_journal(controller, output):
    def query(code, name):
        return parse(controller.cmd(code, 'GameCore_Tuner', name), 'CSC_CE_LATE')

    status = query('assert(CE_AIDistrictScoresDisable()==1);print("CSC_CE_LATE="..CE_AIDistrictScoresStatus())',
                   'retire-and-read-ce-status')
    records = []
    for offset in range(0, status['trace_count'], 16):
        page = query(f'print("CSC_CE_LATE="..CE_AIDistrictScoresTraceRead({offset},16,{status["generation"]}))',
                     f'ce-trace-page-{offset}')
        require(not page['stale'] and page['offset'] == offset and page['total'] == status['trace_count'],
                'CE trace changed after Disable')
        records.extend(page['records'])
    require(len(records) == status['trace_count'] and status['active'] == status['faults'] == status['enabled'] == 0,
            'Incomplete or faulted CE trace')
    write_json(output / 'ce-journal.json', {'status': status, 'records': records})
    return records


def verify_pulse(records, output, before, final, winner, district, early_district):
    relevant = [r for r in records if (r['player'], r['city']) == (1, 65536)]
    late = [r for r in relevant if r['k'] == 'late']
    require(len(late) == 1 and all(late[0][k] == v for k, v in
            dict(district=district, plot=PLOT, base=final, result=winner, reason=0, eligible=1).items()),
            'Expected one exact native late write')
    require(any(r['k'] == 'net' and r['district'] == early_district and r['plot'] == PLOT and
                r['result'] == r['base'] + 1 and r['reason'] == 0 for r in relevant), 'Earlier API did not apply')
    for kind in ('cache', 'best', 'pv'):
        require(any(r['k'] == kind and r['district'] == district and r['plot'] == PLOT and r['result'] == winner
                    for r in relevant[relevant.index(late[0]) + 1:]), f'Missing downstream {kind} value')
    tree = [list(map(str.strip, row)) for row in csv.reader(io.StringIO(read(output / 'AI_Behavior_Trees.csv')))]
    tree = [row[4:7] for row in tree if row[:4] == ['1', '1', 'City LOC_CITY_NAME_DELHI', 'Build City District']]
    require(['SUCCESS', 'Decode Trigger', f'District: DISTRICT_CSC_BAKERS_QUARTER; Value: {winner // 256}'] in tree and
            ['SUCCESS', 'Reserve Plot', 'Reserving plot 26 16'] in tree and
            ['RUNNING', 'Add Goal Tech', 'CIVIC_CRAFTSMANSHIP: Accepted'] in tree, 'Native preparation did not match the pulse')
    write_json(output / 'result.json', dict(verified=True, before_q8=before, original_q8=final, chosen_q8=winner,
                                           late_record=late[0], early_entry_verified=True, preparation_verified=True))


def add_fixture_carrier(package, dll):
    # This old save activates only its recorded mods. Keep its CSC identity
    # and gameplay payload, and select the test proxy through front-end SQL.
    (manifest_path,) = package.glob('*.modinfo')
    tree = ET.parse(manifest_path)
    root = tree.getroot()
    require(root.attrib['id'] == ID, 'Unexpected fixture package identity')
    config = 'Data/CE_Late_Trial_Config.sql'
    proxy = 'Binaries/Win64/' + DLL
    action = ET.SubElement(root.find('FrontEndActions'), 'UpdateDatabase', id='CE_Late_Trial_GameCore')
    properties = ET.SubElement(action, 'Properties')
    ET.SubElement(properties, 'LoadOrder').text = '10'
    ET.SubElement(action, 'File').text = config
    for file in (config, proxy):
        ET.SubElement(root.find('Files'), 'File').text = file
    tree.write(manifest_path, encoding='utf-8', xml_declaration=True)
    (package / config).write_text(f"UPDATE GameCores SET PackageId='{ID}', DllPrefix='GameCore_XP2_CE_AI' "
                                  "WHERE GameCore='Expansion2';\n", encoding='utf-8')
    (package / proxy).parent.mkdir(parents=True)
    shutil.copyfile(dll, package / proxy)


def run(a):
    output = a.output.resolve()
    require(not output.exists() and not native_inventory(), 'Expected fresh output and no native/Tuner owner')
    original_sha = HOTFIX_SHA if a.hotfix else GAME_SHA
    require(not a.ce_base_control or (a.hotfix and a.fixture_carrier),
            'The CE base control must use the same patched executable and fixture carrier')
    require(not a.compat_profile_sha or (a.hotfix and a.fixture_carrier),
            'Use the compatibility build on the patched executable and matched fixture')
    if a.hotfix:
        expected_ce = a.compat_profile_sha or (CE_BASE_SHA if a.ce_base_control else HOTFIX_CE_SHA)
        require(sha(a.ce_dll) == expected_ce and sha(a.binary) == HOTFIX_EXE_SHA,
                'Unexpected CE hotfix DLL or DX11 executable identity')
    installed = [a.mods / 'CSC Mill Building Study']
    if not a.fixture_carrier:
        installed.append(a.mods / 'CE Late Placement Trial')
    require(not any(path.exists() for path in installed), 'An isolated test package is already installed')
    checkpoint = load(a.study / 'run-03/source-checkpoint.json')
    source = Path(checkpoint['native_save'])
    require(sha(source) == sha(Path(checkpoint['archive'])) == SAVE_SHA, 'Unexpected replay checkpoint')
    archived = load(a.study / 'run-03/probe/source-world.json')
    proof = load(a.proof / 'result.json')
    require(load(a.proof / 'restoration.json')['verified'], 'Prior control is not closed and restored')
    matched_world = load(a.proof / 'correction/source-world.json')
    inspect_source(matched_world, archived)
    before, final = (proof['baseline']['calculation'][field] for field in ('before', 'native'))
    winner = proof['pulse']['calculation']['final']
    cfg = archived['observerConfig']
    district, early_district = cfg['districtIndices']
    output.mkdir(parents=True)
    write_json(output / 'carrier.json', dict(fixture_carrier=a.fixture_carrier, dll_sha256=sha(a.ce_dll),
                                             original_sha256=original_sha, exe_sha256=sha(a.binary),
                                             upstream_base_control=a.ce_base_control,
                                             executable_compatibility_patch=bool(a.compat_profile_sha)))
    # Only these dedicated package folders are staged. The working stock and
    # previous CE test installations are never touched.
    untouched = {p: manifest(p) for p in (a.mods / 'Civ Supply Chains', a.mods / 'CivilizationVI_CommunityExtension')}
    require(all(untouched.values()), 'Missing reference installation')
    pins = {}
    controller = make_probe_controller(output, user_root=a.user_root)
    controller.study_endpoint = 2
    controller.allow_observer_warning_dismissal = controller.allow_observer_first_meet_dismissal = True
    controller.allow_observer_congress_review = True
    session = NativeSession(output, controller, inventory=native_inventory, hold=HeldProcess, write=write_json)

    def verify():
        require(all(manifest(path) == expected for path, expected in (pins | untouched).items()), 'Content changed during replay')

    def gate():
        verify_modules(session, (installed[-1] / 'Binaries/Win64' / DLL).resolve(), output, original_sha)
        targets = [{key: target[key] for key in ('player', 'city', 'plot')} for target in archived['targets']]
        code = 'CSC_MILL_STUDY_CONFIG=' + lua(dict(targets=targets)) + ';\n' + read(STUDY / 'world.lua')
        world = parse(controller.cmd(code, 'GameCore_Tuner', 'ce-source-world', wait=30), 'CSC_MILL_BUILDING_WORLD')
        inspect_source(world, archived)
        write_json(output / 'source-world.json', world)
        require(world == matched_world, 'Replay world differs from the matched Frida fixture')
        return True

    try:
        staged = [output / ('prepared-' + path.name) for path in installed]
        shutil.copytree(a.study / 'retired-study-package', staged[0])
        if a.fixture_carrier:
            add_fixture_carrier(staged[0], a.ce_dll)
        else:
            shutil.copytree(a.ce_package, staged[1])
            for relative in ('Data/Config.sql', 'CE_AI_Development.modinfo'):
                path = staged[1] / relative
                original = read(path)
                require(OLD_FORK in original, 'Unexpected CE template package')
                path.write_text(original.replace(OLD_FORK, FORK), encoding='utf-8')
            shutil.copyfile(a.ce_dll, staged[1] / 'Binaries/Win64' / DLL)
        for prepared, destination in zip(staged, installed):
            content = manifest(prepared)
            prepared.rename(destination)
            pins[destination] = content
        write_json(output / 'content-pins.json', {str(p): value for p, value in (pins | untouched).items()})
        verify()
        session.start(lambda: launch(SimpleNamespace(binary=a.binary, user_root=a.user_root), output))
        session.wait_context('MainMenu')
        configure(controller, output, csc_id=ID)
        if not a.fixture_carrier:
            controller.cmd(f"local match;for _,m in ipairs(Modding.GetInstalledMods()) do if m.Id=='{FORK}' then "
                           "assert(not match);match=m end end;assert(match);assert(Modding.CanEnableMod(match.Handle)=='OK');"
                           "Modding.EnableMod(match.Handle,true)", 'MainMenu', 'enable-isolated-ce')
            session.wait_context('MainMenu')
            require({key for key, enabled in flags(controller, 'verify-ce-and-csc')['mods'].items() if enabled} == {ID, FORK},
                    'Unexpected enabled mods')
        boundaries = {name: capture_log_baseline(a.user_root / 'Logs' / name) for name in LOGS}
        session.load_once(source, sha256=SAVE_SHA, native_directory=source.parent, turn=1,
                          contexts=('GameCore_Tuner', 'PlotInfo', 'CSC_AdjacencyGameplay'), eligibility=gate)
        if a.compat_profile_sha:
            controller.cmd('assert(type(Mem)=="function" and type(RegisterProcessor)=="function")',
                           'GameCore_Tuner', 'verify-ce-compatibility-bindings')
        if a.ce_base_control:
            controller.cmd('assert(CE_AIDistrictScoresBegin==nil)', 'GameCore_Tuner', 'verify-ce-control-bindings')
            controller.play(2)
            write_json(output / 'result.json', dict(upstream_base_control=True, turn=2, verified=True,
                                                    executable_compatibility_patch=bool(a.compat_profile_sha)))
            return
        publish = (f'assert(Game.GetCurrentGameTurn()==1);assert(CE_AIDistrictScoresBegin(1,{cfg["mapWidth"]},'
                   f'{cfg["mapHeight"]},{cfg["districtCount"]})==1);assert(CE_AIDistrictScoresAllow(1)==1);'
                   f'assert(CE_AIDistrictScoresEntry(1,65536,{early_district},{PLOT},1)==1);'
                   f'assert(CE_AIDistrictScoresLateEntry(1,65536,{district},{PLOT},{before},{final},{winner-final})==1);'
                   'assert(CE_AIDistrictScoresCommit()==1);print("CSC_CE_LATE="..CE_AIDistrictScoresStatus())')
        status = parse(controller.cmd(publish, 'GameCore_Tuner', 'publish-early-and-late-pairs'), 'CSC_CE_LATE')
        require(status['ready'] == status['enabled'] == status['version'] == 1 and status['entries'] == 2,
                'CE publication did not admit both entries')
        write_json(output / 'publication.json', status)
        controller.play(2)
        records = read_journal(controller, output)
        for name, boundary in boundaries.items():
            _, payload = read_log_delta(a.user_root / 'Logs' / name, boundary)
            (output / name).write_bytes(payload)
        verify_pulse(records, output, before, final, winner, district, early_district)
    finally:
        if session.owner is not None and session.owner.poll() is None:
            session.close(restore_preferences=lambda: restore_preferences(controller, output)
                          if (output / 'original-preferences.json').exists() else None, restore_package=verify)
        if not native_inventory():
            if (output / 'original-preferences.json').exists() and not session.closed:
                # The saved preference identities include the staged packages.
                # Keep them in place until a clean main-menu session restores them.
                write_json(output / 'cleanup-required.json', dict(preferences_verified=False,
                           temporary_packages=[str(path) for path in pins]))
            else:
                for path, expected in pins.items():
                    require(manifest(path) == expected, 'Refusing to retire a changed package')
                    path.rename(output / ('retired-' + path.name))
                require(all(manifest(path) == expected for path, expected in untouched.items()), 'Reference package changed')
                write_json(output / 'restoration.json', dict(verified=True, owners_absent=True, session_closed=session.closed))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for option in ('output', 'study', 'proof', 'mods', 'user-root', 'binary', 'ce-package', 'ce-dll'):
        parser.add_argument('--' + option, type=Path, required=True)
    parser.add_argument('--fixture-carrier', action='store_true', help='Select CE through the isolated saved mod identity')
    parser.add_argument('--hotfix', action='store_true', help='Qualify the pinned CE profile on the November XP2 and DX11 build')
    parser.add_argument('--ce-base-control', action='store_true', help='Replay with pinned upstream CE and no district-score API')
    parser.add_argument('--compat-profile-sha', help='Expected DLL SHA-256 for the selected executable compatibility build')
    run(parser.parse_args())
