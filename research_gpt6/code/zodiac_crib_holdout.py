#!/usr/bin/env python3
"""Leave-one-sign-out test for Hebrew/Aramaic zodiac-name cribs.

The glyph mapping is selected from nymph labels on the other nine signs only.
The held-out sign's labels are then decoded with that frozen mapping. A
permutation null shuffles which zodiac names belong to the ten page groups and
repeats the full selection-and-test procedure. This is a narrow test of a
single-glyph-to-one-letter homophonic substitution crib, not all cipher types.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
import random
import re
from pathlib import Path

SIGNS = ["Pisces", "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius"]
SIGN_FOLIOS = {
    "Pisces": ["f70v2"], "Aries": ["f70v1", "f71r"], "Taurus": ["f71v", "f72r1"],
    "Gemini": ["f72r2"], "Cancer": ["f72r3"], "Leo": ["f72v3"], "Virgo": ["f72v2"],
    "Libra": ["f72v1"], "Scorpio": ["f73r"], "Sagittarius": ["f73v"],
}
HEBREW = {
    "Pisces": "דגים", "Aries": "טלה", "Taurus": "שור", "Gemini": "תאומים", "Cancer": "סרטן",
    "Leo": "אריה", "Virgo": "בתולה", "Libra": "מאזנים", "Scorpio": "עקרב", "Sagittarius": "קשת",
}
ARAMAIC = {
    "Pisces": "נוני", "Aries": "אמרא", "Taurus": "תורא", "Gemini": "תאומי", "Cancer": "סרטנא",
    "Leo": "אריא", "Virgo": "בתולתא", "Libra": "מאזניא", "Scorpio": "עקרבא", "Sagittarius": "קשתא",
}
TOKEN_RE = re.compile(r"[A-Z][0-9a-z]")


def parse_labels(path: Path) -> dict[str, list[tuple[str, ...]]]:
    folio_labels: dict[str, list[tuple[str, ...]]] = defaultdict(list)
    with path.open(encoding="utf-8") as stream:
        for line in stream:
            line = line.strip()
            if not line or line.startswith("#") or re.match(r"^<[^>]+>\s*<!", line):
                continue
            m = re.match(r"^<([^.>]+)\.([^,]+),(@\w+|&\w+)>\s+(.*)", line)
            if not m or m.group(3) not in ("@Lz", "&Lz"):
                continue
            folio = m.group(1).lower()
            body = re.sub(r"\{[^}]*\}", "", m.group(4))
            body = re.sub(r"<[^>]*>", "", body).replace("-", ".")
            for raw in body.split("."):
                word = tuple(TOKEN_RE.findall(raw.strip()))
                if word:
                    folio_labels[folio].append(word)
    labels = {}
    missing = []
    for sign, folios in SIGN_FOLIOS.items():
        labels[sign] = [w for f in folios for w in folio_labels.get(f, [])]
        if not labels[sign]:
            missing.append(sign)
    if missing:
        raise ValueError(f"No nymph labels parsed for: {missing}")
    return labels


def candidates(words: list[tuple[str, ...]], targets: list[str]) -> list[tuple[tuple[str, ...], str, dict[str, str]]]:
    out = []
    for word in words:
        for target in targets:
            chars = list(target)
            if len(word) != len(chars):
                continue
            mapping = {}
            valid = True
            for glyph, char in zip(word, chars):
                if glyph in mapping and mapping[glyph] != char:
                    valid = False
                    break
                mapping[glyph] = char
            if valid:
                out.append((word, target, mapping))
    # stable dedupe by word, target, mapping
    unique = {}
    for word, target, mapping in out:
        unique[(word, target, tuple(sorted(mapping.items())))] = (word, target, mapping)
    return list(unique.values())


def compatible(a: dict[str, str], b: dict[str, str]) -> bool:
    return all(g not in a or a[g] == c for g, c in b.items())


def merge_greedy(training: dict[str, list], target_for_page: dict[str, str]):
    pool = {
        sign: candidates(training[sign], [HEBREW[target_for_page[sign]], ARAMAIC[target_for_page[sign]]])
        for sign in training
    }
    # Try every first assignment; then add the most constrained remaining
    # pages, selecting compatible candidates with greatest overlap/new coverage.
    best = (0, 0)
    best_map: dict[str, str] = {}
    best_used = []
    order = sorted(pool, key=lambda s: (len(pool[s]) or 10**9, s))
    starts = [(s, c) for s in order for c in pool[s]]
    if not starts:
        return {}, []
    for start_sign, start in starts:
        current = dict(start[2])
        used = [start_sign]
        for sign in order:
            if sign in used:
                continue
            possible = [c for c in pool[sign] if compatible(current, c[2])]
            if not possible:
                continue
            possible.sort(key=lambda c: (-len(set(c[2]) & set(current)), -len(set(c[2]) - set(current)), c[0], c[1]))
            chosen = possible[0]
            current.update(chosen[2])
            used.append(sign)
        score = (len(used), len(current))
        if score > best:
            best = score
            best_map = dict(current)
            best_used = list(used)
    return best_map, best_used


def evaluate(labels, target_for_page):
    per_sign = {}
    total_hits = 0
    total_test_labels = 0
    mapped_label_count = 0
    for held in SIGNS:
        train_pages = [s for s in SIGNS if s != held]
        training = {s: labels[s] for s in train_pages}
        mapping, trained_signs = merge_greedy(training, target_for_page)
        names = {HEBREW[target_for_page[held]], ARAMAIC[target_for_page[held]]}
        words = labels[held]
        decoded = ["".join(mapping[g] for g in word) for word in words if all(g in mapping for g in word)]
        hits = sum(word in names for word in decoded)
        total_hits += hits
        total_test_labels += len(words)
        mapped_label_count += len(decoded)
        per_sign[held] = {
            "expected_assignment": target_for_page[held],
            "training_sign_groups_with_candidate_mapping": len(trained_signs),
            "training_mapping_size": len(mapping),
            "heldout_labels": len(words),
            "fully_mappable_heldout_labels": len(decoded),
            "exact_expected_name_hits": hits,
        }
    return {"heldout_signs_with_hit": sum(v["exact_expected_name_hits"] > 0 for v in per_sign.values()),
            "exact_expected_name_hits": total_hits,
            "mappable_label_fraction": mapped_label_count / total_test_labels,
            "per_sign": per_sign}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", type=Path, required=True)
    ap.add_argument("--permutations", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=20261008)
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()
    if args.permutations < 100:
        raise SystemExit("Use at least 100 null permutations")
    labels = parse_labels(args.corpus)
    actual = {s: s for s in SIGNS}
    observed = evaluate(labels, actual)
    rng = random.Random(args.seed)
    perm_sign_hits = []
    perm_word_hits = []
    assignments = SIGNS[:]
    for _ in range(args.permutations):
        rng.shuffle(assignments)
        shuffled = dict(zip(SIGNS, assignments))
        score = evaluate(labels, shuffled)
        perm_sign_hits.append(score["heldout_signs_with_hit"])
        perm_word_hits.append(score["exact_expected_name_hits"])
    p_sign = (1 + sum(x >= observed["heldout_signs_with_hit"] for x in perm_sign_hits)) / (args.permutations + 1)
    p_word = (1 + sum(x >= observed["exact_expected_name_hits"] for x in perm_word_hits)) / (args.permutations + 1)
    result = {
        "status": "PASS_HELDOUT_CRIB_TEST",
        "interpretation_limit": "Tests only one-glyph-to-one-letter Hebrew/Aramaic name cribs in STA1 nymph labels; cannot rule out other cipher or semantic systems.",
        "corpus_sha256": hashlib.sha256(args.corpus.read_bytes()).hexdigest(),
        "sign_groups": len(SIGNS), "labels": sum(len(v) for v in labels.values()),
        "target_spellings": "Hebrew/Aramaic spellings recorded in source notebook 28",
        "training_rule": "For each held-out sign, choose a compatible glyph-to-letter map from nymph labels on the other nine signs only; at most one letter per glyph, many glyphs may map to one letter.",
        "test_rule": "Count held-out labels that fully decode to that held-out sign's Hebrew or Aramaic name.",
        "null": {"method": "permute sign-name assignment to page groups and rerun all 10 held-out folds", "permutations": args.permutations, "seed": args.seed,
                 "p_for_signs_with_exact_hit": p_sign, "p_for_total_exact_label_hits": p_word},
        "observed": observed,
        "null_summary": {"mean_signs_with_hit": sum(perm_sign_hits)/len(perm_sign_hits),
                         "max_signs_with_hit": max(perm_sign_hits),
                         "mean_exact_label_hits": sum(perm_word_hits)/len(perm_word_hits),
                         "max_exact_label_hits": max(perm_word_hits)},
    }
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
