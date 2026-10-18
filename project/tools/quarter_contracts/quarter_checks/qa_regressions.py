"""Checks shared by Quarter validators: event wiring and delivered transactions."""
from pathlib import Path
import re


def material_total(db, building, resource, improvement, yield_type, adjacent=True, owned=True):
    """Evaluate the active plot-yield graph, including overlapping attachments."""
    def args(table, column, key):
        return dict(db.execute(f'SELECT Name,Value FROM {table} WHERE {column}=?', (key,)))

    def requirement(key):
        kind, inverse = db.execute('SELECT RequirementType,Inverse FROM Requirements WHERE RequirementId=?', (key,)).fetchone()
        a = args('RequirementArguments', 'RequirementId', key)
        if kind == 'REQUIREMENT_PLOT_ADJACENT_TO_OWNER':
            result = adjacent
        elif kind == 'REQUIREMENT_PLOT_RESOURCE_TAG_MATCHES':
            result = bool(db.execute('SELECT 1 FROM TypeTags WHERE Type=? AND Tag=?', (resource, a['Tag'])).fetchone())
        elif kind == 'REQUIREMENT_PLOT_IMPROVEMENT_TYPE_MATCHES':
            result = improvement == a['ImprovementType']
        elif kind == 'REQUIREMENT_REQUIREMENTSET_IS_MET':
            result = requirement_set(a['RequirementSetId'])
        else:
            raise ValueError('Unsupported material requirement: ' + kind)
        return not result if inverse else result

    def requirement_set(key):
        if key is None:
            return True
        mode = db.execute('SELECT RequirementSetType FROM RequirementSets WHERE RequirementSetId=?', (key,)).fetchone()[0]
        values = [requirement(r[0]) for r in db.execute('SELECT RequirementId FROM RequirementSetRequirements WHERE RequirementSetId=?', (key,))]
        return any(values) if mode == 'REQUIREMENTSET_TEST_ANY' else all(values)

    # COLLECTION_PLAYER_IMPROVEMENTS contains only owned, improved plots.
    if not owned or not improvement:
        return 0
    total = 0
    roots = list(db.execute('SELECT ModifierId FROM BuildingModifiers WHERE BuildingType=?', (building,)))
    for (root,) in roots:
        child = args('ModifierArguments', 'ModifierId', root).get('ModifierId')
        if not child:
            continue
        row = db.execute('SELECT ModifierType,OwnerRequirementSetId,SubjectRequirementSetId FROM Modifiers WHERE ModifierId=?', (child,)).fetchone()
        if not row or row[0] != 'MODIFIER_SINGLE_PLOT_ADJUST_PLOT_YIELDS':
            continue
        root_type, owner_gate, subject_gate = db.execute('SELECT ModifierType,OwnerRequirementSetId,SubjectRequirementSetId FROM Modifiers WHERE ModifierId=?', (root,)).fetchone()
        if root_type != 'MODIFIER_CSC_PLAYER_IMPROVEMENTS_ATTACH_MODIFIER':
            raise ValueError('Material graph must select owned improvements')
        a = args('ModifierArguments', 'ModifierId', child)
        if a.get('YieldType') == yield_type and requirement_set(owner_gate) and requirement_set(subject_gate) and requirement_set(row[1]) and requirement_set(row[2]):
            total += float(a['Amount'])
    return total


