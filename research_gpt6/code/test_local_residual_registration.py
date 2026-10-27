#!/usr/bin/env python3
"""Numerical controls executable without importing the native OpenCV module."""
import unittest
import numpy as np
from local_residual_registration import project, anchors, corrections, split_guarded, positive_grid

OPTS = {'fit_residual_limit_yale_pixels':20, 'source_group_grid_pixels':.1,
        'radius_source_pixels':80, 'maximum_neighbors':20, 'minimum_groups':3,
        'correction_limit_yale_pixels':20}


class Controls(unittest.TestCase):
    def test_known_smooth_field_and_scrambled_control(self):
        a = np.array([[x,y] for y in np.linspace(0,900,31) for x in np.linspace(0,636,31)])
        h = np.array([[2.,0,30],[0,2.,40],[0,0,1.]])
        delta = np.c_[.01*a[:,0]-3,.008*a[:,1]-3]
        b = project(a,h)+delta
        fit, held, _ = split_guarded(a,[636,900],0,3)
        source,vectors,_ = anchors(a[fit],b[fit],h,OPTS)
        real = corrections(a[held],source,vectors,OPTS)[0]
        order = np.random.default_rng(20261027).permutation(len(source))
        wrong = corrections(a[held],source,vectors[order],OPTS)[0]
        error = np.linalg.norm(real-delta[held],axis=1)
        self.assertLess(float(np.median(error)),float(np.median(np.linalg.norm(delta[held],axis=1)))/3)
        self.assertLess(float(np.median(error)),float(np.median(np.linalg.norm(wrong-delta[held],axis=1))))

    def test_large_discrepancy_cannot_pollute_local_anchors(self):
        a = np.array([[0.,0],[10,0],[0,10],[10,10],[5,5]])
        b = a+np.array([4.,-2]);b[-1] += 500
        source,vectors,kept = anchors(a,b,np.eye(3),OPTS)
        self.assertEqual(len(kept),4)
        self.assertTrue(np.allclose(corrections([[5,5]],source,vectors,OPTS)[0],[[4,-2]]))

    def test_guard_excludes_near_duplicate_on_block_boundary(self):
        a = np.array([[79.4,10],[79.6,10],[200,200],[400,500],[600,800]])
        fit,held,excluded = split_guarded(a,[636,900],0,3)
        self.assertIn(0,held);self.assertIn(1,excluded)
        self.assertFalse(set(fit)&set(held));self.assertFalse(set(fit)&set(excluded))

    def test_no_support_means_no_invented_displacement(self):
        result,support,_ = corrections([[500,500]],np.array([[0.,0],[1,1]]),np.array([[4.,2],[4,2]]),OPTS)
        self.assertTrue(np.allclose(result,0));self.assertEqual(support,[0])

    def test_grid_detects_reflection(self):
        a = np.array([[x,y] for y in range(3) for x in range(4)],dtype=float)
        self.assertTrue(positive_grid(a,[4,3])[0])
        a[:,0] *= -1
        self.assertFalse(positive_grid(a,[4,3])[0])


if __name__ == '__main__': unittest.main(verbosity=2)
