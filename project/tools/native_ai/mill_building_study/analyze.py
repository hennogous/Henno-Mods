"""Offline accounting of a frozen mill-building-study-v1 capture.

No game interfaces are imported. Native source contracts and the limits of each
derived number are stated in the output; source-world gates are not callbacks.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import re
import struct

PROFILE = 'mill-building-study-v1'
KINDS = ('BuildingValue', 'ModifierValue', 'AnalyzeModifier', 'BaseYield',
         'AmenityValue', 'CalculateDistrictValues')
OWN_MODIFIER_RETURN = 0x52c955
OWN_AMENITY_RETURNS = {0x52c422, 0x52c4cb}
INVALID_VALUE = -2559744
LIMITS = dict(maxPairs=16384, maxCallbacks=300000, maxThreads=8,
              maxDepth=16, maxRows=37, maxModifierName=256)
MILL_RULES = {'BUILDING_CSC_BAKERS_WIND_MILL': 'CSC_BAKERS_WIND_MILL_PRODUCTION_FROM_HILLS',
              'BUILDING_CSC_BAKERS_WATER_MILL': 'CSC_BAKERS_WATER_MILL_PRODUCTION_FROM_RIVER'}


def i32(n):
    return (int(n) + 2**31) % 2**32 - 2**31


def restore_q8(whole, yield_index, defaults):
    """ModifierValue's signed integer conversion, not a gameplay-yield total."""
    if yield_index == -1:
        return max(-0x7fffff, min(0x7fffff, whole)) * 256
    value = defaults[yield_index]
    value = struct.unpack('<f', struct.pack('<f', value))[0]
    if not math.isfinite(value):
        raise ValueError('nonfinite Yield.DefaultValue')
    floor = math.floor(value)
    default_q8 = i32((floor << 8) | (int((value - floor) * 256) & 255))
    return i32((default_q8 * i32(whole << 8)) >> 8)


def expand_metadata(world):
    """Decode only the documented one-based dictionary, rejecting bad cells."""
    strings = world.get('databaseStrings', [])
    result = {}
    for name, table in world.get('metadata', {}).items():
        if isinstance(table, list):
            result[name] = table
            continue
        columns = table['columns']
        if len(columns) != len(set(columns)):
            raise ValueError('duplicate metadata columns: ' + name)
        rows = []
        for cells in table['rows']:
            if len(cells) != len(columns):
                raise ValueError('metadata row width: ' + name)
            row = {}
            for key, value in zip(columns, cells):
                if isinstance(value, dict):
                    if set(value) != {'s'} or type(value['s']) is not int or not 1 <= value['s'] <= len(strings):
                        raise ValueError('metadata dictionary reference: ' + name)
                    value = strings[value['s'] - 1]
                if value != table.get('absent', 'ABSENT'):
                    row[key] = value
            rows.append(row)
        result[name] = rows
    return result


def identity(record):
    w = record['entry']['identity']
    return w['player'], w['city']


def inside(a, b):
    return a['entrySequence'] < b['entrySequence'] < b['leave']['sequence'] < a['leave']['sequence']


def address(value):
    return int(value, 16) if isinstance(value, str) else int(value)


def own_call(record, kind):
    try:
        rva = address(record.get('callerRva'))
    except (ValueError, TypeError):
        return False
    return rva == OWN_MODIFIER_RETURN if kind == 'ModifierValue' else rva in OWN_AMENITY_RETURNS


def native_bool(value):
    return value is True or value == 1


def signed32(value):
    return type(value) is int and -2**31 <= value < 2**31


def validate_cache(cache, cfg):
    """Validate serialized bounded payloads independently of callback guards."""
    rows = cache['rows']
    if type(rows) is not int or not 0 <= rows <= cfg['maxRows']:
        raise ValueError('cache row bound')
    if rows == 0:
        if cache['status'] != 'unready' or any(cache[k] for k in ('rawBuildingQ8','mutableBuildingQ8','districtRows')):
            raise ValueError('unready cache contains data')
        return
    if cache['status'] != 'observed' or len(cache['districtRows']) != rows:
        raise ValueError('observed cache row count')
    family = [(b['index'], b['type']) for b in cfg['buildings']]
    for key in ('rawBuildingQ8', 'mutableBuildingQ8'):
        vector = cache[key]
        if [(b['index'], b['type']) for b in vector] != family or any(not signed32(b['value']) for b in vector):
            raise ValueError('cache family vector mismatch')
    if (cache['mutableDistrictLength'] != rows * cfg['districtCount'] or
            not cache['mutableDistrictLength'] <= cache['mutableDistrictCapacity'] <= 37 * 4096):
        raise ValueError('cache district matrix bounds')
    for number, row in enumerate(cache['districtRows']):
        if (row['row'] != number or not 0 <= row['x'] < cfg['mapWidth'] or not 0 <= row['y'] < cfg['mapHeight'] or
                row['plot'] != row['y'] * cfg['mapWidth'] + row['x']):
            raise ValueError('cache row geometry')
        for key in ('districtValues', 'mutableDistrictValues'):
            if ([d['district'] for d in row[key]] != cfg['districtIndices'] or
                    any(not signed32(d['value']) for d in row[key])):
                raise ValueError('cache two-district values')
        if row['rawAliasesMutable'] != (row['rawPointer'] == row['mutableRowPointer']):
            raise ValueError('cache district alias receipt')
    if cache['rawAliasesMutable'] != (cache['rawPointer'] == cache['mutablePointer']):
        raise ValueError('cache building alias receipt')


