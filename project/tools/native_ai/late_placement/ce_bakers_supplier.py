"""Match the main CSC supplier policy against a CE control on the Boston save."""

import argparse
import json
from pathlib import Path
import re
import shutil
import sys
import time
import xml.etree.ElementTree as ET

from ce_replay import (
    HOTFIX_EXE_SHA, add_fixture_carrier, verify_modules, DLL,
)
from driver import (
    HERE, ROOT, ID, HOTFIX_SHA, XP2_IMAGE_SIZE, STUDY, HeldProcess, NativeSession, archive_sources,
    capture_log_baseline, configure, flags, launch, load, lua, make_probe_controller,
    manifest, native_inventory, parse, read, read_log_delta, require,
    restore_preferences, sha, write_json,
)
from natural_chain import operating
from full_game_controller.checkpoint import archive_autosave_window, save_inactive_boundary
from supplier_timeline import write_matched_timelines


CANDIDATE_SHA = '5b62c20bd3fe4ea3a4364e160022bc5c0f2dacac504d6a07ecced2bdf1588545'
AI_ROOT = ROOT / 'Civ Supply Chains/Lua_UI/AI'
AI_FILES = tuple(AI_ROOT / name for name in (
    'CSC_AI_AdjacencyScan.lua', 'CSC_AI_QuarterPlacement.lua', 'CSC_AI_DistrictBridge.lua', 'CSC_AI_BakersGameplay.lua',
))
UI_READS = AI_ROOT.parent / 'Adjacencies/CSC_AdjacencyUI.lua'
LOGS = ('Lua.log', 'AI_CityBuild.csv', 'City_BuildQueue.csv')
BOOTSTRAP = 'CSC_AI_BakersReplay'


def add_policy(package, turn, builders=True, wonders=False, defer=False, recovery=True, harvest=True):
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
    bootstrap = (
        f"assert(Game.GetCurrentGameTurn()=={turn})\n"
        "for _, player in ipairs(PlayerManager.GetAliveMajors()) do\n"
        "    local id=player:GetID()\n"
        "    local human=player:IsHuman()\n"
        "    assert(human==(id==0))\n"
        "    Game:SetProperty('CSC_AI_OriginalHuman_'..id, human and 1 or 0)\n"
        "end\n" +
        ("" if builders else "CE_AIBuilderProtectionAllow=nil\n") +
        ("" if wonders else "CE_AISupplierWonderProtectionStage=nil\n") +
        ("" if recovery else "CE_AIBuilderProtectionBid=nil\n") +
        ("" if harvest else "CE_AIBuilderHarvestProtectionStage=nil\n") +
        "include('CSC_AI_BakersGameplay')\n"
    )
    if defer:
        # An autosave may create gameplay contexts before its saved clock and
        # roles settle. The controller calls this after verifying both.
        bootstrap = ("function CSC_BakersReplay_Initialize()\n" + bootstrap
                     + "CSC_BakersReplay_Initialize=nil\nend\n")
    (package / relative).write_text(bootstrap, encoding='utf-8')
    ET.SubElement(gameplay, 'File').text = relative
    ET.SubElement(files, 'File').text = relative
    tree.write(path, encoding='utf-8', xml_declaration=True)


def observer_sources(args):
    if not args.decision_observer_deps:
        return ()
    if args.wonder_autosave:
        script = 'mill_repair_observer.js'
    else:
        script = 'supplier_clear_gate.js' if args.guard_committed_harvest else 'pasture_recovery_observer.js'
    return STUDY / 'observer.js', HERE / script


