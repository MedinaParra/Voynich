import itertools,unittest
from fractions import Fraction
from boundary_adversary import score,make_locus,certificates

class MathematicalControls(unittest.TestCase):
    def test_uniform_permutation_centering(self):
        middle=['alpha','alpha','alphi','bravo']
        values=[score(['fixed']+list(p)+['last']) for p in itertools.permutations(middle)]
        self.assertEqual(sum(values,Fraction(0)),0)
    def test_two_interiors_are_degenerate(self):
        self.assertEqual(score(['fixed','alpha','alphi','last']),0)
    def test_budget_is_at_most_and_global_extrema_match_exhaustive(self):
        loci=[make_locus('one','alphaalphialpha',[5],[10],[5,10]),make_locus('two','bravobravozulu',[5],[10],[5,10])]
        actual,_=certificates(loci,[0,1,2])
        combos=list(itertools.product(*(l['paths'] for l in loci)))
        for row in actual:
            feasible=[sum((Fraction(*p['score']) for p in combo),Fraction(0)) for combo in combos if sum(p['flips'] for p in combo)<=row['budget']]
            self.assertEqual(Fraction(*row['min']),min(feasible));self.assertEqual(Fraction(*row['max']),max(feasible))
    def test_replica_envelope_dominates_every_global_world(self):
        differences=[[-2,1],[0,-1,2],[-1,0]]
        envelope=sum(map(max,differences))
        self.assertTrue(all(sum(v)<=envelope for v in itertools.product(*differences)))

if __name__=='__main__':unittest.main(verbosity=2)
