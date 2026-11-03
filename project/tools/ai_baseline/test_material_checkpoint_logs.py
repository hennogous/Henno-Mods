import gzip,json,tempfile,unittest
from pathlib import Path
from material_checkpoint_logs import reconstruct_checkpoint

class Bounds(unittest.TestCase):
 def make(self,root,label,start,chunk,end=None):
  p=root/'diagnostics'/label;p.mkdir(parents=True);(p/'AI.csv.gz').write_bytes(gzip.compress(chunk));(p/'log-segments.json').write_text(json.dumps([dict(file='AI.csv',start=start,end=start+len(chunk)if end is None else end,bytes=len(chunk))]))
 def test_future_records_with_same_turn_number_do_not_leak(self):
  with tempfile.TemporaryDirectory()as temp:
   p=Path(temp);early=b'25, before boundary\n';self.make(p,'outcome-25',0,early);self.make(p,'outcome-50',len(early),b'25, later AI activation\n')
   text,cov=reconstruct_checkpoint(p,'AI.csv',25);self.assertEqual(text,early.decode());self.assertTrue(cov['same_numeric_turn_future_records_excluded'])
 def test_prefix_and_overlapping_archives_reconstruct_without_duplication(self):
  with tempfile.TemporaryDirectory()as temp:
   p=Path(temp);self.make(p,'source16',0,b'abc');self.make(p,'outcome-25',2,b'cdef');self.make(p,'outcome-50',0,b'abcdefNEXT');self.assertEqual(reconstruct_checkpoint(p,'AI.csv',25)[0],'abcdef')
 def test_byte_boundary_preserves_multibyte_city_names(self):
  with tempfile.TemporaryDirectory()as temp:
   p=Path(temp);raw='25, João\n'.encode();self.make(p,'outcome-25',0,raw);self.make(p,'outcome-50',len(raw),b'future');self.assertEqual(reconstruct_checkpoint(p,'AI.csv',25)[0],raw.decode())
 def test_missing_prefix_fails(self):
  with tempfile.TemporaryDirectory()as temp:
   p=Path(temp);self.make(p,'outcome-25',5,b'x')
   with self.assertRaises(AssertionError):reconstruct_checkpoint(p,'AI.csv',25)
 def test_conflicting_or_malformed_segment_fails(self):
  for wrong_size in(False,True):
   with tempfile.TemporaryDirectory()as temp:
    p=Path(temp);self.make(p,'source16',0,b'abc');self.make(p,'outcome-25',0,b'abX',4 if wrong_size else None)
    with self.assertRaises(AssertionError):reconstruct_checkpoint(p,'AI.csv',25)

if __name__=='__main__':unittest.main()
