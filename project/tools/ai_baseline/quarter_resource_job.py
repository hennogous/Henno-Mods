"""Background game/analysis supervisor; no model polling or automatic reruns."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time
import traceback


def main():
    sys.stdout.reconfigure(encoding='utf-8',errors='replace');sys.stderr.reconfigure(encoding='utf-8',errors='replace')
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('output','captures','baseline','previous'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--resume-from',type=Path)
    p.add_argument('--improvement-research',action='store_true')
    p.add_argument('--resume-setup',type=Path)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True);here=Path(__file__).resolve().parent
    def status(state,**extra):
        target=a.output/'job-status.json';temp=a.output/'job-status.tmp'
        temp.write_text(json.dumps({'status':state,'updated_unix':time.time(),**extra},indent=2)+'\n',encoding='utf-8');temp.replace(target)
    phase='game';status('starting');child=None
    try:
        worker='improvement_research_trial.py' if a.improvement_research else ('quarter_resource_resume.py' if a.resume_from else 'quarter_resource_trial.py')
        args=[sys.executable,'-X','utf8','-u',str(here/worker)]
        for name in ('output','captures','baseline','previous'):args+=['--'+name,str(getattr(a,name))]
        if a.resume_from:args+=['--resume-from',str(a.resume_from)]
        if a.resume_setup:args+=['--resume-setup',str(a.resume_setup)]
        child=subprocess.Popen(args);missing=0
        while child.poll() is None:
            time.sleep(30)
            if child.poll() is not None:break
            try:
                result=subprocess.run(['tasklist','/FO','CSV','/NH'],capture_output=True,text=True,timeout=10,creationflags=subprocess.CREATE_NO_WINDOW)
                missing=0 if any(name in result.stdout.lower() for name in ('civilizationvi.exe','civilizationvi_dx12.exe')) else missing+1
            except subprocess.TimeoutExpired:continue
            if missing>=2:
                child.terminate();child.wait(timeout=20)
                raise RuntimeError('Civ process absent on two checks; worker stopped, no restart attempted')
        if child.returncode:raise RuntimeError('Native test worker exited '+str(child.returncode))
        phase='analysis';status('analyzing')
        analysis='improvement_research_analyze.py' if a.improvement_research else 'quarter_resource_analyze.py'
        subprocess.run([sys.executable,'-X','utf8',str(here/analysis),'--trial',str(a.output),'--previous',str(a.previous)],check=True)
        status('complete',report=str(a.output/'report.md'))
    except BaseException as exc:
        logs=Path.home()/"AppData/Local/Firaxis Games/Sid Meier's Civilization VI/Logs"
        dest=a.output/'supervisor-failure-logs';dest.mkdir(exist_ok=True)
        for path in logs.glob('*'):
            if path.is_file():shutil.copy2(path,dest/path.name)
        auto=Path.home()/"Documents/My Games/Sid Meier's Civilization VI/Saves/Single/auto"
        dest=a.output/'failure-autosaves';dest.mkdir(exist_ok=True)
        for path in sorted(auto.glob('*.Civ6Save'),key=lambda p:p.stat().st_mtime,reverse=True)[:3]:shutil.copy2(path,dest/path.name)
        if phase=='game' and not (a.output/'preferences-restored.json').exists():
            (a.output/'cleanup-required.json').write_text(json.dumps({'reason':'Original mod preferences may need restoration after interrupted test'})+'\n',encoding='utf-8')
        status('failed',phase=phase,error=str(exc),traceback=traceback.format_exc())
        raise

if __name__=='__main__':main()
