"""Bounded native reception probe for already priced customer footprints.

Baseline records ordinary pre-aggregation and actual comparison values. A
separate matched replay can supply one guarded late correction using those
values; an early arm includes a fresh evaluation over two ordinary turns.
The diagnostic holds the ordinary publisher for that bounded window;
full efficacy games never load this module or external policy.
"""
import json
from pathlib import Path
from driver import read,write_json,require
from ce_replay import read_journal
from district_admission_watch import dependencies


def run(session,controller,output,dependencies_path,quotes,baseline=None,mode='late'):
    output=Path(output);output.mkdir()
    candidates=[q for q in quotes['quotes']if q['available']and q.get('deltaQ8')]
    if baseline:
        qualified=json.loads(Path(baseline).read_text())['qualified']
        require(qualified,'No baseline customer candidate reached native comparison')
        # The legacy guarded additive API deliberately rejects reservations.
        # Prefer a candidate with the native no-active-claim threshold; the CE
        # write still checks the actual reservation ID independently. A claim
        # is never cleared just to obtain a successful diagnostic receipt.
        qualified.sort(key=lambda q:(q['reservationQ8']>=0,q['plot'])if mode=='late'else(-q['deltaQ8'],q['plot']))
        chosen=qualified[0]
        candidates=[q for q in candidates if all(q[k]==chosen[k]for k in('player','city','district','plot'))]
        require(len(candidates)==1,'Matched current customer quote missing')
    require(candidates,'No priced customer targets')
    raw=controller.cmd("local w,h=Map.GetGridSize();local n=0;for r in GameInfo.Districts()do n=math.max(n,r.Index+1)end;"
        "print('CSC_CUSTOMER_GRID='..w..','..h..','..n)",'CSC_AI_BakersGameplay','customer-native-grid')
    width,height,districts=map(int,raw.split('CSC_CUSTOMER_GRID=',1)[1].splitlines()[0].split(','))
    targets=[{**{k:q[k]for k in('player','city','district','plot')},'x':q['plot']%width,'y':q['plot']//width}for q in candidates]
    modules=json.loads((output.parent/'loaded-modules.json').read_text())
    native=modules['GameCore_XP2_FinalRelease.dll']
    frida=dependencies(dependencies_path);attached=frida.attach(session.owner.pid)
    session.customer_diagnostic_attachment=attached
    script=attached.create_script(read(Path(__file__).with_name('customer_native_watch.js')))
    session.customer_diagnostic_script=script
    messages=[];script.on('message',lambda message,data:messages.append(message));script.load()
    require(script.exports_sync.init(native,{'targets':targets})['installed'],'Customer observer not installed')
    # Freeze normal publication so the explicit diagnostic packet survives to
    # the ordinary activation. Existing guidance code still runs; no orders,
    # unlocks, gold grants or physical gameplay changes are injected.
    hold="CSC_AI_DistrictBridge.Publish=function()return true end;assert(CE_AIDistrictScoresDisable()==1);"
    publication=None
    if baseline:
        q=candidates[0];delta=q['deltaQ8']
        hold+=f'''assert(CE_AIDistrictScoresBegin(900001,{width},{height},{districts})==1);
assert(CE_AIDistrictScoresAllow({q['player']})==1);'''
        if mode=='early':
            hold+=f"assert(CE_AIDistrictScoresEntry({q['player']},{q['city']},{q['district']},{q['plot']},{delta})==1);"
        else:
            hold+=f'''assert(CE_AIDistrictScoresLateEntry({q['player']},{q['city']},{q['district']},{q['plot']},
{chosen['beforeQ8']},{chosen['nativeQ8']},{delta})==1);'''
        hold+='assert(CE_AIDistrictScoresCommit()==1);'
        publication={**q,'expectedBeforeQ8':chosen['beforeQ8'],'expectedNativeQ8':chosen['nativeQ8'],'deltaQ8':delta}
        write_json(output/'publication.json',publication)
    controller.cmd(hold,"CSC_AI_BakersGameplay",'hold-publisher-and-stage-customer')
    try:
        # One extra ordinary turn lets the early arm see a fresh off-turn
        # evaluation after publication, instead of testing an already cached row.
        turns=2 if baseline and mode=='early'else 1
        controller.play(250+turns)
        observed=script.exports_sync.freeze()
        write_json(output/'observed.json',{**observed,'messages':messages})
        require(not observed['faults']and not messages,'Customer observer fault')
        qualified=[]
        for q in candidates:
            records=[r for r in observed['records']if all(r[k]==q[k]for k in('player','city','district','plot'))]
            before=next((r for r in records if r['kind']=='before'and r['valueQ8']>0),None)
            aggregate=next((r for r in records if r['kind']=='aggregate'and r['valueQ8']>0),None)
            compared=next((r for r in records if r['kind']=='compare'and aggregate and r['valueQ8']==aggregate['valueQ8']),None)
            if before and aggregate and compared:
                qualified.append({**q,'beforeQ8':before['valueQ8'],'nativeQ8':aggregate['valueQ8'],
                    'reservationQ8':compared['reservationQ8'],'bestSoFarQ8':compared['bestSoFarQ8']})
        result={'diagnostic_only':True,'mode':mode,'ordinary_turns_advanced':turns,'targets':len(targets),'qualified':qualified,
                'publication':publication,'submitted_bids':int(bool(baseline))}
        if baseline:
            journal=read_journal(controller,output)
            matches=[r for r in journal if r['k']==('net'if mode=='early'else'late')and all(r[k]==publication[k]for k in('player','city','district','plot'))]
            if mode=='early':
                applied=[r for r in matches if r['reason']==0 and r['result']==r['base']+publication['deltaQ8']]
                result['landed']=bool(applied)
                # The stock evaluator may multiply the fresh result by1.5 for
                # district need. Match the actual post-factor row and subsequent
                # aggregation/comparison, preserving native weighting.
                consumed=[]
                for r in applied:
                    for b in observed['records']:
                        if b['kind']!='before'or b['valueQ8']not in(r['result'],r['result']*384//256):continue
                        aggregates=[a for a in observed['records']if a['kind']=='aggregate'and a['turn']==b['turn']]
                        for a in aggregates:
                            if any(c['kind']=='compare'and c['turn']==a['turn']and c['valueQ8']==a['valueQ8']for c in observed['records']):
                                consumed.append({'net':r,'before':b,'aggregate':a})
                result['compared']=bool(consumed);result['fresh_consumption']=consumed[:2]
            else:
                expected=publication['expectedNativeQ8']+publication['deltaQ8']
                result['landed']=any(r['reason']==0 and r['result']==expected for r in matches)
                result['compared']=any(r['kind']=='compare'and r['valueQ8']==expected for r in observed['records'])
            result['verified']=result['landed']and result['compared']
        else:result['verified']=bool(qualified)
        write_json(output/'result.json',result)
        require(result['verified'],'No qualified customer native reception')
        return result
    finally:
        try:script.exports_sync.freeze()
        except frida.InvalidOperationError:pass
        # Native observation trampolines remain installed until the controller
        # exits this owned process; the host retains the attachment for cleanup.
        session.customer_diagnostic_attachment=attached
