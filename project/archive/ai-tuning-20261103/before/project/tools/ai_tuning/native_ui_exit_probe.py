"""One zero-AI UI exit regression case using the maintained native session.

Deployment is external and explicit. This driver accepts only the declared611
installation plus its single panel replacement; it never restores that fix.
Each invocation owns one source110 load, complete Core parity, UI-only exercise,
normal Menu/preferences/ExitOK cleanup, and closed-generation log validation.
"""
import ctypes
import hashlib
import json
import os
import re
import sys
import traceback
from pathlib import Path
from ctypes import wintypes

ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'project/tools/ai_baseline'),str(ROOT/'project/tools/ai_tuning')]
from native_session_probe import parser,run
from native_profile_test import manifest
from full_game_controller.probe import write_json
from full_game_controller.log_capture import capture_log_baseline,read_log_delta
from full_game_controller.windows_process import HeldProcess,native_inventory

PANEL='Lua_UI\\Lenses\\CSC_SupplyChainsLensPanel.lua'
PHASE='CSC_UI_EXIT_PHASE='


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def review_exit_log(text,scenario):
    """Closed native logs establish callback completion, never a renderer claim."""
    if scenario not in ('unopened','active-lens'):raise ValueError('Unknown case')
    if re.search(r'Runtime Error|stack traceback|Lua Error',text,re.I):
        raise ValueError('Native Lua error in this fresh closed generation')
    lines=[line.split('CSC Lenses: ',1)[1]for line in text.splitlines()if 'CSC Lenses: 'in line]
    if sum('loaded; quarters='in line for line in lines)!=1:
        raise ValueError('Expected exactly one fresh lens context generation')
    begin=[i for i,line in enumerate(lines)if line.startswith('shutdown begin ')]
    end=[i for i,line in enumerate(lines)if line=='shutdown complete']
    if len(begin)!=1 or len(end)!=1 or begin[0]>=end[0]:
        raise ValueError('Shutdown did not complete once in the captured generation')
    if any(line.startswith(('entry check begin ','choice check begin ','choice init begin '))for line in lines[begin[0]+1:]):
        raise ValueError('Native radio SetCheck initiated during/after shutdown')
    if not any(line.startswith('entry check skipped during shutdown ')for line in lines[begin[0]:end[0]+1]):
        raise ValueError('Missing declared shutdown skip evidence')
    balances={'entry':0,'choice':0,'init':0}
    for line in lines:
        for key,b,e in [('entry','entry check begin ','entry check end '),('choice','choice check begin ','choice check end '),('init','choice init begin ','choice init end ')]:
            if line.startswith(b):balances[key]+=1
            if line.startswith(e):balances[key]-=1
            if balances[key]<0:raise ValueError('Unmatched radio completion marker')
    if any(balances.values()):raise ValueError('Uncompleted radio operation marker')
    phases=[json.loads(m)for m in re.findall(re.escape(PHASE)+r'([^\r\n]+)',text)]
    expected=['initial-unopened','final-unopened']if scenario=='unopened'else['initial-unopened','opened-BAKERS','switched-TAILORS','closed-selection','reopened-BAKERS','final-active']
    if [p['phase']for p in phases]!=expected:raise ValueError('Missing, repeated or unordered UI scenario phases')
    if any(p['turn']!=110 for p in phases):raise ValueError('UI scenario clock changed')
    return dict(verified=True,scenario=scenario,phases=phases,shutdown_begin=lines[begin[0]],
                shutdown_complete=True,radio_markers_balanced=True,
                radio_calls_after_shutdown=0,renderer_visual_validation=False)


def ui_readback(phase,active):
    # All methods below are already used by the exact panel source. No local
    # PlayerConfigurations methods are assumed in the GameCore context.
    expected='true'if active else'false'
    return ("local checked=Controls.SupplyChainsLensEntry:IsChecked()==true;"
            "local visible=Controls.SupplyChainsLensPanel:IsVisible();"
            "local modal=UI.GetInterfaceMode()==InterfaceModeTypes.VIEW_MODAL_LENS;"
            "assert(checked=="+expected+" and visible=="+expected+" and modal=="+expected+",'UI scenario state did not settle');"
            "local turn=Game.GetCurrentGameTurn();assert(turn==110);"
            "print('"+PHASE+"{\"phase\":\""+phase+"\",\"turn\":'..turn..',\"checked\":'..tostring(checked)..',\"visible\":'..tostring(visible)..',\"modal\":'..tostring(modal)..'}');")


