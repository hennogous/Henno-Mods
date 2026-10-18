"""Run the first CSC live regression slice without model decisions between cases.

Requires Civ at the main menu and an installed current CSC package. No killing
processes, screenshots, system settings or campaign mutations. Resume after a UI
barrier with the same arguments. Mutations are never retried automatically.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'adjacencies'))
import tuner


def wait_for_state(name, timeout, preferred):
    deadline = time.monotonic()+timeout
    while time.monotonic()<deadline:
        for port in dict.fromkeys([preferred,4318,4319,4320,4321]):
            tuner.PORT=port
            try:
                if name in tuner.states():
                    return port
            except (OSError,EOFError,ValueError):
                pass
        print(f'Waiting for {name}; {int(deadline-time.monotonic())}s remain', flush=True)
        time.sleep(3)
    raise TimeoutError(f'{name} unavailable. Check load/error logs or a UI barrier; no tests marked passed.')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--disposable-game',action='store_true',required=True)
    parser.add_argument('--timeout',type=int,default=360)
    parser.add_argument('--port',type=int,default=4318)
    args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=True)
    journal=args.output/'pipeline.json'
    state=json.loads(journal.read_text()) if journal.exists() else {'completed':[], 'status':'running'}
    metadata=args.output/'source-metadata.json'
    if not metadata.exists():
        root=Path(__file__).resolve().parents[3]
        paths=[root/'Civ Supply Chains/Data/CSC_Q_TAILORS.sql',
               root/'Civ Supply Chains/Lua_UI/Adjacencies/CSC_AdjacencyCore.lua',
               root/'Civ Supply Chains/Lua_UI/Adjacencies/CSC_AdjacencyGameplay.lua',
               root/'docs/content/quarters/tailors.md',
               root/'project/tests/qa/material_stacking.lua',Path(__file__),
               Path(__file__).with_name('csc_qa.py')]
        metadata.write_text(json.dumps({str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},indent=2))
    stages=[('start','MainMenu'),('materials','CSC_AdjacencyGameplay'),('save','PlotInfo'),
            ('menu','PlotInfo'),('reload','MainMenu'),('recheck','CSC_AdjacencyGameplay'),
            ('snapshot','CSC_AdjacencyGameplay'),('final-menu','PlotInfo'),('restore','MainMenu')]
    for stage, required in stages:
        if stage in state['completed']: continue
        if state.get('in_flight'):
            raise RuntimeError('Previous action has an unknown outcome: '+state['in_flight']+'. Inspect evidence before clearing in_flight in pipeline.json; mutations are never automatically retried.')
        state.update(status='waiting',waiting_for=required)
        journal.write_text(json.dumps(state,indent=2))
        try:
            port=wait_for_state(required,args.timeout,args.port)
        except TimeoutError as exc:
            state.update(status='blocked',reason=str(exc))
            journal.write_text(json.dumps(state,indent=2))
            print(str(exc),flush=True)
            return 20
        action='menu' if stage=='final-menu' else stage
        state.update(status='running',in_flight=stage)
        journal.write_text(json.dumps(state,indent=2))
        command=[sys.executable,str(Path(__file__).with_name('csc_qa.py')),action,
                 '--output',str(args.output),'--port',str(port),'--disposable-game']
        result=subprocess.run(command)
        if result.returncode:
            state.update(status='failed',reason=stage+' failed; inspect results.json')
            journal.write_text(json.dumps(state,indent=2))
            return result.returncode
        state['completed'].append(stage)
        state.pop('in_flight',None)
        journal.write_text(json.dumps(state,indent=2))
    state.update(status='passed')
    state.pop('waiting_for',None)
    journal.write_text(json.dumps(state,indent=2))
    print('PASS: native material stacking, transitions, save/reload and preference restoration',flush=True)
    return 0


if __name__=='__main__':
    raise SystemExit(main())
