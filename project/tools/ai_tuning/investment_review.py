"""Offline investment review and preview of CSC's actual pure Lua host policy.

No native imports, requests, receipt tokens or spending authority. The caller
must still pass the installed host's fresh economic/foundation gates in-game.
"""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path

from chain_coordinator import coordinate
from selective_planner import shortlist
from site_evaluator import value, number


def review(snapshot, combined_threshold=4):
    """Compare starts, existing commitments and deferral without invented ROI."""
    coordinated = coordinate(snapshot)
    starts = shortlist(snapshot['sites'], snapshot['mapping'], combined_threshold)
    commitments = [c for c in coordinated['chains']
                   if value(c['state']) in ('unfinished', 'pillaged')
                   and value(c['request_state']) in ('accepted_waiting', 'selected')]
    proposed = None
    if commitments:
        decision = 'respect_existing_native_commitment'
        reason = 'Observe accepted work; do not duplicate or force its queue/worker assignment'
    elif len(starts['shortlist']) == 1 and not coordinated['unknowns']:
        row = next(r for r in starts['alternatives'] if r['status'] == 'shortlisted_for_investment_review')
        identity = row['identity']
        options = [o for o in coordinated['options'] if o['kind'] == 'start'
                   and o['site'] == dict(city=identity['city'], quarter=row['quarter'], plot=identity['plot'])]
        if len(options) != 1 or options[0]['status'] != 'review' or options[0].get('needs_site_review'):
            return dict(decision='defer_investment', reason='Coordinator deferred or rejected this footprint',
                        proposed_host_candidate=None, native_commitments=[], starts=starts, coordination=coordinated,
                        action_authorization=False, native_calls=0, spending=0)
        credible = {p['plot'] for p in row['evaluation']['future']
                    if p['kind'] == 'material' and p['status'] == 'credible_conditional'}
        supply = [m for m in row['evaluation']['materials']
                  if m['state'] == 'current_supply' or m['plot'] in credible]
        base = sorted(m['plot'] for m in supply if 'base' in m['roles'])
        spec = sorted(m['plot'] for m in supply if 'specialty' in m['roles'])
        if base and spec:
            i = row['identity']
            proposed = dict(player=i['player'], city=i['city'], quarter=row['quarter'], source=i['plot'],
                            materials=[base[0], spec[0]], turn=i['turn'])
            decision = 'review_start_with_guarded_host'
            reason = 'One evidenced shortlist option with Both materials; conditional development and fresh host checks remain'
        else:
            decision = 'defer_unsupported_host_route'
            reason = 'The installed placement host still requires Both materials; +4-only routes without Specialty are not wired'
    else:
        decision = 'defer_investment'
        reason = 'No single fully evidenced, unallocated start; compare missing costs, conflicts and existing work'
    return dict(decision=decision, reason=reason, proposed_host_candidate=proposed,
                native_commitments=deepcopy(commitments), starts=starts, coordination=coordinated,
                action_authorization=False, native_calls=0, spending=0,
                utility='No exchange rate, benefit forecast, assignment guarantee or budget allocation invented')


def preview_host(policy_path, *, player, required, tiles, finance):
    """Run the existing P.Route/P.Funding in isolated Lua, never in Civ.

    Tile inputs describe a sourced observed subgraph, not an assertion of a
    globally optimal path. Later-step quotes remain hints. All quantities use
    the host's own formula rather than a second Python implementation.
    """
    from lupa.lua51 import LuaRuntime
    if isinstance(player, bool) or not isinstance(player, int) or player < 0:
        raise ValueError('Player identity required')
    normalized = {}
    for key, tile in tiles.items():
        if not isinstance(tile.get('source'), str) or not tile['source'].strip():
            raise ValueError('Route tile provenance required')
        idx = int(key)
        owner = tile.get('owner')
        if isinstance(owner, bool) or owner not in (-1, player):
            raise ValueError('Foreign/unknown ownership is outside the host route domain')
        normalized[idx] = deepcopy(tile)
    if any(isinstance(i, bool) or not isinstance(i, int) or i < 0 or i not in normalized for i in required):
        raise ValueError('Required plot identity missing')
    policy_path = Path(policy_path)
    source = policy_path.read_bytes()
    lua = LuaRuntime(register_eval=False, register_builtins=False)
    lua.execute(source.decode('utf-8-sig'))
    policy = lua.globals().CSC_AI_OpportunityPolicy
    def table(v):
        if isinstance(v, (list, dict)):
            t = lua.table()
            for k, x in (enumerate(v, 1) if isinstance(v, list) else v.items()):
                t[k] = table(x)
            return t
        return v
    route = policy.Route(table(normalized), table(required))
    steps = None if route is None else [route[i] for i in range(1, len(route)+1)]
    funding = None; missing = []
    if steps:
        price = normalized[steps[0]].get('price')
        terms = {k:number(finance.get(k)) for k in ('gold','gross','upkeep','spent')}
        subsidies = value(finance.get('subsidies'))
        missing = [k for k,v in terms.items() if v is None or v < 0]
        if type(subsidies) is not bool: missing.append('subsidies')
        if not missing:
            f = policy.Funding(price, terms['gold'], terms['gross'], terms['upkeep'], subsidies, terms['spent'])
            if f is not None: funding = {k:f[k] for k in ('price','own','grant','reserve','gold')}
    return dict(policy_path=str(policy_path), policy_sha256=sha256(source).hexdigest(),
                route=steps, next_tile_funding=funding, unknown_finance=missing,
                quote_scope='historical/estimated input only; fresh per-step native quote required',
                remaining_checks=['original-human/settings/Quarter binding','source/material ownership and legality',
                                  'cooldowns and rolling/site caps','pending one-shot receipt reconciliation',
                                  'fresh treasury/quote/reach','native/UI 0% foundation, cost and queue'],
                action_authorization=False, native_calls=0, spending=0)


def main():
    import argparse
    import json
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--snapshot', type=Path)
    p.add_argument('--host-input', type=Path)
    p.add_argument('--policy', type=Path)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    if not a.snapshot and not a.host_input:
        p.error('Provide a strict snapshot and/or a sourced host-preview input')
    if a.host_input and not a.policy:
        p.error('--host-input requires the actual --policy Lua source')
    if a.output.exists():
        raise FileExistsError('Preserve existing result: '+str(a.output))
    result = dict(action_authorization=False, native_calls=0, inputs=[])
    for key, path in (('snapshot', a.snapshot), ('host_preview', a.host_input)):
        if path:
            raw = path.read_bytes()
            data = json.loads(raw.decode('utf-8-sig'))
            result['inputs'].append(dict(path=str(path), sha256=sha256(raw).hexdigest()))
            result[key] = review(data) if key == 'snapshot' else preview_host(a.policy, **data)
    a.output.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(dict(output=str(a.output), action_authorization=False, native_calls=0)))


if __name__ == '__main__':
    main()
