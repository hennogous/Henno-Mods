"""Hidden supervisor for ONE authorized OFF/ON natural comparison. No restarts."""
import argparse
import csv
import json
import shutil
import subprocess
import sys
import time
import traceback
from pathlib import Path
from run import LOGS,SAVES,write


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--continue-study',action='store_true');a=p.parse_args()
    a.output.mkdir(parents=True,exist_ok=a.continue_study)
    child=None
    try:
        args=[sys.executable,'-X','utf8','-u',str(Path(__file__).with_name('civic_guidance_long_trial.py')),'--output',str(a.output/'study')]
        if a.continue_study:args.append('--continue-study')
        child=subprocess.Popen(args)
        write(a.output/'supervisor.json',{'status':'running','worker_pid':child.pid,'one_off_on_pair_only':True})
        absent=0
        while child.poll() is None:
            time.sleep(30)
            if child.poll() is not None:break
            try:
                result=subprocess.run(['tasklist','/FO','CSV','/NH'],capture_output=True,text=True,timeout=12,creationflags=subprocess.CREATE_NO_WINDOW)
                names={row[0].lower() for row in csv.reader(result.stdout.splitlines()) if row}
                absent=0 if names.intersection({'civilizationvi.exe','civilizationvi_dx12.exe'}) else absent+1
            except subprocess.TimeoutExpired:continue
            if absent>=2:
                child.terminate();child.wait(timeout=20);raise RuntimeError('Civ process exited; worker stopped, no restart')
        assert child.returncode==0,'Worker exit '+str(child.returncode)
        state=json.loads((a.output/'study/job-status.json').read_text())
        assert state['status']=='complete'
        write(a.output/'supervisor.json',{'status':'complete','worker_pid':child.pid,'one_off_on_pair_only':True})
    except BaseException as exc:
        if child and child.poll() is None:child.terminate();child.wait(timeout=20)
        dest=a.output/'supervisor-failure-logs';dest.mkdir(exist_ok=True)
        for f in LOGS.iterdir():
            if f.is_file():shutil.copy2(f,dest/f.name)
        dest=a.output/'failure-autosaves';dest.mkdir(exist_ok=True)
        for f in sorted((SAVES/'auto').glob('*.Civ6Save'),key=lambda p:p.stat().st_mtime,reverse=True)[:3]:shutil.copy2(f,dest/f.name)
        installed=Path.home()/"Documents/My Games/Sid Meier's Civilization VI/Mods/Civ Supply Chains"
        originals=a.output/'study/original-installed'
        restored={}
        if originals.exists():
            for f in originals.rglob('*'):
                if f.is_file():
                    rel=f.relative_to(originals);shutil.copy2(f,installed/rel);restored[str(rel)]=(installed/rel).read_bytes()==f.read_bytes()
        write(a.output/'supervisor.json',{'status':'failed','error':str(exc),'traceback':traceback.format_exc(),'installed_files_restored':restored})
        # Worker normally restores native preferences itself. If process death
        # prevented it, preserve original-preferences and request bounded cleanup.
        pending=[str(x.parent) for x in (a.output/'study').glob('*/original-preferences.json') if not(x.parent/'preferences-restored.json').exists()]
        if pending:write(a.output/'cleanup-required.json',{'native_preferences_pending':pending,'no_automatic_game_restart':True})
        raise


if __name__=='__main__':main()
