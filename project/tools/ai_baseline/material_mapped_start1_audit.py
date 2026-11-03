"""Independent native150 audit for the exact initial-map resource-Farm test."""
import argparse,json,sqlite3,subprocess,time
from pathlib import Path
from material_care_audit import read,sha,require,unique_censuses,funding_gate
from material_forecast_audit import inventory
from material_farm_resource_forecast import verify_loaded
from material_mapped_improvement_forecast import verify_loaded as verify_mapped
from full_game_controller.continuation import world_signature
from full_game_controller.renderer_evidence import review as renderer_review
from material_site_viability import report as viability_report
from material_loss_intelligence import report as loss_report
from material_rejected_work_intelligence import report as work_report
from service_planner.benchmark_report import report_points

def audit(root,runtime):
    root=Path(root);S=Path('C:/Users/Shadow/Desktop/Codex/csc-material-care-v2-20261023');BASE=S/'run-01';V7=S/'raw-resource016-075-material-viability-v7'
    job,sup=read(root/'job-status.json'),read(root/'supervisor.json');require(job['status']=='complete'and job['native_endpoint']==150 and sup['status']=='complete'and sup['exit_code']==0,'Endpoint150/owners incomplete')
    require(not sup['native_fault_observed']and not(root/'native-fault-signal.json').exists(),'Native fault needs review')
    proof=read(root/'source-validation.json');require(proof['verified']and proof['turn']==1 and proof['loads']==1 and proof['new_worlds']==proof['pre1_AI_replay']==proof['recreated_sites']==0 and not proof['resource_pass_reapplied'],'Wrong initial-map provenance')
    require(proof['source_sha256']==sha(BASE/'exact-checkpoints/turn-001.Civ6Save')==read(BASE/'exact-checkpoints/turn-001.json')['sha256'],'Initial save hash differs')
    initial,after=read(root/'initial1.json'),read(root/'source1-after-setup.json');require(world_signature(initial['world'])==world_signature(read(BASE/'game-01/turn-001.json'))==world_signature(after['world']),'Initial world mismatch')
    require(initial['gold']==after['gold']and initial['units']==after['units']and not initial['world']['cities']and not[p for p in initial['world']['plots']if p.get('improvement')],'Unexpected initial world/units/Gold/improvements')
    pins=read(root/'executed-source-pins.json');require(all(sha(Path(p))==v for p,v in pins.items()),'Source pins changed');archive={sha(p)for p in(root/'source-version').iterdir()if p.is_file()};require(set(pins.values())<=archive,'Source archive missing')
    current=sqlite3.connect((root/'native-gameplay.sqlite').as_uri()+'?mode=ro',uri=True);base=sqlite3.connect((V7/'native-gameplay.sqlite').as_uri()+'?mode=ro',uri=True)
    try:farm=verify_loaded(current,base)
    finally:current.close();base.close()
    require(farm==read(root/'farm-resource-loaded-proof.json')and inventory(root/'native-gameplay.sqlite')==read(root/'native-database-inventory.json'),'Native Farm definitions differ')
    current=sqlite3.connect((root/'native-gameplay.sqlite').as_uri()+'?mode=ro',uri=True);control=sqlite3.connect((S/'resource-farm001-150-v9/native-gameplay.sqlite').as_uri()+'?mode=ro',uri=True)
    try:mapped=verify_mapped(current,control)
    finally:current.close();control.close()
    require(mapped==read(root/'mapped-improvement-loaded-proof.json'),'Mapped rule definitions differ')
    mapped_controls=excluded_controls=0
    for t in (1,25,50,75,100,125,150):
        v=read(root/'mapped-values'/f'turn-{t:03d}.json');ui=v['UI'];require(v['Core_turn']==t and ui['turn']in(t,t-1),'Mapped value clock differs')
        require(ui['failed_eligible']==ui['failed_excluded']==0,'Mapped value control failed')
        mapped_controls+=ui['eligible_isolated_controls'];excluded_controls+=ui['excluded_isolated_controls']
        for row in ui['rows']:
            if row.get('expected_private')is not None:require(row['private']==row['expected_private'],'Mapped row contradicts control')
    closed={1,25,50,75,100,125,150};primary=unique_censuses(root/'game-01',150);care=unique_censuses(root/'material-care',150);builders=unique_censuses(root/'builders',150);points=unique_censuses(root/'metric-points',150)
    require(set(primary)==set(care)==set(points)==closed and set(builders)==closed|{5},'Outcome coverage mismatch')
    for c in care.values():require(c['version']==3 and not c['errors']and c['calls']==c['strategy']['active_calls']+c['strategy']['inactive_calls']and care[150]['events'][:len(c['events'])]==c['events'],'Care error/prefix mismatch')
    for b in builders.values():require(not b['errors']and builders[150]['events'][:len(b['events'])]==b['events'],'Builder error/prefix mismatch')
    resource_controls=terrain_controls=0
    for t in closed:
        v=read(root/'farm-values'/f'turn-{t:03d}.json');ui=v['UI'];require(v['Core_turn']==t and ui['turn']in(t-1,t),'Value getter phase mismatch')
        require(ui['failed_resource_controls']==ui['failed_terrain_controls']==0,'Farm value control failed')
        resource_controls+=ui['isolated_resource_controls'];terrain_controls+=ui['isolated_terrain_controls']
        for row in ui['rows']:
            if row.get('expected_private')is not None:require(row['private']==row['expected_private'],'Value row contradicts control count')
        saved=read(root/'exact-checkpoints'/f'turn-{t:03d}.json');require(saved['verified']and saved['native_phase_unchanged']and saved['save_requests']==1 and saved['save_complete_event']and saved['sha256']==sha(root/'exact-checkpoints'/f'turn-{t:03d}.Civ6Save')and saved['planner_cycle_executed']==(t<150),'Exact checkpoint incomplete')
    research=read(root/'research-latest.json');require(research['turn']==150 and not research['errors'],'Research clock/errors');keys=[(v['turn'],v['player'])for v in research['history']];defeats={v['player']:v['turn']for v in research['defeats']};need={(t,p)for t in range(1,150)for p in range(1,6)if t<defeats.get(p,150)};optional={(t,p)for p,t in defeats.items()}
    require(len(keys)==len(set(keys))and not(need-set(keys))and not(set(keys)-(need|optional)),'Research gaps/duplicates')
    path=root/'service-actions.ndjson';rows=[json.loads(v)for v in path.read_text().splitlines()]if path.exists()else[]
    starts={v['request']['token']:v for v in rows if v['event']=='funded-acquisition-begin'};ends=[v for v in rows if v['event']=='funded-acquisition-confirmed'];require(len(ends)==len({v['request']['token']for v in ends})and starts.keys()=={v['request']['token']for v in ends},'Unclosed/duplicate economic mutation');funding=funding_gate([(v['request'],v['receipt'])for v in ends])
    for v in ends:
        matches=[read(p)for p in(root/'funded-acquisitions').glob('*receipt.json')if read(p)['token']==v['request']['token']];require(matches==[v['receipt']],'Economic raw receipt mismatch')
    begins=[v for v in rows if v['event']=='foundation-begin'];placed=[v for v in rows if v['event']=='foundation-confirmed'];key=lambda v:(v['player'],v['city'],v['quarter'],v['plot'])
    require(len(begins)==len(placed)==len({key(v)for v in placed})and {key(v)for v in begins}=={key(v)for v in placed},'Unclosed/duplicate foundation')
    g=read(root/'observations-latest.json');require(not g['errors']and len(g['targets'])==len(placed),'Target observer mismatch')
    physical={d['plot']:(c,d)for c in primary[150]['cities']for d in c['districts']if d.get('type','').startswith('DISTRICT_CSC_')};foundation=[]
    for v in placed:
        p=read(root/'placements'/f"{v['turn']}-{v['player']}-{v['city']}-{v['quarter']}"/'validation.json');z=p['proof'];require(z['verified']and z['native_incomplete']and z['queue_unchanged']and z['progress_before']==z['progress_after']==0 and z['cost_before']==z['cost_after']>0,'Zero-progress proof failed')
        require(all(p['before'][k]==p['after'][k]for k in('queue','queue_size','current_hash')),'Production queue changed')
        t=next(t for t in g['targets']if t['plot']==v['plot']and t['quarter']==v['quarter']);require(t.get('require_both_materials')is True,'Both guard missing');city,district=physical.get(v['plot'],(None,None));complete=bool(district and district['complete'])
        events=[e for e in g['events']if e['order']==2 and e['item']==t['districtIndex']and not e['cancelled']and e['turn']>=v['turn']and e['player']in{v['player'],city['player']if city else v['player']}and e['city']in{v['city'],city['id']if city else v['city']}]
        require(not complete or events,'Physical completion without native event');foundation.append(dict(player=v['player'],plot=v['plot'],quarter=v['quarter'],turn=v['turn'],complete=complete,first_completion=min((e['turn']for e in events),default=None)))
    viability=viability_report(root);require(viability['placements']==viability['precommit_observed']==len(placed)and viability['failed_Both_structural_gate']==viability['unknown_Both_gate']==0,'Precommit material gate failed/missing')
    restored=read(root/'final-restoration.json');require(all(restored[k]for k in('verified','all_Civ_absent','pretest510_equal','prefs144','normal_exit_issued'))and not restored['autostart'],'Restoration incomplete');prefs=read(root/'preferences-restoration.json');require(prefs['verified']and prefs['mods']==144 and not prefs['auto_start'],'Preferences not verified')
    raw=subprocess.run(['powershell','-NoProfile','-Command',"Get-CimInstance Win32_Process | Where-Object { $_.Name -like 'CivilizationVI*' -or ($_.Name -match '^python' -and $_.CommandLine -match 'mapped-improvements-start1-(worker|job)\\.py') } | Select-Object ProcessId,CommandLine | ConvertTo-Json -Compress"],capture_output=True,text=True,check=True).stdout.strip();require(not raw,'Game/controller owner alive')
    runtime=Path(runtime);actual={str(p.relative_to(runtime)):{'sha256':sha(p),'size':p.stat().st_size}for p in runtime.rglob('*')if p.is_file()};require(actual==read(BASE/'pretest-runtime-manifest.json'),'Original510 runtime differs')
    final=read(root/'candidate-runtime-verification.json');require(final['verified']and final['source_pins_verified']and final['files']==517,'Final candidate/source verification missing')
    require(renderer_review(root)['at_or_after_run_start_events']==0,'Native graphics signal needs review')
    return dict(verified=True,mapped_improvement_definitions=mapped,native_mapped_positive_control_observations=mapped_controls,native_exclusion_control_observations=excluded_controls,new_native_incentive_application_observed=mapped_controls>0,endpoint=150,source_turn=1,source_sha256=proof['source_sha256'],new_worlds=0,initial_map_no_improvements=True,full_historical_nonBuilder_reference='UNOBSERVED; initial save hash + fresh before/after census',pins=len(pins),native_tables=len(inventory(root/'native-gameplay.sqlite')),resource_Farm_definitions=farm,isolated_resource_control_observations=resource_controls,isolated_terrain_control_observations=terrain_controls,Farm_value_application_observed=resource_controls>0,terrain_zero_native_control_observed=terrain_controls>0,native_AI_decision_change_proven_by_this_audit=False,research_rows=len(keys),funding=funding,foundations=foundation,material_viability=viability,AI_counts=points[150]['counts'],cohorts=report_points(list(points.values()),g['targets']),losses=loss_report(root,150),work=work_report(root,150),runtime_restored510=True,prefs144=True,actual_Service_payments='UNOBSERVED',later_baseline_comparison_is_descriptive=True,time=time.time())
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--runtime',required=True,type=Path);p.add_argument('--output',required=True,type=Path);a=p.parse_args();value=audit(a.root,a.runtime);a.output.write_text(json.dumps(value,indent=2),encoding='utf-8');print(json.dumps({k:value[k]for k in('verified','endpoint','AI_counts','funding','Farm_value_application_observed','terrain_zero_native_control_observed')}))
