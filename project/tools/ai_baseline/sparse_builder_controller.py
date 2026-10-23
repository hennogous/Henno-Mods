"""Autonomous polling and archival; no model calls or gameplay decisions."""
import json
from pathlib import Path
import re
import shutil
import time
from run import Runner, LOGS, write
from paired_standard import CHECKPOINTS


class SparseBuilderMixin:
    def states(self):
        # Bound a dead connection instead of stacking the old nested retries.
        return Runner.states(self)

    def cmd(self,code,state='GameCore_Tuner',label='command',wait=2,check=True):
        if label.startswith('start-'):
            code=code.replace('ReleasePlayerParameters();',"GameConfiguration.SetValue('CSC_RESOURCE_MAP_ASSISTANCE',1);GameConfiguration.SetValue('CSC_MATERIAL_MAP_DIAGNOSTICS',false);ReleasePlayerParameters();")
        return Runner.cmd(self,code,state,label,wait,check)

    def builder_snapshot(self,turn):
        text=self.cmd(f'CSC_BUILDERS.Export({turn});','CSC_AdjacencyGameplay',f'builders-{turn}',wait=4)
        match=re.search(r'CSC_BUILDERS_SNAPSHOT=([^\r\n]+)',text);assert match
        value=json.loads(match.group(1));assert value['turn']==turn and not value['errors'],value.get('errors')
        write(self.out/f'builders-{turn:03d}.json',value)

    def restore_verified(self):
        errors=[]
        for _ in range(3):
            try:
                self.wait('MainMenu',180);self.restore();time.sleep(3);self.verify_preferences();return
            except (OSError,RuntimeError,KeyError) as exc:
                errors.append(str(exc));time.sleep(5)
        raise RuntimeError('Preference restoration could not be verified: '+repr(errors))

    def archive_failure(self):
        folder=self.out/'failure-logs';folder.mkdir(exist_ok=True)
        for path in LOGS.iterdir():
            if path.is_file():shutil.copy2(path,folder/path.name)
        auto=Path.home()/"Documents/My Games/Sid Meier's Civilization VI/Saves/Single/auto"
        folder=self.out/'failure-autosaves';folder.mkdir(exist_ok=True)
        for path in sorted(auto.glob('*.Civ6Save'),key=lambda p:p.stat().st_mtime,reverse=True)[:3]:shutil.copy2(path,folder/path.name)

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
            for milestone in (50,100,150,200):
                if turn>=milestone and milestone not in milestones:
                    for checkpoint in CHECKPOINTS:
                        if checkpoint<=milestone and checkpoint not in archived:self.snapshot(i,checkpoint);archived.add(checkpoint)
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
