"""Independent OFFLINE audit of a fresh material-care run or explicit prefix.

No native imports or socket client. A prefix audit cannot satisfy the completion
 gate; full results require endpoint artifacts and both controller exits0.
"""
import argparse,collections,hashlib,json,math,sqlite3,subprocess,time
from pathlib import Path
from full_game_controller.renderer_evidence import review as renderer_review
from service_planner.benchmark_report import report_points
from material_loss_intelligence import report as loss_report
from log_intelligence import repair_episodes

def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def require(value,message):
    if not value:raise AssertionError(message)

def completion_gate(job,supervisor,through,endpoint,full):
    if full:
        require(through==endpoint,'Prefix cannot pass full endpoint gate')
        require(job.get('status')=='complete'and job.get('native_endpoint')==endpoint,'Native endpoint/job incomplete')
        require(supervisor.get('status')=='complete'and supervisor.get('exit_code')==0,'Supervisor not complete0')
    return bool(full)

def terminal_gate(job,supervisor,proof,through,endpoint):
    require(through<endpoint,'Terminal partial must remain below endpoint')
    require(job.get('status')=='failed'and supervisor.get('status')=='attention'and supervisor.get('exit_code')==1,'Original failure artifacts must be retained')
    require(proof.get('verified')and proof.get('turn')==through,'Terminal inspection missing')
    require(proof.get('observer_alive')is False and proof.get('endgame_visible')is True and proof.get('one_more_turn_disabled')is True,'Supported continuation not proven unavailable')
    require(proof.get('winning_team')is None and proof.get('winning_kind')is None,'Unexpected winner needs independent review')
    require(proof.get('AI_advance')==0 and proof.get('native_controls_issued')==0 and proof.get('original_controller_owners_absent')is True,'Terminal inspection altered native state or owners remain')
    before,after=proof['core_before'],proof['core_after']
    require(all(before[k]==after[k]for k in ('turn','active','remaining','local_player','player0_human'))and before['turn']==through and before['active']is False,'Terminal clock/phase moved')
    return True

def funding_gate(rows):
    history=[];sites=collections.defaultdict(int);tokens=set();totals=collections.Counter()
    for q,v in sorted(rows,key=lambda x:(x[0]['turn'],x[0]['player'])):
        require(v['token']not in tokens,'Duplicate acquisition token');tokens.add(v['token'])
        require(v['status']=='confirmed'and v['turn']==q['turn']and v['spent']==q['price'],'Unconfirmed/unequal cost')
        require(len(v['steps'])==1,'Expected one tile per one-shot receipt')
        step=v['steps'][0];require((step['owner'],step['city'],step['plot'])==(q['player'],q['city'],q['plot']),'Assignment owner/city/plot mismatch')
        require(v['original_gold']==q['gold']and v['final_gold']==q['gold']+q['grant']-q['price'],'Treasury equation failed')
        require(v['donated']==q['grant']and v['own_gold_spent']==q['own_gold']==q['price']-q['grant'],'Funding split failed')
        reserve=max(25,math.ceil(2*q['maintenance']),math.ceil(10*max(0,-q['net_income'])))
        require(q['reserve']==reserve,'Reserve differs from frozen policy')
        # Both ordinary and fallback steps use the frozen80% safe-wallet allowance.
        require(0<=q['own_gold']<=max(0,q['gold']-reserve),'Own funds breached reserve')
        require(q['player']in range(1,6),'Purchase outside AI cohort')
        require(q['own_gold']==min(q['price'],math.floor(.8*max(0,q['gold']-reserve))),'Own-wallet allowance differs from policy')
        require(v['final_gold']>=min(q['gold'],reserve),'Final wallet below prior/reserve floor')
        recent=[p for p in history if p['player']==q['player']and 0<=q['turn']-p['turn']<5]
        require(len(recent)<3 and sum(p['price']for p in recent)+q['price']<=300,'Rolling purchase count/spend cap')
        require(not any(p['player']==q['player']and p['turn']==q['turn']for p in history),'Repeated player purchase same turn')
        site=(q['player'],q['city'],q['quarter'],q['source']);require(q['remaining_cap']==max(0,min(300-sum(p['price']for p in recent),300-sites[site])),'Remaining cap differs from replayed ledger');sites[site]+=q['price']
        require(sites[site]<=300 and q['price']<=q['remaining_cap']<=300,'Site/remaining cap')
        require(len(q['connectors'])<=2 and len(q['route'])<=5 and q['plot']in q['route'],'Invalid route/connector scope')
        require(not v['native_purchase_command'],'Assisted receipt mislabeled native PURCHASE')
        history.append(q);totals.update(tiles=1,cost=q['price'],own=q['own_gold'],fallback=q['grant'])
    return dict(totals)

