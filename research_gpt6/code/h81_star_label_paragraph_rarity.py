#!/usr/bin/env python3
import argparse
import hashlib
import json
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean, median, pstdev

ZL_BLOB = "2a4533ab9bdfa85db9bad602d590978953055df1"
TAK_BLOB = "7f491b574b65e5fba6b553e57372c3fa50e10fec"
PERMUTATIONS = 9999
ALPHA = 0.025
SEEDS = {"ZL": 20261012, "Takahashi_IT2a": 20261013}
TARGETS_BY_LENGTH = {
    4: ["otys", "olor", "otol", "otor"],
    5: ["otydy", "okeor", "ockhy", "ocphy"],
    6: ["okoaly", "octhey", "otcsey", "otcsdo", "oiinar", "okoldy", "ykchdy", "okshor"],
    7: ["okodaly", "chocphy", "ytchody", "otykchs", "ofcheor", "ordaiin"],
    8: ["otcheody", "cphocthy", "otochedy", "okeeodal", "dolchedy"],
}
TARGETS = [t for k in sorted(TARGETS_BY_LENGTH) for t in TARGETS_BY_LENGTH[k]]


def git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def clean_tokens(text: str):
    clean = re.sub(r"<[^>]*>|\[[^]]*\]|\{[^}]*\}|@[0-9]+;", " ", text)
    clean = clean.replace("?", " ")
    return re.findall(r"(?<![a-z])[a-z]{2,}(?![a-z])", clean.lower())


def locus_type(locator: str):
    loc = re.sub(r"^[@+*=]", "", locator.strip())
    m = re.match(r"([A-Za-z])", loc)
    return m.group(1).upper() if m else None


def parse_source(raw: str):
    pages = {}
    all_tokens = Counter()
    p_tokens = Counter()
    labels = []

    for line in raw.splitlines():
        ph = re.match(r"^<([^>.,]+)>\s*<!([^>]*)>", line)
        if ph:
            meta = dict(re.findall(r"\$([A-Z])=([^\s>]+)", ph.group(2)))
            pages[ph.group(1)] = {
                "Q": meta.get("Q", "?"),
                "L": meta.get("L", "?"),
                "H": meta.get("H", "?"),
            }
            continue

        m = re.match(r"^<([^>]+)>\s*(.*)$", line)
        if not m or "," not in m.group(1):
            continue
        locus, text = m.groups()
        folio = locus.split(".")[0]
        locator = locus.split(",", 1)[1]
        typ = locus_type(locator)
        toks = clean_tokens(text)
        all_tokens.update(toks)

        if typ == "P":
            p_tokens.update(toks)
        elif typ == "L":
            if "?" in text or len(toks) != 1:
                continue
            meta = pages.get(folio, {"Q": "?", "L": "?", "H": "?"})
            labels.append({
                "folio": folio,
                "token": toks[0],
                "Q": meta["Q"],
                "L": meta["L"],
                "H": meta["H"],
            })

    return pages, all_tokens, p_tokens, labels


def descriptive(tokens, p_counts):
    raw = [int(p_counts[t]) for t in tokens]
    return {
        "n": len(tokens),
        "mean_P_count": float(mean(raw)) if raw else None,
        "median_P_count": float(median(raw)) if raw else None,
        "zero_P_count_fraction": (sum(v == 0 for v in raw) / len(raw)) if raw else None,
        "mean_log1p_P_count": float(mean(math.log1p(v) for v in raw)) if raw else None,
        "token_counts": {t: int(p_counts[t]) for t in tokens},
    }


