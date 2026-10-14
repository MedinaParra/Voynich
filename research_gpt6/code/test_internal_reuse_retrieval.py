import unittest
import numpy as np
from internal_reuse_retrieval import parse,clean_tokens,tie_rank


class AnchorFailureControls(unittest.TestCase):
    def test_ties_do_not_create_a_unique_winner(self):
        rank=tie_rank(np.array([.2,.9,.2,.2]),0)
        self.assertEqual((rank['rank_min'],rank['rank_max'],rank['rank_mid']),(2,4,3))

    def test_container_cannot_become_plant_label(self):
        raw='<f100r> <! $Q=S $I=P $L=A $H=1>\n<f100r.1,@Lc> <!116a>jarname\n<f100r.2,@Lf> <!116>rootname\n'
        _,labels=parse(raw)
        self.assertEqual([(x['token'],x['fragment']) for x in labels],[('rootname','116')])

    def test_ambiguity_does_not_create_exact_recurrence(self):
        self.assertEqual(clean_tokens('okal.ok[al:ar].okal,ar.tol<!comment>chd<->chor'),
                         ['okal','tolchd','chor'])

    def test_continued_herbal_paragraph_is_retained(self):
        raw='<f1v> <! $Q=A $I=H $L=A $H=1>\n<f1v.1,@P0> <%>root.leaf\n<f1v.2,+P0> stem.root<$>\n<f1v.3,@Lp> other\n'
        pages,_=parse(raw)
        self.assertEqual(pages['f1v']['tokens'],['root','leaf','stem','root'])


if __name__=='__main__':unittest.main(verbosity=2)
