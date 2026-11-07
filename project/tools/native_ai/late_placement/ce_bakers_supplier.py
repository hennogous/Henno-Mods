"""Match the main CSC supplier policy against a CE control on the Boston save."""

import argparse
import json
from pathlib import Path
import re
import shutil
import xml.etree.ElementTree as ET

from ce_replay import (
    HOTFIX_EXE_SHA, add_fixture_carrier, verify_modules, DLL,
)
from driver import (
    HERE, ROOT, ID, HOTFIX_SHA, HeldProcess, NativeSession, archive_sources,
    capture_log_baseline, configure, flags, launch, load, lua, make_probe_controller,
    manifest, native_inventory, parse, read, read_log_delta, require,
    restore_preferences, sha, write_json,
)


CANDIDATE_SHA = '5b62c20bd3fe4ea3a4364e160022bc5c0f2dacac504d6a07ecced2bdf1588545'
AI_ROOT = ROOT / 'Civ Supply Chains/Lua_UI/AI'
AI_FILES = tuple(AI_ROOT / name for name in (
    'CSC_AI_QuarterPlacement.lua', 'CSC_AI_DistrictBridge.lua', 'CSC_AI_BakersGameplay.lua',
))
UI_READS = AI_ROOT.parent / 'Adjacencies/CSC_AdjacencyUI.lua'
LOGS = ('Lua.log', 'AI_CityBuild.csv', 'City_BuildQueue.csv')
BOOTSTRAP = 'CSC_AI_BakersReplay'


def add_policy(package):
    """Register the actual publisher and seed only saved role metadata for this old fixture."""
    (path,) = package.glob('*.modinfo')
    ui = package / UI_READS.relative_to(AI_ROOT.parent.parent)
    require(ui.is_file(), 'Expected the fixture to use the main CSC UI read context')
    shutil.copyfile(UI_READS, ui)
    tree = ET.parse(path)
    root = tree.getroot()
    actions, files = root.find('InGameActions'), root.find('Files')
    libraries = ET.SubElement(actions, 'ImportFiles', id='CSC_BakersReplayModules')
    ET.SubElement(ET.SubElement(libraries, 'Properties'), 'LoadOrder').text = '490'
    gameplay = ET.SubElement(actions, 'AddGameplayScripts', id='CSC_BakersReplayGameplay')
    ET.SubElement(ET.SubElement(gameplay, 'Properties'), 'LoadOrder').text = '999991'
    imported = {Path(node.text).name for action in actions.findall('ImportFiles') for node in action.findall('File')}
    known = {node.text for node in files.findall('File')}
    for file in AI_FILES:
        relative = 'Lua_UI/AI/' + file.name
        target = package / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(file, target)
        if file.name not in imported:
            ET.SubElement(libraries, 'File').text = relative
        if relative not in known:
            ET.SubElement(files, 'File').text = relative
    relative = f'Lua_UI/AI/{BOOTSTRAP}.lua'
    (package / relative).write_text(
        "assert(Game.GetCurrentGameTurn()==31)\n"
        "for _, player in ipairs(PlayerManager.GetAliveMajors()) do\n"
        "    local id=player:GetID()\n"
        "    local human=player:IsHuman()\n"
        "    assert(human==(id==0))\n"
        "    Game:SetProperty('CSC_AI_OriginalHuman_'..id, human and 1 or 0)\n"
        "end\n"
        "include('CSC_AI_BakersGameplay')\n",
        encoding='utf-8',
    )
    ET.SubElement(gameplay, 'File').text = relative
    ET.SubElement(files, 'File').text = relative
    tree.write(path, encoding='utf-8', xml_declaration=True)


