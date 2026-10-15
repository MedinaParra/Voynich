#!/usr/bin/env python3
import argparse
import csv
import hashlib
import json
import math
import random
from pathlib import Path
from statistics import mean, median, pstdev

import numpy as np
from scipy.optimize import linear_sum_assignment

EXPECTED_ANNOTATION_SHA256 = "e7cb7787118aa71f440fbf544da5b327a6afd8eba8b2989d6e5ca71d40629d04"
EXPECTED_YALE_BLOB_SHA1 = "12c4230fdefc8c566e9bdb3626fc6009c70a7533"
EXPECTED_COORD_FRAME = "crop_x0_0_y0_550"
EXPECTED_METHOD = "star-outline Harris-density refinement"
LABEL_START = 31
LABEL_END = 59
PERMUTATIONS = 9999
PERMUTATION_SEED = 20261007
JITTER_DRAWS = 1000
JITTER_SEED = 20261008
JITTER_HALF_WIDTH = 35.0
PRIMARY_ALPHA = 0.01
SENSITIVITY_ALPHA = 0.05
PAIR_STABILITY_MIN = 0.80
STABLE_PAIR_COUNT_MIN = 20


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def load_star_centres(path: Path):
    data = path.read_bytes()
    digest = sha256_bytes(data)
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
    integrity = {
        "sha256": digest,
        "sha256_matches": digest == EXPECTED_ANNOTATION_SHA256,
        "row_count_29": len(rows) == 29,
        "star_ids_1_to_29_unique": [r["star_id"] for r in rows] == list(range(1, 30)),
        "coordinate_frame_matches": all(r["coordinate_frame"] == EXPECTED_COORD_FRAME for r in rows),
        "annotation_method_matches": all(r["annotation_method"] == EXPECTED_METHOD for r in rows),
    }
    return rows, integrity


def extract_second_top_level_array(raw: str):
    """Return only the second top-level JSON array without interpreting vocabulary entries."""
    if not raw or raw[0] != "[":
        raise ValueError("unexpected Yale JSON top-level structure")
    depth = 0
    in_string = False
    escape = False
    first_array_end = None
    second_start = None
    for i, ch in enumerate(raw):
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
            continue
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 1 and first_array_end is None:
                first_array_end = i
        elif ch == "," and depth == 1 and first_array_end is not None and second_start is None:
            j = i + 1
            while j < len(raw) and raw[j].isspace():
                j += 1
            if j >= len(raw) or raw[j] != "[":
                raise ValueError("second Yale top-level element is not an array")
            second_start = j
            break
    if second_start is None:
        raise ValueError("could not locate second Yale top-level array")

    depth = 0
    in_string = False
    escape = False
    for i in range(second_start, len(raw)):
        ch = raw[i]
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
            continue
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 0:
                return json.loads(raw[second_start:i + 1])
    raise ValueError("unterminated second Yale top-level array")


def load_yale_boxes(path: Path):
    data = path.read_bytes()
    blob = git_blob_sha1(data)
    raw = data.decode("utf-8")
    all_boxes = extract_second_top_level_array(raw)
    if LABEL_END >= len(all_boxes):
        raise ValueError("frozen label block exceeds Yale coordinate array")
    boxes = []
    for occurrence in range(LABEL_START, LABEL_END + 1):
        row = all_boxes[occurrence]
        if not isinstance(row, list) or len(row) < 5:
            raise ValueError(f"invalid coordinate row at occurrence {occurrence}")
        # row[0] is a vocabulary index and is deliberately ignored.
        boxes.append({
            "occurrence": occurrence,
            "x": float(row[1]),
            "y": float(row[2]),
            "width": float(row[3]),
            "height": float(row[4]),
        })
    integrity = {
        "git_blob_sha1": blob,
        "git_blob_sha1_matches": blob == EXPECTED_YALE_BLOB_SHA1,
        "total_coordinate_box_count": len(all_boxes),
        "frozen_block_start": LABEL_START,
        "frozen_block_end": LABEL_END,
        "frozen_block_count_29": len(boxes) == 29,
    }
    return boxes, integrity


