"""Counterexamples for log reconstruction, contract identity and censoring."""
import gzip,json,tempfile,unittest
from pathlib import Path
from log_intelligence import reconstruct,records,summarize_contracts,repair_episodes

class IntelligenceTests(unittest.TestCase):
 def test_segments_reassemble_split_line_and_overlap(self):
  with tempfile.TemporaryDirectory()as tmp:
   root=Path(tmp);data=b'25, 1, first\n26, 1, second\n'
   for n,start,end in [('a',0,9),('b',9,len(data)),('c',0,9)]:
    p=root/'diagnostics'/n;p.mkdir(parents=True);(p/'AI.csv.gz').write_bytes(gzip.compress(data[start:end]));(p/'log-segments.json').write_text(json.dumps([dict(file='AI.csv',start=start,end=end,bytes=end-start)]))
   text,cov=reconstruct(root,'AI.csv');self.assertEqual(text,data.decode());self.assertFalse(cov['gaps']);self.assertFalse(cov['conflicting_segments'])
 def test_cross_city_cancel_is_not_another_builder(self):
  text='\n'.join(['10, 1, A, , CONTRACT 9, SUBMITTED, UNIT_BUILDER','10, 1, B, , CONTRACT 9, SUBMITTED, UNIT_BUILDER','11, 1, A, , CONTRACT 9, CANCELLED, UNIT_BUILDER','11, 1, B, , , UNIT_BUILDER, Build City Improvement, CONTRACT 9','14, 1, B, , CONTRACT 9, COMPLETED, UNIT_BUILDER'])
  contracts,selections=summarize_contracts(records(text,1,20,{1}));self.assertEqual(len(contracts),1);self.assertEqual(contracts[0]['completed'],14);self.assertTrue(contracts[0]['cancelled_or_failed']);self.assertEqual(contracts[0]['submission_to_selection'],1)
 def test_reload_boundary_rows_excluded(self):
  text='24, 1, old\n25, 1, new\n25, 7, minor';self.assertEqual([r[0]for r in records(text,25,169,set(range(1,6)))],[25])
 def test_initial_repair_is_censored_and_native_action_matches(self):
  events=[dict(player=1,plot=75,turn=25,event='work_state',previous='new',state='repair'),dict(player=1,plot=75,turn=30,event='work_state',previous='repair',state='working')]
  ops=[dict(player=1,x=1,y=1,turn=30,operation=147469951)]
  rows=repair_episodes(events,ops,74);self.assertTrue(rows[0]['left_censored']);self.assertTrue(rows[0]['native_repair_matched']);self.assertEqual(rows[0]['elapsed'],5)

if __name__=='__main__':unittest.main()
