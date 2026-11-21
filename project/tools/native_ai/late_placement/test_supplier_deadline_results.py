from pathlib import Path
import sqlite3
from tempfile import TemporaryDirectory
import unittest

from supplier_deadline_results import counts, read_material_job_filter, read_tree_events, supplier_cases, with_early_preparation


class SupplierDeadlineTest(unittest.TestCase):
    def test_early_offer_proves_a_missing_supplier_before_common_eligibility(self):
        surveys = {
            turn: [dict(player='2', quarterPlot='15', quarter='BAKERS', role='base',
                        buyerReady='true' if turn >= 4 else 'false', legal='1' if turn >= 3 else '0',
                        legalPlots='16' if turn >= 3 else '', working='1' if turn >= 3 else '0',
                        workingPlots='16' if turn >= 3 else '')]
            for turn in range(1, 7)
        }
        log = ['CSC_AI_MATERIAL_PREPARATION turn=2 player=2 quarter=15 plot=16 class=base deltaQ8=3328']
        early = with_early_preparation(surveys, log)
        common, = supplier_cases(surveys, {}, {'2'}, 2)
        measured, = supplier_cases(early, {}, {'2'}, 2)
        self.assertEqual(common['cohort'], 'already_working_at_preparation')
        self.assertEqual(measured['cohort'], 'needed_work_at_preparation')
        self.assertEqual(measured['first_eligible'], 2)
        self.assertTrue(measured['by_opening']['working'])

    def test_deadline_uses_work_already_visible_at_the_survey(self):
        surveys = {
            turn: [dict(player='2', quarterPlot='15', quarter='BAKERS', role='base',
                        buyerReady='true' if turn >= 3 else 'false', legal='1', legalPlots='16',
                        working='1' if turn == 4 else '0', workingPlots='16' if turn == 4 else '')]
            for turn in range(1, 6)
        }
        trees = [
            '2, 2, City A, Build City Improvement, SUCCESS, Reserve Plot, Reserving plot 6 1',
            '3, 2, City A, Build City Improvement, SUCCESS, Find Available Unit, Found: UNIT_BUILDER',
            '5, 2, City B, Build City Improvement, SUCCESS, Reserve Plot, Reserving plot 6 1',
        ]
        events = read_tree_events(trees, {'2'}, 10, 5)
        case, = supplier_cases(surveys, events, {'2'}, 2)
        self.assertEqual(case['by_opening'], dict(reserved=True, assigned=False, working=False, ever_worked=False))
        self.assertEqual(case['by_deadline'], dict(reserved=True, assigned=True, working=False, ever_worked=True))

    def test_assignment_can_start_on_an_existing_reservation(self):
        surveys = {
            turn: [dict(player='2', quarterPlot='15', quarter='BAKERS', role='base',
                        buyerReady='true' if turn >= 3 else 'false', legal='1' if turn >= 3 else '0',
                        legalPlots='16' if turn >= 3 else '', working='0', workingPlots='')]
            for turn in range(1, 6)
        }
        trees = [
            '2, 2, City A, Build City Improvement, SUCCESS, Reserve Plot, Reserving plot 6 1',
            '3, 2, City A, Build City Improvement, SUCCESS, Find Available Unit, Found: UNIT_BUILDER',
        ]
        events = read_tree_events(trees, {'2'}, 10, 5)
        case, = supplier_cases(surveys, events, {'2'}, 2)
        self.assertEqual(case['first_observed'], dict(reserved=3, assigned=4))
        self.assertTrue(case['by_opening']['reserved'])

    def test_supplier_that_becomes_legal_after_opening_counts_with_its_shorter_window(self):
        surveys = {
            turn: [dict(player='2', quarterPlot='15', quarter='TAILORS', role='specialty',
                        buyerReady='true', legal='1' if turn >= 2 else '0', legalPlots='16' if turn >= 2 else '',
                        working='1' if turn >= 4 else '0', workingPlots='16' if turn >= 4 else '')]
            for turn in range(1, 6)
        }
        case, = supplier_cases(surveys, {}, {'2'}, 3)
        self.assertTrue(case['eligible_after_opening'])
        self.assertEqual(case['first_eligible'], 2)
        self.assertFalse(case['by_opening']['working'])
        self.assertTrue(case['by_deadline']['working'])
        summary = counts([case])['specialty']
        self.assertEqual(summary['needed_work_at_preparation'], 1)
        self.assertEqual(summary['eligible_after_opening']['working_by_deadline_after_needed_work'], 1)

        too_late, = supplier_cases(surveys, {}, {'2'}, 0)
        self.assertEqual(too_late['cohort'], 'no_legal_supplier_by_deadline')
        self.assertNotIn('eligible_after_opening', too_late)

    def test_matching_plot_with_unmapped_improvement_does_not_count(self):
        with TemporaryDirectory() as temp:
            database = Path(temp) / 'gameplay.sqlite'
            db = sqlite3.connect(database)
            db.executescript('''
                CREATE TABLE Improvement_ValidResources (ResourceType TEXT, ImprovementType TEXT);
                INSERT INTO Improvement_ValidResources VALUES ('RESOURCE_CSC_FLAX', 'IMPROVEMENT_FARM');
            ''')
            db.close()
            material_job = read_material_job_filter([
                'CSC_PLANNING_MATERIAL_STATE\tplayer=2\tmaterialPlot=16\tturn=1\tsequence=1\tresource=RESOURCE_CSC_FLAX',
            ], database)
            trees = [
                '2, 2, City A, Build City Improvement, SUCCESS, Decode Trigger, Improve: IMPROVEMENT_SOLAR_FARM; Value: 85',
                '2, 2, City A, Build City Improvement, SUCCESS, Reserve Plot, Reserving plot 6 1',
                '2, 2, City A, Build City Improvement, SUCCESS, Find Available Unit, Found: UNIT_BUILDER',
                '3, 2, City A, Build City Improvement, SUCCESS, Decode Trigger, Improve: IMPROVEMENT_FARM; Value: 82',
                '3, 2, City A, Build City Improvement, SUCCESS, Reserve Plot, Reserving plot 6 1',
                '4, 2, City A, Build City Improvement, SUCCESS, Find Available Unit, Found: UNIT_BUILDER',
            ]
            actual = read_tree_events(trees, {'2'}, 10, 5, material_job)
            self.assertEqual(actual['2', 16], [(3, 'reserved', 3), (4, 'assigned', 3)])
