"""Isolate one native SQL customer adjacency amount in a verified saved world.

Diagnostic only: unchanged main CSC/CE policy, no fixture edits or scripted
production. A last SQL action changes one rule's YieldChange while preserving
its ID, links, yield index and bias. The shared controller owns the process and
all play. Optional short play observes native winner/loser matrices at the
existing qualified selector boundary; a zero-turn survey reads legal geometry
and fresh native site quotes before choosing a longer diagnostic window.
"""
import argparse
from pathlib import Path
import json
from contextlib import closing
import re
import sqlite3
import shutil
import sys
from types import SimpleNamespace
import traceback
import xml.etree.ElementTree as ET

from planning_continue import prepare, enable, parse_census, compare_structure
from driver import (NativeSession, HeldProcess, make_probe_controller, native_inventory,
    launch, configure, flags, manifest, read, lua, sha, write_json, restore_preferences,
    require, archive_sources)
from ce_replay import DLL, HOTFIX_SHA, verify_modules
from ce_bakers_fresh import LOGS
from customer_adjacency_policy import database_snapshot
from customer_connector_audit import audit as audit_customers
from economy_savings_watch import EconomySavingsWatch

HERE = Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parents[3]/'project/tools/transactions'))
from population_catalogue_fixture import graph as transaction_graph
RULE = 'CSC_AI_CUSTOMER_DISTRICT_COMMERCIAL_HUB__DISTRICT_CSC_BAKERS_QUARTER'
SQL_PATH = 'Data/CSC_DIAG_CUSTOMER_STRENGTH.sql'
CONNECTORS = HERE.parents[3]/'Civ Supply Chains/Data/CSC_Q_ALL_AI_Connectors.sql'


def stage(source, amount, connector_sql=b''):
    require(type(amount) is int and amount in (0, 1, 2, 4, 8, 16), 'Bounded diagnostic amount required')
    root = ET.fromstring(source)
    actions, files = root.find('InGameActions'), root.find('Files')
    require(actions is not None and files is not None, 'Missing package actions/files')
    require(not any(f.text == SQL_PATH for f in files), 'Diagnostic already registered')
    highest = max([0] + [int(p.text) for action in actions for p in action.findall('Properties/LoadOrder')])
    require(highest < 2147483646, 'No last-action load order available')
    action = ET.SubElement(actions, 'UpdateDatabase', id='CSC_DIAG_CUSTOMER_STRENGTH')
    ET.SubElement(ET.SubElement(action, 'Properties'), 'LoadOrder').text = str(highest + 1)
    ET.SubElement(action, 'File').text = SQL_PATH
    ET.SubElement(files, 'File').text = SQL_PATH
    sql = ('-- Diagnostic only: one amount, stable native identities and links.\n'
           f"UPDATE Adjacency_YieldChanges SET YieldChange={amount} WHERE ID='{RULE}';\n")
    # Execute the production generator itself, idempotently, in every arm.
    # That repairs absent Stage3 links without a second diagnostic mapping;
    # all arms then differ only in this single target amount.
    return ET.tostring(root, encoding='utf-8', xml_declaration=True), connector_sql+b'\n'+sql.encode('utf-8')


def qualify_database(snapshot, amount):
    rows = [r for r in snapshot['rules'] if r['ID'] == RULE]
    require(len(rows) == 1 and rows[0]['YieldChange'] == amount and rows[0]['TilesRequired'] == 1,
            'Loaded diagnostic amount differs')
    require(sum(r['DistrictType'] == 'DISTRICT_COMMERCIAL_HUB' and r['YieldChangeId'] == RULE
                for r in snapshot['links']) == 1, 'Target native link missing')
    require(len(snapshot['yields']) == 1 and snapshot['yields'][0]['DefaultValue'] == 1,
            'Private yield identity/value differs')
    require(len(snapshot['biases']) == 1 and snapshot['biases'][0]['Value'] == 25,
            'Private yield bias differs')


