#!/usr/bin/env python3
"""Independent visual-semantic validation of Q13/Q20 ordering hypotheses.

This script deliberately does NOT read Voynich transcription or textual scores.
It consumes the public Xenoglyph per-page visual semantic profiles generated from
Yale/Beinecke page images, aggregates the four page faces of each candidate
singulion, and asks whether visual similarity independently recovers the textual
adjacencies preregistered in research_gpt6/29_resultados_orden_q13_q20.md.

Primary safeguards:
- Three lenses are evaluated separately and as an equal-weight z-score consensus.
- No weight is fitted to Q13 or Q20.
- Text-derived target edges/orders are constants declared before loading profiles.
- Exact label-permutation tests use all 5! / 6! relabellings.
- Dimension bootstrap is a sensitivity diagnostic, not a historical posterior.
"""
from __future__ import annotations

import argparse
import csv
import itertools
import json
import math
import random
from collections import Counter
from pathlib import Path
from statistics import mean, pstdev

LENS_FILES = {
    "voynich": "voynich_profiles.json",
    "archaeology": "voynich_archaeology_profiles.json",
    "cryptological": "voynich_cryptological_profiles.json",
}

Q13 = {
    "75|84": (75, 84),
    "76|83": (76, 83),
    "77|82": (77, 82),
    "78|81": (78, 81),
    "79|80": (79, 80),
}
Q20 = {
    "103|116": (103, 116),
    "104|115": (104, 115),
    "105|114": (105, 114),
    "106|113": (106, 113),
    "107|112": (107, 112),
    "108|111": (108, 111),
}

# Frozen before loading visual profiles: these came from the independent textual
# pipeline documented in 29_resultados_orden_q13_q20.md.
TARGET_EDGES = {
    "Q13": [
        ("75|84", "78|81"),
        ("76|83", "77|82"),
    ],
    "Q20": [
        ("103|116", "108|111"),
        ("105|114", "107|112"),
        ("106|113", "107|112"),
    ],
}
TEXT_CANDIDATE = {
    "Q13": ["79|80", "78|81", "75|84", "76|83", "77|82"],
    "Q20": ["103|116", "108|111", "104|115", "106|113", "107|112", "105|114"],
}
CURRENT_ORDER = {
    "Q13": ["75|84", "76|83", "77|82", "78|81", "79|80"],
    "Q20": ["103|116", "104|115", "105|114", "106|113", "107|112", "108|111"],
}


def canonical_edge(a: str, b: str) -> tuple[str, str]:
    return tuple(sorted((a, b)))


def cosine(a: list[float], b: list[float], dims: list[int] | None = None) -> float:
    if dims is None:
        dims = list(range(len(a)))
    aa = sum(a[i] * a[i] for i in dims)
    bb = sum(b[i] * b[i] for i in dims)
    if aa <= 0.0 or bb <= 0.0:
        return 0.0
    return sum(a[i] * b[i] for i in dims) / math.sqrt(aa * bb)


def zscore_edge_matrix(matrix: dict[tuple[str, str], float]) -> dict[tuple[str, str], float]:
    vals = list(matrix.values())
    mu = mean(vals)
    sd = pstdev(vals)
    if sd == 0:
        return {k: 0.0 for k in matrix}
    return {k: (v - mu) / sd for k, v in matrix.items()}


def add_matrices(mats: list[dict[tuple[str, str], float]]) -> dict[tuple[str, str], float]:
    keys = set(mats[0])
    assert all(set(m) == keys for m in mats)
    return {k: sum(m[k] for m in mats) / len(mats) for k in keys}


def load_metadata(path: Path) -> dict[str, dict]:
    out = {}
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            out[row["image_id"]] = row
    return out


def load_lens(path: Path, metadata: dict[str, dict]) -> tuple[list[str], dict[tuple[int, str], list[float]]]:
    profiles = json.loads(path.read_text(encoding="utf-8"))
    first_scores = next(p.get("archetype_scores", {}) for p in profiles if p.get("archetype_scores"))
    dims = sorted(first_scores)
    pages: dict[tuple[int, str], list[float]] = {}
    for p in profiles:
        iid = p.get("image_id")
        m = metadata.get(iid)
        scores = p.get("archetype_scores", {})
        if not m or not scores:
            continue
        try:
            folio_num = int(float(m["folio_num"]))
        except (ValueError, TypeError, KeyError):
            continue
        side = str(m.get("side", "")).strip()
        if side not in ("r", "v"):
            continue
        pages[(folio_num, side)] = [float(scores.get(d, 0.0)) for d in dims]
    return dims, pages


