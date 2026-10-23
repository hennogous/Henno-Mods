"""Observe CSC's installed Lua helper running automatically on five paired maps.

FireTuner only configures new games and reads results; no planner or resource
setter is invoked through the test controller.
"""
import argparse
import copy
import json
from pathlib import Path
import re
import sys
import traceback
from native_assist import NativeSurvey, write, sha
from assist import read
from continent_analysis import continent_census
from analyze import write_csv
from build import render
from offline import lua_runtime

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]


def list_fields(plan):
    for k in ('additions','attempts','palettes','coverage'):
        if plan.get(k)=={}:plan[k]=[]
    for a in plan.get('additions',[]):
        if a.get('coverage_gains')=={}:a['coverage_gains']=[]
    return plan


class AutomaticSurvey(NativeSurvey):
    def cmd(self,code,state='GameCore_Tuner',label='command',wait=2,check=True):
        if label.startswith('start-'):
            code=code.replace('ReleasePlayerParameters();',"GameConfiguration.SetValue('CSC_RESOURCE_MAP_ASSISTANCE',1);GameConfiguration.SetValue('CSC_MATERIAL_MAP_DIAGNOSTICS',true);ReleasePlayerParameters();")
        return super().cmd(code,state,label,wait,check)

    def assist_current(self,folder):
        i=self.number
        after=read(folder/'map.json')
        # The helper has already run as an installed gameplay context, before
        # the observer connects. Read its captured audit and pre-pass world.
        code="""local a=Game:GetProperty('CSC_MATERIAL_MAP_ASSISTANCE_AUDIT');assert(a and a.status=='complete','Automatic helper did not complete');assert(Game:GetProperty('CSC_MATERIAL_MAP_ASSISTANCE_DONE'));assert(CSC_MaterialMapDebug,'Missing automatic diagnostic capture');print('CSCLUA_AUDIT='..CSC_MaterialMapCore.Json(a));print('CSCLUA_DEBUG='..CSC_MaterialMapCore.Json(CSC_MaterialMapDebug));"""
        text=self.cmd(code,'CSC_MaterialMap',f'automatic-audit-{i}',wait=5)
        audit=list_fields(json.loads(re.search(r'CSCLUA_AUDIT=([^\r\n]+)',text).group(1)))
        debug=json.loads(re.search(r'CSCLUA_DEBUG=([^\r\n]+)',text).group(1))
        write(folder/'automatic-audit.json',audit);write(folder/'automatic-debug.json',debug)
        control=next(m for m in self.bundle['maps'] if m['id']==f'luxuries-4-{i}')
        reference=next(m for m in self.bundle['maps'] if m['id']==f'csc-helper-native-{i}')
        before=copy.deepcopy(after);before['plots']=debug['before']['plots']
        write(folder/'before.json',before)
        fields=('terrain','feature','resource','continent','river','lake','district','owner','neighbors')
        comparison={k:sum(p.get(k)!=q.get(k) for p,q in zip(before['plots'],control['data']['plots'])) for k in fields}
        assert not any(comparison.values()),comparison
        definitions=debug['definitions']
        # The exact installed Lua planner must reproduce its decisions offline
        # when supplied the native eligibility captured during automatic startup.
        lua=lua_runtime(self.lua_deps)
        lua.execute((ROOT/'Civ Supply Chains/Lua_UI/MapGeneration/CSC_MaterialMapCore.lua').read_text())
        eligible={r:{p:True for p in indices} for r,indices in debug['eligible'].items()}
        repeated=lua.globals().CSC_MaterialMapCore.Plan(lua.table_from(debug['before'],recursive=True),lua.table_from(definitions,recursive=True),lua.table_from(eligible,recursive=True),control['settings']['map_seed'],lua.table_from(audit['abundance'],recursive=True) if 'abundance' in audit else None)
        repeated=list_fields(json.loads(lua.globals().CSC_MaterialMapCore.Json(repeated)))
        for k in ('additions','palettes','coverage'):assert repeated[k]==audit[k],f'Offline Lua parity failed: {k}'
        changes={a['plot']:a['resource'] for a in audit['additions']}
        for p,q in zip(before['plots'],after['plots']):
            if p['index'] in changes:
                assert not p.get('resource') and q['resource']==changes[p['index']]
                assert {k:v for k,v in p.items() if k!='resource'}=={k:v for k,v in q.items() if k!='resource'}
            else:assert p==q
        census=continent_census(after,definitions);prior=continent_census(before,definitions)
        for row in audit['coverage']:
            new=next(q for c in census if c['id']==row['continent'] for q in c['quarters'] if q['quarter']==row['quarter'])
            assert new['common_clearable_both']==row['both_after'] and new['common_clearable_base']==row['base_after']
            assert not row['base_before'] or row['base_after'];assert not row['both_before'] or row['both_after']
        delta=sum(p.get('resource')!=q.get('resource') for p,q in zip(after['plots'],reference['data']['plots']))
        coverage={q:{'before':sum(c['id']!=-1 and next(r for r in c['quarters'] if r['quarter']==q)['common_clearable_both']>0 for c in prior),'after':sum(c['id']!=-1 and next(r for r in c['quarters'] if r['quarter']==q)['common_clearable_both']>0 for c in census)} for q in definitions}
        entry={'id':f'csc-helper-lua-{i}','group':'csc-helper-lua','groupLabel':'CSC helper · automatic Lua',
               'number':i,'settings':read(folder/'settings.json'),'data':after,'definitions':definitions,'reference':census[0]['quarters'],'continents':census,'source_sha256':sha(folder/'map.json'),
               'assistance':{'source_id':control['id'],'seed':audit['seed'],'additions':audit['additions'],'attempts':audit['attempts'],'palettes':audit['palettes'],'coverage':coverage,'before_continents':prior,**({'abundance':audit['abundance']} if 'abundance' in audit else {})},
               'provenance':{'native':True,'kind':'automatic-lua','warning':'Installed CSC Lua pass executed automatically during game initialization. CSC-owned deterministic RNG differs from the earlier Python prototype. Exact Lua decisions also reproduce offline using the captured native eligibility.'},
               'native_comparison':{'automatic':True,'preview_id':reference['id'],'offline_preview_id':f'csc-assist-{i}','resource_tile_differences':delta,'eligibility_checks':audit['eligibility_checks'],'deposits':len(changes),'control_tile_differences':comparison,'initialization_turn':audit['initialization_turn'],'phase':audit['phase'],'lua_parity':True}}
        write(folder/'viewer-map.json',entry)
        write(folder/'complete.json',{'automatic_lua_verified':True,'status':'complete','turn':1,'plots':3404,'deposits':len(changes),'lua_parity':True,'initialization_turn':audit['initialization_turn']})
        self.say(f'Map {i}: automatic Lua verified, {len(changes)} additions, initialization turn {audit["initialization_turn"]}, exact offline Lua replay')