SURVEY = '''
local ui=assert(ExposedMembers.CSC_Adjacency)
local h=assert(GameInfo.Districts.DISTRICT_COMMERCIAL_HUB)
local q=assert(GameInfo.Districts.DISTRICT_CSC_BAKERS_QUARTER)
local y=assert(GameInfo.Yields.YIELD_CSC_AI_PLACEMENT)
local r=assert(GameInfo.Adjacency_YieldChanges['__RULE__'])
assert(r.YieldChange==__AMOUNT__)
print('CSC_SIGNAL_RULE',r.Index,r.ID,r.YieldChange,y.Index,y.DefaultValue)
for _,scope in ipairs(__TARGETS__)do
 local pid,id=scope[1],scope[2];local city=assert(CityManager.GetCity(pid,id))
 local ds=city:GetDistricts();local legal={}
 for _,plot in ipairs(ui.GetLegalDistrictTargets(pid,id,h.Hash)or{})do legal[plot]=true end
 print('CSC_SIGNAL_CITY',pid,id,city:GetName(),city:GetPopulation(),ds:HasDistrict(h.Index),city:GetBuildQueue():CurrentlyBuilding())
 local center=Map.GetPlot(city:GetX(),city:GetY())
 for _,p in ipairs(CSC_Adjacency.PlotsInBand(center,1,3))do
  local owner=Cities.GetPlotPurchaseCity(p);local adjacent={}
  for _,near in ipairs(Map.GetAdjacentPlots(p:GetX(),p:GetY()))do
   if near:GetOwner()==pid and near:GetDistrictType()==q.Index then adjacent[#adjacent+1]=near:GetIndex()end
  end
  -- Explicit instant-ready quote isolates native site accounting. The normal
  -- selector retains its own ETA, buildings and preference; capture that
  -- comparison separately rather than presenting this quote as its final bid.
  local quote=CE_AIDistrictSiteAdjustment(pid,id,h.Index,p:GetX(),p:GetY(),0,50,1024)
  print('CSC_SIGNAL_PLOT',pid,id,p:GetIndex(),p:GetOwner(),owner and owner:GetID()or-1,
   p:GetDistrictType(),p:GetResourceType(),p:GetImprovementType(),tostring(p:IsRiver()),
   tostring(legal[p:GetIndex()]or false),table.concat(adjacent,','),quote or'nil')
 end
end
print('CSC_SIGNAL_SURVEY_END',Game.GetCurrentGameTurn())
'''


def survey_code(amount, targets):
    # The shared Lua encoder accepts lists, not Python tuple identities used
    # for scope deduplication. Normalize before any native command is issued.
    return (SURVEY.replace('__RULE__', RULE).replace('__AMOUNT__', str(amount))
            .replace('__TARGETS__', lua([list(t) for t in targets])))


