#!/usr/bin/env python3
"""Controls for the diagnostic harness, with no Kraken or trained network required."""
import unittest
import numpy as np
from PIL import Image
from kraken_visual_specificity import decomposition, transform, groups_and_draws, permutation_summary


class Controls(unittest.TestCase):
    def test_edit_decomposition_known_cases(self):
        cases = [('abc', 'axc', (2, 1, 0, 0)), ('ab', 'a', (1, 0, 1, 0)),
                 ('a', 'ab', (1, 0, 0, 1)), ('', '', (0, 0, 0, 0)), ('aa', 'a', (1, 0, 1, 0))]
        for a, b, expected in cases:
            c = decomposition(a, b)
            self.assertEqual(tuple(c[k] for k in ['matches', 'substitutions', 'deletions', 'insertions']), expected)

    def test_transform_pixel_conservation_and_empty_control(self):
        a = np.arange(11 * 5 * 3, dtype=np.uint8).reshape(5, 11, 3); im = Image.fromarray(a)
        for condition in ['intact', 'mirror_x', 'tile_shuffle_8']:
            b, _ = transform(im, condition, 'fixture', 20261027)
            self.assertEqual(im.size, b.size)
            self.assertEqual(sorted(map(tuple, a.reshape(-1, 3))), sorted(map(tuple, np.asarray(b).reshape(-1, 3))))
        b, _ = transform(im, 'white', 'fixture', 20261027)
        self.assertTrue(np.all(np.asarray(b) == 255))
        b, _ = transform(im, 'mirror_x', 'fixture', 20261027)
        self.assertTrue(np.array_equal(np.asarray(b), a[:, ::-1]))

    def test_permutations_never_cross_geometry_groups(self):
        rows = [{'id': str(i), 'folio': '4r' if i < 8 else '4v', 'crop_size': [i+10, 5], 'text': str(i)} for i in range(16)]
        groups, draws = groups_and_draws(rows, 40, 20261027)
        for draw in draws:
            for group in groups: self.assertEqual(set(draw[group['indices']]), set(group['indices']))

    def test_constant_predictor_has_no_pairing_advantage(self):
        rows = [{'id': str(i), 'folio': '4r', 'crop_size': [i+10, 5], 'text': 'a' * (i+1)} for i in range(8)]
        groups, draws = groups_and_draws(rows, 100, 20261027)
        result = permutation_summary(rows, ['a'] * 8, groups, draws)
        self.assertEqual(result['diagnostic_lower_tail_fraction'], 1.)
        self.assertTrue(all(x == result['observed_errors'] for x in result['null_error_counts']))


if __name__ == '__main__': unittest.main(verbosity=2)
