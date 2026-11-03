"""Run the real native callback only in an owned, disposable Python process."""
from __future__ import annotations
import argparse,hashlib,json,subprocess,sys,time,threading
from pathlib import Path

HERE=Path(__file__).resolve().parent

# These exercise the arithmetic core with supplied metadata. They deliberately
# do not count as proof that on_enter derives scope or lifetime from native data.
PURE_FIXTURE_IDS = (
    *(f'K{i:03}' for i in range(1,19)),
    'K027','K028','K029','K030','K031','K033','K037',
)
REASON_CODES = {
    'applied':0,'disabled':1,'original_human':2,'current_human':2,
    'scope_miss':3,'stale_session':4,'stale_epoch':4,'stale_policy':4,
    'native_ineligible':5,'pointer_mismatch':6,'zero_preserved':7,
    'invalid_sentinel':8,'overflow':9,'sentinel_collision':10,
    'zero_delta':11,'delta_bound':13,
}

def pure_packet(case):
    """Translate independent facts to the documented C14-word decision input."""
    policy, call = case['policy'], case['call']
    matches = [entry for entry in policy['entries']
               if all(entry[key] == call[key]
                      for key in ('player','city','district','x','y'))]
    if len(matches) != 1:
        raise ValueError(f"Pure subset requires one explicit row: {case['id']}")
    return [
        call['score_q8'], matches[0]['delta_q8'], int(policy['enabled']),
        int(call['original_human']), int(call['current_human']),
        int(call['native_admitted']),
        int(int(call['expected_output_pointer'],16)
            == int(call['returned_output_pointer'],16)),
        policy['session_generation'], call['session_generation'],
        policy['analysis_epoch'], call['analysis_epoch'],
        policy['policy_version'], call['policy_version'], 1,
    ]

def exercise_independent_core(rpc, fixture_path, check):
    raw=fixture_path.read_bytes(); pack=json.loads(raw)
    by_id={case['id']:case for case in pack['kernel_cases']}
    rows=[]
    for identifier in PURE_FIXTURE_IDS:
        case=by_id[identifier]; packet=pure_packet(case)
        expected={'score':case['expected']['score_q8'],
                  'reason':REASON_CODES[case['expected']['reason_category']]}
        actual=rpc.evaluate(packet)
        check(f'pure kernel / {identifier} / {case["title"]}',actual,expected)
        rows.append({'id':identifier,'packet':packet,'expected':expected,
                     'actual':actual,'pass':actual==expected})
    return {
        'path':str(fixture_path.resolve()),'sha256':hashlib.sha256(raw).hexdigest(),
        'executed_ids':list(PURE_FIXTURE_IDS),'cases':rows,
        'scope':'C arithmetic and supplied Boolean/generation predicates only',
        'not_established':[
            'Native on_enter derivation of caller, player, city, plot or admission',
            'Observed native analysis epoch or load generation',
            'Live pointer readability, cache coherence, choice response or efficacy',
        ],
        'this_subset_does_not_execute_other_groups':True,
        'excluded_old_bound_cases':['K019','K020'],
        'bound_change':'v2 explicitly uses1048576Q8; the old4096-bound rejection expectations are not reused.',
    }

def exercise_v2_bounds(rpc,check):
    rows=[]
    for name,base,delta,score,reason in [
        ('positive bound',1024,1048576,1049600,0),
        ('negative bound',1024,-1048576,-1047552,0),
        ('positive violation',1024,1048577,1024,13),
        ('negative violation',1024,-1048577,1024,13),
        ('upper endpoint',2146435071,1048576,2147483647,0),
        ('lower endpoint',-2146435072,-1048576,-2147483648,0),
    ]:
        packet=[base,delta,1,0,0,1,1,7,7,41,41,2,2,1]
        actual=rpc.evaluate(packet);expected={'score':score,'reason':reason}
        check('v2 explicit Q8 bound / '+name,actual,expected)
        rows.append({'case':name,'packet':packet,'actual':actual,'expected':expected})
    return rows

def exercise_packet_validation(rpc, check):
    valid=[1024,256,1,0,0,1,1,7,7,41,41,3,3,1]
    malformed=[('short',valid[:-1]),('long',valid+[0]),('empty',[]),
               ('not array',{'packet':valid})]
    for label,value in [('fraction',0.5),('Boolean',True),('string','256'),
                        ('null',None),('above signed32',2147483648),
                        ('below signed32',-2147483649)]:
        packet=valid.copy();packet[1]=value;malformed.append((label,packet))
    rows=[]
    for label,packet in malformed:
        rejected=False;message=''
        try:
            rpc.evaluate(packet)
        except Exception as exc:
            message=str(exc)
            rejected='Exact14int32' in message
        check('RPC packet rejects '+label,rejected,True)
        rows.append({'case':label,'rejected':rejected,'message':message[:1500]})
    check('valid packet after malformed calls',rpc.evaluate(valid),
          {'score':1280,'reason':0})
    return rows

