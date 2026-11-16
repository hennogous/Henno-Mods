"""Summarise closed native SQL dose replays and verify the isolated contrast.

Analysis only. Compare the first real selector matrix in each scoped city, before
later decisions diverge. Preserve native Q8 values and row flags; distinguish a
selected footprint from the later construction phase. Raw matrices stay in the
small native journals rather than being copied into project documentation.
"""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path


CASES = {0:'signal0-150-155', 1:'signal1-150-155-02', 4:'signal4-150-155', 8:'signal8-150-155'}
load = lambda p: json.loads(p.read_text(encoding='utf-8'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def analyse(root):
    root = Path(root)
    arms, matrices, definitions, manifests = {}, {}, {}, {}
    for amount, name in CASES.items():
        p = root/name
        closed = load(p/'session-closed.json')
        assert closed['verified'] and closed['native_exit_code'] == 0 and closed['preferences_verified']
        assert load(p/'complete.json')['reached'] == 155
        proof = load(p/'source-structure-comparison.json')
        assert proof['verified'] and proof['expected_rows'] == 175
        protocol = load(p/'protocol.json')
        records = [json.loads(x) for x in (p/'economy-savings.ndjson').read_text(encoding='utf-8').splitlines()]
        selected = [r for r in records if r['kind'] == 'district-selection']
        captured = [r for r in selected if 'matrix' in r]
        first = {(r['player'],r['city']):r for r in reversed(captured)}
        matrices[amount] = first
        coverage = load(p/'loaded-customer-coverage.json')
        assert coverage['expected'] == coverage['actual'] == 30
        assert not (coverage['missing'] or coverage['unexpected'] or coverage['duplicates'])
        health = load(p/'economy-savings-progress.json')
        assert health['frozen'] and not (health['active'] or health['faults'] or health['buffered'])
        db = load(p/'loaded-customer-database.json')
        identity = deepcopy({k:db[k] for k in ('links','rules','yields','biases')})
        for r in identity['rules']:
            if r['ID'] == protocol['rule']: r['YieldChange'] = 'DOSE'
        for r in identity['links']:
            if r['YieldChangeId'] == protocol['rule']: r['YieldChange'] = 'DOSE'
        definitions[amount] = identity
        manifests[amount] = load(p/'installed-manifests.json')
        prime = first[(5,65536)]
        rows = {r['plot']:r for r in prime['matrix']['rows']}
        columns = prime['matrix']['columns']
        assert prime['turn'] == 150 and len(rows) == 37
        assert columns == len(rows[1379]['scoresQ8'])
        arms[str(amount)] = dict(directory=name, checkpoint_sha256=protocol['checkpoint']['sha256'],
            closure=closed, coverage=dict(expected=30,actual=30,invalid=coverage['invalid']),
            matrix_count=len(captured), native_records=len(records), native_health=health,
            source_structure=proof, first_primary=dict(turn=150,rows=37,columns=columns,
                adjacent_plot=1379,adjacent_valueQ8=rows[1379]['scoresQ8'][6],
                nonadjacent_plot=1601,nonadjacent_valueQ8=rows[1601]['scoresQ8'][6]),
            primary_choices=[{k:r.get(k) for k in ('turn','district','plot','totalQ8')}
                             for r in selected if (r['player'],r['city']) == (5,65536)],
            sql_sha256=sha(p/'diagnostic.sql'),native_journal_sha256=sha(p/'economy-savings.ndjson'))
    assert len({a['checkpoint_sha256'] for a in arms.values()}) == 1
    for dose in (1,4,8):
        assert definitions[dose] == definitions[0]
        changed = sorted((role,k.replace('\\','/')) for role in manifests[0]
            for k in set(manifests[0][role]) | set(manifests[dose][role])
            if manifests[0][role].get(k) != manifests[dose][role].get(k))
        assert changed == [('csc','Data/CSC_DIAG_CUSTOMER_STRENGTH.sql')], changed
        comparisons = []
        for key, a in matrices[0].items():
            b = matrices[dose][key]
            assert a['turn'] == b['turn'] == 150
            assert a['matrix']['columns'] == b['matrix']['columns']
            ra = {r['plot']:r for r in a['matrix']['rows']}
            rb = {r['plot']:r for r in b['matrix']['rows']}
            assert ra.keys() == rb.keys()
            cells = []
            for plot, x in ra.items():
                y = rb[plot]
                assert {k:v for k,v in x.items() if k!='scoresQ8'} == {k:v for k,v in y.items() if k!='scoresQ8'}
                for col, (before,after) in enumerate(zip(x['scoresQ8'], y['scoresQ8'])):
                    if before != after: cells.append(dict(plot=plot,district=col,beforeQ8=before,
                                                          afterQ8=after,deltaQ8=after-before))
            comparisons.append(dict(player=key[0],city=key[1],turn=150,flags_identical=True,
                cells=len(ra)*a['matrix']['columns'],changed=cells))
        arms[str(dose)]['first_native_differences_vs_off'] = comparisons
    # The broader gameplay-tag repair is a separate zero-turn integration arm;
    # it changes more edges and must not enter the isolated strength contrast.
    integration=root/'all-partners1-survey150'
    closure=load(integration/'session-closed.json')
    coverage=load(integration/'loaded-customer-coverage.json')
    structure=load(integration/'source-structure-comparison.json')
    assert closure['verified'] and closure['native_exit_code']==0 and closure['preferences_verified']
    assert coverage['complete'] and coverage['expected']==coverage['actual']
    assert structure['verified'] and load(integration/'complete.json')['reached']==150
    return dict(final_graph_integration=dict(directory=integration.name,closure=closure,
            coverage=coverage,source_structure=structure,turns_advanced=0),
        source='Continents map21951115/game32151115; source150; plays150–155',
        core_fix_commit='83e56d4c', offline_coverage=load(root/'offline-coverage-audit.json'),
        source_checkpoints_identical=True, private_rule_identities_and_other_definitions_identical=True,
        only_package_difference='Data/CSC_DIAG_CUSTOMER_STRENGTH.sql', arms=arms,
        conclusion='Amount1 adds45.699utility to adjacent1379 and changes native154 choice from1601 to1379;4/8 retain that same choice. Keep1 and the coverage repair.',
        construction_window='At inactive155 the target Hub is still a native selected plan; both footprints remain empty.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = analyse(args.root)
    args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({n:dict(value=a['first_primary']['adjacent_valueQ8']/256,
          selected=a['primary_choices'][-1]['plot'],matrices=a['matrix_count']) for n,a in result['arms'].items()},indent=2))
