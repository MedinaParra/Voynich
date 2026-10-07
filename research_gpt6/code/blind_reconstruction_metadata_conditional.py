#!/usr/bin/env python3
"""Exact conditional test of blind bifolio reconstruction beyond hand/Currier.

The text-only predictions are frozen first, separately for ZL3b and Takahashi
IT2a, using the already-selected rule: maximum-weight perfect matching under
within-quire distance-centered aggregate-folio TF-IDF.

For inference, the physical matching is randomized ONLY among matchings that
preserve exactly the observed multiset of pair categories defined by Davis hand
(H) and Currier language (L): (same-H?, same-L?). The predictor is held fixed.
We then count how many edges a compatible random physical architecture would
share with the frozen text prediction. Per-quire overlap distributions are
convolved to obtain an exact global conditional p-value.

This directly asks: after preserving everything captured by the labeled hand /
Currier pairing structure, does the text-only reconstruction still recover too
many physical bifolios?
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
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
    vals = []
    for side in ("r", "v"):
        v = meta.get(f"f{n}{side}", {}).get(key)
        if v is not None:
            vals.append(v)
    return tuple(sorted(set(vals)))


def relation(pair, sigs):
    a,b = pair
    ha,hb = sigs[a]["H"], sigs[b]["H"]
    la,lb = sigs[a]["L"], sigs[b]["L"]
    return (bool(ha) and ha == hb, bool(la) and la == lb)


def profile(matching, sigs):
    return tuple(sorted(Counter(relation(p, sigs) for p in matching).items(), key=lambda kv: str(kv[0])))


def overlap(a, bset):
    return sum((min(x,y), max(x,y)) in bset for x,y in a)


def convolve(a, b):
    out = Counter()
    for x,cx in a.items():
        for y,cy in b.items():
            out[x+y] += cx*cy
    return out


def predict_matching(pages, folios):
    weights = aq.build_tfidf_pair_weights(pages, folios)
    residual, _ = aq.distance_center(weights)
    best = None
    best_score = None
    for m in aq.perfect_matchings(folios):
        s = base.mean([residual[(min(x,y),max(x,y))] for x,y in m])
        key = (s, tuple(m))
        if best is None or key > (best_score, tuple(best)):
            best = m
            best_score = s
    return aq.canonical_matching(best), best_score


def conditional_distribution(folios, true_matching, sigs, fixed_prediction):
    target_profile = profile(true_matching, sigs)
    predset = set(aq.canonical_matching(fixed_prediction))
    dist = Counter()
    admitted = 0
    for m in aq.perfect_matchings(folios):
        m = aq.canonical_matching(m)
        if profile(m, sigs) != target_profile:
            continue
        admitted += 1
        dist[overlap(m, predset)] += 1
    if not admitted:
        raise RuntimeError("Conditional null is empty")
    observed = overlap(true_matching, predset)
    expected = sum(k*c for k,c in dist.items()) / admitted
    p = sum(c for k,c in dist.items() if k >= observed) / admitted
    return {
        "observed_overlap": observed,
        "conditional_null_size": admitted,
        "conditional_expected_overlap": expected,
        "exact_p_overlap_ge_observed": p,
        "overlap_distribution": {str(k):v for k,v in sorted(dist.items())},
        "physical_metadata_profile": [[str(k),v] for k,v in target_profile],
    }, dist


def run_transcription(name, pages, meta_zl):
    rows = []
    joint = Counter({0:1})
    observed_total = 0
    expected_total = 0.0
    total_pairs = 0
    for q,pairs in QUIRES.items():
        true = aq.canonical_matching(pairs)
        folios = sorted({n for p in true for n in p})
        missing = [f"f{n}{side}" for n in folios for side in ("r","v") if not pages.get(f"f{n}{side}")]
        if missing:
            raise SystemExit(f"{name}: missing clean held-out pages in {q}: {missing}")
        sigs = {n:{"H":folio_sig(meta_zl,n,"H"), "L":folio_sig(meta_zl,n,"L")} for n in folios}
        pred, score = predict_matching(pages, folios)
        local, dist = conditional_distribution(folios, true, sigs, pred)
        observed_total += local["observed_overlap"]
        expected_total += local["conditional_expected_overlap"]
        total_pairs += len(true)
        joint = convolve(joint, dist)
        rows.append({
            "quire": q,
            "physical_pairs": [f"{a}|{b}" for a,b in true],
            "predicted_pairs": [f"{a}|{b}" for a,b in pred],
            "prediction_adjusted_score": score,
            "folio_metadata": {str(n):{"H":list(sigs[n]["H"]),"L":list(sigs[n]["L"])} for n in folios},
            **local,
        })
    nnull = sum(joint.values())
    ge = sum(c for k,c in joint.items() if k >= observed_total)
    return {
        "transcription": name,
        "results": rows,
        "global": {
            "observed_recovered_pairs": observed_total,
            "total_physical_pairs": total_pairs,
            "pair_accuracy": observed_total/total_pairs,
            "conditional_expected_recovered_pairs": expected_total,
            "exact_joint_conditional_null_outcomes": nnull,
            "exact_conditional_p_overlap_ge_observed": ge/nnull,
            "joint_conditional_overlap_distribution": {str(k):v for k,v in sorted(joint.items())},
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--zl", type=Path, required=True)
    ap.add_argument("--it", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    zl_bytes = args.zl.read_bytes()
    if base.git_blob_sha1(zl_bytes) != base.SOURCE_BLOB:
        raise SystemExit("ZL corpus blob mismatch")
    it_bytes = args.it.read_bytes()
    it_sha = hashlib.sha256(it_bytes).hexdigest()
    if it_sha != IT2A_SHA256:
        raise SystemExit(f"IT2a SHA256 mismatch: {it_sha}")

    zl_pages, zl_meta, zl_audit = base.parse_pages(zl_bytes.decode("utf-8"))
    it_pages, _, it_audit = base.parse_pages(it_bytes.decode("utf-8", errors="replace"))

    zl = run_transcription("ZL3b", zl_pages, zl_meta)
    it = run_transcription("Takahashi IT2a", it_pages, zl_meta)

    result = {
        "classification": "BLIND_BIFOLIO_RECONSTRUCTION_METADATA_CONDITIONAL_NOT_DECIPHERMENT",
        "zl_source_blob": base.SOURCE_BLOB,
        "it2a_sha256": it_sha,
        "heldout_quires": list(QUIRES),
        "prediction_rule": "frozen maximum perfect matching by within-quire distance-centered aggregate-folio TF-IDF",
        "conditional_null": "all physical perfect matchings preserving exactly the observed multiset of same/different Davis-hand and same/different Currier pair categories",
        "zl": zl,
        "it2a": it,
        "decision_note": "Evidence beyond labeled hand/Currier structure is supported when the exact global conditional overlap p-value remains small with the text prediction held fixed.",
        "guardrails": [
            "Hand/Currier labels come from the frozen ZL metadata and are used only to define the conditional randomization null, not to choose predicted edges.",
            "This controls labeled hand/Currier pairing structure, not every possible paleographic, topical, illustration, or production covariate.",
            "IT2a is an independent transcription of the same manuscript, not an independent manuscript sample.",
            "The outcome is physical-pair reconstruction only; it does not establish reading order or semantics.",
        ],
        "parser_audit": {"ZL3b":zl_audit, "IT2a":it_audit},
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