def average_ranks(values):
    order = sorted(range(len(values)), key=lambda i: (values[i], i))
    ranks = [0.0] * len(values)
    start = 0
    while start < len(order):
        end = start + 1
        while end < len(order) and values[order[end]] == values[order[start]]:
            end += 1
        avg = ((start + 1) + end) / 2.0
        for idx in order[start:end]:
            ranks[idx] = avg
        start = end
    return ranks


def rank_points(points):
    n = len(points)
    if n < 2:
        raise ValueError("need at least two points")
    xr = average_ranks([p[0] for p in points])
    yr = average_ranks([p[1] for p in points])
    return np.array([[(x - 1.0) / (n - 1.0), (y - 1.0) / (n - 1.0)] for x, y in zip(xr, yr)], dtype=float)


def assignment(star_rank, label_rank):
    diff = star_rank[:, None, :] - label_rank[None, :, :]
    costs = np.sqrt((diff * diff).sum(axis=2))
    rows, cols = linear_sum_assignment(costs)
    dists = costs[rows, cols]
    mapping = {int(r): int(c) for r, c in zip(rows, cols)}
    return {
        "mean": float(dists.mean()),
        "median": float(np.median(dists)),
        "max": float(dists.max()),
        "mapping": mapping,
        "distances": {int(r): float(costs[r, c]) for r, c in zip(rows, cols)},
    }


def label_points(boxes, anchor):
    points = []
    for b in boxes:
        x, y = b["x"], b["y"]
        if anchor == "center":
            x += b["width"] / 2.0
            y += b["height"] / 2.0
        points.append((x, y))
    return points


def null_test(star_rank, label_rank, seed):
    observed = assignment(star_rank, label_rank)
    rng = random.Random(seed)
    y = label_rank[:, 1].tolist()
    null_costs = []
    for _ in range(PERMUTATIONS):
        yp = y[:]
        rng.shuffle(yp)
        trial = np.column_stack([label_rank[:, 0], np.array(yp, dtype=float)])
        null_costs.append(assignment(star_rank, trial)["mean"])
    null_mean = mean(null_costs)
    p = (1 + sum(v <= observed["mean"] for v in null_costs)) / (PERMUTATIONS + 1)
    return {
        "observed_mean_assigned_rank_distance": observed["mean"],
        "observed_median_assigned_rank_distance": observed["median"],
        "observed_max_assigned_rank_distance": observed["max"],
        "null_mean": null_mean,
        "null_sd": pstdev(null_costs),
        "observed_minus_null_mean": observed["mean"] - null_mean,
        "p_lower": p,
        "permutations_completed": len(null_costs),
        "assignment": observed,
    }