def preserve_native_failure(output):
    """Read actual remaining owner/window evidence; one small dump, no control."""
    out=Path(output);owner_file=out/'session-owner.json'
    if not owner_file.exists():return
    expected=json.loads(owner_file.read_text());rows=native_inventory()
    write_json(out/'failure-owner-inventory.json',rows)
    matching=[r for r in rows if r.get('identity')==expected]
    if len(matching)!=1:return
    held=HeldProcess(expected['pid'])
    try:
        if held.identity!=expected or held.poll()is not None:return
        user=ctypes.WinDLL('user32',use_last_error=True);cbtype=ctypes.WINFUNCTYPE(wintypes.BOOL,wintypes.HWND,wintypes.LPARAM)
        user.GetWindowThreadProcessId.argtypes=[wintypes.HWND,ctypes.POINTER(wintypes.DWORD)];user.GetWindowThreadProcessId.restype=wintypes.DWORD
        user.GetWindowTextW.argtypes=[wintypes.HWND,wintypes.LPWSTR,ctypes.c_int];user.GetWindowTextW.restype=ctypes.c_int
        user.GetClassNameW.argtypes=[wintypes.HWND,wintypes.LPWSTR,ctypes.c_int];user.GetClassNameW.restype=ctypes.c_int
        user.EnumWindows.argtypes=[cbtype,wintypes.LPARAM];user.EnumChildWindows.argtypes=[wintypes.HWND,cbtype,wintypes.LPARAM]
        windows=[]
        def item(hwnd):
            pid=wintypes.DWORD();tid=user.GetWindowThreadProcessId(hwnd,ctypes.byref(pid));text=ctypes.create_unicode_buffer(8192);cls=ctypes.create_unicode_buffer(256)
            user.GetWindowTextW(hwnd,text,len(text));user.GetClassNameW(hwnd,cls,len(cls))
            return dict(hwnd=hex(hwnd),pid=pid.value,thread=tid,text=text.value,class_name=cls.value)
        @cbtype
        def top(hwnd,param):
            row=item(hwnd)
            if row['pid']==held.pid:
                row['children']=[]
                @cbtype
                def child(ch,param):row['children'].append(item(ch));return True
                user.EnumChildWindows(hwnd,child,0);windows.append(row)
            return True
        user.EnumWindows(top,0)
        write_json(out/'failure-window-metadata.json',dict(identity=expected,windows=windows,read_only=True,controls_invoked=0))
        # Capture post-failure contexts/stacks only; no observer/injection/fullRAM.
        import msvcrt
        kernel=ctypes.WinDLL('kernel32',use_last_error=True);kernel.OpenProcess.argtypes=[wintypes.DWORD,wintypes.BOOL,wintypes.DWORD];kernel.OpenProcess.restype=wintypes.HANDLE
        kernel.CloseHandle.argtypes=[wintypes.HANDLE]
        handle=kernel.OpenProcess(0x410,False,held.pid)
        if not handle:raise ctypes.WinError(ctypes.get_last_error())
        try:
            dbg=ctypes.WinDLL('DbgHelp',use_last_error=True);dbg.MiniDumpWriteDump.argtypes=[wintypes.HANDLE,wintypes.DWORD,wintypes.HANDLE,wintypes.DWORD,ctypes.c_void_p,ctypes.c_void_p,ctypes.c_void_p];dbg.MiniDumpWriteDump.restype=wintypes.BOOL
            target=out/'native-failure-small.dmp'
            with target.open('xb')as stream:
                ok=dbg.MiniDumpWriteDump(handle,held.pid,msvcrt.get_osfhandle(stream.fileno()),0x1120,None,None,None)
                error=ctypes.get_last_error()if not ok else 0;stream.flush();os.fsync(stream.fileno())
            write_json(out/'native-failure-dump.json',dict(identity=expected,success=bool(ok),error=error,flags='0x1120',bytes=target.stat().st_size,sha256=sha(target),injection=False,forced_exit=False))
        finally:kernel.CloseHandle(handle)
    finally:held.close()


