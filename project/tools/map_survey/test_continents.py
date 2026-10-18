"""Material semantics and cross-border support in the continent census."""
import unittest
from continent_analysis import continent_census


class ContinentCensusTests(unittest.TestCase):
    def fixture(self, blocked=False):
        def plot(i, continent, neighbors, **kw):
            return dict(index=i, continent=continent, neighbors=neighbors, water=False, impassable=False, hills=False, **kw)
        data = {'resources': [{'type': 'SILVER', 'class': 'RESOURCECLASS_LUXURY'}, {'type': 'FISH', 'class': 'RESOURCECLASS_BONUS'}],
                'features': [], 'harvests': [], 'continents': [{'index': 0, 'name': 'West'}, {'index': 1, 'name': 'East'}],
                'plots': [plot(0, 0, [1, 2]), plot(1, 1, [0], resource='SILVER'), plot(2, -1, [0], resource='FISH')]}
        data['plots'][1]['hills'] = True; data['plots'][2]['water'] = True
        if blocked: data['plots'][0]['resource'] = 'SILVER'
        definitions = {'HILLS': {'base': {'hills': True}, 'spec': {'resources': ['SILVER']}},
                       'FISH': {'base': {'resources': ['FISH']}, 'spec': {'resources': ['ABSENT']}}}
        return data, definitions

    def test_sources_can_support_candidates_across_continent_borders(self):
        census = continent_census(*self.fixture()); west = next(c for c in census if c['id'] == 0)
        hills = next(q for q in west['quarters'] if q['quarter'] == 'HILLS')
        self.assertEqual(hills['base_source_tiles'], 0)
        self.assertEqual(hills['land_both'], 1)
        self.assertEqual(hills['land_both_clusters'], 1)
        self.assertEqual(hills['land_both_distinct'], 0)

    def test_base_support_does_not_require_specialty_and_can_come_from_water(self):
        west = next(c for c in continent_census(*self.fixture()) if c['id'] == 0)
        fish = next(q for q in west['quarters'] if q['quarter'] == 'FISH')
        self.assertEqual(fish['common_clearable_base'], 1)
        self.assertEqual(fish['common_clearable_base_only'], 1)
        self.assertEqual(fish['common_clearable_both'], 0)

    def test_luxury_blocker_changes_clearing_counts_without_changing_geography(self):
        west = next(c for c in continent_census(*self.fixture(True)) if c['id'] == 0)
        hills = next(q for q in west['quarters'] if q['quarter'] == 'HILLS')
        self.assertEqual(hills['land_both'], 1)
        self.assertEqual(hills['common_clearable_both'], 0)
        self.assertEqual(west['land_luxury_types'], 1)


if __name__ == '__main__': unittest.main()
