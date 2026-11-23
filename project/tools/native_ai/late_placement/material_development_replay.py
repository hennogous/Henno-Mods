"""Run a focused material decision replay with the shared Civ controller.

Both arms load the same checkpoint. The research fixture uses the same
candidate binaries and omits one exact offer in the control. The Flax
replay compares frozen policy packages on the original world. A separate
worker replay reads recruitment and control for these same Flax plots.
These diagnostics are separate from the normal-start campaign totals.
"""
import argparse
from contextlib import contextmanager, nullcontext
import csv
import json
from pathlib import Path
import shutil
import sys
from types import SimpleNamespace

from audit_xp2_hotfix import XP2_IMAGE_SIZE
from ce_bakers_fresh import LOGS, package_identity
from ce_replay import DLL, HOTFIX_SHA, verify_modules
from driver import (STUDY, HeldProcess, NativeSession, configure, flags, launch, load, lua,
                    make_probe_controller, manifest, native_inventory, parse, read,
                    require, restore_preferences, sha, write_json)
from material_development_summary import BUILDER_FIELDS, OFFER, RECEIPT, RESEARCH_FIELDS, link_native_receipts
from planning_continue import HERE, compare_structure, enable, parse_census, prepare


START = 100
# The exact earlier reservation and worker loss are at turns 129–132.
# Advance the unchanged world to 125 before attaching the worker observer.
WORKER_TRACE_START = 125
REPLAYS = {'research': ('material_research_fixture.lua', 108), 'flax': ('material_flax_probe.lua', 135),
           'worker': ('material_flax_probe.lua', 135)}
LUA_FILES = {'CSC_AI_BakersGameplay.lua', 'CSC_AI_DistrictBridge.lua', 'CSC_AI_EconomyAdapters.lua',
             'CSC_AI_EconomyFacts.lua', 'CSC_AI_QuarterPlacement.lua'}


@contextmanager
def observe_workers(frida, session, controller, opening, out):
    # The adapter attaches only to the shared controller's held session after
    # matching the checkpoint, mod packages, and loaded GameCore/CE identity.
    modules = load(out/'loaded-modules.json')
    core = modules['GameCore_XP2_FinalRelease.dll']
    spec = dict(path=core['path'], sha256=core['sha256'], image_size=XP2_IMAGE_SIZE)
    builder = parse(controller.cmd(
        "print('CSC_MATERIAL_BUILDER='..assert(GameInfo.Units.UNIT_BUILDER).Index)",
        'GameCore_Tuner', 'worker-unit-index'), 'CSC_MATERIAL_BUILDER')
    scope = dict(player=opening['player'], city=opening['city'], plots=opening['plots'],
                 improvement=opening['improvement'], builder=builder, cePath=modules[DLL]['path'])
    if opening.get('earlyDispatch'):
        scope['earlyDispatch'] = opening['earlyDispatch']
    if opening.get('axum'):
        scope['axum'] = True
    if opening.get('snapshotOnly'):
        scope['snapshotOnly'] = True
    write_json(out/'worker-scope.json', scope)
    probe = HERE/'material_worker_observer.js'
    shutil.copyfile(probe, out/probe.name)
    attachment = frida.attach(session.owner.pid)
    try:
        code = "'use strict';\nconst CSC_LATE_PLACEMENT_COMPOSITE = true;\n" + read(STUDY/'observer.js') + '\n' + read(probe)
        script = attachment.create_script(code)
        script.load()
        require(script.exports_sync.init(spec, scope), 'Worker observer did not start')
        if scope.get('snapshotOnly'):
            def save_boundary(turn):
                reading = script.exports_sync.boundary(turn)
                write_json(out/f'worker-boundary-{turn}.json', reading)
            yield save_boundary
            return
        try:
            yield
        except Exception as error:
            # The owned process can still answer after an autoplay timeout.
            # Preserve incomplete evidence separately from a qualified trace.
            try:
                write_json(out/'worker-native-partial.json', script.exports_sync.freeze())
            except Exception as capture_error:
                error.add_note(f'Partial worker trace unavailable: {capture_error}')
            raise
        # This runs at an inactive boundary so an unfinished native callback
        # cannot be mistaken for a result. Save faults before rejecting a run.
        evidence = script.exports_sync.freeze()
        write_json(out/'worker-native-evidence.json', evidence)
        require(evidence['active'] == 0 and evidence['fault'] is None and evidence['events'],
                'Worker replay did not finish with complete native evidence')
    finally:
        attachment.detach()