def run(args):
    # Reuse the ordinary saved-world provenance guard without weakening its
    # supported continuation endpoints: this tool declares its own <=5-turn
    # diagnostic window after qualifying the zero-turn source.
    plan = prepare(args.source, args.output, args.at, args.at, args.dependencies, read_only=True)
    require(args.at <= args.through <= args.at + 5, 'At most five diagnostic turns')
    targets = [tuple(t) for t in args.target]
    require(0 < len(targets) <= 8 and len(set(targets)) == len(targets) and
            all(p in plan.identity['original_ai'] and 0 < c < 2**31 for p, c in targets), 'Invalid target scope')
    require(not native_inventory(), 'Preserve foreign Civ/Tuner session')
    out = plan.output
    out.mkdir(parents=True)
    by_role = {p['role']: p for p in plan.packages}
    metadata, = by_role['csc']['source'].glob('*.modinfo')
    staged, sql = stage(metadata.read_bytes(), args.amount, CONNECTORS.read_bytes())
    (out/'diagnostic.modinfo').write_bytes(staged)
    (out/'diagnostic.sql').write_bytes(sql)
    write_json(out/'protocol.json', dict(diagnostic=True, amount=args.amount, rule=RULE,
        source=str(plan.source), checkpoint=plan.checkpoint, start=args.at, through=args.through,
        targets=targets, gameplay_edits=False, main_lua_policy_unchanged=True, shared_stage3_sql_repair=True,
        connector_generator_sha256=sha(CONNECTORS), source_commit='de174092'))
    scripts = [Path(__file__), Path(transaction_graph.__code__.co_filename), HERE/'economy_savings_watch.py', HERE/'economy_savings_watch.js',
               HERE/'full_game_census.lua', HERE/'planning_observer.lua', HERE/'district_adjacency_watch.lua',
               HERE/'customer_connector_audit.py', CONNECTORS]
    pins = {str(p.resolve()): sha(p) for p in scripts}
    write_json(out/'implementation-archive.json', archive_sources(pins, out/'implementation-version'))
    controller = make_probe_controller(out, user_root=plan.user_root)
    controller.study_endpoint = args.through
    controller.autoplay_interval_seconds = 15*60
    controller.allow_observer_warning_dismissal = controller.allow_observer_first_meet_dismissal = True
    controller.allow_observer_congress_review = True
    session = NativeSession(out, controller, inventory=native_inventory, hold=HeldProcess, write=write_json)
    copied, watch, expected = [], None, {}

    def verify():
        for item in copied:
            require(manifest(item['install']) == expected[item['role']], 'Installed diagnostic package changed')
            require(manifest(item['source']) == item['files'], 'Original frozen source changed')
        for item in plan.extras.values():
            require(manifest(Path(item['path'])) == item['files'], 'Optional package changed')
        require(all(sha(Path(p)) == h for p, h in pins.items()), 'Diagnostic implementation changed')

    def gate():
        code = ('CSC_ENDPOINT_PLAYERS='+lua(plan.identity['original_ai'])+'\nCSC_ENDPOINT_EXPECTED_TURN='
                +str(plan.at)+'\n'+read(HERE/'full_game_census.lua'))
        raw = controller.cmd(code, 'CSC_AI_BakersGameplay', 'customer-signal-source-census')
        (out/'source-census.txt').write_text(raw, encoding='utf-8')
        proof = compare_structure(plan.expected_census, parse_census(raw, plan.at))
        write_json(out/'source-structure-comparison.json', proof)
        require(proof['verified'], 'Saved-world structure changed')
        return True

    def survey(label):
        raw = controller.cmd(survey_code(args.amount,targets), 'CSC_AI_BakersGameplay', label)
        (out/(label+'.txt')).write_text(raw, encoding='utf-8')
        require('CSC_SIGNAL_SURVEY_END' in raw, 'Incomplete native site survey')

    try:
        for item in plan.packages:
            shutil.copytree(item['source'], item['install'])
            copied.append(item)
            if item['role'] == 'csc':
                (item['install']/metadata.name).write_bytes(staged)
                (item['install']/SQL_PATH).write_bytes(sql)
            expected[item['role']] = manifest(item['install'])
        write_json(out/'installed-manifests.json', expected)
        session.start(lambda: launch(SimpleNamespace(binary=plan.binary), out))
        session.wait_context('MainMenu')
        configure(controller, out, csc_id=plan.protocol['ce'])
        enable(session, plan.protocol['csc'])
        for identity in plan.extras: enable(session, identity)
        require({k for k, v in flags(controller, 'customer-signal-mods')['mods'].items() if v} ==
                {plan.protocol['ce'], plan.protocol['csc'], *plan.extras}, 'Unexpected enabled packages')
        session.load_once(plan.checkpoint['native_save'], sha256=plan.checkpoint['sha256'],
            native_directory=plan.saves, turn=plan.at,
            contexts=('GameCore_Tuner', 'PlotInfo', 'CSC_AI_BakersGameplay', 'CSC_AdjacencyGameplay'), eligibility=gate)
        verify_modules(session, by_role['ce']['install']/'Binaries/Win64'/DLL, out, HOTFIX_SHA)
        db = database_snapshot(plan.user_root/'Cache/DebugGameplay.sqlite')
        write_json(out/'loaded-customer-database.json', db)
        qualify_database(db, args.amount)
        with closing(sqlite3.connect((plan.user_root/'Cache/DebugGameplay.sqlite').as_uri()+'?mode=ro',uri=True)) as loaded:
            coverage=audit_customers(loaded)
            # Original-package native baseline for cross-cutting gameplay
            # migrations. Capture all CSC effect rows, including Services and
            # shared requirements; a fixed-only closure misses cascading damage.
            write_json(out/'all-csc-native-graph.json',transaction_graph(loaded,'all_csc'))
        write_json(out/'loaded-customer-coverage.json',coverage)
        require(not(coverage['missing']or coverage['unexpected']or coverage['duplicates']),
                'Loaded customer graph does not match gameplay definitions')
        if args.amount>0:require(coverage['complete'],'Loaded customer bonus invalid')
        else:require(len(coverage['invalid'])==1 and coverage['invalid'][0]['amount']==0,
                     'OFF arm changed another customer bonus')
        survey('initial-survey')
        if args.through > args.at:
            catalogue = controller.cmd("for d in GameInfo.Districts()do print('CSC_SIGNAL_DISTRICT',d.Index,d.DistrictType)end",
                                       'CSC_AI_BakersGameplay', 'customer-signal-districts')
            (out/'districts.txt').write_text(catalogue, encoding='utf-8')
            count = max(map(int, re.findall(r'CSC_SIGNAL_DISTRICT\s+(\d+)', catalogue))) + 1
            for name in ('economy_savings_watch.py', 'economy_savings_watch.js'):
                shutil.copyfile(HERE/name, out/name)
            modules = json.loads((out/'loaded-modules.json').read_text(encoding='utf-8'))
            width, height = plan.identity['map_signature'][:2]
            watch = EconomySavingsWatch(directory=plan.dependencies,
                binary=modules['GameCore_XP2_FinalRelease.dll']['path'], output=out,
                start=args.at, through=args.through, write=write_json, width=width, height=height,
                districts=count, matrix_targets=targets, capture_placement=True)
            watch.attach(session.owner, modules)
            # Passive district events join actual foundations to selector data.
            for name in ('planning_observer.lua', 'district_adjacency_watch.lua'):
                raw = controller.cmd(read(HERE/name), 'PlotInfo' if name.startswith('district_') else 'CSC_AI_BakersGameplay', name)
                (out/(name+'.txt')).write_text(raw, encoding='utf-8')
            watch.window(args.at, args.through)
            controller.play(args.through)
            watch.drain()
            survey('endpoint-survey')
        state = controller.state_read('customer-signal-final-clock')
        require(state['turn'] == args.through and not state['active'], 'Wrong diagnostic endpoint')
        write_json(out/'complete.json', dict(verified=True, reached=args.through, amount=args.amount))
    except Exception as error:
        write_json(out/'failure.json', dict(error=str(error), traceback=traceback.format_exc()))
        raise
    finally:
        if session.owner is not None and session.owner.poll() is None:
            session.close(restore_preferences=lambda: restore_preferences(controller, out), restore_package=verify,
                before_menu=lambda: watch.freeze() if watch else None,
                after_native_exit=lambda: watch.after_exit() if watch else None)
        if session.closed:
            for item in copied: item['install'].rename(out/item['install'].name)
            for name in LOGS:
                p = plan.user_root/'Logs'/name
                if p.is_file(): shutil.copyfile(p, out/name)
    if watch: watch.qualify()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ('source', 'output', 'dependencies'): parser.add_argument('--'+key, type=Path, required=True)
    for key in ('at', 'through', 'amount'): parser.add_argument('--'+key, type=int, required=True)
    parser.add_argument('--target', nargs=2, type=int, action='append', required=True, metavar=('PLAYER', 'CITY'))
    run(parser.parse_args())
