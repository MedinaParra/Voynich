#!/usr/bin/env python3
"""Prepare blinded, author-held-out Latin cipher controls (experiment 86).

The public packet contains no case labels, keys, offsets, or reserved plaintexts.
The private packet is an evaluation escrow, not an input to the decipherer.
No Voynich material is used as Latin training or as a translation label.

Replay, after the blind experiment is frozen, with --seed-file pointing to the
original private_seed.json. Identical source bytes and generator bytes reproduce
the public/private JSON bytes. Never print or reveal that seed during solving.
"""

import argparse
import base64
from collections import Counter
import hashlib
import json
from pathlib import Path
import platform
import random
import re
import secrets
import string


ALPHABET = string.ascii_lowercase
TRAIN_PATHS = tuple(f"apicius/apicius{i}.txt" for i in range(1, 6))
TEST_PATHS = tuple(f"caesar/gall{i}.txt" for i in range(1, 4))
LETTERS_PER_CASE = 2000
NORMALIZATION = {
    "drop_first_line": True,
    "drop_lines_where_str_isupper": True,
    "lowercase": "Python str.lower",
    "tokens": "re.findall('[a-z]+', text)",
    "join": "single ASCII space between tokens",
    "u_v_or_i_j_merging": False,
    "unicode_transliteration": False,
    "sample_length": "2000 letters, excluding spaces",
    "window": "uniform starting letter index; boundary words may be clipped",
}


