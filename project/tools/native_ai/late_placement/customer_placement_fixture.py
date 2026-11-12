"""Read-only2.1 preflight, not a policy or a world-edit command.

An archived future footprint is not a current native target. This qualification
requires actual ownership, queue legality, supplier readiness and enough slots
before a separate controlled Quarter fixture can even be considered.
"""

def native_signal_active(facts):
    """Definition evidence only; native score consumption remains unproved."""
    signal=facts.get('nativeSignal',{});definition=signal.get('yieldDefinition',{})
    return (definition.get('type')=='YIELD_CSC_AI_PLACEMENT' and definition.get('defaultValue')==1
        and any(r.get('item')=='YIELD_CSC_AI_PLACEMENT' and r.get('value')==25 for r in signal.get('bias',[]))
        and any(r.get('customer')=='DISTRICT_HARBOR' and r.get('quarter')=='DISTRICT_CSC_TAILORS_QUARTER'
            and r.get('yield')=='YIELD_CSC_AI_PLACEMENT' and r.get('amount')==1 and r.get('tilesRequired')==1
            for r in signal.get('adjacencies',[])))


def qualify_hamburg(facts,ui_city,*,allow_lumber_mill=False,expected_turn=202):
    assert expected_turn in(202,208)and facts['turn']==expected_turn and facts['mutationCommands']==0
    city=facts['city']
    assert (city['player'],city['id'],city['name'])==(3,393221,'LOC_CITY_NAME_HAMBURG')
    assert facts['quarter']['type']=='DISTRICT_CSC_TAILORS_QUARTER'
    assert facts['harbor']['type']=='DISTRICT_HARBOR'
    assert (ui_city['player'],ui_city['city'])==(3,393221)
    assert all(facts[k]['requiresPopulation'] in(False,True)for k in('quarter','harbor'))
    reasons=[]
    if expected_turn==208 and city.get('queueIsDistrict')is not False:
        reasons.append('Common preparation must not touch an existing District production item')
    if city['hasQuarter']or city['hasHarbor']:reasons.append('Quarter or Harbor already placed')
    if not any(s['plot']==1084 and s['owner']==3 and s['resourceType']=='RESOURCE_SHEEP'
        and s['ready']is True for s in facts['suppliers']):
        reasons.append('Expected owned ready Sheep supplier is unavailable')
    customers={p['plot']:p for p in facts['candidates']if p['owner']==3 and p['city']==393221
        and p['district']==-1 and p['resource']==-1 and not p['protected']
        and p['harborTarget']}
    choices=[]
    for site in facts.get('quarterAlternatives',[facts['site']]):
        if (site['owner'],site['city'],site['district'],site['resource'])!=(3,393221,-1,-1):continue
        if site['protected']or not site['quarterTarget']:continue
        if site.get('supplierDistance',1)!=1:continue
        conversion=site['improvement']!=-1
        # This one declared fallback covers an ordinary, unprotected Lumber
        # Mill. It never clears the Sheep supplier or permits resource covers.
        if conversion and not(allow_lumber_mill and site['plot']==1083
            and site.get('improvementType')=='IMPROVEMENT_LUMBER_MILL'):continue
        links=site.get('customerPlots',[p['plot']for p in facts['candidates']if p['quarterDistance']==1])
        candidates=sorted(set(links)&set(customers))
        if candidates:choices.append((conversion,site['plot'],candidates,site))
    choices.sort(key=lambda choice:(choice[0],choice[1])) # Empty first, then stable plot ID.
    if not choices:reasons.append('No native-legal material-safe Quarter/Harbor pair under the declared fixture conversion rule')
    capacity=ui_city.get('ui',{})
    allowed,zoned=capacity.get('allowedDistricts'),capacity.get('zonedDistricts')
    # Do not infer a future population slot or treat unavailable UI data as0.
    required=sum(bool(facts[k]['requiresPopulation'])for k in('quarter','harbor'))
    if allowed is None or zoned is None or allowed-zoned<required:
        reasons.append('Current native capacity cannot accommodate both districts')
    chosen=choices[0]if choices else None
    return dict(eligible=not reasons,reasons=reasons,legal_customer_candidates=chosen[2]if chosen else [],
        quarter_plot=chosen[1]if chosen else None,ordinary_lumber_mill_conversion=chosen[0]if chosen else False,
        available_slots=None if allowed is None or zoned is None else allowed-zoned,
        required_slots=required,mutation_commands=0,native_score_margin_known=False)
