#!/usr/bin/env python3
"""Test glyph-sequence prediction on entirely withheld STA1 quires.

Each quire is held out once, so no folio from its gathering contributes to
training. Models and smoothing match heldout_prediction.py. Predictive evidence
is about transcription regularity only, not recovered meaning or decipherment.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
import random
import re
from pathlib import Path

from heldout_prediction import ALPHA, TOKEN_RE, fit, predict_probs

FOLIO_RE = re.compile(r"^<(fRos|f\d+[rv](?:\d+)?)>")
QUIRE_RE = re.compile(r"\$Q=([^\s>]+)")
MODELS = ["unigram", "position", "ngram1", "ngram2", "ngram3", "ngram4"]
BOOTSTRAPS = 5000
SEED = 20261007


def parse(path: Path):
    words: dict[str, list[list[str]]] = defaultdict(list)
    quire_of: dict[str, str] = {}
    folio: str | None = None
    with path.open(encoding="utf-8") as stream:
        for line in stream:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            head = FOLIO_RE.match(line)
            if head and "<!" in line:
                folio = head.group(1).lower()
                q = QUIRE_RE.search(line)
                if not q:
                    raise ValueError(f"Missing $Q quire metadata on {folio}")
                quire_of[folio] = q.group(1)
                continue
            match = re.match(r"^<[^>]+>\s+(.*)", line)
            if not match or folio is None:
                continue
            body = re.sub(r"\{[^}]*\}", "", match.group(1))
            body = re.sub(r"<[^>]*>", "", body).replace("-", ".")
            for raw in body.split("."):
                glyphs = TOKEN_RE.findall(raw.strip())
                if glyphs:
                    words[folio].append(glyphs)
    if set(words) != set(quire_of):
        raise ValueError("Folio text and quire metadata do not match")
    return dict(words), quire_of


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", type=Path, required=True)
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()
    data, quire_of = parse(args.corpus)
    quires = sorted(set(quire_of.values()))
    folios = sorted(data)
    vocab = sorted({g for ws in data.values() for w in ws for g in w})
    loss = {m: {} for m in MODELS}
    counts: dict[str, int] = {}
    unseen: dict[str, int] = {}
    groups = []
    for q in quires:
        test_ids = [f for f in folios if quire_of[f] == q]
        train_ids = [f for f in folios if quire_of[f] != q]
        train_words = [w for f in train_ids for w in data[f]]
        uni, slots, grams = fit(train_words, vocab)
        train_inventory = set(uni)
        group_glyphs = 0
        group_unseen = 0
        for f in test_ids:
            f_loss = Counter()
            f_count = 0
            f_unseen = 0
            for word in data[f]:
                for i, glyph in enumerate(word):
                    f_count += 1
                    if glyph not in train_inventory:
                        f_unseen += 1
                    for model in MODELS:
                        prob = predict_probs(glyph, word, i, model, vocab, uni, slots, grams)
                        f_loss[model] -= math.log2(prob)
            counts[f] = f_count
            unseen[f] = f_unseen
            group_glyphs += f_count
            group_unseen += f_unseen
            for model in MODELS:
                loss[model][f] = f_loss[model]
        groups.append({"quire": q, "folios": len(test_ids), "glyphs": group_glyphs,
                       "glyphs_unseen_in_training": group_unseen})
    total = sum(counts.values())
    summaries = {}
    rng = random.Random(SEED)
    for model in MODELS:
        summaries[model] = {"cross_entropy_bits_per_glyph": sum(loss[model].values()) / total}
        if model == "unigram":
            continue
        deltas = {f: loss["unigram"][f] - loss[model][f] for f in folios}
        observed = sum(deltas.values()) / total
        # Resample complete quires, not folios, to respect the split unit.
        group_delta = {
            q: sum(deltas[f] for f in folios if quire_of[f] == q)
            for q in quires
        }
        group_count = {q: sum(counts[f] for f in folios if quire_of[f] == q) for q in quires}
        boot = []
        for _ in range(BOOTSTRAPS):
            sample_q = [quires[rng.randrange(len(quires))] for _ in quires]
            den = sum(group_count[q] for q in sample_q)
            boot.append(sum(group_delta[q] for q in sample_q) / den)
        boot.sort()
        summaries[model].update({
            "gain_vs_unigram_bits_per_glyph": observed,
            "quire_bootstrap_95pct_ci_gain": [boot[int(.025 * BOOTSTRAPS)], boot[int(.975 * BOOTSTRAPS)]],
        })
    result = {
        "status": "PASS_DESCRIPTIVE_PREDICTION_TEST",
        "interpretation_limit": "Tests generalization across annotated quires in one transcription. Does not decode meanings, establish language, or test independent transcription accuracy.",
        "corpus_sha256": hashlib.sha256(args.corpus.read_bytes()).hexdigest(),
        "folios": len(folios), "quires": len(quires), "glyphs": total,
        "vocabulary_size": len(vocab),
        "split": "leave-one-quire-out; each whole $Q group held out once",
        "smoothing": {"method": "hierarchical Dirichlet interpolation", "alpha": ALPHA,
                      "position_prior": "training unigram", "orders": [1, 2, 3, 4]},
        "uncertainty": {"method": "bootstrap complete out-of-fold quire losses",
                        "iterations": BOOTSTRAPS, "seed": SEED},
        "unseen_glyph_rate": sum(unseen.values()) / total,
        "heldout_groups": groups,
        "models": summaries,
    }
    output = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(output, encoding="utf-8")
    print(output, end="")


if __name__ == "__main__":
    main()
