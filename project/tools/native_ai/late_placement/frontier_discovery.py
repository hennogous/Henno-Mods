"""Read-only frontier discovery in pinned existing worlds, using one shared owner.

No autoplay or score treatment. Current production scanner/publisher replace
only their two files in a frozen, verified CSC carrier. This keeps unrelated
worktree gameplay/art edits out of the saved-world discovery.
"""
import argparse
import json
import re
from pathlib import Path
import shutil
import traceback
from types import SimpleNamespace

from nicopolis_replay import CE_SHA, DLL, HOTFIX_EXE_SHA, SCANNER
from ce_bakers_fresh import package_identity
from ce_replay import verify_modules
from driver import (HERE, HOTFIX_SHA, HeldProcess, NativeSession, configure, flags,
    launch, load, make_probe_controller, manifest, native_inventory, parse, read,
    restore_preferences, sha, write_json, lua)


def ui_readback(controller, case, state):
    # Gameplay and UI expose different subsets of the API. Query the same
    # proposed buyer/plot pairs in UI as well; absence in Gameplay is never
    # interpreted as a zero quote. CanStartCommand is a read-only query.
    keys = sorted({(row['player'],row['city'],row['plot']) for group in ('sites','supplierLeads')
        for row in state[group]})
    scope = dict(plots=[dict(player=p,city=c,plot=t) for p,c,t in keys],
        players=[row['player'] for row in state['players']],
        cities=[dict(player=r['player'],city=r['city']) for r in state.get('cityStates',[])])
    code = 'local scope=' + lua(scope) + '''
local function safe(object,name,...)
 if not object or type(object[name])~='function' then return nil end
 local ok,value=pcall(object[name],object,...);if ok then return value end
end
for _,r in ipairs(scope.plots) do
 local city=assert(CityManager.GetCity(r.player,r.city))
 local plot=assert(Map.GetPlotByIndex(r.plot))
 local quote=safe(safe(city,'GetGold'),'GetPlotPurchaseCost',r.plot)
 local args={}
 args[CityCommandTypes.PARAM_PLOT_PURCHASE]=true
 args[CityCommandTypes.PARAM_X]=plot:GetX();args[CityCommandTypes.PARAM_Y]=plot:GetY()
 local ok,eligible=pcall(CityManager.CanStartCommand,city,CityCommandTypes.PURCHASE,false,args,true)
 print('CSC_FRONTIER_UI_QUOTE',r.player,r.city,r.plot,tostring(quote),ok and tostring(eligible) or 'unknown')
end
for _,pid in ipairs(scope.players) do
 local t=assert(Players[pid]):GetTreasury()
 print('CSC_FRONTIER_UI_ECONOMY',pid,t:GetGoldBalance(),tostring(safe(t,'GetGoldYield')),tostring(safe(t,'GetTotalMaintenance')))
end
for _,r in ipairs(scope.cities) do
 local c=assert(CityManager.GetCity(r.player,r.city));local d=c:GetDistricts()
 print('CSC_FRONTIER_UI_CITY',r.player,r.city,tostring(safe(d,'GetNumAllowedDistrictsRequiringPopulation')),
  tostring(safe(d,'GetNumZonedDistrictsRequiringPopulation')),c:GetPopulation())
end
print('CSC_FRONTIER_UI_END',Game.GetCurrentGameTurn(),#scope.plots,#scope.players,#scope.cities)
'''
    (case/'ui-readback.lua').write_text(code,encoding='utf-8')
    raw=controller.cmd(code,'PlotInfo','frontier-ui-' + case.name)
    (case/'ui-readback.txt').write_text(raw,encoding='utf-8')
    quotes=re.findall(r'CSC_FRONTIER_UI_QUOTE\t(\d+)\t(\d+)\t(\d+)\t([^\t\r\n]+)\t([^\t\r\n]+)',raw)
    economies=re.findall(r'CSC_FRONTIER_UI_ECONOMY\t(\d+)\t([^\t\r\n]+)\t([^\t\r\n]+)\t([^\t\r\n]+)',raw)
    cities=re.findall(r'CSC_FRONTIER_UI_CITY\t(\d+)\t(\d+)\t([^\t\r\n]+)\t([^\t\r\n]+)\t([^\t\r\n]+)',raw)
    ends=re.findall(r'CSC_FRONTIER_UI_END\t(\d+)\t(\d+)\t(\d+)\t(\d+)',raw)
    assert ends==[(str(state['turn']),str(len(keys)),str(len(scope['players'])),str(len(scope['cities'])))], 'Incomplete UI survey'
    assert len(quotes)==len(keys) and len(economies)==len(scope['players'])
    number=lambda text:None if text=='nil' else float(text)
    # This observer-boundary query is not the native Economic consumer. A
    # false result cannot diagnose its eligibility without caller/turn checks.
    by_key={(int(p),int(c),int(t)):dict(quote=number(q),uiCanStartAtBoundary={'true':True,'false':False}.get(ok))
        for p,c,t,q,ok in quotes}
    assert sorted(by_key)==keys
    for group in ('sites','supplierLeads'):
        for row in state[group]:
            row['ui']=by_key[(row['player'],row['city'],row['plot'])]
    state['uiEconomy']=[dict(player=int(p),treasuryGold=number(g),goldYield=number(y),maintenance=number(m))
        for p,g,y,m in economies]
    by_city={(int(p),int(c)):dict(allowedDistricts=number(a),zonedDistricts=number(z),population=number(n))
        for p,c,a,z,n in cities}
    assert len(by_city)==len(scope['cities'])
    for row in state.get('cityStates',[]):row['ui']=by_city[(row['player'],row['city'])]


