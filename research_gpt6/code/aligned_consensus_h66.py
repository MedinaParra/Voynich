#!/usr/bin/env python3
import argparse, hashlib, json, math, random, re
from collections import defaultdict
from pathlib import Path

SEED = 20261007
BLOBS = {
    'A': '2a4533ab9bdfa85db9bad602d590978953055df1',
    'B': '7f491b574b65e5fba6b553e57372c3fa50e10fec',
}
FULL = (0, 1, 2, 3, 4)
REDUCED = (0, 1, 3)


def blob_sha(b):
    return hashlib.sha1(b'blob ' + str(len(b)).encode() + b'\0' + b).hexdigest()


def clean_tokens(text):
    clean = re.sub(r'<[^>]*>|\[[^]]*\]|\{[^}]*\}|@[0-9]+;', ' ', text).replace('?', ' ')
    return re.findall(r'(?<![a-z])[a-z]{2,}(?![a-z])', clean)


def generic_locus_type(pos):
    m = re.search(r'([PLCR])(?:[A-Za-z0-9]*)', pos)
    return m.group(1) if m else None


def parse(raw):
    pages = {}
    labels = {}
    running = defaultdict(list)
    for line in raw.splitlines():
        p = re.match(r'^<([^>.,]+)>\s*<!([^>]*)>', line)
        if p:
            meta = dict(re.findall(r'\$([A-Z])=([^\s>]+)', p.group(2)))
            pages[p.group(1)] = {'currier': meta.get('L', '?'), 'hand': meta.get('H', '?')}
            continue
        m = re.match(r'^<([^>]+)>\s*(.*)$', line)
        if not m or ',' not in m.group(1):
            continue
        locus, text = m.groups()
        fol = locus.split('.')[0]
        pos = locus.split(',', 1)[1]
        meta = pages.get(fol, {'currier': '?', 'hand': '?'})
        toks = clean_tokens(text)
        lm = re.search(r'(L[A-Za-z]?)', pos)
        if lm and len(toks) == 1 and '?' not in text:
            labels[locus] = {
                'locus': locus,
                'folio': fol,
                'token': toks[0],
                'currier': meta.get('currier', '?'),
                'hand': meta.get('hand', '?'),
            }
            continue
        if generic_locus_type(pos) == 'P':
            for t in toks:
                running[(fol, meta.get('currier', '?'), meta.get('hand', '?'), len(t))].append(t)
    return labels, running


def feat5(t):
    return [
        t.count('o') / len(t),
        t.count('a') / len(t),
        t.count('y') / len(t),
        float(t.startswith('q')),
        float(t.endswith('y')),
    ]


def feat(t, cols):
    f = feat5(t)
    return [f[i] for i in cols]


def build_aligned(labels_a, run_a, labels_b, run_b):
    shared = []
    for locus in sorted(set(labels_a) & set(labels_b)):
        a, b = labels_a[locus], labels_b[locus]
        if a['token'] != b['token']:
            continue
        if a['currier'] != b['currier'] or a['hand'] != b['hand']:
            continue
        key_a = (a['folio'], a['currier'], a['hand'], len(a['token']))
        key_b = (b['folio'], b['currier'], b['hand'], len(b['token']))
        if not run_a.get(key_a) or not run_b.get(key_b):
            continue
        shared.append((locus, a, key_a, key_b))

    rng_a, rng_b = random.Random(SEED), random.Random(SEED)
    pairs_a, pairs_b = [], []
    for locus, a, key_a, key_b in shared:
        ca, cb = run_a[key_a], run_b[key_b]
        pairs_a.append({
            'locus': locus,
            'folio': a['folio'],
            'positive': a['token'],
            'control': ca[rng_a.randrange(len(ca))],
        })
        pairs_b.append({
            'locus': locus,
            'folio': a['folio'],
            'positive': a['token'],
            'control': cb[rng_b.randrange(len(cb))],
        })
    return pairs_a, pairs_b


def standardize(X, T):
    d = len(X[0])
    mu = [sum(x[j] for x in X) / len(X) for j in range(d)]
    sd = []
    for j in range(d):
        v = sum((x[j] - mu[j]) ** 2 for x in X) / len(X)
        sd.append(math.sqrt(v) if v > 0 else 1.0)
    return (
        [[(x[j] - mu[j]) / sd[j] for j in range(d)] for x in X],
        [[(x[j] - mu[j]) / sd[j] for j in range(d)] for x in T],
    )


def d2(a, b):
    return sum((x - y) ** 2 for x, y in zip(a, b))