def audit(trace, world, db):
    errors, warnings = [], []
    cfg = trace.get('config', {})
    def require(condition, message):
        if not condition:
            errors.append(message)
    require(trace.get('profile') == PROFILE and world.get('profile') == PROFILE, 'profile mismatch')
    require(trace.get('read_only') is True and world.get('readOnly') is True, 'read-only receipt missing')
    require(trace.get('frozen') is True and trace.get('started') is True and trace.get('enabled') is False,
            'capture is not a closed frozen window')
    require(not trace.get('pendingPairs') and not trace.get('pendingFrames'), 'native frames remain pending')
    require(not trace.get('stopReason') and not trace.get('faults') and not trace.get('stats', {}).get('errors'),
            'fault or budget stop makes capture incomplete')
    require(cfg == world.get('observerConfig'), 'source-world/observer config mismatch')
    require(all(cfg.get(k) == v for k, v in LIMITS.items()), 'unreviewed capture limits')
    records = trace.get('records', [])
    stats = trace.get('stats', {})
    require(stats.get('acceptedPairs') == stats.get('completedPairs') == len(records), 'pair totals mismatch')
    require(len(records) <= LIMITS['maxPairs'] and stats.get('callbacks', 0) <= LIMITS['maxCallbacks'], 'budget exceeded')
    require(len({r.get('thread') for r in records}) <= LIMITS['maxThreads'], 'thread bound exceeded')
    targets = {(t['player'], t['city']) for t in cfg.get('targets', [])}
    require(len(targets) == 2 and {p for p, _ in targets} == {1, 2}, 'target allowlist mismatch')
    require({(t['player'], t['city']) for t in world.get('targets', [])} == targets and
            all(t.get('exists') is True and t.get('human') is False for t in world.get('targets', [])),
            'source target existence/human identity receipt mismatch')
    family = {b['Index']: b['BuildingType'] for b in db.get('buildings', [])}
    require(len(family) == 19 and family == {b['index']: b['type'] for b in cfg.get('buildings', [])},
            'nineteen-building mapping mismatch')
    require(world.get('mapping', {}).get('family') == cfg.get('buildings'), 'world native index mapping mismatch')
    require(sorted(q['index'] for q in world.get('mapping', {}).get('quarters', [])) == sorted(cfg.get('districtIndices', [])),
            'two-district mapping mismatch')
    ids, sequences = {}, set()
    for r in records:
        rid = r.get('id')
        require(type(rid) is int and rid > 0 and rid not in ids, 'duplicate/invalid record id: ' + str(rid))
        ids[rid] = r
        require(r.get('kind') in KINDS, 'unknown record kind: ' + str(r.get('kind')))
        leave = r.get('leave', {})
        for seq in (r.get('entrySequence'), leave.get('sequence')):
            require(type(seq) is int and seq > 0 and seq not in sequences, 'duplicate/invalid sequence: ' + str(seq))
            sequences.add(seq)
        require(type(r.get('entrySequence')) is int and type(leave.get('sequence')) is int and
                r['entrySequence'] < leave['sequence'], 'invalid interval: ' + str(rid))
        require(not leave.get('incompleteReason') and not leave.get('captureMayBeIncomplete'), 'incomplete pair: ' + str(rid))
        try:
            require(identity(r) in targets, 'root identity outside target: ' + str(rid))
            if r['kind'] == 'BuildingValue':
                e = r['entry']
                require(family.get(e['building']) == e['buildingType'], 'building index/name mismatch: ' + str(rid))
            if r['kind'] in ('BuildingValue', 'ModifierValue', 'AmenityValue'):
                require(type(leave.get('valueQ8')) is int and -2**31 <= leave['valueQ8'] < 2**31,
                        'missing/signed output: ' + str(rid))
            if r['kind'] == 'CalculateDistrictValues':
                require(r['entry']['identity'] == leave['identity'], 'calculation city identity changed: ' + str(rid))
                validate_cache(r['entry']['cache'], cfg)
                validate_cache(leave['cache'], cfg)
            if 'analysis' in r['entry']:
                before, after = r['entry']['analysis'], leave.get('analysis', r['entry']['analysis'])
                require(before['pointer'] == after['pointer'], 'analysis pointer changed: ' + str(rid))
                if r['kind'] in ('BaseYield', 'AnalyzeModifier'):
                    require(leave.get('accumulatorDelta') == after['accumulator'] - before['accumulator'],
                            'accumulator delta mismatch: ' + str(rid))
            if r['kind'] == 'AnalyzeModifier':
                m = r['entry']['modifier']
                require(type(m['name']) is str and 0 <= len(m['name']) <= cfg['maxModifierName'] and
                        m['nameSize'] == len(m['name']) and m['nameCapacity'] >= m['nameSize'] and
                        m['nameCapacity'] <= 4096 and all(32 <= ord(c) < 127 for c in m['name']), 'modifier string contract: ' + str(rid))
                require(leave.get('accepted') in (0, 1), 'invalid analyzer Boolean: ' + str(rid))
            if r['kind'] == 'ModifierValue':
                require(type(r['entry']['modifierCount']) is int and 0 <= r['entry']['modifierCount'] <= 4096,
                        'compiled modifier bound: ' + str(rid))
        except (KeyError, TypeError, ValueError) as exc:
            errors.append('malformed record ' + str(rid) + ': ' + str(exc))
    children = {}
    for r in records:
        parent_id = r.get('parentId')
        if parent_id is not None:
            parent = ids.get(parent_id)
            require(parent is not None, 'missing parent: ' + str(r['id']))
            if parent:
                require(parent['thread'] == r['thread'] and inside(parent, r), 'parent/thread/interval mismatch: ' + str(r['id']))
                children.setdefault(parent_id, []).append(r)
        if r['kind'] not in ('BuildingValue', 'CalculateDistrictValues'):
            root = ids.get(r['entry'].get('buildingCallId'))
            require(root is not None and root['kind'] == 'BuildingValue', 'missing building root: ' + str(r['id']))
            if root:
                require(inside(root, r) and root['thread'] == r['thread'] and
                        r['entry']['identity'] == root['entry']['identity'] and
                        r['entry']['building'] == root['entry']['building'], 'building attribution mismatch: ' + str(r['id']))
                require(parent_id is not None, 'component lacks captured building ancestry: ' + str(r['id']))
    for thread in {r['thread'] for r in records}:
        active = []
        for r in sorted((r for r in records if r['thread'] == thread), key=lambda x: x['entrySequence']):
            while active and active[-1]['leave']['sequence'] < r['entrySequence']:
                active.pop()
            if active:
                require(inside(active[-1], r), 'crossing native intervals: ' + str(r['id']))
                if r['kind'] not in ('BuildingValue', 'CalculateDistrictValues'):
                    require(r['parentId'] == active[-1]['id'], 'nearest paired parent mismatch: ' + str(r['id']))
            active.append(r)
            require(len(active) <= LIMITS['maxDepth'], 'recorded depth bound exceeded')
    for kind in KINDS:
        observed = sum(r['kind'] == kind for r in records)
        count = trace.get('counts', {}).get(kind, {})
        require(count.get('accepted') == observed and count.get('entries', -1) >= observed, 'kind totals mismatch: ' + kind)
    for r in records:
        if r['kind'] == 'ModifierValue':
            direct = sorted((c for c in children.get(r['id'], []) if c['kind'] == 'AnalyzeModifier'), key=lambda c: c['entrySequence'])
            require(len(direct) == r['entry']['modifierCount'], 'compiled inventory count mismatch: ' + str(r['id']))
            for ordinal, child in enumerate(direct):
                try:
                    require(address(child['entry']['modifier']['pointer']) == address(r['entry']['descriptorBase']) + ordinal * 64,
                            'compiled descriptor stride mismatch: ' + str(child['id']))
                except (TypeError, ValueError):
                    errors.append('invalid descriptor address: ' + str(child['id']))
    if not records:
        warnings.append('No callbacks observed: source and capture integrity alone do not demonstrate coverage.')
    return errors, warnings, ids, children