def run_arm(source, candidate, out, *, control, case, frida=None):
    script, endpoint = REPLAYS[case]
    plan = prepare(source, out, START, START, None, read_only=True)
    for item in plan.packages:
        package = candidate / item['role'].upper()
        actual = manifest(package)
        changed = {name.replace('\\', '/') for name in actual.keys() | item['files'].keys()
                   if actual.get(name) != item['files'].get(name)}
        permitted = ({'Binaries/Win64/' + DLL} if item['role'] == 'ce'
                     else {'Lua_UI/AI/' + name for name in LUA_FILES})
        require(changed == permitted and package_identity(package)[0] == item['id'],
                'Fixture must use the same frozen campaign candidate')
        item.update(source=package, files=actual)
    require(not native_inventory(), 'Leave any existing Civ or FireTuner session with its owner')
    out.mkdir()
    fixture = read(HERE / script)
    observe_from = WORKER_TRACE_START if frida else START
    write_json(out/'protocol.json', dict(diagnostic_only=True, case=case, omit_target_offer=control and case=='research',
                                        checkpoint=plan.checkpoint, through=endpoint,
                                        native_observation_start=observe_from if frida else None))
    (out/script).write_text(fixture, encoding='utf-8')
    controller = make_probe_controller(out, user_root=plan.user_root)
    controller.study_endpoint = endpoint
    controller.autoplay_interval_seconds = plan.protocol['interval_minutes'] * 60
    controller.allow_one_more_turn = controller.allow_observer_congress_review = True
    controller.allow_observer_warning_dismissal = controller.allow_observer_first_meet_dismissal = True
    session = NativeSession(out, controller, inventory=native_inventory, hold=HeldProcess, write=write_json)
    copied = []

    def verify_packages():
        for item in copied:
            require(manifest(item['install']) == manifest(item['source']) == item['files'], 'Fixture package drift')
        for item in plan.extras.values():
            require(manifest(Path(item['path'])) == item['files'], 'Optional package drift')

    def source_gate():
        scope = 'CSC_ENDPOINT_PLAYERS=' + lua(plan.identity['original_ai']) + '\nCSC_ENDPOINT_EXPECTED_TURN=100\n'
        raw = controller.cmd(scope + read(HERE/'full_game_census.lua'), 'CSC_AI_BakersGameplay', 'material-source-census')
        proof = compare_structure(plan.expected_census, parse_census(raw, START))
        write_json(out/'source-structure-comparison.json', proof)
        require(proof['verified'], 'Loaded material replay world differs from checkpoint')
        return True

    try:
        for item in plan.packages:
            shutil.copytree(item['source'], item['install'])
            copied.append(item)
        session.start(lambda: launch(SimpleNamespace(binary=plan.binary),out))
        session.wait_context('MainMenu')
        configure(controller, out, csc_id=plan.protocol['ce'])
        enable(session, plan.protocol['csc'])
        for identity in plan.extras:
            enable(session, identity)
        require({k for k, v in flags(controller,'material-fixture-mods')['mods'].items() if v} ==
                {plan.protocol['ce'], plan.protocol['csc'], *plan.extras}, 'Unexpected active packages')
        session.load_once(plan.checkpoint['native_save'], sha256=plan.checkpoint['sha256'],
                          native_directory=plan.saves, turn=START, contexts=('GameCore_Tuner','CSC_AI_BakersGameplay'),
                          eligibility=source_gate)
        ce = next(item for item in copied if item['role'] == 'ce')
        verify_modules(session,ce['install']/'Binaries/Win64'/DLL,out,HOTFIX_SHA)
        raw = controller.cmd('CSC_MATERIAL_RESEARCH_CONTROL=' + lua(control) + '\n' + fixture,
                             'CSC_AI_BakersGameplay', 'material-fixture-start', wait=5)
        (out/'fixture-start.txt').write_text(raw, encoding='utf-8')
        opening = parse(raw, 'CSC_MATERIAL_FIXTURE_START')
        ceiling = None
        if case != 'research':
            ceiling = parse(raw, 'CSC_MATERIAL_FIXTURE_SCORE')['maxBidQ8']
            require(ceiling == (64 if control else 128)*256, 'Unexpected native improvement-score ceiling')
        # Use ordinary five-turn intervals up to the relevant trace window.
        # No extra gameplay commands are introduced at the attach boundary.
        for start in range(START, observe_from, 5):
            controller.play(min(start + 5, observe_from))
        observation = observe_workers(frida, session, controller, opening, out) if frida else nullcontext()
        # The shared controller releases known presentation blockers only
        # when the observer has a verified finite window of at most five turns.
        with observation:
            for start in range(observe_from, endpoint, 5):
                controller.play(min(start + 5, endpoint))
            state = controller.state_read('material-fixture-final-clock')
            require(state['turn']==endpoint and not state['active'], 'Unexpected material diagnostic endpoint')
        raw = controller.cmd("CSC_MaterialFixtureRead('CSC_MATERIAL_FIXTURE_END')",
                             'CSC_AI_BakersGameplay', 'material-fixture-end', wait=5)
        ending = parse(raw, 'CSC_MATERIAL_FIXTURE_END')
    finally:
        if session.owner is not None and session.owner.poll() is None:
            session.close(restore_preferences=lambda: restore_preferences(controller, out)
                          if (out/'original-preferences.json').exists() else None, restore_package=verify_packages)
        if session.closed or session.owner is None and not native_inventory():
            for item in copied:
                item['install'].rename(out/item['install'].name)
            if session.closed:
                for log in LOGS:
                    path = plan.user_root/'Logs'/log
                    if path.is_file():
                        shutil.copyfile(path, out/log)
    require(session.closed and sha(Path(plan.checkpoint['native_save']))==plan.checkpoint['sha256'],
            'Material fixture did not close or preserve the source save')

    measurements = read_research(out, opening) if case=='research' else read_flax(out, opening, endpoint)
    result = dict(opening=opening, ending=ending, improvement_ceiling_q8=ceiling, **measurements)
    if frida:
        result['worker_handoffs'] = worker_handoffs(load(out/'worker-native-evidence.json')['events'])
    write_json(out/'result.json', result)
    return result