def run_arm(args, out, archived, source, digest, probe, installed, treatment, target, start, endpoint,
            expected_source=None):
    require(not native_inventory() and not installed.exists(), 'Expected exclusive ownership and no temporary package')
    out.mkdir()
    prepared = out / 'prepared-package'
    shutil.copytree(archived, prepared)
    add_fixture_carrier(prepared, args.ce_dll)
    advanced = args.builder or args.wonder
    autosave = args.pasture_autosave or args.wonder_autosave
    trace_name = 'mill-repair' if args.wonder_autosave else 'pasture-recovery'
    builder_policy = (treatment or args.wonder or args.pasture_bid or args.guard_committed_harvest
                      or args.publisher_pasture_bid or args.publisher_harvest)
    wonder_policy = args.wonder and (treatment or args.mill_bid or args.project_eligibility)
    if treatment or advanced:
        add_policy(prepared, start, builders=builder_policy, wonders=wonder_policy,
                   defer=bool(autosave),
                   recovery=not args.pasture_autosave or (args.publisher_pasture_bid and treatment),
                   harvest=not args.pasture_autosave or (args.publisher_harvest and treatment))
    package = manifest(prepared)
    try:
        prepared.rename(installed)
    except PermissionError:
        # Some Windows folders disallow a cross-directory move. Keep the
        # prepared evidence and verify a copy before starting the game.
        require(not installed.exists() and not native_inventory(), 'Temporary package destination changed')
        shutil.copytree(prepared, installed)
        require(manifest(installed) == package, 'Copied temporary package differs')
    write_json(out / 'temporary-package.json', {str(installed): package})
    controller = make_probe_controller(out, user_root=args.user_root)
    controller.study_endpoint = endpoint
    controller.allow_observer_warning_dismissal = controller.allow_observer_first_meet_dismissal = True
    controller.allow_observer_congress_review = True
    session = NativeSession(out, controller, inventory=native_inventory, hold=HeldProcess, write=write_json)
    logs = {}
    attachment = observer = None
    observer_ready = False
    observer_messages = []
    checkpoints = []

    def freeze_observer():
        if observer_ready:
            write_json(out / f'{trace_name}-trace-frozen.json', observer.exports_sync.freeze())

    def sample(turn):
        raw = controller.cmd(probe, 'GameCore_Tuner', f'bakers-supplier-{turn}')
        city = parse(raw, 'CSC_NATURAL_FOLLOWTHROUGH')
        neighbors = [json.loads(value) for value in re.findall(r'CSC_BAKERS_SUPPLIER=([^\r\n]+)', raw)]
        require(city['turn'] == turn and len(neighbors) == 6, 'Unexpected supplier census')
        state = dict(city=city, neighbors=neighbors)
        if advanced:
            effects = 'CSC_BAKERS_TARGET=' + lua(target) + ';\n' + read(HERE / 'operating_effects.lua')
            ui = controller.cmd(effects, 'PlotInfo', f'bakers-effects-{turn}')
            state.update(conditions=parse(raw, 'CSC_NATURAL_CHAIN'), effects=parse(ui, 'CSC_BAKERS_EFFECTS'))
            state['operation'] = operating(state, target)
            if (args.publisher_pasture_bid or args.publisher_harvest) and not args.watch_storekeeper:
                controller.cmd(read(HERE / 'storekeeper_runtime.lua'), 'PlotInfo', f'storekeeper-modifiers-{turn}')
        return state

    def status(label):
        return parse(controller.cmd('print("CSC_BAKERS_CE="..CE_AIDistrictScoresStatus())',
                                    'GameCore_Tuner', label), 'CSC_BAKERS_CE')

    def protection_status(kind, label):
        return parse(controller.cmd(f'print("CSC_BAKERS_CE="..CE_AI{kind}ProtectionStatus())',
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
        if treatment or advanced:
            contexts += ('CSC_AdjacencyUI', BOOTSTRAP)
        session.load_once(source, sha256=digest, native_directory=source.parent, turn=start,
                          contexts=contexts, eligibility=ready)
        result['source'] = sample(start)
        require(expected_source is None or result['source'] == expected_source,
                'Continuation differs from the exact protected checkpoint')
        if autosave:
            session.issue_once('activate-supplier-policy', 'CSC_BakersReplay_Initialize()', BOOTSTRAP)
        initial = status('native-before-autoplay')
        district_policy = treatment or advanced
        require(initial['ready'] == 1 and initial['faults'] == 0 and initial['enabled'] == int(district_policy)
                and (args.wonder or bool(initial['entries']) == district_policy), 'Unexpected automatic CSC publication state')
        result['initial'] = initial
        if advanced:
            first = protection_status('Builder', 'builder-before-autoplay')
            require(first['ready'] and not first['faults'] and bool(first['entries']) == builder_policy,
                    'Unexpected initial Builder publication')
            if args.publisher_pasture_bid:
                require(first.get('maxBidQ8') == 8192, 'Expected the bounded CE supplier bid interface')
            result['builder_initial'] = first
        if args.wonder:
            first = protection_status('SupplierWonder', 'wonder-before-autoplay')
            require(first['ready'] and not first['faults'] and bool(first['protected']) == wonder_policy,
                    'Unexpected initial Wonder publication')
            result['wonder_initial'] = first
        if args.publisher_harvest:
            first = protection_status('BuilderHarvest', 'harvest-before-autoplay')
            require(first['ready'] and not first['faults'] and bool(first['protected']) == treatment,
                    'Unexpected initial harvest publication')
            result['harvest_initial'] = first
        # Civ truncates the previous process's logs while loading the save.
        # Take the baseline in the verified gameplay context.
        names = (*LOGS, 'UnitOperations.log', 'AI_Behavior_Trees.csv') if advanced else LOGS
        logs = {name: capture_log_baseline(args.user_root / 'Logs' / name) for name in names}
        if args.watch_storekeeper:
            raw = controller.cmd('CSC_BAKERS_STOREKEEPER_WATCH=true\n' + read(HERE / 'storekeeper_runtime.lua'),
                                 'PlotInfo', 'install-storekeeper-turn-watch')
            require('CSC_BAKERS_STOREKEEPER_WATCH_INSTALLED' in raw, 'Storekeeper watch installation failed')
        if args.decision_observer_deps:
            dependencies = args.decision_observer_deps.resolve()
            sys.path.insert(0, str(dependencies))
            import frida
            require(frida.__version__ == '17.24.3' and Path(frida.__file__).resolve().is_relative_to(dependencies),
                    'Exact existing Frida package required')
            modules = load(out / 'loaded-modules.json')
            if args.wonder_autosave:
                raw = controller.cmd(
                    "print('CSC_BAKERS_MILL_INDEX='..assert(GameInfo.Buildings.BUILDING_CSC_BAKERS_WATER_MILL).Index)",
                    'GameCore_Tuner', 'native-mill-repair-index')
                scope = dict(player=target['player'], city=target['city'], mill=parse(raw, 'CSC_BAKERS_MILL_INDEX'),
                             cePath=modules[DLL]['path'], millBidQ8=98304 if args.mill_bid and treatment else 0,
                             screenProjectEligibility=args.project_eligibility and treatment)
            else:
                scope = dict(load(args.replay / 'pasture-recovery-scope.json'), cePath=modules[DLL]['path'],
                             measurePastureBid=args.pasture_bid, applyPastureBid=args.pasture_bid and treatment,
                             block=args.guard_committed_harvest and treatment)
                require(scope['plot'] in target['base'] and scope['player'] == target['player']
                        and scope['city'] == target['city'], 'Observer scope differs from the matched fixture')
            spec = dict(path=modules['GameCore_XP2_FinalRelease.dll']['path'], image_size=XP2_IMAGE_SIZE)
            code = "'use strict';\nconst CSC_LATE_PLACEMENT_COMPOSITE = true;\n" + '\n'.join(
                map(read, observer_sources(args)))
            attachment = frida.attach(session.owner.pid)
            observer = attachment.create_script(code)
            observer.on('message', lambda value, data: observer_messages.append(value))
            observer.load()
            require(observer.exports_sync.init(spec, scope), 'Expected qualified supplier decision observer')
            observer_ready = True
        if advanced:
            observations = []
            previous = start
            for turn in range(start + 3, endpoint + 1, 3):
                if observer:
                    observer.exports_sync.advance(previous)
                interval_started = time.time_ns()
                controller.play(turn)
                if autosave:
                    archive = out / 'decision-saves'
                    checkpoints.extend(archive_autosave_window(source.parent, archive, previous + 1, turn, interval_started))
                    write_json(archive / 'archive.json', checkpoints)
                observations.append(sample(turn))
                write_json(out / 'observations.json', observations)
                if observer:
                    trace = observer.exports_sync.snapshot()
                    write_json(out / f'{trace_name}-trace-live.json', trace)
                    require(not trace['fault'] and not observer_messages, 'Supplier decision trace fault')
                previous = turn
                if ((args.resume_wonder_treatment or args.pasture_autosave) and len(observations) >= 2
                        and all(row['operation']['operating'] for row in observations[-2:])):
                    break
            result.update(final=observations[-1], builder_native=protection_status('Builder', 'builder-after-autoplay'))
            require(not result['builder_native']['faults'], 'Native Builder policy faulted')
            if args.publisher_harvest:
                result['harvest_native'] = protection_status('BuilderHarvest', 'harvest-after-autoplay')
                require(not result['harvest_native']['faults'], 'Native harvest protection faulted')
        else:
            controller.play(endpoint)
            result['final'] = sample(endpoint)
        result['native'] = status('native-after-autoplay')
        require(result['native']['faults'] == 0, 'Native district policy faulted')
        if args.wonder:
            result['wonder_native'] = protection_status('SupplierWonder', 'wonder-after-autoplay')
            require(not result['wonder_native']['faults'], 'Native Wonder policy faulted')
            if not args.resume_wonder_treatment:
                result['checkpoint'] = save_inactive_boundary(controller, turn=endpoint,
                    name='CSC_BAKERS_WONDER', native_directory=source.parent, archive=out / 'endpoint.Civ6Save')
        write_json(out / 'result.json', result)
    finally:
        if session.owner is not None and session.owner.poll() is None:
            session.close(restore_preferences=lambda: restore_preferences(controller, out)
                          if (out / 'original-preferences.json').exists() else None, restore_package=verify,
                          before_menu=freeze_observer)
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
    advanced = args.builder or args.wonder
    paired_mill = args.mill_bid or args.project_eligibility
    expected = args.ce_sha256 if advanced else CANDIDATE_SHA
    require(not out.exists() and sha(args.ce_dll) == expected and sha(args.binary) == HOTFIX_EXE_SHA,
            'Expected the exact qualified CE build and fresh output')
    require(load(replay / 'restoration.json')['verified'], 'Previous replay must be closed and restored')
    result = load(replay / 'result.json')
    continuation = args.resume_wonder_treatment
    prior_arm = None
    references = ()
    if continuation:
        continuation = continuation.resolve()
        prior_arm = continuation / 'treatment'
        matched_result = continuation / 'result.json'
        # Older successful Wonder matches have separate per-arm closure
        # receipts and no top-level restoration file.
        receipts = tuple(continuation / arm / name for arm in ('control', 'treatment')
                         for name in ('restoration.json', 'session-closed.json'))
        require(load(matched_result)['verified'] and all(load(path)['verified'] for path in receipts),
                'Expected a closed, verified Wonder match')
        references = (matched_result, *receipts, prior_arm / 'result.json')
    earlier = load(prior_arm / 'result.json') if prior_arm else (
        result if args.wonder or args.pasture_autosave else result['treatment'])
    start, endpoint = (210, 222) if args.wonder else ((45, 66) if args.builder else (31, 37))
    expected_source = earlier['final'] if prior_arm else None
    autosave_inputs = ()
    if args.pasture_autosave:
        require(earlier['setup'] == 'remove-pasture' and earlier['native_writes'] == 0
                and load(replay / 'session-closed.json')['verified'], 'Expected a closed stock supplier diagnostic')
        archive = args.pasture_autosave.resolve()
        receipt = archive.parent / 'archive.json'
        saved = next(row for row in load(receipt) if row['status'] == 'archived'
                     and Path(row['archive']).resolve() == archive)
        start, endpoint = saved['turn'], args.through
        digest = saved['sha256']
        if args.guard_committed_harvest or args.publisher_harvest:
            require(start == 72 and digest == '59d39aa77fbf9ecabc7a6694f778d659e95813e55446c1ba62fe46b29d97a285',
                    'Expected the turn-72 harvest decision fixture')
        states = replay / 'states.json'
        expected_source = next(row for row in load(states) if row['city']['turn'] == start)
        require(archive.parent == replay / 'decision-saves' and sha(archive) == digest
                and expected_source['operation']['mill'] and expected_source['operation']['customer']
                and not expected_source['operation']['workingBase'], 'Expected the archived missing-supplier state')
        native = args.mods.resolve().parent / 'Saves' / 'Single'
        source = native / f'CSC_BAKERS_PASTURE_{start}_{digest[:12]}.Civ6Save'
        if not source.exists():
            with archive.open('rb') as saved_file, source.open('xb') as native_file:
                shutil.copyfileobj(saved_file, native_file)
        require(sha(source) == digest, 'Named supplier save differs from its archive')
        autosave_inputs = (archive, receipt, states, replay / 'result.json', replay / 'session-closed.json')
    elif args.wonder_autosave:
        archive = args.wonder_autosave.resolve()
        receipt = archive.parent / 'archive.json'
        saved = next(row for row in load(receipt) if row['status'] == 'archived'
                     and Path(row['archive']).resolve() == archive)
        observed = archive.parent.parent
        require(archive.parent.name == 'decision-saves' and observed.name == 'treatment'
                and all(load(observed / name)['verified'] for name in ('restoration.json', 'session-closed.json'))
                and load(observed / 'result.json')['source'] == expected_source
                and load(observed / 'loaded-modules.json')[DLL]['sha256'] == args.ce_sha256,
                'Expected the closed protected recovery continuation and same CE binary')
        start, endpoint, digest = saved['turn'], args.through, saved['sha256']
        if paired_mill:
            require(start == 261 and digest == 'e393c2047e28ec9c167934799f9f1d55cef564d5e45e0d4f2cc062c84d9580b8',
                    'The matched Mill diagnostic requires the measured turn-261 queue fixture')
        states = observed / 'observations.json'
        expected_source = next(row for row in load(states) if row['city']['turn'] == start)
        require(sha(archive) == digest and expected_source['operation']['customer']
                and not expected_source['operation']['mill'], 'Expected the exact damaged Mill state')
        native = args.mods.resolve().parent / 'Saves' / 'Single'
        source = native / f'CSC_BAKERS_MILL_{start}_{digest[:12]}.Civ6Save'
        if not source.exists():
            with archive.open('rb') as saved_file, source.open('xb') as native_file:
                shutil.copyfileobj(saved_file, native_file)
        require(sha(source) == digest, 'Named Mill save differs from its archive')
        autosave_inputs = (archive, receipt, states, observed / 'result.json', observed / 'loaded-modules.json',
                           observed / 'session-closed.json', observed / 'restoration.json')
    else:
        checkpoint = earlier['checkpoint'] if advanced else load(replay / 'treatment/pre-supplier-checkpoint.json')
        source = Path(checkpoint['native_save']).resolve()
        digest = checkpoint['sha256']
        if prior_arm:
            start, endpoint = 222, args.through
        require(checkpoint['verified'] and checkpoint['turn'] == start and sha(source) == digest
                and sha(Path(checkpoint['archive'])) == digest, 'Expected the exact Boston fixture')
    if prior_arm or args.pasture_autosave:
        require(start < endpoint <= start + 45 and (endpoint - start) % 3 == 0,
                'Expected a bounded three-turn recovery cadence')
    target = load(args.match / 'result.json')['treatment']['plan']['target'] if advanced else earlier['plan']['target']
    if args.wonder:
        require((target['player'], target['city'], target['base']) == (3, 131073, [796]),
                'Expected the archived Cattle and Wonder claim')
    probe_files = tuple(HERE / name for name in ('natural_followthrough.lua', 'natural_chain.lua', 'supplier_world.lua'))
    probe = 'CSC_BAKERS_TARGET=' + lua(target) + ';\n' + '\n'.join(map(read, probe_files))
    out.mkdir()
    extra = (HERE / 'operating_effects.lua', HERE / 'natural_chain.py') if advanced else ()
    if args.publisher_pasture_bid or args.publisher_harvest or args.watch_storekeeper:
        extra += (HERE / 'storekeeper_runtime.lua',)
    observer_inputs = observer_sources(args)
    if args.pasture_autosave:
        tools = ROOT / 'project/tools/ai_baseline'
        autosave_inputs += (HERE / 'supplier_timeline.py', tools / 'full_game_controller/checkpoint.py',
                            tools / 'log_intelligence.py', tools / 'material_loss_intelligence.py')
    pins = {str(path.resolve()): sha(path) for path in (
        Path(__file__), *probe_files, *extra, *AI_FILES, *references, *autosave_inputs, *observer_inputs,
        UI_READS, args.ce_dll, source)}
    write_json(out / 'source-archive.json', archive_sources(pins, out / 'source-version'))
    archived = replay / 'retired-study-copy'
    installed = args.mods.resolve() / 'CSC Mill Building Study'
    if prior_arm:
        if paired_mill:
            control = run_arm(args, out / 'control', archived, source, digest, probe, installed, False,
                              target, start, endpoint, expected_source=expected_source)
        continued = run_arm(args, out / 'treatment', archived, source, digest, probe, installed, True,
                            target, start, endpoint, expected_source=expected_source)
        require(all(sha(Path(path)) == digest for path, digest in pins.items()), 'Pinned source changed during recovery')
        if paired_mill:
            require(control['source'] == continued['source'], 'The Mill arms have different starting states')
            write_json(out / 'result.json', dict(source=digest, start=start, endpoint=endpoint,
                control=control['final']['operation'], treatment=continued['final']['operation']))
            write_json(out / 'restoration.json', dict(verified=True, owners_absent=True))
            return
        write_json(out / 'result.json', continued)
        write_json(out / 'restoration.json', load(out / 'treatment/restoration.json'))
        return
    control = run_arm(args, out / 'control', archived, source, digest, probe, installed, False, target, start, endpoint,
                      expected_source=expected_source)
    treated = run_arm(args, out / 'treatment', archived, source, digest, probe, installed, True, target, start, endpoint,
                      expected_source=expected_source)
    require(control['source'] == treated['source'], 'The arms did not start from the same observed state')
    plot, = target['base']
    lost = next(row for row in control['final']['neighbors'] if row['plot'] == plot)
    kept = next(row for row in treated['final']['neighbors'] if row['plot'] == plot)
    if args.pasture_autosave:
        require(all(sha(Path(path)) == value for path, value in pins.items()), 'Pinned source changed during recovery')
        write_matched_timelines(out, load(replay / 'pasture-recovery-scope.json'))
        experiment = 'builder-protection'
        if args.pasture_bid:
            experiment = 'pasture-bid'
        if args.guard_committed_harvest:
            experiment = 'committed-harvest'
        if args.publisher_pasture_bid:
            experiment = 'published-pasture-bid'
        if args.publisher_harvest:
            experiment = 'published-harvest-protection'
        write_json(out / 'result.json', dict(source=digest, turn=start, plot=plot, experiment=experiment,
                   control=lost, treatment=kept,
                   control_operation=control['final']['operation'], treatment_operation=treated['final']['operation']))
        write_json(out / 'restoration.json', dict(verified=True, owners_absent=True))
        return
    log = read(out / 'treatment/Lua.log')
    if args.wonder:
        require(control['source'] == earlier['state'], 'Matched arms differ from the archived damage')
        statuses = [json.loads(value) for value in re.findall(
            r'CSC_AI_BAKERS_WONDERS [^\r\n]+previous=([^\r\n]+)', log)]
        key = [target['player'], target['city'], plot]
        scores = [s['first'] for s in statuses if s['changed'] and s['first'][:3] == key]
        claim = r'^\d+, 3, City LOC_CITY_NAME_BOSTON, Seek Target Wonder, SUCCESS, Reserve Plot, Reserving plot 56 10\s*$'
        reservations = {arm: len(re.findall(claim, read(out / arm / 'AI_Behavior_Trees.csv'), re.M))
                        for arm in ('control', 'treatment')}
        result = dict(plot=plot, control=lost, treatment=kept, target_score_samples=scores,
                      reservations=reservations, treatment_operation=treated['final']['operation'],
                      verified=bool(scores and reservations['control'] and not reservations['treatment']
                                    and not any(s['faults'] for s in statuses)))
        write_json(out / 'result.json', result)
        require(result['verified'], 'Wonder protection did not change the matched reservation')
        return
    if args.builder:
        statuses = [json.loads(value) for value in re.findall(r'CSC_AI_BAKERS_BUILDERS [^\r\n]+previous=([^\r\n]+)', log)]
        changes = sum(status['changed'] for status in statuses)
        verified = (not lost['working'] and kept['working'] and changes > 0
                    and treated['final']['operation']['operating'] and not any(status['faults'] for status in statuses))
    else:
        changes = sum(map(int, re.findall(r'CSC_AI_BAKERS_DISTRICTS [^\r\n]+previousChanged=(\d+)', log)))
        verified = not lost['deposit'] and kept['working'] and changes > 0
    result = dict(plot=plot, control=lost, treatment=kept, policy_changes=changes, verified=verified)
    write_json(out / 'result.json', result)
    require(result['verified'], 'Automatic preservation did not meet the matched observation')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('output', 'replay', 'mods', 'user-root', 'binary', 'ce-dll'):
        parser.add_argument('--' + name, type=Path, required=True)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument('--builder', action='store_true')
    modes.add_argument('--wonder', action='store_true')
    parser.add_argument('--ce-sha256')
    parser.add_argument('--match', type=Path)
    parser.add_argument('--resume-wonder-treatment', type=Path, help='Continue the closed Wonder treatment from turn 222')
    parser.add_argument('--wonder-autosave', type=Path, help='Read a later damaged-Mill checkpoint from that continuation')
    parser.add_argument('--pasture-autosave', type=Path, help='Pair Builder protection from a preserved supplier decision save')
    parser.add_argument('--decision-observer-deps', type=Path, help='Pinned Frida directory for native selector traces')
    interventions = parser.add_mutually_exclusive_group()
    interventions.add_argument('--pasture-bid', action='store_true',
                               help='Keep Builder protection in both arms and add a bounded Boston Pasture bid in treatment')
    interventions.add_argument('--guard-committed-harvest', action='store_true',
                               help='Keep Builder protection in both arms and reject the verified Clear Plot harvest in treatment')
    interventions.add_argument('--publisher-pasture-bid', action='store_true',
                               help='Keep Builder protection in both arms and enable the native CSC recovery bid in treatment')
    interventions.add_argument('--publisher-harvest', action='store_true',
                               help='Enable the main CSC native Clear Plot protection only in treatment')
    interventions.add_argument('--mill-bid', action='store_true',
                               help='Compare a bounded Mill nomination preference on the exact turn-261 fixture')
    interventions.add_argument('--project-eligibility', action='store_true',
                               help='Screen project candidates with native CanAdvance on the exact turn-261 fixture')
    parser.add_argument('--through', type=int)
    parser.add_argument('--watch-storekeeper', action='store_true',
                        help='Observe native Storekeeper at each autoplay turn start in both arms')
    args = parser.parse_args()
    if (args.builder or args.wonder) and (not args.match or not args.ce_sha256):
        parser.error('--builder or --wonder requires --match and --ce-sha256')
    if (bool(args.resume_wonder_treatment or args.pasture_autosave) != (args.through is not None)
            or (args.resume_wonder_treatment and not args.wonder) or (args.pasture_autosave and not args.builder)):
        parser.error('Use --through with --wonder --resume-wonder-treatment or --builder --pasture-autosave')
    if args.wonder_autosave and (not args.resume_wonder_treatment or not args.decision_observer_deps):
        parser.error('The later Wonder autosave requires the prior treatment and pinned decision observer')
    if (args.mill_bid or args.project_eligibility) and not args.wonder_autosave:
        parser.error('The matched Mill diagnostics require the exact later Wonder autosave')
    if args.decision_observer_deps and not (args.pasture_autosave or args.wonder_autosave):
        parser.error('The decision observer requires a qualified supplier or Mill autosave')
    if (args.pasture_bid or args.guard_committed_harvest) and not args.decision_observer_deps:
        parser.error('The experimental intervention requires the matched supplier observer')
    if (args.publisher_pasture_bid or args.publisher_harvest) and (not args.pasture_autosave or args.decision_observer_deps):
        parser.error('The published policy comparison requires a matched supplier autosave without Frida')
    if args.watch_storekeeper and not args.pasture_autosave:
        parser.error('The Storekeeper clock study requires a matched supplier autosave')
    run(args)
