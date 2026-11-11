"""Read-only frontier discovery in pinned existing worlds, using one shared owner.

Default mode advances no turns. The explicit owned comparison follows the
pinned Continents world to 202, then compares two cities' frontier and owned
options. Production scanner/publisher/quote bridge replace only those files
in a verified carrier; the diagnostic survey publishes no score treatment.
The explicit Boston arms instead compare the current integrated material
preference with its one-pair ablation and retain native follow-through receipts.
"""
import argparse
import json
import re
from pathlib import Path
import shutil
import traceback
import xml.etree.ElementTree as ET
from types import SimpleNamespace

from nicopolis_replay import CE_SHA, DLL, HOTFIX_EXE_SHA, SCANNER, QUOTE_BRIDGE, CASES, qualify_integrated_policy
from ce_bakers_fresh import package_identity
from ce_replay import verify_modules
from boston_material_policy import provenance as boston_provenance, stage as stage_boston_policy, PREPARE_SPECIALTY
from driver import (HERE, HOTFIX_SHA, HeldProcess, NativeSession, configure, flags,
    launch, load, make_probe_controller, manifest, native_inventory, parse, read,
    restore_preferences, sha, write_json, lua)
from full_game_controller.checkpoint import save_inactive_boundary


def ui_readback(controller, case, state):
    # Gameplay and UI expose different subsets of the API. Query the same
    # proposed buyer/plot pairs in UI as well; absence in Gameplay is never
    # interpreted as a zero quote. CanStartCommand is a read-only query.
    keys = sorted({(row['player'],row['city'],row['plot']) for group in ('sites','supplierLeads')
        for row in state[group]})
    scope = dict(plots=[dict(player=p,city=c,plot=t) for p,c,t in keys],
        players=[row['player'] for row in state['players']],
        cities=[dict(player=r['player'],city=r['city']) for r in state.get('cityStates',[])],
        buyerPlots=state.get('buyerPlots',[]))
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
for _,r in ipairs(scope.buyerPlots) do
 for _,city in Players[r.player]:GetCities():Members() do
  local quote=safe(safe(city,'GetGold'),'GetPlotPurchaseCost',r.plot)
  print('CSC_COMPARISON_BUYER_QUOTE',r.player,r.plot,city:GetID(),tostring(quote))
 end