def first_chain(name, prerequisites):
    chain, seen = [], {name}
    while prerequisites.get(name):
        parent = prerequisites[name][0]['prerequisite']
        chain.append(parent)
        if parent in seen:
            return chain, 'cycle'
        seen.add(parent)
        name = parent
    return chain, 'known_selected_child_rows_only'


def analyze(trace, world):
    try:
        return _analyze(trace, world)
    except (KeyError, TypeError, ValueError, OverflowError) as exc:
        return {'schema': 1, 'profile': PROFILE, 'ok': False, 'errors': ['malformed input contract: ' + str(exc)],
                'warnings': [], 'accounting': 'withheld_on_integrity_failure'}


def _analyze(trace, world):
    try:
        db = expand_metadata(world)
    except (KeyError, TypeError, ValueError) as exc:
        return {'schema': 1, 'ok': False, 'errors': ['metadata decode: ' + str(exc)], 'warnings': []}
    errors, warnings, ids, children = audit(trace, world, db)
    # Malformed native records cannot safely support arithmetic. Keep the audit
    # failures reviewable instead of attempting a plausible partial total.
    if errors:
        return {'schema': 1, 'profile': PROFILE, 'ok': False, 'errors': errors, 'warnings': warnings,
                'record_count': len(trace.get('records', [])), 'accounting': 'withheld_on_integrity_failure'}
    records = sorted(trace['records'], key=lambda r: r['entrySequence'])
    definitions = {r['BuildingType']: r for r in db['buildings']}
    by_index = {r['Index']: r for r in db['buildings']}
    modifiers = {r['ModifierId']: r for r in db.get('modifiers', [])}
    arguments, roots, prerequisites = {}, {}, {}
    for row in db.get('modifierArguments', []):
        arguments.setdefault(row['ModifierId'], {})[row['Name']] = row['Value']
    for row in db.get('buildingRoots', []):
        roots.setdefault(row['building'], set()).add(row['modifier'])
    for row in sorted(db.get('prerequisites', []), key=lambda row: row['ordinal']):
        prerequisites.setdefault(row['building'], []).append(row)
    defaults = {r['index']: r['defaultValue'] for r in world.get('yields', [])}
    modifier_calls, modifier_values = [], []
    restored = {}
    observed_own = {}
    for r in records:
        if r['kind'] != 'AnalyzeModifier':
            continue
        entry, leave = r['entry'], r['leave']
        name = entry['modifier']['name']
        source = modifiers.get(name)
        parent = ids.get(r['parentId'])
        own_root = bool(parent and parent['kind'] == 'ModifierValue' and own_call(parent, 'ModifierValue'))
        building_type = by_index[entry['building']]['BuildingType']
        if own_root:
            observed_own.setdefault(building_type, set()).add(name)
            if name not in roots.get(building_type, set()):
                errors.append('own building compiled root is not an active BuildingModifiers row: ' + name)
        if parent and parent['kind'] == 'AnalyzeModifier':
            outer_name = parent['entry']['modifier']['name']
            attached = arguments.get(outer_name, {}).get('ModifierId')
            if attached is not None and attached != name:
                errors.append('Attach child ID disagrees with source: ' + str(r['id']))
        after = leave['analysis']
        value = 0 if leave['accepted'] == 0 else None
        if leave['accepted']:
            try:
                value = restore_q8(after['accumulator'], after['yieldIndex'], defaults)
            except (KeyError, ValueError, OverflowError) as exc:
                errors.append('cannot restore modifier Q8 ' + str(r['id']) + ': ' + str(exc))
        restored[r['id']] = value
        runtime = entry['modifier']
        if source and 'subjectRequirementHash' in source and (int(source['subjectRequirementHash']) & 0xffffffff) != runtime['subjectRequirementHash']:
            errors.append('compiled subject requirement hash differs from source: ' + name)
        modifier_calls.append({'id': r['id'], 'parent_id': r['parentId'], 'building_call_id': entry['buildingCallId'],
            'thread': r['thread'], 'entry_sequence': r['entrySequence'], 'leave_sequence': leave['sequence'],
            'player': identity(r)[0], 'city': identity(r)[1], 'building': entry['building'],
            'building_type': building_type, 'modifier': name, 'source_found': source is not None,
            'source_effect': source.get('EffectType') if source else None,
            'source_collection': source.get('CollectionType') if source else None,
            'owner_requirements': source.get('OwnerRequirementSetId') if source else None,
            'subject_requirements': source.get('SubjectRequirementSetId') if source else None,
            'arguments': arguments.get(name, {}), 'runtime_descriptor': runtime,
            'own_building_root': own_root, 'accepted': leave['accepted'],
            'outcome': 'analyzer_returned_false' if not leave['accepted'] else ('accepted_zero' if value == 0 else 'accepted_nonzero'),
            'before_context': entry['analysis'], 'after_context': after,
            'accumulator_delta': leave['accumulatorDelta'], 'whole_utility_after': after['accumulator'],
            'restored_q8': value, 'consumed_by_modifier_value': bool(parent and parent['kind'] == 'ModifierValue'),
            'base_yield_callbacks': [c['id'] for c in children.get(r['id'], []) if c['kind'] == 'BaseYield'],
            'interpretation': 'accepted is native analyzer outcome; owner gates and economic benefit are not certified'})
    for r in records:
        if r['kind'] != 'ModifierValue':
            continue
        direct = [c for c in children.get(r['id'], []) if c['kind'] == 'AnalyzeModifier']
        values = [restored.get(c['id']) for c in direct]
        derived = i32(sum(values)) if all(v is not None for v in values) else None
        match = derived == r['leave']['valueQ8'] if derived is not None else None
        if match is False:
            errors.append('ModifierValue direct-root restoration mismatch: ' + str(r['id']))
        modifier_values.append({'id': r['id'], 'building_call_id': r['entry']['buildingCallId'],
            'own_building_callsite': own_call(r, 'ModifierValue'), 'caller_rva': r['callerRva'],
            'compiled_count': r['entry']['modifierCount'], 'direct_analyzers': [c['id'] for c in direct],
            'derived_q8': derived, 'value_q8': r['leave']['valueQ8'], 'matches': match})
    components = []
    for r in records:
        if r['kind'] != 'BuildingValue':
            continue
        e = r['entry']; definition = by_index[e['building']]
        direct = children.get(r['id'], [])
        own_mod = [c for c in direct if c['kind'] == 'ModifierValue' and own_call(c, 'ModifierValue')]
        own_amenity = [c for c in direct if c['kind'] == 'AmenityValue' and own_call(c, 'AmenityValue')]
        mod_value = i32(sum(c['leave']['valueQ8'] for c in own_mod))
        amenity_raw = i32(sum(c['leave']['valueQ8'] for c in own_amenity))
        amenity_value = min(amenity_raw, 0x3200) if definition.get('RegionalRange', 0) >= 2 else amenity_raw
        chain, chain_status = first_chain(e['buildingType'], prerequisites)
        if chain and chain[-1] not in definitions:
            chain_status = 'parent_outside_selected_metadata'
        value = r['leave']['valueQ8']; valid = value > INVALID_VALUE
        components.append({'id': r['id'], 'thread': r['thread'], 'player': identity(r)[0], 'city': identity(r)[1],
            'building': e['building'], 'type': e['buildingType'], 'must_purchase': native_bool(definition.get('MustPurchase')),
            'coordinates': e['coordinates'], 'ready': e['ready'], 'horizon': e['horizon'], 'discount_q8': e['discountQ8'],
            'entry_sequence': r['entrySequence'], 'leave_sequence': r['leave']['sequence'],
            'value_q8': value, 'is_native_invalid_sentinel': not valid,
            'own_modifier_call_ids': [c['id'] for c in own_mod], 'own_modifier_q8': mod_value,
            'direct_amenity_call_ids': [c['id'] for c in own_amenity], 'direct_amenity_raw_q8': amenity_raw,
            'direct_amenity_consumed_q8': amenity_value,
            'unattributed_native_remainder_q8': i32(value - mod_value - amenity_value) if valid else None,
            'other_subroute_helper_ids': [c['id'] for c in direct if c['kind'] in ('ModifierValue', 'AmenityValue')
                                         and c not in own_mod and c not in own_amenity],
            'first_prerequisite_chain': chain, 'first_prerequisite_chain_status': chain_status,
            'earlier_income_depth_multiplier': len(chain) * 2 + 1 if chain_status == 'known_selected_child_rows_only' else None,
            'depth_multiplier_scope': 'earlier income subtotal only; not the later modifier or amenity subtotal',
            'specialist_rows': [s for s in db.get('specialists', []) if s['BuildingType'] == e['buildingType']],
            'residual_scope': 'not an attribution to specialists, maintenance, transactions, or real economic benefit'})
    base_yields = [{'id': r['id'], 'parent_id': r['parentId'], 'building_call_id': r['entry']['buildingCallId'],
        'amount': r['entry']['amount'], 'effect_yield_index': r['entry']['effectYieldIndex'],
        'before_context': r['entry']['analysis'], 'after_context': r['leave']['analysis'],
        'accumulator_delta': r['leave']['accumulatorDelta']} for r in records if r['kind'] == 'BaseYield']
    aggregates = aggregation(records, world, db, components, warnings)
    mills = mill_inventory(db, modifier_calls)
    cache_seen = {x['type'] for r in records if r['kind'] == 'CalculateDistrictValues'
                  for x in r['entry']['cache'].get('rawBuildingQ8', [])}
    coverage = []
    for name, d in sorted(definitions.items(), key=lambda item: item[1]['Index']):
        active = roots.get(name, set()); seen = observed_own.get(name, set())
        coverage.append({'type': name, 'index': d['Index'], 'must_purchase': native_bool(d.get('MustPurchase')),
            'building_call_count': sum(c['type'] == name for c in components), 'seen_in_raw_cache': name in cache_seen,
            'active_root_count': len(active), 'observed_own_roots': sorted(seen), 'unobserved_active_roots': sorted(active - seen),
            'unobserved_meaning': 'not reached in this bounded window; no unsupported claim'})
    return {'schema': 1, 'profile': PROFILE, 'ok': not errors, 'errors': errors, 'warnings': warnings,
        'integrity_complete': True, 'modifier_accounting_complete': not errors,
        'source_state_aggregation_complete': bool(aggregates) and all(a.get('districts') and all(d['status'] == 'exact_source_state_aggregation_match' for d in a['districts']) for a in aggregates),
        'record_count': len(records), 'pointer_assurance': 'in-callback exact return-output pointer guards passed; raw output pointers were not serialized',
        'arithmetic_units': 'Q8 native utility; whole accumulator values are converted with loaded Yield.DefaultValue, not gameplay yields',
        'modifier_values': modifier_values, 'modifier_calls': modifier_calls, 'base_yield_calls': base_yields,
        'building_components': components, 'district_aggregations': aggregates, 'mill_inventory': mills,
        'coverage': coverage, 'source_turn': world.get('turn'),
        'limits': ['Source-world presence and pillage gates are not simultaneous native callback receipts.',
                   'Nested Attach results are overwritten/assigned; only direct Analyze roots enter each ModifierValue sum.',
                   'CityCenter-owned population/export consumers outside producer BuildingModifiers are out of scope.',
                   'Specialist rows are source metadata only; the remaining native subtotal is unattributed.',
                   'No gameplay yields, site selection, construction, or economic benefit are proven by this capture.']}


