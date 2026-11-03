"""Extract copied facts from closed captures. No imports from retired AI tooling."""
import argparse
import hashlib
import json
from pathlib import Path

from evaluator import BUILDINGS, CUSTOMERS

ROOT = Path(__file__).resolve().parents[3]


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def material(row, player, *, shadow=False):
    roles = row.get('roles', {}).get('TAILORS', {}) if shadow else row
    base = roles.get('base', False) if shadow else roles.get('base_mapped', False)
    spec = roles.get('specialty', False) if shadow else roles.get('spec_mapped', False)
    improvement = row.get('improvement', '')
    return dict(plot=row['plot'], resource=row.get('resource', ''), base=base, specialty=spec,
        owned=row.get('owner') == player, revealed=row.get('revealed') is True and (
            row.get('resource_visible') is True if shadow else row.get('visible') is True),
        district_free=row.get('district') == -1,
        working=(row.get('owner') == player and row.get('revealed') is True
                 and row.get('resource_visible') is True and row.get('district') == -1
                 and bool(improvement) and row.get('valid_resource_improvement') is True
                 and row.get('improvement_pillaged') is False) if shadow else (
                     row.get('working_base') is True or row.get('working_spec') is True),
        worked=(row['worked'] > 0) if shadow and type(row.get('worked')) is int else None,
        intensity={'IMPROVEMENT_INDUSTRY': 2, 'IMPROVEMENT_CORPORATION': 3}.get(improvement, 1))


def shadow_sites(snapshot, census):
    tiles = {t['plot']: t for t in snapshot['tiles']}
    populations = {(c['owner'], c['id']): c['population'] for c in census['cities']}
    player, city = snapshot['player'], snapshot['city']
    sites = []
    for position, candidate in enumerate(snapshot['candidates']):
        if candidate['quarter'] != 'TAILORS':
            continue
        tile = tiles[candidate['plot']]
        known = {r['index']: r['type'] for r in candidate['mapped_customer_types'] if r['type'] in CUSTOMERS}
        customers = []
        for index in tile['neighbors']:
            neighbor = tiles[index]
            kind = known.get(neighbor['district'])
            if kind:
                building = CUSTOMERS[kind][0]
                entries = [b for b in neighbor['city_building_inventory'] if b['type'] == building]
                customers.append(dict(key=f'{neighbor["owner"]}:{neighbor["purchase_city"]}:{index}:{kind}',
                    owner=neighbor['owner'], city=neighbor['purchase_city'], plot=index, district=kind,
                    building=building if entries else None, functioning=None, district_functioning=None,
                    population=populations.get((neighbor['owner'], neighbor['purchase_city']))))
        counts = {r['count'] for r in candidate['preview']['rules']
                  if r['AdjacencyType'] == 'FROM_RIVER_CROSSING' and r.get('Only') == 'Human&AI'}
        # Only the captured native getter count is reused; old computed amounts,
        # private yields, eligibility heuristics and recommendations are discarded.
        edges = counts.pop() if len(counts) == 1 else None
        sites.append(dict(id=f'shadow110:p{player}:c{city}:TAILORS:{tile["plot"]}',
            group=f'shadow110:p{player}:c{city}:TAILORS', name='Captured turn110 city',
            identity=dict(world='shadow110', turn=snapshot['turn'], player=player, city=city,
                          quarter='TAILORS', plot=tile['plot']), original_human=False,
            provenance=dict(source='shadow', pointer=f'/candidates/{position}',
                            interpretation='Historical geometry under the current mechanics profile'),
            quarter=dict(exists=False, complete=False, pillaged=False),
            city=dict(population=snapshot['city_state']['population'], production=snapshot['economics']['production']),
            land=dict(legal=candidate['legal'], can_produce=candidate['can_produce'],
                      district_cost=snapshot['district_state']['TAILORS']['cost'], reservation=None,
                      improvement=tile['improvement'], resource=tile.get('resource'), worked=tile.get('worked')),
            existing_buildings={str(s): False for s in BUILDINGS}, river_edges=edges,
            materials=[material(tiles[n], player, shadow=True) for n in tile['neighbors']],
            customers=customers, service_unlocks={}, future_footprints=candidate['future_customer_geometry'],
            unknowns=['Plot potential is not a fresh immediate CanZone/reservation receipt',
                      'Farm removal/lost worked yields and alternative district values are unpriced']))
    return sites


