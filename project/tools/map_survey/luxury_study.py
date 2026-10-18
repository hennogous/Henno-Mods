"""Paired native 4/5/6 land-luxury experiment, without editing installed files.

prepare creates a private copy of the installed GS Continents map. Its only
behavioural change is passing LuxuriesPerRegion to the native ResourceGenerator.
The experiment never advances turns. Main-menu preferences are restored on exit.
"""
import argparse
import hashlib
import importlib.util
import json
import re
from pathlib import Path
import shutil
import sys
import time
import traceback

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
_spec = importlib.util.spec_from_file_location('csc_map_survey_runner', HERE / 'run.py')
_survey = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_survey)
Survey, ROOT, read, sha, write = (_survey.Survey, _survey.ROOT, _survey.read, _survey.sha, _survey.write)

GAME = Path("C:/Program Files (x86)/Steam/steamapps/common/Sid Meier's Civilization VI")
ORIGINAL = GAME / 'DLC/Expansion2/Maps/Continents.lua'


def prepare(out):
    out.mkdir(parents=True, exist_ok=True)
    original = ORIGINAL.read_text(encoding='utf-8-sig')
    needle = '\tlocal resGen = ResourceGenerator.Create(args);'
    assert original.count(needle) == 1
    replacement = '''\tlocal cscLuxuryCount = MapConfiguration.GetValue("CSC_LUXURY_TYPES");
\tassert(cscLuxuryCount == 4 or cscLuxuryCount == 5 or cscLuxuryCount == 6, "CSC luxury experiment count missing");
\targs.LuxuriesPerRegion = cscLuxuryCount;
\tprint("CSC_LUXURY_STUDY_COUNT", cscLuxuryCount);
\tCSCcalBegin();
''' + needle + '\n\tCSCcalResourcesEnd();'
    target = out / 'CSC_LuxuryStudy_Continents.lua'
    generated = (HERE / 'calibration_capture.lua').read_text(encoding='utf-8') + '\n' + original.replace(needle, replacement)
    generated = generated.replace('\tlocal GoodyGen = AddGoodies(g_iW, g_iH);', '\tCSCcalEnd();\n\tlocal GoodyGen = AddGoodies(g_iW, g_iH);')
    target.write_text(generated, encoding='utf-8')
    write(out / 'map-script-provenance.json', {
        'original': str(ORIGINAL), 'original_sha256': sha(ORIGINAL),
        'experiment': str(target), 'experiment_sha256': sha(target),
        'change': 'Pass validated MapConfiguration.CSC_LUXURY_TYPES as args.LuxuriesPerRegion. Read-only phase captures and RNG trace; no extra RNG draws.'})
    shutil.copy2(HERE / 'materials.json', out / 'materials.json')
    return target


class LuxurySurvey(Survey):
    def cmd(self, code, state='GameCore_Tuner', label='command', wait=2, check=True):
        if label.startswith('start-'):
            original = "MapConfiguration.SetScript('Continents.lua');"
            assert original in code
            code = code.replace(original, 'MapConfiguration.SetScript(' + json.dumps(str(self.script).replace('\\', '/')) + ');')
            code = code.replace('ReleasePlayerParameters();', f"MapConfiguration.SetValue('CSC_LUXURY_TYPES',{self.luxuries});ReleasePlayerParameters();")
            code = code.replace('Network.HostGame(ServerType.SERVER_TYPE_NONE);', "local result=Network.HostGame(ServerType.SERVER_TYPE_NONE);print('CSC_HOST_RESULT',tostring(result));")
        for attempt in range(8):
            try:
                return super().cmd(code, state, label, wait, check)
            except (RuntimeError, KeyError, OSError, EOFError) as exc:
                before_send = isinstance(exc, KeyError) or str(exc) == 'No responsive tuner states'
                read_only = label == 'ready' or label.startswith(('dump-', 'actual-'))
                if attempt == 7 or not (before_send or read_only): raise
                if attempt == 0: self.say(f'Transient console reload during {label}; retrying safely')
                time.sleep(2)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--reference', type=Path, required=True)
    p.add_argument('--prepare-only', action='store_true')
    p.add_argument('--first-only', action='store_true')
    p.add_argument('--restore-only', action='store_true')
    p.add_argument('--resume-current', action='store_true', help='Finish the loaded, first incomplete native map before continuing')
    a = p.parse_args()
    script = prepare(a.output)
    if a.prepare_only:
        print(script); return
    r = LuxurySurvey(a.output); r.save_maps = False; r.script = script.resolve()
    if a.restore_only:
        r.wait('MainMenu'); r.restore(); return
    try:
        if not a.resume_current:
            r.wait('MainMenu')
            r.cmd("Network.LeaveGame();print('CSC_STUDY_FRONTEND',UI.IsInFrontEnd());", 'MainMenu', 'clear-pending-study-session')
            r.config(); r.select_mods(False)
        resume = a.resume_current
        write(a.output / 'batch.json', {'status': 'running', 'target_maps': 15})
        for count in (4, 5, 6):
            r.luxuries = count
            for i in range(1, 6):
                group = f'luxuries-{count}'
                folder = a.output / group / f'map-{i:02d}'
                if (folder / 'complete.json').exists():
                    assert read(folder / 'settings.json').get('luxury_types_per_continent') == count, 'Unverified completed experiment'
                    continue
                ref = read(a.reference / 'vanilla-abundant' / f'map-{i:02d}' / 'settings.json')
                if resume: r.active_mods = (folder / 'enabled-mods.txt').read_text(encoding='utf-8')
                r.start_map(group, False, 3, i, ref['leaders'], resume=resume)
                resume = False
                settings = read(folder / 'settings.json')
                settings.update(luxury_types_per_continent=count, map=str(r.script), base_map='Continents.lua')
                write(folder / 'settings.json', settings)
                logged_counts = re.findall(r'CSC_LUXURY_STUDY_COUNT\s+(\d+)', (folder / 'logs/Lua.log').read_text(encoding='utf-8', errors='replace'))
                assert logged_counts and int(logged_counts[-1]) == count, 'Experiment script count marker missing or wrong'
                if a.first_only:
                    write(a.output / 'batch.json', {'status': 'background-test-complete', 'maps': 1}); return
        write(a.output / 'batch.json', {'status': 'complete', 'maps': 15, 'turns_advanced': 0})
    except BaseException as exc:
        write(a.output / 'batch.json', {'status': 'interrupted', 'error': str(exc), 'traceback': traceback.format_exc()})
        raise
    finally:
        try:
            if 'MainMenu' in r.states(): r.restore()
            else: r.say('Preferences restoration pending: return to main menu and use --restore-only.')
        except Exception as exc: r.say('Preferences restoration pending: ' + str(exc))


if __name__ == '__main__': main()