def aggregation(records, world, db, components, warnings):
    defs = {d['BuildingType']: d for d in db['buildings']}
    targets = {(t['player'], t['city']): t for t in world.get('targets', [])}
    quarters = {q['type']: q['index'] for q in world['mapping']['quarters']}
    out = []
    for r in records:
        if r['kind'] != 'CalculateDistrictValues':
            continue
        before, after = r['entry']['cache'], r['leave']['cache']
        item = {'id': r['id'], 'player': identity(r)[0], 'city': identity(r)[1], 'districts': [],
                'gate_scope': 'derived from source-world state; not a live gate observation',
                'raw_and_mutable_bindings_retained': True}
        out.append(item)
        if before.get('status') != 'observed' or after.get('status') != 'observed':
            item['status'] = 'cache_unready'; continue
        source = targets.get(identity(r), {})
        present = {b['type']: b['present'] for b in source.get('buildings', [])}
        raw = {b['type']: b['value'] for b in before['rawBuildingQ8']}
        raw_after = {b['type']: b['value'] for b in after['rawBuildingQ8']}
        item['raw_building_before_q8'] = raw; item['raw_building_after_q8'] = raw_after
        before_rows, after_rows = before['districtRows'], after['districtRows']
        if [(x['row'], x['plot']) for x in before_rows] != [(x['row'], x['plot']) for x in after_rows]:
            item['status'] = 'row_identity_changed'; warnings.append('Calculation ' + str(r['id']) + ': district row geometry changed'); continue
        for district, index in quarters.items():
            rules, total, unknown = [], 0, False
            city_districts = [d for d in source.get('districts', []) if d['type'] == district]
            city_gate = not city_districts or all(d.get('pillaged') is True for d in city_districts)
            if any(not isinstance(d.get('pillaged'), bool) for d in city_districts):
                unknown = True
            for name, d in sorted(defs.items(), key=lambda pair: pair[1]['Index']):
                if d.get('PrereqDistrict') != district:
                    continue
                reasons = []
                value = raw.get(name)
                if value is None: reasons.append('raw_input_unobserved'); unknown = True
                elif value <= 0: reasons.append('nonpositive_raw')
                if native_bool(d.get('MustPurchase')): reasons.append('must_purchase')
                if not city_gate: reasons.append('city_has_unpillaged_district')
                for ex in db.get('mutualExclusions', []):
                    if ex['Building'] != name: continue
                    other_name = ex['MutuallyExclusiveBuilding']; other = defs.get(other_name)
                    if present.get(other_name) is True: reasons.append('excluded_building_present:' + other_name)
                    elif other is None: reasons.append('excluded_index_unobserved:' + other_name); unknown = True
                    elif other['Index'] < d['Index']: reasons.append('lower_index_mutual_canonical:' + other_name)
                    elif other_name not in present: unknown = True
                admitted = not reasons
                if admitted: total = i32(total + value)
                prior = [c for c in components if (c['player'], c['city']) == identity(r) and c['type'] == name and c['leave_sequence'] < r['entrySequence']]
                latest = max(prior, key=lambda c: c['leave_sequence']) if prior else None
                rules.append({'type': name, 'index': d['Index'], 'raw_q8': value, 'admitted_by_source_gates': admitted,
                    'reasons': reasons, 'latest_building_call_id': latest['id'] if latest else None,
                    'latest_value_matches_raw': latest['value_q8'] == value if latest else None})
            rows = []
            for a, b in zip(before_rows, after_rows):
                av = {v['district']: v['value'] for v in a['mutableDistrictValues']}[index]
                bv = {v['district']: v['value'] for v in b['mutableDistrictValues']}[index]
                expected = (total if a['row'] == 0 else i32(av + total)) if total and av > 0 else av
                rows.append({'row': a['row'], 'plot': a['plot'], 'before_q8': av, 'after_q8': bv,
                    'delta_q8': bv - av, 'source_derived_after_q8': None if unknown else expected,
                    'matches': None if unknown else bv == expected,
                    'raw_before_q8': {v['district']: v['value'] for v in a['districtValues']}[index],
                    'raw_after_q8': {v['district']: v['value'] for v in b['districtValues']}[index],
                    'raw_aliases_mutable_before': a['rawAliasesMutable'], 'raw_aliases_mutable_after': b['rawAliasesMutable']})
            exact = not unknown and all(row['matches'] for row in rows)
            item['districts'].append({'type': district, 'index': index, 'source_gate_unknown': unknown,
                'source_derived_sum_q8': None if unknown else total, 'buildings': rules, 'rows': rows,
                'status': 'exact_source_state_aggregation_match' if exact else 'source_state_mismatch_or_unknown'})
            if not exact:
                warnings.append('Calculation ' + str(r['id']) + ' ' + district + ': source-state gates or arithmetic do not fully reconcile; preserve actual mutable deltas.')
        # Reverse prerequisite propagation is a separate mutation from the raw
        # family sum. Dependencies outside this selected family remain unknown.
        predicted = {b['type']: b['value'] for b in before['mutableBuildingQ8']}
        observed = {b['type']: b['value'] for b in after['mutableBuildingQ8']}
        dependencies = {}
        for p in db.get('prerequisites', []):
            dependencies.setdefault(p['prerequisite'], []).append(p['building'])
        for name, d in sorted(defs.items(), key=lambda pair: pair[1]['Index']):
            if native_bool(d.get('RequiresPlacement')): continue
            for child in sorted(dependencies.get(name, []), key=lambda n: defs[n]['Index']):
                if predicted.get(child, 0) > 0:
                    predicted[name] = i32(predicted[name] + predicted[child])
        item['dependent_vector'] = {'scope': 'selected-family dependencies only; unselected dependent definitions are not inventoried',
            'source_derived_after_q8': predicted, 'observed_after_q8': observed, 'selected_family_matches': predicted == observed}
        if predicted != observed: warnings.append('Calculation ' + str(r['id']) + ': selected-family dependent vector does not fully reconcile.')
        item['status'] = 'observed_mutable_matrix_and_building_vector'
    return out


