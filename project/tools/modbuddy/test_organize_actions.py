"""Protect loading contracts while making the action list easier to maintain."""
import copy
import json
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

from civ6proj_actions import canonical_data, export_json
from organize_actions import organize, order

ROOT = Path(__file__).resolve().parents[3]


def action(identifier, kind='UpdateDatabase', phase='100', **extra):
    return dict(id=identifier, type=kind, properties={'LoadOrder': phase},
                files=[identifier + '.sql'], **extra)


class OrganizerTests(unittest.TestCase):
    def test_numeric_phase_then_type_then_id(self):
        actions = [action('Z', phase='9'), action('B', phase='100'),
                   action('A', phase='100'), action('0', 'UpdateText')]
        self.assertEqual([a['id'] for a in sorted(actions, key=order)], ['Z', 'A', 'B', '0'])

    def test_criteria_properties_and_extra_metadata_prevent_merging(self):
        base = action('CSC_Q_BAKERS')
        for difference in ({'criteria': ['Mode']}, {'properties': {'LoadOrder': '101'}},
                           {'properties': {'LoadOrder': '100', 'Extra': '1'}},
                           {'extraNodes': [{'tag': 'Custom'}]}):
            other = action('CSC_Q_TAILORS')
            other.update(difference)
            with self.subTest(difference=difference):
                result, mergers = organize([base, other])
                self.assertEqual(len(result), 2)
                self.assertFalse(mergers)

    def test_matching_definitions_merge_without_mutating_input_or_file_order(self):
        inputs = [action('CSC_Q_TAILORS'), action('CSC_Q_BAKERS')]
        inputs[1]['files'] = ['Schema.sql', 'Common.sql']
        original = copy.deepcopy(inputs)
        result, mergers = organize(inputs)
        self.assertEqual(inputs, original)
        self.assertEqual(result[0]['id'], 'CSC_Q_ALL_Definitions')
        self.assertEqual(result[0]['files'], ['Schema.sql', 'Common.sql', 'CSC_Q_TAILORS.sql'])
        self.assertEqual(len(mergers), 1)

    def test_context_creating_actions_remain_individual(self):
        for kind in ('AddGameplayScripts', 'AddUserInterfaces', 'ReplaceUIScript'):
            result, mergers = organize([action('A', kind), action('B', kind)])
            self.assertEqual(len(result), 2)
            self.assertFalse(mergers)

    def test_missing_order_requires_a_deliberate_choice(self):
        source = action('Unknown')
        source['properties'] = {}
        with self.assertRaisesRegex(ValueError, 'Choose a load order'):
            organize([source])

    def test_documented_implicit_orders_become_explicit(self):
        for identifier, expected in (('Settings', '100'), ('Settings_Text', '100'),
                                     ('UpdateIcons', '100'), ('CSC_QuarterPedia', '490')):
            source = action(identifier)
            source['properties'] = {}
            result, _ = organize([source])
            self.assertEqual(result[0]['properties']['LoadOrder'], expected)


class ShippingManifestTests(unittest.TestCase):
    def setUp(self):
        self.project = ROOT / 'Civ Supply Chains/Civ Supply Chains.civ6proj'
        self.manifest = json.loads((ROOT / 'project/modbuddy/CivSupplyChains.actions.json').read_text())

    def test_generated_project_matches_json_and_all_actions_are_sorted(self):
        self.assertEqual(canonical_data(export_json(self.project)), canonical_data(self.manifest))
        for name in ('frontEndActions', 'inGameActions'):
            actions = self.manifest['blocks'][name]
            self.assertEqual(actions, sorted(actions, key=order))
            self.assertEqual(len(actions), len({a['id'] for a in actions}))

    def test_action_files_exist_and_are_packaged(self):
        tree = ET.parse(self.project)
        ns = {'m': 'http://schemas.microsoft.com/developer/msbuild/2003'}
        contents = {item.attrib['Include'].replace('\\', '/')
                    for item in tree.findall('.//m:Content', ns)}
        for name in ('frontEndActions', 'inGameActions'):
            for entry in self.manifest['blocks'][name]:
                for filename in entry.get('files', []):
                    # ModBuddy expands this build-generated art dependency token.
                    if filename == '(Mod Art Dependency File)':
                        continue
                    with self.subTest(action=entry['id'], file=filename):
                        self.assertIn(filename, contents)
                        self.assertTrue((self.project.parent / filename).is_file())

    def test_schema_precedes_common_in_one_early_action(self):
        actions = self.manifest['blocks']['inGameActions']
        shared = next(a for a in actions if a['id'] == 'CSC_Q_ALL')
        self.assertEqual(shared['files'], ['Data/CSC_Q_ALL_Schema.sql', 'Data/CSC_Q_ALL_Common.sql'])
        self.assertLess(int(shared['properties']['LoadOrder']), 100)


if __name__ == '__main__':
    unittest.main()
