"""No game on import: source identity and negative evidence parsing guards."""
import copy
import unittest
from driver import parse_world, validate_world


class SourceGuards(unittest.TestCase):
    def setUp(self):
        self.value = dict(turn=80, mapping=dict(buildingsDense=True, districtsDense=True),
            targets=[dict(player=5, city=65536, exists=True), dict(player=3, city=65536, exists=True)],
            sourceValidation=dict(valid=True))

    def test_exact_historical_source(self):
        self.assertTrue(validate_world(self.value, 80))

    def test_wrong_city_sparse_mapping_and_unqualified_source_fail(self):
        for change in ('city', 'sparse', 'source'):
            value = copy.deepcopy(self.value)
            if change == 'city':
                value['targets'][0]['city'] = 77
            elif change == 'sparse':
                value['mapping']['buildingsDense'] = False
            else:
                value['sourceValidation']['valid'] = False
            with self.assertRaises(ValueError):
                validate_world(value, 80)

    def test_empty_and_ambiguous_receipts_fail(self):
        for text in ('', 'CSC_BAKERS_COMPONENT_WORLD={}\nCSC_BAKERS_COMPONENT_WORLD={}\n'):
            with self.assertRaises(ValueError):
                parse_world(text)


if __name__ == '__main__':
    unittest.main()
