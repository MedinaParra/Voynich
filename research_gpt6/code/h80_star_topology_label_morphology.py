#!/usr/bin/env python3
import argparse
import csv
import hashlib
import json
import math
import random
import re
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
from statistics import mean, pstdev

import numpy as np
from scipy.spatial import Delaunay, QhullError

STAR_SHA256 = "e7cb7787118aa71f440fbf544da5b327a6afd8eba8b2989d6e5ca71d40629d04"
YALE_BLOB_SHA1 = "12c4230fdefc8c566e9bdb3626fc6009c70a7533"
COORD_FRAME = "crop_x0_0_y0_550"
ANNOTATION_METHOD = "star-outline Harris-density refinement"
H79_MAPPING = {
    1: 50, 2: 38, 3: 37, 4: 43, 5: 31, 6: 36, 7: 48, 8: 53, 9: 54,
    10: 41, 11: 32, 12: 55, 13: 56, 14: 46, 15: 34, 16: 39, 17: 59,
    18: 51, 19: 52, 20: 40, 21: 44, 22: 58, 23: 57, 24: 35, 25: 45,
    26: 47, 27: 49, 28: 42, 29: 33,
}
JITTER_DRAWS = 1000
JITTER_SEED = 20261009
JITTER_HALF_WIDTH = 35.0
EDGE_STABILITY_MIN = 0.80
MIN_STABLE_EDGES = 25
MIN_COVERED_STARS = 24
MIN_NONEDGES = 200
PERMUTATIONS = 9999
UNRESTRICTED_SEED = 20261010
LENGTH_SEED = 20261011
ALPHA = 0.025


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def load_stars(path: Path):
    data = path.read_bytes()
    rows = []
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row.get("page") != "f68r1":
                continue
            rows.append({
                "star_id": int(row["star_id"]),
                "x": float(row["x"]),
                "y": float(row["y"]),
                "coordinate_frame": row["coordinate_frame"],
                "annotation_method": row["annotation_method"],
            })
    rows.sort(key=lambda r: r["star_id"])
    checks = {
        "sha256": sha256_bytes(data),
        "sha256_matches": sha256_bytes(data) == STAR_SHA256,
        "row_count_29": len(rows) == 29,
        "star_ids_1_to_29_unique": [r["star_id"] for r in rows] == list(range(1, 30)),
        "coordinate_frame_matches": all(r["coordinate_frame"] == COORD_FRAME for r in rows),
        "annotation_method_matches": all(r["annotation_method"] == ANNOTATION_METHOD for r in rows),
    }
    return rows, checks


def delaunay_edges(points):
    arr = np.asarray(points, dtype=float)
    tri = Delaunay(arr)
    edges = set()
    for simplex in tri.simplices:
        for a, b in combinations(sorted(int(x) for x in simplex), 2):
            edges.add((a, b))
    return edges


def stable_graph(stars):
    points = [(s["x"], s["y"]) for s in stars]
    try:
        base_edges = delaunay_edges(points)
    except QhullError as exc:
        return None, {"status": "BLOCKED", "reason": f"base Delaunay failure: {exc}"}

    counts = Counter()
    rng = random.Random(JITTER_SEED)
    completed = 0
    try:
        for _ in range(JITTER_DRAWS):
            jittered = [
                (
                    x + rng.uniform(-JITTER_HALF_WIDTH, JITTER_HALF_WIDTH),
                    y + rng.uniform(-JITTER_HALF_WIDTH, JITTER_HALF_WIDTH),
                )
                for x, y in points
            ]
            draw_edges = delaunay_edges(jittered)
            for edge in base_edges:
                if edge in draw_edges:
                    counts[edge] += 1
            completed += 1
    except QhullError as exc:
        return None, {"status": "BLOCKED", "reason": f"jitter Delaunay failure after {completed} draws: {exc}"}

    edge_rows = []
    stable = set()
    for a, b in sorted(base_edges):
        frac = counts[(a, b)] / completed if completed else 0.0
        row = {
            "star_id_a": stars[a]["star_id"],
            "star_id_b": stars[b]["star_id"],
            "preservation_fraction": frac,
            "stable": frac >= EDGE_STABILITY_MIN,
        }
        edge_rows.append(row)
        if row["stable"]:
            stable.add((a, b))

    covered = set()
    for a, b in stable:
        covered.add(a)
        covered.add(b)
    all_pairs = set(combinations(range(len(stars)), 2))
    nonedges = all_pairs - stable
    checks = {
        "jitter_draws_completed": completed,
        "base_edge_count": len(base_edges),
        "stable_edge_count": len(stable),
        "stable_edge_covered_star_count": len(covered),
        "nonedge_count": len(nonedges),
        "jitter_draws_complete": completed == JITTER_DRAWS,
        "stable_edges_at_least_25": len(stable) >= MIN_STABLE_EDGES,
        "covered_stars_at_least_24": len(covered) >= MIN_COVERED_STARS,
        "nonedges_at_least_200": len(nonedges) >= MIN_NONEDGES,
    }
    return {
        "base_edges": base_edges,
        "stable_edges": stable,
        "nonedges": nonedges,
        "edge_rows": edge_rows,
    }, checks


