"""Replay CSC stock, ordinary-database guidance and advanced planning on shared starts."""
import argparse
from contextlib import closing
import gzip
import hashlib
import json
from pathlib import Path
import re
import shutil
import sqlite3
from types import SimpleNamespace
import xml.etree.ElementTree as ET

from ce_replay import DLL, verify_modules
from driver import (HERE, HeldProcess, NativeSession, launch, load, lua, make_probe_controller,
                    native_inventory, read, require, restore_preferences, sha, write_json)
from economy_factorial import read_opening, select_stack
from economy_guidance_timing import install_clocks, observed_turns
from full_game_controller.checkpoint import (SaveFileUnavailable, SavePermissionUnavailable,
                                            archive_autosave_window, save_inactive_boundary)
from full_game_controller.controller import ObserverEliminated
from full_game_observation import archive_censuses
from mature_guidance_replay import replace
from shortlist_pair import prepare


def stock_controls(database):
    """Read Firaxis's gameplay export after load, before the next game replaces it."""
    with closing(sqlite3.connect(database.resolve().as_uri()+'?mode=ro',uri=True)) as db:
        return dict(
            builder_priority=db.execute("""SELECT Favored,Value FROM AiFavoredItems
                WHERE ListType='UnitPriorityBoosts' AND Item='UNIT_BUILDER'""").fetchall(),
            recruiting_city=db.execute("""SELECT n.NodeId,t.DefaultData FROM BehaviorTreeNodes n
                LEFT JOIN TreeData t ON t.TreeName=n.TreeName AND t.NodeId=n.NodeId AND t.DefnId=2
                WHERE n.TreeName='Build City Improvement' AND n.NodeType='Build Unit'
                ORDER BY n.NodeId""").fetchall(),
            placements=db.execute("""SELECT d.DistrictType,a.AdjacentDistrict,a.AdjacentImprovement,
                a.YieldChange,a.TilesRequired,a.AdjacentResourceClass FROM District_Adjacencies d
                JOIN Adjacency_YieldChanges a ON a.ID=d.YieldChangeId
                WHERE a.YieldType='YIELD_CSC_AI_PLACEMENT' ORDER BY d.DistrictType,a.ID""").fetchall())


def record_opening_geography(controller, seed_folder):
    """One stock map read per seed, before the measured turns begin."""
    target=seed_folder/'opening-map.json.gz'
    if target.exists():
        return
    source=HERE.parents[1]/'map_survey/dump.lua'
    raw=controller.cmd(read(source),'CSC_AdjacencyGameplay','record-material-geography')
    match=re.search(r'CSCMAP_SURVEY=([^\r\n]+)',raw)
    require(match is not None,'Missing opening geography')
    data=json.loads(match[1])
    require(data['turn']==1 and len(data['plots'])==data['width']*data['height'],'Incomplete opening geography')
    # A shared seed has one immutable plot layout. Keep its neighbor table
    # compressed for offline coastal-material and site audits across all arms.
    temp=target.with_suffix('.tmp')
    temp.write_bytes(gzip.compress(match[1].encode('utf-8'),mtime=0))
    temp.replace(target)


def observers(c,seats):
    # The stock arms have no advanced publisher. Load only read-only fact
    # readers in its existing Lua context for the same physical census in all arms.
    helpers="""
if not CSC_Adjacency then include('CSC_AdjacencyCore') end
CSC_Adjacency.Initialize()
if not CSC_AI_QuarterSiteForecasts then include('CSC_AI_AdjacencyScan') end
if not CSC_AI_QuarterPlacement then include('CSC_AI_QuarterPlacement') end
if not CSC_AI_DistrictBridge then include('CSC_AI_DistrictBridge') end
local CSC_LIFECYCLE_ONLY=true
"""
    context='CSC_AI_BakersGameplay'
    watched='local CSC_OBSERVE_SUPPLIER_LOSS='+lua({i:True for i in seats})+'\n'
    raw=c.cmd(watched+helpers+read(HERE/'quarter_placement_watch.lua'),context,'observe-foundations')
    require('CSC_QUARTER_WATCH_INSTALLED' in raw,'Foundation observer failed')
    raw=c.cmd('local CSC_ENDPOINT_PLAYERS='+lua(list(seats))+'''
GameEvents.OnGameTurnStarted.Add(function()
    local CSC_ENDPOINT_EXPECTED_TURN=Game.GetCurrentGameTurn()
    if CSC_ENDPOINT_EXPECTED_TURN%25~=0 then return end
    print('CSC_FULL_RUN_CENSUS_BEGIN',CSC_ENDPOINT_EXPECTED_TURN)
'''+read(HERE/'full_game_census.lua')+"\nend)\nprint('CSC_NATIVE_CENSUS_READY')",context,'observe-quarter-census')
    require('CSC_NATIVE_CENSUS_READY' in raw,'Quarter census failed')
    raw=c.cmd('CSC_MILESTONE_INCLUDE_HANDOFFS=true\nCSC_MILESTONE_SERVICE_EVERY_TURN=true\nCSC_MILESTONE_SERVICE_PLAYERS='+
              lua({i:True for i in seats})+'\n'+read(HERE/'later_stage_service_watch.lua'),'PlotInfo','observe-service-effects')
    require('CSC_MILESTONE_SERVICE_INSTALLED' in raw,'Service observer failed')
    install_clocks(c,stock=True)


