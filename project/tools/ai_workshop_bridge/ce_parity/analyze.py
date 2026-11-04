"""Audit packaged Lua plans and paged native traces after a closed CE test.

Repeated whole-log archives and repeated frozen-window dumps are deduplicated by
native generation/version/record index, never by end-of-turn reset counters.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re

KINDS = ('net', 'cache', 'best', 'pv')


def marker_rows(path):
    chunks = {}
    with path.open(encoding='utf-8', errors='replace') as stream:
        for line, text in enumerate(stream, 1):
            chunk = re.search(r'CSC_CE_POLICY_CHUNK=(\{.*)', text)
            if chunk:
                try:
                    value = json.loads(chunk[1])
                    key = value['epoch'], value['seq']
                    metadata = {k: value[k] for k in ('schema', 'epoch', 'seq', 'kind',
                        'parts', 'bytes', 'sum32', 'encoding')}
                    if (value['schema'] != 1 or value['encoding'] != 'hex'
                            or not 1 <= value['part'] <= value['parts']
                            or value['parts'] > 100000 or value['bytes'] > 50000000):
                        raise ValueError('Invalid chunk framing')
                    group = chunks.setdefault(key, dict(metadata=metadata, parts=[], source=line))
                    if group['metadata'] != metadata or value['part'] != len(group['parts']) + 1:
                        raise ValueError('Changed metadata or out-of-order chunk')
                    group['parts'].append(bytes.fromhex(value['data']))
                    if value['part'] == value['parts']:
                        payload = b''.join(group['parts'])
                        if len(payload) != value['bytes'] or sum(payload) % 2**32 != value['sum32']:
                            raise ValueError('Chunk length/checksum mismatch')
                        decoded = json.loads(payload.decode('utf-8'))
                        if value['kind'] in ('PLAN', 'NATIVE', 'TRACE', 'STOP', 'TRACE_FAILURE'):
                            yield value['kind'], decoded, dict(path=str(path), line=group['source'],
                                chunks=value['parts'], epoch=value['epoch'], seq=value['seq'])
                        del chunks[key]
                except (KeyError, TypeError, ValueError) as error:
                    raise ValueError(f'Malformed chunk receipt at {path}:{line}: {error}') from error
                continue
            match = re.search(r'CSC_CE_POLICY_(PLAN|NATIVE|TRACE|STOP|TRACE_FAILURE)=(\{.*)', text)
            if match:
                try:
                    yield match[1], json.loads(match[2]), dict(path=str(path), line=line)
                except ValueError as error:
                    raise ValueError(f'Malformed policy receipt at {path}:{line}') from error
    if chunks:
        raise ValueError('Incomplete chunked receipt in ' + str(path))


def audit_records(plans, records):
    counts, signs = Counter(), Counter()
    windows = {}
    for key, record in sorted(records.items()):
        generation, version, index = key
        kind = record['k']
        if kind not in KINDS or record['generation'] != generation or record['version'] != version:
            raise ValueError('Trace framing/generation mismatch')
        counts[kind] += 1
        windows.setdefault((generation, version), []).append(index)
        if record['player'] == 0:
            raise ValueError('Original human appeared in native policy trace')
        if kind != 'net':
            if record['base'] != record['result']:
                raise ValueError('Read-only diagnostic changed a value')
            continue
        plan = plans.get((generation, version))
        if plan is None:
            raise ValueError('Native write has no matching publication')
        pairs = {(e['player'], e['city'], e['district'], e['plot']): e for e in plan['entries']}
        pair = tuple(record[k] for k in ('player', 'city', 'district', 'plot'))
        if pair not in pairs or not record['eligible']:
            raise ValueError('Native mutation outside published pair scope')
        base, result, reason = record['base'], record['result'], record['reason']
        delta = pairs[pair]['delta']
        if reason == 0:
            expected = base + delta
            if delta < 0:
                expected = max(-1048576, expected)
            if (base == 0 or base <= -2559744 or (delta < 0 and base <= -1048576)
                    or expected > 2147483647 // 2 or result != expected):
                raise ValueError('Native signed adjustment arithmetic mismatch')
            signs['positive' if delta > 0 else 'negative'] += 1
        elif reason == 2:
            if result != base or not (base == 0 or base <= -2559744 or (delta < 0 and base <= -1048576)):
                raise ValueError('Protected-result trace mismatch')
            signs['protected'] += 1
        elif reason == 3:
            if result != base:
                raise ValueError('Rejected arithmetic changed a value')
            signs['arithmetic_rejected'] += 1
        else:
            raise ValueError('Native write/record budget fault')
    return dict(kinds=dict(counts), adjustments=dict(signs), windows=len(windows))


def analyze(directory):
    directory = Path(directory)
    paths = sorted((directory / 'logs').rglob('Lua.log'))
    plans, records, totals, failures = {}, {}, {}, []
    observations = []
    for path in paths:
        pending = {}
        for kind, value, source in marker_rows(path):
            if kind == 'PLAN' and value.get('published', True):
                pending[value['version']] = value
            elif kind == 'NATIVE':
                status = value['status']
                if status['faults']:
                    failures.append(dict(source=source, native=status))
                if value['reason'] == 'published':
                    key = status['generation'], status['version']
                    plan = pending.get(status['version'])
                    if plan is None:
                        raise ValueError('Published native window missing its Lua plan')
                    if key in plans and plans[key] != plan:
                        raise ValueError('Conflicting plan for native generation')
                    plans[key] = plan
            elif kind == 'TRACE':
                page = value['page']
                if page['stale'] or page['next'] != page['offset'] + len(page['records']):
                    raise ValueError('Incomplete/stale trace page')
                for offset, record in enumerate(page['records'], page['offset']):
                    key = record['generation'], record['version'], offset
                    window = key[:2]
                    if key in records and records[key] != record:
                        raise ValueError('Conflicting duplicate native trace index')
                    records[key] = record
                    totals[window] = max(totals.get(window, 0), page['total'])
            elif kind == 'TRACE_FAILURE' or (kind == 'STOP' and value.get('failed')):
                failures.append(dict(source=source, receipt=value))
    if failures:
        raise ValueError('Package/native failure receipt: ' + json.dumps(failures[:2]))
    for window, total in totals.items():
        indices = {key[2] for key in records if key[:2] == window}
        if indices != set(range(total)):
            raise ValueError('Missing native records for window ' + str(window))
    audit = audit_records(plans, records)
    for path in sorted((directory / 'observations').glob('*.json')):
        value = json.loads(path.read_text(encoding='utf-8-sig'))
        if 'policy_audit' in value:
            observations.append(dict(path=str(path), turn=value['turn'], phase=value['phase'],
                                     **value['policy_audit']))
    result = dict(verified=True, source=str(directory), log_archives=len(paths),
        published_windows=len(plans), trace_records=len(records),
        policy_audits=len(observations), native_faults=0, **audit,
        all_four_trace_kinds_observed=all(audit['kinds'].get(k, 0) for k in KINDS),
        both_adjustment_signs_observed=all(audit['adjustments'].get(k, 0) for k in ('positive', 'negative')),
        completion_or_benefit_proven=False)
    (directory / 'parity-audit.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    print(json.dumps(analyze(parser.parse_args().directory), indent=2))