def mean_vec(rows: list[list[float]]) -> list[float]:
    if not rows:
        raise ValueError("empty vector set")
    return [sum(x[j] for x in rows) / len(rows) for j in range(len(rows[0]))]


def aggregate_singulions(units: dict[str, tuple[int, int]], pages: dict[tuple[int, str], list[float]]) -> tuple[dict[str, list[float]], dict[str, list[str]]]:
    out = {}
    provenance = {}
    for label, (a, b) in units.items():
        keys = [(a, "r"), (a, "v"), (b, "r"), (b, "v")]
        present = [k for k in keys if k in pages]
        if len(present) < 4:
            raise RuntimeError(f"{label}: expected 4 page faces, found {present}")
        out[label] = mean_vec([pages[k] for k in present])
        provenance[label] = [f"{n}{s}" for n, s in present]
    return out, provenance


def build_matrix(vectors: dict[str, list[float]], sampled_dims: list[int] | None = None) -> dict[tuple[str, str], float]:
    labels = list(vectors)
    return {
        canonical_edge(a, b): cosine(vectors[a], vectors[b], sampled_dims)
        for i, a in enumerate(labels) for b in labels[i + 1:]
    }


def path_score(order: list[str] | tuple[str, ...], matrix: dict[tuple[str, str], float]) -> float:
    return sum(matrix[canonical_edge(a, b)] for a, b in zip(order, order[1:]))


def all_undirected_paths(labels: list[str], matrix: dict[tuple[str, str], float]) -> list[tuple[float, tuple[str, ...]]]:
    rows = []
    for p in itertools.permutations(labels):
        if p > p[::-1]:
            continue
        rows.append((path_score(p, matrix), p))
    rows.sort(key=lambda x: (-x[0], x[1]))
    return rows


def rank_path(order: list[str], paths: list[tuple[float, tuple[str, ...]]]) -> dict:
    canon = min(tuple(order), tuple(reversed(order)))
    for rank, (score, p) in enumerate(paths, 1):
        if min(p, p[::-1]) == canon:
            n = len(paths)
            return {
                "order": list(order),
                "score": score,
                "rank": rank,
                "n_topologies": n,
                "percentile_higher_is_better": 1.0 - (rank - 1) / max(1, n - 1),
            }
    raise KeyError(order)


def edge_ranks(matrix: dict[tuple[str, str], float], targets: list[tuple[str, str]]) -> list[dict]:
    ranked = sorted(matrix.items(), key=lambda kv: (-kv[1], kv[0]))
    rank_of = {e: i + 1 for i, (e, _) in enumerate(ranked)}
    return [{
        "edge": list(canonical_edge(*e)),
        "rank": rank_of[canonical_edge(*e)],
        "n_edges": len(ranked),
        "score": matrix[canonical_edge(*e)],
    } for e in targets]


def target_stat(matrix: dict[tuple[str, str], float], targets: list[tuple[str, str]]) -> float:
    return sum(matrix[canonical_edge(a, b)] for a, b in targets) / len(targets)


def exact_label_permutation_test(labels: list[str], matrix: dict[tuple[str, str], float], targets: list[tuple[str, str]]) -> dict:
    observed = target_stat(matrix, targets)
    vals = []
    for perm in itertools.permutations(labels):
        mapping = dict(zip(labels, perm))
        s = sum(matrix[canonical_edge(mapping[a], mapping[b])] for a, b in targets) / len(targets)
        vals.append(s)
    ge = sum(v >= observed - 1e-15 for v in vals)
    return {
        "observed_mean_target_similarity": observed,
        "n_exact_label_permutations": len(vals),
        "n_ge_observed": ge,
        "exact_p_ge": ge / len(vals),
        "null_mean": mean(vals),
        "null_sd": pstdev(vals),
    }


def bootstrap_dimensions(vectors: dict[str, list[float]], reps: int, seed: int, targets: list[tuple[str, str]]) -> dict:
    rng = random.Random(seed)
    labels = list(vectors)
    d = len(next(iter(vectors.values())))
    edge_counts = Counter()
    path_counts = Counter()
    for _ in range(reps):
        dims = [rng.randrange(d) for _ in range(d)]
        m = zscore_edge_matrix(build_matrix(vectors, dims))
        best = all_undirected_paths(labels, m)[0][1]
        canon = min(best, best[::-1])
        path_counts[canon] += 1
        for a, b in zip(best, best[1:]):
            edge_counts[canonical_edge(a, b)] += 1
    return {
        "reps": reps,
        "target_edge_selection_frequency": [
            {"edge": list(canonical_edge(*e)), "frequency": edge_counts[canonical_edge(*e)] / reps}
            for e in targets
        ],
        "all_edge_selection_frequency": [
            {"edge": list(e), "count": c, "frequency": c / reps}
            for e, c in edge_counts.most_common()
        ],
        "top_paths": [
            {"order": list(p), "count": c, "frequency": c / reps}
            for p, c in path_counts.most_common(12)
        ],
    }


