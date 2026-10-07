#!/usr/bin/env python3
"""H88 preregistered f68r2 historical 36+23 size-partition admissibility audit."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
from pathlib import Path

ENDPOINTS_BLOB = "e9733f16dc18b32ab5643c6d08a11f395c49a9c1"
GROUPS_BLOB = "5bcab575377d59147f313acc5929804f84bf02ab"
EXPECTED_STARS = 59
EXPECTED_GROUPS = 24
EXPECTED_SMALL = 23
EXPECTED_LARGE = 36


def git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def parse_tsv(data: bytes) -> list[dict[str, str]]:
    text = data.decode("utf-8-sig", errors="strict")
    return list(csv.DictReader(io.StringIO(text), delimiter="\t"))


def load_stars(rows: list[dict[str, str]]) -> tuple[dict[str, dict[str, float]], list[str]]:
    stars: dict[str, dict[str, float]] = {}
    errors: list[str] = []
    for row in rows:
        cid = row.get("canonical_id", "")
        if row.get("panel") != "f68r2":
            continue
        if row.get("object_type") != "STAR" or row.get("geometry_type") != "BOX":
            continue
        if row.get("layer") != "STAR_REFERENCE":
            continue
        if not (cid.startswith("HOBJ_f68r2_") or cid.startswith("HNEW_STAR_f68r2_")):
            continue
        if cid in stars:
            errors.append(f"duplicate star id: {cid}")
            continue
        try:
            x1 = float(row["bbox_x1"])
            y1 = float(row["bbox_y1"])
            x2 = float(row["bbox_x2"])
            y2 = float(row["bbox_y2"])
        except (KeyError, TypeError, ValueError) as exc:
            errors.append(f"invalid numeric box for {cid}: {exc}")
            continue
        w = x2 - x1
        h = y2 - y1
        if not (w > 0.0 and h > 0.0):
            errors.append(f"non-positive box for {cid}: w={w}, h={h}")
            continue
        area = w * h
        diagonal = math.hypot(w, h)
        stars[cid] = {
            "x1": x1,
            "y1": y1,
            "x2": x2,
            "y2": y2,
            "width": w,
            "height": h,
            "area": area,
            "diagonal": diagonal,
        }
    return stars, errors


def load_grouped_star_ids(rows: list[dict[str, str]]) -> tuple[list[str], list[str]]:
    ids: list[str] = []
    errors: list[str] = []
    for row in rows:
        if row.get("panel") != "f68r2":
            continue
        if row.get("relation_semantics") != "VISUAL_ASSOCIATION_GROUP":
            continue
        if row.get("human_confidence") != "HIGH":
            continue
        raw = row.get("star_ids", "").strip()
        # Frozen scope requires exactly one star ID, not a compound relation.
        parts = [p for p in raw.replace(";", " ").replace(",", " ").split() if p]
        if len(parts) != 1:
            errors.append(f"group {row.get('canonical_group_id','?')} has {len(parts)} star ids: {raw!r}")
            continue
        ids.append(parts[0])
    if len(ids) != len(set(ids)):
        errors.append("group-associated star IDs are not unique")
    return ids, errors


def optimum_two_cluster(values: dict[str, float]) -> dict[str, object]:
    ordered = sorted(values.items(), key=lambda kv: (math.log(kv[1]), kv[0]))
    logs = [math.log(v) for _, v in ordered]
    n = len(logs)
    candidates: list[tuple[float, int]] = []
    for split in range(1, n):
        left = logs[:split]
        right = logs[split:]
        ml = sum(left) / len(left)
        mr = sum(right) / len(right)
        sse = sum((v - ml) ** 2 for v in left) + sum((v - mr) ** 2 for v in right)
        candidates.append((sse, split))
    ranked = sorted(candidates, key=lambda item: (item[0], item[1]))
    best_sse, best_split = ranked[0]
    second_sse, second_split = ranked[1]
    tied = any(sse == best_sse and split != best_split for sse, split in candidates)
    small_ids = [sid for sid, _ in ordered[:best_split]]
    large_ids = [sid for sid, _ in ordered[best_split:]]
    max_small = max(values[sid] for sid in small_ids)
    min_large = min(values[sid] for sid in large_ids)
    return {
        "unique_optimum": not tied,
        "best_split_rank_small_count": best_split,
        "large_count": n - best_split,
        "best_total_sse_log_space": best_sse,
        "second_best_split_rank_small_count": second_split,
        "second_best_total_sse_log_space": second_sse,
        "second_over_best_sse_ratio": (second_sse / best_sse) if best_sse > 0 else None,
        "max_small_raw": max_small,
        "min_large_raw": min_large,
        "boundary_ratio_min_large_over_max_small": min_large / max_small,
        "small_ids": small_ids,
        "large_ids": large_ids,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--endpoints", type=Path, required=True)
    ap.add_argument("--groups", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    endpoint_bytes = args.endpoints.read_bytes()
    group_bytes = args.groups.read_bytes()
    observed = {
        "confirmed_endpoints": git_blob_sha1(endpoint_bytes),
        "f68r2_group_scope": git_blob_sha1(group_bytes),
    }
    expected = {
        "confirmed_endpoints": ENDPOINTS_BLOB,
        "f68r2_group_scope": GROUPS_BLOB,
    }
    out: dict[str, object] = {
        "classification": "F68R2_HISTORICAL_36_23_SIZE_PARTITION_ADMISSIBILITY_NOT_SEMANTICS",
        "source_blobs": observed,
        "expected_blobs": expected,
        "historical_prediction": {"small_border": EXPECTED_SMALL, "large_interior": EXPECTED_LARGE},
        "method": "exact global 1D k=2 minimum-SSE split in log area and log diagonal; no target-count tuning",
    }

    mismatch = [name for name in expected if observed[name] != expected[name]]
    if mismatch:
        out.update({"status": "BLOCKED", "reason": "frozen source blob mismatch", "mismatched_sources": mismatch})
    else:
        endpoint_rows = parse_tsv(endpoint_bytes)
        group_rows = parse_tsv(group_bytes)
        stars, star_errors = load_stars(endpoint_rows)
        grouped_ids, group_errors = load_grouped_star_ids(group_rows)
        missing_grouped = sorted(set(grouped_ids) - set(stars))
        gates = {
            "star_parse_errors_empty": not star_errors,
            "group_parse_errors_empty": not group_errors,
            "exactly_59_unique_stars": len(stars) == EXPECTED_STARS,
            "exactly_24_unique_groups": len(grouped_ids) == EXPECTED_GROUPS and len(set(grouped_ids)) == EXPECTED_GROUPS,
            "all_grouped_stars_present": not missing_grouped,
        }
        out.update({
            "inventory": {
                "star_count": len(stars),
                "group_count": len(grouped_ids),
                "star_parse_errors": star_errors,
                "group_parse_errors": group_errors,
                "missing_grouped_star_ids": missing_grouped,
            },
            "inventory_gates": gates,
        })
        if not all(gates.values()):
            out.update({"status": "BLOCKED", "reason": "frozen inventory/parsing gate failed"})
        else:
            metrics = {
                "area": optimum_two_cluster({sid: row["area"] for sid, row in stars.items()}),
                "diagonal": optimum_two_cluster({sid: row["diagonal"] for sid, row in stars.items()}),
            }
            area_large = set(metrics["area"]["large_ids"])
            diag_large = set(metrics["diagonal"]["large_ids"])
            grouped = set(grouped_ids)
            area_small_grouped = sorted(grouped - area_large)
            diag_small_grouped = sorted(grouped - diag_large)
            same_membership = set(metrics["area"]["small_ids"]) == set(metrics["diagonal"]["small_ids"])
            agreement_count = sum(
                (sid in area_large) == (sid in diag_large)
                for sid in stars
            )
            decision = {
                "area_unique_optimum": bool(metrics["area"]["unique_optimum"]),
                "diagonal_unique_optimum": bool(metrics["diagonal"]["unique_optimum"]),
                "area_23_small_36_large": metrics["area"]["best_split_rank_small_count"] == EXPECTED_SMALL and metrics["area"]["large_count"] == EXPECTED_LARGE,
                "diagonal_23_small_36_large": metrics["diagonal"]["best_split_rank_small_count"] == EXPECTED_SMALL and metrics["diagonal"]["large_count"] == EXPECTED_LARGE,
                "identical_membership_across_metrics": same_membership,
                "all_24_grouped_stars_large_by_area": not area_small_grouped,
                "all_24_grouped_stars_large_by_diagonal": not diag_small_grouped,
            }
            out.update({
                "metrics": metrics,
                "robustness": {
                    "partition_membership_agreement_count_of_59": agreement_count,
                    "grouped_stars_in_area_small_cluster": area_small_grouped,
                    "grouped_stars_in_diagonal_small_cluster": diag_small_grouped,
                },
                "decision_gates": decision,
            })
            if not metrics["area"]["unique_optimum"] or not metrics["diagonal"]["unique_optimum"]:
                out.update({"status": "BLOCKED", "reason": "non-unique global two-cluster optimum"})
            elif all(decision.values()):
                out["status"] = "PASS_ADMISSIBILITY"
            else:
                out["status"] = "FAIL_ADMISSIBILITY"

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