def jitter_stability(stars, label_rank, base_mapping):
    rng = random.Random(JITTER_SEED)
    preserved = [0] * len(stars)
    completed = 0
    for _ in range(JITTER_DRAWS):
        jittered = [
            (
                s["x"] + rng.uniform(-JITTER_HALF_WIDTH, JITTER_HALF_WIDTH),
                s["y"] + rng.uniform(-JITTER_HALF_WIDTH, JITTER_HALF_WIDTH),
            )
            for s in stars
        ]
        star_rank = rank_points(jittered)
        trial = assignment(star_rank, label_rank)["mapping"]
        for si in range(len(stars)):
            if trial.get(si) == base_mapping.get(si):
                preserved[si] += 1
        completed += 1
    fractions = [count / completed for count in preserved]
    return fractions, completed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stars", type=Path, required=True)
    ap.add_argument("--yale", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    stars, star_integrity = load_star_centres(args.stars)
    boxes, yale_integrity = load_yale_boxes(args.yale)

    source_ok = all([
        star_integrity["sha256_matches"],
        star_integrity["row_count_29"],
        star_integrity["star_ids_1_to_29_unique"],
        star_integrity["coordinate_frame_matches"],
        star_integrity["annotation_method_matches"],
        yale_integrity["git_blob_sha1_matches"],
        yale_integrity["frozen_block_count_29"],
    ])

    out = {
        "classification": "F68R1_STAR_LABEL_GEOMETRIC_PAIRING_NOT_SEMANTICS",
        "source_integrity": {
            "external_star_centres": star_integrity,
            "yale_coordinate_boxes": yale_integrity,
        },
        "parameters": {
            "permutations": PERMUTATIONS,
            "permutation_seed": PERMUTATION_SEED,
            "jitter_draws": JITTER_DRAWS,
            "jitter_seed": JITTER_SEED,
            "jitter_half_width_px": JITTER_HALF_WIDTH,
            "primary_alpha": PRIMARY_ALPHA,
            "sensitivity_alpha": SENSITIVITY_ALPHA,
            "pair_stability_min": PAIR_STABILITY_MIN,
            "stable_pair_count_min": STABLE_PAIR_COUNT_MIN,
        },
    }

    if not source_ok or len(stars) != 29 or len(boxes) != 29:
        out.update({"status": "BLOCKED", "reason": "frozen source-integrity/cardinality gate failed"})
    else:
        star_points = [(s["x"], s["y"]) for s in stars]
        star_rank = rank_points(star_points)
        top_left_rank = rank_points(label_points(boxes, "top_left"))
        center_rank = rank_points(label_points(boxes, "center"))

        primary = null_test(star_rank, top_left_rank, PERMUTATION_SEED)
        sensitivity = null_test(star_rank, center_rank, PERMUTATION_SEED)

        fractions, jitter_completed = jitter_stability(
            stars, top_left_rank, primary["assignment"]["mapping"]
        )
        pair_rows = []
        stable_count = 0
        for si, star in enumerate(stars):
            li = primary["assignment"]["mapping"][si]
            frac = fractions[si]
            stable = frac >= PAIR_STABILITY_MIN
            stable_count += int(stable)
            pair_rows.append({
                "star_id": star["star_id"],
                "star_x": star["x"],
                "star_y": star["y"],
                "yale_occurrence": boxes[li]["occurrence"],
                "label_bbox": [boxes[li]["x"], boxes[li]["y"], boxes[li]["width"], boxes[li]["height"]],
                "base_rank_distance": primary["assignment"]["distances"][si],
                "jitter_pair_preservation_fraction": frac,
                "jitter_stable": stable,
            })

        primary_ok = (
            primary["observed_mean_assigned_rank_distance"] < primary["null_mean"] and
            primary["p_lower"] <= PRIMARY_ALPHA and
            primary["permutations_completed"] == PERMUTATIONS
        )
        sensitivity_ok = (
            sensitivity["observed_mean_assigned_rank_distance"] < sensitivity["null_mean"] and
            sensitivity["p_lower"] <= SENSITIVITY_ALPHA and
            sensitivity["permutations_completed"] == PERMUTATIONS
        )
        stability_ok = stable_count >= STABLE_PAIR_COUNT_MIN and jitter_completed == JITTER_DRAWS
        status = "PASS" if primary_ok and sensitivity_ok and stability_ok else "FAIL"

        # Remove internal zero-based optimizer maps from public metrics; the explicit pair table is clearer.
        primary_public = {k: v for k, v in primary.items() if k != "assignment"}
        sensitivity_public = {k: v for k, v in sensitivity.items() if k != "assignment"}

        out.update({
            "stars": [{"star_id": s["star_id"], "x": s["x"], "y": s["y"]} for s in stars],
            "yale_boxes": boxes,
            "primary_top_left": primary_public,
            "sensitivity_bbox_center": sensitivity_public,
            "jitter": {
                "draws_completed": jitter_completed,
                "stable_pair_count": stable_count,
                "stable_pair_fraction": stable_count / 29.0,
                "median_pair_preservation_fraction": float(median(fractions)),
                "pairs": pair_rows,
            },
            "gates": {
                "primary_geometric_concordance": primary_ok,
                "bbox_center_sensitivity": sensitivity_ok,
                "pairing_jitter_stability": stability_ok,
            },
            "status": status,
        })

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