def established_sites(capture, label):
    physical, ui = capture['physical'], capture['UI']
    cities = {(c['player'], c['city']): c for c in physical['cities']}
    ui_cities = {(c['player'], c['city']): c for c in ui['cities']}
    sites = []
    for index, quarter in enumerate(physical['quarters']):
        if quarter['quarter'] != 'TAILORS' or quarter['player'] == 0:
            continue
        player, city, plot = quarter['player'], quarter['city'], quarter['source']
        owner = cities[(player, city)]
        public = ui_cities.get((player, city), {})
        customers = []
        for customer in quarter['customers']:
            building = customer.get('building', {})
            kind = customer['district']
            if kind not in CUSTOMERS:
                continue
            target_owner = customer['district_owner']
            target = cities.get((target_owner, customer['city']), {})
            customers.append(dict(key=f'{target_owner}:{customer["city"]}:{customer["plot"]}:{kind}',
                owner=target_owner, city=customer['city'], plot=customer['plot'], district=kind,
                building=building.get('type'), functioning=(customer.get('district_complete') is True
                    and customer.get('district_pillaged') is False and building.get('pillaged') is False),
                district_functioning=(customer.get('district_complete') is True and customer.get('district_pillaged') is False),
                population=target.get('population')))
        # Quarter.customers contains functioning customer-building paths only.
        # Add other adjacent district shells using the source material-ring plots.
        adjacent = {m['plot'] for m in quarter['materials']}
        seen = {c['plot'] for c in customers}
        for other in physical['cities']:
            for district in other['districts']:
                kind = district['type']
                if district['plot'] not in adjacent or district['plot'] in seen or kind not in CUSTOMERS:
                    continue
                inventory = ui_cities.get((other['player'], other['city']), {}).get('buildings', [])
                building = next((b for b in inventory if b['type'] == CUSTOMERS[kind][0] and b.get('present') is True), None)
                customers.append(dict(key=f'{other["player"]}:{other["city"]}:{district["plot"]}:{kind}',
                    owner=other['player'], city=other['city'], plot=district['plot'], district=kind,
                    building=building['type'] if building else None, population=other['population'],
                    district_functioning=(district['complete'] is True and district['pillaged'] is False),
                    functioning=(district['complete'] is True and district['pillaged'] is False
                                 and building is not None and building['pillaged'] is False)))
                seen.add(district['plot'])
        existing = {str(s): any(b['type'] == name for b in quarter['producers'])
                    for s, name in BUILDINGS.items()}
        pillaged = [s for s, name in BUILDINGS.items() if any(
            b['type'] == name and b['pillaged'] is True for b in quarter['producers'])]
        unlocks = {}
        for stage, property_name in ((2, 'CSC_TAILORS_STAGE_2_EFFECT_PRODUCTION'),
                                     (3, 'CSC_TAILORS_STAGE_3_EFFECT_FAITH'),
                                     (4, 'CSC_TAILORS_STAGE_4_EFFECT_TOURISM')):
            if owner['properties'].get(property_name, {}).get('value') == 1:
                unlocks[str(stage)] = True
        sites.append(dict(id=f'{label}:p{player}:c{city}:TAILORS:{plot}',
            group=f'{label}:p{player}:c{city}:TAILORS', name=owner['name'],
            identity=dict(world=label, turn=capture['turn'], player=player, city=city, quarter='TAILORS', plot=plot),
            original_human=False, provenance=dict(source=label, pointer=f'/physical/quarters/{index}',
                interpretation='Retrospective upgrade review; historical treatment, not a new placement comparison'),
            quarter=dict(exists=True, complete=quarter['complete'], pillaged=quarter['pillaged']),
            city=dict(population=owner['population'], production=public.get('production'), production_turn=ui['turn']),
            land=dict(legal=None, district_cost=0, reservation=None), existing_buildings=existing,
            river_edges=None, pillaged_buildings=pillaged, materials=[material(m, player) for m in quarter['materials']],
            customers=customers, service_unlocks=unlocks, future_footprints=[],
            unknowns=['River-edge and citizen-working data absent from this capture',
                      'Missing producer/customer unlock and cost quotes need fresh confirmation'] + (
                          ['Production observation is from UI turn '+str(ui['turn'])] if ui['turn'] != capture['turn'] else [])))
    return sites


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ('shadow', 'census', 'candidate', 'reference', 'output'):
        parser.add_argument('--'+key, required=True, type=Path)
    args = parser.parse_args()
    sources = []
    captures = {}
    for key in ('shadow', 'census', 'candidate', 'reference'):
        path = getattr(args, key).resolve()
        raw = path.read_bytes()
        captures[key] = json.loads(raw.decode('utf-8-sig'))
        sources.append(dict(id=key if key in ('shadow', 'census') else key+'150', locator=str(path),
                            sha256=hashlib.sha256(raw).hexdigest()))
    sites = shadow_sites(captures['shadow'], captures['census'])
    sites += established_sites(captures['candidate'], 'candidate150')
    sites += established_sites(captures['reference'], 'reference150')
    sources_pinned = []
    for relative in ('Civ Supply Chains/Data/CSC_Q_TAILORS.sql', 'Civ Supply Chains/Data/CSC_Q_TAILORS_GOLD.sql',
                     'Civ Supply Chains/Lua_UI/CustomerPopulationReturns/CSC_CustomerPopulationReturns.lua',
                     'Civ Supply Chains/Lua_UI/Adjacencies/CSC_AdjacencyCore.lua',
                     'Civ Supply Chains/Lua_UI/Adjacencies/CSC_AdjacencyGameplay.lua'):
        text = (ROOT/relative).read_text(encoding='utf-8-sig').replace('\r\n', '\n')
        sources_pinned.append(dict(path=relative, sha256_lf=hashlib.sha256(text.encode()).hexdigest()))
    assert '0.105' in (ROOT/'Civ Supply Chains/Data/CSC_Q_TAILORS.sql').read_text(encoding='utf-8-sig')
    assert 'math.floor((customerCity:GetPopulation() or 0) / 5)' in (
        ROOT/'Civ Supply Chains/Lua_UI/CustomerPopulationReturns/CSC_CustomerPopulationReturns.lua').read_text(encoding='utf-8-sig')
    assert len({s['id'] for s in sites}) == len(sites)
    rules = dict(profile='tailors-review-20261103-v1', district_cost=60, district_maintenance=1,
                 buildings={'2': dict(cost=80, maintenance=2), '3': dict(cost=160, maintenance=2),
                            '4': dict(cost=250, maintenance=3)}, stage3_engine_amount_per_population=0.105,
                 note='Current SQL uses engine coefficient0.105; design display0.1 is not substituted.',
                 profile_assumptions=['CSC Gold companion enabled', 'Base district/building types; optional integrations unpriced'],
                 primary_sources=sources_pinned)
    result = dict(schema=1, sources=sources, rules=rules, sites=sites,
        scope='Copied historical observations, re-evaluated with an explicit current-mechanics subset. No old policy imports.',
        recent_bridge_case='Sydney source250 trace lacks material type catalogue, buildings and river edges; not silently joined to older worlds.')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(dict(sites=len(sites), new_sites=len([s for s in sites if not s['quarter']['exists']]),
                          output=str(args.output))))


if __name__ == '__main__':
    main()
