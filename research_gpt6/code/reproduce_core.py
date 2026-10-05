#!/usr/bin/env python3
"""Reproduce the STA1 parser and the entropy calculations in notebook 03.

The `notebook` calculation mirrors cell 8's formula while aggregating its
counts efficiently. Two diagnostics are included: renormalizing the notebook's
per-context probability vector, and unsmoothed plug-in conditional entropy.
Neither diagnostic is presented as a canonical replacement estimator.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from hashlib import sha256
import json
import math
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CORPUS_PATH = ROOT / "corpus" / "voynich_sta.txt"


def parse_sta(path: Path) -> list[str]:
    """Faithful port of 03_entropy_spectral.ipynb cell 3 Parser 1."""
    tokens: list[str] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if re.match(r"^<[^>]+>\s*<!", line):
                continue
            match = re.match(r"^<[^>]+>\s+(.*)", line)
            if not match:
                continue
            text = match.group(1).strip()
            text = re.sub(r"\{[^}]*\}", "", text)
            text = re.sub(r"<[^>]*>", "", text)
            text = re.sub(r"-", ".", text).strip()
            for raw_word in text.split("."):
                glyphs = re.findall(r"[A-Z][0-9a-z]", raw_word.strip())
                if glyphs:
                    tokens.extend(glyphs)
                    tokens.append(".")
    return tokens


def context_counts(corpus: list[str], order: int):
    counts: dict[tuple[str, ...], Counter[str]] = defaultdict(Counter)
    for i in range(len(corpus) - order):
        ctx = tuple(corpus[i : i + order])
        counts[ctx][corpus[i + order]] += 1
    return counts


def entropy_notebook(corpus: list[str], order: int) -> tuple[float, float, float]:
    """Return the notebook's entropy plus min/max probability mass by context."""
    vocab = sorted(set(corpus))
    V = len(vocab)
    if order == 0:
        freq = Counter(corpus)
        total = len(corpus)
        H = -sum((c / total) * math.log2(c / total) for c in freq.values())
        return H, 1.0, 1.0

    contexts = context_counts(corpus, order)
    total_ctx = sum(sum(next_counts.values()) for next_counts in contexts.values())
    H = 0.0
    masses = []
    for next_counts in contexts.values():
        ctx_count = sum(next_counts.values())
        T = len(next_counts)
        denom = ctx_count + T
        p_ctx = ctx_count / total_ctx
        probs = []
        H_ctx = 0.0
        for token in vocab:
            c = next_counts.get(token, 0)
            if c:
                p = c / denom
            else:
                p = (T / denom) / V  # exact denominator used by notebook cell 8
            probs.append(p)
            if p:
                H_ctx -= p * math.log2(p)
        masses.append(sum(probs))
        H += p_ctx * H_ctx
    return H, min(masses), max(masses)


def entropy_renormalized(corpus: list[str], order: int) -> float:
    """Diagnostic: normalize the notebook's probabilities context by context."""
    if order == 0:
        return entropy_notebook(corpus, 0)[0]
    contexts = context_counts(corpus, order)
    total_ctx = sum(sum(v.values()) for v in contexts.values())
    V = len(set(corpus))
    H = 0.0
    for next_counts in contexts.values():
        ctx_count = sum(next_counts.values())
        T = len(next_counts)
        denom = ctx_count + T
        probs = [c / denom for c in next_counts.values()]
        escape_per_unseen = (T / denom) / V
        probs.extend([escape_per_unseen] * max(0, V - T))
        mass = sum(probs)
        p_ctx = ctx_count / total_ctx
        H -= p_ctx * sum((p / mass) * math.log2(p / mass) for p in probs if p)
    return H


def entropy_wb_uniform_unseen(corpus: list[str], order: int) -> float:
    """Normalized Witten-Bell escape diagnostic with uniform unseen support.

    This is a transparent correction to the notebook's per-context mass
    allocation, not a claim that uniform backoff is the uniquely right model.
    """
    if order == 0:
        return entropy_notebook(corpus, 0)[0]
    V = len(set(corpus))
    contexts = context_counts(corpus, order)
    total_ctx = sum(sum(v.values()) for v in contexts.values())
    H = 0.0
    for next_counts in contexts.values():
        n = sum(next_counts.values())
        T = len(next_counts)
        p_ctx = n / total_ctx
        if T < V:
            denom = n + T
            seen_probs = [c / denom for c in next_counts.values()]
            unseen_prob = T / (denom * (V - T))
            H_ctx = -sum(p * math.log2(p) for p in seen_probs)
            H_ctx -= (V - T) * unseen_prob * math.log2(unseen_prob)
        else:
            H_ctx = -sum((c / n) * math.log2(c / n) for c in next_counts.values())
        H += p_ctx * H_ctx
    return H


def entropy_plugin(corpus: list[str], order: int) -> float:
    """Unsmoothed empirical conditional entropy; included as a diagnostic."""
    if order == 0:
        return entropy_notebook(corpus, 0)[0]
    contexts = context_counts(corpus, order)
    total = sum(sum(v.values()) for v in contexts.values())
    H = 0.0
    for next_counts in contexts.values():
        n = sum(next_counts.values())
        p_ctx = n / total
        H -= p_ctx * sum((c / n) * math.log2(c / n) for c in next_counts.values())
    return H


def main() -> None:
    raw = parse_sta(CORPUS_PATH)
    words: list[list[str]] = []
    current: list[str] = []
    for token in raw:
        if token == ".":
            if current:
                words.append(current)
                current = []
        else:
            current.append(token)
    if current:
        words.append(current)
    # This intentionally matches notebook cell 4, which removes separators
    # before computing character/glyph n-grams.
    flat = [token for token in raw if token != "."]

    result = {
        "source": str(CORPUS_PATH.relative_to(ROOT)),
        "sha256": sha256(CORPUS_PATH.read_bytes()).hexdigest(),
        "parser": "03_entropy_spectral.ipynb cell 3, Parser 1 (faithful port)",
        "corpus_size": {"tokens_with_dot": len(raw), "glyphs": len(flat),
                        "words": len(words), "vocabulary": len(set(flat))},
        "note": "N-grams intentionally concatenate across word separators, matching notebook cell 4.",
        "orders": {},
    }
    for order in range(5):
        h, min_mass, max_mass = entropy_notebook(flat, order)
        result["orders"][str(order)] = {
            "notebook_formula_bits": h,
            "min_context_probability_mass": min_mass,
            "max_context_probability_mass": max_mass,
            "renormalized_diagnostic_bits": entropy_renormalized(flat, order),
            "normalized_witten_bell_uniform_unseen_bits": entropy_wb_uniform_unseen(flat, order),
            "unsmoothed_plugin_diagnostic_bits": entropy_plugin(flat, order),
        }
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
