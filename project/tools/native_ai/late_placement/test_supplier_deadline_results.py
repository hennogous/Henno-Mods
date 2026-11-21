import unittest

from supplier_deadline_results import read_tree_events, supplier_cases


class SupplierDeadlineTest(unittest.TestCase):
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
