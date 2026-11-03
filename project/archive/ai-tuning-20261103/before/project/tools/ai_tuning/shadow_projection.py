"""Offline attachment-aware projection of a captured CSC shadow snapshot.

BuildingModifiers attach once per functioning source building. The shared preview
uses boolean empire presence instead. This model explains that difference without
changing the game, promoting failed Plot previews, or inventing future development.
"""
from copy import deepcopy
from math import isfinite

YIELDS = ('YIELD_PRODUCTION', 'YIELD_GOLD')


def numeric(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and isfinite(value)


def building_census(raw, core):
    """Join by owner/city, deduplicate repeated district inventories, retain gaps.

    The Core census establishes the complete player city set. A captured district
    carries a city-wide named building census, not buildings located on that plot.
    Empty Core building lists establish empty cities; integer indices alone cannot
    establish the types or pillage state of a nonempty missing inventory.
    """
    if raw['turn'] != core['turn']:
        raise ValueError('Mixed capture clocks')
    cities = {c['id']: c for c in core['cities'] if c['owner'] == raw['player']}
    if len(cities) != sum(c['owner'] == raw['player'] for c in core['cities']):
        raise ValueError('Duplicate city identity')
    inventories = {}
    for tile in raw['tiles']:
        cid = tile['purchase_city']
        if tile['owner'] != raw['player'] or tile['district'] < 0 or cid not in cities:
            continue
        inventory = tile.get('city_building_inventory')
        if not isinstance(inventory, list):
            continue
        named = {b['type']: b['pillaged'] for b in inventory}
        if len(named) != len(inventory):
            raise ValueError('Duplicate source building in a city census')
        if cid in inventories and named != inventories[cid]:
            raise ValueError('Conflicting city-wide building inventories')
        if len(inventory) != len(cities[cid]['buildings']):
            raise ValueError('UI/Core building census disagreement')
        inventories[cid] = named
    for cid, city in cities.items():
        if not city['buildings']:
            inventories.setdefault(cid, {})
    return cities, inventories


def source_instances(rule, city, cities, inventories):
    owner = rule.get('ModifierOwner', 'DistrictModifiers')
    if owner != 'BuildingModifiers':
        return (int(rule['eligible']), []) if isinstance(rule.get('eligible'), bool) else (None, ['eligibility unavailable'])
    scope = rule.get('CollectionType')
    if scope == 'COLLECTION_CITY_DISTRICTS':
        selected = [city]
    elif scope == 'COLLECTION_PLAYER_DISTRICTS':
        selected = sorted(cities)
    else:
        return None, ['unsupported building collection ' + str(scope)]
    count, gaps = 0, []
    building = rule['WhoIsTheOwner']
    for cid in selected:
        inventory = inventories.get(cid)
        if inventory is None:
            gaps.append('missing named building census city ' + str(cid))
        elif building in inventory:
            pillaged = inventory[building]
            if pillaged is False:
                count += 1
            elif pillaged is not True:
                gaps.append('unknown source pillage state city ' + str(cid))
    # Building counts do not override Only/trait restrictions in captured eligibility.
    if rule.get('eligible') is False:
        return 0, []
    if rule.get('eligible') is not True:
        gaps.append('eligibility unavailable')
    return (None if gaps else count), gaps


def project(preview, city, cities, inventories):
    totals = dict.fromkeys(YIELDS, 0)
    details, gaps = [], []
    for rule in preview['rules']:
        if rule.get('ProvideType') != 'SelfBonus' or rule.get('YieldType') not in YIELDS:
            continue
        multiplicity, missing = source_instances(rule, city, cities, inventories)
        amount = rule.get('computed_amount')
        if not numeric(amount):
            missing.append('unknown encoded amount')
        contribution = amount * multiplicity if not missing and multiplicity is not None else None
        details.append(dict(rule=rule['ID'], yield_type=rule['YieldType'],
                            encoded_per_source=amount, active_source_instances=multiplicity,
                            contribution=contribution, gaps=missing))
        if contribution is None:
            totals[rule['YieldType']] = None
            gaps.extend(rule['ID'] + ': ' + issue for issue in missing)
        elif totals[rule['YieldType']] is not None:
            totals[rule['YieldType']] += contribution
    return dict(real=totals, rules=details, gaps=gaps,
                scope='captured CSC SelfBonus only; not all native/modifier yield effects')


def review_projection(raw, core, source):
    if not isinstance(source, str) or not source.strip():
        raise ValueError('Capture provenance required')
    if raw.get('action_authorization') is not False:
        raise ValueError('Shadow snapshot must not authorize actions')
    cities, inventories = building_census(raw, core)
    if raw['city'] not in cities:
        raise ValueError('Target city is not in the captured player census')
    controls, candidates = [], []
    for control in raw['controls']:
        projection = project(control['preview'], control['city'], cities, inventories)
        observed = control['existing_adjacency']
        matched = all(numeric(projection['real'][y]) and numeric(observed.get(y))
                      and projection['real'][y] == observed[y] for y in YIELDS)
        controls.append(dict(city=control['city'], plot=control['plot'], quarter=control['quarter'],
                             shared_computed=deepcopy(control['preview']['computed_real']),
                             existing_adjacency=deepcopy(observed), projection=projection, matched=matched))
    for candidate in raw['candidates']:
        candidates.append(dict(city=raw['city'], plot=candidate['plot'], quarter=candidate['quarter'],
                               shared_computed=deepcopy(candidate['preview']['computed_real']),
                               projection=project(candidate['preview'], raw['city'], cities, inventories)))
    return dict(source=source, controls=controls, candidates=candidates,
                named_city_inventory_count=len(inventories), player_city_count=len(cities),
                controls_matched=sum(c['matched'] for c in controls), control_count=len(controls),
                action_authorization=False, native_plot_preview_validated=False,
                candidate_total_adjacency_validated=False,
                interpretation='attachment-instance model tested against existing controls; no dynamic causal intervention')
