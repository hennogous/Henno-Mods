"""Native bonus/river candidate: one isolated AI-tuning game using the paired baseline's native controller.

The original baseline and its source pins are never edited. Outputs, saves and
preferences belong to this trial. The observer is unchanged and read-only.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys
import time
import traceback

from paired_standard import PairedRunner, CHECKPOINTS, read, sha, verify
from run import ROOT, SAVES, LOGS, write


class TrialRunner(PairedRunner):
    def pin_sources(self):
        super().pin_sources()
        paths = [Path(__file__), ROOT/'Civ Supply Chains/Data/CSC_AI.sql',
                 *list((ROOT/'Civ Supply Chains/Lua_UI/AI').glob('*.lua'))]
        write(self.out/'tuning-source-hashes.json', {str(p): sha(p) for p in paths})

    def start_pair(self, i, resume_map=False):
        super().start_pair(i, resume_map)
        folder = self.out/f'game-{i:02d}'
        settings = read(folder/'settings.json')
        settings['ai'] = 'standard + CSC native bonus-resource/river placement signals v3'
        settings['comparison'] = str(self.baseline/f'game-{i:02d}')
        write(folder/'settings.json', settings)
        self.cmd("local n=0;for r in GameInfo.AiFavoredItems() do if r.ListType=='CSC_AI_ImprovementPriorities' then assert(r.Item=='PSEUDOYIELD_IMPROVEMENT' and r.Value==50);n=n+1 end end;assert(n==1);print('CSC_AI_NATIVE_V3_LOADED',n);",
                 'CSC_AdjacencyGameplay', 'tuning-loaded', wait=3)
        self.cmd("assert(GameInfo.Adjacency_YieldChanges['CSC_AI_BONUS_RESOURCE'].AdjacentResourceClass=='RESOURCECLASS_BONUS');assert(GameInfo.Adjacency_YieldChanges['CSC_AI_BONUS_RESOURCE'].YieldChange==12);assert(GameInfo.Adjacency_YieldChanges['CSC_AI_RIVER'].AdjacentRiver and GameInfo.Adjacency_YieldChanges['CSC_AI_RIVER'].YieldChange==4);for row in GameInfo.Features() do assert(not row.FeatureType:match('^FEATURE_CSC_AI_RESOURCE_')) end;for row in GameInfo.Modifiers() do assert(not row.ModifierId:match('^MOD_CSC_AI_MATERIAL_')) end;print('CSC_AI_NATIVE_V3_RULES_PASSED');", 'CSC_AdjacencyGameplay', 'native-rule-smoke', wait=3)
        import subprocess
        subprocess.run([sys.executable,str(Path(__file__).with_name('validate_tuning.py')),'--loaded','--output',str(self.out/'native-database-validation.json')],check=True)
        self.cmd("assert(GameInfo.Technologies['TECH_CSC_AI_PLACEMENT']==nil);local n=0;for r in GameInfo.Yields() do if r.YieldType=='YIELD_CSC_AI_PLACEMENT' then n=n+1 end end;assert(n==1);print('CSC_AI_GAMEPLAY_SIGNAL_VISIBLE');", 'CSC_AdjacencyGameplay', 'native-signal-database', wait=3)
        code="assert(CSC_AI_UIFilterInstalled);local n=0;for r in GameInfo.Yields() do assert(r.YieldType~='YIELD_CSC_AI_PLACEMENT');n=n+1 end;assert(n==6,n);local r=assert(GameInfo.Yields['YIELD_CSC_AI_PLACEMENT']);assert(GameInfo.Yields[r.Index].YieldType==r.YieldType);for a in GameInfo.District_Adjacencies() do assert(GameInfo.Adjacency_YieldChanges[a.YieldChangeId].YieldType~='YIELD_CSC_AI_PLACEMENT') end;print('CSC_AI_UI_FILTER_PASSED',n);"
        for state in ('PlotInfo','PlotToolTip','ReportScreen','CivilopediaScreen'):
            self.cmd(code,state,'ui-filter-'+state,wait=2)
        text=self.cmd(Path(__file__).with_name('native_guidance_probe.lua').read_text(encoding='utf-8'),'PlotInfo','native-guidance-initial',wait=8)
        match=re.search(r'CSC_AI_NATIVE_GUIDANCE=([^\r\n]+)',text);assert match
        write(self.out/'native-guidance-initial.json',json.loads(match.group(1)))


    def save_checkpoint(self, i, turn):
        folder = self.out/f'game-{i:02d}'
        name = f'CSC AI native bonus river v3 map {i} turn {turn:03d} 20261017'
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

    def verify_preferences(self):
        original = read(self.out/'original-preferences.json')
        entries = ','.join('['+json.dumps(k)+']='+str(v).lower() for k, v in original['mods'].items())
        code = 'local wanted={'+entries+'};local seen={};for _,m in ipairs(Modding.GetInstalledMods()) do if wanted[m.Id]~=nil then assert(m.Enabled==wanted[m.Id],m.Id);seen[m.Id]=true end end;for id in pairs(wanted) do assert(seen[id],id) end;assert(Automation.IsAutoStartEnabled()=='+str(original['auto_start']).lower()+");print('CSC_TRIAL_PREFS_VERIFIED');"
        self.cmd(code, 'MainMenu', 'verify-restored-preferences', wait=3)
        write(self.out/'preferences-restored.json', {'verified': True, 'unique_mods': len(original['mods']), 'auto_start': original['auto_start']})


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--captures', type=Path, required=True)
    p.add_argument('--baseline', type=Path, required=True)
    p.add_argument('--map', type=int, default=1, choices=range(1, 6))
    p.add_argument('--resume-running', action='store_true')
    p.add_argument('--restore-only', action='store_true')
    a = p.parse_args()
    r = TrialRunner(a.output)
    r.captures, r.baseline, r.keep_game = a.captures, a.baseline, False
    if a.restore_only:
        r.wait('MainMenu')
        r.restore()
        r.verify_preferences()
        return
    r.pin_sources()
    if not a.resume_running:
        r.wait('MainMenu')
        r.config()
        original = read(a.baseline/'installed-gameplay-hashes.json')
        current = read(a.output/'installed-gameplay-hashes.json')
        changed = [n for n, h in original.items() if current.get(n) != h]
        added = sorted(current.keys() - original.keys())
        assert set(changed) == {'Civ Supply Chains.modinfo',
               'Lua_UI/Lenses/PlotInfo_CSC_QuarterPlacement.lua',
               'Lua_UI/WonderServices/CSC_WonderServicePlotTooltip_Base.lua',
               'Lua_UI/WonderServices/CSC_WonderServicePlotTooltip_Suk.lua'}, changed
        assert set(added) == {'Data/CSC_AI.sql', 'Text/CSC_AI_TEXT.sql',
               'Lua_UI/AI/CSC_AI_UIFilter.lua', 'Lua_UI/AI/ToolTipLoader_CSC_AI.lua',
               'Lua_UI/AI/CivilopediaPage_CSC_AI.lua', 'Lua_UI/AI/CSC_AI_ReportScreen.lua'}, added
        write(a.output/'baseline-build-comparison.json', {'changed_existing': changed, 'added': added, 'other_gameplay_identical': True})
    try:
        i = a.map
        write(a.output/'batch.json', {'status': 'running', 'target_games': 1, 'target_turn': 250, 'paired_map': i})
        if a.resume_running:
            r.cmd('assert(CSCBASE and CSCBASE.version==3 and AutoplayManager.IsActive());', 'CSC_AdjacencyGameplay', 'resume')
        else:
            r.start_pair(i)
        r.autoplay(i, 250, resume=a.resume_running)
        for target in CHECKPOINTS[1:-1]:
            r.snapshot(i, target)
        r.save_checkpoint(i, 250)
        r.check_installed()
        write(a.output/f'game-{i:02d}'/'complete.json', {'status': 'complete', 'turn': 250})
        # Read-only UI/native diagnostics run only after the benchmark/save are
        # archived. Failed probes remain diagnostic evidence, never rewrite data.
        text = r.cmd((Path(__file__).with_name('native_guidance_probe.lua')).read_text(encoding='utf-8'),
                     'PlotInfo', 'native-placement-probe', wait=15, check=False)
        match = re.search(r'CSC_AI_NATIVE_GUIDANCE=([^\r\n]+)', text)
        write(a.output/'placement-probe.json', json.loads(match.group(1)) if match else {'status':'failed','evidence':'native-placement-probe command'})
        r.menu()
        r.restore()
        r.verify_preferences()
        verify(a.output, partial=True)
        assert all(sha(Path(path)) == digest for path, digest in read(a.output/'tuning-source-hashes.json').items())
        write(a.output/'batch.json', {'status': 'complete', 'target_turn': 250, 'games': [i], 'ai_tuning_version': 'bonus-river-v3'})
    except BaseException as exc:
        write(a.output/'batch.json', {'status': 'interrupted', 'error': str(exc), 'traceback': traceback.format_exc()})
        r.say('STOPPED: '+str(exc))
        raise


if __name__ == '__main__':
    main()
