"""Offline, explainable CSC investment review. No game, old planner or native imports.

The review utility is scenario arithmetic, never a native Q8 adjustment. Partial
ledgers deliberately retain unpriced effects and unknown action feasibility.
"""
from __future__ import annotations

import itertools
import math

STAGES = (2, 3, 4)
BUILDINGS = {2: 'BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP',
             3: 'BUILDING_CSC_TAILORS_TAILOR', 4: 'BUILDING_CSC_TAILORS_FASHION_HOUSE'}
CUSTOMERS = {'DISTRICT_HARBOR': ('BUILDING_LIGHTHOUSE', 2),
             'DISTRICT_COMMERCIAL_HUB': ('BUILDING_MARKET', 3),
             'DISTRICT_HOLY_SITE': ('BUILDING_TEMPLE', 3),
             'DISTRICT_THEATER': ('BUILDING_AMPHITHEATER', 4)}
SERVICE = {2: 'dockmaster', 3: 'sacristan', 4: 'stage_manager'}
OMISSIONS = ['Policies and mod-specific adjacency extensions',
             'Service strategic value unless an explicit review value is supplied',
             'Trade-route demand and export returns', 'Assigned specialists and Great Person points',
             'Amenity/growth feedback and population change',
             'Tile-use, competing district and military opportunity costs',
             'Builder acquisition, travel, safety and repair costs',
             'Native-score overlap and conversion to native utility']


def validate(site):
    if site['identity']['quarter'] != 'TAILORS':
        raise ValueError('First mechanics profile supports Tailors only')
    for collection, key in (('materials', 'plot'), ('customers', 'key')):
        keys = [row[key] for row in site[collection]]
        if len(keys) != len(set(keys)):
            raise ValueError('Duplicate ' + collection + ' identity')
    for m in site['materials']:
        if m.get('intensity', 1) not in (1, 2, 3):
            raise ValueError('Unknown material improvement intensity')
        if m['working'] is True and not (m['owned'] and m['revealed'] and m['district_free']):
            raise ValueError('Working supply contradicts ownership/visibility/footprint')
    if site.get('original_human') is not False:
        raise ValueError('Original AI identity is not established')
    plots = [c['plot'] for c in site['customers']]
    if len(plots) != len(set(plots)):
        raise ValueError('Duplicate customer district footprint')
    if any(c.get('population') is not None and (not math.isfinite(c['population']) or c['population'] < 0)
           for c in site['customers']):
        raise ValueError('Invalid customer population')
    if site.get('river_edges') is not None and not 0 <= site['river_edges'] <= 6:
        raise ValueError('Invalid river edge count')
    if site['city'].get('production') is not None and site['city']['production'] < 0:
        raise ValueError('Negative production')


def add(ledger, key, value, start, note, coverage='unresolved'):
    if abs(value) > 1e-12:
        ledger.append(dict(component=key, value_per_turn=value, start_turn=start,
                           explanation=note, native_coverage=coverage))


