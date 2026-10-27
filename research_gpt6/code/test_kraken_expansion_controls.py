#!/usr/bin/env python3
"""Controls for leakage and candidate selection, without native OCR imports."""
import unittest
from retrain_kraken_expansion import select_rows


def fixture():
    rows=[]
    for count,folio,role in [(100,'f3r','original_train'),(97,'f3v','original_train'),(64,'f4r','historical_development'),(83,'f4v','historical_development'),(20,'f5r','additional_train'),(20,'f6v','additional_train'),(20,'f7r','reserved'),(20,'f7v','reserved')]:
        rows.extend({'id':folio+'_'+str(i),'folio':folio,'role':role} for i in range(count))
    return rows


class Controls(unittest.TestCase):
    def test_continuation_never_gets_additional_or_evaluation_rows(self):
        train,evaluation=select_rows(fixture(),'continuation_200');self.assertEqual(len(train),197);self.assertEqual({r['folio'] for r in train},{'f3r','f3v'});self.assertEqual({r['folio'] for r in evaluation},{'f4r','f4v','f7r','f7v'})
    def test_expanded_gets_additional_only(self):
        train,evaluation=select_rows(fixture(),'expanded_200');self.assertEqual(len(train),237);self.assertFalse({r['id'] for r in train}&{r['id'] for r in evaluation})
    def test_forged_training_role_on_reserved_page_is_rejected(self):
        rows=fixture();next(r for r in rows if r['folio']=='f7r')['role']='additional_train'
        with self.assertRaisesRegex(ValueError,'Physical leaf leakage'):select_rows(rows,'expanded_200')
    def test_duplicate_sample_is_rejected(self):
        rows=fixture();rows.append(rows[0].copy())
        with self.assertRaisesRegex(ValueError,'Duplicate'):select_rows(rows,'expanded_200')
    def test_missing_old_development_row_is_rejected(self):
        rows=fixture();rows=[r for r in rows if r['id']!='f4r_0']
        with self.assertRaisesRegex(ValueError,'historical development'):select_rows(rows,'expanded_200')


if __name__=='__main__':unittest.main(verbosity=2)
