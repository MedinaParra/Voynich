#!/usr/bin/env python3
import itertools
import math
import unittest
from collections import defaultdict
import numpy as np
from ctc_prefix_tools import collapse,greedy,prefix_beam


def exhaustive(p):
    result=defaultdict(float)
    for path in itertools.product(range(p.shape[1]),repeat=len(p)):
        # Independently collapse runs before removing the blank symbol.
        text=tuple(k for k,g in itertools.groupby(path) if k!=0)
        result[text]+=math.prod(p[t,c] for t,c in enumerate(path))
    return dict(result)


class Controls(unittest.TestCase):
    def test_ctc_mass_can_beat_best_single_path(self):
        p=np.array([[.6,.4],[.6,.4]])
        self.assertEqual(greedy(p),());self.assertEqual(prefix_beam(p,32)[0][0],(1,));self.assertAlmostEqual(math.exp(prefix_beam(p,32)[0][1]),.64)
    def test_every_positive_prefix_mass_matches_exhaustive_paths(self):
        p=np.array([[.2,.5,.3],[.4,.35,.25],[.1,.3,.6],[.3,.2,.5]])
        expected=exhaustive(p);actual={k:math.exp(v) for k,v in prefix_beam(p,1000)}
        self.assertEqual(set(actual),{k for k,v in expected.items() if v>0})
        for k,v in expected.items():self.assertAlmostEqual(actual[k],v,places=12)
    def test_blank_separates_repeated_symbols(self):
        p=np.array([[0,1],[1,0],[0,1]],dtype=float)
        self.assertEqual(prefix_beam(p,32)[0][0],(1,1));self.assertEqual(collapse([1,1,0,1]),(1,1))
    def test_negative_or_non_normalized_probabilities_rejected(self):
        for p in [np.array([[.7,.7]]),np.array([[-.1,1.1]])]:
            with self.assertRaises(ValueError):prefix_beam(p)
    def test_empty_sequence_is_empty_text(self):
        p=np.empty((0,3));self.assertEqual(prefix_beam(p),[((),0.)]);self.assertEqual(greedy(p),())
    def test_ties_use_label_order(self):
        p=np.array([[0,.5,.5]]);self.assertEqual(prefix_beam(p,1)[0][0],(1,))


if __name__=='__main__':unittest.main(verbosity=2)
