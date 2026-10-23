"""Independent completed natural OFF/ON evidence audit; no game connection."""
import argparse
import csv
import json
import sqlite3
import time
from pathlib import Path
from civic_modifier_material_audit import read, digest, rows


PLANS = [(1, 'CIVIC_FEUDALISM'), (2, 'CIVIC_MEDIEVAL_FAIRES'),
         (3, 'CIVIC_URBANIZATION'), (4, 'CIVIC_NAVAL_TRADITION'),
         (5, 'CIVIC_DIVINE_RIGHT'), (6, 'CIVIC_OPERA_BALLET')]
PRIMARY = [71, 75, 100, 125, 150, 175, 200, 225, 250]
BUILDERS = [71, 100, 150, 200, 250]


def audit(root):
    assert read(root/'job-status.json')['status'] == 'complete'
    assert read(root.parent/'supervisor.json')['status'] == 'complete'
    recovery = read(root/'controller-recovery-v2/recovery-audit.json')
    assert recovery['passed'] and recovery['executed_tools_unchanged_before_repair']
    native = {}; versions = {}; result = {}
    for arm in ('off', 'on'):
        p = root/arm; version = read(p/'source-version/version.json')
        versions[arm] = version; counts = {}
        for field, folder in [('source_files','repository'), ('installed_files','installed'),
                              ('workshop_files','workshop-real-strategy'), ('rh_example_hashes','rh-readonly-examples')]:
            for rel, expected in version[field].items():
                assert digest(p/'source-version'/folder/rel) == expected, (arm, field, rel)
            counts[field] = len(version[field])
        for name in ('complete', 'validation', 'native-database-validation', 'native-script-validation',
                     'paired-preflight', 'observation-validation'):
            assert read(p/(name+'.json'))['passed'], (arm, name)
        assert not version['fixtures'] and version['natural_play']
        pref = read(p/'preferences-restored.json')
        assert pref['verified'] and pref['auto_start'] is False
        obs = read(p/'observations.json'); assert not obs['errors'] and not obs['native']['errors']
        pairs = {(x['turn'], x['player']) for x in obs['history']}
        assert len(pairs) == len(obs['history'])
        expected = {(t, pid) for t in range(71,250) for pid in range(1,6)}
        missing = expected-pairs; defeats = {x['player']:x['turn'] for x in obs['defeats']}
        assert not pairs-expected and all(pid in defeats and t >= defeats[pid] for t,pid in missing)
        assert read(p/'observation-validation.json')['actual_endpoint'] == 250
        for t in PRIMARY:
            s = read(p/f'game-01/turn-{t:03d}.json'); assert s['turn'] == t and not s['errors']
            for city in s['cities']:
                for i,_ in PLANS:
                    assert abs(city['yields'][f'YIELD_CSC_TEST_LONG_{i}']) < 1e-6
        assert not read(p/'game-01/turn-071.json')['cities'], 'Injected initial cities'
        for t in BUILDERS:
            b = read(p/f'builders-{t:03d}.json'); assert b['turn'] == t and not b['errors']
            for player in b['players']:
                assert player['count'] == len(player['builders'])
                assert player['charges'] == sum(x['charges'] for x in player['builders'])
        saves = {}
        for f,turn in [('initial-save.json',71),('endpoint-save.json',250)]:
            meta = read(p/'game-01'/f); saved = p/'game-01'/Path(meta['path']).name
            assert meta['actual_turn'] == turn and digest(saved) == meta['sha256']
            saves[str(turn)] = meta['sha256']
        autosaves=[{'file':f.name,'filename_turn':int(f.stem.rsplit('_',1)[1]),
                    'sha256':digest(f),'bytes':f.stat().st_size}
                   for f in sorted((p/'endpoint-autosaves').glob('*.Civ6Save'))]
        assert [x['filename_turn'] for x in autosaves] == [248,249,250]
        db = sqlite3.connect(p/'native-gameplay.sqlite'); native[arm] = rows(db)
        gate = db.execute("SELECT a.Value,r.Inverse FROM RequirementSetRequirements s JOIN Requirements r ON r.RequirementId=s.RequirementId JOIN RequirementArguments a ON a.RequirementId=r.RequirementId WHERE s.RequirementSetId='CSC_TEST_LONG_NEVER' AND a.Name='CivicType' ORDER BY r.Inverse").fetchall()
        assert gate == [('CIVIC_FUTURE_CIVIC',0),('CIVIC_FUTURE_CIVIC',1)]
        assert db.execute("SELECT RequirementSetType FROM RequirementSets WHERE RequirementSetId='CSC_TEST_LONG_NEVER'").fetchone() == ('REQUIREMENTSET_TEST_ALL',)
        for i,_ in PLANS:
            flags = db.execute('SELECT ThresholdValue,Forbidden,Disqualifier,Exclusive FROM StrategyConditions WHERE StrategyType=? ORDER BY Exclusive',(f'STRATEGY_CSC_TEST_LONG_{i}',)).fetchall()
            assert flags == [(i,0,0,0),(100+i,1,0,1)]
            assert db.execute('SELECT DefaultValue FROM Yields WHERE YieldType=?',(f'YIELD_CSC_TEST_LONG_{i}',)).fetchone() == (1,)
            assert db.execute('SELECT Value FROM AiFavoredItems WHERE Item=? ORDER BY Value',(f'YIELD_CSC_TEST_LONG_{i}',)).fetchall() == [(-100,),(100,)]
        assert db.execute("SELECT DefaultValue FROM PseudoYields WHERE PseudoYieldType='PSEUDOYIELD_IMPROVEMENT'").fetchone() == (90,)
        assert db.execute("SELECT Value FROM AiFavoredItems WHERE ListType='UnitPriorityBoosts' AND Item='UNIT_BUILDER'").fetchall() == [(50,)]
        assert all(x['active'] == (arm == 'on' and x['eligible']) for x in obs['native']['transitions'])
        assert all(not x['active'] for x in obs['native']['transitions'] if x['owned'])
        for pid in range(1,6):
            for i,_ in PLANS:
                assert obs['native']['calls'].get(f'{pid}:{i}:primary',0) > 0
                assert obs['native']['calls'].get(f'{pid}:{i}:inverse',0) > 0
        # OFF's executable pins were independently checked before the documented repair.
        # ON's actual current executable pins must still match; uninstalled worktree
        # changes are recorded separately and never written into installed gameplay.
        source_changes = []
        if arm == 'on':
            for name in ('tuning-source-hashes','controller-source-hashes'):
                for rel,h in read(p/(name+'.json')).items():
                    if digest(Path(rel)) != h:
                        assert 'Civ Supply Chains' in Path(rel).parts or 'modbuddy' in Path(rel).parts
                        source_changes.append(rel)
        logcheck = read(p/'native-script-validation.json')
        result[arm] = {'archive_counts':counts,'observations':len(pairs),'defeat_censored':len(missing),
                       'endpoint':250,'primary':PRIMARY,'builders':BUILDERS,'save_sha256':saves,
                       'autosaves':autosaves,'autosave_turn_source':'Filename; not independently reloaded. Named endpoint actual turn verified natively.',
                       'preferences':pref,'private_city_yields_zero':True,
                       'retained_localization_duplicates':logcheck.get('localization_duplicate_count',0),
                       'uninstalled_source_changes_since_archive':source_changes,
                       'native_sha256':digest(p/'native-gameplay.sqlite'),
                       'overlay_sha256':digest(p/'source-version/applied-overlay.sql'),
                       'callback_sha256':digest(p/'source-version/applied-callback.lua')}
        db.close()
    assert native['off'].keys() == native['on'].keys()
    changed = [t for t in native['off'] if native['off'][t] != native['on'][t]]
    assert changed == ['CivicModifiers'], changed
    added = native['on']['CivicModifiers']-native['off']['CivicModifiers']
    assert not native['off']['CivicModifiers']-native['on']['CivicModifiers']
    expected = {(civic,f'CSC_TEST_LONG_CIVIC_{i}_{j}') for i,civic in PLANS for j in (1,2)}
    assert set(added) == expected and sum(added.values()) == 12
    for rel in ('game-01/initial-map.json','game-01/turn-071.json','original-preferences.json'):
        assert read(root/'off'/rel) == read(root/'on'/rel),rel
    provenance = read(root/'on/same-world-provenance.json')
    assert provenance['sha256'] == result['off']['save_sha256']['71']
    assert digest(Path(provenance['pristine_origin'])) == provenance['sha256']
    cb = [(root/a/'source-version/applied-callback.lua').read_bytes() for a in ('off','on')]
    assert cb[0].replace(b'local enabled=false',b'local enabled=true') == cb[1]
    sql = [(root/a/'source-version/applied-overlay.sql').read_text() for a in ('off','on')]
    expected_lines = {f"INSERT INTO CivicModifiers (CivicType,ModifierId) VALUES ('{c}','{m}');" for c,m in expected}
    assert '\n'.join(x for x in sql[1].splitlines() if x not in expected_lines) == '\n'.join(sql[0].splitlines())
    # All actually installed pair files are equal except the two intentional overlays.
    differing = []
    for rel,h in versions['off']['installed_files'].items():
        assert rel in versions['on']['installed_files']
        if h != versions['on']['installed_files'][rel]:differing.append(rel)
    ai = ['Data/CSC_AI.sql','Lua_UI/AI/CSC_AI_Research.lua']
    assert {x.replace('\\','/') for x in differing} == set(ai)
    installed = Path.home()/"Documents/My Games/Sid Meier's Civilization VI/Mods/Civ Supply Chains"
    for rel in ai:
        original = root/'original-installed'/rel
        assert (installed/rel).read_bytes() == original.read_bytes()
        for arm in ('off','on'):
            applied = (root/arm/'source-version/installed'/rel).read_bytes()
            suffix = ('\n'+sql[('off','on').index(arm)]).encode() if rel.endswith('.sql') else cb[('off','on').index(arm)]
            assert applied == original.read_bytes()+suffix
    restore = read(root/'installed-restored.json')
    assert restore['verified'] and restore['baseline_reference_unchanged']
    autoplay0 = []
    for row in csv.reader((root/'on/native-logs/AI_Victories.csv').read_text().splitlines()):
        row=[x.strip() for x in row]
        if len(row)>=4 and row[1]=='0' and row[2].startswith('STRATEGY_CSC_TEST_LONG_'):
            autoplay0.append(row)
    result.update(passed=True,audited_unix=time.time(),changed_native_tables=changed,
                  added_civic_attachments=12,installed_pair_changed_files=differing,
                  initial_world_census_preferences_identical=True,callback_only_enabled_literal=True,
                  off_recovered_offline_without_replay=True,restoration=restore,
                  intended_five_player_only_scope_passed=not autoplay0,
                  autoplay_player0_guidance_events=autoplay0,
                  scope_deviation='Player0 also followed two guidance strategies under autoplay. Structural/data checks pass; five-player-only treatment scope does not.' if autoplay0 else None,
                  note='One save-derived paired seed; six combined channels. Valuation and natural choices are separate outcomes.')
    (root/'post-run-audit.json').write_text(json.dumps(result,indent=2)+'\n')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser();parser.add_argument('root',type=Path)
    out = audit(parser.parse_args().root)
    print(json.dumps({k:out[k] for k in ('passed','changed_native_tables','added_civic_attachments','restoration')}))
