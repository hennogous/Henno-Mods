"""Pure offline coordination of evaluator evidence; never an action authority."""
from copy import deepcopy
from math import isfinite

from site_evaluator import evaluate_site, value

CHAIN_STATES = {'complete', 'unfinished', 'pillaged'}
REQUEST_STATES = {'no_request', 'rejected', 'accepted_waiting', 'selected', 'unknown'}


def _int(v, name):
    if isinstance(v, bool) or not isinstance(v, int) or v < 0:
        raise ValueError(name + ' must be a nonnegative integer')
    return v


def _fact(f, name, allowed=None):
    if not isinstance(f, dict) or not isinstance(f.get('source'), str) or not f['source'].strip() or 'value' not in f:
        raise ValueError(name + ' needs sourced evidence')
    v = f['value']
    if allowed is not None and (not isinstance(v, str) or v not in allowed):
        raise ValueError(name + ' has invalid enum')
    return v


def _quantity(f, name):
    v = _fact(f, name)
    if v is not None and (isinstance(v, bool) or not isinstance(v, (int, float)) or not isfinite(v) or v < 0):
        raise ValueError(name + ' must be nonnegative finite number or unknown')
    return v


def _identity(identity, player, turn, label):
    if not isinstance(identity, dict) or not isinstance(identity.get('source'), str) or not identity['source'].strip():
        raise ValueError(label + ' identity requires provenance')
    for k in ('player', 'city', 'turn', 'plot'):
        _int(identity.get(k), label + ' identity ' + k)
    if identity['player'] != player or identity['turn'] != turn:
        raise ValueError(label + ' has mixed player or stale turn')


def _site_key(s):
    i = s['identity']
    return (i['city'], s['quarter'], i['plot'])


def _chain_key(c):
    i = c['identity']
    return (i['city'], c['quarter'], i['plot'])


def _ref(key):
    return {'city': key[0], 'quarter': key[1], 'plot': key[2]}


