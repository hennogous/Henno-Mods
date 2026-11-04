"""Offline representation study against the actual shared CSC Lua writer.

Reads a rules DB without changing it. No game launch, mod installation, SQL
replacement or native scoring operation. Equality covers numerical encoding,
not activation/stacking, gameplay execution or hypothetical AI gate fidelity.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import sqlite3
import sys

ROOT = Path(__file__).resolve().parents[3]
CORE = ROOT / 'Civ Supply Chains/Lua_UI/Adjacencies/CSC_AdjacencyCore.lua'


def count_bound(rule):
    kind = rule['AdjacencyType']
    if kind == 'FROM_RIVER_CROSSING':
        return 6
    if kind == 'FROM_RINGS_CAO_TERRAIN_SETS' and rule['CustomAdjacentObject'] == 'IsHills':
        if rule['MinRings'] == 0 and rule['Rings'] == 0 and rule['MaxRings'] is None:
            return 1
    if kind in ('FROM_RINGS_CAO_DISTRICT', 'FROM_RINGS_TYPETAG_RESOURCE', 'FROM_RINGS_TYPETAG_DISTRICT'):
        if rule['MinRings'] == 1 and rule['Rings'] == 1 and rule['MaxRings'] is None:
            return 6
    raise ValueError('No proven small bound for rule ' + rule['ID'])


def review(database, dependencies):
    sys.path.insert(0, str(dependencies))
    from lupa.lua51 import LuaRuntime
    connection = sqlite3.connect(database.resolve().as_uri() + '?mode=ro', uri=True)
    connection.row_factory = sqlite3.Row
    rules = [dict(row) for row in connection.execute('SELECT * FROM CSC_AdjacencyRules ORDER BY ID')]
    connection.close()
    lua = LuaRuntime(unpack_returned_tuples=True)
    # Source registration captures these enum values at load. The numerical
    # writer exercised here never calls the damage/defence source functions.
    lua.execute('DefenseTypes={DISTRICT_GARRISON=0,DISTRICT_OUTER=1}')
    lua.execute(CORE.read_text(encoding='utf-8-sig'))
    evaluate = lua.eval('''function(id, factor, count)
        local values={}
        local plot={GetProperty=function(_,k)return values[k]end,
                    SetProperty=function(_,k,v)values[k]=v end}
        CSC_Adjacency.Write(plot,{ID=id,YieldChange=factor},count)
        return values
    end''')
    rows, cases = [], 0
    for rule in rules:
        if rule['ProvideType'] != 'SelfBonus' or rule['FreeCompose'] != 0:
            raise ValueError('Unreviewed output/compose semantics: ' + rule['ID'])
        bound = count_bound(rule)
        factor = rule['YieldChange']
        if factor <= 0:
            raise ValueError('Study only qualifies current positive rules')
        maximum = math.trunc(bound * factor)
        bits = []
        bit = 1
        while bit <= maximum:
            bits.append(bit)
            bit *= 2
        samples = []
        for count in range(bound + 1):
            values = evaluate(rule['ID'], factor, count)
            prefix = 'CSC_ADJ_' + rule['ID']
            old = values[prefix + '_ENCODED_AMOUNT']
            binary = sum(bit * values[prefix + '_' + str(bit)] for bit in bits)
            unary = sum(1 for threshold in range(1, maximum + 1) if old >= threshold)
            one_hot = sum(amount for amount in range(1, maximum + 1) if old == amount)
            if not old == binary == unary == one_hot:
                raise AssertionError('Representation mismatch: ' + rule['ID'])
            samples.append(dict(count=count, current=old, bounded_binary=binary,
                                unit_threshold=unary, one_hot=one_hot))
            cases += 1
        rows.append(dict(id=rule['ID'], source=rule['AdjacencyType'], count_max=bound,
            actual_yield_max=maximum, old_children=10, binary_bits=bits,
            binary_children=len(bits), unary_children=maximum,
            ignored_gate_ceilings=dict(old=1023, binary=sum(bits), unary=maximum,
                one_hot=maximum * (maximum + 1) // 2), samples=samples))
    return dict(schema=1, numerical_encoding_equal=True, actual_lua='Lua5.1 shared CSC_Adjacency.Write',
        cases=cases, rules=len(rows),
        database=dict(path=str(database.resolve()), sha256=hashlib.sha256(database.read_bytes()).hexdigest()),
        core_sha256=hashlib.sha256(CORE.read_bytes()).hexdigest(),
        modifier_children=dict(current=sum(x['old_children'] for x in rows),
            bounded_binary=sum(x['binary_children'] for x in rows),
            unit_threshold=sum(x['unary_children'] for x in rows)),
        rows=rows, limits=['No gameplay ownership, activation or stacking parity test.',
            'No change installed; conditional forecast correctness is not established.',
            'New sources, rings, factors or non-yield providers require a new bound review.'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--database', type=Path, required=True)
    parser.add_argument('--dependencies', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('Fresh output required')
    result = review(args.database, args.dependencies)
    args.output.mkdir(parents=True)
    (args.output / 'review.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: result[key] for key in ('numerical_encoding_equal', 'cases', 'rules', 'modifier_children')}))