def evaluate(site, plan, rules, *, horizon=80, weights=None, cost_scale=1.0,
             service_values=None, future=None, future_materials=None):
    """Evaluate a building bundle from the observation, in turns AFTER capture.

    Captured district quotes override nominal district costs. Other unquoted
    building costs use a declared reference-cost multiplier. Construction is
    serial at constant captured production; this is a forecast assumption.
    `future` is an explicitly conditional customer branch, never observed state.
    """
    validate(site)
    if type(horizon) is not int or not 1 <= horizon <= 300:
        raise ValueError('Review horizon must be 1..300')
    weights = weights or dict(production=1.0, gold=0.5, culture=1.0)
    if (any(not math.isfinite(v) or v < 0 for v in weights.values())
            or not math.isfinite(cost_scale) or cost_scale <= 0):
        raise ValueError('Finite nonnegative review weights and positive cost scale required')
    service_values = service_values or {}
    assumptions = []
    unknowns = list(site.get('unknowns', [])) + OMISSIONS
    existing = {int(k) for k, value in site['existing_buildings'].items() if value is True}
    if set(plan) - set(STAGES) or ((3 in plan or 4 in plan) and 2 not in set(plan) | existing):
        raise ValueError('Tailor/Fashion House needs Workshop; Fashion House does not require Tailor')
    if site['quarter'].get('pillaged') is not False or site.get('pillaged_buildings'):
        return dict(status='repair_quote_needed', site=site['id'], plan=list(plan),
                    review_utility=None, unknowns=unknowns + ['Quarter repair cost and timing'])
    new = not site['quarter']['exists']
    if new and site['land'].get('legal') is not True:
        return dict(status='placement_not_established', site=site['id'], plan=list(plan),
                    review_utility=None, unknowns=unknowns + ['Native placement potential'])
    production = site['city'].get('production')
    if not production or production <= 0:
        return dict(status='production_estimate_needed', site=site['id'], plan=list(plan),
                    review_utility=None, unknowns=unknowns + ['City production budget'])
    events, starts, cost, time = [], {s: 0 for s in existing}, 0.0, 0
    if new:
        quote = site['land'].get('district_cost')
        amount = quote if quote is not None else rules['district_cost'] * cost_scale
        time = math.ceil(amount / production)
        cost += amount
        events.append(dict(item='district', turn=time, cost=amount,
                           basis='captured quote' if quote is not None else 'reference-cost assumption'))
    elif site['quarter'].get('complete') is not True:
        return dict(status='remaining_construction_needed', site=site['id'], plan=list(plan),
                    review_utility=None, unknowns=unknowns + ['Remaining district production'])
    district_start = time
    for stage in sorted(set(plan) - existing):
        amount = rules['buildings'][str(stage)]['cost'] * cost_scale
        time += math.ceil(amount / production)
        starts[stage] = time
        cost += amount
        events.append(dict(item=BUILDINGS[stage], turn=time, cost=amount, basis='reference-cost assumption'))
        assumptions.append(f'Stage {stage} unlock and normal production available by turn {time}')
    assumptions += ['Captured production stays constant; no extra queue delay',
                    'Population, material supply and customer state remain fixed',
                    'Unquoted building costs use reference costs times ' + str(cost_scale)]
    if site['land'].get('reservation') is None and new:
        unknowns.append('Fresh native reservation/admission before acting')
    ledger = {key: [] for key in ('production', 'gold', 'culture')}
    eligible = [m for m in site['materials'] if m['owned'] and m['revealed'] and m['district_free']]
    base = [m for m in eligible if m['base']]
    spec = [m for m in eligible if m['specialty']]
    working_base = [m for m in base if m['working'] is True]
    working_spec = [m for m in spec if m['working'] is True]
    material_ready = {m['plot']: 0 for m in working_base + working_spec}
    future_materials = future_materials or []
    if len({m['plot'] for m in future_materials}) != len(future_materials):
        raise ValueError('Duplicate future material investment')
    for investment in future_materials:
        matches = [m for m in eligible if m['plot'] == investment['plot'] and (m['base'] or m['specialty'])]
        if (len(matches) != 1 or investment.get('conflict') is not False or investment.get('legal') is False
                or investment.get('ready_turn', -1) < 0 or investment.get('cost', -1) < 0):
            raise ValueError('Future material needs a mapped owned footprint, conflict assessment, cost and timing')
        material = matches[0]
        if material['working']:
            raise ValueError('Future material is already working')
        if material['base']:
            working_base.append(material)
        if material['specialty']:
            working_spec.append(material)
        material_ready[material['plot']] = investment['ready_turn']
        cost += investment['cost']
        events.append(dict(item='improvement:'+str(material['plot']), turn=investment['ready_turn'],
                           cost=investment['cost'], basis='explicit conditional Builder-work estimate'))
        assumptions.append('CONDITIONAL material development at plot '+str(material['plot']))
        if investment.get('legal') is not True:
            unknowns.append('Improvement legality/unlock unverified at '+str(material['plot']))
    edges = site.get('river_edges')
    if edges is None:
        unknowns.append('Exact river-edge count; riverside Boolean is insufficient')
    district_production = len(base) + len(spec) + (edges // 2 if edges is not None else 0)
    add(ledger['production'], 'district.materials_and_river', district_production, district_start,
        f'{len(base)} Base, {len(spec)} Specialty deposits; {edges} observed river edges', 'ordinary adjacency overlaps native valuation')
    add(ledger['gold'], 'district.maintenance', -rules['district_maintenance'], district_start,
        'Quarter maintenance', 'native costs already participate')

    customers = [dict(c, ready_turn=0) for c in site['customers']]
    if future:
        if (future['owner'] != site['identity']['player'] or future['district'] not in CUSTOMERS
                or future.get('building') != CUSTOMERS[future['district']][0]):
            raise ValueError('Future customer owner/district/building mismatch')
        if future['plot'] == site['identity']['plot'] or any(m['plot'] == future['plot'] for m in eligible):
            raise ValueError('Future customer footprint conflicts with Quarter or material')
        if future.get('conflict') is not False:
            raise ValueError('Future customer needs an explicit conflict assessment')
        if not any(f['plot'] == future['plot'] and f['native_potential'].get(future['district']) is True
                   for f in site.get('future_footprints', [])):
            raise ValueError('Future customer needs a captured matching plot-potential observation')
        if future.get('ready_turn', -1) < 0 or future.get('cost', -1) < 0:
            raise ValueError('Future customer must declare cost and timing')
        if any(c['plot'] == future['plot'] for c in customers):
            raise ValueError('Future customer duplicates an existing customer footprint')
        customers.append(future)
        cost += future['cost']
        assumptions.append('CONDITIONAL customer branch: legality/unlock/build timing require confirmation')
        events.append(dict(item=future['building'], turn=future['ready_turn'], cost=future['cost'],
                           basis='explicit conditional customer estimate'))
        add(ledger['gold'], 'future_customer.maintenance', -future.get('maintenance', 0),
            future['ready_turn'], 'Additional customer maintenance')
        if 'ordinary_yields' in future:
            assumptions.append('Future customer ordinary yields are explicit estimates, not captured forecasts')
            for key, amount in future['ordinary_yields'].items():
                if key not in ledger or not math.isfinite(amount):
                    raise ValueError('Invalid future customer yield estimate')
                add(ledger[key], 'future_customer.ordinary.'+key, amount, future['ready_turn'],
                    'Explicit ordinary customer yield estimate', 'ordinary native district/building value overlaps')
        else:
            unknowns.append('Future customer own baseline yields are unpriced despite charging its investment cost')
        unknowns.append('Future customer competing-site value is unpriced')
    for c in customers:
        if c['owner'] != site['identity']['player']:
            continue
        kind = c['district']
        if kind not in CUSTOMERS:
            continue
        customer_start = max(district_start, c['ready_turn'])
        # Flat district adjacency uses type/ownership, not the later building gates.
        add(ledger['gold'], 'district.customer.' + c['key'], 1, customer_start,
            'Flat Quarter sales adjacency', 'ordinary adjacency overlaps native valuation')
        yield_type = 'production' if kind == 'DISTRICT_HARBOR' else 'culture'
        if c.get('district_functioning') is True:
            add(ledger[yield_type], 'customer.reciprocal.' + c['key'], 1, customer_start,
                'Yield paid to the functioning adjacent district', 'ordinary reciprocal adjacency')
        elif c.get('district_functioning') is None:
            unknowns.append('Customer district completion/pillage missing for '+c['key'])
        stage = CUSTOMERS[kind][1]
        if stage not in starts or not c['functioning'] or c.get('building') != CUSTOMERS[kind][0]:
            continue
        begin = max(starts[stage], c['ready_turn'])
        if stage == 2:
            amount = 1
        elif c.get('population') is None:
            unknowns.append('Customer population missing for ' + c['key'])
            continue
        elif stage == 3:
            amount = c['population'] * rules['stage3_engine_amount_per_population']
        else:
            amount = c['population'] // 5  # per customer/branch, never pooled population
        for key in ('production', 'gold'):
            add(ledger[key], f'stage{stage}.seller.' + c['key'], amount, begin,
                'Ordinary transaction; no material-supply gate')
        add(ledger['production' if stage == 2 else 'culture'], f'stage{stage}.customer.' + c['key'],
            amount, begin, 'Counterparty transaction return')
    for stage, begin in starts.items():
        add(ledger['gold'], f'stage{stage}.maintenance', -rules['buildings'][str(stage)]['maintenance'],
            begin, 'Building maintenance', 'native building costs participate')
    if 2 in starts:
        for material in working_base:
            begin = max(starts[2], material_ready[material['plot']])
            factor = material.get('intensity', 1)
            add(ledger['culture'], 'workshop.material.' + str(material['plot']), factor, begin, 'Working Base → Workshop')
            for key in ('production', 'gold'):
                if material.get('worked') is True:
                    add(ledger[key], 'material.workshop.' + str(material['plot']), factor, begin, 'Worked Base improvement return')
                elif material.get('worked') is None:
                    unknowns.append('Citizen working material tile '+str(material['plot']))
        for stage in (3, 4):
            if stage in starts:
                begin = max(starts[2], starts[stage])
                for key in ('production', 'gold'):
                    add(ledger[key], f'local.stage{stage}.to_workshop', 1, begin, 'Local producer transaction')
                add(ledger['culture'], f'local.workshop.to_stage{stage}', 1, begin, 'Local downstream Culture')
    if 4 in starts:
        for material in working_spec:
            begin = max(starts[4], material_ready[material['plot']])
            factor = material.get('intensity', 1)
            add(ledger['culture'], 'fashion.material.' + str(material['plot']), factor, begin, 'Working Specialty → Fashion House')
            for key in ('production', 'gold'):
                if material.get('worked') is True:
                    add(ledger[key], 'material.fashion.' + str(material['plot']), factor, begin, 'Worked Specialty improvement return')
                elif material.get('worked') is None:
                    unknowns.append('Citizen working material tile '+str(material['plot']))
    services = []
    service_utility = 0.0
    for stage, name in SERVICE.items():
        matches = [c for c in customers if CUSTOMERS.get(c['district'], (None, None))[1] == stage
                   and c['owner'] == site['identity']['player'] and c['functioning']
                   and c.get('building') == CUSTOMERS[c['district']][0]]
        supply = bool(working_base) and (stage != 4 or bool(working_spec))
        unlock = site.get('service_unlocks', {}).get(str(stage))
        feasible = stage in starts and supply and bool(matches)
        state = 'available_in_plan' if feasible and unlock is True else 'conditional_unlock' if feasible else 'missing_path'
        services.append(dict(name=name, state=state, customers=[c['key'] for c in matches]))
        if feasible and unlock is True:
            # User-defined service review value; not an engine conversion.
            base_start = min(material_ready[m['plot']] for m in working_base)
            spec_start = min(material_ready[m['plot']] for m in working_spec) if stage == 4 else 0
            begin = max(starts[stage], min(c['ready_turn'] for c in matches), base_start, spec_start)
            service_utility += service_values.get(name, 0) * max(0, horizon-begin)
            if stage == 2:
                unknowns.append('Dockmaster naval era eligibility and beneficiary production need separate valuation')
    gross = {key: sum(row['value_per_turn'] * max(0, horizon-row['start_turn'])
                      for row in entries) for key, entries in ledger.items()}
    utility = sum(gross[key] * weights.get(key, 0) for key in gross) - cost * weights.get('production', 0) + service_utility
    return dict(site=site['id'], plan=sorted(set(plan)), status='partial_review', horizon=horizon,
                review_utility=round(utility, 6), utility_units='assumed review utility; NOT native Q8',
                modelled_yields={k: round(v, 6) for k, v in gross.items()}, construction_cost=cost,
                ledger=ledger, schedule=events, materials=dict(base=len(base), specialty=len(spec),
                    working_base=len(working_base), working_specialty=len(working_spec),
                    observed_working_base=sum(m['working'] is True for m in base),
                    observed_working_specialty=sum(m['working'] is True for m in spec)),
                services=services, assumptions=assumptions, unknowns=sorted(set(unknowns)),
                conditional_future=bool(future or future_materials), deployable=False)


def review(site, rules, **scenario):
    """Compare incremental investment with retaining the observed state/defer.

    Existing benefits are subtracted from each upgrade. A pre-existing Quarter
    never receives a second construction bill or credit for its sunk baseline.
    """
    existing = {int(k) for k, v in site['existing_buildings'].items() if v is True}
    baseline_scenario = {k: v for k, v in scenario.items() if k not in ('future', 'future_materials')}
    baseline = evaluate(site, sorted(existing), rules, **baseline_scenario) if site['quarter']['exists'] else None
    results = []
    for count in range(4):
        for plan in itertools.combinations(STAGES, count):
            if not existing <= set(plan) or ((3 in plan or 4 in plan) and 2 not in plan):
                continue
            result = evaluate(site, plan, rules, **scenario)
            if result['review_utility'] is not None:
                result['incremental_modelled_yields'] = dict(result['modelled_yields'])
            if result['review_utility'] is not None and baseline:
                if baseline['review_utility'] is None:
                    result['review_utility'] = None
                    result['status'] = baseline['status']
                else:
                    result['review_utility'] = round(result['review_utility']-baseline['review_utility'], 6)
                    result['incremental_modelled_yields'] = {k: round(v-baseline['modelled_yields'][k], 6)
                        for k, v in result['modelled_yields'].items()}
            results.append(result)
    usable = [r for r in results if r['review_utility'] is not None]
    best = max(usable, key=lambda r: (r['review_utility'], -len(r['plan']))) if usable else None
    base_path = bool(best and best['materials']['working_base'])
    base_potential = bool(best and best['materials']['base'])
    goal_status = 'working_or_explicit_conditional_base' if base_path else (
        'base_potential_needs_development' if base_potential else 'no_owned_base_path')
    action = 'retain_or_defer'
    if best and best['review_utility'] > 0:
        action = 'review_upgrade' if site['quarter']['exists'] else (
            'review_investment' if base_path else 'review_only_missing_base_path')
    return dict(site=site['id'], group=site['group'], best=best, plans=results,
                defer_utility=0, preferred_action=action, base_goal_status=goal_status,
                ranking_scope='within captured world/player/city only; partial scenario, not executable recommendation')
