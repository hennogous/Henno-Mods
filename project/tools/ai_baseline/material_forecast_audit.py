"""Independent offline audit of source16..75 forecast diagnostics, never native."""
import argparse,collections,hashlib,json,sqlite3,subprocess,time
from pathlib import Path
from material_care_audit import funding_gate,require,read,sha,unique_censuses
from material_forecast_contract import source_parity,database_delta
from material_forecast_variants import variant,declared_database_delta,verify_raw_control
from native_harvest_rule import verify_live as verify_native_rule
from material_loss_intelligence import report as loss_report
from log_intelligence import repair_episodes
from service_planner.benchmark_report import report_points
from full_game_controller.renderer_evidence import review as renderer_review

def inventory(path):
    db=sqlite3.connect(path.as_uri()+'?mode=ro',uri=True);out={}
    for name, in db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"):
        rows=sorted(json.dumps(list(x),ensure_ascii=False,default=str)for x in db.execute('SELECT * FROM "'+name.replace('"','""')+'"'));out[name]=dict(rows=len(rows),sha256=hashlib.sha256('\n'.join(rows).encode()).hexdigest())
    db.close();return out

def audit(root,runtime):
    root=Path(root);S=root.parent;P=S/'run-01';C=S/'source016-control';PREP=S/'offline-preparation/source016-forecast-pair';PREFIX=S/'offline-preparation/source016-prefix'
    job=read(root/'job-status.json');sup=read(root/'supervisor.json');arm=job['arm'];treatment=arm=='raw-resource';require(arm in('reference','raw-resource'),'Wrong arm')
    cfg=variant(S,arm,read(root/'source.json').get('branch'));PREP=cfg['preparation'];trial=read(PREP/'preparation.json');raw_control=verify_raw_control(trial,S)if cfg['needs_raw_control']else None
    require(job['status']=='complete'and job['native_endpoint']==75 and sup['status']=='complete'and sup['exit_code']==0,'Endpoint/job/owners incomplete')
    require(not sup['native_fault_observed']and not(root/'native-fault-signal.json').exists(),'Native signal needs investigation')
    proof=read(root/'source-validation.json');require(proof['verified']and proof['turn']==16 and proof['loads']==1 and proof['new_worlds']==0 and proof['AI_turns_before_parity']==0 and proof.get('explicit_economic_commands_before_parity',proof.get('economic_effects_before_parity'))==0,'Unproven source boundary')
    require(proof['source_sha256']==read(C/'control-verification.json')['source_sha256']==sha(Path(read(root/'source.json')['source'])),'Source hash drift')
    reference={k:read(C/name)for k,name in [('world','world.json'),('units','units.json'),('gold','all-major-treasuries.json'),('private','private-plot-yields.json'),('production','production-and-quotes.json')]}
    initial=read(root/'source16-initial.json');allocation_proof=None
    if proof.get('observer_treatment_spillover'):
        allocation_proof=read(S/'source16-citizen-allocation-audit.json');require(allocation_proof['source_sha256']==proof['source_sha256'],'Allocation proof source differs')
        reference['allocation']=read(S/'source016-citizen-reference-v2/final-worker-allocation.json')
        provenance=read(root/'observer-allocation-provenance.json');require(provenance['proof_sha256']==sha(S/'source16-citizen-allocation-audit.json')and provenance['reference_audit_sha256']==sha(S/'reference016-075/independent-diagnostic-audit.json'),'Allocation/reference receipt provenance changed')
        from worker_allocation_contract import allocations_stable
        require(allocations_stable(initial['allocation'],read(root/'source16-final-allocation.json')),'Startup citizen assignment moved after validation')
    parity=source_parity(reference,initial,read(PREP/'preparation.json')['raw_resource_yields']if treatment else{},observer_allocation_proof=allocation_proof)
    actual_db=inventory(root/'native-gameplay.sqlite');changes=declared_database_delta(read(P/'native-database-inventory.json'),actual_db,treatment=treatment,boost_gate=cfg['boost_gate'],pasture_forecast=cfg['pasture_forecast'],resource_improvement_forecast=cfg['resource_improvement_forecast'],raw_control=read(raw_control/'native-database-inventory.json')if raw_control else None)
    require(actual_db==read(PREP/'treatment-native-database-inventory.json'if treatment else P/'native-database-inventory.json'),'Native database mismatch')
    if cfg['boost_gate']:
        require(proof['boost_gate_diagnostic']and proof['native_database_delta']==changes and proof['raw_control_audit_sha256']==sha(raw_control/'independent-diagnostic-audit.json'),'Boost-gate/control provenance missing')

    if cfg['needs_raw_control']:require(proof['raw_control_audit_sha256']==sha(raw_control/'independent-diagnostic-audit.json')and proof['native_database_delta']==changes,'Declared raw control/database provenance changed')
    if cfg['pasture_forecast']:
        from material_pasture_forecast import verify_loaded,verify_source
        current_sql=sqlite3.connect((root/'native-gameplay.sqlite').as_uri()+'?mode=ro',uri=True);raw_sql=sqlite3.connect((raw_control/'native-gameplay.sqlite').as_uri()+'?mode=ro',uri=True)
        try:loaded=dict(native=verify_loaded(current_sql,raw_sql),source=verify_source(initial))
        finally:current_sql.close();raw_sql.close()
        require(proof['pasture_forecast_diagnostic']and not proof['runtime_harvest_rule']and proof['pasture_forecast_source_proof']==loaded==read(root/'pasture-forecast-source-proof.json'),'Unproven direct forecast source/table scope')
        require(not list((root/'pending-commands').glob('*-native-harvest-attach-once.lua'))and not(root/'native-rule-activation.json').exists(),'Harvest rule must remain OFF in forecast arm')
        from material_pasture_forecast import verify_final_snapshot
        require(verify_final_snapshot(read(root/'final-native-private-snapshot.json'),read(root/'game-01/turn-075.json'),read(root/'final-native-private-boundary.json'))==read(root/'final-pasture-private-proof.json'),'Final actual Pasture/private-yield snapshot inconsistent')
    if cfg['resource_improvement_forecast']:
        from material_resource_improvement_forecast import verify_loaded,verify_source,verify_final_snapshot
        current_sql=sqlite3.connect((root/'native-gameplay.sqlite').as_uri()+'?mode=ro',uri=True);raw_sql=sqlite3.connect((raw_control/'native-gameplay.sqlite').as_uri()+'?mode=ro',uri=True)
        try:loaded=dict(native=verify_loaded(current_sql,raw_sql),source=verify_source(initial))
        finally:current_sql.close();raw_sql.close()
        require(proof['resource_improvement_forecast_diagnostic']and not proof['runtime_harvest_rule']and proof['resource_improvement_forecast_source_proof']==loaded==read(root/'resource-improvement-forecast-source-proof.json'),'Three-type source/table proof missing')
        require(not list((root/'pending-commands').glob('*-native-harvest-attach-once.lua'))and not(root/'native-rule-activation.json').exists(),'Harvest rule must remain OFF')
        require(verify_final_snapshot(read(root/'final-native-private-snapshot.json'),read(root/'game-01/turn-075.json'),read(root/'final-native-private-boundary.json'))==read(root/'final-resource-improvement-private-proof.json'),'Final native improvement snapshot inconsistent')
    if cfg['runtime_harvest_rule']:
        require(proof['runtime_harvest_rule']and proof['rule_attachments_after_base_parity']==5 and read(root/'base-source16-before-rule.json')['verified'],'Missing declared native-rule activation boundary')
        require(not read(root/'native-rule-before.json')['instances']and read(root/'native-rule-before.json').get('ledger')is None,'Preexisting native rule effects')
        samples=read(root/'native-rule-readbacks.json');require(len(samples)==3,'Wrong runtime proof coverage')
        for sample in samples:verify_native_rule(sample)
        verify_native_rule(read(root/'native-rule-confirmed.json'),confirmed=True)
        measured=None
        if cfg['measured_rule_legality']:
            path=Path(trial['measured_legality_proof']);require(sha(path)==trial['measured_legality_proof_sha256'],'Measured legality receipt changed');measured=read(path)
        source_parity(initial,read(root/'post-native-rule-source16.json'),{},native_rule_legality_proof=measured,native_rule_runtime=read(root/'native-rule-confirmed.json')if measured else None)
        from worker_allocation_contract import allocations_stable
        require(allocations_stable(initial['allocation'],read(root/'post-native-rule-allocation.json')),'Rule changed native citizen allocation before advance')
    pins=read(root/'executed-source-pins.json');require(all(sha(Path(p))==h for p,h in pins.items()),'Executed source changed');archived={sha(p)for p in(root/'source-version').iterdir()if p.is_file()};require(set(pins.values())<=archived,'Source archives incomplete')
    restored=read(root/'final-restoration.json');require(restored['verified']and restored['all_Civ_absent']and restored['pretest510_equal']and restored['prefs144']and restored['autostart']is False and restored['normal_exit_issued'],'Normal exit/restoration missing')
    pref=read(root/'preferences-restoration.json');require(pref['verified']and pref['mods']==144 and pref['auto_start']is False,'Native saved preferences not verified')
    raw=subprocess.run(['powershell','-NoProfile','-Command',"Get-CimInstance Win32_Process | Where-Object { $_.Name -like 'CivilizationVI*' -or ($_.Name -match '^python' -and ($_.CommandLine -like '*material-forecast-worker.py*' -or $_.CommandLine -like '*material-forecast-job.py*')) } | Select-Object ProcessId,CommandLine | ConvertTo-Json -Compress"],capture_output=True,text=True,check=True).stdout.strip();require(not raw,'Native/experiment controller owner still alive')
    runtime=Path(runtime);actual={str(p.relative_to(runtime)):{'sha256':sha(p),'size':p.stat().st_size}for p in runtime.rglob('*')if p.is_file()};require(actual==read(P/'pretest-runtime-manifest.json'),'Original510 not restored')
    require(read(root/'candidate-runtime-verification.json')['verified']and read(root/'candidate-runtime-verification.json')['source_pins_verified'],'Candidate final hashes missing')
    expected=read(root/'expected-installed-manifest.json');require(expected==read(PREP/('treatment-runtime-manifest.json'if treatment else'reference-runtime-manifest.json')),'Wrong candidate manifest')
    require(all(sha(root/'runtime-deltas'/p)==expected[p]['sha256']for p in restored['restored_delta']),'Archived runtime delta mismatch')
    primary=unique_censuses(root/'game-01',75);require(set(primary)=={1,16,25,50,75},'Wrong primary clocks')
    require(sha(root/'game-01/turn-001.json')==sha(P/'game-01/turn-001.json'),'Inherited1 changed')
    builders=unique_censuses(root/'builders',75);require(set(builders)=={1,5,16,25,50,75},'Wrong Builder clocks');B=builders[75];require(not B['errors'],'Builder errors')
    for b in builders.values():require(not b['errors']and B['events'][:len(b['events'])]==b['events'],'Builder prefix changed')
    require(B['events'][:len(read(PREFIX/'Builder-event-prefix.json'))]==read(PREFIX/'Builder-event-prefix.json'),'Inherited Builder events lost')
    care=unique_censuses(root/'material-care',75);require(set(care)=={16,25,50,75},'Wrong care coverage');finalcare=care[75]
    for x in care.values():require(x['version']==3 and not x['errors']and x['calls']==x['strategy']['active_calls']+x['strategy']['inactive_calls']and finalcare['events'][:len(x['events'])]==x['events'],'Care callback/event error')
    rows=[json.loads(x)for x in(root/'service-actions.ndjson').read_text(encoding='utf-8').splitlines()if x.strip()];prefix=[json.loads(x)for x in(PREFIX/'service-actions.ndjson').read_text(encoding='utf-8').splitlines()if x.strip()];require(rows[:len(prefix)]==prefix,'Economic prefix changed')
    starts={x['request']['token']:x for x in rows if x['event']=='funded-acquisition-begin'};closed=[x for x in rows if x['event']=='funded-acquisition-confirmed'];require(len(closed)==len({x['request']['token']for x in closed})and set(starts)=={x['request']['token']for x in closed},'Unclosed/duplicate acquisition')
    funding=funding_gate([(x['request'],x['receipt'])for x in closed])
    for x in closed:
        if x['request']['turn']<16:continue
        receipts=[read(p)for p in(root/'funded-acquisitions').glob('*receipt.json')if read(p)['token']==x['receipt']['token']];require(receipts==[x['receipt']],'Economic raw/journal receipt mismatch')
    require(sum(x['request']['turn']<16 for x in closed)==1,'Inherited purchase not exactly once')
    starts=[x for x in rows if x['event']=='foundation-begin'];placed=[x for x in rows if x['event']=='foundation-confirmed'];key=lambda x:(x['player'],x['city'],x['plot'],x['quarter'])
    require(len(starts)==len(placed)==len({key(x)for x in placed})and {key(x)for x in starts}=={key(x)for x in placed},'Unclosed/duplicate foundation')
    obs=read(root/'observations-latest.json');require(not obs['errors']and len(obs['targets'])==len(placed),'Foundation observer mismatch')
    physical={d['plot']:(city,d)for city in primary[75]['cities']for d in city['districts']if d.get('type','').startswith('DISTRICT_CSC_')};proofs=[]
    for x in placed:
        require(16<=x['turn']<75,'Placement outside diagnostic interval')
        v=read(root/'placements'/f"{x['turn']}-{x['player']}-{x['city']}-{x['quarter']}"/'validation.json');p=v['proof'];cand=v['candidate'];require(p['verified']and p['native_incomplete']and p['queue_unchanged']and p['progress_before']==p['progress_after']==0 and p['cost_before']==p['cost_after']>0,'Invalid0% proof')
        require(cand['owned_base']>0 and cand['owned_specialty']>0 and not cand['same_quarter_present']and cand['current_legal']and not cand['missing_tiles'],'Materials/legality missing')
        require(all(v['before'][k]==v['after'][k]for k in('queue','queue_size','current_hash'))and v['native']['district_present']and not v['native']['complete'],'Queue/native incompleteness mismatch')
        target=next(t for t in obs['targets']if t['plot']==x['plot']and t['quarter']==x['quarter']);city,district=physical.get(x['plot'],(None,None));complete=bool(district and district['complete']);events=[e for e in obs['events']if e['order']==2 and e['item']==target['districtIndex']and not e['cancelled']and e['turn']>=x['turn']and e['player']in{x['player'],city['player']if city else x['player']}and e['city']in{x['city'],city['id']if city else x['city']}]
        require(not complete or events,'Physical completion lacks native event');proofs.append(dict(player=x['player'],plot=x['plot'],quarter=x['quarter'],placed_turn=x['turn'],complete=complete,first_completion_event=min((e['turn']for e in events),default=None)))
    viability=None
    if cfg['material_viability']:
        from material_site_viability import report as viability_report
        viability=viability_report(root)
        require(viability['placements']==viability['precommit_observed']==len(placed)and viability['unknown_Both_gate']==viability['failed_Both_structural_gate']==0,'Material viability failed or missing at exact precommit observation')
        require(proof['material_viability_diagnostic'],'Undeclared material-viability treatment')
        require(all(t.get('require_both_materials')is True for t in obs['targets']),'Selected Both property missing from native target')
    research=read(root/'research-latest.json');require(research['turn']==75 and not research['errors'],'Research errors/wrong clock');keys=[(x['turn'],x['player'])for x in research['history']];require(len(keys)==len(set(keys)),'Duplicate research');defeats={x['player']:x['turn']for x in research['defeats']};need={(t,p)for t in range(1,75)for p in range(1,6)if t<defeats.get(p,75)};optional={(t,p)for p,t in defeats.items()};require(not(need-set(keys))and not(set(keys)-(need|optional)),'Research gap/scope')
    if cfg['runtime_harvest_rule']:
        finalrule=read(root/'native-rule-final.json');require(finalrule['turn']==75 and not finalrule['active']and finalrule['definition']=='TRAIT_MAORI_PREVENT_HARVEST'and finalrule['ledger']['status']=='confirmed','Final native-rule state missing')
        survivors=set(range(1,6))-set(defeats);live_rows=[x for x in finalrule['instances']if x['player']in survivors]
        require({x['player']for x in live_rows}==survivors and len(live_rows)==len(survivors)and all(x['active']for x in live_rows)and all(x['player']in range(1,6)for x in finalrule['instances']),'Native rule inactive/unexpected surviving owner')
    inherited=read(PREFIX/'research-prefix.json')['history'];require([x for x in research['history']if x['turn']<16]==inherited,'Inherited research changed')
    points=unique_censuses(root/'metric-points',75);require(set(points)=={16,25,50,75},'Wrong metric coverage');cohorts=report_points(list(points.values()),obs['targets'])
    graphics=renderer_review(root);require(graphics['at_or_after_run_start_events']==0,'Graphics errors/unknown evidence');losses=loss_report(root,75)
    return dict(verified=True,arm=arm,branch=cfg['branch'],boost_gate_diagnostic=cfg['boost_gate'],pasture_forecast_diagnostic=cfg['pasture_forecast'],resource_improvement_forecast_diagnostic=cfg['resource_improvement_forecast'],material_viability_diagnostic=cfg['material_viability'],material_viability=viability,runtime_harvest_rule=cfg['runtime_harvest_rule'],measured_rule_legality=cfg['measured_rule_legality'],raw_control_audit_sha256=trial.get('raw_control_audit_sha256'),source16_parity=parity,observer_treatment_spillover=parity['observer_treatment_spillover'],mechanism_scope='Broad resource forecast including measured observer allocation effect; not AI-only release',source_sha256=proof['source_sha256'],endpoint=75,raw_replay_range='16..75',new_worlds=0,inherited_research=75,inherited_paid_steps=1,native_database_delta=changes,native_tables=len(actual_db),runtime_restored510=True,prefs144=True,pins=len(pins),funding=funding,new_tile_acquisitions=funding['tiles']-1,new_gold_spent=funding['cost']-25,new_donations=funding['fallback'],foundations=proofs,research_rows=len(keys),care_calls=finalcare['calls'],care_strategy=finalcare['strategy'],repair_episodes=repair_episodes(finalcare['events'],B['events'],primary[75]['width']),loss_attribution=losses,cohorts=cohorts,AI_counts=points[75]['counts'],actual_Service_payments='UNOBSERVED',whole_mod_causal_effect_established=False,time=time.time())

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('root',type=Path);p.add_argument('--runtime',required=True,type=Path);p.add_argument('--output',required=True,type=Path);a=p.parse_args();v=audit(a.root,a.runtime);a.output.write_text(json.dumps(v,indent=2),encoding='utf-8');print(json.dumps({k:v[k]for k in('verified','arm','endpoint','funding','new_tile_acquisitions','AI_counts')}))