def score(pairs, cols, labels=None):
    if labels is None:
        labels = [1] * len(pairs)
    by_fol = defaultdict(list)
    for i, p in enumerate(pairs):
        by_fol[p['folio']].append(i)
    all_ix = list(range(len(pairs)))
    preds, truth = [], []
    for fol in sorted(by_fol):
        te = by_fol[fol]
        tes = set(te)
        tr = [i for i in all_ix if i not in tes]
        if not tr or not te:
            continue
        X, y, T, yt = [], [], [], []
        for i in tr:
            p = pairs[i]
            lab = labels[i]
            X.extend([feat(p['positive'], cols), feat(p['control'], cols)])
            y.extend([lab, 1 - lab])
        for i in te:
            p = pairs[i]
            lab = labels[i]
            T.extend([feat(p['positive'], cols), feat(p['control'], cols)])
            yt.extend([lab, 1 - lab])
        X, T = standardize(X, T)
        means = {}
        for c in (0, 1):
            z = [X[j] for j, v in enumerate(y) if v == c]
            means[c] = [sum(x[k] for x in z) / len(z) for k in range(len(z[0]))]
        preds.extend(min((0, 1), key=lambda c: d2(x, means[c])) for x in T)
        truth.extend(yt)
    rec = []
    for c in (0, 1):
        ix = [i for i, v in enumerate(truth) if v == c]
        rec.append(sum(preds[i] == c for i in ix) / len(ix))
    return sum(rec) / 2


def perm_test(pairs, cols, observed, n, seed):
    rng = random.Random(seed)
    null = []
    for _ in range(n):
        null.append(score(pairs, cols, [rng.randrange(2) for _ in pairs]))
    p = (1 + sum(x >= observed for x in null)) / (1 + len(null))
    return p, sum(null) / len(null), len(null)


def source_result(pairs, nperm, seed_offset):
    full_ba = score(pairs, FULL)
    red_ba = score(pairs, REDUCED)
    if full_ba <= 0.5:
        return {'status': 'BLOCKED', 'reason': 'full-model BA <= 0.5', 'full_ba': full_ba, 'reduced_ba': red_ba}
    pfull, nfull, cfull = perm_test(pairs, FULL, full_ba, nperm, SEED + seed_offset)
    pred, nred, cred = perm_test(pairs, REDUCED, red_ba, nperm, SEED + seed_offset)
    retention = (red_ba - 0.5) / (full_ba - 0.5)
    passed = cfull == 999 and cred == 999 and full_ba > 0.5 and red_ba > 0.5 and pfull <= 0.05 and pred <= 0.05 and retention >= 0.80
    return {
        'full_ba': full_ba,
        'full_null_mean_ba': nfull,
        'full_p': pfull,
        'full_permutations_completed': cfull,
        'reduced_ba': red_ba,
        'reduced_null_mean_ba': nred,
        'reduced_p': pred,
        'reduced_permutations_completed': cred,
        'retention_excess_over_chance': retention,
        'status': 'PASS' if passed else 'FAIL',
    }


def write(path, out):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, indent=2, sort_keys=True) + '\n')
    print(json.dumps(out, indent=2, sort_keys=True))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--source-a', type=Path, required=True)
    ap.add_argument('--source-b', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--permutations', type=int, default=999)
    args = ap.parse_args()

    ba, bb = args.source_a.read_bytes(), args.source_b.read_bytes()
    out = {
        'classification': 'H66_ALIGNED_CONSENSUS_LABELS_NOT_TRANSLATION',
        'seed': SEED,
        'source_a_blob': blob_sha(ba),
        'source_b_blob': blob_sha(bb),
        'permutations_requested_each_model_each_source': args.permutations,
        'minimum_aligned_events': 100,
        'minimum_folios': 8,
    }
    if out['source_a_blob'] != BLOBS['A'] or out['source_b_blob'] != BLOBS['B']:
        out.update({'status': 'BLOCKED', 'reason': 'frozen source blob mismatch'})
        write(args.out, out)
        return

    la, ra = parse(ba.decode())
    lb, rb = parse(bb.decode())
    pa, pb = build_aligned(la, ra, lb, rb)
    loci_a = [p['locus'] for p in pa]
    loci_b = [p['locus'] for p in pb]
    nfol = len(set(p['folio'] for p in pa))
    out.update({
        'source_a_label_count': len(la),
        'source_b_label_count': len(lb),
        'aligned_retained_events': len(pa),
        'represented_folios': nfol,
        'locus_lists_identical': loci_a == loci_b,
    })
    if len(pa) < 100 or nfol < 8 or loci_a != loci_b:
        out.update({'status': 'BLOCKED', 'reason': 'preregistered aligned-sample threshold or identity condition not met'})
        write(args.out, out)
        return

    A = source_result(pa, args.permutations, 0)
    B = source_result(pb, args.permutations, 1)
    out['source_a'] = A
    out['source_b'] = B
    if 'BLOCKED' in (A.get('status'), B.get('status')):
        out['status'] = 'BLOCKED'
    else:
        out['status'] = 'PASS' if A.get('status') == 'PASS' and B.get('status') == 'PASS' else 'FAIL'
    out.update({
        'language_identification': 'NOT_RUN',
        'semantic_identification': 'NOT_RUN',
        'translation': 'NOT_RUN',
        'decipherment': 'NOT_RUN',
    })
    write(args.out, out)


if __name__ == '__main__':
    main()
