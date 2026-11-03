"""Three authorized Ancient-start candidates; historical comparisons only.

No fresh controls, opportunity fixtures, research grants, or automatic reruns.
The known native strategy re-adoption limitation is measured, not claimed fixed.
Installed overlays are temporary; concurrent source edits are never overwritten.
"""
import argparse
import csv
import hashlib
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import time
import traceback
import zlib
from pathlib import Path

import civic_guidance_long_trial as long
from civic_unlock_rst_trial import RSTRunner
from fixed_research_trial import inventory, INSTALLED
from paired_standard import HERE, read, sha
from run import ROOT, LOGS, SAVES, write

VERSION = 'ancient-three-natural-guidance200-clean-legacy-v1'
TEST = 'CSC-three-Ancient-guidance-candidates'
TARGET = 250
ORIGINAL_LONG_CHECK = long.native_check
OLD_PREFIXES = ('CSC_AI_SERVICE_%', 'CSC_AI_FIXED_SERVICE_%')
SQL = Path('Data/CSC_AI.sql')
LUA = Path('Lua_UI/AI/CSC_AI_Research.lua')


def cleanup_sql():
    text = '\n-- Remove legacy strategy preferences, retaining read-only Scan/Evaluate data.\n'
    for prefix in OLD_PREFIXES:
        for table in ('Strategy_Priorities','AiFavoredItems','AiLists','AiListTypes'):
            text += f"DELETE FROM {table} WHERE ListType LIKE '{prefix}';\n"
    for table in ('Strategy_Priorities','StrategyConditions','Strategies'):
        text += f"DELETE FROM {table} WHERE StrategyType LIKE 'STRATEGY_CSC_AI_SERVICE_%' OR StrategyType LIKE 'STRATEGY_CSC_AI_FIXED_SERVICE_%';\n"
    text += "DELETE FROM Types WHERE Type LIKE 'STRATEGY_CSC_AI_SERVICE_%' OR Type LIKE 'STRATEGY_CSC_AI_FIXED_SERVICE_%';\n"
    return text


def overlay():
    return long.overlay('on') + cleanup_sql()


def callback_bytes():
    original = long.callback_bytes('on').decode('utf-8')
    original = original.replace("G.code_version='natural-six-service-civic-guidance200-forbidden-v1'", "G.code_version='"+VERSION+"'")
    old = 'if player and player:IsAlive() and player:IsMajor() and not player:IsHuman() and targets[plan] then'
    new = 'if pid>=1 and pid<=5 and player and player:IsAlive() and player:IsMajor() and not player:IsHuman() and targets[plan] then'
    assert original.count(old) == 1
    original = original.replace(old,new)
    # Record the rejected autoplay slot too, rather than hiding its callbacks.
    original = original.replace('if pid>=1 and pid<=5 and targets[plan] then','if pid>=0 and pid<=5 and targets[plan] then')
    return original.encode('utf-8')


def native_check(db, patch, source):
    result = ORIGINAL_LONG_CHECK(db,'on',patch,source)
    for prefix in OLD_PREFIXES:
        for table in ('AiLists','AiListTypes','AiFavoredItems','Strategy_Priorities'):
            assert db.execute(f'SELECT COUNT(*) FROM {table} WHERE ListType LIKE ?',(prefix,)).fetchone() == (0,)
    for table in ('Strategies','StrategyConditions','Strategy_Priorities'):
        assert db.execute(f"SELECT COUNT(*) FROM {table} WHERE StrategyType LIKE 'STRATEGY_CSC_AI_SERVICE_%' OR StrategyType LIKE 'STRATEGY_CSC_AI_FIXED_SERVICE_%'").fetchone() == (0,)
    assert db.execute('SELECT COUNT(*) FROM CSC_AI_ServiceResearch').fetchone() == (6,)
    assert db.execute('SELECT COUNT(*) FROM CSC_AI_ResearchItems').fetchone()[0] > 0
    assert db.execute("SELECT YieldChange,AdjacentResourceClass FROM Adjacency_YieldChanges WHERE ID='CSC_AI_BONUS_RESOURCE'").fetchall()==[(12,'RESOURCECLASS_BONUS')]
    assert db.execute("SELECT YieldChange,AdjacentRiver FROM Adjacency_YieldChanges WHERE ID='CSC_AI_RIVER'").fetchall()==[(4,1)]
    assert db.execute("SELECT DISTINCT YieldChange FROM Adjacency_YieldChanges WHERE ID LIKE 'CSC_AI_SALES_%'").fetchall()==[(10,)]
    assert db.execute("SELECT DISTINCT Value FROM ModifierArguments WHERE ModifierId LIKE 'MOD_CSC_AI_SUPPLY_%_PRESENT' AND Name='Amount'").fetchall()==[('40',)]
    assert db.execute("SELECT DISTINCT Value FROM ModifierArguments WHERE ModifierId LIKE 'MOD_CSC_AI_IMPROVE_%' AND Name='Amount'").fetchall()==[('80',)]
    result.update(baseline_old_research_preferences_preserved=False,legacy_preferences_removed=True,
                  actual_scan_data_preserved=True,player_scope='explicit1-5; autoplay0 excluded',version=VERSION)
    return result