def run_one(name: str, data: bytes, expected_blob: str):
    blob = git_blob_sha1(data)
    result = {
        "source": name,
        "git_blob_sha1": blob,
        "expected_git_blob_sha1": expected_blob,
        "seed": SEEDS[name],
        "permutations_requested": PERMUTATIONS,
        "alpha_bonferroni": ALPHA,
    }
    if blob != expected_blob:
        result.update({"status": "BLOCKED", "reason": "frozen source blob mismatch"})
        return result

    pages, all_counts, p_counts, labels = parse_source(data.decode("utf-8", errors="strict"))
    fmeta = pages.get("f68r1")
    if fmeta is None:
        result.update({"status": "BLOCKED", "reason": "f68r1 page metadata not found"})
        return result

    admitted = [t for t in TARGETS if all_counts[t] > 0]
    admitted_by_length = defaultdict(list)
    for t in admitted:
        admitted_by_length[len(t)].append(t)

    represented_lengths = sorted(admitted_by_length)
    strata_ge3 = sum(len(v) >= 3 for v in admitted_by_length.values())
    small_strata = [k for k, v in admitted_by_length.items() if len(v) < 3]
    target_valid = (
        len(admitted) >= 20 and
        len(represented_lengths) >= 4 and
        (not small_strata or strata_ge3 >= 4)
    )

    result.update({
        "f68r1_metadata": fmeta,
        "frozen_target_count": len(TARGETS),
        "source_admitted_target_count": len(admitted),
        "source_admitted_targets": admitted,
        "source_admitted_target_lengths": {str(k): len(v) for k, v in sorted(admitted_by_length.items())},
        "represented_target_length_strata": len(represented_lengths),
        "target_strata_with_at_least_3": strata_ge3,
    })
    if not target_valid:
        result.update({"status": "BLOCKED", "reason": "preregistered target-admission validity gate failed"})
        return result

    target_set = set(TARGETS)
    controls_by_length = defaultdict(set)
    for row in labels:
        if row["folio"] == "f68r1":
            continue
        if (row["Q"], row["L"], row["H"]) != (fmeta["Q"], fmeta["L"], fmeta["H"]):
            continue
        tok = row["token"]
        if tok in target_set:
            continue
        k = len(tok)
        if k not in admitted_by_length:
            continue
        controls_by_length[k].add(tok)

    controls_by_length = {k: sorted(v) for k, v in controls_by_length.items()}
    sufficiency = {}
    for k, targets in sorted(admitted_by_length.items()):
        pool_n = len(controls_by_length.get(k, []))
        sufficiency[str(k)] = {
            "target_count": len(targets),
            "control_count": pool_n,
            "sufficient": pool_n >= len(targets),
        }
    unique_controls = sorted({t for vals in controls_by_length.values() for t in vals})
    sufficient_lengths = sum(v["sufficient"] for v in sufficiency.values())
    controls_valid = (
        all(v["sufficient"] for v in sufficiency.values()) and
        len(unique_controls) >= 25 and
        sufficient_lengths >= 4
    )
    result.update({
        "matched_control_sufficiency": sufficiency,
        "matched_unique_control_count": len(unique_controls),
        "matched_control_tokens_by_length": {str(k): vals for k, vals in sorted(controls_by_length.items())},
    })
    if not controls_valid:
        result.update({"status": "BLOCKED", "reason": "preregistered exact documentary/length control-sufficiency gate failed"})
        return result

    obs = descriptive(admitted, p_counts)
    observed_T = obs["mean_log1p_P_count"]
    rng = random.Random(SEEDS[name])
    null = []
    for _ in range(PERMUTATIONS):
        sampled = []
        for k, targets in sorted(admitted_by_length.items()):
            sampled.extend(rng.sample(controls_by_length[k], len(targets)))
        null.append(mean(math.log1p(p_counts[t]) for t in sampled))

    null_mean = mean(null)
    p = (1 + sum(v <= observed_T for v in null)) / (PERMUTATIONS + 1)
    status = "PASS" if observed_T < null_mean and p <= ALPHA else "FAIL"
    result.update({
        "target_descriptive": obs,
        "observed_mean_log1p_P_count": observed_T,
        "null_mean_log1p_P_count": null_mean,
        "null_sd_log1p_P_count": pstdev(null),
        "observed_minus_null_mean": observed_T - null_mean,
        "monte_carlo_p_lower": p,
        "permutations_completed": len(null),
        "status": status,
    })
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--zl", type=Path, required=True)
    ap.add_argument("--takahashi", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    zl = run_one("ZL", args.zl.read_bytes(), ZL_BLOB)
    tak = run_one("Takahashi_IT2a", args.takahashi.read_bytes(), TAK_BLOB)

    if "BLOCKED" in (zl["status"], tak["status"]):
        overall = "BLOCKED"
    elif zl["status"] == "PASS" and tak["status"] == "PASS":
        overall = "PASS"
    else:
        overall = "FAIL"

    out = {
        "classification": "F68R1_STAR_LABEL_GLOBAL_PARAGRAPH_RARITY_NOT_SEMANTICS",
        "frozen_targets": TARGETS_BY_LENGTH,
        "sources": {"ZL": zl, "Takahashi_IT2a": tak},
        "status": overall,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
