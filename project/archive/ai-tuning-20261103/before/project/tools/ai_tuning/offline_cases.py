"""Extract decision opportunities from a CLOSED mechanism-study archive.

Pure JSON/file analysis: no game imports, live cache access, transport or writes
except the explicit output. Comparisons are opportunities, not AI choices.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path

REAL_YIELDS = ("YIELD_FOOD", "YIELD_PRODUCTION", "YIELD_GOLD", "YIELD_SCIENCE", "YIELD_CULTURE", "YIELD_FAITH")
PRIVATE = "YIELD_CSC_AI_PLACEMENT"

def customer_comparisons(rows):
    """Pair adjacent and nonadjacent options ONLY within player/city/type.

    Missing yields stay unknown; gold equality is not whole-site equivalence.
    No conversion between private and real yields or prediction of a winner.
    """
    groups = defaultdict(list)
    seen = set()
    for index, row in enumerate(rows):
        key = (row['player'], row['city'], row['district'])
        unique = key + (row['plot'],)
        if unique in seen:
            raise ValueError(f"Duplicate customer option {unique}")
        seen.add(unique)
        groups[key].append((index, row))
    result=[]
    for key, options in sorted(groups.items()):
        for ai, adjacent in options:
            if not adjacent['adjacent_quarters']:
                continue
            for bi, alternative in options:
                if alternative['adjacent_quarters']:
                    continue
                aa, ba = adjacent['adjacency'], alternative['adjacency']
                shared = [y for y in REAL_YIELDS if y in aa and y in ba]
                delta = {y: ba[y]-aa[y] for y in shared}
                gold = delta.get('YIELD_GOLD')
                result.append({
                    'player':key[0], 'city':key[1], 'district':key[2],
                    'adjacent_plot':adjacent['plot'], 'alternative_plot':alternative['plot'],
                    'source_pointers':[f"/customer_sites/{ai}", f"/customer_sites/{bi}"],
                    'adjacent_quarters':adjacent['adjacent_quarters'],
                    'adjacent_sole_base_conflict':adjacent['sole_base'],
                    'alternative_sole_base_conflict':alternative['sole_base'],
                    'alternative_minus_adjacent_real_yields':delta,
                    'unobserved_yields':[y for y in REAL_YIELDS if y not in shared],
                    'private_values':{'adjacent':aa.get(PRIVATE), 'alternative':ba.get(PRIVATE)},
                    'gold_comparison': 'unobserved' if gold is None else 'alternative_higher' if gold>0 else 'equal' if gold==0 else 'adjacent_higher',
                    'chosen_option':None, 'net_chain_benefit':None,
                })
    return result

def build_casepack(root):
    root=Path(root)
    names=('natural-exposure100.json','coimbra-customer-decision-review.json','quantified-outcomes.json')
    source, receipts = {}, []
    for name in names:
        data=(root/name).read_bytes()
        source[name]=json.loads(data.decode('utf-8-sig'))
        receipts.append({'file':name,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)})
    exposure=source[names[0]]
    if exposure['source_turn']!=100:
        raise ValueError('This extractor targets the archived turn100 mechanism schema only')
    comparisons=customer_comparisons(exposure['customer_sites'])
    coimbra=[x for x in comparisons if (x['player'],x['city'],x['district'])==(4,131073,'DISTRICT_HARBOR')]
    logs=source[names[1]]
    repair=[{'source_pointer':f'/support/{i}',**x} for i,x in enumerate(exposure['support']) if x['state']=='repair']
    outcomes=source[names[2]]
    return {
        'schema_version':1,'source_turn':100,'source_root':str(root.resolve()),'source_files':receipts,
        'scope':'archived opportunities and logged events; no native calls or new outcome simulation',
        'source_index_mapping_caveat':exposure.get('index_mapping'),
        'counts':{'customer_options':len(exposure['customer_sites']),'same_city_pairs':len(comparisons),
                  'pairs_alternative_higher_gold':sum(x['gold_comparison']=='alternative_higher' for x in comparisons),
                  'pairs_equal_gold':sum(x['gold_comparison']=='equal' for x in comparisons),
                  'support_links':len(exposure['support']),'repair_links':len(repair)},
        'customer_comparisons':comparisons,
        'cases':{
            'coimbra_harbor':{'identity':{'player':4,'city':131073,'name':'LOC_CITY_NAME_COIMBRA'},
                'options':coimbra,'logged_harbor_rows_by_arm':{arm:len(value['harbor_tree_rows']) for arm,value in logs.items()},
                'baseline_production_rows':logs['baseline']['production_rows'],
                'choice_response':'unobserved when no logged Harbor decision; opportunity is not exposure',
                'logs_identity_limit':'source review filters by player/city name; no numeric city ID in these raw lines'},
            'material_repair':{'links':repair,'builder_access_safety_and_job_selection':'not established by these source records'},
            'maize_1863':{'source_turn':100,'baseline_outcome':[v for v in outcomes['baseline']['new_native_Quarters'] if v['player']==1 and v['plot']==1863],
                'precommitment_evidence':'See mechanism-results report and original turn99 logs; treatment at100 follows accepted contract2012.',
                'counterfactual_before_commitment':'unobserved; do not label post-commitment failure a clean avoidance test'},
        },
        'planner_data_gaps':['Current-versus-future benefit decomposition','Time and capacity to develop future sites',
          'Marginal chain yields/effects/payments','Whole-site opportunity costs beyond captured adjacency',
          'Queue/contract state at every candidate decision','Full reachability and threat for repair jobs'],
    }

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('archive',type=Path)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    report=build_casepack(args.archive)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report['counts']))
if __name__=='__main__': main()