def sha256(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical_bytes(value):
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode()


def write_json(path, value, private=False):
    path.write_bytes(canonical_bytes(value))
    if private:
        path.chmod(0o600)


def load_sources(path):
    bundle = json.loads(path.read_text())
    texts, provenance = {}, []
    wanted = set(TRAIN_PATHS + TEST_PATHS)
    for entry in bundle["files"]:
        if entry["path"] not in wanted:
            continue
        raw = base64.b64decode(entry["base64"], validate=False)
        blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        if blob != entry["sha"] or len(raw) != int(entry["size"]):
            raise ValueError(f"Source integrity mismatch: {entry['path']}")
        lines = [line for i, line in enumerate(raw.decode("utf-8").splitlines())
                 if i > 0 and not line.isupper()]
        tokens = re.findall("[a-z]+", "\n".join(lines).lower())
        text = " ".join(tokens)
        texts[entry["path"]] = text
        provenance.append({"path": entry["path"], "git_blob_sha1": blob,
                           "raw_sha256": sha256(raw), "raw_bytes": len(raw),
                           "normalized_sha256": sha256(text.encode()),
                           "words": len(tokens), "letters": sum(map(len, tokens))})
    if set(texts) != wanted:
        raise ValueError("Required Latin sources are missing or duplicated")
    if len(provenance) != len(wanted):
        raise ValueError("Duplicate Latin source entries")
    return bundle["commit"], texts, provenance


def letter_window(text, start, n=LETTERS_PER_CASE):
    positions = [i for i, char in enumerate(text) if char != " "]
    if not 0 <= start <= len(positions) - n:
        raise ValueError("Letter window outside source")
    selected = text[positions[start]:positions[start + n - 1] + 1]
    assert len(selected.replace(" ", "")) == n
    return selected


def random_window(text, rng, excluded=None):
    nletters = len(text.replace(" ", ""))
    if excluded is None:
        start = rng.randrange(nletters - LETTERS_PER_CASE + 1)
    else:
        lo, hi = excluded
        candidates = [i for i in range(nletters - LETTERS_PER_CASE + 1)
                      if i + LETTERS_PER_CASE <= lo or i >= hi]
        if not candidates:
            raise ValueError("No disjoint reserved homophonic window")
        start = rng.choice(candidates)
    return start, letter_window(text, start)


def mono_key(rng):
    symbols = list(ALPHABET)
    rng.shuffle(symbols)
    encryption = "".join(symbols)
    decryption = "".join(ALPHABET[encryption.index(c)] for c in ALPHABET)
    return encryption, decryption


def apply_key(text, key):
    return text.translate(str.maketrans(ALPHABET, key))


def permute_letters_preserving_spaces(ciphertext, rng):
    symbols = list(ciphertext.replace(" ", ""))
    rng.shuffle(symbols)
    shuffled = iter(symbols)
    result = "".join(" " if char == " " else next(shuffled) for char in ciphertext)
    assert Counter(result) == Counter(ciphertext)
    assert [i for i, c in enumerate(result) if c == " "] == [
        i for i, c in enumerate(ciphertext) if c == " "]
    return result


def homophonic_cipher(plaintext, rng):
    counts = Counter(plaintext.replace(" ", ""))
    plain_symbols = sorted(counts)
    if len(plain_symbols) >= len(ALPHABET):
        raise ValueError("Homophonic control requires spare cipher symbols")
    available = list(ALPHABET)
    rng.shuffle(available)
    aliases = {plain: [available.pop()] for plain in plain_symbols}
    frequency_order = sorted(plain_symbols, key=lambda char: (-counts[char], char))
    for i, cipher in enumerate(available):
        aliases[frequency_order[i % len(frequency_order)]].append(cipher)
    ciphertext = "".join(" " if char == " " else rng.choice(aliases[char])
                         for char in plaintext)
    actual = Counter(ciphertext.replace(" ", ""))
    ceiling_correct = sum(max(actual[c] for c in group) for group in aliases.values())
    reverse = {c: plain for plain, group in aliases.items() for c in group}
    decryption = "".join(reverse[c] for c in ALPHABET)
    assert len(reverse) == 26 and len(set(decryption)) < 26
    return ciphertext, aliases, decryption, ceiling_correct


def prepare(source_path, out, seed_file=None):
    public, private = out / "public", out / "private"
    if out.exists() and any(out.iterdir()):
        raise ValueError("Output directory must be empty; refuse to replace a packet")
    out.mkdir(parents=True, exist_ok=True)
    public.mkdir()
    private.mkdir(mode=0o700)
    private.chmod(0o700)
    source_commit, texts, provenance = load_sources(source_path)
    generator_sha = sha256(Path(__file__).read_bytes())
    if seed_file is None:
        seed = secrets.randbits(64)
    else:
        previous = json.loads(seed_file.read_text())
        seed = previous["seed_uint64"]
        if previous.get("generator_sha256") != generator_sha:
            raise ValueError("Replay requires the identical generator bytes")
        if previous.get("source_bundle_sha256") != sha256(source_path.read_bytes()):
            raise ValueError("Replay requires the identical source bundle bytes")
    if not isinstance(seed, int) or isinstance(seed, bool) or not 0 <= seed < 2 ** 64:
        raise ValueError("Seed must be an unsigned 64-bit integer")
    rng = random.Random(seed)
    cases, sampled = [], {}
    for index, path in enumerate(TEST_PATHS, 1):
        start, plaintext = random_window(texts[path], rng)
        sampled[path] = (start, start + LETTERS_PER_CASE)
        encryption, decryption = mono_key(rng)
        ciphertext = apply_key(plaintext, encryption)
        pair = f"P{index}"
        common = {"role": "monoalphabetic_positive", "pair_id": pair,
                  "source_path": path, "letter_start": start,
                  "letter_end_exclusive": start + LETTERS_PER_CASE,
                  "encryption_key_plain_to_cipher": encryption,
                  "decryption_key_cipher_to_plain": decryption}
        for variant, plain, cipher in (
                ("spaces", plaintext, ciphertext),
                ("no_spaces", plaintext.replace(" ", ""), ciphertext.replace(" ", ""))):
            cases.append({**common, "variant": variant, "ciphertext": cipher,
                          "plaintext": plain, "letters_plaintext": plain.replace(" ", "")})
        null_cipher = permute_letters_preserving_spaces(ciphertext, rng)
        null_plain = apply_key(null_cipher, decryption)
        cases.append({**common, "role": "frequency_matched_null", "variant": "spaces",
                      "ciphertext": null_cipher, "plaintext": null_plain,
                      "letters_plaintext": null_plain.replace(" ", ""),
                      "accuracy_interpretation": "Generating-key recovery only; the shuffled plaintext is not coherent Latin"})
    path = TEST_PATHS[1]
    start, plaintext = random_window(texts[path], rng, sampled[path])
    ciphertext, aliases, decryption, ceiling = homophonic_cipher(plaintext, rng)
    cases.append({"role": "homophonic_wrong_model", "variant": "spaces",
                  "pair_id": None, "source_path": path, "letter_start": start,
                  "letter_end_exclusive": start + LETTERS_PER_CASE,
                  "ciphertext": ciphertext, "plaintext": plaintext,
                  "letters_plaintext": plaintext.replace(" ", ""),
                  "aliases_plain_to_cipher": aliases,
                  "decryption_key_cipher_to_plain": decryption,
                  "best_bijective_correct_letters": ceiling,
                  "best_bijective_character_accuracy": ceiling / LETTERS_PER_CASE})
    rng.shuffle(cases)
    for index, case in enumerate(cases, 1):
        case["id"] = f"C{index:02d}"
        case["observed_cipher_symbols"] = "".join(sorted(set(case["ciphertext"]) - {" "}))
        assert len(case["letters_plaintext"]) == LETTERS_PER_CASE
        assert set(case["ciphertext"]) <= set(ALPHABET + " ")
    training = {"schema": "known-cipher-training-v1", "author_group": "apicius",
                "books": [{"source_path": path, "text": texts[path]} for path in TRAIN_PATHS]}
    cipher_public = {"schema": "known-cipher-cases-v1",
                     "cases": [{"id": case["id"], "ciphertext": case["ciphertext"]} for case in cases]}
    truth = {"schema": "known-cipher-truth-v1", "experiment": 86,
             "source_commit": source_commit, "generator_sha256": generator_sha,
             "normalization": NORMALIZATION, "cases": cases}
    write_json(public / "training_corpus.json", training)
    write_json(public / "ciphertexts.json", cipher_public)
    write_json(private / "truth.json", truth, private=True)
    seed_record = {"schema": "known-cipher-private-seed-v1", "seed_uint64": seed,
                   "rng": "random.Random", "seed_bits": 64,
                   "python_version": platform.python_version(),
                   "generator_sha256": generator_sha,
                   "source_bundle_sha256": sha256(source_path.read_bytes())}
    write_json(private / "private_seed.json", seed_record, private=True)
    manifest = {"schema": "known-cipher-manifest-v1", "experiment": 86,
                "alphabet": ALPHABET, "space": "ASCII U+0020, preserved",
                "case_count": len(cases), "letters_per_case": LETTERS_PER_CASE,
                "normalization": NORMALIZATION, "source_commit": source_commit,
                "source_bundle_sha256": sha256(source_path.read_bytes()),
                "sources": provenance, "training_sources": list(TRAIN_PATHS),
                "reserved_sources": list(TEST_PATHS), "generator_sha256": generator_sha,
                "truth_commitment_sha256": sha256((private / "truth.json").read_bytes()),
                "private_seed_commitment_sha256": sha256((private / "private_seed.json").read_bytes()),
                "public_files_sha256": {name: sha256((public / name).read_bytes())
                                        for name in ("training_corpus.json", "ciphertexts.json")}}
    write_json(public / "manifest.json", manifest)
    receipt = {"schema": "known-cipher-generation-receipt-v1",
               "files_sha256": {f"{group}/{path.name}": sha256(path.read_bytes())
                                for group in ("public", "private")
                                for path in sorted((out / group).iterdir()) if path.is_file()}}
    write_json(private / "generation_receipt.json", receipt, private=True)
    return {"public_path": str(public.resolve()),
            "private_path": str(private.resolve()), "case_count": len(cases),
            "manifest_sha256": sha256((public / "manifest.json").read_bytes()),
            "truth_commitment_sha256": manifest["truth_commitment_sha256"],
            "generator_sha256": generator_sha}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--latin", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--seed-file", type=Path, help="Private replay seed; never supply to solver")
    args = parser.parse_args()
    print(json.dumps(prepare(args.latin, args.out, args.seed_file), sort_keys=True))


if __name__ == "__main__":
    main()
