#!/usr/bin/env python3
import argparse, hashlib, json, math, random, re
from collections import defaultdict
from pathlib import Path

SEED = 20261007
SOURCES = {
    'A': {
        'blob': '2a4533ab9bdfa85db9bad602d590978953055df1',
        'expected': (780, 495, 34, 285),
    },
    'B': {
        'blob': '7f491b574b65e5fba6b553e57372c3fa50e10fec',
        'expected': (669, 388, 32, 281),
    },
}
FULL = (0, 1, 2, 3, 4)
REDUCED = (0, 1, 3)


def blob_sha(b):
    return hashlib.sha1(b'blob ' + str(len(b)).encode() + b'\0' + b).hexdigest()


def all_feats(t):
    return [
        t.count('o') / len(t),
        t.count('a') / len(t),
        t.count('y') / len(t),
        float(t.startswith('q')),
        float(t.endswith('y')),
    ]


def feats(t, cols):
    f = all_feats(t)
    return [f[i] for i in cols]


def clean_tokens(text):
    clean = re.sub(r'<[^>]*>|\[[^]]*\]|\{[^}]*\}|@[0-9]+;', ' ', text).replace('?', ' ')
    return re.findall(r'(?<![a-z])[a-z]{2,}(?![a-z])', clean)


def generic_locus_type(pos):
    m = re.search(r'([PLCR])(?:[A-Za-z0-9]*)', pos)
    return m.group(1) if m else None


def parse(raw):
    pages, positives = {}, []
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
        meta = pages.get(fol, {})
        toks = clean_tokens(text)
        lm = re.search(r'(L[A-Za-z]?)', pos)
        if lm and len(toks) == 1 and '?' not in text:
            positives.append({'folio': fol, 'token': toks[0], **meta})
            continue
        if generic_locus_type(pos) == 'P':
            for t in toks:
                running[(fol, meta.get('currier', '?'), meta.get('hand', '?'), len(t))].append(t)
    return positives, running


def build_pairs(positives, running):
    rng = random.Random(SEED)
    pairs, excluded = [], 0
    for r in sorted(positives, key=lambda x: (x['folio'], x['token'], x['currier'], x['hand'])):
        key = (r['folio'], r['currier'], r['hand'], len(r['token']))
        cand = running.get(key, [])
        if not cand:
            excluded += 1
            continue
        pairs.append({'folio': r['folio'], 'positive': r['token'], 'control': cand[rng.randrange(len(cand))]})
    return pairs, excluded


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
    preds, truth = [], []
    by_fol = defaultdict(list)
    for i, p in enumerate(pairs):
        by_fol[p['folio']].append(i)
    all_ix = list(range(len(pairs)))
    for fol in sorted(by_fol):
        te = by_fol[fol]
        te_set = set(te)
        tr = [i for i in all_ix if i not in te_set]
        if not tr or not te:
            continue
        X, y, T, yt = [], [], [], []
        for i in tr:
            p = pairs[i]
            lab = labels[i]
            X.extend([feats(p['positive'], cols), feats(p['control'], cols)])
            y.extend([lab, 1 - lab])
        for i in te:
            p = pairs[i]
            lab = labels[i]
            T.extend([feats(p['positive'], cols), feats(p['control'], cols)])
            yt.extend([lab, 1 - lab])
        X, T = standardize(X, T)
        means = {}
        for c in (0, 1):
            z = [X[j] for j, v in enumerate(y) if v == c]
            means[c] = [sum(x[k] for x in z) / len(z) for k in range(len(z[0]))]
        preds.extend(min((0, 1), key=lambda c: d2(x, means[c])) for x in T)
        truth.extend(yt)
    recalls = []
    for c in (0, 1):
        ix = [i for i, v in enumerate(truth) if v == c]
        recalls.append(sum(preds[i] == c for i in ix) / len(ix))
    return sum(recalls) / 2


def run_source(name, rawb, permutations):
    cfg = SOURCES[name]
    observed_blob = blob_sha(rawb)
    out = {'source': name, 'expected_blob': cfg['blob'], 'observed_blob': observed_blob}
    if observed_blob != cfg['blob']:
        out.update({'status': 'BLOCKED', 'reason': 'frozen source blob mismatch', 'permutations_completed': 0})
        return out
    positives, running = parse(rawb.decode())
    pairs, excluded = build_pairs(positives, running)
    rec = (len(positives), len(pairs), len(set(p['folio'] for p in pairs)), excluded)
    out['reconstruction'] = rec
    out['expected_reconstruction'] = cfg['expected']
    if rec != cfg['expected']:
        out.update({'status': 'BLOCKED', 'reason': 'frozen sample reconstruction mismatch', 'permutations_completed': 0})
        return out
    full_ba = score(pairs, FULL)
    reduced_ba = score(pairs, REDUCED)
    if full_ba <= 0.5:
        out.update({'status': 'BLOCKED', 'reason': 'full-model BA is not above chance', 'full_ba': full_ba, 'reduced_ba': reduced_ba, 'permutations_completed': 0})
        return out
    retention = (reduced_ba - 0.5) / (full_ba - 0.5)
    rng = random.Random(SEED)
    null = []
    for _ in range(permutations):
        null.append(score(pairs, REDUCED, [rng.randrange(2) for _ in pairs]))
    p = (1 + sum(x >= reduced_ba for x in null)) / (1 + len(null))
    valid = len(null) == 999
    passed = valid and reduced_ba > 0.5 and p <= 0.05 and retention >= 0.80
    out.update({
        'full_ba': full_ba,
        'reduced_ba': reduced_ba,
        'absolute_ba_delta_reduced_minus_full': reduced_ba - full_ba,
        'retention_excess_over_chance': retention,
        'reduced_null_mean_ba': sum(null) / len(null),
        'reduced_monte_carlo_p': p,
        'permutations_completed': len(null),
        'status': 'PASS' if passed else 'FAIL',
    })
    return out


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
    out = {
        'classification': 'H65_MINIMAL_THREE_FEATURE_MODEL_NOT_TRANSLATION',
        'seed': SEED,
        'full_features': ['frac_o', 'frac_a', 'frac_y', 'starts_q', 'ends_y'],
        'reduced_features': ['frac_o', 'frac_a', 'starts_q'],
        'retention_threshold': 0.80,
        'permutations_requested_each_source': args.permutations,
    }
    A = run_source('A', args.source_a.read_bytes(), args.permutations)
    B = run_source('B', args.source_b.read_bytes(), args.permutations)
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
