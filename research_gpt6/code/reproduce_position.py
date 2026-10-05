#!/usr/bin/env python3
"""Reproduce positional MI and test it under within-word permutations."""
from __future__ import annotations

import argparse
import os

from collections import Counter, defaultdict
from hashlib import sha256
import json
import math
import re
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
CORPUS = Path(os.environ.get("VOYNICH_CORPUS", str(ROOT / "corpus" / "voynich_sta.txt")))
SEED = 20261005
N_PERM = 999


def parse_sta(path: Path) -> list[list[str]]:
    """Faithful port of notebook 03 cell 3 Parser 1 + cell 4 word split."""
    tokens: list[str] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or re.match(r"^<[^>]+>\s*<!", line):
                continue
            match = re.match(r"^<[^>]+>\s+(.*)", line)
            if not match:
                continue
            text = match.group(1).strip()
            text = re.sub(r"\{[^}]*\}", "", text)
            text = re.sub(r"<[^>]*>", "", text)
            text = re.sub(r"-", ".", text)
            for word in text.split("."):
                glyphs = re.findall(r"[A-Z][0-9a-z]", word.strip())
                if glyphs:
                    tokens.extend(glyphs)
                    tokens.append(".")
    words: list[list[str]] = []
    current: list[str] = []
    for token in tokens:
        if token == ".":
            if current:
                words.append(current)
                current = []
        else:
            current.append(token)
    if current:
        words.append(current)
    return words


def positions(length: int, singleton_mode: str = "onset") -> list[int]:
    if length == 1:
        return [0] if singleton_mode == "onset" else [3]
    return [0 if i == 0 else 2 if i == length - 1 else 1 for i in range(length)]


def mutual_information(words: list[list[int]], singleton_mode: str = "onset") -> float:
    joint: Counter[tuple[int, int]] = Counter()
    glyph_counts: Counter[int] = Counter()
    pos_counts: Counter[int] = Counter()
    total = 0
    for word in words:
        ps = positions(len(word), singleton_mode)
        for glyph, pos in zip(word, ps):
            joint[glyph, pos] += 1
            glyph_counts[glyph] += 1
            pos_counts[pos] += 1
            total += 1
    return sum((count / total) * math.log2(
        (count / total) / ((glyph_counts[glyph] / total) * (pos_counts[pos] / total)))
        for (glyph, pos), count in joint.items())


def main() -> None:
    global CORPUS
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--corpus", type=Path,
        default=CORPUS,
        help="Path to corpus/voynich_sta.txt from the source repository; can also be set with VOYNICH_CORPUS.",
    )
    args = parser.parse_args()
    CORPUS = args.corpus.expanduser().resolve()
    if not CORPUS.is_file():
        parser.error(f"STA1 corpus not found: {CORPUS}. Pass --corpus or set VOYNICH_CORPUS.")
    words_glyphs = parse_sta(CORPUS)
    vocab = {glyph: i for i, glyph in enumerate(sorted({g for w in words_glyphs for g in w}))}
    words = [[vocab[g] for g in w] for w in words_glyphs]
    observed = mutual_information(words)
    no_single = mutual_information([w for w in words if len(w) > 1])
    singleton_separate = mutual_information(words, "separate")

    grouped: dict[int, list[list[int]]] = defaultdict(list)
    for word in words:
        grouped[len(word)].append(word)
    matrices = {length: np.asarray(group, dtype=np.int32)
                for length, group in grouped.items() if length > 0}
    rng = np.random.default_rng(SEED)
    null = []
    V = len(vocab)
    for _ in range(N_PERM):
        joint = np.zeros((V, 3), dtype=np.int64)
        for length, matrix in matrices.items():
            if length == 1:
                joint[:, 0] += np.bincount(matrix[:, 0], minlength=V)
                continue
            # Independently permute each word while preserving its glyph multiset.
            order = np.argsort(rng.random(matrix.shape), axis=1)
            permuted = np.take_along_axis(matrix, order, axis=1)
            for col in range(length):
                pos = 0 if col == 0 else 2 if col == length - 1 else 1
                joint[:, pos] += np.bincount(permuted[:, col], minlength=V)
        row = joint.sum(axis=1)
        col = joint.sum(axis=0)
        total = joint.sum()
        mi = 0.0
        nz = np.argwhere(joint > 0)
        for g, p in nz:
            c = joint[g, p]
            mi += (c / total) * math.log2((c * total) / (row[g] * col[p]))
        null.append(mi)
    null_arr = np.asarray(null)
    p_value = (1 + int(np.sum(null_arr >= observed))) / (N_PERM + 1)
    result = {
        "source": str(CORPUS),
        "sha256": sha256(CORPUS.read_bytes()).hexdigest(),
        "parser": "03_entropy_spectral.ipynb cells 3-4 (faithful port)",
        "position_definition": "first=onset, last=final, internal=middle; singleton is onset, as notebook 02 cell 21",
        "corpus": {"words": len(words), "glyphs": sum(map(len, words)),
                   "vocabulary": len(vocab), "singleton_words": sum(len(w) == 1 for w in words)},
        "observed_MI_bits": observed,
        "sensitivity_MI_bits": {"exclude_singleton_words": no_single,
                                 "singleton_as_own_class": singleton_separate},
        "within_word_permutation": {"seed": SEED, "n_permutations": N_PERM,
                                    "null_mean": float(null_arr.mean()),
                                    "null_sd": float(null_arr.std(ddof=0)),
                                    "null_99pct": float(np.quantile(null_arr, .99)),
                                    "empirical_one_sided_p": p_value},
        "interpretation_limit": "Tests whether glyph-position association exceeds random reorderings within the observed words; it does not establish linguistic or semantic function.",
    }
    out = ROOT / "research_gpt6" / "results" / "position_reproduction.json"
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