def exercise_config_bounds(rpc, invoke, check):
    # This reaches C configure; configurepacket validates only packet shape/type.
    valid=[7,41,3,3,131073,11,750,256,0,0,74,46,128,20]
    check('native config baseline',rpc.configurepacket(valid),0)
    invalid=[('session zero',0,0),('epoch zero',1,0),('version zero',2,0),
             ('negative player',3,-1),('observer player zero',3,0),('player above bound',3,62),('negative city',4,-1),
             ('negative district',5,-1),('district zero',5,0),('district at count',5,20),
             ('plot below monitor sentinel',6,-2),('plot at map size',6,3404),
             ('positive delta beyond bound',7,1048577),
             ('negative delta beyond bound',7,-1048577),
             ('width zero',10,0),('width above bound',10,257),
             ('height zero',11,0),('height above bound',11,257),
             ('change budget zero',12,0),('change budget above bound',12,129),
             ('district count zero',13,0),('district count above bound',13,4097)]
    rows=[]
    for label,index,value in invalid:
        packet=valid.copy();packet[index]=value
        actual=rpc.configurepacket(packet)
        check('native config rejects '+label,actual,-2)
        # A refusal must preserve the previous configuration, not a partial copy.
        check('enable after rejected config / '+label,rpc.mode(2),0)
        check('previous policy intact / '+label,invoke(256),
              {'score':512,'samePointer':True,'originalCalls':1})
        check('freeze after rejected config / '+label,rpc.mode(0),0)
        rows.append({'case':label,'packet':packet,'return':actual,
                     'previous_policy_preserved':True})
    monitor=valid.copy();monitor[6]=-1
    check('wildcard allowed only as monitor config',rpc.configurepacket(monitor),0)
    check('wildcard cannot arm mutation',rpc.mode(2),-1)
    check('restore exact plot after monitor test',rpc.configurepacket(valid),0)
    return rows

