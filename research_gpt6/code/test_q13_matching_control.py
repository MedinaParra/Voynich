"""Scientific controls for the Q13 matching analysis; no real corpus fit."""
import itertools
import json
import math
import unittest

import q13_matching_control as q


class MatchingControls(unittest.TestCase):
    def test_complete_matching_space(self):
        records = list(q.perfect_matchings(q.LEAVES))
        self.assertEqual(len(records), 945)
        self.assertEqual(len(set(records)), 945)
        for matching in records:
            self.assertEqual(sorted(itertools.chain.from_iterable(matching)), list(q.LEAVES))

    def test_cross_half_space_is_subset(self):
        cross = set(q.cross_half_matchings(q.LEAVES))
        self.assertEqual(len(cross), 120)
        self.assertTrue(cross <= set(q.perfect_matchings(q.LEAVES)))
        self.assertIn(q.canonical(q.OBSERVED), cross)

    def test_known_pairing_positive_control(self):
        observed_keys = {q.edge_key(p) for p in q.OBSERVED}
        edges = {q.edge_key(p): float(q.edge_key(p) in observed_keys)
                 for p in itertools.combinations(q.LEAVES, 2)}
        summary, _ = q.assess({'synthetic': edges})
        self.assertEqual(summary['synthetic']['all']['rank_best_is_1'], 1)
        self.assertEqual(summary['synthetic']['all']['exact_tail_p'], 1 / 945)
        self.assertEqual(summary['synthetic']['cross_half']['exact_tail_p'], 1 / 120)

    def test_flat_negative_control_includes_ties(self):
        edges = {q.edge_key(p): .5 for p in itertools.combinations(q.LEAVES, 2)}
        summary, _ = q.assess({'flat': edges})
        self.assertEqual(summary['flat']['all']['exact_tail_p'], 1)
        self.assertEqual(summary['flat']['cross_half']['exact_tail_p'], 1)

    def test_anti_pairing_negative_control(self):
        keys = {q.edge_key(p) for p in q.OBSERVED}
        edges = {q.edge_key(p): -float(q.edge_key(p) in keys)
                 for p in itertools.combinations(q.LEAVES, 2)}
        summary, _ = q.assess({'anti': edges})
        self.assertEqual(summary['anti']['all']['exact_tail_p'], 1)

    def test_node_additive_nuisance_cancels(self):
        edges = {q.edge_key((a, b)): a * a + b * b for a, b in itertools.combinations(q.LEAVES, 2)}
        scores = [q.matching_score(m, edges) for m in q.perfect_matchings(q.LEAVES)]
        self.assertEqual(len(set(scores)), 1)

    def test_noise_inside_tolerance_is_a_tie(self):
        d = q.exact_summary(1, [1, 1 + 1e-13, 1 - 1e-13])
        self.assertEqual(d['exact_tail_p'], 1)

    def test_lower_tail_is_not_upper_tail(self):
        self.assertEqual(q.exact_summary(1, [1, 2, 3], higher=False)['exact_tail_p'], 1 / 3)
        self.assertEqual(q.exact_summary(1, [1, 2, 3], higher=True)['exact_tail_p'], 1)

    def test_idf_training_excludes_q13(self):
        idf, n = q.make_idf({'f1r': ['alpha'], 'f1v': ['beta'], 'f75r': ['forbidden']})
        self.assertNotIn('forbidden', idf)
        self.assertEqual(n, 1)

    def test_symbol_names_do_not_add_semantics(self):
        words = ['qok', 'qok', 'dy']
        other = ['qok', 'dy', 'dy']
        before = q.cosine(q.tfidf(words, {'qok': 2, 'dy': 3}), q.tfidf(other, {'qok': 2, 'dy': 3}))
        after = q.cosine(q.tfidf(['apple', 'apple', 'moon'], {'apple': 2, 'moon': 3}),
                         q.tfidf(['apple', 'moon', 'moon'], {'apple': 2, 'moon': 3}))
        self.assertAlmostEqual(before, after)

    def test_parser_ambiguity_and_annotations(self):
        raw = '<f75r> <! $Q=M $B=1 $H=2 $L=B >\n<f75r.1,+P0> ab,cd.ef<->gh.ij<!x>kl.??.mn\n'
        split, _, _ = q.parse_pages(raw, 'split')
        join, _, _ = q.parse_pages(raw, 'join')
        self.assertEqual(split['f75r'], ['ab', 'cd', 'ef', 'gh', 'ij', 'kl', 'mn'])
        self.assertEqual(join['f75r'], ['abcd', 'ef', 'gh', 'ij', 'kl', 'mn'])
        self.assertNotIn('ijkl', split['f75r'])

    def test_incomplete_physical_mapping_is_rejected(self):
        with self.assertRaises(ValueError):
            q.validate_metadata({})

    def test_pure_style_signal_is_removed(self):
        words = {a: ['ab'] * (a - 70) for a in q.LEAVES}
        style = {q.edge_key((a, b)): ((a + 3*b) % 11) / 11 for a, b in itertools.combinations(q.LEAVES, 2)}
        raw = {q.edge_key((a, b)): .2 + .7 * style[q.edge_key((a, b))]
               + .15 * abs(math.log(len(words[a]) / len(words[b]))) + .02 * (a-b)**2 / 100
               for a, b in itertools.combinations(q.LEAVES, 2)}
        residual, fit = q.nuisance_residual(raw, style, words)
        self.assertEqual(fit['matrix_rank'], 4)
        self.assertLess(max(abs(v) for v in residual.values()), 1e-12)
        summary, _ = q.assess({'residual': residual})
        self.assertEqual(summary['residual']['all']['exact_tail_p'], 1)

    def test_timesfm_cost_uses_eight_cross_leaf_directions(self):
        page_errors = {}
        ids = [f'f{n}{s}' for n in q.LEAVES for s in ('r', 'v')]
        for src in ids:
            for tgt in ids:
                if src != tgt:
                    page_errors[f'{src}->{tgt}'] = [1.0, 2.0]
        page_errors['f75r->f84v'] = [9.0, 2.0]
        page_errors['f75r->f75v'] = [10000.0, 10000.0]
        self.assertEqual(q.timesfm_edges(page_errors, [0])['75|84'], 2)
        self.assertEqual(q.timesfm_edges(page_errors, [1])['75|84'], 2)

    def test_missing_or_nonfinite_edges_do_not_get_imputed(self):
        with self.assertRaises(KeyError):
            q.matching_score(q.OBSERVED, {})
        with self.assertRaises(ValueError):
            q.exact_summary(1, [float('nan')])

    def test_pair_removal_has_correct_reference_size(self):
        for omitted in q.OBSERVED:
            nodes = [n for n in q.LEAVES if n not in omitted]
            self.assertEqual(len(list(q.perfect_matchings(nodes))), 105)
            self.assertEqual(len(list(q.cross_half_matchings(nodes))), 24)


if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(MatchingControls)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print(json.dumps({'classification': 'Q13_MATCHING_SCIENTIFIC_HARNESS',
                      'status': 'PASS' if result.wasSuccessful() else 'FAIL',
                      'tests_run': result.testsRun, 'failures': len(result.failures),
                      'errors': len(result.errors)}, sort_keys=True))
    raise SystemExit(0 if result.wasSuccessful() else 1)
