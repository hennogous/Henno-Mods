"""Count only sampled Storekeeper turns with a native attachment and growth recipient."""

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import re


ATTACH = 'MOD_CSC_BAKERS_STAGE_2_EFFECT_ATTACH_CITY_'
GROWTH = 'MOD_CSC_BAKERS_STAGE_2_EFFECT_GROWTH_'
MILLS = {'WATER', 'WIND'}


def district_object(value):
    instance, kind, fields = value.split(' ', 2)
    if kind != 'LOC_MODIFIER_OBJECT_DISTRICT':
        raise ValueError(f'Expected a native district object, got {kind}')
    values = {key: int(raw) for key, raw in re.findall(r'(\w+):\s*(-?\d+)', fields)}
    return int(instance), values['Owner'], values['City'], values['District']


def confirmed_chains(instances, subjects):
    anchors = defaultdict(set)
    growth = defaultdict(set)
    for modifier, (definition, active, count, owner) in instances.items():
        recipients = subjects.get(modifier, ())
        if len(recipients) != count or len(set(recipients)) != count:
            raise ValueError(f'Incomplete Storekeeper subjects for {modifier}')
        if not active or not recipients:
            continue
        if definition.startswith(ATTACH) and definition[len(ATTACH):] in MILLS:
            source = district_object(owner)
            for subject in recipients:
                customer = district_object(subject)
                if customer[1] == source[1]:
                    anchors[definition[len(ATTACH):], customer].add(source[1:])
        elif definition.startswith(GROWTH) and definition[len(GROWTH):] in MILLS:
            customer = district_object(owner)
            if len(recipients) == 1 and district_object(recipients[0]) == customer:
                growth[definition[len(GROWTH):], customer].add(modifier)

    # A recipient may get the same effect from two Quarters. Count the
    # sources only if there are enough independently active effect copies
    # to match every observed attachment for that recipient and Mill type.
    return {chain for key, sources in anchors.items() if len(sources) == len(growth[key]) for chain in sources}


def sampled_chains(text):
    instances, subjects, samples = {}, defaultdict(list), {}
    current = None
    for line in text.splitlines():
        if 'CSC_STOREKEEPER_' not in line:
            continue
        kind, raw_turn, *fields = line.split('CSC_STOREKEEPER_', 1)[1].strip().split('\t')
        turn = int(raw_turn)
        if current is not None and current != turn:
            raise ValueError('Storekeeper snapshot lacks its end record')
        current = turn
        if kind == 'INSTANCE':
            raw_modifier, definition, active, count, owner = fields
            modifier = int(raw_modifier)
            if modifier in instances or active not in ('true', 'false'):
                raise ValueError('Invalid Storekeeper modifier instance')
            instances[modifier] = definition, active == 'true', int(count), owner
        elif kind == 'SUBJECT':
            raw_modifier, subject = fields
            modifier = int(raw_modifier)
            if modifier not in instances:
                raise ValueError('Storekeeper subject has no modifier instance')
            subjects[modifier].append(subject)
        elif kind == 'END':
            if fields != [str(len(instances))]:
                raise ValueError('Incorrect Storekeeper instance count')
            chains = confirmed_chains(instances, subjects)
            if turn in samples and samples[turn] != chains:
                raise ValueError(f'Conflicting Storekeeper samples at turn {turn}')
            samples[turn] = chains
            instances, subjects, current = {}, defaultdict(list), None
        else:
            raise ValueError(f'Unknown Storekeeper record {kind}')
    if current is not None:
        raise ValueError('Unfinished Storekeeper snapshot')
    return samples


def audit(text, players):
    samples = sampled_chains(text)
    if not samples:
        raise ValueError('No Storekeeper snapshots')
    active = Counter(chain for chains in samples.values() for chain in chains if chain[0] in players)
    return {
        'sampled_turns': sorted(samples),
        'unsampled_turns': sorted(set(range(min(samples), max(samples) + 1)) - samples.keys()),
        'active_turns': [
            dict(player=player, city=city, quarter=district, turns=turns)
            for (player, city, district), turns in sorted(active.items())
        ],
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('log', type=Path)
    parser.add_argument('--players', type=int, nargs='+', required=True,
                        help='Original AI player IDs from the verified game setup')
    args = parser.parse_args()
    print(json.dumps(audit(args.log.read_text(encoding='utf-8-sig'), set(args.players)), indent=2))