def mill_inventory(db, calls):
    mods = {r['ModifierId']: r for r in db.get('modifiers', [])}
    args = {}
    for a in db.get('modifierArguments', []): args.setdefault(a['ModifierId'], {})[a['Name']] = a['Value']
    results = []
    for building, rule in MILL_RULES.items():
        # Rule IDs are discovered from source instead of assuming an Amount=1
        # modifier is a Mill; Workshop naval production also uses small amounts.
        candidates = [r['ID'] for r in db.get('adjacencyRules', []) if r.get('WhoIsTheOwner') == building
                      and r.get('ProvideType', 'SelfBonus') == 'SelfBonus']
        if len(candidates) == 1: rule = candidates[0]
        active = [r['modifier'] for r in db.get('buildingRoots', []) if r['building'] == building]
        matched = []
        for root in active:
            child = args.get(root, {}).get('ModifierId')
            child_args = args.get(child, {})
            suffix = re.fullmatch(re.escape('MOD_CSC_ADJ_' + rule + '_') + r'(STEP_[1-9][0-9]*|1|2|4|8|16|32|64|128|256|512)', child or '')
            if (not suffix or root != 'ATTACH_' + child or
                    mods.get(root, {}).get('EffectType') != 'EFFECT_ATTACH_MODIFIER' or
                    mods.get(child, {}).get('EffectType') != 'EFFECT_ADJUST_DISTRICT_BASE_YIELD_CHANGE'):
                continue
            amount = child_args.get('Amount')
            try: amount = int(amount)
            except (ValueError, TypeError): amount = None
            observations = []
            for outer in (c for c in calls if c['building_type'] == building and c['modifier'] == root and c['own_building_root']):
                contexts = {}
                child_calls = [c for c in calls if c['parent_id'] == outer['id'] and c['modifier'] == child]
                for callback in sorted(child_calls, key=lambda c: c['entry_sequence']):
                    ctx = callback['before_context']
                    key = (ctx['cityPointer'], ctx['districtPointer'], ctx['plotPointer'])
                    contexts.setdefault(key, []).append(callback)
                observations.append({'root_call_id': outer['id'], 'root_result_q8': outer['restored_q8'],
                    'root_whole_utility_after': outer['whole_utility_after'],
                    'child_callbacks': len(child_calls),
                    'actual_contexts': [{'city_pointer': key[0], 'district_pointer': key[1], 'plot_pointer': key[2],
                        'calls': [c['id'] for c in group], 'last_child_whole_utility': group[-1]['whole_utility_after'],
                        'last_child_restored_q8': group[-1]['restored_q8'],
                        'last_child_accepted': group[-1]['accepted']} for key, group in contexts.items()],
                    'scope': 'child context results are diagnostic; only the root result enters ModifierValue'})
            matched.append({'root': root, 'child': child, 'amount': amount,
                'source_collection': mods.get(root, {}).get('CollectionType'),
                'observations': observations,
                'observed_calls': [c['id'] for c in calls if c['building_type'] == building and c['modifier'] == root and c['own_building_root']],
                'observed_root_results_q8': [c['restored_q8'] for c in calls if c['building_type'] == building and c['modifier'] == root and c['own_building_root']]})
        capacity = next((r['MaxAmount'] for r in db.get('unitSteps', []) if r['ID'] == rule), None)
        results.append({'building': building, 'rule': rule, 'source_step_capacity': capacity,
            'source_unit_root_count': sum('_STEP_' in x['child'] and x['amount'] == 1 for x in matched),
            'source_legacy_weighted_root_count': sum('_STEP_' not in x['child'] and x['amount'] in (1,2,4,8,16,32,64,128,256,512) for x in matched),
            'active_adjacency_roots': matched,
            'scope': 'active exact source topology only; dormant legacy definitions and unrelated Amount bits are not counted'})
    return results


