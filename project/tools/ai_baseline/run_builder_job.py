"""Run one native test and its offline comparison without assistant polling."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import time
import traceback


def main():
    sys.stdout.reconfigure(encoding='utf-8',errors='replace');sys.stderr.reconfigure(encoding='utf-8',errors='replace')
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('output','captures','baseline','previous','placement','resource-catalog'):
        p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--resume-prepared',action='store_true')
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    here=Path(__file__).resolve().parent
    def status(state,**extra):
        (a.output/'job-status.json').write_text(json.dumps({'status':state,'updated_unix':time.time(),**extra},indent=2)+'\n',encoding='utf-8')
    status('starting')
    phase='game'
    try:
        subprocess.run([sys.executable,'-u',str(here/'builder_tuning_trial.py'),
            '--output',str(a.output),'--captures',str(a.captures),'--baseline',str(a.baseline),*(['--resume-prepared'] if a.resume_prepared else [])],check=True)
        phase='analysis';status('analyzing')
        subprocess.run([sys.executable,'-X','utf8',str(here/'analyze_builder_tuning.py'),
            '--trial',str(a.output),'--baseline',str(a.baseline),'--previous',str(a.previous),
            '--placement',str(a.placement),'--resource-catalog',str(a.resource_catalog)],check=True)
        status('complete',report=str(a.output/'report.md'))
    except BaseException as exc:
        status('failed',phase=phase,error=str(exc),traceback=traceback.format_exc())
        raise


if __name__=='__main__':main()