def run(args):
    out = args.output.resolve()
    reference = args.reference.resolve(strict=True)
    previous = args.previous_survey.resolve(strict=True)
    home, user_root = args.my_games.resolve(), args.user_root.resolve()
    assert not out.exists() and not native_inventory(), 'Fresh output and exclusive native session required'
    assert load(reference / 'complete.json')['verified'] and load(reference / 'session-closed.json')['verified']
    assert load(previous / 'complete.json')['verified'] and load(previous / 'session-closed.json')['verified']
    saves, identities = {}, {}
    for name in args.case:
        meta = load(args.worlds / name / 'checkpoint.json')
        source = Path(meta['native_save']).resolve(strict=True)
        assert meta['verified'] and meta['turn'] == 200
        assert source.parent == (home / 'Saves/Single').resolve() and source.suffix == '.Civ6Save'
        assert sha(source) == sha(args.worlds / name / 'endpoint.Civ6Save') == meta['sha256']
        prior = load(previous / (name + '.json'))
        assert prior['save_sha256'] == meta['sha256']
        saves[name] = dict(path=str(source), sha256=meta['sha256'])
        # Independent source-city/owned-plot checks prevent a same-turn load
        # receipt from accidentally qualifying a different saved world.
        selected, seen = [], set()
        for row in prior['sites']:
            key = (int(row[0]), int(row[1]))
            if key not in seen:
                selected.append(dict(player=key[0], city=key[1], name=row[2], plot=int(row[5])))
                seen.add(key)
            if len(selected) == 2:
                break
        assert len(selected) == 2
        identities[name] = selected
    packages = {reference / name: home / 'Mods' / name for name in
        ('CSC Bakers Development CE', 'CSC Bakers Development Mod')}
    assert not any(path.exists() for path in packages.values())
    ce, csc = packages
    ce_id, _ = package_identity(ce)
    csc_id, _ = package_identity(csc)
    ce_relative = Path('Binaries/Win64') / DLL
    assert sha(ce / ce_relative) == CE_SHA
    binary = Path(load(reference / 'launch-bootstrap.json')['binary'])
    assert sha(binary) == HOTFIX_EXE_SHA
    replacements = {relative: (args.policy_root / relative).read_bytes() for relative in
        (SCANNER, Path('Lua_UI/AI/CSC_AI_BakersGameplay.lua'))}
    pins = {source: manifest(source) for source in packages}
    import hashlib
    for relative, data in replacements.items():
        pins[csc][str(relative)] = dict(size=len(data), sha256=hashlib.sha256(data).hexdigest())
    out.mkdir(parents=True)
    write_json(out / 'inputs.json', dict(saves=saves, identities=identities, ce_sha256=CE_SHA,
        require_model=args.require_model,
        packages={source.name: pin for source,pin in pins.items()}))
    shutil.copyfile(Path(__file__), out / Path(__file__).name)
    shutil.copyfile(HERE / 'frontier_site_survey.lua', out / 'frontier_site_survey.lua')
    controller = make_probe_controller(out, user_root=user_root)
    controller.study_endpoint = 200
    session = NativeSession(out,controller,inventory=native_inventory,hold=HeldProcess,write=write_json)
    installed = []

    def verify():
        assert all(manifest(packages[source]) == pins[source] for source in installed)

    try:
        for source,destination in packages.items():
            shutil.copytree(source,destination)
            installed.append(source)
        for relative,data in replacements.items():
            (packages[csc] / relative).write_bytes(data)
            (out / relative.name).write_bytes(data)
        verify()
        session.start(lambda: launch(SimpleNamespace(binary=binary),out))
        session.wait_context('MainMenu')
        configure(controller,out,csc_id=ce_id)
        session.issue_once('enable-csc', f"""
local selected
for _,m in ipairs(Modding.GetInstalledMods()) do
 if m.Id=='{csc_id}' then assert(not selected);selected=m end
end
assert(selected and Modding.CanEnableMod(selected.Handle)=='OK')
Modding.EnableMod(selected.Handle,true)
""", 'MainMenu')
        assert {key for key,value in flags(controller,'verify-pair')['mods'].items() if value} == {ce_id,csc_id}
        for index,name in enumerate(args.case):
            case = out / 'cases' / name
            case.mkdir(parents=True)
            source = saves[name]
            assert sha(source['path']) == source['sha256']
            write_json(case / 'load-input.json',source)
            session.issue_once('load-' + name,
                'Automation.SetAutoStartEnabled(true);Network.LoadGame(' + json.dumps(source['path'])
                + ',ServerType.SERVER_TYPE_NONE);', 'MainMenu')

            def ready():
                verify()
                verify_modules(session,(packages[ce] / ce_relative).resolve(),case,HOTFIX_SHA)
                checks = []
                for identity in identities[name]:
                    checks.append(f"""
do
 local c=assert(CityManager.GetCity({identity['player']},{identity['city']}))
 assert(c:GetName()=={json.dumps(identity['name'])},'Loaded city identity differs')
 local p=assert(Map.GetPlotByIndex({identity['plot']}))
 local owner=assert(Cities.GetPlotPurchaseCity(p))
 assert(p:GetOwner()=={identity['player']} and owner:GetID()==c:GetID(),'Loaded source ownership differs')
end
""")
                raw=controller.cmd('\n'.join(checks)+read(out/'frontier_site_survey.lua'),
                    'CSC_AI_BakersGameplay','frontier-survey-' + name)
                state=parse(raw,'CSC_FRONTIER_SURVEY')
                assert state['turn']==200 and state['mutationCommands']==0 and state['players']
                assert not args.require_model or state['modelAvailable'], 'Shared production model unavailable'
                assert not args.require_model or state['typeFilterAvailable'], 'Future district eligibility unavailable'
                assert all(row['supply']['base'] for row in state['sites'])
                write_json(case / 'gameplay-survey.json',state)
                ui_readback(controller,case,state)
                write_json(case / 'survey.json',state)
                return True

            session.ready_after_issue(200,('GameCore_Tuner','PlotInfo','CSC_AI_BakersGameplay'),eligibility=ready)
            shutil.copyfile(out/'session-source-ready.json',case/'source-ready.json')
            print('Frontier survey complete',name,flush=True)
            if index + 1 < len(args.case):
                session.issue_once('menu-' + name,'Events.ExitToMainMenu();','PlotInfo')
                session.wait_context('MainMenu',180)
    except Exception as error:
        write_json(out/'failure.json',dict(error=str(error),traceback=traceback.format_exc()))
        raise
    finally:
        if session.owner is not None and session.owner.poll() is None:
            session.close(restore_preferences=lambda:restore_preferences(controller,out)
                if (out/'original-preferences.json').exists() else None,restore_package=verify)
        if session.closed:
            for source in installed:
                packages[source].rename(out/source.name)
    assert session.closed
    write_json(out/'complete.json',dict(verified=True,turns_advanced=0,cases=args.case))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('output','reference','previous-survey','worlds','my-games','user-root','policy-root'):
        parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--case',action='append',choices=('run-v3-continents','baseline-pangaea','baseline-fractal'))
    parser.add_argument('--require-model',action='store_true',help='Require the shared read-only production adjacency calculator')
    args=parser.parse_args()
    args.case=args.case or ['run-v3-continents','baseline-pangaea','baseline-fractal']
    assert len(args.case)==len(set(args.case))
    run(args)
