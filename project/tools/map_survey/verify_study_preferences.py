"""Fresh native confirmation of restored preferences and test-map cleanup."""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'ai_baseline'))
from run import Runner, write


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    original=json.loads((a.output/'original-preferences.json').read_text())
    wanted=','.join('['+json.dumps(k)+']='+str(v).lower() for k,v in original['mods'].items())
    code='local wanted={'+wanted+'};for _,m in ipairs(Modding.GetInstalledMods()) do if wanted[m.Id]~=nil then assert(m.Enabled==wanted[m.Id],m.Id) end end;'
    code+='assert(Automation.IsAutoStartEnabled()=='+str(original['auto_start']).lower()+');'
    code+='''local script=MapConfiguration.GetScript();if script and script:find('CSC_LuxuryStudy_Continents',1,true) then MapConfiguration.SetScript('Continents.lua') end;print('CSC_STUDY_PREFS_VERIFIED',Automation.IsAutoStartEnabled(),MapConfiguration.GetScript());'''
    r=Runner(a.output);r.wait('MainMenu');result=r.cmd(code,'MainMenu','fresh-preferences-verification',wait=3)
    assert 'CSC_STUDY_PREFS_VERIFIED' in result
    write(a.output/'preferences-restored.json',{'verified':True,'community_mod_flags_checked':len(original['mods']),'auto_start':original['auto_start'],'test_map_selection_cleared':True,'evidence':result})
    print('PASS: original community-mod flags and auto-start freshly verified; private test map deselected')


if __name__=='__main__':main()
