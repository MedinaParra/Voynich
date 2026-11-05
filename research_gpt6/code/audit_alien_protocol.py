#!/usr/bin/env python3
"""Independent mathematical and witness audit of the frozen protocol diagnostic.

Imports no production modules. Verifies archived count certificates, normalized
probabilities, pair equality codes, source-unit reconstruction, split assignment,
reported statistics and the synthetic semantic counterexample. It does not
authenticate a manuscript, validate the IVTFF parser against photographs, rerun
the shuffle generator, or identify meanings or a historical writing mechanism.
"""
import argparse
from collections import Counter, defaultdict
from fractions import Fraction
import gzip
import hashlib
import json
import math
from pathlib import Path
import re


CELLS = 576
WIDTH = CELLS * 4
SEED = 20261105
TRAIN_NULLS = 8
TEST_NULLS = 199
GROUPS = ("cfh", "ckh", "cph", "cth", "ch", "sh")
GROUP_SYMBOLS = {s: chr(0xE100 + i) for i, s in enumerate(GROUPS)}
GROUP_PATTERN = re.compile("|".join(map(re.escape, GROUPS)) + r"|.", re.DOTALL)
REAL_CASES = tuple(a + "_" + b + "_" + c
                   for a in ("VT", "ZL") for b in ("split", "join")
                   for c in ("letters", "groups"))
CONTROL_CASES = tuple("control_" + c for c in ("iid", "iid_layout", "echo", "morphology"))


class Checks:
    def __init__(self):
        self.total = 0
        self.mismatches = []
        self.mismatch_count = 0

    def check(self, name, actual, expected=True):
        self.total += 1
        if actual != expected:
            self.mismatch_count += 1
            if len(self.mismatches) < 60:
                self.mismatches.append({"check": name, "actual": actual, "expected": expected})
            return False
        return True

    def close(self, name, actual, expected, tolerance=2e-11):
        valid = (type(actual) in (int, float) and math.isfinite(actual)
                 and abs(actual - expected) <= tolerance)
        return self.check(name, actual if not valid else True, True)


def safe(base, relative):
    p = Path(relative)
    if p.is_absolute() or ".." in p.parts:
        raise ValueError("Unsafe bundle-relative input")
    result = base / p
    if not result.resolve().is_relative_to(base.resolve()):
        raise ValueError("Input resolves outside bundle")
    return result


def read_json(path, hashes, key=None):
    raw = path.read_bytes()
    if key is not None:
        hashes[key] = hashlib.sha256(raw).hexdigest()
    return json.loads(raw)


def read_compressed_json(path, hashes, key):
    raw = path.read_bytes()
    hashes[key] = hashlib.sha256(raw).hexdigest()
    return json.loads(gzip.decompress(raw))


def units(raw, mode):
    if mode == "letters":
        return list(raw)
    if mode != "groups":
        raise ValueError("Unsupported unitization")
    return [GROUP_SYMBOLS.get(m.group(), m.group()) for m in GROUP_PATTERN.finditer(raw)]


def bin_length(n):
    for i, upper in enumerate((3, 5, 8)):
        if n <= upper:
            return i
    return 3


def canonical(a, b):
    inverse = list(dict.fromkeys(list(a) + list(b)))
    return [[inverse.index(x) for x in a], [inverse.index(x) for x in b]], inverse


def expected_context(a, b, position):
    value = bin_length(len(a))
    value = 4 * value + bin_length(len(b))
    value = 3 * value + min(2, len(a) - len(set(a)))
    value = 3 * value + min(2, len(b) - len(set(b)))
    return 4 * value + position


def split(leaf, seed):
    digest = hashlib.sha256((str(seed) + ":" + leaf).encode()).digest()
    return "test" if digest[0] % 5 == 0 else "train"


