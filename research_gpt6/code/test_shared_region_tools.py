#!/usr/bin/env python3
import unittest
import numpy as np
from shared_region_tools import perturb, training_only


class Controls(unittest.TestCase):
    def fixture(self):
        rgb = np.full((20, 20, 3), 200, dtype=np.uint8)
        rgb[3:13, 3:13] = 40
        target = np.ones((20, 20), dtype=bool)
        shared = np.zeros((20, 20), dtype=bool)
        shared[3:6, 3:9] = True
        return rgb, target, shared

    def test_pixel_count_matched_random_control_and_original_preservation(self):
        rgb, target, shared = self.fixture()
        a, selected, s = perturb(rgb, target, shared, 'word', 'shared_ink', 20261103)
        b, random, r = perturb(rgb, target, shared, 'word', 'random_ink', 20261103)
        self.assertEqual(s['selected_pixels'], r['selected_pixels'])
        self.assertEqual(s['selected_pixels'], 18)
        self.assertTrue(np.array_equal(selected, shared))
        self.assertFalse(np.any(random & (rgb[:, :, 0] > 40)))
        self.assertTrue(np.array_equal(a[~selected], rgb[~selected]))
        self.assertTrue(np.all(a[selected] == 120))
        self.assertEqual(s['changed_pixels'], 18)

    def test_identity_and_reproducibility(self):
        rgb, target, shared = self.fixture()
        out, selected, stats = perturb(rgb, target, shared, 'x', 'repeat', 1)
        self.assertTrue(np.array_equal(out, rgb))
        self.assertFalse(selected.any())
        a, b, c = perturb(rgb, target, shared, 'x', 'random_ink', 1)
        x, y, z = perturb(rgb, target, shared, 'x', 'random_ink', 1)
        self.assertTrue(np.array_equal(a, x) and np.array_equal(b, y) and c == z)

    def test_zero_dark_or_zero_shared_pixels(self):
        rgb, target, shared = self.fixture()
        for im, region in [(np.full_like(rgb, 200), shared), (rgb, np.zeros_like(shared))]:
            out, mask, record = perturb(im, target, region, 'x', 'shared_ink', 1)
            self.assertEqual(record['selected_pixels'], 0)
            self.assertTrue(np.array_equal(im, out))

    def test_integer_rounding_no_unsigned_overflow(self):
        rgb = np.full((3, 3, 3), 251, dtype=np.uint8)
        rgb[0, 0] = 10
        shared = np.zeros((3, 3), dtype=bool)
        shared[0, 0] = True
        out, _, _ = perturb(rgb, np.ones((3, 3), bool), shared, 'x', 'shared_ink', 1)
        self.assertEqual(out[0, 0].tolist(), [131, 131, 131])

    def test_invalid_shapes_regions_and_variants(self):
        rgb, target, shared = self.fixture()
        for t, s, variant in [(np.zeros_like(target), shared, 'shared_ink'), (target[:2], shared, 'repeat'), (target, shared, 'unknown')]:
            with self.assertRaises(ValueError):
                perturb(rgb, t, s, 'x', variant, 1)
        target[3, 3] = False
        with self.assertRaises(ValueError):
            perturb(rgb, target, shared, 'x', 'shared_ink', 1)

    def test_training_only_and_physical_leaf_leakage(self):
        rows = [{'id': 'a', 'folio': 'f3r', 'role': 'original_train'}, {'id': 'b', 'folio': 'f4r', 'role': 'reserved'},
                {'id': 'c', 'folio': 'f8r', 'role': 'fresh_reserved'}]
        self.assertEqual([r['id'] for r in training_only(rows)], ['a'])
        rows.append({'id': 'd', 'folio': 'f3v', 'role': 'reserved'})
        with self.assertRaises(ValueError):
            training_only(rows)


if __name__ == '__main__':
    unittest.main(verbosity=2)
