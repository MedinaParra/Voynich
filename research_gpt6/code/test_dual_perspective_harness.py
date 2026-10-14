"""Scientific failure-mode controls, not a claim about Voynich meanings."""
import unittest
import numpy as np
from dual_perspective_harness import evaluate,parse,rename_witness,run


def fixture(style=False,random_labels=False):
    rng=np.random.default_rng(777);rows=[]
    for q in range(3):
        for f in range(4):
            for i in range(20):
                y=i%2
                token='aaaaao' if y else 'oooooa'
                if style: token='a'*(6+2*y)
                if random_labels: y=int(rng.integers(2))
                rows.append(dict(id=f'{q}:{f}:{i}',folio=f'{q}:{f}',quire=str(q),
                    currier='A',hand='1',token=token,label=str(y)))
    return rows


class FailureModeControls(unittest.TestCase):
    def test_recovers_known_cross_view_signal(self):
        # Repeated literal strings here are deliberate synthetic design;
        # the real Voynich execution purges them across folds.
        result=run(fixture(),199,purge=False)
        self.assertGreater(result['observed']['forward_gain'],.1)
        self.assertGreater(result['observed']['inverse_gain'],.05)
        self.assertTrue(result['numerical_pilot_pass'])
        self.assertEqual(result['semantic_gate'],'BLOCKED')

    def test_length_only_is_not_content(self):
        result=run(fixture(style=True),39,purge=False)
        self.assertEqual(result['permutation']['exchangeable_rows'],0)
        self.assertAlmostEqual(result['observed']['forward_gain'],0)
        self.assertAlmostEqual(result['observed']['inverse_gain'],0)
        self.assertFalse(result['numerical_pilot_pass'])

    def test_random_labels_control(self):
        result=run(fixture(random_labels=True),39,purge=False)
        self.assertGreater(result['permutation']['intersection_union_p'],.05)
        self.assertFalse(result['numerical_pilot_pass'])

    def test_renaming_preserves_scores(self):
        rows=fixture()
        # Use distinct suffixes to retain training examples after purging.
        for i,r in enumerate(rows): r['token'] += 'r'*(1+i//80)
        self.assertEqual(rename_witness(rows)['max_gain_difference'],0)

    def test_purge_blocks_memorized_dictionary(self):
        with self.assertRaises(ValueError): evaluate(fixture(),purge=True)

    def test_parser_rejects_ambiguous_or_multiple_tokens(self):
        raw='<f1r> <! $Q=A $L=A $H=1>\n<f1r.1,@Lc> okal\n<f1r.2,@Lf> ok[al:ar]\n<f1r.3,@Lf> okal,ar\n<f1r.4,@Lf> okal.otar\n'
        self.assertEqual([r['token'] for r in parse(raw)],['okal'])


if __name__=='__main__': unittest.main(verbosity=2)
