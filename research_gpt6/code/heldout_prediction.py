#!/usr/bin/env python3
"""Five-fold folio-held-out glyph prediction on the pinned STA1 transcription.

Models are fixed in advance: unigram, word-position category, and hierarchical
within-word character n-grams of orders 1--4. Folios, never individual words,
are assigned to folds. This is a prediction/structure test, not a decipherment.
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

ALPHA = 1.0
FOLDS = 5
SEED = 20261005
BOOTSTRAPS = 2000
TOKEN_RE = re.compile(r"[A-Z][0-9a-z]")
FOLIO_RE = re.compile(r"^<([fF]\d+[rv](?:\d+)?)")


def parse_folios(path: Path) -> dict[str, list[list[str]]]:
    """Parse visible word tokens by folio, preserving the audit's STA1 tokens."""
    data: dict[str, list[list[str]]] = defaultdict(list)
    folio: str | None = None
    with path.open(encoding="utf-8") as stream:
        for line in stream:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            header = FOLIO_RE.match(line)
            if header and re.search(r"\s*<!", line):
                folio = header.group(1).lower()
                continue
            match = re.match(r"^<[^>]+>\s+(.*)", line)
            if not match or folio is None:
                continue
            body = re.sub(r"\{[^}]*\}", "", match.group(1))
            body = re.sub(r"<[^>]*>", "", body).replace("-", ".")
            for raw_word in body.split("."):
                word = TOKEN_RE.findall(raw_word.strip())
                if word:
                    data[folio].append(word)
    return dict(data)


def slot(word: list[str], i: int) -> str:
    if len(word) == 1:
        return "singleton"
    if i == 0:
        return "initial"
    if i == len(word) - 1:
        return "final"
    return "medial"


def fit(words: list[list[str]], vocab: list[str]):
    uni = Counter(g for w in words for g in w)
    slots: dict[str, Counter[str]] = defaultdict(Counter)
    grams: dict[int, dict[tuple[str, ...], Counter[str]]] = {
        n: defaultdict(Counter) for n in range(1, 5)
    }
    for word in words:
        for i, glyph in enumerate(word):
            slots[slot(word, i)][glyph] += 1
            for n in range(1, min(4, i) + 1):
                grams[n][tuple(word[i - n:i])][glyph] += 1
    return uni, slots, grams


def predict_probs(glyph: str, word: list[str], i: int, model: str,
                  vocab: list[str], uni: Counter[str], slots, grams) -> float:
    V = len(vocab)
    total = sum(uni.values())
    p = (uni[glyph] + ALPHA / V) / (total + ALPHA)
    if model == "unigram":
        return p
    if model == "position":
        counts = slots.get(slot(word, i), Counter())
        denom = sum(counts.values()) + ALPHA
        return (counts[glyph] + ALPHA * p) / denom
    order = int(model.removeprefix("ngram"))
    for n in range(1, min(order, i) + 1):
        ctx = tuple(word[i - n:i])
        counts = grams[n].get(ctx, Counter())
        denom = sum(counts.values()) + ALPHA
        p = (counts[glyph] + ALPHA * p) / denom
    return p


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", type=Path, required=True)
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()
    data = parse_folios(args.corpus)
    folios = sorted(data)
    if len(folios) < FOLDS:
        raise SystemExit(f"Need at least {FOLDS} folios; parsed {len(folios)}")
    vocab = sorted({g for words in data.values() for w in words for g in w})
    rng = random.Random(SEED)
    shuffled = folios[:]
    rng.shuffle(shuffled)
    fold_of = {folio: i % FOLDS for i, folio in enumerate(shuffled)}
    models = ["unigram", "position", "ngram1", "ngram2", "ngram3", "ngram4"]
    per_folio_loss = {m: {} for m in models}
    per_folio_count: dict[str, int] = {}
    glyph_count = 0
    fold_info = []
    for fold in range(FOLDS):
        test_ids = [f for f in folios if fold_of[f] == fold]
        train_ids = [f for f in folios if fold_of[f] != fold]
        train_words = [w for f in train_ids for w in data[f]]
        uni, slots, grams = fit(train_words, vocab)
        fold_counts = Counter()
        for folio in test_ids:
            losses = Counter()
            count = 0
            for word in data[folio]:
                for i, glyph in enumerate(word):
                    count += 1
                    for model in models:
                        prob = predict_probs(glyph, word, i, model, vocab, uni, slots, grams)
                        losses[model] -= math.log2(prob)
            glyph_count += count
            fold_counts[fold] = count
            per_folio_count[folio] = count
            for model in models:
                per_folio_loss[model][folio] = losses[model]
        fold_info.append({"fold": fold, "train_folios": len(train_ids),
                          "test_folios": len(test_ids),
                          "test_glyphs": sum(sum(len(w) for w in data[f]) for f in test_ids)})

    # Cluster bootstrap: resample complete folios, preserving the unit of split.
    bootstrap_rng = random.Random(SEED + 1)
    folio_deltas = {
        m: {f: per_folio_loss["unigram"][f] - per_folio_loss[m][f] for f in folios}
        for m in models if m != "unigram"
    }
    summaries = {}
    for model in models:
        total_glyphs = sum(per_folio_count.values())
        summary = {"cross_entropy_bits_per_glyph": sum(per_folio_loss[model].values()) / total_glyphs}
        if model != "unigram":
            total_gain = sum(folio_deltas[model].values()) / total_glyphs
            boots = []
            for _ in range(BOOTSTRAPS):
                sample_ids = [folios[bootstrap_rng.randrange(len(folios))] for _ in folios]
                sample_count = sum(per_folio_count[f] for f in sample_ids)
                boots.append(sum(folio_deltas[model][f] for f in sample_ids) / sample_count)
            boots.sort()
            summary.update({
                "gain_vs_unigram_bits_per_glyph": total_gain,
                "folio_bootstrap_95pct_ci_gain": [boots[int(.025 * BOOTSTRAPS)], boots[int(.975 * BOOTSTRAPS)]],
            })
        summaries[model] = summary

    result = {
        "status": "PASS_DESCRIPTIVE_PREDICTION_TEST",
        "interpretation_limit": "Predictive generalization of glyph regularities only; does not identify meaning, language, or decipherment.",
        "corpus": str(args.corpus),
        "corpus_sha256": hashlib.sha256(args.corpus.read_bytes()).hexdigest(),
        "folios": len(folios), "glyphs": glyph_count, "vocabulary_size": len(vocab),
        "split": {"method": "5-fold whole-folio cross-validation", "seed": SEED,
                  "per_fold": fold_info},
        "smoothing": {"method": "hierarchical Dirichlet interpolation", "alpha": ALPHA,
                      "position_prior": "training unigram", "orders": [1, 2, 3, 4]},
        "uncertainty": {"method": "bootstrap over out-of-fold folio-level losses",
                        "iterations": BOOTSTRAPS, "seed": SEED + 1},
        "models": summaries,
    }
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
