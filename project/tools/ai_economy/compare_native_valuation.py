"""Summarise closed native-valuation qualifications without running the game."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'native_ai/late_placement'))
from planning_results import analyse,parse


def load(path):return json.loads(path.read_text(encoding='utf-8'))


def game(path):
    summary=analyse(path)
    closed=load(path/'session-closed.json')
    assert closed['verified']and closed['native_exit_code']==0 and closed['preferences_verified']
    text=(path/'Lua.log').read_text(encoding='utf-8',errors='replace')
    watched=parse(text,'CSC_QUARTER_WATCH_')
    sites=[r for r in watched
           if r['kind']=='SITE'and r.get('event')=='foundation'and r['player']in range(1,6)]
    selected={(r['player'],r['city'],r['district'],r['plot'])for r in watched
              if r['kind']=='BEST'and r.get('existingDistrict')==0 and r['player']in range(1,6)
              and r.get('result')==r.get('bidQ8')==r.get('lastWriteQ8')and r.get('bidQ8',0)>0}
    matched=sum((r['player'],r['city'],r['district'],r['plot'])in selected for r in sites)
    return dict(path=str(path),closure=closed,quality=summary['quarter_quality_at_foundation'],
        foundations=sites,foundations_with_matching_native_winner=matched,native_best=summary['new_quarter_native_best'],
        exact_native_best=summary['new_quarter_native_best_exact_bid_write'],
        resource_losses=summary['raw_resource_loss_events'],planning_faults=summary['faults'],
        source_log_sha256=hashlib.sha256((path/'Lua.log').read_bytes()).hexdigest())


def prices(path):
    record=load(path/'native-valuation-preflight.json')
    rows=[]
    for r in record['records']:
        q,s=r['quote'],r['site']
        assert sum(x['valueQ8']for x in q['streams'])+q['siteAdjustmentQ8']==q['valueQ8']
        assert sum(x['bidValueQ8']for x in q['streams'])+q['siteAdjustmentQ8']==q['bidValueQ8']
        rows.append(dict(player=r['player'],city=r['city'],plot=r['plot'],quarter=r['quarter'],
            adjacency=r['adjacency'],base=r['base'],spec=r['spec'],quarter_ready=s['quarterReady'],
            customer_rows=len(s['customers']),economic_Q8=q['valueQ8'],
            forecast_adjustment_Q8=q['forecastAdjustmentQ8'],site_adjustment_Q8=q['siteAdjustmentQ8'],
            bid_Q8=r['bidQ8'],quality_cap_Q8=r['parts'].get('qualityCapQ8'),
            readiness_scale=s.get('sitingReadiness'),
            weighted_streams=[dict(id=x['id'],depth=x.get('forecastDepth'),raw_Q8=x['valueQ8'],bid_Q8=x['bidValueQ8'])
                              for x in q['streams']if x.get('forecastDepth',0)>0]))
    return dict(path=str(path),context=record['context'],summary=record['summary'],
        diagnostic_command_seconds=record['controller_command_seconds'],records=rows)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('root','previous','output'):parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args()
    new=args.root/'fresh50-01'
    before,after=load(args.previous/'source.json'),load(new/'source.json')
    parity={k:before[k]==after[k]for k in ('original_ai','map_signature','starts','units')}
    assert all(parity.values()),'Different starting world'
    mature=args.root/'mature200-02'
    structure=load(mature/'source-structure-comparison.json')
    assert structure['verified']and load(mature/'valuation-complete.json')['game_turns_advanced']==0
    result=dict(scope='Stock AI, Online, Small Continents, CL/R2/Suk, main CSC policy only',
        matched_start=parity,previous=game(args.previous),qualified=game(new),
        pre_calibration_25=prices(args.root/'fresh25-01'),calibrated_50=prices(new),
        mature_200=prices(mature),mature_structure=structure,
        mature_closure=load(mature/'session-closed.json'),
        ce_sha256='1be0545b94b35adaf582df2d70e827ecdb8014ccf91b59c5cc9f9b72fdc06bfc',
        xp2_sha256='092abfbb2176f8df04b5212f819dc269dd83aea866ff05aaf489904a1ff7c41f')
    args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print('Starting parity, native receipts, component reconciliation and mature zero-turn structure: PASS')


if __name__=='__main__':main()
