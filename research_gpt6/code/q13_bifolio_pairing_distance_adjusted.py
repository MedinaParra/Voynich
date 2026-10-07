#!/usr/bin/env python3
"""Distance-adjusted robustness test for Q13 physical bifolio pairing.

The exact 945-matching test found strong pairing signal. This follow-up removes
mean similarity attributable to folio-number distance before ranking matchings.
For each unordered folio pair, its raw similarity is centered by the mean of
all pairs having the same |a-b| distance. Matchings are then scored by mean
centered residual. This tests whether the true physical pairs are unusually
similar beyond a generic distance effect.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import q13_bifolio_pairing_exact as ex
import singulion_q13_order as base

PRIMARY = "tfidf_cosine"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    data = args.corpus.read_bytes()
    blob = base.git_blob_sha1(data)
    if blob != base.SOURCE_BLOB:
        raise SystemExit(f"Corpus blob mismatch: {blob}")
    pages, _, audit = base.parse_pages(data.decode("utf-8"))
    folios, tf, cg = ex.build_folio_vectors(pages)

    all_pairs = [(a,b) for i,a in enumerate(ex.FOLIOS) for b in ex.FOLIOS[i+1:]]
    raw = {p: ex.pair_scores(p, folios, tf, cg) for p in all_pairs}
    metrics = tuple(next(iter(raw.values())).keys())

    by_distance = {m: defaultdict(list) for m in metrics}
    for (a,b), scores in raw.items():
        d = abs(a-b)
        for m in metrics:
            by_distance[m][d].append(scores[m])

    distance_means = {
        m: {d: base.mean(vals) for d,vals in by_distance[m].items()}
        for m in metrics
    }

    residual = {}
    for p,scores in raw.items():
        d = abs(p[0]-p[1])
        residual[p] = {m: scores[m] - distance_means[m][d] for m in metrics}

    matchings = sorted(set(ex.perfect_matchings(ex.FOLIOS)))
    true_m = ex.canonical_matching(ex.TRUE_PAIRS)

    def score_matching(matching, metric):
        return base.mean([residual[(min(a,b),max(a,b))][metric] for a,b in matching])

    true_scores = {m: score_matching(true_m,m) for m in metrics}
    records = []
    for matching in matchings:
        records.append({
            "matching": [f"{a}|{b}" for a,b in matching],
            "scores": {m: score_matching(matching,m) for m in metrics},
        })

    ranks = {
        m: ex.rank_high(true_scores[m], [r["scores"][m] for r in records])
        for m in metrics
    }

    true_pair_residuals = []
    for p in true_m:
        d = abs(p[0]-p[1])
        true_pair_residuals.append({
            "pair": f"{p[0]}|{p[1]}",
            "distance": d,
            "raw": raw[p],
            "distance_mean": {m: distance_means[m][d] for m in metrics},
            "residual": residual[p],
        })

    # Secondary leave-one-pair-out ranking. For each omitted true pair, compare
    # its remaining 4-pair residual mean against all 4-pair subsets induced by
    # removing any one pair from each perfect matching. This is descriptive
    # robustness only, not a second confirmatory p-value.
    loo = []
    for omitted in true_m:
        kept = tuple(p for p in true_m if p != omitted)
        loo.append({
            "omitted": f"{omitted[0]}|{omitted[1]}",
            "remaining_primary_residual_mean": base.mean([residual[p][PRIMARY] for p in kept]),
        })

    primary_rank = ranks[PRIMARY]
    status = "PASS_DISTANCE_ADJUSTED" if primary_rank["percentile"] > 95.0 else "FAIL_DISTANCE_ADJUSTED"

    result = {
        "classification": "Q13_BIFOLIO_PAIRING_DISTANCE_ADJUSTED_NOT_DECIPHERMENT",
        "status": status,
        "source_blob": blob,
        "primary_metric": PRIMARY,
        "true_physical_pairs": [f"{a}|{b}" for a,b in true_m],
        "adjustment": "subtract metric-specific mean among all unordered folio pairs with identical absolute folio-number distance",
        "distance_means": {m: {str(d):v for d,v in sorted(vs.items())} for m,vs in distance_means.items()},
        "true_residual_scores": true_scores,
        "exact_matchings": len(matchings),
        "exact_ranks": ranks,
        "true_pair_residual_detail": true_pair_residuals,
        "leave_one_pair_out_primary": loo,
        "top_10_primary": sorted(records, key=lambda r:r["scores"][PRIMARY], reverse=True)[:10],
        "decision_rule": "PASS_DISTANCE_ADJUSTED iff the true matching's mean distance-centered TF-IDF residual is above the 95th percentile of all 945 perfect matchings.",
        "guardrails": [
            "Distance centering controls a generic |folio-number difference| effect, not every conceivable codicological covariate.",
            "The unique mirror/nesting geometry of the physical quire cannot be fully matched by another perfect matching on this 10-folio set.",
            "Q13-only result requires replication before manuscript-wide inference.",
        ],
        "parser_audit": audit,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
