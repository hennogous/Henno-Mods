"""Run the Lua-only CE capability package with the shared native controller."""
import argparse,json,sys,traceback,hashlib,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
sys.path[:0]=[str(HERE.parent),str(ROOT/'project/tools/ai_baseline')]
from run_smoke import setup
from full_game_controller.probe import make_probe_controller
from full_game_controller.session import NativeSession
from full_game_controller.windows_process import HeldProcess,native_inventory
from full_game_controller.environment import launch,configure,flags,manifest,restore_preferences,write_json,archive_sources
from full_game_controller.log_capture import capture_log_baseline,read_log_delta
MOD='d0f3a2ab-4fa6-4a7a-bf9b-b82a66fe2a05'
CE='3351473b-0746-417a-a618-2b66a04d8f3d'
CSC='c5e66bd1-d804-443b-ac3d-1917a20dba3c'
GAME_SHA='324c51e9ea3531758842e16c69e6cddbefbb226c5b675c3d6e60111646c2e98c'
CE_SHA='36ba871516326878984dac0d1903a08a48490ad386516cca4910c83f846f662f'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run(a):
    out=a.output.resolve()
    if out.exists()or native_inventory():raise RuntimeError('Fresh output and no native/Tuner owner required')
    out.mkdir(parents=True)
    roots=[a.package,a.installed,a.ce]
    before={str(p):manifest(p)for p in roots}
    paths=list(HERE.glob('*'));paths=[p for p in paths if p.is_file()]
    paths+=[HERE.parent/'run_smoke.py']+list((ROOT/'project/tools/ai_baseline/full_game_controller').glob('*.py'))+list((ROOT/'project/tools/ai_baseline/full_game_controller').glob('*.lua'))
    pins={str(p.resolve()):sha(p)for p in paths}
    write_json(out/'pins.json',pins);write_json(out/'source-archive.json',archive_sources(pins,out/'source-version'));write_json(out/'before.json',before)
    c=make_probe_controller(out,user_root=a.user_root);c.study_endpoint=3
    c.allow_observer_warning_dismissal=c.allow_observer_first_meet_dismissal=c.allow_observer_congress_review=True
    s=NativeSession(out,c,inventory=native_inventory,hold=HeldProcess,write=write_json)
    logs={};error=None;last=None
    def verify():
        if any(sha(p)!=v for p,v in pins.items()):raise RuntimeError('Frozen source changed')
        if any(manifest(p)!=before[str(p)]for p in roots):raise RuntimeError('Installed content changed')
    def gate():
        nonlocal last
        last=1
        c.cmd("assert(Game.GetCurrentGameTurn()==1 and Players[0]:IsHuman());assert(type(Mem)=='function'and type(ObjMem)=='function');print('CE_SCORE_API',type(CE_AIDistrictScoresBegin),type(CE_AIDistrictScoresStatus));",'CSC_CE_Probe','CE-capability-query')
        return True
    try:
        verify();s.start(lambda:launch(a,out));s.wait_context('MainMenu');configure(c,out,'BASIC')
        selected_subscription='' if a.ce_subscription=='local'else a.ce_subscription
        c.cmd("local ce=nil;for _,m in ipairs(Modding.GetInstalledMods())do if m.Id=='"+CE+"'and tostring(m.SubscriptionId or '')=='"+selected_subscription+"'then assert(not ce);ce=m end end;assert(ce,'Missing selected CE entry');Modding.EnableMod(ce.Handle,true);",'MainMenu','enable-selected-CE')
        s.wait_context('MainMenu',90)
        # Enabling a dependency rebuilds the menu mod collection. Resolve the
        # dependent package's current handle only after that transition.
        flags(c,'verify-CE-before-probe')
        c.cmd("local probe=nil;for _,m in ipairs(Modding.GetInstalledMods())do if m.Id=='"+MOD+"'then assert(not probe);probe=m end end;assert(probe,'Missing probe');local err,xtra=Modding.CanEnableMod(probe.Handle);print('CE_PROBE_CAN_ENABLE',err);if type(xtra)=='table'then for k,v in pairs(xtra)do print('CE_PROBE_ENABLE_DETAIL',k,type(v));if type(v)=='table'then for a,b in pairs(v)do print('CE_PROBE_ENABLE_FIELD',a,tostring(b))end end end end;assert(err=='OK','Probe eligibility: '..tostring(err));Modding.EnableMod(probe.Handle);",'MainMenu','enable-probe-after-CE')
        s.wait_context('MainMenu',90)
        selected=flags(c,'verify-CE-probe-set')
        if {k for k,v in selected['mods'].items()if v}!={CSC,CE,MOD}:raise RuntimeError('Unexpected mod set')
        activeCE=[v for v in selected['entries']if v['id']==CE and v['enabled']]
        if len(activeCE)!=1 or activeCE[0]['subscription']!=selected_subscription:raise RuntimeError('Wrong CE subscription')
        for name in('Lua.log','Database.log','Modding.log','AI_CityBuild.csv'):
            logs[name]=capture_log_baseline(a.user_root/'Logs'/name)
        s.issue_once('host-CE-probe',setup(0),'MainMenu')
        s.ready_after_issue(1,('GameCore_Tuner','PlotInfo','CSC_CE_Probe'),eligibility=gate,timeout=300)
        code="Get-Process -Id "+str(s.owner.pid)+" -ErrorAction Stop | ForEach-Object {$_.Modules} | Where-Object {$_.ModuleName -match 'GameCore_XP2'} | Select-Object ModuleName,FileName | ConvertTo-Json -Compress"
        modules=json.loads(subprocess.check_output(['powershell','-NoProfile','-Command',code],text=True,creationflags=subprocess.CREATE_NO_WINDOW))
        if isinstance(modules,dict):modules=[modules]
        expected={'GameCore_XP2_CE_FinalRelease.dll':CE_SHA,'GameCore_XP2_FinalRelease.dll':GAME_SHA}
        if {v['ModuleName']for v in modules}!=set(expected):raise RuntimeError('Unexpected native carrier set')
        for m in modules:
            if sha(m['FileName'])!=expected[m['ModuleName']]:raise RuntimeError('Loaded module hash mismatch')
            if m['ModuleName']=='GameCore_XP2_CE_FinalRelease.dll'and Path(m['FileName']).resolve()!=(a.ce/'Binaries/Win64/GameCore_XP2_CE_FinalRelease.dll').resolve():raise RuntimeError('Wrong CE module path')
        write_json(out/'loaded-modules.json',modules)
        for turn in(2,3):verify();c.play(turn);last=turn;write_json(out/'progress.json',dict(turn=last))
    except BaseException as failure:
        error=failure;write_json(out/'failure.json',dict(error=str(failure),traceback=traceback.format_exc(),last_turn=last))
    finally:
        if s.owner is not None and s.owner.poll()is None:
            try:s.close(restore_preferences=lambda:restore_preferences(c,out)if(out/'original-preferences.json').exists()else None,restore_package=verify)
            except BaseException as failure:error=error or failure;write_json(out/'cleanup-failure.json',dict(error=str(failure),traceback=traceback.format_exc()))
        for name,baseline in logs.items():
            path=a.user_root/'Logs'/name
            if path.exists():
                current,delta=read_log_delta(path,baseline);dest=out/'logs-closed'/name;dest.parent.mkdir(exist_ok=True);dest.write_bytes(current.data)
                write_json(dest.with_suffix(dest.suffix+'.boundary.json'),dict(initial=baseline.evidence(),current=current.evidence(),delta_bytes=len(delta)))
        write_json(out/'final-inventory.json',native_inventory())
    text=(out/'logs-closed/Lua.log').read_text(encoding='utf-8',errors='replace')if(out/'logs-closed/Lua.log').exists()else''
    rows=[dict(line=n,text=t)for n,t in enumerate(text.splitlines(),1)if'[CSC_CE_PROBE]'in t]
    write_json(out/'probe-receipts.json',rows)
    result=dict(closed=s.closed,endpoint=last,error=str(error)if error else None,own_DLL=False,frida=False,probe_memory_writes=0,receipts=len(rows),city_receipts=sum('kind=city'in v['text']for v in rows),score_receipts=sum('kind=score'in v['text']for v in rows),disabled_receipts=[v for v in rows if'kind=disabled'in v['text']],installed_unchanged=all(manifest(p)==before[str(p)]for p in roots),safe_score_write_window_proved=False)
    write_json(out/'result.json',result);print(json.dumps(result),flush=True)
    if error:raise error
    if result['disabled_receipts']or not result['city_receipts']:raise RuntimeError('CE cache probe did not qualify')
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in('output','binary','user-root','package','installed','ce'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--ce-subscription',default='3277976174',help='Exact Workshop ID, or local for an existing local copy')
    run(p.parse_args())
