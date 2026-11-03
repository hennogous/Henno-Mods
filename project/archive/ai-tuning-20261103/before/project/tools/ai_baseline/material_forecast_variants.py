"""Declared same-save diagnostic variants; no game control or economic mutation."""
import hashlib
import json
from pathlib import Path
from material_forecast_contract import database_delta

GATE_TABLES = {'AiFavoredItems', 'AiListTypes', 'AiLists', 'Strategy_Priorities'}
HARVEST_TABLES = {'Modifiers', 'ModifierArguments', 'TraitModifiers'}
BRANCHES = (None, 'allocation-v2', 'boost-gate-v3', 'native-harvest-v4', 'native-harvest-live-v4', 'native-harvest-live-v4b', 'native-harvest-live-v4c', 'pasture-forecast-v5', 'resource-improvement-forecast-v6', 'material-viability-v7')

def variant(series, arm, branch):
    if arm not in ('reference', 'raw-resource') or branch not in BRANCHES:
        raise AssertionError('Undeclared diagnostic variant')
    if branch is not None and arm != 'raw-resource':
        raise AssertionError('Measured diagnostic branches require raw-resource control')
    gate = branch == 'boost-gate-v3'
    harvest = branch == 'native-harvest-v4'
    live = branch in ('native-harvest-live-v4','native-harvest-live-v4b', 'native-harvest-live-v4c')
    measured = branch in ('native-harvest-live-v4b','native-harvest-live-v4c')
    pasture = branch == 'pasture-forecast-v5'
    viability = branch == 'material-viability-v7'
    resource = branch in ('resource-improvement-forecast-v6','material-viability-v7')
    extra = gate or harvest or pasture or resource
    preparation = 'source016-material-viability' if viability else 'source016-resource-improvement-forecast' if resource else 'source016-pasture-forecast' if pasture else 'source016-measured-harvest-rule' if measured else 'source016-existing-harvest-rule' if live else 'source016-native-harvest-guard' if harvest else 'source016-boost-gate' if gate else 'source016-forecast-pair'
    return dict(branch=branch, boost_gate=gate, native_harvest_guard=harvest, pasture_forecast=pasture, resource_improvement_forecast=resource, material_viability=viability,
                needs_raw_control=extra or live, measured_allocation=branch is not None, runtime_harvest_rule=live, measured_rule_legality=measured, runtime_rule_token=branch if live else None, ready_for_native=not harvest,
                preparation=Path(series) / 'offline-preparation' / preparation,
                files=515 if resource else 514 if extra else (513 if arm == 'raw-resource' else 512),
                runtime_deltas=7 if resource else 6 if extra else (5 if arm == 'raw-resource' else 4),
                extra_SQL='CSC_AI_ResourceImprovementForecast_Diagnostic.sql' if resource else 'CSC_AI_ImprovementForecast_Diagnostic.sql' if pasture else 'CSC_AI_NativeHarvestGuard_Diagnostic.sql' if harvest else 'CSC_AI_MaterialBoostGate_Diagnostic.sql' if gate else None)

def changed_tables(before, after):
    return sorted(k for k in before.keys() | after.keys() if before.get(k) != after.get(k))

def declared_database_delta(before, actual, *, treatment, boost_gate=False,
                            native_harvest_guard=False, pasture_forecast=False, resource_improvement_forecast=False, raw_control=None):
    if sum(bool(x)for x in(boost_gate,native_harvest_guard,pasture_forecast,resource_improvement_forecast))>1:
        raise AssertionError('Cannot conflate distinct interventions')
    if not (boost_gate or native_harvest_guard or pasture_forecast or resource_improvement_forecast):
        return database_delta(before, actual, treatment=treatment)
    if not treatment or raw_control is None:
        raise AssertionError('Diagnostic needs declared raw control')
    database_delta(before, raw_control, treatment=True)
    allowed = {'Improvement_YieldChanges'} if pasture_forecast or resource_improvement_forecast else HARVEST_TABLES if native_harvest_guard else GATE_TABLES
    if set(changed_tables(raw_control, actual)) != allowed:
        raise AssertionError('Unexpected declared native database scope')
    return changed_tables(before, actual)

def verify_raw_control(preparation, series):
    root = Path(series) / 'raw-resource016-075-allocation-v2'
    if Path(preparation['raw_control']).resolve() != root.resolve():
        raise AssertionError('Wrong raw-control identity')
    path = root / 'independent-diagnostic-audit.json'
    audit = json.loads(path.read_text(encoding='utf-8-sig'))
    if hashlib.sha256(path.read_bytes()).hexdigest() != preparation['raw_control_audit_sha256']:
        raise AssertionError('Raw-control receipt changed')
    if not (audit['verified'] and audit['endpoint'] == 75 and audit['arm'] == 'raw-resource'
            and audit['runtime_restored510'] and audit['source_sha256'] == preparation['source_sha256']):
        raise AssertionError('Raw-control proof incomplete')
    return root

def verify_native_guard_scope(db, players, expected):
    """Verify loaded rule/owner bindings, not its unobserved decision-level effect."""
    modifier = 'MOD_CSC_AI_NATIVE_HARVEST_GUARD_DIAGNOSTIC'
    rows = [tuple(r) for r in db.execute('SELECT ModifierType,OwnerRequirementSetId FROM Modifiers WHERE ModifierId=?', (modifier,))]
    if rows != [('MODIFIER_PLAYER_ADJUST_PREVENT_HARVEST_RESOURCE', 'REQSET_CSC_AI_SUPPLY_AI')]:
        raise AssertionError('Wrong native resource-harvest modifier')
    rows = [tuple(r) for r in db.execute('SELECT Name,Value FROM ModifierArguments WHERE ModifierId=?', (modifier,))]
    if rows != [('Enable', '1')]:
        raise AssertionError('Wrong native guard arguments')
    rows = [tuple(r) for r in db.execute("SELECT CollectionType,EffectType FROM DynamicModifiers WHERE ModifierType='MODIFIER_PLAYER_ADJUST_PREVENT_HARVEST_RESOURCE'")]
    if rows != [('COLLECTION_OWNER', 'EFFECT_ADJUST_PLAYER_PREVENT_HARVEST_RESOURCE')]:
        raise AssertionError('Wrong native effect/collection')
    current = {p['id']: p for p in players}
    if len(expected) != 5 or {p['player'] for p in expected} != set(range(1, 6)):
        raise AssertionError('Guard must name exactly the five diagnostic AI owners')
    traits = {r[0] for r in db.execute('SELECT TraitType FROM TraitModifiers WHERE ModifierId=?', (modifier,))}
    if traits != {p['trait'] for p in expected}:
        raise AssertionError('Unexpected native owner attachment')
    for row in expected:
        player = current[row['player']]
        if player['human'] or player['leader'] != row['leader']:
            raise AssertionError('Source player/leader/human identity changed')
        owners = {r[0] for r in db.execute('SELECT LeaderType FROM LeaderTraits WHERE TraitType=?', (row['trait'],))}
        if owners != {row['leader']}:
            raise AssertionError('Guard owner trait is not exact and unique')
    observer = current[0]
    observer_traits = {r[0] for r in db.execute('SELECT TraitType FROM LeaderTraits WHERE LeaderType=?', (observer['leader'],))}
    if observer_traits & traits:
        raise AssertionError('Observer0 must remain excluded even during autoplay')
    return dict(verified_loaded_rule_and_owner_scope=True, players=[1,2,3,4,5],
                observer0_excluded_by_unique_traits=True, all_resource_harvesting_scope=True,
                per_material_or_Quarter_targeted=False, native_prevention_effect_proven=False)