def load_yale_labels(path: Path):
    data = path.read_bytes()
    blob = git_blob_sha1(data)
    raw = json.loads(data.decode("utf-8"))
    if not isinstance(raw, list) or len(raw) != 2:
        raise ValueError("unexpected Yale coordinate JSON structure")
    vocab, boxes = raw
    tokens = {}
    token_rows = []
    occurrence_seen = set()
    for star_id in range(1, 30):
        occurrence = H79_MAPPING[star_id]
        if occurrence in occurrence_seen or occurrence >= len(boxes):
            raise ValueError("duplicate or out-of-range H79 occurrence")
        occurrence_seen.add(occurrence)
        coord_row = boxes[occurrence]
        if not isinstance(coord_row, list) or len(coord_row) < 5:
            raise ValueError(f"invalid Yale coordinate row {occurrence}")
        vocab_index = int(coord_row[0])
        if vocab_index < 0 or vocab_index >= len(vocab):
            raise ValueError(f"invalid vocabulary index at occurrence {occurrence}")
        vocab_row = vocab[vocab_index]
        if not isinstance(vocab_row, list) or not vocab_row:
            raise ValueError(f"invalid vocabulary row {vocab_index}")
        token = vocab_row[0]
        if not isinstance(token, str) or re.fullmatch(r"[a-z]{2,}", token) is None:
            raise ValueError(f"invalid token at star {star_id}: {token!r}")
        tokens[star_id] = token
        token_rows.append({
            "star_id": star_id,
            "yale_occurrence": occurrence,
            "vocab_index": vocab_index,
            "token": token,
            "length": len(token),
        })
    checks = {
        "git_blob_sha1": blob,
        "git_blob_sha1_matches": blob == YALE_BLOB_SHA1,
        "resolved_token_count_29": len(tokens) == 29,
        "unique_occurrence_count_29": len(occurrence_seen) == 29,
        "unique_star_count_29": len(set(tokens)) == 29,
        "all_tokens_lowercase_ascii_len_ge_2": all(re.fullmatch(r"[a-z]{2,}", t) is not None for t in tokens.values()),
    }
    return tokens, token_rows, checks


def levenshtein(a, b):
    if a == b:
        return 0
    if len(a) < len(b):
        a, b = b, a
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(
                cur[-1] + 1,
                prev[j] + 1,
                prev[j - 1] + (ca != cb),
            ))
        prev = cur
    return prev[-1]


def distance_matrix(tokens_by_star):
    ordered = [tokens_by_star[i] for i in range(1, 30)]
    n = len(ordered)
    mat = np.zeros((n, n), dtype=float)
    for i in range(n):
        for j in range(i + 1, n):
            d = levenshtein(ordered[i], ordered[j]) / max(len(ordered[i]), len(ordered[j]))
            mat[i, j] = mat[j, i] = d
    return mat, ordered


def pair_mean(mat, assignment, pairs):
    vals = [mat[assignment[a], assignment[b]] for a, b in pairs]
    return float(mean(vals))


def delta_for_assignment(mat, assignment, edges, nonedges):
    edge_mean = pair_mean(mat, assignment, edges)
    nonedge_mean = pair_mean(mat, assignment, nonedges)
    return edge_mean, nonedge_mean, edge_mean - nonedge_mean


def permutation_test(mat, base_assignment, edges, nonedges, mode, groups=None):
    seed = UNRESTRICTED_SEED if mode == "unrestricted" else LENGTH_SEED
    rng = random.Random(seed)
    observed_edge, observed_nonedge, observed_delta = delta_for_assignment(
        mat, base_assignment, edges, nonedges
    )
    null = []
    n = len(base_assignment)
    for _ in range(PERMUTATIONS):
        assigned = list(base_assignment)
        if mode == "unrestricted":
            rng.shuffle(assigned)
        else:
            for idxs in groups.values():
                if len(idxs) < 2:
                    continue
                vals = [assigned[i] for i in idxs]
                rng.shuffle(vals)
                for i, val in zip(idxs, vals):
                    assigned[i] = val
        _, _, delta = delta_for_assignment(mat, assigned, edges, nonedges)
        null.append(delta)
    p = (1 + sum(v <= observed_delta for v in null)) / (PERMUTATIONS + 1)
    return {
        "observed_edge_mean_normalized_edit": observed_edge,
        "observed_nonedge_mean_normalized_edit": observed_nonedge,
        "observed_delta_edit": observed_delta,
        "null_mean_delta": mean(null),
        "null_sd_delta": pstdev(null),
        "p_lower": p,
        "permutations_completed": len(null),
        "seed": seed,
    }


