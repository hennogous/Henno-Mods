from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest

from later_stage_results import _recovered_measurements, comparable_services, service_durations, stage_census, verify_policy


class ServiceDurations(unittest.TestCase):
    def test_counts_physical_links_and_reports_missing_turns(self):
        log = '\n'.join((
            'UI: CSC_MILESTONE_SERVICE_LINK\t40\t1\tBAKERS\t2\tSTOREKEEPER\t45\t90',
            'UI: CSC_MILESTONE_SERVICE_END\t40\t1\t0',
            'UI: CSC_MILESTONE_UNLOCK\t40\t1\tcivic\tCIVIC_FEUDALISM',
            'UI: CSC_MILESTONE_SERVICE_LINK\t42\t1\tBAKERS\t2\tSTOREKEEPER\t45\t90',
            'UI: CSC_MILESTONE_SERVICE_LINK\t42\t1\tBAKERS\t2\tSTOREKEEPER\t46\t90',
            'UI: CSC_MILESTONE_SERVICE_END\t42\t2\t0',
            'UI: CSC_MILESTONE_SERVICE_END\t43\t0\t0',
        ))
        result = service_durations(log, 40, 44)
        self.assertEqual(result['observed_turns'], [40, 42, 43])
        self.assertEqual(result['missing_turns'], [41])
        self.assertEqual(result['totals'], [dict(quarter='BAKERS', stage=2, active_link_turns=3)])
        self.assertEqual([chain['active_turns'] for chain in result['chains']], [2, 1])
        self.assertEqual(result['unlocked'][0]['topic'], 'CIVIC_FEUDALISM')

    def test_rejects_an_incomplete_native_snapshot(self):
        for line in ('CSC_MILESTONE_SERVICE_END\t40\t1\t0',
                     'CSC_MILESTONE_SERVICE_FAULT\t40\tError'):
            with self.subTest(line=line), self.assertRaises(ValueError):
                service_durations(line, 40, 41)

    def test_exposes_an_ambiguous_native_turn_without_counting_it(self):
        result = service_durations('CSC_MILESTONE_SERVICE_END\t40\t0\t1', 40, 41)
        self.assertEqual(result['ambiguous_turns'], {40: 1})
        self.assertEqual(result['observed_turns'], [])
        self.assertEqual(result['missing_turns'], [40])

    def test_matched_comparison_uses_only_common_observed_turns(self):
        stock = dict(observed_turns=[40, 42], chains=[dict(quarter='BAKERS', stage=2, turns=[40, 42])])
        combined = dict(observed_turns=[40, 41], chains=[dict(quarter='BAKERS', stage=2, turns=[41])])
        result = comparable_services(stock, combined)
        self.assertEqual(result['common_turns'], [40])
        self.assertEqual(result['stock'], [dict(quarter='BAKERS', stage=2, chains=1, turns=1)])
        self.assertEqual(result['combined'], [])


class Census(unittest.TestCase):
    def test_two_quarters_share_one_customer_host(self):
        rows = [
            ('QUARTER', 'BAKERS\t1\t2\t45\ttrue\tfalse\tfalse\t0\t0\t0'),
            ('QUARTER', 'BAKERS\t1\t2\t46\ttrue\tfalse\tfalse\t0\t0\t0'),
            ('PRODUCER', '45\t4\tCAFE\t2'),
            ('PRODUCER', '46\t4\tCAFE\t2'),
            ('CUSTOMER', '45\t47\t4\tDISTRICT_ENTERTAINMENT_COMPLEX\ttrue\t2'),
            ('CUSTOMER', '46\t47\t4\tDISTRICT_ENTERTAINMENT_COMPLEX\ttrue\t2'),
            ('POPULATION_EXCHANGE', '45\t47\t4\tCAFE_ZOO\t2\t2'),
        ]
        stage = stage_census(rows)['BAKERS']['stages'][2]
        self.assertEqual(stage['customer_hosts'], 1)
        self.assertEqual(stage['physical_exchange_pairs'], 2)
        self.assertEqual(stage['positive_population_exchanges'], 1)


