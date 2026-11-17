"""Architecture regressions fail on misplaced terms and broken shared loading."""
import copy
import json
import re
from pathlib import Path
import sys
import tempfile
import unittest
import yaml

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
from sql_architecture import ROOT, load_contract, statements, validate_core, validate_pipeline
from validate_phase import CONTRACTS, validate_action_wiring


class CoreOwnershipTests(unittest.TestCase):
    def setUp(self):
        self.source = (ROOT/'Civ Supply Chains/Data/CSC_Q_BAKERS.sql').read_text(encoding='utf-8')

    def errors(self, source):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'core.sql'
            path.write_text(source, encoding='utf-8')
            return validate_core(path)

    def transaction(self):
        for tokens in statements(self.source):
            body = self.source[tokens[0].start():tokens[-1].end()]
            if body.startswith('INSERT INTO CSC_BuildingTransactions\n'):
                return body
        self.fail('Missing actual building transaction declaration')

    def test_both_current_quarters_obey_ownership(self):
        for quarter in ('BAKERS', 'TAILORS'):
            self.assertEqual(validate_core(ROOT/f'Civ Supply Chains/Data/CSC_Q_{quarter}.sql'), [])

    def test_terms_at_foot_of_file_are_rejected(self):
        body = self.transaction()
        errors = self.errors(self.source.replace(body, '', 1) + '\n' + body)
        self.assertTrue(any('belongs in section(s) [5]' in error for error in errors))

    def test_split_declaration_batches_are_rejected(self):
        body = self.transaction()
        errors = self.errors(self.source.replace(body, body + '\n' + body))
        self.assertTrue(any('combine 2 declaration batches' in error for error in errors))

    def test_copied_projection_and_persistent_schema_are_rejected(self):
        errors = self.errors(self.source + '\nCREATE TABLE CSC_CopiedSchema(A TEXT);\n'
                             'INSERT INTO CSC_Stage3CustomerTransactions(A) VALUES(1);')
        self.assertTrue(any('persistent tables' in error for error in errors))
        self.assertTrue(any('is generated' in error for error in errors))

    def test_comment_examples_do_not_count_as_sql(self):
        self.assertEqual(self.errors(self.source + '\n-- INSERT INTO CSC_Stage3CustomerTransactions VALUES(1);\n'), [])

    def test_missing_definition_value_label_is_rejected(self):
        source = re.sub(r'/\*\s*Cost,\s*\*/', '', self.source, count=1)
        self.assertTrue(any('definition value needs' in error for error in self.errors(source)))


class SharedPipelineTests(unittest.TestCase):
    def setUp(self):
        self.contract = load_contract()
        self.actions = json.loads((ROOT/'project/modbuddy/CivSupplyChains.actions.json').read_text(encoding='utf-8'))

    def errors(self):
        return validate_pipeline(ROOT, self.contract, self.actions)

    def owner(self, filename):
        return next(action for action in self.actions['blocks']['inGameActions']
                    if filename in action.get('files', []))

    def test_current_shared_pipeline_is_valid(self):
        self.assertEqual(self.errors(), [])

    def test_common_before_schema_inside_one_action_is_rejected(self):
        action = self.owner('Data/CSC_Q_ALL_Schema.sql')
        action['files'].reverse()
        self.assertTrue(any('schema must load before common' in error for error in self.errors()))

    def test_duplicate_registration_is_rejected(self):
        self.actions['blocks']['inGameActions'].append(copy.deepcopy(self.owner('Data/CSC_Q_ALL_Common.sql')))
        self.assertTrue(any('one file registration' in error for error in self.errors()))

    def test_optional_declarations_after_compilation_are_rejected(self):
        self.owner('Data/CSC_Q_TAILORS_MC_MODE.sql')['properties']['LoadOrder'] = '2501'
        self.assertTrue(any('before the transaction compiler' in error for error in self.errors()))

    def test_core_economy_cannot_be_gated_on_ce(self):
        self.owner('Data/CSC_Q_ALL_Schema.sql')['criteria'] = ['CSC_CE_SupplierExclusion']
        self.assertTrue(any('incorrect shared SQL criteria' in error for error in self.errors()))

    def test_retired_companion_cannot_be_registered(self):
        self.owner('Data/CSC_Q_ALL_Common.sql')['files'].append('Data/CSC_Q_TAILORS_TRANSACTIONS.sql')
        self.assertTrue(any('retired SQL input' in error for error in self.errors()))

    def test_schema_input_must_actually_define_the_shared_tables(self):
        self.contract['files']['schema']['file'] = self.contract['files']['common']['file']
        self.assertTrue(any('missing shared table definition' in error for error in self.errors()))


class ConsolidatedActionTests(unittest.TestCase):
    def setUp(self):
        self.wiring = {'actions': {'core': {'id': 'BothQuarters', 'type': 'UpdateDatabase',
            'file': 'Data/CSC_Q_TAILORS.sql', 'load_order': 100, 'criteria': []}}}
        self.action = {'id': 'BothQuarters', 'type': 'UpdateDatabase',
            'properties': {'LoadOrder': '100'}, 'files': ['Data/CSC_Q_BAKERS.sql', 'Data/CSC_Q_TAILORS.sql']}
        self.document = {'blocks': {'inGameActions': [self.action]}}

    def test_compatible_sibling_is_accepted(self):
        self.assertEqual(validate_action_wiring(self.document, self.wiring, {'core'}), [])

    def test_grouping_does_not_hide_criteria_or_duplicate_files(self):
        self.action['criteria'] = ['Unexpected']
        self.action['files'].append('Data/CSC_Q_TAILORS.sql')
        errors = validate_action_wiring(self.document, self.wiring, {'core'})
        self.assertTrue(any('criteria' in error for error in errors))
        self.assertTrue(any('action files' in error for error in errors))


class RouteProjectionOrderTests(unittest.TestCase):
    def setUp(self):
        self.contract = yaml.safe_load((ROOT/'project/specs/tailors/implementation.yaml').read_text(encoding='utf-8'))
        self.requirement = next(row for row in CONTRACTS.flatten_requirements(self.contract)
                                if row['id'] == 'I.STAGE3_TRADE')

    def errors(self):
        result = CONTRACTS.Validation()
        CONTRACTS.validate_trade_route_yield_presentation_requirement(
            self.requirement, {'YIELD_CULTURE': 1.0}, self.contract, result)
        return result.errors

    def test_late_database_projection_can_have_a_higher_order_than_ui_script(self):
        self.assertEqual(self.errors(), [])

    def test_projection_before_final_route_reader_is_rejected(self):
        self.contract['build_wiring']['actions']['trade_route_yield_presentation_suk']['load_order'] = 9999000
        self.assertTrue(any('after the final route reader' in error for error in self.errors()))


if __name__ == '__main__':
    unittest.main()