def unique_censuses(folder,through):
    out={}
    for p in folder.glob('turn-???.json'):
        x=read(p)
        if x['turn']>through:continue
        require(x['turn']not in out,'Duplicate actual census clock');out[x['turn']]=x
    return out

def audit(root,through,*,endpoint=225,full=False,runtime=None,terminal=False):
    root=Path(root);job=read(root/'job-status.json');sup=read(root/'supervisor.json');isfull=completion_gate(job,sup,through,endpoint,full)
    require(not(full and terminal),'Terminal partial cannot be full')
    require(not(full or terminal)or runtime is not None,'Full/terminal audit requires current runtime hash verification')
    terminal_path=root/('terminal'+str(through))
    if terminal:terminal_gate(job,sup,read(terminal_path/'verification.json'),through,endpoint)
    settings=read(root/'settings.json');require(settings['endpoint']==endpoint,'Declared endpoint mismatch')
    require(not sup['native_fault_observed']and not(root/'native-fault-signal.json').exists(),'Native signal requires separate investigation')
    if full:
        pref=read(root/'final-restoration.json');require(pref.get('verified')and pref.get('mods')==144 and pref.get('auto_start')is False,'Original preferences/autostart not restored')
    if full or terminal:
        ids=[sup['supervisor_pid'],sup['worker_pid']]
        cmd='Get-CimInstance Win32_Process | Where-Object { $_.ProcessId -in @('+','.join(map(str,ids))+') } | Select-Object ProcessId,CommandLine | ConvertTo-Json -Compress'
        raw=subprocess.run(['powershell','-NoProfile','-Command',cmd],capture_output=True,text=True,check=True).stdout.strip();live=json.loads(raw)if raw else []
        if isinstance(live,dict):live=[live]
        require(not any('material-care-v2-worker.py'in(x.get('CommandLine')or'')or'material-care-v2-job.py'in(x.get('CommandLine')or'')for x in live),'Original controllers still alive')
    pins=read(root/'executed-service-pins.json');require(all(sha(p)==v for p,v in pins.items()),'Pinned source mismatch')
    archived={sha(p)for p in(root/'source-version').iterdir()if p.is_file()};require(set(pins.values())<=archived,'Executed source archive incomplete')
    if runtime is not None:
        runtime=Path(runtime);actual={str(p.relative_to(runtime)):{'sha256':sha(p),'size':p.stat().st_size}for p in runtime.rglob('*')if p.is_file()};require(actual==read(root/'expected-installed-manifest.json'),'Installed package differs')
    require(len(read(root/'expected-installed-manifest.json'))==512,'Expected v2 candidate512')
    primary=unique_censuses(root/'game-01',through);required={1,*range(25,through+1,25)}
    if terminal:
        primary[through]=read(terminal_path/'primary.json');required.add(through)
    require(set(primary)==required,'Primary coverage differs')
    require(through in primary,'Audit requires an actual outcome boundary')
    builders=unique_censuses(root/'builders',through);breq={t for t in(1,5,50,100,150,200,endpoint)if t<=through}
    if terminal:builders[through]=read(terminal_path/'builders.json');breq.add(through)
    require(set(builders)==breq,'Builder coverage differs')
    terminal_b=builders[max(builders)];require(not terminal_b['errors'],'Builder observer errors')
    for b in builders.values():require(not b['errors']and terminal_b['events'][:len(b['events'])]==b['events'],'Builder event prefix changed')
    care=unique_censuses(root/'material-care',through)
    if terminal:care[through]=read(terminal_path/'care.json')
    require(set(care)==required,'Care outcome coverage differs')
    finalcare=care[through]
    for t,x in sorted(care.items()):
        require(x['version']==3 and not x['errors'],'Material-care version/errors')
        require(x['calls']==x['strategy']['active_calls']+x['strategy']['inactive_calls'],'Strategy count equation')
        require(finalcare['events'][:len(x['events'])]==x['events'],'Material-work event prefix changed')
        require(all(not e['active']or e['player']in range(1,6)for e in x['strategy']['transitions']),'Human/minor strategy activated')
    journal=[]
    for line in(root/'service-actions.ndjson').read_text(encoding='utf-8-sig').splitlines():
        if not line.strip():continue
        x=json.loads(line)
        if x.get('turn',x.get('request',{}).get('turn',0))<=through:journal.append(x)
    begun={x['request']['token']:x for x in journal if x['event']=='funded-acquisition-begin'}
    closed=[x for x in journal if x['event']=='funded-acquisition-confirmed'];require(len(closed)==len({x['receipt']['token']for x in closed}),'Duplicate confirmation')
    require(set(begun)=={x['receipt']['token']for x in closed},'Ambiguous/unclosed economic effect')
    for x in closed:
        matching=[p for p in(root/'funded-acquisitions').glob('*receipt.json')if read(p)['token']==x['receipt']['token']];require(len(matching)==1 and read(matching[0])==x['receipt'],'Economic journal/receipt mismatch')
    funding=funding_gate([(x['request'],x['receipt'])for x in closed])
    starts=[x for x in journal if x['event']=='foundation-begin'];placed=[x for x in journal if x['event']=='foundation-confirmed'];key=lambda x:(x['player'],x['city'],x['plot'],x['quarter'])
    require(len(placed)==len(starts)==len({key(x)for x in placed})and {key(x)for x in placed}=={key(x)for x in starts},'Unclosed/duplicate foundation')
    observations=read(root/'observations-latest.json');require(not observations['errors'],'Foundation observer errors');targets=[t for t in observations['targets']if t['placed_turn']<=through]
    require(len(targets)==len(placed),'Foundation target/journal mismatch')
    final_primary=primary[through];physical={d['plot']:(c,d)for c in final_primary['cities']for d in c['districts']if d.get('type','').startswith('DISTRICT_CSC_')};proofs=[]
    for x in placed:
        v=read(root/'placements'/f"{x['turn']}-{x['player']}-{x['city']}-{x['quarter']}"/'validation.json');p=v['proof'];c=v['candidate']
        require(p['verified']and p['native_incomplete']and p['queue_unchanged'],'Invalid placement proof')
        require(p['progress_before']==p['progress_after']==0 and p['cost_before']==p['cost_after']>0,'Nonzero progress or cost mutation')
        require(c['owned_base']>0 and c['owned_specialty']>0 and c['current_legal']and c['eligible_ai']and not c['human']and not c['missing_tiles']and not c['same_quarter_present'],'Placement material/legality failure')
        require(all(v['before'][k]==v['after'][k]for k in('queue','queue_size','current_hash')),'Queue overwritten')
        require(v['native']['district_present']and not v['native']['complete']and v['native']['owner']==x['player'],'Native new incomplete district missing')
        t=next(t for t in targets if t['plot']==x['plot']and t['quarter']==x['quarter']);events=[e for e in observations['events']if e['turn']<=through and e['turn']>=x['turn']and e['order']==2 and e['item']==t['districtIndex']and not e['cancelled']]
        history=[h for h in observations['history']if h['plot']==x['plot']and h['quarter']==x['quarter']and h['turn']<=through and h.get('complete')and h.get('district_present')and h.get('district_type')==t['districtIndex']]
        city,district=physical.get(x['plot'],(None,None));events=[e for e in events if e['player']in {x['player'],city['player']if city else x['player']}and e['city']in {x['city'],city['id']if city else x['city']}]
        complete=bool(history or(district and district['complete']));require(not complete or bool(events),'Physical completion without native completion event')
        proofs.append(dict(player=x['player'],city=x['city'],plot=x['plot'],quarter=x['quarter'],placed_turn=x['turn'],ever_complete=complete,first_completion_event=min((e['turn']for e in events),default=None),current_major_owner=city['player']if city else None,current_major_complete=district['complete']if district else None,missing_final_completion='UNOBSERVED'if district is None else None))
    research=read(terminal_path/'research.json'if terminal else root/'research-latest.json');require(research['turn']>=through and not research['errors'],'Research prefix unavailable/errors')
    history=[x for x in research['history']if x['turn']<through];keys=[(x['turn'],x['player'])for x in history];require(len(keys)==len(set(keys)),'Duplicate research rows')
    defeat={x['player']:x['turn']for x in research['defeats']if x['turn']<through};required_research={(t,p)for t in range(1,through)for p in range(1,6)if t<defeat.get(p,through)};optional={(t,p)for p,t in defeat.items()}
    require(not(required_research-set(keys))and not(set(keys)-(required_research|optional)),'Unexplained research gap/scope')
    points=unique_censuses(root/'metric-points',through)
    if terminal:points[through]=read(terminal_path/'metric-point.json')
    require(set(points)==required,'Metric coverage differs');cohorts=report_points(list(points.values()),targets)
    graphics=renderer_review(root);require(graphics['at_or_after_run_start_events']==0,'Renderer errors or missing archived evidence')
    db=sqlite3.connect((root/'native-gameplay.sqlite').as_uri()+'?mode=ro',uri=True)
    inventory={}
    for name, in db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"):
        rows=sorted(json.dumps(list(x),ensure_ascii=False,default=str)for x in db.execute('SELECT * FROM "'+name.replace('"','""')+'"'));inventory[name]=dict(rows=len(rows),sha256=hashlib.sha256('\n'.join(rows).encode()).hexdigest())
    require(inventory==read(root/'native-database-inventory.json'),'Native database fingerprint changed')
    require(db.execute("SELECT DefaultValue FROM PseudoYields WHERE PseudoYieldType='PSEUDOYIELD_IMPROVEMENT'").fetchone()==(30,),'Wrong improvement base')
    require(db.execute("SELECT StringValue FROM StrategyConditions WHERE StrategyType='STRATEGY_CSC_AI_MATERIAL_BACKLOG' AND ConditionFunction='Call Lua Function'").fetchall()==[('CSC_AI_MaterialWorkReady',)],'Wrong work strategy callback');db.close()
    losses=loss_report(root,through,terminal=terminal_path if terminal else None)
    return dict(verified_observed_prefix=True,full_endpoint_verified=isfull,terminal_partial_verified=terminal,terminal_reason=read(terminal_path/'verification.json')['terminal_reason']if terminal else None,through=through,declared_endpoint=endpoint,settings=settings,current_pins=len(pins),archived_sources_verified=True,runtime_hashes_verified=runtime is not None,native_database_tables=len(read(root/'native-database-inventory.json')),funding=funding,foundations=proofs,assisted_foundations=len(proofs),ever_completed=sum(p['ever_complete']for p in proofs),research_rows=len(keys),research_defeats=defeat,primary_turns=sorted(primary),Builder_turns=sorted(builders),care_turns=sorted(care),care_strategy=dict(calls=finalcare['calls'],active=finalcare['strategy']['active_calls'],inactive=finalcare['strategy']['inactive_calls'],transitions=finalcare['strategy']['transitions']),repair_episodes=repair_episodes(finalcare['events'],terminal_b['events'],final_primary['width']),loss_attribution=losses,cohorts=cohorts,AI_counts=points[through]['counts'],renderer=dict(segments=len(graphics['segments']),new_errors=0),actual_Service_payments='UNOBSERVED',causal_effectiveness_established=False,final_normal_exit_and_pretest510_cleanup_pending=True,time=time.time())

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('root',type=Path);p.add_argument('--through',type=int,required=True);p.add_argument('--endpoint',type=int,default=225);p.add_argument('--full',action='store_true');p.add_argument('--terminal',action='store_true');p.add_argument('--runtime',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args();v=audit(a.root,a.through,endpoint=a.endpoint,full=a.full,runtime=a.runtime,terminal=a.terminal);a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(v,indent=2),encoding='utf-8');print(json.dumps({k:v[k]for k in('verified_observed_prefix','full_endpoint_verified','through','funding','assisted_foundations','ever_completed','research_rows','AI_counts')}))