def combine(bundle_path,out):
    entries=[read(p.parent/'viewer-map.json') for p in sorted(out.glob('csc-helper-lua/map-*/complete.json')) if read(p).get('automatic_lua_verified')]
    assert len(entries)==5
    # This run verifies Lua decisions using captured native eligibility; it does
    # not compare a separate offline habitat interpreter. Do not imply a measured
    # zero habitat discrepancy using the earlier API-test schema's field.
    for entry in entries:entry['native_comparison'].pop('eligibility_mismatches',None)
    bundle=read(bundle_path);bundle['maps']=[m for m in bundle['maps'] if m['group']!='csc-helper-lua']+entries;bundle['default_group']='csc-helper-lua'
    bundle_path.write_text(json.dumps(bundle,separators=(',',':')),encoding='utf-8');render(bundle,bundle_path.with_name('index.html'))
    rows=[]
    for q in entries[0]['definitions']:
        row={'quarter':q}
        for group,label in [('luxuries-4','original'),('csc-assist','offline_python'),('csc-helper-native','python_native_api'),('csc-helper-lua','automatic_lua')]:
            row[label]=sum(c['id']!=-1 and next(r for r in c['quarters'] if r['quarter']==q)['common_clearable_both']>0 for m in bundle['maps'] if m['group']==group for c in m['continents'])
        rows.append(row)
    write_csv(out/'coverage-comparison.csv',rows)
    write(out/'analysis.json',{'maps':5,'coverage':rows,'additions':{m['number']:len(m['assistance']['additions']) for m in entries},'all_exact_lua_parity':True})


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('output','bundle','lua-dependencies'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--first-only',action='store_true');p.add_argument('--combine-only',action='store_true');a=p.parse_args()
    if a.combine_only:combine(a.bundle,a.output);return
    r=AutomaticSurvey(a.output);r.bundle=read(a.bundle);r.lua_deps=a.lua_dependencies;r.pending_folder=None;r.save_maps=False
    try:
        r.wait('MainMenu');r.config();r.select_mods(False)
        write(a.output/'batch.json',{'status':'running','target_maps':5,'mode':'installed automatic Lua'})
        for i in range(1,6):
            marker=a.output/'csc-helper-lua'/f'map-{i:02d}'/'complete.json'
            if marker.exists() and read(marker).get('automatic_lua_verified'):continue
            r.number=i;r.pending_folder=marker.parent
            source=next(m for m in r.bundle['maps'] if m['id']==f'luxuries-4-{i}')
            r.start_map('csc-helper-lua',False,3,i,source['settings']['leaders'])
            if a.first_only:break
        done=sum(read(p).get('automatic_lua_verified',False) for p in a.output.glob('csc-helper-lua/map-*/complete.json'))
        write(a.output/'batch.json',{'status':'complete' if done==5 else 'partial','maps':done,'turns_advanced':0})
    except BaseException as exc:
        write(a.output/'batch.json',{'status':'interrupted','error':str(exc),'traceback':traceback.format_exc()});raise
    finally:
        r.pending_folder=None
        try:
            if 'MainMenu' not in r.states():r.menu()
            if (a.output/'original-preferences.json').exists():r.restore()
        except Exception as exc:r.say('Preferences restoration pending: '+str(exc))
    if done==5:combine(a.bundle,a.output)


if __name__=='__main__':main()
