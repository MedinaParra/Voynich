#!/usr/bin/env python3
"""Input and label controls requiring neither Torch nor Kraken."""
import unittest
from collections import Counter
import numpy as np
from PIL import Image
from kraken_eva_word_training import crop_word,permuted_training_labels,sample_name


class Controls(unittest.TestCase):
    def test_crop_keeps_source_pixels_and_whitens_outside_mask(self):
        a=np.arange(80*60*3,dtype=np.uint8).reshape(60,80,3);im=Image.fromarray(a)
        out,mask,b=crop_word(im,[[20,10],[55,12],[54,40],[18,38]],4)
        m=np.asarray(mask)>0;actual=np.asarray(out);raw=a[b[1]:b[3],b[0]:b[2]]
        self.assertTrue(np.array_equal(actual[m],raw[m]));self.assertTrue(np.all(actual[~m]==255))

    def test_boundary_crop_stays_inside_source(self):
        out,mask,b=crop_word(Image.new('RGB',(30,20),'gray'),[[0,0],[8,0],[8,10],[0,10]],4)
        self.assertEqual(b[:2],[0,0]);self.assertLessEqual(b[2],30);self.assertLessEqual(b[3],20)
        self.assertEqual(out.size,mask.size)

    def test_zero_area_is_rejected(self):
        with self.assertRaises(ValueError):crop_word(Image.new('RGB',(30,20)),[[2,2],[2,2],[2,10],[2,10]],4)

    def test_permutation_keeps_development_and_training_strata(self):
        rows=[{'id':str(i),'folio':'f3r' if i<4 else 'f3v','role':'train','reference':w}
              for i,w in enumerate(['ab','cd','aaa','bbb','ef','gh','ccc','ddd'])]
        rows.append({'id':'dev','folio':'f4r','role':'development','reference':'zz'})
        assigned=permuted_training_labels(rows,20261027);by={r['id']:r for r in rows}
        self.assertEqual(assigned['dev'],{'text':'zz','source_id':'dev'})
        for r in rows[:-1]:
            src=by[assigned[r['id']]['source_id']]
            self.assertEqual(src['role'],'train');self.assertEqual(src['folio'],r['folio'])
            self.assertEqual(len(src['reference']),len(r['reference']));self.assertNotEqual(src['id'],r['id'])
        self.assertEqual(Counter(v['text'] for k,v in assigned.items() if k!='dev'),Counter(r['reference'] for r in rows[:-1]))

    def test_sample_names_do_not_have_internal_suffixes(self):
        self.assertEqual(sample_name('f3r',12),'f3r_w0012');self.assertNotIn('.',sample_name('f4v',1))


if __name__=='__main__':unittest.main(verbosity=2)
