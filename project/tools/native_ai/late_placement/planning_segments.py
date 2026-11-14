"""Normalize two CLOSED observation segments; never contact or resume a game.

The exact save-complete marker cuts Lua evidence, not a turn-number guess.
Native turn200 pre-save ordering is unavailable: exclude it explicitly, retain
it separately, and label the coverage gap. Versions/ordinals remain segment-local.
Normalized Lua.log is derived evidence, NOT a copy of either raw game log.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import shutil

ROW = re.compile(r'(CSC_PLANNING_|CSC_QUARTER_WATCH_|CSC_DISTRICT_UI_)([A-Z_]+)\t([^\r\n]*)')
COVERAGE = re.compile(r'CSC_AI_QUARTER_COVERAGE turn=(\d+) version=(\d+) player=(\d+) district=(\d+) result=(\{[^\r\n]+\})')
LIMITS = [
    'Normalized derivative of two sessions, not raw or uninterrupted evidence.',
    'Native coverage excludes original turn200 pre-save events: ordering relative to save is unknown.',
    'Reload resets native caches, policy versions, ordinals and observer sequence identity; segment keys are mandatory.',
    'First post-reload native bids can lack offer metadata; missing joins are unknown, not delivery failures.',
    'History fills physical dates only; no cross-reload foundation, decision causality or reconsideration is invented.',
    'Canonical Lua.log contains planning/watch/UI rows only; Service/Storekeeper evidence requires the raw segments.',
]


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def _fields(payload):
    return dict(field.split('=', 1) for field in payload.split('\t') if '=' in field)


def _update_history(history, prefix, kind, fields):
    if prefix != 'CSC_PLANNING_' or kind not in ('FOUNDATION', 'COMPLETION', 'REMOVED'):
        return
    key = (fields.get('plot'), fields.get('district'))
    if kind == 'REMOVED':
        history.pop(key, None); return
    if kind == 'FOUNDATION':
        # A later physical foundation at this tile supersedes its old lifetime.
        for old in [old for old in history if old[0] == key[0]]:
            history.pop(old)
    entry = history.setdefault(key, {})
    if fields.get('districtType'):
        entry['districtType'] = fields['districtType']
    for field in ('foundationTurn', 'completionTurn'):
        if field in fields:
            entry[field] = fields[field]
            entry[field + 'Segment'] = fields.get('segment', 'unknown')
    if kind == 'COMPLETION' and 'completionTurn' not in entry and 'turn' in fields:
        entry['completionTurn'] = fields['turn']
        entry['completionTurnSegment'] = fields.get('segment', 'unknown')


def _fill_relation(fields, history):
    # Preserve the recorded values as well as row order. Only supply a missing
    # date from a recorded physical event at the same plot AND district type.
    # Original history survives reload; later physical events replace it.
    qtype = 'DISTRICT_CSC_' + fields.get('quarter', '') + '_QUARTER'
    q = next((v for (plot, _), v in history.items()
              if plot == fields.get('quarterPlot') and v.get('districtType') == qtype), {})
    neighbour = history.get((fields.get('neighbourPlot'), fields.get('neighbourDistrict')), {})
    changed, used = False, set()
    for event in ('Foundation', 'Completion'):
        event_changed = False
        key = event.lower() + 'Turn'
        for label, source in (('quarter', q), ('neighbour', neighbour)):
            field = label + event + 'Turn'
            if field not in fields and key in source:
                fields[field] = source[key]; changed = event_changed = True
                used.add(source.get(key + 'Segment', 'unknown'))
        a, b = fields.get('quarter' + event + 'Turn'), fields.get('neighbour' + event + 'Turn')
        if a is not None and b is not None and event_changed:
            order = event.lower() + 'Order'
            fields['recorded' + event + 'Order'] = fields.get(order, 'missing')
            fields[order] = 'sameTurn' if int(a) == int(b) else 'quarterFirst' if int(a) < int(b) else 'neighbourFirst'
    if changed:
        fields['historyFilled'] = 'true'
        fields['historySourceSegment'] = ','.join(sorted(used))
    return changed


def _parse_lua(lines, segment):
    rows = []
    for number, line in enumerate(lines, 1):
        match = ROW.search(line)
        if match:
            prefix, kind, payload = match.groups()
            fields = _fields(payload)
            require('segment' not in fields, 'Input already normalized')
            rows.append((number, prefix, kind, dict(fields, segment=segment)))
        receipt = COVERAGE.search(line)
        if receipt:
            turn, version, player, district, body = receipt.groups()
            json.loads(body)  # Reject damaged receipts rather than counting them.
            rows.append((number, 'CSC_PLANNING_', 'MANAGED_COVERAGE',
                         dict(segment=segment, turn=turn, version=version,
                              player=player, district=district, receiptJson=body)))
    return rows


def merge(original, continuation, output, at=200):
    """Create a new derived archive only after BOTH inputs close and restore."""
    original, continuation = Path(original).resolve(strict=True), Path(continuation).resolve(strict=True)
    output = Path(output).resolve()
    require(at == 200, 'This audited merger supports the save200 continuation only')
    require(not output.exists() and output not in (original, continuation), 'New normalized output required')
    for root in (original, continuation):
        require(load(root / 'session-closed.json').get('verified') is True
                and load(root / 'preferences-restored.json').get('verified') is True, 'Inputs must be closed/restored')
    checkpoint = load(original / 'checkpoint-200.json')
    require(checkpoint.get('verified') is True and checkpoint['turn'] == at, 'Invalid checkpoint')
    save = original / 'turn-200.Civ6Save'
    require(sha(save) == checkpoint['sha256'], 'Checkpoint bytes changed')
    resume = load(continuation / 'continuation.json')
    require(Path(resume['source']).resolve() == original and resume['at'] == at
            and resume['source_checkpoint']['sha256'] == checkpoint['sha256'], 'Wrong continuation parent/checkpoint')
    require(load(continuation / 'source-structure-comparison.json').get('verified') is True,
            'Missing verified loaded structure equivalence')
    source = load(original / 'source.json')
    require(load(continuation / 'source.json')['original_ai'] == source['original_ai'], 'AI cohort changed')
    before = (original / 'Lua.log').read_text(encoding='utf-8-sig').splitlines(keepends=True)
    marker = re.compile(r'CSC_EXACT_CHECKPOINT_COMPLETE\t' + re.escape(checkpoint['unique_name']) + r'\ttrue(?:\s|$)')
    cuts = [i for i, line in enumerate(before) if marker.search(line)]
    require(len(cuts) == 1, 'Exactly one named save-complete marker required')
    cut = cuts[0] + 1
    original_rows = _parse_lua(before[:cut], 'original')
    continuation_rows = _parse_lua((continuation / 'Lua.log').read_text(encoding='utf-8-sig').splitlines(), 'continuation')
    history, filled = {}, 0
    for _, prefix, kind, fields in original_rows:
        _update_history(history, prefix, kind, fields)
    for _, prefix, kind, fields in continuation_rows:
        if prefix == 'CSC_PLANNING_' and kind == 'RELATION':
            filled += _fill_relation(fields, history)
        _update_history(history, prefix, kind, fields)
    output.mkdir(parents=True)
    provenance = dict(normalized=True, raw=False, fresh_game=False, uninterrupted=False,
                      original=str(original), continuation=str(continuation), at=at, limits=LIMITS,
                      lua_cutoff=dict(marker=checkpoint['unique_name'], inclusive_original_line=cut,
                                      discarded_tail_lines=len(before)-cut), history_filled_relations=filled,
                      native_coverage_gap=dict(turn=at, segment='original', phase='preload',
                                               reason='Save-relative native ordering unavailable'), inputs={}, copies={})
    def copy(root, name, target=None):
        src = root / name
        if not src.exists():
            return
        dest = output / (target or name)
        dest.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(src, dest)
        provenance['copies'][str(dest.relative_to(output))] = dict(source=str(src), sha256=sha(src))
    for root, segment in ((original, 'original'), (continuation, 'continuation')):
        for name in ('Lua.log', 'economy-savings.ndjson', 'source.json', 'protocol.json', 'packages.json',
                     'extra-mods.json', 'session-closed.json', 'preferences-restored.json', 'continuation.json',
                     'source-structure-comparison.json', 'resource-stack-preflight.json'):
            path = root / name
            if path.exists():
                provenance['inputs'][segment + '/' + name] = dict(path=str(path), sha256=sha(path), bytes=path.stat().st_size)
                if name not in ('Lua.log', 'economy-savings.ndjson'):
                    copy(root, name, 'segments/' + segment + '/' + name)
        for path in root.glob('checkpoint*.json'):
            copy(root, path.name, 'segments/' + segment + '/' + path.name)
    for name in ('source.json', 'loaded-district-catalogue.txt', 'resource-stack-preflight.json', 'resource-origins.lua'):
        require((original / name).exists(), 'Missing original analysis input ' + name)
        copy(original, name)
    for turn in range(25, 251, 25):
        root = original if turn <= at else continuation
        require((root / f'full-census-{turn}.json').exists(), 'Missing selected census ' + str(turn))
        copy(root, f'full-census-{turn}.json')
    # Boundary contexts are later observed facts, not exact native call facts.
    # Keep their source segment in the filename; abandoned original205+ must
    # never leak into a budget/purchase join against retained native evidence.
    for root, segment in ((original, 'original'), (continuation, 'continuation')):
        for path in root.glob('purchase-context-*.txt'):
            match = re.fullmatch(r'purchase-context-(\d+)\.txt', path.name)
            if match:
                boundary = int(match[1])
                selected = boundary <= at if segment == 'original' else boundary > at
                if selected:
                    copy(root, path.name, f'purchase-context-{segment}-{boundary}.txt')
    copy(original, 'checkpoint-200.json'); copy(original, save.name)
    copy(continuation, 'checkpoint.json', 'continuation-endpoint-checkpoint.json')
    normalized = []
    for _, prefix, kind, fields in original_rows + continuation_rows:
        normalized.append(prefix + kind + '\t' + '\t'.join(k + '=' + str(v) for k, v in fields.items()))
    (output / 'Lua.log').write_text('\n'.join(normalized) + '\n', encoding='utf-8')
    kept, excluded, reasons = [], [], Counter()
    for root, segment in ((original, 'original'), (continuation, 'continuation')):
        for line in (root / 'economy-savings.ndjson').read_text(encoding='utf-8').splitlines():
            row = json.loads(line)
            require('segment' not in row, 'Native input already normalized')
            turn = row.get('turn')
            accepted = type(turn) is int and (turn < at if segment == 'original' else turn >= at)
            tagged = dict(row, segment=segment)
            if accepted:
                kept.append(tagged)
            else:
                reason = 'undated' if type(turn) is not int else 'original_at_or_after_save_turn' if segment == 'original' else 'continuation_before_load_turn'
                reasons[reason] += 1; excluded.append(dict(record=tagged, exclusionReason=reason))
    for name, rows in (('economy-savings.ndjson', kept), ('excluded-native-boundaries.ndjson', excluded)):
        (output / name).write_text(''.join(json.dumps(row, sort_keys=True) + '\n' for row in rows), encoding='utf-8')
    protocol = dict(load(original / 'protocol.json'), fresh_game=False, normalized=True,
                    uninterrupted=False, natural_continuation=True, continuation_start=at,
                    original_fresh_game=load(original / 'protocol.json').get('fresh_game'))
    (output / 'protocol.json').write_text(json.dumps(protocol, indent=2) + '\n', encoding='utf-8')
    provenance.update(native_kept=len(kept), native_excluded=len(excluded), exclusion_reasons=dict(reasons),
                      original_rows=len(original_rows), continuation_rows=len(continuation_rows))
    provenance['derived_manifest'] = {str(p.relative_to(output)): sha(p) for p in output.rglob('*') if p.is_file()}
    (output / 'normalized-segments.json').write_text(json.dumps(provenance, indent=2) + '\n', encoding='utf-8')
    return provenance


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('original', 'continuation', 'output'):
        parser.add_argument(name, type=Path)
    parser.add_argument('--at', type=int, default=200)
    args = parser.parse_args()
    print(json.dumps(merge(args.original, args.continuation, args.output, args.at), indent=2))