def witness_table(path, cid, mode, role, seed, checks, hashes):
    prefix = cid + "/" + role
    hashes[str(Path(cid) / path.name)] = hashlib.sha256(path.read_bytes()).hexdigest()
    counts = [0] * WIDTH
    leaves = set()
    lines = {}
    pair_count = 0
    with gzip.open(path, "rt", encoding="utf-8") as stream:
        for physical_number, text in enumerate(stream, 1):
            row = json.loads(text)
            a, b = units(row["left"], mode), units(row["right"], mode)
            position = int(row["word_index"] == 0) + 2 * int(row["word_index"] + 1 == row["line_words"] - 1)
            code, inverse = canonical(a, b)
            renamed, _ = canonical([2 * ord(x) + 1 for x in a], [2 * ord(x) + 1 for x in b])
            context = expected_context(a, b, position)
            category = min(3, len(set(a).intersection(b)))
            expected_leaf = (re.match(r"^f\d+", row["folio"]).group()
                             if cid in REAL_CASES else row["folio"][:-1])
            details = {
                "units_left": row["units_left"] == a,
                "units_right": row["units_right"] == b,
                "joint_code": row["code"] == code,
                "inverse": row["inverse"] == inverse,
                "global_renaming_invariance": renamed == code,
                "context": row["context"] == context,
                "category": row["category"] == category,
                "split": row["split"] == role == split(row["leaf"], seed),
                "leaf": row["leaf"] == expected_leaf,
                "position_bounds": type(row["word_index"]) is int and type(row["line_words"]) is int
                    and row["line_words"] >= 2 and 0 <= row["word_index"] < row["line_words"] - 1,
                "source_unit_reconstruction": "".join(GROUPS[ord(x) - 0xE100]
                    if 0xE100 <= ord(x) < 0xE100 + len(GROUPS) else x for x in a) == row["left"]
                    and "".join(GROUPS[ord(x) - 0xE100]
                    if 0xE100 <= ord(x) < 0xE100 + len(GROUPS) else x for x in b) == row["right"],
            }
            checks.check(prefix + "/witness/" + str(physical_number),
                         True if all(details.values()) else [k for k, v in details.items() if not v])
            if not (0 <= context < CELLS and 0 <= category < 4):
                raise ValueError("Computed witness category outside model")
            counts[4 * context + category] += 1
            leaves.add(row["leaf"])
            key = (row["id"], row["folio"], row["leaf"])
            if key not in lines:
                lines[key] = {"n": row["line_words"], "words": {}, "pairs": set()}
            line = lines[key]
            i = row["word_index"]
            consistent = line["n"] == row["line_words"] and i not in line["pairs"]
            for offset, raw in ((i, row["left"]), (i + 1, row["right"])):
                if offset in line["words"]:
                    consistent = consistent and line["words"][offset] == raw
                line["words"][offset] = raw
            line["pairs"].add(i)
            checks.check(prefix + "/chain/" + str(physical_number), consistent)
            pair_count += 1
    for key, line in lines.items():
        checks.check(prefix + "/complete_line/" + key[0],
                     line["pairs"] == set(range(line["n"] - 1))
                     and set(line["words"]) == set(range(line["n"])))
    slots = sum(line["n"] for line in lines.values())
    pools = defaultdict(list)
    for (_, folio, _), line in lines.items():
        for i in range(line["n"]):
            raw = line["words"][i]
            slot_position = "first" if i == 0 else "last" if i == line["n"] - 1 else "middle"
            pools[(folio, len(units(raw, mode)), slot_position)].append(raw)
    movable = sum(len(words) for words in pools.values() if len(set(words)) > 1)
    return counts, {"pairs": pair_count, "leaves": sorted(leaves), "lines": len(lines),
                    "slots": slots, "pools": len(pools), "slots_in_nonconstant_pools": movable}


def check_table(value, name, checks):
    valid = (isinstance(value, list) and len(value) == WIDTH
             and all(type(v) is int and v >= 0 for v in value))
    checks.check(name, valid)
    if not valid:
        raise ValueError("Malformed count table: " + name)
    return value