class CampaignPolicy(unittest.TestCase):
    def test_stock_requires_both_policy_paths_withheld(self):
        native = dict(ready=1, faults=0, enabled=0, version=0, entries=0, matched=0, changed=0)
        database = dict(links=[], rules=[], yields=[], biases=[])
        timing = dict(publication_attempts=0, published_packets=0)
        verify_policy(native, database, timing, untuned=True)
        for inputs in ((dict(native, version=1), database, timing),
                       (native, dict(database, links=[1]), timing),
                       (native, database, dict(timing, publication_attempts=1))):
            with self.subTest(inputs=inputs), self.assertRaisesRegex(ValueError, 'Stock arm'):
                verify_policy(*inputs, untuned=True)

    def test_combined_requires_policy_and_customer_sql(self):
        native = dict(ready=1, faults=0, enabled=1, version=250)
        timing = dict(published_packets=250)
        verify_policy(native, dict(links=[1]), timing, untuned=False)
        with self.assertRaisesRegex(ValueError, 'Combined arm'):
            verify_policy(native, dict(links=[]), timing, untuned=False)


class RecoveredCampaign(unittest.TestCase):
    def test_uses_only_saved_prefix_and_deduplicates_same_chain_across_reload(self):
        with tempfile.TemporaryDirectory() as directory:
            before, after = (Path(directory)/part for part in ('original', 'resume'))
            before.mkdir()
            after.mkdir()

            def write(side, name, value):
                (side/name).write_text(json.dumps(value), encoding='utf-8')

            save = b'CIV6 pinned input'
            (before/'turn-50.Civ6Save').write_bytes(save)
            checkpoint = dict(verified=True, turn=50, sha256=sha256(save).hexdigest(), unique_name='exact')
            write(before, 'checkpoint-50.json', checkpoint)
            write(after, 'continuation.json', dict(source=str(before), at=50, source_checkpoint=checkpoint))
            write(after, 'source-structure-comparison.json', dict(verified=True))
            write(before, 'session-closed.json', dict(verified=True))
            write(before, 'session-source-ready.json', dict(verified=True, caller_eligibility_verified=True, turn=1))
            write(before, 'loaded-native-customer-database.json', dict(links=[1]))
            protocol = {key: None for key in ('map', 'map_size', 'map_seed', 'game_seed', 'input_digests',
                       'extra_mods', 'native_profile', 'untuned', 'external_policy', 'gameplay_interventions',
                       'service_observation')}
            for side in (before, after):
                write(side, 'source.json', dict(native=dict(ready=1, faults=0, enabled=1, version=1)))
                write(side, 'loaded-modules.json', {'CE': {'sha256': 'same engine'}})
            write(before, 'protocol.json', protocol)
            write(after, 'protocol.json', dict(protocol, natural_continuation=True, continuation_start=50))
            for turn in (25, 50):
                write(before, f'full-census-{turn}.json', dict(rows=[]))
            write(after, 'stage-census.json', {'250': {}})

            def sample(turn):
                return (f'CSC_MILESTONE_SERVICE_LINK\t{turn}\t1\tBAKERS\t2\tSTOREKEEPER\t45\t90\n'
                        f'CSC_MILESTONE_SERVICE_END\t{turn}\t1\t0\n'
                        f'CSC_AI_PROCESSING turn={turn} published=1 ok=1 wallMicros=500\n')

            (before/'Lua.log').write_text(sample(49)+sample(50)+'CSC_EXACT_CHECKPOINT_COMPLETE\texact\ttrue\n'
                                          +sample(51), encoding='utf-8')
            (after/'Lua.log').write_text(sample(50)+sample(52), encoding='utf-8')
            combined = _recovered_measurements(before, after)
            self.assertEqual(list(combined['census']), ['25', '50', '250'])
            self.assertEqual(len(combined['services']['chains']), 1)
            self.assertEqual(combined['services']['chains'][0]['turns'], [49, 50, 52])
            self.assertEqual(combined['performance']['published_packets'], 3)
