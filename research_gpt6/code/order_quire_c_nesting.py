#!/usr/bin/env python3
"""Reconstruct the nesting order of Quire C (folios 17--24).

This is deliberately different from the Q13/Q20 loose-singulion model.
Quire C is treated as a normal gathering of four known physical bifolia:
  B1=17|24, B2=18|23, B3=19|22, B4=20|21.

For an outer->inner nesting (a1|b1, ..., an|bn), with each bifolium's current
leaf orientation fixed, the reading leaf sequence is:
  a1, a2, ..., an, bn, ..., b2, b1.

Each candidate therefore implies seven cross-leaf reading transitions
  verso(previous leaf) -> recto(next leaf).
We score those transitions using only transcription content, never folio-number
spacing, and enumerate all 4! = 24 possible nestings.

Robustness design:
- frozen ZL3b transcription;
- independent Takahashi IT2a transcription;
- boundary windows 25, 50, 100, 200 tokens plus whole-page boundaries;
- three frozen components at every window: token TF-IDF, character 3--5gram
  TF-IDF, token-set Jaccard;
- components are z-scored over all 56 directed leaf transitions and equally
  averaged; no weights are fitted to Quire C;
- the current physical nesting is prespecified before reading the output.

This tests reading-continuity compatibility of alternative nestings. It does
not prove historical rebinding and does not decode Voynichese.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median

IT2A_SHA256 = "7f27a8b0feed8f6de0a99900df6bf912dd1d295c38e5f830bac8b41c3f536fb5"
FOLIOS = tuple(range(17, 25))
BIFOLIA = {
    "B1_17|24": (17, 24),
    "B2_18|23": (18, 23),
    "B3_19|22": (19, 22),
    "B4_20|21": (20, 21),
}
CURRENT = tuple(BIFOLIA)
WINDOWS = (25, 50, 100, 200, 0)  # 0 = whole verso/recto page


def physical_leaf(page: str) -> str:
    m = re.match(r"^(f[0-9]+)", page)
    return m.group(1) if m else ""


def parse_pages(raw: str):
    """Conservative EVA parser compatible with ZL3b and Takahashi IT2a."""
    pages = defaultdict(list)
    audit = Counter()
    for line in raw.splitlines():
        m = re.match(r"^<([^>]+)>\s*(.*)$", line)
        if not m or "," not in m.group(1):
            continue
        locus, text = m.groups()
        if not re.search(r"P[0-9a-z]", locus.split(",", 1)[1]):
            continue
        page = locus.split(".", 1)[0]
        if not physical_leaf(page):
            continue
        text = re.sub(r"<[^>]*>", "", text.replace("<->", "|"))
        text = re.sub(r"\s+", ".", text.strip()).replace(",", ".")
        for token in re.split(r"([.|])", text):
            if not token or token == ".":
                continue
            if token != "|" and re.fullmatch(r"[a-z]{1,64}", token):
                pages[page].append(token)
            else:
                if token == "|":
                    audit["drawing_breaks"] += 1
                else:
                    audit["uncertain_chunks"] += 1
        audit["paragraph_loci"] += 1
    return dict(pages), dict(audit)


def leaf_sequence(nesting):
    pairs = [BIFOLIA[x] for x in nesting]
    return [a for a, _ in pairs] + [b for _, b in reversed(pairs)]


def page_ids_for_transition(a: int, b: int):
    return f"f{a}v", f"f{b}r"


def window_tokens(tokens, side: str, n: int):
    if n == 0:
        return list(tokens)
    return list(tokens[-n:] if side == "tail" else tokens[:n])


def token_counter(tokens):
    return Counter(tokens)


def char_counter(tokens):
    c = Counter()
    for w in tokens:
        s = f"^{w}$"
        for n in (3, 4, 5):
            for i in range(max(0, len(s) - n + 1)):
                c[s[i:i+n]] += 1
    return c


def tfidf(counters):
    names = list(counters)
    n = len(names)
    df = Counter()
    for c in counters.values():
        df.update(c.keys())
    idf = {k: math.log((1+n)/(1+d)) + 1.0 for k, d in df.items()}
    out = {}
    for name, c in counters.items():
        total = sum(c.values()) or 1
        out[name] = {k: (v/total)*idf[k] for k, v in c.items()}
    return out


def cosine(a, b):
    if not a or not b:
        return 0.0
    dot = sum(v*b.get(k, 0.0) for k, v in a.items())
    na = math.sqrt(sum(v*v for v in a.values()))
    nb = math.sqrt(sum(v*v for v in b.values()))
    return dot/(na*nb) if na and nb else 0.0


def jaccard(a, b):
    aa, bb = set(a), set(b)
    u = len(aa | bb)
    return len(aa & bb)/u if u else 0.0


def znorm(d):
    vals = list(d.values())
    mu = sum(vals)/len(vals)
    sd = math.sqrt(sum((x-mu)**2 for x in vals)/len(vals)) or 1.0
    return {k:(v-mu)/sd for k,v in d.items()}


def directed_transition_matrix(pages, window):
    tails = {}
    heads = {}
    for f in FOLIOS:
        v = f"f{f}v"; r = f"f{f}r"
        tails[f] = window_tokens(pages[v], "tail", window)
        heads[f] = window_tokens(pages[r], "head", window)

    # TF-IDF must share a vocabulary between all tail/head boundary documents.
    tok_docs = {f"T{f}": token_counter(tails[f]) for f in FOLIOS}
    tok_docs.update({f"H{f}": token_counter(heads[f]) for f in FOLIOS})
    chr_docs = {f"T{f}": char_counter(tails[f]) for f in FOLIOS}
    chr_docs.update({f"H{f}": char_counter(heads[f]) for f in FOLIOS})
    tok_vec = tfidf(tok_docs)
    chr_vec = tfidf(chr_docs)

    comps = {"token_tfidf": {}, "char35_tfidf": {}, "token_jaccard": {}}
    for a in FOLIOS:
        for b in FOLIOS:
            if a == b:
                continue
            pair = (a, b)
            comps["token_tfidf"][pair] = cosine(tok_vec[f"T{a}"], tok_vec[f"H{b}"])
            comps["char35_tfidf"][pair] = cosine(chr_vec[f"T{a}"], chr_vec[f"H{b}"])
            comps["token_jaccard"][pair] = jaccard(tails[a], heads[b])
    z = {k: znorm(v) for k, v in comps.items()}
    combined = {pair: sum(z[k][pair] for k in z)/len(z) for pair in z["token_tfidf"]}
    return combined, comps


def score_nesting(nesting, matrix):
    leaves = leaf_sequence(nesting)
    transitions = list(zip(leaves, leaves[1:]))
    return sum(matrix[p] for p in transitions), leaves, transitions


def enumerate_nestings(matrix):
    rows = []
    for p in itertools.permutations(BIFOLIA):
        s, leaves, transitions = score_nesting(p, matrix)
        rows.append({
            "nesting_outer_to_inner": list(p),
            "leaf_reading_order": leaves,
            "transitions": [list(x) for x in transitions],
            "score": s,
        })
    rows.sort(key=lambda r: (-r["score"], r["nesting_outer_to_inner"]))
    for i, r in enumerate(rows, 1):
        r["rank"] = i
        r["percentile_higher_is_better"] = 1.0 - (i-1)/(len(rows)-1)
    return rows


def analyse_corpus(label, raw):
    pages, audit = parse_pages(raw)
    wanted = [f"f{f}{side}" for f in FOLIOS for side in ("r", "v")]
    missing = [x for x in wanted if not pages.get(x)]
    if missing:
        raise RuntimeError(f"{label}: missing pages {missing}")

    by_window = []
    ranks = defaultdict(list)
    top_counts = Counter()
    for w in WINDOWS:
        matrix, comps = directed_transition_matrix(pages, w)
        rows = enumerate_nestings(matrix)
        current = next(r for r in rows if tuple(r["nesting_outer_to_inner"]) == CURRENT)
        best = rows[0]
        for r in rows:
            ranks[tuple(r["nesting_outer_to_inner"])].append(r["rank"])
        top_counts[tuple(best["nesting_outer_to_inner"])] += 1
        by_window.append({
            "boundary_tokens": "whole_page" if w == 0 else w,
            "best": best,
            "current": current,
            "exact_p_current_ge": current["rank"]/24.0,
            "top5": rows[:5],
        })

    stability = []
    for nesting, rs in ranks.items():
        stability.append({
            "nesting_outer_to_inner": list(nesting),
            "top1_windows": top_counts[nesting],
            "median_rank_across_5_windows": median(rs),
            "worst_rank_across_5_windows": max(rs),
            "ranks_by_window": rs,
        })
    stability.sort(key=lambda r: (-r["top1_windows"], r["median_rank_across_5_windows"], r["worst_rank_across_5_windows"], r["nesting_outer_to_inner"]))
    return {"parser_audit": audit, "by_window": by_window, "stability": stability}


def cross_transcription(zl, it):
    z = {tuple(r["nesting_outer_to_inner"]): r for r in zl["stability"]}
    t = {tuple(r["nesting_outer_to_inner"]): r for r in it["stability"]}
    rows = []
    for nesting in z:
        ranks = z[nesting]["ranks_by_window"] + t[nesting]["ranks_by_window"]
        rows.append({
            "nesting_outer_to_inner": list(nesting),
            "zl_top1_windows": z[nesting]["top1_windows"],
            "it2a_top1_windows": t[nesting]["top1_windows"],
            "top1_windows_out_of_10": z[nesting]["top1_windows"] + t[nesting]["top1_windows"],
            "median_rank_across_10_tests": median(ranks),
            "worst_rank_across_10_tests": max(ranks),
            "ranks_zl": z[nesting]["ranks_by_window"],
            "ranks_it2a": t[nesting]["ranks_by_window"],
        })
    rows.sort(key=lambda r: (-r["top1_windows_out_of_10"], r["median_rank_across_10_tests"], r["worst_rank_across_10_tests"], r["nesting_outer_to_inner"]))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--zl", type=Path, required=True)
    ap.add_argument("--it", type=Path, required=True)
    ap.add_argument("--json", type=Path)
    args = ap.parse_args()

    zl_raw = args.zl.read_text(encoding="utf-8", errors="replace")
    it_bytes = args.it.read_bytes()
    it_sha = hashlib.sha256(it_bytes).hexdigest()
    if it_sha != IT2A_SHA256:
        raise SystemExit(f"IT2a SHA256 mismatch: {it_sha}")
    it_raw = it_bytes.decode("utf-8", errors="replace")

    zl = analyse_corpus("ZL3b", zl_raw)
    it = analyse_corpus("IT2a", it_raw)
    cross = cross_transcription(zl, it)
    current_cross = next(r for r in cross if tuple(r["nesting_outer_to_inner"]) == CURRENT)

    result = {
        "status": "QUIRE_C_NESTING_RECONSTRUCTION_NOT_DECIPHERMENT",
        "quire": "C",
        "folios": list(FOLIOS),
        "known_physical_bifolia": {k: list(v) for k, v in BIFOLIA.items()},
        "current_nesting_outer_to_inner": list(CURRENT),
        "current_leaf_reading_order": leaf_sequence(CURRENT),
        "n_exact_nestings": 24,
        "model": "fixed bifolium orientation; permute outer-to-inner nesting; score verso(previous leaf)->recto(next leaf)",
        "windows": [25, 50, 100, 200, "whole_page"],
        "components": ["token TF-IDF", "character 3-5gram TF-IDF", "token Jaccard"],
        "ZL3b": zl,
        "IT2a": it,
        "cross_transcription_stability": cross,
        "current_cross_transcription": current_cross,
        "guardrails": [
            "Quire C was selected for ordering only after it uniquely survived bifolio-pairing replication and distance+metadata controls; this creates selection conditioning and must be stated.",
            "The model tests nesting compatibility, not whether Quire C historically existed as loose singulions.",
            "Bifolium internal orientation is held fixed; flip sensitivity is a separate experiment.",
            "Folio numbers are never used in the transition score.",
            "IT2a is an independent transcription of the same manuscript, not an independent manuscript sample.",
            "A high continuity rank can reflect topic, scribe or local formulae rather than narrative semantics.",
        ],
    }
    text = json.dumps(result, ensure_ascii=False, indent=2)
    print(text)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
