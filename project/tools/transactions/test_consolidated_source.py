"""Compare the complete economy/native graph to pre-cleanup gameplay hashes.

The reference was generated from the pre-consolidation working SQL on 17 Nov
2026 using this same loader. It includes core/Gold, Garden, M&C and replacement
combinations. Update it only after reviewing an intentional gameplay change.
"""
import hashlib
import itertools
import json
from pathlib import Path
import unittest

from population_catalogue_fixture import compile_catalogue


class ConsolidatedSourceTests(unittest.TestCase):
    def test_complete_native_graph_and_economic_catalogue_in_sixteen_configurations(self):
        reference = json.loads(Path(__file__).with_name('consolidation_qa_reference.json').read_text())
        for flags in itertools.product((False, True), repeat=4):
            config = dict(zip(('gold', 'lgd', 'mc', 'uniques'), flags))
            key = ':'.join(str(int(flag)) for flag in flags)
            db = compile_catalogue(**config)
            try:
                for table in reference['tables']:
                    with self.subTest(config=key, table=table):
                        rows = sorted((dict(row) for row in db.execute('SELECT * FROM ' + table)),
                                      key=lambda row: json.dumps(row, sort_keys=True))
                        digest = hashlib.sha256(json.dumps(rows, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
                        self.assertEqual(len(rows), reference['cases'][key][table]['rows'])
                        self.assertEqual(digest, reference['cases'][key][table]['sha256'])
            finally:
                db.close()


if __name__ == '__main__':
    unittest.main()