def relief_sql(weight):
    """Rebuild exactly the candidate loaded by the replay or its saved-game audit."""
    return (f"\nCREATE TEMP TABLE CSC_AI_ReliefWeight(Amount INTEGER); INSERT INTO CSC_AI_ReliefWeight VALUES ({int(weight)});\n".encode()
            +(HERE/'layout_relief_rules.sql').read_bytes())


def split_relief_sql():
    # Reuse the existing gated positive and negative rules. Each city selects
    # at most two. Equal signed weights let a rival's second terrain offset
    # its first exactly when the mixed-sign policy returns to ordinary scores.
    return (HERE/'paired_material_rules.sql').read_bytes()+b"""
UPDATE ModifierArguments SET Value=3
WHERE Name='Amount' AND ModifierId GLOB 'CSC_AI_PAIR_*__P_TERRAIN_*';
UPDATE ModifierArguments SET Value=-3
WHERE Name='Amount' AND ModifierId GLOB 'CSC_AI_PAIR_*__N_TERRAIN_*';
"""


def replay(root,seed,mode,end,label=None,ce_opening=False,deposit_cues=False,customer_buildings=False,supplier_jobs=False,
           city_cue_probe=False,local_material_cues=False,as_installed=False,no_base_city=False,probe_no_base=False,
           observe_no_base=False,paired_layout=False,river_cue=False,layout_floor=None,frontier=False,
           release_ambiguous_floor=False, record_layouts=False, split_relief=False, third_relief=False,
           vocabulary=False, probe_vocabulary=False):
    study=load(root/'study.json')
    floor_trial=layout_floor is not None
    require(not frontier or layout_floor in (6,8,10),'A frontier check needs positive site relief')
    require(not release_ambiguous_floor or frontier,'The ordinary-score fallback requires the frontier check')
    require(not record_layouts or frontier,'Layout observations need frontier geometry')
    require(not split_relief or (release_ambiguous_floor and layout_floor==6),
            'Split relief needs the six-point candidate with the ordinary-score fallback')
    require(not third_relief or split_relief,'A third term is the fallback after two smaller terrain cues')
    require(not vocabulary or (layout_floor==6 and release_ambiguous_floor and not split_relief and not record_layouts),
            'The full vocabulary is a separate city policy over the same floor')
    require(not probe_vocabulary or vocabulary,'A vocabulary readback requires the staged rules')
    release_trial=no_base_city or paired_layout or river_cue or floor_trial
    if release_trial:
        require(sum(map(bool,(no_base_city,paired_layout,river_cue,floor_trial)))==1,'Test each release overlay independently')
        require(mode=='native' and deposit_cues and label and not any((as_installed,local_material_cues,
                city_cue_probe,customer_buildings,supplier_jobs)),'Use the ordinary release for the no-Base comparison')
    require(not probe_no_base or no_base_city,'The readback needs the city treatment')
    require(not observe_no_base or (no_base_city and not probe_no_base),
            'The matched control records opportunity and leaves every district preference unchanged')
    if as_installed or release_trial:
        require(mode in ('native','advanced') and not city_cue_probe and label,
                'An installed-build check needs a separate label and a real treatment')
    pins=study['pins'];game=pins['seeds'][str(seed)]
    source=root/str(seed)/'opening'
    if mode=='prepare':
        return prepare(pins,seed,game,source,stack=('csc',))
    if mode in ('verify-off','prepare-advanced'):
        enabled=mode=='prepare-advanced'
        folder=source.parent/mode
        prepare(pins,seed,game,folder,stack=('csc','ce'),advanced_option=enabled,
                save_name=f'CSC_LIGHT_{seed}_{mode.upper()}_START')
        require(load(source/'source.json')==load(folder/'source.json'),'Seeded opening map or seats differ')
        return
    if ce_opening:
        require(mode=='advanced','Only the CE arm may need its own seeded opening')
        source=source.parent/'prepare-advanced'
    record=load(source/'checkpoint.json')
    if city_cue_probe:
        require(mode=='native' and end in (25,50) and not (deposit_cues or customer_buildings or supplier_jobs or local_material_cues),
                'The local cue probe needs its own short no-CE game')
    arm_name=label or (mode+('-deposits' if deposit_cues else '')+('-buildings' if customer_buildings else '')
                      +('-jobs' if supplier_jobs else '')+('-city-cue-probe' if city_cue_probe else '')
                      +('-local-materials' if local_material_cues else ''))
    out=source.parent/arm_name
    require(not native_inventory() and not out.exists(),'Game in use or output exists')
    out.mkdir()
    ce=mode=='advanced'
    enabled=['csc','ce'] if ce else ['csc']
    user=Path(pins['userdata']);saves=Path(pins['saves'])
    c=make_probe_controller(out,user_root=user);c.study_endpoint=end
    c.observer_warning_senders=range(1,len(game['roster']));c.autoplay_interval_seconds=2700
    c.allow_observer_warning_dismissal=c.allow_observer_first_meet_dismissal=True
    c.allow_observer_congress_review=c.allow_one_more_turn=True
    session=NativeSession(out,c,inventory=native_inventory,hold=HeldProcess,write=write_json)
    manifest=next(Path(pins['packages']['csc']['path']).glob('*.modinfo'))
    original=manifest.read_bytes()
    if as_installed or release_trial:
        # Qualify the package a player loads. Flags below describe expected
        # runtime behaviour; none may stage an experimental file in this mode.
        # Hash the SQL, settings and every AI Lua module against the checkout.
        mod_source=HERE.parents[3]/'Civ Supply Chains'
        checked=['Data/CSC_Q_ALL_AI_Connectors.sql','Settings/Settings.xml','Settings/Settings_Text.xml']
        checked.extend(p.relative_to(mod_source).as_posix() for p in sorted((mod_source/'Lua_UI/AI').glob('*.lua')))
        hashes={f:sha(mod_source/f) for f in checked}
        require(all(sha(manifest.parent/f)==digest for f,digest in hashes.items()),
                'Installed guidance differs from the source being qualified')
        actions=load(HERE.parents[3]/'project/modbuddy/CivSupplyChains.actions.json')['blocks']['inGameActions']
        connector=next(a for a in actions if a['id']=='CSC_AI_Connectors')
        release_manifest=ET.fromstring(original)
        registered={e.text.replace('\\','/') for e in release_manifest.findall('Files/File')}
        require(set(checked)<=registered,'Installed manifest is missing a qualified guidance or settings file')
        built=release_manifest.find("InGameActions/UpdateDatabase[@id='CSC_AI_Connectors']")
        require(built is not None and built.findtext('Properties/LoadOrder')==connector['properties']['LoadOrder']
                and [e.text for e in built.findall('File')]==connector['files'] and built.find('Criteria') is None,
                'Installed native connector action differs from the release source')
        write_json(out/'installed-guidance.json',dict(files=hashes,manifest=sha(manifest)))
    else:
        require(original==(root/'candidate.modinfo').read_bytes(),'Installed manifest changed before replay')
    staged_path=manifest
    active=original
    if mode=='stock':
        doc=ET.fromstring(original)
        actions=doc.find('InGameActions');connectors=actions.find("UpdateDatabase[@id='CSC_AI_Connectors']")
        require(connectors is not None,'Expected native action')
        actions.remove(connectors)
        active=ET.tostring(doc,encoding='utf-8',xml_declaration=True)
    if release_trial:
        staged_path=manifest.parent/'Data/CSC_Q_ALL_AI_Connectors.sql'
        original=staged_path.read_bytes()
        overlay='paired_material_rules.sql' if paired_layout else 'river_cue.sql' if river_cue else 'no_base_city_rules.sql'
        active=original+b'\n'+(HERE/overlay).read_bytes()
        if floor_trial and layout_floor:
            active+=relief_sql(layout_floor)
        if split_relief:
            active+=split_relief_sql()
        if vocabulary:
            active+=b'\n'+(HERE/'city_vocabulary_rules.sql').read_bytes()
            (out/'vocabulary-connectors.sql').write_bytes(active)
    elif not as_installed and (deposit_cues or customer_buildings or supplier_jobs or city_cue_probe or local_material_cues):
        require(mode in ('native','advanced'),'The stock control must keep ordinary AI')
        staged_path=manifest.parent/'Data/CSC_Q_ALL_AI_Connectors.sql'
        require(sha(staged_path)==load(root/'material-candidate.json')['full'],'Underlying connector revision changed')
        original=staged_path.read_bytes()
        active=original
        for enabled_overlay,name in [(deposit_cues,'undeveloped_material_candidate.sql'),
                                     (customer_buildings,'customer_building_candidate.sql'),
                                     (city_cue_probe,'city_material_cue_candidate.sql'),
                                     (local_material_cues,'local_material_rules.sql')]:
            if enabled_overlay:
                addition=(HERE/name).read_bytes()
                active+=b'\n'+addition
                (out/name).write_bytes(addition)
    host_path=manifest.parent/'Data/CSC_Q_ALL_MaterialHosts.sql'
    host_before=host_active=None
    if supplier_jobs and not as_installed:
        # The pinned connector action runs at 3001. CSC resolves actual supplier
        # hosts at 800010 after optional mods register their improvements.
        # Append this experimental consumer immediately after that producer.
        require(sha(host_path)==sha(HERE.parents[3]/'Civ Supply Chains/Data/CSC_Q_ALL_MaterialHosts.sql'),
                'Installed material-host reconciliation differs from the qualified source')
        host_before=host_path.read_bytes()
        job_rules=(HERE/'supplier_job_candidate.sql').read_bytes()
        host_active=host_before+b'\n'+job_rules
        (out/'supplier_job_candidate.sql').write_bytes(job_rules)
    script_path=manifest.parent/'Lua_UI/AI/CSC_AI_BakersGameplay.lua'
    script_before=script_active=None
    if (local_material_cues or no_base_city or paired_layout or floor_trial) and not as_installed:
        require(sha(script_path)==sha(HERE.parents[3]/'Civ Supply Chains/Lua_UI/AI/CSC_AI_BakersGameplay.lua'),
                'Installed gameplay entry differs from the qualified CSC entry')
        script_before=script_path.read_bytes()
        # Load at the normal CSC gameplay entry, including save/reload. This
        # treatment runs through Workshop Lua and SQL with the Firaxis core.
        scripts=('no_base_city.lua',) if no_base_city else (
            'city_material_cue_choice.lua','city_material_cue_sites.lua','local_material_guidance.lua')
        if paired_layout:
            scripts=('city_material_cue_sites.lua','paired_material_layout.lua','local_material_guidance.lua')
        if floor_trial:
            scripts=('city_material_cue_sites.lua','paired_material_layout.lua','layout_floor.lua','local_material_guidance.lua')
        parts=[read(HERE/name) for name in scripts]
        if frontier:
            parts.insert(-1,'pairPolicy.guardFrontier=true')
        if release_ambiguous_floor:
            parts.insert(-1,'pairPolicy.releaseAmbiguousFloor=true')
        if split_relief:
            parts.insert(-1,read(HERE/'split_floor_relief.lua'))
        if third_relief:
            parts.insert(-1,'pairPolicy.thirdRelief=true')
        if vocabulary:
            parts.insert(-1,read(HERE/'city_vocabulary.lua'))
        if record_layouts:
            parts.insert(-1,read(HERE/'observe_floor_geometry.lua'))
        if floor_trial:
            parts.insert(0,f'local reliefWeight={int(layout_floor)}')
        if observe_no_base:
            parts.insert(0,'local CSC_NO_BASE_OBSERVE_ONLY=true')
        script_active=('do\n'+'\n'.join(parts)+'\nend\n'+script_before.decode('utf-8-sig')).encode()
        (out/'local-gameplay.lua').write_bytes(script_active)
    write_json(out/'protocol.json',dict(seed=seed,turn=end,mode=mode,shared_save=record['sha256'],
        opening=source.name,deposit_cues=deposit_cues,customer_buildings=customer_buildings,
        supplier_jobs=supplier_jobs,city_cue_probe=city_cue_probe,local_material_cues=local_material_cues,
        paired_layout=paired_layout,river_cue=river_cue,layout_floor=layout_floor,frontier=frontier,
        release_ambiguous_floor=release_ambiguous_floor,as_installed=as_installed,no_base_city=no_base_city,probe_no_base=probe_no_base,observe_no_base=observe_no_base,
        record_layouts=record_layouts,split_relief=split_relief,third_relief=third_relief,
        vocabulary=vocabulary,probe_vocabulary=probe_vocabulary,
        gameplay_sha256=hashlib.sha256(script_active).hexdigest() if script_active else None,
        material_hosts_sha256=hashlib.sha256(host_active).hexdigest() if host_active else None,active_file=staged_path.name,
        active_sha256=hashlib.sha256(active).hexdigest()))
    eliminated = False
    try:
        if active!=original:replace(staged_path,active)
        if host_active is not None:replace(host_path,host_active)
        if script_active is not None:replace(script_path,script_active)
        session.start(lambda:launch(SimpleNamespace(binary=Path(pins['binary'])),out))
        session.wait_context('MainMenu')
        select_stack(session,out,[pins['packages'][key]['id'] for key in enabled])
        def eligible():
            return read_opening(c,out,game['roster'],csc=True,cl=False,ce=ce)
        session.load_once(record['native_save'],sha256=record['sha256'],native_directory=saves,turn=1,
            contexts=('GameCore_Tuner','PlotInfo','CSC_AI_BakersGameplay'),eligibility=eligible,timeout=600)
        require(load(source/'source.json')==load(out/'source.json'),'Map or seats differ')
        fork=Path(pins['packages']['ce']['path'])/'Binaries/Win64'/DLL if ce else None
        verify_modules(session,fork,out,pins['core_sha256'])
        code=f"local native={lua(mode!='stock')};local advanced={lua(ce)};local deposits={lua(deposit_cues)}\n"+"""
assert((GameInfo.Yields.YIELD_CSC_AI_PLACEMENT~=nil)==native)
assert((CSC_AI_EconomyAdapters~=nil)==advanced)
local edges,materialRules,depositRules=0,0,0
for r in GameInfo.District_Adjacencies() do
 if string.find(r.YieldChangeId,'CSC_AI_QUARTER_',1,true)==1 then edges=edges+1 end
 if string.find(r.YieldChangeId,'CSC_AI_SUPPLIER_',1,true)==1 then materialRules=materialRules+1 end
 if string.find(r.YieldChangeId,'CSC_AI_DEPOSIT_',1,true)==1 then depositRules=depositRules+1 end
end
assert((edges>0)==native and (materialRules>0)==native and (depositRules>0)==deposits)
print('CSC_LIGHT_MODE_OK',edges,tostring(GameConfiguration.GetValue('CSC_ADVANCED_AI_PLANNING')),materialRules,depositRules)
"""
        raw=c.cmd(code,'CSC_AI_BakersGameplay','verify-running-treatment')
        require('CSC_LIGHT_MODE_OK' in raw,'Runtime tuning mode differs')
        (out/'mode.txt').write_text(raw,encoding='utf8')
        controls=stock_controls(user/'Cache/DebugGameplay.sqlite')
        # Confirm the ordinary AI actually loaded the exact customer-building
        # list generated for this treatment before attributing results to it.
        with closing(sqlite3.connect((user/'Cache/DebugGameplay.sqlite').as_uri()+'?mode=ro',uri=True)) as db:
            controls['customer_buildings']=db.execute("""SELECT f.Item,f.Favored,f.Value
                FROM AiLists a JOIN AiFavoredItems f USING(ListType)
                WHERE a.ListType='CSC_AI_FIRST_CUSTOMER_BUILDINGS' AND a.System='Buildings'
                AND a.LeaderType='TRAIT_LEADER_MAJOR_CIV' ORDER BY f.Item""").fetchall()
            controls['supplier_jobs']=db.execute("""SELECT i.ImprovementType,r.AdjacentDistrict,r.YieldChange
                FROM Improvement_Adjacencies i JOIN Adjacency_YieldChanges r ON r.ID=i.YieldChangeId
                WHERE r.ID GLOB 'CSC_AI_SUPPLY_JOB_*' ORDER BY i.ImprovementType,r.AdjacentDistrict""").fetchall()
            if floor_trial:
                if vocabulary:
                    controls['city_switches']=db.execute("""SELECT ModifierType,COUNT(*)
                        FROM Modifiers WHERE ModifierId GLOB 'CSC_AI_VOC_*' GROUP BY ModifierType""").fetchall()
                    require(len(controls['city_switches'])==5,'Incomplete native adjacency vocabulary')
                controls['floor_weights']=db.execute("""SELECT CAST(Value AS INTEGER),COUNT(*)
                    FROM ModifierArguments WHERE Name='Amount' AND
                    (ModifierId GLOB 'CSC_AI_NO_BASE_*' OR ModifierId GLOB 'CSC_AI_PAIR_*__R_*')
                    GROUP BY CAST(Value AS INTEGER) ORDER BY 1""").fetchall()
                weights=dict(controls['floor_weights'])
                penalties=weights.pop(-1,0)
                expected={layout_floor:penalties} if layout_floor else {}
                require(penalties>0 and weights==expected,
                        'Private penalties and relief must cover the same Quarter and terrain combinations')
                if split_relief:
                    rows=db.execute("""SELECT CAST(Value AS INTEGER),COUNT(*) FROM ModifierArguments
                        WHERE Name='Amount' AND (ModifierId GLOB 'CSC_AI_PAIR_*__P_TERRAIN_*'
                        OR ModifierId GLOB 'CSC_AI_PAIR_*__N_TERRAIN_*')
                        GROUP BY CAST(Value AS INTEGER) ORDER BY 1""").fetchall()
                    require(rows==[(-3,penalties),(3,penalties)],'Both terrain signs must cover every Quarter')
        require(bool(controls['customer_buildings'])==customer_buildings,'Customer building control differs')
        require(bool(controls['supplier_jobs'])==supplier_jobs,'Supplier job control differs')
        write_json(out/'stock-controls.json',controls)
        if paired_layout or river_cue:
            with closing(sqlite3.connect((user/'Cache/DebugGameplay.sqlite').as_uri()+'?mode=ro',uri=True)) as db:
                rivers=db.execute("SELECT DistrictType FROM District_Adjacencies WHERE YieldChangeId='CSC_AI_TRIAL_RIVER'").fetchall()
                signs=db.execute("""SELECT DISTINCT CAST(Value AS INT) FROM ModifierArguments
                    WHERE ModifierId GLOB 'CSC_AI_PAIR_*' AND Name='Amount' ORDER BY 1""").fetchall()
            require(rivers==([('DISTRICT_CSC_TAILORS_QUARTER',)] if river_cue else []),'Unexpected river trial scope')
            require(signs==([(-2,),(2,)] if paired_layout else []),'Missing or unexpected signed rule definitions')
            write_json(out/'layout-controls.json',dict(rivers=rivers,signs=signs))
        if mode!='stock':
            require(controls['builder_priority']==[(1,10)] and controls['recruiting_city']==[(13,None),(23,None)],
                    'Expected the stock city bindings and the standalone Builder request preference')
        if not (source.parent/'opening-map.json.gz').exists():
            # Geometry is a secondary diagnostic. A failed export should be
            # visible and retryable next arm without discarding a matched game.
            try:
                record_opening_geography(c,source.parent)
            except (ValueError, RuntimeError, OSError, KeyError) as exc:
                write_json(out/'opening-map-error.json',dict(error=str(exc)))
        observers(c,range(1,len(game['roster'])))
        if vocabulary and not probe_vocabulary:
            raw=c.cmd(read(HERE/'vocabulary_watch.lua'),'PlotInfo','read-vocabulary-sites')
            require('CSC_VOCAB_WATCH_READY' in raw,'Vocabulary preview observer failed')
        if seed==171124601 and ((paired_layout and end>50) or floor_trial):
            # Read-only follow-up to the short replay. Tenochtitlan's turn-26
            # review favored 675 and its turn-37 foundation occupied 750.
            # UI receipts expose whether these two sites actually competed
            # on owned legal land and how the native private previews ranked.
            c.cmd("""
Events.TurnBegin.Add(function()
 local t=Game.GetCurrentGameTurn()
 if t<24 or t>37 then return end
 local city=CityManager.GetCity(3,65536)
 if not city or city:GetName()~='LOC_CITY_NAME_TENOCHTITLAN' then return end
 local center=Map.GetPlot(city:GetX(),city:GetY())
 local d=GameInfo.Districts.DISTRICT_CSC_TAILORS_QUARTER
 local prefix='CSC_AI_PAIR_ACTIVE_'..d.DistrictType
 for _,i in ipairs({599,675,750}) do
  local plot=Map.GetPlotByIndex(i)
  local owner=Cities.GetPlotPurchaseCity(plot)
  local legal=plot:CanHaveDistrict(d.Index,3,65536)
  local assigned=plot:GetOwner()==3 and owner and owner:GetID()==65536
  print('CSC_PAIR_TENO',t,i,plot:GetOwner(),owner and owner:GetID() or -1,
        assigned and legal==true or false,legal and plot:GetAdjacencyYield(3,65536,d.Index,GameInfo.Yields.YIELD_CSC_AI_PLACEMENT.Index) or '-',
        center:GetProperty(prefix..1) or '-',center:GetProperty(prefix..2) or '-')
 end
end)
""",'PlotInfo','observe-tenochtitlan-competition')
        if no_base_city:
            c.cmd("""Events.DistrictAddedToMap.Add(function(pid,did,cid,x,y,kind)
                print('CSC_NO_BASE_DISTRICT_ADDED',Game.GetCurrentGameTurn(),pid,cid,x,y,kind)
            end)""",'CSC_AI_BakersGameplay','record-district-alternatives')
        for turn in range(5,end+1,5):
            c.play(turn)
            # Keep full-game outcomes free of diagnostic property toggles.
            if paired_layout and end<=50 and turn in (25,50):
                from paired_material_preview import observe
                observe(c,out,turn)
            if probe_no_base and turn%10==0 and not (out/'no-base-preview.json').exists():
                from no_base_preview import observe
                observe(c,out,turn)
            if city_cue_probe and turn>=20 and not (out/'city-cue-result.json').is_file():
                from city_material_cue_probe import observe_city_cue
                observe_city_cue(c,out,range(1,len(game['roster'])),turn,allow_fallback=turn>=end-5)
        if city_cue_probe:
            require((out/'city-cue-result.json').is_file(),'No testable owned material/terrain pair by endpoint')
        # Keep the native save name short even when the experimental arm
        # has a long descriptive directory. The checkpoint helper appends
        # a per-directory identifier to distinguish runs of the same mode.
        try:
            ck=save_inactive_boundary(c,turn=end,name=f'CSC_LIGHT_{seed}_{mode.upper()}_T{end}',
                                      native_directory=saves,archive=out/'endpoint.Civ6Save')
            write_json(out/'checkpoint.json',ck)
        except (SaveFileUnavailable, SavePermissionUnavailable) as error:
            # An AI turn boundary can be fully observed while the local seat
            # lacks manual-save permission. Keep the native autosave from
            # this launch before rotation, along with the reason for fallback.
            keep_endpoint_autosave(out,saves,end,str(error))
        if probe_vocabulary:
            from vocabulary_preview import inspect
            inspect(c,out,end)
    except ObserverEliminated as error:
        # The native game can defeat the observer during a five-turn window.
        # Preserve a playable lead-in before the next game's autosave rotation.
        # The last status belongs to the preceding live observer turn.
        eliminated = True
        status = out/'live-status.json'
        live = load(status)['turn'] if status.is_file() else None
        receipts = []
        if live is not None:
            start_ns = int(load(out/'launch-bootstrap.json')['time']*1_000_000_000)
            receipts = archive_autosave_window(saves,out/'elimination-autosaves',
                                               max(1,live-1),min(end,live+1),start_ns)
        write_json(out/'observer-eliminated.json',dict(last_live_turn=live,reason=str(error),autosaves=receipts))
        raise
    finally:
        try:
            if session.owner is not None and session.owner.poll() is None:
                session.close(restore_preferences=lambda:restore_preferences(c,out) if
                    (out/'original-preferences.json').is_file() else None,menu_timeout=600)
        finally:
            if session.closed:
                shutil.copyfile(user/'Logs/Lua.log',out/'Lua.log')
                if release_trial or as_installed:
                    for name in ('AI_CityBuild.csv','City_BuildQueue.csv'):
                        path=user/'Logs'/name
                        if path.is_file():
                            shutil.copyfile(path,out/name)
            if not native_inventory():
                for path,staged,prior in ((script_path,script_active,script_before),(host_path,host_active,host_before),
                                          (staged_path,active,original)):
                    if staged!=prior:
                        current=path.read_bytes()
                        require(current in (staged,prior),'Installed benchmark input changed during replay: '+str(path))
                        if current!=prior:replace(path,prior)
            if eliminated and (out/'Lua.log').is_file():
                archive_censuses(read(out/'Lua.log'),out)
    summarize_finished(out,end,ce,no_base_city,local_material_cues or paired_layout or floor_trial)


