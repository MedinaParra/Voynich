#!/usr/bin/env python3
"""H84: exact panel × token-length robustness audit of external astronomical-label hapax enrichment."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import statistics
from collections import Counter, defaultdict
from pathlib import Path

REVISION = "2bb4437906b714c1fba26f9897f8df3e7660a0b0"
EXPECTED_METADATA_SHA256 = "ba0342e15d8c468ec4e9f741e97cdb4a11938fe1f0ae3ac4338b73aaf1bd773a"
EXPECTED_MATCHES_SHA256 = "4b78659807f83ea16da872eaf29dc259393bef96a10bc96361919a79db822000"
PANELS = ("f67r1", "f67r2", "f67v1", "f68r1", "f68r2", "f68r3", "f68v2", "f68v1")
PERMUTATIONS = 19_999
SEED_PRIMARY = 20261016
SEED_STAR = 20261017
MASK64 = (1 << 64) - 1


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
        if n <= 0:
            raise ValueError("n must be positive")
        threshold = (1 << 64) % n
        while True:
            x = self.next_u64()
            if x >= threshold:
                return x % n

    def sample(self, population: list[int], k: int) -> list[int]:
        if not 0 <= k <= len(population):
            raise ValueError("invalid sample size")
        work = population.copy()
        for i in range(k):
            j = i + self.randbelow(len(work) - i)
            work[i], work[j] = work[j], work[i]
        return work[:k]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_result(path: Path, result: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


def build_cells(occurrences: dict[int, dict]) -> dict[tuple[str, int], list[int]]:
    cells: dict[tuple[str, int], list[int]] = defaultdict(list)
    for pos, row in occurrences.items():
        cells[(row["folio"], len(row["token"]))].append(pos)
    return cells


def cell_inventory(selected: set[int], occurrences: dict[int, dict], cells: dict[tuple[str, int], list[int]]) -> tuple[list[dict], int, int, int]:
    counts: Counter[tuple[str, int]] = Counter((occurrences[p]["folio"], len(occurrences[p]["token"])) for p in selected)
    rows: list[dict] = []
    movable_positions = 0
    movable_cells = 0
    movable_panels: set[str] = set()
    for panel, length in sorted(counts):
        n = counts[(panel, length)]
        N = len(cells[(panel, length)])
        movable = N > n and n > 0
        if movable:
            movable_positions += n
            movable_cells += 1
            movable_panels.add(panel)
        rows.append({"panel": panel, "token_length": length, "selected_n": n, "cell_N": N, "movable": movable})
    return rows, movable_positions, movable_cells, len(movable_panels)


def run_null(selected: set[int], occurrences: dict[int, dict], cells: dict[tuple[str, int], list[int]], hapax: set[int], seed: int) -> dict:
    counts: Counter[tuple[str, int]] = Counter((occurrences[p]["folio"], len(occurrences[p]["token"])) for p in selected)
    observed_count = len(selected & hapax)
    observed_fraction = observed_count / len(selected)
    rng = SplitMix64(seed)
    values: list[float] = []
    for _ in range(PERMUTATIONS):
        hapax_count = 0
        total = 0
        for cell, n in counts.items():
            draw = rng.sample(cells[cell], n)
            hapax_count += sum(p in hapax for p in draw)
            total += n
        values.append(hapax_count / total)
    return {
        "seed": seed,
        "requested": PERMUTATIONS,
        "completed": len(values),
        "observed_hapax_count": observed_count,
        "sample_size": len(selected),
        "observed_fraction": observed_fraction,
        "null_mean": statistics.fmean(values),
        "null_sd": statistics.pstdev(values),
        "p_upper": (1 + sum(v >= observed_fraction for v in values)) / (len(values) + 1),
        "null_min": min(values),
        "null_max": max(values),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--metadata", required=True, type=Path)
    ap.add_argument("--matches", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()

    meta_bytes = args.metadata.read_bytes()
    match_bytes = args.matches.read_bytes()
    result: dict = {
        "classification": "ASTRONOMICAL_LABEL_HAPAX_EXACT_LENGTH_ROBUSTNESS_NOT_SEMANTICS",
        "status": "BLOCKED",
        "source": {
            "repository": "brigadire/voinich",
            "revision": REVISION,
            "metadata_sha256": sha256_bytes(meta_bytes),
            "metadata_expected_sha256": EXPECTED_METADATA_SHA256,
            "matches_sha256": sha256_bytes(match_bytes),
            "matches_expected_sha256": EXPECTED_MATCHES_SHA256,
        },
    }
    if result["source"]["metadata_sha256"] != EXPECTED_METADATA_SHA256 or result["source"]["matches_sha256"] != EXPECTED_MATCHES_SHA256:
        result["reason"] = "frozen external input SHA-256 mismatch"
        write_result(args.out, result)
        return

    occurrences: dict[int, dict] = {}
    for line in meta_bytes.decode("utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("section") != "A" or row.get("folio") not in PANELS:
            continue
        pos = int(row["absolute_token_position"])
        if pos in occurrences:
            result["reason"] = f"duplicate absolute token position {pos}"
            write_result(args.out, result)
            return
        token = row.get("token")
        if not isinstance(token, str):
            result["reason"] = f"non-string token at position {pos}"
            write_result(args.out, result)
            return
        occurrences[pos] = {"folio": row["folio"], "token": token}

    token_frequency = Counter(row["token"] for row in occurrences.values())
    hapax = {p for p, row in occurrences.items() if token_frequency[row["token"]] == 1}

    matched_rows = 0
    labels: set[int] = set()
    stars: set[int] = set()
    reader = csv.DictReader(match_bytes.decode("utf-8").splitlines(), delimiter="\t")
    for row in reader:
        if row.get("match_status") != "MATCHED":
            continue
        matched_rows += 1
        raw_positions = row.get("absolute_token_positions", "")
        positions = {int(x) for x in raw_positions.split(",") if x.strip()}
        labels.update(positions)
        if row.get("object_type") == "star":
            stars.update(positions)

    result["integrity"] = {
        "section_occurrences": len(occurrences),
        "section_hapax_occurrences": len(hapax),
        "matched_source_rows": matched_rows,
        "confirmed_label_positions": len(labels),
        "confirmed_label_hapax": len(labels & hapax),
        "star_positions": len(stars),
        "all_labels_inside_section": labels <= occurrences.keys(),
        "all_stars_inside_section": stars <= occurrences.keys(),
    }
    integrity_ok = (
        len(occurrences) == 901
        and len(hapax) == 518
        and matched_rows == 130
        and len(labels) == 112
        and labels <= occurrences.keys()
        and len(labels & hapax) == 80
        and stars <= occurrences.keys()
    )
    if not integrity_ok:
        result["reason"] = "published frozen-input invariant reproduction failed"
        write_result(args.out, result)
        return

    cells = build_cells(occurrences)
    primary_cells, movable_positions, movable_cells, movable_panels = cell_inventory(labels, occurrences, cells)
    exchange_gates = {
        "movable_label_positions_ge_80": movable_positions >= 80,
        "movable_occupied_cells_ge_12": movable_cells >= 12,
        "movable_panels_ge_7": movable_panels >= 7,
    }
    result["primary_exchangeability"] = {
        "occupied_cells": primary_cells,
        "movable_label_positions": movable_positions,
        "movable_occupied_cells": movable_cells,
        "movable_panels": movable_panels,
        "gates": exchange_gates,
    }
    if not all(exchange_gates.values()):
        result["reason"] = "frozen panel×exact-length exchangeability gate failed"
        write_result(args.out, result)
        return

    primary = run_null(labels, occurrences, cells, hapax, SEED_PRIMARY)
    result["primary"] = primary
    complete = primary["completed"] == PERMUTATIONS
    decision = {
        "observed_gt_null_mean": primary["observed_fraction"] > primary["null_mean"],
        "p_upper_le_0_05": primary["p_upper"] <= 0.05,
        "permutations_complete": complete,
    }
    result["primary_decision_gates"] = decision
    result["status"] = "PASS_ROBUSTNESS" if all(decision.values()) else "FAIL_ROBUSTNESS"

    # Frozen secondary/descriptive STAR family; it cannot alter the primary status.
    star_cells, star_movable_positions, star_movable_cells, star_movable_panels = cell_inventory(stars, occurrences, cells)
    result["secondary_star_exchangeability"] = {
        "occupied_cells": star_cells,
        "movable_star_positions": star_movable_positions,
        "movable_occupied_cells": star_movable_cells,
        "movable_panels": star_movable_panels,
    }
    if stars:
        result["secondary_star"] = run_null(stars, occurrences, cells, hapax, SEED_STAR)
    else:
        result["secondary_star"] = {"status": "NOT_RUN", "reason": "no frozen STAR positions"}

    result["interpretation_ceiling"] = "structural/documentary label-specialization robustness; not semantics"
    write_result(args.out, result)


if __name__ == "__main__":
    main()
