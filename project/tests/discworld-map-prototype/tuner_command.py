"""Journal one native API transaction; no desktop control and no mutation resend."""
import argparse,json,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'project/tools/adjacencies'))
sys.path.insert(0,str(ROOT/'project/tools/ai_baseline'))
import tuner
from full_game_controller.transport import receive_command
sys.stdout.reconfigure(encoding='utf-8',errors='replace')
OUT=Path.home()/'Desktop/Codex/discworld-prototype-20261110'
def states():
    for port in (4318,4319,4320,4321,4322):
        tuner.PORT=port
        try:
            found=tuner.states()
            if found:return port,found
        except (OSError,EOFError,ValueError):pass
    raise RuntimeError('No available FireTuner session')
def command(code,state,label):
    port,found=states();assert state in found,found
    folder=OUT/'commands';folder.mkdir(parents=True,exist_ok=True)
    tag=time.strftime('%Y%m%d-%H%M%S')+'-'+label
    (folder/(tag+'.lua')).write_text(code,encoding='utf-8')
    token='DISC_ACK_'+str(time.time_ns())
    try:
        text,ack=receive_command(code,found[state],token,port,timeout=25)
    except Exception as exc:
        (folder/(tag+'.txt')).write_text(getattr(exc,'text',str(exc)),encoding='utf-8');raise
    (folder/(tag+'.txt')).write_text(text,encoding='utf-8');print(text)
    return text
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--states',action='store_true');p.add_argument('--state',default='GameCore_Tuner');p.add_argument('--file',type=Path);p.add_argument('--lua');p.add_argument('--label',default='query');a=p.parse_args()
    if a.states:print(json.dumps(states()))
    else:command(a.file.read_text(encoding='utf-8-sig') if a.file else a.lua,a.state,a.label)
