"""Recover game3 endpoint state, explicitly retaining its known event gap."""
import json
from pathlib import Path
import re
from run import Runner,write
from continue_saved import read,sha

def main():
    out=Path.home()/'Desktop/Codex/csc-ai-baseline-turn400-20261016';r=Runner(out);folder=out/'game-03'
    saved=read(folder/'save.json');path=folder/Path(saved['path']).name;assert sha(path)==saved['sha256']
    r.config();r.cmd(f'Automation.SetAutoStartEnabled(true);Network.LoadGame({json.dumps(str(path))},ServerType.SERVER_TYPE_NONE);','MainMenu','recover-load-3',wait=3,check=False)
    r.wait('CSC_AdjacencyGameplay',300)
    r.cmd(Path(__file__).with_name('observer.lua').read_text(encoding='utf-8'),'CSC_AdjacencyGameplay','recover-observer-3',wait=4)
    text=r.cmd('CSCBASE.snapshot();','CSC_AdjacencyGameplay','recover-endpoint-3',wait=5)
    s=json.loads(re.search(r'CSCBASE_SNAPSHOT=([^\r\n]+)',text).group(1));assert s['turn']==400 and not s['errors']
    s['events']=read(folder/'turn-375.json')['events'];s['event_history_gap']={'after_turn':375,'through_turn':400,'reason':'Endpoint was saved before observer export during controller changeover'}
    write(folder/'turn-400.json',s);write(folder/'complete.json',{'turn':400,'status':'complete_with_event_gap','event_history_gap':s['event_history_gap']})
    r.say('Recovered exact game3 turn400 state; event gap375-400 explicitly recorded')
    r.menu();r.restore()

if __name__=='__main__':main()