def exercise_admission_flags(rpc, invoke, fixture_path, check):
    """Exercise real on_enter reads of the owned R12 row, not packet booleans."""
    if fixture_path:
        cases=json.loads(fixture_path.read_bytes())['admission_cases']
    else:
        cases=[{'id':'A001','row_flags':{'can_build_district_u8':0,'owned_u8':1,'can_purchase_u8':0},'expected_native_admitted':False,'expected_score_q8':1024},
               {'id':'A002','row_flags':{'can_build_district_u8':1,'owned_u8':0,'can_purchase_u8':0},'expected_native_admitted':False,'expected_score_q8':1024},
               {'id':'A003','row_flags':{'can_build_district_u8':1,'owned_u8':0,'can_purchase_u8':1},'expected_native_admitted':True,'expected_score_q8':1280},
               {'id':'A006','row_flags':{'can_build_district_u8':2,'owned_u8':255,'can_purchase_u8':0},'expected_native_admitted':True,'expected_score_q8':1280}]
    check('enable owned row-flag adapter tests',rpc.mode(2),0)
    rows=[]
    try:
        for case in cases:
            flags=case['row_flags']
            rpc.setflags(flags['can_build_district_u8'],flags['owned_u8'],flags['can_purchase_u8'])
            before=rpc.snapshot();actual=invoke(1024)
            expected={'score':case['expected_score_q8'],'samePointer':True,'originalCalls':1}
            check('native R12 admission / '+case['id'],actual,expected)
            after=rpc.snapshot()
            check('native admitted counter / '+case['id'],
                  after['header'][4]-before['header'][4],
                  int(case['expected_native_admitted']))
            rows.append({'id':case['id'],'flags':flags,'actual':actual,
                         'expected':expected,'native_row_derivation_exercised':True})
    finally:
        rpc.setflags(1,1,0)
        check('freeze row-flag window',rpc.mode(0),0)
    return rows

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--dependencies',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--fixtures',type=Path,help='Independent fixture pack; only the explicitly listed decision-core subset is executed.')
    ap.add_argument('--scenario',choices=['standard','budget'],default='standard',help='Use a separate fresh owned process for terminal budget and fatal-error cases.')
    args=ap.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    sys.path.insert(0,str(args.dependencies));import frida
    assert frida.__version__=='17.24.3',frida.__version__
    proc=subprocess.Popen([sys.executable,'-B','-u','-c','import sys; sys.stdin.readline()'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    timed_out=[]
    def deadline():
        if proc.poll() is None:timed_out.append(True);proc.terminate()
    watchdog=threading.Timer(45,deadline);watchdog.daemon=True;watchdog.start()
    session=script=None;result={'profile':'quarter-placement-choice-v2','scenario':args.scenario,'target_pid':proc.pid,'target_executable':sys.executable,'game_actions':False,'checks':[]}
    source_paths=[HERE/name for name in ('kernel.c','synthetic.js','synthetic_target.c','run_synthetic.py')]
    result['start_source_hashes']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in source_paths}
    messages=[]
    try:
        session=frida.attach(proc.pid)
        source=(HERE/'synthetic.js').read_text(encoding='utf-8').replace('__KERNEL_C__',json.dumps((HERE/'kernel.c').read_text(encoding='utf-8'))).replace('__TARGET_C__',json.dumps((HERE/'synthetic_target.c').read_text(encoding='utf-8')))
        script=session.create_script(source);script.on('message',lambda m,d:messages.append(m));script.load();rpc=script.exports_sync
        result['info']=rpc.info()
        def check(name,value,expected):
            result['checks'].append({'name':name,'actual':value,'expected':expected,'pass':value==expected});assert value==expected,(name,value,expected)
        # Frida RPC supplies a trailing binary-data argument. Pass the complete
        # declared call packet rather than allowing it to occupy an omitted slot.
        def invoke(base,district=11,bad_return=0):return rpc.invoke(base,district,bad_return)
        check('configure',rpc.configure(256,0,0,750),0)
        check('disabled native call',invoke(256),{'score':256,'samePointer':True,'originalCalls':1})
        check('enable',rpc.mode(2),0)
        check('native additive pointer ABI',invoke(256),{'score':512,'samePointer':True,'originalCalls':1})
        check('native negative score',invoke(-128),{'score':128,'samePointer':True,'originalCalls':1})
        check('zero early return preserved',invoke(0),{'score':0,'samePointer':True,'originalCalls':1})
        check('invalid sentinel preserved',invoke(-2559744),{'score':-2559744,'samePointer':True,'originalCalls':1})
        check('overflow unchanged',invoke(2147483647),{'score':2147483647,'samePointer':True,'originalCalls':1})
        check('wrong district unchanged',invoke(256,12),{'score':256,'samePointer':True,'originalCalls':1})
        check('nested callback frame independence',rpc.recursive(256),{'score':512,'samePointer':True,'originalCalls':2})
        check('policy update while enabled refused',rpc.configure(512,0,0,750),-1)
        result['before_performance']=rpc.snapshot()
        result['performance']=rpc.bulk(1000000,12)
        check('1000000 rejected native callbacks',result['performance']['count'],1000000)
        check('out of scope records unchanged',result['performance']['snapshot']['header'][2],result['before_performance']['header'][2])
        result['parallel']=rpc.parallel(25000)
        check('parallel workers joined',result['parallel']['result'],0)
        check('100000 parallel original calls',result['parallel']['count'],100000)
        check('all seven arguments forwarded; score-only writes',rpc.guards(),{'prefix':0xa55ac33c,'suffix':0x11223344,'argErrors':0})
        check('freeze',rpc.mode(0),0)
        result['packet_validation']=exercise_packet_validation(rpc,check)
        result['v2_arithmetic_bound']=exercise_v2_bounds(rpc,check)
        if args.fixtures:
            result['independent_fixture_subset']=exercise_independent_core(rpc,args.fixtures,check)
        else:
            result['independent_fixture_subset']={'executed':False,'reason':'--fixtures not supplied'}
        result['native_config_bounds']=exercise_config_bounds(rpc,invoke,check)
        result['native_admission_flags']=exercise_admission_flags(rpc,invoke,args.fixtures,check)
        result['valid_span']=rpc.validspan()
        check('native memory span gates',result['valid_span'],
              {'null_read':False,'null_write':False,'unmapped_read':False,
               'readable_read':True,'read_only_write':False,'writable_write':True})
        check('original human configuration',rpc.configure(256,1,0,750),0)
        check('human window enabled',rpc.mode(2),0)
        check('original human excluded',invoke(256),{'score':256,'samePointer':True,'originalCalls':1})
        check('freeze original-human window',rpc.mode(0),0)
        check('current human configuration',rpc.configure(256,0,1,750),0)
        check('current human window enabled',rpc.mode(2),0)
        check('current human excluded',invoke(256),{'score':256,'samePointer':True,'originalCalls':1})
        check('freeze current-human window',rpc.mode(0),0)
        check('monitor normal-role configuration',rpc.configure(256,0,0,750),0)
        check('enable monitor window',rpc.mode(1),0)
        result['native_monitors']=rpc.monitors()
        check('native monitor values and pointer identity',
              {k:result['native_monitors'][k] for k in ('best','bestXY','pvPointer','pv','noBest','nullPointer','nullPV','monitorCalls','active','errors','fatal')},
              {'best':11,'bestXY':[10,10],'pvPointer':True,'pv':768,
               'noBest':-1,'nullPointer':True,'nullPV':1024,'monitorCalls':5,
               'active':0,'errors':0,'fatal':0})
        check('native monitor record kinds',
              [r[-1] for r in result['native_monitors']['records']],
              [1,2,3,2,3])
        check('monitor reservation capture',rpc.snapshot()['reservations'],
              [{'plot':750,'controller':-1,'score':-2559744,'cacheScore':768}])
        result['native_ranking']=rpc.ranking()
        ranking=result['native_ranking'];a,z=ranking['baseline'],ranking['treatment']
        check('wildcard native raw candidates',[(r[3],r[6],r[7]) for r in a['records'] if r[-1]==0],[(751,1024,1024),(752,768,768)])
        check('wildcard cache skips first ineligible row then includes both candidates',[(r[3],r[6]) for r in a['records'] if r[-1]==1],[(751,1024),(752,768)])
        check('baseline native model winner',{'district':a['district'],'xy':a['xy'],'pvA':a['pvA'],'pvB':a['pvB'],'originalCalls':a['originalCalls']},
              {'district':11,'xy':[11,10],'pvA':1024,'pvB':768,'originalCalls':2})
        check('strict targeted native model changes site',{'district':z['district'],'xy':z['xy'],'pv':z['pv'],'samePointers':z['samePointers'],'originalCalls':z['originalCalls']},
              {'district':11,'xy':[12,10],'pv':1025,'samePointers':True,'originalCalls':2})
        check('repeated fresh calls do not compound cached delta',[z['firstScore'],z['secondScore'],z['changes'],z['mode']],[1025,1025,2,2])
        check('baseline reservations captured before native winner',[r['controller'] for r in a['reservations']],[-1,-1])
        check('reservation capture counter is fresh for next winner',z['captureCount'],a['captureCount']+1)
        check('active reservation model blocks target despite higher score',{'district':ranking['reserved']['district'],'xy':ranking['reserved']['xy']},
              {'district':11,'xy':[11,10]})
        check('reserved target metadata is explicit',[r for r in ranking['reserved']['reservations'] if r['plot']==752],
              [{'plot':752,'controller':7,'score':2048,'cacheScore':1025}])
        if args.scenario=='budget':
            result['native_budget']=rpc.budget()
            check('mutation budget stops rather than silently switching to monitor',result['native_budget'],
                  {'first':512,'second':256,'changed':1,'mode':0,'budget':2,'reenable':-1,'firstMode':0})
        else:
            rpc.mode(0);rpc.configure(256,0,0,750);rpc.mode(2)
            check('mismatched output pointer disarms',invoke(256,11,1),{'score':256,'samePointer':False,'originalCalls':1})
            check('fatal pointer error latched',rpc.snapshot()['header'][9],1)
            check('fatal adapter cannot re-enable',rpc.mode(2),-1)
        rpc.mode(0);result['final']=rpc.finish();result['ok']=True
    finally:
        if script:
            try:script.unload()
            except Exception as e:result['unload_error']=str(e)
        if session:
            try:session.detach()
            except Exception as e:result['detach_error']=str(e)
        if proc.poll() is None:proc.communicate(b'finish\n',timeout=15)
        result['target_exit']=proc.returncode
        watchdog.cancel();result['deadline_exceeded']=bool(timed_out)
        result['source_hashes']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in source_paths}
        result['source_hashes_unchanged']=result['source_hashes']==result['start_source_hashes']
        result['messages']=messages
        if not result['source_hashes_unchanged'] or result['deadline_exceeded'] or proc.returncode!=0:
            result['ok']=False
        (args.output/'result.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'ok':result.get('ok',False),'profile':result['profile'],'scenario':args.scenario,
                      'checks':len(result['checks']),'passed':sum(c['pass'] for c in result['checks']),
                      'target_exit':result.get('target_exit'),'output':str(args.output/'result.json')},indent=2))
if __name__=='__main__':main()
