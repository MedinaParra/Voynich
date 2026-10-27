#!/usr/bin/env python3
"""Synthetic geometric failure controls, not manuscript annotation validation."""
import unittest
import cv2
import numpy as np
from register_voynichese_yale import project, image_holdout, mapped_words


class Controls(unittest.TestCase):
    def test_known_transform_composition(self):
        a = np.array([[2., 0, 10], [0, 3, -4], [0, 0, 1]])
        b = np.array([[1., .2, -2], [0, 1, 6], [0, 0, 1]])
        points = [[3, 4], [1, 2], [10, 20]]
        self.assertTrue(np.allclose(project(points, b @ a), project(project(points, a), b)))
        self.assertTrue(np.allclose(project([[3, 4]], a), [[16, 8]]))

    def test_ransac_recovers_known_geometry_with_outliers(self):
        rng = np.random.default_rng(20261027)
        a = rng.uniform(0, 500, (100, 2)); truth = np.array([[1.4, .03, 20], [-.02, 1.7, 30], [0, 0, 1]])
        b = project(a, truth) + rng.normal(0, .15, (100, 2)); b[:30] = rng.uniform(0, 1000, (30, 2))
        cv2.setRNGSeed(20261027)
        m, mask = cv2.findHomography(a, b, cv2.RANSAC, 3)
        self.assertGreaterEqual(int(mask.sum()), 65)
        self.assertLess(float(np.linalg.norm(project(a[30:], m) - project(a[30:], truth), axis=1).max()), 1)

    def test_spatial_duplicates_stay_in_same_partition(self):
        a = [[2., 3], [2., 3], [630, 890], [300, 400]]
        held = image_holdout(a, (636, 900))
        self.assertEqual(held[0], held[1])
        self.assertTrue(held.any()); self.assertTrue((~held).any())

    def test_invalid_source_box_is_not_silently_repaired(self):
        page = {'folio': 'fixture', 'words': [{'index': 0, 'eva': 'x', 'xml_bbox': [1, 2, 0, 4]},
                                             {'index': 1, 'eva': 'y', 'xml_bbox': [1, 2, 3, 4]}]}
        result = mapped_words(page, np.eye(3), (100, 100))
        self.assertIsNone(result[0]['yale_polygon'])
        self.assertIn('source_nonpositive_width', result[0]['flags'])
        self.assertIsNotNone(result[1]['yale_polygon'])


if __name__ == '__main__': unittest.main(verbosity=2)
