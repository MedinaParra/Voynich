#!/usr/bin/env python3
"""H85: preregistered exploratory f68r2 spatial ↔ label-length replication challenge."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import statistics
from pathlib import Path

RN_EXPECTED_BLOB_SHA1 = "b19bbeae51334ab124f05f081b5dc6e07ef2ae42"
SEETON_EXPECTED_SHA256 = "e7cb7787118aa71f440fbf544da5b327a6afd8eba8b2989d6e5ca71d40629d04"
YALE_EXPECTED_BLOB_SHA1 = "12c4230fdefc8c566e9bdb3626fc6009c70a7533"
PERMUTATIONS = 19_999
SEED_F68R2 = 20261018
SEED_F68R1 = 20261019
LABEL_RE = re.compile(r"^[a-z]{2,}$")
MASK64 = (1 << 64) - 1
H79_MAPPING = {
    1:50, 2:38, 3:37, 4:43, 5:31, 6:36, 7:48, 8:53, 9:54, 10:41,
    11:32, 12:55, 13:56, 14:46, 15:34, 16:39, 17:59, 18:51, 19:52,
    20:40, 21:44, 22:58, 23:57, 24:35, 25:45, 26:47, 27:49, 28:42, 29:33,
}


class SplitMix64:
    def __init__(self, seed: int):
        self.state = seed & MASK64

    def next_u64(self) -> int:
        self.state = (self.state + 0x9E3779B97F4A7C15) & MASK64
        z = self.state
        z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & MASK64
        z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & MASK64
        return (z ^ (z >> 31)) & MASK64

    def randbelow(self, n: int) -> int:
        threshold = (1 << 64) % n
        while True:
            x = self.next_u64()
            if x >= threshold:
                return x % n

    def shuffled(self, seq: list[int]) -> list[int]:
        out = seq.copy()
        for i in range(len(out) - 1, 0, -1):
            j = self.randbelow(i + 1)
            out[i], out[j] = out[j], out[i]
        return out


def git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def average_ranks(values: list[float]) -> list[float]:
    order = sorted(range(len(values)), key=values.__getitem__)
    ranks = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i + 1
        v = values[order[i]]
        while j < len(order) and values[order[j]] == v:
            j += 1
        avg = (i + 1 + j) / 2.0
        for k in range(i, j):
            ranks[order[k]] = avg
        i = j
    return ranks


def pearson(x: list[float], y: list[float]) -> float:
    mx = statistics.fmean(x)
    my = statistics.fmean(y)
    dx = [v - mx for v in x]
    dy = [v - my for v in y]
    sx = math.sqrt(sum(v * v for v in dx))
    sy = math.sqrt(sum(v * v for v in dy))
    if sx == 0.0 or sy == 0.0:
        raise ValueError("zero variance")
    return sum(a * b for a, b in zip(dx, dy)) / (sx * sy)


def spearman(x: list[float], y: list[float]) -> float:
    return pearson(average_ranks(x), average_ranks(y))


def pair_vectors(coords: list[tuple[float, float]], lengths: list[int]) -> tuple[list[float], list[float]]:
    g: list[float] = []
    l: list[float] = []
    for i in range(len(coords)):
        for j in range(i + 1, len(coords)):
            g.append(math.hypot(coords[i][0] - coords[j][0], coords[i][1] - coords[j][1]))
            l.append(float(abs(lengths[i] - lengths[j])))
    return g, l


def permutation_test(coords: list[tuple[float, float]], lengths: list[int], seed: int) -> dict:
    spatial, lengthdiff = pair_vectors(coords, lengths)
    observed = spearman(spatial, lengthdiff)
    rng = SplitMix64(seed)
    null: list[float] = []
    for _ in range(PERMUTATIONS):
        perm_lengths = rng.shuffled(lengths)
        _, perm_diff = pair_vectors(coords, perm_lengths)
        null.append(spearman(spatial, perm_diff))
    return {
        "n_objects": len(coords),
        "n_pairs": len(spatial),
        "rho_observed": observed,
        "null_mean": statistics.fmean(null),
        "null_sd": statistics.pstdev(null),
        "null_min": min(null),
        "null_max": max(null),
        "p_upper": (1 + sum(v >= observed for v in null)) / (len(null) + 1),
        "seed": seed,
        "requested": PERMUTATIONS,
        "completed": len(null),
    }


def write_result(path: Path, result: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--f68r2-csv", required=True, type=Path)
    ap.add_argument("--f68r1-centres", required=True, type=Path)
    ap.add_argument("--f68r1-yale", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()

    rn_raw = args.f68r2_csv.read_bytes()
    seeton_raw = args.f68r1_centres.read_bytes()
    yale_raw = args.f68r1_yale.read_bytes()
    result: dict = {
        "classification": "F68R2_SPATIAL_LABEL_LENGTH_REPLICATION_EXPLORATORY_NOT_SEMANTICS",
        "status": "BLOCKED",
        "sources": {
            "f68r2_rn_top": {
                "git_blob_sha1": git_blob_sha1(rn_raw),
                "expected_git_blob_sha1": RN_EXPECTED_BLOB_SHA1,
            },
            "f68r1_seeton": {
                "sha256": hashlib.sha256(seeton_raw).hexdigest(),
                "expected_sha256": SEETON_EXPECTED_SHA256,
            },
            "f68r1_yale": {
                "git_blob_sha1": git_blob_sha1(yale_raw),
                "expected_git_blob_sha1": YALE_EXPECTED_BLOB_SHA1,
            },
        },
    }
    source_ok = (
        result["sources"]["f68r2_rn_top"]["git_blob_sha1"] == RN_EXPECTED_BLOB_SHA1
        and result["sources"]["f68r1_seeton"]["sha256"] == SEETON_EXPECTED_SHA256
        and result["sources"]["f68r1_yale"]["git_blob_sha1"] == YALE_EXPECTED_BLOB_SHA1
    )
    if not source_ok:
        result["reason"] = "frozen source-integrity gate failed"
        write_result(args.out, result)
        return

    # Primary f68r2 arm.
    rows = list(csv.DictReader(rn_raw.decode("utf-8").splitlines()))
    f68r2 = [r for r in rows if r.get("panel") == "f68r2"]
    result["f68r2_raw_rows"] = len(f68r2)
    if len(f68r2) != 23:
        result["reason"] = "f68r2 raw cardinality is not exactly 23"
        write_result(args.out, result)
        return

    valid2: list[dict] = []
    excluded2: list[dict] = []
    for r in f68r2:
        zl = r.get("zl_label", "")
        if " " not in zl:
            excluded2.append({"star": r.get("star"), "zl_label": zl, "reason": "no locator/string separator"})
            continue
        _, token = zl.split(None, 1)
        if not LABEL_RE.fullmatch(token):
            excluded2.append({"star": r.get("star"), "zl_label": zl, "token": token, "reason": "token fails ^[a-z]{2,}$"})
            continue
        valid2.append({
            "star": int(r["star"]),
            "x": float(r["x"]),
            "y": float(r["y"]),
            "token": token,
            "length": len(token),
        })

    result["f68r2_excluded"] = excluded2
    lengths2 = [r["length"] for r in valid2]
    coords2 = [(r["x"], r["y"]) for r in valid2]
    stars2 = [r["star"] for r in valid2]
    spatial2, diff2 = pair_vectors(coords2, lengths2) if len(valid2) >= 2 else ([], [])
    sample_gates = {
        "valid_rows_ge_18": len(valid2) >= 18,
        "distinct_lengths_ge_5": len(set(lengths2)) >= 5,
        "unique_star_ids": len(stars2) == len(set(stars2)),
        "spatial_variance_nonzero": len(spatial2) > 1 and len(set(spatial2)) > 1,
        "length_difference_variance_nonzero": len(diff2) > 1 and len(set(diff2)) > 1,
    }
    result["f68r2_sample"] = {
        "valid_rows": len(valid2),
        "token_length_counts": {str(k): lengths2.count(k) for k in sorted(set(lengths2))},
        "gates": sample_gates,
    }
    if not all(sample_gates.values()):
        result["reason"] = "frozen f68r2 sample/variance gate failed"
        write_result(args.out, result)
        return

    primary = permutation_test(coords2, lengths2, SEED_F68R2)
    result["primary_f68r2"] = primary
    decision = {
        "rho_gt_0": primary["rho_observed"] > 0,
        "p_upper_le_0_05": primary["p_upper"] <= 0.05,
        "permutations_complete": primary["completed"] == PERMUTATIONS,
    }
    result["primary_decision_gates"] = decision
    result["status"] = "PASS_EXPLORATORY" if all(decision.values()) else "FAIL_EXPLORATORY"

    # Diagnostic f68r1 arm.
    centre_rows = list(csv.DictReader(seeton_raw.decode("utf-8").splitlines()))
    centres = {int(r["star_id"]): (float(r["x"]), float(r["y"])) for r in centre_rows if r.get("page") == "f68r1"}
    diagnostic: dict = {"status": "BLOCKED_DIAGNOSTIC"}
    try:
        if set(centres) != set(range(1, 30)):
            raise ValueError("f68r1 star IDs are not exactly 1..29")
        if len(set(H79_MAPPING.values())) != 29:
            raise ValueError("H79 occurrence mapping is not unique")
        yale = json.loads(yale_raw.decode("utf-8"))
        if not (isinstance(yale, list) and len(yale) == 2):
            raise ValueError("unexpected Yale JSON top-level shape")
        vocab, coord_rows = yale
        tokens1: list[str] = []
        coords1: list[tuple[float, float]] = []
        resolved: list[dict] = []
        for star in range(1, 30):
            occurrence = H79_MAPPING[star]
            row = coord_rows[occurrence]
            vocab_index = int(row[0])
            token = vocab[vocab_index][0]
            if not isinstance(token, str) or not LABEL_RE.fullmatch(token):
                raise ValueError(f"invalid Yale token for star {star}: {token!r}")
            tokens1.append(token)
            coords1.append(centres[star])
            resolved.append({"star": star, "occurrence": occurrence, "token": token, "length": len(token)})
        lengths1 = [len(t) for t in tokens1]
        spatial1, diff1 = pair_vectors(coords1, lengths1)
        if len(set(spatial1)) <= 1 or len(set(diff1)) <= 1:
            raise ValueError("zero diagnostic variance")
        diag_test = permutation_test(coords1, lengths1, SEED_F68R1)
        diagnostic = {
            "status": "EXECUTED_DISCOVERY_DIAGNOSTIC",
            "resolved_labels": resolved,
            "token_length_counts": {str(k): lengths1.count(k) for k in sorted(set(lengths1))},
            **diag_test,
        }
    except Exception as exc:
        diagnostic = {"status": "BLOCKED_DIAGNOSTIC", "reason": str(exc)}
    result["diagnostic_f68r1"] = diagnostic
    result["interpretation_ceiling"] = "exploratory coarse spatial organization of token length; not semantics or coordinate decoding"
    write_result(args.out, result)


if __name__ == "__main__":
    main()
