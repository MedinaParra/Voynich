#!/usr/bin/env python3
"""Exact Q13 bifolio-pairing falsification test.

Question: do the five physical Q13 bifolio pairs stand out textually among all
perfect matchings of folios 75..84? This deliberately ignores any proposed
inter-bifolio order. It is therefore a cleaner test of the 'physical unit'
signal suggested by the earlier singulion-order experiment.

Primary statistic: mean TF-IDF cosine between aggregate folio texts (r+v).
Null: all 945 perfect matchings of 10 labeled folios into 5 unordered pairs.
Secondary metrics are reported without changing the primary decision.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import singulion_q13_order as base

FOLIOS = tuple(range(75, 85))
TRUE_PAIRS = ((75, 84), (76, 83), (77, 82), (78, 81), (79, 80))
ADJACENT_PAIRS = ((75, 76), (77, 78), (79, 80), (81, 82), (83, 84))
PRIMARY = "tfidf_cosine"


def canonical_matching(pairs):
    return tuple(sorted((min(a,b), max(a,b)) for a,b in pairs))


def perfect_matchings(items):
    items = tuple(items)
    if not items:
        yield tuple()
        return
    a = items[0]
    for i in range(1, len(items)):
        b = items[i]
        rest = items[1:i] + items[i+1:]
        for tail in perfect_matchings(rest):
            yield canonical_matching(((a,b),) + tail)


def folio_tokens(pages, n):
    return list(pages[f"f{n}r"]) + list(pages[f"f{n}v"])


def build_folio_vectors(pages):
    folios = {n: folio_tokens(pages, n) for n in FOLIOS}
    ids = list(FOLIOS)
    df = Counter()
    for n in ids:
        df.update(set(folios[n]))
    N = len(ids)
    import math
    idf = {w: math.log((1+N)/(1+d))+1.0 for w,d in df.items()}
    tf = {n: base.tfidf(folios[n], idf) for n in ids}
    cg = {n: base.char_ngrams(folios[n], 3) for n in ids}
    return folios, tf, cg


def pair_scores(pair, folios, tf, cg):
    a,b = pair
    return {
        "tfidf_cosine": base.cosine(tf[a], tf[b]),
        "char3_cosine": base.cosine(cg[a], cg[b]),
        "token_jaccard": base.jaccard(folios[a], folios[b]),
        "char_js_similarity": base.js_similarity(folios[a], folios[b]),
    }


def matching_scores(matching, folios, tf, cg):
    by_pair = [pair_scores(p, folios, tf, cg) for p in matching]
    metrics = by_pair[0].keys()
    return {m: base.mean([x[m] for x in by_pair]) for m in metrics}


def rank_high(value, vals):
    n = len(vals)
    return {
        "rank_best_is_1": 1 + sum(x > value for x in vals),
        "n_exact_matchings": n,
        "percentile": 100.0 * sum(x <= value for x in vals) / n,
        "exact_upper_tail_p_including_observed": sum(x >= value for x in vals) / n,
        "null_min": min(vals),
        "null_mean": base.mean(vals),
        "null_max": max(vals),
    }


def distance_multiset(matching):
    return tuple(sorted(abs(a-b) for a,b in matching))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    data = args.corpus.read_bytes()
    blob = base.git_blob_sha1(data)
    if blob != base.SOURCE_BLOB:
        raise SystemExit(f"Corpus blob mismatch: {blob}")

    pages, meta, audit = base.parse_pages(data.decode("utf-8"))
    missing = [f"f{n}{s}" for n in FOLIOS for s in ("r","v") if not pages.get(f"f{n}{s}")]
    if missing:
        raise SystemExit(f"Missing/empty pages: {missing}")

    folios, tf, cg = build_folio_vectors(pages)
    true_m = canonical_matching(TRUE_PAIRS)
    adjacent_m = canonical_matching(ADJACENT_PAIRS)
    true_scores = matching_scores(true_m, folios, tf, cg)
    adjacent_scores = matching_scores(adjacent_m, folios, tf, cg)

    matchings = sorted(set(perfect_matchings(FOLIOS)))
    if len(matchings) != 945:
        raise SystemExit(f"Expected 945 perfect matchings, got {len(matchings)}")

    records = []
    for m in matchings:
        records.append({
            "matching": [f"{a}|{b}" for a,b in m],
            "distance_multiset": list(distance_multiset(m)),
            "scores": matching_scores(m, folios, tf, cg),
        })

    metrics = tuple(true_scores)
    ranks = {metric: rank_high(true_scores[metric], [r["scores"][metric] for r in records]) for metric in metrics}

    true_dist = distance_multiset(true_m)
    distance_matched = [r for r in records if tuple(r["distance_multiset"]) == true_dist]
    distance_ranks = {
        metric: rank_high(true_scores[metric], [r["scores"][metric] for r in distance_matched])
        for metric in metrics
    }

    pair_detail = []
    for p in true_m:
        pair_detail.append({
            "pair": f"{p[0]}|{p[1]}",
            "distance": abs(p[0]-p[1]),
            "scores": pair_scores(p, folios, tf, cg),
        })

    # Leave-one-pair-out robustness: does the true matching remain strong if one
    # physical pair is removed from the mean? This catches one-pair domination.
    loo = []
    for omitted in true_m:
        kept = tuple(p for p in true_m if p != omitted)
        vals = [pair_scores(p, folios, tf, cg)[PRIMARY] for p in kept]
        loo.append({
            "omitted": f"{omitted[0]}|{omitted[1]}",
            "primary_mean_remaining": base.mean(vals),
        })

    primary_rank = ranks[PRIMARY]
    pass_pairing = primary_rank["percentile"] > 95.0

    top10 = sorted(records, key=lambda r: r["scores"][PRIMARY], reverse=True)[:10]

    result = {
        "classification": "Q13_BIFOLIO_PAIRING_EXACT_NOT_DECIPHERMENT",
        "status": "PASS_PAIRING" if pass_pairing else "FAIL_PAIRING",
        "source_blob": blob,
        "source_policy": "same conservative literal-lowercase EVA parser as Q13 order experiment",
        "folios": list(FOLIOS),
        "true_physical_pairs": [f"{a}|{b}" for a,b in true_m],
        "adjacent_control_pairs": [f"{a}|{b}" for a,b in adjacent_m],
        "primary_metric": PRIMARY,
        "true_scores": true_scores,
        "adjacent_control_scores": adjacent_scores,
        "exact_matchings": len(records),
        "exact_ranks": ranks,
        "true_distance_multiset": list(true_dist),
        "distance_matched_null_size": len(distance_matched),
        "distance_matched_ranks": distance_ranks,
        "true_pair_detail": pair_detail,
        "leave_one_pair_out_primary": loo,
        "top_10_matchings_primary": top10,
        "decision_rule": "PASS_PAIRING iff mean aggregate-folio TF-IDF cosine for the five physical pairs is above the 95th percentile of all 945 perfect matchings.",
        "interpretation_guardrails": [
            "Tests physical pairing only; does not test the inter-bifolio order.",
            "Aggregate folio similarity is orientation-independent and therefore avoids choosing recto/verso direction after seeing results.",
            "Q13 alone cannot establish manuscript-wide generality.",
            "A positive result is structural/codicological corroboration, not decipherment or semantics.",
        ],
        "parser_audit": audit,
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
