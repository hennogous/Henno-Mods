"""Independent offline accepted-prefix audit for source75 mature follow-through."""
import argparse,json,subprocess,time
from pathlib import Path
from material_care_audit import funding_gate,require,read,sha,unique_censuses
from material_forecast_audit import inventory
from material_mature_contract import source_gate,no_setup_effect,production_gate,endpoint_action_gate
from material_site_viability import report as viability_report
from material_loss_intelligence import report as loss_report
from log_intelligence import repair_episodes
from full_game_controller.renderer_evidence import review as renderer_review
from service_planner.benchmark_report import report_points


def audit(root,runtime):
    root=Path(root);parent=root.parent;meta=read(root/'preparation.json');proof=read(root/'source-validation.json')
    job,sup=read(root/'job-status.json'),read(root/'supervisor.json')
    require(job['status']=='complete'and job['native_endpoint']==175 and sup['status']=='complete'and sup['exit_code']==0,'Endpoint/owners incomplete')
    require(not sup['native_fault_observed']and not(root/'native-fault-signal.json').exists(),'Native fault needs independent review')
    require(read(parent/'independent-diagnostic-audit.json')['verified']and sha(parent/'independent-diagnostic-audit.json')==meta['parent_audit_sha256']==proof['parent_audit_sha256'],'Parent audit provenance changed')
    require(proof['verified']and proof['loads']==1 and proof['pre75_AI_replay']==proof['new_worlds']==proof['recreated_sites']==0,'Invalid continuation')
    require(sha(parent/'exact-checkpoints/turn-075.Civ6Save')==meta['source_sha256']==proof['source_sha256'],'Wrong75 source')
    initial=read(root/'source75-initial.json');before_care=read(root/'source75-care-baseline.json')
    recomputed=source_gate(parent_world=read(parent/'game-01/turn-075.json'),world=initial['world'],parent_cash=read(parent/'metric-points/turn-075.json')['treasury_cashflow'],gold=initial['gold'],parent_allocation=read(parent/'final-native-private-snapshot.json'),allocation=read(root/'source75-allocation.json'),parent_builders=read(parent/'builders/turn-075.json'),builders=read(root/'source75-builders.json'),parent_care=read(parent/'material-care/turn-075.json'),care=before_care)
    require(recomputed==proof['world_parity']==read(root/'source75-world-parity.json'),'Source gate cannot be reproduced')
    require(no_setup_effect(initial,read(root/'source75-after-setup.json'))==proof['setup_no_effect'],'Setup changed world/units/gold')
    # Capture files retain restored history and their original validation reason.
    g,u=read(root/'observations-latest.json'),read(root/'ui-observations-latest.json')
    parent_g,parent_u=read(parent/'observations-latest.json'),read(parent/'ui-observations-latest.json')
    # Targets may grow after source75; use only the restored source target set.
    source_g=dict(g,targets=parent_g['targets'])
    require(production_gate(parent_g,parent_u,source_g,u,reason='source75-production-parity')==read(root/'source75-production-parity.json'),'Unproven initial production parity')
    parent_rows=[json.loads(x)for x in(parent/'service-actions.ndjson').read_text().splitlines()]
    require(endpoint_action_gate(parent_rows)==proof['cycle'],'Parent75 action timeline incorrect')
    pins=read(root/'executed-source-pins.json');require(all(sha(Path(p))==v for p,v in pins.items()),'Executed source changed')
    archive={sha(p)for p in(root/'source-version').iterdir()if p.is_file()};require(set(pins.values())<=archive,'Incomplete source archive')
    require(inventory(root/'native-gameplay.sqlite')==read(parent/'native-database-inventory.json')==read(root/'native-database-inventory.json'),'Native DB differs')
    require(read(root/'expected-installed-manifest.json')==read(parent/'expected-installed-manifest.json'),'Runtime treatment changed')
    restored=read(root/'final-restoration.json');require(all(restored[k]for k in('verified','all_Civ_absent','pretest510_equal','prefs144','normal_exit_issued'))and restored['autostart']is False,'Cleanup incomplete')
    prefs=read(root/'preferences-restoration.json');require(prefs['verified']and prefs['mods']==144 and prefs['auto_start']is False,'Preferences mismatch')
    raw=subprocess.run(['powershell','-NoProfile','-Command',"Get-CimInstance Win32_Process | Where-Object { $_.Name -like 'CivilizationVI*' -or ($_.Name -match '^python' -and ($_.CommandLine -like '*material-mature-worker.py*' -or $_.CommandLine -like '*material-mature-job.py*')) } | Select-Object ProcessId,CommandLine | ConvertTo-Json -Compress"],capture_output=True,text=True,check=True).stdout.strip();require(not raw,'Owner or Civ still alive')
    runtime=Path(runtime);actual={str(p.relative_to(runtime)):{'sha256':sha(p),'size':p.stat().st_size}for p in runtime.rglob('*')if p.is_file()};require(actual==read(parent/'pretest-runtime-manifest.json'),'Original510 not restored')
    final_package=read(root/'candidate-runtime-verification.json');require(final_package['verified']and final_package['source_pins_verified']and final_package['files']==515,'Final candidate/pins missing')
    require(all(sha(root/'runtime-deltas'/p)==read(parent/'expected-installed-manifest.json')[p]['sha256']for p in restored['restored_delta']),'Archived candidate delta differs')
    clocks={1,16,25,50,75,100,125,150,175};primary=unique_censuses(root/'game-01',175);require(set(primary)==clocks,'Primary coverage incomplete')
    for t in(1,16,25,50):require(sha(root/'game-01'/f'turn-{t:03d}.json')==sha(parent/'game-01'/f'turn-{t:03d}.json'),'Inherited primary changed')
    builders=unique_censuses(root/'builders',175);require(set(builders)==clocks|{5},'Builder coverage incomplete');final_b=builders[175]
    require(not final_b['errors']and final_b['events'][:len(read(parent/'builders/turn-075.json')['events'])]==read(parent/'builders/turn-075.json')['events'],'Builder prefix lost')
    for value in builders.values():require(not value['errors']and final_b['events'][:len(value['events'])]==value['events'],'Builder prefix drift')
    care=unique_censuses(root/'material-care',175);require(set(care)=={75,100,125,150,175},'Care coverage incomplete');final_c=care[175]
    for value in care.values():require(value['version']==3 and not value['errors']and value['calls']==value['strategy']['active_calls']+value['strategy']['inactive_calls']and final_c['events'][:len(value['events'])]==value['events'],'Care errors/counter drift')
    rows=[json.loads(x)for x in(root/'service-actions.ndjson').read_text().splitlines()];require(rows[:len(parent_rows)]==parent_rows,'Economic parent prefix changed')
    starts={v['request']['token']:v for v in rows if v['event']=='funded-acquisition-begin'};closed=[v for v in rows if v['event']=='funded-acquisition-confirmed']
    require(len(closed)==len({v['request']['token']for v in closed})and starts.keys()=={v['request']['token']for v in closed},'Unclosed/duplicate financial action')
    funding=funding_gate([(v['request'],v['receipt'])for v in closed])
    for v in closed:
        if v['request']['turn']<75:continue
        matches=[read(p)for p in(root/'funded-acquisitions').glob('*-receipt.json')if read(p)['token']==v['request']['token']];require(matches==[v['receipt']],'Raw economic receipt mismatch')
    begins=[v for v in rows if v['event']=='foundation-begin'];placed=[v for v in rows if v['event']=='foundation-confirmed'];key=lambda v:(v['player'],v['city'],v['quarter'],v['plot'])
    require(len(begins)==len(placed)==len({key(v)for v in placed})and {key(v)for v in begins}=={key(v)for v in placed},'Unclosed/duplicate foundation')
    require(len(g['targets'])==len(placed)and not g['errors']and not u['errors'],'Observer target/error mismatch')
    physical={d['plot']:(city,d)for city in primary[175]['cities']for d in city['districts']if d.get('type','').startswith('DISTRICT_CSC_')};sites=[]
    for v in placed:
        inherited=v['turn']<75;owner=parent if inherited else root
        validation=read(owner/'placements'/f"{v['turn']}-{v['player']}-{v['city']}-{v['quarter']}"/'validation.json');p=validation['proof']
        require(p['verified']and p['native_incomplete']and p['queue_unchanged']and p['progress_before']==p['progress_after']==0 and p['cost_before']==p['cost_after']>0,'Invalid zero-progress proof')
        require(all(validation['before'][k]==validation['after'][k]for k in('queue','queue_size','current_hash')),'Queue overwritten')
        t=next(t for t in g['targets']if t['plot']==v['plot']and t['quarter']==v['quarter']);require(t.get('require_both_materials')is True,'Both native target flag missing')
        city,district=physical.get(v['plot'],(None,None));complete=bool(district and district['complete'])
        events=[e for e in g['events']if e['order']==2 and e['item']==t['districtIndex']and not e['cancelled']and e['turn']>=v['turn']and e['player']in{v['player'],city['player']if city else v['player']}and e['city']in{v['city'],city['id']if city else v['city']}]
        require(not complete or events,'Physical completion without native event');sites.append(dict(player=v['player'],plot=v['plot'],quarter=v['quarter'],turn=v['turn'],inherited=inherited,complete=complete,first_completion=min((e['turn']for e in events),default=None)))
    viability=viability_report(root);new_sites=sum(v['turn']>=75 for v in placed)
    require(viability['placements']==viability['precommit_observed']==new_sites and viability['failed_Both_structural_gate']==viability['unknown_Both_gate']==0,'New material precommit quality failed or missing')
    research=read(root/'research-latest.json');require(research['turn']==175 and not research['errors'],'Wrong research clock/errors');keys=[(v['turn'],v['player'])for v in research['history']]
    defeats={v['player']:v['turn']for v in research['defeats']};need={(t,p)for t in range(1,175)for p in range(1,6)if t<defeats.get(p,175)};optional={(t,p)for p,t in defeats.items()}
    require(len(keys)==len(set(keys))and not(need-set(keys))and not(set(keys)-(need|optional)),'Research gaps/duplicates')
    require([v for v in research['history']if v['turn']<75]==read(parent/'research-latest.json')['history'],'Research prefix altered')
    points=unique_censuses(root/'metric-points',175);require(set(points)==clocks-{1},'Wrong outcome clocks')
    for t in(75,100,125,150,175):
        receipt=read(root/'exact-checkpoints'/f'turn-{t:03d}.json');require(receipt['verified']and receipt['turn']==t and receipt['native_phase_unchanged']and receipt['save_requests']==1 and receipt['save_complete_event']and receipt['sha256']==sha(root/'exact-checkpoints'/f'turn-{t:03d}.Civ6Save')and receipt['planner_cycle_executed']==(t<175)and receipt['post_action_current_census'],'Exact source checkpoint incomplete')
    graphics=renderer_review(root);require(graphics['at_or_after_run_start_events']==0,'Graphics errors')
    losses=loss_report(root,175)
    return dict(verified=True,endpoint=175,source_turn=75,source_sha256=proof['source_sha256'],new_worlds=0,pre75_replay=0,parent_counterfactual='16..75, separate trajectory from accepted main192',source_gate=recomputed,care_age_boundary_censored=True,material_events_scope='Child75..175; parent16..75 audited separately; reload baseline is not AI action',pins=len(pins),native_tables=len(inventory(root/'native-gameplay.sqlite')),runtime_restored510=True,prefs144=True,funding=funding,new_tile_acquisitions=funding['tiles']-8,new_cost=funding['cost']-345,new_fallback=funding['fallback']-139,foundations=sites,new_material_viability=viability,research_rows=len(keys),care_calls=final_c['calls'],care_strategy=final_c['strategy'],loss_attribution=losses,repairs=repair_episodes(final_c['events'],final_b['events'],primary[175]['width']),AI_counts=points[175]['counts'],cohorts=report_points(list(points.values()),g['targets']),actual_Service_payments='UNOBSERVED',whole_mod_causal_effect_established=False,time=time.time())

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('root',type=Path);p.add_argument('--runtime',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();value=audit(a.root,a.runtime);a.output.write_text(json.dumps(value,indent=2),encoding='utf-8');print(json.dumps({k:value[k]for k in('verified','endpoint','funding','new_tile_acquisitions','AI_counts')}))