def run_arm(args, out, archived, source, digest, probe, installed, treatment):
    require(not native_inventory() and not installed.exists(), 'Expected exclusive ownership and no temporary package')
    out.mkdir()
    prepared = out / 'prepared-package'
    shutil.copytree(archived, prepared)
    add_fixture_carrier(prepared, args.ce_dll)
    if treatment:
        add_policy(prepared)
    package = manifest(prepared)
    prepared.rename(installed)
    write_json(out / 'temporary-package.json', {str(installed): package})
    controller = make_probe_controller(out, user_root=args.user_root)
    controller.study_endpoint = 37
    controller.allow_observer_warning_dismissal = controller.allow_observer_first_meet_dismissal = True
    controller.allow_observer_congress_review = True
    session = NativeSession(out, controller, inventory=native_inventory, hold=HeldProcess, write=write_json)
    logs = {}

    def sample(turn):
        raw = controller.cmd(probe, 'GameCore_Tuner', f'bakers-supplier-{turn}')
        city = parse(raw, 'CSC_NATURAL_FOLLOWTHROUGH')
        neighbors = [json.loads(value) for value in re.findall(r'CSC_BAKERS_SUPPLIER=([^\r\n]+)', raw)]
        require(city['turn'] == turn and len(neighbors) == 6, 'Unexpected supplier census')
        return dict(city=city, neighbors=neighbors)

    def status(label):
        return parse(controller.cmd('print("CSC_BAKERS_CE="..CE_AIDistrictScoresStatus())',
                                    'GameCore_Tuner', label), 'CSC_BAKERS_CE')

    def verify():
        require(manifest(installed) == package, 'Temporary package changed')

    result = {}
    try:
        session.start(lambda: launch(args, out))
        session.wait_context('MainMenu')
        configure(controller, out, 'BASIC', csc_id=ID)
        require({key for key, enabled in flags(controller, 'verify-isolated-csc')['mods'].items() if enabled} == {ID},
                'Unexpected enabled package')

        def ready():
            verify_modules(session, (installed / 'Binaries/Win64' / DLL).resolve(), out, HOTFIX_SHA)
            return True

        contexts = ('GameCore_Tuner', 'PlotInfo', 'CSC_AdjacencyGameplay')
        if treatment:
            contexts += ('CSC_AdjacencyUI', BOOTSTRAP)
        session.load_once(source, sha256=digest, native_directory=source.parent, turn=31,
                          contexts=contexts, eligibility=ready)
        result['source'] = sample(31)
        initial = status('native-before-autoplay')
        require(initial['ready'] == 1 and initial['faults'] == 0 and initial['enabled'] == int(treatment)
                and bool(initial['entries']) == treatment, 'Unexpected automatic CSC publication state')
        result['initial'] = initial
        # Civ truncates the previous process's logs while loading the save.
        # Take the baseline in the verified gameplay context.
        logs = {name: capture_log_baseline(args.user_root / 'Logs' / name) for name in LOGS}
        controller.play(37)
        result.update(final=sample(37), native=status('native-after-autoplay'))
        require(result['native']['faults'] == 0, 'Native district policy faulted')
        write_json(out / 'result.json', result)
    finally:
        if session.owner is not None and session.owner.poll() is None:
            session.close(restore_preferences=lambda: restore_preferences(controller, out)
                          if (out / 'original-preferences.json').exists() else None, restore_package=verify)
        if session.closed:
            verify()
            installed.rename(out / 'retired-package')
            write_json(out / 'restoration.json', dict(verified=True, owners_absent=True))
            for name, baseline in logs.items():
                _, payload = read_log_delta(args.user_root / 'Logs' / name, baseline)
                (out / name).write_bytes(payload)
    return result


def run(args):
    replay, out = args.replay.resolve(), args.output.resolve()
    require(not out.exists() and sha(args.ce_dll) == CANDIDATE_SHA and sha(args.binary) == HOTFIX_EXE_SHA,
            'Expected the exact qualified CE build and fresh output')
    require(load(replay / 'restoration.json')['verified'], 'Previous replay must be closed and restored')
    checkpoint = load(replay / 'treatment/pre-supplier-checkpoint.json')
    source = Path(checkpoint['native_save']).resolve()
    digest = checkpoint['sha256']
    require(checkpoint['verified'] and checkpoint['turn'] == 31 and sha(source) == digest
            and sha(Path(checkpoint['archive'])) == digest, 'Expected the exact turn-31 fixture')
    target = load(replay / 'result.json')['treatment']['plan']['target']
    probe_files = tuple(HERE / name for name in ('natural_followthrough.lua', 'natural_chain.lua', 'supplier_world.lua'))
    probe = 'CSC_BAKERS_TARGET=' + lua(target) + ';\n' + '\n'.join(map(read, probe_files))
    out.mkdir()
    pins = {str(path.resolve()): sha(path) for path in (Path(__file__), *probe_files, *AI_FILES, UI_READS, args.ce_dll, source)}
    write_json(out / 'source-archive.json', archive_sources(pins, out / 'source-version'))
    archived = replay / 'retired-study-copy'
    installed = args.mods.resolve() / 'CSC Mill Building Study'
    control = run_arm(args, out / 'control', archived, source, digest, probe, installed, False)
    treated = run_arm(args, out / 'treatment', archived, source, digest, probe, installed, True)
    require(control['source'] == treated['source'], 'The arms did not start from the same observed state')
    plot, = target['base']
    lost = next(row for row in control['final']['neighbors'] if row['plot'] == plot)
    kept = next(row for row in treated['final']['neighbors'] if row['plot'] == plot)
    consumed = re.findall(r'CSC_AI_BAKERS_DISTRICTS [^\r\n]+previousChanged=(\d+)',
                          read(out / 'treatment/Lua.log'))
    result = dict(plot=plot, control=lost, treatment=kept, policy_changes=sum(map(int, consumed)),
                  verified=not lost['deposit'] and kept['working'] and any(int(count) for count in consumed))
    write_json(out / 'result.json', result)
    require(result['verified'], 'Automatic preservation did not meet the matched observation')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('output', 'replay', 'mods', 'user-root', 'binary', 'ce-dll'):
        parser.add_argument('--' + name, type=Path, required=True)
    run(parser.parse_args())
