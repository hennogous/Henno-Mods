"""Smoke-test automatic abundance scaling on native Sparse and TAR Plentiful.

Only configures games and reads the already-executed installed helper. No
FireTuner resource writes. Keeps these new fixtures apart from the v1 study.
"""
import argparse
import copy
import json
from pathlib import Path
import re
import traceback
from automatic_assist import AutomaticSurvey, list_fields, ROOT
from assist import read
from native_assist import write, sha
from offline import lua_runtime
from continent_analysis import continent_census


class ScalingSurvey(AutomaticSurvey):
    def assist_current(self,folder):
        after=read(folder/'map.json');settings=read(folder/'settings.json')
        if self.verify_only:
            audit=list_fields(read(folder/'automatic-audit.json'));debug=read(folder/'automatic-debug.json')
        else:
            text=self.cmd("""local a=Game:GetProperty('CSC_MATERIAL_MAP_ASSISTANCE_AUDIT');assert(a and a.status=='complete');assert(Game:GetProperty('CSC_MATERIAL_MAP_ASSISTANCE_DONE'));assert(CSC_MaterialMapDebug);print('CSCSCALE_AUDIT='..CSC_MaterialMapCore.Json(a));print('CSCSCALE_DEBUG='..CSC_MaterialMapCore.Json(CSC_MaterialMapDebug));""",'CSC_MaterialMap','scaling-audit-'+settings['group'],wait=5)
            audit=list_fields(json.loads(re.search(r'CSCSCALE_AUDIT=([^\r\n]+)',text).group(1)))
            debug=json.loads(re.search(r'CSCSCALE_DEBUG=([^\r\n]+)',text).group(1))
            write(folder/'automatic-audit.json',audit);write(folder/'automatic-debug.json',debug)
        profile=audit['abundance'];expected=54 if settings['tar'] else 27
        assert audit['version']==2 and profile['nominal_density']==expected
        assert profile['standard_density']==(29 if settings['tar'] else 30)
        assert audit['initialization_turn']==1 and len(audit['additions'])<=audit['max_per_map']
        before=copy.deepcopy(after);before['plots']=debug['before']['plots'];write(folder/'before.json',before)
        lua=lua_runtime(self.lua_deps);lua.execute((ROOT/'Civ Supply Chains/Lua_UI/MapGeneration/CSC_MaterialMapCore.lua').read_text())
        eligible={r:{i:True for i in values} for r,values in debug['eligible'].items()}
        repeat=lua.globals().CSC_MaterialMapCore.Plan(lua.table_from(debug['before'],recursive=True),lua.table_from(debug['definitions'],recursive=True),lua.table_from(eligible,recursive=True),settings['map_seed'],lua.table_from(profile,recursive=True))
        repeated=list_fields(json.loads(lua.globals().CSC_MaterialMapCore.Json(repeat)))
        for k in ('additions','coverage','palettes','abundance'):assert repeated[k]==audit[k],k
        changes={a['plot']:a['resource'] for a in audit['additions']}
        for p,q in zip(before['plots'],after['plots']):
            if p['index'] in changes:
                assert not p.get('resource') and q['resource']==changes[p['index']]
                assert {k:v for k,v in p.items() if k!='resource'}=={k:v for k,v in q.items() if k!='resource'}
            else:assert p==q
        census=continent_census(after,debug['definitions'])
        for row in audit['coverage']:
            check=next(q for c in census if c['id']==row['continent'] for q in c['quarters'] if q['quarter']==row['quarter'])
            assert check['common_clearable_both']==row['both_after'] and check['common_clearable_base']==row['base_after']
            assert not row['both_before'] or row['both_after'];assert not row['base_before'] or row['base_after']
        logs=(folder/'logs/Lua.log').read_text(encoding='utf-8',errors='replace')
        start=logs.rfind('Generating Continents Map');assert start>=0;logs=logs[start:]
        assert logs.count('CSC_MaterialMap: CSC_MATERIAL_MAP_RESULT')==1
        assert logs.index('CSC_MATERIAL_MAP_RESULT')<logs.index('InGame: Loading InGame UI')
        assert 'CSC_MATERIAL_MAP_ERROR' not in logs and 'Runtime Error:' not in logs
        database=(folder/'logs/Database.log').read_text(encoding='utf-8',errors='replace')
        assert '[Gameplay] ERROR:' not in database
        self.results.append({'group':settings['group'],'profile':profile,'deposits':len(changes),'turn':1,'exact_offline_lua_parity':True,'original_resources_preserved':True,'coverage_preserved':True,'automatic_before_ui':True})
        self.say(f"{settings['group']}: density {expected}, {len(changes)} automatic deposits; exact offline replay and coverage checks passed")


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ('output','bundle','lua-dependencies'):p.add_argument('--'+k,type=Path,required=True)
    p.add_argument('--verify-only',action='store_true',help='Recheck saved native captures without starting games')
    a=p.parse_args();r=ScalingSurvey(a.output);r.pending_folder=None;r.save_maps=False;r.results=[];r.lua_deps=a.lua_dependencies;r.verify_only=a.verify_only
    installed=Path.home()/"Documents/My Games/Sid Meier's Civilization VI/Mods/Civ Supply Chains"
    hashes={str(p.relative_to(installed)):sha(p) for p in installed.rglob('*') if p.is_file() and p.suffix in ('.sql','.lua','.xml','.modinfo')}
    def finish():
        baseline=read(a.output/'installed-gameplay-hashes.json')
        assert all(sha(installed/name)==digest for name,digest in baseline.items())
        for path in (a.output/'commands').glob('*.lua'):
            code=path.read_text()
            assert not any(s in code for s in ('ResourceBuilder.SetResourceType','CSC_MaterialMapCore.Plan(', 'CSC_InitializeMaterialMap('))
        write(a.output/'native-scaling-validation.json',{'passed':True,'maps':r.results,'installed_files_unchanged':len(baseline),'observer_read_only':True})
    if a.verify_only:
        for group in ('scaling-vanilla-sparse','scaling-tar-plentiful'):r.assist_current(a.output/group/'map-01')
        finish();return
    try:
        r.wait('MainMenu');r.config()
        roster=next(m for m in read(a.bundle)['maps'] if m['id']=='luxuries-4-1')['settings']['leaders']
        for group,tar,setting in [('scaling-vanilla-sparse',False,1),('scaling-tar-plentiful',True,25)]:
            r.select_mods(tar);r.pending_folder=a.output/group/'map-01';r.number=1
            r.start_map(group,tar,setting,1,roster)
        assert all(sha(installed/name)==digest for name,digest in hashes.items())
        finish()
    except BaseException as exc:
        write(a.output/'batch-error.json',{'error':str(exc),'traceback':traceback.format_exc()});raise
    finally:
        r.pending_folder=None
        if 'MainMenu' not in r.states():r.menu()
        r.cmd("GameConfiguration.SetValue('CSC_MATERIAL_MAP_DIAGNOSTICS',false);",'MainMenu','clear-diagnostics')
        if (a.output/'original-preferences.json').exists():r.restore()


if __name__=='__main__':main()
