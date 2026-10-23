"""Verify the installed resource-assistance toggle on fresh paired native maps.

Only setup values are changed by the controller. The installed gameplay script
owns resource placement; all map/audit observation commands are read-only.
"""
import argparse
import json
from pathlib import Path
import re
import shutil
import time
import traceback

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
from native_assist import Survey, write, sha, LOGS

SETTING = 'CSC_RESOURCE_MAP_ASSISTANCE'
DIAGNOSTICS = 'CSC_MATERIAL_MAP_DIAGNOSTICS'
INSTALLED = Path.home() / "Documents/My Games/Sid Meier's Civilization VI/Mods/Civ Supply Chains"
SAVES = Path.home() / "Documents/My Games/Sid Meier's Civilization VI/Saves/Single"


def payload(text, prefix):
    match = re.search(re.escape(prefix) + r'=([^\r\n]+)', text)
    assert match, 'Missing complete ' + prefix
    return json.loads(match.group(1))


class ToggleSurvey(Survey):
    enabled = 0

    def cmd(self, code, state='GameCore_Tuner', label='command', wait=2, check=True):
        if label.startswith('start-'):
            code = code.replace('ReleasePlayerParameters();',
                f"GameConfiguration.SetValue('{SETTING}',{self.enabled});"
                f"GameConfiguration.SetValue('{DIAGNOSTICS}',true);"
                f"assert(GameConfiguration.GetValue('{SETTING}')=={self.enabled});"
                'ReleasePlayerParameters();')
        # Commands known to be reads can be retried during console reloads.
        readonly = label == 'ready' or label.startswith(('dump-', 'actual-', 'toggle-audit-'))
        for attempt in range(4):
            try:
                return super().cmd(code, state, label, wait, check)
            except (OSError, EOFError, KeyError, RuntimeError) as exc:
                before = isinstance(exc, KeyError) or str(exc) == 'No responsive tuner states'
                if attempt == 3 or not (before or readonly):
                    raise
                time.sleep(3)

    def menu(self):
        if self.pending:
            folder = self.pending
            self.pending = None
            code = f"""assert(Game.GetCurrentGameTurn()==1);
local a=Game:GetProperty('CSC_MATERIAL_MAP_ASSISTANCE_AUDIT');assert(a);
assert(Game:GetProperty('CSC_MATERIAL_MAP_ASSISTANCE_DONE'));
assert(GameConfiguration.GetValue('{SETTING}')=={self.enabled});
assert(GameConfiguration.GetValue('{DIAGNOSTICS}')==true);
print('CSCTOGGLE_AUDIT='..CSC_MaterialMapCore.Json(a));
if CSC_MaterialMapDebug then print('CSCTOGGLE_DEBUG='..CSC_MaterialMapCore.Json(CSC_MaterialMapDebug)) end;
print('CSCTOGGLE_CONFIG',GameConfiguration.GetValue('{SETTING}'));"""
            text = self.cmd(code, 'CSC_MaterialMap', 'toggle-audit-' + str(self.enabled), wait=6)
            audit = payload(text, 'CSCTOGGLE_AUDIT')
            write(folder / 'automatic-audit.json', audit)
            if self.enabled:
                assert audit['status'] == 'complete', audit
                assert audit['initialization_turn'] == 1
                debug = payload(text, 'CSCTOGGLE_DEBUG')
                write(folder / 'automatic-debug.json', debug)
                assert isinstance(audit['additions'], list) and audit['additions']
            else:
                assert audit['status'] == 'skipped' and audit['reason'] == 'disabled', audit
                assert 'CSCTOGGLE_DEBUG=' not in text
            lua_log = (LOGS / 'Lua.log').read_text(encoding='utf-8', errors='replace')
            if self.enabled:
                assert len(re.findall(r'CSC_MATERIAL_MAP_RESULT\s+complete', lua_log)) == 1
                assert len(re.findall(r'CSC_MATERIAL_MAP_ADDED\s', lua_log)) == len(audit['additions'])
            else:
                assert len(re.findall(r'CSC_MATERIAL_MAP_SKIPPED\s+disabled', lua_log)) == 1
                assert 'CSC_MATERIAL_MAP_ADDED' not in lua_log
                assert 'CSC_MATERIAL_MAP_RESULT' not in lua_log
            db_log = (LOGS / 'Database.log').read_text(encoding='utf-8', errors='replace')
            assert '[Gameplay] ERROR' not in db_log, 'Gameplay database error'
            write(folder / 'toggle-verified.json', {'enabled': bool(self.enabled), 'status': audit['status'],
                'setting_value': self.enabled, 'native_startup_log_verified': True, 'turn': 1})
            self.say(('On' if self.enabled else 'Off') + ': native audit verified')
        super().menu()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert not (args.output / 'original-preferences.json').exists(), 'Use a fresh output directory'
    runner = ToggleSurvey(args.output)
    runner.pending = None
    runner.save_maps = False
    original_settings = None
    preserved = None
    try:
        states = runner.states()
        original_query = f"local setting=GameConfiguration.GetValue('{SETTING}');local diagnostics=GameConfiguration.GetValue('{DIAGNOSTICS}');print('CSCTOGGLE_ORIGINAL='..tostring(setting)..','..tostring(diagnostics));"
        if 'MainMenu' not in states:
            text = runner.cmd(f"""assert(not AutoplayManager.IsActive(),'An autoplay test is active');
{original_query}
print('CSCTOGGLE_TURN',Game.GetCurrentGameTurn());""", 'PlotInfo', 'preserve-current-state')
            original_settings = re.search(r'CSCTOGGLE_ORIGINAL=([^\r\n]+)', text).group(1).split(',')
            name = 'CSC before resource setting test ' + time.strftime('%Y%m%d-%H%M%S')
            started = time.time_ns()
            runner.cmd('local s={Name=' + json.dumps(name) + ',Location=SaveLocations.LOCAL_STORAGE,Type=SaveTypes.SINGLE_PLAYER,IsAutosave=false,IsQuicksave=false};assert(Network.SaveGame(s)~=false);',
                       'PlotInfo', 'save-original-game', wait=4)
            path = SAVES / (name + '.Civ6Save')
            for _ in range(40):
                if path.exists() and path.stat().st_mtime_ns >= started and path.stat().st_size:
                    stamp = (path.stat().st_size, path.stat().st_mtime_ns)
                    time.sleep(1)
                    if stamp == (path.stat().st_size, path.stat().st_mtime_ns):
                        break
                time.sleep(1)
            else:
                raise RuntimeError('Original game save not confirmed; leaving game intact')
            shutil.copy2(path, args.output / path.name)
            preserved = {'path': str(path), 'sha256': sha(path)}
            write(args.output / 'preserved-game.json', preserved)
            runner.menu()
        else:
            text = runner.cmd(original_query, 'MainMenu', 'original-settings')
            original_settings = re.search(r'CSCTOGGLE_ORIGINAL=([^\r\n]+)', text).group(1).split(',')
        assert all(v in ('nil','true','false','0','1') for v in original_settings), original_settings
        write(args.output / 'original-settings.json', dict(zip((SETTING, DIAGNOSTICS), original_settings)))
        for name in ('Lua_UI/MapGeneration/CSC_MaterialMap.lua', 'Settings/Settings.xml', 'Settings/Settings_Text.xml'):
            assert sha(INSTALLED / name) == sha(ROOT / 'Civ Supply Chains' / name), name
        runner.config()
        runner.select_mods(False)
        bundle = json.loads((ROOT / 'project/snapshots/map-lab/maps.json').read_text(encoding='utf-8'))
        control = next(m for m in bundle['maps'] if m['group'] == 'luxuries-4' and m['number'] == 1)
        roster = control['settings']['leaders']
        for enabled, group in ((0, 'off'), (1, 'on')):
            runner.enabled = enabled
            runner.pending = args.output / group / 'map-01'
            runner.start_map(group, False, 3, 1, roster)
        read = lambda name: json.loads((args.output / name).read_text(encoding='utf-8'))
        off = read('off/map-01/map.json')
        on = read('on/map-01/map.json')
        debug = read('on/map-01/automatic-debug.json')
        audit = read('on/map-01/automatic-audit.json')
        assert off['plots'] == debug['before']['plots'], 'Off world differs from exact On pre-pass world'
        assert off['players'] == on['players'] and off['starting_plots'] == on['starting_plots']
        additions = {a['plot']: a for a in audit['additions']}
        assert len(additions) == len(audit['additions'])
        changed = []
        for old, new in zip(off['plots'], on['plots']):
            if old != new:
                a = additions[old['index']]
                assert not old.get('resource') and old['resource_count'] == 0
                assert new['resource'] == a['resource'] and new['resource_count'] == a['quantity'] == 1
                assert {k:v for k,v in old.items() if k not in ('resource','resource_count')} == {k:v for k,v in new.items() if k not in ('resource','resource_count')}
                changed.append(old['index'])
        assert set(changed) == set(additions) and changed
        result = {'passed': True, 'setting': SETTING, 'maps': 2, 'turns_advanced': 0,
            'map_seed': control['settings']['map_seed'], 'game_seed': control['settings']['game_seed'],
            'resource_setting': 'Abundant', 'off_status': 'skipped: disabled', 'off_added_deposits': 0,
            'on_status': 'complete', 'on_added_deposits': len(changed), 'changed_plots': changed,
            'off_matches_on_prepass_exactly': True, 'only_audited_resource_additions_differ': True,
            'original_resources_quantities_terrain_starts_preserved': True, 'preserved_game': preserved}
        write(args.output / 'results.json', result)
        runner.say('PASS: matching native maps; Off adds zero, On adds ' + str(len(changed)) + ' deposits')
    except BaseException as exc:
        write(args.output / ('failure-' + time.strftime('%H%M%S') + '.json'), {'error': str(exc), 'traceback': traceback.format_exc()})
        raise
    finally:
        runner.pending = None
        if (args.output / 'original-preferences.json').exists():
            if 'MainMenu' not in runner.states():
                runner.menu()
            runner.restore()
            if original_settings:
                a,b = original_settings
                runner.cmd(f"GameConfiguration.SetValue('{SETTING}',{a});GameConfiguration.SetValue('{DIAGNOSTICS}',{b});assert(GameConfiguration.GetValue('{SETTING}')=={a});assert(GameConfiguration.GetValue('{DIAGNOSTICS}')=={b});", 'MainMenu', 'restore-settings')
            pins = json.loads((args.output / 'installed-gameplay-hashes.json').read_text())
            assert all(sha(INSTALLED / name) == digest for name,digest in pins.items())
            write(args.output / 'restoration.json', {'passed': True, 'mod_flags_restored': True,
                'auto_start_restored': True, 'setting_values_restored': True, 'installed_files_unchanged': len(pins), 'left_at_main_menu': True})


if __name__ == '__main__':
    main()
