import itertools
import math
import random
import string
import unittest

from local_copy_probe import (Mechanism, band, edit_events, parse, physical_leaf,
    metrics, validate_plan, evaluate)


def rows(*words):
    return [{'words': list(words)}]


def tiny_model():
    return Mechanism(rows('ab', 'aa', 'a', 'b', 'ba', 'bb', 'ab', 'b'), alphabet='ab', maximum=2)


class LocalCopyFailureControls(unittest.TestCase):
    def test_parser_breaks_uncertainty_drawing_and_lines(self):
        text = '<f1r> <! $L=A $H=1 $Q=A $I=H>\n<f1r.1,+P0> aa.bb<->cc.?dd.ee\n<f1r.2,+P0> ff.gg'
        r, _ = parse(text, 'split')
        self.assertEqual([x['words'] for x in r], [['aa', 'bb'], ['cc'], ['ee'], ['ff', 'gg']])

    def test_both_comma_modes_preserve_distinction(self):
        text = '<f1r> <! $L=A $H=1>\n<f1r.1,+P0> aa,bb.cc'
        self.assertEqual(parse(text, 'split')[0][0]['words'], ['aa', 'bb', 'cc'])
        self.assertEqual(parse(text, 'join')[0][0]['words'], ['aabb', 'cc'])

    def test_all_panels_and_sides_are_one_leaf(self):
        self.assertEqual(physical_leaf('f102r1'), physical_leaf('f102v2'))
        self.assertIsNone(physical_leaf('fRos'))

    def test_all_three_word_distributions_normalize(self):
        model = tiny_model()
        vocabulary = [''.join(s) for n in (1, 2) for s in itertools.product('ab', repeat=n)]
        for previous in (None, 'a', 'ab', 'bb'):
            for kind in ('independent', 'edge', 'edge_copy'):
                for b in range(4):
                    self.assertAlmostEqual(sum(model.probability(w, previous, b, kind) for w in vocabulary), 1, places=12)

    def test_copy_paths_normalize_at_length_limits(self):
        model = tiny_model()
        vocabulary = [''.join(s) for n in (1, 2) for s in itertools.product('ab', repeat=n)]
        for previous in vocabulary:
            self.assertAlmostEqual(sum(model.copy_probability(w, previous) for w in vocabulary), 1, places=12)

    def test_repeated_character_paths_are_all_counted(self):
        self.assertEqual(len(edit_events('a', 'aa')), 2)
        self.assertEqual(len(edit_events('aaa', 'aa')), 3)
        self.assertFalse(edit_events('ab', 'ba'))

    def test_samples_are_nonempty_and_respect_support(self):
        model, rng = tiny_model(), random.Random(4)
        for previous in ('a', 'ab'):
            for _ in range(100):
                word = model.copy_sample(previous, rng)
                self.assertTrue(1 <= len(word) <= 2)
                self.assertTrue(edit_events(previous, word))

    def test_known_copy_signal_improves_unseen_sequence_scores(self):
        rng = random.Random(19)
        pool = [''.join(s) for s in itertools.product('abcd', repeat=4)]
        def generate(n):
            out = []
            for _ in range(n):
                r = []
                for i in range(12):
                    r.append(r[-1] if i and rng.random() < .3 else rng.choice(pool))
                out.append({'words': r})
            return out
        training, heldout = generate(160), generate(70)
        model = Mechanism(training)
        gains = []
        for r in heldout:
            for i in range(1, len(r['words'])):
                a, w = r['words'][i - 1:i + 1]
                b = band(i, len(r['words']))
                gains.append(math.log2(model.probability(w, a, b, 'edge_copy') / model.probability(w, a, b, 'edge')))
        self.assertGreater(sum(gains) / len(gains), .2)
        self.assertGreater(model.gamma, .1)

    def test_unrelated_neighbor_control_turns_copy_channel_off(self):
        model = Mechanism(rows(*(['aaaa', 'bbbb', 'cccc', 'dddd'] * 100)))
        self.assertEqual(model.gamma, 0)

    def test_counterfeit_preserves_edge_and_excludes_real_context(self):
        model = Mechanism(rows('aab', 'ccb', 'ddd', 'eeb', 'ffb', 'aab'))
        sampler = model.matched_context_sampler('aab')
        rng = random.Random(2)
        for _ in range(20):
            false = sampler.draw(rng)
            self.assertNotEqual(false, 'aab')
            self.assertEqual((len(false), false[-1]), (3, 'b'))
            self.assertEqual(model.edge_probability('ddd', false, 1), model.edge_probability('ddd', 'aab', 1))

    def test_meaning_renaming_cannot_change_probabilities_or_metrics(self):
        translation = str.maketrans(string.ascii_lowercase, string.ascii_lowercase[7:] + string.ascii_lowercase[:7])
        original = rows('aab', 'aab', 'acb', 'ddd', 'eed', 'ffd', 'ffdd', 'acb')
        renamed = [{'words': [w.translate(translation) for w in r['words']]} for r in original]
        first, second = Mechanism(original), Mechanism(renamed)
        self.assertAlmostEqual(first.gamma, second.gamma, places=12)
        for r in original:
            for i in range(1, len(r['words'])):
                a, w = r['words'][i - 1:i + 1]
                for kind in ('independent', 'edge', 'edge_copy'):
                    self.assertAlmostEqual(first.probability(w, a, 1, kind),
                        second.probability(w.translate(translation), a.translate(translation), 1, kind), places=12)
        m1 = metrics([r['words'] for r in original], random.Random(5))
        m2 = metrics([r['words'] for r in renamed], random.Random(5))
        for key in m1:
            self.assertAlmostEqual(m1[key], m2[key], places=12)

    def test_unknown_word_has_positive_probability(self):
        model = Mechanism(rows('aab', 'aab', 'acb', 'ddd', 'eed'))
        self.assertGreater(model.probability('xyz', 'aab', 1, 'edge_copy'), 0)

    def test_reserved_scoring_cannot_update_fitted_parameters(self):
        import copy
        model = Mechanism(rows('aab', 'aab', 'acb', 'ddd', 'eed', 'ffb'))
        before = copy.deepcopy((model.gamma, model.words, model.bands,
            model.operations, model.edge_p, model.start_p, model.inside))
        evaluate(model, [{'leaf': 'f999', 'words': ['zz', 'zzz', 'zyz', 'yyy']}], random.Random(4))
        after = (model.gamma, model.words, model.bands, model.operations,
            model.edge_p, model.start_p, model.inside)
        self.assertEqual(before, after)

    def test_frozen_configuration_is_checked(self):
        from pathlib import Path
        import json
        p = Path(__file__).resolve().parent.parent / 'data' / 'local_copy_plan.json'
        if not p.exists():
            p = Path(__file__).with_name('local_copy_plan.json')
        plan = json.loads(p.read_text())
        validate_plan(plan)
        plan['simulation']['draws_per_model'] = 31
        with self.assertRaises(ValueError):
            validate_plan(plan)


if __name__ == '__main__':
    unittest.main()