def offline_preflight(path, source):
    ref=sqlite3.connect(long.harness.REFERENCE.as_uri()+'?mode=ro',uri=True)
    db=sqlite3.connect(':memory:');ref.backup(db);ref.close()
    db.create_function('Make_Hash',1,lambda x:zlib.crc32(x.encode()))
    patch=overlay();db.executescript(source+'\n'+patch)
    result=native_check(db,patch,source)
    write(path,{k:v for k,v in result.items() if k!='inventory'})


class AncientRunner(long.LongRunner):
    def cmd(self,code,state='GameCore_Tuner',label='command',wait=2,check=True):
        # Avoid the inherited Medieval host adapter. Explicit Ancient setup is
        # assembled below; other calls retain bounded read-only retries.
        if label.startswith('start-'):
            self.offsets={p.name:{'bytes':p.stat().st_size,'hash':sha(p)} for p in LOGS.iterdir() if p.is_file()}
            label='host-ancient-'+label[6:]
        return RSTRunner.cmd(self,code,state,label,wait,check)

    def pin_sources(self):
        super().pin_sources()
        p=self.out/'controller-source-hashes.json';pins=read(p)
        for f in (Path(__file__),HERE/'civic_guidance_ancient_job.py'):
            pins[str(f)]=sha(f)
        write(p,pins)

    def archive_version(self):
        long.BASE_ARCHIVE_VERSION(self)
        p=self.out/'source-version/version.json';v=read(p)
        v.update(code_version=VERSION,test=TEST,run=self.run_number,arm='candidate',
                 start_era='ERA_ANCIENT',target_turn=TARGET,analyzed_rounds=249,
                 map_seed=self.map_seed,game_seed=self.game_seed,leaders=self.roster,
                 natural_play=True,fixtures=False,legacy_preferences_removed=True,
                 player_scope='explicit IDs1-5; player0 recorded but ineligible',
                 research={'channel_amount':200,'static_bias':-100,'active_bias':100,'known_restart_gap':True},
                 historical_comparison_only=True,no_new_controls=True,
                 common_overlay='Six inert private civic channels; legacy preference lists/strategies removed, Scan/Evaluate data retained. Vanilla preferences preserved.',
                 installed_baseline_reference=str(self.out.parent/'original-installed'))
        write(p,v)
        (p.parent/'applied-callback.lua').write_bytes(callback_bytes())

    def start_pair(self,i=1,resume_map=False):
        assert i==1 and not resume_map
        folder=self.out/'game-01';folder.mkdir(exist_ok=True)
        self.check_installed();self.select_mods(False)
        leaders='local leaders={'+','.join(json.dumps(x) for x in self.roster)+'};for j,pid in ipairs(GameConfiguration.GetParticipatingPlayerIDs()) do PlayerConfigurations[pid]:SetLeaderTypeName(leaders[j]);end;'
        code="GameConfiguration.SetToDefaults();GameConfiguration.SetRuleSet('RULESET_EXPANSION_2');BuildHeadlessGameSetup();RebuildPlayerParameters(true);GameSetup_RefreshParameters();MapConfiguration.SetScript('Continents.lua');MapConfiguration.SetMapSize('MAPSIZE_SMALL');GameConfiguration.SetParticipatingPlayerCount(6);GameConfiguration.SetValue('CITY_STATE_COUNT',9);GameConfiguration.SetGameSpeedType('GAMESPEED_ONLINE');GameConfiguration.SetHandicapType('DIFFICULTY_PRINCE');GameConfiguration.SetValue('GAME_SYNC_RANDOM_SEED',"+str(self.game_seed)+");MapConfiguration.SetValue('RANDOM_SEED',"+str(self.map_seed)+");MapConfiguration.SetValue('resources',2);GameConfiguration.SetValue('CSC_INCLUDE_ANIMAL_RESOURCES',1);GameConfiguration.SetValue('CSC_REMOVE_UNUSED_MODDED_RESOURCES',1);GameConfiguration.SetValue('GAMEMODE_MONOPOLIES',false);GameConfiguration.SetValue('CSC_RESOURCE_MAP_ASSISTANCE',1);GameConfiguration.SetValue('CSC_MATERIAL_MAP_DIAGNOSTICS',false);GameConfiguration.SetStartEra(DB.MakeHash('ERA_ANCIENT'));"+leaders+"ReleasePlayerParameters();HideGameSetup();Automation.SetAutoStartEnabled(true);Network.HostGame(ServerType.SERVER_TYPE_NONE);"
        self.cmd(code,'MainMenu','start-ancient-'+str(self.run_number),wait=3,check=False)
        self.wait('CSC_AdjacencyGameplay',300)
        self.cmd("assert(GameConfiguration.GetStartEra()==DB.MakeHash('ERA_ANCIENT'));assert(Game.GetCurrentGameTurn()==1);assert(not AutoplayManager.IsActive());",'GameCore_Tuner','verify-start-era',wait=3)
        self.start_turn=1
        text=self.cmd((HERE.parent/'map_survey/dump.lua').read_text(encoding='utf-8'),'CSC_AdjacencyGameplay','dump-ancient',wait=4)
        world=json.loads(re.search(r'CSCMAP_SURVEY=([^\r\n]+)',text)[1]);assert world['turn']==1
        write(folder/'initial-map.json',world)
        write(folder/'settings.json',{'code_version':VERSION,'map_seed':self.map_seed,'game_seed':self.game_seed,
              'leaders':self.roster,'start_era':'ERA_ANCIENT','initial_turn':1,'target_turn':250,
              'speed':'Online','difficulty':'Prince','resource_setting':2,'resource_pass':4,
              'simulation_rounds':249,'natural_start':True,'opportunity_fixture':False,
              'legacy_research_removed':True,'treated_players':[1,2,3,4,5],'autoplay0_excluded':True,
              'comparison':'Historical only; not a fresh matched control',
              'ai':'Quarter40/improvement-owned80/improvement90/Builder50/native12/4/10; six guidance200 channels'})
        (folder/'enabled-mods.txt').write_text(self.active_mods,encoding='utf-8')
        write(self.out/'checkpoint-layout.json',{'primary':[1,*range(25,251,25)],'builders':[1,50,100,150,200,250],'analyzed_turns':[1,249]})
        text=self.cmd("local a=Game:GetProperty('CSC_MATERIAL_MAP_ASSISTANCE_AUDIT');assert(a and a.status=='complete' and a.version==4 and a.initialization_turn==1);print('CSC_ANCIENT_ASSIST='..CSC_MaterialMapCore.Json(a));",'CSC_MaterialMap','assistance-audit',wait=3)
        write(folder/'assistance-audit.json',json.loads(re.search(r'CSC_ANCIENT_ASSIST=([^\r\n]+)',text)[1]))
        subprocess.run([sys.executable,'-X','utf8',str(HERE/'capture_reference.py'),'--output',str(folder/'mechanics-reference.json')],check=True)
        shutil.copy2(folder/'mechanics-reference.json',self.out/'mechanics-reference.json')
        self.cmd((HERE/'paired_observer.lua').read_text(encoding='utf-8'),'CSC_AdjacencyGameplay','observer-1',wait=3)
        self.snapshot(1,1);self.save_checkpoint(1,1)
        initial=read(folder/'turn-001.json')
        assert len(initial['players'])==6 and not initial['cities']
        assert [x['id'] for x in initial['players']]==list(range(6))
        assert all('CIVIC_NAVAL_TRADITION' not in x['civics'] for x in initial['players'])
        self.cmd((HERE/'builder_observer.lua').read_text(encoding='utf-8'),'CSC_AdjacencyGameplay','builder-unit-observer',wait=2)
        self.finish_preflight(1)

    def finish_preflight(self,i):
        self.reset_logs=set()
        for name,old in self.offsets.items():
            f=LOGS/name
            if f.exists():
                b=f.read_bytes()
                if len(b)<old['bytes'] or hashlib.sha256(b[:old['bytes']]).hexdigest()!=old['hash']:self.reset_logs.add(name)
        write(self.out/'native-log-offsets.json',{'before_host':self.offsets,'reset_detected_during_load':sorted(self.reset_logs)})
        self.cmd("assert(CSC_RESEARCH_PROBE_NATIVE.code_version=='"+VERSION+"');assert(CSC_AI_Research.version==1);assert(not Game:GetProperty('CSC_RESEARCH_CHOICE_FIXTURE'));assert(not Game:GetProperty('CSC_C7_MATERIAL_SITES'));",'CSC_AI_Research','probe-loaded')
        cache=Path.home()/"AppData/Local/Firaxis Games/Sid Meier's Civilization VI/Cache/DebugGameplay.sqlite"
        source=sqlite3.connect(cache.as_uri()+'?mode=ro',uri=True);db=sqlite3.connect(':memory:');source.backup(db);source.close()
        dest=sqlite3.connect(self.out/'native-gameplay.sqlite');db.backup(dest);dest.close()
        write(self.out/'native-database-validation.json',native_check(db,self.overlay,self.original_sql.decode('utf-8')))
        self.cmd((HERE/'builder_export.lua').read_text(encoding='utf-8'),'CSC_AdjacencyGameplay','builder-unit-export',wait=2)
        self.builder_snapshot(1)

    def save_checkpoint(self,i,turn):
        name=f'CSC_AncientGuidance_20261021_{self.run_number}_{turn:03d}';path=SAVES/(name+'.Civ6Save');stamp=time.time()
        try:
            text=self.cmd("print('CSC_ANCIENT_SAVE_TURN',Game.GetCurrentGameTurn());",'GameCore_Tuner','actual-save-turn')
            actual=int(re.search(r'CSC_ANCIENT_SAVE_TURN\s+(\d+)',text)[1]);assert actual==turn
            self.cmd('local s={Name='+json.dumps(name)+',Location=SaveLocations.LOCAL_STORAGE,Type=SaveTypes.SINGLE_PLAYER,IsAutosave=false,IsQuicksave=false};assert(Network.SaveGame(s)~=false);','PlotInfo','save-'+str(turn),wait=5)
            for _ in range(20):
                if path.exists() and path.stat().st_mtime>=stamp-2 and path.stat().st_size:
                    size=path.stat().st_size;time.sleep(1)
                    if size==path.stat().st_size:
                        dest=self.out/'game-01'/path.name;shutil.copy2(path,dest)
                        write(self.out/'game-01'/('initial-save.json' if turn==1 else 'endpoint-save.json'),{'path':str(path),'sha256':sha(dest),'actual_turn':actual,'kind':'confirmed named native save'})
                        return
                time.sleep(1)
            raise RuntimeError('Named save not confirmed')
        except Exception as exc:
            write(self.out/f'save-warning-{turn}.json',{'error':str(exc),'requested_turn':turn})
            if turn==1:raise

    def observe(self):
        self.cmd((HERE/'strategy_research_observer.lua').read_text(encoding='utf-8'),'CSC_AI_Research','probe-observer-install',wait=4)
        self.observer_active=True;self.export_probe()
        self.cmd("Events.PlayerTurnActivated.Add(function() if Game.GetCurrentGameTurn()>=250 and AutoplayManager.IsActive() then AutoplayManager.SetActive(false) end end);",'GameCore_Tuner','target250-hook')
        self.cmd("Automation.SetActive(false);AutoplayManager.SetDisableAssertsForAutoplay(true);AutoplayManager.SetTurns(250-Game.GetCurrentGameTurn());AutoplayManager.SetReturnAsPlayer(0);AutoplayManager.SetObserveAsPlayer(-1);AutoplayManager.SetActive(true);",'GameCore_Tuner','ancient-autoplay-start',wait=3)
        self.say(f'{TEST}/run{self.run_number}: NATURAL autoplay started Ancient1 to250; no fixtures; player0 explicitly excluded.')
        archived={1};builders={1};deadline=time.monotonic()+14400;last=1;changed=time.monotonic();failures=0
        while time.monotonic()<deadline:
            time.sleep(25)
            try:
                text=self.cmd("print('CSC_LONG_PROGRESS',Game.GetCurrentGameTurn(),AutoplayManager.IsActive());",'GameCore_Tuner','research-probe-poll-long',wait=2)
                current,active=re.findall(r'CSC_LONG_PROGRESS\s+(\d+)\s+(true|false)',text)[-1];current=int(current);active=active=='true';failures=0
            except (RuntimeError,OSError,KeyError,AssertionError,IndexError):
                failures+=1
                if failures>=3:raise RuntimeError('Three failed native polls; stop, no restart')
                continue
            if current!=last:last=current;changed=time.monotonic()
            write(self.out/'live-status.json',{'status':'running','run':self.run_number,'turn':current,'target':250,'updated_unix':time.time()})
            for t in range(25,251,25):
                if t<=min(current,250) and t not in archived:
                    self.snapshot(1,t);snap=read(self.out/f'game-01/turn-{t:03d}.json')
                    for city in snap['cities']:
                        for plan,*_ in long.PLANS:assert abs(city['yields'][long.yield_type(plan)])<1e-6
                    data=self.export_probe();assert not data['errors'] and not data['native']['errors']
                    assert not any(x['player']==0 and x['active'] for x in data['native']['transitions'])
                    archived.add(t)
                    if t%50==0:self.builder_snapshot(t);builders.add(t)
                    self.say(f'run{self.run_number}: checkpoint{t}, research and private-yield checks archived.')
            if current>=250:
                if active:self.cmd('AutoplayManager.SetActive(false);','GameCore_Tuner','ancient-autoplay-stop')
                assert current==250,'Endpoint overshoot; preserve frozen250, no rerun'
                break
            if not active:raise RuntimeError('Autoplay stopped early at'+str(current))
            if time.monotonic()-changed>600:raise RuntimeError('Native game stalled ten minutes')
        else:raise RuntimeError('Four-hour bound exceeded')
        data=self.export_probe();assert not data['errors'] and not data['native']['errors']
        history=[x for x in data['history'] if 1<=x['turn']<250]
        pairs={(x['turn'],x['player']) for x in history};assert len(pairs)==len(history)
        defeat={x['player']:x['turn'] for x in data['defeats']};missing={(t,pid) for t in range(1,250) for pid in range(1,6)}-pairs
        assert all(pid in defeat and t>=defeat[pid] for t,pid in missing)
        assert not any(x['player']==0 and x['active'] for x in data['native']['transitions'])
        write(self.out/'observations.json',{**data,'history':history})
        write(self.out/'observation-validation.json',{'passed':True,'observations':len(history),'expected_uncensored':1245,'censored_pairs':sorted(missing),'analyzed_turns':[1,249],'actual_endpoint':250,'player0_explicitly_excluded':True})
        self.save_checkpoint(1,250);self.archive_native_logs()
        validation=long.classify_native_logs(self.out/'native-logs');write(self.out/'native-script-validation.json',validation);assert validation['passed'],validation['errors']
        player0=[]
        for row in csv.reader((self.out/'native-logs/AI_Victories.csv').read_text().splitlines()):
            row=[x.strip() for x in row]
            if len(row)>3 and row[1]=='0' and row[2].startswith('STRATEGY_CSC_TEST_LONG_') and row[3]=='Following':player0.append(row)
        assert not player0,'Autoplay0 unexpectedly adopted guidance'
        autos=self.out/'endpoint-autosaves';autos.mkdir(exist_ok=True)
        for f in sorted((SAVES/'auto').glob('*.Civ6Save'),key=lambda f:f.stat().st_mtime,reverse=True)[:3]:shutil.copy2(f,autos/f.name)
        self.check_installed();source_changes=[]
        for name in ('tuning-source-hashes','controller-source-hashes'):
            for rel,h in read(self.out/(name+'.json')).items():
                if sha(Path(rel))!=h:
                    assert Path(rel).is_relative_to(ROOT/'Civ Supply Chains') or Path(rel).is_relative_to(ROOT/'project/modbuddy'),rel
                    source_changes.append(rel)
        self.actual_endpoint=250
        write(self.out/'validation.json',{'passed':True,'actual_endpoint':250,'primary_checkpoints':sorted(archived),'builder_checkpoints':sorted(builders),'private_yields_zero':True,'no_player0_adoption':True,'uninstalled_worktree_changes':source_changes})


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);parser.add_argument('--preflight-only',action='store_true');args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=args.preflight_only)
    originals={rel:(INSTALLED/rel).read_bytes() for rel in (SQL,LUA)}
    offline_preflight(args.output/'offline-preflight.json',originals[SQL].decode('utf-8'))
    if args.preflight_only:return
    for rel,content in originals.items():
        f=args.output/'original-installed'/rel;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(content)
    captures=Path.home()/'Desktop/Codex/csc-implemented-native-20261016'
    runs=[read(captures/f'implemented-vanilla-standard/map-{i:02d}/settings.json') for i in (1,2,3)]
    runner=None;completed=[]
    try:
        bootstrap=AncientRunner(args.output/'session-preservation');bootstrap.preserve_existing_game()
        for number,settings in enumerate(runs,1):
            for rel,content in originals.items():assert (INSTALLED/rel).read_bytes()==content
            (INSTALLED/SQL).write_bytes(originals[SQL]+b'\n'+overlay().encode())
            (INSTALLED/LUA).write_bytes(originals[LUA]+callback_bytes())
            runner=AncientRunner(args.output/f'run-{number:02d}')
            runner.run_number=number;runner.map_seed=settings['map_seed'];runner.game_seed=settings['game_seed'];runner.roster=settings['leaders']
            runner.original_sql=originals[SQL];runner.original_rst=False;runner.arm='candidate';runner.phase='ancient';runner.rounds=249;runner.overlay=overlay();runner.keep_game=False;runner.captures=captures
            runner.pin_sources();runner.archive_version()
            write(args.output/'active-stage.json',{'run':number,'output':str(runner.out),'pid':os.getpid(),'version':VERSION})
            write(args.output/'job-status.json',{'status':'running','run':number,'pid':os.getpid(),'version':VERSION,'updated_unix':time.time(),'only_three_candidates':True})
            runner.wait('MainMenu',180);runner.config();runner.start_pair();runner.observe();runner.menu();runner.restore_verified()
            for rel,content in originals.items():(INSTALLED/rel).write_bytes(content)
            write(runner.out/'complete.json',{'passed':True,'run':number,'actual_endpoint':250,'source_gameplay_not_deployed':True})
            completed.append(number);runner=None
        write(args.output/'job-status.json',{'status':'complete','runs':completed,'version':VERSION,'historical_comparison_only':True,'updated_unix':time.time()})
    except BaseException as exc:
        write(args.output/'failure.json',{'error':str(exc),'traceback':traceback.format_exc(),'completed_runs':completed,'no_automatic_retry':True})
        if runner:
            try:
                if getattr(runner,'observer_active',False):runner.export_probe()
                runner.archive_failure()
            except Exception:pass
            try:
                runner.states()
                if 'PlotInfo' in runner.state:runner.menu()
                if (runner.out/'original-preferences.json').exists():runner.restore_verified()
            except Exception as error:write(args.output/'cleanup-required.json',{'error':str(error)})
        write(args.output/'job-status.json',{'status':'failed','error':str(exc),'completed_runs':completed,'updated_unix':time.time()})
        raise
    finally:
        for rel,content in originals.items():(INSTALLED/rel).write_bytes(content)
        write(args.output/'installed-restored.json',{'verified':all((INSTALLED/rel).read_bytes()==content for rel,content in originals.items()),'original_baseline_reference':'original-installed; worktree edits preserved'})


if __name__=='__main__':main()
