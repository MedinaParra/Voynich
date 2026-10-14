import unittest
from transformation_probe import (apply_rule, build_cases, learn_rule, parse,
    predict, rank_exact, score_predictions, units, sample_assignment)


class TransformationFailureControls(unittest.TestCase):
    def toy(self):
        words = ['alen', 'borem', 'civar', 'dolen', 'emir', 'falen']
        return [dict(id=str(i), entity='e' + str(i), leaf='f' + str(i // 2),
            source_folio='e' + str(i), source_words=(w,), label=w + 'y')
            for i, w in enumerate(words)]

    def test_known_shared_rule_predicts_new_family(self):
        cases = self.toy()
        pred, _ = predict(cases)
        _, score = score_predictions(pred, cases)
        self.assertEqual(score['learned']['unique_top1'], 6)
        self.assertEqual(score['identity']['generated'], 0)

    def test_heldout_label_cannot_change_its_predictions(self):
        cases = self.toy()
        pred, folds = predict(cases)
        changed = [dict(c, label='zzzzz') if c['leaf'] == 'f0' else c for c in cases]
        pred2, folds2 = predict(changed)
        self.assertEqual([p for p in pred if p['leaf'] == 'f0'],
                         [p for p in pred2 if p['leaf'] == 'f0'])
        self.assertEqual(folds[0], folds2[0])

    def test_unrelated_caption_control_is_not_decoded(self):
        captions = ['qzxqz', 'vjuvj', 'zxqzx', 'jvujv', 'qjzqj', 'vxjvx']
        cases = [dict(c, label=y) for c, y in zip(self.toy(), captions)]
        pred, _ = predict(cases)
        _, score = score_predictions(pred, cases)
        self.assertEqual(score['learned']['generated'], 0)

    def test_shared_family_is_purged_across_leaves(self):
        cases = self.toy()
        cases[2]['entity'] = cases[0]['entity']
        _, folds = predict(cases)
        self.assertEqual(folds[0]['purged_shared_entities'], 1)

    def test_numbers_do_not_turn_containers_into_plants(self):
        raw = '<f1v> <! $L=A $H=1 $I=H>\n<f1v.1,@P0> alen.borem\n'
        raw += '<f99r> <! $L=A $H=1 $I=P>\n<f99r.1,@Lc> <!94a>jar\n<f99r.2,@Lf> <!94b>tolsasy\n'
        pages, labels = parse(raw)
        inv = {'relations': [dict(pharma='f99r', fragment='94', herbal='f1v')]}
        cases, _ = build_cases(pages, labels, inv)
        self.assertEqual([c['label'] for c in cases], ['tolsasy'])
        _, labels2 = parse(raw.replace('tolsasy', 'tol[s:r]asy'))
        self.assertEqual(len(build_cases(pages, labels2, inv)[0]), 0)

    def test_one_fragment_with_two_labels_is_not_a_unique_pair(self):
        raw = '<f1v> <! $I=H>\n<f1v.1,@P0> alen\n<f99r> <! $I=P>\n'
        raw += '<f99r.1,@Lf> <!110>otal\n<f99r.2,@Lf> <!110b>chor.olekor\n'
        pages, labels = parse(raw)
        cases, _ = build_cases(pages, labels, {'relations': [dict(pharma='f99r', fragment='110', herbal='f1v')]})
        self.assertFalse(cases)

    def test_tied_scores_do_not_manufacture_top1(self):
        rank = rank_exact([('alen', -.5), ('borem', -.5)], 'alen')
        self.assertFalse(rank['unique_top1'])
        self.assertEqual(rank['rank_max'], 2)

    def test_bench_units_cannot_be_split_by_affix_rule(self):
        self.assertEqual(units('qockhy'), ('q', 'o', 'ckh', 'y'))
        self.assertIsNone(apply_rule('ckhalen', (('c',), (), (), ('y',))))

    def test_wrong_match_keeps_distinct_families_on_distinct_pages(self):
        import random
        assignment = sample_assignment({'a': ['p', 'q'], 'b': ['p']}, random.Random(1))
        self.assertEqual(assignment, {'a': 'q', 'b': 'p'})

    def test_rule_needs_two_physical_training_leaves(self):
        train = [dict(c, leaf='f0') for c in self.toy()]
        self.assertIsNone(learn_rule(train)[0])


if __name__ == '__main__':
    unittest.main(verbosity=2)
