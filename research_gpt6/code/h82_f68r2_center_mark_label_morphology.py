#!/usr/bin/env python3
"""H82: preregistered exploratory f68r2 centre-mark ↔ label-morphology test."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import random
import re
import statistics
from collections import defaultdict
from pathlib import Path

EXPECTED_BLOB_SHA1 = "b19bbeae51334ab124f05f081b5dc6e07ef2ae42"
PERMUTATIONS = 19_999
SEED_UNRESTRICTED = 20261014
SEED_LENGTH = 20261015
ALPHA = 0.025
LABEL_RE = re.compile(r"^[a-z]{2,}$")


def git_blob_sha1(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def levenshtein(a: str, b: str) -> int:
    if len(a) < len(b):
        a, b = b, a
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, start=1):
        cur = [i]
        for j, cb in enumerate(b, start=1):
            cur.append(min(cur[-1] + 1, prev[j] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def norm_edit(a: str, b: str) -> float:
    return levenshtein(a, b) / max(len(a), len(b))


def morphology_stat(tokens: list[str], marked: set[int]) -> dict[str, float]:
    between: list[float] = []
    within_marked: list[float] = []
    within_plain: list[float] = []
    for i in range(len(tokens)):
        for j in range(i + 1, len(tokens)):
            d = norm_edit(tokens[i], tokens[j])
            mi = i in marked
            mj = j in marked
            if mi != mj:
                between.append(d)
            elif mi:
                within_marked.append(d)
            else:
                within_plain.append(d)
    if not between or not within_marked or not within_plain:
        raise ValueError("insufficient pair classes for frozen statistic")
    d_between = statistics.fmean(between)
    d_marked = statistics.fmean(within_marked)
    d_plain = statistics.fmean(within_plain)
    d_within = 0.5 * (d_marked + d_plain)
    return {
        "D_between": d_between,
        "D_marked": d_marked,
        "D_plain": d_plain,
        "D_within": d_within,
        "S": d_between - d_within,
    }


def summarize_null(values: list[float], observed: float) -> dict[str, float | int]:
    return {
        "mean": statistics.fmean(values),
        "sd": statistics.pstdev(values),
        "p_upper": (1 + sum(v >= observed for v in values)) / (len(values) + 1),
        "completed": len(values),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()

    raw = args.csv.read_bytes()
    blob_sha1 = git_blob_sha1(raw)
    result: dict = {
        "classification": "F68R2_CENTER_MARK_LABEL_MORPHOLOGY_EXPLORATORY_NOT_SEMANTICS",
        "source": {
            "repository": "RN-Top/Voynich",
            "revision": "1eb6c0d1e98fb56acaadc0095c4d88a4a1c5bed0",
            "path": "analyses/star_centres_f68r2_r3.csv",
            "expected_git_blob_sha1": EXPECTED_BLOB_SHA1,
            "git_blob_sha1": blob_sha1,
        },
        "status": "BLOCKED",
    }

    if blob_sha1 != EXPECTED_BLOB_SHA1:
        result["reason"] = "source Git blob SHA-1 mismatch"
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(result, indent=2, sort_keys=True))
        return

    rows = list(csv.DictReader(raw.decode("utf-8").splitlines()))
    f68 = [r for r in rows if r.get("panel") == "f68r2"]
    result["raw_f68r2_rows"] = len(f68)
    if len(f68) != 23:
        result["reason"] = "raw f68r2 cardinality is not exactly 23"
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(result, indent=2, sort_keys=True))
        return

    allowed_centres = {"plain", "ring", "dot"}
    if any(r.get("centre") not in allowed_centres for r in f68):
        result["reason"] = "unexpected centre class"
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(result, indent=2, sort_keys=True))
        return

    valid: list[dict] = []
    excluded: list[dict] = []
    for r in f68:
        star = r.get("star", "")
        zl = r.get("zl_label", "")
        if " " not in zl:
            excluded.append({"star": star, "zl_label": zl, "reason": "zl_label has no locator/string separator"})
            continue
        _, token = zl.split(None, 1)
        if not LABEL_RE.fullmatch(token):
            excluded.append({"star": star, "zl_label": zl, "extracted": token, "reason": "label does not match ^[a-z]{2,}$"})
            continue
        valid.append({
            "star": int(star),
            "centre": r["centre"],
            "visual_class": "marked" if r["centre"] in {"ring", "dot"} else "plain",
            "token": token,
            "length": len(token),
        })

    result["excluded_rows"] = excluded
    result["valid_rows"] = valid

    stars = [r["star"] for r in valid]
    marked_count = sum(r["visual_class"] == "marked" for r in valid)
    plain_count = sum(r["visual_class"] == "plain" for r in valid)
    lengths = sorted({r["length"] for r in valid})
    sample_gates = {
        "valid_rows_ge_18": len(valid) >= 18,
        "marked_ge_5": marked_count >= 5,
        "plain_ge_12": plain_count >= 12,
        "distinct_lengths_ge_4": len(lengths) >= 4,
        "unique_star_ids": len(stars) == len(set(stars)),
    }
    result["sample"] = {
        "n_valid": len(valid),
        "marked": marked_count,
        "plain": plain_count,
        "distinct_lengths": lengths,
        "gates": sample_gates,
    }
    if not all(sample_gates.values()):
        result["reason"] = "frozen sample-validity gate failed"
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(result, indent=2, sort_keys=True))
        return

    tokens = [r["token"] for r in valid]
    observed_marked = {i for i, r in enumerate(valid) if r["visual_class"] == "marked"}

    by_length: dict[int, list[int]] = defaultdict(list)
    for i, r in enumerate(valid):
        by_length[r["length"]].append(i)

    length_inventory: dict[str, dict[str, int | bool]] = {}
    mixed_lengths: list[int] = []
    movable_positions = 0
    movable_marked = 0
    for length, idxs in sorted(by_length.items()):
        m = sum(i in observed_marked for i in idxs)
        p = len(idxs) - m
        mixed = m > 0 and p > 0
        if mixed:
            mixed_lengths.append(length)
            movable_positions += len(idxs)
            movable_marked += m
        length_inventory[str(length)] = {
            "total": len(idxs),
            "marked": m,
            "plain": p,
            "mixed": mixed,
        }

    exchange_gates = {
        "movable_positions_ge_10": movable_positions >= 10,
        "mixed_length_strata_ge_3": len(mixed_lengths) >= 3,
        "movable_marked_ge_4": movable_marked >= 4,
    }
    result["exact_length_inventory"] = length_inventory
    result["exchangeability"] = {
        "mixed_length_strata": mixed_lengths,
        "movable_positions": movable_positions,
        "movable_marked_positions": movable_marked,
        "gates": exchange_gates,
    }
    if not all(exchange_gates.values()):
        result["reason"] = "frozen exact-length exchangeability gate failed"
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(result, indent=2, sort_keys=True))
        return

    observed = morphology_stat(tokens, observed_marked)
    result["observed"] = observed
    result["length_diagnostic"] = {
        "mean_marked": statistics.fmean(r["length"] for r in valid if r["visual_class"] == "marked"),
        "mean_plain": statistics.fmean(r["length"] for r in valid if r["visual_class"] == "plain"),
    }

    rng_a = random.Random(SEED_UNRESTRICTED)
    null_a: list[float] = []
    all_indices = list(range(len(valid)))
    for _ in range(PERMUTATIONS):
        perm_marked = set(rng_a.sample(all_indices, marked_count))
        null_a.append(morphology_stat(tokens, perm_marked)["S"])
    null_a_summary = summarize_null(null_a, observed["S"])
    null_a_summary["seed"] = SEED_UNRESTRICTED
    null_a_summary["requested"] = PERMUTATIONS
    result["null_unrestricted"] = null_a_summary

    rng_b = random.Random(SEED_LENGTH)
    null_b: list[float] = []
    observed_m_by_length = {
        length: sum(i in observed_marked for i in idxs) for length, idxs in by_length.items()
    }
    for _ in range(PERMUTATIONS):
        perm_marked: set[int] = set()
        for length, idxs in by_length.items():
            m = observed_m_by_length[length]
            if m:
                perm_marked.update(rng_b.sample(idxs, m))
        null_b.append(morphology_stat(tokens, perm_marked)["S"])
    null_b_summary = summarize_null(null_b, observed["S"])
    null_b_summary["seed"] = SEED_LENGTH
    null_b_summary["requested"] = PERMUTATIONS
    result["null_length_preserving"] = null_b_summary

    completed = (
        null_a_summary["completed"] == PERMUTATIONS
        and null_b_summary["completed"] == PERMUTATIONS
    )
    scientific = {
        "S_gt_0": observed["S"] > 0,
        "p_unrestricted_le_0_025": null_a_summary["p_upper"] <= ALPHA,
        "p_length_preserving_le_0_025": null_b_summary["p_upper"] <= ALPHA,
        "permutations_complete": completed,
    }
    result["decision"] = scientific
    result["status"] = "PASS_EXPLORATORY" if all(scientific.values()) else "FAIL_EXPLORATORY"
    result["interpretation_ceiling"] = "exploratory visual-class↔label-character-form association; not semantics"

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
