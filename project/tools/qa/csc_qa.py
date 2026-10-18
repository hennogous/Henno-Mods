"""CSC native-game QA. Startup/UI actions remain explicit; never target a campaign.

Uses the existing framed tuner transport and resolves Lua state names on every
command. Each check requires its own completion token and xpcall success marker.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'project/tools/adjacencies'))
import tuner

FIXTURE = ROOT / 'project/tests/qa/material_stacking.lua'

def fixture_source(path):
    return (ROOT/'project/tests/qa/placement.lua').read_text(encoding='utf-8')+'\n'+path.read_text(encoding='utf-8')



class Run:
    def __init__(self, output):
        self.output = output
        output.mkdir(parents=True, exist_ok=True)
        self.path = output / 'results.json'
        self.results = json.loads(self.path.read_text()) if self.path.exists() else {'checks': []}

    def execute(self, name, code, state='CSC_AdjacencyGameplay', wait=2, allow_event_errors=False):
        token = 'CSC_QA_' + uuid.uuid4().hex
        wrapped = ('local ok,err=xpcall(function()\n' + code +
                   '\nend,function(err) return tostring(err) end); if ok then print("' + token +
                   ':PASS") else print("' + token + ':FAIL",tostring(err)) end')
        start = time.monotonic()
        try:
            states = tuner.states()
            if state not in states:
                raise RuntimeError(f'{state} unavailable; current states: {states}')
            messages = tuner.command(wrapped, states[state], wait)
            text = '\n'.join(messages)
            success = token + ':PASS' in text and token + ':FAIL' not in text and (allow_event_errors or 'Runtime Error:' not in text)
        except Exception as exc:
            text = repr(exc)
            success = False
        filename = f'{len(self.results["checks"]):03d}-' + re.sub(r'[^a-z0-9]+', '-', name.lower()) + '.txt'
        (self.output / filename).write_text(text, encoding='utf-8')
        (self.output / filename.replace('.txt', '.lua')).write_text(code, encoding='utf-8')
        self.results['checks'].append({'name': name, 'status': 'passed' if success else 'failed',
                                       'seconds': round(time.monotonic()-start, 2), 'evidence': filename,
                                       'event_runtime_errors': text.count('Runtime Error:')})
        self.path.write_text(json.dumps(self.results, indent=2) + '\n')
        print(('PASS ' if success else 'FAIL ') + name, flush=True)
        if not success:
            raise RuntimeError(text)
        return text


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['status', 'start', 'materials', 'recheck', 'save', 'reload', 'menu', 'restore', 'snapshot'])
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--port', type=int, default=4318)
    parser.add_argument('--disposable-game', action='store_true')
    parser.add_argument('--save-name', default='CSC QA materials 20261015')
    parser.add_argument('--monopolies', action='store_true', help='Enable M&C in a new disposable game')
    args = parser.parse_args()
    tuner.PORT = args.port
    run = Run(args.output)
    if args.action == 'status':
        available = tuner.states()
        (args.output/'states.json').write_text(json.dumps(available, indent=2))
        print(json.dumps(available, indent=2))
    elif args.action == 'start':
        assert args.disposable_game, 'New game requires --disposable-game'
        prefs = args.output/'original-mod-preferences.json'
        if not prefs.exists():
            text = run.execute('capture mod preferences', '''local entries={};
for _,mod in ipairs(Modding.GetInstalledMods()) do
 if mod.Source=='Mod' and not mod.Official then entries[#entries+1]='"'..mod.Id..'":'..tostring(mod.Enabled); end
end
print('CSC_QA_PREFS={'..table.concat(entries,',')..'}');''', 'MainMenu')
            match = re.search(r'CSC_QA_PREFS=(\{[^\r\n]*\})', text)
            assert match, text
            prefs.write_text(json.dumps(json.loads(match.group(1)), indent=2))
        else:
            print('Preserving original preference snapshot from earlier startup attempt.')
        auto_path = args.output/'original-auto-start.json'
        if not auto_path.exists():
            text = run.execute('capture native auto-start preference', 'print("CSC_QA_AUTOSTART",tostring(Automation.IsAutoStartEnabled()));', 'MainMenu')
            match = re.search(r'CSC_QA_AUTOSTART\s+(true|false)', text)
            assert match, text
            auto_path.write_text(json.dumps(match.group(1)=='true'))
        code = (ROOT/'project/tests/adjacencies/start_csc_only.lua').read_text()
        # Current native enum is 0; the historical hard-coded -1 tries an
        # incompatible network transport. BuildHeadlessGameSetup populates slots.
        code = code[:code.rindex('Network.HostGame(-1);')] + '''
GameConfiguration.SetToDefaults();
GameConfiguration.SetValue('RULESET','RULESET_EXPANSION_2');
BuildHeadlessGameSetup(); RebuildPlayerParameters(true); GameSetup_RefreshParameters();
MapConfiguration.SetValue('MAP_SIZE','MAPSIZE_DUEL');
MapConfiguration.SetValue('MAP_SCRIPT','Continents.lua');
MapConfiguration.SetValue('RANDOM_SEED',314159);
GameConfiguration.SetValue('RANDOM_SEED',271828);
ReleasePlayerParameters(); HideGameSetup();
Automation.SetAutoStartEnabled(true);
assert(Automation.IsAutoStartEnabled(),'Native auto-start did not enable');
Network.HostGame(ServerType.SERVER_TYPE_NONE);
'''
        if args.monopolies:
            code=code.replace('ReleasePlayerParameters(); HideGameSetup();', "GameConfiguration.SetValue('GAMEMODE_MONOPOLIES',true); ReleasePlayerParameters(); HideGameSetup();")
        # A transition can tear down its originating Lua state before returning.
        # Persist dispatch evidence; readiness is checked separately, never inferred.
        available = tuner.states()
        messages = tuner.command(code, available['MainMenu'], 3)
        (args.output/'start-dispatch.txt').write_text('\n'.join(messages), encoding='utf-8')
        print('New test game dispatched; observe Begin Game if needed, then run materials.')
    elif args.action == 'materials':
        assert args.disposable_game, 'Fixture mutation requires --disposable-game'
        run.execute('create disposable material fixture', fixture_source(FIXTURE) + '\nCSC_QA_CreateMaterials()')
        stages = [('one base material', 'CSC_QA_Resource(1,true)', 1),
                  ('two base materials stack', 'CSC_QA_Resource(2,true)', 2),
                  ('specialty material stacks with base', 'CSC_QA_Resource(3,true)', 3),
                  ('resource removal clears one contribution', 'CSC_QA_Resource(2,false)', 2),
                  ('resource restoration restores one contribution', 'CSC_QA_Resource(2,true)', 3)]
        run.execute('zero material baseline', 'CSC_QA_AssertMaterials(0)')
        for name, mutation, expected in stages:
            run.execute(name + ' mutation', mutation)
            # Separate native command permits the game's event/update cycle to run.
            run.execute(name, f'CSC_QA_AssertMaterials({expected})')
        run.execute('unchanged refresh remains idempotent', 'CSC_RefreshAdjacencies(); CSC_QA_AssertMaterials(3)')
        # WorldBuilder ownership writes are silent, unlike a player's tile purchase.
        # Use the former only to prepare the latter, then exercise the real command.
        run.execute('prepare unowned resource for purchase', '''CSC_QA_Owner(false); CSC_RefreshAdjacencies();
local f=Game:GetProperty("CSC_QA_MATERIAL_FIXTURE"); Players[f.PlayerID]:GetTreasury():ChangeGoldBalance(10000);
CSC_QA_AssertMaterials(2);''')
        run.execute('purchase resource through native city command', '''
local f=Game:GetProperty('CSC_QA_MATERIAL_FIXTURE'); local p=Map.GetPlotByIndex(f.Slots[1]);
local city=Players[f.PlayerID]:GetCities():FindID(f.CityID); local params={};
params[CityCommandTypes.PARAM_PLOT_PURCHASE]=true;
params[CityCommandTypes.PARAM_X]=p:GetX(); params[CityCommandTypes.PARAM_Y]=p:GetY();
assert(CityManager.CanStartCommand(city,CityCommandTypes.PURCHASE,params),'Fixture tile is not purchasable');
CityManager.RequestCommand(city,CityCommandTypes.PURCHASE,params);''', 'PlotInfo')
        run.execute('native purchase automatically refreshes material yield', '''
local f=Game:GetProperty('CSC_QA_MATERIAL_FIXTURE'); assert(Map.GetPlotByIndex(f.Slots[1]):GetOwner()==f.PlayerID);
CSC_QA_AssertMaterials(3);''')
    elif args.action == 'recheck':
        run.execute('saved fixture survives reload', fixture_source(FIXTURE) + '\nCSC_QA_AssertMaterials(3)')
    elif args.action == 'save':
        run.execute('verify disposable fixture before saving', 'assert(Game:GetProperty("CSC_QA_MATERIAL_FIXTURE") or Game:GetProperty("CSC_TAILORS_QA"));')
        name = json.dumps(args.save_name)
        started = time.time_ns()
        run.execute('dispatch fixture save', f'''local sg={{Name={name},Location=SaveLocations.LOCAL_STORAGE,Type=SaveTypes.SINGLE_PLAYER,IsAutosave=false,IsQuicksave=false}};
Events.SaveComplete.Add(function() print('CSC_QA_SAVE_COMPLETE'); end);
assert(Network.SaveGame(sg)~=false,'Save request rejected');''', 'PlotInfo', 4)
        # Confirm a completed file, not just acceptance of the asynchronous API.
        save_root = Path.home()/'Documents/My Games/Sid Meier\'s Civilization VI/Saves/Single'
        deadline = time.monotonic()+60
        save = None
        while time.monotonic()<deadline:
            candidates = list(save_root.rglob(args.save_name+'.Civ6Save'))
            if len(candidates)==1:
                candidate = candidates[0]
                a = (candidate.stat().st_size, candidate.stat().st_mtime_ns)
                if a[0] > 0 and a[1] >= started:
                    time.sleep(1)
                    if a == (candidate.stat().st_size, candidate.stat().st_mtime_ns):
                        save = candidate
                        break
            time.sleep(.5)
        assert save, 'No fresh, completed save file confirmed within 60 seconds'
        shutil.copy2(save, args.output/save.name)
        (args.output/'save.json').write_text(json.dumps({'path':str(save), 'sha256':hashlib.sha256(save.read_bytes()).hexdigest()}, indent=2))
        print('Confirmed completed save:', save)
    elif args.action == 'reload':
        saved = json.loads((args.output/'save.json').read_text())
        states = tuner.states()
        state = states.get('MainMenu', states.get('PlotInfo'))
        assert state is not None, states
        code = f'print("CSC_QA_LOAD_DISPATCH",Network.LoadGame({json.dumps(saved["path"])}, ServerType.SERVER_TYPE_NONE));'
        messages = tuner.command(code, state, 3)
        (args.output/'reload-dispatch.txt').write_text('\n'.join(messages), encoding='utf-8')
        print('Load dispatched; recheck after gameplay states return.')
    elif args.action == 'menu':
        states = tuner.states()
        assert 'PlotInfo' in states
        messages = tuner.command('Events.ExitToMainMenu();', states['PlotInfo'], 3)
        (args.output/'menu-dispatch.txt').write_text('\n'.join(messages), encoding='utf-8')
        assert not any('ERR:' in message for message in messages), '\n'.join(messages)
    elif args.action == 'restore':
        import subprocess
        subprocess.run([sys.executable, str(ROOT/'project/tools/adjacencies/restore_mod_preferences.py'),
                        '--preferences', str(args.output/'original-mod-preferences.json'),
                        '--output', str(args.output/'restored-mod-preferences.txt'), '--port', str(args.port)], check=True)
        auto_path = args.output/'original-auto-start.json'
        if auto_path.exists():
            value = str(json.loads(auto_path.read_text())).lower()
            run.execute('restore native auto-start preference', f'Automation.SetAutoStartEnabled({value}); assert(Automation.IsAutoStartEnabled()=={value});', 'MainMenu')
    elif args.action == 'snapshot':
        for name in ['Database.log', 'Modding.log', 'Lua.log']:
            source = Path.home()/'AppData/Local/Firaxis Games/Sid Meier\'s Civilization VI/Logs'/name
            if source.exists(): shutil.copy2(source, args.output/name)


if __name__ == '__main__':
    main()
