"""Supervise one Medieval-start natural game; never restart a failed game."""
import argparse,json,subprocess,sys,time,shutil,traceback
from pathlib import Path
from run import write,SAVES,LOGS

def main():
 p=argparse.ArgumentParser()
 for n in ('output','captures','baseline','previous','mechanism'):p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
 args=[sys.executable,'-X','utf8','-u',str(Path(__file__).with_name('research_priorities_trial.py')),'--phase','natural']
 for n in ('output','captures','baseline','previous','mechanism'):args+=['--'+n,str(getattr(a,n))]
 child=None
 try:
  child=subprocess.Popen(args);write(a.output/'supervisor.json',{'status':'running','worker_pid':child.pid})
  missing=0
  while child.poll() is None:
   time.sleep(30)
   if child.poll() is not None:break
   try:
    task=subprocess.run(['tasklist','/FO','CSV','/NH'],capture_output=True,text=True,timeout=10,creationflags=subprocess.CREATE_NO_WINDOW)
    missing=0 if any(x in task.stdout.lower() for x in ('civilizationvi.exe','civilizationvi_dx12.exe')) else missing+1
   except subprocess.TimeoutExpired:continue
   if missing>=2:
    child.terminate();child.wait(timeout=20);raise RuntimeError('Civ exited; stopped worker, no automatic restart')
  assert child.returncode==0,'Worker exit '+str(child.returncode)
  assert json.loads((a.output/'job-status.json').read_text())['status']=='complete'
  write(a.output/'supervisor.json',{'status':'complete','worker_pid':child.pid})
 except BaseException as exc:
  dest=a.output/'supervisor-failure-logs';dest.mkdir(exist_ok=True)
  for f in LOGS.iterdir():
   if f.is_file():shutil.copy2(f,dest/f.name)
  dest=a.output/'failure-autosaves';dest.mkdir(exist_ok=True)
  for f in sorted((SAVES/'auto').glob('*.Civ6Save'),key=lambda f:f.stat().st_mtime,reverse=True)[:3]:shutil.copy2(f,dest/f.name)
  write(a.output/'supervisor.json',{'status':'failed','error':str(exc),'traceback':traceback.format_exc()})
  if not (a.output/'preferences-restored.json').exists():write(a.output/'cleanup-required.json',{'reason':'Check original-preferences.json and restore when native main menu is available.'})
  raise
if __name__=='__main__':main()