def analyze_quire(name: str, units: dict[str, tuple[int, int]], lens_vectors: dict[str, dict[str, list[float]]], reps: int, seed: int) -> dict:
    labels = list(units)
    targets = TARGET_EDGES[name]
    lens_results = {}
    normalized = []
    for offset, (lens, vectors) in enumerate(lens_vectors.items()):
        raw = build_matrix(vectors)
        m = zscore_edge_matrix(raw)
        normalized.append(m)
        paths = all_undirected_paths(labels, m)
        lens_results[lens] = {
            "dimension_count": len(next(iter(vectors.values()))),
            "best_path": {"score": paths[0][0], "order": list(paths[0][1])},
            "text_candidate": rank_path(TEXT_CANDIDATE[name], paths),
            "current_order": rank_path(CURRENT_ORDER[name], paths),
            "target_edges": edge_ranks(m, targets),
            "target_edge_exact_test": exact_label_permutation_test(labels, m, targets),
            "dimension_bootstrap": bootstrap_dimensions(vectors, reps, seed + 1000 * offset, targets),
        }

    consensus = add_matrices(normalized)
    paths = all_undirected_paths(labels, consensus)
    lens_results["equal_weight_lens_consensus"] = {
        "construction": "mean of within-lens z-scored pairwise cosine similarities; no fitted weights",
        "best_path": {"score": paths[0][0], "order": list(paths[0][1])},
        "text_candidate": rank_path(TEXT_CANDIDATE[name], paths),
        "current_order": rank_path(CURRENT_ORDER[name], paths),
        "target_edges": edge_ranks(consensus, targets),
        "target_edge_exact_test": exact_label_permutation_test(labels, consensus, targets),
        "top10_paths": [
            {"rank": i + 1, "score": s, "order": list(p)}
            for i, (s, p) in enumerate(paths[:10])
        ],
    }
    return lens_results


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("profiles_dir", type=Path, help="Xenoglyph data/public/voynich_semantic_profiles")
    ap.add_argument("--reps", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=20261007)
    ap.add_argument("--json", type=Path)
    args = ap.parse_args()

    metadata = load_metadata(args.profiles_dir / "corpus_metadata.csv")
    by_quire: dict[str, dict[str, dict[str, list[float]]]] = {"Q13": {}, "Q20": {}}
    provenance = {"Q13": {}, "Q20": {}}
    lens_dims = {}

    for lens, fn in LENS_FILES.items():
        dims, pages = load_lens(args.profiles_dir / fn, metadata)
        lens_dims[lens] = dims
        for qname, units in (("Q13", Q13), ("Q20", Q20)):
            vecs, prov = aggregate_singulions(units, pages)
            by_quire[qname][lens] = vecs
            provenance[qname][lens] = prov

    result = {
        "status": "VISUAL_SEMANTIC_EXTERNAL_VALIDATION",
        "source": {
            "dataset": "xenoglyph-ai/voynich-public visual semantic profiles",
            "profile_generation": "image-only foundation-model profile vectors; no Voynich transcription consumed by this script",
        },
        "frozen_text_hypotheses": {
            "target_edges": {k: [list(e) for e in v] for k, v in TARGET_EDGES.items()},
            "candidate_orders": TEXT_CANDIDATE,
            "current_orders": CURRENT_ORDER,
        },
        "lens_dimensions": lens_dims,
        "page_face_provenance": provenance,
        "Q13": analyze_quire("Q13", Q13, by_quire["Q13"], args.reps, args.seed),
        "Q20": analyze_quire("Q20", Q20, by_quire["Q20"], args.reps, args.seed + 100000),
        "interpretation_guardrails": [
            "This is an external visual-semantic validation channel, not physical codicology.",
            "Profile dimensions are correlated semantic measurements; dimension bootstrap is sensitivity only.",
            "Exact label-permutation p-values test alignment with the preregistered textual edge set, not historical truth.",
            "The missing Q20 109|110 bifolium remains unmodelled.",
            "No lens weight or edge threshold is fitted on Q13/Q20.",
        ],
    }
    text = json.dumps(result, ensure_ascii=False, indent=2)
    print(text)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
