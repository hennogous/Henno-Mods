"""Bounded delivery check using the shared controller, never external injection.

The package must already be installed in a fresh dedicated mod directory. This
driver selects it, hosts one Online world, reads package-owned native receipts,
then verifies ordinary exit, exact preferences and unchanged package contents.
"""
from __future__ import annotations
import argparse, hashlib, json, re, sys, time, traceback
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'project/tools/ai_baseline'))
from full_game_controller.probe import make_probe_controller
from full_game_controller.session import NativeSession
from full_game_controller.windows_process import HeldProcess,native_inventory
from full_game_controller.environment import launch,configure,flags,manifest,restore_preferences,write_json,archive_sources
from full_game_controller.log_capture import capture_log_baseline,read_log_delta

MOD='d0f3a2ab-4fa6-4a7a-bf9b-b82a66fe2a04'
CSC='c5e66bd1-d804-443b-ac3d-1917a20dba3c'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def parse(raw,marker):
    values=re.findall(re.escape(marker)+r'=([^\r\n]+)',raw)
    if len(values)!=1:raise RuntimeError('Missing/ambiguous '+marker)
    return json.loads(values[0])

def log_delivery(path, expected_delta):
    """Publish resets window counters; retain package receipts from before reset.

    Several player events can print the same cumulative window. Count its largest
    receipt once, preserving line locators and every verified sample.
    """
    windows={}
    if path.exists():
        for line,text in enumerate(path.read_text(encoding='utf-8',errors='replace').splitlines(),1):
            if 'CSC_WORKSHOP_BRIDGE ' not in text or '{' not in text:continue
            try:value=json.loads(text[text.index('{'):])
            except ValueError:continue
            if not value.get('changed'):continue
            if value['faults'] or any(s[0]==0 or s[5]-s[4]!=expected_delta for s in value['samples']):
                raise RuntimeError('Invalid package-owned native log receipt')
            key=value['generation']
            if key not in windows or windows[key]['receipt']['changed']<value['changed']:
                windows[key]=dict(line=line,receipt=value)
    return dict(verified=True,source=str(path),windows=list(windows.values()),observed_adjustments=sum(v['receipt']['changed']for v in windows.values()),scope='Maximum captured counter once per policy generation; not a completion/economic outcome')
def setup(delta):
    return """GameConfiguration.SetToDefaults();GameConfiguration.SetRuleSet('RULESET_EXPANSION_2');BuildHeadlessGameSetup();RebuildPlayerParameters(true);GameSetup_RefreshParameters();MapConfiguration.SetScript('Continents.lua');MapConfiguration.SetMapSize('MAPSIZE_SMALL');GameConfiguration.SetParticipatingPlayerCount(6);GameConfiguration.SetValue('CITY_STATE_COUNT',9);GameConfiguration.SetGameSpeedType('GAMESPEED_ONLINE');GameConfiguration.SetHandicapType('DIFFICULTY_PRINCE');GameConfiguration.SetValue('GAME_SYNC_RANDOM_SEED',26141104);MapConfiguration.SetValue('RANDOM_SEED',16141104);MapConfiguration.SetValue('resources',2);GameConfiguration.SetValue('GAMEMODE_MONOPOLIES',false);GameConfiguration.SetStartEra(DB.MakeHash('ERA_ANCIENT'));GameConfiguration.SetValue('CSC_BRIDGE_SMOKE_DELTA',"""+str(delta)+""");for _,pid in ipairs(GameConfiguration.GetParticipatingPlayerIDs())do PlayerConfigurations[pid]:SetLeaderTypeName(nil)end;ReleasePlayerParameters();HideGameSetup();Automation.SetAutoStartEnabled(true);Network.HostGame(ServerType.SERVER_TYPE_NONE);"""

