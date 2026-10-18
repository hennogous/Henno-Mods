"""Six fresh native v4 maps: three paired seeds, Standard and Abundant.

Only configure and observe Civ. The installed pass performs all resource writes
automatically. Verify native quantities and replay its captured inputs offline.
"""
import argparse
import copy
from collections import Counter
import json
from pathlib import Path
import re
import shutil
import sys
import time
import traceback
from automatic_assist import AutomaticSurvey,list_fields,ROOT
from native_assist import write,sha,LOGS
from offline import lua_runtime
from continent_analysis import continent_census
from analyze import write_csv

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'ai_baseline'))
from run import Runner


class DensitySurvey(AutomaticSurvey):
    def cmd(self,code,state='GameCore_Tuner',label='command',wait=2,check=True):
        if label.startswith('start-'):
            code=code.replace('ReleasePlayerParameters();',"GameConfiguration.SetValue('CSC_MATERIAL_MAP_ASSISTANCE',1);GameConfiguration.SetValue('CSC_MATERIAL_MAP_DIAGNOSTICS',true);ReleasePlayerParameters();")
        for attempt in range(4):
            try:return Runner.cmd(self,code,state,label,wait,check)
            except (OSError,EOFError,RuntimeError,KeyError) as exc:
                before=isinstance(exc,KeyError) or str(exc)=='No responsive tuner states'
                readonly=label=='ready' or label.startswith(('dump-','actual-','density-audit-'))
                if attempt==3 or not (before or readonly):raise
                time.sleep(3)

    def assist_current(self,folder):
        after=read(folder/'map.json');settings=read(folder/'settings.json')
        code="local a=Game:GetProperty('CSC_MATERIAL_MAP_ASSISTANCE_AUDIT');assert(a and a.status=='complete' and a.version==4);assert(CSC_MaterialMapDebug);print('CSCDENS_AUDIT='..CSC_MaterialMapCore.Json(a));print('CSCDENS_DEBUG='..CSC_MaterialMapCore.Json(CSC_MaterialMapDebug));"
        text=self.cmd(code,'CSC_MaterialMap','density-audit-'+str(self.number),wait=6)
        audit=list_fields(json.loads(re.search(r'CSCDENS_AUDIT=([^\r\n]+)',text).group(1)))
        debug=json.loads(re.search(r'CSCDENS_DEBUG=([^\r\n]+)',text).group(1))
        write(folder/'automatic-audit.json',audit);write(folder/'automatic-debug.json',debug)
        assert audit['initialization_turn']==1 and set(debug['definitions'])=={'BAKERS','TAILORS'}
        assert audit['abundance']['setting']==settings['resource_setting'] and audit['abundance']['standard_density']==30
        before=copy.deepcopy(after);before['plots']=debug['before']['plots'];write(folder/'before.json',before)
        lua=lua_runtime(self.lua_deps);lua.execute((ROOT/'Civ Supply Chains/Lua_UI/MapGeneration/CSC_MaterialMapCore.lua').read_text(encoding='utf-8'))
        C=lua.globals().CSC_MaterialMapCore
        eligible={r:{i:True for i in indices} for r,indices in debug['eligible'].items()}
        replay=C.Plan(lua.table_from(debug['before'],recursive=True),lua.table_from(debug['definitions'],recursive=True),lua.table_from(eligible,recursive=True),settings['map_seed'],lua.table_from(audit['abundance'],recursive=True))
        replay=list_fields(json.loads(C.Json(replay)))
        for key in ('additions','coverage','palettes','site_density'):
            assert replay[key]==audit[key],('Native/offline replay',key)
        changes={a['plot']:a for a in audit['additions']};assert len(changes)==len(audit['additions'])
        for old,new in zip(before['plots'],after['plots']):
            if old['index'] in changes:
                a=changes[old['index']]
                assert not old.get('resource') and old['resource_count']==0
                assert new['resource']==a['resource'] and new['resource_count']==a['quantity']==1
                assert a['quarter']=='TAILORS' and a['plot'] in debug['eligible'][a['resource']]
                if a.get('phase')=='site_density':assert a['plot'] not in debug['starting_plots']
                assert {k:v for k,v in old.items() if k not in ('resource','resource_count')}=={k:v for k,v in new.items() if k not in ('resource','resource_count')}
            else:assert old==new
        assert sum(p['resource_count'] for p in after['plots'])-sum(p['resource_count'] for p in before['plots'])==len(changes)
        definitions=debug['definitions'];prior=continent_census(before,definitions);census=continent_census(after,definitions)
        write(folder/'continent-census.json',{'before':prior,'after':census})
        density=audit['site_density']
        tailors=next(q for q in census[0]['quarters'] if q['quarter']=='TAILORS')
        assert density['after']=={'base_only':tailors['common_clearable_base_only'],'both':tailors['common_clearable_both']}
        assert all(density['met'].values()),('Unmet site target',density)
        for row in audit['coverage']:
            q=next(q for c in census if c['id']==row['continent'] for q in c['quarters'] if q['quarter']==row['quarter'])
            assert (row['base_after'],row['both_after'])==(q['common_clearable_base'],q['common_clearable_both'])
        logs=(folder/'logs/Lua.log').read_text(encoding='utf-8',errors='replace');start=logs.rfind('Generating Continents Map');assert start>=0;logs=logs[start:]
        assert logs.count('CSC_MATERIAL_MAP_RESULT')==1 and logs.count('CSC_MATERIAL_MAP_ADDED')==len(changes)
        assert 'Runtime Error' not in logs and 'CSC_MATERIAL_MAP_ERROR' not in logs
        assert logs.index('CSC_MATERIAL_MAP_RESULT')<logs.index('Loading InGame UI')
        assert '[Gameplay] ERROR' not in (folder/'logs/Database.log').read_text(errors='replace')
        resource_counts=Counter(p['resource'] for p in after['plots'] if p.get('resource'))
        copies=Counter()
        for p in after['plots']:
            if p.get('resource'):copies[p['resource']]+=p['resource_count']
        rows=[]
        for q,defs in definitions.items():
            current=next(r for r in census[0]['quarters'] if r['quarter']==q)
            initial=next(r for r in prior[0]['quarters'] if r['quarter']==q)
            row={'setting':settings['resource_setting'],'level':'Standard' if settings['resource_setting']==2 else 'Abundant','map':self.number-5,'map_seed':settings['map_seed'],'game_seed':settings['game_seed'],'quarter':q,
                 'base_only':current['common_clearable_base_only'],'both':current['common_clearable_both'],'base_supported':current['common_clearable_base'],
                 'base_only_before':initial['common_clearable_base_only'],'both_before':initial['common_clearable_both'],
                 'both_clusters':current['common_clearable_both_clusters'],
                 'continents_with_base':sum(next(r for r in c['quarters'] if r['quarter']==q)['common_clearable_base']>0 for c in census[1:]),
                 'continents_with_both':sum(next(r for r in c['quarters'] if r['quarter']==q)['common_clearable_both']>0 for c in census[1:]),
                 'continents':len(census)-1,'all_csc_added_copies':len(changes),'density_added_copies':density['additions']}
            for kind in ('base','spec'):
                mapped=set(defs[kind]['resources'])
                row[kind+'_resource_tiles']=sum(resource_counts[r] for r in mapped)
                row[kind+'_resource_copies']=sum(copies[r] for r in mapped)
                row[kind+'_copies_added']=sum(a['quantity'] for a in changes.values() if a['resource'] in mapped)
                row[kind+'_inventory']={r:copies[r] for r in sorted(mapped) if copies[r]}
            rows.append(row)
        write(folder/'resource-stats.json',rows)
        write(folder/'verified.json',{'passed':True,'version':4,'native':True,'turn':1,'plots':len(after['plots']),'additions':len(changes),'exact_lua_replay':True,'targets_met':True})
        self.say(f"Verified {rows[0]['level']} seed{settings['map_seed']}: {len(changes)} added copies; B {rows[0]['base_only']}/{rows[0]['both']}, T {rows[1]['base_only']}/{rows[1]['both']} Base-only/both")

    def cleanup(self):
        for attempt in range(3):
            try:
                self.wait('MainMenu',180)
                self.cmd("GameConfiguration.SetValue('CSC_MATERIAL_MAP_DIAGNOSTICS',false);",'MainMenu','clear-diagnostics')
                self.restore();time.sleep(3)
                original=read(self.out/'original-preferences.json')
                wanted=','.join('['+json.dumps(k)+']='+str(v).lower() for k,v in original['mods'].items())
                code='local wanted={'+wanted+'};for _,m in ipairs(Modding.GetInstalledMods()) do if wanted[m.Id]~=nil then assert(m.Enabled==wanted[m.Id],m.Id) end end;assert(Automation.IsAutoStartEnabled()=='+str(original['auto_start']).lower()+");assert(GameConfiguration.GetValue('CSC_MATERIAL_MAP_DIAGNOSTICS')==false);print('CSCDENS_PREFS_VERIFIED');"
                self.cmd(code,'MainMenu','fresh-preferences',wait=3)
                write(self.out/'preferences-restored.json',{'verified':True,'mods':len(original['mods']),'auto_start':original['auto_start'],'diagnostics':False});return
            except (RuntimeError,KeyError,OSError):
                if attempt==2:raise
                time.sleep(3)


