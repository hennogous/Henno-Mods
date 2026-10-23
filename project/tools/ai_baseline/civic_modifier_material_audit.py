"""Independent archive/parity/score audit for C8 and its inert-guard follow-up.

Reads completed evidence only; never connects to Civilization or mutates mods.
Historical archive validation is separate from optional current source pins.
"""
import argparse
import collections
import csv
import hashlib
import json
from pathlib import Path
import sqlite3
import time


def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def rows(db):
    return {t: collections.Counter(db.execute('SELECT * FROM "'+t+'"'))
            for (t,) in db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")}


def scores(p):
    result = {}
    for r in csv.reader(p.read_text(errors='replace').splitlines()):
        r = [x.strip() for x in r]
        # Native candidate records have the literal Civic field.
        if len(r) >= 5 and r[2] == 'Civic' and r[0].isdigit() and 1 <= int(r[1]) <= 5:
            result[(int(r[0]), int(r[1]), r[3])] = float(r[4])
    return result


def audit(root, current_pins=False):
    assert read(root/'job-status.json')['status'] == 'complete'
    summary = {}
    inventories = {}
    for arm in ('off', 'on'):
        p = root/arm
        v = read(p/'source-version/version.json')
        counts = {}
        for field, folder in (('source_files','repository'), ('installed_files','installed'),
                              ('workshop_files','workshop-real-strategy'), ('rh_example_hashes','rh-readonly-examples')):
            for rel, expected in v[field].items():
                assert digest(p/'source-version'/folder/rel) == expected, (arm,field,rel)
            counts[field] = len(v[field])
        if current_pins:
            for rel, expected in read(p/'tuning-source-hashes.json').items():
                assert digest(Path(rel)) == expected, ('current pin',rel)
            for rel, expected in read(p/'controller-source-hashes.json').items():
                assert digest(Path(rel)) == expected, ('current controller pin',rel)
        for name in ('complete','native-database-validation','native-script-validation',
                     'observation-validation','material-case-validation',
                     'strategy-activation-validation','paired-preflight','guard-before','guard-after'):
            assert read(p/(name+'.json'))['passed'], (arm,name)
        obs = read(p/'observation-validation.json')
        assert obs['observations'] == 40 and obs['analyzed_turns'] == [71,78]
        restored = read(p/'preferences-restored.json')
        assert restored['verified'] and restored['auto_start'] is False
        assert read(p/'guard-before.json')['dormant_gate_false'] and read(p/'guard-after.json')['dormant_gate_false']
        db = sqlite3.connect(p/'native-gameplay.sqlite')
        inventories[arm] = rows(db)
        cases = read(p/'material-case-validation.json')['cases']
        assert [x['ready'] for x in cases] == [False,False,True,True,True]
        assert cases[2]['improvement'] == 'NONE' and cases[2]['resource'] == 'RESOURCE_CSC_FLAX'
        summary[arm] = dict(archive_counts=counts, observations=40, preferences=restored,
                            native_db_sha256=digest(p/'native-gameplay.sqlite'),
                            overlay_sha256=digest(p/'source-version/applied-overlay.sql'),
                            callback_sha256=digest(p/'source-version/applied-callback.lua'))
    changed = [t for t in inventories['off'] if inventories['off'][t] != inventories['on'][t]]
    assert changed == ['CivicModifiers'], changed
    added = inventories['on']['CivicModifiers'] - inventories['off']['CivicModifiers']
    removed = inventories['off']['CivicModifiers'] - inventories['on']['CivicModifiers']
    assert not removed and sum(added.values()) == 2
    assert {r[0] for r in added} == {'CIVIC_DIVINE_RIGHT'}
    for rel in ('game-01/initial-map.json','game-01/turn-071.json','original-preferences.json','material-case-validation.json'):
        assert read(root/'off'/rel) == read(root/'on'/rel), rel
    def canon(d):
        d['options'] = sorted(d['options'], key=lambda x:(x['player'],x['city'],x['quarter']))
        return d
    assert canon(read(root/'off/fixture-census.json')) == canon(read(root/'on/fixture-census.json'))
    callbacks = [(root/a/'source-version/applied-callback.lua').read_bytes() for a in ('off','on')]
    assert callbacks[0].replace(b'local CSC_C6_ENABLED=false',b'local CSC_C6_ENABLED=true') == callbacks[1], 'Other callback changes'
    measured = {a:scores(root/a/'native-logs/AI_GovtPolicies.csv') for a in ('off','on')}
    initial = {k:v for k,v in measured['off'].items() if k[0]==71}
    assert len(initial)==55
    assert all(measured['on'].get(k)==v for k,v in initial.items())
    delta = {p:measured['on'][(72,p,'CIVIC_DIVINE_RIGHT')]-measured['off'][(72,p,'CIVIC_DIVINE_RIGHT')] for p in range(1,6)}
    assert all(abs(delta[p]) < .05 for p in (1,2))
    assert all(delta[p] > .05 for p in (3,4,5))
    assert read(root/'installed-restored.json') == {'verified':True,'source_unchanged':True}
    summary.update(passed=True, audited_unix=time.time(), native_changed_tables=changed,
                   initial_records_identical=55, first_response_turn=72, target_deltas72=delta,
                   current_pins_checked=current_pins, combined_treatment=True,
                   caveat='Diagnostic valuation evidence, not natural play or lifecycle proof.')
    (root/'post-run-audit.json').write_text(json.dumps(summary,indent=2)+'\n')
    return summary


if __name__ == '__main__':
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--current-pins',action='store_true')
    a=p.parse_args();r=audit(a.root,a.current_pins)
    print(json.dumps({k:r[k] for k in ('passed','initial_records_identical','target_deltas72','current_pins_checked')}))
