#!/usr/bin/env python3
"""Blind bifolio reconstruction after removing distance and H/Currier effects.

For each held-out complete quire A,C,D,E,F,G and each transcription (ZL3b and
Takahashi IT2a):

1. Build aggregate-folio TF-IDF similarities for every candidate folio pair.
2. Using only folio number and frozen ZL metadata (Davis H / Currier L), project
   those edge weights onto the orthogonal complement of two additive nuisance
   spaces by alternating exact group centering until convergence:
      a) absolute folio-number distance;
      b) exact unordered pair of (H-signature, L-signature) folio categories.
   No physical bifolio $B label is used in the predictor.
3. Choose the maximum-weight perfect matching on the residual edge weights.
4. Only after prediction, compare to the physical $B matching.
5. Report both the ordinary exact overlap null and an exact metadata-conditioned
   overlap null preserving the physical matching's same/different H/L profile.

This is a stronger test of incremental textual pairing information beyond known
folio distance and labeled scribal/language structure. It is not decipherment.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

import singulion_q13_order as base
import all_quires_bifolio_holdout as aq

IT2A_SHA256 = "7f27a8b0feed8f6de0a99900df6bf912dd1d295c38e5f830bac8b41c3f536fb5"
QUIRES = {
    "A": ((1,8),(2,7),(3,6),(4,5)),
    "C": ((17,24),(18,23),(19,22),(20,21)),
    "D": ((25,32),(26,31),(27,30),(28,29)),
    "E": ((33,40),(34,39),(35,38),(36,37)),
    "F": ((41,48),(42,47),(43,46),(44,45)),
    "G": ((49,56),(50,55),(51,54),(52,53)),
}


def folio_sig(meta, n, key):
    vals=[]
    for side in ("r","v"):
        v=meta.get(f"f{n}{side}",{}).get(key)
        if v is not None: vals.append(v)
    return tuple(sorted(set(vals)))


def full_sig(meta,n):
    return (folio_sig(meta,n,"H"), folio_sig(meta,n,"L"))


def metadata_edge_key(pair, sigs):
    a,b=pair
    sa,sb=sigs[a],sigs[b]
    return tuple(sorted((repr(sa),repr(sb))))


def relation(pair,sigs):
    a,b=pair
    ha,la=sigs[a]; hb,lb=sigs[b]
    return (bool(ha) and ha==hb, bool(la) and la==lb)


def relation_profile(matching,sigs):
    c=Counter(relation(p,sigs) for p in matching)
    return tuple(sorted(c.items(),key=lambda kv:str(kv[0])))


def alternating_residualize(weights, sigs, tol=1e-14, max_iter=10000):
    """Remove additive group means for distance and exact metadata-pair class."""
    residual=dict(weights)
    global_mean=sum(residual.values())/len(residual)
    residual={p:v-global_mean for p,v in residual.items()}

    def center(group_key):
        groups=defaultdict(list)
        for p,v in residual.items(): groups[group_key(p)].append((p,v))
        max_abs=0.0
        for rows in groups.values():
            m=sum(v for _,v in rows)/len(rows)
            max_abs=max(max_abs,abs(m))
            for p,_ in rows: residual[p]-=m
        return max_abs

    last=None
    for it in range(1,max_iter+1):
        dmean=center(lambda p:abs(p[0]-p[1]))
        mmean=center(lambda p:metadata_edge_key(p,sigs))
        err=max(dmean,mmean)
        if err<tol:
            return residual,{"iterations":it,"converged":True,"max_group_mean_before_last_center":err,"raw_global_mean":global_mean}
        if last is not None and abs(last-err)<tol*1e-3 and it>100:
            # Numerical plateau well below any ranking-relevant scale.
            return residual,{"iterations":it,"converged":False,"plateau":True,"max_group_mean_before_last_center":err,"raw_global_mean":global_mean}
        last=err
    return residual,{"iterations":max_iter,"converged":False,"max_group_mean_before_last_center":last,"raw_global_mean":global_mean}


def predict(residual,folios):
    best=None; best_score=None
    for m in aq.perfect_matchings(folios):
        m=aq.canonical_matching(m)
        score=base.mean([residual[(min(a,b),max(a,b))] for a,b in m])
        key=(score,tuple(m))
        if best is None or key>(best_score,tuple(best)):
            best=m;best_score=score
    return best,best_score


def overlap(m, target_set):
    return sum((min(a,b),max(a,b)) in target_set for a,b in m)


def convolve(a,b):
    out=Counter()
    for x,cx in a.items():
        for y,cy in b.items(): out[x+y]+=cx*cy
    return out


def null_distribution(folios,pred,true,sigs,conditional=False):
    predset=set(pred)
    true_profile=relation_profile(true,sigs)
    dist=Counter()
    for m in aq.perfect_matchings(folios):
        m=aq.canonical_matching(m)
        if conditional and relation_profile(m,sigs)!=true_profile:
            continue
        dist[overlap(m,predset)]+=1
    return dist


def summarize_dist(dist,observed):
    n=sum(dist.values())
    expected=sum(k*c for k,c in dist.items())/n
    p=sum(c for k,c in dist.items() if k>=observed)/n
    return {"null_size":n,"expected_overlap":expected,"exact_p_overlap_ge_observed":p,"distribution":{str(k):v for k,v in sorted(dist.items())}}


def run_transcription(name,pages,meta):
    rows=[]
    joint_all=Counter({0:1});joint_cond=Counter({0:1})
    observed_total=0; total_pairs=0
    for q,pairs in QUIRES.items():
        true=aq.canonical_matching(pairs); trueset=set(true)
        folios=sorted({n for p in true for n in p})
        missing=[f"f{n}{s}" for n in folios for s in ("r","v") if not pages.get(f"f{n}{s}")]
        if missing: raise SystemExit(f"{name}: missing pages in {q}: {missing}")
        sigs={n:full_sig(meta,n) for n in folios}
        raw=aq.build_tfidf_pair_weights(pages,folios)
        residual,fit=alternating_residualize(raw,sigs)
        pred,score=predict(residual,folios)
        observed=overlap(pred,trueset)
        d_all=null_distribution(folios,pred,true,sigs,False)
        d_cond=null_distribution(folios,pred,true,sigs,True)
        joint_all=convolve(joint_all,d_all);joint_cond=convolve(joint_cond,d_cond)
        observed_total+=observed; total_pairs+=len(true)
        rows.append({
            "quire":q,
            "physical_pairs":[f"{a}|{b}" for a,b in true],
            "predicted_pairs":[f"{a}|{b}" for a,b in pred],
            "recovered":observed,
            "total":len(true),
            "accuracy":observed/len(true),
            "residual_prediction_score":score,
            "residualization":fit,
            "ordinary_overlap_null":summarize_dist(d_all,observed),
            "metadata_conditioned_overlap_null":summarize_dist(d_cond,observed),
        })
    return {
        "transcription":name,
        "results":rows,
        "global":{
            "recovered_pairs":observed_total,
            "total_pairs":total_pairs,
            "pair_accuracy":observed_total/total_pairs,
            "ordinary_exact":summarize_dist(joint_all,observed_total),
            "metadata_conditioned_exact":summarize_dist(joint_cond,observed_total),
        },
    }


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--zl',type=Path,required=True);ap.add_argument('--it',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    zlb=args.zl.read_bytes();itb=args.it.read_bytes()
    if base.git_blob_sha1(zlb)!=base.SOURCE_BLOB: raise SystemExit('ZL blob mismatch')
    itsha=hashlib.sha256(itb).hexdigest()
    if itsha!=IT2A_SHA256: raise SystemExit(f'IT2a SHA256 mismatch: {itsha}')
    zl_pages,zl_meta,zl_audit=base.parse_pages(zlb.decode('utf-8'))
    it_pages,_,it_audit=base.parse_pages(itb.decode('utf-8',errors='replace'))
    result={
        "classification":"BIFOLIO_DISTANCE_METADATA_DOUBLE_RESIDUAL_BLIND_RECONSTRUCTION_NOT_DECIPHERMENT",
        "zl_source_blob":base.SOURCE_BLOB,
        "it2a_sha256":itsha,
        "heldout_quires":list(QUIRES),
        "edge_residualization":"alternating additive group centering of TF-IDF edge similarity by absolute folio-number distance and exact unordered Davis-H/Currier-L folio-signature pair category",
        "predictor":"maximum-weight perfect matching on nuisance-residual edge weights; physical $B never used for edge selection",
        "zl":run_transcription('ZL3b',zl_pages,zl_meta),
        "it2a":run_transcription('Takahashi IT2a',it_pages,zl_meta),
        "guardrails":[
            "Residualization removes additive distance and labeled H/L edge effects, not arbitrary interactions or unlabeled paleographic/topic covariates.",
            "Metadata are nuisance covariates only; physical $B labels are used after prediction for evaluation.",
            "IT2a is a transcription replication of the same manuscript, not an independent manuscript.",
            "This tests physical pairing, not reading order or semantics.",
        ],
        "parser_audit":{"ZL3b":zl_audit,"IT2a":it_audit},
    }
    args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,indent=2))

if __name__=='__main__':main()