def read(path):return json.loads(path.read_text(encoding='utf-8'))

def main():
    sys.stdout.reconfigure(encoding='utf-8',errors='replace');sys.stderr.reconfigure(encoding='utf-8',errors='replace')
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('output','rosters','lua-dependencies'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--resume-current',action='store_true')
    a=p.parse_args();r=DensitySurvey(a.output);r.pending_folder=None;r.save_maps=False;r.lua_deps=a.lua_dependencies
    paths=[Path(__file__),ROOT/'Civ Supply Chains/Lua_UI/MapGeneration/CSC_MaterialMapCore.lua',ROOT/'Civ Supply Chains/Lua_UI/MapGeneration/CSC_MaterialMap.lua']
    pins={str(path):sha(path) for path in paths};write(a.output/'source-hashes.json',pins)
    try:
        if a.resume_current:
            r.wait('CSC_AdjacencyGameplay',60)
            r.cmd("assert(Game.GetCurrentGameTurn()==1);print('CSCDENS_RESUME_CURRENT');",'CSC_AdjacencyGameplay','resume-current')
            r.active_mods=(a.output/'density-v4-abundant/map-06/enabled-mods.txt').read_text(encoding='utf-8')
        else:
            r.wait('MainMenu',240);r.config();r.select_mods(False)
        write(a.output/'batch.json',{'status':'running','version':4,'target_maps':6,'fresh_seed_indices':[6,7,8],'resource_settings':[2,3]})
        for setting in (2,3):
            group='density-v4-standard' if setting==2 else 'density-v4-abundant'
            for number in range(6,9):
                folder=a.output/group/f'map-{number:02d}'
                if (folder/'verified.json').exists():continue
                r.number=number;r.pending_folder=folder
                roster=read(a.rosters/f'map-{number-5:02d}'/'settings.json')['leaders']
                r.start_map(group,False,setting,number,roster,resume=a.resume_current and setting==3 and number==6)
        for number in range(6,9):
            worlds=[read(a.output/group/f'map-{number:02d}'/'before.json') for group in ('density-v4-standard','density-v4-abundant')]
            for key in ('terrain','feature','continent','river','lake','neighbors'):
                assert all(p.get(key)==q.get(key) for p,q in zip(worlds[0]['plots'],worlds[1]['plots'])),('Paired landscape',number,key)
    except BaseException as exc:
        write(a.output/'batch.json',{'status':'interrupted','error':str(exc),'traceback':traceback.format_exc()})
        raise
    finally:
        r.pending_folder=None
        try:
            if 'MainMenu' not in r.states():r.menu()
            r.cleanup()
        except Exception as exc:write(a.output/'cleanup-required.json',{'error':str(exc)});raise
    cleanup_marker=a.output/'cleanup-required.json'
    if cleanup_marker.exists():cleanup_marker.rename(a.output/'connection-reload/cleanup-resolved.json')
    installed=Path.home()/"Documents/My Games/Sid Meier's Civilization VI/Mods/Civ Supply Chains"
    hashes=read(a.output/'installed-gameplay-hashes.json');assert all(sha(installed/n)==h for n,h in hashes.items())
    assert all(sha(Path(n))==h for n,h in pins.items())
    for path in (a.output/'commands').glob('*.lua'):
        assert not any(x in path.read_text(encoding='utf-8') for x in ('ResourceBuilder.SetResourceType','CSC_MaterialMapCore.Plan(', 'CSC_InitializeMaterialMap('))
    stats=[row for path in sorted(a.output.glob('density-v4-*/map-*/resource-stats.json')) for row in read(path)]
    assert len(stats)==12
    write(a.output/'resource-stats.json',stats);write_csv(a.output/'resource-stats.csv',stats)
    write(a.output/'batch.json',{'status':'complete','maps':6,'version':4,'native':True,'turns_advanced':0,'installed_files_unchanged':len(hashes),'source_pins_verified':True,'read_only_observer':True,'prefs_restored':True})
    print(json.dumps(stats),flush=True)

if __name__=='__main__':main()
