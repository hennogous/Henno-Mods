"""Offline parity contracts for a matched resource-forecast diagnostic.

No game connection or mutation. A private-yield treatment may alter only its
declared channel at the source boundary; it may not alter the saved world,
treasury, unit census, production or real plot yields before advancement.
Derived observer output may differ only with explicit opt-in and direct native
worked-plot evidence; this is recorded as treatment spillover, not inertness.
"""
from full_game_controller.continuation import world_signature
from worker_allocation_contract import observer_output_evidence

PRODUCTION_FIELDS=('player','city','population','human','eligible_ai','district_defs',
 'district_state','same_quarter_types','queue_size','queue_delay','current_production_hash','production')

def production_signature(data):
    return sorted(({k:city[k]for k in PRODUCTION_FIELDS}for city in data['cities']),
                  key=lambda x:(x['player'],x['city']))

def private_yield_parity(reference,actual,amounts):
    before={p['plot']:p for p in reference};after={p['plot']:p for p in actual}
    assert len(before)==len(reference)and len(after)==len(actual),'Duplicate material plot'
    assert before.keys()==after.keys(),'Material scope changed before advancement'
    for plot,b in before.items():
        a=after[plot]
        assert (a['resource'],a['owner'])==(b['resource'],b['owner']),('Resource/owner drift',plot)
        assert a['economic']==b['economic'],('Economic yield changed',plot)
        expected=b['private']+amounts.get(b['resource'],0)
        assert a['private']==expected,('Unexpected private-yield delta',plot,b['private'],a['private'],expected)
    return dict(verified=True,plots=len(before),treatment_resources=len(amounts),economic_yields_equal=True)

def economic_cities(world):
    return sorted((c['player'],c['id'],{k:v for k,v in c['yields'].items()if not k.startswith('YIELD_CSC_AI_')})for c in world['cities'])

def source_parity(reference,actual,amounts,*,observer_allocation_proof=None,native_rule_legality_proof=None,native_rule_runtime=None):
    assert world_signature(actual['world'])==world_signature(reference['world']),'Source world drift'
    observer=[]
    if economic_cities(actual['world'])!=economic_cities(reference['world']):
        assert observer_allocation_proof and amounts,'City economic yields changed'
        assert observer_allocation_proof.get('verified_zero_turn_pair')and observer_allocation_proof.get('direct_worked_plot_evidence_supports_reassignment')and observer_allocation_proof.get('economic_plot_yield_inputs_unchanged')and observer_allocation_proof.get('output_change_scope')==[0],'Observer change lacks verified zero-turn evidence'
        assert 'allocation'in reference and 'allocation'in actual,'Direct native worker-allocation evidence required'
        observer=observer_output_evidence(reference['world'],actual['world'],reference['allocation'],actual['allocation'])
        normalize=lambda rows:{(r['player'],r['city']):{k:v for k,v in r.get('derived_city_economic_delta',r.get('delta',{})).items()if v!=0}for r in rows}
        assert normalize(observer)==normalize(observer_allocation_proof['derived_city_output_changes']),'Observer output differs from the measured zero-turn case'
    assert actual['units']==reference['units'],'Unit inventory/position/charges changed'
    assert actual['gold']==reference['gold'],'Treasury changed'
    legality=None
    if native_rule_legality_proof is not None:
        from material_native_rule_legality import verify_measured_change
        legality=verify_measured_change(reference['production'],actual['production'],native_rule_legality_proof,native_rule_runtime)
    else:
        assert production_signature(actual['production'])==production_signature(reference['production']),'Production/Quarter state changed'
    result=private_yield_parity(reference['private'],actual['private'],amounts)
    result.update(observer_treatment_spillover=bool(observer),observer_reallocation_evidence=observer,city_output_inertness_claimed=not observer)
    result.update(native_rule_legality_changed=legality is not None,native_rule_legality_evidence=legality)
    return result

def database_delta(reference,actual,*,treatment):
    changed={k for k in reference.keys()|actual.keys()if reference.get(k)!=actual.get(k)}
    assert changed==({'Resource_YieldChanges'}if treatment else set()),('Unexpected native database delta',changed)
    return sorted(changed)