def length_diagnostic(tokens, edges, nonedges):
    lengths = [len(tokens[i]) for i in range(1, 30)]
    edge_vals = [abs(lengths[a] - lengths[b]) for a, b in edges]
    nonedge_vals = [abs(lengths[a] - lengths[b]) for a, b in nonedges]
    em = mean(edge_vals)
    nm = mean(nonedge_vals)
    return {
        "edge_mean_absolute_length_difference": em,
        "nonedge_mean_absolute_length_difference": nm,
        "edge_minus_nonedge": em - nm,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stars", type=Path, required=True)
    ap.add_argument("--yale", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    stars, star_checks = load_stars(args.stars)
    star_source_ok = all(v for k, v in star_checks.items() if k != "sha256")

    out = {
        "classification": "F68R1_STAR_TOPOLOGY_LABEL_MORPHOLOGY_NOT_TRANSLATION",
        "sources": {"stars": star_checks},
        "h79_mapping": {str(k): v for k, v in H79_MAPPING.items()},
        "parameters": {
            "jitter_draws": JITTER_DRAWS,
            "jitter_seed": JITTER_SEED,
            "jitter_half_width_px": JITTER_HALF_WIDTH,
            "stable_edge_fraction_min": EDGE_STABILITY_MIN,
            "permutations_per_null": PERMUTATIONS,
            "unrestricted_seed": UNRESTRICTED_SEED,
            "length_preserving_seed": LENGTH_SEED,
            "alpha_per_confirmatory_null": ALPHA,
        },
    }

    if not star_source_ok:
        out.update({"status": "BLOCKED", "reason": "star source-integrity gate failed"})
    else:
        graph, graph_checks = stable_graph(stars)
        out["graph_validity"] = graph_checks
        if graph is None or not all(v for k, v in graph_checks.items() if isinstance(v, bool)):
            out.update({"status": "BLOCKED", "reason": "preregistered robust-star-graph validity gate failed"})
        else:
            try:
                tokens, token_rows, yale_checks = load_yale_labels(args.yale)
            except Exception as exc:
                out.update({"status": "BLOCKED", "reason": f"Yale mapping/token resolution failure: {type(exc).__name__}: {exc}"})
                yale_checks = None
                tokens = None
            if tokens is not None:
                out["sources"]["yale"] = yale_checks
                yale_ok = all(v for k, v in yale_checks.items() if k != "git_blob_sha1")
                if not yale_ok:
                    out.update({"status": "BLOCKED", "reason": "Yale source/mapping/token validity gate failed"})
                else:
                    out["tokens"] = token_rows
                    out["base_delaunay_edges"] = graph_checks["base_edge_count"]
                    out["edge_stability"] = graph["edge_rows"]
                    out["stable_edges"] = [
                        [stars[a]["star_id"], stars[b]["star_id"]]
                        for a, b in sorted(graph["stable_edges"])
                    ]

                    length_groups = defaultdict(list)
                    for i, star_id in enumerate(range(1, 30)):
                        length_groups[len(tokens[star_id])].append(i)
                    movable = sum(len(v) for v in length_groups.values() if len(v) >= 2)
                    swappable_strata = sum(1 for v in length_groups.values() if len(v) >= 2)
                    exchangeability = {
                        "length_strata": {str(k): len(v) for k, v in sorted(length_groups.items())},
                        "movable_positions": movable,
                        "swappable_length_strata": swappable_strata,
                        "movable_positions_at_least_10": movable >= 10,
                        "swappable_length_strata_at_least_2": swappable_strata >= 2,
                    }
                    out["length_preserving_exchangeability"] = exchangeability
                    if not exchangeability["movable_positions_at_least_10"] or not exchangeability["swappable_length_strata_at_least_2"]:
                        out.update({"status": "BLOCKED", "reason": "exact-length-preserving exchangeability gate failed"})
                    else:
                        mat, ordered = distance_matrix(tokens)
                        base_assignment = list(range(29))
                        unrestricted = permutation_test(
                            mat, base_assignment, graph["stable_edges"], graph["nonedges"], "unrestricted"
                        )
                        length_preserving = permutation_test(
                            mat, base_assignment, graph["stable_edges"], graph["nonedges"],
                            "length_preserving", groups=length_groups
                        )
                        diag = length_diagnostic(tokens, graph["stable_edges"], graph["nonedges"])
                        scientific_pass = (
                            unrestricted["observed_delta_edit"] < 0 and
                            unrestricted["p_lower"] <= ALPHA and
                            length_preserving["p_lower"] <= ALPHA and
                            unrestricted["permutations_completed"] == PERMUTATIONS and
                            length_preserving["permutations_completed"] == PERMUTATIONS
                        )
                        out.update({
                            "unrestricted_null": unrestricted,
                            "exact_length_preserving_null": length_preserving,
                            "length_diagnostic": diag,
                            "status": "PASS" if scientific_pass else "FAIL",
                        })

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
