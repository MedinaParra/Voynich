#!/usr/bin/env python3
"""H89 preregistered f68r2 border-ring geometry admissibility test."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from pathlib import Path

EXPECTED_BLOB = "e9733f16dc18b32ab5643c6d08a11f395c49a9c1"
EPS = 1e-9
SMALL_IDS = {
    "HOBJ_f68r2_9B165406AD77",
    "HOBJ_f68r2_EBC81EC14071",
    "HOBJ_f68r2_222319BDB3B7",
    "HOBJ_f68r2_3A47CFE17F40",
    "HOBJ_f68r2_1CF5F57F6301",
    "HOBJ_f68r2_11B515BAA47C",
    "HOBJ_f68r2_F78E01F368AC",
    "HOBJ_f68r2_665E5F11C7FC",
    "HOBJ_f68r2_FDEE7796EE6E",
    "HOBJ_f68r2_07C6E78D42DD",
    "HOBJ_f68r2_FD6FEE3E56A4",
    "HOBJ_f68r2_65E2D78262E2",
    "HOBJ_f68r2_50D2198107DB",
    "HOBJ_f68r2_A4F4A1C7116A",
    "HOBJ_f68r2_9C5B596B5265",
    "HOBJ_f68r2_6D595B71AAAC",
    "HOBJ_f68r2_34D8D73B52BB",
    "HOBJ_f68r2_4C62BFF7A717",
    "HOBJ_f68r2_0BCC383185CE",
    "HOBJ_f68r2_90CEDA9618ED",
    "HOBJ_f68r2_7437D0A5A09A",
    "HOBJ_f68r2_7A528C1AAC25",
    "HOBJ_f68r2_CA59FCCC6F79",
    "HOBJ_f68r2_25982A4DBF9C",
}


def git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def parse_stars(data: bytes) -> tuple[dict[str, tuple[float, float]], list[str]]:
    rows = csv.DictReader(io.StringIO(data.decode("utf-8-sig", errors="strict")), delimiter="\t")
    stars: dict[str, tuple[float, float]] = {}
    errors: list[str] = []
    for row in rows:
        cid = row.get("canonical_id", "")
        if row.get("panel") != "f68r2" or row.get("object_type") != "STAR":
            continue
        if row.get("geometry_type") != "BOX" or row.get("layer") != "STAR_REFERENCE":
            continue
        if not (cid.startswith("HOBJ_f68r2_") or cid.startswith("HNEW_STAR_f68r2_")):
            continue
        if cid in stars:
            errors.append(f"duplicate star id: {cid}")
            continue
        try:
            x1 = float(row["bbox_x1"]); y1 = float(row["bbox_y1"])
            x2 = float(row["bbox_x2"]); y2 = float(row["bbox_y2"])
        except (KeyError, TypeError, ValueError) as exc:
            errors.append(f"invalid box {cid}: {exc}")
            continue
        if not (x2 > x1 and y2 > y1):
            errors.append(f"non-positive box {cid}")
            continue
        stars[cid] = ((x1 + x2) / 2.0, (y1 + y2) / 2.0)
    return stars, errors


def cross(o, a, b) -> float:
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def convex_hull(points: list[tuple[float, float, str]]) -> list[tuple[float, float, str]]:
    pts = sorted(points, key=lambda p: (p[0], p[1], p[2]))
    if len(pts) < 3:
        return pts
    lower: list[tuple[float, float, str]] = []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= EPS:
            lower.pop()
        lower.append(p)
    upper: list[tuple[float, float, str]] = []
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= EPS:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


def inside_or_on_convex(point: tuple[float, float], hull: list[tuple[float, float, str]]) -> bool:
    if len(hull) < 3:
        return False
    p = (point[0], point[1], "")
    # Andrew hull is counter-clockwise; boundary is inside.
    for i, a in enumerate(hull):
        b = hull[(i + 1) % len(hull)]
        if cross(a, b, p) < -EPS:
            return False
    return True


def polygon_area(hull: list[tuple[float, float, str]]) -> float:
    if len(hull) < 3:
        return 0.0
    s = 0.0
    for i, p in enumerate(hull):
        q = hull[(i + 1) % len(hull)]
        s += p[0] * q[1] - q[0] * p[1]
    return abs(s) / 2.0


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--endpoints", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    data = args.endpoints.read_bytes()
    blob = git_blob_sha1(data)
    out: dict[str, object] = {
        "classification": "F68R2_BORDER_RING_GEOMETRY_ADMISSIBILITY_NOT_SEMANTICS",
        "source_blob": blob,
        "expected_blob": EXPECTED_BLOB,
        "frozen_small_id_count": len(SMALL_IDS),
        "numerical_tolerance": EPS,
    }
    if blob != EXPECTED_BLOB:
        out.update({"status": "BLOCKED", "reason": "frozen source blob mismatch"})
    else:
        stars, errors = parse_stars(data)
        missing_small = sorted(SMALL_IDS - set(stars))
        large_ids = set(stars) - SMALL_IDS
        gates = {
            "parse_errors_empty": not errors,
            "exactly_59_stars": len(stars) == 59,
            "all_24_small_ids_present": not missing_small and len(SMALL_IDS) == 24,
            "large_complement_exactly_35": len(large_ids) == 35,
        }
        out.update({
            "inventory": {
                "star_count": len(stars),
                "parse_errors": errors,
                "missing_small_ids": missing_small,
                "large_count": len(large_ids),
            },
            "inventory_gates": gates,
        })
        if not all(gates.values()):
            out.update({"status": "BLOCKED", "reason": "inventory gate failed"})
        else:
            large_hull = convex_hull([(stars[s][0], stars[s][1], s) for s in large_ids])
            if len(large_hull) < 3 or polygon_area(large_hull) <= 0:
                out.update({"status": "BLOCKED", "reason": "invalid 35-large convex hull"})
            else:
                inside_small = sorted(s for s in SMALL_IDS if inside_or_on_convex(stars[s], large_hull))
                out["large_hull"] = {
                    "vertex_count": len(large_hull),
                    "vertex_ids": [p[2] for p in large_hull],
                    "polygon_area": polygon_area(large_hull),
                }
                out["small_inside_or_on_large_hull"] = {
                    "count": len(inside_small),
                    "ids": inside_small,
                }
                if len(inside_small) != 1:
                    out.update({
                        "status": "FAIL_ADMISSIBILITY",
                        "reason": "preregistered unique small-interior candidate condition failed",
                    })
                else:
                    candidate = inside_small[0]
                    border_ids = sorted(SMALL_IDS - {candidate})
                    interior_ids = sorted(large_ids | {candidate})
                    border_hull = convex_hull([(stars[s][0], stars[s][1], s) for s in border_ids])
                    if len(border_hull) < 3 or polygon_area(border_hull) <= 0:
                        out.update({"status": "BLOCKED", "reason": "invalid 23-border convex hull"})
                    else:
                        outside_interior = sorted(s for s in interior_ids if not inside_or_on_convex(stars[s], border_hull))
                        out.update({
                            "small_interior_candidate": candidate,
                            "proposed_border_ids": border_ids,
                            "proposed_interior_ids": interior_ids,
                            "border_hull": {
                                "vertex_count": len(border_hull),
                                "vertex_ids": [p[2] for p in border_hull],
                                "polygon_area": polygon_area(border_hull),
                            },
                            "interior_containment": {
                                "contained_count": 36 - len(outside_interior),
                                "outside_ids": outside_interior,
                            },
                            "status": "PASS_ADMISSIBILITY" if not outside_interior else "FAIL_ADMISSIBILITY",
                        })
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
