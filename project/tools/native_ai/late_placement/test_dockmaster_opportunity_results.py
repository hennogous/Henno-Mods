"""Coastal summaries deduplicate layouts and preserve unknown Harbor quality."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from dockmaster_opportunity_results import analyse


class CoastalResults(unittest.TestCase):
    def capture(self,root,extended):
        rows=['CSC_COAST_META\t250\t43\t4\t1',
              'CSC_COAST_BASE\t0\tRESOURCE_CSC_FLAX\t1\t0\t0\t2\t1:2,1:3',
              'CSC_COAST_MAP\t0\t0\t0\tTERRAIN_GRASS\tNONE\tfalse\tfalse\tfalse\t1\t7\tNONE\tRESOURCE_CSC_FLAX\t1',
              'CSC_COAST_MAP\t1\t1\t0\tTERRAIN_GRASS\tNONE\tfalse\tfalse\tfalse\t1\t7\tNONE\tNONE\t-1',
              'CSC_COAST_MAP\t2\t2\t0\tTERRAIN_COAST\tNONE\ttrue\tfalse\tfalse\t1\t7\tNONE\tNONE\t-1',
              'CSC_COAST_MAP\t3\t3\t0\tTERRAIN_COAST\tNONE\ttrue\ttrue\tfalse\t1\t7\tNONE\tNONE\t-1']
        pair=['1','7','1','true','false','true','true','1','0','0','','false','1','1','7','4','2','1','false','true','false']
        if extended:pair+=['2','3','false','0']
        rows+=['CSC_COAST_PAIR\t'+'\t'.join(pair),'CSC_COAST_PAIR\t'+'\t'.join(pair),'CSC_COAST_END\t250']
        path=root/'capture.txt';path.write_text('\n'.join(rows));return path

    def test_lakes_duplicates_and_missing_harbor_quotes(self):
        with TemporaryDirectory()as temporary:
            root=Path(temporary)
            old=analyse(self.capture(root,False))['summary']
            self.assertEqual(old['resource_free_sea_layouts'],1)
            self.assertEqual(old['coastal_material_clusters'],1)
            self.assertEqual(old['player_city_native_pairs'],1)
            self.assertEqual(old['owned_harbor_quality_known'],0)
            self.assertIsNone(old['owned_harbor_gold_at_least2'])
            new=analyse(self.capture(root,True))['summary']
            self.assertEqual(new['owned_harbor_gold_at_least2'],1)
            self.assertEqual(new['owned_pairs_matching_best_harbor'],0)


if __name__=='__main__':unittest.main()