def run(a):
    out=a.output.resolve()
    if out.exists() or native_inventory():raise RuntimeError('Fresh output and no existing native/Tuner owner required')
    if not 2<=a.endpoint<=20:raise ValueError('Smoke endpoint must be2..20')
    out.mkdir(parents=True)
    package=manifest(a.package); installed=manifest(a.installed)
    files=[p for p in HERE.iterdir() if p.is_file()]
    files+=list((ROOT/'project/tools/ai_baseline/full_game_controller').glob('*.py'))
    files+=list((ROOT/'project/tools/ai_baseline/full_game_controller').glob('*.lua'))
    pins={str(p.resolve()):sha(p) for p in files}
    write_json(out/'pins.json',pins);write_json(out/'sources.json',archive_sources(pins,out/'source-version'))
    write_json(out/'package-before.json',package);write_json(out/'installed-before.json',installed)
    write_json(out/'protocol.json',dict(endpoint=a.endpoint,speed='GAMESPEED_ONLINE',delta=a.delta,frida=False,external_policy_publication=False,worlds=2 if a.recreate_observe else 1,second_world_endpoint=2 if a.recreate_observe else None,load_games=0,original_humans_excluded=True,delivery_only=True))
    c=make_probe_controller(out,user_root=a.user_root)
    c.allow_observer_warning_dismissal=c.allow_observer_first_meet_dismissal=c.allow_observer_congress_review=True
    c.study_endpoint=a.endpoint
    s=NativeSession(out,c,inventory=native_inventory,hold=HeldProcess,write=write_json)
    observations=[];error=None;logs={};last=None;phase=1;expected_delta=a.delta;recreated=False
    def verify():
        if any(sha(p)!=v for p,v in pins.items()):raise RuntimeError('Pinned source changed')
        if manifest(a.package)!=package or manifest(a.installed)!=installed:raise RuntimeError('Installed package changed')
    def read_status(label):
        raw=c.cmd("assert(type(CSCBridgeStatus)=='function');print('CSC_NATIVE_DELIVERY='..CSCBridgeStatus());",'CSC_AI_WorkshopBridge',label)
        value=parse(raw,'CSC_NATIVE_DELIVERY');value['turn']=last;value['label']=label;value['phase']=phase
        write_json(out/'observations'/('phase-'+str(phase)+'-'+label+'.json'),value);observations.append(value)
        if value['ready']!=1 or value['faults']!=0:raise RuntimeError('Native bridge not healthy')
        for sample in value['samples']:
            if sample[0]==0 or sample[5]-sample[4]!=expected_delta:raise RuntimeError('Invalid score receipt or human target')
        return value
    def gate():
        nonlocal last
        last=1
        c.cmd("assert(Game.GetCurrentGameTurn()==1);assert(GameInfo.Yields.YIELD_CSC_AI_PLACEMENT==nil);assert(Players[0]:IsHuman());assert(GameConfiguration.GetValue('CSC_BRIDGE_SMOKE_DELTA')=="+str(expected_delta)+");",'GameCore_Tuner','source-identity')
        value=read_status('source-1')
        if expected_delta==0 and (value['enabled']!=0 or value['changed']!=0 or value['version']!=0 or value['entries']!=0):raise RuntimeError('Observation mode retained a policy')
        return True
    try:
        verify();s.start(lambda:launch(a,out));s.wait_context('MainMenu');configure(c,out,'BASIC')
        c.cmd("local best=nil;for _,m in ipairs(Modding.GetInstalledMods())do if m.Id=='"+MOD+"'then assert(not best,'Duplicate prototype');best=m end end;assert(best,'Prototype missing');Modding.EnableMod(best.Handle,true);",'MainMenu','enable-package-once')
        s.wait_context('MainMenu',90)
        selected=flags(c,'verify-CSC-and-bridge-only')
        if {k for k,v in selected['mods'].items() if v}!={CSC,MOD}:raise RuntimeError('Unexpected enabled mod set')
        for name in('Lua.log','Database.log','Modding.log','AI_CityBuild.csv','AI_Behavior_Trees.csv','City_BuildQueue.csv'):
            logs[name]=capture_log_baseline(a.user_root/'Logs'/name)
        s.issue_once('host',setup(a.delta),'MainMenu')
        s.ready_after_issue(1,('GameCore_Tuner','PlotInfo','CSC_AI_WorkshopBridge'),eligibility=gate,timeout=300)
        import subprocess
        code="Get-Process -Id "+str(s.owner.pid)+" -ErrorAction Stop | ForEach-Object { $_.Modules } | Where-Object {$_.ModuleName -match 'GameCore_XP2'} | Select-Object ModuleName,FileName | ConvertTo-Json -Compress"
        modules=json.loads(subprocess.check_output(['powershell','-NoProfile','-Command',code],text=True,creationflags=subprocess.CREATE_NO_WINDOW))
        if isinstance(modules,dict):modules=[modules]
        expected=(a.package/'Binaries/Win64/GameCore_XP2_CSC_Bridge_FinalRelease.dll').resolve()
        if not any(Path(m['FileName']).resolve()==expected for m in modules):raise RuntimeError('Package DLL not in native module list')
        if any('CE_FinalRelease' in m['ModuleName']for m in modules):raise RuntimeError('Unexpected CE module')
        write_json(out/'loaded-modules.json',modules)
        for target in range(2,a.endpoint+1):
            verify();c.play(target);last=target;read_status('turn-'+str(target))
            write_json(out/'progress.json',dict(turn=last,endpoint=a.endpoint,unix=time.time()))
        c.cmd("assert(CSCBridgeDisable()==1);",'CSC_AI_WorkshopBridge','disable-package-policy')
        value=read_status('disabled')
        if value['enabled']!=0:raise RuntimeError('Disable failed')
        if a.recreate_observe:
            retired_generation=value['generation']
            s.issue_once('retire-first-context','Events.ExitToMainMenu();','PlotInfo')
            s.wait_context('MainMenu',180)
            phase=2;expected_delta=0
            s.issue_once('host-observation-context',setup(0),'MainMenu')
            s.ready_after_issue(1,('GameCore_Tuner','PlotInfo','CSC_AI_WorkshopBridge'),eligibility=gate,timeout=300)
            if observations[-1]['generation']<=retired_generation:raise RuntimeError('Context generation did not advance')
            c.study_endpoint=2
            c.play(2);last=2
            value=read_status('second-context-turn-2')
            if value['enabled'] or value['changed'] or value['entries'] or value['version']:raise RuntimeError('Old policy crossed context boundary')
            recreated=True
    except BaseException as failure:
        error=failure;write_json(out/'failure.json',dict(error=str(failure),traceback=traceback.format_exc(),last_turn=last))
    finally:
        if s.owner is not None and s.owner.poll() is None:
            try:
                s.close(restore_preferences=lambda:restore_preferences(c,out) if(out/'original-preferences.json').exists()else None,restore_package=verify)
            except BaseException as failure:
                error=error or failure;write_json(out/'cleanup-failure.json',dict(error=str(failure),traceback=traceback.format_exc()))
        for name,baseline in logs.items():
            p=a.user_root/'Logs'/name
            if p.exists():
                current,delta=read_log_delta(p,baseline)
                dest=out/'logs-closed'/name;dest.parent.mkdir(exist_ok=True);dest.write_bytes(current.data)
                write_json(dest.with_suffix(dest.suffix+'.boundary.json'),dict(initial=baseline.evidence(),current=current.evidence(),delta_bytes=len(delta)))
        write_json(out/'final-inventory.json',native_inventory())
    delivery=log_delivery(out/'logs-closed/Lua.log',a.delta);write_json(out/'log-delivery.json',delivery)
    result=dict(endpoint=last,first_world_endpoint=a.endpoint if phase==2 else last,context_recreated=recreated,closed=s.closed,error=str(error)if error else None,observations=len(observations),max_changed=max((v['changed']for v in observations),default=0),log_observed_adjustments=delivery['observed_adjustments'],native_faults=max((v['faults']for v in observations),default=0),package_unchanged=manifest(a.package)==package,CSC_unchanged=manifest(a.installed)==installed,frida_used=False,package_owned_publication=True,workshop_upload_tested=False)
    write_json(out/'result.json',result);print(json.dumps(result),flush=True)
    if error:raise error
    if a.delta and not(result['max_changed']or delivery['observed_adjustments']):raise RuntimeError('No nonzero delivery observed')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in('output','binary','user-root','package','installed'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--delta',type=int,choices=(0,256),default=0);p.add_argument('--endpoint',type=int,default=6)
    p.add_argument('--recreate-observe',action='store_true')
    run(p.parse_args())