def validate_material_returns(db, cases):
    failures = []
    selection = db.execute("SELECT CollectionType,EffectType FROM DynamicModifiers WHERE ModifierType='MODIFIER_CSC_PLAYER_IMPROVEMENTS_ATTACH_MODIFIER'").fetchone()
    if selection != ('COLLECTION_PLAYER_IMPROVEMENTS', 'EFFECT_ATTACH_MODIFIER'):
        failures.append('Material attachments must select owned improvements')
    for building, resource, totals in cases:
        for improvement, expected in zip(('IMPROVEMENT_PLANTATION', 'IMPROVEMENT_INDUSTRY', 'IMPROVEMENT_CORPORATION'), totals):
            if not db.execute('SELECT 1 FROM Improvements WHERE ImprovementType=?', (improvement,)).fetchone():
                continue
            for yield_type in ('YIELD_PRODUCTION', 'YIELD_GOLD'):
                actual = material_total(db, building, resource, improvement, yield_type)
                if abs(actual - expected) > .00001:
                    failures.append(f'{building} {resource} {improvement} {yield_type}: expected total {expected}, delivered {actual}')
                for context in ({'adjacent': False}, {'owned': False}):
                    if material_total(db, building, resource, improvement, yield_type, **context):
                        failures.append(f'{building}: ineligible material must receive zero: {context}')
    return failures


def validate_mechanism_bindings(db, implementation, phase):
    """A declared mechanism must own the actual active graphs, not just a note."""
    failures = []
    bindings = implementation.get('mechanism_bindings', {})
    if bindings.get('ownership_refresh', {}).get('native_event') != 'CityTileOwnershipChanged':
        failures.append('Contract must bind ownership refresh to the real native event')
    if phase == 'foundation':
        return failures
    material = bindings.get('material_producer_returns', {})
    if material.get('implementation') != 'bakers_modifier_pattern':
        failures.append('Contract must declare the existing Bakers material-return pattern')
    if set(material.get('participants', [])) != {'BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP', 'BUILDING_CSC_TAILORS_FASHION_HOUSE'}:
        failures.append('Material contract must cover both Base and Specialty producers')
    if material.get('tier_totals') != [1, 2, 3] or set(material.get('yields', [])) != {'YIELD_PRODUCTION', 'YIELD_GOLD'}:
        failures.append('Material contract must specify complete 1/2/3 Production and Gold totals')
    failures.extend(validate_material_returns(db, [
        ('BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP', 'RESOURCE_COTTON', tuple(material.get('tier_totals', (1,2,3)))),
        ('BUILDING_CSC_TAILORS_FASHION_HOUSE', 'RESOURCE_DYES', tuple(material.get('tier_totals', (1,2,3)))),
    ]))
    notifications = bindings.get('service_notifications', {})
    if notifications.get('implementation') != 'shared_notifications_handler' or notifications.get('cache_keys') != 'live_strings_or_serialized_hashes':
        failures.append('Contract must bind Services to the shared save-compatible notification handler')
    if phase in ('stage3', 'stage4'):
        customer = bindings.get('customer_population_sales', {})
        if customer.get('registry') != 'CSC_Stage3CustomerTransactions' or customer.get('customer_delivery') != 'customer_owned_property_bits':
            failures.append('Contract must declare immediate customer-owned population delivery')
        actual = {r[0] for r in db.execute("SELECT TransactionId FROM CSC_Stage3CustomerTransactions WHERE TransactionId LIKE 'CSC_TAILORS_%'")}
        if set(customer.get('participants', [])) != actual:
            failures.append('Customer population participants differ from the contract')
    return failures


