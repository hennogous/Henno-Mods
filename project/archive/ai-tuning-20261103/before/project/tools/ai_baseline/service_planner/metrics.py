"""Read-only metric points from native facts, independent of planner rankings.

Ratios retain numerator and denominator. This is a partial pilot evaluator:
native Service flags and structural customer adjacency are not transactions.
Use exact native source-recipient requirements for the formal benchmark.
"""
PRODUCERS={'BAKERS':{'BUILDING_CSC_BAKERS_WATER_MILL','BUILDING_CSC_BAKERS_WIND_MILL'},
           'TAILORS':{'BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP'}}
STAGE4={'BAKERS':'BUILDING_CSC_BAKERS_CAFE','TAILORS':'BUILDING_CSC_TAILORS_FASHION_HOUSE'}

def summarize(snapshot):
    assert not snapshot['errors'], 'Native metric errors must remain visible'
    counts={k:0 for k in ('cities','population','quarters','completed_quarters','unfinished_quarters',
                           'producer_built','producer_with_base','producer_with_both',
                           'stage4_built','stage4_with_both','functioning_producers',
                           'functioning_with_structural_sales','service_property_instances')}
    sites=[];yields={}
    for city in snapshot['cities']:
        counts['cities']+=1;counts['population']+=city['population']
        buildings={b['type'] for b in city['buildings'] if not b['pillaged']}
        for name,value in city['yields'].items():yields[name]=yields.get(name,0)+value
        counts['service_property_instances']+=sum(v>0 for v in city['properties'].values())
        for q in city['quarters']:
            key=q['quarter'];s=q['site'];producer=bool(PRODUCERS.get(key,set())&buildings)
            base=s['base_improved']>0;both=base and s['spec_improved']>0
            usable=q['complete'] and not q['pillaged']
            counts['quarters']+=1;counts['completed_quarters']+=q['complete'];counts['unfinished_quarters']+=not q['complete']
            developed=producer and usable;stage4=STAGE4.get(key) in buildings and usable
            counts['producer_built']+=developed;counts['producer_with_base']+=developed and base
            counts['producer_with_both']+=developed and both;counts['stage4_built']+=stage4
            counts['stage4_with_both']+=stage4 and both
            functioning=developed and base;counts['functioning_producers']+=functioning
            counts['functioning_with_structural_sales']+=functioning and s['sales']>0
            sites.append({'player':city['player'],'city':city['city'],'plot':q['plot'],'quarter':key,
                          'complete':q['complete'],'pillaged':q['pillaged'],'producer_built':producer,
                          'stage4_built':stage4,'owned_base':s['base'],'owned_spec':s['spec'],
                          'improved_base':s['base_improved'],'improved_spec':s['spec_improved'],
                          'sales_neighbor_plots':s['sales_plots'],'materials':s['materials']})
    def ratio(n,d):return {'numerator':counts[n],'denominator':counts[d],
                           'value':counts[n]/counts[d] if counts[d] else None}
    return {'turn':snapshot['turn'],'phase':snapshot.get('phase'),'counts':counts,'sites':sites,
            'ratios':{'effective_base_supply':ratio('producer_with_base','producer_built'),
                      'stage4_effective_both':ratio('stage4_with_both','stage4_built'),
                      'structural_sales_coverage':ratio('functioning_with_structural_sales','functioning_producers')},
            'yields':yields,'treasury_cashflow':snapshot.get('treasury_cashflow'),
            'coverage':{'service':'native recipient property flags; exact source identity unresolved',
                        'sales':'structural district neighbors; functioning exact customer requirements unverified',
                        'opportunity_conversion':'requires independent frozen denominator and longitudinal cohort audit',
                        'strategic_usefulness':'deferred; no active-strategy inference'},
            'proxy_scope':'Producer functioning fields mean completed/unpillaged Quarter + producer + any improved owned Base. Exact per-resource improvement and customer requirements remain unverified; raw identities support later audit.',
            'sales_transactions_observed':False,'formal_benchmark_ready':False}
