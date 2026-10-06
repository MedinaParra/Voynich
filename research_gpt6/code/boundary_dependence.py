#!/usr/bin/env python3
"""Exploratory IVTFF paragraph-token and EVA edge-character dependence audit.

Not an exact replication of a paper and not a decipherment. Standard library only.
Uncertain comma separators are tested both split and joined. Unreadable or
alternative tokens break adjacency; drawing gaps break runs. No cross-line pairs.
"""
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import random
import re
import sys

SOURCE_COMMIT = '47e6a77dc9d5cd570c375f4aff710fa4a0567278'
SOURCE_BLOB = '2a4533ab9bdfa85db9bad602d590978953055df1'


def parse(raw, commas):
    rows, rejected, locus_count = [], 0, 0
    meta = {}
    for line in raw.splitlines():
        page = re.match(r'^<([^>.,]+)>\s*<!', line)
        if page:
            meta = dict(re.findall(r'\$([A-Z])=([^\s>]+)', line))
            continue
        m = re.match(r'^<([^>]+)>\s*(.*)$', line)
        if not m or ',' not in m[1]:
            continue
        locus, text = m.groups()
        kind = locus.split(',', 1)[1]
        if not re.search(r'P[0-9a-z]', kind):
            continue
        locus_count += 1
        text = text.replace('<->', '|')
        text = re.sub(r'<[^>]*>', '', text)
        # Braces and bracket alternatives deliberately remain invalid tokens.
        text = text.replace(',', '.' if commas == 'split' else '')
        text = re.sub(r'\s+', '.', text.strip())
        run = []
        for token in re.split(r'([.|])', text):
            if token == '.':
                continue
            if token == '|':
                if run:
                    rows.append({'locus': locus, 'quire': meta.get('Q'),
                                 'folio': locus.split('.')[0], 'words': run})
                    run = []
                continue
            if not token:
                continue
            if re.fullmatch(r'[a-z]+', token):
                run.append(token)
            else:
                rejected += 1
                if run:
                    rows.append({'locus': locus, 'quire': meta.get('Q'),
                                 'folio': locus.split('.')[0], 'words': run})
                    run = []
        if run:
            rows.append({'locus': locus, 'quire': meta.get('Q'),
                         'folio': locus.split('.')[0], 'words': run})
    return rows, rejected, locus_count


def entropy(counts):
    n = sum(counts.values())
    return -sum(c / n * math.log2(c / n) for c in counts.values()) if n else 0.0


def mi(pairs):
    joint = Counter(pairs)
    left, right = Counter(), Counter()
    for (x, y), c in joint.items():
        left[x] += c
        right[y] += c
    n = sum(joint.values())
    return sum(c / n * math.log2(c * n / (left[x] * right[y]))
               for (x, y), c in joint.items()) if n else 0.0


def metric(runs, mapping=None):
    if mapping is None:
        return mi((a[-1], b[0]) for row in runs for a, b in zip(row, row[1:]))
    return mi((mapping.get(a, -1), mapping.get(b, -1))
              for row in runs for a, b in zip(row, row[1:]))


def formula_checks():
    assert abs(mi([(0, 0), (0, 1), (1, 0), (1, 1)])) < 1e-12
    assert abs(mi([(0, 0), (1, 1)]) - 1.0) < 1e-12
    assert mi([(0, 0)] * 10) == 0


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--corpus', required=True, type=Path)
    ap.add_argument('--out', required=True, type=Path)
    ap.add_argument('--permutations', type=int, default=199)
    ap.add_argument('--seed', type=int, default=20261006)
    args = ap.parse_args()
    formula_checks()
    binary = args.corpus.read_bytes()
    raw = binary.decode('utf-8')
    blob_hash = hashlib.sha1(b'blob ' + str(len(binary)).encode() + b'\0' + binary).hexdigest()
    if blob_hash != SOURCE_BLOB:
        raise SystemExit('Source Git blob mismatch: ' + blob_hash)
    out = {'classification': 'EXPLORATORY_NEW_ANALYSIS_NOT_EXACT_PAPER_REPLICATION',
           'source_commit': SOURCE_COMMIT, 'source_blob': blob_hash,
           'source_sha256': hashlib.sha256(binary).hexdigest(),
           'seed': args.seed, 'permutations': args.permutations,
           'environment': {'python': sys.version.split()[0]},
           'null': 'independent Fisher-Yates permutation within each retained valid run; line composition and frequencies preserved',
           'interpretation': 'MI excess is an observed-minus-shuffle statistic, not a nonnegative estimator of true MI or a semantic measure.',
           'glyph_warning': 'EVA final/initial characters are transliteration characters, not established manuscript glyph units.',
           'modes': {}}
    all_tests = []
    for mode in ('split', 'join'):
        rows, excluded, loci = parse(raw, mode)
        runs = [r['words'] for r in rows]
        counts = Counter(w for row in runs for w in row)
        ranked = sorted(counts, key=lambda w: (-counts[w], w))
        mappings = {str(k): {w: i for i, w in enumerate(ranked[:k])} for k in (200, 1000, 2000)}
        mappings['edges'] = None
        obs = {k: metric(runs, mapping) for k, mapping in mappings.items()}
        nulls = {k: [] for k in mappings}
        rng = random.Random(args.seed)
        for _ in range(args.permutations):
            shuffled = []
            for row in runs:
                s = list(row)
                rng.shuffle(s)
                shuffled.append(s)
            for k, mapping in mappings.items():
                nulls[k].append(metric(shuffled, mapping))
        tests = {}
        for k, mapping in mappings.items():
            values = nulls[k]
            mean = sum(values) / len(values)
            p = (1 + sum(v >= obs[k] - 1e-12 for v in values)) / (len(values) + 1)
            if mapping is None:
                marginal = Counter(c for row in runs for w in row for c in (w[-1], w[0]))
                token_mass = None
            else:
                marginal = Counter()
                for w, c in counts.items():
                    marginal[mapping.get(w, -1)] += c
                token_mass = sum(c for w, c in counts.items() if w in mapping) / sum(counts.values())
            h = entropy(marginal)
            test = {'observed_mi_bits': obs[k], 'shuffle_mean_bits': mean,
                    'shuffle_sd_bits': math.sqrt(sum((v - mean) ** 2 for v in values) / len(values)),
                    'excess_bits': obs[k] - mean, 'marginal_entropy_bits': h,
                    'excess_fraction_of_marginal_entropy': (obs[k] - mean) / h if h else None,
                    'p_one_sided_mc': p, 'top_k_token_mass': token_mass}
            tests[k] = test
            all_tests.append(test)
        out['modes'][mode] = {'paragraph_loci': loci, 'retained_runs': len(runs),
            'physical_lines_with_clean_words': len(set(r['locus'] for r in rows)),
            'folios': len(set(r['folio'] for r in rows)),
            'quire_metadata_groups': len(set(r['quire'] for r in rows)),
            'tokens': sum(counts.values()), 'types': len(counts),
            'rejected_token_chunks': excluded,
            'pairs': sum(max(0, len(row) - 1) for row in runs),
            'hapax_type_fraction': sum(c == 1 for c in counts.values()) / len(counts),
            'tests': tests}
        print(mode, json.dumps(out['modes'][mode], ensure_ascii=False), flush=True)
    ordered = sorted(all_tests, key=lambda t: t['p_one_sided_mc'])
    running = 0.0
    for i, test in enumerate(ordered):
        running = max(running, min(1.0, (len(ordered) - i) * test['p_one_sided_mc']))
        test['p_holm_family_8'] = running
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print('Saved', args.out, flush=True)


if __name__ == '__main__':
    main()