def main():
    p=parser()
    p.add_argument('--candidate',type=Path,required=True)
    p.add_argument('--baseline-panel',type=Path,required=True)
    p.add_argument('--baseline-installed',type=Path,required=True)
    p.add_argument('--source-panel',type=Path,required=True)
    p.add_argument('--logs',type=Path,required=True)
    p.add_argument('--scenario',choices=('unopened','active-lens'),required=True)
    a=p.parse_args()
    if a.turn!=110 or a.reference_key:raise ValueError('Require the entire declared source110 Core reference')
    baseline=json.loads(a.baseline_installed.read_text(encoding='utf-8-sig'))
    actual=manifest(a.installed)
    if len(actual)!=611 or actual.keys()!=baseline.keys():raise ValueError('Package inventory changed')
    changed=[key for key in actual if actual[key]!=baseline[key]]
    if changed!=[PANEL]:raise ValueError('Require exactly the declared panel delta: '+repr(changed))
    if baseline[PANEL]['sha256']!=sha(a.baseline_panel):raise ValueError('Baseline panel mismatch')
    if actual[PANEL]['sha256']!=sha(a.candidate)or sha(a.source_panel)!=sha(a.candidate):raise ValueError('Candidate is not the exact source/installed panel')
    boundary=None
    def capture(r,out,label):
        nonlocal boundary
        if label=='shadow-initial':
            boundary=capture_log_baseline(a.logs/'Lua.log')
            if not boundary.existed:raise RuntimeError('Fresh loaded native Lua.log missing')
            (out/'lua-loaded-prefix.log').write_bytes(boundary.data)
            write_json(out/'lua-loaded-boundary.json',boundary.evidence())
            r.cmd(ui_readback('initial-unopened',False),'CSC_SupplyChainsLensPanel','UI-initial-unopened')
            if a.scenario=='active-lens':
                for code,phase,active in [
                    ("LuaEvents.CSC_SupplyChainsLens_OpenPanel('BAKERS');",'opened-BAKERS',True),
                    ("LuaEvents.CSC_SupplyChainsLens_OpenPanel('TAILORS');",'switched-TAILORS',True),
                    ('UI.SetInterfaceMode(InterfaceModeTypes.SELECTION);','closed-selection',False),
                    ("LuaEvents.CSC_SupplyChainsLens_OpenPanel('BAKERS');",'reopened-BAKERS',True)]:
                    r.cmd(code,'CSC_SupplyChainsLensPanel','UI-'+phase+'-once')
                    r.ready(110,'UI-'+phase+'-Core-boundary')
                    r.cmd(ui_readback(phase,active),'CSC_SupplyChainsLensPanel','UI-'+phase+'-readback')
        else:
            r.cmd(ui_readback('final-active'if a.scenario=='active-lens'else'final-unopened',a.scenario=='active-lens'),'CSC_SupplyChainsLensPanel','UI-final-readback')
    failure=None
    try:
        run(a,capture=capture,extra_pins=(Path(__file__),Path(__file__).with_name('test_native_ui_exit.py'),a.candidate,a.baseline_panel,a.baseline_installed,a.source_panel))
    except BaseException as error:
        failure=error
        if a.output.exists():
            try:preserve_native_failure(a.output)
            except BaseException as diagnostic_error:write_json(a.output/'failure-diagnostic-error.json',dict(error=str(diagnostic_error),traceback=traceback.format_exc()))
    finally:
        if a.output.exists():
            for name in ('Lua.log','Database.log','UserInterface.log','Engine.log'):
                path=a.logs/name
                if path.exists():
                    target=a.output/'closed-logs'/name;target.parent.mkdir(exist_ok=True);target.write_bytes(path.read_bytes())
    if failure is not None:raise failure
    if boundary is None:raise RuntimeError('Missing loaded log boundary')
    closed,delta=read_log_delta(a.logs/'Lua.log',boundary)
    write_json(a.output/'lua-closed-boundary.json',dict(before=boundary.evidence(),after=closed.evidence(),tail_bytes=len(delta)))
    result=review_exit_log(closed.data.decode('utf-8',errors='replace'),a.scenario)
    result.update(dict(candidate_kept_installed=True,only_installed_delta=PANEL,AI_turns=0,source_loads=1,
                       full_Core_initial_final_equal=True,normal_native_exit0=True,preferences_restored=True,owners_absent=True))
    write_json(a.output/'UI-exit-result.json',result)
    print(json.dumps(result),flush=True)


if __name__=='__main__':main()
