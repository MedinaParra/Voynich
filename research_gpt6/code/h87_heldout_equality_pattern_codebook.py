#!/usr/bin/env python3
"""H87 preregistered leave-one-folio-out equality-pattern codebook recurrence."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import re
import statistics
from collections import Counter, defaultdict
from pathlib import Path

ZL_BLOB = "2a4533ab9bdfa85db9bad602d590978953055df1"
TAKAHASHI_BLOB = "7f491b574b65e5fba6b553e57372c3fa50e10fec"
PERMUTATIONS = 9_999
ALPHA_PER_ARM = 0.025
MIN_PAIRS = 60
MIN_FOLIOS = 8
ARM_CONFIG = {
    "ZL": {"pairing_seed": 20261024, "null_seed": 20261026},
    "Takahashi": {"pairing_seed": 20261025, "null_seed": 20261027},
}


def blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def clean_tokens(text: str) -> list[str]:
    clean = re.sub(r"<[^>]*>|\[[^]]*\]|\{[^}]*\}|@[0-9]+;", " ", text).replace("?", " ")
    return re.findall(r"(?<![a-z])[a-z]{2,}(?![a-z])", clean)


def generic_locus_type(pos: str) -> str | None:
    match = re.search(r"([PLCR])(?:[A-Za-z0-9]*)", pos)
    return match.group(1) if match else None


def canonical_pattern(token: str) -> tuple[int, ...]:
    mapping: dict[str, int] = {}
    out: list[int] = []
    for symbol in token:
        if symbol not in mapping:
            mapping[symbol] = len(mapping)
        out.append(mapping[symbol])
    return tuple(out)


def parse(raw: str) -> tuple[list[dict[str, object]], dict[tuple[str, str, str, int], list[dict[str, object]]]]:
    pages: dict[str, dict[str, str]] = {}
    labels: list[dict[str, object]] = []
    controls: dict[tuple[str, str, str, int], list[dict[str, object]]] = defaultdict(list)
    occurrence_id = 0
    for line in raw.splitlines():
        page = re.match(r"^<([^>.,]+)>\s*<!([^>]*)>", line)
        if page:
            metadata = dict(re.findall(r"\$([A-Z])=([^\s>]+)", page.group(2)))
            pages[page.group(1)] = {
                "currier": metadata.get("L", "?"),
                "hand": metadata.get("H", "?"),
            }
            continue
        record = re.match(r"^<([^>]+)>\s*(.*)$", line)
        if not record or "," not in record.group(1):
            continue
        locus, text = record.groups()
        folio = locus.split(".")[0]
        pos = locus.split(",", 1)[1]
        meta = pages.get(folio, {"currier": "?", "hand": "?"})
        tokens = clean_tokens(text)
        locus_type = generic_locus_type(pos)
        if locus_type == "L" and len(tokens) == 1 and "?" not in text:
            token = tokens[0]
            labels.append({
                "folio": folio,
                "token": token,
                "currier": meta["currier"],
                "hand": meta["hand"],
                "length": len(token),
                "pattern": canonical_pattern(token),
            })
        elif locus_type == "P":
            for token in tokens:
                occurrence_id += 1
                key = (folio, meta["currier"], meta["hand"], len(token))
                controls[key].append({
                    "occurrence_id": occurrence_id,
                    "folio": folio,
                    "token": token,
                    "currier": meta["currier"],
                    "hand": meta["hand"],
                    "length": len(token),
                    "pattern": canonical_pattern(token),
                })
    return labels, controls


def build_pairs(
    labels: list[dict[str, object]],
    controls: dict[tuple[str, str, str, int], list[dict[str, object]]],
    seed: int,
) -> tuple[list[dict[str, object]], int]:
    rng = random.Random(seed)
    pools: dict[tuple[str, str, str, int], list[dict[str, object]]] = {}
    for key in sorted(controls):
        pool = list(controls[key])
        rng.shuffle(pool)
        pools[key] = pool
    cursors: dict[tuple[str, str, str, int], int] = defaultdict(int)
    pairs: list[dict[str, object]] = []
    excluded = 0
    for label in sorted(labels, key=lambda row: (str(row["folio"]), str(row["token"]), str(row["currier"]), str(row["hand"]))):
        key = (str(label["folio"]), str(label["currier"]), str(label["hand"]), int(label["length"]))
        pool = pools.get(key, [])
        cursor = cursors[key]
        if cursor >= len(pool):
            excluded += 1
            continue
        control = pool[cursor]
        cursors[key] = cursor + 1
        pairs.append({
            "folio": label["folio"],
            "length": label["length"],
            "label_pattern": label["pattern"],
            "control_pattern": control["pattern"],
            "label_token": label["token"],
            "control_token": control["token"],
            "control_occurrence_id": control["occurrence_id"],
        })
    return pairs, excluded


def pattern_key(pattern: tuple[int, ...]) -> str:
    return "-".join(str(value) for value in pattern)


def run_arm(name: str, raw: bytes) -> dict[str, object]:
    config = ARM_CONFIG[name]
    labels, controls = parse(raw.decode("utf-8", errors="strict"))
    pairs, excluded_no_control = build_pairs(labels, controls, int(config["pairing_seed"]))
    control_occurrence_ids = [int(pair["control_occurrence_id"]) for pair in pairs]
    matched_folios = sorted({str(pair["folio"]) for pair in pairs})
    initial_gates = {
        "matched_pairs_at_least_60": len(pairs) >= MIN_PAIRS,
        "represented_folios_at_least_8": len(matched_folios) >= MIN_FOLIOS,
        "controls_without_replacement": len(control_occurrence_ids) == len(set(control_occurrence_ids)),
    }
    result: dict[str, object] = {
        "eligible_label_tokens": len(labels),
        "P_token_occurrences": sum(len(values) for values in controls.values()),
        "matched_pairs_before_codebook_gate": len(pairs),
        "represented_folios_before_codebook_gate": len(matched_folios),
        "excluded_labels_no_unused_exact_control": excluded_no_control,
        "pairing_seed": config["pairing_seed"],
        "null_seed": config["null_seed"],
        "initial_sample_gates": initial_gates,
    }
    if not all(initial_gates.values()):
        result.update({"status": "BLOCKED", "reason": "preregistered without-replacement matching/sample gate failed"})
        return result

    pairs_by_folio: dict[str, list[dict[str, object]]] = defaultdict(list)
    for pair in pairs:
        pairs_by_folio[str(pair["folio"])].append(pair)

    evaluated: list[dict[str, object]] = []
    excluded_no_training_length = 0
    folio_deltas: dict[str, list[float]] = defaultdict(list)
    label_scores: list[float] = []
    control_scores: list[float] = []
    label_seen: list[bool] = []
    control_seen: list[bool] = []

    # The training distribution is pooled and unlabelled: both L and P members from all non-held-out folios.
    for heldout in sorted(pairs_by_folio):
        codebook: dict[int, Counter[tuple[int, ...]]] = defaultdict(Counter)
        for training_folio, training_pairs in pairs_by_folio.items():
            if training_folio == heldout:
                continue
            for pair in training_pairs:
                length = int(pair["length"])
                codebook[length][tuple(pair["label_pattern"])] += 1  # type: ignore[arg-type]
                codebook[length][tuple(pair["control_pattern"])] += 1  # type: ignore[arg-type]
        for pair in pairs_by_folio[heldout]:
            length = int(pair["length"])
            if not codebook.get(length):
                excluded_no_training_length += 1
                continue
            label_pattern = tuple(pair["label_pattern"])  # type: ignore[arg-type]
            control_pattern = tuple(pair["control_pattern"])  # type: ignore[arg-type]
            label_count = codebook[length][label_pattern]
            control_count = codebook[length][control_pattern]
            r_label = math.log1p(label_count)
            r_control = math.log1p(control_count)
            delta = r_label - r_control
            evaluated.append({
                "folio": heldout,
                "length": length,
                "label_pattern": label_pattern,
                "control_pattern": control_pattern,
                "label_score": r_label,
                "control_score": r_control,
                "delta": delta,
                "label_seen": label_count > 0,
                "control_seen": control_count > 0,
            })
            folio_deltas[heldout].append(delta)
            label_scores.append(r_label)
            control_scores.append(r_control)
            label_seen.append(label_count > 0)
            control_seen.append(control_count > 0)

    evaluable_folios = sorted(folio_deltas)
    evaluable_gates = {
        "evaluable_pairs_at_least_60": len(evaluated) >= MIN_PAIRS,
        "evaluable_folios_at_least_8": len(evaluable_folios) >= MIN_FOLIOS,
    }
    result.update({
        "excluded_pairs_no_same_length_training_codebook": excluded_no_training_length,
        "evaluable_pairs": len(evaluated),
        "evaluable_folios": len(evaluable_folios),
        "evaluable_sample_gates": evaluable_gates,
    })
    if not all(evaluable_gates.values()):
        result.update({"status": "BLOCKED", "reason": "preregistered leave-one-folio-out codebook sample gate failed"})
        return result

    delta_by_folio = {folio: statistics.mean(values) for folio, values in sorted(folio_deltas.items())}
    observed_delta = statistics.mean(delta_by_folio.values())

    rng = random.Random(int(config["null_seed"]))
    folio_values = list(delta_by_folio.values())
    null: list[float] = []
    for _ in range(PERMUTATIONS):
        null.append(statistics.mean(value if rng.getrandbits(1) else -value for value in folio_values))
    p_upper = (1 + sum(value >= observed_delta for value in null)) / (PERMUTATIONS + 1)

    by_length: dict[int, list[dict[str, object]]] = defaultdict(list)
    for row in evaluated:
        by_length[int(row["length"])].append(row)
    length_diagnostics: dict[str, object] = {}
    for length in sorted(by_length):
        rows = by_length[length]
        if len(rows) < 20:
            continue
        length_diagnostics[str(length)] = {
            "pairs": len(rows),
            "mean_label_score": statistics.mean(float(row["label_score"]) for row in rows),
            "mean_control_score": statistics.mean(float(row["control_score"]) for row in rows),
            "mean_pair_delta": statistics.mean(float(row["delta"]) for row in rows),
        }

    unique_label_patterns = {tuple(row["label_pattern"]) for row in evaluated}  # type: ignore[arg-type]
    unique_control_patterns = {tuple(row["control_pattern"]) for row in evaluated}  # type: ignore[arg-type]
    result.update({
        "observed": {
            "Delta_equal_folio_mean": observed_delta,
            "label_mean_recurrence_score": statistics.mean(label_scores),
            "control_mean_recurrence_score": statistics.mean(control_scores),
            "label_median_recurrence_score": statistics.median(label_scores),
            "control_median_recurrence_score": statistics.median(control_scores),
            "label_seen_pattern_fraction": sum(label_seen) / len(label_seen),
            "control_seen_pattern_fraction": sum(control_seen) / len(control_seen),
            "unique_label_patterns": len(unique_label_patterns),
            "unique_control_patterns": len(unique_control_patterns),
            "by_folio_Delta": delta_by_folio,
            "fraction_folios_Delta_positive": sum(value > 0 for value in delta_by_folio.values()) / len(delta_by_folio),
            "by_length_descriptive": length_diagnostics,
        },
        "null": {
            "permutations_requested": PERMUTATIONS,
            "permutations_completed": len(null),
            "null_mean_Delta": statistics.mean(null),
            "null_sd_Delta": statistics.pstdev(null),
            "p_upper": p_upper,
        },
    })
    complete = len(null) == PERMUTATIONS
    gates = {
        "Delta_positive": observed_delta > 0,
        "p_upper_at_most_0_025": p_upper <= ALPHA_PER_ARM,
        "permutations_complete": complete,
    }
    result["scientific_gates"] = gates
    if not complete:
        result.update({"status": "BLOCKED", "reason": "preregistered permutation-completion gate failed"})
    elif observed_delta > 0 and p_upper <= ALPHA_PER_ARM:
        result["status"] = "PASS"
    else:
        result["status"] = "FAIL"
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--zl", type=Path, required=True)
    parser.add_argument("--takahashi", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    zl = args.zl.read_bytes()
    takahashi = args.takahashi.read_bytes()
    observed_blobs = {"ZL": blob_sha(zl), "Takahashi": blob_sha(takahashi)}
    expected_blobs = {"ZL": ZL_BLOB, "Takahashi": TAKAHASHI_BLOB}
    output: dict[str, object] = {
        "classification": "HELDOUT_EQUALITY_PATTERN_CODEBOOK_RECURRENCE_NOT_SEMANTICS",
        "source_blobs": observed_blobs,
        "expected_blobs": expected_blobs,
        "familywise_alpha": 0.05,
        "alpha_per_arm": ALPHA_PER_ARM,
        "permutations_per_arm": PERMUTATIONS,
        "codebook": "leave_one_folio_out pooled unlabeled L+P exact canonical equality patterns conditioned on token length",
        "matching": "without replacement within exact folio+Currier+hand+length stratum",
    }
    mismatch = [name for name in expected_blobs if observed_blobs[name] != expected_blobs[name]]
    if mismatch:
        output.update({"status": "BLOCKED", "reason": "frozen source blob mismatch", "mismatched_sources": mismatch})
    else:
        arms = {"ZL": run_arm("ZL", zl), "Takahashi": run_arm("Takahashi", takahashi)}
        output["arms"] = arms
        statuses = [str(arms[name]["status"]) for name in ("ZL", "Takahashi")]
        if "BLOCKED" in statuses:
            output.update({"status": "BLOCKED", "reason": "at least one preregistered corpus arm is blocked"})
        elif statuses == ["PASS", "PASS"]:
            output["status"] = "PASS"
        else:
            output["status"] = "FAIL"

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