def model_weights(real, pooled, replicates, checks, prefix):
    base = [0] * WIDTH
    for base_cell in range(CELLS // 4):
        for category in range(4):
            total = sum(real[4 * (4 * base_cell + position) + category] for position in range(4))
            for position in range(4):
                base[4 * (4 * base_cell + position) + category] = total
    coupling, framing = [], []
    for cell in range(CELLS):
        real_cell, null_cell, base_cell = (table[4 * cell:4 * cell + 4] for table in (real, pooled, base))
        rp = [Fraction(2 * n + 1, 2 * sum(real_cell) + 4) for n in real_cell]
        np = [Fraction(2 * n + replicates, 2 * sum(null_cell) + 4 * replicates) for n in null_cell]
        bp = [Fraction(2 * n + 1, 2 * sum(base_cell) + 4) for n in base_cell]
        checks.check(prefix + "/exact_normalization/" + str(cell),
                     sum(rp) == sum(np) == sum(bp) == 1 and all(p > 0 for p in rp + np + bp))
        # Exact fractions establish the formula; conversion here reproduces the
        # declared IEEE-floating log-ratio evaluation, without importing it.
        coupling.extend(math.log2(float(a) / float(b)) for a, b in zip(rp, np))
        framing.extend(math.log2(float(a) / float(b)) for a, b in zip(rp, bp))
    return coupling, framing


def score(counts, weights):
    total = sum(counts)
    if total <= 0:
        raise ValueError("No scored pairs")
    return math.fsum(n * w for n, w in zip(counts, weights) if n) / total


def audit_case(bundle, row, seed, checks, hashes):
    cid = row["id"]
    folder = safe(bundle, cid)
    c = read_compressed_json(folder / "counts.json.gz", hashes, cid + "/counts.json.gz")
    checks.check(cid + "/schema", c.get("schema"), "alien-protocol-counts-v1")
    checks.check(cid + "/case_id", c.get("case_id"), cid)
    checks.check(cid + "/null_replicates", c.get("train_null_replicates"), TRAIN_NULLS)
    real = check_table(c["real_train"], cid + "/real_train_table", checks)
    pooled = check_table(c["null_train_pooled"], cid + "/pooled_table", checks)
    observed = check_table(c["real_test"], cid + "/test_table", checks)
    checks.check(cid + "/test_null_count", len(c["null_test"]), TEST_NULLS)
    for i, t in enumerate(c["null_test"]):
        check_table(t, cid + "/null_test_table/" + str(i), checks)
    mode = "groups" if cid.endswith("_groups") else "letters"
    checks.check(cid + "/unitization", row["units"], mode)
    actual_counts = {}
    partitions = {}
    for role in ("train", "test"):
        actual_counts[role], partitions[role] = witness_table(
            folder / (role + "_pairs.jsonl.gz"), cid, mode, role, seed, checks, hashes)
        checks.check(cid + "/" + role + "_witness_table", actual_counts[role], real if role == "train" else observed)
        checks.check(cid + "/" + role + "_leaves", partitions[role]["leaves"],
                     row["training_leaves"] if role == "train" else row["test_leaves"])
        checks.check(cid + "/" + role + "_pair_total", partitions[role]["pairs"],
                     row["training_pairs"] if role == "train" else row["test_pairs"])
        pool_name = "training_pools" if role == "train" else "test_pools"
        for key in ("slots", "pools", "slots_in_nonconstant_pools"):
            checks.check(cid + "/" + role + "/" + key, row[pool_name][key], partitions[role][key])
    checks.check(cid + "/leaf_disjointness", not (set(partitions["train"]["leaves"]) & set(partitions["test"]["leaves"])))
    checks.check(cid + "/line_count", partitions["train"]["lines"] + partitions["test"]["lines"], row["lines"])
    checks.check(cid + "/pooled_total", sum(pooled), TRAIN_NULLS * sum(real))
    for i, t in enumerate(c["null_test"]):
        checks.check(cid + "/null_total/" + str(i), sum(t), sum(observed))
    weights, framing = model_weights(real, pooled, TRAIN_NULLS, checks, cid)
    actual = score(observed, weights)
    frame_score = score(observed, framing)
    null_scores = [score(t, weights) for t in c["null_test"]]
    checks.close(cid + "/coupling_score", row["coupling_bits_per_pair"], actual)
    checks.close(cid + "/format_score", row["format_bits_per_pair"], frame_score)
    checks.check(cid + "/recorded_null_score_count", len(row["null_scores"]), TEST_NULLS)
    for i, (stored, calculated) in enumerate(zip(row["null_scores"], null_scores)):
        checks.close(cid + "/null_score/" + str(i), stored, calculated)
    exceed = sum(value >= actual for value in null_scores)
    tail = Fraction(1 + exceed, 1 + len(null_scores))
    checks.check(cid + "/tail_exceedances", row["null_exceedances"], exceed)
    checks.close(cid + "/tail", row["conditional_randomization_tail"], float(tail))
    positive = actual > 0 and tail <= Fraction(1, 20)
    checks.check(cid + "/positive_flag", row["positive"], positive)
    checks.check(cid + "/training_draws", row["training_null_replicates"], TRAIN_NULLS)
    checks.check(cid + "/test_draws", row["test_null_replicates"], TEST_NULLS)
    witnesses = sum(partitions[role]["pairs"] for role in partitions)
    checks.check(cid + "/witness_renaming_count", row["pair_reconstruction_and_global_renaming_checks"], witnesses)
    return {"witness_pairs": witnesses, "training_pairs": sum(real), "test_pairs": sum(observed),
            "exactly_normalized_cells": CELLS, "test_null_scores_checked": len(null_scores),
            "coupling_bits_per_pair": round(actual, 12), "format_bits_per_pair": round(frame_score, 12),
            "conditional_randomization_tail": float(tail), "positive": positive,
            "line_count": partitions["train"]["lines"] + partitions["test"]["lines"],
            "word_slots": partitions["train"]["slots"] + partitions["test"]["slots"]}


def audit_semantics(bundle, checks, hashes):
    s = read_json(bundle / "semantic_certificate.json", hashes, "semantic_certificate.json")
    checks.check("semantic/schema", s.get("schema"), "alien-protocol-semantic-certificate-v1")
    words = s["observed_words"]
    a, b = s["codebook_a"], s["codebook_b"]
    checks.check("semantic/same_cipher_vocabulary", set(a) == set(b) == set(words))
    checks.check("semantic/codebook_bijections", len(set(a.values())) == len(a) and len(set(b.values())) == len(b))
    ta = [a[word] for word in words]
    tb = [b[word] for word in words]
    checks.check("semantic/translations_recorded", [s["translation_a"], s["translation_b"]], [ta, tb])
    checks.check("semantic/all_meanings_differ", all(x != y for x, y in zip(ta, tb)))
    observed = ".".join(words)
    for label, mapping, translation in (("a", a, ta), ("b", b, tb)):
        inverse = {v: k for k, v in mapping.items()}
        recovered = [inverse[value] for value in translation]
        checks.check("semantic/roundtrip_" + label + "_words", s["roundtrip_" + label + "_words"], recovered)
        checks.check("semantic/roundtrip_" + label + "_text", s["roundtrip_" + label + "_text"], observed)
        checks.check("semantic/roundtrip_" + label + "_identity", recovered, words)
    checks.check("semantic/observed_text", s["observed_text"], observed)
    checks.check("semantic/same_text_flag", s["same_observed_text"], True)
    checks.check("semantic/different_meanings_flag", s["different_translations"], True)
    return {"observed_words": len(words), "two_bijective_codebooks_roundtrip_same_text": True,
            "all_observed_meaning_assignments_differ": ta != tb,
            "scope": "Synthetic observational equivalence only; no Voynich meanings identified"}


def audit(bundle):
    checks, hashes = Checks(), {}
    result = {"schema": "alien-protocol-audit-v1",
              "scope": "Independent archived-witness, count, probability and score checks. Not historical-source authentication, validation of source parsing against manuscript images, shuffle-generator replay, proof of isolated holdout, language identification, or semantic translation.",
              "production_modules_imported": False,
              "semantic_translation_validated": False,
              "expert_paleographic_accuracy_validated": False,
              "shuffle_permutations_independently_replayed": False}
    try:
        manifest = read_json(bundle / "file_manifest.json", hashes, "file_manifest.json")
        checks.check("manifest/schema", manifest.get("schema"), "alien-protocol-files-v1")
        entries = manifest["files"]
        checks.check("manifest/unique_paths", len({row["path"] for row in entries}), len(entries))
        required = {"result.json", "source_inventories.json", "semantic_certificate.json"}
        required.update(cid + "/" + name for cid in REAL_CASES + CONTROL_CASES
                        for name in ("counts.json.gz", "train_pairs.jsonl.gz", "test_pairs.jsonl.gz"))
        checks.check("manifest/required_calculation_inputs", required.issubset({row["path"] for row in entries}))
        for row in entries:
            p = safe(bundle, row["path"])
            raw = p.read_bytes()
            checks.check("manifest/" + row["path"],
                         len(raw) == row["bytes"] and hashlib.sha256(raw).hexdigest() == row["sha256"])
        report = read_json(bundle / "result.json", hashes, "result.json")
        checks.check("result/schema", report.get("schema"), "alien-protocol-result-v1")
        checks.check("result/seed", report["seed"], SEED)
        cases = {r["id"]: r for r in report["cases"]}
        checks.check("result/unique_cases", len(cases), len(report["cases"]))
        checks.check("result/case_set", sorted(cases), sorted(REAL_CASES + CONTROL_CASES))
        summaries = {}
        for cid in REAL_CASES + CONTROL_CASES:
            summaries[cid] = audit_case(bundle, cases[cid], report["seed"], checks, hashes)
        gate = (not summaries["control_iid"]["positive"] and not summaries["control_iid_layout"]["positive"]
                and summaries["control_echo"]["positive"])
        checks.check("result/control_gate", report["synthetic_control_gate"], "PASS" if gate else "FAIL")
        checks.check("result/eight_projection_flag", report["robust_across_all_eight_projections"],
                     all(summaries[cid]["positive"] for cid in REAL_CASES))
        checks.check("result/morphology_rival_flag", report["morphological_rival_positive"], summaries["control_morphology"]["positive"])
        checks.check("result/semantic_status", report["semantic_translation"], "NOT_IDENTIFIED")
        checks.check("result/no_Voynich_translation", report["Voynich_translation_validated"], False)
        checks.check("result/no_Kraken_training", report["Kraken_training"], "NOT_RUN")
        checks.check("result/no_novelty_claim", report["novelty_claimed"], False)
        inventories = read_json(bundle / "source_inventories.json", hashes, "source_inventories.json")
        checks.check("inventory/set", sorted(inventories), ["VT_join", "VT_split", "ZL_join", "ZL_split"])
        for key, inv in inventories.items():
            checks.check("inventory/" + key + "/exclusive_rejection_count",
                         sum(inv["rejected_by_reason"].values()), len(inv["rejected_rows"]))
            checks.check("inventory/" + key + "/record_accounting",
                         inv["accepted_lines"] + len(inv["rejected_rows"]), inv["logical_records"])
            for mode in ("letters", "groups"):
                cid = key + "_" + mode
                checks.check("inventory/" + cid + "/accepted_lines", inv["accepted_lines"], summaries[cid]["line_count"])
                checks.check("inventory/" + cid + "/accepted_words", inv["accepted_words"], summaries[cid]["word_slots"])
        result["cases"] = summaries
        result["semantic_certificate"] = audit_semantics(bundle, checks, hashes)
        result["counts"] = {"cases": len(summaries), "witness_pairs": sum(s["witness_pairs"] for s in summaries.values()),
                            "normalized_four_category_cells": CELLS * len(summaries),
                            "heldout_null_scores_recomputed": TEST_NULLS * len(summaries)}
        result["experimental_control_gate"] = report["synthetic_control_gate"]
    except (OSError, ValueError, TypeError, KeyError, IndexError, ZeroDivisionError, AttributeError) as exc:
        detail = str(exc).replace(str(bundle), "<bundle>")
        checks.check("audit/required_processing", type(exc).__name__ + ": " + detail, "all required inputs processed")
    result.update({"status": "PASS" if checks.mismatch_count == 0 else "FAIL", "checks": checks.total,
                   "mismatch_count": checks.mismatch_count, "mismatches": checks.mismatches,
                   "input_sha256": dict(sorted(hashes.items()))})
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.bundle.resolve())
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: result[k] for k in ("status", "checks", "mismatch_count")}, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
