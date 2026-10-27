#!/usr/bin/env python3
"""Failure controls for provisional ownership extraction, not glyph validation."""
import unittest
import numpy as np
from PIL import Image, ImageDraw
from kraken_crop_repair import repair

OPTS={'ownership_delta':.06,'minimum_pitch_fraction':.5,'center_penalty':.25,
      'component_dominance_review_threshold':.75,'minimum_component_review_area':10,
      'halo_pixels':2,'crop_padding_pixels':3}


class Controls(unittest.TestCase):
    def fixture(self):
        im=Image.new('RGB',(240,140),'white');d=ImageDraw.Draw(im)
        d.rectangle((25,40,210,46),fill='black');d.rectangle((25,75,210,81),fill='black')
        d.rectangle((45,28,48,42),fill='black')
        rows=[{'id':'a','paragraph':1,'bbox':[.05,.15,.95,.53]},
              {'id':'b','paragraph':1,'bbox':[.05,.43,.95,.77]}]
        regions=[{'paragraph':1,'polygons':[[[0,0],[1,0],[1,1],[0,1]]]}]
        return im,rows,regions
    def test_proxy_conserved_without_duplicates(self):
        im,rows,regions=self.fixture();c,s=repair(im,rows,regions,OPTS)
        self.assertEqual(len(c),2)
        self.assertTrue(all(v['repeated_after']==0 and v['lost_candidate_positions']==0 for v in s['metrics'].values()))
    def test_original_pixels_not_invented(self):
        im,rows,regions=self.fixture();c,_=repair(im,rows,regions,OPTS)
        src=np.asarray(im)
        for r in c:
            x0,y0,x1,y1=r['bounds'];out=np.asarray(r['image'])
            self.assertTrue(np.array_equal(out[r['mask']],src[y0:y1,x0:x1][r['mask']]))
    def test_ascender_component_not_cut(self):
        im,rows,regions=self.fixture();c,_=repair(im,rows,regions,OPTS)
        covered=[]
        for r in c:
            x0,y0,x1,y1=r['bounds'];mask=np.zeros((140,240),bool);mask[y0:y1,x0:x1]=r['mask']
            covered.append(mask[28:47,45:49].all())
        self.assertEqual(sum(covered),1)
    def test_unidentifiable_guides_rejected(self):
        im,rows,regions=self.fixture();rows[1]['bbox']=rows[0]['bbox'][:]
        with self.assertRaises(ValueError):repair(im,rows,regions,OPTS)
    def test_blank_rows_block_export(self):
        im,rows,regions=self.fixture()
        with self.assertRaises(ValueError):repair(Image.new('RGB',im.size,'white'),rows,regions,OPTS)
    def test_masked_out_ink_not_counted(self):
        im,rows,regions=self.fixture();d=ImageDraw.Draw(im);d.rectangle((0,120,239,139),fill='black')
        c,s=repair(im,rows,regions,OPTS)
        self.assertTrue(all(r['bounds'][3]<120 for r in c))


if __name__=='__main__':unittest.main(verbosity=2)