def validate_customer_delivery(db):
    failures = []
    bits = [r[0] for r in db.execute('SELECT Bit FROM CSC_ScaledAmountBits')]
    for family in ('MARKET', 'TEMPLE'):
        prop = f'CSC_TAILORS_STAGE_3_{family}_CULTURE_AMOUNT'
        row = db.execute('SELECT CustomerYieldAmountProperty FROM CSC_Stage3CustomerTransactions WHERE TransactionId=?', ('CSC_TAILORS_TAILOR_' + family,)).fetchone()
        if row != (prop,):
            failures.append(f'{family}: customer-owned property delivery is required')
        for bit in bits:
            modifier = f'MOD_CSC_TAILORS_{family}_CUSTOMER_CULTURE_BIT_{bit}'
            row = db.execute('SELECT M.ModifierType,M.OwnerRequirementSetId FROM Modifiers M JOIN DistrictModifiers D ON D.ModifierId=M.ModifierId WHERE D.DistrictType=? AND M.ModifierId=?', ('DISTRICT_CITY_CENTER', modifier)).fetchone()
            if row != ('MODIFIER_SINGLE_CITY_ADJUST_CITY_YIELD_PER_POPULATION', None):
                failures.append(f'{modifier}: customer centre must own an ungated population effect')
                continue
            args = dict(db.execute('SELECT Name,Value FROM ModifierArguments WHERE ModifierId=?', (modifier,)))
            if args.get('YieldType') != 'YIELD_CULTURE' or abs(float(args.get('Amount', -1)) - bit / 10000) > 1e-8:
                failures.append(f'{modifier}: wrong Culture amount')
            requirements = list(db.execute('SELECT A.Name,A.Value FROM Modifiers M JOIN RequirementSetRequirements S ON S.RequirementSetId=M.SubjectRequirementSetId JOIN Requirements R ON R.RequirementId=S.RequirementId JOIN RequirementArguments A ON A.RequirementId=R.RequirementId WHERE M.ModifierId=? AND R.RequirementType=?', (modifier, 'REQUIREMENT_PLOT_PROPERTY_MATCHES')))
            if dict(requirements) != {'PropertyName': prop + '_BIT_' + str(bit), 'PropertyMinimum': '1'}:
                failures.append(f'{modifier}: property-bit activation graph is incomplete')
    old = db.execute("SELECT COUNT(*) FROM BuildingModifiers WHERE ModifierId IN ('MOD_CSC_TAILORS_TAILOR_ATTACH_MARKET','MOD_CSC_TAILORS_TAILOR_ATTACH_TEMPLE')").fetchone()[0]
    if old:
        failures.append('Direct seller-owned Culture attachments duplicate or defer customer delivery')
    return failures


def validate_ownership_event(gameplay):
    event_list = re.search(r'for _,name in ipairs\(\{(.*?)\}\)', gameplay, re.S)
    names = re.findall(r"'([^']+)'", event_list[1]) if event_list else []
    if 'CityTileOwnershipChanged' not in names or 'PlotOwnershipChanged' in names:
        return ['Ownership refresh must subscribe to CityTileOwnershipChanged']
    return []


def validate_qa_regressions(root: Path, db, phase):
    gameplay = (root / 'Civ Supply Chains/Lua_UI/Adjacencies/CSC_AdjacencyGameplay.lua').read_text(encoding='utf-8')
    failures = validate_ownership_event(gameplay)
    if phase != 'foundation':
        failures.extend(validate_material_returns(db, [
            ('BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP', 'RESOURCE_COTTON', (1, 2, 3)),
            ('BUILDING_CSC_TAILORS_FASHION_HOUSE', 'RESOURCE_DYES', (1, 2, 3)),
            ('BUILDING_CSC_BAKERS_WATER_MILL', 'RESOURCE_WHEAT', (1, 2, 3)),
            ('BUILDING_CSC_BAKERS_WIND_MILL', 'RESOURCE_WHEAT', (1, 2, 3)),
            ('BUILDING_CSC_BAKERS_CAFE', 'RESOURCE_COFFEE', (1, 2, 3)),
        ]))
        try:
            from lupa import LuaRuntime
            lua = LuaRuntime(unpack_returned_tuples=True)
            fixture = root / 'project/tools/quarter_contracts/tests/fixtures/notification_cache_world.lua'
            lua.execute(fixture.read_text())
            source = (root / 'Civ Supply Chains/Lua_UI/Notifications_Suk_MCUIS/CSC_UI_Notifications.lua').read_text()
            lua.execute(re.sub(r'\s*:\s*(?:number|table|string|boolean)\b', '', source))
            lua.globals().TestNotificationCache()
        except Exception as error:
            failures.append('Saved notification cache regression: ' + str(error))
    return failures
