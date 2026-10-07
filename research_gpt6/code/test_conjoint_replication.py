"""Scientific controls for generalized matching and exact pooled inference."""
import itertools
import json
import math
import statistics
import unittest

import conjoint_replication as r
import q13_matching_control as base

PAIRS=((1,8),(2,7),(3,6),(4,5))


def synthetic_group(sign=1, flat=False):
    physical={base.edge_key(p) for p in PAIRS}
    edges={base.edge_key(p):.25 if flat else sign*float(base.edge_key(p) in physical)
           for p in itertools.combinations(range(1,9),2)}
    metrics={k:dict(edges) for k in ('tfidf','tfidf_residual','tfidf_recto','tfidf_verso')}
    summary,records=r.assess(metrics,PAIRS)
    return {'summary':summary,'all_matching_scores':records,
            'gates':{'recto_all_positive':True,'verso_all_positive':True,'all_leave_pair_out_positive':True}}


class ReplicationControls(unittest.TestCase):
    def test_eight_leaf_reference_and_physically_defined_halves(self):
        group=synthetic_group()
        self.assertEqual(len(group['all_matching_scores']),105)
        self.assertEqual(sum(x['cross_half'] for x in group['all_matching_scores']),24)
        self.assertEqual(group['summary']['tfidf']['all']['exact_tail_p'],1/105)
        self.assertEqual(group['summary']['tfidf']['cross_half']['exact_tail_p'],1/24)

    def test_numeric_relabeling_preserves_pairing_rank(self):
        pairs=((105,114),(106,113),(107,112),(108,111))
        physical={base.edge_key(p) for p in pairs}
        nodes=sorted(itertools.chain.from_iterable(pairs))
        edges={base.edge_key(p):float(base.edge_key(p) in physical) for p in itertools.combinations(nodes,2)}
        summary,_=r.assess({'toy':edges},pairs)
        self.assertEqual(summary['toy']['cross_half']['exact_tail_p'],1/24)

    def test_three_group_positive_control_has_exact_product_size(self):
        groups={name:synthetic_group() for name in ('a','b','c')}
        result=r.pooled_exact(groups,'tfidf')['summary']
        self.assertEqual(result['all']['n_exact'],105**3)
        self.assertEqual(result['cross_half']['n_exact'],24**3)
        self.assertEqual(result['all']['inclusive_tail_count'],1)
        self.assertEqual(result['cross_half']['inclusive_tail_count'],1)

    def test_flat_negative_control_is_not_significant(self):
        groups={name:synthetic_group(flat=True) for name in ('a','b','c')}
        result=r.panel_analysis(groups)
        self.assertFalse(result['all_gates_pass'])
        for null in ('all','cross_half'):
            self.assertEqual(result['pooled']['tfidf']['summary'][null]['exact_tail_p'],1)

    def test_sign_reversal_cannot_be_rescued_by_other_groups(self):
        groups={'a':synthetic_group(),'b':synthetic_group(),'c':synthetic_group(sign=-1)}
        result=r.panel_analysis(groups)
        self.assertFalse(result['gates']['c_tfidf_positive'])
        self.assertFalse(result['all_gates_pass'])

    def test_pooled_normalization_and_cartesian_rank_against_bruteforce(self):
        groups={}
        vals_by_group=[[0.,1.,3.],[1.,2.,4.],[2.,4.,5.]]
        for i,vals in enumerate(vals_by_group):
            groups[str(i)]={'all_matching_scores':[{'scores':{'toy':v},'cross_half':j<2} for j,v in enumerate(vals)],
                            'summary':{'toy':{'all':{'observed':vals[1]}}}}
        result=r.pooled_exact(groups,'toy')
        normalized=[[(v-statistics.mean(vals))/statistics.pstdev(vals) for v in vals] for vals in vals_by_group]
        observed=sum(x[1] for x in normalized)/3
        null=[sum(x)/3 for x in itertools.product(*normalized)]
        expected=sum(x>=observed-1e-12 for x in null)/len(null)
        self.assertEqual(result['summary']['all']['exact_tail_p'],expected)
        self.assertAlmostEqual(result['summary']['all']['observed'],observed)

    def test_nuisance_only_signal_is_removed_on_generalized_leaves(self):
        leaves=tuple(range(1,9));words={n:['ab']*(n+2) for n in leaves}
        style={base.edge_key((a,b)):((a+2*b)%7)/7 for a,b in itertools.combinations(leaves,2)}
        edges={base.edge_key((a,b)):.3+.4*style[base.edge_key((a,b))]
               +.2*abs(math.log(len(words[a])/len(words[b])))+.1*(a-b)**2/100
               for a,b in itertools.combinations(leaves,2)}
        residual,_=r.nuisance_residual(edges,style,words,leaves)
        self.assertLess(max(abs(x) for x in residual.values()),1e-12)
        summary,_=r.assess({'residual':residual},PAIRS)
        self.assertEqual(summary['residual']['all']['exact_tail_p'],1)

    def test_training_excludes_whole_quire_not_just_selected_pairs(self):
        idf,n=r.make_idf({'f1r':['outside'],'f103r':['unselected'],'f105r':['selected']},range(103,117))
        self.assertEqual(n,1)
        self.assertEqual(set(idf),{'outside'})

    def test_unknown_hand_and_empty_sides_are_rejected(self):
        group={'quire':'A','hand':'1','currier':'A','pairs':PAIRS}
        metadata={};pages={}
        for index,pair in enumerate(PAIRS,1):
            for n in pair:
                for side in ('r','v'):
                    page=f'f{n}{side}';metadata[page]={'Q':'A','H':'1','L':'A','B':str(index)};pages[page]=['ab']
        r.validate_group(group,metadata,pages)
        metadata['f1r']['H']='@'
        with self.assertRaises(ValueError):r.validate_group(group,metadata,pages)
        metadata['f1r']['H']='1';pages['f1v']=[]
        with self.assertRaises(ValueError):r.validate_group(group,metadata,pages)

    def test_timesfm_insufficient_rows_block_without_importing_model(self):
        result=r.timesfm_group('<f1r.1,+P0> ab.cd.ef.gh\n',{'pairs':PAIRS})
        self.assertEqual(result['status'],'BLOCKED_INSUFFICIENT_CLEAN_ROWS')
        self.assertFalse(result['partial_group_scored'])

    def test_leave_pair_out_has_fifteen_and_six_references(self):
        group=synthetic_group();edges={'tfidf':{base.edge_key(p):float(base.edge_key(p) in {base.edge_key(x) for x in PAIRS})
                    for p in itertools.combinations(range(1,9),2)}}
        for omitted in PAIRS:
            pairs=tuple(p for p in PAIRS if p!=omitted)
            summary,_=r.assess(edges,pairs)
            self.assertEqual(summary['tfidf']['all']['n_exact'],15)
            self.assertEqual(summary['tfidf']['cross_half']['n_exact'],6)

    def test_q13_global_configuration_is_not_mutated(self):
        before=(base.LEAVES,base.OBSERVED)
        synthetic_group();list(r.cross_matchings(PAIRS))
        self.assertEqual((base.LEAVES,base.OBSERVED),before)


if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ReplicationControls))
    print(json.dumps({'classification':'CONJOINT_REPLICATION_SCIENTIFIC_HARNESS','status':'PASS' if result.wasSuccessful() else 'FAIL',
                      'tests_run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors)},sort_keys=True))
    raise SystemExit(0 if result.wasSuccessful() else 1)
