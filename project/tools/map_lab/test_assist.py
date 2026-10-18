"""Evidence-preservation, habitat, successful-site and deterministic-preview checks."""
import argparse
from collections import Counter
import copy
import hashlib
import json
from pathlib import Path
from assist import Helper, Rules, read
from offline import OfflineWorld


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--bundle', type=Path, required=True)
    p.add_argument('--database', type=Path, required=True)
    p.add_argument('--game-root', type=Path, required=True)
    p.add_argument('--workshop-root', type=Path, required=True)
    p.add_argument('--lua-dependencies', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args(); bundle = read(args.bundle); rules = Rules(args.database)
    checks = 0; deposits = 0; losses = []; originals = {m['id']: m for m in bundle['maps'] if m['group'] == 'luxuries-4'}
    for preview in [m for m in bundle['maps'] if m['group'] == 'csc-assist']:
        source = originals[preview['assistance']['source_id']]
        before_hash = hashlib.sha256(json.dumps(source, sort_keys=True).encode()).hexdigest()
        helper = Helper(source, rules, preview['assistance']['seed']); replay = helper.run()
        assert replay == preview, 'Same seed must reproduce the complete preview and audit trail'
        assert hashlib.sha256(json.dumps(source, sort_keys=True).encode()).hexdigest() == before_hash
        additions = preview['assistance']['additions']; assert len(additions) <= 10
        changes = {a['plot']: a for a in additions}; assert len(changes) == len(additions)
        for original, new in zip(source['data']['plots'], preview['data']['plots']):
            if original['index'] not in changes: assert original == new
            else:
                assert not original.get('resource')
                assert {k: v for k, v in original.items() if k != 'resource'} == {k: v for k, v in new.items() if k != 'resource'}
        # Check selected deposits against the existing Lua adapter independently
        # of the Python helper's port of those eligibility rules.
        world = OfflineWorld(source['data'], args.database, args.game_root, args.workshop_root,
                             123, 3, args.lua_dependencies)
        world.bootstrap()
        for a in additions:
            world.lua.globals().CHECK_INDEX = a['plot']; world.lua.globals().CHECK_RESOURCE = a['resource']
            assert world.lua.eval('ResourceBuilder.CanHaveResource(Map.GetPlotByIndex(CHECK_INDEX), GameInfo.Resources[CHECK_RESOURCE].Index)')
            assert rules.can_place(source['data']['plots'][a['plot']], a['resource'], source['data']['plots'])
            center = preview['data']['plots'][a['center']]
            assert center['continent'] == a['continent'] == preview['data']['plots'][a['plot']]['continent']
            assert a['plot'] in center['neighbors'] and helper.clearable(center)
            assert a['center'] in helper.sites()[a['continent'], a['quarter']]
            deposits += 1
        for cid, count in Counter(a['continent'] for a in additions).items(): assert count <= 4
        old_base = Helper(source, rules).sites(mode='base'); after_base = helper.sites(mode='base')
        for key, old in helper.baseline_sites.items():
            after = helper.sites()[key]
            assert not old or after, 'Cannot remove a continent’s last both-class opportunity'
            assert not old_base[key] or after_base[key], 'Cannot remove a continent’s last base-supported opportunity'
            if old - after: losses.append({'map': preview['number'], 'continent': key[0], 'quarter': key[1], 'lost_tiles': len(old - after)})
        checks += 8 + len(additions) * 4
    # Exercise the rare two-deposit path on a landscape with neither Gold class.
    source = copy.deepcopy(next(iter(originals.values())))
    gold = source['definitions']['GOLDSMITHS']; gold_resources = set(gold['base']['resources'] + gold['spec']['resources'])
    for tile in source['data']['plots']:
        if tile.get('resource') in gold_resources: tile.pop('resource')
    h = Helper(source, rules); current = h.sites()
    options = h.options(h.ids[0], 'GOLDSMITHS', current)
    assert options and all(len(o['deposits']) == 2 for o in options)
    selected = h.choose(options, h.ids[0], 'GOLDSMITHS', current); assert selected
    for i, r in selected['deposits']: h.plots[i]['resource'] = r
    assert selected['center'] in h.sites()[h.ids[0], 'GOLDSMITHS']
    for i, _ in selected['deposits']: h.plots[i].pop('resource')
    h.budget[h.ids[0]] = 4
    assert h.choose(options, h.ids[0], 'GOLDSMITHS', current) is None
    result = {'passed': True, 'maps': len(originals), 'deposits_checked': deposits,
              'checks': checks + 4, 'two_deposit_and_budget_paths': True,
              'lost_candidate_tiles': losses, 'native_execution_tested': False}
    args.output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result))


if __name__ == '__main__': main()