def coordinate(snapshot):
    """Return deterministic evidence and conflict review, never choices or actions.

    See README for the precise schema. All references are copied; the caller's
    snapshot and the returned evidence cannot mutate one another.
    """
    if not isinstance(snapshot, dict) or not isinstance(snapshot.get('source'), str) or not snapshot['source'].strip():
        raise ValueError('snapshot provenance required')
    player = _int(snapshot.get('player'), 'player')
    turn = _int(snapshot.get('turn'), 'turn')
    mapping = snapshot.get('mapping')
    if not isinstance(mapping, dict) or value(mapping.get('validated')) is not True or not mapping.get('snapshot'):
        raise ValueError('validated mapping snapshot required')
    if not isinstance(snapshot.get('sites'), list) or not isinstance(snapshot.get('chains'), list):
        raise ValueError('sites and chains lists required')
    capacity = _quantity(snapshot.get('production_capacity'), 'production_capacity')
    sites, chains = {}, {}
    for s in snapshot['sites']:
        if not isinstance(s, dict):
            raise ValueError('invalid site')
        _identity(s.get('identity'), player, turn, 'site')
        if not isinstance(s.get('quarter'), str) or not s['quarter'].strip():
            raise ValueError('site quarter required')
        k = _site_key(s)
        if k in sites:
            raise ValueError('duplicate site identity')
        if not isinstance(s.get('future', []), list):
            raise ValueError('site future must be a list')
        for f in s.get('future', []):
            _int(f.get('plot'), 'future plot')
            if f.get('kind') not in ('customer', 'material') or not isinstance(f.get('source'), str) or not f['source'].strip():
                raise ValueError('future kind and provenance required')
        sites[k] = s
    for c in snapshot['chains']:
        if not isinstance(c, dict):
            raise ValueError('invalid chain')
        _identity(c.get('identity'), player, turn, 'chain')
        if not isinstance(c.get('quarter'), str) or not c['quarter'].strip():
            raise ValueError('chain quarter required')
        k = _chain_key(c)
        if k in chains:
            raise ValueError('duplicate chain identity')
        _fact(c.get('state'), 'chain state', CHAIN_STATES)
        _fact(c.get('request_state'), 'request state', REQUEST_STATES)
        _quantity(c.get('remaining_production'), 'remaining_production')
        if not isinstance(c.get('material_dependencies'), list):
            raise ValueError('material_dependencies list required')
        seen = set()
        for dep in c['material_dependencies']:
            if not isinstance(dep, dict):
                raise ValueError('invalid dependency')
            plot = _int(dep.get('plot'), 'dependency plot')
            if plot in seen:
                raise ValueError('duplicate dependency plot')
            seen.add(plot)
            if _fact(dep.get('native_bound'), 'dependency native_bound') is not True:
                raise ValueError('dependency needs explicit native-bound evidence')
        chains[k] = c
    # A pair-specific proof is optional; absence never implies either possibility.
    sharing = {}
    for proof in snapshot.get('customer_sharing', []):
        if not isinstance(proof, dict) or not isinstance(proof.get('sites'), list) or len(proof['sites']) != 2:
            raise ValueError('sharing proof requires two site references')
        keys = []
        for ref in proof['sites']:
            if not isinstance(ref, dict):
                raise ValueError('invalid sharing site reference')
            _int(ref.get('city'), 'sharing city'); _int(ref.get('plot'), 'sharing site plot')
            if not isinstance(ref.get('quarter'), str) or not ref['quarter'].strip():
                raise ValueError('sharing quarter required')
            key = (ref['city'], ref['quarter'], ref['plot'])
            if key not in sites:
                raise ValueError('sharing references unknown site')
            keys.append(key)
        if keys[0] == keys[1]:
            raise ValueError('sharing references must differ')
        plot = _int(proof.get('plot'), 'sharing plot')
        for key in keys:
            if not any(f['plot'] == plot and f['kind'] == 'customer' for f in sites[key].get('future', [])):
                raise ValueError('sharing proof must match both customer plans')
        v = _fact(proof.get('shareable'), 'sharing proof')
        if type(v) is not bool:
            raise ValueError('shareable must be boolean')
        key = (tuple(sorted(keys)), plot)
        if key in sharing:
            raise ValueError('duplicate sharing proof')
        sharing[key] = proof['shareable']
    keys = sorted(sites)
    evaluated = {k: evaluate_site(sites[k], mapping) for k in keys}
    vectors = [{'site': _ref(k), 'evidence': evaluated[k]} for k in keys]
    relations = []
    for n, a in enumerate(keys):
        sa = sites[a]
        for b in keys[n+1:]:
            sb = sites[b]
            if a[2] == b[2]:
                relations.append({'sites': [_ref(a), _ref(b)], 'plot': a[2], 'kind': 'footprint', 'status': 'incompatible'})
            claims_a = [(a[2], 'footprint', None)] + [(f['plot'], f['kind'], e['status']) for f, e in zip(sa.get('future', []), evaluated[a]['future'])]
            claims_b = [(b[2], 'footprint', None)] + [(f['plot'], f['kind'], e['status']) for f, e in zip(sb.get('future', []), evaluated[b]['future'])]
            for pa, ka, ea in claims_a:
                for pb, kb, eb in claims_b:
                    if pa != pb or (ka == kb == 'footprint'):
                        continue
                    if ka == kb == 'customer':
                        proof = sharing.get(((a, b), pa))
                        status = 'unresolved' if proof is None else ('shareable_with_proof' if proof['value'] else 'incompatible_with_proof')
                        rel = {'sites': [_ref(a), _ref(b)], 'plot': pa, 'kind': 'future_customer', 'status': status}
                        if proof is not None:
                            rel['sharing_evidence'] = deepcopy(proof)
                    elif ka == kb == 'material':
                        rel = {'sites': [_ref(a), _ref(b)], 'plot': pa, 'kind': 'future_material', 'status': 'unresolved'}
                    else:
                        rel = {'sites': [_ref(a), _ref(b)], 'plot': pa, 'kind': 'plot_claim', 'claims': [ka, kb], 'status': 'incompatible'}
                    rel['plan_statuses'] = [ea, eb]
                    rel['future_feasibility_established'] = all(x is None or x == 'credible_conditional' for x in (ea, eb))
                    if not rel['future_feasibility_established']:
                        rel['status_if_feasible'] = rel['status']
                        rel['status'] = 'conditional_unresolved'
                    if rel not in relations:
                        relations.append(rel)
    dependencies = []
    for sk in keys:
        for ck in sorted(chains):
            for dep in chains[ck]['material_dependencies']:
                if sk[2] == dep['plot']:
                    dependencies.append({'site': _ref(sk), 'chain': _ref(ck), 'plot': dep['plot'],
                                         'kind': 'material_dependency_tradeoff', 'evidence': deepcopy(dep),
                                         'loss_value': None})
    start_status = {'infeasible': 'ineligible', 'insufficient_evidence': 'deferred',
                    'tradeoff_review': 'review', 'promising_review': 'review',
                    'marginal_no_mapped_base': 'review', 'marginal_review': 'review'}
    options = [{'kind': 'start', 'site': _ref(k),
                'status': start_status[evaluated[k]['recommendation']],
                'recommendation': evaluated[k]['recommendation'],
                'needs_site_review': bool(evaluated[k]['unknowns'] or evaluated[k]['rejections'] or any(f['status'] == 'withheld' for f in evaluated[k]['future'])),
                'unknowns': deepcopy(evaluated[k]['unknowns']),
                'rejections': deepcopy(evaluated[k]['rejections'])} for k in keys]
    for k in sorted(chains):
        c = chains[k]; state = value(c['state'])
        if state in ('unfinished', 'pillaged'):
            options.append({'kind': 'finish' if state == 'unfinished' else 'repair', 'chain': _ref(k),
                            'request_state': deepcopy(c['request_state']), 'remaining_production': deepcopy(c['remaining_production']), 'status': 'review'})
    # A start is inconsistent with a declared existing Quarter footprint. Keep
    # both facts visible rather than silently offer a duplicate start or assume
    # a demolition/replacement policy. Native legality must be reconciled first.
    for option in options:
        if option['kind'] != 'start':
            continue
        occupants = [k for k in sorted(chains) if k[2] == option['site']['plot']]
        if occupants:
            option['status'] = 'deferred'
            option['needs_site_review'] = True
            option['unknowns'].append('candidate overlaps a declared existing Quarter footprint')
            option['existing_footprints'] = [_ref(k) for k in occupants]
    unknowns = []
    if capacity is None:
        unknowns.append('production capacity unknown: joint allocation and preference deferred')
    if any(r['status'] == 'unresolved' and r['kind'] == 'future_customer' for r in relations):
        unknowns.append('customer sharing unresolved')
    if any(r['status'] == 'unresolved' and r['kind'] == 'future_material' for r in relations):
        unknowns.append('material sharing unresolved')
    if any(value(c['request_state']) == 'unknown' for c in chains.values()):
        unknowns.append('chain request state unknown')
    if any(value(c['remaining_production']) is None for c in chains.values()):
        unknowns.append('chain remaining production unknown')
    if dependencies:
        unknowns.append('material dependency loss value and alternatives unassessed')
    return {'snapshot': {'player': player, 'turn': turn, 'source': snapshot['source'], 'mapping_snapshot': deepcopy(mapping['snapshot'])},
            'production_capacity': deepcopy(snapshot['production_capacity']),
            'production_capacity_semantics': 'opaque sourced observation; units and allocation comparability not established', 'site_evidence': vectors,
            'chains': [deepcopy(chains[k]) for k in sorted(chains)], 'options': options,
            'site_relationships': relations, 'chain_dependencies': dependencies,
            'unknowns': unknowns, 'joint_allocation': 'deferred', 'preference': 'deferred',
            'action_authorization': False}