def read_research(out, opening):
    offers, comparisons = [], []
    for line in (out/'Lua.log').read_text(encoding='utf-8-sig', errors='replace').splitlines():
        offer = OFFER.search(line)
        if offer and offer[1]=='RESEARCH':
            fields = dict(field.split('=',1) for field in offer[2].split())
            if (int(fields['player']), int(fields['kind']), int(fields['index'])) == (opening['player'],0,opening['topic']):
                offers.append(fields)
        receipt = RECEIPT.search(line)
        if receipt:
            row = json.loads(receipt[3])
            if row['tech']:
                sample = dict(zip(RESEARCH_FIELDS,row['techFirst'],strict=True))
                if (sample['player'], sample['first_topic']) == (opening['player'],opening['topic']):
                    comparisons.append(dict(read_turn=int(receipt[1]), version=int(receipt[2]), **sample))
    research = {}
    with (out/'AI_Research.csv').open(encoding='utf-8-sig', errors='replace', newline='') as log:
        for row in csv.reader(log, skipinitialspace=True):
            if (len(row) >= 7 and row[2:4] == ['Tech', 'TECH_IRRIGATION']
                    and int(row[1]) == opening['player'] and row[5] in ('GOAL', 'RESEARCHING', 'OWNED')):
                research.setdefault(row[5], int(row[0]))
    return dict(proposals=offers, comparisons=comparisons, first_logged_research_states=research)


