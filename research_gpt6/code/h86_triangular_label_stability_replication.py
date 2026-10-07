#!/usr/bin/env python3
"""H86 preregistered triangular replication of inverse label stability."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Sequence

ZL_BLOB_SHA1 = "2a4533ab9bdfa85db9bad602d590978953055df1"
IT_SHA256 = "db624a731114f26854bbfe3a59d40827fa8911be46d086b6c558d99e557241ee"
GC_SHA256 = "b09570cb6c993bc2d87134d115e60a978650a8a6495483ddbb1f6005a586096f"
PERMUTATIONS = 9_999
MIN_PAIRS = 60
MIN_FOLIOS = 8
ALPHA_PER_ARM = 0.025
ARM_CONFIG = {
    "ZL_IT": {"pairing_seed": 20261020, "null_seed": 20261021},
    "ZL_GC": {"pairing_seed": 20261022, "null_seed": 20261023},
}


def git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def clean_tokens(payload: str) -> list[str]:
    # Preserve explicit layout breaks as token boundaries before dropping markup.
    text = payload.replace("<->", " ")
    text = re.sub(r"<[^>]*>", " ", text)
    text = re.sub(r"\[[^]]*\]", " ", text)
    text = re.sub(r"\{[^}]*\}", " ", text)
    text = re.sub(r"@[0-9]+;", " ", text)
    out: list[str] = []
    for piece in re.split(r"[.,\s]+", text):
        piece = piece.strip()
        if not piece or "?" in piece:
            continue
        if re.fullmatch(r"[A-Za-z]{2,}", piece):
            out.append(piece.lower())
    return out


def parse_records(data: bytes) -> dict[tuple[str, int], dict[str, object]]:
    records: dict[tuple[str, int], dict[str, object]] = {}
    for line in data.decode("utf-8", errors="strict").splitlines():
        match = re.match(r"^<(f\d+[rv]\d*)\.(\d+),([^>]+)>\s*(.*)$", line)
        if not match:
            continue
        folio, number, locator, payload = match.groups()
        records[(folio, int(number))] = {
            "folio": folio,
            "number": int(number),
            "locator": locator,
            "tokens": clean_tokens(payload),
        }
    return records


def generic_type(locator: str) -> str | None:
    loc = re.sub(r"^[@+*=]", "", locator.strip())
    if loc.startswith("L"):
        return "L"
    if loc.startswith("P"):
        return "P"
    return None


def pattern(token: str) -> tuple[int, ...]:
    mapping: dict[str, int] = {}
    result: list[int] = []
    for symbol in token:
        if symbol not in mapping:
            mapping[symbol] = len(mapping)
        result.append(mapping[symbol])
    return tuple(result)


def levenshtein(a: Sequence[int], b: Sequence[int]) -> int:
    previous = list(range(len(b) + 1))
    for i, left in enumerate(a, 1):
        current = [i]
        for j, right in enumerate(b, 1):
            current.append(min(current[-1] + 1, previous[j] + 1, previous[j - 1] + (left != right)))
        previous = current
    return previous[-1]


def disagreement(left: str, right: str) -> float:
    a, b = pattern(left), pattern(right)
    return levenshtein(a, b) / max(len(a), len(b), 1)


def run_arm(
    arm_name: str,
    zl_records: dict[tuple[str, int], dict[str, object]],
    other_records: dict[tuple[str, int], dict[str, object]],
) -> dict[str, object]:
    config = ARM_CONFIG[arm_name]
    labels: list[dict[str, object]] = []
    controls: list[dict[str, object]] = []
    p_exact = 0
    p_nonempty = 0
    p_equal_count = 0
    p_size_distribution: Counter[int] = Counter()

    for key, zl in zl_records.items():
        kind = generic_type(str(zl["locator"]))
        if kind not in {"L", "P"}:
            continue
        other = other_records.get(key)
        if other is None:
            continue
        ztokens = list(zl["tokens"])  # type: ignore[arg-type]
        otokens = list(other["tokens"])  # type: ignore[arg-type]
        if kind == "L":
            if len(ztokens) == 1 and len(otokens) == 1:
                ztok, otok = str(ztokens[0]), str(otokens[0])
                labels.append({
                    "folio": key[0], "number": key[1], "zl_token": ztok, "other_token": otok,
                    "zl_length": len(ztok), "other_length": len(otok), "D": disagreement(ztok, otok),
                })
            continue

        p_exact += 1
        if not ztokens or not otokens:
            continue
        p_nonempty += 1
        if len(ztokens) != len(otokens):
            continue
        p_equal_count += 1
        p_size_distribution[len(ztokens)] += 1
        for ordinal, (zraw, oraw) in enumerate(zip(ztokens, otokens), 1):
            ztok, otok = str(zraw), str(oraw)
            controls.append({
                "folio": key[0], "number": key[1], "record_key": key, "ordinal": ordinal,
                "zl_token": ztok, "other_token": otok, "zl_length": len(ztok),
                "other_length": len(otok), "D": disagreement(ztok, otok),
            })

    pools: dict[tuple[str, int], list[dict[str, object]]] = defaultdict(list)
    for row in controls:
        pools[(str(row["folio"]), int(row["zl_length"]))].append(row)
    pairing_rng = random.Random(int(config["pairing_seed"]))
    for stratum in sorted(pools):
        pools[stratum].sort(key=lambda row: (int(row["number"]), int(row["ordinal"])))
        pairing_rng.shuffle(pools[stratum])

    cursors: dict[tuple[str, int], int] = defaultdict(int)
    used_records: set[tuple[str, int]] = set()
    pairs: list[dict[str, object]] = []
    unmatched = 0
    for label in sorted(labels, key=lambda row: (str(row["folio"]), int(row["number"]))):
        stratum = (str(label["folio"]), int(label["zl_length"]))
        candidates = pools.get(stratum, [])
        cursor = cursors[stratum]
        chosen = None
        while cursor < len(candidates):
            candidate = candidates[cursor]
            cursor += 1
            record_key = candidate["record_key"]
            if record_key in used_records:
                continue
            chosen = candidate
            used_records.add(record_key)  # type: ignore[arg-type]
            break
        cursors[stratum] = cursor
        if chosen is None:
            unmatched += 1
            continue
        pairs.append({
            "folio": label["folio"], "zl_length": label["zl_length"],
            "label_number": label["number"], "paragraph_number": chosen["number"],
            "paragraph_ordinal": chosen["ordinal"], "label_D": label["D"],
            "paragraph_D": chosen["D"], "delta": float(label["D"]) - float(chosen["D"]),
            "label_other_length": label["other_length"],
            "paragraph_other_length": chosen["other_length"],
            "label_abs_length_difference": abs(int(label["zl_length"]) - int(label["other_length"])),
            "paragraph_abs_length_difference": abs(int(chosen["zl_length"]) - int(chosen["other_length"])),
        })

    folios = sorted({str(pair["folio"]) for pair in pairs})
    sample_gates = {
        "matched_pairs_at_least_60": len(pairs) >= MIN_PAIRS,
        "represented_folios_at_least_8": len(folios) >= MIN_FOLIOS,
        "distinct_P_records_equals_pair_count": len(used_records) == len(pairs),
    }
    result: dict[str, object] = {
        "coverage": {
            "label_single_token_mappable": len(labels),
            "label_folios": len({str(row["folio"]) for row in labels}),
            "P_exact_records_present_in_both": p_exact,
            "P_records_nonempty_in_both": p_nonempty,
            "P_records_equal_known_token_count": p_equal_count,
            "P_ordinal_token_candidates": len(controls),
            "P_equal_token_count_record_size_distribution": {str(k): v for k, v in sorted(p_size_distribution.items())},
        },
        "matching": {
            "matched_pairs": len(pairs), "represented_folios": len(folios), "folio_ids": folios,
            "distinct_P_records_used": len(used_records), "unmatched_labels_no_unused_record_control": unmatched,
            "sample_gates": sample_gates,
        },
        "parameters": config,
    }
    if not all(sample_gates.values()):
        result.update({"status": "BLOCKED", "reason": "preregistered arm sample gate failed"})
        return result

    label_d = [float(pair["label_D"]) for pair in pairs]
    paragraph_d = [float(pair["paragraph_D"]) for pair in pairs]
    deltas = [float(pair["delta"]) for pair in pairs]
    observed = statistics.mean(deltas)
    by_folio: dict[str, list[float]] = defaultdict(list)
    for pair in pairs:
        by_folio[str(pair["folio"])].append(float(pair["delta"]))
    result["observed"] = {
        "label_mean_D": statistics.mean(label_d), "label_median_D": statistics.median(label_d),
        "paragraph_mean_D": statistics.mean(paragraph_d), "paragraph_median_D": statistics.median(paragraph_d),
        "Delta": observed,
        "label_exact_pattern_agreement_fraction": sum(value == 0 for value in label_d) / len(label_d),
        "paragraph_exact_pattern_agreement_fraction": sum(value == 0 for value in paragraph_d) / len(paragraph_d),
        "by_folio_mean_delta": {folio: statistics.mean(values) for folio, values in sorted(by_folio.items())},
    }

    null_rng = random.Random(int(config["null_seed"]))
    null: list[float] = []
    for _ in range(PERMUTATIONS):
        null.append(statistics.mean(delta if null_rng.getrandbits(1) else -delta for delta in deltas))
    p_lower = (1 + sum(value <= observed for value in null)) / (PERMUTATIONS + 1)
    result["null"] = {
        "permutations_requested": PERMUTATIONS, "permutations_completed": len(null),
        "null_mean_Delta": statistics.mean(null), "null_sd_Delta": statistics.pstdev(null),
        "p_lower": p_lower,
    }

    label_len = [int(pair["label_abs_length_difference"]) for pair in pairs]
    paragraph_len = [int(pair["paragraph_abs_length_difference"]) for pair in pairs]
    result["diagnostics"] = {
        "label_mean_absolute_length_difference": statistics.mean(label_len),
        "paragraph_mean_absolute_length_difference": statistics.mean(paragraph_len),
        "label_equal_length_fraction": sum(value == 0 for value in label_len) / len(label_len),
        "paragraph_equal_length_fraction": sum(value == 0 for value in paragraph_len) / len(paragraph_len),
    }
    sensitivity = [
        pair for pair in pairs
        if int(pair["zl_length"]) == int(pair["label_other_length"])
        and int(pair["zl_length"]) == int(pair["paragraph_other_length"])
    ]
    sensitivity_folios = {str(pair["folio"]) for pair in sensitivity}
    if len(sensitivity) >= 30 and len(sensitivity_folios) >= 6:
        result["equal_source_length_sensitivity"] = {
            "status": "RUN_DESCRIPTIVE_ONLY", "pairs": len(sensitivity), "folios": len(sensitivity_folios),
            "label_mean_D": statistics.mean(float(pair["label_D"]) for pair in sensitivity),
            "paragraph_mean_D": statistics.mean(float(pair["paragraph_D"]) for pair in sensitivity),
            "Delta": statistics.mean(float(pair["delta"]) for pair in sensitivity),
        }
    else:
        result["equal_source_length_sensitivity"] = {
            "status": "NOT_RUN_INSUFFICIENT_SAMPLE", "pairs": len(sensitivity),
            "folios": len(sensitivity_folios), "required_pairs": 30, "required_folios": 6,
        }

    complete = len(null) == PERMUTATIONS
    gates = {"Delta_negative": observed < 0, "p_lower_at_most_0_025": p_lower <= ALPHA_PER_ARM, "permutations_complete": complete}
    result["scientific_gates"] = gates
    if not complete:
        result.update({"status": "BLOCKED", "reason": "permutation-completion gate failed"})
    elif observed < 0 and p_lower <= ALPHA_PER_ARM:
        result["status"] = "PASS"
    else:
        result["status"] = "FAIL"
    return result


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--zl", type=Path, required=True)
    ap.add_argument("--it", type=Path, required=True)
    ap.add_argument("--gc", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    raw_zl, raw_it, raw_gc = args.zl.read_bytes(), args.it.read_bytes(), args.gc.read_bytes()
    hashes = {"ZL_blob_sha1": git_blob_sha1(raw_zl), "IT_sha256": sha256(raw_it), "GC_sha256": sha256(raw_gc)}
    expected = {"ZL_blob_sha1": ZL_BLOB_SHA1, "IT_sha256": IT_SHA256, "GC_sha256": GC_SHA256}
    out: dict[str, object] = {
        "classification": "TRIANGULAR_LABEL_STABILITY_REPLICATION_NOT_SEMANTICS",
        "source_hashes": hashes, "expected_hashes": expected,
        "familywise_alpha": 0.05, "alpha_per_arm": ALPHA_PER_ARM,
        "permutations_per_arm": PERMUTATIONS,
    }
    mismatched = [key for key in expected if hashes[key] != expected[key]]
    if mismatched:
        out.update({"status": "BLOCKED", "reason": "frozen source hash mismatch", "mismatched_sources": mismatched})
    else:
        zl_records = parse_records(raw_zl)
        it_records = parse_records(raw_it)
        gc_records = parse_records(raw_gc)
        arms = {
            "ZL_IT": run_arm("ZL_IT", zl_records, it_records),
            "ZL_GC": run_arm("ZL_GC", zl_records, gc_records),
        }
        out["arms"] = arms
        statuses = [str(arms[name]["status"]) for name in ("ZL_IT", "ZL_GC")]
        if "BLOCKED" in statuses:
            out["status"] = "BLOCKED"
            out["reason"] = "at least one preregistered arm is blocked"
        elif statuses == ["PASS", "PASS"]:
            out["status"] = "PASS"
        else:
            out["status"] = "FAIL"

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
