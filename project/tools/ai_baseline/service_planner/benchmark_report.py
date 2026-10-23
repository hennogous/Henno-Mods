"""Offline pilot observations; no game imports or connections."""
import json
from pathlib import Path

def ratio(n,d):return dict(numerator=n,denominator=d,value=n/d if d else None)
def key(s):return s['plot'],s['quarter']
def links(s):return {(key(s),m['plot'],m['category'],m['resource'])for m in s['materials']if m['owner']==s['player']and m.get('improvement')and not m.get('pillaged',False)}
def report_points(points,targets):
 assert points,'No observations; never invent zero outcomes'
 points=sorted(points,key=lambda p:p['turn']);turns=[p['turn']for p in points];assert len(turns)==len(set(turns)),'Duplicate actual native turn'
 assisted={key(t)for t in targets};last=points[-1];groups={n:[]for n in ('assisted','natural')}
 for s in last['sites']:groups['assisted'if key(s)in assisted else'natural'].append(s)
 counts={}
 for name,sites in groups.items():
  producers=[s for s in sites if s['producer_built']];functioning=[s for s in producers if s['complete']and not s['pillaged']and s['improved_base']>0]
  counts[name]=dict(current_AI_quarters=len(sites),completed=sum(s['complete']for s in sites),producer_built=len(producers),owned_base_sites=sum(s['owned_base']>0 for s in sites),owned_both_sites=sum(s['owned_base']>0 and s['owned_spec']>0 for s in sites),producer_base_proxy=ratio(len(functioning),len(producers)))
 sets=[set().union(*(links(s)for s in p['sites']))for p in points];first=sets[0];final=sets[-1];always=first.intersection(*sets)
 private={k:v for k,v in last.get('yields',{}).items()if k.startswith('YIELD_CSC_AI_')}
 return dict(actual_turn=last['turn'],groups=counts,assisted_targets_ever=len(assisted),assisted_targets_not_in_current_AI_census=len(assisted-{key(s)for s in last['sites']}),missing_target_scope='Outside current major-AI census or absent; do not infer destroyed',observed_material_link_retention=ratio(len(first&final),len(first)),material_links_available_at_every_observed_checkpoint=ratio(len(always),len(first)),durability_scope='Owned improved unpillaged material links per physical Quarter at observed boundaries. Endpoint retention is not uninterrupted availability. Shared materials may count per Quarter.',economic_yields={k:v for k,v in last.get('yields',{}).items()if k not in private},private_AI_signals_excluded=private,coverage=dict(first_observed_turn=turns[0],last_observed_turn=turns[-1],observations=len(turns),missing_turns=[t for t in range(turns[0],turns[-1]+1)if t not in set(turns)],left_censored_before_first_turn=True,source_census='major AI1..5 only'),Service_scope='Producer effectiveness is a structural proxy; exact improvement/customer gates and transactions unverified',formal_benchmark_ready=False,causal_gain_estimated=False)
def report_root(root,through=None):
 root=Path(root);points=[]
 for p in(root/'metric-points').glob('*.json'):
  d=json.loads(p.read_text(encoding='utf-8-sig'))
  if through is None or d['turn']<=through:points.append(d)
 obs=json.loads((root/'observations-latest.json').read_text(encoding='utf-8-sig'));targets=[t for t in obs['targets']if through is None or t['placed_turn']<=through]
 result=report_points(points,targets);events=[json.loads(x)for x in(root/'service-actions.ndjson').read_text(encoding='utf-8-sig').splitlines()if x.strip()];events=[e for e in events if through is None or e.get('turn',0)<=through];confirmed=[e for e in events if e['event']=='purchase-confirmed'];gold=sum(e['real_gold_spent']for e in confirmed)
 result['acquisition']=dict(native_purchase_requests=sum(e['event']=='purchase-begin'for e in events),confirmed=len(confirmed),confirmed_real_gold_spent=gold,cost_per_confirmed_purchase=ratio(gold,len(confirmed)),diagnostic_scenes_excluded=True,evidence='Accepted root journal only');result['root']=str(root);return result
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--through',type=int);p.add_argument('--output',type=Path,required=True);a=p.parse_args();result=report_root(a.root,a.through);a.output.write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result))
