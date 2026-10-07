#!/usr/bin/env python3
"""Blind predictive reconstruction of physical bifolia in held-out complete quires.

The similarity rule was fixed by the earlier Q13/Q20 work: aggregate-folio
TF-IDF cosine, centered by absolute folio-number distance. For prediction, $B is
NOT used to choose edges. We select the maximum-weight perfect matching from the
folio texts alone and only then compare it with the physical $B pairing.

To avoid leakage through missing-data selection, the confirmatory held-out set
contains only previously unseen quires whose eligible structure has no incomplete
$B groups: Q=A,C,D,E,F,G. Q=M/T are excluded because they motivated the rule;
Q=B is excluded because one incomplete physical bifolium would make selecting a
10/6-folio test set depend on $B metadata.

The global p-value is exact: convolve the overlap-count distributions of all
perfect matchings in each held-out quire and ask how often random matchings would
recover at least as many physical edges as the text-only predictions.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import singulion_q13_order as base
import all_quires_bifolio_holdout as aq

SEEN={"M","T"}


def convolve(a,b):
    out=Counter()
    for x,cx in a.items():
        for y,cy in b.items(): out[x+y]+=cx*cy
    return out


def overlap(m,true_set):
    return sum((min(a,b),max(a,b)) in true_set for a,b in m)


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--corpus',type=Path,required=True); ap.add_argument('--out',type=Path,required=True); args=ap.parse_args()
    data=args.corpus.read_bytes(); blob=base.git_blob_sha1(data)
    if blob!=base.SOURCE_BLOB: raise SystemExit('Corpus blob mismatch')
    pages,meta,audit=base.parse_pages(data.decode('utf-8'))
    byq,saudit=aq.build_complete_bifolia(pages,meta)

    rows=[]; excluded=[]; global_dist=Counter({0:1}); observed_total=0; total_pairs=0; expected_random=0.0
    for q,true_pairs in sorted(byq.items()):
        if q in SEEN:
            excluded.append({"quire":q,"reason":"seen Q13/Q20"}); continue
        if len(true_pairs)<3:
            excluded.append({"quire":q,"reason":"fewer than 3 complete bifolia"}); continue
        if saudit[q]['nonpair_groups']:
            excluded.append({"quire":q,"reason":"incomplete B group would leak metadata into folio-set selection"}); continue
        folios=sorted({n for p in true_pairs for n in p}); k=len(true_pairs)
        true=aq.canonical_matching(true_pairs); true_set=set(true)
        weights=aq.build_tfidf_pair_weights(pages,folios)
        residual,_=aq.distance_center(weights)

        best=None; best_score=None; dist=Counter(); nmatch=0
        for m in aq.perfect_matchings(folios):
            nmatch+=1
            s=base.mean([residual[(min(a,b),max(a,b))] for a,b in m])
            ov=overlap(m,true_set); dist[ov]+=1
            key=(s, tuple(m))
            if best is None or key>(best_score,tuple(best)):
                best=m; best_score=s
        recovered=overlap(best,true_set)
        observed_total+=recovered; total_pairs+=k
        expected_random+=k/(2*k-1)
        global_dist=convolve(global_dist,dist)
        rows.append({
            "quire":q,"folios":folios,"physical_pairs":[f"{a}|{b}" for a,b in true],
            "predicted_pairs":[f"{a}|{b}" for a,b in best],
            "predicted_adjusted_score":best_score,
            "recovered_physical_pairs":recovered,"total_physical_pairs":k,
            "pair_accuracy":recovered/k,
            "exact_matching_count":nmatch,
            "random_overlap_distribution":{str(x):c for x,c in sorted(dist.items())},
        })

    total_null=sum(global_dist.values())
    ge=sum(c for x,c in global_dist.items() if x>=observed_total)
    result={
        "classification":"BLIND_BIFOLIO_RECONSTRUCTION_HOLDOUT_NOT_DECIPHERMENT",
        "source_blob":blob,
        "prediction_rule":"maximum perfect matching by distance-centered aggregate-folio TF-IDF; no $B metadata used for edge selection",
        "heldout_quires":[r['quire'] for r in rows],
        "results":rows,
        "global":{
            "recovered_pairs":observed_total,"total_pairs":total_pairs,
            "pair_accuracy":observed_total/total_pairs if total_pairs else None,
            "random_expected_recovered_pairs":expected_random,
            "exact_joint_null_outcomes":total_null,
            "exact_p_random_recovers_at_least_observed":ge/total_null if total_null else None,
            "joint_overlap_distribution":{str(x):c for x,c in sorted(global_dist.items())},
        },
        "excluded":excluded,
        "guardrails":[
            "This predicts physical pair membership, not reading order or semantic content.",
            "Quires with incomplete $B groups are excluded from the predictive hold-out to prevent metadata leakage in choosing the folio set.",
            "The prediction rule was selected after Q13/Q20, but all reported predictive quires are held out from that selection.",
        ],
        "parser_audit":audit,
    }
    args.out.parent.mkdir(parents=True,exist_ok=True); args.out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8'); print(json.dumps(result,indent=2))

if __name__=='__main__': main()
