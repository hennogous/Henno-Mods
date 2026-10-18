"""Dedicated archive/save variants; historical controllers remain unchanged."""
import json
import re
import shutil
import time
from paired_standard import CHECKPOINTS,read,sha
from run import SAVES,LOGS,write

class DensityMethods:
    def autoplay(self,i,target,resume=False):
        code=f"""Automation.SetActive(false);AutoplayManager.SetDisableAssertsForAutoplay(true);
    if not CSCPAIR_RETURN_GUARD then CSCPAIR_RETURN_GUARD=function() if AutoplayManager.IsActive() then local a=PlayerManager.GetAliveMajors();if a[1] then AutoplayManager.SetReturnAsPlayer(a[1]:GetID()) end end end;Events.PlayerDefeat.Add(CSCPAIR_RETURN_GUARD) end;
    AutoplayManager.SetTurns({target}-Game.GetCurrentGameTurn());AutoplayManager.SetReturnAsPlayer(PlayerManager.GetAliveMajors()[1]:GetID());AutoplayManager.SetObserveAsPlayer(-1);AutoplayManager.SetActive(true);"""
        if not resume:self.cmd(code,'GameCore_Tuner','autoplay-start',check=False)
        start=time.monotonic();last_progress=start;last_release=0;turn=-1;inactive=0;last_notice=0;failures=0
        archived={int(p.stem[-3:]) for p in (self.out/f'game-{i:02d}').glob('turn-*.json')}
        milestones={t for t in (50,100,150,200) if (self.out/f'builders-{t:03d}.json').exists()}
        while time.monotonic()-start<10800:
            time.sleep(20)
            try:
                text=self.cmd('print("CSC_SPARSE_PROGRESS",Game.GetCurrentGameTurn(),AutoplayManager.IsActive());','GameCore_Tuner','poll',wait=1)
                match=re.search(r'CSC_SPARSE_PROGRESS\s+(\d+)\s+(true|false)',text);assert match
                current=int(match.group(1));active=match.group(2)=='true';failures=0
            except (OSError,RuntimeError,KeyError,AssertionError) as exc:
                failures+=1
                write(self.out/'live-status.json',{'status':'connection-retry','last_confirmed_turn':turn,'failures':failures,'error':str(exc)[-500:]})
                if failures>=3:raise RuntimeError('Debug connection failed three times; last turn '+str(turn)) from exc
                continue
            if current!=turn:turn=current;last_progress=time.monotonic()
            write(self.out/'live-status.json',{'status':'running','turn':turn,'target':target,'autoplay':active,'updated_unix':time.time()})
            for checkpoint in CHECKPOINTS:
                if checkpoint<target and checkpoint<=turn and checkpoint not in archived:
                    self.snapshot(i,checkpoint);archived.add(checkpoint)
            for milestone in (50,100,150,200):
                if turn>=milestone and milestone not in milestones:
                    self.builder_snapshot(milestone);milestones.add(milestone)
                    self.say(f'Checkpoint {milestone} archived; native autoplay continues.')
            if not active:
                if turn<target:
                    inactive+=1
                    if inactive<=3:continue
                assert turn==target,('Autoplay endpoint',turn,target)
                self.snapshot(i,target);return
            assert turn<=target,'Autoplay overrun'
            if time.monotonic()-last_progress>60 and time.monotonic()-last_release>60:
                for state,action in [('NaturalDisasterPopup','OnLocalPlayerTurnEnd()'),('DiplomacyActionView','Close()')]:
                    if state in self.state:
                        self.cmd("if Game.GetLocalPlayer()==-1 and not ContextPtr:IsHidden() then "+action+" end;",state,'playback-release',wait=1)
                last_release=time.monotonic()
            if time.monotonic()-last_progress>600:raise RuntimeError(f'Autoplay stalled at {turn} for ten minutes')
            if time.monotonic()-last_notice>=900:self.say(f'Game {i}: turn {turn}/{target}');last_notice=time.monotonic()
        raise TimeoutError('Autoplay exceeded three hours')

    def save_checkpoint(self, i, turn):
        folder = self.out/f'game-{i:02d}'
        name = f'CSC AI density4 builder90 map {i} turn {turn:03d} 20261017'
        if turn == 250:
            closed = []
            self.states()
            for state, action in [('NaturalDisasterPopup', 'OnClose()'), ('DiplomacyActionView', 'Close()')]:
                if state not in self.state:
                    continue
                text = self.cmd("if not ContextPtr:IsHidden() then "+action+";print('CSC_TRIAL_PLAYBACK_CLOSED') end;", state, 'endpoint-playback-'+state, wait=2)
                if 'CSC_TRIAL_PLAYBACK_CLOSED' in text:
                    closed.append(state)
            text = self.cmd("assert(Game.GetCurrentGameTurn()==250 and not AutoplayManager.IsActive());local old=CSCBASE.checkpoints[250];local ok,e=pcall(function() CSCBASE.checkpoints[250]=nil;CSCBASE.snapshot(250) end);CSCBASE.checkpoints[250]=old;assert(ok,e);", 'CSC_AdjacencyGameplay', 'snapshot-settled', wait=5)
            settled = json.loads(re.search(r'CSCBASE_SNAPSHOT=([^\r\n]+)', text).group(1))
            assert settled['turn'] == 250 and not settled['errors']
            write(folder/'save-state-turn-250.json', settled)
            prior = read(folder/'turn-250.json')
            write(folder/'save-state-comparison.json', {'turn': 250, 'closed_playback_contexts': closed,
                  'first_activation_census_identical': prior == settled,
                  'changed_sections': [k for k in prior.keys() | settled.keys() if prior.get(k) != settled.get(k)],
                  'game_turn_advanced': False})
        started = time.time_ns()
        self.cmd('local s={Name='+json.dumps(name)+',Location=SaveLocations.LOCAL_STORAGE,Type=SaveTypes.SINGLE_PLAYER,IsAutosave=false,IsQuicksave=false};assert(Network.SaveGame(s)~=false);', 'PlotInfo', f'save-{i}-{turn}', wait=4)
        path = SAVES/(name+'.Civ6Save')
        for _ in range(45):
            if path.exists() and path.stat().st_mtime_ns >= started and path.stat().st_size > 0:
                stamp = (path.stat().st_size, path.stat().st_mtime_ns)
                time.sleep(1)
                if stamp == (path.stat().st_size, path.stat().st_mtime_ns):
                    break
            time.sleep(1)
        else:
            raise RuntimeError('Trial save not confirmed')
        shutil.copy2(path, folder/path.name)
        write(folder/('save.json' if turn == 250 else 'initial-save.json'), {'path': str(path), 'sha256': sha(path), 'turn': turn})
        if turn == 250:
            logs = folder/'logs'
            logs.mkdir(exist_ok=True)
            for p in LOGS.iterdir():
                if p.is_file() and p.suffix in ('.log', '.csv'):
                    shutil.copy2(p, logs/p.name)