def read_flax(out, opening, endpoint):
    player, improvement = opening['player'], opening['improvement']
    plots = {site['plot'] for site in opening['plots']}
    requests, reservations, offers = [], [], []
    with (out/'Lua.log').open(encoding='utf-8-sig', errors='replace') as log:
        for line in log:
            offer = OFFER.search(line)
            if offer and offer[1]=='REQUEST':
                fields = dict(field.split('=',1) for field in offer[2].split())
                if int(fields['player']) == player and int(fields['plot']) in plots and int(fields['improvement']) == improvement:
                    offers.append({k:int(v) for k,v in fields.items()})
            receipt = RECEIPT.search(line)
            if receipt:
                row = json.loads(receipt[3])
                if row['builder']:
                    sample = dict(zip(BUILDER_FIELDS, row['builderFirst'], strict=True))
                    if sample['player'] == player and sample['plot'] in plots and sample['improvement'] == improvement:
                        requests.append(dict(read_turn=int(receipt[1]), version=int(receipt[2]), **sample))
    native = {'tech':{'first_per_packet':[]}, 'civic':{'first_per_packet':[]},
              'builder':{'first_per_packet':requests}}
    with (out/'AI_CityBuild.csv').open(encoding='utf-8-sig', errors='replace', newline='') as log:
        link_native_receipts({'turn':endpoint, 'native':native, 'offers':{'REQUEST':offers}, 'work_history':[]}, log)
    positions = {f"Reserving plot {site['x']} {site['y']}": site['plot'] for site in opening['plots']}
    with (out/'AI_Behavior_Trees.csv').open(encoding='utf-8-sig', errors='replace', newline='') as log:
        for row in csv.reader(log, skipinitialspace=True):
            if (len(row) >= 7 and row[1] == str(player) and row[3:6] ==
                    ['Build City Improvement', 'SUCCESS', 'Reserve Plot'] and row[6] in positions):
                reservations.append({'turn': int(row[0]), 'tree': row[2], 'plot': positions[row[6]]})
    return dict(offers=offers, request_samples=requests, reservations=reservations)


def worker_handoffs(events):
    """Join a job's controlled workers to its empty protection list.

    A recent match names the individual still present, released, reassigned
    or departing. Keep empty-list events with no matching prior worker too.
    """
    previous, empty = {}, []
    for event in events:
        if event['kind'] not in ('recruit', 'protect'):
            continue
        controller = event.get('controller')
        if controller is None or controller < 0:
            continue
        plot, turn = event['plot'], event['turn']
        key = plot, controller
        if event['kind'] == 'recruit':
            units = [unit['unit'] for unit in event['after'] if unit['controller'] == controller]
        elif 'units' in event:
            units = event['units']['items']
            if not units:
                last_turn, last_units = previous.pop(key, (None, ()))
                recent = last_turn is not None and 0 <= turn - last_turn <= 1
                roster = {unit['unit']: unit for unit in event['roster']}
                empty.append(dict(turn=turn, plot=plot, controller=controller, status=event['status'],
                                  previous_turn=last_turn if recent else None,
                                  previous_workers=[dict(unit=unit, now=roster.get(unit))
                                                    for unit in last_units] if recent else []))
        else:
            continue
        if units:
            previous[key] = turn, units
    return empty


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('source', 'candidate', 'output'):
        parser.add_argument('--'+name, type=Path, required=True)
    parser.add_argument('--case', choices=REPLAYS, default='research')
    parser.add_argument('--baseline-candidate', type=Path, help='Original frozen candidate for the Flax replay')
    parser.add_argument('--probe-dependencies', type=Path, help='Existing Frida 17.24.3 package for the worker replay')
    args = parser.parse_args()
    if (args.baseline_candidate is not None) != (args.case == 'flax'):
        parser.error('Supply a baseline candidate only for the Flax replay')
    if (args.probe_dependencies is not None) != (args.case == 'worker'):
        parser.error('Supply probe dependencies only for the worker replay')
    if args.case == 'worker':
        dependencies = args.probe_dependencies.resolve(strict=True)
        sys.path.insert(0, str(dependencies))
        import frida
        require(frida.__version__ == '17.24.3' and Path(frida.__file__).resolve().is_relative_to(dependencies),
                'Exact existing Frida package required')
        run_arm(args.source, args.candidate, args.output, control=False, case='worker', frida=frida)
        return
    args.output.mkdir()
    before = run_arm(args.source, args.baseline_candidate or args.candidate, args.output/'control', control=True, case=args.case)
    after = run_arm(args.source, args.candidate, args.output/'treatment', control=False, case=args.case)
    require(before['opening']==after['opening'], 'Unequal material fixture openings')
    write_json(args.output/'comparison.json', dict(control=before, treatment=after))


if __name__=='__main__':
    main()