end
print('CSC_FRONTIER_UI_END',Game.GetCurrentGameTurn(),#scope.plots,#scope.players,#scope.cities)
'''
    (case/'ui-readback.lua').write_text(code,encoding='utf-8')
    raw=controller.cmd(code,'PlotInfo','frontier-ui-' + case.name)
    (case/'ui-readback.txt').write_text(raw,encoding='utf-8')
    quotes=re.findall(r'CSC_FRONTIER_UI_QUOTE\t(\d+)\t(\d+)\t(\d+)\t([^\t\r\n]+)\t([^\t\r\n]+)',raw)
    economies=re.findall(r'CSC_FRONTIER_UI_ECONOMY\t(\d+)\t([^\t\r\n]+)\t([^\t\r\n]+)\t([^\t\r\n]+)',raw)
    cities=re.findall(r'CSC_FRONTIER_UI_CITY\t(\d+)\t(\d+)\t([^\t\r\n]+)\t([^\t\r\n]+)\t([^\t\r\n]+)',raw)
    buyers=re.findall(r'CSC_COMPARISON_BUYER_QUOTE\t(\d+)\t(\d+)\t(\d+)\t([^\t\r\n]+)',raw)
    ends=re.findall(r'CSC_FRONTIER_UI_END\t(\d+)\t(\d+)\t(\d+)\t(\d+)',raw)
    assert ends==[(str(state['turn']),str(len(keys)),str(len(scope['players'])),str(len(scope['cities'])))], 'Incomplete UI survey'
    assert len(quotes)==len(keys) and len(economies)==len(scope['players'])
    number=lambda text:None if text=='nil' else float(text)
    state['buyerQuotes']=[dict(player=int(pid),plot=int(plot),city=int(city),quote=number(quote))
        for pid,plot,city,quote in buyers]
    # A unique positive quote is meaningful only after every current city
    # has answered once. Missing or unreadable competing buyers stay unknown.
    expected_buyers={(target['player'],target['plot'],city['city'])
        for target in scope['buyerPlots'] for city in state.get('cityStates',[])
        if city['player']==target['player']}
    actual_buyers=[(row['player'],row['plot'],row['city']) for row in state['buyerQuotes']]
    assert len(actual_buyers)==len(expected_buyers) and set(actual_buyers)==expected_buyers \
        and all(row['quote'] is not None for row in state['buyerQuotes']), 'Incomplete all-city comparison quotes'
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
    boston = args.case == ['boston-selection']
    boston_arm=getattr(args,'boston_arm',None)
    prepare_specialty=getattr(args,'boston_prepare_specialty',False)
    prepared=getattr(args,'boston_prepared',None)
    assert not boston_arm or boston and 23<=args.through<=40
    assert not prepare_specialty or boston and not boston_arm and not prepared
    assert not prepared or boston and boston_arm and not prepare_specialty
    assert not out.exists() and not native_inventory(), 'Fresh output and exclusive native session required'
    assert load(reference / 'complete.json')['verified'] and load(reference / 'session-closed.json')['verified']
    assert load(previous / 'complete.json')['verified'] and load(previous / 'session-closed.json')['verified']
    saves, identities = {}, {}
    for name in args.case:
        if boston:
            # Known native decision window, not a fresh world search. Its old
            # gap-derived pulse is NOT reused. Survey the current main model
            # without publishing a diagnostic score or advancing the save.
            meta=load(args.worlds/'matched-02/discovery/search-result.json')['checkpoint']
            assert meta['verified'] and meta['turn']==22 and meta['sha256']== \
                '9675be27c614a2429a9cdca485a09a8d7421e627cc7833cb472bb9b1c390f55a'
            archive=Path(meta['archive']).resolve(strict=True)
            assert sha(archive)==meta['sha256']
            source=Path(meta['native_save']).resolve()
            assert source.parent==(home/'Saves/Single').resolve()
            if not source.exists():
                with archive.open('rb') as old,source.open('xb') as restored:
                    shutil.copyfileobj(old,restored)
            assert sha(source)==meta['sha256']
            saves[name]=dict(path=str(source),sha256=meta['sha256'],turn=22)
            if prepared:
                # Both arms reopen the SAME saved derivative, never replay
                # resource/ownership edits separately. These are fixture edits,
                # not native acquisition or shipping CSC map intervention.
                assert load(prepared/'complete.json')['verified']
                assert load(prepared/'session-closed.json')['verified']
                evidence=load(prepared/'specialty-preparation.json')
                assert evidence['original_save_sha256']==meta['sha256']
                assert evidence['edits']==[dict(plot=722,owner=3,city=131073),
                    dict(plot=722,resource='RESOURCE_SUGAR')]
                assert evidence['policy_delta_q8']==12288 and evidence['adjacency']==4
                checkpoint=load(prepared/'prepared-checkpoint.json')
                source=Path(checkpoint['native_save']).resolve(strict=True)
                assert checkpoint['verified'] and checkpoint['turn']==22
                assert source.parent==(home/'Saves/Single').resolve()
                assert sha(source)==sha(Path(checkpoint['archive']))==checkpoint['sha256']
                saves[name]=dict(path=str(source),sha256=checkpoint['sha256'],turn=22)
            identities[name]=[dict(player=3,city=131073,name='LOC_CITY_NAME_BOSTON',plot=721)]
            continue
        meta = load(args.worlds / name / 'checkpoint.json')
        source = Path(meta['native_save']).resolve(strict=True)
        assert meta['verified'] and meta['turn'] == 200
        assert source.parent == (home / 'Saves/Single').resolve() and source.suffix == '.Civ6Save'
        assert sha(source) == sha(args.worlds / name / 'endpoint.Civ6Save') == meta['sha256']
        prior = load(previous / (name + '.json'))
        assert prior['save_sha256'] == meta['sha256']
        saves[name] = dict(path=str(source), sha256=meta['sha256'],turn=200)
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
    compare_owned=getattr(args,'compare_owned',False)
    assert not compare_owned or args.case==['run-v3-continents'],'Owned comparison is pinned to the Continents fixture'
    replacements = {relative: (args.policy_root / relative).read_bytes() for relative in
        (SCANNER, Path('Lua_UI/AI/CSC_AI_BakersGameplay.lua'),QUOTE_BRIDGE)}
    role_provenance=None
    if boston_arm or prepare_specialty:
        # Reproduce the actual current reusable modules, not just a new
        # scanner calling a historical policy helper in the carrier.
        for filename in ('CSC_AI_QuarterPlacement.lua','CSC_AI_DistrictBridge.lua'):
            relative=Path('Lua_UI/AI')/filename
            replacements[relative]=(args.policy_root/relative).read_bytes()
        role_provenance=boston_provenance(args.worlds)
        if boston_arm:
            relative=Path('Lua_UI/AI/CSC_AI_BakersGameplay.lua')
            replacements[relative]=stage_boston_policy(replacements[relative],boston_arm,args.through,
                expected_delta=12288 if prepared else 6144)
    if boston:
        # Match this older save's CSC identity while keeping the verified
        # carrier's gameplay content identical across future matched arms.
        # Native values must be observed afresh; old published scores are
        # historical, not assertions about this newer content carrier.
        metadata,=csc.glob('*.modinfo')
        relative=metadata.relative_to(csc)
        data=metadata.read_bytes()
        csc_id='d0f3a2ab-4fa6-4a7a-bf9b-b82a66fe2a09'
        replacements[relative],changed=re.subn(rb'(<Mod\b[^>]*\bid=")[^"]+("[^>]*>)',
            lambda match:match[1]+csc_id.encode()+match[2],data,count=1)
        assert changed==1
        # The old save activates only recorded mods, so the separate new CE
        # package is not selected as its GameCore carrier. Use the documented
        # add_fixture_carrier pattern inside this diagnostic copy of CSC.
        # Order11 follows CE's order10 configuration deterministically. The
        # shipping CSC and both original package sources stay untouched.
        root=ET.fromstring(replacements[relative])
        config=Path('Data/CE_Boston_Compatibility_Config.sql')
        proxy=Path('Binaries/Win64')/DLL
        action=ET.SubElement(root.find('FrontEndActions'),'UpdateDatabase',id='CE_Boston_Compatibility')
        ET.SubElement(ET.SubElement(action,'Properties'),'LoadOrder').text='11'
        ET.SubElement(action,'File').text=config.as_posix()
        for file in (config,proxy):ET.SubElement(root.find('Files'),'File').text=file.as_posix()
        replacements[relative]=ET.tostring(root,encoding='utf-8',xml_declaration=True)
        replacements[config]=(f"UPDATE GameCores SET PackageId='{csc_id}', DllPrefix='GameCore_XP2_CE_AI' "
            "WHERE GameCore='Expansion2';\n").encode()
        replacements[proxy]=(ce/ce_relative).read_bytes()
    pins = {source: manifest(source) for source in packages}
    import hashlib
    for relative, data in replacements.items():
        pins[csc][str(relative)] = dict(size=len(data), sha256=hashlib.sha256(data).hexdigest())
    out.mkdir(parents=True)
    write_json(out / 'inputs.json', dict(saves=saves, identities=identities, ce_sha256=CE_SHA,
        require_model=args.require_model,compare_owned=compare_owned,boston_arm=boston_arm,
        through=args.through if boston_arm else None,role_provenance=role_provenance,
        prepare_specialty=prepare_specialty,prepared_source=str(prepared) if prepared else None,
        packages={source.name: pin for source,pin in pins.items()}))
    shutil.copyfile(Path(__file__), out / Path(__file__).name)
    shutil.copyfile(HERE / 'frontier_site_survey.lua', out / 'frontier_site_survey.lua')
    if boston:shutil.copyfile(HERE/'quarter_site_survey.lua',out/'quarter_site_survey.lua')
    if boston_arm or prepare_specialty:shutil.copyfile(HERE/'boston_material_policy.py',out/'boston_material_policy.py')
    controller = make_probe_controller(out, user_root=user_root)
    controller.study_endpoint = 22 if boston else 200
    session = NativeSession(out,controller,inventory=native_inventory,hold=HeldProcess,write=write_json)
    installed = []

    def verify():
        assert all(manifest(packages[source]) == pins[source] for source in installed)

    try:
        for source,destination in packages.items():
            shutil.copytree(source,destination)
            installed.append(source)
        for relative,data in replacements.items():
            target=packages[csc]/relative
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(data)
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
                carrier=packages[csc] if boston else packages[ce]
                verify_modules(session,(carrier / ce_relative).resolve(),case,HOTFIX_SHA)
                if prepare_specialty:
                    raw=session.issue_once('prepare-boston-specialty',PREPARE_SPECIALTY,'CSC_AI_BakersGameplay')
                    (case/'specialty-preparation.txt').write_text(raw,encoding='utf-8')
                    assert 'CSC_MATERIAL_PREPARED\t722\tRESOURCE_SUGAR\t3\t131073\t2' in raw
                if prepared:
                    # Assert persisted facts after reload, in addition to the
                    # host's saved-byte hashes, before qualifying publication.
                    session.issue_once('verify-prepared-boston','''
local p=assert(Map.GetPlotByIndex(722))
assert(p:GetOwner()==3 and Cities.GetPlotPurchaseCity(p):GetID()==131073)
assert(p:GetResourceType()==GameInfo.Resources.RESOURCE_SUGAR.Index)
assert(p:GetDistrictType()==-1 and p:GetImprovementType()==-1)
''','CSC_AI_BakersGameplay')
                if boston_arm:
                    qualify_integrated_policy(controller,case,dict(player=3,city=131073,
                        district=36,profile='BAKERS',purchasePlots=[721]))
                    receipt=load(case/'policy-qualification.json')['targetReceipt']
                    assert receipt and receipt['staged']==(0 if boston_arm=='control' else 1), \
                        'Expected initial Boston target staging/ablation is absent'
                    raw=controller.cmd('CSC_MATERIAL_DIAG_Snapshot(true)',
                        'CSC_AI_BakersGameplay','boston-initial-receipt')
                    (case/'initial-receipt.txt').write_text(raw,encoding='utf-8')
                if compare_owned:
                    qualify_integrated_policy(controller,case,CASES['nicopolis'])
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
                prefix='CSC_FRONTIER_COMPARISON='+lua({3:{131073:True}})+'\n' if boston else ''
                raw=controller.cmd('\n'.join(checks)+prefix+read(out/'frontier_site_survey.lua'),
                    'CSC_AI_BakersGameplay','frontier-survey-' + name)
                state=parse(raw,'CSC_FRONTIER_SURVEY')
                assert state['turn']==source['turn'] and state['mutationCommands']==0 and state['players']
                assert not args.require_model or state['modelAvailable'], 'Shared production model unavailable'
                assert not args.require_model or state['typeFilterAvailable'], 'Future district eligibility unavailable'
                assert all(row['supply']['base'] for row in state['sites'])
                write_json(case / 'gameplay-survey.json',state)
                ui_readback(controller,case,state)
                write_json(case / 'survey.json',state)
                if boston:
                    # Read only the six neighboring plots before designing a
                    # controlled material fixture. A resource on the sole future
                    # customer footprint can trade one benefit for another;
                    # CanHaveResource supplies native map suitability, not an
                    # instruction to create a resource or change ownership.
                    raw=controller.cmd('''
local site=assert(Map.GetPlotByIndex(721))
for _,plot in ipairs(Map.GetAdjacentPlots(site:GetX(),site:GetY())) do
 local owner=Cities.GetPlotPurchaseCity(plot)
 local terrain=GameInfo.Terrains[plot:GetTerrainType()]
 local feature=GameInfo.Features[plot:GetFeatureType()]
 print('CSC_MATERIAL_NEIGHBOR',plot:GetIndex(),plot:GetOwner(),owner and owner:GetID() or -1,
  terrain and terrain.TerrainType or '-',feature and feature.FeatureType or '-',
  plot:GetDistrictType(),plot:GetResourceType(),plot:GetImprovementType(),
  PlayersVisibility[3]:IsRevealed(plot:GetX(),plot:GetY()))
 for resource in GameInfo.Resources()do
  if CSC_Adjacency.HasTag('CLASS_CSC_BAKERS_SPEC',resource.ResourceType)then
   print('CSC_MATERIAL_RESOURCE_POTENTIAL',plot:GetIndex(),resource.ResourceType,
    ResourceBuilder.CanHaveResource(plot,resource.Index))
  end
 end
end
''','CSC_AI_BakersGameplay','boston-neighbor-geometry')
                    (case/'neighbor-geometry.txt').write_text(raw,encoding='utf-8')
                    raw=controller.cmd('CSC_QUARTER_SURVEY_PLAYERS={3};\n'+read(out/'quarter_site_survey.lua'),
                        'CSC_AI_BakersGameplay','boston-current-policy-offers')
                    (case/'actual-policy-survey.txt').write_text(raw,encoding='utf-8')
                    if prepare_specialty:
                        # Do not assume the new material buys a stronger band:
                        # the unchanged main model and retained host must show it.
                        assert re.search(r'CSC_QUARTER_SURVEY_SITE\t3\t131073\tLOC_CITY_NAME_BOSTON\tBAKERS\t36\t721\t12288\t4\t',raw)
                        target=next(r for r in state['sites'] if r['player']==3
                            and r['city']==131073 and r['profile']=='BAKERS' and r['plot']==721)
                        assert any(h['plot']==720 for h in target['futureHosts'])
                        assert any(s['plot']==722 for s in target['supply']['specialty'])
                        checkpoint=save_inactive_boundary(controller,turn=22,name='CSC_BOSTON_MATERIAL_STRONG',
                            native_directory=home/'Saves/Single',archive=out/'prepared.Civ6Save')
                        write_json(out/'prepared-checkpoint.json',checkpoint)
                        write_json(out/'specialty-preparation.json',dict(
                            original_save_sha256=source['sha256'],
                            edits=[dict(plot=722,owner=3,city=131073),dict(plot=722,resource='RESOURCE_SUGAR')],
                            policy_delta_q8=12288,adjacency=4,proof='cases/boston-selection/specialty-preparation.txt'))
                return True

            session.ready_after_issue(source['turn'],('GameCore_Tuner','PlotInfo','CSC_AI_BakersGameplay'),eligibility=ready)
            shutil.copyfile(out/'session-source-ready.json',case/'source-ready.json')
            print('Frontier survey complete',name,flush=True)
            if boston_arm:
                controller.study_endpoint=args.through
                controller.play(args.through)
                state=controller.state_read('boston-material-endpoint')
                assert state['turn']==args.through and not state['active']
                raw=controller.cmd('CSC_MATERIAL_DIAG_Snapshot(true)',
                    'CSC_AI_BakersGameplay','boston-terminal-receipt')
                (case/'terminal-receipt.txt').write_text(raw,encoding='utf-8')
                for log in ('Lua.log','AI_CityBuild.csv','AI_Behavior_Trees.csv','City_BuildQueue.csv'):
                    shutil.copyfile(user_root/'Logs'/log,out/log)
                logs=read(out/'Lua.log')
                for failure in ('CSC_MATERIAL_DIAG_FAILED','CSC_AI_BAKERS_DISTRICTS_FAILED',
                        'CSC_AI_INDUSTRY_PLACEMENT_FAILED'):
                    assert failure not in logs,'Policy/diagnostic failure: '+failure
                print('Boston material arm complete',boston_arm,args.through,flush=True)
            if compare_owned:
                # Nuremberg is founded naturally on 201. Pause at 202 rather
                # than inventing it in the source. Native AI and main CSC run
                # during these two turns; this is not a zero-turn survey.
                controller.study_endpoint=202
                controller.play(202)
                boundary=controller.state_read('comparison-boundary')
                assert boundary['turn']==202 and not boundary['active']
                comparison=case/'owned-comparison-202'
                comparison.mkdir()
                prefix='CSC_FRONTIER_COMPARISON='+lua({3:{393221:True,458758:True}})+'\n'
                raw=controller.cmd(prefix+read(out/'frontier_site_survey.lua'),
                    'CSC_AI_BakersGameplay','owned-frontier-comparison-202')
                (comparison/'gameplay-survey.txt').write_text(raw,encoding='utf-8')
                state=parse(raw,'CSC_FRONTIER_SURVEY')
                write_json(comparison/'gameplay-survey.json',state)
                assert state['turn']==202 and state['mutationCommands']==0
                cities={r['city']:r for r in state['cityStates'] if r['player']==3}
                assert cities[393221]['name']=='LOC_CITY_NAME_HAMBURG'
                assert cities[458758]['name']=='LOC_CITY_NAME_NUREMBERG'
                state['buyerPlots']=[dict(player=3,plot=index) for index in (862,1011)]
                ui_readback(controller,comparison,state)
                write_json(comparison/'survey.json',state)
                for log in ('Lua.log','AI_CityBuild.csv','AI_Behavior_Trees.csv'):
                    shutil.copyfile(user_root/'Logs'/log,out/log)
                print('Owned/frontier comparison complete at202',flush=True)
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
    advanced=args.through-22 if boston_arm else 2 if compare_owned else 0
    write_json(out/'complete.json',dict(verified=True,turns_advanced=advanced,cases=args.case))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('output','reference','previous-survey','worlds','my-games','user-root','policy-root'):
        parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--case',action='append',choices=('run-v3-continents','baseline-pangaea','baseline-fractal','boston-selection'))
    parser.add_argument('--require-model',action='store_true',help='Require the shared read-only production adjacency calculator')
    parser.add_argument('--compare-owned',action='store_true',
        help='Continents only: advance naturally to202 and inspect Nuremberg/Hamburg owned alternatives')
    parser.add_argument('--boston-arm',choices=('control','treatment'),
        help='Matched Boston material preference: control removes only its retained positive offer')
    parser.add_argument('--through',type=int,default=33)
    parser.add_argument('--boston-prepare-specialty',action='store_true',
        help='Diagnostic only: prepare and save one terrain-valid Sugar722/ownership derivative; advance zero turns')
    parser.add_argument('--boston-prepared',type=Path,
        help='Matched arms only: reopen the exact verified strong-material derivative directory')
    args=parser.parse_args()
    args.case=args.case or ['run-v3-continents','baseline-pangaea','baseline-fractal']
    assert len(args.case)==len(set(args.case))
    if 'boston-selection' in args.case and args.case!=['boston-selection']:
        parser.error('Boston requires its own source window')
    if args.boston_arm and (args.case!=['boston-selection'] or args.compare_owned):
        parser.error('Boston arms require the single Boston source and no Continents comparison')
    run(args)
