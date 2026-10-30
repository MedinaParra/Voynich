#!/usr/bin/env python3
"""Controls with exhaustive CTC paths and known shifted-mask geometry."""
from collections import defaultdict
import itertools
import math
import unittest

import numpy as np
from kraken_alignment_diagnostic import ctc_log_probability, overlap_mask
from audit_kraken_alignment_diagnostic import probability_logmass
from render_kraken_alignment_review import review_queue


def collapse(path):
    return tuple(c for c, _ in itertools.groupby(path) if c != 0)


class DiagnosticControls(unittest.TestCase):
    def test_all_strings_from_exhaustive_paths(self):
        rng = np.random.default_rng(20261030)
        for frames in range(5):
            p = rng.random((frames, 3))
            p /= p.sum(axis=1, keepdims=True)
            total = defaultdict(float)
            for path in itertools.product(range(3), repeat=frames):
                total[collapse(path)] += math.prod(p[t, c] for t, c in enumerate(path))
            self.assertAlmostEqual(sum(total.values()), 1)
            for text, probability in total.items():
                self.assertAlmostEqual(math.exp(ctc_log_probability(p, text)), probability, places=12)

    def test_empty_text_and_repeated_character(self):
        p = np.array([[.6, .4], [.6, .4]])
        self.assertAlmostEqual(math.exp(ctc_log_probability(p, ())), .36)
        self.assertAlmostEqual(math.exp(ctc_log_probability(p, (1,))), .64)
        self.assertEqual(ctc_log_probability(p, (1, 1)), -math.inf)
        self.assertAlmostEqual(math.exp(ctc_log_probability(np.full((3, 2), .5), (1, 1))), .125)
        self.assertEqual(ctc_log_probability(np.empty((0, 2)), ()), 0)
        self.assertEqual(ctc_log_probability(np.empty((0, 2)), (1,)), -math.inf)

    def test_exact_zeros_and_tiny_probability(self):
        self.assertEqual(ctc_log_probability(np.array([[1., 0.]]), (1,)), -math.inf)
        p = np.tile([.999999, .0000005, .0000005], (400, 1))
        target = (1, 2) * 200
        self.assertAlmostEqual(ctc_log_probability(p, target), 400*math.log(.0000005), places=8)

    def test_invalid_probabilities_and_targets(self):
        for p in [np.array([[.9, .9]]), np.array([[math.nan, .1]]), np.array([[-.1, 1.1]]), np.array([.5, .5])]:
            with self.assertRaises(ValueError):
                ctc_log_probability(p, (1,))
        for target in [(0,), (2,), (1.5,)]:
            with self.assertRaises(ValueError):
                ctc_log_probability(np.array([[.5, .5]]), target)

    def test_independent_scaled_recurrence_and_extreme_underflow(self):
        rng = np.random.default_rng(75)
        for frames in range(5):
            p = rng.random((frames, 3))
            p /= p.sum(axis=1, keepdims=True)
            for n in range(frames+1):
                for target in itertools.product([1, 2], repeat=n):
                    a, b = ctc_log_probability(p, target), probability_logmass(p, target)
                    self.assertTrue(a == b or math.isclose(a, b, abs_tol=1e-12))
        p = np.tile([.999999, .0000005, .0000005], (400, 1))
        self.assertAlmostEqual(probability_logmass(p, (1, 2)*200), 400*math.log(.0000005), places=8)

    def test_shifted_masks_union_not_sum(self):
        target = ([10, 10, 12, 12], np.ones((2, 2), dtype=bool))
        other = ([11, 11, 13, 13], np.ones((2, 2), dtype=bool))
        shared, neighbors = overlap_mask(target, [('a', other), ('b', other)])
        self.assertEqual(shared.tolist(), [[False, False], [False, True]])
        self.assertEqual([r['shared_mask_pixels'] for r in neighbors], [1, 1])
        self.assertEqual(int(shared.sum()), 1)

    def test_touching_bounds_and_sparse_masks(self):
        target = ([0, 0, 2, 2], np.eye(2, dtype=bool))
        touching = ([2, 0, 4, 2], np.ones((2, 2), dtype=bool))
        sparse = ([0, 0, 2, 2], np.fliplr(np.eye(2, dtype=bool)))
        shared, neighbors = overlap_mask(target, [('touching', touching), ('sparse', sparse)])
        self.assertFalse(shared.any())
        self.assertEqual(neighbors, [])

    def test_review_queue_excludes_all_evaluation_rows(self):
        source = []
        geom = []
        for i, role in enumerate(['reserved', 'original_train', 'historical_development', 'additional_train']):
            identity = str(i)
            source.append({'id': identity, 'folio': 'f1r', 'role': role, 'reference': 'a', 'source_image_path': 'p',
                           'source_image_sha256': 'h', 'bounds': [0, 0, 1, 1], 'polygon': [], 'image_sha256': 'i', 'mask_sha256': 'm'})
            geom.append({'id': identity, 'role': role, 'reference': 'a', 'shared_mask_fraction': 1,
                         'ink_proxies': {'40': {'shared_fraction': i/4}}, 'neighbors': []})
        queue = review_queue(source, geom)
        self.assertEqual([r['id'] for r in queue], ['3', '1'])
        self.assertTrue(all(r['review_status'] == 'UNREVIEWED' and r['approved_reference'] is None for r in queue))


if __name__ == '__main__':
    unittest.main(verbosity=2)
