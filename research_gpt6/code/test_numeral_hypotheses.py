#!/usr/bin/env python3
"""Exploratory falsification of explicit simple numeral hypotheses, not a decoder."""
import argparse
import csv
import hashlib
import itertools
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from numeral_context_inventory import parse_ivtff, strip_comments

POLICIES = ("dot_full", "dot_comma_full", "dot_left", "dot_comma_left")


def tokens(text, policy):
    if policy.endswith("left"):
        text = text.split("<->", 1)[0]
    else:
        text = text.replace("<->", ".")
    text = strip_comments(text)
    return len([x for x in re.split(r"[.,]" if "comma" in policy else r"\.", text) if x])


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def write_csv(path, rows):
    with path.open("w", newline="") as stream:
        fields = list(dict.fromkeys(k for r in rows for k in r))
        w = csv.DictWriter(stream, fieldnames=fields)
        w.writeheader()
        for row in rows:
            w.writerow({k: json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v for k, v in row.items()})


def eligible_label(raw):
    s = strip_comments(raw)
    if re.fullmatch(r"[a-z]+(?:\.[a-z]+)*", s):
        return s.replace(".", " ")
    return None


def run(corpus, plan_path, out):
    plan = json.loads(plan_path.read_text())
    corpus_hash = hashlib.sha256(corpus.read_bytes()).hexdigest()
    if corpus_hash != plan["corpus_sha256"]:
        raise ValueError("Unexpected corpus")
    out.mkdir(parents=True, exist_ok=True)
    by_folio = defaultdict(list)
    for row in parse_ivtff(corpus):
        by_folio[row["folio"]].append(row)
    f49 = by_folio["49v"]
    ll = [r for r in f49 if r["kind"].endswith("L0")]
    pp = [r for r in f49 if r["kind"].endswith("P0")]
    if len(ll) != 26 or len(pp) != 26:
        raise ValueError("f49v coverage changed")
    aligned = []
    for i, (l, p) in enumerate(zip(ll, pp), 1):
        if l["locus"] + 1 != p["locus"]:
            raise ValueError("Non-adjacent f49v pair")
        aligned.append(dict(folio="49v", physical_line=i, sign=strip_comments(l["text"]),
                            label_locus=l["locus"], text_locus=p["locus"],
                            role="anchor" if i in plan["anchor_physical_lines"] else "within_page_test",
                            **{policy: tokens(p["text"], policy) for policy in POLICIES}))
    external = by_folio[plan["external_folio"]]
    for i, l in enumerate(external[:-1]):
        p = external[i + 1]
        if l["kind"].endswith("L0") and p["kind"].endswith("P0"):
            aligned.append(dict(folio=plan["external_folio"], physical_line=None, sign=strip_comments(l["text"]),
                                label_locus=l["locus"], text_locus=p["locus"], role="external_test",
                                **{policy: tokens(p["text"], policy) for policy in POLICIES}))
    direct = []
    scores = []
    for mode in ("strict", "fixed_alias_sensitivity"):
        for row in aligned:
            sign = row["sign"]
            if mode != "strict":
                sign = plan["alias_sensitivity_only"].get(sign, sign)
            value = plan["arabic_aligned_map"].get(sign)
            if value is not None:
                direct.append({**row, "mode": mode, "hypothesized_value": value,
                               **{policy + "_match": row[policy] == value for policy in POLICIES}})
        for role in ("anchor", "within_page_test", "external_test"):
            selected = [r for r in direct if r["mode"] == mode and r["role"] == role]
            for policy in POLICIES:
                scores.append(dict(mode=mode, role=role, policy=policy,
                                   correct=sum(r[policy + "_match"] for r in selected), total=len(selected)))

    # A best possible fit on f49v: a generous ceiling, not held-out accuracy.
    best_fit = []
    for policy in POLICIES:
        groups = defaultdict(Counter)
        for row in aligned:
            if row["folio"] == "49v":
                groups[row["sign"]][row[policy]] += 1
        best_fit.append(dict(policy=policy, best_possible_correct=sum(max(c.values()) for c in groups.values()), total=26,
                             inconsistent_signs={s: dict(c) for s, c in groups.items() if len(c) > 1},
                             sign_count_distributions={s: dict(c) for s, c in groups.items()}))

    labels = []
    zodiac_map = {r["folio"]: r["sign"] for r in json.loads((plan_path.parent / "numeral_inventory.json").read_text())["zodiac"]}
    for folio in plan["zodiac_folios"]:
        for row in by_folio[folio]:
            if row["kind"].endswith(plan["zodiac_label_locus_suffix"]):
                clean = strip_comments(row["text"])
                clock = re.search(r"<!(\d\d:\d\d)[^>]*>", row["text"])
                canonical = eligible_label(row["text"])
                labels.append(dict(folio=folio, sign=zodiac_map[folio], locus=row["locus"], kind=row["kind"],
                                   clock_hint=clock.group(1) if clock else None, raw_without_comments=clean,
                                   eligible=canonical is not None, canonical=canonical))
    if len(labels) != 299:
        raise ValueError("Zodiac label coverage changed")
    duplicates = []
    overlaps = []
    summaries = []
    signs = list(dict.fromkeys(zodiac_map[f] for f in plan["zodiac_folios"]))
    for mode in ("preserve_words", "join_words_sensitivity"):
        grouped = {}
        for sign in signs:
            selected = [r for r in labels if r["sign"] == sign]
            eligible = [r for r in selected if r["eligible"]]
            key = lambda r: r["canonical"] if mode == "preserve_words" else r["canonical"].replace(" ", "")
            counts = Counter(key(r) for r in eligible)
            grouped[sign] = (counts, len(selected), len(selected) - len(eligible))
            repeated = {s: n for s, n in counts.items() if n > 1}
            summaries.append(dict(mode=mode, sign=sign, total_labels=len(selected), eligible_labels=len(eligible),
                                  omitted=len(selected) - len(eligible), distinct_eligible=len(counts),
                                  duplicate_types=len(repeated), extra_repetitions=sum(n - 1 for n in repeated.values())))
            for s, n in repeated.items():
                occurrences = [dict(folio=r["folio"], locus=r["locus"], clock_hint=r["clock_hint"]) for r in eligible if key(r) == s]
                duplicates.append(dict(mode=mode, sign=sign, label=s, count=n, occurrences=occurrences))
        for a, b in itertools.combinations(signs, 2):
            ca, na, missing_a = grouped[a]
            cb, nb, missing_b = grouped[b]
            shared = sum((ca & cb).values())
            overlaps.append(dict(mode=mode, sign_a=a, sign_b=b, total_a=na, total_b=nb,
                                 eligible_a=sum(ca.values()), eligible_b=sum(cb.values()), shared_exact=shared,
                                 generous_upper_bound=min(na, nb, shared + missing_a + missing_b),
                                 shared_labels=dict(ca & cb)))

    # Individual equal-size diagram pairs avoid combining half-sign drawings.
    individual = []
    complete = [f for f in plan["zodiac_folios"] if len([r for r in labels if r["folio"] == f]) == 30]
    for a, b in itertools.combinations(complete, 2):
        la = [r for r in labels if r["folio"] == a]
        lb = [r for r in labels if r["folio"] == b]
        ca = Counter(r["raw_without_comments"] for r in la)
        cb = Counter(r["raw_without_comments"] for r in lb)
        individual.append(dict(folio_a=a, folio_b=b, total=30, exact_raw_overlap=sum((ca & cb).values())))

    primary_dup = [r for r in duplicates if r["mode"] == "preserve_words"]
    primary_overlap = [r for r in overlaps if r["mode"] == "preserve_words"]
    result = {
        "status": "EXPLORATORY_NUMERAL_HYPOTHESIS_AUDIT",
        "corpus_sha256": corpus_hash, "plan_sha256": hashlib.sha256(plan_path.read_bytes()).hexdigest(),
        "direct_key": {"scores": scores, "unknown_signs_not_imputed": True, "unaligned_f66r_excluded": True},
        "free_wordcount_map_fit_ceiling": best_fit,
        "zodiac": {"labels_total": len(labels), "labels_primary_eligible": sum(r["eligible"] for r in labels),
                    "signs": len(signs), "signs_with_definite_duplicate_labels": sorted({r["sign"] for r in primary_dup}),
                    "duplicate_types": len(primary_dup), "duplicate_occurrences": sum(r["count"] for r in primary_dup),
                    "eligible_sign_pair_count": len(primary_overlap),
                    "max_generous_overlap_upper_bound": max(r["generous_upper_bound"] for r in primary_overlap),
                    "individual_complete_30_label_pairs": len(individual),
                    "max_raw_overlap_in_complete_diagram_pairs": max(r["exact_raw_overlap"] for r in individual)},
        "limits": [
            "No fresh blind dataset; this is an exploratory check of explicitly narrow models.",
            "The Arabic-key check addresses row word counts, not every possible numerical function.",
            "Duplicates contradict a canonical full-label distinct-ordinal model, not all numerical encodings.",
            "Low overlap is reported with omitted-label coverage and a generous upper bound.",
            "Thirty-unit diagram structure remains compatible with labels that contain names, properties or context-dependent information.",
            "Transcription agreement is not independent palaeographic validation."
        ],
    }
    write_json(out / "result.json", result)
    write_json(out / "duplicates.json", duplicates)
    write_json(out / "all_label_records.json", labels)
    write_csv(out / "direct_key_rows.csv", direct)
    write_csv(out / "direct_key_scores.csv", scores)
    write_csv(out / "zodiac_sign_summary.csv", summaries)
    write_csv(out / "zodiac_order_free_overlap.csv", overlaps)
    write_csv(out / "zodiac_complete_diagram_overlap.csv", individual)
    return result


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--corpus", type=Path, required=True)
    p.add_argument("--plan", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    print(json.dumps(run(a.corpus, a.plan, a.output), indent=2, ensure_ascii=False))
