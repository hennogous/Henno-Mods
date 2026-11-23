"""Check the 15-turn supplier qualification against explicit poll evidence."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from material_development_summary import (
    CE_CORE, add_construction_work, builder_followthrough, buyer_timelines, compare_buyer_readiness,
    dispatch_package_parity, summarise, worker_followthrough,
)


def row(plot, *, working=0, ready=True, legal=1, role='base', player=1):
    return dict(player=str(player), quarter='BAKERS', quarterPlot=str(plot), role=role,
                buyerReady=str(ready).lower(), legal=str(legal), working=str(working))


class BuyerReadinessTests(unittest.TestCase):
    def test_includes_shortages_and_counts_supply_on_opening_day(self):
        polls = {turn: [] for turn in range(1, 24)}
        for turn in polls:
            polls[turn] = [row(10, working=1), row(11), row(99, player=99, working=1)]
            if turn >= 3:
                polls[turn] += [row(12, working=int(turn >= 18), role='specialty')]
            if turn >= 9:
                polls[turn] += [row(13, working=1)]
        result = buyer_timelines(polls, {1}, 23)
        self.assertEqual(result['counts']['all'], dict(eligible=3, on_time=2, late_openings=1,
                                                      rate=2/3, working_at_endpoint=3))
        self.assertEqual(result['counts']['BAKERS/specialty']['on_time'], 1)
        self.assertEqual(result['counts']['specialty']['on_time'], 1)
        self.assertEqual(result['counts']['base']['eligible'], 2)
        self.assertEqual(result['buyers'][0]['opened'], result['buyers'][0]['first_working'])

    def test_recovery_tracks_last_supplier_and_an_unavailable_buyer_ends_the_episode(self):
        polls = {1: [row(10, working=2)], 2: [row(10, working=1)], 3: [row(10)],
                 4: [row(10, working=1)], 5: [row(10)], 6: [row(10, ready=False)], 7: []}
        result = buyer_timelines(polls, {1}, 7)
        self.assertEqual([episode['lost'] for episode in result['recoveries']], [3, 5])
        self.assertEqual(result['recoveries'][0]['turns_to_restore'], 1)
        self.assertEqual(result['recoveries'][1]['unavailable'], 6)
        self.assertIsNone(result['recoveries'][1]['restored'])

    def test_construction_requires_the_same_unfinished_buyer_on_either_side_of_work(self):
        polls = {
            1: [dict(row(10, ready=False, role='specialty'), constructing='CAFE'), row(11, ready=False)],
            2: [dict(row(10, ready=False, role='specialty', working=1), constructing='CAFE', workingPlots='20'),
                dict(row(11, ready=False, working=1), constructing='MILL')],
            3: [row(10, working=1, role='specialty'), row(11, working=1)],
        }
        result = buyer_timelines(polls, {1}, 3)
        self.assertEqual(result['prepared_during_construction'], [
            dict(player=1, plot=10, role='BAKERS/specialty', buyer='CAFE', when=2, suppliers=[20]),
        ])
        observed_work = dict(player=1, plot=20, turn=1, roles=['BAKERS/specialty'], quarter_plots=[10])
        unrelated_work = dict(observed_work, quarter_plots=[11])
        add_construction_work(result, [observed_work, unrelated_work])
        self.assertEqual(result['prepared_during_construction'][0]['work'], [observed_work])

    def test_missing_sample_cannot_qualify_and_poll_count_is_checked(self):
        result = buyer_timelines({1: [], 3: []}, {1}, 3)
        self.assertEqual(result, {'verified': False, 'missing_turns': [2]})
        lines = ['CSC_PLANNING_SUPPLIER_BUYER_POLL\tturn=1\tsource=poll\tbuyers=1']
        with self.assertRaisesRegex(ValueError, 'Incomplete supplier buyer census'):
            summarise(lines, {1}, 1, require_finished=False)

    def test_finished_census_tracks_the_exact_buyer_on_every_turn(self):
        lines = []
        for turn in range(1, 18):
            fields = dict(row(10, ready=turn >= 2, working=int(turn >= 2)), turn=turn, source='poll')
            buyer_record = 'CSC_PLANNING_SUPPLIER_BUYER\t' + '\t'.join(f'{k}={v}' for k, v in fields.items())
            lines.extend([buyer_record, f'CSC_PLANNING_SUPPLIER_BUYER_POLL\tturn={turn}\tsource=poll\tbuyers=1'])
        lines.append('CSC_PLANNING_FINISH\tturn=17\tincomplete=false')
        result = summarise(lines, {1}, 17)['buyer_readiness']
        self.assertTrue(result['verified'])
        self.assertEqual(result['counts']['base']['on_time'], 1)
        self.assertEqual(result['buyers'][0]['opened'], 2)
        with self.assertRaisesRegex(ValueError, 'Unclosed supplier buyer census'):
            summarise(lines[:-2], {1}, 17, require_finished=False)

    def test_qualification_requires_data_in_both_arms_and_accepts_exactly_75_percent(self):
        polls = {turn: [row(plot, working=int(plot < 3)) for plot in range(4)] for turn in range(1, 17)}
        measured = buyer_timelines(polls, {1}, 16)
        self.assertFalse(compare_buyer_readiness({'verified': False}, measured)['verified'])
        self.assertTrue(compare_buyer_readiness(measured, measured)['meets_target'])
        empty = buyer_timelines({turn: [] for turn in polls}, {1}, 16)
        self.assertFalse(compare_buyer_readiness(measured, empty)['meets_target'])

    def test_worker_receipt_keeps_offer_and_physical_work_separate(self):
        lines = [
            'CSC_AI_MATERIAL_WORKER_OFFER turn=1 version=1 player=1 city=4 plot=20 improvement=8 unit=9',
            'CSC_AI_MATERIAL_DEVELOPMENT_RECEIPT turn=2 version=1 {"version":1,"workerReady":1,'
            '"workerStart":1,"workerStartFirst":[1,4,20,8,9,18,1,0]}',
            'CSC_PLANNING_FINISH\tturn=2\tincomplete=false',
        ]
        result = summarise(lines, {1}, 2)
        evidence = worker_followthrough(result)
        sample = evidence['workerStart']['samples'][0]
        self.assertEqual(evidence['published_offers'], 1)
        self.assertEqual(sample['offer']['plot'], 20)
        self.assertIsNone(sample['later_plot_work'])
        # A different native improvement at the plot does not confirm work.
        result['work_history'] = [dict(player=1, plot=20, improvement_index=7, turn=2)]
        self.assertIsNone(worker_followthrough(result)['workerStart']['samples'][0]['later_plot_work'])
        result['work_history'].append(dict(player=1, plot=20, improvement_index=8, turn=2))
        self.assertEqual(worker_followthrough(result)['workerStart']['samples'][0]['later_plot_work']['turn'], 2)

    def test_worker_pair_links_loaded_dll_and_rejects_gameplay_drift(self):
        relative = 'Binaries\\Win64\\' + CE_CORE
        with TemporaryDirectory() as temporary:
            control, treatment = (Path(temporary)/name for name in ('control', 'treatment'))
            for folder in (control, treatment):
                folder.mkdir()
            binaries = {'control': {CE_CORE: 'base'}, 'treatment': {CE_CORE: 'dispatch'}}

            def write(folder, dll, gameplay):
                files = {'ce': {'files': {relative: {'sha256': dll}}},
                         'csc': {'files': {'Data\\CSC_Q_ALL.sql': {'sha256': gameplay}}}}
                (folder/'packages.json').write_text(json.dumps(files), encoding='utf-8')

            write(control, 'base', 'same')
            write(treatment, 'dispatch', 'same')
            self.assertTrue(dispatch_package_parity(control, treatment, binaries)['verified'])
            write(treatment, 'dispatch', 'changed')
            with self.assertRaisesRegex(ValueError, 'change only the CE'):
                dispatch_package_parity(control, treatment, binaries)
            write(treatment, 'different', 'same')
            with self.assertRaisesRegex(ValueError, 'Loaded CE fingerprint'):
                dispatch_package_parity(control, treatment, binaries)

    def test_retained_request_offers_can_predate_contingency_tag(self):
        historical = dict(version=1, player=1, city=4, plot=20, improvement=8, unit=9)
        modern = dict(historical, version=2, contingency=1)
        result = builder_followthrough(dict(offers={'REQUEST': [historical, modern]}, native={}))
        self.assertEqual(result['published_offers'],2)
        self.assertEqual(result['contingency_offers'],1)


if __name__ == '__main__':
    unittest.main()
