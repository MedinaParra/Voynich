#!/usr/bin/env python3
"""Q13 singulion-order experiment.

Tests a fixed Layfield–Davis Q13 bifolium order against the current bound page
order and the exact null of all 5! bifolium permutations.  No semantic claims.
The corpus hash, parser policy, representations and primary statistic are fixed
in this file before examining the output.
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

SOURCE_BLOB = "2a4533ab9bdfa85db9bad602d590978953055df1"
Q13_FOLIOS = tuple(range(75, 85))
BIFOLIA = ((75, 84), (76, 83), (77, 82), (78, 81), (79, 80))
LAYFIELD_DAVIS = ((77, 82), (78, 81), (75, 84), (76, 83), (79, 80))
PRIMARY = "tfidf_cosine_all"
EDGE_TOKENS = 50


def git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def physical_leaf(page: str) -> str:
    m = re.match(r"^(f[0-9]+)", page)
    return m.group(1) if m else ""


def parse_pages(raw: str):
    """Conservative parser reused from the project's local-copy audit policy.

    Keep only literal lowercase EVA chunks from paragraph loci. Drawing breaks,
    uncertain chunks and annotations split runs rather than being guessed.
    """
    pages = defaultdict(list)
    meta_by_page = {}
    audit = Counter()
    meta = {}
    current_page = None

    for line in raw.splitlines():
        pm = re.match(r"^<([^>.,]+)>\s*<!", line)
        if pm:
            current_page = pm.group(1)
            meta = dict(re.findall(r"\$([A-Z])=([^\s>]+)", line))
            meta_by_page[current_page] = dict(meta)
            continue

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
        run = []
        for token in re.split(r"([.|])", text):
            if not token or token == ".":
                continue
            if token != "|" and re.fullmatch(r"[a-z]{1,64}", token):
                run.append(token)
            else:
                if token == "|":
                    audit["drawing_breaks"] += 1
                else:
                    audit["uncertain_chunks"] += 1
        pages[page].extend(run)
        audit["paragraph_loci"] += 1

    return dict(pages), meta_by_page, dict(audit)


def q13_page_ids():
    return [f"f{n}{side}" for n in Q13_FOLIOS for side in ("r", "v")]


def current_sequence():
    return q13_page_ids()


def singulion_sequence(order):
    seq = []
    for a, b in order:
        seq.extend((f"f{a}r", f"f{a}v", f"f{b}r", f"f{b}v"))
    return seq


def build_idf(pages, ids):
    n = len(ids)
    df = Counter()
    for pid in ids:
        df.update(set(pages[pid]))
    return {w: math.log((1 + n) / (1 + d)) + 1.0 for w, d in df.items()}


def tfidf(tokens, idf):
    c = Counter(tokens)
    if not c:
        return {}
    total = sum(c.values())
    return {w: (v / total) * idf.get(w, 0.0) for w, v in c.items() if w in idf}


def char_ngrams(tokens, n=3):
    c = Counter()
    for w in tokens:
        s = f"^{w}$"
        for i in range(max(0, len(s) - n + 1)):
            c[s[i:i+n]] += 1
    return c


def cosine(a, b):
    if not a or not b:
        return 0.0
    dot = sum(v * b.get(k, 0.0) for k, v in a.items())
    na = math.sqrt(sum(v * v for v in a.values()))
    nb = math.sqrt(sum(v * v for v in b.values()))
    return dot / (na * nb) if na and nb else 0.0


def jaccard(a, b):
    sa, sb = set(a), set(b)
    u = len(sa | sb)
    return len(sa & sb) / u if u else 0.0


def js_similarity(a_tokens, b_tokens):
    a = Counter("".join(a_tokens)); b = Counter("".join(b_tokens))
    na, nb = sum(a.values()), sum(b.values())
    if not na or not nb:
        return 0.0
    keys = set(a) | set(b)
    pa = {k: a[k] / na for k in keys}; pb = {k: b[k] / nb for k in keys}
    m = {k: 0.5 * (pa[k] + pb[k]) for k in keys}
    def kl(p):
        return sum(v * math.log2(v / m[k]) for k, v in p.items() if v > 0 and m[k] > 0)
    js = 0.5 * kl(pa) + 0.5 * kl(pb)
    return max(0.0, 1.0 - js)  # JSD is bounded by 1 bit for two distributions.


def page_vectors(pages, ids):
    idf = build_idf(pages, ids)
    tf = {pid: tfidf(pages[pid], idf) for pid in ids}
    cg = {pid: char_ngrams(pages[pid], 3) for pid in ids}
    return idf, tf, cg


def mean(xs):
    return sum(xs) / len(xs) if xs else float("nan")


def sequence_scores(seq, pages, idf, tf, cg, boundary_only=False):
    pairs = list(zip(seq, seq[1:]))
    if boundary_only:
        # In a singulion concatenation every fourth transition crosses units.
        pairs = [pairs[i] for i in range(3, len(pairs), 4)]
    vals = defaultdict(list)
    for a, b in pairs:
        vals["tfidf_cosine"].append(cosine(tf[a], tf[b]))
        vals["char3_cosine"].append(cosine(cg[a], cg[b]))
        vals["token_jaccard"].append(jaccard(pages[a], pages[b]))
        vals["char_js_similarity"].append(js_similarity(pages[a], pages[b]))
        tail = pages[a][-EDGE_TOKENS:]
        head = pages[b][:EDGE_TOKENS]
        vals["edge_tfidf_cosine"].append(cosine(tfidf(tail, idf), tfidf(head, idf)))
    return {k: mean(v) for k, v in vals.items()}


def full_scores(seq, pages, idf, tf, cg, is_singulion=False):
    all_s = sequence_scores(seq, pages, idf, tf, cg, False)
    out = {f"{k}_all": v for k, v in all_s.items()}
    if is_singulion:
        bd = sequence_scores(seq, pages, idf, tf, cg, True)
        out.update({f"{k}_boundary": v for k, v in bd.items()})
    return out


def rank_info(value, null_values, higher_is_better=True):
    n = len(null_values)
    if higher_is_better:
        better = sum(x > value for x in null_values)
        ge = sum(x >= value for x in null_values)
        percentile = 100.0 * sum(x <= value for x in null_values) / n
    else:
        better = sum(x < value for x in null_values)
        ge = sum(x <= value for x in null_values)
        percentile = 100.0 * sum(x >= value for x in null_values) / n
    return {
        "rank_best_is_1": better + 1,
        "n_exact_permutations": n,
        "percentile": percentile,
        "exact_upper_tail_p_including_observed": ge / n,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    data = args.corpus.read_bytes()
    blob = git_blob_sha1(data)
    if blob != SOURCE_BLOB:
        raise SystemExit(f"Corpus blob mismatch: {blob} != {SOURCE_BLOB}")
    pages, meta, audit = parse_pages(data.decode("utf-8"))
    ids = q13_page_ids()
    missing = [p for p in ids if not pages.get(p)]
    if missing:
        raise SystemExit(f"Missing/empty Q13 pages: {missing}")

    idf, tf, cg = page_vectors(pages, ids)
    current = current_sequence()
    proposed = singulion_sequence(LAYFIELD_DAVIS)
    current_scores = full_scores(current, pages, idf, tf, cg, False)
    proposed_scores = full_scores(proposed, pages, idf, tf, cg, True)

    records = []
    for perm in itertools.permutations(BIFOLIA):
        seq = singulion_sequence(perm)
        scores = full_scores(seq, pages, idf, tf, cg, True)
        records.append({
            "order": [f"{a}|{b}" for a, b in perm],
            "scores": scores,
        })

    primary_null = [r["scores"][PRIMARY] for r in records]
    primary_value = proposed_scores[PRIMARY]
    primary_rank = rank_info(primary_value, primary_null, True)

    # The current bound order is not one of the bifolium-permutation nulls.
    delta_vs_current = primary_value - current_scores[PRIMARY]
    top = sorted(records, key=lambda r: r["scores"][PRIMARY], reverse=True)[:10]

    # Stable adjacency support among the top 10% exact permutations.
    topk_n = max(1, math.ceil(0.10 * len(records)))
    topk = sorted(records, key=lambda r: r["scores"][PRIMARY], reverse=True)[:topk_n]
    edge_counts = Counter()
    for r in topk:
        o = r["order"]
        for a, b in zip(o, o[1:]):
            edge_counts[(a, b)] += 1
    proposed_edges = []
    po = [f"{a}|{b}" for a, b in LAYFIELD_DAVIS]
    for a, b in zip(po, po[1:]):
        proposed_edges.append({"edge": f"{a} -> {b}", "top10pct_support": edge_counts[(a,b)] / topk_n})

    pass_order = (
        delta_vs_current > 0
        and primary_rank["percentile"] > 95.0
    )

    result = {
        "classification": "Q13_SINGULION_ORDER_CONTINUITY_NOT_DECIPHERMENT",
        "status": "PASS_ORDER" if pass_order else "FAIL_ORDER",
        "source_blob": blob,
        "source_policy": "literal lowercase EVA paragraph chunks; uncertain chunks split, never guessed",
        "q13_pages": ids,
        "tokens_by_page": {p: len(pages[p]) for p in ids},
        "metadata_by_page": {p: meta.get(p, {}) for p in ids},
        "parser_audit": audit,
        "current_bound_sequence": current,
        "layfield_davis_order": [f"{a}|{b}" for a, b in LAYFIELD_DAVIS],
        "layfield_davis_sequence": proposed,
        "primary_metric": PRIMARY,
        "higher_is_better": True,
        "current_scores": current_scores,
        "layfield_davis_scores": proposed_scores,
        "primary_delta_layfield_minus_current": delta_vs_current,
        "primary_exact_null": {
            "min": min(primary_null),
            "mean": mean(primary_null),
            "max": max(primary_null),
            **primary_rank,
        },
        "top_10_orders": top,
        "proposed_edge_support_top10pct": proposed_edges,
        "decision_rule": "PASS_ORDER iff proposed primary score > current bound score and proposed order is above the 95th percentile of all 120 fixed-orientation bifolium permutations.",
        "limitations": [
            "Q13 only; Q20 is not included until its exact published sequence is independently extracted.",
            "The primary metric is lexical continuity, not semantic decoding.",
            "The 120-order null preserves each bifolium's fixed internal page orientation; orientation-flip sensitivity is a separate test.",
            "Layfield-Davis Q13 order is currently sourced from an independent reproduction quoting the article and remains pending primary-table verification.",
        ],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