def write_outputs(result, output):
    output.mkdir(parents=True, exist_ok=True)
    (output / 'analysis.json').write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    tables = {'building-components.csv': result.get('building_components', []),
              'modifier-calls.csv': result.get('modifier_calls', []),
              'district-aggregation.csv': [dict(calculation_id=a['id'], player=a['player'], city=a['city'], district=d['type'], **r)
                    for a in result.get('district_aggregations', []) for d in a.get('districts', []) for r in d['rows']]}
    for filename, rows in tables.items():
        columns = list(dict.fromkeys(k for r in rows for k in r))
        with (output / filename).open('w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=columns); writer.writeheader()
            writer.writerows({k: json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else v for k, v in row.items()} for row in rows)
    lines = ['# Native building component ledger', '', 'Audit: **' + ('PASS' if result['ok'] else 'FAIL') + '**; ' + str(result.get('record_count', 0)) + ' paired records.', '',
             'All scores are native utility in Q8. The residual remains unattributed; source gates describe the supplied world phase.', '',
             '| Player/city | Building | Full Q8 | Own modifiers Q8 | Own amenities Q8 | Unattributed Q8 |', '|---|---|---:|---:|---:|---:|']
    for b in result.get('building_components', []):
        lines.append('| {player}/{city} | {type} | {value_q8} | {own_modifier_q8} | {direct_amenity_consumed_q8} | {unattributed_native_remainder_q8} |'.format(**b))
    lines += ['', '## Errors and qualifications', '']
    lines += ['- ' + message for message in result.get('errors', []) + result.get('warnings', []) + result.get('limits', [])]
    (output / 'summary.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--trace', type=Path, required=True)
    parser.add_argument('--world', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    options = parser.parse_args()
    trace_bytes, world_bytes = options.trace.read_bytes(), options.world.read_bytes()
    result = analyze(json.loads(trace_bytes), json.loads(world_bytes))
    result['inputs'] = {'trace': str(options.trace.resolve()), 'trace_sha256': hashlib.sha256(trace_bytes).hexdigest(),
                        'world': str(options.world.resolve()), 'world_sha256': hashlib.sha256(world_bytes).hexdigest()}
    write_outputs(result, options.output)
    print(json.dumps({'ok': result['ok'], 'records': result.get('record_count'), 'errors': len(result['errors']),
                      'warnings': len(result['warnings']), 'output': str(options.output)}, separators=(',', ':')))
    return 0 if result['ok'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
