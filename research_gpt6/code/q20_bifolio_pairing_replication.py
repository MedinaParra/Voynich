#!/usr/bin/env python3
"""Q20 replication of exact physical-bifolio textual pairing signal.

Uses the same conservative EVA parser and aggregate-folio similarity metrics as
Q13. Surviving Q20 folios are 103-108 and 111-116; the six physical bifolia are
(103,116),(104,115),(105,114),(106,113),(107,112),(108,111). The missing central
bifolium is not represented.

Primary raw test: true pairing vs all 10,395 perfect matchings of 12 folios.
Primary robustness test: repeat after centering each pair score by the mean score
of all folio pairs at the same absolute folio-number distance.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

import singulion_q13_order as base

FOLIOS = (103,104,105,106,107,108,111,112,113,114,115,116)
TRUE_PAIRS = ((103,116),(104,115),(105,114),(106,113),(107,112),(108,111))
PRIMARY = "tfidf_cosine"


def canonical_matching(pairs):
    return tuple(sorted((min(a,b), max(a,b)) for a,b in pairs))


def perfect_matchings(items):
    items = tuple(items)
    if not items:
        yield tuple(); return
    a = items[0]
    for i in range(1, len(items)):
        b = items[i]
        rest = items[1:i] + items[i+1:]
        for tail in perfect_matchings(rest):
            yield canonical_matching(((a,b),)+tail)


def folio_tokens(pages,n):
    return list(pages[f"f{n}r"]) + list(pages[f"f{n}v"])


def build_vectors(pages):
    folios={n:folio_tokens(pages,n) for n in FOLIOS}
    df=Counter()
    for n in FOLIOS: df.update(set(folios[n]))
    import math
    N=len(FOLIOS)
    idf={w:math.log((1+N)/(1+d))+1.0 for w,d in df.items()}
    tf={n:base.tfidf(folios[n],idf) for n in FOLIOS}
    cg={n:base.char_ngrams(folios[n],3) for n in FOLIOS}
    return folios,tf,cg


def pair_scores(pair,folios,tf,cg):
    a,b=pair
    return {
        "tfidf_cosine":base.cosine(tf[a],tf[b]),
        "char3_cosine":base.cosine(cg[a],cg[b]),
        "token_jaccard":base.jaccard(folios[a],folios[b]),
        "char_js_similarity":base.js_similarity(folios[a],folios[b]),
    }


def rank_high(value, vals):
    n=len(vals)
    return {
        "rank_best_is_1":1+sum(x>value for x in vals),
        "n_exact_matchings":n,
        "percentile":100.0*sum(x<=value for x in vals)/n,
        "exact_upper_tail_p_including_observed":sum(x>=value for x in vals)/n,
        "null_min":min(vals),"null_mean":base.mean(vals),"null_max":max(vals),
    }


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--corpus',type=Path,required=True); ap.add_argument('--out',type=Path,required=True); a=ap.parse_args()
    data=a.corpus.read_bytes(); blob=base.git_blob_sha1(data)
    if blob!=base.SOURCE_BLOB: raise SystemExit(f"Corpus blob mismatch: {blob}")
    pages,meta,audit=base.parse_pages(data.decode('utf-8'))
    missing=[f"f{n}{s}" for n in FOLIOS for s in ('r','v') if not pages.get(f"f{n}{s}")]
    if missing: raise SystemExit(f"Missing/empty Q20 pages: {missing}")

    folios,tf,cg=build_vectors(pages)
    all_pairs=[(x,y) for i,x in enumerate(FOLIOS) for y in FOLIOS[i+1:]]
    raw={p:pair_scores(p,folios,tf,cg) for p in all_pairs}
    metrics=tuple(next(iter(raw.values())).keys())

    true=canonical_matching(TRUE_PAIRS)
    matchings=sorted(set(perfect_matchings(FOLIOS)))
    if len(matchings)!=10395: raise SystemExit(f"Expected 10395 matchings, got {len(matchings)}")

    def raw_match_score(m,metric): return base.mean([raw[(min(x,y),max(x,y))][metric] for x,y in m])
    true_raw={metric:raw_match_score(true,metric) for metric in metrics}
    raw_records=[{"matching":[f"{x}|{y}" for x,y in m],"scores":{metric:raw_match_score(m,metric) for metric in metrics}} for m in matchings]
    raw_ranks={metric:rank_high(true_raw[metric],[r['scores'][metric] for r in raw_records]) for metric in metrics}

    # Distance-centered residuals.
    bydist={metric:defaultdict(list) for metric in metrics}
    for (x,y),sc in raw.items():
        d=abs(x-y)
        for metric in metrics: bydist[metric][d].append(sc[metric])
    distmean={metric:{d:base.mean(vals) for d,vals in ds.items()} for metric,ds in bydist.items()}
    residual={p:{metric:sc[metric]-distmean[metric][abs(p[0]-p[1])] for metric in metrics} for p,sc in raw.items()}
    def resid_match_score(m,metric): return base.mean([residual[(min(x,y),max(x,y))][metric] for x,y in m])
    true_resid={metric:resid_match_score(true,metric) for metric in metrics}
    resid_records=[{"matching":[f"{x}|{y}" for x,y in m],"scores":{metric:resid_match_score(m,metric) for metric in metrics}} for m in matchings]
    resid_ranks={metric:rank_high(true_resid[metric],[r['scores'][metric] for r in resid_records]) for metric in metrics}

    pair_detail=[]
    for p in true:
        d=abs(p[0]-p[1])
        pair_detail.append({"pair":f"{p[0]}|{p[1]}","distance":d,"raw":raw[p],"distance_mean":{m:distmean[m][d] for m in metrics},"residual":residual[p]})

    status = "PASS_REPLICATION" if (raw_ranks[PRIMARY]['percentile']>95.0 and resid_ranks[PRIMARY]['percentile']>95.0) else "FAIL_REPLICATION"
    result={
        "classification":"Q20_BIFOLIO_PAIRING_REPLICATION_NOT_DECIPHERMENT",
        "status":status,
        "source_blob":blob,
        "folios":list(FOLIOS),
        "true_physical_pairs":[f"{x}|{y}" for x,y in true],
        "missing_central_bifolium":"not represented; only surviving six bifolia tested",
        "primary_metric":PRIMARY,
        "exact_matchings":len(matchings),
        "raw_true_scores":true_raw,
        "raw_exact_ranks":raw_ranks,
        "distance_adjustment":"subtract metric-specific mean among all unordered Q20 folio pairs with identical absolute folio-number distance",
        "distance_adjusted_true_scores":true_resid,
        "distance_adjusted_exact_ranks":resid_ranks,
        "true_pair_detail":pair_detail,
        "top_10_raw_primary":sorted(raw_records,key=lambda r:r['scores'][PRIMARY],reverse=True)[:10],
        "top_10_distance_adjusted_primary":sorted(resid_records,key=lambda r:r['scores'][PRIMARY],reverse=True)[:10],
        "decision_rule":"PASS_REPLICATION iff true Q20 physical matching is >95th percentile for primary TF-IDF in both raw and distance-adjusted exact 10,395-matching nulls.",
        "guardrails":["Replication is structural/codicological, not semantic decipherment.","Q20 folio set excludes the missing central bifolium.","Distance centering removes generic folio-number-distance effects but not every latent scribal/codicological covariate."],
        "parser_audit":audit,
    }
    a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8'); print(json.dumps(result,indent=2))

if __name__=='__main__': main()