def keep_endpoint_autosave(out,saves,end,reason):
    start_ns=int(load(out/'launch-bootstrap.json')['time']*1_000_000_000)
    receipt,=archive_autosave_window(saves,out/'endpoint-autosave',end,end,start_ns)
    require(receipt['status']=='archived','Current game has no matching endpoint autosave')
    write_json(out/'endpoint-autosave.json',dict(receipt=receipt,manual_save=reason))


def summarize_finished(out,end,ce,no_base_city,local_material_cues):
    """Validate the retained observations, including after a late save failure."""
    log=read(out/'Lua.log')
    if no_base_city:
        require('CSC_NO_BASE_INSTALLED' in log and 'CSC_NO_BASE_REVIEW' in log
                and not any('Runtime Error' in line and 'CSC_AI_BakersGameplay' in line for line in log.splitlines()),
                'City opportunity review failed to run cleanly')
    require('CSC_MILESTONE_SERVICE_FAULT' not in log and 'CSC_QUARTER_WATCH_FAULT' not in log,'Observer fault')
    if local_material_cues:
        require('CSC_LOCAL_CUE_INSTALLED' in log and 'CSC_LOCAL_CUE_REVIEW' in log and
                'CSC_LOCAL_CUE_FAULT' not in log,'Local material guidance failed or missed every city review')
    require(set(archive_censuses(log,out))==set(range(25,end+1,25)),'Incomplete physical census')
    # The final gameplay census can arrive while the UI is still on the
    # preceding turn. Preserve the measured prefix when that exact gameplay
    # endpoint has a native autosave. Interior clock gaps remain errors.
    timing_end=end
    if (out/'endpoint-autosave.json').exists() and not re.search(r'CSC_GUIDANCE_CLOCK\s+'+str(end)+r'\s+',log):
        timing_end=end-1
    times,excluded,direct=observed_turns(out,timing_end,2)
    require(bool(direct['published_packets'])==ce,'Unexpected advanced publications')
    write_json(out/'measured.json',dict(clean=times,direct=direct['publisher_wall'],last_ui_clock=timing_end,
        excluded={t:sorted(v) for t,v in excluded.items()}))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('root',type=Path);p.add_argument('seed',type=int)
    p.add_argument('mode',choices=['prepare','verify-off','prepare-advanced','native','stock','advanced'])
    p.add_argument('--ce-opening',action='store_true',help='Use the separately verified same-seed CE opening')
    p.add_argument('--deposit-cues',action='store_true',help='Test the undeveloped-resource class cue on this seed')
    p.add_argument('--customer-buildings',action='store_true',help='Test the stock preference for first customer buildings')
    p.add_argument('--supplier-jobs',action='store_true',help='Test stock Builder improvement values next to a Quarter')
    p.add_argument('--city-cue-probe',action='store_true',help='Inspect a city-specific stock adjacency in a disposable replay')
    p.add_argument('--local-material-cues',action='store_true',help='Run bounded city-specific material guidance from CSC')
    p.add_argument('--as-installed',action='store_true',help='Verify the installed release against source and leave its files untouched; other flags describe expected controls')
    p.add_argument('--no-base-city',action='store_true',help='Stage the city opportunity trial over the verified ordinary release')
    p.add_argument('--paired-layout',action='store_true',help='Test one or two signed terrain cues per city')
    p.add_argument('--layout-floor',type=int,choices=(0,6,8,10),help='Default penalty with this private terrain relief on distinguishable supplied sites (zero for penalty only)')
    p.add_argument('--frontier',action='store_true',help='Reject proxies that reward weak legal frontier footprints; refresh after ownership changes')
    p.add_argument('--release-ambiguous-floor',action='store_true',help='Use ordinary scores if a supplied owned site has no safe terrain cue')
    p.add_argument('--record-layouts',action='store_true',help='Record the legal site geometry for offline cue comparisons')
    p.add_argument('--split-relief',action='store_true',help='Try two smaller terrain cues when the single cue fails')
    p.add_argument('--third-relief',action='store_true',help='Try a third terrain term when two cannot isolate a supplied site')
    p.add_argument('--vocabulary',action='store_true',help='Use the full catalogue of native city-switchable spatial clues')
    p.add_argument('--probe-vocabulary',action='store_true',help='Test native preview changes after the endpoint save')
    p.add_argument('--river-cue',action='store_true',help='Test the fixed private river cue separately')
    p.add_argument('--probe-no-base',action='store_true',help='Toggle and restore one active gate for an intra-turn native readback')
    p.add_argument('--observe-no-base',action='store_true',help='Run the identical opportunity review with its scoring action disabled')
    p.add_argument('--end',type=int,default=250);p.add_argument('--label')
    a=p.parse_args();replay(a.root,a.seed,a.mode,a.end,a.label,a.ce_opening,a.deposit_cues,a.customer_buildings,
                           a.supplier_jobs,a.city_cue_probe,a.local_material_cues,a.as_installed,a.no_base_city,a.probe_no_base,
                           a.observe_no_base,a.paired_layout,a.river_cue,a.layout_floor,a.frontier,a.release_ambiguous_floor,
                           a.record_layouts,a.split_relief,a.third_relief,a.vocabulary,a.probe_vocabulary)
